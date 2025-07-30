# Windows Troubleshooting Script for Quiz Master

Write-Host "🔧 Quiz Master Windows Troubleshooter" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

Write-Host "This script will help you fix common Windows issues:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Fix PowerShell Execution Policy" -ForegroundColor Cyan
Write-Host "2. Check Python Installation" -ForegroundColor Cyan
Write-Host "3. Check Node.js Installation" -ForegroundColor Cyan
Write-Host "4. Check Database Status" -ForegroundColor Cyan
Write-Host "5. Reset Database" -ForegroundColor Cyan
Write-Host "6. Install Redis" -ForegroundColor Cyan
Write-Host "7. Test All Components" -ForegroundColor Cyan
Write-Host "8. Exit" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-8)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🔧 Fixing PowerShell Execution Policy..." -ForegroundColor Yellow
        
        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Write-Host "✅ Execution policy updated successfully!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to update execution policy" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
        }
    }
    "2" {
        Write-Host ""
        Write-Host "🐍 Checking Python Installation..." -ForegroundColor Yellow
        
        try {
            $pythonVersion = python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
            } else {
                Write-Host "❌ Python not found or not in PATH" -ForegroundColor Red
                Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Python not found" -ForegroundColor Red
            Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
        }
    }
    "3" {
        Write-Host ""
        Write-Host "📦 Checking Node.js Installation..." -ForegroundColor Yellow
        
        try {
            $nodeVersion = node --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
            } else {
                Write-Host "❌ Node.js not found or not in PATH" -ForegroundColor Red
                Write-Host "Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Node.js not found" -ForegroundColor Red
            Write-Host "Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host ""
        Write-Host "🗄️  Checking Database Status..." -ForegroundColor Yellow
        
        if (Test-Path "check_db.py") {
            try {
                python check_db.py
            } catch {
                Write-Host "❌ Failed to check database" -ForegroundColor Red
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ check_db.py not found" -ForegroundColor Red
        }
    }
    "5" {
        Write-Host ""
        Write-Host "🔄 Resetting Database..." -ForegroundColor Yellow
        
        if (Test-Path "reset_db.py") {
            try {
                python reset_db.py
                Write-Host "✅ Database reset successfully!" -ForegroundColor Green
            } catch {
                Write-Host "❌ Failed to reset database" -ForegroundColor Red
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ reset_db.py not found" -ForegroundColor Red
        }
    }
    "6" {
        Write-Host ""
        Write-Host "🔧 Installing Redis..." -ForegroundColor Yellow
        
        if (Test-Path "install_redis.py") {
            try {
                python install_redis.py
                Write-Host "✅ Redis installation completed!" -ForegroundColor Green
            } catch {
                Write-Host "❌ Failed to install Redis" -ForegroundColor Red
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ install_redis.py not found" -ForegroundColor Red
        }
    }
    "7" {
        Write-Host ""
        Write-Host "🧪 Testing All Components..." -ForegroundColor Yellow
        
        # Test Python
        Write-Host "Testing Python..." -ForegroundColor Cyan
        try {
            $pythonVersion = python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Python: OK" -ForegroundColor Green
            } else {
                Write-Host "❌ Python: FAILED" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Python: FAILED" -ForegroundColor Red
        }
        
        # Test Node.js
        Write-Host "Testing Node.js..." -ForegroundColor Cyan
        try {
            $nodeVersion = node --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Node.js: OK" -ForegroundColor Green
            } else {
                Write-Host "❌ Node.js: FAILED" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Node.js: FAILED" -ForegroundColor Red
        }
        
        # Test Database
        Write-Host "Testing Database..." -ForegroundColor Cyan
        if (Test-Path "check_db.py") {
            try {
                python check_db.py
            } catch {
                Write-Host "❌ Database: FAILED" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Database: check_db.py not found" -ForegroundColor Red
        }
        
        # Test Scripts
        Write-Host "Testing Scripts..." -ForegroundColor Cyan
        $scripts = @("start.ps1", "start.bat", "run.bat", "run.ps1")
        foreach ($script in $scripts) {
            if (Test-Path $script) {
                Write-Host "✅ $script: OK" -ForegroundColor Green
            } else {
                Write-Host "❌ $script: NOT FOUND" -ForegroundColor Red
            }
        }
    }
    "8" {
        Write-Host ""
        Write-Host "Goodbye!" -ForegroundColor Green
        Write-Host ""
        exit
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please enter 1-8." -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') 