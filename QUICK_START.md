# Quick Start Guide

## 🚀 Fastest Way to Download All Your Solutions

### Step 1: Get Your Cookies (One-time setup)

1. Open Chrome and go to [LeetCode](https://leetcode.com) (make sure you're logged in)
2. Press `F12` to open Developer Tools
3. Go to **Application** tab → **Cookies** → `https://leetcode.com`
4. Copy these two values:
   - `LEETCODE_SESSION`
   - `csrftoken`

### Step 2: Set Environment Variables

```bash
export LEETCODE_SESSION='your-session-value-here'
export LEETCODE_CSRF='your-csrf-value-here'
```

### Step 3: Download Everything!

```bash
# From workspace root
python "Leet code/Crawler/batch_download_solutions.py"
```

That's it! All your solved problems will be downloaded to `Leet code/To-Revise/` 🎉

---

## 📋 What You Get

Each downloaded file contains:
- ✅ Your actual submitted code
- ✅ Full problem description (formatted)
- ✅ Examples and constraints
- ✅ Hints (if available)
- ✅ Performance stats (runtime, memory percentiles)

Example output:
```
Leet code/To-Revise/
├── two-sum.py
├── add-two-numbers.py
├── longest-substring-without-repeating-characters.py
├── median-of-two-sorted-arrays.py
└── ... (all your solved problems)
```

---

## 🔧 Common Options

### Download only recent problems
```bash
python "Leet code/Crawler/batch_download_solutions.py" --limit 50
```

### Safe to run multiple times (skips existing files automatically)
```bash
python "Leet code/Crawler/batch_download_solutions.py"
```

### Update files with newer submissions
```bash
python "Leet code/Crawler/batch_download_solutions.py" --update
```

### Force re-download (overwrite existing files)
```bash
python "Leet code/Crawler/batch_download_solutions.py" --force
```

### Include community solutions (slower)
```bash
python "Leet code/Crawler/batch_download_solutions.py" --with-solutions
```

### Custom output directory
```bash
python "Leet code/Crawler/batch_download_solutions.py" --output-dir "Leet code/My-Solutions"
```

---

## 📊 List Your Solved Problems

```bash
# Quick list
python "Leet code/Crawler/fetch_solved_problems.py"

# Export to markdown
python "Leet code/Crawler/fetch_solved_problems.py" --output progress.md --format md

# Get only URLs
python "Leet code/Crawler/fetch_solved_problems.py" --urls-only --output urls.txt
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Authentication required" | Check your cookies are set correctly |
| Cookies expired | Get fresh cookies from browser (they last 2-4 weeks) |
| Want to re-download | Use `--force` flag to overwrite existing files |
| Rate limited | Increase `--delay` (e.g., `--delay 2.0`) |

---

## 💡 Pro Tips

1. **Cookies last weeks** - Set them once and forget
2. **Safe to re-run** - Automatically skips existing files
3. **Default is fast** - Community solutions are opt-in
4. **Rate limiting** - Default 1s delay is safe, don't go below 0.5s
5. **Use `--force`** - Only when you want to refresh existing files

---

For more details, see [README.md](README.md)
