# Finance News Agent - GCP Deployment Guide

**Cost-Optimized E2-micro Deployment for Personal Use**

This guide helps you deploy the Finance News Agent on Google Cloud Platform using an E2-micro instance with manual start/stop control for maximum cost efficiency.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Cost Breakdown](#cost-breakdown)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Management](#management)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)

---

## 🎯 Overview

### Architecture

```
Windows PC (PowerShell 7.5)
    ↓
Google Cloud Platform
    ↓
E2-micro Instance (1GB RAM, 0.25-2 vCPU)
    ↓
Finance News Agent (Agno + FastAPI)
    ↓
SQLite Database (Local Storage)
```

### Why E2-micro?

✅ **Perfect resource match** - 1 GB RAM handles agent's 400-600 MB usage
✅ **Cost-effective** - $7.11/month ($0.90 with free tier)
✅ **Free tier eligible** - First instance FREE for 12 months
✅ **Manual control** - Start/stop as needed for usage windows
✅ **No cold starts** - Unlike Cloud Run, no startup delay

### Features

- 🚀 **One-command deployment** - Automated setup scripts
- 💰 **Cost optimized** - Pay only when running (~$1/month for 2 hours/day)
- 🔐 **Secure** - Environment-based API key management
- 📊 **Full-featured** - Market data, news, crypto, sector analysis
- 🗄️ **Persistent** - SQLite database for session history
- 🎮 **Easy management** - PowerShell scripts for control

---

## 📦 Prerequisites

### Required Software

1. **PowerShell 7.5** (Windows)
   ```powershell
   # Check version
   $PSVersionTable.PSVersion
   # Should show 7.5.x
   ```
   Download: https://github.com/PowerShell/PowerShell/releases

2. **Google Cloud SDK (gcloud)**
   ```powershell
   # Check installation
   gcloud --version
   ```
   Download: https://cloud.google.com/sdk/docs/install

3. **GCP Account**
   - Free tier eligible: https://cloud.google.com/free
   - Billing account enabled

### Required API Keys

**Required (choose one):**
- **OpenAI API Key** - https://platform.openai.com/api-keys
- **Anthropic API Key** - https://console.anthropic.com/

**Optional (enhanced features):**
- **Tavily API Key** - https://tavily.com/ (for advanced search)

### Environment Setup

```powershell
# Set API keys in PowerShell
$env:OPENAI_API_KEY = "sk-..."
# OR
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Optional
$env:TAVILY_API_KEY = "tvly-..."

# Make permanent (add to PowerShell profile)
notepad $PROFILE
# Add the export commands above
```

---

## 💰 Cost Breakdown

### Monthly Costs

| Component | Cost | Notes |
|-----------|------|-------|
| E2-micro instance | $7.11/month | **FREE with free tier (12 months)** |
| 10GB Disk Storage | $0.40/month | Charged even when stopped |
| Network Egress | ~$0.50/month | Minimal for personal use |
| **Total (running 24/7)** | **$8.01/month** | **$0.90 with free tier** |

### Usage-Based Costs (with manual start/stop)

| Usage Pattern | Monthly Cost | With Free Tier |
|---------------|--------------|----------------|
| 2 hours/day (60 hrs/month) | $1.49 | **$0.99** |
| 4 hours/day (120 hrs/month) | $2.58 | **$1.48** |
| 8 hours/day (240 hrs/month) | $4.75 | **$2.75** |
| Always on (730 hrs/month) | $8.01 | **$0.90** |

**Cost Formula:** Compute ($0.0098/hour × hours) + Disk ($0.40) + Network (~$0.50)

### Free Tier Benefits

- ✅ 1 e2-micro instance in us-central1, us-east1, or us-west1
- ✅ 30 GB-month standard persistent disk
- ✅ 1 GB network egress (North America)
- ⏱️ Duration: 12 months from signup

---

## 🚀 Quick Start

### Step 1: Clone Repository

```powershell
cd C:\Users\YourName\Projects
git clone <your-agno-repo-url>
cd agno\example\news\deploy\gcp
```

### Step 2: Create GCP Instance

```powershell
# Run instance creation script
.\01-create-instance.ps1 -ProjectId "your-gcp-project-id"

# Wait for completion (~2 minutes)
# ✅ Instance created: finance-news-agent
```

### Step 3: Deploy Application

```powershell
# Deploy agent to instance (uses environment API keys)
.\02-deploy-agent.ps1

# Or specify API key directly
.\02-deploy-agent.ps1 -OpenAIKey "sk-..."

# Wait for completion (~3 minutes)
# ✅ Agent deployed and running
```

### Step 4: Access Your Agent

```powershell
# Get agent URL
.\03-manage-instance.ps1 url

# Output:
# 🌐 http://35.123.45.67:7777
```

Open in browser: `http://YOUR_IP:7777`

**Done! Your Finance News Agent is running! 🎉**

---

## 📚 Detailed Setup

### 1. GCP Project Setup

#### Create GCP Project (if needed)

```powershell
# List projects
gcloud projects list

# Create new project
gcloud projects create finance-agent-project --name="Finance Agent"

# Set as active
gcloud config set project finance-agent-project

# Enable billing
# Go to: https://console.cloud.google.com/billing
```

#### Enable Required APIs

```powershell
gcloud services enable compute.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Instance Creation

**Script:** `01-create-instance.ps1`

```powershell
# Basic usage
.\01-create-instance.ps1 -ProjectId "your-project-id"

# Custom zone (for free tier)
.\01-create-instance.ps1 -ProjectId "your-project-id" -Zone "us-east1-b"

# Custom instance name
.\01-create-instance.ps1 -ProjectId "your-project-id" -InstanceName "my-finance-agent"
```

**What it does:**
1. ✅ Creates E2-micro instance in free tier zone
2. ✅ Configures 10GB disk storage
3. ✅ Sets up firewall rules (port 7777)
4. ✅ Installs Python 3.11 and dependencies
5. ✅ Creates application directories
6. ✅ Saves configuration for other scripts

**Output:**
```
✅ Instance created: finance-news-agent
📋 External IP: 35.123.45.67
💰 Monthly cost: $0.90 (with free tier)
```

### 3. Application Deployment

**Script:** `02-deploy-agent.ps1`

```powershell
# Deploy with environment variables
.\02-deploy-agent.ps1

# Deploy with explicit API key
.\02-deploy-agent.ps1 -OpenAIKey "sk-..."

# Deploy with Anthropic (Claude)
.\02-deploy-agent.ps1 -AnthropicKey "sk-ant-..."

# Deploy with all features
.\02-deploy-agent.ps1 -OpenAIKey "sk-..." -TavilyKey "tvly-..."
```

**What it does:**
1. ✅ Uploads application code to instance
2. ✅ Creates Python virtual environment
3. ✅ Installs dependencies (agno, openai, yfinance, etc.)
4. ✅ Configures environment variables
5. ✅ Creates systemd service
6. ✅ Starts agent service
7. ✅ Creates management scripts on instance

**Output:**
```
✅ Deployment complete!
🌐 Agent URL: http://35.123.45.67:7777
📚 API Docs: http://35.123.45.67:7777/docs
```

### 4. Verification

```powershell
# Check status
.\03-manage-instance.ps1 status

# View logs
.\03-manage-instance.ps1 logs

# Get URL
.\03-manage-instance.ps1 url
```

---

## 🎮 Management

### Management Script

**Script:** `03-manage-instance.ps1`

All commands:

```powershell
# Start instance and agent
.\03-manage-instance.ps1 start

# Stop agent and instance
.\03-manage-instance.ps1 stop

# Restart agent service
.\03-manage-instance.ps1 restart

# Check status
.\03-manage-instance.ps1 status

# SSH into instance
.\03-manage-instance.ps1 ssh

# View logs
.\03-manage-instance.ps1 logs

# Show access URLs
.\03-manage-instance.ps1 url

# Cost estimate
.\03-manage-instance.ps1 cost

# Help
.\03-manage-instance.ps1 help
```

### Daily Workflow

**Start your work session:**
```powershell
# Morning: Start agent
.\03-manage-instance.ps1 start
# Wait 30 seconds for startup

# Get URL and open in browser
.\03-manage-instance.ps1 url
```

**End your work session:**
```powershell
# Evening: Stop to save costs
.\03-manage-instance.ps1 stop
# Saves ~$0.29/day in compute costs
```

### On-Instance Management

If you SSH into the instance:

```bash
# Start agent
/opt/finance-agent/start.sh

# Stop agent
/opt/finance-agent/stop.sh

# Check status
/opt/finance-agent/status.sh

# View logs
tail -f /opt/finance-agent/logs/agent.log

# Restart systemd service
sudo systemctl restart finance-agent
```

---

## 🔧 Troubleshooting

### Agent Not Responding

**Check status:**
```powershell
.\03-manage-instance.ps1 status
```

**Check logs:**
```powershell
.\03-manage-instance.ps1 logs
```

**Common issues:**

1. **API key not set**
   ```powershell
   # SSH into instance
   .\03-manage-instance.ps1 ssh

   # Check environment
   cat /opt/finance-agent/.env

   # Update key
   nano /opt/finance-agent/.env
   # Add: OPENAI_API_KEY=sk-...

   # Restart
   sudo systemctl restart finance-agent
   ```

2. **Port 7777 blocked**
   ```powershell
   # Check firewall
   gcloud compute firewall-rules list

   # Recreate rule
   gcloud compute firewall-rules create allow-finance-agent \
     --allow=tcp:7777 \
     --target-tags=finance-agent
   ```

3. **Service not starting**
   ```powershell
   # SSH and check logs
   .\03-manage-instance.ps1 ssh
   sudo journalctl -u finance-agent -n 50
   ```

### Instance Won't Start

```powershell
# Check quota
gcloud compute project-info describe --project=your-project-id

# Check status
gcloud compute instances describe finance-news-agent \
  --zone=us-central1-a

# Force restart
gcloud compute instances reset finance-news-agent \
  --zone=us-central1-a
```

### Connection Timeout

```powershell
# Check external IP
gcloud compute instances describe finance-news-agent \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Test connectivity
Test-NetConnection -ComputerName YOUR_IP -Port 7777

# Check firewall
gcloud compute firewall-rules describe allow-finance-agent
```

### Database Issues

```bash
# SSH into instance
.\03-manage-instance.ps1 ssh

# Check database
sqlite3 /opt/finance-agent/data/finance_agent.db ".tables"

# Reset database (CAREFUL - deletes history)
rm /opt/finance-agent/data/finance_agent.db
sudo systemctl restart finance-agent
```

---

## 💡 Cost Optimization

### Best Practices

1. **Stop when not in use**
   ```powershell
   # Stop every evening
   .\03-manage-instance.ps1 stop
   # Saves: $0.0098/hour = $0.24/day
   ```

2. **Schedule automation** (optional)
   ```powershell
   # Create scheduled task in Windows
   # Task: Run at 6 AM daily
   .\03-manage-instance.ps1 start

   # Task: Run at 10 PM daily
   .\03-manage-instance.ps1 stop
   ```

3. **Monitor usage**
   ```powershell
   # Check cost estimate
   .\03-manage-instance.ps1 cost

   # GCP Console billing
   # https://console.cloud.google.com/billing
   ```

4. **Free tier optimization**
   - Use us-central1, us-east1, or us-west1 zones
   - Keep total usage <730 hours/month (always-on)
   - Monitor free tier limits

### Cost Tracking

```powershell
# Weekly cost check
gcloud billing projects describe your-project-id

# Set budget alert (in GCP Console)
# Billing > Budgets & alerts
# Set alert at $5/month
```

---

## 🔐 Security Best Practices

1. **API Keys**
   - Never commit .env files to git
   - Use environment variables
   - Rotate keys regularly

2. **Firewall**
   - Only port 7777 exposed
   - Consider IP whitelisting for production

3. **SSH Access**
   - Use gcloud SSH (automatic key management)
   - Enable OS Login for team access

4. **Updates**
   ```bash
   # SSH into instance monthly
   sudo apt update && sudo apt upgrade -y
   ```

---

## 📊 Monitoring

### Instance Metrics

```powershell
# GCP Console Monitoring
# https://console.cloud.google.com/compute/instances

# CLI monitoring
gcloud compute instances get-serial-port-output \
  finance-news-agent --zone=us-central1-a
```

### Application Logs

```powershell
# View logs locally
.\03-manage-instance.ps1 logs

# Or SSH and tail logs
.\03-manage-instance.ps1 ssh
tail -f /opt/finance-agent/logs/agent.log
```

### Set up Alerts (Optional)

```bash
# Create uptime check (GCP Console)
# Monitoring > Uptime Checks
# URL: http://YOUR_IP:7777/health
# Frequency: 5 minutes
```

---

## 🆘 Support & Resources

### Documentation
- [Agno Framework](https://docs.agno.com)
- [GCP Compute Engine](https://cloud.google.com/compute/docs)
- [PowerShell 7.5](https://docs.microsoft.com/powershell)

### Useful Commands

```powershell
# List all instances
gcloud compute instances list

# Get instance info
gcloud compute instances describe finance-news-agent --zone=us-central1-a

# View billing
gcloud billing accounts list

# SSH with port forwarding (access from localhost)
gcloud compute ssh finance-news-agent \
  --zone=us-central1-a \
  --ssh-flag="-L 7777:localhost:7777"
# Access at: http://localhost:7777
```

---

## 🎓 Next Steps

1. **Customize agent**
   - Edit prompts in `src/agents/prompts/finance_news_prompt.py`
   - Add tools in `src/agents/tools/finance_tools.py`

2. **Upgrade instance** (if needed)
   - Stop instance
   - Change machine type to e2-small or e2-medium
   - Restart instance

3. **Add monitoring**
   - Set up Cloud Monitoring
   - Configure alerts
   - Enable logging

4. **Scale up** (future)
   - Migrate to Cloud Run for auto-scaling
   - Add Cloud SQL for multi-device access
   - Set up load balancing

---

## 📝 License

Finance News Agent deployment scripts are provided as-is for personal use.

---

**Happy Analyzing! 💰📊**

*Remember: This is not financial advice. Always do your own research.*
