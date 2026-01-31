# CI/CD Pipeline Documentation

This document describes the complete CI/CD pipeline for the Coding Platform Crawler project.

## Overview

The project uses a **multi-layered quality gate system** to ensure production-ready code:

1. **Local Git Hooks** - Run on every commit/push
1. **GitHub Actions** - Run on every push to main/develop and PRs
1. **Release Pipeline** - Automated releases on version tags

## Local Development Pipeline

### Git Hooks (Pre-commit)

Installed via `pre-commit install`, these hooks run automatically:

#### Pre-commit Hook (runs on `git commit`)

**Code Formatting:**

- `black` - Python code formatter (line length: 100)
- `isort` - Import statement sorter
- `pretty-format-yaml` - YAML formatter
- `mdformat` - Markdown formatter

**Code Quality:**

- `flake8` - Python linting (max complexity: 10)
- `mypy` - Static type checking
- `pydocstyle` - Docstring validation (Google style)

**Security:**

- `bandit` - Security vulnerability scanner
- `detect-private-key` - Credential detection

**General Checks:**

- `trailing-whitespace` - Remove trailing whitespace
- `end-of-file-fixer` - Ensure files end with newline
- `check-yaml` - YAML syntax validation
- `check-json` - JSON syntax validation
- `check-added-large-files` - Prevent large files (>1MB)
- `check-merge-conflict` - Detect merge conflict markers
- `check-case-conflict` - Detect case-insensitive filename conflicts
- `mixed-line-ending` - Enforce LF line endings

#### Commit-msg Hook (runs on `git commit`)

**Commit Message Validation:**

- `conventional-pre-commit` - Enforces Conventional Commits format

Valid commit types:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Test additions or modifications
- `chore:` - Build process or auxiliary tool changes
- `ci:` - CI/CD configuration changes

Example valid commit messages:

```
feat: add batch download command
fix: handle rate limit errors correctly
docs: update README with installation instructions
test: add unit tests for problem entity
```

#### Pre-push Hook (runs on `git push`)

**Test Execution:**

- `pytest` - Runs all tests with verbose output
- Fails fast on first test failure
- Prevents pushing broken code

### Setup Instructions

**Automated setup (recommended):**

```bash
# Linux/macOS
./scripts/setup-dev.sh

# Windows PowerShell
.\scripts\setup-dev.ps1

# Windows Command Prompt
scripts\setup-dev.bat
```

**Manual setup:**

```bash
# Install package and dependencies
pip install -e ".[dev]"
pip install pre-commit

# Install git hooks
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg
```

### Running Checks Manually

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run mypy --all-files

# Run tests
pytest
pytest --cov=src/crawler --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/
```

## GitHub Actions Pipeline

### Workflow: Pre-commit Checks

**File:** `.github/workflows/pre-commit.yml`

**Triggers:**

- Push to `main` or `develop` branches
- Pull requests to any branch

**Jobs:**

1. Checkout code
1. Set up Python 3.9
1. Install pre-commit
1. Cache pre-commit environments
1. Run all pre-commit hooks

**Purpose:** Ensures all code quality checks pass before merging

### Workflow: Test Suite

**File:** `.github/workflows/test.yml`

**Triggers:**

- Push to `main` or `develop` branches
- Pull requests to any branch
- Scheduled nightly runs (for property-based tests)

**Jobs:**

#### Unit Tests

- **Matrix:** Python 3.8, 3.9, 3.10, 3.11
- **Steps:**
  1. Checkout code
  1. Set up Python
  1. Install dependencies
  1. Run pytest with coverage
  1. Upload coverage to Codecov

#### Integration Tests

- **Depends on:** Unit tests passing
- **Steps:**
  1. Run integration tests
  1. Verify platform client functionality

**Purpose:** Ensures code works across Python versions and all tests pass

### Workflow: Release

**File:** `.github/workflows/release.yml`

**Triggers:**

- Push of version tags (e.g., `v2.0.0`)

**Jobs:**

1. Run full test suite
1. Build Python package
1. Create GitHub release
1. Publish to PyPI (if configured)

**Purpose:** Automated release process

## Quality Gates Summary

| Stage              | When         | What                               | Blocks  |
| ------------------ | ------------ | ---------------------------------- | ------- |
| **Pre-commit**     | `git commit` | Format, lint, type check, security | Commit  |
| **Commit-msg**     | `git commit` | Validate commit message format     | Commit  |
| **Pre-push**       | `git push`   | Run all tests                      | Push    |
| **GitHub Actions** | Push/PR      | All checks + multi-version tests   | Merge   |
| **Release**        | Tag push     | Full suite + build + publish       | Release |

## Bypassing Hooks (Emergency Only)

```bash
# Skip pre-commit hooks (NOT RECOMMENDED)
git commit --no-verify -m "emergency fix"

# Skip pre-push hooks (NOT RECOMMENDED)
git push --no-verify
```

⚠️ **Warning:** Bypassing hooks should only be done in emergencies. The CI will still catch issues.

## Troubleshooting

### Pre-commit hook fails

```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clear cache and retry
pre-commit clean
pre-commit run --all-files
```

### Tests fail on push

```bash
# Run tests locally to debug
pytest -v --tb=short

# Run specific test
pytest tests/unit/test_problem.py -v

# Run with debugging
pytest --pdb
```

### Commit message rejected

```bash
# Check commit message format
# Must be: type(scope): description

# Good examples:
git commit -m "feat: add new feature"
git commit -m "fix(cli): handle edge case"
git commit -m "docs: update README"

# Bad examples:
git commit -m "updated stuff"  # ❌ No type
git commit -m "Fix bug"        # ❌ Type not lowercase
```

## Best Practices

1. **Commit Early, Commit Often** - Small, focused commits
1. **Write Descriptive Messages** - Follow Conventional Commits
1. **Run Tests Locally** - Don't rely solely on CI
1. **Keep Hooks Updated** - Run `pre-commit autoupdate` monthly
1. **Review Hook Output** - Don't ignore warnings
1. **Fix Issues Immediately** - Don't accumulate technical debt

## Configuration Files

- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `.github/workflows/*.yml` - GitHub Actions workflows
- `pyproject.toml` - Tool configurations (black, isort, pytest, etc.)
- `pytest.ini` - Pytest configuration
- `.coveragerc` - Coverage configuration

## Metrics & Coverage

**Current Coverage:** 73%
**Target Coverage:** >80%

View coverage report:

```bash
pytest --cov=src/crawler --cov-report=html
open htmlcov/index.html
```

## Continuous Improvement

The CI/CD pipeline is continuously improved. Suggestions welcome via issues or PRs!
