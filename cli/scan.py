import os
import requests
import click
import shutil
import tempfile
import sys
import time
import zipfile
from datetime import datetime
from colorama import Fore, Style, init
from .utils import get_config_value

# Initialize colorama
init(autoreset=True)

SUCCESS_EXIT_CODE = 0
ERROR_EXIT_CODE = 1
FAILURE_EXIT_CODE = 2

@click.command()
@click.option('--target', required=True, help='Path to the target codebase')
@click.option('--project', required=True, help='Project name in CodeThreat')
@click.option('--url', default=lambda: get_config_value("CODETHREAT_APP_URL"), help='CodeThreat application URL')
@click.option('--token', default=lambda: get_config_value("CODETHREAT_SECRET"), help='Personal Access Token')
@click.option('--org', default=lambda: get_config_value("CODETHREAT_ORG"), help='Organization name')
@click.option('--branch', default=None, help='Branch name for the scan (optional)')
@click.option('--policy_id', default=None, help='Policy ID under which the analysis should be processed (optional)')
def scan(target, project, url, token, org, branch, policy_id):
    """Run a SAST scan on the specified target."""

    # Ensure the base URL doesn't have a trailing slash
    base_url = url.rstrip('/')

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "CodeThreat-CLI",
        "x-ct-organization": org,
    }

    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def print_message(message, color=Fore.WHITE, newline=True):
        if newline:
            print(f"{color}[{get_timestamp()}] {message}{Style.RESET_ALL}")
        else:
            print(f"{color}[{get_timestamp()}] {message}{Style.RESET_ALL}", end="\r")
    
    # Log scan initiation details
    print_message(f"[CT*] ===== CODETHREAT CLI SCAN STARTED =====", Fore.CYAN)
    print_message(f"[CT*] Scan initiated at: {get_timestamp()}", Fore.CYAN)
    print_message(f"[CT*] Target: {target}", Fore.CYAN)
    print_message(f"[CT*] Project: {project}", Fore.CYAN)
    print_message(f"[CT*] Organization: {org}", Fore.CYAN)
    print_message(f"[CT*] Base URL: {base_url}", Fore.CYAN)
    if branch:
        print_message(f"[CT*] Branch: {branch}", Fore.CYAN)
    if policy_id:
        print_message(f"[CT*] Policy ID: {policy_id}", Fore.CYAN)

    def poll_scan_status(scan_id):
        status_url = f"{base_url}/api/scan/status/{scan_id}"
        seen_logs = set()
        scan_started = False

        # Track the previous values of SAST and SCA severities
        previous_sast = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        previous_sca = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        while True:
            status_response = requests.get(status_url, headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                state = status_data.get('state', 'unknown')

                # Print new logs
                logs = status_data.get('logs', [])
                for log in logs:
                    log_id = (log['logType'], log['message'], log['create_date'])
                    if log_id not in seen_logs:
                        print_message(f"[CT*] {log['logType']}: {log['message']}", Fore.YELLOW)
                        seen_logs.add(log_id)

                        # Notify the user when the scan officially starts
                        if log['logType'] == "information" and log['message'] == "INFO110: Scan is starting...":
                            if not scan_started:
                                scan_started = True
                                print_message(f"[CT*] The scan has officially started. The CLI will notify you when the scan is complete.", Fore.CYAN)

                # Display scan metrics if they have changed
                sast_severities = status_data.get('sast_severities', {})
                sca_severities = status_data.get('sca_severities', {})

                sast_changes = {
                    severity: sast_severities.get(severity, 0) - previous_sast[severity]
                    for severity in previous_sast
                    if sast_severities.get(severity, 0) > previous_sast[severity]
                }

                sca_changes = {
                    severity: sca_severities.get(severity, 0) - previous_sca[severity]
                    for severity in previous_sca
                    if sca_severities.get(severity, 0) > previous_sca[severity]
                }

                if sast_changes or sca_changes:
                    # Beautify the findings output
                    if sca_changes:
                        print_message("[CT*] New Dependency Issues Found:", Fore.RED)
                        for severity, count in sca_changes.items():
                            print_message(f"  {Fore.RED if severity == 'critical' else Fore.YELLOW if severity == 'high' else Fore.MAGENTA}• {count} {severity.capitalize()} Issue{'s' if count > 1 else ''}{Style.RESET_ALL}")

                    if sast_changes:
                        print_message("[CT*] New Code Issues Found:", Fore.RED)
                        for severity, count in sast_changes.items():
                            print_message(f"  {Fore.RED if severity == 'critical' else Fore.YELLOW if severity == 'high' else Fore.MAGENTA}• {count} {severity.capitalize()} Issue{'s' if count > 1 else ''}{Style.RESET_ALL}")

                    # Update previous values
                    previous_sast.update(sast_severities)
                    previous_sca.update(sca_severities)

                # Check if the scan is complete
                if state.lower() == 'end':
                    print_message(f"[CT*] Scan completed successfully.", Fore.GREEN)
                    report_url = f"{base_url}/projects/project-details/{project}?tenant={org}"
                    print_message(f"Check the report here: {report_url}", Fore.BLUE)
                    sys.exit(SUCCESS_EXIT_CODE)
                elif state.lower() in ['failed', 'error']:
                    print_message(f"[CT*] Scan failed or encountered an error.", Fore.RED)
                    sys.exit(FAILURE_EXIT_CODE)
            else:
                print_message(f"[CT*] Failed to retrieve scan status: {status_response.status_code} - {status_response.text}", Fore.RED)
                sys.exit(ERROR_EXIT_CODE)

            time.sleep(10)

    # Check if the project exists
    print_message(f"[CT*] ===== PROJECT VERIFICATION =====", Fore.CYAN)
    project_check_url = f"{base_url}/api/project?key={project}"
    print_message(f"[CT*] Checking project existence at: {project_check_url}", Fore.BLUE)
    
    try:
    response = requests.get(project_check_url, headers=headers)
        print_message(f"[CT*] Project check response: {response.status_code}", Fore.BLUE)
    except Exception as e:
        print_message(f"[CT*] ERROR: Failed to check project existence: {e}", Fore.RED)
        sys.exit(ERROR_EXIT_CODE)

    if response.status_code == 200:
        print_message(f"[CT*] Project '{project}' exists. Proceeding with scan.", Fore.GREEN)
    else:
        # Create the project if it doesn't exist
        create_project_url = f"{base_url}/api/project/add"
        project_data = {
            "project_name": project,
            "description": f"Project {project} created by CodeThreat CLI",
            "tags": ["code-threat", "cli"]
        }
        response = requests.post(create_project_url, headers=headers, json=project_data)

        # Correctly handle the response based on the `error` field and `message`
        if response.status_code == 200:
            response_data = response.json()
            if not response_data.get('error') and response_data.get('result', {}).get('message') == "successfull":
                print_message(f"[CT*] Project '{project}' created successfully.", Fore.GREEN)
            else:
                print_message(f"[CT*] Failed to create project '{project}': {response.text}", Fore.RED)
                sys.exit(ERROR_EXIT_CODE)
        else:
            print_message(f"[CT*] Failed to create project '{project}': {response.text}", Fore.RED)
            sys.exit(ERROR_EXIT_CODE)

    # Zip the target directory in a cross-platform manner
    print_message(f"[CT*] Starting ZIP creation process...", Fore.CYAN)
    print_message(f"[CT*] Target directory: {target}", Fore.CYAN)
    
    # Log system information
    import platform
    print_message(f"[CT*] System: {platform.system()} {platform.release()}", Fore.BLUE)
    print_message(f"[CT*] Python: {platform.python_version()}", Fore.BLUE)
    
    # Check if target directory exists and get initial size
    if not os.path.exists(target):
        print_message(f"[CT*] ERROR: Target directory does not exist: {target}", Fore.RED)
        sys.exit(ERROR_EXIT_CODE)
    
    # Calculate initial directory size
    total_size = 0
    file_count = 0
    dir_count = 0
    
    print_message(f"[CT*] Analyzing target directory structure...", Fore.CYAN)
    for root, dirs, files in os.walk(target):
        dir_count += len(dirs)
        for file in files:
            file_count += 1
            try:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
            except (OSError, IOError) as e:
                print_message(f"[CT*] WARNING: Cannot access file {file}: {e}", Fore.YELLOW)
    
    print_message(f"[CT*] Initial analysis complete:", Fore.CYAN)
    print_message(f"[CT*] - Total files: {file_count:,}", Fore.CYAN)
    print_message(f"[CT*] - Total directories: {dir_count:,}", Fore.CYAN)
    print_message(f"[CT*] - Total size: {total_size / (1024*1024):.2f} MB", Fore.CYAN)
    
    # Define comprehensive excluded patterns for files that shouldn't be scanned
    exclude_patterns = [
        # System & Temp files
        '*.log', '*.tmp', '*.cache', '*.DS_Store', '*.swp', '*.swo',
        '*~', '*.bak', '*.orig', 'Thumbs.db', 'ehthumbs.db',
        
        # Version Control
        '.git/', '.svn/', '.hg/', '.bzr/', 'CVS/',
        
        # Node.js & JavaScript
        'node_modules/', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
        '.npm/', '.yarn/', 'dist/', 'coverage/', '.nyc_output/', '.coverage',
        
        # Python
        '__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python', 'pip-log.txt',
        'pip-delete-this-directory.txt', '.tox/', '.coverage', '.pytest_cache/',
        '.venv/', 'venv/', 'env/', 'ENV/', 'env.bak/', 'venv.bak/',
        
        # Java & Android
        '*.class', '*.jar', '*.war', '*.ear', 'target/', '.gradle/', 'build/',
        'gradle/', 'gradlew', 'gradlew.bat', '.idea/', '*.iml', '*.iws', '*.ipr',
        
        # iOS & Swift
        'Pods/', 'DerivedData/', 'build/', '.build/', 'xcuserdata/',
        '*.xcworkspace/', '*.xcodeproj/', '*.dSYM/', '*.framework/',
        '*.xcarchive/', 'fastlane/report.xml', 'fastlane/Preview.html',
        'fastlane/screenshots/', 'fastlane/test_output/',
        
        # React Native specific
        'ios/build/', 'android/build/', 'android/.gradle/', 'android/app/build/',
        'metro.config.js', 'react-native.config.js',
        
        # .NET & C#
        'bin/', 'obj/', '*.dll', '*.exe', '*.pdb', 'packages/',
        '*.user', '*.suo', '*.cache', '*.docstates',
        
        # Ruby
        'vendor/', '.bundle/', 'Gemfile.lock',
        
        # Go
        'vendor/', 'go.sum',
        
        # Rust
        'target/', 'Cargo.lock',
        
        # Database
        '*.sqlite', '*.db', '*.sqlite3',
        
        # Archives & Binaries
        '*.zip', '*.tar', '*.gz', '*.rar', '*.7z', '*.dmg', '*.iso',
        '*.so', '*.dylib', '*.a', '*.lib',
        
        # IDE & Editor files
        '.vscode/', '.settings/', '.project', '.classpath',
        '*.sublime-project', '*.sublime-workspace',
        
        # Documentation & Images (large files)
        '*.pdf', '*.doc', '*.docx', '*.ppt', '*.pptx',
        '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
        '*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv',
        '*.mp3', '*.wav', '*.flac', '*.aac',
        
        # Logs & Debug
        'logs/', '*.log.*', 'debug.log', 'error.log', 'access.log',
        'npm-debug.log', 'yarn-debug.log', 'yarn-error.log'
    ]
    
    print_message(f"[CT*] Exclusion patterns applied: {len(exclude_patterns)} patterns", Fore.CYAN)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, f"{project}.zip")
        
        def should_exclude(path):
            """Check if a file/directory should be excluded from zip"""
            for pattern in exclude_patterns:
                if pattern.endswith('/'):
                    if pattern[:-1] in path.split(os.sep):
                        return True
                else:
                    if pattern.startswith('*.'):
                        if path.endswith(pattern[1:]):
                            return True
                    elif pattern in os.path.basename(path):
                        return True
            return False
        
        # Create a custom zip with exclusions
        print_message(f"[CT*] Creating ZIP file: {zip_path}", Fore.CYAN)
        print_message(f"[CT*] Temporary directory: {temp_dir}", Fore.BLUE)
        
        excluded_files = 0
        excluded_dirs = 0
        included_files = 0
        excluded_size = 0
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                print_message(f"[CT*] ZIP file opened successfully for writing", Fore.CYAN)
                
                for root, dirs, files in os.walk(target):
                    # Log current directory being processed
                    current_dir = os.path.relpath(root, target)
                    if current_dir != '.':
                        print_message(f"[CT*] Processing directory: {current_dir}", Fore.BLUE)
                    
                    # Check and exclude directories
                    original_dirs = dirs.copy()
                    dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                    
                    # Count excluded directories
                    for excluded_dir in set(original_dirs) - set(dirs):
                        excluded_dirs += 1
                        excluded_dir_path = os.path.join(root, excluded_dir)
                        print_message(f"[CT*] EXCLUDED DIR: {os.path.relpath(excluded_dir_path, target)}", Fore.YELLOW)
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not should_exclude(file_path):
                            try:
                                # Calculate relative path from target
                                arcname = os.path.relpath(file_path, target)
                                file_size = os.path.getsize(file_path)
                                zipf.write(file_path, arcname)
                                included_files += 1
                                
                                # Log large files
                                if file_size > 10 * 1024 * 1024:  # 10MB+
                                    print_message(f"[CT*] LARGE FILE: {arcname} ({file_size / (1024*1024):.2f} MB)", Fore.MAGENTA)
                                    
                            except (OSError, IOError) as e:
                                print_message(f"[CT*] ERROR: Cannot add file {file}: {e}", Fore.RED)
                        else:
                            excluded_files += 1
                            try:
                                excluded_size += os.path.getsize(file_path)
                                excluded_file_rel = os.path.relpath(file_path, target)
                                if excluded_files <= 10:  # Log first 10 excluded files
                                    print_message(f"[CT*] EXCLUDED FILE: {excluded_file_rel}", Fore.YELLOW)
                                elif excluded_files == 11:
                                    print_message(f"[CT*] ... (more excluded files not shown)", Fore.YELLOW)
                            except (OSError, IOError):
                                pass
                
                print_message(f"[CT*] ZIP file closed successfully", Fore.CYAN)
                
        except Exception as e:
            print_message(f"[CT*] ERROR: Failed to create ZIP file: {e}", Fore.RED)
            print_message(f"[CT*] Exception type: {type(e).__name__}", Fore.RED)
            import traceback
            print_message(f"[CT*] Traceback: {traceback.format_exc()}", Fore.RED)
            sys.exit(ERROR_EXIT_CODE)
        
        print_message(f"[CT*] ZIP creation completed with exclusions applied", Fore.GREEN)
        print_message(f"[CT*] Files included: {included_files:,}", Fore.GREEN)
        print_message(f"[CT*] Files excluded: {excluded_files:,}", Fore.YELLOW)
        print_message(f"[CT*] Directories excluded: {excluded_dirs:,}", Fore.YELLOW)
        print_message(f"[CT*] Excluded data size: {excluded_size / (1024*1024):.2f} MB", Fore.YELLOW)

        # Check file size before upload
        zip_size = os.path.getsize(zip_path)
        zip_size_mb = zip_size / (1024*1024)
        print_message(f"[CT*] ZIP file size: {zip_size_mb:.2f} MB", Fore.CYAN)
        
        # Define file size limits and warnings
        OPTIMAL_SIZE_MB = 50       # Optimal size for fast upload
        LARGE_SIZE_MB = 100        # Large but manageable  
        WARNING_SIZE_MB = 500      # Warning threshold
        MAXIMUM_SIZE_MB = 2048     # Hard limit (2GB)
        
        print_message(f"[CT*] ===== FILE SIZE ANALYSIS =====", Fore.CYAN)
        print_message(f"[CT*] ZIP file size: {zip_size_mb:.2f} MB", Fore.CYAN)
        
        # Categorize file size and provide appropriate messaging
        if zip_size_mb > MAXIMUM_SIZE_MB:
            print_message(f"[CT*] ❌ CRITICAL: File size exceeds maximum limit!", Fore.RED)
            print_message(f"[CT*] Maximum allowed: {MAXIMUM_SIZE_MB} MB, Your file: {zip_size_mb:.2f} MB", Fore.RED)
            print_message(f"[CT*] This upload will definitely fail. Please reduce file size.", Fore.RED)
            print_message(f"[CT*] REQUIRED ACTIONS:", Fore.RED)
            print_message(f"[CT*] 1. Remove large binary files, logs, and build artifacts", Fore.RED)
            print_message(f"[CT*] 2. Split the project into smaller modules", Fore.RED)
            print_message(f"[CT*] 3. Use .gitignore patterns to exclude unnecessary files", Fore.RED)
            sys.exit(ERROR_EXIT_CODE)
            
        elif zip_size_mb > WARNING_SIZE_MB:
            print_message(f"[CT*] ⚠️  WARNING: Very large file size ({zip_size_mb:.2f} MB)", Fore.YELLOW)
            print_message(f"[CT*] This is approaching the practical limit ({MAXIMUM_SIZE_MB} MB)", Fore.YELLOW)
            print_message(f"[CT*] Upload may take 10-30 minutes or fail due to network issues", Fore.YELLOW)
            print_message(f"[CT*] RECOMMENDATIONS:", Fore.YELLOW)
            print_message(f"[CT*] - Consider excluding more files to get below {WARNING_SIZE_MB} MB", Fore.YELLOW)
            print_message(f"[CT*] - Ensure stable network connection", Fore.YELLOW)
            print_message(f"[CT*] - Split project if possible", Fore.YELLOW)
            
        elif zip_size_mb > LARGE_SIZE_MB:
            print_message(f"[CT*] 📦 Large file size detected ({zip_size_mb:.2f} MB)", Fore.MAGENTA)
            print_message(f"[CT*] Upload will take 3-10 minutes depending on connection", Fore.MAGENTA)
            print_message(f"[CT*] Using optimized upload method for large files", Fore.MAGENTA)
            
        elif zip_size_mb > OPTIMAL_SIZE_MB:
            print_message(f"[CT*] 📊 Good file size ({zip_size_mb:.2f} MB)", Fore.GREEN)
            print_message(f"[CT*] Upload should complete in 1-3 minutes", Fore.GREEN)
            
        else:
            print_message(f"[CT*] ✅ Optimal file size ({zip_size_mb:.2f} MB)", Fore.GREEN)
            print_message(f"[CT*] Upload should complete in under 1 minute", Fore.GREEN)
        
        # Show size category info
        print_message(f"[CT*] File Size Categories:", Fore.BLUE)
        print_message(f"[CT*] • Optimal: 0-{OPTIMAL_SIZE_MB} MB (fastest)", Fore.BLUE)
        print_message(f"[CT*] • Good: {OPTIMAL_SIZE_MB}-{LARGE_SIZE_MB} MB (fast)", Fore.BLUE)
        print_message(f"[CT*] • Large: {LARGE_SIZE_MB}-{WARNING_SIZE_MB} MB (slower)", Fore.BLUE)
        print_message(f"[CT*] • Warning: {WARNING_SIZE_MB}-{MAXIMUM_SIZE_MB} MB (risky)", Fore.BLUE)
        print_message(f"[CT*] • Maximum: {MAXIMUM_SIZE_MB} MB (hard limit)", Fore.BLUE)

        # Upload the zipped directory and start the scan
        upload_url = f"{base_url}/api/scan/start"
        print_message(f"[CT*] Upload URL: {upload_url}", Fore.BLUE)
        
        # Dynamic timeout based on ZIP file size
        zip_size_mb = zip_size / (1024 * 1024)
        
        # Calculate VERY generous timeouts based on file size
        # Designed for slow connections (1 MB/s minimum)
        if zip_size_mb <= OPTIMAL_SIZE_MB:  # <= 50MB
            connection_timeout = 60    # 1 minute
            read_timeout = 900         # 15 minutes
        elif zip_size_mb <= LARGE_SIZE_MB:  # <= 100MB
            connection_timeout = 120   # 2 minutes
            read_timeout = 1800        # 30 minutes
        elif zip_size_mb <= WARNING_SIZE_MB:  # <= 500MB
            connection_timeout = 300   # 5 minutes  
            read_timeout = 5400        # 90 minutes (1.5 hours)
        else:  # Very large files
            connection_timeout = 600   # 10 minutes
            read_timeout = 10800       # 3 hours
        
        timeout = (connection_timeout, read_timeout)
        print_message(f"[CT*] Dynamic timeout for {zip_size_mb:.2f}MB: Connection={connection_timeout}s, Read={read_timeout}s", Fore.BLUE)
        
        # Log network environment details
        import socket
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            print_message(f"[CT*] Local IP: {local_ip}", Fore.BLUE)
        except:
            print_message(f"[CT*] Could not determine local IP", Fore.BLUE)
        
        # Check proxy settings
        proxy_info = {}
        for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            if os.getenv(proxy_var):
                proxy_info[proxy_var] = os.getenv(proxy_var)
        
        if proxy_info:
            print_message(f"[CT*] Proxy settings detected:", Fore.BLUE)
            for key, value in proxy_info.items():
                print_message(f"[CT*] - {key}: {value}", Fore.BLUE)
        else:
            print_message(f"[CT*] No proxy settings detected", Fore.BLUE)
        
        try:
            # Create a session with proper configuration for large uploads
            print_message(f"[CT*] Creating HTTP session...", Fore.CYAN)
            session = requests.Session()
            
            print_message(f"[CT*] Configuring retry mechanism...", Fore.CYAN)
            adapter = requests.adapters.HTTPAdapter(
                max_retries=requests.packages.urllib3.util.retry.Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504]
                )
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            print_message(f"[CT*] HTTP session configured successfully", Fore.CYAN)
            
            print_message(f"[CT*] Opening ZIP file for upload...", Fore.CYAN)
            
            # Check if we can read the file properly first
            try:
                with open(zip_path, 'rb') as test_f:
                    # Try to read first few bytes to ensure file is accessible
                    test_f.read(1024)
                    print_message(f"[CT*] ZIP file accessibility test passed", Fore.CYAN)
            except Exception as e:
                print_message(f"[CT*] ERROR: Cannot read ZIP file: {e}", Fore.RED)
                raise
            
            # For very large files, use a different approach to avoid memory issues
            if zip_size_mb > LARGE_SIZE_MB:  # 100MB+ files
                print_message(f"[CT*] Large file detected ({zip_size_mb:.2f} MB), using streaming upload", Fore.YELLOW)
                
                # Use custom file-like object with progress tracking
                class ProgressTrackingFileReader:
                    def __init__(self, file_path, chunk_size=65536):  # 64KB chunks for better progress
                        self.file_path = file_path
                        self.chunk_size = chunk_size
                        self._file = None
                        self.file_size = os.path.getsize(file_path)
                        self.bytes_read = 0
                        self.last_progress_time = 0
                        self.start_time = None
                        
                    def __enter__(self):
                        self._file = open(self.file_path, 'rb')
                        self.start_time = time.time()
                        print_message(f"[CT*] 📤 Starting upload of {self.file_size / (1024*1024):.2f} MB file...", Fore.CYAN)
                        return self
                        
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        if self._file:
                            self._file.close()
                        if self.start_time:
                            total_time = time.time() - self.start_time
                            speed_mbps = (self.bytes_read / (1024*1024)) / max(total_time, 1)
                            print_message(f"[CT*] ✅ Upload completed in {total_time:.1f}s at {speed_mbps:.2f} MB/s", Fore.GREEN)
                    
                    def read(self, size=-1):
                        if size == -1:
                            data = self._file.read()
                        else:
                            data = self._file.read(size)
                        
                        # Update progress tracking
                        self.bytes_read += len(data)
                        current_time = time.time()
                        
                        # Show progress every 5 seconds or every 10% of file
                        if (current_time - self.last_progress_time >= 5.0) or (self.bytes_read % (self.file_size // 10) < len(data)):
                            progress_percent = (self.bytes_read / self.file_size) * 100
                            elapsed_time = current_time - self.start_time if self.start_time else 0
                            
                            if elapsed_time > 0:
                                speed_mbps = (self.bytes_read / (1024*1024)) / elapsed_time
                                remaining_bytes = self.file_size - self.bytes_read
                                eta_seconds = remaining_bytes / (self.bytes_read / elapsed_time) if self.bytes_read > 0 else 0
                                
                                print_message(f"[CT*] 📊 Upload Progress: {progress_percent:.1f}% "
                                             f"({self.bytes_read / (1024*1024):.1f}/{self.file_size / (1024*1024):.1f} MB) "
                                             f"Speed: {speed_mbps:.2f} MB/s "
                                             f"ETA: {eta_seconds:.0f}s", Fore.BLUE)
                            
                            self.last_progress_time = current_time
                        
                        return data
                    
                    def seek(self, offset, whence=0):
                        result = self._file.seek(offset, whence)
                        # Update bytes_read based on current position
                        self.bytes_read = self._file.tell()
                        return result
                    
                    def tell(self):
                        return self._file.tell()
                
                with ProgressTrackingFileReader(zip_path) as chunked_file:
                    files = {'upfile': (f"{project}.zip", chunked_file, 'application/zip')}
                    data = {
                        'project': project,
                        'scan_source': 'CLI'
                    }
                    if branch:
                        data['branch'] = branch
                        print_message(f"[CT*] Branch parameter: {branch}", Fore.BLUE)
                    if policy_id:
                        data['policy_id'] = policy_id
                        print_message(f"[CT*] Policy ID parameter: {policy_id}", Fore.BLUE)

                    print_message(f"[CT*] Upload parameters: {data}", Fore.BLUE)
                    
                    # Disable connection pooling for large uploads to avoid issues
                    upload_headers = headers.copy()
                    upload_headers['Connection'] = 'close'
                    upload_headers['Expect'] = '100-continue'  # Help with large uploads
                    print_message(f"[CT*] Upload headers configured for large file", Fore.BLUE)
                    
                    print_message(f"[CT*] Starting chunked file upload... This may take several minutes for large projects.", Fore.CYAN)
                    print_message(f"[CT*] Upload started at: {get_timestamp()}", Fore.CYAN)
                    
                    # Attempt upload with chunked reading
                    response = session.post(
                        upload_url, 
                        headers=upload_headers, 
                        files=files, 
                        data=data, 
                        timeout=timeout,
                        stream=False
                    )
            else:
                # Standard upload for smaller files
                print_message(f"[CT*] Small file detected ({zip_size_mb:.2f} MB), using standard upload", Fore.CYAN)
                
                with open(zip_path, 'rb') as f:
                    print_message(f"[CT*] 📤 Starting upload of {zip_size_mb:.2f} MB file...", Fore.CYAN)
                    upload_start_time = time.time()
                    
                    files = {'upfile': (f"{project}.zip", f, 'application/zip')}
                    data = {
                        'project': project,
                        'scan_source': 'CLI'
                    }
                    if branch:
                        data['branch'] = branch
                        print_message(f"[CT*] Branch parameter: {branch}", Fore.BLUE)
                    if policy_id:
                        data['policy_id'] = policy_id
                        print_message(f"[CT*] Policy ID parameter: {policy_id}", Fore.BLUE)

                    print_message(f"[CT*] Upload parameters: {data}", Fore.BLUE)
                    
                    # Configure headers
                    upload_headers = headers.copy()
                    upload_headers['Connection'] = 'close'
                    print_message(f"[CT*] Upload headers configured", Fore.BLUE)
                    
                    print_message(f"[CT*] Starting file upload...", Fore.CYAN)
                    print_message(f"[CT*] Upload started at: {get_timestamp()}", Fore.CYAN)
                    
                    # Attempt upload
                    response = session.post(
                        upload_url, 
                        headers=upload_headers, 
                        files=files, 
                        data=data, 
                        timeout=timeout,
                        stream=False  # Don't stream response for file uploads
                    )
                
                    upload_end_time = time.time()
                    upload_duration = upload_end_time - upload_start_time
                    upload_speed = (zip_size_mb) / max(upload_duration, 1)
                    
                    print_message(f"[CT*] ✅ Upload completed in {upload_duration:.1f}s at {upload_speed:.2f} MB/s", Fore.GREEN)
                    print_message(f"[CT*] Upload finished at: {get_timestamp()}", Fore.CYAN)
                    print_message(f"[CT*] Response status code: {response.status_code}", Fore.CYAN)
                    print_message(f"[CT*] Response headers: {dict(response.headers)}", Fore.BLUE)
                
        except requests.exceptions.ConnectionError as e:
            print_message(f"[CT*] ===== CONNECTION ERROR DETAILS =====", Fore.RED)
            print_message(f"[CT*] Upload failed due to connection error. This usually happens with very large projects.", Fore.RED)
            print_message(f"[CT*] Error timestamp: {get_timestamp()}", Fore.RED)
            print_message(f"[CT*] Error type: {type(e).__name__}", Fore.RED)
            print_message(f"[CT*] Error details: {str(e)}", Fore.RED)
            
            # Get more detailed error information
            if hasattr(e, 'args') and e.args:
                print_message(f"[CT*] Error args: {e.args}", Fore.RED)
            
            # Check for specific error patterns
            error_str = str(e).lower()
            if 'errno 22' in error_str or 'invalid argument' in error_str:
                print_message(f"[CT*] SPECIFIC ERROR: OSError(22) - Invalid argument detected", Fore.RED)
                print_message(f"[CT*] This is the EXACT error from StackOverflow references!", Fore.RED)
                print_message(f"[CT*] Common causes for this error:", Fore.RED)
                print_message(f"[CT*] - File too large for system memory handling", Fore.RED)
                print_message(f"[CT*] - Windows file path/handle limitations", Fore.RED)
                print_message(f"[CT*] - File descriptor exhaustion", Fore.RED)
                print_message(f"[CT*] - Network buffer overflow with large files", Fore.RED)
                
                # Additional Windows-specific checks
                if platform.system() == 'Windows':
                    print_message(f"[CT*] Windows detected - this confirms StackOverflow pattern", Fore.RED)
                    print_message(f"[CT*] Try using the chunked upload method for files >200MB", Fore.YELLOW)
                    
            elif 'connection aborted' in error_str:
                print_message(f"[CT*] SPECIFIC ERROR: Connection was aborted during upload", Fore.RED)
                print_message(f"[CT*] This may be due to proxy timeout or network instability", Fore.RED)
            elif 'timeout' in error_str:
                print_message(f"[CT*] SPECIFIC ERROR: Timeout occurred during upload", Fore.RED)
            
            print_message(f"[CT*] ===== DIAGNOSTIC INFORMATION =====", Fore.YELLOW)
            print_message(f"[CT*] ZIP file size: {zip_size_mb:.2f} MB", Fore.YELLOW)
            print_message(f"[CT*] Files included: {included_files:,}", Fore.YELLOW)
            print_message(f"[CT*] Upload URL: {upload_url}", Fore.YELLOW)
            
            import traceback
            print_message(f"[CT*] Full traceback:", Fore.RED)
            print_message(f"{traceback.format_exc()}", Fore.RED)
            
            print_message(f"[CT*] ===== SUGGESTIONS =====", Fore.YELLOW)
            print_message(f"[CT*] 1. Try reducing project size by excluding unnecessary files", Fore.YELLOW)
            print_message(f"[CT*] 2. Check your network connection and proxy settings", Fore.YELLOW)
            print_message(f"[CT*] 3. Contact support if the problem persists", Fore.YELLOW)
            print_message(f"[CT*] 4. Share this detailed log with support team for faster resolution", Fore.YELLOW)
            sys.exit(ERROR_EXIT_CODE)
            
        except requests.exceptions.Timeout as e:
            print_message(f"[CT*] ===== TIMEOUT ERROR DETAILS =====", Fore.RED)
            print_message(f"[CT*] Upload timed out. The project might be too large.", Fore.RED)
            print_message(f"[CT*] Error timestamp: {get_timestamp()}", Fore.RED)
            print_message(f"[CT*] Error type: {type(e).__name__}", Fore.RED)
            print_message(f"[CT*] Error details: {str(e)}", Fore.RED)
            print_message(f"[CT*] Timeout settings were: connection={timeout[0]}s, read={timeout[1]}s", Fore.RED)
            print_message(f"[CT*] ZIP file size: {zip_size_mb:.2f} MB", Fore.RED)
            
            import traceback
            print_message(f"[CT*] Full traceback:", Fore.RED)
            print_message(f"{traceback.format_exc()}", Fore.RED)
            sys.exit(ERROR_EXIT_CODE)
            
        except Exception as e:
            print_message(f"[CT*] ===== UNEXPECTED ERROR DETAILS =====", Fore.RED)
            print_message(f"[CT*] Unexpected error during upload", Fore.RED)
            print_message(f"[CT*] Error timestamp: {get_timestamp()}", Fore.RED)
            print_message(f"[CT*] Error type: {type(e).__name__}", Fore.RED)
            print_message(f"[CT*] Error details: {str(e)}", Fore.RED)
            
            import traceback
            print_message(f"[CT*] Full traceback:", Fore.RED)
            print_message(f"{traceback.format_exc()}", Fore.RED)
            sys.exit(ERROR_EXIT_CODE)

        print_message(f"[CT*] ===== UPLOAD RESPONSE ANALYSIS =====", Fore.CYAN)
        print_message(f"[CT*] Response status code: {response.status_code}", Fore.CYAN)
        
        try:
            response_json = response.json()
            print_message(f"[CT*] Response JSON: {response_json}", Fore.BLUE)
        except Exception as json_error:
            print_message(f"[CT*] Failed to parse response as JSON: {json_error}", Fore.YELLOW)
            print_message(f"[CT*] Raw response text: {response.text}", Fore.YELLOW)
            response_json = {}
        
        if response.status_code == 200 and not response_json.get("error", True):
            scan_id = response_json.get('scan_id')
            print_message(f"[CT*] ===== UPLOAD SUCCESS =====", Fore.GREEN)
            print_message(f"[CT*] Scan started successfully for project '{project}'", Fore.GREEN)
            print_message(f"[CT*] Scan ID: {scan_id}", Fore.GREEN)
            print_message(f"[CT*] Upload completed successfully at: {get_timestamp()}", Fore.GREEN)
        else:
            print_message(f"[CT*] ===== UPLOAD FAILED =====", Fore.RED)
            print_message(f"[CT*] Scan initiation failed", Fore.RED)
            print_message(f"[CT*] Status code: {response.status_code}", Fore.RED)
            print_message(f"[CT*] Response text: {response.text}", Fore.RED)
            if response_json:
                print_message(f"[CT*] Error in response: {response_json.get('error', 'Unknown')}", Fore.RED)
            print_message(f"[CT*] Failed at: {get_timestamp()}", Fore.RED)
            sys.exit(FAILURE_EXIT_CODE)

    # Start the scan status polling in the main thread
    poll_scan_status(scan_id)

if __name__ == "__main__":
    scan()
