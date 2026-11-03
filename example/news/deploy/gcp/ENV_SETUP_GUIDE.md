# Environment Variables Setup Guide for Windows

This guide shows you how to set environment variables in Windows PowerShell, similar to using `.env` files in Linux.

---

## 🎯 Quick Start (Recommended)

### **Option 1: Interactive Setup Script** ⭐

The easiest way - interactive prompts for all API keys:

```powershell
# Navigate to deploy directory
cd C:\path\to\agno\example\news\deploy\gcp

# Run setup script
.\set-env.ps1 -Permanent
```

**What it does:**
- ✅ Prompts for all required API keys
- ✅ Validates that all mandatory keys are provided
- ✅ Saves to PowerShell profile (persistent across sessions)
- ✅ Shows masked values for security
- ✅ Provides helpful error messages with links to get API keys

---

## 📋 Manual Methods

### **Option 2: PowerShell Profile (Permanent)**

Similar to adding `export` commands to `.bashrc` in Linux:

```powershell
# Open PowerShell profile in editor
notepad $PROFILE

# Add these lines (replace with your actual keys):
$env:OPENAI_API_KEY = "sk-proj-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:TAVILY_API_KEY = "tvly-..."
$env:BRAVE_API_KEY = "BSA..."

# Save and close notepad

# Reload profile to apply changes
. $PROFILE
```

**Pros:**
- ✅ Persistent across all PowerShell sessions
- ✅ Easy to edit and update
- ✅ User-specific (doesn't affect other users)

**Cons:**
- ⚠️ Only works in PowerShell (not CMD)
- ⚠️ Need to reload profile or restart PowerShell

---

### **Option 3: Current Session Only (Temporary)**

Similar to running `export VAR=value` in Linux terminal:

```powershell
# Set for current PowerShell session only
$env:OPENAI_API_KEY = "sk-proj-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:TAVILY_API_KEY = "tvly-..."
$env:BRAVE_API_KEY = "BSA..."
```

**Pros:**
- ✅ Quick and simple
- ✅ No permanent changes

**Cons:**
- ❌ Lost when you close PowerShell
- ❌ Must set again in every new terminal

---

### **Option 4: Windows Environment Variables (System-wide)**

Similar to adding to `/etc/environment` in Linux:

```powershell
# Open Environment Variables GUI
# Method 1: Search Windows for "environment variables"
# Method 2: Run this command
rundll32.exe sysdm.cpl,EditEnvironmentVariables

# Or use PowerShell (requires admin):
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-proj-...", "User")
[Environment]::SetEnvironmentVariable("TAVILY_API_KEY", "tvly-...", "User")
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "BSA...", "User")
```

**Pros:**
- ✅ Works in all programs and terminals
- ✅ Persistent across reboots
- ✅ System-wide availability

**Cons:**
- ⚠️ Requires restart of applications to take effect
- ⚠️ More steps to set up
- ⚠️ Harder to change quickly

---

## 🔍 Verify Environment Variables

Check if your environment variables are set:

```powershell
# View all API keys
Get-ChildItem env: | Where-Object Name -like '*API_KEY'

# View specific key (first 20 characters)
$env:OPENAI_API_KEY.Substring(0, 20)

# Check if key exists
if ($env:TAVILY_API_KEY) { "Tavily key is set ✅" } else { "Tavily key missing ❌" }

# Test all required keys
@('OPENAI_API_KEY', 'TAVILY_API_KEY', 'BRAVE_API_KEY') | ForEach-Object {
    $value = [Environment]::GetEnvironmentVariable($_, 'Process')
    if ($value) {
        Write-Host "✅ $_ is set" -ForegroundColor Green
    } else {
        Write-Host "❌ $_ is missing" -ForegroundColor Red
    }
}
```

---

## 📝 Using .env File (Alternative)

If you prefer using a `.env` file like in Linux:

### Step 1: Create .env file

```powershell
# Copy template
Copy-Item .env.example .env

# Edit with your API keys
notepad .env
```

### Step 2: Load .env file

Create a helper script `load-env.ps1`:

```powershell
# load-env.ps1
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.+?)\s*$') {
        $name = $matches[1]
        $value = $matches[2]
        Set-Item -Path "env:$name" -Value $value
        Write-Host "✅ Loaded: $name" -ForegroundColor Green
    }
}
```

### Step 3: Use it

```powershell
# Load environment variables from .env
.\load-env.ps1

# Now deploy
.\02-deploy-agent.ps1
```

---

## 🆚 Comparison: Linux vs Windows

| Linux Command | Windows PowerShell Equivalent |
|---------------|-------------------------------|
| `export VAR=value` | `$env:VAR = "value"` |
| `source .env` | `.\load-env.ps1` |
| `echo $VAR` | `$env:VAR` or `echo $env:VAR` |
| `unset VAR` | `Remove-Item env:VAR` |
| `env | grep API` | `Get-ChildItem env: | Where-Object Name -like '*API*'` |
| `~/.bashrc` | `$PROFILE` (PowerShell profile) |
| `/etc/environment` | System Environment Variables |

---

## 🎯 Recommended Workflow

### **For Development (Daily Use):**

```powershell
# 1. One-time setup (saves to profile)
.\set-env.ps1 -Permanent

# 2. Every new PowerShell session
# Keys are automatically loaded!

# 3. Deploy agent
.\02-deploy-agent.ps1
```

### **For Quick Testing:**

```powershell
# Set temporarily
$env:OPENAI_API_KEY = "sk-..."
$env:TAVILY_API_KEY = "tvly-..."
$env:BRAVE_API_KEY = "BSA..."

# Deploy
.\02-deploy-agent.ps1
```

### **For Production:**

```powershell
# Use system environment variables or Azure Key Vault
# Never commit .env files to git!
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Use PowerShell profile for personal development
- Use `.gitignore` to exclude `.env` files
- Use masked output when displaying keys
- Rotate keys regularly
- Use separate keys for dev/prod

### ❌ DON'T:
- Commit API keys to version control
- Share keys in chat/email
- Use production keys in development
- Store keys in plain text files in shared locations

### .gitignore Configuration

```gitignore
# Environment files
.env
.env.local
.env.*.local

# PowerShell profile (if it contains keys)
*profile*.ps1

# Instance config
instance-config.json
```

---

## 🆘 Troubleshooting

### Issue: Keys not loading after setting in profile

**Solution:**
```powershell
# Reload profile
. $PROFILE

# Or restart PowerShell
```

### Issue: Profile doesn't exist

**Solution:**
```powershell
# Create profile
New-Item -Path $PROFILE -ItemType File -Force

# Edit it
notepad $PROFILE
```

### Issue: Can't find PowerShell profile location

**Solution:**
```powershell
# Show profile path
echo $PROFILE

# Navigate to profile directory
cd (Split-Path $PROFILE)
```

### Issue: Environment variables not working in deployment script

**Solution:**
```powershell
# Verify keys are set
Get-ChildItem env: | Where-Object Name -like '*API_KEY'

# If empty, run set-env.ps1 again
.\set-env.ps1 -Permanent
. $PROFILE
```

---

## 📚 Additional Resources

- **PowerShell Profile Docs:** https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_profiles
- **Environment Variables:** https://learn.microsoft.com/windows/win32/procthread/environment-variables
- **OpenAI API Keys:** https://platform.openai.com/api-keys
- **Anthropic Console:** https://console.anthropic.com/
- **Tavily API:** https://tavily.com/
- **Brave Search API:** https://brave.com/search/api/

---

## ✨ Example: Complete Setup Flow

```powershell
# 1. Clone repository
git clone <repo-url>
cd agno\example\news\deploy\gcp

# 2. Setup environment variables (interactive)
.\set-env.ps1 -Permanent

# Output:
# ℹ️  Configure your API keys for Finance News Agent
# 🤖 AI Model Keys (choose at least one):
# OpenAI API Key (required): sk-proj-...
# Tavily API Key (required): tvly-...
# Brave Search API Key (required): BSA...
# ✅ API keys saved to PowerShell profile

# 3. Reload profile
. $PROFILE

# 4. Verify
Get-ChildItem env: | Where-Object Name -like '*API_KEY'

# 5. Create GCP instance
.\01-create-instance.ps1 -ProjectId "your-project-id"

# 6. Deploy agent (uses environment variables automatically)
.\02-deploy-agent.ps1

# Done! 🎉
```

---

**Remember:** The `set-env.ps1` script is the easiest and recommended way to manage your API keys in Windows! 🚀
