"""Unit tests for Difficulty value object"""
import pytest
from src.crawler.domain.value_objects import Difficulty


class TestDifficulty:
    """Test suite for Difficulty value object"""
    
    def test_valid_easy_difficulty(self):
        """Test creating Easy difficulty"""
        diff = Difficulty("Easy")
        assert diff.level == "Easy"
        assert diff.is_easy()
        assert not diff.is_medium()
        assert not diff.is_hard()
    
    def test_valid_medium_difficulty(self):
        """Test creating Medium difficulty"""
        diff = Difficulty("Medium")
        assert diff.level == "Medium"
        assert not diff.is_easy()
        assert diff.is_medium()
        assert not diff.is_hard()
    
    def test_valid_hard_difficulty(self):
        """Test creating Hard difficulty"""
        diff = Difficulty("Hard")
        assert diff.level == "Hard"
        assert not diff.is_easy()
        assert not diff.is_medium()
        assert diff.is_hard()
    
    def test_invalid_difficulty_raises_error(self):
        """Test that invalid difficulty raises ValueError"""
        with pytest.raises(ValueError, match="Invalid difficulty"):
            Difficulty("Impossible")
    
    def test_empty_difficulty_raises_error(self):
        """Test that empty difficulty raises ValueError"""
        with pytest.raises(ValueError, match="Invalid difficulty"):
            Difficulty("")
    
    def test_difficulty_is_immutable(self):
        """Test that Difficulty is immutable"""
        diff = Difficulty("Easy")
        with pytest.raises(AttributeError):
            diff.level = "Hard"
    
    def test_difficulty_equality(self):
        """Test that two difficulties with same level are equal"""
        diff1 = Difficulty("Easy")
        diff2 = Difficulty("Easy")
        assert diff1 == diff2
    
    def test_difficulty_hash(self):
        """Test that Difficulty can be used in sets/dicts"""
        diff1 = Difficulty("Easy")
        diff2 = Difficulty("Medium")
        diff_set = {diff1, diff2, diff1}
        assert len(diff_set) == 2
