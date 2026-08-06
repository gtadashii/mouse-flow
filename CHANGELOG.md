# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-08-06

### Added

- Release automation with GitHub Actions workflow
- Post-publication validation for PyPI packages
- Configuration guide (`docs/configuration.md`)
- CLI reference (`docs/cli-reference.md`)
- Troubleshooting guide (`docs/troubleshooting.md`)
- Release process documentation (`docs/release.md`)
- Release readiness checklist

### Changed

- Updated README with PyPI installation instructions
- Added complete package metadata for PyPI distribution
- Configured package for `pip` and `uv tool` installation

## [0.1.0] - 2026-01-01

### Added

- Per-application mouse actions for Wayland compositors
- Daemon for monitoring mouse events
- Configuration via YAML files
- CLI interface with `start`, `status`, `devices`, and `config` commands
- Support for button events (BTN_SIDE, BTN_EXTRA, BTN_FORWARD)
- Support for horizontal wheel (REL_HWHEEL)
- Gesture recognition (UP, DOWN, LEFT, RIGHT)
- Keyboard action type
- Command action type
- Sway IPC integration for window identification
- Systemd user service support

[Unreleased]: https://github.com/gtadashii/mouse-flow/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/gtadashii/mouse-flow/releases/tag/v1.0.0
[0.1.0]: https://github.com/gtadashii/mouse-flow/releases/tag/v0.1.0
