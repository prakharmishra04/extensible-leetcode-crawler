# LeetCode Crawler v1 - Usage Examples

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set authentication (required)
export LEETCODE_SESSION='your-session-cookie'
export LEETCODE_CSRF='your-csrf-token'
```

## Example 1: Download a Single Problem

```bash
# Basic download
python leetcode_crawler.py https://leetcode.com/problems/two-sum/

# Output: two-sum.py with your submission code
```

**Output file (`two-sum.py`):**

```python
"""
LeetCode Problem #1: Two Sum
Difficulty: Easy
Topics: Array, Hash Table

My Last Accepted Submission:
  Language: python3
  Runtime: 52 ms (beats 95.2%)
  Memory: 15.2 MB (beats 87.3%)
  Submitted: 2024-01-15

Problem Description:
Given an array of integers nums and an integer target, return indices of the
two numbers such that they add up to target...
"""


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your actual submission code here
        ...
```

## Example 2: List Your Solved Problems

```bash
# List recent 100 solved problems
python fetch_solved_problems.py

# Show detailed information
python fetch_solved_problems.py --details

# Get all problems with status
python fetch_solved_problems.py --all-with-status
```

**Output:**

```
✓ Authenticated session detected
✓ Fetching problems for user: prakhargreen16

================================================================================
Found 150 solved problems
================================================================================

1. Two Sum (two-sum)
2. Add Two Numbers (add-two-numbers)
3. Longest Substring Without Repeating Characters (longest-substring-without-repeating-characters)
...
```

## Example 3: Export Solved Problems

### As JSON

```bash
python fetch_solved_problems.py --output solved.json
```

**Output (`solved.json`):**

```json
[
  {
    "id": "1",
    "title": "Two Sum",
    "titleSlug": "two-sum",
    "timestamp": "1705334400"
  },
  ...
]
```

### As Markdown

```bash
python fetch_solved_problems.py --output solved.md --format md
```

**Output (`solved.md`):**

```markdown
# My Solved LeetCode Problems

Total: 150 problems

## 1. Two Sum

- **Difficulty:** Easy
- **Topics:** Array, Hash Table
- **Link:** [Two Sum](https://leetcode.com/problems/two-sum/)

## 2. Add Two Numbers

- **Difficulty:** Medium
- **Topics:** Linked List, Math, Recursion
- **Link:** [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/)
```

### As URL List

```bash
python fetch_solved_problems.py --output urls.txt --urls-only
```

**Output (`urls.txt`):**

```
https://leetcode.com/problems/two-sum/
https://leetcode.com/problems/add-two-numbers/
https://leetcode.com/problems/longest-substring-without-repeating-characters/
...
```

## Example 4: Batch Download All Solutions

### Basic Batch Download

```bash
python batch_download_solutions.py
```

**Output:**

```
✓ Output directory: /path/to/v1-scripts/LeetCode/To-Revise

Fetching your solved problems...
✓ Found 150 unique solved problems

================================================================================
Starting batch download of 150 problems
Output: /path/to/v1-scripts/LeetCode/To-Revise
Delay: 1.0s between requests
================================================================================

[1/150] Downloading two-sum... ✓
[2/150] Downloading add-two-numbers... ✓
[3/150] ⏭  Skipping longest-substring-without-repeating-characters (already exists)
...

================================================================================
Batch Download Complete!
================================================================================
  ✓ Success: 147
  ⏭  Skipped: 3
  Total:     150

Files saved to: /path/to/v1-scripts/LeetCode/To-Revise
================================================================================
```

### Custom Output Directory

```bash
python batch_download_solutions.py --output-dir "My-LeetCode-Solutions"
```

### Download Only Recent Problems

```bash
# Download only last 50 problems
python batch_download_solutions.py --limit 50
```

### Update Mode (Smart Refresh)

```bash
# Only update files with newer submissions
python batch_download_solutions.py --update
```

**Output:**

```
[1/150] Checking two-sum... ✓ (up to date)
[2/150] Checking add-two-numbers... 🔄 (newer submission found)
[2/150] Updating add-two-numbers... ✓
...

================================================================================
Batch Download Complete!
================================================================================
  ✓ Success: 5
  🔄 Updated: 5
  ⏭  Skipped: 145
  Total:     150
```

### Force Re-download

```bash
# Overwrite all existing files
python batch_download_solutions.py --force
```

### Faster Download (Adjust Delay)

```bash
# Reduce delay to 0.5 seconds (be careful with rate limits)
python batch_download_solutions.py --delay 0.5

# Increase delay to 2 seconds (safer for large batches)
python batch_download_solutions.py --delay 2.0
```

## Example 5: Include Community Solutions

```bash
# Download with community solutions (much slower)
python leetcode_crawler.py https://leetcode.com/problems/two-sum/ --with-solutions

# Batch download with solutions (not recommended for large batches)
python batch_download_solutions.py --with-solutions --limit 10
```

**Note:** Including community solutions significantly increases download time. Use sparingly.

## Example 6: Custom Authentication

If you don't want to use environment variables:

```bash
python leetcode_crawler.py https://leetcode.com/problems/two-sum/ \
  --session "your-session-cookie" \
  --csrf "your-csrf-token"

python batch_download_solutions.py \
  --session "your-session-cookie" \
  --csrf "your-csrf-token"
```

## Example 7: Workflow - Track Your Progress

### Step 1: Export your solved problems

```bash
python fetch_solved_problems.py --output progress-$(date +%Y%m%d).md --format md
```

### Step 2: Download all solutions

```bash
python batch_download_solutions.py --output-dir "Solutions-Backup"
```

### Step 3: Weekly updates

```bash
# Run this weekly to get new solutions
python batch_download_solutions.py --update --output-dir "Solutions-Backup"
```

## Example 8: Selective Downloads

### Download only Easy problems

```bash
# First, get all problems with status
python fetch_solved_problems.py --all-with-status --output all-problems.json

# Then manually filter and download specific problems
# (v1 doesn't have built-in difficulty filtering for batch downloads)
```

### Download specific problems from a list

```bash
# Create a file with URLs (one per line)
cat > my-problems.txt << EOF
https://leetcode.com/problems/two-sum/
https://leetcode.com/problems/add-two-numbers/
https://leetcode.com/problems/median-of-two-sorted-arrays/
EOF

# Download each one
while read url; do
  python leetcode_crawler.py "$url"
  sleep 1
done < my-problems.txt
```

## Common Workflows

### Workflow 1: First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set authentication
export LEETCODE_SESSION='...'
export LEETCODE_CSRF='...'

# 3. Download all your solutions
python batch_download_solutions.py

# 4. Export progress report
python fetch_solved_problems.py --output my-progress.md --format md
```

### Workflow 2: Daily Practice

```bash
# After solving a new problem, download it
python leetcode_crawler.py https://leetcode.com/problems/new-problem/
```

### Workflow 3: Weekly Sync

```bash
# Update any changed solutions
python batch_download_solutions.py --update

# Update progress report
python fetch_solved_problems.py --output progress-$(date +%Y%m%d).md --format md
```

### Workflow 4: Backup Everything

```bash
# Full backup with all metadata
python batch_download_solutions.py --force --output-dir "Backup-$(date +%Y%m%d)"
python fetch_solved_problems.py --all-with-status --output "all-problems-$(date +%Y%m%d).json"
```

## Tips

1. **Rate Limiting**: Always use appropriate delays to respect LeetCode's servers

   - Default 1.0s is safe for most use cases
   - Use 2.0s for large batches (100+ problems)
   - Avoid going below 0.5s

1. **Authentication**: Cookies expire after 2-4 weeks

   - Get fresh cookies when you see authentication errors
   - Store them in environment variables for convenience

1. **Resume Downloads**: By default, existing files are skipped

   - Use `--update` to refresh only changed files
   - Use `--force` to re-download everything

1. **Output Organization**:

   - Default directory: `LeetCode/To-Revise`
   - Use `--output-dir` for custom locations
   - Files are named by problem slug (e.g., `two-sum.py`)

1. **Community Solutions**: Only fetch when needed

   - Significantly increases download time
   - Use for specific problems, not batch downloads
