# Frontend Tests

This directory contains Jest tests for the Waldo frontend JavaScript modules.

## Test Structure

- `setup.js` - Jest configuration and global mocks
- `map.test.js` - Tests for MapManager class
- `api.test.js` - Tests for ApiClient class  
- `ui.test.js` - Tests for UIManager class
- `app.test.js` - Tests for WaldoApp class (main application)

## Running Tests

### Prerequisites

```bash
cd frontend
npm install
```

### Test Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## Test Coverage

The tests aim for 80% coverage across:
- Functions
- Statements  
- Branches
- Lines

## Mocking Strategy

### External Dependencies
- **Leaflet**: Mocked globally in `setup.js`
- **Fetch API**: Mocked for API testing
- **DOM Elements**: Created in test setup

### Test Isolation
Each test file:
1. Sets up clean DOM state
2. Creates fresh instances
3. Clears mocks between tests
4. Tests both success and error scenarios

## Test Categories

### Unit Tests
- Individual class methods
- Input validation
- Error handling
- State management

### Integration Tests  
- Event handler workflows
- API communication flows
- UI state transitions

## Best Practices

1. **Arrange-Act-Assert**: Clear test structure
2. **Descriptive Names**: Tests explain what they verify
3. **Mock External Dependencies**: Focus on unit behavior
4. **Test Error Cases**: Verify error handling
5. **Clean Setup/Teardown**: Isolated test environment