"""LeetCode adapter for converting API responses to domain models."""

import json
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from crawler.domain.entities import Problem, Submission
from crawler.domain.entities.enums import SubmissionStatus
from crawler.domain.value_objects import Difficulty, Example, Percentiles


class LeetCodeAdapter:
    """Adapts LeetCode API responses to domain models.
    
    This adapter handles the conversion of LeetCode-specific API response
    formats to our domain entities (Problem, Submission). It isolates
    API-specific parsing logic from the rest of the application.
    
    Key responsibilities:
    - Parse HTML content to plain text
    - Extract and parse example test cases
    - Convert API response structures to domain entities
    - Handle missing or optional fields gracefully
    
    Example:
        >>> adapter = LeetCodeAdapter()
        >>> problem = adapter.adapt_problem(api_response)
        >>> print(problem.title)
        "Two Sum"
    """
    
    def adapt_problem(self, raw_data: Dict[str, Any]) -> Problem:
        """Convert LeetCode API response to Problem entity.
        
        Args:
            raw_data: Raw API response from LeetCode GraphQL API
        
        Returns:
            Problem entity with all fields populated
        
        Raises:
            KeyError: If required fields are missing from the response
            ValueError: If data validation fails
        
        Example:
            >>> response = {"data": {"question": {...}}}
            >>> problem = adapter.adapt_problem(response)
        """
        question = raw_data["data"]["question"]
        
        # Parse HTML content to plain text
        description = self._parse_html(question["content"])
        
        # Parse example test cases
        examples = self._parse_examples(question.get("exampleTestcases", ""))
        
        # Parse acceptance rate from stats JSON
        acceptance_rate = self._parse_acceptance_rate(question.get("stats", "{}"))
        
        # Extract topic tags
        topics = [tag["name"] for tag in question.get("topicTags", [])]
        
        # Get hints (may be empty list)
        hints = question.get("hints", [])
        
        # Get constraints (may be empty string)
        constraints = question.get("constraints", "")
        
        return Problem(
            id=question["titleSlug"],
            platform="leetcode",
            title=question["title"],
            difficulty=Difficulty(question["difficulty"]),
            description=description,
            topics=topics,
            constraints=constraints,
            examples=examples,
            hints=hints,
            acceptance_rate=acceptance_rate
        )
    
    def adapt_submission(self, raw_data: Dict[str, Any], problem_id: str = "unknown") -> Submission:
        """Convert LeetCode submission response to Submission entity.
        
        Args:
            raw_data: Raw API response from LeetCode submission API
            problem_id: The problem ID this submission belongs to (default: "unknown")
        
        Returns:
            Submission entity with all fields populated
        
        Raises:
            KeyError: If required fields are missing from the response
            ValueError: If data validation fails
        
        Example:
            >>> response = {"data": {"submissionDetails": {...}}}
            >>> submission = adapter.adapt_submission(response, "two-sum")
        """
        details = raw_data["data"]["submissionDetails"]
        
        # Map LeetCode status to our enum
        status = self._map_submission_status(details["statusDisplay"])
        
        # Parse percentiles if available
        percentiles = None
        if "runtimePercentile" in details and "memoryPercentile" in details:
            percentiles = Percentiles(
                runtime=float(details["runtimePercentile"]),
                memory=float(details["memoryPercentile"])
            )
        
        # Convert timestamp string to integer
        timestamp = int(details["timestamp"])
        
        return Submission(
            id=details["id"],
            problem_id=problem_id,
            language=details["langName"],
            code=details["code"],
            status=status,
            runtime=details["runtime"],
            memory=details["memory"],
            timestamp=timestamp,
            percentiles=percentiles
        )
    
    def _parse_html(self, html: str) -> str:
        """Extract plain text from HTML content.
        
        Uses BeautifulSoup to parse HTML and extract text content,
        removing all HTML tags and formatting.
        
        Args:
            html: HTML string to parse
        
        Returns:
            Plain text content with HTML tags removed
        
        Example:
            >>> html = "<p>Hello <code>world</code></p>"
            >>> adapter._parse_html(html)
            "Hello world"
        """
        if not html:
            return ""
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up whitespace
        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _parse_examples(self, examples_str: str) -> List[Example]:
        """Parse example test cases from LeetCode format.
        
        LeetCode provides examples as a string with newline-separated test cases.
        Each test case is typically in the format: "input = value"
        
        Args:
            examples_str: String containing example test cases
        
        Returns:
            List of Example value objects
        
        Example:
            >>> examples = "nums = [2,7,11,15], target = 9\\nnums = [3,2,4], target = 6"
            >>> result = adapter._parse_examples(examples)
            >>> len(result)
            2
        """
        if not examples_str:
            return []
        
        examples = []
        
        # Split by newline to get individual test cases
        lines = examples_str.strip().split('\n')
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Each line is an input example
            # We don't have explicit outputs in the exampleTestcases field,
            # so we'll use the line as input and a placeholder for output
            examples.append(Example(
                input=line.strip(),
                output=f"Example {i + 1} output",  # Placeholder
                explanation=None
            ))
        
        return examples
    
    def _parse_acceptance_rate(self, stats_json: str) -> float:
        """Parse acceptance rate from stats JSON string.
        
        Args:
            stats_json: JSON string containing problem statistics
        
        Returns:
            Acceptance rate as a float (0-100)
        
        Example:
            >>> stats = '{"acRate": "49.1%"}'
            >>> adapter._parse_acceptance_rate(stats)
            49.1
        """
        if not stats_json:
            return 0.0
        
        try:
            stats = json.loads(stats_json)
            ac_rate_str = stats.get("acRate", "0%")
            
            # Remove '%' and convert to float
            ac_rate = float(ac_rate_str.rstrip('%'))
            
            return ac_rate
        except (json.JSONDecodeError, ValueError, KeyError):
            return 0.0
    
    def _map_submission_status(self, status_display: str) -> SubmissionStatus:
        """Map LeetCode status string to SubmissionStatus enum.
        
        Args:
            status_display: Status string from LeetCode API
        
        Returns:
            Corresponding SubmissionStatus enum value
        
        Example:
            >>> adapter._map_submission_status("Accepted")
            SubmissionStatus.ACCEPTED
        """
        status_map = {
            "Accepted": SubmissionStatus.ACCEPTED,
            "Wrong Answer": SubmissionStatus.WRONG_ANSWER,
            "Time Limit Exceeded": SubmissionStatus.TIME_LIMIT_EXCEEDED,
            "Memory Limit Exceeded": SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
            "Runtime Error": SubmissionStatus.RUNTIME_ERROR,
            "Compile Error": SubmissionStatus.COMPILE_ERROR,
        }
        
        return status_map.get(status_display, SubmissionStatus.RUNTIME_ERROR)
