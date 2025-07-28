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

    this.realtimeClient.on('complete', async (data) => {
      this.progressUI.showComplete(data);

      // Fetch final results when processing completes
      try {
        console.log('Fetching results for session:', data.session_id);
        const resultsResponse = await fetch(`/api/results/${data.session_id}`);

        if (resultsResponse.ok) {
          const results = await resultsResponse.json();
          console.log('Results received:', results);

          // Update UI with final results
          this.uiManager.updateResults(results);
          this.uiManager.showResults();

          // Initialize map after DOM is visible
          setTimeout(() => {
            this.mapManager.init();
            this.mapManager.addMarkers(results.locations);
          }, 100);
        } else {
          const errorData = await resultsResponse.json();
          console.error('Results fetch failed:', errorData);
          this.uiManager.showError(
            `Failed to get results: ${errorData.error || 'Unknown error'}`
          );
        }
      } catch (error) {
        console.error('Error fetching results:', error);
        this.uiManager.showError('Failed to fetch results: ' + error.message);
      } finally {
        this.uiManager.setButtonLoading(false);
      }
    });

    this.realtimeClient.on('error', (data) => {
      this.progressUI.showError(data.error || data.message || 'Unknown error');
      this.uiManager.setButtonLoading(false);
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

      // Start the API call and get session_id immediately
      const startResponse = await this.apiClient.extractLocations(input);

      if (startResponse.session_id) {
        // Connect to real-time progress updates immediately
        this.realtimeClient.connect(startResponse.session_id);

        // Wait for processing to complete via SSE events
        // Results will be handled in the realtime callbacks
      } else {
        throw new Error('No session ID received from server');
      }
    } catch (error) {
      console.error('Error:', error);
      this.progressUI.showError(error.message);
      this.uiManager.showError(error.message);
      this.uiManager.setButtonLoading(false);
    }
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new WaldoApp();
});
