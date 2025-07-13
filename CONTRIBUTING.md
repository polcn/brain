# Contributing to Brain

Thank you for your interest in contributing to Brain! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/brain.git
   cd brain
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/polcn/brain.git
   ```
4. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Process

### Setting Up Development Environment

1. Follow the setup instructions in README.md
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Making Changes

1. **Write Tests First**: Follow TDD practices when possible
2. **Follow Code Style**: 
   - Python: PEP 8, enforced by Black
   - Use type hints for all functions
   - Add docstrings to public functions
3. **Keep Changes Focused**: One feature/fix per PR
4. **Update Documentation**: Update relevant docs with your changes

### Code Quality Checks

Before submitting, ensure your code passes all checks:

```bash
# Format code
black backend/
isort backend/

# Run linting
flake8 backend/

# Type checking
mypy backend/

# Run tests
pytest -v

# Security scan
bandit -r backend/
```

### Commit Guidelines

- Use clear, descriptive commit messages
- Format: `type: brief description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Example: `feat: add PDF text extraction support`

### Pull Request Process

1. Update your branch with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub with:
   - Clear title and description
   - Reference any related issues
   - Screenshots/examples if applicable

4. Address review feedback promptly

## Testing

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

### Writing Tests
- Place tests in `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Include both positive and negative test cases
- Mock external services (S3, Bedrock, etc.)

## Architecture Guidelines

### Database
- Use transactions for multi-step operations
- Always use parameterized queries
- Include proper indexes for performance
- Document schema changes clearly

### API Design
- Follow RESTful principles
- Use proper HTTP status codes
- Include request/response validation
- Document with OpenAPI/Swagger

### Security
- Never commit secrets or credentials
- Validate all user inputs
- Use proper authentication/authorization
- Follow OWASP guidelines

## Documentation

### Code Documentation
- Add docstrings to all public functions
- Include type hints
- Document complex algorithms
- Add inline comments for non-obvious logic

### API Documentation
- Update OpenAPI specs
- Include example requests/responses
- Document error scenarios
- Keep README.md current

## Performance Considerations

- Profile before optimizing
- Use async/await properly
- Implement proper caching
- Monitor database query performance
- Consider batch operations for bulk actions

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Check PostgreSQL and pgvector installation
3. **AWS Errors**: Verify credentials and permissions
4. **Type Errors**: Run `mypy` to catch type issues

### Getting Help

- Check existing issues on GitHub
- Read through CLAUDE.md for AI-specific guidance
- Review REQUIREMENTS.md for architecture details
- Ask questions in pull request comments

## Release Process

1. Ensure all tests pass
2. Update version in `backend/__init__.py`
3. Update CHANGELOG.md
4. Create release PR
5. Tag release after merge

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- Project documentation

Thank you for contributing to Brain!