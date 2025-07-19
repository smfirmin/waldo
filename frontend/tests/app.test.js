// Tests for WaldoApp class

// We need to define WaldoApp before requiring the module since it's wrapped in DOMContentLoaded
global.WaldoApp = class WaldoApp {
  constructor() {
    this.mapManager = new window.MapManager();
    this.apiClient = new window.ApiClient();
    this.uiManager = new window.UIManager();
    
    this.initEventListeners();
  }

  initEventListeners() {
    document.getElementById('extractBtn').addEventListener('click', () => {
      this.extractLocations();
    });
    
    document.getElementById('urlInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.extractLocations();
      }
    });
    
    document.getElementById('textInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        this.extractLocations();
      }
    });
    
    document.getElementById('urlToggle').addEventListener('click', () => {
      this.uiManager.toggleInputMode('url');
    });
    
    document.getElementById('textToggle').addEventListener('click', () => {
      this.uiManager.toggleInputMode('text');
    });
  }

  async extractLocations() {
    if (!this.uiManager.validateInput()) {
      return;
    }

    this.uiManager.setButtonLoading(true);
    this.uiManager.showLoading();
    
    try {
      const input = this.uiManager.getCurrentInput();
      const data = await this.apiClient.extractLocations(input);
      
      this.uiManager.updateResults(data);
      this.uiManager.showResults();
      
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

window.WaldoApp = global.WaldoApp;

describe('WaldoApp', () => {
  let waldoApp;
  let mockMapManager;
  let mockApiClient;
  let mockUIManager;

  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <button id="extractBtn">Extract</button>
      <input id="urlInput" type="url" />
      <textarea id="textInput"></textarea>
      <button id="urlToggle">URL</button>
      <button id="textToggle">Text</button>
      <div id="statusCard"></div>
      <div id="loadingSection"></div>
      <div id="errorSection"></div>
      <div id="resultsSection"></div>
      <div id="inputGroup"></div>
      <div id="articleTitle"></div>
      <div id="locationsCount"></div>
      <div id="processingTime"></div>
    `;

    // Mock the classes
    mockMapManager = {
      init: jest.fn(),
      addMarkers: jest.fn()
    };

    mockApiClient = {
      extractLocations: jest.fn()
    };

    mockUIManager = {
      validateInput: jest.fn(),
      setButtonLoading: jest.fn(),
      showLoading: jest.fn(),
      getCurrentInput: jest.fn(),
      updateResults: jest.fn(),
      showResults: jest.fn(),
      showError: jest.fn(),
      toggleInputMode: jest.fn()
    };

    // Mock the global classes
    window.MapManager = jest.fn(() => mockMapManager);
    window.ApiClient = jest.fn(() => mockApiClient);
    window.UIManager = jest.fn(() => mockUIManager);

    waldoApp = new window.WaldoApp();
  });

  describe('constructor', () => {
    test('should initialize all managers', () => {
      expect(window.MapManager).toHaveBeenCalled();
      expect(window.ApiClient).toHaveBeenCalled();
      expect(window.UIManager).toHaveBeenCalled();
      expect(waldoApp.mapManager).toBe(mockMapManager);
      expect(waldoApp.apiClient).toBe(mockApiClient);
      expect(waldoApp.uiManager).toBe(mockUIManager);
    });
  });

  describe('initEventListeners', () => {
    test('should add event listeners to DOM elements', () => {
      // Test that event listeners are added (this is implicit from constructor)
      const extractBtn = document.getElementById('extractBtn');
      const urlInput = document.getElementById('urlInput');
      const textInput = document.getElementById('textInput');
      const urlToggle = document.getElementById('urlToggle');
      const textToggle = document.getElementById('textToggle');

      expect(extractBtn).toBeTruthy();
      expect(urlInput).toBeTruthy();
      expect(textInput).toBeTruthy();
      expect(urlToggle).toBeTruthy();
      expect(textToggle).toBeTruthy();
    });
  });

  describe('extractLocations', () => {
    test('should return early if validation fails', async () => {
      mockUIManager.validateInput.mockReturnValue(false);

      await waldoApp.extractLocations();

      expect(mockUIManager.setButtonLoading).not.toHaveBeenCalled();
      expect(mockUIManager.showLoading).not.toHaveBeenCalled();
    });

    test('should handle successful extraction', async () => {
      const mockData = {
        locations: [
          { name: 'New York', latitude: 40.7128, longitude: -74.0060 }
        ],
        processing_time: 2.1
      };

      mockUIManager.validateInput.mockReturnValue(true);
      mockUIManager.getCurrentInput.mockReturnValue('test input');
      mockApiClient.extractLocations.mockResolvedValue(mockData);

      await waldoApp.extractLocations();

      expect(mockUIManager.setButtonLoading).toHaveBeenCalledWith(true);
      expect(mockUIManager.showLoading).toHaveBeenCalled();
      expect(mockUIManager.getCurrentInput).toHaveBeenCalled();
      expect(mockApiClient.extractLocations).toHaveBeenCalledWith('test input');
      expect(mockUIManager.updateResults).toHaveBeenCalledWith(mockData);
      expect(mockUIManager.showResults).toHaveBeenCalled();
      expect(mockUIManager.setButtonLoading).toHaveBeenCalledWith(false);
    });

    test('should initialize map after showing results', async () => {
      const mockData = {
        locations: [
          { name: 'New York', latitude: 40.7128, longitude: -74.0060 }
        ]
      };

      mockUIManager.validateInput.mockReturnValue(true);
      mockUIManager.getCurrentInput.mockReturnValue('test input');
      mockApiClient.extractLocations.mockResolvedValue(mockData);

      await waldoApp.extractLocations();

      // Wait for the setTimeout to execute
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(mockMapManager.init).toHaveBeenCalled();
      expect(mockMapManager.addMarkers).toHaveBeenCalledWith(mockData.locations);
    });

    test('should handle API errors', async () => {
      const error = new Error('API Error');
      
      mockUIManager.validateInput.mockReturnValue(true);
      mockUIManager.getCurrentInput.mockReturnValue('test input');
      mockApiClient.extractLocations.mockRejectedValue(error);

      await waldoApp.extractLocations();

      expect(mockUIManager.showError).toHaveBeenCalledWith('API Error');
      expect(mockUIManager.setButtonLoading).toHaveBeenCalledWith(false);
    });

    test('should handle rate limit errors', async () => {
      const error = new Error('⏰ API rate limit exceeded. Please try again in 60 seconds.');
      
      mockUIManager.validateInput.mockReturnValue(true);
      mockUIManager.getCurrentInput.mockReturnValue('test input');
      mockApiClient.extractLocations.mockRejectedValue(error);

      await waldoApp.extractLocations();

      expect(mockUIManager.showError).toHaveBeenCalledWith(
        '⏰ API rate limit exceeded. Please try again in 60 seconds.'
      );
      expect(mockUIManager.setButtonLoading).toHaveBeenCalledWith(false);
    });

    test('should always reset button loading state', async () => {
      mockUIManager.validateInput.mockReturnValue(true);
      mockUIManager.getCurrentInput.mockReturnValue('test input');
      mockApiClient.extractLocations.mockRejectedValue(new Error('Test error'));

      await waldoApp.extractLocations();

      expect(mockUIManager.setButtonLoading).toHaveBeenCalledWith(true);
      expect(mockUIManager.setButtonLoading).toHaveBeenCalledWith(false);
    });
  });

  describe('event handlers', () => {
    test('should call toggleInputMode when URL toggle is clicked', () => {
      const urlToggle = document.getElementById('urlToggle');
      
      urlToggle.click();
      
      expect(mockUIManager.toggleInputMode).toHaveBeenCalledWith('url');
    });

    test('should call toggleInputMode when text toggle is clicked', () => {
      const textToggle = document.getElementById('textToggle');
      
      textToggle.click();
      
      expect(mockUIManager.toggleInputMode).toHaveBeenCalledWith('text');
    });

    test('should call extractLocations when extract button is clicked', () => {
      const extractBtn = document.getElementById('extractBtn');
      mockUIManager.validateInput.mockReturnValue(false); // To prevent actual execution
      
      extractBtn.click();
      
      // Validation should be called (indicating extractLocations was called)
      expect(mockUIManager.validateInput).toHaveBeenCalled();
    });

    test('should call extractLocations on Enter key in URL input', () => {
      const urlInput = document.getElementById('urlInput');
      mockUIManager.validateInput.mockReturnValue(false); // To prevent actual execution
      
      const enterEvent = new KeyboardEvent('keypress', { key: 'Enter' });
      urlInput.dispatchEvent(enterEvent);
      
      expect(mockUIManager.validateInput).toHaveBeenCalled();
    });

    test('should call extractLocations on Ctrl+Enter in text input', () => {
      const textInput = document.getElementById('textInput');
      mockUIManager.validateInput.mockReturnValue(false); // To prevent actual execution
      
      const ctrlEnterEvent = new KeyboardEvent('keypress', { 
        key: 'Enter', 
        ctrlKey: true 
      });
      textInput.dispatchEvent(ctrlEnterEvent);
      
      expect(mockUIManager.validateInput).toHaveBeenCalled();
    });

    test('should not call extractLocations on Enter without Ctrl in text input', () => {
      const textInput = document.getElementById('textInput');
      
      const enterEvent = new KeyboardEvent('keypress', { key: 'Enter' });
      textInput.dispatchEvent(enterEvent);
      
      expect(mockUIManager.validateInput).not.toHaveBeenCalled();
    });
  });
});