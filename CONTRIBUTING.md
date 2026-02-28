# Contributing to AI Watchlist

Thank you for your interest in contributing to AI Watchlist! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies: `pip install -r requirements.txt`
4. Create a feature branch: `git checkout -b feature/my-feature`

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/G3niusYukki/AIWatchlist/issues)
- If not, create a new issue with:
  - Clear title and description
  - Steps to reproduce
  - Expected vs actual behavior
  - Your environment (Python version, OS)

### Suggesting Enhancements

- Open an issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would benefit the project

### Adding New Indicators

1. Create a new file in `ai_watchlist/indicators/`
2. Inherit the indicator pattern from existing indicators
3. Add to `indicators/__init__.py`
4. Update `config.py` with weight configuration
5. Add tests
6. Update documentation

### Adding New Companies

Edit `ai_watchlist/config.py`:

```python
{
    "ticker": "NEW",
    "name": "New Company",
    "github_orgs": ["org-name"],
    "sec_cik": "0000000000"
}
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/G3niusYukki/AIWatchlist.git
cd AIWatchlist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run the tool
python -m ai_watchlist analyze
```

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for classes and public methods
- Keep functions focused and under 50 lines when possible
- Use meaningful variable names
- Add comments for complex logic

### Example Code Style

```python
async def fetch_data(self, ticker: str) -> dict:
    """
    Fetch indicator data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing indicator values and metadata
    """
    # Implementation
    pass
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update CHANGELOG.md following the existing format
3. Ensure all tests pass
4. Request review from maintainers
5. PR must be approved before merging

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Documentation updated if needed
- [ ] Tests added/updated for new functionality
- [ ] All tests passing
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear and descriptive

## Questions?

Feel free to open an issue for any questions or reach out to the maintainers.

Thank you for contributing!
