## Purpose

Validates that published packages work correctly after release, ensuring end users can install and use the application as expected.

### Requirement: Installation is validated with uv tool
The system SHALL validate that the package can be installed using `uv tool install`.

#### Scenario: uv tool installation succeeds
- **WHEN** package is published to PyPI
- **THEN** `uv tool install mouseflow` succeeds
- **THEN** installation completes without errors
- **THEN** package is available in PATH

#### Scenario: uv tool installation works in clean environment
- **WHEN** package is installed via uv tool
- **WHEN** environment has no prior Python packages
- **THEN** installation succeeds
- **THEN** all dependencies are resolved correctly

### Requirement: Installation is validated with pip
The system SHALL validate that the package can be installed using `pip install`.

#### Scenario: pip installation succeeds
- **WHEN** package is published to PyPI
- **THEN** `pip install mouseflow` succeeds
- **THEN** installation completes without errors
- **THEN** package is available in PATH

#### Scenario: pip installation works in virtual environment
- **WHEN** package is installed via pip
- **WHEN** installation is in a fresh virtual environment
- **THEN** installation succeeds
- **THEN** all dependencies are installed correctly

### Requirement: Version command is validated
The system SHALL validate that the `--version` command works correctly after installation.

#### Scenario: Version command executes
- **WHEN** package is installed
- **WHEN** user runs `mouseflow --version`
- **THEN** command executes without errors
- **THEN** output matches released version
- **THEN** exit code is zero

#### Scenario: Version matches release tag
- **WHEN** release workflow completes
- **THEN** version reported by `--version` matches Git tag
- **THEN** version follows semantic versioning format

### Requirement: Help command is validated
The system SHALL validate that the `--help` command works correctly after installation.

#### Scenario: Help command executes
- **WHEN** package is installed
- **WHEN** user runs `mouseflow --help`
- **THEN** command executes without errors
- **THEN** help text is displayed
- **THEN** exit code is zero

#### Scenario: Help shows all commands
- **WHEN** user runs `mouseflow --help`
- **THEN** help shows all available subcommands
- **THEN** help shows command descriptions
- **THEN** help is readable and useful

### Requirement: Basic functionality is validated
The system SHALL validate that basic CLI commands work after installation.

#### Scenario: Status command works
- **WHEN** package is installed
- **WHEN** user runs `mouseflow status`
- **THEN** command executes (may fail if daemon not running, but should not crash)
- **THEN** error message is clear if daemon not running
- **THEN** command does not raise unhandled exceptions

#### Scenario: Devices command works
- **WHEN** package is installed
- **WHEN** user runs `mouseflow devices`
- **THEN** command executes (may fail if daemon not running, but should not crash)
- **THEN** error message is clear if daemon not running
- **THEN** command does not raise unhandled exceptions

### Requirement: Validation runs automatically
The system SHALL run validation automatically after release publication.

#### Scenario: Validation is part of release workflow
- **WHEN** release workflow publishes to PyPI
- **THEN** validation workflow is triggered
- **THEN** validation runs in clean environment
- **THEN** validation results are reported

#### Scenario: Validation failure is reported
- **WHEN** validation fails
- **THEN** failure is clearly reported
- **THEN** error details are available
- **THEN** maintainers are notified

### Requirement: Validation uses clean environments
The system SHALL validate installation in clean, isolated environments.

#### Scenario: Validation uses fresh environment
- **WHEN** validation runs
- **THEN** environment has no prior MouseFlow installation
- **THEN** environment has no cached packages
- **THEN** validation tests real user experience

#### Scenario: Validation tests multiple installers
- **WHEN** validation runs
- **THEN** both uv tool and pip are tested
- **THEN** each installer is tested independently
- **THEN** results are reported separately
