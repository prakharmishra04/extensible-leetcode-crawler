# LeetCode Crawler

A Python toolkit to crawl LeetCode problems and manage your solutions.

## Features

- ✅ **Fetch YOUR last accepted submission** with performance stats
- ✅ Full problem description with proper formatting
- ✅ Examples, constraints, and hints
- ✅ Access official solutions (requires LeetCode Premium)
- ✅ Fetch top community solutions
- ✅ **List all your solved problems** with filtering options
- ✅ Optional JSON export

## Scripts

### 1. `leetcode_crawler.py` - Problem Crawler
Crawls individual LeetCode problems and extracts your solutions.

### 2. `fetch_solved_problems.py` - Solved Problems Lister
Lists all problems you've solved with filtering and export options.

### 3. `batch_download_solutions.py` - Batch Downloader (NEW!)
Downloads ALL your solved problems at once to `Leet code/To-Revise/` directory.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Session Cookies

Open Chrome → Go to [LeetCode](https://leetcode.com) (logged in) → Press `F12` → **Application** tab → **Cookies** → `https://leetcode.com`

Copy these two values:
- `LEETCODE_SESSION`
- `csrftoken`

### 3. Set Environment Variables

```bash
export LEETCODE_SESSION='your-session-value'
export LEETCODE_CSRF='your-csrf-value'
```

## Usage

### Batch Download All Solved Problems (Recommended!)

```bash
# Download ALL your solved problems to "Leet code/To-Revise/"
python "Leet code/Crawler/batch_download_solutions.py"

# Download only recent 50 problems
python "Leet code/Crawler/batch_download_solutions.py" --limit 50

# Include community solutions (slower)
python "Leet code/Crawler/batch_download_solutions.py" --with-solutions

# Safe to run multiple times - automatically skips existing files
python "Leet code/Crawler/batch_download_solutions.py"

# Update files with newer submissions (smart update)
python "Leet code/Crawler/batch_download_solutions.py" --update

# Force re-download (overwrite existing files)
python "Leet code/Crawler/batch_download_solutions.py" --force
```

### Crawl Individual Problems

```bash
# From workspace root
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/two-sum/"
```

**Output:** Creates `Leet code/two_sum.py` with your actual submitted code!

### List Your Solved Problems

```bash
# List recent solved problems (default: 100)
python "Leet code/Crawler/fetch_solved_problems.py"

# List more problems
python "Leet code/Crawler/fetch_solved_problems.py" --limit 200

# Filter by difficulty
python "Leet code/Crawler/fetch_solved_problems.py" --difficulty Easy
python "Leet code/Crawler/fetch_solved_problems.py" --difficulty Medium,Hard

# Save to file
python "Leet code/Crawler/fetch_solved_problems.py" --output solved.json --format json
python "Leet code/Crawler/fetch_solved_problems.py" --output solved.txt --format txt
python "Leet code/Crawler/fetch_solved_problems.py" --output solved.md --format md

# Get only URLs (one per line) - useful for custom scripts
python "Leet code/Crawler/fetch_solved_problems.py" --urls-only --output urls.txt

# Get ALL problems with solve status (slower)
python "Leet code/Crawler/fetch_solved_problems.py" --all-with-status
```

## Problem Crawler Examples

```bash
# Basic usage (creates Python file with your submission, no community solutions)
python "Leet code/Crawler/leetcode_crawler.py" "URL"

# Include community solutions (slower)
python "Leet code/Crawler/leetcode_crawler.py" "URL" --with-solutions

# Save JSON data (optional)
python "Leet code/Crawler/leetcode_crawler.py" "URL" --save-json

# Custom output filename
python "Leet code/Crawler/leetcode_crawler.py" "URL" --template "Leet code/my_solution.py"
```

## What Gets Created

### Problem Crawler Output

**By default:**
- ✅ Python file in `Leet code/` directory with:
  - Your last accepted submission code
  - Full problem description (formatted, wrapped at 78 chars)
  - Examples and constraints
  - Hints (if available)
  - Performance stats (runtime, memory percentiles)
- ❌ No JSON file (keeps directory clean)

**With `--save-json`:**
- ✅ Python file (as above)
- ✅ JSON file in `leetcode_data/` directory with complete problem data

### Solved Problems Lister Output

**Console output:**
```
Your Solved Problems (15 most recent):

#1. Two Sum [Easy]
    Topics: Array, Hash Table
    Solved: 2024-01-15
    URL: https://leetcode.com/problems/two-sum/

#2. Add Two Numbers [Medium]
    Topics: Linked List, Math, Recursion
    Solved: 2024-01-14
    URL: https://leetcode.com/problems/add-two-numbers/
...
```

**File formats:**
- JSON: Complete problem data with metadata
- TXT: Simple text list
- MD: Markdown formatted list

## Command Line Options

### leetcode_crawler.py

| Option | Description |
|--------|-------------|
| `--session` | LEETCODE_SESSION cookie value |
| `--csrf` | csrftoken cookie value |
| `--with-solutions` | Fetch community solutions (disabled by default) |
| `--no-my-submission` | Skip fetching your submission |
| `--save-json` | Save problem data as JSON (disabled by default) |
| `--json-dir` | Directory for JSON files (default: `leetcode_data`) |
| `-o, --output` | Custom JSON filename |
| `-t, --template` | Custom Python template filename |

### fetch_solved_problems.py

| Option | Description |
|--------|-------------|
| `--session` | LEETCODE_SESSION cookie value |
| `--csrf` | csrftoken cookie value |
| `--limit` | Number of recent problems to fetch (default: 100) |
| `--difficulty` | Filter by difficulty (Easy, Medium, Hard) |
| `--all-with-status` | Fetch ALL problems with solve status (slower) |
| `--urls-only` | Output only URLs (one per line, requires --output) |
| `--output` | Save to file |
| `--format` | Output format: json, txt, md (default: json) |

### batch_download_solutions.py

| Option | Description |
|--------|-------------|
| `--session` | LEETCODE_SESSION cookie value |
| `--csrf` | csrftoken cookie value |
| `--output-dir` | Output directory (default: Leet code/To-Revise) |
| `--with-solutions` | Include community solutions (slower) |
| `--limit` | Limit number of problems to download (default: all) |
| `--delay` | Delay between requests in seconds (default: 1.0) |
| `--resume` | Skip already downloaded files (default behavior) |
| `--update` | Update files if newer submission exists |
| `--force` | Force re-download even if files exist (overwrite) |

## Getting Cookies (Detailed)

### Chrome/Edge
1. Open LeetCode and log in
2. Press `F12` → **Application** tab
3. Left sidebar: **Storage** → **Cookies** → `https://leetcode.com`
4. Find `LEETCODE_SESSION` and `csrftoken`
5. Double-click the Value column to copy

### Firefox
1. Open LeetCode and log in
2. Press `F12` → **Storage** tab
3. **Cookies** → `https://leetcode.com`
4. Copy the cookie values

### Safari
1. Enable Developer menu: Preferences → Advanced → Show Develop menu
2. Develop → Show Web Inspector → Storage → Cookies
3. Copy the cookie values

## Example Workflows

### Workflow 1: Batch Download All Your Solutions (Easiest!)

```bash
# Set cookies once per session
export LEETCODE_SESSION='eyJhbGci...'
export LEETCODE_CSRF='ClNJNqrk...'

# Download everything to "Leet code/To-Revise/"
python "Leet code/Crawler/batch_download_solutions.py"

# Result: All your solved problems in one directory, ready to review!
```

### Workflow 2: Crawl Specific Problems

```bash
# Set cookies once per session
export LEETCODE_SESSION='eyJhbGci...'
export LEETCODE_CSRF='ClNJNqrk...'

# Crawl multiple problems (fast - no community solutions)
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/two-sum/"
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/add-two-numbers/"
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/reverse-integer/"

# Result: Clean Leet code/ directory with Python files containing your solutions!
```

### Workflow 2: Crawl Specific Problems

```bash
# Set cookies once per session
export LEETCODE_SESSION='eyJhbGci...'
export LEETCODE_CSRF='ClNJNqrk...'

# Crawl specific problems (fast - no community solutions)
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/two-sum/"
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/add-two-numbers/"
python "Leet code/Crawler/leetcode_crawler.py" "https://leetcode.com/problems/reverse-integer/"

# Result: Python files in Leet code/ directory with your solutions!
```

### Workflow 3: Review Your Progress

```bash
# List all solved problems
python "Leet code/Crawler/fetch_solved_problems.py" --limit 200

# Filter by difficulty
python "Leet code/Crawler/fetch_solved_problems.py" --difficulty Easy --limit 100

# Export to markdown for documentation
python "Leet code/Crawler/fetch_solved_problems.py" --output my_progress.md --format md
```

### Workflow 4: Smart Resume (Default Behavior)

```bash
# Run multiple times - it automatically skips existing files
python "Leet code/Crawler/batch_download_solutions.py"

# This is safe to run repeatedly - won't waste time re-downloading

# To force re-download (e.g., if you want fresh data)
python "Leet code/Crawler/batch_download_solutions.py" --force
```

### Workflow 5: Update After New Submissions

```bash
# You solved more problems or improved existing solutions
# Use --update to refresh only files with newer submissions
python "Leet code/Crawler/batch_download_solutions.py" --update

# This checks timestamps and only updates files with newer submissions
# Much faster than --force which re-downloads everything
```

## Output Example

Generated Python file includes:

```python
"""
LeetCode Problem #1: Two Sum
Difficulty: Easy
Topics: Array, Hash Table

My Last Accepted Submission:
  Language: python3
  Runtime: 52 ms (beats 89.5%)
  Memory: 15.2 MB (beats 76.3%)

Problem Description:
Given an array of integers nums and an integer target, return indices of the
two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may
not use the same element twice.

[Full description with examples, constraints, and hints...]
"""

# Your actual submitted code here
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your solution...
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No accepted submissions found" | You haven't solved this problem yet |
| "Authentication required" | Provide valid session cookies |
| "Premium subscription required" | Official solution needs LeetCode Premium |
| Cookies expired | Get fresh cookies from browser (they last 2-4 weeks) |

## Security

⚠️ **Keep your cookies private!**
- Never commit cookies to git
- Add `.env` to `.gitignore` (already done)
- Treat cookies like passwords

## Tips

1. **Cookies last weeks** - Set them once per terminal session
2. **Community solutions are opt-in** - Use `--with-solutions` only when needed
3. **JSON is optional** - Only use `--save-json` if you need raw data
4. **Files are gitignored** - `leetcode_data/` and `*.json` are in `.gitignore`

## License

For personal use only. Respect LeetCode's Terms of Service.
