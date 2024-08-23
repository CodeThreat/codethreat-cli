
# CodeThreat CLI

CodeThreat CLI is a command-line interface tool designed to enhance application security by integrating with the CodeThreat platform. It allows developers and security professionals to analyze codebases, detect vulnerabilities, and generate security reports directly from the command line.

## Table of Contents

1.  [Introduction](#introduction)
3.  [Installation](#installation)
4.  [Usage](#usage)
    -   [Authentication](#authentication)
    -   [Scanning Projects](#scanning-projects)
5.  [Configuration](#configuration)
7.  [Contributing](#contributing)
8.  [License](#license)
9.  [Support](#support)

## Introduction

The CodeThreat CLI is part of the CodeThreat application security platform, designed to streamline the security analysis process for developers and security teams. By leveraging this tool, users can automate security scans, integrate with CI/CD pipelines, and receive actionable insights to improve the security posture of their applications.

## Installation

### Installing from Releases

To install the CodeThreat CLI, download the appropriate version for your operating system from the [Releases page](https://github.com/CodeThreat/codethreat-cli/releases).

1.  **Download** the latest release for your operating system.
2.  **Extract** the contents of the downloaded archive.
3.  **Move** the executable (`codethreat-cli` or `codethreat-cli.exe`) to a directory included in your system's `PATH`. (Optional)

## Usage

Once installed, the CodeThreat CLI can be invoked using the `codethreat-cli` command. Below are some common usage scenarios.

### Authentication

Before performing any scans, you must authenticate with the CodeThreat platform.

-   **Login**:

    `codethreat-cli auth login --org <your-organization> --token <your-api-token>` 
    
-   **Remove authentication**:

    `codethreat-cli auth remove` 
    

### Scanning Projects

To scan a project for security vulnerabilities, use the `scan` command.

-   **Basic Scan**:
    
    `codethreat-cli scan --target /path/to/your/project --project <project-name>` 
    

 ## Contributing

We welcome contributions from the community! If you would like to contribute:

1.  Fork the repository
2.  Create a new branch (`git checkout -b feature/your-feature-name`)
3.  Make your changes
4.  Commit your changes (`git commit -m 'Add some feature'`)
5.  Push to the branch (`git push origin feature/your-feature-name`)
6.  Create a pull request

Please refer to our [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

If you encounter any issues or have any questions, please feel free to [open an issue](https://github.com/CodeThreat/codethreat-cli/issues) or contact our support team at support@codethreat.com.