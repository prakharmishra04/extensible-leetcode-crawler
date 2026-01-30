"""Unit tests for LeetCode adapter."""

import pytest

from crawler.domain.entities import Problem, Submission
from crawler.domain.entities.enums import SubmissionStatus
from crawler.domain.value_objects import Difficulty, Example, Percentiles
from crawler.infrastructure.platforms.leetcode.adapter import LeetCodeAdapter
from tests.fixtures.api_responses import (
    get_leetcode_problem_response,
    get_leetcode_submission_response,
    get_leetcode_problem_with_no_hints_response,
    get_leetcode_problem_with_many_examples_response,
    get_leetcode_problem_with_html_content_response,
)


class TestLeetCodeAdapter:
    """Test suite for LeetCodeAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create a LeetCodeAdapter instance."""
        return LeetCodeAdapter()
    
    def test_adapt_problem_with_valid_data(self, adapter):
        """Test adapting a problem with all fields present."""
        response = get_leetcode_problem_response()
        
        problem = adapter.adapt_problem(response)
        
        assert isinstance(problem, Problem)
        assert problem.id == "two-sum"
        assert problem.platform == "leetcode"
        assert problem.title == "Two Sum"
        assert problem.difficulty == Difficulty("Easy")
        assert "array of integers" in problem.description.lower()
        assert "Array" in problem.topics
        assert "Hash Table" in problem.topics
        assert len(problem.hints) == 2
        assert "brute force" in problem.hints[0].lower()
        assert len(problem.examples) > 0
        assert 40 < problem.acceptance_rate < 60  # Around 49.1%
    
    def test_adapt_problem_with_no_hints(self, adapter):
        """Test adapting a problem with no hints."""
        response = get_leetcode_problem_with_no_hints_response()
        
        problem = adapter.adapt_problem(response)
        
        assert isinstance(problem, Problem)
        assert problem.id == "reverse-integer"
        assert problem.title == "Reverse Integer"
        assert problem.difficulty == Difficulty("Medium")
        assert len(problem.hints) == 0
        assert len(problem.examples) > 0
    
    def test_adapt_problem_with_many_examples(self, adapter):
        """Test adapting a problem with multiple examples."""
        response = get_leetcode_problem_with_many_examples_response()
        
        problem = adapter.adapt_problem(response)
        
        assert isinstance(problem, Problem)
        assert problem.id == "fizz-buzz"
        assert len(problem.examples) == 5  # n=3, n=5, n=15, n=1, n=100
        assert all(isinstance(ex, Example) for ex in problem.examples)
    
    def test_adapt_problem_with_html_content(self, adapter):
        """Test adapting a problem with complex HTML content."""
        response = get_leetcode_problem_with_html_content_response()
        
        problem = adapter.adapt_problem(response)
        
        assert isinstance(problem, Problem)
        assert problem.id == "regular-expression-matching"
        assert problem.difficulty == Difficulty("Hard")
        # Check that HTML tags are removed
        assert "<p>" not in problem.description
        assert "<code>" not in problem.description
        assert "<ul>" not in problem.description
        # Check that content is preserved
        assert "regular expression matching" in problem.description.lower()
        assert "." in problem.description or "Matches any single character" in problem.description
    
    def test_adapt_submission_with_valid_data(self, adapter):
        """Test adapting a submission with all fields present."""
        response = get_leetcode_submission_response()
        
        submission = adapter.adapt_submission(response, "two-sum")
        
        assert isinstance(submission, Submission)
        assert submission.id == "12345"
        assert submission.problem_id == "two-sum"
        assert submission.language == "Python3"
        assert "def twoSum" in submission.code
        assert submission.status == SubmissionStatus.ACCEPTED
        assert submission.runtime == "52 ms"
        assert submission.memory == "15.2 MB"
        assert submission.timestamp == 1704067200
        assert submission.percentiles is not None
        assert isinstance(submission.percentiles, Percentiles)
        assert submission.percentiles.runtime == 85.3
        assert submission.percentiles.memory == 72.1
    
    def test_parse_html_removes_tags(self, adapter):
        """Test that HTML parsing removes all tags."""
        html = "<p>Hello <code>world</code></p>"
        
        text = adapter._parse_html(html)
        
        assert text == "Hello world"
        assert "<p>" not in text
        assert "<code>" not in text
    
    def test_parse_html_with_complex_structure(self, adapter):
        """Test HTML parsing with nested tags and lists."""
        html = """
        <p>Given an input string <code>s</code> and a pattern <code>p</code>.</p>
        <ul>
            <li><code>'.'</code> Matches any single character.</li>
            <li><code>'*'</code> Matches zero or more.</li>
        </ul>
        """
        
        text = adapter._parse_html(html)
        
        assert "<p>" not in text
        assert "<ul>" not in text
        assert "<li>" not in text
        assert "<code>" not in text
        assert "Given an input string" in text
        assert "Matches any single character" in text
    
    def test_parse_html_with_empty_string(self, adapter):
        """Test HTML parsing with empty string."""
        text = adapter._parse_html("")
        
        assert text == ""
    
    def test_parse_html_cleans_whitespace(self, adapter):
        """Test that HTML parsing cleans up excessive whitespace."""
        html = "<p>Hello    \n\n   world</p>"
        
        text = adapter._parse_html(html)
        
        assert text == "Hello world"
        assert "    " not in text
        assert "\n\n" not in text
    
    def test_parse_examples_with_multiple_lines(self, adapter):
        """Test parsing examples with multiple test cases."""
        examples_str = "nums = [2,7,11,15], target = 9\nnums = [3,2,4], target = 6\nnums = [3,3], target = 6"
        
        examples = adapter._parse_examples(examples_str)
        
        assert len(examples) == 3
        assert all(isinstance(ex, Example) for ex in examples)
        assert examples[0].input == "nums = [2,7,11,15], target = 9"
        assert examples[1].input == "nums = [3,2,4], target = 6"
        assert examples[2].input == "nums = [3,3], target = 6"
    
    def test_parse_examples_with_empty_string(self, adapter):
        """Test parsing examples with empty string."""
        examples = adapter._parse_examples("")
        
        assert examples == []
    
    def test_parse_examples_with_blank_lines(self, adapter):
        """Test parsing examples ignores blank lines."""
        examples_str = "n = 3\n\nn = 5\n\n\nn = 15"
        
        examples = adapter._parse_examples(examples_str)
        
        assert len(examples) == 3
        assert examples[0].input == "n = 3"
        assert examples[1].input == "n = 5"
        assert examples[2].input == "n = 15"
    
    def test_parse_acceptance_rate_with_valid_json(self, adapter):
        """Test parsing acceptance rate from valid JSON."""
        stats_json = '{"acRate": "49.1%"}'
        
        rate = adapter._parse_acceptance_rate(stats_json)
        
        assert rate == 49.1
    
    def test_parse_acceptance_rate_with_high_rate(self, adapter):
        """Test parsing high acceptance rate."""
        stats_json = '{"acRate": "98.7%"}'
        
        rate = adapter._parse_acceptance_rate(stats_json)
        
        assert rate == 98.7
    
    def test_parse_acceptance_rate_with_low_rate(self, adapter):
        """Test parsing low acceptance rate."""
        stats_json = '{"acRate": "12.4%"}'
        
        rate = adapter._parse_acceptance_rate(stats_json)
        
        assert rate == 12.4
    
    def test_parse_acceptance_rate_with_empty_string(self, adapter):
        """Test parsing acceptance rate with empty string."""
        rate = adapter._parse_acceptance_rate("")
        
        assert rate == 0.0
    
    def test_parse_acceptance_rate_with_invalid_json(self, adapter):
        """Test parsing acceptance rate with invalid JSON."""
        rate = adapter._parse_acceptance_rate("not json")
        
        assert rate == 0.0
    
    def test_parse_acceptance_rate_with_missing_field(self, adapter):
        """Test parsing acceptance rate with missing acRate field."""
        stats_json = '{"otherField": "value"}'
        
        rate = adapter._parse_acceptance_rate(stats_json)
        
        assert rate == 0.0
    
    def test_map_submission_status_accepted(self, adapter):
        """Test mapping Accepted status."""
        status = adapter._map_submission_status("Accepted")
        
        assert status == SubmissionStatus.ACCEPTED
    
    def test_map_submission_status_wrong_answer(self, adapter):
        """Test mapping Wrong Answer status."""
        status = adapter._map_submission_status("Wrong Answer")
        
        assert status == SubmissionStatus.WRONG_ANSWER
    
    def test_map_submission_status_time_limit_exceeded(self, adapter):
        """Test mapping Time Limit Exceeded status."""
        status = adapter._map_submission_status("Time Limit Exceeded")
        
        assert status == SubmissionStatus.TIME_LIMIT_EXCEEDED
    
    def test_map_submission_status_memory_limit_exceeded(self, adapter):
        """Test mapping Memory Limit Exceeded status."""
        status = adapter._map_submission_status("Memory Limit Exceeded")
        
        assert status == SubmissionStatus.MEMORY_LIMIT_EXCEEDED
    
    def test_map_submission_status_runtime_error(self, adapter):
        """Test mapping Runtime Error status."""
        status = adapter._map_submission_status("Runtime Error")
        
        assert status == SubmissionStatus.RUNTIME_ERROR
    
    def test_map_submission_status_compile_error(self, adapter):
        """Test mapping Compile Error status."""
        status = adapter._map_submission_status("Compile Error")
        
        assert status == SubmissionStatus.COMPILE_ERROR
    
    def test_map_submission_status_unknown(self, adapter):
        """Test mapping unknown status defaults to RUNTIME_ERROR."""
        status = adapter._map_submission_status("Unknown Status")
        
        assert status == SubmissionStatus.RUNTIME_ERROR
    
    def test_adapt_problem_missing_optional_fields(self, adapter):
        """Test adapting a problem with missing optional fields."""
        response = {
            "data": {
                "question": {
                    "questionId": "999",
                    "title": "Minimal Problem",
                    "titleSlug": "minimal-problem",
                    "difficulty": "Easy",
                    "content": "<p>Minimal content</p>",
                    # Missing: topicTags, hints, exampleTestcases, constraints, stats
                }
            }
        }
        
        problem = adapter.adapt_problem(response)
        
        assert isinstance(problem, Problem)
        assert problem.id == "minimal-problem"
        assert problem.title == "Minimal Problem"
        assert problem.topics == []
        assert problem.hints == []
        assert problem.examples == []
        assert problem.constraints == ""
        assert problem.acceptance_rate == 0.0
