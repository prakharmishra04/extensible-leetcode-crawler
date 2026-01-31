# Release Guide

This guide explains how to release new versions of the Coding Platform Crawler.

## Prerequisites

Before you can release to PyPI, you need to set up authentication:

### 1. Create a PyPI Account

1. Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
1. Create an account and verify your email

### 2. Generate PyPI API Token

1. Log in to PyPI
1. Go to [Account Settings](https://pypi.org/manage/account/)
1. Scroll to "API tokens" section
1. Click "Add API token"
1. Give it a name (e.g., "GitHub Actions - extensible-leetcode-crawler")
1. Scope: "Entire account" (for first release) or "Project: coding-platform-crawler" (for subsequent releases)
1. Click "Add token"
1. **IMPORTANT:** Copy the token immediately - you won't see it again!

### 3. Add Token to GitHub Secrets

1. Go to your GitHub repository
1. Navigate to: **Settings** → **Secrets and variables** → **Actions**
1. Click "New repository secret"
1. Name: `PYPI_API_TOKEN`
1. Value: Paste your PyPI token (starts with `pypi-`)
1. Click "Add secret"

## Release Process

### Automated Release (Recommended)

The release process is fully automated via GitHub Actions. When you push a version tag, it will:

1. ✅ Run all tests (must pass with 80%+ coverage)
1. ✅ Build distribution packages (.whl and .tar.gz)
1. ✅ Publish to PyPI
1. ✅ Create GitHub Release with changelog

### Steps to Release

#### 1. Update Version Number

Edit `pyproject.toml`:

```toml
[project]
name = "coding-platform-crawler"
version = "2.1.0"  # Update this
```

#### 2. Update CHANGELOG.md

Add a new section for the version:

```markdown
## [2.1.0] - 2026-02-15

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix A
- Bug fix B

### Changed
- Improvement C
```

#### 3. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 2.1.0"
git push
```

#### 4. Create and Push Tag

```bash
# Create annotated tag
git tag -a v2.1.0 -m "Release v2.1.0 - Brief description"

# Push tag to trigger release workflow
git push origin v2.1.0
```

#### 5. Monitor Release

1. Go to [GitHub Actions](https://github.com/prakharmishra04/extensible-leetcode-crawler/actions)
1. Watch the "Release" workflow
1. If successful, your package will be on PyPI!
1. Check: https://pypi.org/project/coding-platform-crawler/

### Verify Release

After release, verify it works:

```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from PyPI
pip install coding-platform-crawler==2.1.0

# Test the CLI
crawler --version
crawler --help
```

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes

  - Example: v2.0.0 → v3.0.0 (removed old CLI commands)

- **MINOR** (0.X.0): New features, backwards-compatible

  - Example: v2.0.0 → v2.1.0 (added new platform support)

- **PATCH** (0.0.X): Bug fixes, backwards-compatible

  - Example: v2.0.0 → v2.0.1 (fixed download bug)

### Examples

```bash
# Bug fix release
v2.0.0 → v2.0.1

# New feature release
v2.0.1 → v2.1.0

# Breaking change release
v2.1.0 → v3.0.0
```

## Troubleshooting

### Release Workflow Fails

**Tests Fail:**

- Fix the failing tests
- Push fixes to main
- Delete the tag: `git tag -d v2.1.0 && git push origin :refs/tags/v2.1.0`
- Create tag again after fixes

**PyPI Authentication Fails:**

- Verify `PYPI_API_TOKEN` secret is set correctly
- Check token hasn't expired
- Ensure token has correct permissions

**Package Already Exists:**

- PyPI doesn't allow overwriting versions
- Increment version number and create new tag
- Example: v2.1.0 failed → use v2.1.1

### Manual Release (Emergency)

If automated release fails, you can release manually:

```bash
# Build package
python -m pip install build twine
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
# Enter your PyPI username and password when prompted
```

## Release Checklist

Before releasing, ensure:

- [ ] All tests pass locally
- [ ] Code coverage is ≥80%
- [ ] CHANGELOG.md is updated
- [ ] Version number is updated in pyproject.toml
- [ ] Documentation is up to date
- [ ] GitHub Actions workflows are passing
- [ ] PyPI token is configured (first release only)

## Post-Release

After successful release:

1. ✅ Verify package on PyPI: https://pypi.org/project/coding-platform-crawler/
1. ✅ Test installation: `pip install coding-platform-crawler`
1. ✅ Check GitHub Release: https://github.com/prakharmishra04/extensible-leetcode-crawler/releases
1. ✅ Update documentation if needed
1. ✅ Announce release (optional)

## Release Schedule

Suggested release cadence:

- **Patch releases**: As needed for critical bugs
- **Minor releases**: Monthly or when significant features are ready
- **Major releases**: Annually or when breaking changes are necessary

## Questions?

If you encounter issues:

1. Check [GitHub Actions logs](https://github.com/prakharmishra04/extensible-leetcode-crawler/actions)
1. Review [PyPI documentation](https://packaging.python.org/tutorials/packaging-projects/)
1. Open an issue on GitHub
