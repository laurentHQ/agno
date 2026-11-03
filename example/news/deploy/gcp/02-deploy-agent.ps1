# Finance News Agent - Application Deployment Script
# PowerShell 7.5 Script for Windows
# ============================================

<#
.SYNOPSIS
    Deploys the Finance News Agent application to GCP E2-micro instance

.DESCRIPTION
    This script uploads the Finance News Agent codebase to the GCP instance,
    installs dependencies, configures the environment, and sets up systemd service.

    Prerequisites:
    - Instance must be created (run 01-create-instance.ps1 first)
    - OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable set

.PARAMETER ProjectId
    Your GCP Project ID

.PARAMETER Zone
    GCP Zone where instance is located

.PARAMETER InstanceName
    Name of the compute instance

.PARAMETER OpenAIKey
    OpenAI API Key (required - or use AnthropicKey, reads from environment if not provided)

.PARAMETER AnthropicKey
    Anthropic API Key (required - or use OpenAIKey, reads from environment if not provided)

.PARAMETER TavilyKey
    Tavily API Key for advanced search (required, reads from environment if not provided)

.PARAMETER BraveKey
    Brave Search API Key (required, reads from environment if not provided)

.EXAMPLE
    # Using environment variables (recommended)
    $env:OPENAI_API_KEY = "sk-..."
    $env:TAVILY_API_KEY = "tvly-..."
    $env:BRAVE_API_KEY = "BSA..."
    .\02-deploy-agent.ps1 -ProjectId "my-project-123"

.EXAMPLE
    # Using command-line parameters
    .\02-deploy-agent.ps1 -OpenAIKey "sk-..." -TavilyKey "tvly-..." -BraveKey "BSA..."
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId,

    [Parameter(Mandatory=$false)]
    [string]$Zone,

    [Parameter(Mandatory=$false)]
    [string]$InstanceName,

    [Parameter(Mandatory=$false)]
    [string]$OpenAIKey = $env:OPENAI_API_KEY,

    [Parameter(Mandatory=$false)]
    [string]$AnthropicKey = $env:ANTHROPIC_API_KEY,

    [Parameter(Mandatory=$false)]
    [string]$TavilyKey = $env:TAVILY_API_KEY,

    [Parameter(Mandatory=$false)]
    [string]$BraveKey = $env:BRAVE_API_KEY
)

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

# ==============================================================================
# Helper Functions
# ==============================================================================

function Write-StepHeader {
    param([string]$Message)
    Write-Host "`n$('=' * 80)" -ForegroundColor $ColorInfo
    Write-Host "  $Message" -ForegroundColor $ColorInfo
    Write-Host "$('=' * 80)`n" -ForegroundColor $ColorInfo
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $ColorSuccess
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $ColorInfo
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $ColorWarning
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ColorError
}

# ==============================================================================
# Load Configuration
# ==============================================================================

Write-StepHeader "Finance News Agent - Application Deployment"

$configPath = Join-Path $PSScriptRoot "instance-config.json"

if (Test-Path $configPath) {
    Write-Info "Loading configuration from instance-config.json..."
    $config = Get-Content $configPath | ConvertFrom-Json

    if (-not $ProjectId) { $ProjectId = $config.ProjectId }
    if (-not $Zone) { $Zone = $config.Zone }
    if (-not $InstanceName) { $InstanceName = $config.InstanceName }

    Write-Success "Configuration loaded"
}

# Validate required parameters
if (-not $ProjectId -or -not $Zone -or -not $InstanceName) {
    Write-ErrorMsg "Missing required parameters!"
    Write-Info "Either run 01-create-instance.ps1 first, or provide:"
    Write-Info "  -ProjectId, -Zone, -InstanceName"
    exit 1
}

# Validate API keys - All are mandatory
$missingKeys = @()

if (-not $OpenAIKey -and -not $AnthropicKey) {
    $missingKeys += "OPENAI_API_KEY or ANTHROPIC_API_KEY (at least one required)"
}
if (-not $TavilyKey) {
    $missingKeys += "TAVILY_API_KEY"
}
if (-not $BraveKey) {
    $missingKeys += "BRAVE_API_KEY"
}

if ($missingKeys.Count -gt 0) {
    Write-ErrorMsg "Missing required API keys!"
    Write-Host ""
    Write-Host "Missing keys:" -ForegroundColor Yellow
    foreach ($key in $missingKeys) {
        Write-Host "  ❌ $key" -ForegroundColor Red
    }
    Write-Host ""
    Write-Info "Set environment variables:"
    Write-Info '  $env:OPENAI_API_KEY = "sk-..."          # OR Anthropic'
    Write-Info '  $env:ANTHROPIC_API_KEY = "sk-ant-..."   # OR OpenAI'
    Write-Info '  $env:TAVILY_API_KEY = "tvly-..."        # Required'
    Write-Info '  $env:BRAVE_API_KEY = "BSA..."           # Required'
    Write-Host ""
    Write-Info "Or provide as parameters:"
    Write-Info '  .\02-deploy-agent.ps1 -OpenAIKey "sk-..." -TavilyKey "tvly-..." -BraveKey "BSA..."'
    Write-Host ""
    Write-Info "Get API keys from:"
    Write-Info "  • OpenAI:   https://platform.openai.com/api-keys"
    Write-Info "  • Anthropic: https://console.anthropic.com/"
    Write-Info "  • Tavily:   https://tavily.com/"
    Write-Info "  • Brave:    https://brave.com/search/api/"
    exit 1
}

# Determine which model to use
$ModelChoice = if ($OpenAIKey) { "openai" } else { "anthropic" }
Write-Success "API keys validated"
Write-Info "Using $ModelChoice model for agent"

# ==============================================================================
# Prepare Application Files
# ==============================================================================

Write-StepHeader "Preparing Application Files"

# Find the news agent directory
$newsDir = Resolve-Path (Join-Path $PSScriptRoot "../../")
Write-Info "Source directory: $newsDir"

# Create temporary deployment directory
$tempDir = Join-Path $env:TEMP "finance-agent-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Write-Info "Temporary directory: $tempDir"

# Copy necessary files
Write-Info "Copying application files..."
$filesToCopy = @(
    "src",
    "pyproject.toml",
    "README_NEW_STRUCTURE.md"
)

foreach ($item in $filesToCopy) {
    $sourcePath = Join-Path $newsDir $item
    $destPath = Join-Path $tempDir $item

    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
        Write-Success "Copied: $item"
    }
    else {
        Write-Warning "Not found: $item"
    }
}

# Create .env file
Write-Info "Creating environment configuration..."
$envContent = @"
# Finance News Agent - Environment Configuration
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# AI Model Configuration
OPENAI_API_KEY=$OpenAIKey
ANTHROPIC_API_KEY=$AnthropicKey

# Search & News API Keys
TAVILY_API_KEY=$TavilyKey
BRAVE_API_KEY=$BraveKey

# Agent Configuration
AGNO_TELEMETRY=false
MODEL_CHOICE=$ModelChoice

# Database Configuration
DATABASE_URL=sqlite:////opt/finance-agent/data/finance_agent.db

# Server Configuration
HOST=0.0.0.0
PORT=7777
"@

$envContent | Out-File -FilePath (Join-Path $tempDir ".env") -Encoding utf8 -Force
Write-Success "Environment file created"

# Create AgentOS wrapper script
Write-Info "Creating AgentOS production wrapper..."
$agentOSScript = @'
#!/usr/bin/env python3
"""Finance News Agent - AgentOS Production Deployment"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Import Agno components
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb

# Import our agent
from src.agents.finance_news_agent import create_finance_news_agent

# Configuration
MODEL_CHOICE = os.getenv("MODEL_CHOICE", "openai")
DB_PATH = os.getenv("DATABASE_URL", "sqlite:////opt/finance-agent/data/finance_agent.db")

# Ensure data directory exists
data_dir = Path("/opt/finance-agent/data")
data_dir.mkdir(parents=True, exist_ok=True)

# Create database instance
db_file = DB_PATH.replace("sqlite:///", "")
agent_db = SqliteDb(
    session_table="finance_sessions",
    db_file=db_file
)

print(f"🗄️  Using database: {db_file}")
print(f"🤖 Using model: {MODEL_CHOICE}")

# Create finance agent
finance_agent = create_finance_news_agent(
    model_choice=MODEL_CHOICE,
    interactive=False
)
finance_agent.db = agent_db
finance_agent.debug_mode = False

# Create AgentOS
agent_os = AgentOS(
    id="finance-news-os",
    description="Finance News & Market Analysis Agent - Personal Deployment",
    agents=[finance_agent],
)

# Get FastAPI app
app = agent_os.get_app()

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7777))

    print(f"\n{'=' * 80}")
    print("💰 Finance News Agent - Production Mode")
    print(f"{'=' * 80}\n")
    print(f"🌐 Server starting on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🖥️  Web Interface: http://{host}:{port}/ui")
    print(f"\n{'=' * 80}\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
'@

$agentOSScript | Out-File -FilePath (Join-Path $tempDir "agent_server.py") -Encoding utf8 -Force
Write-Success "AgentOS wrapper created"

# Create requirements.txt
Write-Info "Creating requirements.txt..."
$requirementsContent = @"
# Finance News Agent - Production Requirements
agno>=0.1.0
openai>=1.0.0
anthropic>=0.20.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
yfinance>=0.2.0
duckduckgo-search>=6.0.0
uvicorn[standard]>=0.30.0
fastapi>=0.100.0
"@

$requirementsContent | Out-File -FilePath (Join-Path $tempDir "requirements.txt") -Encoding utf8 -Force
Write-Success "requirements.txt created"

# ==============================================================================
# Upload Files to Instance
# ==============================================================================

Write-StepHeader "Uploading Files to GCP Instance"

# First, create the remote directory
Write-Info "Creating remote directory..."
gcloud compute ssh $InstanceName `
    --zone=$Zone `
    --project=$ProjectId `
    --command="mkdir -p /tmp/finance-agent" 2>$null

Write-Info "Uploading application files (this may take 30-60 seconds)..."
try {
    # Use --scp-flag to create parent directories
    gcloud compute scp --recurse $tempDir "${InstanceName}:/tmp/" `
        --zone=$Zone `
        --project=$ProjectId `
        --compress

    if ($LASTEXITCODE -eq 0) {
        # Rename the uploaded directory to finance-agent
        $tempDirName = Split-Path $tempDir -Leaf
        gcloud compute ssh $InstanceName `
            --zone=$Zone `
            --project=$ProjectId `
            --command="mv /tmp/$tempDirName /tmp/finance-agent 2>/dev/null || rm -rf /tmp/finance-agent && mv /tmp/$tempDirName /tmp/finance-agent"

        Write-Success "Files uploaded successfully"
    }
    else {
        throw "Upload failed"
    }
}
catch {
    Write-ErrorMsg "Failed to upload files: $_"
    Write-Info "Attempting alternative upload method..."

    # Alternative: Upload as tar archive
    try {
        $tarFile = "$env:TEMP\finance-agent-deploy.tar.gz"
        Write-Info "Creating tar archive..."

        # Create tar using PowerShell (requires tar.exe in Windows 10+)
        Push-Location $tempDir
        tar -czf $tarFile *
        Pop-Location

        Write-Info "Uploading tar archive..."
        gcloud compute scp $tarFile "${InstanceName}:/tmp/finance-agent.tar.gz" `
            --zone=$Zone `
            --project=$ProjectId

        Write-Info "Extracting on remote..."
        gcloud compute ssh $InstanceName `
            --zone=$Zone `
            --project=$ProjectId `
            --command="mkdir -p /tmp/finance-agent && tar -xzf /tmp/finance-agent.tar.gz -C /tmp/finance-agent && rm /tmp/finance-agent.tar.gz"

        Remove-Item $tarFile -Force
        Write-Success "Files uploaded successfully (via tar)"
    }
    catch {
        Write-ErrorMsg "Both upload methods failed: $_"
        exit 1
    }
}
finally {
    # Clean up temp directory
    Remove-Item -Path $tempDir -Recurse -Force
    Write-Info "Temporary files cleaned up"
}

# ==============================================================================
# Install and Configure on Instance
# ==============================================================================

Write-StepHeader "Installing Application on Instance"

$installScript = @'
#!/bin/bash
set -e

echo "🚀 Finance News Agent - Installation Starting..."

# Move files to final location
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/finance-agent
sudo chown -R $USER:$USER /opt/finance-agent
cp -r /tmp/finance-agent/* /opt/finance-agent/
rm -rf /tmp/finance-agent

# Create data and logs directories
mkdir -p /opt/finance-agent/data
mkdir -p /opt/finance-agent/logs

cd /opt/finance-agent

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Test import
echo "🧪 Testing agent import..."
python3 -c "from src.agents.finance_news_agent import create_finance_news_agent; print('✅ Import successful')"

echo "✅ Application installed successfully!"
'@

Write-Info "Running installation script on instance..."
$installScript | gcloud compute ssh $InstanceName `
    --zone=$Zone `
    --project=$ProjectId `
    --command="bash -s"

if ($LASTEXITCODE -eq 0) {
    Write-Success "Installation completed"
}
else {
    Write-ErrorMsg "Installation failed"
    exit 1
}

# ==============================================================================
# Create Systemd Service
# ==============================================================================

Write-StepHeader "Configuring Systemd Service"

$systemdService = @'
[Unit]
Description=Finance News Agent - AI Market Analysis
After=network.target

[Service]
Type=simple
User=%REPLACE_USER%
WorkingDirectory=/opt/finance-agent
Environment="PATH=/opt/finance-agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/finance-agent/venv/bin/python agent_server.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/opt/finance-agent/logs/agent.log
StandardError=append:/opt/finance-agent/logs/agent.error.log

[Install]
WantedBy=multi-user.target
'@

Write-Info "Creating systemd service..."
$systemdService | gcloud compute ssh $InstanceName `
    --zone=$Zone `
    --project=$ProjectId `
    --command="cat > /tmp/finance-agent.service && \
               sed -i 's/%REPLACE_USER%/'`$USER'/g' /tmp/finance-agent.service && \
               sudo mv /tmp/finance-agent.service /etc/systemd/system/finance-agent.service && \
               sudo systemctl daemon-reload && \
               sudo systemctl enable finance-agent.service && \
               echo '✅ Systemd service configured'"

if ($LASTEXITCODE -eq 0) {
    Write-Success "Systemd service created and enabled"
}
else {
    Write-ErrorMsg "Systemd service setup failed"
    exit 1
}

# ==============================================================================
# Create Management Scripts on Instance
# ==============================================================================

Write-StepHeader "Creating Management Scripts"

$startScript = @'
#!/bin/bash
echo "🚀 Starting Finance News Agent..."
sudo systemctl start finance-agent
sleep 2
sudo systemctl status finance-agent --no-pager
echo ""
echo "✅ Agent is running!"
echo "📊 View logs: tail -f /opt/finance-agent/logs/agent.log"
'@

$stopScript = @'
#!/bin/bash
echo "⏸️  Stopping Finance News Agent..."
sudo systemctl stop finance-agent
echo "✅ Agent stopped"
'@

$statusScript = @'
#!/bin/bash
echo "📊 Finance News Agent Status:"
echo ""
sudo systemctl status finance-agent --no-pager
echo ""
echo "📋 Recent logs:"
tail -n 20 /opt/finance-agent/logs/agent.log
'@

Write-Info "Creating management scripts on instance..."

@"
cat > /opt/finance-agent/start.sh <<'EOF'
$startScript
EOF

cat > /opt/finance-agent/stop.sh <<'EOF'
$stopScript
EOF

cat > /opt/finance-agent/status.sh <<'EOF'
$statusScript
EOF

chmod +x /opt/finance-agent/*.sh
echo '✅ Management scripts created'
"@ | gcloud compute ssh $InstanceName `
    --zone=$Zone `
    --project=$ProjectId `
    --command="bash -s"

Write-Success "Management scripts created"

# ==============================================================================
# Start the Agent
# ==============================================================================

Write-StepHeader "Starting Finance News Agent"

Write-Info "Starting the agent service..."
gcloud compute ssh $InstanceName `
    --zone=$Zone `
    --project=$ProjectId `
    --command="/opt/finance-agent/start.sh"

Start-Sleep -Seconds 5

# ==============================================================================
# Get Instance IP and Display Access Info
# ==============================================================================

Write-StepHeader "Deployment Complete"

try {
    $instanceInfo = gcloud compute instances describe $InstanceName `
        --zone=$Zone `
        --project=$ProjectId `
        --format=json | ConvertFrom-Json

    $externalIP = $instanceInfo.networkInterfaces[0].accessConfigs[0].natIP

    Write-Success "Finance News Agent deployed successfully!"
    Write-Host ""

    Write-Host "🌐 Access Information:" -ForegroundColor White
    Write-Host "  • Agent URL:        http://${externalIP}:7777" -ForegroundColor Cyan
    Write-Host "  • API Docs:         http://${externalIP}:7777/docs" -ForegroundColor Cyan
    Write-Host "  • Web Interface:    http://${externalIP}:7777/ui" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "🎮 Management Commands (on instance):" -ForegroundColor White
    Write-Host "  • Start:   /opt/finance-agent/start.sh" -ForegroundColor Yellow
    Write-Host "  • Stop:    /opt/finance-agent/stop.sh" -ForegroundColor Yellow
    Write-Host "  • Status:  /opt/finance-agent/status.sh" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "📊 View Logs:" -ForegroundColor White
    Write-Host "  tail -f /opt/finance-agent/logs/agent.log" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "💡 Tips:" -ForegroundColor White
    Write-Host "  • Use .\03-manage-instance.ps1 for local control" -ForegroundColor Gray
    Write-Host "  • Stop instance when not in use to save costs" -ForegroundColor Gray
    Write-Host "  • Database stored in: /opt/finance-agent/data/" -ForegroundColor Gray
    Write-Host ""

    # Update config with deployment status
    $config.DeployedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $config.AgentURL = "http://${externalIP}:7777"
    $config | ConvertTo-Json | Out-File -FilePath $configPath -Encoding utf8 -Force
}
catch {
    Write-Warning "Could not retrieve instance IP"
}

Write-Host "$('=' * 80)" -ForegroundColor $ColorSuccess
Write-Host "  ✅ Deployment Complete!" -ForegroundColor $ColorSuccess
Write-Host "$('=' * 80)" -ForegroundColor $ColorSuccess
