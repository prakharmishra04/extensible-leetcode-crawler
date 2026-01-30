# Adding a New Platform to the Coding Platform Crawler

## Overview

This guide provides step-by-step instructions for adding support for a new coding platform (e.g., HackerRank, CodeChef, Codeforces) to the crawler system. The architecture is designed to make this process straightforward through the use of interfaces and design patterns.

**Time Estimate**: 4-6 hours for a complete implementation

**Prerequisites**:
- Understanding of the platform's API (REST or GraphQL)
- API credentials or authentication method
- Python 3.8+ knowledge
- Familiarity with the project structure

## Architecture Overview

The system uses the **Strategy Pattern** to support multiple platforms. Each platform requires:

1. **PlatformClient**: Implements the `PlatformClient` interface
2. **Adapter**: Converts platform-specific API responses to domain models
3. **Factory Registration**: Adds the new platform to `PlatformClientFactory`

```
┌─────────────────────────────────────────────────────────────┐
│                  PlatformClient Interface                   │
│  (Abstract methods all platforms must implement)            │
└─────────────────────────────────────────────────────────────┘
                            ↑
                            │ implements
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────────────┐  ┌────────────────┐  ┌──────────────┐
│ LeetCodeClient│  │HackerRankClient│  │CodeChefClient│
│   + Adapter   │  │   + Adapter    │  │  + Adapter   │
└───────────────┘  └────────────────┘  └──────────────┘
```

## Step-by-Step Implementation Guide

### Step 1: Create Platform Directory Structure

Create a new directory for your platform under `src/crawler/infrastructure/platforms/`:

```bash
mkdir -p src/crawler/infrastructure/platforms/hackerrank
touch src/crawler/infrastructure/platforms/hackerrank/__init__.py
touch src/crawler/infrastructure/platforms/hackerrank/client.py
touch src/crawler/infrastructure/platforms/hackerrank/adapter.py
```


### Step 2: Implement the Adapter

The adapter converts platform-specific API responses to domain models. Start with the adapter as it defines how you'll parse the API data.

**File**: `src/crawler/infrastructure/platforms/hackerrank/adapter.py`

```python
"""HackerRank adapter for converting API responses to domain models."""

import json
from typing import Any, Dict, List

from crawler.domain.entities import Problem, Submission
from crawler.domain.entities.enums import SubmissionStatus
from crawler.domain.value_objects import Difficulty, Example, Percentiles


class HackerRankAdapter:
    """Adapts HackerRank API responses to domain models.
    
    This adapter handles the conversion of HackerRank-specific API response
    formats to our domain entities (Problem, Submission).
    
    Key responsibilities:
    - Parse API response structures
    - Map platform-specific difficulty levels to our Difficulty enum
    - Extract and format examples
    - Handle missing or optional fields gracefully
    """
    
    def adapt_problem(self, raw_data: Dict[str, Any]) -> Problem:
        """Convert HackerRank API response to Problem entity.
        
        Args:
            raw_data: Raw API response from HackerRank API
        
        Returns:
            Problem entity with all fields populated
        
        Example HackerRank API response structure:
        {
            "model": {
                "id": 123,
                "slug": "fizzbuzz",
                "name": "FizzBuzz",
                "difficulty": "easy",
                "body_html": "<p>Problem description...</p>",
                "tags": ["algorithms", "strings"],
                "success_ratio": 85.5
            }
        }
        """
        model = raw_data.get("model", raw_data)
        
        # Map HackerRank difficulty to our standard levels
        difficulty = self._map_difficulty(model.get("difficulty", "medium"))
        
        # Parse HTML description
        description = self._parse_html(model.get("body_html", ""))
        
        # Extract examples (platform-specific parsing)
        examples = self._parse_examples(model.get("sample_input", ""), 
                                       model.get("sample_output", ""))
        
        return Problem(
            id=model.get("slug", str(model.get("id"))),
            platform="hackerrank",
            title=model.get("name", "Unknown"),
            difficulty=difficulty,
            description=description,
            topics=model.get("tags", []),
            constraints=model.get("constraints", ""),
            examples=examples,
            hints=model.get("hints", []),
            acceptance_rate=float(model.get("success_ratio", 0.0))
        )

    
    def adapt_submission(self, raw_data: Dict[str, Any], problem_id: str = "unknown") -> Submission:
        """Convert HackerRank submission response to Submission entity.
        
        Args:
            raw_data: Raw API response from HackerRank submission API
            problem_id: The problem ID this submission belongs to
        
        Returns:
            Submission entity with all fields populated
        """
        # Map HackerRank status to our enum
        status = self._map_submission_status(raw_data.get("status", ""))
        
        # Parse percentiles if available
        percentiles = None
        if "runtime_percentile" in raw_data and "memory_percentile" in raw_data:
            percentiles = Percentiles(
                runtime=float(raw_data["runtime_percentile"]),
                memory=float(raw_data["memory_percentile"])
            )
        
        return Submission(
            id=str(raw_data.get("id", "unknown")),
            problem_id=problem_id,
            language=raw_data.get("language", "unknown"),
            code=raw_data.get("code", ""),
            status=status,
            runtime=raw_data.get("time", "N/A"),
            memory=raw_data.get("memory", "N/A"),
            timestamp=int(raw_data.get("created_at", 0)),
            percentiles=percentiles
        )
    
    def _map_difficulty(self, platform_difficulty: str) -> Difficulty:
        """Map platform-specific difficulty to standard Difficulty enum.
        
        HackerRank uses: easy, medium, hard, expert
        We map: easy->Easy, medium->Medium, hard/expert->Hard
        """
        difficulty_map = {
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard",
            "expert": "Hard",  # Map expert to Hard
        }
        
        standard_difficulty = difficulty_map.get(
            platform_difficulty.lower(), 
            "Medium"  # Default to Medium if unknown
        )
        
        return Difficulty(standard_difficulty)
    
    def _parse_html(self, html: str) -> str:
        """Extract plain text from HTML content."""
        from bs4 import BeautifulSoup
        import re
        
        if not html:
            return ""
        
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _parse_examples(self, sample_input: str, sample_output: str) -> List[Example]:
        """Parse example test cases from sample input/output."""
        if not sample_input or not sample_output:
            return []
        
        return [Example(
            input=sample_input.strip(),
            output=sample_output.strip(),
            explanation=None
        )]
    
    def _map_submission_status(self, status: str) -> SubmissionStatus:
        """Map platform status to SubmissionStatus enum."""
        status_map = {
            "accepted": SubmissionStatus.ACCEPTED,
            "wrong answer": SubmissionStatus.WRONG_ANSWER,
            "time limit exceeded": SubmissionStatus.TIME_LIMIT_EXCEEDED,
            "runtime error": SubmissionStatus.RUNTIME_ERROR,
            "compilation error": SubmissionStatus.COMPILE_ERROR,
        }
        
        return status_map.get(
            status.lower(), 
            SubmissionStatus.RUNTIME_ERROR
        )
```

**Key Points**:
- Implement `adapt_problem()` and `adapt_submission()` methods
- Handle platform-specific field names and structures
- Map platform difficulty levels to standard Easy/Medium/Hard
- Parse HTML content if the platform returns HTML descriptions
- Provide sensible defaults for missing fields


### Step 3: Implement the PlatformClient

The client implements the `PlatformClient` interface and handles all API communication.

**File**: `src/crawler/infrastructure/platforms/hackerrank/client.py`

```python
"""HackerRank platform client implementation."""

from logging import Logger
from typing import Dict, List

from crawler.application.interfaces import PlatformClient
from crawler.config.settings import Config
from crawler.domain.entities import Problem, Submission
from crawler.domain.exceptions import (
    AuthenticationException,
    ProblemNotFoundException,
    NetworkException,
)
from crawler.infrastructure.http import HTTPClient

from .adapter import HackerRankAdapter


class HackerRankClient(PlatformClient):
    """HackerRank-specific API client.
    
    This client implements the PlatformClient interface for HackerRank,
    handling REST API communication and authentication.
    
    Attributes:
        http_client: HTTP client with retry and rate limiting
        adapter: Adapter for converting API responses
        config: Configuration settings
        logger: Logger for tracking operations
        api_key: Optional API key for authentication
    """
    
    def __init__(
        self,
        http_client: HTTPClient,
        adapter: HackerRankAdapter,
        config: Config,
        logger: Logger
    ):
        """Initialize the HackerRank client.
        
        Args:
            http_client: HTTP client for making requests
            adapter: Adapter for converting API responses
            config: Configuration settings
            logger: Logger for tracking operations
        """
        self.http_client = http_client
        self.adapter = adapter
        self.config = config
        self.logger = logger
        self.api_key = config.hackerrank_api_key  # Add to Config class
    
    def fetch_problem(self, problem_id: str) -> Problem:
        """Fetch a single problem from HackerRank.
        
        Args:
            problem_id: The problem's slug (e.g., "fizzbuzz")
        
        Returns:
            Problem entity with all metadata
        
        Raises:
            ProblemNotFoundException: If the problem doesn't exist
            NetworkException: If the network request fails
        """
        self.logger.info(f"Fetching problem: {problem_id}")
        
        try:
            # Example API endpoint (adjust based on actual HackerRank API)
            url = f"{self.config.hackerrank_api_url}/challenges/{problem_id}"
            
            response = self.http_client.get(
                url=url,
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Check for errors
            if response.status_code == 404:
                raise ProblemNotFoundException(problem_id, "hackerrank")
            
            # Adapt response to domain model
            problem = self.adapter.adapt_problem(data)
            
            self.logger.info(f"Successfully fetched problem: {problem.title}")
            return problem
            
        except ProblemNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to fetch problem {problem_id}: {e}")
            raise NetworkException(f"Failed to fetch problem: {e}")

    
    def fetch_solved_problems(self, username: str) -> List[Problem]:
        """Fetch all problems solved by a user.
        
        Args:
            username: The HackerRank username
        
        Returns:
            List of Problem entities for all solved problems
        """
        self.logger.info(f"Fetching solved problems for user: {username}")
        
        try:
            url = f"{self.config.hackerrank_api_url}/users/{username}/submissions"
            
            response = self.http_client.get(
                url=url,
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Get unique problem IDs from submissions
            problem_ids = set()
            for submission in data.get("models", []):
                if submission.get("status") == "accepted":
                    problem_ids.add(submission.get("challenge_slug"))
            
            # Fetch full details for each problem
            problems = []
            for problem_id in problem_ids:
                try:
                    problem = self.fetch_problem(problem_id)
                    problems.append(problem)
                except Exception as e:
                    self.logger.warning(f"Failed to fetch problem {problem_id}: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(problems)} solved problems")
            return problems
            
        except Exception as e:
            self.logger.error(f"Failed to fetch solved problems for {username}: {e}")
            raise NetworkException(f"Failed to fetch solved problems: {e}")
    
    def fetch_submission(self, problem_id: str, username: str) -> Submission:
        """Fetch the last accepted submission for a problem.
        
        Args:
            problem_id: The problem's slug
            username: The HackerRank username
        
        Returns:
            Submission entity with code and metadata
        """
        self.logger.info(f"Fetching submission for problem: {problem_id}, user: {username}")
        
        try:
            url = f"{self.config.hackerrank_api_url}/users/{username}/submissions"
            params = {"challenge_slug": problem_id, "status": "accepted", "limit": 1}
            
            response = self.http_client.get(
                url=url,
                params=params,
                headers=self._get_headers()
            )
            
            data = response.json()
            submissions = data.get("models", [])
            
            if not submissions:
                raise Exception(f"No accepted submission found for {problem_id}")
            
            # Get the most recent submission
            submission_data = submissions[0]
            submission = self.adapter.adapt_submission(submission_data, problem_id)
            
            self.logger.info(f"Successfully fetched submission")
            return submission
            
        except Exception as e:
            self.logger.error(f"Failed to fetch submission for {problem_id}: {e}")
            raise NetworkException(f"Failed to fetch submission: {e}")
    
    def fetch_community_solutions(self, problem_id: str, limit: int = 10) -> List[Submission]:
        """Fetch top community solutions for a problem.
        
        Args:
            problem_id: The problem's slug
            limit: Maximum number of solutions to fetch
        
        Returns:
            List of Submission entities representing community solutions
        """
        self.logger.info(f"Fetching community solutions for problem: {problem_id}")
        
        # Note: This depends on whether HackerRank provides a public API
        # for community solutions. Adjust based on actual API availability.
        
        self.logger.warning("Community solutions not yet implemented for HackerRank")
        return []
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with HackerRank using API key.
        
        Args:
            credentials: Dictionary containing "api_key"
        
        Returns:
            True if authentication succeeded
        
        Raises:
            AuthenticationException: If authentication fails
        """
        self.logger.info("Authenticating with HackerRank")
        
        api_key = credentials.get("api_key")
        
        if not api_key:
            raise AuthenticationException(
                "hackerrank",
                "api_key is required for authentication"
            )
        
        # Store the API key
        self.api_key = api_key
        
        # Verify authentication by making a test request
        try:
            url = f"{self.config.hackerrank_api_url}/user"
            response = self.http_client.get(
                url=url,
                headers=self._get_headers()
            )
            
            if response.status_code == 401:
                raise AuthenticationException("hackerrank", "Invalid API key")
            
            self.logger.info("Successfully authenticated with HackerRank")
            return True
            
        except AuthenticationException:
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise AuthenticationException("hackerrank", str(e))
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for HackerRank API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; CodingPlatformCrawler/2.0)"
        }
        
        # Add API key if available
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
```

**Key Points**:
- Implement all five abstract methods from `PlatformClient`
- Use `self.http_client` for all network requests (includes retry logic)
- Use `self.adapter` to convert API responses to domain models
- Handle platform-specific authentication (API key, OAuth, session token, etc.)
- Log all operations for debugging
- Raise appropriate exceptions (ProblemNotFoundException, NetworkException, etc.)


### Step 4: Register Platform in Factory

Add your new platform to the `PlatformClientFactory` so it can be instantiated at runtime.

**File**: `src/crawler/infrastructure/platforms/factory.py`

```python
# Add import at the top
from .hackerrank.adapter import HackerRankAdapter
from .hackerrank.client import HackerRankClient

# In the create() method, add a new elif branch:
def create(self, platform: str) -> PlatformClient:
    """Create a platform client based on platform identifier."""
    platform = platform.lower()
    
    if platform == "leetcode":
        self.logger.info(f"Creating LeetCode client")
        adapter = LeetCodeAdapter()
        return LeetCodeClient(
            self.http_client,
            adapter,
            self.config,
            self.logger
        )
    
    elif platform == "hackerrank":  # ADD THIS BLOCK
        self.logger.info(f"Creating HackerRank client")
        adapter = HackerRankAdapter()
        return HackerRankClient(
            self.http_client,
            adapter,
            self.config,
            self.logger
        )
    
    else:
        self.logger.error(f"Unsupported platform requested: {platform}")
        raise UnsupportedPlatformException(platform)
```

### Step 5: Update Configuration

Add platform-specific configuration to the `Config` class.

**File**: `src/crawler/config/settings.py`

```python
class Config:
    """Configuration settings for the crawler."""
    
    def __init__(self):
        # ... existing config ...
        
        # HackerRank configuration
        self.hackerrank_api_url = os.getenv(
            "HACKERRANK_API_URL",
            "https://www.hackerrank.com/rest"
        )
        self.hackerrank_api_key = os.getenv("HACKERRANK_API_KEY", None)
```

### Step 6: Create Unit Tests

Write comprehensive unit tests for your adapter and client.

**File**: `tests/unit/infrastructure/platforms/test_hackerrank_adapter.py`

```python
"""Unit tests for HackerRank adapter."""

import pytest

from crawler.domain.entities import Problem, Submission
from crawler.domain.value_objects import Difficulty
from crawler.infrastructure.platforms.hackerrank.adapter import HackerRankAdapter


class TestHackerRankAdapter:
    """Test suite for HackerRankAdapter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = HackerRankAdapter()
    
    def test_adapt_problem_with_valid_data(self):
        """Test adapting a valid problem response."""
        raw_data = {
            "model": {
                "id": 123,
                "slug": "fizzbuzz",
                "name": "FizzBuzz",
                "difficulty": "easy",
                "body_html": "<p>Write a program that prints FizzBuzz</p>",
                "tags": ["algorithms", "strings"],
                "success_ratio": 85.5,
                "sample_input": "1 2 3",
                "sample_output": "1 2 Fizz"
            }
        }
        
        problem = self.adapter.adapt_problem(raw_data)
        
        assert problem.id == "fizzbuzz"
        assert problem.platform == "hackerrank"
        assert problem.title == "FizzBuzz"
        assert problem.difficulty == Difficulty("Easy")
        assert "FizzBuzz" in problem.description
        assert "algorithms" in problem.topics
        assert problem.acceptance_rate == 85.5
        assert len(problem.examples) == 1
    
    def test_adapt_problem_with_missing_optional_fields(self):
        """Test adapting a problem with missing optional fields."""
        raw_data = {
            "model": {
                "id": 456,
                "slug": "test-problem",
                "name": "Test Problem",
                "difficulty": "medium"
            }
        }
        
        problem = self.adapter.adapt_problem(raw_data)
        
        assert problem.id == "test-problem"
        assert problem.title == "Test Problem"
        assert problem.difficulty == Difficulty("Medium")
        assert problem.description == ""
        assert problem.topics == []
        assert problem.acceptance_rate == 0.0
    
    def test_map_difficulty_levels(self):
        """Test difficulty mapping."""
        assert self.adapter._map_difficulty("easy") == Difficulty("Easy")
        assert self.adapter._map_difficulty("medium") == Difficulty("Medium")
        assert self.adapter._map_difficulty("hard") == Difficulty("Hard")
        assert self.adapter._map_difficulty("expert") == Difficulty("Hard")
        assert self.adapter._map_difficulty("unknown") == Difficulty("Medium")
```


**File**: `tests/unit/infrastructure/platforms/test_hackerrank_client.py`

```python
"""Unit tests for HackerRank client."""

import pytest
from unittest.mock import Mock, MagicMock

from crawler.domain.exceptions import ProblemNotFoundException, NetworkException
from crawler.infrastructure.platforms.hackerrank.client import HackerRankClient
from crawler.infrastructure.platforms.hackerrank.adapter import HackerRankAdapter


class TestHackerRankClient:
    """Test suite for HackerRankClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.http_client = Mock()
        self.adapter = HackerRankAdapter()
        self.config = Mock()
        self.config.hackerrank_api_url = "https://api.hackerrank.com"
        self.config.hackerrank_api_key = "test_key"
        self.logger = Mock()
        
        self.client = HackerRankClient(
            self.http_client,
            self.adapter,
            self.config,
            self.logger
        )
    
    def test_fetch_problem_success(self):
        """Test successful problem fetching."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": {
                "id": 123,
                "slug": "fizzbuzz",
                "name": "FizzBuzz",
                "difficulty": "easy",
                "body_html": "<p>Test</p>",
                "tags": ["algorithms"],
                "success_ratio": 85.5
            }
        }
        self.http_client.get.return_value = mock_response
        
        # Execute
        problem = self.client.fetch_problem("fizzbuzz")
        
        # Assert
        assert problem.id == "fizzbuzz"
        assert problem.title == "FizzBuzz"
        assert problem.platform == "hackerrank"
        self.http_client.get.assert_called_once()
    
    def test_fetch_problem_not_found(self):
        """Test fetching non-existent problem."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        self.http_client.get.return_value = mock_response
        
        # Execute and assert
        with pytest.raises(ProblemNotFoundException):
            self.client.fetch_problem("nonexistent")
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        # Mock successful auth response
        mock_response = Mock()
        mock_response.status_code = 200
        self.http_client.get.return_value = mock_response
        
        # Execute
        result = self.client.authenticate({"api_key": "valid_key"})
        
        # Assert
        assert result is True
        assert self.client.api_key == "valid_key"
```

### Step 7: Create Integration Tests

Write integration tests that test the client with mocked HTTP responses.

**File**: `tests/integration/platforms/test_hackerrank_integration.py`

```python
"""Integration tests for HackerRank client."""

import pytest
from unittest.mock import Mock

from crawler.infrastructure.platforms.hackerrank.client import HackerRankClient
from crawler.infrastructure.platforms.hackerrank.adapter import HackerRankAdapter
from crawler.infrastructure.http import HTTPClient, RateLimiter, RetryConfig
from crawler.config.settings import Config
from crawler.config.logging_config import get_logger


class TestHackerRankIntegration:
    """Integration tests for HackerRank platform."""
    
    def setup_method(self):
        """Set up test fixtures."""
        retry_config = RetryConfig(max_retries=1, initial_delay=0.01)
        rate_limiter = RateLimiter(10.0)
        logger = get_logger(__name__)
        
        # Use real HTTP client but we'll mock the session
        self.http_client = HTTPClient(retry_config, rate_limiter, logger)
        self.adapter = HackerRankAdapter()
        self.config = Config()
        
        self.client = HackerRankClient(
            self.http_client,
            self.adapter,
            self.config,
            logger
        )
    
    def test_full_problem_fetch_workflow(self):
        """Test complete workflow of fetching a problem."""
        # Mock the HTTP session
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": {
                "id": 123,
                "slug": "fizzbuzz",
                "name": "FizzBuzz",
                "difficulty": "easy",
                "body_html": "<p>Test problem</p>",
                "tags": ["algorithms"],
                "success_ratio": 85.5
            }
        }
        mock_session.request.return_value = mock_response
        self.http_client.session = mock_session
        
        # Execute
        problem = self.client.fetch_problem("fizzbuzz")
        
        # Assert
        assert problem.id == "fizzbuzz"
        assert problem.platform == "hackerrank"
        assert problem.title == "FizzBuzz"
        assert len(problem.topics) > 0
```


### Step 8: Update Documentation

Update the main README and other documentation to mention the new platform.

**File**: `README.md`

Add to the supported platforms section:
```markdown
## Supported Platforms

- ✅ **LeetCode** - Fully implemented
- ✅ **HackerRank** - Fully implemented
- 🚧 **CodeChef** - Coming soon
- 🚧 **Codeforces** - Coming soon
```

Add usage examples:
```markdown
### HackerRank Examples

```bash
# Download a single problem
python leetcode_crawler.py download --platform hackerrank --problem fizzbuzz

# Batch download all solved problems
python batch_download_solutions.py --platform hackerrank --username your_username

# List solved problems
python fetch_solved_problems.py --platform hackerrank --username your_username
```
```

## Testing Your Implementation

### Run Unit Tests

```bash
# Test adapter
pytest tests/unit/infrastructure/platforms/test_hackerrank_adapter.py -v

# Test client
pytest tests/unit/infrastructure/platforms/test_hackerrank_client.py -v
```

### Run Integration Tests

```bash
pytest tests/integration/platforms/test_hackerrank_integration.py -v
```

### Run All Tests

```bash
pytest tests/ -v --cov=src/crawler/infrastructure/platforms/hackerrank
```

### Manual Testing

```python
# Create a test script: test_hackerrank.py
from crawler.infrastructure.http import HTTPClient, RateLimiter, RetryConfig
from crawler.infrastructure.platforms.factory import PlatformClientFactory
from crawler.config.settings import Config
from crawler.config.logging_config import get_logger

# Set up dependencies
retry_config = RetryConfig()
rate_limiter = RateLimiter(2.0)
logger = get_logger(__name__)
http_client = HTTPClient(retry_config, rate_limiter, logger)
config = Config()

# Create factory and client
factory = PlatformClientFactory(http_client, config, logger)
client = factory.create("hackerrank")

# Test fetching a problem
try:
    problem = client.fetch_problem("fizzbuzz")
    print(f"✅ Successfully fetched: {problem.title}")
    print(f"   Difficulty: {problem.difficulty.level}")
    print(f"   Topics: {', '.join(problem.topics)}")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run the test:
```bash
python test_hackerrank.py
```

## Common Pitfalls and Solutions

### 1. API Rate Limiting

**Problem**: Platform returns 429 Too Many Requests

**Solution**: The `HTTPClient` already includes rate limiting via `RateLimiter`. Adjust the rate:

```python
# In factory.py or your initialization code
rate_limiter = RateLimiter(1.0)  # 1 request per second
```

### 2. Authentication Issues

**Problem**: 401 Unauthorized errors

**Solution**: 
- Verify API credentials are correct
- Check if credentials are properly loaded from environment variables
- Ensure headers are correctly formatted
- Some platforms require specific header names (e.g., `X-API-Key` vs `Authorization`)

### 3. HTML Parsing

**Problem**: Description contains HTML tags or is poorly formatted

**Solution**: Use BeautifulSoup for robust HTML parsing:

```python
from bs4 import BeautifulSoup
import re

def _parse_html(self, html: str) -> str:
    if not html:
        return ""
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

### 4. Missing Fields

**Problem**: API response doesn't include all expected fields

**Solution**: Always provide defaults and use `.get()` with fallbacks:

```python
# ❌ Bad - will crash if field is missing
title = raw_data["title"]

# ✅ Good - provides default
title = raw_data.get("title", "Unknown")
```

### 5. Different Difficulty Levels

**Problem**: Platform uses different difficulty terminology

**Solution**: Create a mapping function:

```python
def _map_difficulty(self, platform_difficulty: str) -> Difficulty:
    """Map platform-specific difficulty to standard levels."""
    # Platform uses: beginner, intermediate, advanced, expert
    difficulty_map = {
        "beginner": "Easy",
        "intermediate": "Medium",
        "advanced": "Hard",
        "expert": "Hard",
    }
    
    standard = difficulty_map.get(platform_difficulty.lower(), "Medium")
    return Difficulty(standard)
```


## Platform-Specific Considerations

### REST API vs GraphQL

**LeetCode** uses GraphQL:
```python
query = """
query getProblem($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        title
        difficulty
    }
}
"""
response = http_client.post(url, json={"query": query, "variables": variables})
```

**HackerRank** uses REST:
```python
response = http_client.get(f"{base_url}/challenges/{problem_id}")
```

### Authentication Methods

Different platforms use different authentication:

| Platform | Method | Header Format |
|----------|--------|---------------|
| LeetCode | Session Cookie | `Cookie: LEETCODE_SESSION=...` |
| HackerRank | API Key | `Authorization: Bearer <api_key>` |
| CodeChef | OAuth 2.0 | `Authorization: Bearer <access_token>` |
| Codeforces | API Key + Secret | Custom signature in URL params |

### Pagination

Some platforms paginate results:

```python
def fetch_solved_problems(self, username: str) -> List[Problem]:
    """Fetch all solved problems with pagination."""
    all_problems = []
    page = 1
    has_more = True
    
    while has_more:
        response = self.http_client.get(
            url=f"{self.config.api_url}/users/{username}/submissions",
            params={"page": page, "limit": 100}
        )
        
        data = response.json()
        problems = data.get("problems", [])
        
        all_problems.extend(problems)
        
        # Check if there are more pages
        has_more = len(problems) == 100
        page += 1
    
    return all_problems
```

## Checklist for New Platform

Use this checklist to ensure you've completed all necessary steps:

- [ ] **Step 1**: Created platform directory structure
  - [ ] `__init__.py`
  - [ ] `client.py`
  - [ ] `adapter.py`

- [ ] **Step 2**: Implemented Adapter
  - [ ] `adapt_problem()` method
  - [ ] `adapt_submission()` method
  - [ ] Difficulty mapping
  - [ ] HTML parsing (if needed)
  - [ ] Example parsing

- [ ] **Step 3**: Implemented PlatformClient
  - [ ] `fetch_problem()` method
  - [ ] `fetch_solved_problems()` method
  - [ ] `fetch_submission()` method
  - [ ] `fetch_community_solutions()` method
  - [ ] `authenticate()` method
  - [ ] `_get_headers()` helper method

- [ ] **Step 4**: Registered in Factory
  - [ ] Added import statements
  - [ ] Added elif branch in `create()` method

- [ ] **Step 5**: Updated Configuration
  - [ ] Added API URL to Config
  - [ ] Added authentication credentials to Config
  - [ ] Added environment variable support

- [ ] **Step 6**: Created Unit Tests
  - [ ] Adapter tests (valid data, missing fields, edge cases)
  - [ ] Client tests (success cases, error cases, authentication)
  - [ ] Achieved >80% code coverage

- [ ] **Step 7**: Created Integration Tests
  - [ ] Full workflow tests with mocked HTTP
  - [ ] Error handling tests
  - [ ] Authentication flow tests

- [ ] **Step 8**: Updated Documentation
  - [ ] Added platform to README
  - [ ] Added usage examples
  - [ ] Updated supported platforms list

- [ ] **Testing**
  - [ ] All unit tests pass
  - [ ] All integration tests pass
  - [ ] Manual testing completed
  - [ ] Code coverage >80%

- [ ] **Code Quality**
  - [ ] Type hints on all methods
  - [ ] Docstrings on all classes and methods
  - [ ] Logging statements for debugging
  - [ ] Error handling with appropriate exceptions

## Example: Complete Minimal Implementation

Here's a minimal but complete implementation for reference:

```python
# adapter.py
from typing import Any, Dict
from crawler.domain.entities import Problem
from crawler.domain.value_objects import Difficulty

class MinimalAdapter:
    def adapt_problem(self, raw_data: Dict[str, Any]) -> Problem:
        return Problem(
            id=raw_data.get("id", "unknown"),
            platform="minimal",
            title=raw_data.get("title", "Unknown"),
            difficulty=Difficulty(raw_data.get("difficulty", "Medium")),
            description=raw_data.get("description", ""),
            topics=raw_data.get("topics", []),
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=0.0
        )

# client.py
from typing import Dict, List
from crawler.application.interfaces import PlatformClient
from crawler.domain.entities import Problem, Submission

class MinimalClient(PlatformClient):
    def __init__(self, http_client, adapter, config, logger):
        self.http_client = http_client
        self.adapter = adapter
        self.config = config
        self.logger = logger
    
    def fetch_problem(self, problem_id: str) -> Problem:
        response = self.http_client.get(f"{self.config.api_url}/problems/{problem_id}")
        return self.adapter.adapt_problem(response.json())
    
    def fetch_solved_problems(self, username: str) -> List[Problem]:
        return []  # Implement based on API
    
    def fetch_submission(self, problem_id: str, username: str) -> Submission:
        raise NotImplementedError("Submissions not supported")
    
    def fetch_community_solutions(self, problem_id: str, limit: int = 10) -> List[Submission]:
        return []  # Optional feature
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        return True  # Implement if authentication required
```

## Getting Help

If you encounter issues while implementing a new platform:

1. **Check existing implementations**: Look at `LeetCodeClient` and `LeetCodeAdapter` for reference
2. **Review the interface**: Ensure you're implementing all required methods from `PlatformClient`
3. **Test incrementally**: Test each method as you implement it
4. **Check logs**: Use the logger to debug API responses and errors
5. **Consult API documentation**: Refer to the platform's official API documentation

## Next Steps

After successfully implementing a new platform:

1. **Submit a Pull Request**: Share your implementation with the community
2. **Add Examples**: Create example scripts showing how to use the new platform
3. **Update Tests**: Ensure comprehensive test coverage
4. **Document Edge Cases**: Note any platform-specific quirks or limitations
5. **Monitor Issues**: Help users who encounter problems with the new platform

## Conclusion

Adding a new platform to the crawler is straightforward thanks to the extensible architecture. The key steps are:

1. Implement the Adapter (converts API responses to domain models)
2. Implement the PlatformClient (handles API communication)
3. Register in the Factory (enables runtime platform selection)
4. Add Configuration (API URLs and credentials)
5. Write Tests (ensure correctness and maintainability)
6. Update Documentation (help users discover and use the new platform)

By following this guide, you can add support for any coding platform in approximately 4-6 hours. The architecture ensures that your implementation integrates seamlessly with the existing system without requiring changes to core functionality.

Happy coding! 🚀
