"""Custom Hypothesis strategies for property-based testing

This module provides custom strategies for generating valid domain entities
for property-based testing. These strategies generate realistic test data
that respects all validation rules defined in the domain layer.

Requirements: 1.5 (Unit tests for all business logic)
"""
from hypothesis import strategies as st
from hypothesis.strategies import composite

from src.crawler.domain.entities.problem import Problem
from src.crawler.domain.entities.submission import Submission
from src.crawler.domain.entities.enums import SubmissionStatus
from src.crawler.domain.value_objects.difficulty import Difficulty
from src.crawler.domain.value_objects.example import Example
from src.crawler.domain.value_objects.percentiles import Percentiles


# ============================================================================
# Value Object Strategies
# ============================================================================

@composite
def example_strategy(draw) -> Example:
    """
    Generate valid Example value objects.
    
    Generates examples with:
    - Non-empty input strings (1-500 chars)
    - Non-empty output strings (1-500 chars)
    - Optional explanation (None or 1-500 chars)
    
    Returns:
        Example: A valid Example value object
    """
    input_text = draw(st.text(min_size=1, max_size=500, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'),  # Exclude surrogates and control chars
        blacklist_characters='\x00'
    )))
    output_text = draw(st.text(min_size=1, max_size=500, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'),
        blacklist_characters='\x00'
    )))
    explanation = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=500, alphabet=st.characters(
            blacklist_categories=('Cs', 'Cc'),
            blacklist_characters='\x00'
        ))
    ))
    
    return Example(
        input=input_text,
        output=output_text,
        explanation=explanation
    )


@composite
def difficulty_strategy(draw) -> Difficulty:
    """
    Generate valid Difficulty value objects.
    
    Generates difficulties with valid levels: Easy, Medium, or Hard.
    
    Returns:
        Difficulty: A valid Difficulty value object
    """
    level = draw(st.sampled_from(["Easy", "Medium", "Hard"]))
    return Difficulty(level)


@composite
def percentiles_strategy(draw) -> Percentiles:
    """
    Generate valid Percentiles value objects.
    
    Generates percentiles with:
    - Runtime percentile: 0.0 to 100.0
    - Memory percentile: 0.0 to 100.0
    
    Returns:
        Percentiles: A valid Percentiles value object
    """
    runtime = draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    memory = draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    
    return Percentiles(runtime=runtime, memory=memory)


# ============================================================================
# Entity Strategies
# ============================================================================

@composite
def problem_strategy(draw) -> Problem:
    """
    Generate valid Problem entities.
    
    Generates problems with:
    - Non-empty ID (1-50 chars, alphanumeric and hyphens)
    - Valid platform (leetcode, hackerrank, codechef, codeforces)
    - Non-empty title (1-200 chars)
    - Valid difficulty (Easy, Medium, Hard)
    - Non-empty description (10-5000 chars)
    - Topics list (1-10 topics, each 1-50 chars)
    - Constraints string (0-1000 chars)
    - Examples list (1-5 examples)
    - Hints list (0-5 hints, each 1-200 chars)
    - Acceptance rate (0.0-100.0)
    
    Returns:
        Problem: A valid Problem entity
    """
    # Generate ID with alphanumeric and hyphens
    problem_id = draw(st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_')
    ))
    
    # Ensure ID is not empty after generation
    if not problem_id.strip():
        problem_id = "problem-1"
    
    platform = draw(st.sampled_from(["leetcode", "hackerrank", "codechef", "codeforces"]))
    
    title = draw(st.text(min_size=1, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'),
        blacklist_characters='\x00'
    )))
    
    # Ensure title is not empty
    if not title.strip():
        title = "Sample Problem"
    
    difficulty = draw(difficulty_strategy())
    
    description = draw(st.text(min_size=10, max_size=5000, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'),
        blacklist_characters='\x00'
    )))
    
    # Ensure description is not empty
    if not description.strip() or len(description.strip()) < 10:
        description = "This is a sample problem description with sufficient length."
    
    topics = draw(st.lists(
        st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters=' -'
        )),
        min_size=1,
        max_size=10
    ))
    
    # Ensure topics are not empty strings
    topics = [t.strip() if t.strip() else "Array" for t in topics]
    
    constraints = draw(st.text(min_size=0, max_size=1000, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'),
        blacklist_characters='\x00'
    )))
    
    examples = draw(st.lists(example_strategy(), min_size=1, max_size=5))
    
    hints = draw(st.lists(
        st.text(min_size=1, max_size=200, alphabet=st.characters(
            blacklist_categories=('Cs', 'Cc'),
            blacklist_characters='\x00'
        )),
        min_size=0,
        max_size=5
    ))
    
    # Filter out empty hints
    hints = [h for h in hints if h.strip()]
    
    acceptance_rate = draw(st.floats(
        min_value=0.0,
        max_value=100.0,
        allow_nan=False,
        allow_infinity=False
    ))
    
    return Problem(
        id=problem_id,
        platform=platform,
        title=title,
        difficulty=difficulty,
        description=description,
        topics=topics,
        constraints=constraints,
        examples=examples,
        hints=hints,
        acceptance_rate=acceptance_rate
    )


@composite
def submission_strategy(draw, status=None) -> Submission:
    """
    Generate valid Submission entities.
    
    Generates submissions with:
    - Non-empty ID (1-50 chars)
    - Non-empty problem_id (1-50 chars)
    - Valid language (Python3, Java, C++, JavaScript, etc.)
    - Non-empty code (10-5000 chars)
    - Valid status (ACCEPTED by default, or specified)
    - Runtime string (e.g., "52 ms")
    - Memory string (e.g., "15.2 MB")
    - Non-negative timestamp (Unix timestamp)
    - Optional percentiles (None or valid Percentiles)
    
    Args:
        status: Optional SubmissionStatus to use. If None, generates ACCEPTED status.
    
    Returns:
        Submission: A valid Submission entity
    """
    submission_id = draw(st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_')
    ))
    
    if not submission_id.strip():
        submission_id = "sub-1"
    
    problem_id = draw(st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_')
    ))
    
    if not problem_id.strip():
        problem_id = "problem-1"
    
    language = draw(st.sampled_from([
        "Python3",
        "Java",
        "C++",
        "JavaScript",
        "TypeScript",
        "Go",
        "Rust",
        "C",
        "C#",
        "Ruby",
        "Swift",
        "Kotlin"
    ]))
    
    code = draw(st.text(min_size=10, max_size=5000, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'),
        blacklist_characters='\x00'
    )))
    
    # Ensure code is not empty
    if not code.strip() or len(code.strip()) < 10:
        code = "def solution():\n    return True\n"
    
    # Use provided status or default to ACCEPTED
    if status is None:
        submission_status = SubmissionStatus.ACCEPTED
    else:
        submission_status = status
    
    # Generate runtime string
    runtime_value = draw(st.integers(min_value=1, max_value=10000))
    runtime = f"{runtime_value} ms"
    
    # Generate memory string
    memory_value = draw(st.floats(min_value=1.0, max_value=500.0, allow_nan=False, allow_infinity=False))
    memory = f"{memory_value:.1f} MB"
    
    # Generate non-negative timestamp (Unix timestamp)
    # Use reasonable range: 2020-01-01 to 2030-12-31
    timestamp = draw(st.integers(min_value=1577836800, max_value=1924905600))
    
    # Generate optional percentiles (50% chance of None)
    percentiles = draw(st.one_of(
        st.none(),
        percentiles_strategy()
    ))
    
    return Submission(
        id=submission_id,
        problem_id=problem_id,
        language=language,
        code=code,
        status=submission_status,
        runtime=runtime,
        memory=memory,
        timestamp=timestamp,
        percentiles=percentiles
    )


@composite
def accepted_submission_strategy(draw) -> Submission:
    """
    Generate valid Submission entities with ACCEPTED status.
    
    This is a convenience strategy for generating only accepted submissions,
    which is the most common case in testing.
    
    Returns:
        Submission: A valid Submission entity with ACCEPTED status
    """
    return draw(submission_strategy(status=SubmissionStatus.ACCEPTED))


@composite
def failed_submission_strategy(draw) -> Submission:
    """
    Generate valid Submission entities with non-ACCEPTED status.
    
    Generates submissions with status:
    - WRONG_ANSWER
    - TIME_LIMIT_EXCEEDED
    - MEMORY_LIMIT_EXCEEDED
    - RUNTIME_ERROR
    - COMPILE_ERROR
    
    Returns:
        Submission: A valid Submission entity with failed status
    """
    failed_status = draw(st.sampled_from([
        SubmissionStatus.WRONG_ANSWER,
        SubmissionStatus.TIME_LIMIT_EXCEEDED,
        SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
        SubmissionStatus.RUNTIME_ERROR,
        SubmissionStatus.COMPILE_ERROR
    ]))
    
    return draw(submission_strategy(status=failed_status))


# ============================================================================
# Specialized Strategies
# ============================================================================

@composite
def problem_with_platform_strategy(draw, platform: str) -> Problem:
    """
    Generate a Problem entity for a specific platform.
    
    Args:
        platform: The platform name (leetcode, hackerrank, codechef, codeforces)
    
    Returns:
        Problem: A valid Problem entity for the specified platform
    """
    problem = draw(problem_strategy())
    # Create a new Problem with the specified platform
    return Problem(
        id=problem.id,
        platform=platform,
        title=problem.title,
        difficulty=problem.difficulty,
        description=problem.description,
        topics=problem.topics,
        constraints=problem.constraints,
        examples=problem.examples,
        hints=problem.hints,
        acceptance_rate=problem.acceptance_rate
    )


@composite
def problem_with_difficulty_strategy(draw, difficulty_level: str) -> Problem:
    """
    Generate a Problem entity with a specific difficulty level.
    
    Args:
        difficulty_level: The difficulty level (Easy, Medium, Hard)
    
    Returns:
        Problem: A valid Problem entity with the specified difficulty
    """
    problem = draw(problem_strategy())
    # Create a new Problem with the specified difficulty
    return Problem(
        id=problem.id,
        platform=problem.platform,
        title=problem.title,
        difficulty=Difficulty(difficulty_level),
        description=problem.description,
        topics=problem.topics,
        constraints=problem.constraints,
        examples=problem.examples,
        hints=problem.hints,
        acceptance_rate=problem.acceptance_rate
    )


@composite
def submission_for_problem_strategy(draw, problem: Problem) -> Submission:
    """
    Generate a Submission entity for a specific Problem.
    
    Args:
        problem: The Problem entity to create a submission for
    
    Returns:
        Submission: A valid Submission entity for the specified problem
    """
    submission = draw(submission_strategy())
    # Create a new Submission with the problem's ID
    return Submission(
        id=submission.id,
        problem_id=problem.id,
        language=submission.language,
        code=submission.code,
        status=submission.status,
        runtime=submission.runtime,
        memory=submission.memory,
        timestamp=submission.timestamp,
        percentiles=submission.percentiles
    )


# ============================================================================
# List Strategies
# ============================================================================

def problems_list_strategy(min_size: int = 1, max_size: int = 10):
    """
    Generate a list of valid Problem entities.
    
    Args:
        min_size: Minimum number of problems (default: 1)
        max_size: Maximum number of problems (default: 10)
    
    Returns:
        Strategy that generates List[Problem]
    """
    return st.lists(problem_strategy(), min_size=min_size, max_size=max_size)


def submissions_list_strategy(min_size: int = 1, max_size: int = 10):
    """
    Generate a list of valid Submission entities.
    
    Args:
        min_size: Minimum number of submissions (default: 1)
        max_size: Maximum number of submissions (default: 10)
    
    Returns:
        Strategy that generates List[Submission]
    """
    return st.lists(submission_strategy(), min_size=min_size, max_size=max_size)


def examples_list_strategy(min_size: int = 1, max_size: int = 5):
    """
    Generate a list of valid Example value objects.
    
    Args:
        min_size: Minimum number of examples (default: 1)
        max_size: Maximum number of examples (default: 5)
    
    Returns:
        Strategy that generates List[Example]
    """
    return st.lists(example_strategy(), min_size=min_size, max_size=max_size)


# ============================================================================
# Export all strategies
# ============================================================================

__all__ = [
    # Value object strategies
    'example_strategy',
    'difficulty_strategy',
    'percentiles_strategy',
    
    # Entity strategies
    'problem_strategy',
    'submission_strategy',
    'accepted_submission_strategy',
    'failed_submission_strategy',
    
    # Specialized strategies
    'problem_with_platform_strategy',
    'problem_with_difficulty_strategy',
    'submission_for_problem_strategy',
    
    # List strategies
    'problems_list_strategy',
    'submissions_list_strategy',
    'examples_list_strategy',
]
