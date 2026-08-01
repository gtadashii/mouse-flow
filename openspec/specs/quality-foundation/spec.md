## Purpose

Establishes automated code quality checks that run before commits and on every pull request, ensuring consistent code style, type safety, and test coverage across the project.

## Requirements

### Requirement: Automatic code formatting
The system SHALL automatically format all Python source code according to a consistent style.

#### Scenario: Code is formatted on save
- **WHEN** a developer saves a Python file
- **THEN** the file is automatically formatted according to the project's formatting rules

#### Scenario: Formatting check in CI
- **WHEN** a pull request is opened or updated
- **THEN** the CI pipeline verifies all code is properly formatted

### Requirement: Code linting
The system SHALL validate code for common issues and style violations.

#### Scenario: Linting check in CI
- **WHEN** a pull request is opened or updated
- **THEN** the CI pipeline runs linting and reports any violations

#### Scenario: Linting prevents commit
- **WHEN** a developer attempts to commit code with linting violations
- **THEN** the commit is rejected until violations are fixed

### Requirement: Static type checking
The system SHALL verify type annotations are correct and consistent.

#### Scenario: Type checking in CI
- **WHEN** a pull request is opened or updated
- **THEN** the CI pipeline verifies all type annotations are correct

#### Scenario: Type checking prevents commit
- **WHEN** a developer attempts to commit code with type errors
- **THEN** the commit is rejected until type errors are fixed

### Requirement: Unit test execution
The system SHALL execute all unit tests and report results.

#### Scenario: Tests run in CI
- **WHEN** a pull request is opened or updated
- **THEN** the CI pipeline executes all unit tests and reports pass/fail status

#### Scenario: Tests prevent commit on failure
- **WHEN** a developer attempts to commit code that breaks tests
- **THEN** the commit is rejected until tests pass

### Requirement: Pre-commit hooks
The system SHALL run quality checks locally before commits are created.

#### Scenario: Pre-commit runs on git commit
- **WHEN** a developer runs `git commit`
- **THEN** formatting, linting, and type checking run automatically on staged files

#### Scenario: Pre-commit blocks invalid commits
- **WHEN** any quality check fails during pre-commit
- **THEN** the commit is blocked and the developer receives feedback on what needs to be fixed

### Requirement: Continuous integration pipeline
The system SHALL execute all quality checks on every pull request.

#### Scenario: CI runs on pull request
- **WHEN** a pull request is opened or updated
- **THEN** GitHub Actions executes formatting, linting, type checking, and tests

#### Scenario: CI reports status
- **WHEN** all quality checks pass
- **THEN** the pull request shows a passing status

#### Scenario: CI blocks on failure
- **WHEN** any quality check fails
- **THEN** the pull request shows a failing status and cannot be merged

### Requirement: Single command validation
The system SHALL provide a single command to run all quality checks locally.

#### Scenario: Run all checks with one command
- **WHEN** a developer runs the validation command
- **THEN** formatting, linting, type checking, and tests all execute in sequence

#### Scenario: Command reports overall status
- **WHEN** all checks pass
- **THEN** the command exits with success status

#### Scenario: Command reports failures
- **WHEN** any check fails
- **THEN** the command exits with failure status and displays which checks failed
