# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## \[Unreleased\]

### ✨ Features

- **Implemented smart UPDATE mode** - UPDATE mode now properly detects newer submissions on the platform and only re-downloads when necessary. Previously, UPDATE mode behaved identically to SKIP mode.
  - Compares stored submission timestamp with platform submission timestamp
  - Only re-downloads if platform has a newer submission
  - Automatically downloads problems that exist but have no submission stored
  - Gracefully handles comparison failures by skipping the problem

### 🔧 Technical Improvements

- **Added `get_submission_timestamp()` to repository interface** - New method enables efficient timestamp comparison without loading entire problem entities
- **Enhanced batch download logic** - UPDATE mode now makes intelligent decisions about when to re-download based on submission freshness

### 📝 Notes

This update makes UPDATE mode work as originally intended - it's now the recommended mode for keeping your local problem repository synchronized with the platform. Use:

- `--mode skip` - Never re-download existing problems (fastest)
- `--mode update` - Re-download only when newer submissions exist (smart sync)
- `--mode force` - Always re-download everything (complete refresh)

## \[2.0.3\] - 2026-01-31

### 🐛 Bug Fixes

- **Fixed `--limit` to apply to NEW problems only in SKIP mode** - The `--limit` parameter now correctly applies to new problems to download, not total problems including already-downloaded ones. Previously, with 150 solved problems and 50 already downloaded, `--limit 50` would process the first 50 (all existing) and download 0 new problems. Now it downloads 50 NEW problems after filtering out existing ones.
- **Added rate limit handling for LeetCode submission API** - Implemented 1-second delay after each submission fetch to avoid aggressive rate limiting. LeetCode's submission API has strict rate limits that apply to ALL users including Premium members.
- **Added smart retry logic for 403/429 errors** - HTTP client now automatically retries requests that fail with 403 Forbidden or 429 Too Many Requests status codes, using exponential backoff (2x delay multiplier) to respect rate limits.

### 🔄 Breaking Changes

- **`--limit` behavior change in SKIP mode** - The `--limit` parameter now applies to NEW problems only when using `--mode skip`. Already-downloaded problems are pre-filtered before applying the limit.

  **Old behavior:**

  ```bash
  # With 150 solved, 50 already downloaded
  crawler batch user --limit 50 --mode skip
  # Would process first 50 problems (all existing), download 0 new
  ```

  **New behavior:**

  ```bash
  # With 150 solved, 50 already downloaded
  crawler batch user --limit 50 --mode skip
  # Filters out 50 existing, then downloads 50 NEW problems
  ```

### ✨ Improvements

- **Better handling of partial failures** - Batch download continues even if some submissions fail due to rate limits, ensuring maximum coverage
- **Enhanced success logic** - Command success now determined by whether any failures occurred, properly handling cases where all problems were pre-filtered

### 📝 Notes

This patch addresses two critical issues:

1. Rate limiting problems when fetching submissions during batch downloads
1. Incorrect `--limit` behavior that counted already-downloaded problems

The `--limit` change is considered breaking because it changes the behavior of the command, though it makes it work as users would intuitively expect.

## \[2.0.2\] - 2026-01-31

### 🐛 Bug Fixes

- **Fixed batch download to use `fetch_all_problems_with_status()`** - The batch download command now fetches ALL solved problems instead of just recent submissions, ensuring complete coverage
- **Updated tests** - Fixed all unit tests to use the new method

### 📝 Notes

This patch ensures that `crawler batch` command now fetches all your solved problems, not just the recent 20-100. This was the critical missing piece from v2.0.1.

## \[2.0.1\] - 2026-01-31

### 🐛 Bug Fixes

- **Added `fetch_all_problems_with_status()` method** - Implemented comprehensive problem fetching that retrieves ALL LeetCode problems with their solve status (solved/attempted/not started), matching v1 functionality
- **Added `adapt_problem_from_list()` adapter method** - New adapter method to convert problemsetQuestionList API responses to Problem entities

### ✨ Improvements

- **Enhanced `fetch_solved_problems()` documentation** - Updated to reference the new `fetch_all_problems_with_status()` method for complete problem lists
- **Better API coverage** - Now supports both the limited `recentAcSubmissionList` API (for recent submissions) and the comprehensive `problemsetQuestionList` API (for all problems with status)

### 📝 Notes

This patch addresses the limitation where v2 could only fetch recent solved problems (typically 20-100) while v1 could fetch all problems with their status. The new `fetch_all_problems_with_status()` method provides:

- Complete list of all LeetCode problems
- Solve status for each problem (ac/notac/null)
- Optional filtering by status
- Pagination support for large result sets

## [2.0.0] - 2026-01-31

### 🎉 Initial Production Release

This is the first production-ready release of the Coding Platform Crawler, a complete rewrite from v1 scripts with clean architecture, comprehensive testing, and professional CI/CD.

### ✨ Features

#### Core Functionality

- **Download Individual Problems** - Fetch single problems with full descriptions and submissions
- **Batch Download** - Download all solved problems at once with smart filtering
- **List Problems** - View and filter downloaded problems by difficulty and topics
- **Multiple Output Formats** - Support for Python, Markdown, and JSON formats
- **Smart Update Modes** - Skip existing, update changed, or force overwrite
- **Flexible Configuration** - CLI args, environment variables, or config files (YAML/JSON)

#### Architecture & Design

- **Clean Architecture** - Domain-driven design with clear separation of concerns
- **SOLID Principles** - Maintainable and extensible codebase
- **Extensible Platform Support** - Easy to add new coding platforms beyond LeetCode
- **Robust Error Handling** - Automatic retries with exponential backoff
- **Rate Limiting** - Configurable rate limiting to respect API limits
- **Rich CLI Output** - Beautiful terminal output with progress indicators

#### Developer Experience

- **Comprehensive Testing** - 618 tests (588 unit + 29 integration + 1 e2e)
- **89% Code Coverage** - Exceeds industry standard of 80%
- **Type Hints** - Full type annotations throughout codebase
- **Documentation** - Extensive README, architecture docs, and inline documentation
- **Pre-commit Hooks** - Automated code quality checks (Black, flake8, mypy, etc.)

### 🔧 Technical Details

#### Supported Python Versions

- Python 3.8, 3.9, 3.10, 3.11, 3.12

#### Dependencies

- `requests>=2.31.0` - HTTP client
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser
- `pyyaml>=6.0` - YAML configuration
- `rich>=13.0.0` - Terminal formatting

#### CI/CD Pipeline

- **GitHub Actions** - Automated testing on all Python versions
- **Pre-commit Checks** - Code formatting and linting
- **Code Quality** - Black, flake8, mypy, isort, bandit
- **Coverage Reports** - Automated coverage tracking
- **Release Automation** - Automatic PyPI publishing on version tags

### 📦 Installation

```bash
# Install from PyPI
pip install coding-platform-crawler

# Or install from source
git clone https://github.com/prakharmishra04/extensible-leetcode-crawler.git
cd extensible-leetcode-crawler
pip install -e .
```

### 🚀 Quick Start

```bash
# Download a single problem
crawler download two-sum --platform leetcode

# Batch download all solved problems
crawler batch your-username --platform leetcode

# List downloaded problems
crawler list --difficulty Medium
```

### 📚 Documentation

- [README.md](README.md) - Getting started guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [docs/CI_CD.md](docs/CI_CD.md) - CI/CD documentation

### 🙏 Acknowledgments

This project is a complete rewrite of the v1 scripts with:

- Professional software architecture
- Comprehensive test coverage
- Production-ready CI/CD pipeline
- Extensible design for future platforms

### 🔗 Links

- **GitHub Repository**: https://github.com/prakharmishra04/extensible-leetcode-crawler
- **PyPI Package**: https://pypi.org/project/coding-platform-crawler/
- **Issue Tracker**: https://github.com/prakharmishra04/extensible-leetcode-crawler/issues

______________________________________________________________________

## [1.0.0] - Legacy Scripts

The v1 version consisted of standalone Python scripts in the `v1-scripts/` directory. These have been preserved for reference but are superseded by the v2.0.0 architecture.

[1.0.0]: https://github.com/prakharmishra04/extensible-leetcode-crawler/tree/main/v1-scripts
[2.0.0]: https://github.com/prakharmishra04/extensible-leetcode-crawler/releases/tag/v2.0.0
