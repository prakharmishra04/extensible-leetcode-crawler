"""Unit tests for User entity"""
import pytest
from src.crawler.domain.entities import User


class TestUser:
    """Test suite for User entity"""
    
    def test_valid_user(self):
        """Test creating a valid user"""
        user = User(
            username="john_doe",
            platform="leetcode",
            solved_count=150,
            problems_solved=["two-sum", "add-two-numbers"] + ["problem"] * 148
        )
        assert user.username == "john_doe"
        assert user.platform == "leetcode"
        assert user.solved_count == 150
        assert len(user.problems_solved) == 150
    
    def test_user_with_zero_solved(self):
        """Test creating user with zero solved problems"""
        user = User(
            username="newbie",
            platform="leetcode",
            solved_count=0,
            problems_solved=[]
        )
        assert user.solved_count == 0
        assert len(user.problems_solved) == 0
    
    def test_empty_username_raises_error(self):
        """Test that empty username raises ValueError"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            User(
                username="",
                platform="leetcode",
                solved_count=0,
                problems_solved=[]
            )
    
    def test_empty_platform_raises_error(self):
        """Test that empty platform raises ValueError"""
        with pytest.raises(ValueError, match="Platform cannot be empty"):
            User(
                username="john_doe",
                platform="",
                solved_count=0,
                problems_solved=[]
            )
    
    def test_negative_solved_count_raises_error(self):
        """Test that negative solved count raises ValueError"""
        with pytest.raises(ValueError, match="Solved count must be non-negative"):
            User(
                username="john_doe",
                platform="leetcode",
                solved_count=-1,
                problems_solved=[]
            )
    
    def test_mismatched_count_and_list_raises_error(self):
        """Test that mismatched count and list length raises ValueError"""
        with pytest.raises(ValueError, match="Problems solved list length .* must match solved count"):
            User(
                username="john_doe",
                platform="leetcode",
                solved_count=10,
                problems_solved=["two-sum", "add-two-numbers"]  # Only 2 items
            )
    
    def test_list_longer_than_count_raises_error(self):
        """Test that list longer than count raises ValueError"""
        with pytest.raises(ValueError, match="Problems solved list length .* must match solved count"):
            User(
                username="john_doe",
                platform="leetcode",
                solved_count=1,
                problems_solved=["two-sum", "add-two-numbers"]  # 2 items but count is 1
            )
