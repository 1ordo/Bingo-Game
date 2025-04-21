# Contributing to Belgian Bingo Game

Thank you for considering contributing to the Belgian Bingo Game! This document provides guidelines and workflows to make the contribution process smooth and effective.

## Development Process

We use a simplified Git workflow:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Setting Up Development Environment

1. Clone your fork:
```
git clone https://github.com/YOUR_USERNAME/belgian-bingo.git
cd belgian-bingo
```

2. Create virtual environment:
```
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Code Style

We follow these coding standards:
- Use 4 spaces for indentation
- Follow PEP 8 guidelines for Python code
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions small and focused

## Testing

Before submitting changes:

1. Test the game in both hardware and simulation modes
2. Verify all features still work as expected
3. Check for any visual glitches or performance issues

## Pull Request Process

1. Update the README.md and documentation with details of changes if needed
2. Update the CHANGELOG.md with notes on your changes
3. Submit your pull request with a clear title and description
4. Link any relevant issues in your PR description using keywords like "Fixes #123"

## Feature Requests and Bug Reports

Please use GitHub Issues to report bugs or suggest features. When filing an issue, please include:

- A clear, descriptive title
- A detailed description of the issue or feature
- Steps to reproduce (for bugs)
- Expected behavior
- Screenshots if applicable
- System information (OS, Python version, etc.)

## Animation and UI Improvements

For animation and UI enhancements:
- Submit a mockup or description of your idea first as an issue
- Use pygame's built-in animation capabilities when possible
- Keep performance in mind, especially for lower-end hardware
- Consider both hardware and simulation modes

## Arduino Code Contributions

When modifying Arduino code:
- Test changes on both Uno and Mega architectures
- Document pin connections clearly
- Provide circuit diagrams for new hardware features
- Consider compatibility with existing hardware setups

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.