// Tests for ApiClient class

// Import the module
require('../js/api.js');

describe('ApiClient', () => {
  let apiClient;

  beforeEach(() => {
    apiClient = new window.ApiClient();

    // Reset fetch mock
    fetch.mockClear();
  });

  describe('constructor', () => {
    test('should initialize with empty baseUrl', () => {
      expect(apiClient.baseUrl).toBe('');
    });
  });

  describe('extractLocations', () => {
    test('should make POST request to /api/extract', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          locations: [],
          processing_time: 1.5,
        }),
      };

      fetch.mockResolvedValue(mockResponse);

      await apiClient.extractLocations('test input');

      expect(fetch).toHaveBeenCalledWith('/api/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: 'test input' }),
      });
    });

    test('should return parsed JSON on success', async () => {
      const expectedData = {
        locations: [
          { name: 'New York', latitude: 40.7128, longitude: -74.006 },
        ],
        processing_time: 2.1,
      };

      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue(expectedData),
      };

      fetch.mockResolvedValue(mockResponse);

      const result = await apiClient.extractLocations('test input');

      expect(result).toEqual(expectedData);
    });

    test('should handle rate limit errors specially', async () => {
      const mockErrorResponse = {
        ok: false,
        status: 429,
        headers: {
          get: jest.fn().mockReturnValue('120'),
        },
        json: jest.fn().mockResolvedValue({
          error_code: 'RATE_LIMIT_EXCEEDED',
          message: 'Rate limit exceeded',
        }),
      };

      fetch.mockResolvedValue(mockErrorResponse);

      await expect(apiClient.extractLocations('test input')).rejects.toThrow(
        '⏰ API rate limit exceeded. Please try again in 120 seconds.'
      );
    });

    test('should handle rate limit errors without retry-after header', async () => {
      const mockErrorResponse = {
        ok: false,
        status: 429,
        headers: {
          get: jest.fn().mockReturnValue(null),
        },
        json: jest.fn().mockResolvedValue({
          error_code: 'RATE_LIMIT_EXCEEDED',
          retry_after: 90,
        }),
      };

      fetch.mockResolvedValue(mockErrorResponse);

      await expect(apiClient.extractLocations('test input')).rejects.toThrow(
        '⏰ API rate limit exceeded. Please try again in 90 seconds.'
      );
    });

    test('should handle rate limit errors with default retry time', async () => {
      const mockErrorResponse = {
        ok: false,
        status: 429,
        headers: {
          get: jest.fn().mockReturnValue(null),
        },
        json: jest.fn().mockResolvedValue({
          error_code: 'RATE_LIMIT_EXCEEDED',
        }),
      };

      fetch.mockResolvedValue(mockErrorResponse);

      await expect(apiClient.extractLocations('test input')).rejects.toThrow(
        '⏰ API rate limit exceeded. Please try again in 60 seconds.'
      );
    });

    test('should handle general errors', async () => {
      const mockErrorResponse = {
        ok: false,
        status: 400,
        json: jest.fn().mockResolvedValue({
          message: 'Invalid input provided',
        }),
      };

      fetch.mockResolvedValue(mockErrorResponse);

      await expect(apiClient.extractLocations('')).rejects.toThrow(
        'Invalid input provided'
      );
    });

    test('should handle errors without message', async () => {
      const mockErrorResponse = {
        ok: false,
        status: 500,
        json: jest.fn().mockResolvedValue({
          error: 'Internal server error',
        }),
      };

      fetch.mockResolvedValue(mockErrorResponse);

      await expect(apiClient.extractLocations('test input')).rejects.toThrow(
        'Internal server error'
      );
    });

    test('should handle errors with fallback message', async () => {
      const mockErrorResponse = {
        ok: false,
        status: 500,
        json: jest.fn().mockResolvedValue({}),
      };

      fetch.mockResolvedValue(mockErrorResponse);

      await expect(apiClient.extractLocations('test input')).rejects.toThrow(
        'Failed to extract locations'
      );
    });
  });
});
