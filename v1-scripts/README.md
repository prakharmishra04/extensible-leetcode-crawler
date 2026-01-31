# LeetCode Crawler v1 - Simple Script-Based Version

A lightweight, script-based LeetCode crawler for quick problem downloads. Perfect for users who want a simple, no-installation solution.

> **⚡ Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for 60-second setup!

## Features

- 🎯 Single problem download with your submission
- 📦 Batch download all solved problems
- 📋 List your solved problems
- 🔄 Smart update detection (skip unchanged files)
- 📝 Python template generation with your code
- 🚀 No complex setup - just Python scripts

## Quick Start

### 1. Install Dependencies

```bash
pip install requests beautifulsoup4
```

### 2. Set Up Authentication

Get your LeetCode session cookies:

1. Open https://leetcode.com (logged in) → Press F12
1. Application tab → Cookies → https://leetcode.com
1. Copy `LEETCODE_SESSION` and `csrftoken` values

Set environment variables:

```bash
export LEETCODE_SESSION='your-session-token'
export LEETCODE_CSRF='your-csrf-token'
```

### 3. Download Your First Problem

```bash
cd v1-scripts
python leetcode_crawler.py https://leetcode.com/problems/two-sum/
```

## Usage

### Download a Single Problem

```bash
# Download with your submission
python leetcode_crawler.py https://leetcode.com/problems/two-sum/

# With authentication (if not using env vars)
python leetcode_crawler.py https://leetcode.com/problems/two-sum/ \
  --session "your-session" --csrf "your-csrf"

# Include community solutions (slower)
python leetcode_crawler.py https://leetcode.com/problems/two-sum/ --with-solutions

# Custom output filename
python leetcode_crawler.py https://leetcode.com/problems/two-sum/ -t my_solution.py
```

### List Your Solved Problems

```bash
# List recent solved problems
python fetch_solved_problems.py

# Show detailed information
python fetch_solved_problems.py --details

# Save to file
python fetch_solved_problems.py --output solved.json
python fetch_solved_problems.py --output solved.md --format md

# Get all problems with status
python fetch_solved_problems.py --all-with-status
```

### Batch Download All Solutions

```bash
# Download all your solved problems
python batch_download_solutions.py

# Download to custom directory
python batch_download_solutions.py --output-dir "My-Solutions"

# Download only recent 50 problems
python batch_download_solutions.py --limit 50

# Update files with newer submissions
python batch_download_solutions.py --update

# Force re-download (overwrite existing)
python batch_download_solutions.py --force

# Include community solutions (much slower)
python batch_download_solutions.py --with-solutions
```

## Output Structure

```
v1-scripts/
├── two-sum.py              # Your solution with submission code
├── add-two-numbers.py      # Another solution
└── ...
```

Or with custom directory:

```
My-Solutions/
├── two-sum.py
├── add-two-numbers.py
└── ...
```

## Scripts Overview

### Core Scripts

- **`leetcode_crawler.py`** - Download single problems with your submissions
- **`fetch_solved_problems.py`** - List and export your solved problems
- **`batch_download_solutions.py`** - Batch download all your solutions

### Utility Modules

- **`utils/leetcode_client.py`** - LeetCode API client with GraphQL support
- **`utils/formatters.py`** - HTML cleaning and text formatting utilities

## Configuration

### Environment Variables

```bash
export LEETCODE_SESSION='your-session-token'
export LEETCODE_CSRF='your-csrf-token'
```

### Command Line Arguments

All scripts support `--session` and `--csrf` flags if you prefer not to use environment variables.

## Features Comparison: v1 vs v2

| Feature        | v1 (Scripts)              | v2 (Architecture)         |
| -------------- | ------------------------- | ------------------------- |
| Setup          | Simple - just run scripts | Install as package        |
| Architecture   | Procedural scripts        | Clean architecture layers |
| Extensibility  | Hardcoded for LeetCode    | Easy to add platforms     |
| Testing        | Manual                    | 73% test coverage         |
| Configuration  | Env vars + CLI args       | Config files + env + CLI  |
| Output Formats | Python templates          | Python, JSON, Markdown    |
| Use Case       | Quick downloads           | Production-ready tool     |

## When to Use v1

Use v1 if you:

- Want a quick, simple solution
- Only need LeetCode support
- Prefer standalone scripts over packages
- Don't need extensive testing or architecture

## When to Use v2

Use v2 (main project) if you:

- Want a production-ready tool
- Need multiple output formats
- Plan to add other platforms
- Want comprehensive testing
- Prefer clean architecture

## Troubleshooting

**"Authentication required"**

- Set `LEETCODE_SESSION` and `LEETCODE_CSRF` environment variables
- Or use `--session` and `--csrf` flags
- Cookies expire after 2-4 weeks - get fresh ones from browser

**"No accepted submissions found"**

- You haven't solved this problem yet
- Check the problem URL is correct

**"Rate limit exceeded"**

- Use `--delay` flag to increase delay between requests
- Default is 1 second, try 2-3 seconds

## Examples

### Download your top 10 problems

```bash
python batch_download_solutions.py --limit 10
```

### Update only changed solutions

```bash
python batch_download_solutions.py --update
```

### Export solved problems as markdown

```bash
python fetch_solved_problems.py --output my-progress.md --format md
```

### Download with custom delay (be nice to servers)

```bash
python batch_download_solutions.py --delay 2.0
```

## Migration to v2

If you want to upgrade to the full-featured v2:

```bash
# Go back to project root
cd ..

# Install v2
pip install -e .

# Use v2 CLI
crawler download two-sum --platform leetcode
```

See main [README.md](../README.md) for v2 documentation.

## License

For personal use only. Respect LeetCode's Terms of Service and rate limits.

______________________________________________________________________

## Documentation Index

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 60 seconds
- **[README.md](README.md)** - Full documentation (you are here)
- **[EXAMPLES.md](EXAMPLES.md)** - Detailed usage examples and workflows
- **[COMPARISON.md](COMPARISON.md)** - v1 vs v2 feature comparison
- **[MIGRATION.md](MIGRATION.md)** - Upgrade guide to v2

## Main Project

This is v1 - the simple script-based version. For the full-featured v2 with clean architecture:

- [Main README](../README.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Development Guide](../DEVELOPMENT.md)
