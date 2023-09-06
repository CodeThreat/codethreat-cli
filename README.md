---

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://codethreat.com">
    <img src="https://www.codethreat.com/_next/static/media/ct-logo.0cc6530f.svg" alt="Logo" width="259" height="39">
  </a>

  <h3 align="center">CodeThreat CLI</h3>

</p>
[CodeThreat](https://codethreat.com)

A CLI tool to integrate with CodeThreat services for code scanning.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Scan Command](#scan-command)
  - [Configuration](#configuration)
- [Features](#features)

## Installation

```bash
npm install codethreat-cli -g
```

## Usage

### Scan Command

To scan a project:

```bash
codethreat scan <target_dir> -p <project_name>
```

### Configuration

Set up your CodeThreat configuration:

```bash
codethreat config
```

And follow the prompts to enter your base URL, organization name, and CT access token.

Sure! Here's the "API Reference" section refined for your `README.md`:

---

## API Reference

### `getProject(projectName)`

Fetches a project.

- **projectName**: The name of the project to fetch.

Returns a `Promise` that resolves to the project data.

---

### `createProject(projectName)`

Creates a new project.

- **projectName**: The name of the new project.

Returns a `Promise` that resolves to the created project data.

---

### `startScan(projectName, zipFilePath)`

Starts a scan for a project.

- **projectName**: Name of the project to scan.
- **zipFilePath**: Path to the zipped target directory.

Returns a `Promise` that resolves to the scan status.

---

### `getScanProgress(scanId)`

Fetches the progress of a scan.

- **scanId**: ID of the scan to fetch progress for.

Returns a `Promise` that resolves to the scan progress data.
---
