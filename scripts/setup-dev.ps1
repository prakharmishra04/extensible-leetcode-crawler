# Development Environment Setup Script (PowerShell)
# This script sets up a production-ready development environment on Windows

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up development environment..." -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
Write-Host "   Python version: $pythonVersion" -ForegroundColor Gray

# Install package in development mode
Write-Host ""
Write-Host "📦 Installing package in development mode..." -ForegroundColor Cyan
pip install -e ".[dev]"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install package" -ForegroundColor Red
    exit 1
}

# Install pre-commit
Write-Host ""
Write-Host "🔧 Installing pre-commit hooks..." -ForegroundColor Cyan
pip install pre-commit

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install pre-commit" -ForegroundColor Red
    exit 1
}

# Install all git hooks
Write-Host ""
Write-Host "🪝 Installing git hooks..." -ForegroundColor Cyan
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install git hooks" -ForegroundColor Red
    exit 1
}

# Run pre-commit on all files to ensure everything is set up correctly
Write-Host ""
Write-Host "✅ Running pre-commit checks on all files..." -ForegroundColor Cyan
Write-Host "   (This may take a few minutes on first run)" -ForegroundColor Gray
pre-commit run --all-files

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Some pre-commit checks failed. This is normal on first setup." -ForegroundColor Yellow
    Write-Host "   The hooks have auto-fixed most issues." -ForegroundColor Yellow
    Write-Host "   Review the changes and commit them." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Copy config template: Copy-Item my-config.yaml.example my-config.yaml" -ForegroundColor Gray
Write-Host "   2. Add your LeetCode credentials to my-config.yaml" -ForegroundColor Gray
Write-Host "   3. Run tests: pytest" -ForegroundColor Gray
Write-Host "   4. Start coding! Git hooks will run automatically on commit/push" -ForegroundColor Gray
Write-Host ""
Write-Host "🔒 Git hooks installed:" -ForegroundColor Cyan
Write-Host "   • pre-commit: Code formatting, linting, type checking" -ForegroundColor Gray
Write-Host "   • pre-push: Additional validation before push" -ForegroundColor Gray
Write-Host "   • commit-msg: Conventional commit message validation" -ForegroundColor Gray
Write-Host ""
