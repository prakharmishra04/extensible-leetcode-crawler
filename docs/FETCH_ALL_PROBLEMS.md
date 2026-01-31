# Fetching All Problems with Status

This guide explains how to use the `fetch_all_problems_with_status()` method to retrieve a complete list of all LeetCode problems along with their solve status.

## Overview

The LeetCode API provides two main ways to fetch problems:

1. **`fetch_solved_problems(username, limit)`** - Fetches recent solved problems using the `recentAcSubmissionList` API

   - ✅ Fast and lightweight
   - ❌ Limited to ~20-100 recent submissions
   - ❌ May not return all solved problems

1. **`fetch_all_problems_with_status(status_filter)`** - Fetches ALL problems using the `problemsetQuestionList` API

   - ✅ Complete list of all LeetCode problems
   - ✅ Includes solve status for each problem
   - ✅ Supports filtering by status
   - ❌ Slower (fetches all ~3000+ problems)

## When to Use Each Method

### Use `fetch_solved_problems()` when:

- You only need recent submissions
- You want faster execution
- You're downloading problems for practice

### Use `fetch_all_problems_with_status()` when:

- You need a complete list of all problems
- You want to see which problems you haven't attempted
- You're building statistics or analytics
- You need to compare solved vs. unsolved problems

## Usage Examples

### Example 1: Fetch All Problems

```python
from crawler.infrastructure.platforms.leetcode import LeetCodeClient

# Initialize client (see main README for setup)
client = LeetCodeClient(http_client, adapter, config, logger)

# Fetch all problems with their status
all_problems = client.fetch_all_problems_with_status()

print(f"Total problems: {len(all_problems)}")
```

### Example 2: Fetch Only Solved Problems

```python
# Fetch only problems you've solved
solved_problems = client.fetch_all_problems_with_status(status_filter="ac")

print(f"Solved: {len(solved_problems)} problems")
```

### Example 3: Fetch Only Attempted Problems

```python
# Fetch only problems you've attempted but not solved
attempted_problems = client.fetch_all_problems_with_status(status_filter="notac")

print(f"Attempted but not solved: {len(attempted_problems)}")
```

### Example 4: Categorize Problems by Status

```python
# Fetch all problems
all_problems = client.fetch_all_problems_with_status()

# Note: The Problem entity doesn't store status by default
# You'll need to extend it or use a different approach for categorization
# This is a simplified example

# Categorize by difficulty
easy = [p for p in all_problems if p.difficulty.level == "Easy"]
medium = [p for p in all_problems if p.difficulty.level == "Medium"]
hard = [p for p in all_problems if p.difficulty.level == "Hard"]

print(f"Easy: {len(easy)}, Medium: {len(medium)}, Hard: {len(hard)}")
```

## Status Filter Values

The `status_filter` parameter accepts the following values:

- `None` (default) - Returns all problems regardless of status
- `"ac"` or `"SOLVED"` - Returns only solved problems (accepted submissions)
- `"notac"` or `"ATTEMPTED"` - Returns only attempted but not solved problems

## Performance Considerations

### Pagination

The method automatically handles pagination, fetching problems in batches of 100:

```python
# This will make multiple API calls to fetch all problems
all_problems = client.fetch_all_problems_with_status()
# Typical execution time: 10-30 seconds for ~3000 problems
```

### Rate Limiting

The HTTP client includes built-in rate limiting to respect LeetCode's API limits:

```python
# Configure rate limiting (default: 2 requests/second)
rate_limiter = RateLimiter(requests_per_second=2.0)
http_client = HTTPClient(retry_config, rate_limiter, logger)
```

### Caching

For better performance, consider caching the results:

```python
import json
from pathlib import Path

# Fetch and cache
all_problems = client.fetch_all_problems_with_status()

# Save to cache
cache_file = Path("problems_cache.json")
with cache_file.open("w") as f:
    json.dump([p.to_dict() for p in all_problems], f)

# Load from cache
with cache_file.open("r") as f:
    cached_data = json.load(f)
```

## Comparison with v1 Scripts

This method provides the same functionality as the v1 `fetch_all_problems_with_status()` method:

### v1 (Legacy)

```python
# v1-scripts/utils/leetcode_client.py
client = LeetCodeClient(session_cookie, csrf_token)
all_problems = client.fetch_all_problems_with_status()
```

### v2 (Current)

```python
# src/crawler/infrastructure/platforms/leetcode/client.py
client = LeetCodeClient(http_client, adapter, config, logger)
all_problems = client.fetch_all_problems_with_status()
```

## Complete Example

See `examples/fetch_all_problems_example.py` for a complete working example that demonstrates:

- Fetching all problems with status
- Categorizing by difficulty
- Finding top problems by acceptance rate
- Filtering by solve status

## API Response Format

The method returns a list of `Problem` entities with the following fields:

```python
Problem(
    id="two-sum",  # Problem slug
    platform="leetcode",  # Platform name
    title="Two Sum",  # Problem title
    difficulty=Difficulty("Easy"),  # Difficulty level
    description="",  # Empty in list view
    topics=["Array", "Hash Table"],  # Topic tags
    constraints=[],  # Empty in list view
    examples=[],  # Empty in list view
    hints=[],  # Empty in list view
    acceptance_rate=49.1,  # Acceptance percentage
)
```

**Note:** The list view doesn't include full problem details (description, examples, constraints, hints). To get these, call `fetch_problem(problem_id)` for each problem.

## Error Handling

The method includes comprehensive error handling:

```python
try:
    all_problems = client.fetch_all_problems_with_status()
except Exception as e:
    logger.error(f"Failed to fetch problems: {e}")
    # Handle error appropriately
```

Common errors:

- **Network errors** - Automatic retry with exponential backoff
- **Authentication errors** - Check your session token
- **Rate limiting** - Built-in rate limiter prevents this

## Authentication

Authentication is required to see your solve status:

```bash
# Set environment variables
export LEETCODE_SESSION='your-session-token'
export LEETCODE_CSRF='your-csrf-token'
```

Without authentication, you'll still get all problems but without personalized status information.

## See Also

- [Main README](../README.md) - Getting started guide
- [Architecture Documentation](../ARCHITECTURE.md) - System design
- [API Reference](../docs/API_REFERENCE.md) - Complete API documentation
