@echo off
REM Quiz Master Launcher Script
REM This script will help you start the application

echo 🚀 Quiz Master Launcher
echo =====================
echo.
echo Choose your startup method:
echo.
echo 1. PowerShell (Recommended)
echo 2. Command Prompt (Batch)
echo 3. Debug Mode (PowerShell)
echo 4. Debug Mode (Command Prompt)
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto powershell
if "%choice%"=="2" goto batch
if "%choice%"=="3" goto debug_powershell
if "%choice%"=="4" goto debug_batch
if "%choice%"=="5" goto exit
goto invalid

:powershell
echo.
echo Starting with PowerShell...
echo.
REM Check if PowerShell script exists
if not exist "start.ps1" (
    echo ❌ Error: start.ps1 not found in current directory
    echo Please make sure you're running this from the quiz-master folder
    pause
    goto end
)
REM Run PowerShell with proper error handling
powershell -ExecutionPolicy Bypass -NoProfile -File "start.ps1"
if errorlevel 1 (
    echo ❌ PowerShell script failed to run
    echo Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    pause
)
goto end

:batch
echo.
echo Starting with Command Prompt...
echo.
REM Check if batch script exists
if not exist "start.bat" (
    echo ❌ Error: start.bat not found in current directory
    echo Please make sure you're running this from the quiz-master folder
    pause
    goto end
)
call start.bat
goto end

:debug_powershell
echo.
echo Starting Debug Mode with PowerShell...
echo.
REM Check if PowerShell debug script exists
if not exist "start_debug.ps1" (
    echo ❌ Error: start_debug.ps1 not found in current directory
    echo Please make sure you're running this from the quiz-master folder
    pause
    goto end
)
REM Run PowerShell debug script with proper error handling
powershell -ExecutionPolicy Bypass -NoProfile -File "start_debug.ps1"
if errorlevel 1 (
    echo ❌ PowerShell debug script failed to run
    echo Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    pause
)
goto end

:debug_batch
echo.
echo Starting Debug Mode with Command Prompt...
echo.
REM Check if batch debug script exists
if not exist "start_debug.bat" (
    echo ❌ Error: start_debug.bat not found in current directory
    echo Please make sure you're running this from the quiz-master folder
    pause
    goto end
)
call start_debug.bat
goto end

:invalid
echo.
echo Invalid choice. Please enter 1-5.
echo.
pause
goto end

:exit
echo.
echo Goodbye!
echo.
pause
goto end

:end
echo.
echo Press any key to exit...
pause >nul 