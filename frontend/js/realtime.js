// Real-time progress updates using Server-Sent Events
class RealtimeClient {
  constructor() {
    this.eventSource = null;
    this.callbacks = {};
    this.isConnected = false;
  }

  // Connect to SSE stream for a session
  connect(sessionId) {
    if (this.eventSource) {
      this.disconnect();
    }

    const url = `/api/progress/${sessionId}`;
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      console.log('Progress stream connected');
      this.isConnected = true;
      this.triggerCallback('connected', { sessionId });
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Skip heartbeat messages
        if (data.heartbeat) {
          return;
        }

        console.log('Progress update:', data);

        // Trigger status-specific callbacks
        if (data.status && this.callbacks[data.status]) {
          this.callbacks[data.status](data);
        }

        // Trigger general progress callback
        this.triggerCallback('progress', data);

        // Auto-disconnect on completion or error
        if (data.status === 'complete' || data.status === 'error') {
          setTimeout(() => this.disconnect(), 1000);
        }
      } catch (error) {
        console.error('Error parsing progress data:', error);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('Progress stream error:', error);
      this.isConnected = false;

      // Only trigger error if we haven't completed successfully
      if (this.eventSource.readyState === EventSource.CLOSED) {
        console.log('SSE connection closed normally');
      } else {
        this.triggerCallback('error', { error: 'Connection lost' });
      }
    };
  }

  // Disconnect from SSE stream
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.isConnected = false;
      console.log('Progress stream disconnected');
    }
  }

  // Register callback for specific status or event
  on(event, callback) {
    this.callbacks[event] = callback;
  }

  // Remove callback
  off(event) {
    delete this.callbacks[event];
  }

  // Trigger callback if it exists
  triggerCallback(event, data) {
    if (this.callbacks[event]) {
      this.callbacks[event](data);
    }
  }
}

// Progress UI Manager
class ProgressUI {
  constructor() {
    this.progressContainer = null;
    this.progressBar = null;
    this.statusText = null;
    this.detailsText = null;
    this.currentStep = null;

    this.initProgressUI();
  }

  initProgressUI() {
    // Create progress UI elements if they don't exist
    if (!document.getElementById('progressContainer')) {
      this.createProgressHTML();
    }

    this.progressContainer = document.getElementById('progressContainer');
    this.progressBar = document.getElementById('progressBar');
    this.statusText = document.getElementById('statusText');
    this.detailsText = document.getElementById('detailsText');
    this.currentStep = document.getElementById('currentStep');
  }

  createProgressHTML() {
    const progressHTML = `
            <div id="progressContainer" class="progress-container" style="display: none;">
                <div class="progress-header">
                    <h3 id="statusText">Processing...</h3>
                    <div class="progress-bar-container">
                        <div id="progressBar" class="progress-bar"></div>
                    </div>
                </div>
                <div class="progress-details">
                    <div id="currentStep" class="current-step"></div>
                    <div id="detailsText" class="details-text"></div>
                </div>
            </div>
        `;

    // Insert after the input card
    const inputCard = document.querySelector('.input-card');
    if (inputCard) {
      inputCard.insertAdjacentHTML('afterend', progressHTML);
    }
  }

  show() {
    if (this.progressContainer) {
      this.progressContainer.style.display = 'block';
      this.progressContainer.classList.add('show');
    }
  }

  hide() {
    if (this.progressContainer) {
      this.progressContainer.style.display = 'none';
      this.progressContainer.classList.remove('show');
    }
  }

  updateProgress(data) {
    const {
      status,
      message,
      progress_percent,
      current_item,
      current_index,
      total_items,
    } = data;

    // Update progress bar
    if (this.progressBar && progress_percent !== undefined) {
      this.progressBar.style.width = `${progress_percent}%`;
    }

    // Update status text
    if (this.statusText && message) {
      this.statusText.textContent = message;
    }

    // Update current step with status-specific styling
    if (this.currentStep) {
      this.currentStep.textContent = this.getStepDescription(status);
      this.currentStep.className = `current-step step-${status}`;
    }

    // Update details text
    if (this.detailsText) {
      let details = '';

      if (current_item) {
        details = `Current: ${current_item}`;
      }

      // Progress counter removed - showing only current item if available

      this.detailsText.textContent = details;
    }
  }

  getStepDescription(status) {
    const steps = {
      starting: '🔄 Initializing...',
      extracting_article: '📄 Extracting article content',
      extracting_locations: '🌍 Finding locations',
      processing_locations: '📍 Processing locations',
      filtering: '🔍 Filtering results',
      complete: '✅ Complete!',
      error: '❌ Error occurred',
    };

    return steps[status] || status;
  }

  showError(message) {
    this.show();
    if (this.statusText) {
      this.statusText.textContent = `Error: ${message}`;
      this.statusText.className = 'status-error';
    }
    if (this.currentStep) {
      this.currentStep.textContent = '❌ Processing failed';
      this.currentStep.className = 'current-step step-error';
    }
    if (this.detailsText) {
      this.detailsText.textContent = message;
    }
  }

  showComplete(data) {
    if (this.statusText) {
      this.statusText.textContent = data.message || 'Processing complete!';
      this.statusText.className = 'status-complete';
    }

    // Auto-hide after success
    setTimeout(() => {
      this.hide();
    }, 2000);
  }
}
