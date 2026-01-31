"""
Example: Fetch all LeetCode problems with their solve status

This example demonstrates how to use the new fetch_all_problems_with_status()
method to get a complete list of all LeetCode problems along with their
solve status (solved/attempted/not started).

This is more comprehensive than fetch_solved_problems() which only returns
recent submissions (typically 20-100 problems).
"""

import logging
import os
from typing import List

from crawler.config.logging_config import setup_logging
from crawler.config.settings import Config
from crawler.domain.entities import Problem
from crawler.infrastructure.http import HTTPClient, RateLimiter, RetryConfig
from crawler.infrastructure.platforms.leetcode import LeetCodeAdapter, LeetCodeClient

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Fetch all problems with their solve status."""
    # Get credentials from environment
    session_token = os.getenv("LEETCODE_SESSION")
    csrf_token = os.getenv("LEETCODE_CSRF")

    if not session_token:
        print("⚠️  Warning: LEETCODE_SESSION not set. Authentication required for status info.")
        print("Set environment variables:")
        print("  export LEETCODE_SESSION='your-session-token'")
        print("  export LEETCODE_CSRF='your-csrf-token'")
        return

    # Initialize components
    config = Config()
    config.leetcode_session_token = session_token
    config.leetcode_csrf_token = csrf_token

    retry_config = RetryConfig()
    rate_limiter = RateLimiter(requests_per_second=2.0)
    http_client = HTTPClient(retry_config, rate_limiter, logger)
    adapter = LeetCodeAdapter()

    # Create LeetCode client
    client = LeetCodeClient(http_client, adapter, config, logger)

    print("\n" + "=" * 80)
    print("Fetching ALL LeetCode problems with solve status...")
    print("=" * 80 + "\n")

    # Fetch all problems with status
    all_problems: List[Problem] = client.fetch_all_problems_with_status()

    # Categorize by status (note: status is not stored in Problem entity by default)
    # In a real implementation, you'd need to extend the Problem entity or use a different approach
    print(f"\n✅ Successfully fetched {len(all_problems)} problems\n")

    # Display statistics by difficulty
    easy = [p for p in all_problems if p.difficulty.level == "Easy"]
    medium = [p for p in all_problems if p.difficulty.level == "Medium"]
    hard = [p for p in all_problems if p.difficulty.level == "Hard"]

    print("📊 Problem Statistics by Difficulty:")
    print(f"  Easy:   {len(easy):4d} problems")
    print(f"  Medium: {len(medium):4d} problems")
    print(f"  Hard:   {len(hard):4d} problems")
    print(f"  Total:  {len(all_problems):4d} problems")

    # Display top 10 problems by acceptance rate
    print("\n🏆 Top 10 Problems by Acceptance Rate:")
    sorted_by_acceptance = sorted(all_problems, key=lambda p: p.acceptance_rate, reverse=True)
    for i, problem in enumerate(sorted_by_acceptance[:10], 1):
        print(
            f"  {i:2d}. {problem.title:50s} "
            f"({problem.difficulty.level:6s}) - {problem.acceptance_rate:.1f}%"
        )

    # Example: Fetch only solved problems
    print("\n" + "=" * 80)
    print("Fetching ONLY solved problems...")
    print("=" * 80 + "\n")

    solved_problems: List[Problem] = client.fetch_all_problems_with_status(status_filter="ac")
    print(f"✅ You have solved {len(solved_problems)} problems!\n")

    if solved_problems:
        print("📝 Your solved problems (first 10):")
        for i, problem in enumerate(solved_problems[:10], 1):
            print(
                f"  {i:2d}. {problem.title:50s} "
                f"({problem.difficulty.level:6s}) - {problem.acceptance_rate:.1f}%"
            )

        if len(solved_problems) > 10:
            print(f"  ... and {len(solved_problems) - 10} more")


if __name__ == "__main__":
    main()
