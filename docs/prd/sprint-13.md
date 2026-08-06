# PRD — Sprint 13

# Title

Release 1.0

---

# Objective

Deliver MouseFlow 1.0 as the official public release of the project.

This sprint is not just about publishing a package, but delivering a complete experience of installation, documentation, and distribution. The goal is to provide a solid, reproducible, and automated release process that users can trust.

At the end of this sprint, users should be able to:
- Install MouseFlow from PyPI or source
- Follow comprehensive documentation
- Trust that the release process is automated and validated

---

# Problem

MouseFlow is feature-complete for core functionality but lacks the infrastructure needed for a proper public release.

Current gaps:
- No automated release pipeline
- No validation that published packages actually work
- No dedicated documentation for the release process
- No formal checklist to ensure release readiness
- Distribution limited to manual source installation

This sprint addresses these gaps to deliver a production-ready Release 1.0.

---

# User Story

As a Linux user,

I want to install MouseFlow from PyPI using standard tools,

so that I can easily set up and use per-application mouse actions on my Wayland compositor with confidence that the package is properly tested and documented.

---

# Success Criteria

Users can install MouseFlow from PyPI using `pip` or `uv tool`.

Installed packages are validated to work correctly (commands execute successfully).

Release creation is fully automated through Git tags and GitHub Actions.

Version management follows semantic versioning principles.

Complete documentation is available for end users and maintainers.

A formal release readiness checklist ensures quality before publication.

---

# Scope

This sprint includes:

## Distribution Channels

- Source installation (from Git repository);
- PyPI distribution (official Python package repository).

**Note:** AUR (Arch User Repository) packaging is intentionally deferred to a future release to stabilize the official publication process first.

## Release Pipeline

Fully automated release workflow triggered by Git tags:

```
Git Tag (v1.0.0)
    ↓
GitHub Actions
    ↓
Lint (ruff)
    ↓
Type Check (mypy)
    ↓
Tests (pytest)
    ↓
Build (sdist + wheel)
    ↓
Publish to PyPI
    ↓
Create GitHub Release
    ↓
Attach Release Artifacts
```

## Release Validation

Post-publication validation to ensure the released package works:

- Installation test using `uv tool install mouseflow`;
- Installation test using `pip install mouseflow`;
- Validation of `mouseflow --version` command;
- Validation of `mouseflow --help` command;
- Validation of basic functionality.

## Documentation

- Complete README with installation and usage instructions;
- Configuration guide;
- CLI reference;
- Troubleshooting section;
- **Release process documentation** (`docs/release.md`) covering:
  - Distribution strategy;
  - Versioning strategy;
  - Publication workflow;
  - How to create a new release;
  - Responsibilities of each pipeline stage.

## Release Readiness

Formal checklist to validate before publication:

- [ ] Documentation updated;
- [ ] README complete and accurate;
- [ ] CHANGELOG updated;
- [ ] License present and correct;
- [ ] CONTRIBUTING guidelines updated (if needed);
- [ ] CI fully green;
- [ ] Package installable locally;
- [ ] Basic commands working;
- [ ] Version numbering consistent;
- [ ] All tests passing;
- [ ] Linter and type checker passing.

---

# Out of Scope

This sprint does not include:

- AUR (Arch User Repository) packaging (future work);
- Flatpak or Snap packaging (future work);
- Binary distribution (future work);
- Plugin system (future work);
- New application features or functionality.

---

# Functional Requirements

## Package Configuration

The application shall be properly configured as a Python package suitable for PyPI distribution.

This includes:
- Proper `pyproject.toml` configuration;
- Complete package metadata (description, author, license, classifiers);
- Accurate dependency specification;
- Entry points configuration;
- README as long description on PyPI.

---

## Release Automation

The project shall have a fully automated release workflow triggered by Git tags.

The workflow shall:
- Trigger on version tags (e.g., `v1.0.0`);
- Run all quality checks (lint, type check, tests);
- Build distribution packages (sdist and wheel);
- Publish to PyPI;
- Create GitHub release with release notes;
- Attach distribution artifacts to GitHub release.

---

## Release Validation

The project shall validate that published packages work correctly.

Validation shall include:
- Installation via `uv tool install mouseflow`;
- Installation via `pip install mouseflow`;
- Execution of `mouseflow --version`;
- Execution of `mouseflow --help`;
- Basic functionality smoke test.

---

## Version Management

The project shall follow semantic versioning (SemVer) for release numbering.

Version format: `MAJOR.MINOR.PATCH`

- MAJOR: Incompatible API changes;
- MINOR: New functionality (backwards compatible);
- PATCH: Bug fixes (backwards compatible).

---

## Documentation

The project shall have complete documentation for end users and maintainers.

End-user documentation:
- Installation instructions (PyPI and source);
- Configuration guide;
- Usage examples;
- Troubleshooting section;
- CLI reference;
- Systemd service setup.

Maintainer documentation (`docs/release.md`):
- Distribution strategy;
- Versioning strategy;
- Publication workflow;
- How to create a new release;
- Responsibilities of each pipeline stage;
- Release readiness checklist.

---

## Release Notes

Each release shall have release notes describing changes.

Release notes shall include:
- New features;
- Bug fixes;
- Breaking changes;
- Upgrade instructions;
- Known issues.

---

# Non-functional Requirements

The solution should:

- follow Python packaging best practices;
- be fully automated (minimal manual intervention);
- be reproducible (same tag produces same artifacts);
- validate the published package actually works;
- be maintainable and extensible for future distribution channels;
- be easy to understand for contributors and maintainers.

---

# Design Principles

This sprint should prioritize:

- automation over manual processes;
- reproducibility over ad-hoc solutions;
- validation over assumption;
- user experience over implementation details;
- maintainability over cleverness;
- standard practices over custom solutions.

---

# Responsibilities

The release infrastructure is responsible for:

- building distribution packages;
- automating the entire release workflow;
- validating published packages;
- managing version numbers;
- generating release notes;
- publishing to distribution channels;
- maintaining release documentation.

It is not responsible for:

- implementing application features;
- fixing bugs (though releases may include bug fixes);
- user support (though documentation helps).

---

# Expected Behavior

A maintainer decides to create Release 1.0.0.

The maintainer ensures the release readiness checklist is complete.

The maintainer creates a Git tag `v1.0.0`.

GitHub Actions automatically triggers the release workflow.

All quality checks run (lint, type check, tests).

Distribution packages are built (sdist and wheel).

Packages are published to PyPI.

A GitHub release is created with auto-generated release notes.

Distribution artifacts are attached to the GitHub release.

Post-publication validation runs automatically.

Validation confirms packages can be installed and basic commands work.

Users can install the new version from PyPI with confidence.

---

# Acceptance Criteria

The sprint is complete when:

- package can be built successfully;
- package can be installed from PyPI via `pip` and `uv tool`;
- installed packages pass validation tests;
- release workflow is fully automated (triggered by Git tag);
- version management follows SemVer;
- end-user documentation is complete;
- maintainer documentation (`docs/release.md`) is complete;
- release readiness checklist is defined and used;
- release process is documented and reproducible.

---

# Risks

Potential challenges include:

- PyPI publishing requirements and API tokens;
- GitHub Actions workflow complexity;
- Post-publication validation reliability;
- Documentation completeness and accuracy;
- Version management conflicts;
- Ensuring published packages actually work for end users.

Mitigations:

- Test release workflow with test PyPI first;
- Validate installation in clean environments;
- Document the entire process thoroughly;
- Use established tools and best practices;
- Start with minimal distribution channels (PyPI only).

---

# Future Work

Future sprints may include:

- AUR packaging for Arch Linux users;
- Flatpak or Snap packaging for universal Linux distribution;
- Binary distribution for users without Python;
- Plugin system for extensibility;
- GUI interface for configuration;
- Additional validation tests;
- Automated dependency updates.
