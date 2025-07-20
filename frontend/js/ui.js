// UI state management module
class UIManager {
  constructor() {
    this.statusCard = document.getElementById('statusCard');
    this.loadingSection = document.getElementById('loadingSection');
    this.errorSection = document.getElementById('errorSection');
    this.resultsSection = document.getElementById('resultsSection');
    this.extractBtn = document.getElementById('extractBtn');
    this.urlInput = document.getElementById('urlInput');
    this.textInput = document.getElementById('textInput');
    this.inputGroup = document.getElementById('inputGroup');
  }

  // Show/hide status card and manage states
  showLoading() {
    this.statusCard.classList.add('show');
    this.loadingSection.style.display = 'block';
    this.errorSection.style.display = 'none';
    this.resultsSection.style.display = 'none';
  }

  showError(message) {
    this.statusCard.classList.add('show');
    this.loadingSection.style.display = 'none';
    this.errorSection.style.display = 'block';
    this.resultsSection.style.display = 'none';
    this.errorSection.textContent = message;
  }

  showResults() {
    this.statusCard.classList.add('show');
    this.loadingSection.style.display = 'none';
    this.errorSection.style.display = 'none';
    this.resultsSection.style.display = 'grid';
  }

  hideStatus() {
    this.statusCard.classList.remove('show');
  }

  hideResults() {
    this.statusCard.classList.remove('show');
    this.loadingSection.style.display = 'none';
    this.errorSection.style.display = 'none';
    this.resultsSection.style.display = 'none';
  }

  // Toggle between URL and text input modes
  toggleInputMode(mode) {
    const urlToggle = document.getElementById('urlToggle');
    const textToggle = document.getElementById('textToggle');

    if (mode === 'url') {
      urlToggle.classList.add('active');
      textToggle.classList.remove('active');
      this.urlInput.style.display = 'block';
      this.textInput.style.display = 'none';
      this.inputGroup.classList.remove('text-mode');
    } else {
      urlToggle.classList.remove('active');
      textToggle.classList.add('active');
      this.urlInput.style.display = 'none';
      this.textInput.style.display = 'block';
      this.inputGroup.classList.add('text-mode');
    }
  }

  // Update results UI
  updateResults(data) {
    document.getElementById('articleTitle').textContent =
      data.article_title || 'Article';
    document.getElementById('locationsCount').textContent =
      `${data.locations.length} locations found`;
    document.getElementById('processingTime').textContent =
      `Processed in ${data.processing_time.toFixed(2)}s`;
  }

  // Get current input value and mode
  getCurrentInput() {
    const isUrlMode = this.urlInput.style.display !== 'none';

    let input;
    if (isUrlMode) {
      input = this.urlInput.value.trim();
      if (!input) {
        throw new Error('Please enter a valid URL');
      }
    } else {
      input = this.textInput.value.trim();
      if (!input) {
        throw new Error('Please paste article text');
      }
    }

    return input;
  }

  // Set button loading state
  setButtonLoading(loading) {
    this.extractBtn.disabled = loading;
  }

  // Validate input
  validateInput() {
    const isUrlMode = this.urlInput.style.display !== 'none';

    if (isUrlMode) {
      const input = this.urlInput.value.trim();
      if (!input) {
        this.showError('Please enter a valid URL');
        return false;
      }
    } else {
      const input = this.textInput.value.trim();
      if (!input) {
        this.showError('Please paste article text');
        return false;
      }
    }

    return true;
  }
}

// Export for global use
window.UIManager = UIManager;
