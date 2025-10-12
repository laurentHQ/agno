# Finance News AgentOS - Web UI

A modern web interface for the Finance News AgentOS with markdown rendering support.

## 🌟 Features

- **📊 Market Overview** - Real-time market analysis with markdown formatting
- **🔍 Quick Stock Analysis** - Instant stock symbol analysis
- **💬 Custom Queries** - Ask any financial question
- **📝 Session Management** - View chat sessions
- **🎨 Markdown Rendering** - Beautiful formatting with syntax highlighting
- **📱 Responsive Design** - Works on desktop and mobile
- **⚡ Real-time Status** - Connection status monitoring

## 🚀 Quick Start

### Prerequisites

- Node.js 16+
- Finance News AgentOS running on `http://localhost:8080`

### Installation

```bash
# Navigate to the webui directory
cd webui

# Install dependencies
npm install

# Start the development server
npm run dev

# Or start production server
npm start
```

### Access

- **Web UI**: http://localhost:3000
- **Backend**: http://localhost:8080 (AgentOS)

## 🔧 Configuration

### Environment Variables

```bash
# .env file (optional)
PORT=3000
AGENTOS_URL=http://localhost:8080
```

### Backend Configuration

The web UI expects the Finance News AgentOS to be running with the following endpoints:

- `GET /health` - Health check
- `GET /agents` - List agents
- `GET /finance/quick-analysis?symbol=AAPL` - Quick stock analysis
- `GET /finance/market-overview` - Market overview
- `POST /agents/finance-news-agent/runs` - Custom queries
- `GET /sessions` - Chat sessions

## 📱 Usage

### Market Overview
1. Click the "📊 Market Overview" tab
2. Click "🔄 Refresh" to get latest market data
3. View beautifully formatted markdown content

### Quick Analysis
1. Click the "🔍 Quick Analysis" tab
2. Enter a stock symbol (e.g., AAPL, TSLA)
3. Click "Analyze" or press Enter
4. View detailed stock analysis

### Custom Queries
1. Click the "💬 Custom Query" tab
2. Type your financial question
3. Click "Send Query"
4. View AI-generated response with markdown formatting

### Sessions
1. Click the "📝 Sessions" tab
2. View all chat sessions
3. Click "🔄 Refresh" to update

## 🎨 Features

### Markdown Rendering
- Headers and subheaders
- Bullet points and lists
- **Bold** and *italic* text
- Code blocks with syntax highlighting
- Tables and blockquotes
- Links and images

### Responsive Design
- Mobile-friendly interface
- Adaptive navigation
- Touch-friendly buttons
- Optimized for all screen sizes

### Real-time Features
- Connection status indicator
- Loading animations
- Error handling
- Auto-refresh capabilities

## 🛠️ Development

### Project Structure

```
webui/
├── package.json          # Dependencies and scripts
├── server.js            # Express server with API proxy
├── public/
│   ├── index.html       # Main HTML file
│   ├── styles.css       # CSS styling
│   └── app.js          # Frontend JavaScript
└── README.md           # This file
```

### API Integration

The web UI acts as a proxy to the AgentOS backend:

```javascript
// Example API call
const response = await fetch('/api/finance/quick-analysis?symbol=AAPL');
const data = await response.json();

// Markdown rendering is handled server-side
if (data.analysisHtml) {
  container.innerHTML = data.analysisHtml;
}
```

### Styling

Uses modern CSS with:
- CSS custom properties (variables)
- Flexbox and Grid layouts
- Smooth animations
- Professional color scheme
- Mobile-first responsive design

## 🔍 Troubleshooting

### Common Issues

**Connection Error**
- Ensure AgentOS is running on port 8080
- Check if CORS is enabled on the backend
- Verify network connectivity

**Port Already in Use**
```bash
# Use different port
PORT=3001 npm start
```

**Missing Dependencies**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**API Errors**
- Check AgentOS logs
- Verify API endpoints are available
- Ensure proper API key configuration

### Debug Mode

Start with debug logging:
```bash
DEBUG=express:* npm start
```

## 📊 Performance

### Optimization Features
- Efficient markdown rendering with caching
- Lazy loading of tab content
- Debounced API calls
- Compressed assets
- Minimal dependencies

### Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🔐 Security

### Best Practices
- Input validation and sanitization
- CORS configuration
- No sensitive data in frontend
- Rate limiting protection
- XSS prevention with proper escaping

## 🚀 Deployment

### Production Deployment

```bash
# Install production dependencies
npm install --production

# Start production server
NODE_ENV=production npm start
```

### Docker Deployment

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📄 License

Part of the Finance News AgentOS project.

---

## 🔗 Related

- [Finance News AgentOS](../AGENTOS_README.md) - Main AgentOS documentation
- [Configuration Guide](../CONFIG_GUIDE.md) - AI model configuration
- [Agent Documentation](../agents/) - Finance agent details