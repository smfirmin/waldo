// Tests for MapManager class

// Import the module
require('../js/map.js');

describe('MapManager', () => {
  let mapManager;

  beforeEach(() => {
    // Reset DOM
    document.body.innerHTML = '<div id="map"></div>';

    // Create new instance
    mapManager = new window.MapManager();

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    test('should initialize with null map and empty markers', () => {
      expect(mapManager.map).toBeNull();
      expect(mapManager.markers).toEqual([]);
    });
  });

  describe('init', () => {
    test('should create a new map instance', () => {
      mapManager.init();

      expect(L.map).toHaveBeenCalledWith('map', {
        center: [20, 0],
        zoom: 2,
        zoomControl: true,
        attributionControl: true,
      });
    });

    test('should remove existing map before creating new one', () => {
      const mockRemove = jest.fn();
      mapManager.map = { remove: mockRemove };

      mapManager.init();

      expect(mockRemove).toHaveBeenCalled();
    });

    test('should reset markers array', () => {
      mapManager.markers = ['marker1', 'marker2'];

      mapManager.init();

      expect(mapManager.markers).toEqual([]);
    });
  });

  describe('createCustomMarker', () => {
    test('should create a div icon with custom SVG', () => {
      const result = mapManager.createCustomMarker();

      expect(L.divIcon).toHaveBeenCalledWith({
        html: expect.stringContaining('<svg'),
        className: 'custom-marker',
        iconSize: [32, 42],
        iconAnchor: [16, 42],
        popupAnchor: [0, -42],
      });
    });
  });

  describe('addMarkers', () => {
    beforeEach(() => {
      mapManager.map = {
        removeLayer: jest.fn(),
        invalidateSize: jest.fn(),
        fitBounds: jest.fn(),
        setView: jest.fn(),
      };
    });

    test('should handle empty locations array', () => {
      mapManager.addMarkers([]);

      expect(console.log).toHaveBeenCalledWith('No locations to display');
    });

    test('should handle null locations', () => {
      mapManager.addMarkers(null);

      expect(console.log).toHaveBeenCalledWith('No locations to display');
    });

    test('should create markers for valid locations', () => {
      const locations = [
        {
          name: 'New York',
          latitude: 40.7128,
          longitude: -74.006,
          events_summary: 'Test event',
        },
      ];

      mapManager.addMarkers(locations);

      expect(L.marker).toHaveBeenCalledWith(
        [40.7128, -74.006],
        expect.objectContaining({
          title: 'New York',
        })
      );
    });

    test('should skip locations with invalid coordinates', () => {
      const locations = [
        {
          name: 'Invalid Location',
          latitude: 'invalid',
          longitude: 'invalid',
        },
        {
          name: 'Valid Location',
          latitude: 40.7128,
          longitude: -74.006,
        },
      ];

      mapManager.addMarkers(locations);

      expect(console.warn).toHaveBeenCalledWith(
        'Invalid coordinates for location Invalid Location: NaN, NaN'
      );
      expect(L.marker).toHaveBeenCalledTimes(1);
    });

    test('should fit bounds for multiple valid locations', () => {
      const locations = [
        { name: 'Location 1', latitude: 40.7128, longitude: -74.006 },
        { name: 'Location 2', latitude: 34.0522, longitude: -118.2437 },
      ];

      mapManager.addMarkers(locations);

      expect(L.featureGroup).toHaveBeenCalled();
      expect(mapManager.map.fitBounds).toHaveBeenCalled();
    });
  });
});
