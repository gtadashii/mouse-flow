## Context

MouseFlow is a Python application with existing CI/CD infrastructure (GitHub Actions for lint, type check, and tests). The project uses `pyproject.toml` for package configuration and `uv` for dependency management. The application is currently installable from source but not from PyPI.

Current state:
- GitHub Actions workflow exists for CI (lint, type check, tests)
- `pyproject.toml` has basic package configuration
- No release automation
- No post-publication validation
- README has basic usage instructions but not comprehensive installation guide

Constraints:
- Must use GitHub Actions for automation (existing infrastructure)
- Must follow Python packaging best practices
- Must support both `pip` and `uv tool` installation
- Must validate published packages actually work
- No changes to application code

## Goals / Non-Goals

**Goals:**
- Configure package for PyPI distribution with complete metadata
- Automate entire release process via Git tags
- Validate published packages work correctly
- Provide comprehensive documentation for users and maintainers
- Establish release readiness checklist
- Keep implementation simple and maintainable

**Non-Goals:**
- AUR or other distribution channels (future work)
- Binary distribution (future work)
- Complex release orchestration (keep simple)
- Changes to application functionality
- Automated version bumping (manual for now)

## Decisions

### 1. Release Trigger: Git Tags

**Decision:** Use Git tags (pattern `v*.*.*`) to trigger release workflow.

**Rationale:**
- Standard practice for Python packages
- Simple and explicit (maintainer controls when to release)
- Integrates naturally with GitHub releases
- No additional tooling needed

**Alternatives considered:**
- Manual workflow dispatch: More steps, error-prone
- Automated version bumping: Adds complexity, not needed for first release
- Branch-based releases: Less explicit, harder to manage

**Trade-offs:**
- Requires manual tag creation (acceptable for now)
- Version must be updated in code before tagging (documented in release process)

### 2. Build Tool: python-build

**Decision:** Use `python -m build` for creating distributions.

**Rationale:**
- Official Python packaging tool
- Simple and well-documented
- Creates both sdist and wheel
- No external dependencies beyond stdlib

**Alternatives considered:**
- `setuptools` directly: More complex, lower-level
- `flit`: Additional dependency, not needed
- `poetry`: Heavyweight, overkill for this project

**Trade-offs:**
- Basic functionality only (sufficient for our needs)
- No advanced features like dynamic versioning (not needed)

### 3. PyPI Publishing: twine with Trusted Publishing

**Decision:** Use `twine` with PyPI Trusted Publishing (OIDC).

**Rationale:**
- Official Python packaging tool
- Trusted Publishing is more secure than API tokens
- No secrets to manage in GitHub
- Standard practice for GitHub Actions

**Alternatives considered:**
- API token in secrets: Less secure, requires secret management
- `poetry publish`: Additional dependency
- Direct API calls: More complex, error-prone

**Trade-offs:**
- Requires PyPI account setup (one-time)
- Trusted Publishing requires PyPI configuration (documented in release process)

### 4. Release Validation: Separate Workflow Job

**Decision:** Run validation as a separate job after PyPI publish.

**Rationale:**
- Validates actual published package (not local build)
- Tests in clean environment (real user experience)
- Can test multiple installation methods
- Clear separation of concerns

**Alternatives considered:**
- Validate local build only: Doesn't catch PyPI-specific issues
- Validate in same job: Less clear, harder to debug
- Manual validation: Error-prone, not reproducible

**Trade-offs:**
- Adds time to release process (acceptable for quality)
- Requires waiting for PyPI propagation (usually fast)

### 5. Documentation Strategy: README + docs/

**Decision:** Keep README focused on quick start, use `docs/` for detailed guides.

**Rationale:**
- README is first thing users see (should be concise)
- Detailed guides belong in `docs/` (better organization)
- `docs/release.md` for maintainer documentation
- Standard Python project structure

**Alternatives considered:**
- Everything in README: Too long, hard to navigate
- External documentation site: Overkill for now
- Wiki: Harder to maintain with code

**Trade-offs:**
- Multiple files to maintain (acceptable for clarity)
- Need to keep README and docs in sync (documented in checklist)

### 6. CHANGELOG Management: Manual with Template

**Decision:** Maintain CHANGELOG manually with consistent template.

**Rationale:**
- Simple and explicit
- Maintainer controls what goes in CHANGELOG
- No additional tooling needed
- Standard practice for many projects

**Alternatives considered:**
- Auto-generated from commits: Less curated, may include noise
- `towncrier`: Additional dependency, more complex
- No CHANGELOG: Poor user experience

**Trade-offs:**
- Manual effort required (acceptable for quality)
- Need to remember to update (documented in checklist)

### 7. Version Management: Manual in pyproject.toml

**Decision:** Manually update version in `pyproject.toml` before creating tag.

**Rationale:**
- Simple and explicit
- No additional tooling needed
- Version is source of truth in code
- Standard practice for Python packages

**Alternatives considered:**
- `setuptools-scm`: Automatic from Git tags, adds complexity
- `bumpversion`: Additional dependency
- Dynamic versioning: Overkill for now

**Trade-offs:**
- Manual step required (documented in release process)
- Version must match tag (validated in checklist)

### 8. GitHub Release: Auto-generated with gh CLI

**Decision:** Use `gh release create` with auto-generated release notes.

**Rationale:**
- Built into GitHub CLI
- Auto-generates notes from commits
- Simple and reliable
- No additional configuration needed

**Alternatives considered:**
- Manual release notes: More work, error-prone
- Custom release notes generator: Overkill
- Third-party tools: Additional dependencies

**Trade-offs:**
- Release notes may need manual editing (acceptable)
- Format is GitHub's default (good enough)

## Risks / Trade-offs

### Risk: PyPI Publishing Failures
**Risk:** PyPI upload may fail due to network issues, authentication problems, or PyPI outages.

**Mitigation:**
- Use Trusted Publishing (more reliable than tokens)
- Workflow fails clearly with error message
- Can retry by re-running workflow
- Document troubleshooting in release docs

### Risk: Post-Publication Validation Failures
**Risk:** Published package may not work even though local build works.

**Mitigation:**
- Validate in clean environment (real user experience)
- Test both `pip` and `uv tool` installation
- Validate basic commands work
- Clear error reporting if validation fails

### Risk: Version Mismatch
**Risk:** Version in code may not match Git tag.

**Mitigation:**
- Release readiness checklist includes version validation
- Document version update process clearly
- Validate version in CI before release

### Risk: Documentation Drift
**Risk:** Documentation may become outdated as code changes.

**Mitigation:**
- Release readiness checklist includes documentation review
- Keep documentation close to code (same repository)
- Review documentation in PRs that change behavior

### Trade-off: Manual vs Automated Version Bumping
**Trade-off:** Manual version updates require maintainer action but are simpler and more explicit.

**Mitigation:**
- Document process clearly
- Include in release checklist
- Acceptable for project size and release frequency

### Trade-off: Simple vs Feature-Rich Release Process
**Trade-off:** Keeping release process simple means fewer features but easier maintenance.

**Mitigation:**
- Start simple, add features if needed
- Document process thoroughly
- Can extend later without breaking existing flow

## Migration Plan

### Deployment Steps

1. **Update pyproject.toml**
   - Add complete metadata
   - Configure entry points
   - Add build system configuration

2. **Create release workflow**
   - Add `.github/workflows/release.yml`
   - Configure build, test, publish steps
   - Set up Trusted Publishing with PyPI

3. **Create validation workflow**
   - Add post-publication validation
   - Test installation with pip and uv tool
   - Validate basic commands work

4. **Update documentation**
   - Update README with installation instructions
   - Create `docs/release.md` with release process
   - Add configuration guide and CLI reference

5. **Create release readiness checklist**
   - Document checklist in `docs/release.md`
   - Include all validation steps
   - Make checklist actionable

6. **Test release process**
   - Create test release on Test PyPI
   - Validate entire workflow works
   - Fix any issues before production release

### Rollback Strategy

If release process has issues:
1. Delete Git tag: `git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`
2. Delete GitHub release
3. Delete PyPI release (if possible) or yank it
4. Fix issues in code
5. Create new tag with incremented version

Rollback is straightforward because:
- No database migrations
- No breaking changes to existing code
- Release infrastructure is additive
- Can always fall back to source installation

### Backward Compatibility

- Existing source installation continues to work
- No changes to application code
- No breaking changes to CLI
- New installation methods are additive

## Open Questions

None at this time. All critical decisions have been made:
- Release trigger: Git tags (decided)
- Build tool: python-build (decided)
- PyPI publishing: twine with Trusted Publishing (decided)
- Validation approach: Separate workflow job (decided)
- Documentation structure: README + docs/ (decided)
- CHANGELOG: Manual with template (decided)
- Version management: Manual in pyproject.toml (decided)
- GitHub release: Auto-generated with gh CLI (decided)
