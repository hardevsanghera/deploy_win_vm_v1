# Quick Nutanix V4 API Setup - Copy this script to your Windows VM
# Save as: Quick-Setup-V4API.ps1

# Run this script on your freshly deployed Windows VM
# Right-click PowerShell and "Run as Administrator"

# One-liner execution command (copy this to your VM):
# irm https://raw.githubusercontent.com/hardevsanghera/deploy_win_vm_v1/main/Setup-NutanixV4ApiEnvironment.ps1 | iex

# OR manual execution:

# Step 1: Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Step 2: Create working directory
$WorkDir = "C:\Temp\NutanixV4Setup"
New-Item -ItemType Directory -Path $WorkDir -Force

# Step 3: Download the setup script
$SetupScriptUrl = "https://raw.githubusercontent.com/hardevsanghera/deploy_win_vm_v1/main/Setup-NutanixV4ApiEnvironment.ps1"
$SetupScript = "$WorkDir\Setup-NutanixV4ApiEnvironment.ps1"
Invoke-WebRequest -Uri $SetupScriptUrl -OutFile $SetupScript

# Step 4: Execute the setup script
& $SetupScript -Verbose

Write-Host "`n=== Quick Setup Complete ===" -ForegroundColor Green
Write-Host "📁 All files are in: $WorkDir" -ForegroundColor Yellow
Write-Host "💡 Run validation: $WorkDir\Validate-NutanixV4Environment.ps1" -ForegroundColor Yellow