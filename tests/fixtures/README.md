# Test Fixtures

This directory contains reusable test fixtures for the coding platform crawler project.

## Overview

Test fixtures provide sample data for testing without needing to make real API calls or create test data manually. They cover common scenarios and edge cases as specified in Requirements 1.5.

## Available Fixtures

### 1. Problem Fixtures (`problems.py`)

Sample Problem entities for various scenarios:

- **`create_easy_problem()`** - Two Sum (Easy difficulty)
- **`create_medium_problem()`** - Add Two Numbers (Medium difficulty)
- **`create_hard_problem()`** - Median of Two Sorted Arrays (Hard difficulty)
- **`create_problem_with_no_hints()`** - Problem without hints (edge case)
- **`create_problem_with_minimal_data()`** - Minimal required fields (edge case)
- **`create_problem_with_many_topics()`** - Problem with 10+ topics
- **`create_hackerrank_problem()`** - Sample from HackerRank platform
- **`create_codechef_problem()`** - Sample from CodeChef platform
- **`create_problem_with_high_acceptance()`** - 98.7% acceptance rate
- **`create_problem_with_low_acceptance()`** - 12.4% acceptance rate
- **`create_problems_list()`** - List of all sample problems

### 2. Submission Fixtures (`submissions.py`)

Sample Submission entities for various scenarios:

- **`create_python_submission()`** - Python3 submission with percentiles
- **`create_java_submission()`** - Java submission
- **`create_cpp_submission()`** - C++ submission
- **`create_javascript_submission()`** - JavaScript submission
- **`create_submission_without_percentiles()`** - No percentiles (edge case)
- **`create_submission_with_perfect_percentiles()`** - 100/100 percentiles
- **`create_submission_with_low_percentiles()`** - Low performance
- **`create_old_submission()`** - Old timestamp (2021)
- **`create_recent_submission()`** - Recent timestamp (2024)
- **`create_minimal_submission()`** - Minimal code
- **`create_long_submission()`** - Very long code
- **`create_wrong_answer_submission()`** - WRONG_ANSWER status
- **`create_time_limit_exceeded_submission()`** - TLE status
- **`create_runtime_error_submission()`** - Runtime error status
- **`create_submissions_list()`** - List of all sample submissions

### 3. API Response Fixtures (`api_responses.py`)

Mock API responses from various platforms:

#### LeetCode Responses

- **`get_leetcode_problem_response()`** - Problem query response
- **`get_leetcode_submission_response()`** - Submission details
- **`get_leetcode_user_profile_response()`** - User profile
- **`get_leetcode_solved_problems_response()`** - List of solved problems
- **`get_leetcode_community_solutions_response()`** - Community solutions
- **`get_leetcode_error_response()`** - Error response
- **`get_leetcode_rate_limit_response()`** - Rate limit error
- **`get_leetcode_authentication_error_response()`** - Auth error
- **`get_leetcode_problem_with_no_hints_response()`** - No hints
- **`get_leetcode_problem_with_many_examples_response()`** - Many examples
- **`get_leetcode_problem_with_html_content_response()`** - Complex HTML

#### Other Platforms

- **`get_hackerrank_problem_response()`** - HackerRank problem
- **`get_hackerrank_submission_response()`** - HackerRank submission
- **`get_codechef_problem_response()`** - CodeChef problem
- **`get_codechef_submission_response()`** - CodeChef submission
- **`get_codeforces_problem_response()`** - Codeforces problem
- **`get_codeforces_submission_response()`** - Codeforces submission

#### Edge Cases

- **`get_empty_response()`** - Empty response
- **`get_malformed_response()`** - Malformed data
- **`get_partial_data_response()`** - Missing fields
- **`get_network_timeout_response()`** - Timeout error
- **`get_server_error_response()`** - 500 error

#### Organized Access

- **`get_api_responses_by_platform()`** - All responses organized by platform

## Usage Examples

### Basic Usage

```python
from tests.fixtures import (
    create_easy_problem,
    create_python_submission,
    get_leetcode_problem_response,
)


# Use in tests
def test_problem_entity():
    problem = create_easy_problem()
    assert problem.title == "Two Sum"
    assert problem.difficulty.is_easy()


def test_submission_entity():
    submission = create_python_submission()
    assert submission.status == SubmissionStatus.ACCEPTED
    assert submission.percentiles.runtime > 80


def test_api_adapter():
    response = get_leetcode_problem_response()
    problem = adapter.adapt_problem(response)
    assert problem.title == "Two Sum"
```

### Testing Different Scenarios

```python
from tests.fixtures.problems import (
    create_problem_with_no_hints,
    create_problem_with_minimal_data,
    create_problems_list,
)


def test_problem_without_hints():
    """Test handling of problems with no hints"""
    problem = create_problem_with_no_hints()
    assert len(problem.hints) == 0


def test_minimal_problem():
    """Test handling of minimal required data"""
    problem = create_problem_with_minimal_data()
    assert problem.constraints == ""
    assert len(problem.hints) == 0


def test_batch_processing():
    """Test batch processing with multiple problems"""
    problems = create_problems_list()
    assert len(problems) == 8
    # Process all problems...
```

### Testing Edge Cases

```python
from tests.fixtures.submissions import (
    create_submission_without_percentiles,
    create_old_submission,
    create_recent_submission,
)


def test_submission_without_percentiles():
    """Test handling of submissions without percentiles"""
    submission = create_submission_without_percentiles()
    assert submission.percentiles is None


def test_update_mode_logic():
    """Test update mode with old vs recent submissions"""
    old = create_old_submission()
    recent = create_recent_submission()
    assert recent.timestamp > old.timestamp
    # Test update logic...
```

### Mocking API Responses

```python
from unittest.mock import Mock
from tests.fixtures.api_responses import (
    get_leetcode_problem_response,
    get_leetcode_error_response,
)


def test_successful_api_call():
    """Test successful API call"""
    mock_http = Mock()
    mock_http.post.return_value = Mock(json=lambda: get_leetcode_problem_response())
    # Use mock_http in client...


def test_api_error_handling():
    """Test API error handling"""
    mock_http = Mock()
    mock_http.post.return_value = Mock(json=lambda: get_leetcode_error_response())
    # Test error handling...
```

### Testing Multiple Platforms

```python
from tests.fixtures.api_responses import get_api_responses_by_platform


def test_all_platforms():
    """Test adapter works for all platforms"""
    responses = get_api_responses_by_platform()

    for platform, platform_responses in responses.items():
        if platform == "edge_cases":
            continue

        problem_response = platform_responses.get("problem")
        if problem_response:
            # Test platform-specific adapter...
            pass
```

## Design Principles

1. **Realistic Data**: Fixtures use realistic data from actual coding platforms
1. **Edge Cases**: Include edge cases like empty fields, extreme values, errors
1. **Variety**: Cover different difficulties, languages, platforms, statuses
1. **Reusability**: Easy to import and use across different test files
1. **Maintainability**: Well-organized and documented for easy updates

## Coverage

These fixtures support testing for:

- ✅ Domain entity validation
- ✅ Value object immutability
- ✅ API client implementations
- ✅ Adapter transformations
- ✅ Repository operations
- ✅ Use case business logic
- ✅ Error handling scenarios
- ✅ Edge cases and boundary conditions
- ✅ Multi-platform support
- ✅ Batch operations

## Adding New Fixtures

When adding new fixtures:

1. Follow the existing naming convention: `create_*` for entities, `get_*` for responses
1. Add comprehensive docstrings explaining the scenario
1. Include edge cases and error scenarios
1. Update this README with the new fixture
1. Export commonly used fixtures in `__init__.py`

## Related Documentation

- [Requirements Document](../../.kiro/specs/coding-platform-crawler-refactor/requirements.md)
- [Design Document](../../.kiro/specs/coding-platform-crawler-refactor/design.md)
- [Tasks Document](../../.kiro/specs/coding-platform-crawler-refactor/tasks.md)
