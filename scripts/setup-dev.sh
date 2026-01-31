#!/bin/bash
# Development Environment Setup Script
# This script sets up a production-ready development environment

set -e  # Exit on error

echo "🚀 Setting up development environment..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Install package in development mode
echo ""
echo "📦 Installing package in development mode..."
pip install -e ".[dev]"

# Install pre-commit
echo ""
echo "🔧 Installing pre-commit hooks..."
pip install pre-commit

# Install all git hooks
echo ""
echo "🪝 Installing git hooks..."
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg

# Run pre-commit on all files to ensure everything is set up correctly
echo ""
echo "✅ Running pre-commit checks on all files..."
echo "   (This may take a few minutes on first run)"
pre-commit run --all-files || {
    echo ""
    echo "⚠️  Some pre-commit checks failed. This is normal on first setup."
    echo "   The hooks have auto-fixed most issues."
    echo "   Review the changes and commit them."
}

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Copy config template: cp my-config.yaml.example my-config.yaml"
echo "   2. Add your LeetCode credentials to my-config.yaml"
echo "   3. Run tests: pytest"
echo "   4. Start coding! Git hooks will run automatically on commit/push"
echo ""
echo "🔒 Git hooks installed:"
echo "   • pre-commit: Code formatting, linting, type checking"
echo "   • pre-push: Additional validation before push"
echo "   • commit-msg: Conventional commit message validation"
echo ""
