const express = require('express');
const path = require('path');
const axios = require('axios');
const { marked } = require('marked');
const hljs = require('highlight.js');
const cors = require('cors');
const multer = require('multer');

const app = express();
const PORT = process.env.PORT || 3000;
const AGENTOS_URL = process.env.AGENTOS_URL || 'http://localhost:8080';

// Configure multer for handling multipart/form-data
const upload = multer();

// Configure marked for better markdown rendering
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {}
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Helper function to render markdown
function renderMarkdown(text) {
  if (!text) return '';
  return marked(text);
}

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API proxy endpoints
app.get('/api/health', async (req, res) => {
  try {
    const response = await axios.get(`${AGENTOS_URL}/health`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch health status', details: error.message });
  }
});

app.get('/api/agents', async (req, res) => {
  try {
    const response = await axios.get(`${AGENTOS_URL}/agents`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch agents', details: error.message });
  }
});

app.get('/api/finance/quick-analysis', async (req, res) => {
  try {
    const symbol = req.query.symbol || 'SPY';
    const response = await axios.get(`${AGENTOS_URL}/finance/quick-analysis?symbol=${symbol}`);

    // Render markdown if analysis is present
    if (response.data.analysis) {
      response.data.analysisHtml = renderMarkdown(response.data.analysis);
    }

    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch quick analysis', details: error.message });
  }
});

app.get('/api/finance/market-overview', async (req, res) => {
  try {
    const response = await axios.get(`${AGENTOS_URL}/finance/market-overview`);

    // Render markdown if analysis is present
    if (response.data.analysis) {
      response.data.analysisHtml = renderMarkdown(response.data.analysis);
    }

    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch market overview', details: error.message });
  }
});

app.post('/api/agents/:agentName/runs', upload.none(), async (req, res) => {
  try {
    const { agentName } = req.params;
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Create FormData for multipart/form-data request
    const FormData = require('form-data');
    const formData = new FormData();
    formData.append('message', message);

    const response = await axios.post(`${AGENTOS_URL}/agents/${agentName}/runs`, formData, {
      headers: {
        ...formData.getHeaders()
      }
    });

    // Render markdown if content is present
    if (response.data.content) {
      response.data.contentHtml = renderMarkdown(response.data.content);
    }

    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to run agent', details: error.message });
  }
});

// Sessions endpoint
app.get('/api/sessions', async (req, res) => {
  try {
    const response = await axios.get(`${AGENTOS_URL}/sessions`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch sessions', details: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log('🌐 Finance AgentOS Web UI Starting...');
  console.log('='.repeat(50));
  console.log(`📱 Web UI: http://localhost:${PORT}`);
  console.log(`🔗 AgentOS Backend: ${AGENTOS_URL}`);
  console.log('='.repeat(50));
  console.log('✅ Server ready! Access the web interface above.');
});