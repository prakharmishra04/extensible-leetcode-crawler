# CI/CD Setup Guide

This document explains how to set up and use the CI/CD pipelines for the Coding Platform Crawler.

## Overview

The project uses GitHub Actions for continuous integration and deployment with three main workflows:

1. **test.yml** - Runs tests on every push and PR
1. **release.yml** - Builds and publishes releases when tags are pushed
1. **pre-commit.yml** - Runs code quality checks

## Workflows

### 1. Test Workflow (`test.yml`)

**Triggers:**

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Scheduled nightly runs (for property-based tests)

**Jobs:**

#### Unit Tests

- Runs on Python 3.8, 3.9, 3.10, 3.11
- Executes all unit tests with coverage
- Uploads coverage to Codecov

#### Integration Tests

- Runs after unit tests pass
- Tests platform clients with mocked HTTP
- Tests repository with temporary filesystem

#### E2E Tests

- Runs on PRs and main branch merges
- Tests full CLI workflows
- Requires LeetCode credentials (optional)

#### Property-Based Tests (Nightly)

- Runs daily at 2 AM UTC
- Extended iterations for thorough testing
- Uses Hypothesis library

#### Code Quality

- Black formatting check
- Flake8 linting
- MyPy type checking

#### Coverage Report

- Generates HTML coverage report
- Enforces 80% minimum coverage
- Comments coverage on PRs

### 2. Release Workflow (`release.yml`)

**Triggers:**

- Push of version tags (e.g., `v2.0.0`)

**Jobs:**

#### Test

- Runs full test suite before release
- Ensures 80% coverage

#### Build

- Builds source and wheel distributions
- Validates with twine
- Uploads artifacts

#### Publish to PyPI

- Publishes to PyPI using API token
- Skips if version already exists

#### Create GitHub Release

- Creates GitHub release with changelog
- Attaches distribution files
- Extracts notes from CHANGELOG.md

### 3. Pre-commit Workflow (`pre-commit.yml`)

**Triggers:**

- Pull requests
- Push to `main` or `develop` branches

**Checks:**

- Runs all pre-commit hooks
- Ensures code quality standards

## Setup Instructions

### 1. Enable GitHub Actions

GitHub Actions should be enabled by default. Verify in:

- Repository Settings → Actions → General
- Ensure "Allow all actions and reusable workflows" is selected

### 2. Configure Secrets

Add the following secrets in Repository Settings → Secrets and variables → Actions:

#### Required for E2E Tests (Optional)

```
LEETCODE_SESSION_TOKEN - Your LeetCode session cookie
LEETCODE_USERNAME - Your LeetCode username
```

#### Required for PyPI Publishing

```
PYPI_API_TOKEN - Your PyPI API token
```

**To get PyPI API token:**

1. Go to https://pypi.org/manage/account/token/
1. Create a new API token
1. Scope: "Entire account" or specific project
1. Copy the token (starts with `pypi-`)
1. Add to GitHub secrets

### 3. Configure Codecov (Optional)

For coverage reporting:

1. Go to https://codecov.io/
1. Sign in with GitHub
1. Add your repository
1. Copy the upload token
1. Add as `CODECOV_TOKEN` secret (optional, works without it for public repos)

### 4. Set Up Pre-commit Locally

Install pre-commit hooks for local development:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### 5. Configure Branch Protection

Recommended branch protection rules for `main`:

1. Go to Settings → Branches → Add rule
1. Branch name pattern: `main`
1. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - Select: `Unit Tests`, `Integration Tests`, `Code Quality Checks`
   - ✅ Require branches to be up to date before merging
   - ✅ Require conversation resolution before merging

## Usage

### Running Tests Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src/crawler --cov-report=html

# Run specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest -m property              # Property-based tests only

# Run with verbose output
pytest -v

# Run pre-commit checks
pre-commit run --all-files
```

### Creating a Release

1. **Update version** in `pyproject.toml` and `src/crawler/__init__.py`

1. **Update CHANGELOG.md** with release notes:

   ```markdown
   ## [2.0.0] - 2026-01-31

   ### Added
   - New feature X
   - New feature Y

   ### Changed
   - Updated Z

   ### Fixed
   - Bug fix A
   ```

1. **Commit changes:**

   ```bash
   git add pyproject.toml src/crawler/__init__.py CHANGELOG.md
   git commit -m "chore: Bump version to 2.0.0"
   git push
   ```

1. **Create and push tag:**

   ```bash
   git tag -a v2.0.0 -m "Release version 2.0.0"
   git push origin v2.0.0
   ```

1. **Monitor release workflow:**

   - Go to Actions tab
   - Watch the release workflow
   - Verify PyPI publication
   - Check GitHub release creation

### Monitoring Workflows

**View workflow runs:**

- Go to repository → Actions tab
- Click on a workflow to see runs
- Click on a run to see job details
- Click on a job to see step logs

**Troubleshooting failed workflows:**

1. Check the error message in logs
1. Verify secrets are configured correctly
1. Ensure dependencies are up to date
1. Run tests locally to reproduce
1. Check for API rate limits or service issues

## Workflow Status Badges

Add these badges to your README.md:

```markdown
[![Tests](https://github.com/prakharmishra04/extensible-leetcode-crawler/workflows/Tests/badge.svg)](https://github.com/prakharmishra04/extensible-leetcode-crawler/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/prakharmishra04/extensible-leetcode-crawler/branch/main/graph/badge.svg)](https://codecov.io/gh/prakharmishra04/extensible-leetcode-crawler)
[![PyPI version](https://badge.fury.io/py/coding-platform-crawler.svg)](https://badge.fury.io/py/coding-platform-crawler)
[![Python versions](https://img.shields.io/pypi/pyversions/coding-platform-crawler.svg)](https://pypi.org/project/coding-platform-crawler/)
```

## Best Practices

### For Contributors

1. **Always run pre-commit before pushing:**

   ```bash
   pre-commit run --all-files
   ```

1. **Write tests for new features:**

   - Unit tests for business logic
   - Integration tests for external dependencies
   - E2E tests for CLI commands

1. **Maintain test coverage:**

   - Aim for >80% overall coverage
   - 100% for critical domain logic

1. **Follow conventional commits:**

   ```
   feat: Add new feature
   fix: Fix bug
   docs: Update documentation
   test: Add tests
   chore: Update dependencies
   ```

### For Maintainers

1. **Review PR checks before merging:**

   - All tests pass
   - Coverage meets threshold
   - Code quality checks pass

1. **Use semantic versioning:**

   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

1. **Keep dependencies updated:**

   - Review Dependabot PRs
   - Test thoroughly before merging

1. **Monitor workflow performance:**

   - Optimize slow tests
   - Cache dependencies
   - Parallelize when possible

## Troubleshooting

### Common Issues

**Issue: Tests fail on CI but pass locally**

- Solution: Ensure same Python version, check environment variables

**Issue: Coverage drops below threshold**

- Solution: Add tests for new code, remove dead code

**Issue: PyPI publish fails**

- Solution: Check API token, verify version doesn't exist, check package name

**Issue: Pre-commit hooks fail**

- Solution: Run `pre-commit run --all-files` locally and fix issues

**Issue: E2E tests fail**

- Solution: Check if credentials are set, verify LeetCode API is accessible

### Getting Help

- Check workflow logs in Actions tab
- Review this setup guide
- Check GitHub Actions documentation
- Open an issue with workflow run link

## Maintenance

### Regular Tasks

**Weekly:**

- Review failed workflow runs
- Check coverage trends
- Update dependencies if needed

**Monthly:**

- Review and update CI/CD configuration
- Check for GitHub Actions updates
- Audit secrets and tokens

**Per Release:**

- Update CHANGELOG.md
- Bump version numbers
- Create and push tag
- Verify PyPI publication
- Test installation from PyPI

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Codecov Documentation](https://docs.codecov.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Semantic Versioning](https://semver.org/)
