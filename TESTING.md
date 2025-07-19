# Testing Guide

This document describes the testing setup for the Waldo application, which includes both backend Python tests and frontend JavaScript tests.

## Overview

The Waldo project uses a comprehensive testing strategy:
- **Backend**: Python tests using pytest with coverage reporting
- **Frontend**: JavaScript tests using Jest with coverage reporting
- **CI/CD**: GitHub Actions pipeline that runs both test suites

## Backend Testing

### Framework
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **Ruff**: Code linting

### Running Backend Tests

```bash
# Run all backend tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_routes.py

# Run with verbose output
pytest -v
```

### Backend Test Structure
```
tests/
├── test_models/
│   └── test_data_models.py
├── test_services/
│   ├── test_article_extractor.py
│   ├── test_geocoding.py
│   ├── test_location_extractor.py
│   └── test_summarizer.py
├── test_routes.py
├── test_spatial_filtering.py
└── test_rate_limiting.py
```

## Frontend Testing

### Framework
- **Jest**: Test framework
- **Jest-DOM**: DOM testing utilities
- **JSDoc**: Coverage reporting

### Running Frontend Tests

```bash
cd frontend

# Run all frontend tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### Frontend Test Structure
```
frontend/tests/
├── setup.js           # Global mocks and configuration
├── api.test.js        # ApiClient tests
├── map.test.js        # MapManager tests
├── ui.test.js         # UIManager tests
├── app.test.js        # WaldoApp integration tests
└── README.md          # Frontend testing documentation
```

### Coverage Targets
- **Statements**: 80%+
- **Branches**: 80%+
- **Functions**: 80%+
- **Lines**: 80%+

## Running All Tests

### Local Development

```bash
# Run comprehensive test suite (both backend and frontend)
./test-all.sh

# Or run separately
pytest --cov=app --cov-report=term-missing
cd frontend && npm run test:coverage
```

### GitHub Actions CI

The CI pipeline automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

**Pipeline Jobs:**
1. **backend-test**: Runs Python tests on Python 3.11 and 3.12
2. **frontend-test**: Runs Jest tests on Node.js 18
3. **docker**: Builds and tests Docker image (only on main branch)

## Coverage Reporting

Both backend and frontend tests generate coverage reports that are uploaded to Codecov:
- Backend coverage: `coverage.xml`
- Frontend coverage: `frontend/coverage/lcov.info`

## Best Practices

### Writing Tests
1. **Arrange-Act-Assert**: Structure tests clearly
2. **Descriptive Names**: Test names should explain what they verify
3. **Mock External Dependencies**: Use mocks for external services
4. **Test Error Cases**: Include negative test scenarios
5. **Maintain Coverage**: Aim for 80%+ coverage

### Test Organization
1. **Backend**: Group tests by module/service
2. **Frontend**: One test file per JavaScript module
3. **Integration**: Test complete workflows
4. **Unit**: Test individual functions/methods

### Continuous Integration
1. **Fast Feedback**: Tests run on every push
2. **Parallel Execution**: Backend and frontend tests run concurrently
3. **Quality Gates**: All tests must pass before merging
4. **Coverage Tracking**: Coverage reports prevent regression

## Troubleshooting

### Common Issues

**Backend Tests:**
- Virtual environment not activated
- Missing dependencies in requirements-dev.txt
- API key environment variables not set

**Frontend Tests:**
- Node.js version mismatch (use Node 18+)
- Missing package-lock.json
- DOM elements not properly mocked

**CI Pipeline:**
- Package-lock.json out of sync
- Cache invalidation needed
- Dependency version conflicts

### Getting Help

1. Check test output for specific error messages
2. Verify all dependencies are installed
3. Ensure environment variables are set
4. Run tests locally before pushing to CI