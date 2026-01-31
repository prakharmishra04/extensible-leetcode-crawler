# Architecture & Technical Design

## Overview

A well-architected system for crawling coding platforms following clean architecture principles, SOLID design patterns, and comprehensive testing strategies.

## Core Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                               │
│  Commands: download, batch, list                            │
│  Progress tracking and user interaction                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                          │
│  Use Cases: FetchProblem, BatchDownload, ListProblems      │
│  Business logic orchestration                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│  Entities: Problem, Submission, User                        │
│  Value Objects: Difficulty, Example, Constraint            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  Platform clients, HTTP, file system, formatters           │
└─────────────────────────────────────────────────────────────┘
```

## Domain Model

### Entities

```python
@dataclass
class Problem:
    id: str  # "two-sum"
    platform: str  # "leetcode"
    title: str  # "Two Sum"
    difficulty: Difficulty  # Value object
    description: str  # Full problem description
    topics: List[str]  # ["Array", "Hash Table"]
    constraints: List[Constraint]  # Structured constraints
    examples: List[Example]  # Structured examples
    hints: List[str]
    acceptance_rate: float


@dataclass
class Submission:
    id: str
    problem_id: str
    language: str  # "python3"
    code: str  # Actual solution code
    status: SubmissionStatus
    runtime: str  # "52 ms"
    memory: str  # "15.2 MB"
    timestamp: int
    percentiles: Optional[Percentiles]
```

### Value Objects (Immutable)

```python
@dataclass(frozen=True)
class Difficulty:
    level: str  # Easy, Medium, Hard


@dataclass(frozen=True)
class Example:
    input: str
    output: str
    explanation: Optional[str]


@dataclass(frozen=True)
class Constraint:
    text: str


@dataclass(frozen=True)
class Percentiles:
    runtime: float
    memory: float
```

## Data Flow: API to Files

### Complete Flow

```
User Request
    ↓
CLI Command (download.py)
    ↓
FetchProblemUseCase
    ↓
PlatformClient.fetch_problem()
    ↓
HTTPClient → LeetCode GraphQL API
    ↓
Raw JSON Response
    ↓
LeetCodeAdapter.adapt_problem()
    ├─→ Parse HTML description
    ├─→ Extract examples
    └─→ Parse constraints
    ↓
Problem Entity (domain model)
    ↓
PlatformClient.fetch_submission()
    ↓
Submission Entity
    ↓
OutputFormatter.format_problem()
    ↓
Repository.save()
    ↓
FileSystem: problems/leetcode/{problem-id}/solution.py
```

### Enhanced Problem Parsing

**Constraint Parsing**:

```
Input: "1 <= nums.length <= 10^4\n-10^4 <= nums[i] <= 10^4"
Process: Split by numeric patterns, remove bullets
Output: [Constraint("1 <= nums.length <= 10^4"),
         Constraint("-10^4 <= nums[i] <= 10^4")]
```

**Example Parsing**:

```
Input: "Example 1:\nInput: nums = [2,7], target = 9\nOutput: [0,1]"
Process: Extract Input/Output/Explanation fields
Output: Example(input="nums = [2,7], target = 9",
               output="[0,1]",
               explanation="...")
```

## Design Patterns

- **Strategy Pattern**: PlatformClient, OutputFormatter - swap implementations
- **Repository Pattern**: ProblemRepository - abstract storage
- **Adapter Pattern**: LeetCodeAdapter - convert API responses to domain models
- **Observer Pattern**: DownloadObserver - progress tracking
- **Factory Pattern**: PlatformClientFactory - create platform clients
- **Command Pattern**: CLI commands - encapsulate operations
- **Dependency Injection**: Constructor injection throughout

## Key Interfaces

### PlatformClient (Strategy Pattern)

```python
class PlatformClient(ABC):
    @abstractmethod
    def fetch_problem(self, problem_id: str) -> Problem

    @abstractmethod
    def fetch_solved_problems(self, username: str) -> List[Problem]

    @abstractmethod
    def fetch_submission(self, problem_id: str, username: str) -> Submission

    @abstractmethod
    def fetch_community_solutions(self, problem_id: str, limit: int) -> List[Submission]

    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool
```

### ProblemRepository (Repository Pattern)

```python
class ProblemRepository(ABC):
    @abstractmethod
    def save(self, problem: Problem, submission: Optional[Submission]) -> None

    @abstractmethod
    def find_by_id(self, problem_id: str, platform: str) -> Optional[Problem]

    @abstractmethod
    def exists(self, problem_id: str, platform: str) -> bool

    @abstractmethod
    def list_all(self, platform: Optional[str]) -> List[Problem]
```

### OutputFormatter (Strategy Pattern)

```python
class OutputFormatter(ABC):
    @abstractmethod
    def format_problem(self, problem: Problem, submission: Optional[Submission]) -> str

    @abstractmethod
    def get_file_extension(self) -> str
```

## Project Structure

```
src/crawler/
├── domain/
│   ├── entities/          # Problem, Submission, User
│   ├── value_objects/     # Difficulty, Example, Constraint, Percentiles
│   └── exceptions.py      # Domain exceptions
├── application/
│   ├── interfaces/        # PlatformClient, Repository, Formatter, Observer
│   └── use_cases/         # FetchProblem, BatchDownload, ListProblems
├── infrastructure/
│   ├── platforms/
│   │   └── leetcode/      # LeetCodeClient, LeetCodeAdapter
│   ├── repositories/      # FileSystemRepository
│   ├── formatters/        # Python, JSON, Markdown formatters
│   └── http/              # HTTPClient, RateLimiter, RetryConfig
├── cli/
│   ├── commands/          # Download, Batch, List commands
│   ├── observers/         # ConsoleProgress, LoggingObserver
│   └── main.py            # CLI entry point
└── config/
    ├── settings.py        # Configuration management
    └── logging_config.py  # Structured logging
```

## Error Handling

- **Domain Layer**: Fail-fast validation (ValueError for invalid data)
- **Application Layer**: Fail-safe parsing (return empty lists on errors)
- **Infrastructure Layer**: Retry with exponential backoff (network errors)
- **CLI Layer**: User-friendly messages with actionable suggestions

## Configuration

**Precedence**: CLI args > Environment vars > Config file > Defaults

**Sources**:

- YAML/JSON config files
- Environment variables (CRAWLER\_ prefix)
- CLI arguments

## Testing Strategy

- **Unit Tests (80%)**: Domain entities, value objects, use cases
- **Integration Tests (15%)**: Platform clients with mocked HTTP
- **E2E Tests (5%)**: Full CLI workflows
- **Property-Based Tests**: Universal correctness properties (hypothesis)

**Coverage Goals**: Overall >80%, Domain >95%, Application >85%

## Performance

- **API Response**: \<5s (p95)
- **Batch Download**: 100 problems in \<5 minutes
- **Memory Usage**: \<100MB
- **Startup Time**: \<1s

## Extensibility: Adding New Platforms

### Step 1: Create Platform Directory

```bash
mkdir -p src/crawler/infrastructure/platforms/hackerrank
touch src/crawler/infrastructure/platforms/hackerrank/__init__.py
touch src/crawler/infrastructure/platforms/hackerrank/client.py
touch src/crawler/infrastructure/platforms/hackerrank/adapter.py
```

### Step 2: Implement Adapter

```python
class HackerRankAdapter:
    def adapt_problem(self, raw_data: Dict[str, Any]) -> Problem:
        # Convert HackerRank API response to Problem entity
        return Problem(
            id=raw_data["slug"],
            platform="hackerrank",
            title=raw_data["name"],
            difficulty=self._map_difficulty(raw_data["difficulty"]),
            # ... map all fields
        )

    def adapt_submission(self, raw_data: Dict[str, Any]) -> Submission:
        # Convert HackerRank submission to Submission entity
        return Submission(...)
```

### Step 3: Implement PlatformClient

```python
class HackerRankClient(PlatformClient):
    def fetch_problem(self, problem_id: str) -> Problem:
        response = self.http_client.get(f"{self.api_url}/challenges/{problem_id}")
        return self.adapter.adapt_problem(response.json())

    def fetch_submission(self, problem_id: str, username: str) -> Submission:
        # Fetch user's submission
        pass

    # Implement other abstract methods...
```

### Step 4: Register in Factory

```python
# In PlatformClientFactory.create()
elif platform == "hackerrank":
    adapter = HackerRankAdapter()
    return HackerRankClient(self.http_client, adapter, self.config, self.logger)
```

### Step 5: Add Configuration

```python
# In Config class
self.hackerrank_api_url = os.getenv("CRAWLER_HACKERRANK_API_URL", "...")
self.hackerrank_api_key = os.getenv("CRAWLER_HACKERRANK_API_KEY", None)
```

### Step 6: Write Tests

```python
class TestHackerRankAdapter:
    def test_adapt_problem_with_valid_data(self):
        raw_data = {...}
        problem = self.adapter.adapt_problem(raw_data)
        assert problem.id == "fizzbuzz"
        assert problem.platform == "hackerrank"
```

## Key Features

✅ Multi-platform support (extensible architecture)
✅ Smart update modes (skip/update/force)
✅ Structured constraint parsing
✅ Enhanced example extraction
✅ Multiple output formats (Python, JSON, Markdown)
✅ Retry logic with exponential backoff
✅ Rate limiting (token bucket)
✅ Progress tracking (observer pattern)
✅ Comprehensive error handling
✅ 73% test coverage

## Status

**Current**: v2.0 - LeetCode fully implemented with extensible architecture
**Future**: HackerRank, CodeChef, Codeforces (via PlatformClient interface)
**Coverage**: 73% overall, 100% domain layer
