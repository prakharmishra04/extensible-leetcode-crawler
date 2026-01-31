"""Unit tests for Problem entity"""

import pytest

from src.crawler.domain.entities import Problem
from src.crawler.domain.value_objects import Constraint, Difficulty, Example


class TestProblem:
    """Test suite for Problem entity"""

    def test_valid_problem(self):
        """Test creating a valid problem"""
        problem = Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Find two numbers that add up to target",
            topics=["Array", "Hash Table"],
            constraints=[Constraint(text="2 <= nums.length <= 10^4")],
            examples=[Example(input="[2,7,11,15], 9", output="[0,1]")],
            hints=["Use a hash map"],
            acceptance_rate=49.5,
        )
        assert problem.id == "two-sum"
        assert problem.platform == "leetcode"
        assert problem.title == "Two Sum"
        assert problem.difficulty.is_easy()
        assert len(problem.topics) == 2
        assert len(problem.examples) == 1
        assert len(problem.hints) == 1
        assert len(problem.constraints) == 1
        assert problem.constraints[0].text == "2 <= nums.length <= 10^4"

    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError"""
        with pytest.raises(ValueError, match="Problem ID cannot be empty"):
            Problem(
                id="",
                platform="leetcode",
                title="Test",
                difficulty=Difficulty("Easy"),
                description="Test",
                topics=[],
                constraints=[],
                examples=[],
                hints=[],
                acceptance_rate=50.0,
            )

    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError"""
        with pytest.raises(ValueError, match="Problem title cannot be empty"):
            Problem(
                id="test",
                platform="leetcode",
                title="",
                difficulty=Difficulty("Easy"),
                description="Test",
                topics=[],
                constraints=[],
                examples=[],
                hints=[],
                acceptance_rate=50.0,
            )

    def test_empty_platform_raises_error(self):
        """Test that empty platform raises ValueError"""
        with pytest.raises(ValueError, match="Problem platform cannot be empty"):
            Problem(
                id="test",
                platform="",
                title="Test",
                difficulty=Difficulty("Easy"),
                description="Test",
                topics=[],
                constraints=[],
                examples=[],
                hints=[],
                acceptance_rate=50.0,
            )

    def test_negative_acceptance_rate_raises_error(self):
        """Test that negative acceptance rate raises ValueError"""
        with pytest.raises(ValueError, match="Acceptance rate must be between 0 and 100"):
            Problem(
                id="test",
                platform="leetcode",
                title="Test",
                difficulty=Difficulty("Easy"),
                description="Test",
                topics=[],
                constraints=[],
                examples=[],
                hints=[],
                acceptance_rate=-1.0,
            )

    def test_acceptance_rate_over_100_raises_error(self):
        """Test that acceptance rate over 100 raises ValueError"""
        with pytest.raises(ValueError, match="Acceptance rate must be between 0 and 100"):
            Problem(
                id="test",
                platform="leetcode",
                title="Test",
                difficulty=Difficulty("Easy"),
                description="Test",
                topics=[],
                constraints=[],
                examples=[],
                hints=[],
                acceptance_rate=101.0,
            )

    def test_problem_with_empty_lists(self):
        """Test creating problem with empty lists"""
        problem = Problem(
            id="test",
            platform="leetcode",
            title="Test",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=[],
            constraints=[],
            examples=[],
            hints=[],
            acceptance_rate=50.0,
        )
        assert len(problem.topics) == 0
        assert len(problem.examples) == 0
        assert len(problem.hints) == 0
        assert len(problem.constraints) == 0

    def test_constraints_text_property(self):
        """Test backward compatibility property for constraints_text"""
        constraints = [
            Constraint(text="1 <= n <= 100"),
            Constraint(text="-10^4 <= nums[i] <= 10^4"),
            Constraint(text="All elements are unique"),
        ]
        problem = Problem(
            id="test",
            platform="leetcode",
            title="Test",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=[],
            constraints=constraints,
            examples=[],
            hints=[],
            acceptance_rate=50.0,
        )
        expected_text = "1 <= n <= 100\n-10^4 <= nums[i] <= 10^4\nAll elements are unique"
        assert problem.constraints_text == expected_text

    def test_constraints_text_property_empty_list(self):
        """Test constraints_text property with empty constraints list"""
        problem = Problem(
            id="test",
            platform="leetcode",
            title="Test",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=[],
            constraints=[],
            examples=[],
            hints=[],
            acceptance_rate=50.0,
        )
        assert problem.constraints_text == ""
