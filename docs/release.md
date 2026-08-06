# Release Process

This document describes the release process for MouseFlow, including versioning strategy, distribution, and the automated release workflow.

## Versioning Strategy

MouseFlow follows [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

Version format: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.2.3`)

## Distribution Strategy

MouseFlow is distributed through:

1. **PyPI** - Primary distribution channel (`pip install mouseflow`)
2. **GitHub Releases** - Source archives and release notes
3. **Source** - Direct installation from repository

### PyPI

The package is published to PyPI using Trusted Publishing (OIDC), which provides secure, token-free authentication from GitHub Actions.

### GitHub Releases

Each release creates a GitHub release with:
- Auto-generated release notes from commits
- Source distribution (sdist) attached
- Wheel distribution attached

## Release Workflow

The release workflow is defined in `.github/workflows/release.yml` and is triggered automatically when a version tag is pushed.

### Workflow Stages

#### 1. Quality Checks

Three parallel jobs validate code quality:

- **lint** - Runs `ruff format --check` and `ruff check`
- **typecheck** - Runs `mypy`
- **test** - Runs `pytest`

**Responsibility:** Ensure code meets quality standards before building.

**Failure behavior:** If any check fails, the workflow stops and no artifacts are built.

#### 2. Build

Builds distribution packages after quality checks pass.

- Creates source distribution (sdist)
- Creates wheel distribution (pure Python, platform-independent)
- Uploads distributions as workflow artifact

**Responsibility:** Produce distributable packages.

**Failure behavior:** If build fails, the workflow stops.

#### 3. Publish

Uploads distributions to PyPI.

- Downloads distributions artifact
- Uses PyPI Trusted Publishing (OIDC) for authentication
- No secrets or tokens required

**Responsibility:** Make package available on PyPI.

**Failure behavior:** If publish fails, GitHub release is not created. Error is logged for investigation.

#### 4. GitHub Release

Creates a GitHub release with notes and artifacts.

- Downloads distributions artifact
- Creates release using `gh release create`
- Auto-generates release notes from commits since last tag
- Attaches sdist and wheel to release

**Responsibility:** Provide release notes and downloadable artifacts.

#### 5. Validation

Validates the published package works correctly.

- Tests installation with `pip` in a fresh virtual environment
- Tests installation with `uv tool` in a clean environment
- Validates `mouseflow --version` works
- Validates `mouseflow --help` works
- Validates `mouseflow status` fails gracefully (daemon not running)
- Validates `mouseflow devices` fails gracefully (daemon not running)

**Responsibility:** Ensure end users can install and use the package.

**Failure behavior:** Validation failure is reported but does not roll back the release. Maintainers are notified to investigate.

## How to Create a New Release

### Prerequisites

- PyPI account configured with Trusted Publishing for the GitHub repository
- All changes merged to `main` branch
- CI is green on `main`

### Steps

1. **Update version in `pyproject.toml`:**

   ```toml
   version = "1.2.3"
   ```

2. **Update `CHANGELOG.md`:**

   Add an entry for the new version following the template.

3. **Commit changes:**

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 1.2.3"
   ```

4. **Create and push tag:**

   ```bash
   git tag v1.2.3
   git push origin main --tags
   ```

5. **Monitor the workflow:**

   Watch the release workflow at: `https://github.com/gtadashii/mouse-flow/actions`

6. **Verify the release:**

   - Check PyPI: `https://pypi.org/project/mouseflow/`
   - Check GitHub release: `https://github.com/gtadashii/mouse-flow/releases`
   - Check validation workflow passed

### Post-Release

- Test installation: `pip install mouseflow` and `uv tool install mouseflow`
- Verify `mouseflow --version` shows correct version
- Update any documentation if needed

## PyPI Trusted Publishing Setup

Trusted Publishing uses OpenID Connect (OIDC) to authenticate GitHub Actions with PyPI without storing secrets.

### One-Time Setup

1. **Create or verify PyPI account:**

   Go to [pypi.org](https://pypi.org) and create an account if needed.

2. **Create a PyPI project:**

   The project will be created automatically on first publish, or you can create it manually.

3. **Configure Trusted Publishing:**

   In PyPI project settings, add a new "Pending publisher":

   - **PyPI project name:** `mouseflow`
   - **OIDC issuer:** `https://token.actions.githubusercontent.com`
   - **Repository owner:** `gtadashii` (or your GitHub username/org)
   - **Repository name:** `mouse-flow`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`

4. **Verify GitHub environment:**

   The workflow uses the `pypi` environment. In GitHub repository settings:

   - Go to Settings > Environments
   - Create environment named `pypi`
   - Optionally add protection rules (required reviewers, wait timers)

### How It Works

1. GitHub Actions requests an OIDC token from GitHub's token service
2. The token includes claims about the repository, workflow, and environment
3. PyPI verifies the token against the configured trusted publisher
4. If claims match, PyPI grants upload permission
5. `twine` uploads the package using the temporary credentials

No API tokens or secrets are stored anywhere.

## Rollback Strategy

If a release has issues:

1. **Delete the Git tag:**

   ```bash
   git tag -d v1.2.3
   git push origin :refs/tags/v1.2.3
   ```

2. **Delete the GitHub release** (from GitHub UI or `gh release delete`)

3. **Yank the PyPI release:**

   Go to PyPI project settings and yank the release, or:

   ```bash
   pip install yank
   yank mouseflow 1.2.3
   ```

4. **Fix issues and create a new release** with an incremented version number.

## Release Readiness Checklist

Before creating a release, verify all items below.

### Documentation

- [ ] README is up to date
- [ ] Installation instructions work
- [ ] Configuration guide is accurate
- [ ] CLI reference is complete
- [ ] Troubleshooting section covers common issues
- [ ] All documentation examples work correctly
- [ ] Cross-links between documents are valid

### Code Quality

- [ ] Linter passes: `make lint`
- [ ] Formatter passes: `make format`
- [ ] Type checker passes: `make typecheck`
- [ ] No linting warnings remain

### Tests

- [ ] All unit tests pass: `make test`
- [ ] Test coverage is adequate
- [ ] Integration tests pass (if applicable)

### Package

- [ ] Package builds locally: `python -m build`
- [ ] Both sdist and wheel are created
- [ ] Package installs from local build
- [ ] `mouseflow` command works after installation
- [ ] Package excludes tests and development files

### Version

- [ ] Version follows SemVer
- [ ] Version in `pyproject.toml` is updated
- [ ] Version matches the intended tag
- [ ] Version is consistent across all files

### CHANGELOG

- [ ] CHANGELOG includes entry for this release
- [ ] CHANGELOG lists all user-facing changes
- [ ] CHANGELOG follows consistent format
- [ ] CHANGELOG is organized by category (Added, Changed, Fixed, etc.)

### License

- [ ] LICENSE file is present
- [ ] LICENSE file is complete
- [ ] `pyproject.toml` references the license
- [ ] README mentions the license

### CI

- [ ] CI is green on `main` branch
- [ ] All CI checks pass (lint, typecheck, test)
- [ ] No CI warnings remain
