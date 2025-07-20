// Main application logic
class WaldoApp {
  constructor() {
    this.mapManager = new MapManager();
    this.apiClient = new ApiClient();
    this.uiManager = new UIManager();
    this.realtimeClient = new RealtimeClient();
    this.progressUI = new ProgressUI();

    this.initEventListeners();
    this.initRealtimeHandlers();
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

  // Initialize real-time progress handlers
  initRealtimeHandlers() {
    this.realtimeClient.on('progress', (data) => {
      this.progressUI.updateProgress(data);
    });

    this.realtimeClient.on('complete', (data) => {
      this.progressUI.showComplete(data);
    });

    this.realtimeClient.on('error', (data) => {
      this.progressUI.showError(data.error || data.message || 'Unknown error');
    });
  }

  // Main extraction workflow
  async extractLocations() {
    if (!this.uiManager.validateInput()) {
      return;
    }

    this.uiManager.setButtonLoading(true);
    this.uiManager.hideResults(); // Hide previous results
    this.progressUI.show(); // Show progress UI

    try {
      const input = this.uiManager.getCurrentInput();

      // Start the API call and get immediate response with session_id
      const apiPromise = this.apiClient.extractLocations(input);

      // Wait a moment for the API to start processing, then connect to SSE
      // The API response should include the session_id we need
      apiPromise
        .then((data) => {
          if (data.session_id) {
            // Connect to real-time progress updates
            this.realtimeClient.connect(data.session_id);
          }
        })
        .catch(() => {
          // Ignore errors here, they'll be handled below
        });

      // Wait for the full API response
      const data = await apiPromise;

      // Update UI with final results
      this.uiManager.updateResults(data);
      this.uiManager.showResults();

      // Initialize map after DOM is visible
      setTimeout(() => {
        this.mapManager.init();
        this.mapManager.addMarkers(data.locations);
      }, 100);
    } catch (error) {
      console.error('Error:', error);
      this.progressUI.showError(error.message);
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
