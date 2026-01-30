"""Unit tests for Submission entity"""
import pytest
from src.crawler.domain.entities import Submission, SubmissionStatus
from src.crawler.domain.value_objects import Percentiles


class TestSubmission:
    """Test suite for Submission entity"""
    
    def test_valid_submission_without_percentiles(self):
        """Test creating a valid submission without percentiles"""
        submission = Submission(
            id="12345",
            problem_id="two-sum",
            language="Python3",
            code="def twoSum(nums, target): pass",
            status=SubmissionStatus.ACCEPTED,
            runtime="52 ms",
            memory="14.5 MB",
            timestamp=1640000000
        )
        assert submission.id == "12345"
        assert submission.problem_id == "two-sum"
        assert submission.language == "Python3"
        assert submission.status == SubmissionStatus.ACCEPTED
        assert submission.percentiles is None
    
    def test_valid_submission_with_percentiles(self):
        """Test creating a valid submission with percentiles"""
        submission = Submission(
            id="12345",
            problem_id="two-sum",
            language="Python3",
            code="def twoSum(nums, target): pass",
            status=SubmissionStatus.ACCEPTED,
            runtime="52 ms",
            memory="14.5 MB",
            timestamp=1640000000,
            percentiles=Percentiles(runtime=85.5, memory=92.3)
        )
        assert submission.percentiles is not None
        assert submission.percentiles.runtime == 85.5
        assert submission.percentiles.memory == 92.3
    
    def test_empty_code_raises_error(self):
        """Test that empty code raises ValueError"""
        with pytest.raises(ValueError, match="Submission code cannot be empty"):
            Submission(
                id="12345",
                problem_id="two-sum",
                language="Python3",
                code="",
                status=SubmissionStatus.ACCEPTED,
                runtime="52 ms",
                memory="14.5 MB",
                timestamp=1640000000
            )
    
    def test_negative_timestamp_raises_error(self):
        """Test that negative timestamp raises ValueError"""
        with pytest.raises(ValueError, match="Timestamp must be non-negative"):
            Submission(
                id="12345",
                problem_id="two-sum",
                language="Python3",
                code="def twoSum(nums, target): pass",
                status=SubmissionStatus.ACCEPTED,
                runtime="52 ms",
                memory="14.5 MB",
                timestamp=-1
            )
    
    def test_empty_problem_id_raises_error(self):
        """Test that empty problem_id raises ValueError"""
        with pytest.raises(ValueError, match="Problem ID cannot be empty"):
            Submission(
                id="12345",
                problem_id="",
                language="Python3",
                code="def twoSum(nums, target): pass",
                status=SubmissionStatus.ACCEPTED,
                runtime="52 ms",
                memory="14.5 MB",
                timestamp=1640000000
            )
    
    def test_empty_language_raises_error(self):
        """Test that empty language raises ValueError"""
        with pytest.raises(ValueError, match="Language cannot be empty"):
            Submission(
                id="12345",
                problem_id="two-sum",
                language="",
                code="def twoSum(nums, target): pass",
                status=SubmissionStatus.ACCEPTED,
                runtime="52 ms",
                memory="14.5 MB",
                timestamp=1640000000
            )
    
    def test_different_submission_statuses(self):
        """Test creating submissions with different statuses"""
        statuses = [
            SubmissionStatus.ACCEPTED,
            SubmissionStatus.WRONG_ANSWER,
            SubmissionStatus.TIME_LIMIT_EXCEEDED,
            SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
            SubmissionStatus.RUNTIME_ERROR,
            SubmissionStatus.COMPILE_ERROR
        ]
        
        for status in statuses:
            submission = Submission(
                id="12345",
                problem_id="two-sum",
                language="Python3",
                code="def twoSum(nums, target): pass",
                status=status,
                runtime="52 ms",
                memory="14.5 MB",
                timestamp=1640000000
            )
            assert submission.status == status
