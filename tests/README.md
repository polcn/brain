# Brain Tests

This directory contains the test suite for the Brain application.

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── utils.py             # Test utilities and helpers
├── test_vector_store.py # Vector store service tests
├── test_embeddings.py   # Embeddings service tests
├── test_llm.py          # LLM service tests
├── test_document_processor.py # Document processor tests
├── test_api_documents.py # Document API endpoint tests
├── test_api_chat.py     # Chat API endpoint tests
└── test_integration.py  # Integration tests
```

## Running Tests

### Run all tests
```bash
./scripts/run_tests.sh
```

### Run specific test categories
```bash
# Unit tests only
./scripts/run_tests.sh unit

# Integration tests only
./scripts/run_tests.sh integration

# Fast tests (no integration)
./scripts/run_tests.sh fast

# With coverage report
./scripts/run_tests.sh coverage

# Verbose output
./scripts/run_tests.sh verbose
```

### Run specific test files
```bash
# Run vector store tests
pytest tests/test_vector_store.py

# Run specific test
pytest tests/test_vector_store.py::TestVectorStoreService::test_similarity_search

# Run with specific marker
pytest -m "not integration"
```

## Test Markers

- `@pytest.mark.asyncio` - Async tests (automatically applied)
- `@pytest.mark.integration` - Tests requiring database/external services
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.unit` - Unit tests (no external dependencies)

## Writing Tests

### Basic Test Structure
```python
@pytest.mark.asyncio
async def test_something(mock_dependency):
    # Arrange
    service = MyService(mock_dependency)
    
    # Act
    result = await service.do_something()
    
    # Assert
    assert result == expected_value
```

### Using Fixtures
```python
async def test_with_fixtures(db_pool, mock_embeddings_service):
    # Fixtures are automatically injected
    service = VectorStoreService(db_pool)
    # ...
```

### Mocking Dependencies
```python
@pytest.fixture
def mock_service():
    service = Mock(spec=RealService)
    service.method = AsyncMock(return_value="mocked")
    return service
```

## Test Database

Integration tests use a separate test database (`brain_test`). The test runner automatically:
1. Creates the test database if needed
2. Runs migrations
3. Cleans data between tests

## Coverage

We aim for >80% code coverage. Coverage reports are generated in:
- Terminal: After each test run
- HTML: `htmlcov/index.html` (when using coverage mode)

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (S3, Bedrock, etc.)
3. **Fixtures**: Use fixtures for common setup
4. **Async**: Use `pytest.mark.asyncio` for async tests
5. **Naming**: Use descriptive test names that explain what's being tested
6. **AAA Pattern**: Arrange, Act, Assert structure
7. **Error Cases**: Test both success and failure scenarios

## Troubleshooting

### Database Connection Errors
```bash
# Ensure PostgreSQL is running
sudo systemctl status postgresql

# Check test database exists
psql -U postgres -c "\\l" | grep brain_test
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### Async Test Issues
- Always use `pytest.mark.asyncio` for async tests
- Use `AsyncMock` instead of `Mock` for async methods
- Check event loop fixtures in conftest.py