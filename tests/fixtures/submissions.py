"""Test fixtures for Submission entities

This module provides sample Submission entities for use in tests.
Covers common scenarios and edge cases as per Requirements 1.5.
"""
from typing import List
from src.crawler.domain.entities.submission import Submission
from src.crawler.domain.entities.enums import SubmissionStatus
from src.crawler.domain.value_objects.percentiles import Percentiles


def create_python_submission() -> Submission:
    """Create a sample Python submission for Two Sum"""
    return Submission(
        id="sub-12345",
        problem_id="two-sum",
        language="Python3",
        code='''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """
        Find two numbers that add up to target using hash map.
        Time: O(n), Space: O(n)
        """
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="52 ms",
        memory="15.2 MB",
        timestamp=1704067200,  # 2024-01-01 00:00:00 UTC
        percentiles=Percentiles(runtime=85.3, memory=72.1)
    )


def create_java_submission() -> Submission:
    """Create a sample Java submission"""
    return Submission(
        id="sub-23456",
        problem_id="add-two-numbers",
        language="Java",
        code='''/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;
        int carry = 0;
        
        while (l1 != null || l2 != null || carry != 0) {
            int sum = carry;
            if (l1 != null) {
                sum += l1.val;
                l1 = l1.next;
            }
            if (l2 != null) {
                sum += l2.val;
                l2 = l2.next;
            }
            
            carry = sum / 10;
            current.next = new ListNode(sum % 10);
            current = current.next;
        }
        
        return dummy.next;
    }
}
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="2 ms",
        memory="44.1 MB",
        timestamp=1704153600,  # 2024-01-02 00:00:00 UTC
        percentiles=Percentiles(runtime=95.7, memory=68.4)
    )


def create_cpp_submission() -> Submission:
    """Create a sample C++ submission"""
    return Submission(
        id="sub-34567",
        problem_id="median-of-two-sorted-arrays",
        language="C++",
        code='''class Solution {
public:
    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {
        if (nums1.size() > nums2.size()) {
            return findMedianSortedArrays(nums2, nums1);
        }
        
        int m = nums1.size();
        int n = nums2.size();
        int left = 0, right = m;
        
        while (left <= right) {
            int partitionX = (left + right) / 2;
            int partitionY = (m + n + 1) / 2 - partitionX;
            
            int maxLeftX = (partitionX == 0) ? INT_MIN : nums1[partitionX - 1];
            int minRightX = (partitionX == m) ? INT_MAX : nums1[partitionX];
            
            int maxLeftY = (partitionY == 0) ? INT_MIN : nums2[partitionY - 1];
            int minRightY = (partitionY == n) ? INT_MAX : nums2[partitionY];
            
            if (maxLeftX <= minRightY && maxLeftY <= minRightX) {
                if ((m + n) % 2 == 0) {
                    return (max(maxLeftX, maxLeftY) + min(minRightX, minRightY)) / 2.0;
                } else {
                    return max(maxLeftX, maxLeftY);
                }
            } else if (maxLeftX > minRightY) {
                right = partitionX - 1;
            } else {
                left = partitionX + 1;
            }
        }
        
        throw invalid_argument("Input arrays are not sorted");
    }
};
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="16 ms",
        memory="89.3 MB",
        timestamp=1704240000,  # 2024-01-03 00:00:00 UTC
        percentiles=Percentiles(runtime=78.9, memory=55.2)
    )


def create_javascript_submission() -> Submission:
    """Create a sample JavaScript submission"""
    return Submission(
        id="sub-45678",
        problem_id="reverse-integer",
        language="JavaScript",
        code='''/**
 * @param {number} x
 * @return {number}
 */
var reverse = function(x) {
    const INT_MAX = 2147483647;
    const INT_MIN = -2147483648;
    
    let result = 0;
    let num = Math.abs(x);
    
    while (num !== 0) {
        const digit = num % 10;
        num = Math.floor(num / 10);
        
        // Check for overflow before multiplying
        if (result > Math.floor(INT_MAX / 10)) {
            return 0;
        }
        
        result = result * 10 + digit;
    }
    
    result = x < 0 ? -result : result;
    
    // Final overflow check
    if (result < INT_MIN || result > INT_MAX) {
        return 0;
    }
    
    return result;
};
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="68 ms",
        memory="43.7 MB",
        timestamp=1704326400,  # 2024-01-04 00:00:00 UTC
        percentiles=Percentiles(runtime=62.4, memory=81.3)
    )


def create_submission_without_percentiles() -> Submission:
    """Create a submission without percentiles (edge case)"""
    return Submission(
        id="sub-56789",
        problem_id="fizz-buzz",
        language="Python3",
        code='''class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        result = []
        for i in range(1, n + 1):
            if i % 15 == 0:
                result.append("FizzBuzz")
            elif i % 3 == 0:
                result.append("Fizz")
            elif i % 5 == 0:
                result.append("Buzz")
            else:
                result.append(str(i))
        return result
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="45 ms",
        memory="14.8 MB",
        timestamp=1704412800,  # 2024-01-05 00:00:00 UTC
        percentiles=None  # No percentiles
    )


def create_submission_with_perfect_percentiles() -> Submission:
    """Create a submission with perfect percentiles (edge case)"""
    return Submission(
        id="sub-67890",
        problem_id="simple-array-sum",
        language="Python3",
        code='''def simpleArraySum(ar):
    return sum(ar)
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="1 ms",
        memory="10.0 MB",
        timestamp=1704499200,  # 2024-01-06 00:00:00 UTC
        percentiles=Percentiles(runtime=100.0, memory=100.0)
    )


def create_submission_with_low_percentiles() -> Submission:
    """Create a submission with low percentiles (edge case)"""
    return Submission(
        id="sub-78901",
        problem_id="regular-expression-matching",
        language="Python3",
        code='''class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        # Brute force recursive solution (slow)
        if not p:
            return not s
        
        first_match = bool(s) and p[0] in {s[0], '.'}
        
        if len(p) >= 2 and p[1] == '*':
            return (self.isMatch(s, p[2:]) or
                    first_match and self.isMatch(s[1:], p))
        else:
            return first_match and self.isMatch(s[1:], p[1:])
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="5000 ms",
        memory="200.0 MB",
        timestamp=1704585600,  # 2024-01-07 00:00:00 UTC
        percentiles=Percentiles(runtime=5.2, memory=8.7)
    )


def create_old_submission() -> Submission:
    """Create an old submission (for testing update mode)"""
    return Submission(
        id="sub-old-001",
        problem_id="two-sum",
        language="Python3",
        code='''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Old brute force solution
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="5000 ms",
        memory="14.0 MB",
        timestamp=1609459200,  # 2021-01-01 00:00:00 UTC (old)
        percentiles=Percentiles(runtime=10.5, memory=45.2)
    )


def create_recent_submission() -> Submission:
    """Create a recent submission (for testing update mode)"""
    return Submission(
        id="sub-new-001",
        problem_id="two-sum",
        language="Python3",
        code='''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Optimized hash map solution
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
''',
        status=SubmissionStatus.ACCEPTED,
        runtime="48 ms",
        memory="15.1 MB",
        timestamp=1704672000,  # 2024-01-08 00:00:00 UTC (recent)
        percentiles=Percentiles(runtime=88.5, memory=75.3)
    )


def create_minimal_submission() -> Submission:
    """Create a submission with minimal code (edge case)"""
    return Submission(
        id="sub-minimal",
        problem_id="minimal-problem",
        language="Python3",
        code="return sum(nums)",
        status=SubmissionStatus.ACCEPTED,
        runtime="1 ms",
        memory="10.0 MB",
        timestamp=1704758400,  # 2024-01-09 00:00:00 UTC
        percentiles=Percentiles(runtime=99.0, memory=95.0)
    )


def create_long_submission() -> Submission:
    """Create a submission with very long code"""
    long_code = '''class Solution:
    def complexAlgorithm(self, data):
        """
        A very long and complex algorithm implementation.
        This is used to test handling of large code submissions.
        """
        # Initialize data structures
        result = []
        cache = {}
        visited = set()
        
        # Helper function 1
        def helper1(x):
            if x in cache:
                return cache[x]
            # Complex computation
            value = x * 2 + 1
            cache[x] = value
            return value
        
        # Helper function 2
        def helper2(y):
            if y in visited:
                return False
            visited.add(y)
            return True
        
        # Main algorithm
        for i in range(len(data)):
            if helper2(i):
                temp = helper1(data[i])
                result.append(temp)
        
        # Post-processing
        result.sort()
        result = list(set(result))
        
        # More processing steps...
        ''' + '\n        # Step ' + '\n        # Step '.join([str(i) for i in range(100)]) + '''
        
        return result
'''
    
    return Submission(
        id="sub-long",
        problem_id="complex-problem",
        language="Python3",
        code=long_code,
        status=SubmissionStatus.ACCEPTED,
        runtime="150 ms",
        memory="25.5 MB",
        timestamp=1704844800,  # 2024-01-10 00:00:00 UTC
        percentiles=Percentiles(runtime=45.8, memory=52.3)
    )


def create_submissions_list() -> List[Submission]:
    """Create a list of sample submissions for batch testing"""
    return [
        create_python_submission(),
        create_java_submission(),
        create_cpp_submission(),
        create_javascript_submission(),
        create_submission_without_percentiles(),
        create_submission_with_perfect_percentiles(),
        create_submission_with_low_percentiles(),
        create_old_submission(),
        create_recent_submission(),
        create_minimal_submission(),
        create_long_submission()
    ]


def create_wrong_answer_submission() -> Submission:
    """Create a submission with WRONG_ANSWER status (for testing error cases)"""
    return Submission(
        id="sub-wrong",
        problem_id="two-sum",
        language="Python3",
        code='''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Incorrect implementation
        return [0, 1]  # Always returns [0, 1]
''',
        status=SubmissionStatus.WRONG_ANSWER,
        runtime="N/A",
        memory="N/A",
        timestamp=1704931200,  # 2024-01-11 00:00:00 UTC
        percentiles=None
    )


def create_time_limit_exceeded_submission() -> Submission:
    """Create a submission with TIME_LIMIT_EXCEEDED status"""
    return Submission(
        id="sub-tle",
        problem_id="median-of-two-sorted-arrays",
        language="Python3",
        code='''class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # Inefficient O(n) solution that times out
        merged = sorted(nums1 + nums2)
        n = len(merged)
        if n % 2 == 0:
            return (merged[n//2 - 1] + merged[n//2]) / 2
        return merged[n//2]
''',
        status=SubmissionStatus.TIME_LIMIT_EXCEEDED,
        runtime="N/A",
        memory="N/A",
        timestamp=1705017600,  # 2024-01-12 00:00:00 UTC
        percentiles=None
    )


def create_runtime_error_submission() -> Submission:
    """Create a submission with RUNTIME_ERROR status"""
    return Submission(
        id="sub-runtime-error",
        problem_id="reverse-integer",
        language="Python3",
        code='''class Solution:
    def reverse(self, x: int) -> int:
        # This will cause a runtime error for certain inputs
        return int(str(x)[::-1])  # Doesn't handle negative numbers correctly
''',
        status=SubmissionStatus.RUNTIME_ERROR,
        runtime="N/A",
        memory="N/A",
        timestamp=1705104000,  # 2024-01-13 00:00:00 UTC
        percentiles=None
    )
