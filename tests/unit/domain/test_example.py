"""Unit tests for Example value object"""
import pytest
from src.crawler.domain.value_objects import Example


class TestExample:
    """Test suite for Example value object"""
    
    def test_valid_example_without_explanation(self):
        """Test creating example without explanation"""
        example = Example(input="[1,2,3]", output="6")
        assert example.input == "[1,2,3]"
        assert example.output == "6"
        assert example.explanation is None
    
    def test_valid_example_with_explanation(self):
        """Test creating example with explanation"""
        example = Example(
            input="[1,2,3]",
            output="6",
            explanation="Sum of all elements"
        )
        assert example.input == "[1,2,3]"
        assert example.output == "6"
        assert example.explanation == "Sum of all elements"
    
    def test_empty_input_raises_error(self):
        """Test that empty input raises ValueError"""
        with pytest.raises(ValueError, match="input cannot be empty"):
            Example(input="", output="6")
    
    def test_empty_output_raises_error(self):
        """Test that empty output raises ValueError"""
        with pytest.raises(ValueError, match="output cannot be empty"):
            Example(input="[1,2,3]", output="")
    
    def test_example_is_immutable(self):
        """Test that Example is immutable"""
        example = Example(input="[1,2,3]", output="6")
        with pytest.raises(AttributeError):
            example.input = "[4,5,6]"
    
    def test_example_equality(self):
        """Test that two examples with same values are equal"""
        ex1 = Example(input="[1,2]", output="3")
        ex2 = Example(input="[1,2]", output="3")
        assert ex1 == ex2
    
    def test_example_with_different_explanation_not_equal(self):
        """Test that examples with different explanations are not equal"""
        ex1 = Example(input="[1,2]", output="3", explanation="Sum")
        ex2 = Example(input="[1,2]", output="3", explanation="Total")
        assert ex1 != ex2
