@echo off
REM Development Environment Setup Script (Windows Batch)
REM This script sets up a production-ready development environment on Windows

echo.
echo ========================================
echo   Development Environment Setup
echo ========================================
echo.

REM Check Python version
echo [1/4] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)
echo.

REM Install package in development mode
echo [2/4] Installing package in development mode...
pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install package
    exit /b 1
)
echo.

REM Install pre-commit
echo [3/4] Installing pre-commit hooks...
pip install pre-commit
if %errorlevel% neq 0 (
    echo ERROR: Failed to install pre-commit
    exit /b 1
)
echo.

REM Install all git hooks
echo [4/4] Installing git hooks...
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg
if %errorlevel% neq 0 (
    echo ERROR: Failed to install git hooks
    exit /b 1
)
echo.

REM Run pre-commit on all files
echo Running pre-commit checks on all files...
echo (This may take a few minutes on first run)
pre-commit run --all-files
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some pre-commit checks failed. This is normal on first setup.
    echo          The hooks have auto-fixed most issues.
    echo          Review the changes and commit them.
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Copy config template: copy my-config.yaml.example my-config.yaml
echo   2. Add your LeetCode credentials to my-config.yaml
echo   3. Run tests: pytest
echo   4. Start coding! Git hooks will run automatically
echo.
echo Git hooks installed:
echo   - pre-commit: Code formatting, linting, type checking
echo   - pre-push: Additional validation before push
echo   - commit-msg: Conventional commit message validation
echo.
pause
