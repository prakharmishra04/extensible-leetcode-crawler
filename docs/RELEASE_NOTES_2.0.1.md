# Release Notes - Version 2.0.1

**Release Date:** January 31, 2026

## Overview

This patch release addresses a critical limitation in v2.0.0 where the `fetch_solved_problems()` method could only retrieve recent submissions (typically 20-100 problems), while v1 scripts could fetch all problems with their solve status.

## What's New

### New Method: `fetch_all_problems_with_status()`

A comprehensive method that fetches ALL LeetCode problems (3000+) along with their solve status using the `problemsetQuestionList` GraphQL API.

**Key Features:**

- ✅ Complete list of all LeetCode problems
- ✅ Solve status for each problem (solved/attempted/not started)
- ✅ Optional filtering by status
- ✅ Automatic pagination handling
- ✅ Built-in rate limiting and retry logic

**Usage:**

```python
# Fetch all problems
all_problems = client.fetch_all_problems_with_status()

# Fetch only solved problems
solved = client.fetch_all_problems_with_status(status_filter="ac")

# Fetch only attempted problems
attempted = client.fetch_all_problems_with_status(status_filter="notac")
```

### New Adapter Method: `adapt_problem_from_list()`

A lightweight adapter method that converts `problemsetQuestionList` API responses to `Problem` entities. This is optimized for list views where full problem details (description, examples, constraints) are not needed.

## Bug Fixes

- **Fixed incomplete problem fetching** - v2 can now fetch all problems like v1
- **Enhanced documentation** - Updated `fetch_solved_problems()` to reference the new comprehensive method

## Documentation

### New Documentation Files

1. **`docs/FETCH_ALL_PROBLEMS.md`** - Comprehensive guide on using the new method

   - Usage examples
   - Performance considerations
   - Comparison with v1
   - API response format

1. **`examples/fetch_all_problems_example.py`** - Complete working example

   - Fetching all problems
   - Categorizing by difficulty
   - Finding top problems by acceptance rate
   - Filtering by solve status

## Migration Guide

### From v1 to v2.0.1

**v1 (Legacy):**

```python
from utils.leetcode_client import LeetCodeClient

client = LeetCodeClient(session_cookie, csrf_token)
all_problems = client.fetch_all_problems_with_status()
```

**v2.0.1 (Current):**

```python
from crawler.infrastructure.platforms.leetcode import LeetCodeClient

client = LeetCodeClient(http_client, adapter, config, logger)
all_problems = client.fetch_all_problems_with_status()
```

### Choosing the Right Method

| Method                             | Use Case                          | Speed | Coverage |
| ---------------------------------- | --------------------------------- | ----- | -------- |
| `fetch_solved_problems()`          | Recent submissions for download   | Fast  | Limited  |
| `fetch_all_problems_with_status()` | Complete problem list & analytics | Slow  | Complete |

## Performance Impact

- **Execution Time:** 10-30 seconds for ~3000 problems
- **API Calls:** Multiple paginated requests (100 problems per request)
- **Rate Limiting:** Built-in 2 requests/second limit (configurable)

## Breaking Changes

None. This is a backward-compatible patch release.

## Testing

- ✅ All 618 existing tests pass
- ✅ No new test failures
- ✅ Code coverage maintained at 89%

## Installation

### From PyPI (when released)

```bash
pip install --upgrade coding-platform-crawler
```

### From Source

```bash
git clone https://github.com/prakharmishra04/extensible-leetcode-crawler.git
cd extensible-leetcode-crawler
git checkout v2.0.1
pip install -e .
```

## What's Next

Future enhancements being considered:

- Caching mechanism for problem lists
- Incremental updates (fetch only new/changed problems)
- Export to various formats (CSV, Excel, etc.)
- Integration with other coding platforms

## Feedback

If you encounter any issues or have suggestions, please:

- Open an issue: https://github.com/prakharmishra04/extensible-leetcode-crawler/issues
- Submit a PR: https://github.com/prakharmishra04/extensible-leetcode-crawler/pulls

## Acknowledgments

Thanks to the community for reporting the limitation and helping improve the project!

______________________________________________________________________

**Full Changelog:** https://github.com/prakharmishra04/extensible-leetcode-crawler/blob/main/CHANGELOG.md
