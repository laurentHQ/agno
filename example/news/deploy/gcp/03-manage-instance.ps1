# Finance News Agent - Instance Management Script
# PowerShell 7.5 Script for Windows
# ============================================

<#
.SYNOPSIS
    Manages the Finance News Agent GCP instance (start/stop/status/connect)

.DESCRIPTION
    Provides convenient commands to manage your Finance News Agent instance
    from your local Windows machine.

    Commands:
    - start    : Start the instance and agent service
    - stop     : Stop the agent service and instance
    - restart  : Restart the agent service
    - status   : Check instance and agent status
    - ssh      : SSH into the instance
    - logs     : View agent logs
    - url      : Display agent access URL
    - cost     : Show cost estimate

.PARAMETER Command
    The management command to execute

.PARAMETER ProjectId
    GCP Project ID (loaded from config if not provided)

.PARAMETER Zone
    GCP Zone (loaded from config if not provided)

.PARAMETER InstanceName
    Instance name (loaded from config if not provided)

.EXAMPLE
    .\03-manage-instance.ps1 start

.EXAMPLE
    .\03-manage-instance.ps1 stop

.EXAMPLE
    .\03-manage-instance.ps1 status

.EXAMPLE
    .\03-manage-instance.ps1 ssh
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'ssh', 'logs', 'url', 'cost', 'help')]
    [string]$Command,

    [Parameter(Mandatory=$false)]
    [string]$ProjectId,

    [Parameter(Mandatory=$false)]
    [string]$Zone,

    [Parameter(Mandatory=$false)]
    [string]$InstanceName
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

function Get-InstanceStatus {
    try {
        $result = gcloud compute instances describe $InstanceName `
            --zone=$Zone `
            --project=$ProjectId `
            --format='value(status)' 2>&1

        if ($LASTEXITCODE -eq 0) {
            return $result.Trim()
        }
        return "UNKNOWN"
    }
    catch {
        return "UNKNOWN"
    }
}

function Get-ExternalIP {
    try {
        $result = gcloud compute instances describe $InstanceName `
            --zone=$Zone `
            --project=$ProjectId `
            --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>&1

        if ($LASTEXITCODE -eq 0) {
            return $result.Trim()
        }
        return "N/A"
    }
    catch {
        return "N/A"
    }
}

# ==============================================================================
# Load Configuration
# ==============================================================================

$configPath = Join-Path $PSScriptRoot "instance-config.json"

if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json

    if (-not $ProjectId) { $ProjectId = $config.ProjectId }
    if (-not $Zone) { $Zone = $config.Zone }
    if (-not $InstanceName) { $InstanceName = $config.InstanceName }
}

if (-not $ProjectId -or -not $Zone -or -not $InstanceName) {
    Write-ErrorMsg "Configuration not found!"
    Write-Info "Run 01-create-instance.ps1 first or provide parameters"
    exit 1
}

# ==============================================================================
# Command Handlers
# ==============================================================================

function Start-FinanceAgent {
    Write-StepHeader "Starting Finance News Agent"

    $status = Get-InstanceStatus

    if ($status -eq "RUNNING") {
        Write-Info "Instance is already running"
    }
    else {
        Write-Info "Starting instance..."
        gcloud compute instances start $InstanceName --zone=$Zone --project=$ProjectId

        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Failed to start instance"
            return
        }

        Write-Success "Instance started"
        Write-Info "Waiting for instance to be ready (30 seconds)..."
        Start-Sleep -Seconds 30
    }

    Write-Info "Starting agent service..."
    gcloud compute ssh $InstanceName `
        --zone=$Zone `
        --project=$ProjectId `
        --command="/opt/finance-agent/start.sh"

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Agent service started successfully!"

        $externalIP = Get-ExternalIP
        Write-Host ""
        Write-Host "🌐 Agent Access:" -ForegroundColor White
        Write-Host "  • URL: http://${externalIP}:7777" -ForegroundColor Cyan
        Write-Host "  • API Docs: http://${externalIP}:7777/docs" -ForegroundColor Cyan
        Write-Host "  • UI: http://${externalIP}:7777/ui" -ForegroundColor Cyan
    }
    else {
        Write-ErrorMsg "Failed to start agent service"
    }
}

function Stop-FinanceAgent {
    Write-StepHeader "Stopping Finance News Agent"

    $status = Get-InstanceStatus

    if ($status -ne "RUNNING") {
        Write-Info "Instance is not running"
        return
    }

    Write-Info "Stopping agent service..."
    gcloud compute ssh $InstanceName `
        --zone=$Zone `
        --project=$ProjectId `
        --command="/opt/finance-agent/stop.sh" 2>$null

    Write-Success "Agent service stopped"

    Write-Host ""
    $response = Read-Host "Stop the instance to save costs? (yes/no)"

    if ($response -eq 'yes') {
        Write-Info "Stopping instance..."
        gcloud compute instances stop $InstanceName --zone=$Zone --project=$ProjectId

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Instance stopped - no compute charges while stopped"
            Write-Host ""
            Write-Host "💰 Cost Savings:" -ForegroundColor Green
            Write-Host "  • Instance charges: $0/hour while stopped" -ForegroundColor Green
            Write-Host "  • Only disk storage charged: ~$0.40/month" -ForegroundColor Green
        }
        else {
            Write-ErrorMsg "Failed to stop instance"
        }
    }
    else {
        Write-Info "Instance still running (incurring charges)"
    }
}

function Restart-FinanceAgent {
    Write-StepHeader "Restarting Finance News Agent"

    $status = Get-InstanceStatus

    if ($status -ne "RUNNING") {
        Write-ErrorMsg "Instance is not running. Use 'start' command first."
        return
    }

    Write-Info "Restarting agent service..."
    gcloud compute ssh $InstanceName `
        --zone=$Zone `
        --project=$ProjectId `
        --command="sudo systemctl restart finance-agent"

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Agent service restarted"
        Start-Sleep -Seconds 3
        Show-AgentStatus
    }
    else {
        Write-ErrorMsg "Failed to restart agent service"
    }
}

function Show-AgentStatus {
    Write-StepHeader "Finance News Agent Status"

    $instanceStatus = Get-InstanceStatus
    $externalIP = Get-ExternalIP

    Write-Host "📊 Instance Information:" -ForegroundColor White
    Write-Host "  • Name:      $InstanceName" -ForegroundColor White
    Write-Host "  • Zone:      $Zone" -ForegroundColor White
    Write-Host "  • Status:    $instanceStatus" -ForegroundColor $(if ($instanceStatus -eq "RUNNING") { "Green" } else { "Yellow" })
    Write-Host "  • IP:        $externalIP" -ForegroundColor White

    if ($instanceStatus -eq "RUNNING") {
        Write-Host ""
        Write-Host "🤖 Agent Service Status:" -ForegroundColor White

        gcloud compute ssh $InstanceName `
            --zone=$Zone `
            --project=$ProjectId `
            --command="sudo systemctl status finance-agent --no-pager | head -n 10"

        Write-Host ""
        Write-Host "🌐 Access URLs:" -ForegroundColor White
        Write-Host "  • Agent:     http://${externalIP}:7777" -ForegroundColor Cyan
        Write-Host "  • API Docs:  http://${externalIP}:7777/docs" -ForegroundColor Cyan
        Write-Host "  • UI:        http://${externalIP}:7777/ui" -ForegroundColor Cyan
    }
    else {
        Write-Warning "Instance is not running. Use 'start' command to start."
    }
}

function Show-AgentLogs {
    Write-StepHeader "Finance News Agent Logs"

    $status = Get-InstanceStatus

    if ($status -ne "RUNNING") {
        Write-ErrorMsg "Instance is not running"
        return
    }

    Write-Info "Fetching last 50 lines of agent logs..."
    Write-Host ""

    gcloud compute ssh $InstanceName `
        --zone=$Zone `
        --project=$ProjectId `
        --command="tail -n 50 /opt/finance-agent/logs/agent.log"

    Write-Host ""
    Write-Info "For live logs, use: .\03-manage-instance.ps1 ssh"
    Write-Info "Then run: tail -f /opt/finance-agent/logs/agent.log"
}

function Connect-SSH {
    Write-StepHeader "SSH Connection"

    $status = Get-InstanceStatus

    if ($status -ne "RUNNING") {
        Write-ErrorMsg "Instance is not running"
        Write-Info "Start instance first: .\03-manage-instance.ps1 start"
        return
    }

    Write-Info "Connecting to instance via SSH..."
    Write-Host ""

    gcloud compute ssh $InstanceName --zone=$Zone --project=$ProjectId
}

function Show-AgentURL {
    Write-StepHeader "Agent Access Information"

    $status = Get-InstanceStatus

    if ($status -ne "RUNNING") {
        Write-Warning "Instance is not running"
        Write-Info "Start instance first: .\03-manage-instance.ps1 start"
        return
    }

    $externalIP = Get-ExternalIP

    Write-Host "🌐 Finance News Agent URLs:" -ForegroundColor White
    Write-Host ""
    Write-Host "  Main Interface:" -ForegroundColor Cyan
    Write-Host "  http://${externalIP}:7777" -ForegroundColor White
    Write-Host ""
    Write-Host "  API Documentation:" -ForegroundColor Cyan
    Write-Host "  http://${externalIP}:7777/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "  Web UI:" -ForegroundColor Cyan
    Write-Host "  http://${externalIP}:7777/ui" -ForegroundColor White
    Write-Host ""

    # Copy to clipboard if available
    $url = "http://${externalIP}:7777"
    try {
        Set-Clipboard -Value $url
        Write-Success "Main URL copied to clipboard!"
    }
    catch {
        Write-Info "To copy: $url"
    }
}

function Show-CostEstimate {
    Write-StepHeader "Cost Estimate"

    $status = Get-InstanceStatus
    $isRunning = $status -eq "RUNNING"

    Write-Host "💰 Finance News Agent - Cost Breakdown" -ForegroundColor White
    Write-Host ""

    Write-Host "📊 E2-micro Instance:" -ForegroundColor White
    Write-Host "  • Monthly (always on):   `$7.11/month" -ForegroundColor White
    Write-Host "  • Hourly rate:           `$0.0098/hour" -ForegroundColor Gray
    Write-Host "  • Free Tier:             First 12 months FREE!" -ForegroundColor Green
    Write-Host ""

    Write-Host "💾 Storage (10GB Disk):" -ForegroundColor White
    Write-Host "  • Monthly cost:          `$0.40/month" -ForegroundColor White
    Write-Host "  • Charged even when stopped" -ForegroundColor Gray
    Write-Host ""

    Write-Host "🌐 Network Egress:" -ForegroundColor White
    Write-Host "  • Estimated:             `$0.50/month (minimal usage)" -ForegroundColor White
    Write-Host ""

    Write-Host "$('-' * 80)" -ForegroundColor Gray

    Write-Host "📈 Usage Scenarios:" -ForegroundColor White
    Write-Host ""

    Write-Host "  2 hours/day (60 hours/month):" -ForegroundColor Cyan
    Write-Host "    • Compute: `$0.59/month" -ForegroundColor White
    Write-Host "    • Storage: `$0.40/month" -ForegroundColor White
    Write-Host "    • Total:   `$0.99/month (with free tier)" -ForegroundColor Green
    Write-Host ""

    Write-Host "  Always on (730 hours/month):" -ForegroundColor Cyan
    Write-Host "    • Compute: `$7.11/month" -ForegroundColor White
    Write-Host "    • Storage: `$0.40/month" -ForegroundColor White
    Write-Host "    • Total:   `$7.51/month (with free tier)" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "💡 Cost Optimization Tips:" -ForegroundColor White
    Write-Host "  • Stop instance when not in use" -ForegroundColor Gray
    Write-Host "  • Use free tier (first 12 months)" -ForegroundColor Gray
    Write-Host "  • Schedule start/stop with scripts" -ForegroundColor Gray
    Write-Host ""

    if ($isRunning) {
        Write-Host "⚠️  Instance Status: RUNNING (incurring charges)" -ForegroundColor Yellow
        Write-Host "   Stop to save costs: .\03-manage-instance.ps1 stop" -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ Instance Status: STOPPED (minimal charges)" -ForegroundColor Green
        Write-Host "   Only storage costs apply (~`$0.40/month)" -ForegroundColor Green
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Finance News Agent - Management Commands" -ForegroundColor Cyan
    Write-Host "$('=' * 80)" -ForegroundColor Gray
    Write-Host ""

    Write-Host "USAGE:" -ForegroundColor White
    Write-Host "  .\03-manage-instance.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "COMMANDS:" -ForegroundColor White
    Write-Host "  start      Start instance and agent service" -ForegroundColor Yellow
    Write-Host "  stop       Stop agent service and instance" -ForegroundColor Yellow
    Write-Host "  restart    Restart agent service" -ForegroundColor Yellow
    Write-Host "  status     Show instance and agent status" -ForegroundColor Yellow
    Write-Host "  ssh        Connect to instance via SSH" -ForegroundColor Yellow
    Write-Host "  logs       View agent logs" -ForegroundColor Yellow
    Write-Host "  url        Show agent access URLs" -ForegroundColor Yellow
    Write-Host "  cost       Display cost estimate" -ForegroundColor Yellow
    Write-Host "  help       Show this help message" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "EXAMPLES:" -ForegroundColor White
    Write-Host "  .\03-manage-instance.ps1 start" -ForegroundColor Gray
    Write-Host "  .\03-manage-instance.ps1 status" -ForegroundColor Gray
    Write-Host "  .\03-manage-instance.ps1 logs" -ForegroundColor Gray
    Write-Host "  .\03-manage-instance.ps1 stop" -ForegroundColor Gray
    Write-Host ""

    Write-Host "CONFIGURATION:" -ForegroundColor White
    Write-Host "  • Project:  $ProjectId" -ForegroundColor Gray
    Write-Host "  • Zone:     $Zone" -ForegroundColor Gray
    Write-Host "  • Instance: $InstanceName" -ForegroundColor Gray
    Write-Host ""
}

# ==============================================================================
# Main Command Router
# ==============================================================================

switch ($Command) {
    'start'   { Start-FinanceAgent }
    'stop'    { Stop-FinanceAgent }
    'restart' { Restart-FinanceAgent }
    'status'  { Show-AgentStatus }
    'ssh'     { Connect-SSH }
    'logs'    { Show-AgentLogs }
    'url'     { Show-AgentURL }
    'cost'    { Show-CostEstimate }
    'help'    { Show-Help }
}

Write-Host ""
