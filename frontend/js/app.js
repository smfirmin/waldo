// Main application logic
class WaldoApp {
  constructor() {
    this.mapManager = new MapManager();
    this.apiClient = new ApiClient();
    this.uiManager = new UIManager();

    this.initEventListeners();
  }

  // Initialize event listeners
  initEventListeners() {
    // Extract button
    document.getElementById('extractBtn').addEventListener('click', () => {
      this.extractLocations();
    });

    // URL input enter key
    document.getElementById('urlInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.extractLocations();
      }
    });

    // Text input ctrl+enter
    document.getElementById('textInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        this.extractLocations();
      }
    });

    // Toggle buttons
    document.getElementById('urlToggle').addEventListener('click', () => {
      this.uiManager.toggleInputMode('url');
    });

    document.getElementById('textToggle').addEventListener('click', () => {
      this.uiManager.toggleInputMode('text');
    });
  }

  // Main extraction workflow
  async extractLocations() {
    if (!this.uiManager.validateInput()) {
      return;
    }

    this.uiManager.setButtonLoading(true);
    this.uiManager.hideResults(); // Hide previous results
    this.uiManager.showLoading(); // Show loading state

    try {
      const input = this.uiManager.getCurrentInput();

      // Direct API call - get results immediately
      const results = await this.apiClient.extractLocations(input);

      console.log('Results received:', results);

      // Update UI with results
      this.uiManager.updateResults(results);
      this.uiManager.showResults();

      // Initialize map after DOM is visible
      setTimeout(() => {
        this.mapManager.init();
        this.mapManager.addMarkers(results.locations);
      }, 100);
    } catch (error) {
      console.error('Error:', error);
      this.uiManager.showError(error.message);
    } finally {
      this.uiManager.setButtonLoading(false);
    }
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new WaldoApp();
});
