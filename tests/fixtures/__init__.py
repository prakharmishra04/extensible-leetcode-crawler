"""Test fixtures package

This package provides reusable test fixtures for the coding platform crawler.
Includes sample entities, mock API responses, and helper functions for testing.

Usage:
    from tests.fixtures.problems import create_easy_problem, create_medium_problem
    from tests.fixtures.submissions import create_python_submission
    from tests.fixtures.api_responses import get_leetcode_problem_response
"""

# Import commonly used fixtures for convenience
from .problems import (
    create_easy_problem,
    create_medium_problem,
    create_hard_problem,
    create_problems_list,
)

from .submissions import (
    create_python_submission,
    create_java_submission,
    create_cpp_submission,
    create_submissions_list,
)

from .api_responses import (
    get_leetcode_problem_response,
    get_leetcode_submission_response,
    get_api_responses_by_platform,
)

__all__ = [
    # Problem fixtures
    "create_easy_problem",
    "create_medium_problem",
    "create_hard_problem",
    "create_problems_list",
    # Submission fixtures
    "create_python_submission",
    "create_java_submission",
    "create_cpp_submission",
    "create_submissions_list",
    # API response fixtures
    "get_leetcode_problem_response",
    "get_leetcode_submission_response",
    "get_api_responses_by_platform",
]
