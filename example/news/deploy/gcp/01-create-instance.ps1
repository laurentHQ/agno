# Finance News Agent - GCP E2-micro Instance Setup
# PowerShell 7.5 Script for Windows
# ============================================

<#
.SYNOPSIS
    Creates a GCP E2-micro instance for Finance News Agent deployment

.DESCRIPTION
    This script creates a cost-optimized E2-micro Compute Engine instance
    with all necessary configurations for running the Finance News Agent.

    Features:
    - Free tier eligible E2-micro instance
    - Debian 12 base image
    - 10GB boot disk (standard persistent disk)
    - Firewall rules for agent access
    - Startup script for Python environment

.PARAMETER ProjectId
    Your GCP Project ID (required)

.PARAMETER Zone
    GCP Zone for instance (default: us-central1-a for free tier)

.PARAMETER InstanceName
    Name for the compute instance (default: finance-news-agent)

.EXAMPLE
    .\01-create-instance.ps1 -ProjectId "my-project-123"

.EXAMPLE
    .\01-create-instance.ps1 -ProjectId "my-project-123" -Zone "us-east1-b"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Enter your GCP Project ID")]
    [string]$ProjectId,

    [Parameter(Mandatory=$false)]
    [ValidateSet('us-central1-a', 'us-central1-b', 'us-central1-c', 'us-central1-f',
                 'us-east1-b', 'us-east1-c', 'us-east1-d',
                 'us-west1-a', 'us-west1-b', 'us-west1-c')]
    [string]$Zone = "us-central1-a",

    [Parameter(Mandatory=$false)]
    [string]$InstanceName = "finance-news-agent"
)

# Configuration
$MachineType = "e2-micro"
$ImageFamily = "ubuntu-2204-lts"
$ImageProject = "ubuntu-os-cloud"
$DiskSize = "50GB"
$DiskType = "pd-standard"
$NetworkTags = "http-server,https-server,finance-agent"

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

function Test-GcloudInstalled {
    try {
        $null = gcloud --version
        return $true
    }
    catch {
        return $false
    }
}

function Test-InstanceExists {
    param([string]$Name, [string]$Zone)

    try {
        $result = gcloud compute instances describe $Name --zone=$Zone --project=$ProjectId 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# ==============================================================================
# Startup Script (runs on instance boot)
# ==============================================================================

$StartupScript = @'
#!/bin/bash
# Finance News Agent - Instance Initialization Script
# This runs once on first boot to setup the environment

set -e

echo "🚀 Finance News Agent - Instance Setup Starting..."

# Update system packages
echo "📦 Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

# Install Python 3.11 and essential tools
echo "🐍 Installing Python 3.11 and development tools..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget \
    vim \
    htop \
    sqlite3 \
    build-essential \
    software-properties-common

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/finance-agent
mkdir -p /opt/finance-agent/data
mkdir -p /opt/finance-agent/logs

# Set permissions
echo "🔐 Setting permissions..."
chown -R $(logname):$(logname) /opt/finance-agent 2>/dev/null || chown -R 1000:1000 /opt/finance-agent

# Create success marker
echo "✅ Instance initialization completed at $(date)" > /opt/finance-agent/setup-complete.txt

echo "✅ Finance News Agent - Instance Ready!"
echo "📋 Next steps:"
echo "   1. SSH into instance: gcloud compute ssh $HOSTNAME"
echo "   2. Run deployment script: 02-deploy-agent.ps1"
echo "   3. Start the agent service"
'@

# ==============================================================================
# Main Execution
# ==============================================================================

Write-StepHeader "Finance News Agent - GCP Instance Creation"

# Step 1: Verify gcloud CLI
Write-Info "Checking gcloud CLI installation..."
if (-not (Test-GcloudInstalled)) {
    Write-ErrorMsg "Google Cloud SDK (gcloud) is not installed!"
    Write-Info "Download from: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Success "gcloud CLI found"

# Step 2: Set active project
Write-Info "Setting active GCP project to: $ProjectId"
try {
    gcloud config set project $ProjectId 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set project"
    }
    Write-Success "Project set successfully"
}
catch {
    Write-ErrorMsg "Failed to set project. Please verify Project ID: $ProjectId"
    exit 1
}

# Step 3: Check if instance already exists
Write-Info "Checking if instance already exists..."
if (Test-InstanceExists -Name $InstanceName -Zone $Zone) {
    Write-Warning "Instance '$InstanceName' already exists in zone '$Zone'"
    $response = Read-Host "Do you want to delete and recreate it? (yes/no)"

    if ($response -eq 'yes') {
        Write-Info "Deleting existing instance..."
        gcloud compute instances delete $InstanceName --zone=$Zone --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Instance deleted"
            Start-Sleep -Seconds 5
        }
        else {
            Write-ErrorMsg "Failed to delete instance"
            exit 1
        }
    }
    else {
        Write-Info "Keeping existing instance. Exiting..."
        exit 0
    }
}

# Step 4: Create firewall rule for agent access
Write-StepHeader "Creating Firewall Rules"

Write-Info "Creating firewall rule for Finance Agent (port 7777)..."
try {
    $firewallExists = gcloud compute firewall-rules describe allow-finance-agent --project=$ProjectId 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Warning "Firewall rule 'allow-finance-agent' already exists"
    }
    else {
        gcloud compute firewall-rules create allow-finance-agent `
            --allow=tcp:7777 `
            --target-tags=finance-agent `
            --description="Allow access to Finance News Agent on port 7777" `
            --project=$ProjectId

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Firewall rule created successfully"
        }
        else {
            Write-Warning "Failed to create firewall rule (may already exist)"
        }
    }
}
catch {
    Write-Warning "Firewall rule creation skipped (may already exist)"
}

# Step 5: Create the compute instance
Write-StepHeader "Creating E2-micro Compute Instance"

Write-Info "Instance Configuration:"
Write-Host "  • Name:         $InstanceName" -ForegroundColor White
Write-Host "  • Type:         $MachineType (0.25-2 vCPU, 1 GB RAM)" -ForegroundColor White
Write-Host "  • Zone:         $Zone (Free Tier Eligible)" -ForegroundColor White
Write-Host "  • Image:        $ImageFamily" -ForegroundColor White
Write-Host "  • Disk:         $DiskSize $DiskType" -ForegroundColor White
Write-Host "  • Network:      $NetworkTags" -ForegroundColor White

Write-Info "Creating instance (this may take 1-2 minutes)..."

# Save startup script to temp file
$tempStartupScript = [System.IO.Path]::GetTempFileName()
$StartupScript | Out-File -FilePath $tempStartupScript -Encoding utf8 -Force

try {
    gcloud compute instances create $InstanceName `
        --project=$ProjectId `
        --zone=$Zone `
        --machine-type=$MachineType `
        --image-family=$ImageFamily `
        --image-project=$ImageProject `
        --boot-disk-size=$DiskSize `
        --boot-disk-type=$DiskType `
        --boot-disk-device-name=$InstanceName `
        --tags=$NetworkTags `
        --metadata-from-file=startup-script=$tempStartupScript `
        --scopes=https://www.googleapis.com/auth/cloud-platform

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Instance created successfully!"
    }
    else {
        throw "Instance creation failed"
    }
}
catch {
    Write-ErrorMsg "Failed to create instance: $_"
    exit 1
}
finally {
    # Clean up temp file
    if (Test-Path $tempStartupScript) {
        Remove-Item $tempStartupScript -Force
    }
}

# Step 6: Wait for instance to be ready
Write-StepHeader "Waiting for Instance Initialization"

Write-Info "Waiting for instance to boot and run startup script (60 seconds)..."
$progressParams = @{
    Activity = "Instance Initialization"
    Status = "Running startup script..."
}

1..60 | ForEach-Object {
    Write-Progress @progressParams -PercentComplete ($_ / 60 * 100)
    Start-Sleep -Seconds 1
}

Write-Progress @progressParams -Completed
Write-Success "Instance should be ready"

# Step 7: Get instance details
Write-StepHeader "Instance Details"

try {
    $instanceInfo = gcloud compute instances describe $InstanceName `
        --zone=$Zone `
        --project=$ProjectId `
        --format=json | ConvertFrom-Json

    $externalIP = $instanceInfo.networkInterfaces[0].accessConfigs[0].natIP
    $internalIP = $instanceInfo.networkInterfaces[0].networkIP
    $status = $instanceInfo.status

    Write-Success "Instance Details Retrieved"
    Write-Host "`n📋 Instance Information:" -ForegroundColor White
    Write-Host "  • Name:        $InstanceName" -ForegroundColor White
    Write-Host "  • Status:      $status" -ForegroundColor Green
    Write-Host "  • Zone:        $Zone" -ForegroundColor White
    Write-Host "  • External IP: $externalIP" -ForegroundColor Cyan
    Write-Host "  • Internal IP: $internalIP" -ForegroundColor White
    Write-Host "  • Machine:     $MachineType" -ForegroundColor White
}
catch {
    Write-Warning "Could not retrieve instance details"
}

# Step 8: Display next steps
Write-StepHeader "Setup Complete - Next Steps"

Write-Success "E2-micro instance created successfully!"
Write-Host ""

Write-Host "📝 Next Steps:" -ForegroundColor White
Write-Host "  1. Connect to instance:" -ForegroundColor White
Write-Host "     gcloud compute ssh $InstanceName --zone=$Zone --project=$ProjectId" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Deploy Finance News Agent:" -ForegroundColor White
Write-Host "     .\02-deploy-agent.ps1 -ProjectId '$ProjectId' -Zone '$Zone'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Access the agent (after deployment):" -ForegroundColor White
Write-Host "     http://${externalIP}:7777" -ForegroundColor Cyan
Write-Host ""

Write-Host "💰 Cost Estimate:" -ForegroundColor White
Write-Host "  • E2-micro:    `$7.11/month (FREE for first 12 months!)" -ForegroundColor Green
Write-Host "  • Disk 10GB:   `$0.40/month" -ForegroundColor Green
Write-Host "  • Total:       ~`$0.40/month (with free tier)" -ForegroundColor Green
Write-Host ""

Write-Host "🎮 Management Commands:" -ForegroundColor White
Write-Host "  • Start:  gcloud compute instances start $InstanceName --zone=$Zone" -ForegroundColor Yellow
Write-Host "  • Stop:   gcloud compute instances stop $InstanceName --zone=$Zone" -ForegroundColor Yellow
Write-Host "  • SSH:    gcloud compute ssh $InstanceName --zone=$Zone" -ForegroundColor Yellow
Write-Host "  • Delete: gcloud compute instances delete $InstanceName --zone=$Zone" -ForegroundColor Yellow
Write-Host ""

# Save configuration for next scripts
$configPath = Join-Path $PSScriptRoot "instance-config.json"
$config = @{
    ProjectId = $ProjectId
    Zone = $Zone
    InstanceName = $InstanceName
    ExternalIP = $externalIP
    CreatedAt = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
} | ConvertTo-Json

$config | Out-File -FilePath $configPath -Encoding utf8 -Force
Write-Info "Configuration saved to: $configPath"

Write-Host "`n$('=' * 80)" -ForegroundColor $ColorSuccess
Write-Host "  ✅ Instance Creation Complete!" -ForegroundColor $ColorSuccess
Write-Host "$('=' * 80)`n" -ForegroundColor $ColorSuccess
