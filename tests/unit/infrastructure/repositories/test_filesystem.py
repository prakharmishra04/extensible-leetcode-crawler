"""Unit tests for FileSystemRepository."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock

from crawler.infrastructure.repositories.filesystem import FileSystemRepository
from crawler.application.interfaces.formatter import OutputFormatter
from crawler.domain.entities import Problem, Submission
from crawler.domain.value_objects import Difficulty, Example, Percentiles
from crawler.domain.entities.enums import SubmissionStatus
from crawler.domain.exceptions import RepositoryException


class MockFormatter(OutputFormatter):
    """Mock formatter for testing."""
    
    def format_problem(self, problem: Problem, submission=None) -> str:
        """Return a simple formatted string."""
        return f"Problem: {problem.title}"
    
    def get_file_extension(self) -> str:
        """Return py extension."""
        return "py"


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository for testing."""
    formatter = MockFormatter()
    logger = Mock()
    return FileSystemRepository(tmp_path, formatter, logger)


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id="two-sum",
        platform="leetcode",
        title="Two Sum",
        difficulty=Difficulty("Easy"),
        description="Find two numbers that add up to target",
        topics=["Array", "Hash Table"],
        constraints="2 <= nums.length <= 10^4",
        examples=[
            Example(
                input="nums = [2,7,11,15], target = 9",
                output="[0,1]",
                explanation="nums[0] + nums[1] == 9"
            )
        ],
        hints=["Use a hash map"],
        acceptance_rate=49.1
    )


@pytest.fixture
def sample_submission():
    """Create a sample submission for testing."""
    return Submission(
        id="sub-123",
        problem_id="two-sum",
        language="Python",
        code="def twoSum(nums, target):\n    pass",
        status=SubmissionStatus.ACCEPTED,
        runtime="52 ms",
        memory="15.2 MB",
        timestamp=1234567890,
        percentiles=Percentiles(runtime=85.5, memory=90.2)
    )


class TestFileSystemRepository:
    """Test FileSystemRepository implementation."""
    
    def test_initialization_creates_base_directory(self, tmp_path):
        """Test that initialization creates the base directory."""
        base_path = tmp_path / "problems"
        formatter = MockFormatter()
        logger = Mock()
        
        repo = FileSystemRepository(base_path, formatter, logger)
        
        assert base_path.exists()
        assert base_path.is_dir()
    
    def test_save_creates_problem_directory(self, temp_repo, sample_problem, tmp_path):
        """Test that save creates the correct directory structure."""
        temp_repo.save(sample_problem)
        
        problem_dir = tmp_path / "leetcode" / "two-sum"
        assert problem_dir.exists()
        assert problem_dir.is_dir()
    
    def test_save_creates_solution_file(self, temp_repo, sample_problem, tmp_path):
        """Test that save creates the solution file."""
        temp_repo.save(sample_problem)
        
        solution_file = tmp_path / "leetcode" / "two-sum" / "solution.py"
        assert solution_file.exists()
        assert solution_file.read_text() == "Problem: Two Sum"
    
    def test_save_creates_metadata_file(self, temp_repo, sample_problem, tmp_path):
        """Test that save creates the metadata file."""
        temp_repo.save(sample_problem)
        
        metadata_file = tmp_path / "leetcode" / "two-sum" / "metadata.json"
        assert metadata_file.exists()
        
        metadata = json.loads(metadata_file.read_text())
        assert metadata["id"] == "two-sum"
        assert metadata["title"] == "Two Sum"
        assert metadata["platform"] == "leetcode"
    
    def test_save_with_submission_includes_submission_data(
        self, temp_repo, sample_problem, sample_submission, tmp_path
    ):
        """Test that save includes submission data in metadata."""
        temp_repo.save(sample_problem, sample_submission)
        
        metadata_file = tmp_path / "leetcode" / "two-sum" / "metadata.json"
        metadata = json.loads(metadata_file.read_text())
        
        assert "submission" in metadata
        assert metadata["submission"]["id"] == "sub-123"
        assert metadata["submission"]["code"] == "def twoSum(nums, target):\n    pass"
    
    def test_find_by_id_returns_problem_when_exists(
        self, temp_repo, sample_problem
    ):
        """Test that find_by_id returns the problem when it exists."""
        temp_repo.save(sample_problem)
        
        found = temp_repo.find_by_id("two-sum", "leetcode")
        
        assert found is not None
        assert found.id == "two-sum"
        assert found.title == "Two Sum"
        assert found.difficulty.level == "Easy"
    
    def test_find_by_id_returns_none_when_not_exists(self, temp_repo):
        """Test that find_by_id returns None when problem doesn't exist."""
        found = temp_repo.find_by_id("nonexistent", "leetcode")
        
        assert found is None
    
    def test_find_by_id_reconstructs_all_fields(
        self, temp_repo, sample_problem
    ):
        """Test that find_by_id correctly reconstructs all problem fields."""
        temp_repo.save(sample_problem)
        
        found = temp_repo.find_by_id("two-sum", "leetcode")
        
        assert found.id == sample_problem.id
        assert found.platform == sample_problem.platform
        assert found.title == sample_problem.title
        assert found.difficulty == sample_problem.difficulty
        assert found.description == sample_problem.description
        assert found.topics == sample_problem.topics
        assert found.constraints == sample_problem.constraints
        assert len(found.examples) == len(sample_problem.examples)
        assert found.hints == sample_problem.hints
        assert found.acceptance_rate == sample_problem.acceptance_rate
    
    def test_exists_returns_true_for_saved_problem(
        self, temp_repo, sample_problem
    ):
        """Test that exists returns True for saved problems."""
        temp_repo.save(sample_problem)
        
        assert temp_repo.exists("two-sum", "leetcode") is True
    
    def test_exists_returns_false_for_unsaved_problem(self, temp_repo):
        """Test that exists returns False for unsaved problems."""
        assert temp_repo.exists("nonexistent", "leetcode") is False
    
    def test_list_all_returns_empty_list_when_no_problems(self, temp_repo):
        """Test that list_all returns empty list when no problems exist."""
        problems = temp_repo.list_all()
        
        assert problems == []
    
    def test_list_all_returns_all_problems(self, temp_repo):
        """Test that list_all returns all saved problems."""
        problem1 = Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=50.0
        )
        problem2 = Problem(
            id="three-sum",
            platform="leetcode",
            title="Three Sum",
            difficulty=Difficulty("Medium"),
            description="Test",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=30.0
        )
        
        temp_repo.save(problem1)
        temp_repo.save(problem2)
        
        problems = temp_repo.list_all()
        
        assert len(problems) == 2
        assert any(p.id == "two-sum" for p in problems)
        assert any(p.id == "three-sum" for p in problems)
    
    def test_list_all_filters_by_platform(self, temp_repo):
        """Test that list_all filters by platform when specified."""
        leetcode_problem = Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=50.0
        )
        hackerrank_problem = Problem(
            id="array-sum",
            platform="hackerrank",
            title="Array Sum",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=60.0
        )
        
        temp_repo.save(leetcode_problem)
        temp_repo.save(hackerrank_problem)
        
        leetcode_problems = temp_repo.list_all(platform="leetcode")
        
        assert len(leetcode_problems) == 1
        assert leetcode_problems[0].id == "two-sum"
        assert leetcode_problems[0].platform == "leetcode"
    
    def test_delete_removes_problem_directory(
        self, temp_repo, sample_problem, tmp_path
    ):
        """Test that delete removes the problem directory."""
        temp_repo.save(sample_problem)
        
        problem_dir = tmp_path / "leetcode" / "two-sum"
        assert problem_dir.exists()
        
        deleted = temp_repo.delete("two-sum", "leetcode")
        
        assert deleted is True
        assert not problem_dir.exists()
    
    def test_delete_returns_false_when_problem_not_exists(self, temp_repo):
        """Test that delete returns False when problem doesn't exist."""
        deleted = temp_repo.delete("nonexistent", "leetcode")
        
        assert deleted is False
    
    def test_delete_is_idempotent(self, temp_repo, sample_problem):
        """Test that delete can be called multiple times safely."""
        temp_repo.save(sample_problem)
        
        # First delete should succeed
        assert temp_repo.delete("two-sum", "leetcode") is True
        
        # Second delete should return False but not raise error
        assert temp_repo.delete("two-sum", "leetcode") is False
    
    def test_save_overwrites_existing_problem(self, temp_repo, sample_problem):
        """Test that save overwrites existing problems."""
        temp_repo.save(sample_problem)
        
        # Modify and save again
        sample_problem.title = "Two Sum Updated"
        temp_repo.save(sample_problem)
        
        found = temp_repo.find_by_id("two-sum", "leetcode")
        assert found.title == "Two Sum Updated"
    
    def test_find_by_id_raises_exception_on_invalid_json(
        self, temp_repo, sample_problem, tmp_path
    ):
        """Test that find_by_id raises RepositoryException on invalid JSON."""
        temp_repo.save(sample_problem)
        
        # Corrupt the metadata file
        metadata_file = tmp_path / "leetcode" / "two-sum" / "metadata.json"
        metadata_file.write_text("invalid json{")
        
        with pytest.raises(RepositoryException, match="Failed to parse metadata"):
            temp_repo.find_by_id("two-sum", "leetcode")
    
    def test_serialize_problem_includes_all_fields(self, temp_repo, sample_problem):
        """Test that _serialize_problem includes all problem fields."""
        data = temp_repo._serialize_problem(sample_problem)
        
        assert data["id"] == "two-sum"
        assert data["platform"] == "leetcode"
        assert data["title"] == "Two Sum"
        assert data["difficulty"] == "Easy"
        assert data["description"] == "Find two numbers that add up to target"
        assert data["topics"] == ["Array", "Hash Table"]
        assert data["constraints"] == "2 <= nums.length <= 10^4"
        assert len(data["examples"]) == 1
        assert data["hints"] == ["Use a hash map"]
        assert data["acceptance_rate"] == 49.1
    
    def test_serialize_problem_with_submission(
        self, temp_repo, sample_problem, sample_submission
    ):
        """Test that _serialize_problem includes submission data."""
        data = temp_repo._serialize_problem(sample_problem, sample_submission)
        
        assert "submission" in data
        assert data["submission"]["id"] == "sub-123"
        assert data["submission"]["problem_id"] == "two-sum"
        assert data["submission"]["language"] == "Python"
        assert data["submission"]["code"] == "def twoSum(nums, target):\n    pass"
        assert data["submission"]["status"] == "Accepted"
        assert data["submission"]["runtime"] == "52 ms"
        assert data["submission"]["memory"] == "15.2 MB"
        assert data["submission"]["timestamp"] == 1234567890
        assert data["submission"]["percentiles"]["runtime"] == 85.5
        assert data["submission"]["percentiles"]["memory"] == 90.2
    
    def test_deserialize_problem_reconstructs_correctly(
        self, temp_repo, sample_problem
    ):
        """Test that _deserialize_problem correctly reconstructs a problem."""
        data = temp_repo._serialize_problem(sample_problem)
        reconstructed = temp_repo._deserialize_problem(data)
        
        assert reconstructed.id == sample_problem.id
        assert reconstructed.platform == sample_problem.platform
        assert reconstructed.title == sample_problem.title
        assert reconstructed.difficulty == sample_problem.difficulty
        assert reconstructed.description == sample_problem.description
        assert reconstructed.topics == sample_problem.topics
        assert reconstructed.constraints == sample_problem.constraints
        assert len(reconstructed.examples) == len(sample_problem.examples)
        assert reconstructed.hints == sample_problem.hints
        assert reconstructed.acceptance_rate == sample_problem.acceptance_rate
    
    def test_round_trip_serialization(self, temp_repo, sample_problem):
        """Test that serialize -> deserialize preserves all data."""
        data = temp_repo._serialize_problem(sample_problem)
        reconstructed = temp_repo._deserialize_problem(data)
        
        # Serialize again and compare
        data2 = temp_repo._serialize_problem(reconstructed)
        
        assert data == data2
