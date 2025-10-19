# Nutanix V4 API Environment Setup Guide

This guide provides instructions for setting up the Nutanix V4 API environment on a freshly deployed Windows VM using the Install-NtnxV4ApiEnvironment.ps1 script.

## Prerequisites

### Target Windows VM Requirements
- **OS**: Windows Server 2019/2022 or Windows 10/11
- **PowerShell**: Version 5.1 or later (PowerShell 7+ recommended)
- **Internet Access**: Required for downloading modules and dependencies
- **Administrator Access**: Script must be run with elevated privileges
- **Execution Policy**: Must allow script execution

### Repository Access
- **Private Repository**: https://github.com/hardevsanghera/runner-setup_v4api.git
- **Public Repository**: https://github.com/hardevsanghera/ntnx-v4api-cats.git
- **Target Script**: `experimental/Install-NtnxV4ApiEnvironment.ps1`

## Setup Configuration

### Step 1: Prepare Windows VM
Connect to your freshly deployed Windows VM and open PowerShell as Administrator:

```powershell
# Check PowerShell version
$PSVersionTable.PSVersion

# Set execution policy to allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force

# Enable TLS 1.2 for secure downloads
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

### Step 2: Install Git (if not already installed)
```powershell
# Download and install Git for Windows
$GitUrl = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.42.0.2-64-bit.exe"
$GitInstaller = "$env:TEMP\Git-Installer.exe"

# Download Git installer
Invoke-WebRequest -Uri $GitUrl -OutFile $GitInstaller

# Install Git silently
Start-Process -FilePath $GitInstaller -ArgumentList "/SILENT" -Wait

# Add Git to PATH for current session
$env:PATH += ";C:\Program Files\Git\bin"

# Verify installation
git --version
```

### Step 3: Clone Required Repositories

#### Clone Private Repository (runner-setup_v4api)
```powershell
# Navigate to working directory
Set-Location "C:\Temp"
New-Item -ItemType Directory -Path "NutanixV4Setup" -Force
Set-Location "C:\Temp\NutanixV4Setup"

# Clone private repository (you'll be prompted for credentials)
git clone https://github.com/hardevsanghera/runner-setup_v4api.git

# Alternative: Clone using personal access token
# git clone https://YOUR_TOKEN@github.com/hardevsanghera/runner-setup_v4api.git
```

#### Clone Public Repository (ntnx-v4api-cats)
```powershell
# Clone public repository containing the installation script
git clone https://github.com/hardevsanghera/ntnx-v4api-cats.git
```

### Step 4: Locate and Prepare Installation Script
```powershell
# Navigate to the experimental folder
Set-Location "C:\Temp\NutanixV4Setup\ntnx-v4api-cats\experimental"

# Verify the script exists
if (Test-Path "Install-NtnxV4ApiEnvironment.ps1") {
    Write-Host "✅ Installation script found" -ForegroundColor Green
    Get-ChildItem "Install-NtnxV4ApiEnvironment.ps1" | Select-Object Name, Length, LastWriteTime
} else {
    Write-Host "❌ Installation script not found" -ForegroundColor Red
    exit 1
}
```

## Execution Instructions

### Step 5: Review Script Parameters
Before execution, check what parameters the script accepts:

```powershell
# Display script help and parameters
Get-Help .\Install-NtnxV4ApiEnvironment.ps1 -Full

# Or examine the script parameters directly
Get-Content .\Install-NtnxV4ApiEnvironment.ps1 | Select-String "param\(|Parameter|\.PARAMETER" -A 5
```

### Step 6: Execute Installation Script

#### Basic Execution
```powershell
# Run with default parameters
.\Install-NtnxV4ApiEnvironment.ps1
```

#### Execution with Common Parameters (adjust as needed)
```powershell
# Example with typical parameters (modify based on actual script parameters)
.\Install-NtnxV4ApiEnvironment.ps1 `
    -InstallPath "C:\NutanixV4API" `
    -ModuleScope "AllUsers" `
    -Force `
    -Verbose
```

#### Execution with Logging
```powershell
# Run with transcript logging
$LogPath = "C:\Temp\NutanixV4Setup\install-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
Start-Transcript -Path $LogPath

try {
    .\Install-NtnxV4ApiEnvironment.ps1 -Verbose
    Write-Host "✅ Installation completed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    throw
} finally {
    Stop-Transcript
    Write-Host "📄 Log saved to: $LogPath" -ForegroundColor Yellow
}
```

## Post-Installation Verification

### Step 7: Verify Installation
```powershell
# Check installed PowerShell modules
Get-Module -ListAvailable | Where-Object Name -like "*Nutanix*"

# Check if Nutanix V4 API module is available
if (Get-Module -ListAvailable -Name "Nutanix.Prism.v4") {
    Write-Host "✅ Nutanix V4 API module installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Nutanix V4 API module not found" -ForegroundColor Red
}

# Test module import
try {
    Import-Module Nutanix.Prism.v4 -Force
    Write-Host "✅ Module imported successfully" -ForegroundColor Green
    Get-Command -Module Nutanix.Prism.v4 | Select-Object Name | Sort-Object Name
} catch {
    Write-Host "❌ Failed to import module: $($_.Exception.Message)" -ForegroundColor Red
}
```

### Step 8: Test API Connectivity (Optional)
```powershell
# Test connection to Nutanix cluster (replace with your cluster details)
$ClusterIP = "YOUR_CLUSTER_IP"
$Username = "YOUR_USERNAME"
$Password = "YOUR_PASSWORD"

# Create credential object
$SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force
$Credential = New-Object System.Management.Automation.PSCredential($Username, $SecurePassword)

# Test connection (adjust based on actual V4 API cmdlets)
try {
    # Example connection test (modify based on actual V4 API commands)
    Connect-NutanixCluster -Server $ClusterIP -Credential $Credential
    Write-Host "✅ Successfully connected to Nutanix cluster" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to connect to cluster: $($_.Exception.Message)" -ForegroundColor Red
}
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Execution Policy Restriction
```powershell
# Solution: Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

#### Issue: Git Authentication Failure
```powershell
# Solution: Use personal access token
# 1. Generate PAT in GitHub settings
# 2. Use token in clone URL:
git clone https://YOUR_TOKEN@github.com/hardevsanghera/runner-setup_v4api.git
```

#### Issue: PowerShell Module Installation Failure
```powershell
# Solution: Install PowerShellGet and update package providers
Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
Install-Module -Name PowerShellGet -Force -AllowClobber
```

#### Issue: TLS/SSL Connection Errors
```powershell
# Solution: Enable TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

## Environment Validation Script

### Step 9: Create Validation Script
```powershell
# Create a validation script for future use
$ValidationScript = @'
# Nutanix V4 API Environment Validation Script
Write-Host "=== Nutanix V4 API Environment Validation ===" -ForegroundColor Cyan

# Check PowerShell version
Write-Host "`n🔍 PowerShell Version:" -ForegroundColor Yellow
$PSVersionTable.PSVersion

# Check execution policy
Write-Host "`n🔍 Execution Policy:" -ForegroundColor Yellow
Get-ExecutionPolicy -List

# Check Nutanix modules
Write-Host "`n🔍 Nutanix Modules:" -ForegroundColor Yellow
$NutanixModules = Get-Module -ListAvailable | Where-Object Name -like "*Nutanix*"
if ($NutanixModules) {
    $NutanixModules | Select-Object Name, Version, ModuleBase
} else {
    Write-Host "❌ No Nutanix modules found" -ForegroundColor Red
}

# Check V4 API specific module
Write-Host "`n🔍 V4 API Module Test:" -ForegroundColor Yellow
try {
    Import-Module Nutanix.Prism.v4 -ErrorAction Stop
    Write-Host "✅ V4 API module loaded successfully" -ForegroundColor Green
    
    # List available commands
    $V4Commands = Get-Command -Module Nutanix.Prism.v4
    Write-Host "📋 Available V4 API Commands: $($V4Commands.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to load V4 API module: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
'@

# Save validation script
$ValidationScript | Out-File -FilePath "C:\Temp\NutanixV4Setup\Validate-NutanixV4Environment.ps1" -Encoding UTF8
Write-Host "💾 Validation script saved to: C:\Temp\NutanixV4Setup\Validate-NutanixV4Environment.ps1" -ForegroundColor Green
```

## Cleanup (Optional)

### Step 10: Clean Up Installation Files
```powershell
# Remove cloned repositories if no longer needed
# WARNING: Only run this after successful installation and verification
<#
Remove-Item "C:\Temp\NutanixV4Setup\ntnx-v4api-cats" -Recurse -Force
Remove-Item "C:\Temp\NutanixV4Setup\runner-setup_v4api" -Recurse -Force
#>

# Keep validation script and logs for future reference
Write-Host "📋 Installation files preserved for troubleshooting" -ForegroundColor Yellow
Write-Host "📁 Location: C:\Temp\NutanixV4Setup\" -ForegroundColor Yellow
```

## Security Considerations

### Important Security Notes
- **Credentials**: Never hardcode credentials in scripts
- **Access Tokens**: Store GitHub PATs securely and rotate regularly
- **Execution Policy**: Revert to restricted policy after installation if required
- **Firewall**: Ensure appropriate firewall rules for Nutanix API access
- **Logging**: Review logs for sensitive information before sharing

### Recommended Security Practices
```powershell
# Use credential manager for storing sensitive information
# Install-Module -Name Microsoft.PowerShell.SecretManagement
# Install-Module -Name Microsoft.PowerShell.SecretStore

# Store credentials securely
# Set-Secret -Name "NutanixCredential" -Secret $Credential
# $StoredCredential = Get-Secret -Name "NutanixCredential"
```

---

**Note**: This guide assumes the `Install-NtnxV4ApiEnvironment.ps1` script exists in the experimental folder of the ntnx-v4api-cats repository. The exact parameters and execution method may vary based on the actual script implementation. Always review the script documentation and parameters before execution.