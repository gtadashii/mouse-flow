## Purpose

Automates the entire release process from Git tag to published package, ensuring releases are reproducible, consistent, and require minimal manual intervention.

### Requirement: Release workflow triggers on Git tags
The system SHALL automatically trigger the release workflow when a version tag is pushed.

#### Scenario: Tag triggers release
- **WHEN** maintainer pushes tag matching pattern `v*.*.*`
- **THEN** release workflow is automatically triggered
- **THEN** workflow extracts version number from tag
- **THEN** workflow does not trigger on non-version tags

#### Scenario: Workflow validates tag format
- **WHEN** tag does not match semantic versioning pattern
- **THEN** workflow fails with clear error message
- **THEN** no release artifacts are created

### Requirement: Quality checks run before release
The system SHALL run all quality checks before building release artifacts.

#### Scenario: Linter runs
- **WHEN** release workflow executes
- **THEN** linter (ruff) runs on all source code
- **THEN** workflow fails if linter finds issues
- **THEN** no artifacts are built if linter fails

#### Scenario: Type checker runs
- **WHEN** release workflow executes
- **THEN** type checker (mypy) runs on all source code
- **THEN** workflow fails if type checker finds issues
- **THEN** no artifacts are built if type checker fails

#### Scenario: Tests run
- **WHEN** release workflow executes
- **THEN** full test suite runs
- **THEN** workflow fails if any test fails
- **THEN** no artifacts are built if tests fail

### Requirement: Distribution packages are built
The system SHALL build both source distribution and wheel packages.

#### Scenario: Source distribution is built
- **WHEN** quality checks pass
- **THEN** source distribution (sdist) is created
- **THEN** sdist contains all necessary files
- **THEN** sdist is stored as workflow artifact

#### Scenario: Wheel is built
- **WHEN** quality checks pass
- **THEN** wheel distribution is created
- **THEN** wheel is platform-independent
- **THEN** wheel is stored as workflow artifact

### Requirement: Packages are published to PyPI
The system SHALL automatically publish packages to PyPI after successful build.

#### Scenario: Packages published to PyPI
- **WHEN** packages are built successfully
- **THEN** packages are uploaded to PyPI
- **THEN** upload uses secure authentication
- **THEN** PyPI project is updated with new version

#### Scenario: PyPI publish failure is handled
- **WHEN** PyPI upload fails
- **THEN** workflow fails with clear error message
- **THEN** GitHub release is not created
- **THEN** error is logged for investigation

### Requirement: GitHub release is created
The system SHALL create a GitHub release with release notes and artifacts.

#### Scenario: GitHub release is created
- **WHEN** packages are published to PyPI
- **THEN** GitHub release is created for the tag
- **THEN** release includes auto-generated release notes
- **THEN** release notes include commits since last release

#### Scenario: Artifacts are attached
- **WHEN** GitHub release is created
- **THEN** source distribution is attached to release
- **THEN** wheel distribution is attached to release
- **THEN** artifacts are downloadable from release page

### Requirement: Release is reproducible
The system SHALL produce identical artifacts for the same source code.

#### Scenario: Same tag produces same artifacts
- **WHEN** release workflow runs multiple times for same tag
- **THEN** artifacts have same content
- **THEN** artifacts have same checksums
- **THEN** build is deterministic

### Requirement: Workflow provides clear feedback
The system SHALL provide clear status updates throughout the release process.

#### Scenario: Workflow status is visible
- **WHEN** release workflow is running
- **THEN** each step shows clear status
- **THEN** failures show detailed error messages
- **THEN** success shows summary of actions taken

#### Scenario: Release summary is provided
- **WHEN** release workflow completes
- **THEN** summary shows version released
- **THEN** summary shows PyPI URL
- **THEN** summary shows GitHub release URL
