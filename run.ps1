# Quiz Master PowerShell Launcher Script

Write-Host "🚀 Quiz Master Launcher" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""

Write-Host "Choose your startup method:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. PowerShell (Recommended)" -ForegroundColor Cyan
Write-Host "2. Command Prompt (Batch)" -ForegroundColor Cyan
Write-Host "3. Debug Mode (PowerShell)" -ForegroundColor Cyan
Write-Host "4. Debug Mode (Command Prompt)" -ForegroundColor Cyan
Write-Host "5. Exit" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting with PowerShell..." -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path "start.ps1") {
            try {
                & ".\start.ps1"
            } catch {
                Write-Host "❌ PowerShell script failed to run" -ForegroundColor Red
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
                Read-Host "Press Enter to continue"
            }
        } else {
            Write-Host "❌ Error: start.ps1 not found in current directory" -ForegroundColor Red
            Write-Host "Please make sure you're running this from the quiz-master folder" -ForegroundColor Yellow
            Read-Host "Press Enter to continue"
        }
    }
    "2" {
        Write-Host ""
        Write-Host "Starting with Command Prompt..." -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path "start.bat") {
            cmd /c start.bat
        } else {
            Write-Host "❌ Error: start.bat not found in current directory" -ForegroundColor Red
            Write-Host "Please make sure you're running this from the quiz-master folder" -ForegroundColor Yellow
            Read-Host "Press Enter to continue"
        }
    }
    "3" {
        Write-Host ""
        Write-Host "Starting Debug Mode with PowerShell..." -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path "start_debug.ps1") {
            try {
                & ".\start_debug.ps1"
            } catch {
                Write-Host "❌ PowerShell debug script failed to run" -ForegroundColor Red
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
                Read-Host "Press Enter to continue"
            }
        } else {
            Write-Host "❌ Error: start_debug.ps1 not found in current directory" -ForegroundColor Red
            Write-Host "Please make sure you're running this from the quiz-master folder" -ForegroundColor Yellow
            Read-Host "Press Enter to continue"
        }
    }
    "4" {
        Write-Host ""
        Write-Host "Starting Debug Mode with Command Prompt..." -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path "start_debug.bat") {
            cmd /c start_debug.bat
        } else {
            Write-Host "❌ Error: start_debug.bat not found in current directory" -ForegroundColor Red
            Write-Host "Please make sure you're running this from the quiz-master folder" -ForegroundColor Yellow
            Read-Host "Press Enter to continue"
        }
    }
    "5" {
        Write-Host ""
        Write-Host "Goodbye!" -ForegroundColor Green
        Write-Host ""
        exit
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please enter 1-5." -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to continue"
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 