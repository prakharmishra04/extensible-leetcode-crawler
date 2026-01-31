# Development Guide

## Development Standards

### Code Style

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Document all public methods with Google-style docstrings
- **Line Length**: Maximum 100 characters
- **Imports**: Group by standard library, third-party, local

### Example

```python
from typing import List, Optional


def fetch_problem(problem_id: str, platform: str = "leetcode") -> Optional[Problem]:
    """Fetch a single problem from the specified platform.

    Args:
        problem_id: The problem's unique identifier (e.g., "two-sum")
        platform: Platform name (default: "leetcode")

    Returns:
        Problem entity if found, None otherwise

    Raises:
        ProblemNotFoundException: If problem doesn't exist
        NetworkException: If network request fails
    """
    pass
```

## Testing Standards

### Test Coverage Goals

- **Overall**: >80%
- **Domain Layer**: >95%
- **Application Layer**: >85%
- **Infrastructure Layer**: >70%

### Test Structure

```
tests/
├── unit/                  # Fast, isolated tests
│   ├── domain/           # Entity and value object tests
│   ├── application/      # Use case tests
│   └── infrastructure/   # Adapter and formatter tests
├── integration/          # Tests with mocked HTTP
│   └── platforms/        # Platform client integration tests
└── fixtures/             # Shared test data
    ├── api_responses.py  # Mock API responses
    └── problems.py       # Test problem entities
```

### Writing Tests

**Unit Test Example**:

```python
class TestProblem:
    def test_create_problem_with_valid_data(self):
        problem = Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Given an array...",
            topics=["Array", "Hash Table"],
            constraints=[Constraint("1 <= nums.length <= 10^4")],
            examples=[Example("nums = [2,7]", "[0,1]", "...")],
            hints=[],
            acceptance_rate=56.9,
        )

        assert problem.id == "two-sum"
        assert problem.difficulty.level == "Easy"
        assert len(problem.topics) == 2
```

**Integration Test Example**:

```python
class TestLeetCodeClient:
    def test_fetch_problem_with_mocked_http(self):
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"question": {...}}}
        self.http_client.post.return_value = mock_response

        # Execute
        problem = self.client.fetch_problem("two-sum")

        # Assert
        assert problem.id == "two-sum"
        self.http_client.post.assert_called_once()
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/crawler --cov-report=html

# Specific test file
pytest tests/unit/domain/entities/test_problem.py

# Specific test
pytest tests/unit/domain/entities/test_problem.py::TestProblem::test_create_problem

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Git Workflow

### Commit Message Convention

Follow Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `style`: Code style changes

**Examples**:

```bash
git commit -m "feat(domain): add Constraint value object"
git commit -m "fix(leetcode): handle missing percentiles in submission"
git commit -m "test: add property-based tests for Problem entity"
git commit -m "docs: update README with authentication guide"
```

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes

### Pull Request Process

1. Create feature branch from `develop`
1. Make changes with tests
1. Run full test suite
1. Update documentation
1. Create PR with description
1. Address review comments
1. Merge to `develop`

## Project Structure

### Directory Organization

```
src/crawler/
├── domain/              # Core business logic (no dependencies)
│   ├── entities/       # Problem, Submission, User
│   ├── value_objects/  # Difficulty, Example, Constraint
│   └── exceptions.py   # Domain exceptions
├── application/        # Use cases (depends on domain)
│   ├── interfaces/     # Abstract interfaces
│   └── use_cases/      # Business logic orchestration
├── infrastructure/     # External systems (depends on application)
│   ├── platforms/      # Platform-specific implementations
│   ├── repositories/   # Data persistence
│   ├── formatters/     # Output formatting
│   └── http/           # HTTP client with retry/rate limiting
├── cli/                # User interface (depends on all layers)
│   ├── commands/       # CLI command handlers
│   └── observers/      # Progress tracking
└── config/             # Configuration management
    ├── settings.py     # Config loading
    └── logging_config.py  # Logging setup
```

### Dependency Rules

- **Domain**: No dependencies on other layers
- **Application**: Depends only on domain
- **Infrastructure**: Depends on application and domain
- **CLI**: Depends on all layers

## Clean Development Environment

### Intermediate Files (DO NOT COMMIT)

```
__pycache__/           # Python bytecode cache
.pytest_cache/         # Pytest cache
.hypothesis/           # Hypothesis test data
.coverage              # Coverage data
htmlcov/               # HTML coverage reports
logs/                  # Application logs
*.pyc, *.pyo, *.pyd   # Compiled Python files
.DS_Store              # macOS metadata
.vscode/, .idea/       # IDE settings
```

### Cleanup Script

```bash
#!/bin/bash
echo "Cleaning intermediate files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
rm -rf .pytest_cache .hypothesis htmlcov .coverage logs/*.log
echo "Done!"
```

### Before Committing

```bash
# Check status (should not show intermediate files)
git status

# Run tests
pytest

# Check coverage
pytest --cov=src/crawler --cov-report=term-missing

# Stage changes
git add <files>

# Commit
git commit -m "type(scope): description"
```

## Adding New Features

### 1. Start with Domain

Define entities and value objects:

```python
# src/crawler/domain/entities/new_entity.py
@dataclass
class NewEntity:
    id: str
    name: str
    # ... fields
```

### 2. Define Interface

Create abstract interface:

```python
# src/crawler/application/interfaces/new_interface.py
class NewInterface(ABC):
    @abstractmethod
    def do_something(self) -> Result:
        pass
```

### 3. Implement Use Case

Create application logic:

```python
# src/crawler/application/use_cases/new_use_case.py
class NewUseCase:
    def execute(self, input: Input) -> Output:
        # Business logic here
        pass
```

### 4. Implement Infrastructure

Create concrete implementation:

```python
# src/crawler/infrastructure/new_implementation.py
class NewImplementation(NewInterface):
    def do_something(self) -> Result:
        # Implementation here
        pass
```

### 5. Add CLI Command

Create command handler:

```python
# src/crawler/cli/commands/new_command.py
class NewCommand:
    def execute(self, args):
        # CLI logic here
        pass
```

### 6. Write Tests

Add comprehensive tests:

```python
# tests/unit/domain/test_new_entity.py
class TestNewEntity:
    def test_creation(self):
        entity = NewEntity(...)
        assert entity.id == "..."
```

### 7. Update Documentation

- Update README.md with usage examples
- Update ARCHITECTURE.md with design decisions
- Add docstrings to all public methods

## Debugging

### Enable Verbose Logging

```bash
# Set log level
export CRAWLER_LOG_LEVEL=DEBUG

# Run with verbose output
python -m crawler.cli.main --verbose download two-sum --platform leetcode
```

### Use Python Debugger

```python
# Add breakpoint
import pdb

pdb.set_trace()

# Or use built-in breakpoint (Python 3.7+)
breakpoint()
```

### Check HTTP Requests

```python
# Enable HTTP logging
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Profiling

```bash
# Profile code
python -m cProfile -o profile.stats -m crawler.cli.main download two-sum --platform leetcode

# View results
python -m pstats profile.stats
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Profile memory
python -m memory_profiler script.py
```

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'crawler'`

**Solution**: Install in editable mode

```bash
pip install -e .
```

### Test Failures

**Problem**: Tests fail with import errors

**Solution**: Ensure PYTHONPATH includes src directory

```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Coverage Not Working

**Problem**: Coverage shows 0%

**Solution**: Install coverage and pytest-cov

```bash
pip install coverage pytest-cov
```

## Best Practices

### 1. Write Tests First (TDD)

```python
# 1. Write failing test
def test_new_feature():
    result = new_feature()
    assert result == expected


# 2. Implement feature
def new_feature():
    return expected


# 3. Refactor
```

### 2. Keep Functions Small

- Single responsibility
- Maximum 20-30 lines
- Extract complex logic to helper functions

### 3. Use Type Hints

```python
# Good
def process(data: List[str]) -> Dict[str, int]:
    pass


# Bad
def process(data):
    pass
```

### 4. Handle Errors Gracefully

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### 5. Log Appropriately

```python
logger.debug("Detailed debug information")
logger.info("Important state changes")
logger.warning("Recoverable issues")
logger.error("Errors requiring attention")
```

## Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

## Questions?

- Check existing tests for examples
- Review ARCHITECTURE.md for design patterns
- Run `pytest -v` to see test structure
- Use `git log` to see commit history
