# LeetCode Crawler Project Structure

## 📁 Directory Layout

```
Leet code/
├── Crawler/                          # Main crawler toolkit
│   ├── leetcode_crawler.py           # Individual problem crawler
│   ├── fetch_solved_problems.py      # List solved problems
│   ├── batch_download_solutions.py   # Batch download all solutions (NEW!)
│   ├── requirements.txt              # Python dependencies
│   ├── README.md                     # Full documentation
│   ├── QUICK_START.md                # Quick start guide (NEW!)
│   ├── PROJECT_STRUCTURE.md          # This file (NEW!)
│   └── utils/                        # Reusable modules
│       ├── __init__.py
│       ├── leetcode_client.py        # LeetCode API client
│       └── formatters.py             # Text formatting utilities
│
├── To-Revise/                        # Downloaded solutions (NEW!)
│   ├── two-sum.py
│   ├── add-two-numbers.py
│   └── ... (all your solved problems)
│
└── leetcode_data/                    # Optional JSON exports
    └── *.json
```

## 🔧 Core Components

### 1. Utils Module (`utils/`)

**leetcode_client.py**
- `LeetCodeClient` class - Main API client
- Methods:
  - `fetch_problem()` - Get problem details
  - `fetch_solved_problems()` - Get user's solved problems
  - `fetch_all_problems_with_status()` - Get all problems with solve status
  - `get_last_accepted_submission()` - Get user's last submission
  - `fetch_official_solution()` - Get official solution (Premium)
  - `fetch_solution_articles()` - Get community solutions
  - `parse_problem()` - Parse and format problem data

**formatters.py**
- `clean_html()` - Remove HTML tags, preserve structure
- `wrap_text()` - Wrap text at specified width

### 2. Main Scripts

**leetcode_crawler.py**
- Crawls individual problems
- Extracts your submitted code
- Creates Python template files
- Optional JSON export
- Optional community solutions

**fetch_solved_problems.py**
- Lists all your solved problems
- Filter by difficulty
- Export to JSON/TXT/MD
- URLs-only mode for scripting

**batch_download_solutions.py** (NEW!)
- Downloads ALL solved problems at once
- Saves to `Leet code/To-Revise/`
- Resume capability
- Rate limiting
- Progress tracking

## 🎯 Use Cases

### Use Case 1: Quick Review
**Goal:** Download all solutions for interview prep

```bash
python "Leet code/Crawler/batch_download_solutions.py"
```

**Output:** All solutions in `Leet code/To-Revise/`

---

### Use Case 2: Track Progress
**Goal:** See what you've solved

```bash
python "Leet code/Crawler/fetch_solved_problems.py" --output progress.md --format md
```

**Output:** Markdown file with all solved problems

---

### Use Case 3: Specific Problem
**Goal:** Get one problem with community solutions

```bash
python "Leet code/Crawler/leetcode_crawler.py" "URL" --with-solutions
```

**Output:** Python file in `Leet code/` directory

---

### Use Case 4: Custom Scripting
**Goal:** Build your own automation

```bash
# Get URLs only
python "Leet code/Crawler/fetch_solved_problems.py" --urls-only --output urls.txt

# Process URLs with your script
while read url; do
  # Your custom logic here
done < urls.txt
```

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      LeetCode API                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   LeetCodeClient (utils)                    │
│  • Authentication                                           │
│  • API calls                                                │
│  • Data parsing                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Individual    │  │ List Solved      │  │ Batch Download   │
│ Crawler       │  │ Problems         │  │ All Solutions    │
│               │  │                  │  │                  │
│ • One problem │  │ • List/filter    │  │ • All problems   │
│ • Detailed    │  │ • Export         │  │ • Auto-save      │
│ • Custom path │  │ • URLs only      │  │ • Resume         │
└───────────────┘  └──────────────────┘  └──────────────────┘
        ↓                   ↓                   ↓
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Leet code/    │  │ progress.md      │  │ To-Revise/       │
│ problem.py    │  │ urls.txt         │  │ ├── problem1.py  │
│               │  │ solved.json      │  │ ├── problem2.py  │
└───────────────┘  └──────────────────┘  │ └── ...          │
                                         └──────────────────┘
```

## 🚀 Quick Commands Reference

```bash
# Setup (once)
export LEETCODE_SESSION='your-session'
export LEETCODE_CSRF='your-csrf'

# Download everything
python "Leet code/Crawler/batch_download_solutions.py"

# List solved problems
python "Leet code/Crawler/fetch_solved_problems.py"

# Get one problem
python "Leet code/Crawler/leetcode_crawler.py" "URL"

# Resume download
python "Leet code/Crawler/batch_download_solutions.py" --resume

# Export progress
python "Leet code/Crawler/fetch_solved_problems.py" --output progress.md --format md
```

## 📦 Dependencies

```
requests>=2.31.0
beautifulsoup4>=4.12.0
```

Install with:
```bash
pip install -r requirements.txt
```

## 🔐 Authentication

All scripts use environment variables for authentication:
- `LEETCODE_SESSION` - Session cookie
- `LEETCODE_CSRF` - CSRF token

These can also be passed via command-line arguments:
```bash
--session "your-session" --csrf "your-csrf"
```

## 📝 Output Formats

### Python Files
- Full problem description
- Your submitted code
- Performance stats
- Examples and constraints
- Hints

### JSON Files (optional)
- Complete problem data
- All metadata
- Solutions (if requested)

### Text/Markdown Files
- Problem lists
- URLs
- Progress tracking

## 🎓 Best Practices

1. **Set cookies once** - They last weeks
2. **Use batch download** - Fastest way to get everything
3. **Use `--resume`** - If interrupted
4. **Respect rate limits** - Default 1s delay is safe
5. **Keep cookies private** - Never commit to git

## 🔧 Extending the Toolkit

The modular design makes it easy to extend:

1. **Add new API methods** - Edit `utils/leetcode_client.py`
2. **Add new formatters** - Edit `utils/formatters.py`
3. **Create new scripts** - Import from `utils` module

Example:
```python
from utils.leetcode_client import LeetCodeClient

client = LeetCodeClient(session, csrf)
problems = client.fetch_solved_problems()
# Your custom logic here
```

## 📚 Documentation

- [README.md](README.md) - Complete documentation
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - This file

---

**Version:** 2.0  
**Last Updated:** January 2026  
**Author:** LeetCode Crawler Toolkit
