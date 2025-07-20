module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],

  // Test file patterns
  testMatch: ['<rootDir>/tests/**/*.test.js'],

  // Coverage configuration
  collectCoverageFrom: [
    'js/**/*.js',
    '!js/app.js', // Exclude main app file from coverage (integration-focused)
    '!**/node_modules/**',
  ],

  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'text-summary', 'lcov', 'html'],


  // Mock static assets
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },

  // Transform configuration (using default)

  // Test timeout
  testTimeout: 10000,

  // Verbose output
  verbose: true,
};
