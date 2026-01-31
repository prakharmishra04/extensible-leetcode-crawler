"""Test fixtures for Problem entities

This module provides sample Problem entities for use in tests.
Covers common scenarios and edge cases as per Requirements 1.5.
"""
from typing import List

from src.crawler.domain.entities.problem import Problem
from src.crawler.domain.value_objects.constraint import Constraint
from src.crawler.domain.value_objects.difficulty import Difficulty
from src.crawler.domain.value_objects.example import Example


def create_easy_problem() -> Problem:
    """Create a sample easy problem (Two Sum)"""
    return Problem(
        id="two-sum",
        platform="leetcode",
        title="Two Sum",
        difficulty=Difficulty("Easy"),
        description=(
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add up to target.\n\n"
            "You may assume that each input would have exactly one solution, "
            "and you may not use the same element twice.\n\n"
            "You can return the answer in any order."
        ),
        topics=["Array", "Hash Table"],
        constraints=[
            Constraint(text="2 <= nums.length <= 10^4"),
            Constraint(text="-10^9 <= nums[i] <= 10^9"),
            Constraint(text="-10^9 <= target <= 10^9"),
            Constraint(text="Only one valid answer exists."),
        ],
        examples=[
            Example(
                input="nums = [2,7,11,15], target = 9",
                output="[0,1]",
                explanation="Because nums[0] + nums[1] == 9, we return [0, 1].",
            ),
            Example(
                input="nums = [3,2,4], target = 6",
                output="[1,2]",
                explanation="Because nums[1] + nums[2] == 6, we return [1, 2].",
            ),
            Example(
                input="nums = [3,3], target = 6",
                output="[0,1]",
                explanation="Because nums[0] + nums[1] == 6, we return [0, 1].",
            ),
        ],
        hints=[
            "A really brute force way would be to search for all possible pairs of numbers but that would be too slow.",
            "Use a hash map to store the complement of each number as you iterate through the array.",
        ],
        acceptance_rate=49.1,
    )


def create_medium_problem() -> Problem:
    """Create a sample medium problem (Add Two Numbers)"""
    return Problem(
        id="add-two-numbers",
        platform="leetcode",
        title="Add Two Numbers",
        difficulty=Difficulty("Medium"),
        description=(
            "You are given two non-empty linked lists representing two non-negative integers. "
            "The digits are stored in reverse order, and each of their nodes contains a single digit. "
            "Add the two numbers and return the sum as a linked list.\n\n"
            "You may assume the two numbers do not contain any leading zero, except the number 0 itself."
        ),
        topics=["Linked List", "Math", "Recursion"],
        constraints=[
            Constraint(text="The number of nodes in each linked list is in the range [1, 100]."),
            Constraint(text="0 <= Node.val <= 9"),
            Constraint(
                text="It is guaranteed that the list represents a number that does not have leading zeros."
            ),
        ],
        examples=[
            Example(
                input="l1 = [2,4,3], l2 = [5,6,4]", output="[7,0,8]", explanation="342 + 465 = 807."
            ),
            Example(input="l1 = [0], l2 = [0]", output="[0]", explanation="0 + 0 = 0."),
            Example(
                input="l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]",
                output="[8,9,9,9,0,0,0,1]",
                explanation="9999999 + 9999 = 10009998.",
            ),
        ],
        hints=[
            "Think about how you would add two numbers on paper.",
            "Don't forget to handle the carry when the sum is greater than 9.",
        ],
        acceptance_rate=41.2,
    )


def create_hard_problem() -> Problem:
    """Create a sample hard problem (Median of Two Sorted Arrays)"""
    return Problem(
        id="median-of-two-sorted-arrays",
        platform="leetcode",
        title="Median of Two Sorted Arrays",
        difficulty=Difficulty("Hard"),
        description=(
            "Given two sorted arrays nums1 and nums2 of size m and n respectively, "
            "return the median of the two sorted arrays.\n\n"
            "The overall run time complexity should be O(log (m+n))."
        ),
        topics=["Array", "Binary Search", "Divide and Conquer"],
        constraints=[
            Constraint(text="nums1.length == m"),
            Constraint(text="nums2.length == n"),
            Constraint(text="0 <= m <= 1000"),
            Constraint(text="0 <= n <= 1000"),
            Constraint(text="1 <= m + n <= 2000"),
            Constraint(text="-10^6 <= nums1[i], nums2[i] <= 10^6"),
        ],
        examples=[
            Example(
                input="nums1 = [1,3], nums2 = [2]",
                output="2.00000",
                explanation="merged array = [1,2,3] and median is 2.",
            ),
            Example(
                input="nums1 = [1,2], nums2 = [3,4]",
                output="2.50000",
                explanation="merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.",
            ),
        ],
        hints=[
            "Use binary search to partition the arrays.",
            "The key is to find the correct partition point.",
        ],
        acceptance_rate=37.8,
    )


def create_problem_with_no_hints() -> Problem:
    """Create a problem with no hints (edge case)"""
    return Problem(
        id="reverse-integer",
        platform="leetcode",
        title="Reverse Integer",
        difficulty=Difficulty("Medium"),
        description=(
            "Given a signed 32-bit integer x, return x with its digits reversed. "
            "If reversing x causes the value to go outside the signed 32-bit integer range "
            "[-2^31, 2^31 - 1], then return 0."
        ),
        topics=["Math"],
        constraints=[Constraint(text="-2^31 <= x <= 2^31 - 1")],
        examples=[
            Example(input="x = 123", output="321", explanation=None),
            Example(input="x = -123", output="-321", explanation=None),
            Example(input="x = 120", output="21", explanation=None),
        ],
        hints=[],  # No hints
        acceptance_rate=27.5,
    )


def create_problem_with_minimal_data() -> Problem:
    """Create a problem with minimal required data (edge case)"""
    return Problem(
        id="minimal-problem",
        platform="leetcode",
        title="Minimal Problem",
        difficulty=Difficulty("Easy"),
        description="A minimal problem description.",
        topics=["Array"],
        constraints=[],  # Empty constraints
        examples=[Example(input="[1,2,3]", output="6", explanation=None)],
        hints=[],
        acceptance_rate=50.0,
    )


def create_problem_with_many_topics() -> Problem:
    """Create a problem with many topics"""
    return Problem(
        id="complex-problem",
        platform="leetcode",
        title="Complex Problem",
        difficulty=Difficulty("Hard"),
        description="A complex problem with many topics.",
        topics=[
            "Array",
            "Hash Table",
            "Linked List",
            "Math",
            "Two Pointers",
            "String",
            "Binary Search",
            "Divide and Conquer",
            "Dynamic Programming",
            "Backtracking",
        ],
        constraints=[Constraint(text="Complex constraints here.")],
        examples=[Example(input="input1", output="output1", explanation="explanation1")],
        hints=["Hint 1", "Hint 2", "Hint 3", "Hint 4", "Hint 5"],
        acceptance_rate=15.3,
    )


def create_hackerrank_problem() -> Problem:
    """Create a sample problem from HackerRank platform"""
    return Problem(
        id="simple-array-sum",
        platform="hackerrank",
        title="Simple Array Sum",
        difficulty=Difficulty("Easy"),
        description=(
            "Given an array of integers, find the sum of its elements.\n\n"
            "For example, if the array ar = [1,2,3], 1+2+3 = 6, so return 6."
        ),
        topics=["Array", "Math"],
        constraints=[Constraint(text="0 < n <= 1000"), Constraint(text="0 < ar[i] <= 1000")],
        examples=[
            Example(
                input="6\n1 2 3 4 10 11",
                output="31",
                explanation="We print the sum of the array's elements: 1+2+3+4+10+11 = 31.",
            )
        ],
        hints=[],
        acceptance_rate=95.2,
    )


def create_codechef_problem() -> Problem:
    """Create a sample problem from CodeChef platform"""
    return Problem(
        id="life-universe-everything",
        platform="codechef",
        title="Life, the Universe, and Everything",
        difficulty=Difficulty("Easy"),
        description=(
            "Your program is to use the brute-force approach in order to find the Answer to Life, "
            "the Universe, and Everything. More precisely... rewrite small numbers from input to output. "
            "Stop processing input after reading in the number 42. All numbers at input are integers "
            "of one or two digits."
        ),
        topics=["Basic Programming"],
        constraints=[Constraint(text="1 <= input <= 99")],
        examples=[
            Example(
                input="1\n2\n88\n42\n99",
                output="1\n2\n88",
                explanation="Stop at 42 and don't print it or anything after.",
            )
        ],
        hints=[],
        acceptance_rate=87.6,
    )


def create_problems_list() -> List[Problem]:
    """Create a list of sample problems for batch testing"""
    return [
        create_easy_problem(),
        create_medium_problem(),
        create_hard_problem(),
        create_problem_with_no_hints(),
        create_problem_with_minimal_data(),
        create_problem_with_many_topics(),
        create_hackerrank_problem(),
        create_codechef_problem(),
    ]


def create_problem_with_high_acceptance() -> Problem:
    """Create a problem with very high acceptance rate (edge case)"""
    return Problem(
        id="fizz-buzz",
        platform="leetcode",
        title="Fizz Buzz",
        difficulty=Difficulty("Easy"),
        description=(
            "Given an integer n, return a string array answer (1-indexed) where:\n"
            "- answer[i] == 'FizzBuzz' if i is divisible by 3 and 5.\n"
            "- answer[i] == 'Fizz' if i is divisible by 3.\n"
            "- answer[i] == 'Buzz' if i is divisible by 5.\n"
            "- answer[i] == i (as a string) if none of the above conditions are true."
        ),
        topics=["Math", "String", "Simulation"],
        constraints=[Constraint(text="1 <= n <= 10^4")],
        examples=[
            Example(input="n = 3", output='["1","2","Fizz"]', explanation=None),
            Example(input="n = 5", output='["1","2","Fizz","4","Buzz"]', explanation=None),
            Example(
                input="n = 15",
                output='["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]',
                explanation=None,
            ),
        ],
        hints=[],
        acceptance_rate=98.7,
    )


def create_problem_with_low_acceptance() -> Problem:
    """Create a problem with very low acceptance rate (edge case)"""
    return Problem(
        id="regular-expression-matching",
        platform="leetcode",
        title="Regular Expression Matching",
        difficulty=Difficulty("Hard"),
        description=(
            "Given an input string s and a pattern p, implement regular expression matching "
            "with support for '.' and '*' where:\n"
            "- '.' Matches any single character.\n"
            "- '*' Matches zero or more of the preceding element.\n"
            "The matching should cover the entire input string (not partial)."
        ),
        topics=["String", "Dynamic Programming", "Recursion"],
        constraints=[
            Constraint(text="1 <= s.length <= 20"),
            Constraint(text="1 <= p.length <= 20"),
            Constraint(text="s contains only lowercase English letters."),
            Constraint(text="p contains only lowercase English letters, '.', and '*'."),
        ],
        examples=[
            Example(
                input='s = "aa", p = "a"',
                output="false",
                explanation='"a" does not match the entire string "aa".',
            ),
            Example(
                input='s = "aa", p = "a*"',
                output="true",
                explanation='"*" means zero or more of the preceding element, "a".',
            ),
            Example(
                input='s = "ab", p = ".*"',
                output="true",
                explanation='".*" means "zero or more (*) of any character (.)".',
            ),
        ],
        hints=["Use dynamic programming.", "Consider the base cases carefully."],
        acceptance_rate=12.4,
    )
