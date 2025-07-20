// Tests for UIManager class

// Import the module
require('../js/ui.js');

describe('UIManager', () => {
  let uiManager;

  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <div id="statusCard" class="status-card">
        <div id="loadingSection" style="display: none;"></div>
        <div id="errorSection" style="display: none;"></div>
        <div id="resultsSection" style="display: none;"></div>
      </div>
      <button id="extractBtn">Extract</button>
      <input id="urlInput" type="url" />
      <textarea id="textInput" style="display: none;"></textarea>
      <div id="inputGroup"></div>
      <div id="articleTitle"></div>
      <div id="locationsCount"></div>
      <div id="processingTime"></div>
      <button id="urlToggle" class="active">URL</button>
      <button id="textToggle">Text</button>
    `;

    uiManager = new window.UIManager();
  });

  describe('constructor', () => {
    test('should initialize with DOM elements', () => {
      expect(uiManager.statusCard).toBeTruthy();
      expect(uiManager.loadingSection).toBeTruthy();
      expect(uiManager.errorSection).toBeTruthy();
      expect(uiManager.resultsSection).toBeTruthy();
      expect(uiManager.extractBtn).toBeTruthy();
      expect(uiManager.urlInput).toBeTruthy();
      expect(uiManager.textInput).toBeTruthy();
      expect(uiManager.inputGroup).toBeTruthy();
    });
  });

  describe('showLoading', () => {
    test('should show loading section and hide others', () => {
      uiManager.showLoading();

      expect(uiManager.statusCard.classList.contains('show')).toBe(true);
      expect(uiManager.loadingSection.style.display).toBe('block');
      expect(uiManager.errorSection.style.display).toBe('none');
      expect(uiManager.resultsSection.style.display).toBe('none');
    });
  });

  describe('showError', () => {
    test('should show error section with message', () => {
      const errorMessage = 'Test error message';

      uiManager.showError(errorMessage);

      expect(uiManager.statusCard.classList.contains('show')).toBe(true);
      expect(uiManager.loadingSection.style.display).toBe('none');
      expect(uiManager.errorSection.style.display).toBe('block');
      expect(uiManager.resultsSection.style.display).toBe('none');
      expect(uiManager.errorSection.textContent).toBe(errorMessage);
    });
  });

  describe('showResults', () => {
    test('should show results section and hide others', () => {
      uiManager.showResults();

      expect(uiManager.statusCard.classList.contains('show')).toBe(true);
      expect(uiManager.loadingSection.style.display).toBe('none');
      expect(uiManager.errorSection.style.display).toBe('none');
      expect(uiManager.resultsSection.style.display).toBe('grid');
    });
  });

  describe('hideStatus', () => {
    test('should remove show class from status card', () => {
      uiManager.statusCard.classList.add('show');

      uiManager.hideStatus();

      expect(uiManager.statusCard.classList.contains('show')).toBe(false);
    });
  });

  describe('toggleInputMode', () => {
    test('should switch to URL mode', () => {
      const urlToggle = document.getElementById('urlToggle');
      const textToggle = document.getElementById('textToggle');

      uiManager.toggleInputMode('url');

      expect(urlToggle.classList.contains('active')).toBe(true);
      expect(textToggle.classList.contains('active')).toBe(false);
      expect(uiManager.urlInput.style.display).toBe('block');
      expect(uiManager.textInput.style.display).toBe('none');
      expect(uiManager.inputGroup.classList.contains('text-mode')).toBe(false);
    });

    test('should switch to text mode', () => {
      const urlToggle = document.getElementById('urlToggle');
      const textToggle = document.getElementById('textToggle');

      uiManager.toggleInputMode('text');

      expect(urlToggle.classList.contains('active')).toBe(false);
      expect(textToggle.classList.contains('active')).toBe(true);
      expect(uiManager.urlInput.style.display).toBe('none');
      expect(uiManager.textInput.style.display).toBe('block');
      expect(uiManager.inputGroup.classList.contains('text-mode')).toBe(true);
    });
  });

  describe('updateResults', () => {
    test('should update results display with data', () => {
      const data = {
        article_title: 'Test Article',
        locations: [{ name: 'Location 1' }, { name: 'Location 2' }],
        processing_time: 2.5,
      };

      uiManager.updateResults(data);

      expect(document.getElementById('articleTitle').textContent).toBe(
        'Test Article'
      );
      expect(document.getElementById('locationsCount').textContent).toBe(
        '2 locations found'
      );
      expect(document.getElementById('processingTime').textContent).toBe(
        'Processed in 2.50s'
      );
    });

    test('should use default title when not provided', () => {
      const data = {
        locations: [],
        processing_time: 1.0,
      };

      uiManager.updateResults(data);

      expect(document.getElementById('articleTitle').textContent).toBe(
        'Article'
      );
    });
  });

  describe('getCurrentInput', () => {
    test('should return URL input when in URL mode', () => {
      uiManager.urlInput.value = 'https://example.com';
      uiManager.urlInput.style.display = 'block';

      const result = uiManager.getCurrentInput();

      expect(result).toBe('https://example.com');
    });

    test('should return text input when in text mode', () => {
      uiManager.textInput.value = 'Sample article text';
      uiManager.urlInput.style.display = 'none';

      const result = uiManager.getCurrentInput();

      expect(result).toBe('Sample article text');
    });

    test('should throw error for empty URL input', () => {
      uiManager.urlInput.value = '';
      uiManager.urlInput.style.display = 'block';

      expect(() => uiManager.getCurrentInput()).toThrow(
        'Please enter a valid URL'
      );
    });

    test('should throw error for empty text input', () => {
      uiManager.textInput.value = '';
      uiManager.urlInput.style.display = 'none';

      expect(() => uiManager.getCurrentInput()).toThrow(
        'Please paste article text'
      );
    });
  });

  describe('setButtonLoading', () => {
    test('should disable button when loading', () => {
      uiManager.setButtonLoading(true);

      expect(uiManager.extractBtn.disabled).toBe(true);
    });

    test('should enable button when not loading', () => {
      uiManager.setButtonLoading(false);

      expect(uiManager.extractBtn.disabled).toBe(false);
    });
  });

  describe('validateInput', () => {
    test('should return true for valid URL input', () => {
      uiManager.urlInput.value = 'https://example.com';
      uiManager.urlInput.style.display = 'block';

      const result = uiManager.validateInput();

      expect(result).toBe(true);
    });

    test('should return true for valid text input', () => {
      uiManager.textInput.value = 'Sample text';
      uiManager.urlInput.style.display = 'none';

      const result = uiManager.validateInput();

      expect(result).toBe(true);
    });

    test('should return false and show error for empty URL', () => {
      uiManager.urlInput.value = '';
      uiManager.urlInput.style.display = 'block';

      const result = uiManager.validateInput();

      expect(result).toBe(false);
    });

    test('should return false and show error for empty text', () => {
      uiManager.textInput.value = '';
      uiManager.urlInput.style.display = 'none';

      const result = uiManager.validateInput();

      expect(result).toBe(false);
    });
  });
});
