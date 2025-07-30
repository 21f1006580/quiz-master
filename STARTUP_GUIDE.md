# Quiz Master Startup Guide

## Available Startup Scripts

### Windows Users

#### 1. PowerShell Scripts (Recommended)
```powershell
# Normal startup
.\start.ps1

# Debug startup (with enhanced error handling)
.\start_debug.ps1
```

#### 2. Batch Scripts
```cmd
# Normal startup
start.bat

# Debug startup (with enhanced error handling)
start_debug.bat
```

### Mac/Linux Users

#### 1. Shell Scripts
```bash
# Make scripts executable (first time only)
chmod +x start.sh start_debug.sh

# Normal startup
./start.sh

# Debug startup (with enhanced error handling)
./start_debug.sh
```

## Which Script Should You Use?

### For First-Time Setup or Troubleshooting
Use the **debug** versions:
- Windows: `start_debug.ps1` or `start_debug.bat`
- Mac/Linux: `start_debug.sh`

### For Regular Use
Use the **normal** versions:
- Windows: `start.ps1` or `start.bat`
- Mac/Linux: `start.sh`

## PowerShell Execution Policy Issues

If you get execution policy errors on Windows, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## What Each Script Does

1. **Checks Requirements**: Python, Node.js, npm
2. **Sets Up Environment**: Virtual environment, dependencies
3. **Initializes Database**: Creates and seeds if needed
4. **Starts Services**:
   - Flask backend (port 5001)
   - Vue frontend (port 8080)
   - Celery worker (if Redis available)
   - Celery beat scheduler (if Redis available)

## Debug Scripts vs Normal Scripts

### Debug Scripts Include:
- ✅ Enhanced error handling
- ✅ Health checks
- ✅ Detailed logging
- ✅ Automatic debugging tools installation
- ✅ Better process management

### Normal Scripts Include:
- ✅ Basic error handling
- ✅ Standard startup process
- ✅ Faster execution

## Troubleshooting

### If Scripts Don't Work:

1. **Windows PowerShell Issues**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Permission Issues**:
   - Run as Administrator (Windows)
   - Use `sudo` if needed (Mac/Linux)

3. **Port Conflicts**:
   ```bash
   # Check if ports are in use
   netstat -an | findstr :5001  # Windows
   lsof -i :5001                 # Mac/Linux
   ```

4. **Database Issues**:
   ```bash
   python reset_db.py
   python seed_data.py
   ```

5. **JWT Issues**:
   ```bash
   python debug_jwt.py
   ```

## Manual Startup (Alternative)

If scripts don't work, you can start services manually:

### Terminal 1: Backend
```bash
python app.py
```

### Terminal 2: Frontend
```bash
npm run serve
```

### Terminal 3: Celery Worker (Optional)
```bash
python celery_worker.py
```

## Quick Start Commands

### Windows (PowerShell)
```powershell
# First time
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start_debug.ps1

# Regular use
.\start.ps1
```

### Windows (Command Prompt)
```cmd
start_debug.bat
```

### Mac/Linux
```bash
chmod +x *.sh
./start_debug.sh
```

## Access URLs

After successful startup:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5001
- **Admin Login**: admin@gmail.com / admin123

## Stopping the Application

- **Scripts**: Press `Ctrl+C` or the key indicated
- **Manual**: Stop each terminal process with `Ctrl+C` 