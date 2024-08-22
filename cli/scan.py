import os
import requests
import click
import shutil
import tempfile
import sys
import time
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
    project_check_url = f"{base_url}/api/project?key={project}"
    response = requests.get(project_check_url, headers=headers)

    if response.status_code == 200:
        print_message(f"[CT*] Project '{project}' exists. Proceeding with scan.", Fore.CYAN)
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
    print_message(f"[CT*] Zipping the target directory: {target}", Fore.CYAN)
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, f"{project}.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', target)

        # Upload the zipped directory and start the scan
        upload_url = f"{base_url}/api/scan/start"
        with open(zip_path, 'rb') as f:
            files = {'upfile': (f"{project}.zip", f, 'application/zip')}
            data = {
                'project': project,
            }
            if branch:
                data['branch'] = branch
            if policy_id:
                data['policy_id'] = policy_id

            response = requests.post(upload_url, headers=headers, files=files, data=data)

        if response.status_code == 200 and not response.json().get("error", True):
            scan_id = response.json().get('scan_id')
            print_message(f"[CT*] Scan started successfully for project '{project}'. Scan ID: {scan_id}", Fore.GREEN)
        else:
            print_message(f"[CT*] Scan initiation failed: {response.status_code} - {response.text}", Fore.RED)
            sys.exit(FAILURE_EXIT_CODE)

    # Start the scan status polling in the main thread
    poll_scan_status(scan_id)

if __name__ == "__main__":
    scan()
