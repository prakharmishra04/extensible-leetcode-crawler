# Contributing to Coding Platform Crawler

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/coding-platform-crawler.git
cd coding-platform-crawler
```

### 2. Set Up Development Environment

```bash
# Run the automated setup script
./scripts/setup-dev.sh

# Or follow manual setup in README.md
```

This will:

- Install the package in development mode
- Install all development dependencies
- Set up git hooks for code quality
- Run initial checks

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feat/your-feature-name

# Or a bugfix branch
git checkout -b fix/bug-description
```

## Development Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow existing code style and patterns
- Add type hints to all functions
- Write docstrings (Google style)

### 2. Write Tests

```bash
# Add tests for your changes
# Unit tests go in tests/unit/
# Integration tests go in tests/integration/

# Run tests
pytest

# Run with coverage
pytest --cov=src/crawler --cov-report=html
```

**Test Requirements:**

- All new features must have tests
- Bug fixes should include regression tests
- Maintain >80% code coverage

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run all pre-commit checks
pre-commit run --all-files

# Type check
mypy src/

# Security scan
bandit -r src/
```

### 4. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Format: type(scope): description

git commit -m "feat: add support for HackerRank platform"
git commit -m "fix(cli): handle empty problem list"
git commit -m "docs: update installation instructions"
git commit -m "test: add unit tests for Problem entity"
```

**Commit Types:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `test:` - Adding or updating tests
- `chore:` - Build process or tooling
- `ci:` - CI/CD changes

**Commit Message Rules:**

- Use imperative mood ("add" not "added")
- Don't end with a period
- Keep subject line under 50 characters
- Add body for complex changes

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feat/your-feature-name

# Create a Pull Request on GitHub
```

## Code Style Guidelines

### Python Style

- **PEP 8** compliance (enforced by flake8)
- **Line length:** 100 characters
- **Imports:** Sorted with isort
- **Formatting:** Black formatter
- **Type hints:** Required for all functions
- **Docstrings:** Google style, required for public APIs

### Example

```python
from typing import Optional, List


def fetch_problem(
    problem_id: str, platform: str, include_solutions: bool = False
) -> Optional[Problem]:
    """Fetch a problem from the specified platform.

    Args:
        problem_id: The unique identifier for the problem.
        platform: The platform name (e.g., 'leetcode').
        include_solutions: Whether to include community solutions.

    Returns:
        A Problem object if found, None otherwise.

    Raises:
        PlatformError: If the platform is not supported.
        NetworkError: If the request fails.
    """
    # Implementation
    pass
```

### Architecture Principles

- **Clean Architecture** - Maintain layer separation
- **SOLID Principles** - Follow object-oriented best practices
- **Dependency Injection** - Use constructor injection
- **Interface Segregation** - Keep interfaces focused
- **Single Responsibility** - One class, one purpose

## Testing Guidelines

### Test Structure

```python
import pytest
from hypothesis import given, strategies as st


class TestProblem:
    """Tests for Problem entity."""

    def test_create_problem_with_valid_data(self):
        """Test creating a problem with valid data."""
        # Arrange
        data = {...}

        # Act
        problem = Problem(**data)

        # Assert
        assert problem.title == "Two Sum"

    @given(st.text())
    def test_problem_title_property(self, title: str):
        """Property-based test for problem title."""
        # Property-based testing with Hypothesis
        pass
```

### Test Types

1. **Unit Tests** - Test individual components in isolation
1. **Integration Tests** - Test component interactions
1. **Property-based Tests** - Test properties with random inputs (Hypothesis)
1. **E2E Tests** - Test complete workflows (optional)

### Test Coverage

- Aim for >80% coverage
- Focus on critical paths
- Test edge cases and error conditions
- Use mocks for external dependencies

## Adding a New Platform

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed instructions on adding support for new coding platforms.

**Quick checklist:**

1. Create platform client in `src/crawler/infrastructure/platforms/`
1. Implement `PlatformClient` interface
1. Add adapter for data transformation
1. Register in platform factory
1. Add tests (unit + integration)
1. Update documentation

## Documentation

### Update Documentation When:

- Adding new features
- Changing public APIs
- Modifying configuration options
- Adding new platforms
- Changing architecture

### Documentation Files:

- `README.md` - User-facing documentation
- `ARCHITECTURE.md` - Technical architecture
- `DEVELOPMENT.md` - Development guidelines
- `docs/CI_CD.md` - CI/CD pipeline
- Docstrings - In-code documentation

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] No linting errors (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] Commit messages follow Conventional Commits
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. Automated checks must pass (GitHub Actions)
1. Code review by maintainer(s)
1. Address review feedback
1. Approval and merge

## Issue Guidelines

### Reporting Bugs

Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version)
- Error messages/stack traces
- Minimal reproducible example

### Requesting Features

Include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Alternatives considered

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## Questions?

- Open an issue for questions
- Check existing issues and documentation first
- Be patient and respectful

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

## Recognition

Contributors will be recognized in:

- GitHub contributors page
- Release notes (for significant contributions)
- Project documentation (for major features)

Thank you for contributing! 🎉
