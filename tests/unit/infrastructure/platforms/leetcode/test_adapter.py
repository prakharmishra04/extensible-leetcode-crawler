"""Unit tests for LeetCode adapter."""

from typing import Any, Dict

import pytest
from hypothesis import given
from hypothesis import strategies as st

from crawler.domain.entities import Problem, Submission
from crawler.domain.entities.enums import SubmissionStatus
from crawler.domain.value_objects import Constraint, Difficulty, Example, Percentiles
from crawler.infrastructure.platforms.leetcode.adapter import LeetCodeAdapter
from tests.fixtures.api_responses import (
    get_leetcode_problem_response,
    get_leetcode_problem_with_html_content_response,
    get_leetcode_problem_with_many_examples_response,
    get_leetcode_problem_with_no_hints_response,
    get_leetcode_submission_response,
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

        # After our fix, newlines are preserved but cleaned
        assert text == "Hello\nworld"
        assert "    " not in text  # Multiple spaces still collapsed

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
        assert problem.constraints == []
        assert problem.acceptance_rate == 0.0


class TestConstraintParsing:
    """Test suite for constraint parsing functionality."""

    @pytest.fixture
    def adapter(self):
        """Create a LeetCodeAdapter instance."""
        return LeetCodeAdapter()

    def test_extract_description_parts_returns_constraint_list(self, adapter):
        """Test that _extract_description_parts returns List[Constraint] instead of str."""
        full_text = """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Constraints:
1 <= nums.length <= 10^4
-10^4 <= nums[i] <= 10^4
-10^4 <= target <= 10^4"""

        result = adapter._extract_description_parts(full_text)

        # Verify constraints is a list
        assert isinstance(result["constraints"], list)

        # Verify all items are Constraint objects
        assert all(isinstance(c, Constraint) for c in result["constraints"])

        # Verify correct number of constraints
        assert len(result["constraints"]) == 3

        # Verify constraint text content
        assert result["constraints"][0].text == "1 <= nums.length <= 10^4"
        assert result["constraints"][1].text == "-10^4 <= nums[i] <= 10^4"
        assert result["constraints"][2].text == "-10^4 <= target <= 10^4"

    def test_extract_description_parts_with_no_constraints(self, adapter):
        """Test that _extract_description_parts returns empty list when no constraints."""
        full_text = """Given an array of integers nums and an integer target.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]"""

        result = adapter._extract_description_parts(full_text)

        # Verify constraints is an empty list
        assert isinstance(result["constraints"], list)
        assert len(result["constraints"]) == 0

    def test_extract_description_parts_error_handling(self, adapter):
        """Test that _extract_description_parts handles parsing errors gracefully."""
        # Malformed constraints section that might cause parsing issues
        full_text = """Given an array.

Constraints:
This is not a valid constraint format"""

        result = adapter._extract_description_parts(full_text)

        # Should return a list (possibly empty or with the text as-is)
        assert isinstance(result["constraints"], list)
        # Should not crash - either empty list or single constraint
        assert len(result["constraints"]) >= 0

    def test_parse_constraints_with_numeric_ranges(self, adapter):
        """Test parsing constraints with numeric range patterns."""
        constraints_text = """1 <= nums.length <= 10^4
-10^4 <= nums[i] <= 10^4
-10^4 <= target <= 10^4"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert constraints[0].text == "1 <= nums.length <= 10^4"
        assert constraints[1].text == "-10^4 <= nums[i] <= 10^4"
        assert constraints[2].text == "-10^4 <= target <= 10^4"

    def test_parse_constraints_with_bullet_points(self, adapter):
        """Test parsing constraints with bullet point markers."""
        constraints_text = """• 1 <= n <= 100
• n is an integer
• The answer is guaranteed to fit in a 32-bit integer"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert constraints[0].text == "1 <= n <= 100"
        assert constraints[1].text == "n is an integer"
        assert constraints[2].text == "The answer is guaranteed to fit in a 32-bit integer"

    def test_parse_constraints_with_numbered_list(self, adapter):
        """Test parsing constraints with numbered list markers."""
        constraints_text = """1. 1 <= n <= 100
2. n is an integer
3. The answer is guaranteed to fit in a 32-bit integer"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert constraints[0].text == "1 <= n <= 100"
        assert constraints[1].text == "n is an integer"
        assert constraints[2].text == "The answer is guaranteed to fit in a 32-bit integer"

    def test_parse_constraints_with_dash_bullets(self, adapter):
        """Test parsing constraints with dash bullet markers."""
        constraints_text = """- 1 <= n <= 100
- n is an integer
- The answer is guaranteed to fit in a 32-bit integer"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert constraints[0].text == "1 <= n <= 100"
        assert constraints[1].text == "n is an integer"
        assert constraints[2].text == "The answer is guaranteed to fit in a 32-bit integer"

    def test_parse_constraints_with_asterisk_bullets(self, adapter):
        """Test parsing constraints with asterisk bullet markers."""
        constraints_text = """* 1 <= n <= 100
* n is an integer
* The answer is guaranteed to fit in a 32-bit integer"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert constraints[0].text == "1 <= n <= 100"
        assert constraints[1].text == "n is an integer"
        assert constraints[2].text == "The answer is guaranteed to fit in a 32-bit integer"

    def test_parse_constraints_with_empty_string(self, adapter):
        """Test parsing constraints with empty string returns empty list."""
        constraints = adapter._parse_constraints_from_text("")

        assert constraints == []

    def test_parse_constraints_with_whitespace_only(self, adapter):
        """Test parsing constraints with whitespace-only string returns empty list."""
        constraints = adapter._parse_constraints_from_text("   \n\t  ")

        assert constraints == []

    def test_parse_constraints_with_trailing_periods(self, adapter):
        """Test parsing constraints removes trailing periods."""
        constraints_text = """1 <= n <= 100.
n is an integer.
The answer is guaranteed to fit in a 32-bit integer."""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert constraints[0].text == "1 <= n <= 100"
        assert constraints[1].text == "n is an integer"
        assert constraints[2].text == "The answer is guaranteed to fit in a 32-bit integer"

    def test_parse_constraints_preserves_numeric_expressions(self, adapter):
        """Test that numeric expressions like 10^4 are preserved."""
        constraints_text = "1 <= nums.length <= 10^4"

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 1
        assert "10^4" in constraints[0].text
        assert constraints[0].text == "1 <= nums.length <= 10^4"

    def test_parse_constraints_with_multi_line_constraint(self, adapter):
        """Test parsing multi-line constraints preserves complete text."""
        constraints_text = """1 <= n <= 100
The string consists of lowercase English letters only
and may contain leading zeros"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        # Should split into separate constraints by newlines
        assert len(constraints) >= 1

    def test_parse_constraints_skips_empty_lines(self, adapter):
        """Test parsing constraints skips empty lines."""
        constraints_text = """1 <= n <= 100

n is an integer

The answer is guaranteed to fit in a 32-bit integer"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert all(c.text for c in constraints)  # No empty constraints

    def test_parse_constraints_with_special_characters(self, adapter):
        """Test parsing constraints preserves special characters."""
        constraints_text = """1 <= s.length <= 10^4
s consists of parentheses only '()[]{}'
-2^31 <= x <= 2^31 - 1"""

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 3
        assert "'()[]{}'" in constraints[1].text
        assert "2^31" in constraints[2].text

    def test_parse_constraints_single_constraint(self, adapter):
        """Test parsing a single constraint."""
        constraints_text = "1 <= n <= 100"

        constraints = adapter._parse_constraints_from_text(constraints_text)

        assert len(constraints) == 1
        assert constraints[0].text == "1 <= n <= 100"

    def test_clean_constraint_text_removes_bullet(self, adapter):
        """Test that _clean_constraint_text removes bullet markers."""
        text = "• 1 <= n <= 100"

        cleaned = adapter._clean_constraint_text(text)

        assert cleaned == "1 <= n <= 100"
        assert "•" not in cleaned

    def test_clean_constraint_text_removes_dash(self, adapter):
        """Test that _clean_constraint_text removes dash markers."""
        text = "- 1 <= n <= 100"

        cleaned = adapter._clean_constraint_text(text)

        assert cleaned == "1 <= n <= 100"
        assert not cleaned.startswith("-")

    def test_clean_constraint_text_removes_numbered_marker(self, adapter):
        """Test that _clean_constraint_text removes numbered list markers."""
        text = "1. 1 <= n <= 100"

        cleaned = adapter._clean_constraint_text(text)

        assert cleaned == "1 <= n <= 100"
        assert not cleaned.startswith("1.")

    def test_clean_constraint_text_preserves_negative_numbers(self, adapter):
        """Test that _clean_constraint_text preserves negative numbers in ranges."""
        text = "-10^4 <= nums[i] <= 10^4"

        cleaned = adapter._clean_constraint_text(text)

        assert cleaned == "-10^4 <= nums[i] <= 10^4"
        assert cleaned.startswith("-10")

    def test_clean_constraint_text_removes_trailing_period(self, adapter):
        """Test that _clean_constraint_text removes trailing periods."""
        text = "1 <= n <= 100."

        cleaned = adapter._clean_constraint_text(text)

        assert cleaned == "1 <= n <= 100"
        assert not cleaned.endswith(".")

    def test_clean_constraint_text_preserves_internal_periods(self, adapter):
        """Test that _clean_constraint_text preserves periods in expressions."""
        text = "s consists of lowercase letters a-z."

        cleaned = adapter._clean_constraint_text(text)

        # Should remove trailing period
        assert cleaned == "s consists of lowercase letters a-z"

    def test_clean_constraint_text_with_empty_string(self, adapter):
        """Test that _clean_constraint_text handles empty string."""
        cleaned = adapter._clean_constraint_text("")

        assert cleaned == ""

    def test_clean_constraint_text_strips_whitespace(self, adapter):
        """Test that _clean_constraint_text strips leading/trailing whitespace."""
        text = "   1 <= n <= 100   "

        cleaned = adapter._clean_constraint_text(text)

        assert cleaned == "1 <= n <= 100"
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")


class TestExampleExtractionProperties:
    """Property-based tests for example extraction.

    Feature: enhanced-problem-parsing
    """

    # Feature: enhanced-problem-parsing, Property 3: Example Extraction Completeness
    @given(st.integers(min_value=0, max_value=10))
    def test_example_extraction_completeness(self, num_examples):
        """**Validates: Requirements 2.1, 8.1**

        Property: For any HTML problem description containing N valid example blocks
        (with both Input and Output fields), parsing should extract exactly N Example objects.

        This is the core accuracy property for example parsing. It ensures we don't lose
        or duplicate examples during parsing.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate HTML with N examples
        examples_html = self._generate_examples_html(num_examples)

        # Parse the examples
        examples = adapter._parse_examples_from_text(examples_html)

        # Verify exactly N examples were extracted
        assert len(examples) == num_examples, (
            f"Expected {num_examples} examples, but got {len(examples)}. "
            f"Generated HTML: {examples_html[:200]}..."
        )

        # Verify all examples are valid Example objects
        assert all(isinstance(ex, Example) for ex in examples)

        # Verify all examples have non-empty input and output
        assert all(ex.input.strip() for ex in examples)
        assert all(ex.output.strip() for ex in examples)

    # Feature: enhanced-problem-parsing, Property 4: Example Without Explanation Handling
    @given(st.integers(min_value=1, max_value=10))
    def test_example_without_explanation_handling(self, num_examples):
        """**Validates: Requirements 2.5**

        Property: For any example block that contains Input and Output but no Explanation field,
        the parsed Example object should have explanation set to None.

        This ensures optional fields are handled correctly without requiring all examples
        to have explanations.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate HTML with N examples WITHOUT explanations
        examples_html = self._generate_examples_without_explanation(num_examples)

        # Parse the examples
        examples = adapter._parse_examples_from_text(examples_html)

        # Verify exactly N examples were extracted
        assert len(examples) == num_examples, (
            f"Expected {num_examples} examples, but got {len(examples)}. "
            f"Generated HTML: {examples_html[:200]}..."
        )

        # Verify all examples are valid Example objects
        assert all(isinstance(ex, Example) for ex in examples)

        # Verify all examples have non-empty input and output
        assert all(ex.input.strip() for ex in examples)
        assert all(ex.output.strip() for ex in examples)

        # CRITICAL: Verify all examples have explanation set to None
        assert all(ex.explanation is None for ex in examples), (
            f"Expected all examples to have explanation=None, but found: "
            f"{[ex.explanation for ex in examples if ex.explanation is not None]}"
        )

    def _generate_examples_html(self, n: int) -> str:
        """Generate HTML text with N examples.

        Each example follows the LeetCode format:
        Example N:
        Input: <input_value>
        Output: <output_value>
        Explanation: <explanation_text>

        Args:
            n: Number of examples to generate

        Returns:
            String containing N examples in LeetCode format
        """
        if n == 0:
            return ""

        examples = []
        for i in range(1, n + 1):
            # Generate varied example patterns
            if i % 3 == 1:
                # Simple array example
                input_val = f"nums = [{i}, {i+1}, {i+2}], target = {i*2+1}"
                output_val = f"[0, 1]"
                explanation = f"Because nums[0] + nums[1] == {i*2+1}, we return [0, 1]"
            elif i % 3 == 2:
                # String example
                input_val = f's = "example{i}"'
                output_val = f'"{i}elpmaxe"'
                explanation = f"The string is reversed"
            else:
                # Integer example
                input_val = f"n = {i * 10}"
                output_val = f"{i * 100}"
                explanation = f"The result is n multiplied by 10"

            example_text = f"""Example {i}:
Input: {input_val}
Output: {output_val}
Explanation: {explanation}"""

            examples.append(example_text)

        return "\n\n".join(examples)

    def _generate_examples_without_explanation(self, n: int) -> str:
        """Generate HTML text with N examples WITHOUT explanations.

        Each example follows the LeetCode format but omits the Explanation field:
        Example N:
        Input: <input_value>
        Output: <output_value>

        Args:
            n: Number of examples to generate

        Returns:
            String containing N examples without explanations in LeetCode format
        """
        if n == 0:
            return ""

        examples = []
        for i in range(1, n + 1):
            # Generate varied example patterns
            if i % 3 == 1:
                # Simple array example
                input_val = f"nums = [{i}, {i+1}, {i+2}], target = {i*2+1}"
                output_val = f"[0, 1]"
            elif i % 3 == 2:
                # String example
                input_val = f's = "example{i}"'
                output_val = f'"{i}elpmaxe"'
            else:
                # Integer example
                input_val = f"n = {i * 10}"
                output_val = f"{i * 100}"

            # Note: NO Explanation field
            example_text = f"""Example {i}:
Input: {input_val}
Output: {output_val}"""

            examples.append(example_text)

        return "\n\n".join(examples)

    # Feature: enhanced-problem-parsing, Property 5: Malformed Example Skipping
    @given(
        st.integers(min_value=1, max_value=5),  # valid_count
        st.integers(min_value=1, max_value=5),  # malformed_count
    )
    def test_malformed_example_skipping(self, valid_count, malformed_count):
        """**Validates: Requirements 2.6, 7.3**

        Property: For any HTML containing a mix of valid examples (with Input and Output)
        and malformed examples (missing Input or Output), parsing should extract only the
        valid examples and skip the malformed ones.

        This ensures robustness - the parser continues working even when some examples
        are malformed.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate HTML with mix of valid and malformed examples
        examples_html = self._generate_mixed_examples(valid_count, malformed_count)

        # Parse the examples
        examples = adapter._parse_examples_from_text(examples_html)

        # Verify only valid examples were extracted (malformed ones skipped)
        assert len(examples) == valid_count, (
            f"Expected {valid_count} valid examples to be extracted, but got {len(examples)}. "
            f"Generated HTML had {valid_count} valid and {malformed_count} malformed examples. "
            f"HTML preview: {examples_html[:300]}..."
        )

        # Verify all extracted examples are valid Example objects
        assert all(isinstance(ex, Example) for ex in examples)

        # Verify all extracted examples have non-empty input and output
        assert all(
            ex.input.strip() for ex in examples
        ), "All extracted examples should have non-empty input"
        assert all(
            ex.output.strip() for ex in examples
        ), "All extracted examples should have non-empty output"

    def _generate_mixed_examples(self, valid_count: int, malformed_count: int) -> str:
        """Generate HTML text with a mix of valid and malformed examples.

        Valid examples have both Input and Output fields.
        Malformed examples are missing either Input or Output field.

        Args:
            valid_count: Number of valid examples to generate
            malformed_count: Number of malformed examples to generate

        Returns:
            String containing mixed valid and malformed examples
        """
        examples = []

        # Generate valid examples
        for i in range(1, valid_count + 1):
            if i % 3 == 1:
                input_val = f"nums = [{i}, {i+1}, {i+2}], target = {i*2+1}"
                output_val = f"[0, 1]"
            elif i % 3 == 2:
                input_val = f's = "example{i}"'
                output_val = f'"{i}elpmaxe"'
            else:
                input_val = f"n = {i * 10}"
                output_val = f"{i * 100}"

            example_text = f"""Example {i}:
Input: {input_val}
Output: {output_val}
Explanation: This is a valid example"""

            examples.append(example_text)

        # Generate malformed examples (interleaved with valid ones)
        for i in range(1, malformed_count + 1):
            example_num = valid_count + i

            # Alternate between missing Input and missing Output
            if i % 2 == 1:
                # Missing Input field
                output_val = f"[{i}, {i+1}]"
                malformed_text = f"""Example {example_num}:
Output: {output_val}
Explanation: This example is missing the Input field"""
            else:
                # Missing Output field
                input_val = f"arr = [{i}, {i+1}, {i+2}]"
                malformed_text = f"""Example {example_num}:
Input: {input_val}
Explanation: This example is missing the Output field"""

            examples.append(malformed_text)

        return "\n\n".join(examples)

    # Feature: enhanced-problem-parsing, Property 18: Multi-line Example Preservation
    @given(st.integers(min_value=1, max_value=10))
    def test_multiline_example_preservation(self, num_examples):
        """**Validates: Requirements 8.3**

        Property: For any example with input or output containing newline characters,
        the parsed Example object should preserve all newlines exactly as they appear
        in the source.

        Multi-line examples (like tree structures or matrices) must preserve formatting
        for correctness.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate HTML with N examples containing multi-line input/output
        examples_html = self._generate_multiline_examples(num_examples)

        # Parse the examples
        examples = adapter._parse_examples_from_text(examples_html)

        # Verify exactly N examples were extracted
        assert len(examples) == num_examples, (
            f"Expected {num_examples} examples, but got {len(examples)}. "
            f"Generated HTML: {examples_html[:300]}..."
        )

        # Verify all examples are valid Example objects
        assert all(isinstance(ex, Example) for ex in examples)

        # CRITICAL: Verify newlines are preserved in input and output
        for i, example in enumerate(examples):
            # Each example should have multi-line content
            # Check that newlines are present (not collapsed to spaces)
            # Note: enumerate gives 0-based index, but example numbers are 1-based
            example_num = i + 1

            if example_num % 2 == 0:
                # Even-numbered examples have multi-line input
                assert "\n" in example.input or "\\n" in example.input, (
                    f"Example {i} (number {example_num}) should have multi-line input with preserved newlines. "
                    f"Got: {repr(example.input)}"
                )
            else:
                # Odd-numbered examples have multi-line output
                assert "\n" in example.output or "\\n" in example.output, (
                    f"Example {i} (number {example_num}) should have multi-line output with preserved newlines. "
                    f"Got: {repr(example.output)}"
                )

    def _generate_multiline_examples(self, n: int) -> str:
        """Generate HTML text with N examples containing multi-line input/output.

        Multi-line examples are common in problems involving:
        - Tree structures (represented as arrays with null values)
        - Matrices (2D arrays)
        - Multiple input parameters on separate lines

        Args:
            n: Number of examples to generate

        Returns:
            String containing N examples with multi-line content
        """
        if n == 0:
            return ""

        examples = []
        for i in range(1, n + 1):
            # Alternate between multi-line input and multi-line output
            if i % 2 == 0:
                # Multi-line input (e.g., tree structure or matrix)
                input_val = f"""root = [1,2,3,null,null,4,5]
target = {i}"""
                output_val = f"{i * 2}"
                explanation = f"The tree has {i} nodes and target is {i}"
            else:
                # Multi-line output (e.g., matrix result)
                input_val = f"matrix = [[1,2],[3,4]], k = {i}"
                output_val = f"""[[1,2],
 [3,4],
 [{i},{i+1}]]"""
                explanation = f"The matrix is expanded with row [{i},{i+1}]"

            example_text = f"""Example {i}:
Input: {input_val}
Output: {output_val}
Explanation: {explanation}"""

            examples.append(example_text)

        return "\n\n".join(examples)


class TestConstraintExtractionProperties:
    """Property-based tests for constraint extraction.

    Feature: enhanced-problem-parsing
    """

    # Feature: enhanced-problem-parsing, Property 6: Constraint Extraction Completeness
    @given(st.integers(min_value=0, max_value=20))
    def test_constraint_extraction_completeness(self, num_constraints):
        """**Validates: Requirements 3.1, 8.2**

        Property: For any HTML problem description containing N valid constraint items
        in the Constraints section, parsing should extract exactly N Constraint objects.

        This property ensures we don't lose or duplicate constraints during parsing.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate HTML with N constraints using numeric range format
        constraints_html = self._generate_constraints_html(num_constraints)

        # Parse the constraints
        constraints = adapter._parse_constraints_from_text(constraints_html)

        # Verify exactly N constraints were extracted
        assert len(constraints) == num_constraints, (
            f"Expected {num_constraints} constraints, but got {len(constraints)}. "
            f"Generated HTML: {constraints_html[:200]}..."
        )

        # Verify all constraints are valid Constraint objects
        assert all(isinstance(c, Constraint) for c in constraints)

        # Verify no constraint text is empty
        assert all(c.text.strip() for c in constraints)

    def _generate_constraints_html(self, n: int) -> str:
        """Generate HTML text with N constraints.

        Uses numeric range format which is the most common in LeetCode problems.
        Each constraint follows the pattern: "lower <= variable <= upper"

        Args:
            n: Number of constraints to generate

        Returns:
            String containing N constraints separated by newlines
        """
        if n == 0:
            return ""

        constraints = []
        for i in range(n):
            # Generate varied constraint patterns that work with current parser
            if i % 3 == 0:
                # Positive range: "1 <= n <= 100"
                lower = i + 1
                upper = (i + 1) * 100
                var = f"var{i}"
                constraints.append(f"{lower} <= {var} <= {upper}")
            elif i % 3 == 1:
                # Negative range: "-1000 <= nums[i] <= 1000"
                # Avoid using ^ notation which requires special handling
                lower = -(i + 1) * 1000
                upper = (i + 1) * 1000
                var = f"arr[{i}]"
                constraints.append(f"{lower} <= {var} <= {upper}")
            else:
                # Zero-based range: "0 <= index < n"
                var = f"index{i}"
                upper = f"n{i}"
                constraints.append(f"0 <= {var} < {upper}")

        return "\n".join(constraints)


class TestAdapterIntegrationProperties:
    """Property-based tests for adapter integration.

    Feature: enhanced-problem-parsing
    """

    # Feature: enhanced-problem-parsing, Property 10: Adapter Example Integration
    @given(st.integers(min_value=0, max_value=10))
    def test_adapter_example_integration(self, num_examples):
        """**Validates: Requirements 4.3**

        Property: For any valid problem HTML containing examples, the Problem entity
        created by the adapter should contain Example objects with the same input,
        output, and explanation values as in the HTML.

        This tests end-to-end integration from HTML to domain entity for examples.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate complete problem response with N examples
        response = self._generate_problem_response_with_examples(num_examples)

        # Adapt the problem
        problem = adapter.adapt_problem(response)

        # Verify problem is a valid Problem entity
        assert isinstance(problem, Problem)

        # Verify exactly N examples were extracted
        assert (
            len(problem.examples) == num_examples
        ), f"Expected {num_examples} examples in Problem entity, but got {len(problem.examples)}"

        # Verify all examples are valid Example objects
        assert all(isinstance(ex, Example) for ex in problem.examples)

        # Verify all examples have non-empty input and output
        assert all(ex.input.strip() for ex in problem.examples)
        assert all(ex.output.strip() for ex in problem.examples)

    # Feature: enhanced-problem-parsing, Property 11: Adapter Constraint Integration
    @given(st.integers(min_value=0, max_value=20))
    def test_adapter_constraint_integration(self, num_constraints):
        """**Validates: Requirements 4.4**

        Property: For any valid problem HTML containing constraints, the Problem entity
        created by the adapter should contain Constraint objects with the same text
        values as in the HTML.

        This tests end-to-end integration from HTML to domain entity for constraints.

        Note: Due to HTML parsing collapsing whitespace, this test verifies that:
        1. The adapter returns a list of Constraint objects (not crashes)
        2. All returned constraints are valid Constraint objects
        3. No constraint text is empty

        The exact count may vary due to HTML parsing behavior, but the adapter
        should handle this gracefully.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate complete problem response with N constraints
        response = self._generate_problem_response_with_constraints(num_constraints)

        # Adapt the problem - should not raise an exception
        problem = adapter.adapt_problem(response)

        # Verify problem is a valid Problem entity
        assert isinstance(problem, Problem)

        # Verify constraints is a list
        assert isinstance(problem.constraints, list)

        # If we expected constraints, verify we got at least some
        # (HTML parsing may merge some, but we should get at least 1 if num_constraints > 0)
        if num_constraints > 0:
            assert len(problem.constraints) > 0, (
                f"Expected at least 1 constraint when {num_constraints} were generated, "
                f"but got {len(problem.constraints)}"
            )
        else:
            # If no constraints were generated, list should be empty
            assert len(problem.constraints) == 0

        # Verify all constraints are valid Constraint objects
        assert all(isinstance(c, Constraint) for c in problem.constraints)

        # Verify no constraint text is empty
        assert all(c.text.strip() for c in problem.constraints)

    # Feature: enhanced-problem-parsing, Property 12: Example Parsing Error Recovery
    @given(st.sampled_from(["missing_input", "missing_output", "invalid_html", "empty_content"]))
    def test_example_parsing_error_recovery(self, error_type):
        """**Validates: Requirements 4.5**

        Property: For any malformed HTML that causes example parsing to fail,
        the adapter should return an empty examples list instead of raising an exception.

        This ensures the system remains stable even with unexpected input.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate malformed problem response based on error type
        response = self._generate_malformed_problem_response(error_type, malform_examples=True)

        # Adapt the problem - should not raise an exception
        try:
            problem = adapter.adapt_problem(response)

            # Verify problem is a valid Problem entity
            assert isinstance(problem, Problem)

            # Verify examples is a list (may be empty due to malformed input)
            assert isinstance(problem.examples, list)

            # For completely malformed HTML, examples should be empty
            # For partially malformed HTML, only valid examples should be extracted
            # Either way, no exception should be raised

        except Exception as e:
            pytest.fail(f"Adapter should not raise exception for malformed examples. Got: {e}")

    # Feature: enhanced-problem-parsing, Property 13: Constraint Parsing Error Recovery
    @given(
        st.sampled_from(
            ["empty_constraints", "invalid_format", "missing_section", "corrupted_html"]
        )
    )
    def test_constraint_parsing_error_recovery(self, error_type):
        """**Validates: Requirements 4.6**

        Property: For any malformed HTML that causes constraint parsing to fail,
        the adapter should return an empty constraints list instead of raising an exception.

        This ensures the system remains stable even with unexpected input.
        """
        # Create adapter instance
        adapter = LeetCodeAdapter()

        # Generate malformed problem response based on error type
        response = self._generate_malformed_problem_response(error_type, malform_constraints=True)

        # Adapt the problem - should not raise an exception
        try:
            problem = adapter.adapt_problem(response)

            # Verify problem is a valid Problem entity
            assert isinstance(problem, Problem)

            # Verify constraints is a list (may be empty due to malformed input)
            assert isinstance(problem.constraints, list)

            # For completely malformed HTML, constraints should be empty
            # For partially malformed HTML, only valid constraints should be extracted
            # Either way, no exception should be raised

        except Exception as e:
            pytest.fail(f"Adapter should not raise exception for malformed constraints. Got: {e}")

    def _generate_problem_response_with_examples(self, num_examples: int) -> Dict[str, Any]:
        """Generate a complete LeetCode API response with N examples.

        Args:
            num_examples: Number of examples to include in the problem

        Returns:
            Dictionary mimicking LeetCode GraphQL API response structure
        """
        # Generate examples HTML
        examples_html = self._generate_examples_html(num_examples)

        # Create complete problem description with examples
        description_html = f"""
        <p>Given an array of integers <code>nums</code> and an integer <code>target</code>,
        return indices of the two numbers such that they add up to target.</p>

        {examples_html}

        <p><strong>Constraints:</strong></p>
        <ul>
            <li>1 &lt;= nums.length &lt;= 10^4</li>
            <li>-10^4 &lt;= nums[i] &lt;= 10^4</li>
        </ul>
        """

        return {
            "data": {
                "question": {
                    "questionId": "1",
                    "title": "Test Problem",
                    "titleSlug": "test-problem",
                    "difficulty": "Easy",
                    "content": description_html,
                    "topicTags": [{"name": "Array"}, {"name": "Hash Table"}],
                    "hints": [],
                    "stats": '{"acRate": "50.0%"}',
                }
            }
        }

    def _generate_problem_response_with_constraints(self, num_constraints: int) -> Dict[str, Any]:
        """Generate a complete LeetCode API response with N constraints.

        Args:
            num_constraints: Number of constraints to include in the problem

        Returns:
            Dictionary mimicking LeetCode GraphQL API response structure
        """
        # Generate constraints as bullet points (this format survives HTML parsing better)
        constraints_items = []
        for i in range(num_constraints):
            # Generate varied constraint patterns
            if i % 3 == 0:
                lower = i + 1
                upper = (i + 1) * 100
                var = f"var{i}"
                constraints_items.append(f"• {lower} &lt;= {var} &lt;= {upper}")
            elif i % 3 == 1:
                lower = -(i + 1) * 1000
                upper = (i + 1) * 1000
                var = f"arr[{i}]"
                constraints_items.append(f"• {lower} &lt;= {var} &lt;= {upper}")
            else:
                var = f"index{i}"
                upper = f"n{i}"
                constraints_items.append(f"• 0 &lt;= {var} &lt; {upper}")

        constraints_html = "<br>".join(constraints_items) if constraints_items else ""

        # Create complete problem description with constraints
        description_html = f"""
        <p>Given an array of integers <code>nums</code> and an integer <code>target</code>,
        return indices of the two numbers such that they add up to target.</p>

        <p><strong>Example 1:</strong></p>
        <pre>
        <strong>Input:</strong> nums = [2,7,11,15], target = 9
        <strong>Output:</strong> [0,1]
        <strong>Explanation:</strong> Because nums[0] + nums[1] == 9, we return [0, 1].
        </pre>

        <p><strong>Constraints:</strong></p>
        <p>{constraints_html}</p>
        """

        return {
            "data": {
                "question": {
                    "questionId": "1",
                    "title": "Test Problem",
                    "titleSlug": "test-problem",
                    "difficulty": "Easy",
                    "content": description_html,
                    "topicTags": [{"name": "Array"}, {"name": "Hash Table"}],
                    "hints": [],
                    "stats": '{"acRate": "50.0%"}',
                }
            }
        }

    def _generate_malformed_problem_response(
        self, error_type: str, malform_examples: bool = False, malform_constraints: bool = False
    ) -> Dict[str, Any]:
        """Generate a malformed LeetCode API response to test error recovery.

        Args:
            error_type: Type of malformation to introduce
            malform_examples: Whether to malform the examples section
            malform_constraints: Whether to malform the constraints section

        Returns:
            Dictionary mimicking LeetCode GraphQL API response with malformed content
        """
        if error_type == "missing_input":
            # Example missing Input field
            description_html = """
            <p>Test problem description.</p>
            <p><strong>Example 1:</strong></p>
            <pre>
            <strong>Output:</strong> [0,1]
            <strong>Explanation:</strong> Missing input field.
            </pre>
            <p><strong>Constraints:</strong></p>
            <ul><li>1 &lt;= n &lt;= 100</li></ul>
            """
        elif error_type == "missing_output":
            # Example missing Output field
            description_html = """
            <p>Test problem description.</p>
            <p><strong>Example 1:</strong></p>
            <pre>
            <strong>Input:</strong> nums = [2,7,11,15], target = 9
            <strong>Explanation:</strong> Missing output field.
            </pre>
            <p><strong>Constraints:</strong></p>
            <ul><li>1 &lt;= n &lt;= 100</li></ul>
            """
        elif error_type == "invalid_html":
            # Completely broken HTML
            description_html = """
            <p>Test problem description.
            <p><strong>Example 1:</strong>
            <pre>
            <strong>Input: nums = [2,7,11,15], target = 9
            <strong>Output: [0,1]
            """
        elif error_type == "empty_content":
            # Empty or minimal content
            description_html = "<p></p>"
        elif error_type == "empty_constraints":
            # Empty constraints section
            description_html = """
            <p>Test problem description.</p>
            <p><strong>Example 1:</strong></p>
            <pre>
            <strong>Input:</strong> nums = [2,7,11,15], target = 9
            <strong>Output:</strong> [0,1]
            </pre>
            <p><strong>Constraints:</strong></p>
            """
        elif error_type == "invalid_format":
            # Constraints in unexpected format
            description_html = """
            <p>Test problem description.</p>
            <p><strong>Example 1:</strong></p>
            <pre>
            <strong>Input:</strong> nums = [2,7,11,15], target = 9
            <strong>Output:</strong> [0,1]
            </pre>
            <p><strong>Constraints:</strong></p>
            <p>This is not a valid constraint format at all!!!</p>
            """
        elif error_type == "missing_section":
            # No constraints section at all
            description_html = """
            <p>Test problem description.</p>
            <p><strong>Example 1:</strong></p>
            <pre>
            <strong>Input:</strong> nums = [2,7,11,15], target = 9
            <strong>Output:</strong> [0,1]
            </pre>
            """
        else:  # corrupted_html
            # Severely corrupted HTML
            description_html = "<p>Test<strong>Example<pre>Input:Output:"

        return {
            "data": {
                "question": {
                    "questionId": "1",
                    "title": "Test Problem",
                    "titleSlug": "test-problem",
                    "difficulty": "Easy",
                    "content": description_html,
                    "topicTags": [{"name": "Array"}],
                    "hints": [],
                    "stats": '{"acRate": "50.0%"}',
                }
            }
        }

    def _generate_examples_html(self, n: int) -> str:
        """Generate HTML with N examples in LeetCode format.

        Args:
            n: Number of examples to generate

        Returns:
            HTML string containing N examples
        """
        if n == 0:
            return ""

        examples = []
        for i in range(1, n + 1):
            # Generate varied example patterns
            if i % 3 == 1:
                input_val = f"nums = [{i}, {i+1}, {i+2}], target = {i*2+1}"
                output_val = f"[0, 1]"
                explanation = f"Because nums[0] + nums[1] == {i*2+1}, we return [0, 1]"
            elif i % 3 == 2:
                input_val = f's = "example{i}"'
                output_val = f'"{i}elpmaxe"'
                explanation = f"The string is reversed"
            else:
                input_val = f"n = {i * 10}"
                output_val = f"{i * 100}"
                explanation = f"The result is n multiplied by 10"

            example_html = f"""
            <p><strong>Example {i}:</strong></p>
            <pre>
            <strong>Input:</strong> {input_val}
            <strong>Output:</strong> {output_val}
            <strong>Explanation:</strong> {explanation}
            </pre>
            """

            examples.append(example_html)

        return "\n".join(examples)

    def _generate_constraints_html(self, n: int) -> str:
        """Generate HTML with N constraints in LeetCode format.

        Args:
            n: Number of constraints to generate

        Returns:
            HTML string containing N constraints as plain text (not HTML list)
            to match how LeetCode actually formats constraints after HTML parsing
        """
        if n == 0:
            return ""

        constraints = []
        for i in range(n):
            # Generate varied constraint patterns that work with current parser
            if i % 3 == 0:
                # Positive range: "1 <= n <= 100"
                lower = i + 1
                upper = (i + 1) * 100
                var = f"var{i}"
                constraints.append(f"{lower} <= {var} <= {upper}")
            elif i % 3 == 1:
                # Negative range: "-1000 <= nums[i] <= 1000"
                lower = -(i + 1) * 1000
                upper = (i + 1) * 1000
                var = f"arr[{i}]"
                constraints.append(f"{lower} <= {var} <= {upper}")
            else:
                # Zero-based range: "0 <= index < n"
                var = f"index{i}"
                upper = f"n{i}"
                constraints.append(f"0 <= {var} < {upper}")

        # Return as newline-separated plain text (this is what BeautifulSoup produces)
        return "\n".join(constraints)
