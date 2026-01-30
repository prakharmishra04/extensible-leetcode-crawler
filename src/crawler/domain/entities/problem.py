"""Problem entity"""
from dataclasses import dataclass
from typing import List

from ..value_objects.difficulty import Difficulty
from ..value_objects.example import Example


@dataclass
class Problem:
    """Represents a coding problem from any platform"""
    
    id: str
    platform: str
    title: str
    difficulty: Difficulty
    description: str
    topics: List[str]
    constraints: str
    examples: List[Example]
    hints: List[str]
    acceptance_rate: float
    
    def __post_init__(self):
        """Validate Problem entity fields"""
        if not self.id:
            raise ValueError("Problem ID cannot be empty")
        if not self.title:
            raise ValueError("Problem title cannot be empty")
        if not self.platform:
            raise ValueError("Problem platform cannot be empty")
        if self.acceptance_rate < 0 or self.acceptance_rate > 100:
            raise ValueError("Acceptance rate must be between 0 and 100")
