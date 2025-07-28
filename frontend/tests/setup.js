// Jest setup file for frontend tests

// Mock Leaflet for tests
global.L = {
  map: jest.fn(() => ({
    remove: jest.fn(),
    setView: jest.fn(),
    fitBounds: jest.fn(),
    invalidateSize: jest.fn(),
    removeLayer: jest.fn(),
  })),
  tileLayer: jest.fn(() => ({
    addTo: jest.fn(),
    on: jest.fn(),
    removeLayer: jest.fn(),
  })),
  marker: jest.fn(() => ({
    bindPopup: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
  })),
  divIcon: jest.fn(() => ({})),
  featureGroup: jest.fn(() => ({
    getBounds: jest.fn(() => ({
      isValid: jest.fn(() => true),
    })),
  })),
};

// Mock fetch for API tests
global.fetch = jest.fn();

// Mock DOM elements that might be needed
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
  },
  writable: true,
});

// Setup console mocking to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};
