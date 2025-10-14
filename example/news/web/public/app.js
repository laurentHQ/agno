// Finance News AgentOS Web UI JavaScript

class FinanceWebUI {
  constructor() {
    this.baseURL = '/api';
    this.backendURL = 'http://localhost:8080';
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.checkConnection();
    this.updateBackendURL();
  }

  setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-button').forEach(button => {
      button.addEventListener('click', () => this.switchTab(button.dataset.tab));
    });

    // Market overview
    document.getElementById('refresh-market').addEventListener('click', () => {
      this.fetchMarketOverview();
    });

    // Quick analysis
    document.getElementById('analyze-stock').addEventListener('click', () => {
      this.analyzeStock();
    });

    // Enter key for stock analysis
    document.getElementById('symbol-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.analyzeStock();
      }
    });

    // Custom query
    document.getElementById('send-query').addEventListener('click', () => {
      this.sendCustomQuery();
    });

    document.getElementById('clear-query').addEventListener('click', () => {
      document.getElementById('custom-message').value = '';
      document.getElementById('query-result').innerHTML = '';
    });

    // Sessions
    document.getElementById('refresh-sessions').addEventListener('click', () => {
      this.fetchSessions();
    });
  }

  updateBackendURL() {
    document.getElementById('backend-url').textContent = this.backendURL;
  }

  async checkConnection() {
    const statusElement = document.getElementById('connection-status');

    try {
      const response = await fetch(`${this.baseURL}/health`);
      if (response.ok) {
        statusElement.textContent = '🟢 Connected';
        statusElement.className = 'status-connected';
      } else {
        throw new Error('Health check failed');
      }
    } catch (error) {
      statusElement.textContent = '🔴 Connection Error';
      statusElement.className = 'status-error';
      console.error('Connection check failed:', error);
    }
  }

  switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
      button.classList.remove('active');
    });

    // Show selected tab content
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Load data for the selected tab
    switch (tabName) {
      case 'market-overview':
        this.fetchMarketOverview();
        break;
      case 'sessions':
        this.fetchSessions();
        break;
    }
  }

  showLoading(loadingId) {
    document.getElementById(loadingId).classList.remove('hidden');
  }

  hideLoading(loadingId) {
    document.getElementById(loadingId).classList.add('hidden');
  }

  renderContent(containerId, content, metadata = {}) {
    const container = document.getElementById(containerId);

    let html = '';

    if (content) {
      html += `<div class="markdown-content">${content}</div>`;
    }

    if (Object.keys(metadata).length > 0) {
      html += '<div class="metadata">';
      Object.entries(metadata).forEach(([key, value]) => {
        if (value) {
          html += `<span><strong>${this.formatKey(key)}:</strong> ${value}</span>`;
        }
      });
      html += '</div>';
    }

    container.innerHTML = html;

    // Highlight code blocks
    container.querySelectorAll('pre code').forEach(block => {
      hljs.highlightElement(block);
    });
  }

  renderError(containerId, error, details = '') {
    const container = document.getElementById(containerId);
    container.innerHTML = `
      <div class="error-message">
        <strong>Error: ${error}</strong>
        ${details ? `<div>${details}</div>` : ''}
      </div>
    `;
  }

  formatKey(key) {
    return key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
  }

  formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  }

  async fetchMarketOverview() {
    this.showLoading('market-loading');

    try {
      const response = await fetch(`${this.baseURL}/finance/market-overview`);
      const data = await response.json();

      if (response.ok) {
        if (data.error) {
          this.renderError('market-result', data.error);
        } else {
          this.renderContent('market-result', data.analysisHtml || data.analysis, {
            timestamp: this.formatTimestamp(data.timestamp)
          });
        }
      } else {
        throw new Error(data.error || 'Failed to fetch market overview');
      }
    } catch (error) {
      this.renderError('market-result', 'Failed to fetch market overview', error.message);
    } finally {
      this.hideLoading('market-loading');
    }
  }

  async analyzeStock() {
    const symbol = document.getElementById('symbol-input').value.trim().toUpperCase();

    if (!symbol) {
      this.renderError('analysis-result', 'Please enter a stock symbol');
      return;
    }

    document.getElementById('analyzing-symbol').textContent = symbol;
    this.showLoading('analysis-loading');

    try {
      const response = await fetch(`${this.baseURL}/finance/quick-analysis?symbol=${encodeURIComponent(symbol)}`);
      const data = await response.json();

      if (response.ok) {
        if (data.error) {
          this.renderError('analysis-result', data.error);
        } else {
          this.renderContent('analysis-result', data.analysisHtml || data.analysis, {
            symbol: data.symbol,
            timestamp: this.formatTimestamp(data.timestamp)
          });
        }
      } else {
        throw new Error(data.error || 'Failed to analyze stock');
      }
    } catch (error) {
      this.renderError('analysis-result', `Failed to analyze ${symbol}`, error.message);
    } finally {
      this.hideLoading('analysis-loading');
    }
  }

  async sendCustomQuery() {
    const message = document.getElementById('custom-message').value.trim();

    if (!message) {
      this.renderError('query-result', 'Please enter a query');
      return;
    }

    this.showLoading('query-loading');

    try {
      // Create FormData for multipart/form-data request
      const formData = new FormData();
      formData.append('message', message);

      const response = await fetch(`${this.baseURL}/agents/finance-news-agent/runs`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        if (data.error) {
          this.renderError('query-result', data.error);
        } else {
          this.renderContent('query-result', data.contentHtml || data.content, {
            timestamp: this.formatTimestamp(data.created_at || data.timestamp)
          });
        }
      } else {
        throw new Error(data.error || 'Failed to process query');
      }
    } catch (error) {
      this.renderError('query-result', 'Failed to process query', error.message);
    } finally {
      this.hideLoading('query-loading');
    }
  }

  async fetchSessions() {
    this.showLoading('sessions-loading');

    try {
      const response = await fetch(`${this.baseURL}/sessions`);
      const data = await response.json();

      if (response.ok) {
        // API returns paginated response with data and meta fields
        const sessions = data.data || [];
        this.renderSessions('sessions-result', sessions, data.meta);
      } else {
        throw new Error(data.error || 'Failed to fetch sessions');
      }
    } catch (error) {
      this.renderError('sessions-result', 'Failed to fetch sessions', error.message);
    } finally {
      this.hideLoading('sessions-loading');
    }
  }

  renderSessions(containerId, sessions, meta = null) {
    const container = document.getElementById(containerId);

    if (!sessions || sessions.length === 0) {
      container.innerHTML = '<div class="result-container empty">No sessions found</div>';
      return;
    }

    let html = '';

    // Add pagination info if available
    if (meta) {
      html += `
        <div class="metadata" style="margin-bottom: 15px;">
          <span><strong>Total Sessions:</strong> ${meta.total_count || 0}</span>
          <span><strong>Page:</strong> ${meta.page || 1} of ${meta.total_pages || 1}</span>
          <span><strong>Showing:</strong> ${sessions.length} sessions</span>
        </div>
      `;
    }

    sessions.forEach((session, index) => {
      html += `
        <div class="session-item">
          <div class="session-header">${session.session_name || `Session ${index + 1}`}</div>
          <div><strong>ID:</strong> ${session.session_id || session.id || 'N/A'}</div>
          <div><strong>Created:</strong> ${this.formatTimestamp(session.created_at)}</div>
          <div><strong>Updated:</strong> ${this.formatTimestamp(session.updated_at)}</div>
        </div>
      `;
    });

    container.innerHTML = html;
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new FinanceWebUI();
});