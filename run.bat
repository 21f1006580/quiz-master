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
powershell -ExecutionPolicy Bypass -File "start.ps1"
goto end

:batch
echo.
echo Starting with Command Prompt...
echo.
call start.bat
goto end

:debug_powershell
echo.
echo Starting Debug Mode with PowerShell...
echo.
powershell -ExecutionPolicy Bypass -File "start_debug.ps1"
goto end

:debug_batch
echo.
echo Starting Debug Mode with Command Prompt...
echo.
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