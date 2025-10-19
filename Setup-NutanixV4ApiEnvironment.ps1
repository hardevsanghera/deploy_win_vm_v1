# Nutanix V4 API Environment Setup Automation Script
# This script automates the setup of Nutanix V4 API environment on a Windows VM

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$WorkingDirectory = "C:\Temp\NutanixV4Setup",
    
    [Parameter(Mandatory = $false)]
    [string]$GitHubToken = "",
    
    [Parameter(Mandatory = $false)]
    [string]$GitHubUsername = "hardevsanghera",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipGitInstall,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force,
    
    [Parameter(Mandatory = $false)]
    [string]$LogPath = ""
)

# Initialize logging
if ([string]::IsNullOrEmpty($LogPath)) {
    $LogPath = "$WorkingDirectory\setup-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
}

# Ensure working directory exists
if (-not (Test-Path $WorkingDirectory)) {
    New-Item -ItemType Directory -Path $WorkingDirectory -Force | Out-Null
}

Start-Transcript -Path $LogPath -Append

try {
    Write-Host "=== Nutanix V4 API Environment Setup ===" -ForegroundColor Cyan
    Write-Host "📁 Working Directory: $WorkingDirectory" -ForegroundColor Yellow
    Write-Host "📄 Log File: $LogPath" -ForegroundColor Yellow
    Write-Host ""

    # Step 1: Environment Preparation
    Write-Host "🔧 Step 1: Preparing PowerShell Environment" -ForegroundColor Green
    
    # Check if running as Administrator
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $IsAdmin) {
        Write-Warning "⚠️  Script is not running as Administrator. Some operations may fail."
        Write-Host "💡 Consider running PowerShell as Administrator for best results." -ForegroundColor Yellow
    }
    
    # Set execution policy
    Write-Host "🔓 Setting execution policy..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✅ Execution policy set successfully" -ForegroundColor Green
    } catch {
        Write-Warning "⚠️  Failed to set execution policy: $($_.Exception.Message)"
    }
    
    # Enable TLS 1.2
    Write-Host "🔒 Enabling TLS 1.2..." -ForegroundColor Yellow
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Host "✅ TLS 1.2 enabled" -ForegroundColor Green

    # Step 2: Install Git (if needed)
    if (-not $SkipGitInstall) {
        Write-Host "`n🔧 Step 2: Checking Git Installation" -ForegroundColor Green
        
        try {
            $GitVersion = git --version 2>$null
            if ($GitVersion) {
                Write-Host "✅ Git already installed: $GitVersion" -ForegroundColor Green
            } else {
                throw "Git not found"
            }
        } catch {
            Write-Host "📥 Installing Git for Windows..." -ForegroundColor Yellow
            
            $GitUrl = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.42.0.2-64-bit.exe"
            $GitInstaller = "$env:TEMP\Git-Installer.exe"
            
            try {
                Invoke-WebRequest -Uri $GitUrl -OutFile $GitInstaller -UseBasicParsing
                Start-Process -FilePath $GitInstaller -ArgumentList "/SILENT" -Wait
                
                # Add Git to PATH
                $GitPath = "C:\Program Files\Git\bin"
                if ($env:PATH -notlike "*$GitPath*") {
                    $env:PATH += ";$GitPath"
                }
                
                # Verify installation
                $GitVersion = git --version 2>$null
                if ($GitVersion) {
                    Write-Host "✅ Git installed successfully: $GitVersion" -ForegroundColor Green
                } else {
                    throw "Git installation verification failed"
                }
            } catch {
                Write-Warning "⚠️  Failed to install Git: $($_.Exception.Message)"
                Write-Host "💡 Please install Git manually and re-run the script with -SkipGitInstall" -ForegroundColor Yellow
                throw
            }
        }
    } else {
        Write-Host "⏭️  Skipping Git installation check" -ForegroundColor Yellow
    }

    # Step 3: Clone Repositories
    Write-Host "`n🔧 Step 3: Cloning Required Repositories" -ForegroundColor Green
    
    Set-Location $WorkingDirectory
    
    # Repository URLs
    $PrivateRepoUrl = "https://github.com/$GitHubUsername/runner-setup_v4api.git"
    $PublicRepoUrl = "https://github.com/$GitHubUsername/ntnx-v4api-cats.git"
    
    # Clone private repository
    $PrivateRepoPath = "$WorkingDirectory\runner-setup_v4api"
    if (Test-Path $PrivateRepoPath) {
        if ($Force) {
            Write-Host "🗑️  Removing existing private repository..." -ForegroundColor Yellow
            Remove-Item $PrivateRepoPath -Recurse -Force
        } else {
            Write-Host "✅ Private repository already exists: $PrivateRepoPath" -ForegroundColor Green
        }
    }
    
    if (-not (Test-Path $PrivateRepoPath)) {
        Write-Host "📥 Cloning private repository..." -ForegroundColor Yellow
        try {
            if (-not [string]::IsNullOrEmpty($GitHubToken)) {
                $AuthUrl = $PrivateRepoUrl -replace "https://", "https://$GitHubToken@"
                git clone $AuthUrl 2>&1 | Out-Host
            } else {
                Write-Host "💡 You may be prompted for GitHub credentials..." -ForegroundColor Yellow
                git clone $PrivateRepoUrl 2>&1 | Out-Host
            }
            
            if (Test-Path $PrivateRepoPath) {
                Write-Host "✅ Private repository cloned successfully" -ForegroundColor Green
            } else {
                throw "Repository clone verification failed"
            }
        } catch {
            Write-Warning "⚠️  Failed to clone private repository: $($_.Exception.Message)"
            Write-Host "💡 Ensure you have access to the repository and correct credentials" -ForegroundColor Yellow
            throw
        }
    }
    
    # Clone public repository
    $PublicRepoPath = "$WorkingDirectory\ntnx-v4api-cats"
    if (Test-Path $PublicRepoPath) {
        if ($Force) {
            Write-Host "🗑️  Removing existing public repository..." -ForegroundColor Yellow
            Remove-Item $PublicRepoPath -Recurse -Force
        } else {
            Write-Host "✅ Public repository already exists: $PublicRepoPath" -ForegroundColor Green
        }
    }
    
    if (-not (Test-Path $PublicRepoPath)) {
        Write-Host "📥 Cloning public repository..." -ForegroundColor Yellow
        try {
            git clone $PublicRepoUrl 2>&1 | Out-Host
            
            if (Test-Path $PublicRepoPath) {
                Write-Host "✅ Public repository cloned successfully" -ForegroundColor Green
            } else {
                throw "Repository clone verification failed"
            }
        } catch {
            Write-Warning "⚠️  Failed to clone public repository: $($_.Exception.Message)"
            throw
        }
    }

    # Step 4: Locate Installation Script
    Write-Host "`n🔧 Step 4: Locating Installation Script" -ForegroundColor Green
    
    $ScriptPath = "$PublicRepoPath\experimental\Install-NtnxV4ApiEnvironment.ps1"
    if (Test-Path $ScriptPath) {
        Write-Host "✅ Installation script found: $ScriptPath" -ForegroundColor Green
        
        # Get script information
        $ScriptInfo = Get-ChildItem $ScriptPath
        Write-Host "📄 Script Details:" -ForegroundColor Yellow
        Write-Host "   Name: $($ScriptInfo.Name)" -ForegroundColor White
        Write-Host "   Size: $([math]::Round($ScriptInfo.Length / 1KB, 2)) KB" -ForegroundColor White
        Write-Host "   Last Modified: $($ScriptInfo.LastWriteTime)" -ForegroundColor White
    } else {
        Write-Error "❌ Installation script not found at: $ScriptPath"
        Write-Host "💡 Please verify the script exists in the experimental folder" -ForegroundColor Yellow
        throw "Installation script not found"
    }

    # Step 5: Analyze Script Parameters
    Write-Host "`n🔧 Step 5: Analyzing Script Parameters" -ForegroundColor Green
    
    try {
        # Get script parameters using AST
        $ScriptContent = Get-Content $ScriptPath -Raw
        $Tokens = $null
        $Errors = $null
        $AST = [System.Management.Automation.Language.Parser]::ParseInput($ScriptContent, [ref]$Tokens, [ref]$Errors)
        
        $ParamBlock = $AST.FindAll({ param($node) $node -is [System.Management.Automation.Language.ParamBlockAst] }, $false)
        
        if ($ParamBlock -and $ParamBlock.Parameters) {
            Write-Host "📋 Script Parameters Found:" -ForegroundColor Yellow
            foreach ($param in $ParamBlock.Parameters) {
                $paramName = $param.Name.VariablePath.UserPath
                $paramType = if ($param.StaticType) { $param.StaticType.Name } else { "Object" }
                Write-Host "   - $paramName [$paramType]" -ForegroundColor White
            }
        } else {
            Write-Host "📋 No parameters found or script uses simple parameter structure" -ForegroundColor Yellow
        }
    } catch {
        Write-Warning "⚠️  Could not analyze script parameters: $($_.Exception.Message)"
        Write-Host "💡 You can review parameters manually using: Get-Help $ScriptPath -Full" -ForegroundColor Yellow
    }

    # Step 6: Execute Installation Script
    Write-Host "`n🔧 Step 6: Executing Installation Script" -ForegroundColor Green
    
    Set-Location (Split-Path $ScriptPath -Parent)
    
    Write-Host "📍 Current Location: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "🚀 Executing: $ScriptPath" -ForegroundColor Yellow
    Write-Host "⏱️  Starting execution..." -ForegroundColor Yellow
    
    try {
        # Execute the installation script with verbose output
        & $ScriptPath -Verbose
        
        Write-Host "✅ Installation script completed successfully" -ForegroundColor Green
    } catch {
        Write-Error "❌ Installation script failed: $($_.Exception.Message)"
        Write-Host "💡 Check the error details above and the log file for more information" -ForegroundColor Yellow
        throw
    }

    # Step 7: Verify Installation
    Write-Host "`n🔧 Step 7: Verifying Installation" -ForegroundColor Green
    
    # Check for Nutanix modules
    $NutanixModules = Get-Module -ListAvailable | Where-Object Name -like "*Nutanix*"
    if ($NutanixModules) {
        Write-Host "✅ Nutanix modules found:" -ForegroundColor Green
        foreach ($module in $NutanixModules) {
            Write-Host "   - $($module.Name) v$($module.Version)" -ForegroundColor White
        }
    } else {
        Write-Warning "⚠️  No Nutanix modules found"
    }
    
    # Test V4 API module specifically
    try {
        $V4Module = Get-Module -ListAvailable -Name "*v4*" | Where-Object Name -like "*Nutanix*"
        if ($V4Module) {
            Import-Module $V4Module.Name -Force
            Write-Host "✅ V4 API module imported successfully: $($V4Module.Name)" -ForegroundColor Green
            
            $V4Commands = Get-Command -Module $V4Module.Name
            Write-Host "📋 Available V4 API Commands: $($V4Commands.Count)" -ForegroundColor Green
        } else {
            Write-Warning "⚠️  V4 API module not found"
        }
    } catch {
        Write-Warning "⚠️  Failed to import V4 API module: $($_.Exception.Message)"
    }

    # Step 8: Generate Summary Report
    Write-Host "`n📊 Installation Summary" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    Write-Host "✅ Setup completed successfully" -ForegroundColor Green
    Write-Host "📁 Working Directory: $WorkingDirectory" -ForegroundColor Yellow
    Write-Host "📄 Log File: $LogPath" -ForegroundColor Yellow
    Write-Host "🔧 PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Yellow
    Write-Host "🔓 Execution Policy: $(Get-ExecutionPolicy -Scope CurrentUser)" -ForegroundColor Yellow
    
    if ($NutanixModules) {
        Write-Host "📦 Nutanix Modules: $($NutanixModules.Count) installed" -ForegroundColor Yellow
    }
    
    Write-Host "`n💡 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Review the installation log: $LogPath" -ForegroundColor White
    Write-Host "2. Test connectivity to your Nutanix cluster" -ForegroundColor White
    Write-Host "3. Explore available V4 API commands" -ForegroundColor White
    Write-Host "4. Run validation script: $WorkingDirectory\Validate-NutanixV4Environment.ps1" -ForegroundColor White

} catch {
    Write-Error "❌ Setup failed: $($_.Exception.Message)"
    Write-Host "📄 Check the log file for details: $LogPath" -ForegroundColor Yellow
    exit 1
} finally {
    Stop-Transcript
}

# Create validation script for future use
$ValidationScriptPath = "$WorkingDirectory\Validate-NutanixV4Environment.ps1"
$ValidationScript = @'
# Nutanix V4 API Environment Validation Script
Write-Host "=== Nutanix V4 API Environment Validation ===" -ForegroundColor Cyan

# Check PowerShell version
Write-Host "`n🔍 PowerShell Version:" -ForegroundColor Yellow
$PSVersionTable.PSVersion

# Check execution policy
Write-Host "`n🔍 Execution Policy:" -ForegroundColor Yellow
Get-ExecutionPolicy -List | Format-Table

# Check Nutanix modules
Write-Host "`n🔍 Nutanix Modules:" -ForegroundColor Yellow
$NutanixModules = Get-Module -ListAvailable | Where-Object Name -like "*Nutanix*"
if ($NutanixModules) {
    $NutanixModules | Select-Object Name, Version, ModuleBase | Format-Table -AutoSize
} else {
    Write-Host "❌ No Nutanix modules found" -ForegroundColor Red
}

# Check V4 API specific module
Write-Host "`n🔍 V4 API Module Test:" -ForegroundColor Yellow
$V4Modules = Get-Module -ListAvailable | Where-Object Name -like "*v4*" | Where-Object Name -like "*Nutanix*"
if ($V4Modules) {
    foreach ($module in $V4Modules) {
        try {
            Import-Module $module.Name -ErrorAction Stop
            Write-Host "✅ $($module.Name) loaded successfully" -ForegroundColor Green
            
            $Commands = Get-Command -Module $module.Name
            Write-Host "📋 Available Commands: $($Commands.Count)" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to load $($module.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ No V4 API modules found" -ForegroundColor Red
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
'@

$ValidationScript | Out-File -FilePath $ValidationScriptPath -Encoding UTF8
Write-Host "`n💾 Validation script created: $ValidationScriptPath" -ForegroundColor Green

Write-Host "`n🎉 Nutanix V4 API Environment Setup Complete!" -ForegroundColor Green