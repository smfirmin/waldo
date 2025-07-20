// Map management module
class MapManager {
  constructor() {
    this.map = null;
    this.markers = [];
  }

  // Initialize map
  init() {
    if (this.map) {
      this.map.remove();
    }

    // Clear any existing markers
    this.markers = [];

    // Create map with better default view
    this.map = L.map('map', {
      center: [20, 0], // More neutral center
      zoom: 2,
      zoomControl: true,
      attributionControl: true,
    });

    // Add modern CartoDB Positron basemap
    const tileLayer = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
        minZoom: 1,
      }
    );

    tileLayer.addTo(this.map);

    // Force map to refresh after a brief delay
    setTimeout(() => {
      this.map.invalidateSize();
    }, 100);
  }

  // Create custom marker icon
  createCustomMarker() {
    const svgIcon = `
            <svg width="32" height="42" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 0C7.164 0 0 7.164 0 16c0 12 16 26 16 26s16-14 16-26C32 7.164 24.836 0 16 0z" 
                      fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
                <circle cx="16" cy="16" r="6" fill="#ffffff"/>
                <circle cx="16" cy="16" r="3" fill="#2563eb"/>
            </svg>
        `;

    return L.divIcon({
      html: svgIcon,
      className: 'custom-marker',
      iconSize: [32, 42],
      iconAnchor: [16, 42],
      popupAnchor: [0, -42],
    });
  }

  // Add markers to map
  addMarkers(locations) {
    if (!locations || locations.length === 0) {
      console.log('No locations to display');
      return;
    }

    console.log(`Adding ${locations.length} markers to map`);

    // Clear existing markers
    this.markers.forEach((marker) => {
      this.map.removeLayer(marker);
    });
    this.markers = [];

    const validLocations = [];
    const customIcon = this.createCustomMarker();

    locations.forEach((location, index) => {
      const lat = parseFloat(location.latitude);
      const lng = parseFloat(location.longitude);

      // Validate coordinates
      if (
        isNaN(lat) ||
        isNaN(lng) ||
        lat < -90 ||
        lat > 90 ||
        lng < -180 ||
        lng > 180
      ) {
        console.warn(
          `Invalid coordinates for location ${location.name}: ${lat}, ${lng}`
        );
        return;
      }

      validLocations.push(location);

      const marker = L.marker([lat, lng], {
        icon: customIcon,
        title: location.name,
      }).bindPopup(
        `
                <div class="popup-container">
                    <div class="popup-header">
                        <svg class="popup-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
                        </svg>
                        <span class="popup-title">${location.name}</span>
                    </div>
                    <div class="popup-summary">${location.events_summary || 'Mentioned in article.'}</div>
                </div>
            `,
        {
          maxWidth: 320,
          className: 'modern-popup',
        }
      );

      this.markers.push(marker);
      marker.addTo(this.map);
    });

    console.log(`Successfully added ${validLocations.length} valid markers`);

    // Fit map to show all markers with proper bounds
    if (validLocations.length > 0) {
      const group = new L.featureGroup(this.markers);
      const bounds = group.getBounds();

      if (bounds.isValid()) {
        // Add padding and set max zoom for single locations
        const padding = [40, 40];
        const maxZoom = validLocations.length === 1 ? 12 : 14;

        this.map.fitBounds(bounds, {
          padding: padding,
          maxZoom: maxZoom,
        });
      } else {
        console.warn('Invalid bounds calculated, using default view');
        this.map.setView([20, 0], 2);
      }
    }

    // Force map refresh
    setTimeout(() => {
      this.map.invalidateSize();
    }, 200);
  }
}

// Export for global use
window.MapManager = MapManager;
