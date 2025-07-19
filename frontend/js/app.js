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
        this.uiManager.showLoading();
        
        try {
            const input = this.uiManager.getCurrentInput();
            const data = await this.apiClient.extractLocations(input);
            
            // Update UI with results
            this.uiManager.updateResults(data);
            this.uiManager.showResults();
            
            // Initialize map after DOM is visible
            setTimeout(() => {
                this.mapManager.init();
                this.mapManager.addMarkers(data.locations);
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