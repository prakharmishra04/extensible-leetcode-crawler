# Development Guide

## Intermediate Files (Generated During Development)

These files are automatically generated and should NOT be committed to git:

### Testing & Coverage
- `.pytest_cache/` - pytest cache directory
- `.coverage` - coverage data file
- `htmlcov/` - HTML coverage reports
- `.hypothesis/` - hypothesis test data cache

### Python Runtime
- `__pycache__/` - Python bytecode cache directories
- `*.pyc`, `*.pyo`, `*.pyd` - Compiled Python files
- `*.so` - Shared object files

### Logs
- `logs/` - Application log files
- `*.log` - Individual log files

### IDE & Editor
- `.vscode/` - VS Code settings
- `.idea/` - PyCharm/IntelliJ settings
- `*.swp`, `*.swo` - Vim swap files
- `.DS_Store` - macOS Finder metadata

### Build & Distribution
- `build/`, `dist/` - Build artifacts
- `*.egg-info/` - Package metadata
- `.eggs/` - Egg packages

## Git Repository Setup

The `Leet code/Crawler` directory is now an independent git repository:

```bash
cd "Leet code/Crawler"
git status  # Check repository status
git log     # View commit history
```

### Initial Commit

The initial commit includes:
- Domain layer (entities, value objects, enums)
- Application interfaces (Strategy, Repository, Observer patterns)
- Test infrastructure (pytest, hypothesis, fixtures)
- Logging framework (structured JSON logging)
- 105 passing tests with 73.15% coverage

### .gitignore Configuration

The `.gitignore` file is configured to exclude:
- All Python cache and bytecode files
- Test artifacts and coverage reports
- Log files
- IDE/editor configuration
- Virtual environments
- Build artifacts

## Clean Development Environment

To clean up intermediate files:

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove test artifacts
rm -rf .pytest_cache .hypothesis htmlcov .coverage

# Remove logs
rm -rf logs/*.log

# Remove build artifacts
rm -rf build dist *.egg-info
```

Or use the provided script:

```bash
# Create a cleanup script
cat > clean.sh << 'EOF'
#!/bin/bash
echo "Cleaning intermediate files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
rm -rf .pytest_cache .hypothesis htmlcov .coverage logs/*.log
echo "Done!"
EOF

chmod +x clean.sh
./clean.sh
```

## Development Workflow

1. **Make changes** to source code
2. **Run tests** to verify: `pytest`
3. **Check coverage**: `pytest --cov=src --cov-report=html`
4. **Stage changes**: `git add <files>`
5. **Commit**: `git commit -m "type: description"`
6. **Clean up** intermediate files before committing

## Commit Message Convention

Follow Conventional Commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example:
```bash
git commit -m "feat(domain): add Problem entity validation"
git commit -m "test: add hypothesis strategies for entities"
git commit -m "docs: update README with usage examples"
```

## Keeping Repository Clean

**Always check before committing:**

```bash
git status  # Should not show .pytest_cache, htmlcov, logs, etc.
```

**If you accidentally staged intermediate files:**

```bash
git reset HEAD <file>  # Unstage specific file
git reset HEAD .       # Unstage all files
```

## Remote Repository Setup

To push to a remote repository:

```bash
# Add remote
git remote add origin <your-repo-url>

# Push initial commit
git push -u origin main
```

## Best Practices

1. **Never commit** intermediate files (they're in .gitignore)
2. **Run tests** before committing
3. **Keep commits atomic** - one logical change per commit
4. **Write descriptive** commit messages
5. **Clean up** before pushing to remote

## File Structure

```
Leet code/Crawler/
├── src/                    # Source code (commit)
├── tests/                  # Test code (commit)
├── examples/               # Example scripts (commit)
├── utils/                  # Utility modules (commit)
├── .gitignore             # Git ignore rules (commit)
├── pytest.ini             # Pytest config (commit)
├── requirements.txt       # Dependencies (commit)
├── README.md              # Documentation (commit)
├── .pytest_cache/         # DO NOT COMMIT
├── .hypothesis/           # DO NOT COMMIT
├── htmlcov/               # DO NOT COMMIT
├── logs/                  # DO NOT COMMIT
└── __pycache__/           # DO NOT COMMIT
```

## Questions?

- Check `.gitignore` to see what's excluded
- Run `git status` to verify clean working directory
- Use `git diff` to review changes before committing
