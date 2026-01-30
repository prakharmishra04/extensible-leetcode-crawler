# Coding Platform Crawler

A well-architected, extensible Python toolkit for downloading and managing coding problems from LeetCode and other platforms. Built with SOLID principles, comprehensive test coverage, and support for multiple output formats.

## ✨ Features

- 🎯 **Download individual problems** with full descriptions and your submissions
- 📦 **Batch download** all your solved problems at once
- 📋 **List and filter** downloaded problems by difficulty, topics, and more
- 🔄 **Smart update modes**: skip existing, update changed, or force overwrite
- 📝 **Multiple output formats**: Python, Markdown, or JSON
- 🏗️ **Extensible architecture**: Easy to add support for new platforms
- ⚙️ **Flexible configuration**: CLI args, environment variables, or config files
- 🔁 **Robust error handling**: Automatic retries with exponential backoff
- 📊 **Progress tracking**: Real-time progress bars for batch operations
- 🧪 **Comprehensive tests**: >80% code coverage with unit, integration, and E2E tests

## 🏛️ Architecture Overview

The crawler follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                               │
│  Commands: download, batch, list                            │
│  Progress tracking and user interaction                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                          │
│  Use Cases: FetchProblem, BatchDownload, ListProblems      │
│  Business logic orchestration                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│  Entities: Problem, Submission, User                        │
│  Value Objects: Difficulty, Example, Percentiles           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  Platform clients (LeetCode, extensible for others)         │
│  File system repository, HTTP client, formatters           │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns Used

- **Strategy Pattern**: Platform-specific implementations (LeetCode, future platforms)
- **Repository Pattern**: Abstract data persistence (file system, future database support)
- **Observer Pattern**: Progress tracking and event notifications
- **Command Pattern**: CLI command encapsulation
- **Factory Pattern**: Platform client creation
- **Adapter Pattern**: API response transformation to domain models
- **Dependency Injection**: Testability and flexibility

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd "Leet code/Crawler"
pip install -r requirements.txt
```

### Optional: Install YAML Support

For YAML configuration files:

```bash
pip install pyyaml
```

## 🚀 Quick Start

### 1. Get Your LeetCode Session Cookies

1. Open Chrome and go to [LeetCode](https://leetcode.com) (logged in)
2. Press `F12` → **Application** tab → **Cookies** → `https://leetcode.com`
3. Copy these values:
   - `LEETCODE_SESSION`
   - `csrftoken`

### 2. Set Environment Variables

```bash
export CRAWLER_LEETCODE_SESSION_TOKEN='your-session-value'
export CRAWLER_LEETCODE_USERNAME='your-username'
```

### 3. Download Your First Problem

```bash
python -m crawler.cli.main download two-sum --platform leetcode
```

That's it! Your problem is now in `./problems/leetcode/two-sum/`

## 📖 Usage

### Command Overview

The crawler provides three main commands:

```bash
# Download a single problem
python -m crawler.cli.main download <problem-id> --platform <platform>

# Batch download all solved problems
python -m crawler.cli.main batch <username> --platform <platform>

# List downloaded problems
python -m crawler.cli.main list [options]
```

### Download Command

Download a single problem with your submission.

**Basic Usage:**

```bash
# Download a problem
python -m crawler.cli.main download two-sum --platform leetcode

# Force re-download (overwrite existing)
python -m crawler.cli.main download two-sum --platform leetcode --force

# Download as Markdown
python -m crawler.cli.main download two-sum --platform leetcode --format markdown

# Download as JSON
python -m crawler.cli.main download two-sum --platform leetcode --format json
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `problem-id` | Problem identifier (e.g., "two-sum") | Required |
| `--platform` | Platform name (leetcode) | Required |
| `--format` | Output format (python, markdown, json) | python |
| `--force` | Force re-download even if exists | False |

**Examples:**

```bash
# Download multiple problems
python -m crawler.cli.main download two-sum --platform leetcode
python -m crawler.cli.main download add-two-numbers --platform leetcode
python -m crawler.cli.main download longest-substring --platform leetcode

# Download with custom output directory
python -m crawler.cli.main --output-dir ./my-problems download two-sum --platform leetcode

# Download with verbose logging
python -m crawler.cli.main --verbose download two-sum --platform leetcode
```

### Batch Download Command

Download all your solved problems at once with smart update modes.

**Basic Usage:**

```bash
# Download all solved problems (skip existing)
python -m crawler.cli.main batch your-username --platform leetcode

# Update files with newer submissions
python -m crawler.cli.main batch your-username --platform leetcode --mode update

# Force re-download everything
python -m crawler.cli.main batch your-username --platform leetcode --mode force

# Download only Easy problems
python -m crawler.cli.main batch your-username --platform leetcode --difficulty Easy

# Download only Array and Hash Table problems
python -m crawler.cli.main batch your-username --platform leetcode --topics "Array" "Hash Table"
```

**Update Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `skip` | Skip existing files (default) | First download or resuming |
| `update` | Update only if newer submission exists | After solving more problems |
| `force` | Always overwrite existing files | Fresh start or fixing issues |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `username` | Your platform username | Required |
| `--platform` | Platform name (leetcode) | Required |
| `--mode` | Update mode (skip, update, force) | skip |
| `--format` | Output format (python, markdown, json) | python |
| `--difficulty` | Filter by difficulty (Easy, Medium, Hard) | All |
| `--topics` | Filter by topics (space-separated) | All |
| `--include-community` | Include community solutions | False |

**Examples:**

```bash
# Download all Easy and Medium problems
python -m crawler.cli.main batch john_doe --platform leetcode \
  --difficulty Easy Medium

# Download all Array problems as Markdown
python -m crawler.cli.main batch john_doe --platform leetcode \
  --topics Array --format markdown

# Update existing files with newer submissions
python -m crawler.cli.main batch john_doe --platform leetcode --mode update

# Download to custom directory
python -m crawler.cli.main --output-dir ~/leetcode-backup \
  batch john_doe --platform leetcode

# Download with community solutions (slower)
python -m crawler.cli.main batch john_doe --platform leetcode \
  --include-community
```

### List Command

List and filter your downloaded problems.

**Basic Usage:**

```bash
# List all downloaded problems
python -m crawler.cli.main list

# List only LeetCode problems
python -m crawler.cli.main list --platform leetcode

# List only Easy problems
python -m crawler.cli.main list --difficulty Easy

# List only Hard problems
python -m crawler.cli.main list --difficulty Hard

# List Array and Hash Table problems
python -m crawler.cli.main list --topics Array "Hash Table"

# Sort by difficulty (reverse order)
python -m crawler.cli.main list --sort-by difficulty --reverse
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--platform` | Filter by platform | All |
| `--difficulty` | Filter by difficulty (Easy, Medium, Hard) | All |
| `--topics` | Filter by topics (space-separated) | All |
| `--sort-by` | Sort field (id, title, difficulty) | id |
| `--reverse` | Reverse sort order | False |

**Examples:**

```bash
# List Medium and Hard problems sorted by title
python -m crawler.cli.main list --difficulty Medium Hard --sort-by title

# List all problems with verbose output
python -m crawler.cli.main --verbose list

# List problems from custom directory
python -m crawler.cli.main --output-dir ~/leetcode-backup list
```

## ⚙️ Configuration

The crawler supports multiple configuration sources with clear precedence:

**Precedence Order (highest to lowest):**
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

### Environment Variables

All environment variables are prefixed with `CRAWLER_`:

```bash
# LeetCode credentials
export CRAWLER_LEETCODE_SESSION_TOKEN='your-session-token'
export CRAWLER_LEETCODE_USERNAME='your-username'

# Output configuration
export CRAWLER_OUTPUT_DIR='./problems'
export CRAWLER_DEFAULT_FORMAT='python'

# Rate limiting
export CRAWLER_REQUESTS_PER_SECOND='2.0'

# Retry configuration
export CRAWLER_MAX_RETRIES='3'
export CRAWLER_INITIAL_DELAY='1.0'
export CRAWLER_MAX_DELAY='60.0'

# Logging
export CRAWLER_LOG_LEVEL='INFO'
export CRAWLER_LOG_FILE='./logs/crawler.log'
```

### Configuration File

Create a `config.yaml` or `config.json` file:

**YAML Example (`config.yaml`):**

```yaml
# LeetCode configuration
leetcode_session_token: "your-session-token"
leetcode_username: "your-username"

# Output configuration
output_dir: "./problems"
default_format: "python"

# Rate limiting
requests_per_second: 2.0

# Retry configuration
max_retries: 3
initial_delay: 1.0
max_delay: 60.0
exponential_base: 2.0
jitter: true

# Logging
log_level: "INFO"
log_file: "./logs/crawler.log"
```

**JSON Example (`config.json`):**

```json
{
  "leetcode_session_token": "your-session-token",
  "leetcode_username": "your-username",
  "output_dir": "./problems",
  "default_format": "python",
  "requests_per_second": 2.0,
  "max_retries": 3,
  "initial_delay": 1.0,
  "max_delay": 60.0,
  "exponential_base": 2.0,
  "jitter": true,
  "log_level": "INFO",
  "log_file": "./logs/crawler.log"
}
```

**Using Configuration File:**

```bash
# Use custom config file
python -m crawler.cli.main --config config.yaml download two-sum --platform leetcode

# Config file with CLI overrides
python -m crawler.cli.main --config config.yaml --output-dir ./custom \
  download two-sum --platform leetcode
```

### Configuration Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `leetcode_session_token` | string | None | LeetCode session cookie |
| `leetcode_username` | string | None | LeetCode username |
| `output_dir` | string | "./problems" | Base directory for downloads |
| `default_format` | string | "python" | Default output format |
| `requests_per_second` | float | 2.0 | API rate limit |
| `max_retries` | int | 3 | Maximum retry attempts |
| `initial_delay` | float | 1.0 | Initial retry delay (seconds) |
| `max_delay` | float | 60.0 | Maximum retry delay (seconds) |
| `exponential_base` | float | 2.0 | Exponential backoff base |
| `jitter` | bool | true | Add random jitter to retries |
| `log_level` | string | "INFO" | Logging level |
| `log_file` | string | None | Optional log file path |

## 📁 Output Structure

Downloaded problems are organized by platform and problem ID:

```
problems/
├── leetcode/
│   ├── two-sum/
│   │   ├── solution.py          # Your solution (default format)
│   │   └── metadata.json        # Problem metadata
│   ├── add-two-numbers/
│   │   ├── solution.py
│   │   └── metadata.json
│   └── longest-substring/
│       ├── solution.md          # Markdown format
│       └── metadata.json
└── logs/
    └── crawler.log              # Application logs
```

### Output Formats

#### Python Format (`.py`)

```python
"""
Two Sum
Difficulty: Easy
Platform: leetcode
Topics: Array, Hash Table

My Last Accepted Submission:
  Language: python3
  Runtime: 52 ms (beats 89.5%)
  Memory: 15.2 MB (beats 76.3%)

Problem Description:
Given an array of integers nums and an integer target, return indices of the
two numbers such that they add up to target.

[Full description with examples, constraints, and hints...]
"""

# Your actual submitted code here
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your solution...
```

#### Markdown Format (`.md`)

```markdown
# Two Sum

**Difficulty:** Easy
**Platform:** leetcode
**Topics:** Array, Hash Table
**Acceptance Rate:** 49.2%

## Description

Given an array of integers nums and an integer target, return indices...

## Constraints

- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9

## Examples

### Example 1

**Input:** `nums = [2,7,11,15], target = 9`
**Output:** `[0,1]`
**Explanation:** Because nums[0] + nums[1] == 9, we return [0, 1].

## Solution

**Language:** python3
**Runtime:** 52 ms
**Memory:** 15.2 MB

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your solution...
```
```

#### JSON Format (`.json`)

```json
{
  "id": "two-sum",
  "platform": "leetcode",
  "title": "Two Sum",
  "difficulty": "Easy",
  "description": "Given an array of integers...",
  "topics": ["Array", "Hash Table"],
  "examples": [...],
  "constraints": "...",
  "hints": [...],
  "acceptance_rate": 49.2,
  "submission": {
    "language": "python3",
    "code": "class Solution:...",
    "runtime": "52 ms",
    "memory": "15.2 MB"
  }
}
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Authentication required"** | Set `CRAWLER_LEETCODE_SESSION_TOKEN` environment variable |
| **"No accepted submissions found"** | You haven't solved this problem yet |
| **"Rate limit exceeded"** | Reduce `requests_per_second` in config |
| **"Connection timeout"** | Check internet connection, increase `max_delay` |
| **Cookies expired** | Get fresh cookies from browser (last 2-4 weeks) |
| **"Unsupported platform"** | Currently only LeetCode is supported |

### Getting Fresh Cookies

**Chrome/Edge:**
1. Open LeetCode and log in
2. Press `F12` → **Application** tab
3. **Storage** → **Cookies** → `https://leetcode.com`
4. Copy `LEETCODE_SESSION` value

**Firefox:**
1. Open LeetCode and log in
2. Press `F12` → **Storage** tab
3. **Cookies** → `https://leetcode.com`
4. Copy `LEETCODE_SESSION` value

**Safari:**
1. Enable Developer menu: Preferences → Advanced
2. Develop → Show Web Inspector → Storage → Cookies
3. Copy `LEETCODE_SESSION` value

### Verbose Logging

Enable verbose logging for debugging:

```bash
# Enable DEBUG level logging
python -m crawler.cli.main --verbose download two-sum --platform leetcode

# Save logs to file
python -m crawler.cli.main --log-file debug.log --verbose \
  download two-sum --platform leetcode
```

### Network Issues

If you experience network issues:

1. **Increase retry attempts:**
   ```bash
   export CRAWLER_MAX_RETRIES=5
   export CRAWLER_MAX_DELAY=120.0
   ```

2. **Reduce rate limit:**
   ```bash
   export CRAWLER_REQUESTS_PER_SECOND=1.0
   ```

3. **Check connectivity:**
   ```bash
   curl -I https://leetcode.com/graphql
   ```

## 🎯 Example Workflows

### Workflow 1: First-Time Setup

```bash
# 1. Set up environment
export CRAWLER_LEETCODE_SESSION_TOKEN='your-token'
export CRAWLER_LEETCODE_USERNAME='your-username'

# 2. Download all your solutions
python -m crawler.cli.main batch your-username --platform leetcode

# 3. List what you downloaded
python -m crawler.cli.main list --platform leetcode

# Result: All your solved problems in ./problems/leetcode/
```

### Workflow 2: Daily Practice

```bash
# 1. Solve problems on LeetCode
# 2. Update your local collection
python -m crawler.cli.main batch your-username --platform leetcode --mode update

# 3. List new problems
python -m crawler.cli.main list --platform leetcode --sort-by id --reverse

# Result: Only new/updated problems are downloaded
```

### Workflow 3: Focused Study

```bash
# 1. Download only Easy problems for review
python -m crawler.cli.main batch your-username --platform leetcode \
  --difficulty Easy --format markdown

# 2. Download specific topics
python -m crawler.cli.main batch your-username --platform leetcode \
  --topics "Dynamic Programming" "Backtracking"

# 3. List and review
python -m crawler.cli.main list --difficulty Easy --topics "Array"

# Result: Focused collection for targeted practice
```

### Workflow 4: Backup and Export

```bash
# 1. Create backup directory
mkdir -p ~/leetcode-backup

# 2. Download everything as JSON
python -m crawler.cli.main --output-dir ~/leetcode-backup \
  batch your-username --platform leetcode --format json --mode force

# 3. Verify backup
python -m crawler.cli.main --output-dir ~/leetcode-backup list

# Result: Complete backup in JSON format
```

### Workflow 5: Multiple Formats

```bash
# 1. Download as Python for coding
python -m crawler.cli.main batch your-username --platform leetcode \
  --format python

# 2. Download as Markdown for documentation
python -m crawler.cli.main --output-dir ./docs \
  batch your-username --platform leetcode --format markdown --mode force

# Result: Code in ./problems/, docs in ./docs/
```

## 🧪 Testing

The project has comprehensive test coverage (>80%):

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/crawler --cov-report=html

# Run specific test categories
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/e2e/              # End-to-end tests

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/domain/entities/test_problem.py
```

## 🔐 Security

**⚠️ Important Security Notes:**

- **Never commit credentials** to version control
- **Keep session tokens private** - treat them like passwords
- **Tokens expire** - refresh every 2-4 weeks
- **Use environment variables** or config files (gitignored)
- **Don't share config files** containing credentials

**Best Practices:**

1. Use environment variables for credentials
2. Add `config.yaml` and `config.json` to `.gitignore` (already done)
3. Use separate config files for different environments
4. Rotate session tokens regularly

## 🚀 Extending the Crawler

The crawler is designed to be easily extensible. See the [Adding New Platforms Guide](docs/adding_new_platform.md) for detailed instructions on adding support for new coding platforms.

**Quick Overview:**

1. Implement the `PlatformClient` interface
2. Create a platform-specific adapter
3. Register in the `PlatformClientFactory`
4. Add platform-specific configuration

**Example platforms that can be added:**
- HackerRank
- CodeChef
- Codeforces
- AtCoder
- TopCoder

## 📚 Additional Documentation

- [Adding New Platforms](docs/adding_new_platform.md) - Guide for extending to new platforms
- [Architecture Overview](docs/architecture.md) - Detailed architecture documentation
- [API Reference](docs/api_reference.md) - Complete API documentation
- [Contributing Guide](docs/contributing.md) - How to contribute to the project

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: Follow PEP 8 and use type hints
2. **Tests**: Add tests for new features (maintain >80% coverage)
3. **Documentation**: Update README and docstrings
4. **Commits**: Use conventional commit messages

## 📄 License

For personal use only. Respect LeetCode's Terms of Service and rate limits.

## 🙏 Acknowledgments

- Built with Python 3.8+
- Uses LeetCode's GraphQL API
- Inspired by the need for better problem management tools
- Designed with SOLID principles and clean architecture

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Enable verbose logging: `--verbose`
3. Check existing issues on GitHub
4. Create a new issue with:
   - Command you ran
   - Error message
   - Log output (with credentials removed)

---

**Happy Coding! 🎉**
