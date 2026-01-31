"""Test fixtures for mock API responses

This module provides mock API responses from various coding platforms.
Used for testing API clients and adapters without making real HTTP requests.
Covers common scenarios and edge cases as per Requirements 1.5.
"""

from typing import Any, Dict


def get_leetcode_problem_response() -> Dict[str, Any]:
    """Mock LeetCode GraphQL API response for fetching a problem"""
    return {
        "data": {
            "question": {
                "questionId": "1",
                "questionFrontendId": "1",
                "title": "Two Sum",
                "titleSlug": "two-sum",
                "difficulty": "Easy",
                "content": (
                    "<p>Given an array of integers <code>nums</code> and an integer "
                    "<code>target</code>, return <em>indices of the two numbers such that "
                    "they add up to <code>target</code></em>.</p>\n\n"
                    "<p>You may assume that each input would have <strong><em>exactly</em> "
                    "one solution</strong>, and you may not use the <em>same</em> element twice.</p>\n\n"
                    "<p>You can return the answer in any order.</p>\n\n"
                    "<p><strong>Example 1:</strong></p>\n"
                    "<pre>Input: nums = [2,7,11,15], target = 9\n"
                    "Output: [0,1]\n"
                    "Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].</pre>\n\n"
                    "<p><strong>Example 2:</strong></p>\n"
                    "<pre>Input: nums = [3,2,4], target = 6\n"
                    "Output: [1,2]</pre>\n\n"
                    "<p><strong>Example 3:</strong></p>\n"
                    "<pre>Input: nums = [3,3], target = 6\n"
                    "Output: [0,1]</pre>"
                ),
                "topicTags": [
                    {"name": "Array", "slug": "array"},
                    {"name": "Hash Table", "slug": "hash-table"},
                ],
                "hints": [
                    "A really brute force way would be to search for all possible pairs of numbers but that would be too slow.",
                    "Use a hash map to store the complement of each number as you iterate through the array.",
                ],
                "exampleTestcases": "nums = [2,7,11,15], target = 9\nnums = [3,2,4], target = 6\nnums = [3,3], target = 6",
                "constraints": (
                    "2 <= nums.length <= 10^4\n"
                    "-10^9 <= nums[i] <= 10^9\n"
                    "-10^9 <= target <= 10^9\n"
                    "Only one valid answer exists."
                ),
                "stats": '{"totalAccepted": "5.2M", "totalSubmission": "10.6M", "totalAcceptedRaw": 5200000, "totalSubmissionRaw": 10600000, "acRate": "49.1%"}',
            }
        }
    }


def get_leetcode_submission_response() -> Dict[str, Any]:
    """Mock LeetCode API response for fetching a submission"""
    return {
        "data": {
            "submissionDetails": {
                "id": "12345",
                "lang": "python3",
                "langName": "Python3",
                "code": """class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
""",
                "statusCode": 10,
                "statusDisplay": "Accepted",
                "runtime": "52 ms",
                "memory": "15.2 MB",
                "timestamp": "1704067200",
                "runtimePercentile": 85.3,
                "memoryPercentile": 72.1,
            }
        }
    }


def get_leetcode_user_profile_response() -> Dict[str, Any]:
    """Mock LeetCode API response for user profile"""
    return {
        "data": {
            "matchedUser": {
                "username": "testuser",
                "profile": {"realName": "Test User", "ranking": 12345},
                "submitStats": {
                    "acSubmissionNum": [
                        {"difficulty": "All", "count": 150, "submissions": 300},
                        {"difficulty": "Easy", "count": 80, "submissions": 120},
                        {"difficulty": "Medium", "count": 60, "submissions": 150},
                        {"difficulty": "Hard", "count": 10, "submissions": 30},
                    ]
                },
            }
        }
    }


def get_leetcode_solved_problems_response() -> Dict[str, Any]:
    """Mock LeetCode API response for user's solved problems"""
    return {
        "data": {
            "recentAcSubmissionList": [
                {"id": "1", "title": "Two Sum", "titleSlug": "two-sum", "timestamp": "1704067200"},
                {
                    "id": "2",
                    "title": "Add Two Numbers",
                    "titleSlug": "add-two-numbers",
                    "timestamp": "1704153600",
                },
                {
                    "id": "4",
                    "title": "Median of Two Sorted Arrays",
                    "titleSlug": "median-of-two-sorted-arrays",
                    "timestamp": "1704240000",
                },
            ]
        }
    }


def get_leetcode_community_solutions_response() -> Dict[str, Any]:
    """Mock LeetCode API response for community solutions"""
    return {
        "data": {
            "questionSolutions": {
                "solutions": [
                    {
                        "id": "sol-1",
                        "title": "Hash Map Solution - O(n) Time",
                        "content": "Detailed explanation...",
                        "voteCount": 1250,
                        "author": {"username": "expert_coder"},
                    },
                    {
                        "id": "sol-2",
                        "title": "Two Pointer Approach",
                        "content": "Alternative solution...",
                        "voteCount": 850,
                        "author": {"username": "algorithm_master"},
                    },
                ]
            }
        }
    }


def get_leetcode_error_response() -> Dict[str, Any]:
    """Mock LeetCode API error response"""
    return {"errors": [{"message": "Question not found", "extensions": {"code": "NOT_FOUND"}}]}


def get_leetcode_rate_limit_response() -> Dict[str, Any]:
    """Mock LeetCode API rate limit response"""
    return {
        "errors": [
            {
                "message": "Rate limit exceeded. Please try again later.",
                "extensions": {"code": "RATE_LIMIT_EXCEEDED"},
            }
        ]
    }


def get_leetcode_authentication_error_response() -> Dict[str, Any]:
    """Mock LeetCode API authentication error response"""
    return {
        "errors": [
            {
                "message": "You are not authorized to access this resource",
                "extensions": {"code": "UNAUTHORIZED"},
            }
        ]
    }


def get_hackerrank_problem_response() -> Dict[str, Any]:
    """Mock HackerRank API response for fetching a problem"""
    return {
        "model": {
            "id": 12345,
            "name": "Simple Array Sum",
            "slug": "simple-array-sum",
            "difficulty": "Easy",
            "body_html": (
                "<p>Given an array of integers, find the sum of its elements.</p>\n"
                "<p>For example, if the array <code>ar = [1,2,3]</code>, "
                "<code>1+2+3 = 6</code>, so return <code>6</code>.</p>"
            ),
            "track": {"name": "Algorithms", "slug": "algorithms"},
            "topics": [{"name": "Arrays"}, {"name": "Math"}],
            "success_ratio": 95.2,
            "total_count": 1000000,
        }
    }


def get_hackerrank_submission_response() -> Dict[str, Any]:
    """Mock HackerRank API response for fetching a submission"""
    return {
        "model": {
            "id": 67890,
            "challenge_id": 12345,
            "language": "python3",
            "code": "def simpleArraySum(ar):\n    return sum(ar)\n",
            "status": "Accepted",
            "time_taken": 0.05,
            "memory": 10240,
            "created_at": "2024-01-05T00:00:00Z",
        }
    }


def get_codechef_problem_response() -> Dict[str, Any]:
    """Mock CodeChef API response for fetching a problem"""
    return {
        "status": "success",
        "result": {
            "data": {
                "content": {
                    "problemCode": "TEST",
                    "problemName": "Life, the Universe, and Everything",
                    "difficulty": "Simple",
                    "body": (
                        "Your program is to use the brute-force approach in order to find "
                        "the Answer to Life, the Universe, and Everything. More precisely... "
                        "rewrite small numbers from input to output. Stop processing input "
                        "after reading in the number 42."
                    ),
                    "tags": ["basic-programming"],
                    "successfulSubmissions": 500000,
                    "totalSubmissions": 570000,
                }
            }
        },
    }


def get_codechef_submission_response() -> Dict[str, Any]:
    """Mock CodeChef API response for fetching a submission"""
    return {
        "status": "success",
        "result": {
            "data": {
                "content": {
                    "id": "54321",
                    "problemCode": "TEST",
                    "language": "PYTH 3.6",
                    "code": "while True:\n    n = int(input())\n    if n == 42:\n        break\n    print(n)\n",
                    "result": "AC",
                    "time": "0.00",
                    "memory": "5120",
                    "date": "2024-01-06T00:00:00Z",
                }
            }
        },
    }


def get_codeforces_problem_response() -> Dict[str, Any]:
    """Mock Codeforces API response for fetching a problem"""
    return {
        "status": "OK",
        "result": {
            "problems": [
                {
                    "contestId": 1,
                    "index": "A",
                    "name": "Theatre Square",
                    "type": "PROGRAMMING",
                    "rating": 1000,
                    "tags": ["math"],
                }
            ],
            "problemStatistics": [{"contestId": 1, "index": "A", "solvedCount": 100000}],
        },
    }


def get_codeforces_submission_response() -> Dict[str, Any]:
    """Mock Codeforces API response for fetching a submission"""
    return {
        "status": "OK",
        "result": [
            {
                "id": 98765,
                "contestId": 1,
                "problem": {"contestId": 1, "index": "A", "name": "Theatre Square"},
                "programmingLanguage": "Python 3",
                "verdict": "OK",
                "timeConsumedMillis": 100,
                "memoryConsumedBytes": 10485760,
                "creationTimeSeconds": 1704672000,
            }
        ],
    }


def get_empty_response() -> Dict[str, Any]:
    """Mock empty API response (edge case)"""
    return {"data": {}}


def get_malformed_response() -> Dict[str, Any]:
    """Mock malformed API response (edge case)"""
    return {"unexpected_field": "unexpected_value", "missing": "expected_fields"}


def get_partial_data_response() -> Dict[str, Any]:
    """Mock API response with partial/missing data (edge case)"""
    return {
        "data": {
            "question": {
                "questionId": "999",
                "title": "Incomplete Problem",
                # Missing many required fields
                "difficulty": "Medium",
            }
        }
    }


def get_network_timeout_response() -> Dict[str, Any]:
    """Mock response simulating network timeout (for testing error handling)"""
    return {"error": "Request timeout", "code": "TIMEOUT"}


def get_server_error_response() -> Dict[str, Any]:
    """Mock 500 Internal Server Error response"""
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred on the server",
        "code": 500,
    }


def get_leetcode_problem_with_no_hints_response() -> Dict[str, Any]:
    """Mock LeetCode response for a problem with no hints (edge case)"""
    return {
        "data": {
            "question": {
                "questionId": "7",
                "title": "Reverse Integer",
                "titleSlug": "reverse-integer",
                "difficulty": "Medium",
                "content": (
                    "<p>Given a signed 32-bit integer x, return x with its digits reversed.</p>\n\n"
                    "<p><strong>Example 1:</strong></p>\n"
                    "<pre>Input: x = 123\n"
                    "Output: 321</pre>\n\n"
                    "<p><strong>Example 2:</strong></p>\n"
                    "<pre>Input: x = -123\n"
                    "Output: -321</pre>\n\n"
                    "<p><strong>Example 3:</strong></p>\n"
                    "<pre>Input: x = 120\n"
                    "Output: 21</pre>"
                ),
                "topicTags": [{"name": "Math", "slug": "math"}],
                "hints": [],  # No hints
                "exampleTestcases": "x = 123\nx = -123\nx = 120",
                "constraints": "-2^31 <= x <= 2^31 - 1",
                "stats": '{"acRate": "27.5%"}',
            }
        }
    }


def get_leetcode_problem_with_many_examples_response() -> Dict[str, Any]:
    """Mock LeetCode response for a problem with many examples"""
    return {
        "data": {
            "question": {
                "questionId": "412",
                "title": "Fizz Buzz",
                "titleSlug": "fizz-buzz",
                "difficulty": "Easy",
                "content": (
                    "<p>Given an integer n, return a string array.</p>\n\n"
                    "<p><strong>Example 1:</strong></p>\n"
                    "<pre>Input: n = 3\n"
                    'Output: ["1","2","Fizz"]</pre>\n\n'
                    "<p><strong>Example 2:</strong></p>\n"
                    "<pre>Input: n = 5\n"
                    'Output: ["1","2","Fizz","4","Buzz"]</pre>\n\n'
                    "<p><strong>Example 3:</strong></p>\n"
                    "<pre>Input: n = 15\n"
                    'Output: ["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]</pre>\n\n'
                    "<p><strong>Example 4:</strong></p>\n"
                    "<pre>Input: n = 1\n"
                    'Output: ["1"]</pre>\n\n'
                    "<p><strong>Example 5:</strong></p>\n"
                    "<pre>Input: n = 100\n"
                    'Output: ["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz",...]</pre>'
                ),
                "topicTags": [
                    {"name": "Math", "slug": "math"},
                    {"name": "String", "slug": "string"},
                ],
                "hints": [],
                "exampleTestcases": ("n = 3\n" "n = 5\n" "n = 15\n" "n = 1\n" "n = 100"),
                "constraints": "1 <= n <= 10^4",
                "stats": '{"acRate": "98.7%"}',
            }
        }
    }


def get_leetcode_problem_with_html_content_response() -> Dict[str, Any]:
    """Mock LeetCode response with complex HTML content"""
    return {
        "data": {
            "question": {
                "questionId": "10",
                "title": "Regular Expression Matching",
                "titleSlug": "regular-expression-matching",
                "difficulty": "Hard",
                "content": (
                    "<p>Given an input string <code>s</code> and a pattern <code>p</code>, "
                    "implement regular expression matching with support for <code>'.'</code> "
                    "and <code>'*'</code>.</p>\n"
                    "<ul>\n"
                    "<li><code>'.'</code> Matches any single character.</li>\n"
                    "<li><code>'*'</code> Matches zero or more of the preceding element.</li>\n"
                    "</ul>\n"
                    "<p>The matching should cover the <strong>entire</strong> input string "
                    "(not partial).</p>"
                ),
                "topicTags": [
                    {"name": "String", "slug": "string"},
                    {"name": "Dynamic Programming", "slug": "dynamic-programming"},
                    {"name": "Recursion", "slug": "recursion"},
                ],
                "hints": ["Use dynamic programming.", "Consider the base cases carefully."],
                "exampleTestcases": 's = "aa", p = "a"\ns = "aa", p = "a*"\ns = "ab", p = ".*"',
                "constraints": (
                    "1 <= s.length <= 20\n"
                    "1 <= p.length <= 20\n"
                    "s contains only lowercase English letters.\n"
                    "p contains only lowercase English letters, '.', and '*'."
                ),
                "stats": '{"acRate": "12.4%"}',
            }
        }
    }


def get_api_responses_by_platform() -> Dict[str, Dict[str, Any]]:
    """Get all API responses organized by platform"""
    return {
        "leetcode": {
            "problem": get_leetcode_problem_response(),
            "submission": get_leetcode_submission_response(),
            "user_profile": get_leetcode_user_profile_response(),
            "solved_problems": get_leetcode_solved_problems_response(),
            "community_solutions": get_leetcode_community_solutions_response(),
            "error": get_leetcode_error_response(),
            "rate_limit": get_leetcode_rate_limit_response(),
            "auth_error": get_leetcode_authentication_error_response(),
            "no_hints": get_leetcode_problem_with_no_hints_response(),
            "many_examples": get_leetcode_problem_with_many_examples_response(),
            "html_content": get_leetcode_problem_with_html_content_response(),
        },
        "hackerrank": {
            "problem": get_hackerrank_problem_response(),
            "submission": get_hackerrank_submission_response(),
        },
        "codechef": {
            "problem": get_codechef_problem_response(),
            "submission": get_codechef_submission_response(),
        },
        "codeforces": {
            "problem": get_codeforces_problem_response(),
            "submission": get_codeforces_submission_response(),
        },
        "edge_cases": {
            "empty": get_empty_response(),
            "malformed": get_malformed_response(),
            "partial_data": get_partial_data_response(),
            "timeout": get_network_timeout_response(),
            "server_error": get_server_error_response(),
        },
    }
