"""Python file formatter for problems."""

from typing import Optional

from crawler.application.interfaces.formatter import OutputFormatter
from crawler.domain.entities import Problem, Submission


class PythonFormatter(OutputFormatter):
    """
    Format problems as Python files with comments.
    
    This formatter creates Python files with the problem description,
    constraints, examples, and hints as comments, followed by the
    user's submission code if available.
    
    The output format is designed to be:
    - Readable as documentation
    - Executable as Python code
    - Compatible with Python syntax highlighting
    """
    
    def format_problem(
        self,
        problem: Problem,
        submission: Optional[Submission] = None
    ) -> str:
        """
        Format a problem as a Python file with comments.
        
        Args:
            problem: The problem entity to format
            submission: Optional submission entity to include
        
        Returns:
            str: Formatted Python file content
        
        Example output:
            '''
            Two Sum
            Difficulty: Easy
            Platform: leetcode
            Topics: Array, Hash Table
            
            Description:
            Given an array of integers nums and an integer target,
            return indices of the two numbers such that they add up to target.
            
            Constraints:
            2 <= nums.length <= 10^4
            '''
            
            # Example 1:
            # Input: nums = [2,7,11,15], target = 9
            # Output: [0,1]
            # Explanation: nums[0] + nums[1] == 9
            
            # Last Accepted Submission
            # Runtime: 52 ms
            # Memory: 15.2 MB
            
            def twoSum(nums, target):
                pass
        """
        lines = []
        
        # Add docstring header
        lines.append('"""')
        lines.append(problem.title)
        lines.append(f"Difficulty: {problem.difficulty.level}")
        lines.append(f"Platform: {problem.platform}")
        
        if problem.topics:
            lines.append(f"Topics: {', '.join(problem.topics)}")
        
        lines.append("")
        
        # Add description
        lines.append("Description:")
        lines.append(problem.description)
        lines.append("")
        
        # Add constraints
        if problem.constraints:
            lines.append("Constraints:")
            lines.append(problem.constraints)
            lines.append("")
        
        lines.append('"""')
        lines.append("")
        
        # Add examples as comments
        if problem.examples:
            for i, example in enumerate(problem.examples, 1):
                lines.append(f"# Example {i}:")
                lines.append(f"# Input: {example.input}")
                lines.append(f"# Output: {example.output}")
                if example.explanation:
                    lines.append(f"# Explanation: {example.explanation}")
                lines.append("")
        
        # Add hints as comments
        if problem.hints:
            lines.append("# Hints:")
            for i, hint in enumerate(problem.hints, 1):
                lines.append(f"# {i}. {hint}")
            lines.append("")
        
        # Add submission code if available
        if submission:
            lines.append("# Last Accepted Submission")
            lines.append(f"# Runtime: {submission.runtime}")
            lines.append(f"# Memory: {submission.memory}")
            if submission.percentiles:
                lines.append(
                    f"# Runtime Percentile: {submission.percentiles.runtime:.1f}%"
                )
                lines.append(
                    f"# Memory Percentile: {submission.percentiles.memory:.1f}%"
                )
            lines.append("")
            lines.append(submission.code)
        else:
            # Add placeholder function
            lines.append("# TODO: Implement solution")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_file_extension(self) -> str:
        """
        Get the file extension for Python files.
        
        Returns:
            str: "py"
        """
        return "py"
