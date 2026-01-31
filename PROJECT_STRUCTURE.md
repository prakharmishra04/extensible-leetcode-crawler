# Project Structure Overview

This document provides a high-level overview of the entire project structure, including both v1 and v2.

## Project Versions

### v2 (Main) - Clean Architecture

The primary version with extensible architecture, comprehensive testing, and production-ready code.

**Location**: Root directory (`src/`, `tests/`)

**Key Features**:

- Clean architecture with layered design
- 73% test coverage
- Multiple output formats (Python, JSON, Markdown)
- Extensible to multiple platforms
- Advanced error handling and retry logic

### v1 - Simple Scripts

Lightweight script-based version for quick downloads and simple use cases.

**Location**: `v1-scripts/`

**Key Features**:

- Standalone Python scripts
- Minimal dependencies (2 packages)
- Quick setup (60 seconds)
- Hardcoded for LeetCode
- Perfect for personal use

## Directory Structure

```
Crawler/
├── README.md                    # Main project documentation
├── ARCHITECTURE.md              # v2 technical architecture
├── DEVELOPMENT.md               # v2 development guide
├── PROJECT_STRUCTURE.md         # This file
│
├── v1-scripts/                  # v1 Simple Scripts
│   ├── README.md               # v1 full documentation
│   ├── QUICKSTART.md           # 60-second setup guide
│   ├── EXAMPLES.md             # Detailed usage examples
│   ├── COMPARISON.md           # v1 vs v2 comparison
│   ├── MIGRATION.md            # v1 to v2 upgrade guide
│   ├── requirements.txt        # v1 dependencies (2 packages)
│   │
│   ├── leetcode_crawler.py     # Single problem download
│   ├── fetch_solved_problems.py # List solved problems
│   ├── batch_download_solutions.py # Batch download
│   │
│   └── utils/                  # v1 utility modules
│       ├── leetcode_client.py  # LeetCode API client
│       └── formatters.py       # Text formatting utilities
│
├── src/crawler/                 # v2 Source Code
│   ├── domain/                 # Business entities
│   │   ├── entities/          # Problem, Submission, User
│   │   └── value_objects/     # Difficulty, Example, Constraint
│   │
│   ├── application/            # Use cases
│   │   ├── interfaces/        # Abstract interfaces
│   │   └── use_cases/         # Business logic
│   │
│   ├── infrastructure/         # External systems
│   │   ├── platforms/         # Platform clients (LeetCode, etc.)
│   │   ├── repositories/      # Data persistence
│   │   ├── formatters/        # Output formatters
│   │   └── http/              # HTTP client with retry/rate limiting
│   │
│   ├── cli/                    # Command-line interface
│   │   ├── commands/          # CLI command handlers
│   │   └── observers/         # Progress tracking
│   │
│   └── config/                 # Configuration management
│       ├── settings.py        # Config loading
│       └── logging_config.py  # Logging setup
│
├── tests/                       # v2 Test Suite
│   ├── unit/                   # Unit tests (fast, isolated)
│   │   ├── domain/            # Entity and value object tests
│   │   ├── application/       # Use case tests
│   │   └── infrastructure/    # Adapter and formatter tests
│   │
│   ├── integration/            # Integration tests (mocked HTTP)
│   │   └── platforms/         # Platform client tests
│   │
│   └── fixtures/               # Shared test data
│       ├── api_responses.py   # Mock API responses
│       └── problems.py        # Test problem entities
│
├── config.example.yaml          # Example configuration file
├── requirements.txt             # v2 dependencies
├── pyproject.toml              # Package configuration
└── pytest.ini                  # Test configuration
```

## Code Statistics

### v1 Scripts

- **Total Lines**: ~1,425 lines
- **Scripts**: 3 main scripts
- **Utilities**: 2 utility modules
- **Dependencies**: 2 packages (requests, beautifulsoup4)
- **Test Coverage**: None (manual testing)

### v2 Architecture

- **Total Lines**: ~3,000+ lines
- **Modules**: 30+ modules
- **Dependencies**: 10+ packages
- **Test Coverage**: 73%
- **Tests**: 100+ test cases

## Documentation Map

### Getting Started

1. **New Users (v2)**: Start with [README.md](README.md)
1. **Quick & Simple (v1)**: Start with [v1-scripts/QUICKSTART.md](v1-scripts/QUICKSTART.md)

### v1 Documentation

- [v1-scripts/README.md](v1-scripts/README.md) - Full v1 documentation
- [v1-scripts/QUICKSTART.md](v1-scripts/QUICKSTART.md) - 60-second setup
- [v1-scripts/EXAMPLES.md](v1-scripts/EXAMPLES.md) - Usage examples
- [v1-scripts/COMPARISON.md](v1-scripts/COMPARISON.md) - v1 vs v2
- [v1-scripts/MIGRATION.md](v1-scripts/MIGRATION.md) - Upgrade guide

### v2 Documentation

- [README.md](README.md) - Main documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

## Usage Comparison

### v1 Usage

```bash
cd v1-scripts
python leetcode_crawler.py https://leetcode.com/problems/two-sum/
python batch_download_solutions.py
```

### v2 Usage

```bash
crawler download two-sum --platform leetcode
crawler batch username --platform leetcode
```

## When to Use Each Version

### Use v1 When:

- ✅ You need a quick solution (setup in 60 seconds)
- ✅ You only need LeetCode support
- ✅ You prefer simple scripts over packages
- ✅ You want minimal dependencies
- ✅ You're doing personal downloads

### Use v2 When:

- ✅ You need production-ready code
- ✅ You want multiple output formats
- ✅ You plan to add other platforms
- ✅ You need comprehensive testing
- ✅ You prefer clean architecture
- ✅ You're building a tool for others

## Development Workflow

### v1 Development

```bash
cd v1-scripts
# Edit scripts directly
python leetcode_crawler.py URL
```

### v2 Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Check coverage
pytest --cov=src/crawler

# Use CLI
crawler download two-sum --platform leetcode
```

## Output Structure

### v1 Output

```
v1-scripts/
├── two-sum.py
├── add-two-numbers.py
└── ...
```

### v2 Output

```
problems/
└── leetcode/
    ├── two-sum/
    │   ├── solution.py
    │   └── metadata.json
    └── add-two-numbers/
        ├── solution.py
        └── metadata.json
```

## Architecture Comparison

### v1 Architecture

```
Scripts → Utils → LeetCode API
```

- Procedural programming
- Direct API calls
- Simple and straightforward

### v2 Architecture

```
CLI → Application → Domain → Infrastructure
```

- Clean architecture
- Dependency injection
- SOLID principles
- Testable and extensible

## Migration Path

1. **Start with v1**: Learn the basics
1. **Explore v2**: When you need more features
1. **Use Both**: v1 for quick tasks, v2 for production

See [v1-scripts/MIGRATION.md](v1-scripts/MIGRATION.md) for detailed migration guide.

## Contributing

### v1 Contributions

- Keep it simple
- Maintain backward compatibility
- Focus on LeetCode support

### v2 Contributions

- Follow clean architecture
- Write tests (maintain >80% coverage)
- Update documentation
- Follow SOLID principles

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed guidelines.

## Support

- **v1 Issues**: Check [v1-scripts/README.md](v1-scripts/README.md)
- **v2 Issues**: Check [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
- **General Questions**: Open an issue on the repository

## License

For personal use only. Respect LeetCode's Terms of Service and rate limits.

______________________________________________________________________

**Quick Links**:

- [Main README](README.md)
- [v1 Quick Start](v1-scripts/QUICKSTART.md)
- [v1 vs v2 Comparison](v1-scripts/COMPARISON.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Development Guide](DEVELOPMENT.md)
