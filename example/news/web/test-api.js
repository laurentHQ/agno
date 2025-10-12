// Simple test script for Web UI API endpoints
const axios = require('axios');

const BASE_URL = 'http://localhost:3000/api';
const AGENTOS_URL = 'http://localhost:8080';

async function testEndpoints() {
  console.log('🧪 Testing Finance AgentOS Web UI API endpoints...\n');

  const tests = [
    {
      name: 'Health Check',
      url: `${BASE_URL}/health`,
      method: 'GET'
    },
    {
      name: 'Quick Analysis (AAPL)',
      url: `${BASE_URL}/finance/quick-analysis?symbol=AAPL`,
      method: 'GET'
    },
    {
      name: 'Market Overview',
      url: `${BASE_URL}/finance/market-overview`,
      method: 'GET'
    },
    {
      name: 'Agents List',
      url: `${BASE_URL}/agents`,
      method: 'GET'
    }
  ];

  for (const test of tests) {
    try {
      console.log(`Testing: ${test.name}`);
      const response = await axios({
        method: test.method,
        url: test.url,
        timeout: 10000
      });

      if (response.status === 200) {
        console.log(`✅ ${test.name}: OK`);

        // Check for markdown content
        if (response.data.analysisHtml) {
          console.log(`   📝 Markdown rendered: ${response.data.analysisHtml.length} chars`);
        }
        if (response.data.overviewHtml) {
          console.log(`   📝 Markdown rendered: ${response.data.overviewHtml.length} chars`);
        }
      } else {
        console.log(`⚠️  ${test.name}: Status ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ ${test.name}: ${error.message}`);
    }
    console.log('');
  }

  console.log('🎯 Test Summary:');
  console.log('- Web UI should be accessible at http://localhost:3000');
  console.log('- AgentOS should be running at http://localhost:8080');
  console.log('- All endpoints should return proper JSON responses');
  console.log('- Markdown content should be rendered to HTML');
}

if (require.main === module) {
  testEndpoints().catch(console.error);
}

module.exports = { testEndpoints };