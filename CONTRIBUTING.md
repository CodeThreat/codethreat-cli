
# Contributing to CodeThreat CLI

First off, thank you for considering contributing to CodeThreat CLI! Your involvement helps us make this tool even better. The following is a set of guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it to understand what actions will and will not be tolerated.

## How to Contribute

### Reporting Issues

If you encounter a bug or have a question, please open an issue on GitHub. When reporting an issue, provide as much detail as possible:

-   A clear title and description.
-   Steps to reproduce the issue.
-   Expected and actual results.
-   System information (OS, Python version, etc.).

### Suggesting Enhancements

We welcome ideas and suggestions! To propose a new feature:

1.  Search the existing issues and discussions to see if the idea has already been discussed.
2.  If not, open a new issue describing your idea.
3.  Explain your proposal clearly, including potential use cases, benefits, and possible implementation strategies.

### Submitting Pull Requests

We appreciate your efforts to contribute to the codebase. Here’s how you can submit a pull request (PR):

1.  Fork the repository and create your branch from `master`.
2.  Make your changes in a new branch (e.g., `feature/add-new-command`).
3.  Ensure that your code adheres to our style guides and passes all tests.
4.  Commit your changes following the conventional commit guidelines.
5.  Push your branch to your fork and submit a pull request.
6.  In your pull request, describe what changes were made and why they are necessary.

## Development Process

### Setting Up the Environment

To set up a development environment, follow these steps:

1.  **Clone the repository:**
    
    `git clone https://github.com/CodeThreat/codethreat-cli.git
    cd codethreat-cli` 
    
2.  **Create a virtual environment:**
       
    `python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate` 
    
3.  **Install dependencies:**
    
    `pip install -r requirements.txt` 
    

### Running Tests

We use `pytest` for testing. Ensure all tests pass before submitting your PR:

1.  **Run all tests:**
    
    `pytest tests/` 
    
2.  **Check test coverage:**
    
    `pytest --cov=cli tests/` 
    

## Style Guides

### Git Commit Messages

We use Conventional Commits for our commit messages. This helps in automatically generating changelogs and versioning. Here’s a summary of the format:

-   **feat**: A new feature (e.g., `feat: add scan command`)
-   **fix**: A bug fix (e.g., `fix: resolve auth token issue`)
-   **docs**: Documentation only changes (e.g., `docs: update README`)
-   **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
-   **refactor**: A code change that neither fixes a bug nor adds a feature
-   **test**: Adding missing tests or correcting existing tests
-   **chore**: Changes to the build process or auxiliary tools and libraries (e.g., `chore: update dependencies`)

**Example commit message:**

feat: add authentication support

- Added login and logout commands
- Improved token management` 

## License

By contributing, you agree that your contributions will be licensed under the MIT License. See the LICENSE file for more details.