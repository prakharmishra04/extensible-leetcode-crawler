"""Unit tests for output formatters."""

import json
import pytest

from crawler.infrastructure.formatters import (
    PythonFormatter,
    MarkdownFormatter,
    JSONFormatter
)
from crawler.domain.entities import Problem, Submission
from crawler.domain.value_objects import Difficulty, Example, Percentiles
from crawler.domain.entities.enums import SubmissionStatus


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id="two-sum",
        platform="leetcode",
        title="Two Sum",
        difficulty=Difficulty("Easy"),
        description="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        topics=["Array", "Hash Table"],
        constraints="2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9",
        examples=[
            Example(
                input="nums = [2,7,11,15], target = 9",
                output="[0,1]",
                explanation="Because nums[0] + nums[1] == 9, we return [0, 1]."
            ),
            Example(
                input="nums = [3,2,4], target = 6",
                output="[1,2]",
                explanation=None
            )
        ],
        hints=["Use a hash map to store complements", "Check if target - current exists"],
        acceptance_rate=49.1
    )


@pytest.fixture
def sample_submission():
    """Create a sample submission for testing."""
    return Submission(
        id="sub-123",
        problem_id="two-sum",
        language="Python",
        code="def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i",
        status=SubmissionStatus.ACCEPTED,
        runtime="52 ms",
        memory="15.2 MB",
        timestamp=1234567890,
        percentiles=Percentiles(runtime=85.5, memory=90.2)
    )


class TestPythonFormatter:
    """Test PythonFormatter implementation."""
    
    def test_get_file_extension(self):
        """Test that get_file_extension returns 'py'."""
        formatter = PythonFormatter()
        assert formatter.get_file_extension() == "py"
    
    def test_format_problem_without_submission(self, sample_problem):
        """Test formatting a problem without submission."""
        formatter = PythonFormatter()
        output = formatter.format_problem(sample_problem)
        
        # Check docstring header
        assert '"""' in output
        assert "Two Sum" in output
        assert "Difficulty: Easy" in output
        assert "Platform: leetcode" in output
        assert "Topics: Array, Hash Table" in output
        
        # Check description
        assert "Description:" in output
        assert "Given an array of integers" in output
        
        # Check constraints
        assert "Constraints:" in output
        assert "2 <= nums.length <= 10^4" in output
        
        # Check examples
        assert "# Example 1:" in output
        assert "# Input: nums = [2,7,11,15], target = 9" in output
        assert "# Output: [0,1]" in output
        assert "# Explanation: Because nums[0] + nums[1] == 9" in output
        
        assert "# Example 2:" in output
        assert "# Input: nums = [3,2,4], target = 6" in output
        assert "# Output: [1,2]" in output
        
        # Check hints
        assert "# Hints:" in output
        assert "# 1. Use a hash map to store complements" in output
        assert "# 2. Check if target - current exists" in output
        
        # Check placeholder
        assert "# TODO: Implement solution" in output
    
    def test_format_problem_with_submission(self, sample_problem, sample_submission):
        """Test formatting a problem with submission."""
        formatter = PythonFormatter()
        output = formatter.format_problem(sample_problem, sample_submission)
        
        # Check submission header
        assert "# Last Accepted Submission" in output
        assert "# Runtime: 52 ms" in output
        assert "# Memory: 15.2 MB" in output
        assert "# Runtime Percentile: 85.5%" in output
        assert "# Memory Percentile: 90.2%" in output
        
        # Check submission code
        assert "def twoSum(nums, target):" in output
        assert "seen = {}" in output
        assert "return [seen[complement], i]" in output
    
    def test_format_problem_without_hints(self, sample_problem):
        """Test formatting a problem without hints."""
        sample_problem.hints = []
        formatter = PythonFormatter()
        output = formatter.format_problem(sample_problem)
        
        assert "# Hints:" not in output
    
    def test_format_problem_without_constraints(self, sample_problem):
        """Test formatting a problem without constraints."""
        sample_problem.constraints = ""
        formatter = PythonFormatter()
        output = formatter.format_problem(sample_problem)
        
        # Constraints section should not appear
        lines = output.split("\n")
        # Find the docstring end
        docstring_end = [i for i, line in enumerate(lines) if line == '"""'][1]
        # Check that "Constraints:" is not after the first docstring
        assert "Constraints:" not in "\n".join(lines[docstring_end:])
    
    def test_format_problem_is_valid_python(self, sample_problem, sample_submission):
        """Test that formatted output is valid Python syntax."""
        formatter = PythonFormatter()
        output = formatter.format_problem(sample_problem, sample_submission)
        
        # Try to compile the output
        try:
            compile(output, "<string>", "exec")
        except SyntaxError:
            pytest.fail("Formatted output is not valid Python syntax")


class TestMarkdownFormatter:
    """Test MarkdownFormatter implementation."""
    
    def test_get_file_extension(self):
        """Test that get_file_extension returns 'md'."""
        formatter = MarkdownFormatter()
        assert formatter.get_file_extension() == "md"
    
    def test_format_problem_without_submission(self, sample_problem):
        """Test formatting a problem without submission."""
        formatter = MarkdownFormatter()
        output = formatter.format_problem(sample_problem)
        
        # Check title
        assert "# Two Sum" in output
        
        # Check metadata
        assert "**Difficulty:** Easy" in output
        assert "**Platform:** leetcode" in output
        assert "**Topics:** Array, Hash Table" in output
        assert "**Acceptance Rate:** 49.1%" in output
        
        # Check description section
        assert "## Description" in output
        assert "Given an array of integers" in output
        
        # Check constraints section
        assert "## Constraints" in output
        assert "2 <= nums.length <= 10^4" in output
        
        # Check examples section
        assert "## Examples" in output
        assert "### Example 1" in output
        assert "**Input:** `nums = [2,7,11,15], target = 9`" in output
        assert "**Output:** `[0,1]`" in output
        assert "**Explanation:** Because nums[0] + nums[1] == 9" in output
        
        assert "### Example 2" in output
        assert "**Input:** `nums = [3,2,4], target = 6`" in output
        assert "**Output:** `[1,2]`" in output
        
        # Check hints section
        assert "## Hints" in output
        assert "1. Use a hash map to store complements" in output
        assert "2. Check if target - current exists" in output
    
    def test_format_problem_with_submission(self, sample_problem, sample_submission):
        """Test formatting a problem with submission."""
        formatter = MarkdownFormatter()
        output = formatter.format_problem(sample_problem, sample_submission)
        
        # Check solution section
        assert "## Solution" in output
        assert "**Language:** Python" in output
        assert "**Runtime:** 52 ms" in output
        assert "**Memory:** 15.2 MB" in output
        assert "**Runtime Percentile:** 85.5%" in output
        assert "**Memory Percentile:** 90.2%" in output
        
        # Check code block
        assert "```python" in output
        assert "def twoSum(nums, target):" in output
        assert "```" in output
    
    def test_format_problem_without_hints(self, sample_problem):
        """Test formatting a problem without hints."""
        sample_problem.hints = []
        formatter = MarkdownFormatter()
        output = formatter.format_problem(sample_problem)
        
        assert "## Hints" not in output
    
    def test_format_problem_without_constraints(self, sample_problem):
        """Test formatting a problem without constraints."""
        sample_problem.constraints = ""
        formatter = MarkdownFormatter()
        output = formatter.format_problem(sample_problem)
        
        assert "## Constraints" not in output
    
    def test_format_problem_language_mapping(self, sample_problem, sample_submission):
        """Test that language names are correctly mapped for code blocks."""
        formatter = MarkdownFormatter()
        
        # Test C++ mapping
        sample_submission.language = "C++"
        output = formatter.format_problem(sample_problem, sample_submission)
        assert "```cpp" in output
        
        # Test C# mapping
        sample_submission.language = "C#"
        output = formatter.format_problem(sample_problem, sample_submission)
        assert "```csharp" in output
        
        # Test Python (no mapping needed)
        sample_submission.language = "Python"
        output = formatter.format_problem(sample_problem, sample_submission)
        assert "```python" in output


class TestJSONFormatter:
    """Test JSONFormatter implementation."""
    
    def test_get_file_extension(self):
        """Test that get_file_extension returns 'json'."""
        formatter = JSONFormatter()
        assert formatter.get_file_extension() == "json"
    
    def test_format_problem_without_submission(self, sample_problem):
        """Test formatting a problem without submission."""
        formatter = JSONFormatter()
        output = formatter.format_problem(sample_problem)
        
        # Parse JSON
        data = json.loads(output)
        
        # Check all fields
        assert data["id"] == "two-sum"
        assert data["platform"] == "leetcode"
        assert data["title"] == "Two Sum"
        assert data["difficulty"] == "Easy"
        assert "Given an array of integers" in data["description"]
        assert data["topics"] == ["Array", "Hash Table"]
        assert "2 <= nums.length <= 10^4" in data["constraints"]
        assert len(data["examples"]) == 2
        assert len(data["hints"]) == 2
        assert data["acceptance_rate"] == 49.1
        assert "submission" not in data
    
    def test_format_problem_with_submission(self, sample_problem, sample_submission):
        """Test formatting a problem with submission."""
        formatter = JSONFormatter()
        output = formatter.format_problem(sample_problem, sample_submission)
        
        # Parse JSON
        data = json.loads(output)
        
        # Check submission fields
        assert "submission" in data
        assert data["submission"]["id"] == "sub-123"
        assert data["submission"]["problem_id"] == "two-sum"
        assert data["submission"]["language"] == "Python"
        assert "def twoSum(nums, target):" in data["submission"]["code"]
        assert data["submission"]["status"] == "Accepted"
        assert data["submission"]["runtime"] == "52 ms"
        assert data["submission"]["memory"] == "15.2 MB"
        assert data["submission"]["timestamp"] == 1234567890
        assert data["submission"]["percentiles"]["runtime"] == 85.5
        assert data["submission"]["percentiles"]["memory"] == 90.2
    
    def test_format_problem_examples_structure(self, sample_problem):
        """Test that examples are correctly structured in JSON."""
        formatter = JSONFormatter()
        output = formatter.format_problem(sample_problem)
        
        data = json.loads(output)
        
        # Check first example
        assert data["examples"][0]["input"] == "nums = [2,7,11,15], target = 9"
        assert data["examples"][0]["output"] == "[0,1]"
        assert data["examples"][0]["explanation"] == "Because nums[0] + nums[1] == 9, we return [0, 1]."
        
        # Check second example (no explanation)
        assert data["examples"][1]["input"] == "nums = [3,2,4], target = 6"
        assert data["examples"][1]["output"] == "[1,2]"
        assert data["examples"][1]["explanation"] is None
    
    def test_format_problem_is_valid_json(self, sample_problem, sample_submission):
        """Test that formatted output is valid JSON."""
        formatter = JSONFormatter()
        output = formatter.format_problem(sample_problem, sample_submission)
        
        # Should not raise exception
        try:
            json.loads(output)
        except json.JSONDecodeError:
            pytest.fail("Formatted output is not valid JSON")
    
    def test_format_problem_pretty_printed(self, sample_problem):
        """Test that JSON output is pretty-printed."""
        formatter = JSONFormatter()
        output = formatter.format_problem(sample_problem)
        
        # Check for indentation
        assert "  " in output  # 2-space indentation
        assert "\n" in output  # Multiple lines
    
    def test_format_problem_preserves_unicode(self, sample_problem):
        """Test that Unicode characters are preserved."""
        sample_problem.description = "Test with unicode: \u2192 \u2713 \u2717"
        formatter = JSONFormatter()
        output = formatter.format_problem(sample_problem)
        
        data = json.loads(output)
        assert "\u2192" in data["description"]
        assert "\u2713" in data["description"]
        assert "\u2717" in data["description"]


class TestFormatterComparison:
    """Test that all formatters include essential information."""
    
    def test_all_formatters_include_title(self, sample_problem):
        """Test that all formatters include the problem title."""
        python_formatter = PythonFormatter()
        markdown_formatter = MarkdownFormatter()
        json_formatter = JSONFormatter()
        
        python_output = python_formatter.format_problem(sample_problem)
        markdown_output = markdown_formatter.format_problem(sample_problem)
        json_output = json_formatter.format_problem(sample_problem)
        
        assert "Two Sum" in python_output
        assert "Two Sum" in markdown_output
        assert "Two Sum" in json_output
    
    def test_all_formatters_include_difficulty(self, sample_problem):
        """Test that all formatters include the difficulty."""
        python_formatter = PythonFormatter()
        markdown_formatter = MarkdownFormatter()
        json_formatter = JSONFormatter()
        
        python_output = python_formatter.format_problem(sample_problem)
        markdown_output = markdown_formatter.format_problem(sample_problem)
        json_output = json_formatter.format_problem(sample_problem)
        
        assert "Easy" in python_output
        assert "Easy" in markdown_output
        assert "Easy" in json_output
    
    def test_all_formatters_include_description(self, sample_problem):
        """Test that all formatters include the description."""
        python_formatter = PythonFormatter()
        markdown_formatter = MarkdownFormatter()
        json_formatter = JSONFormatter()
        
        python_output = python_formatter.format_problem(sample_problem)
        markdown_output = markdown_formatter.format_problem(sample_problem)
        json_output = json_formatter.format_problem(sample_problem)
        
        assert "Given an array of integers" in python_output
        assert "Given an array of integers" in markdown_output
        assert "Given an array of integers" in json_output
    
    def test_all_formatters_include_examples(self, sample_problem):
        """Test that all formatters include examples."""
        python_formatter = PythonFormatter()
        markdown_formatter = MarkdownFormatter()
        json_formatter = JSONFormatter()
        
        python_output = python_formatter.format_problem(sample_problem)
        markdown_output = markdown_formatter.format_problem(sample_problem)
        json_output = json_formatter.format_problem(sample_problem)
        
        assert "nums = [2,7,11,15], target = 9" in python_output
        assert "nums = [2,7,11,15], target = 9" in markdown_output
        assert "nums = [2,7,11,15], target = 9" in json_output
    
    def test_all_formatters_include_submission_code(
        self, sample_problem, sample_submission
    ):
        """Test that all formatters include submission code when provided."""
        python_formatter = PythonFormatter()
        markdown_formatter = MarkdownFormatter()
        json_formatter = JSONFormatter()
        
        python_output = python_formatter.format_problem(sample_problem, sample_submission)
        markdown_output = markdown_formatter.format_problem(sample_problem, sample_submission)
        json_output = json_formatter.format_problem(sample_problem, sample_submission)
        
        assert "def twoSum(nums, target):" in python_output
        assert "def twoSum(nums, target):" in markdown_output
        assert "def twoSum(nums, target):" in json_output
