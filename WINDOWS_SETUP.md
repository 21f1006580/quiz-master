# Windows Setup Guide

## 🚀 Quick Start

### **Easiest Method: Use the Launcher**
1. Double-click `run.bat`
2. Choose your preferred startup method
3. Follow the prompts

### **Manual Method**

#### **Option 1: PowerShell (Recommended)**
1. Right-click in your project folder
2. Select "Open PowerShell window here"
3. Run: `.\start.ps1`

#### **Option 2: Command Prompt**
1. Right-click in your project folder
2. Select "Open command window here"
3. Run: `start.bat`

## 🔧 Troubleshooting

### **"start.bat is not recognized" Error**

This happens when you try to run the script incorrectly. Here's how to fix it:

#### **Method 1: Use Command Prompt**
```cmd
# Open Command Prompt (cmd)
# Navigate to your project folder
cd C:\path\to\quiz-master

# Run the script
start.bat
```

#### **Method 2: Use PowerShell**
```powershell
# Open PowerShell
# Navigate to your project folder
cd C:\path\to\quiz-master

# Run the script
.\start.ps1
```

#### **Method 3: Double-Click**
1. Open File Explorer
2. Navigate to your quiz-master folder
3. Double-click `start.bat`

### **PowerShell Execution Policy Error**

If you get "execution policy" errors:

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **"python is not recognized" Error**

Python is not in your PATH. Fix this by:

1. **Reinstall Python** and check "Add Python to PATH" during installation
2. **Or add Python manually** to your PATH environment variable

### **"node is not recognized" Error**

Node.js is not installed or not in PATH. Install it from:
https://nodejs.org/

## 📋 Step-by-Step Instructions

### **First Time Setup:**

1. **Install Requirements:**
   - Python 3.8+: https://python.org
   - Node.js 16+: https://nodejs.org

2. **Open PowerShell:**
   - Press `Win + X`
   - Select "Windows PowerShell" or "Terminal"

3. **Navigate to Project:**
   ```powershell
   cd C:\path\to\your\quiz-master
   ```

4. **Set Execution Policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

5. **Run the Application:**
   ```powershell
   .\start.ps1
   ```

### **For Troubleshooting 422 Errors:**

1. **Check Database Status:**
   ```powershell
   python check_db.py
   ```

2. **Reset Database:**
   ```powershell
   python reset_db.py
   python init_db.py
   ```

2. **Use Debug Mode:**
   ```powershell
   .\start_debug.ps1
   ```

3. **Test JWT:**
   ```powershell
   python debug_jwt.py
   ```

## 🎯 Recommended Workflow

### **For First-Time Users:**
1. Use `run.bat` (double-click)
2. Choose option 3 (Debug Mode PowerShell)
3. Follow the prompts

### **For Regular Use:**
1. Use `run.bat` (double-click)
2. Choose option 1 (PowerShell)
3. Follow the prompts

### **For Troubleshooting:**
1. Use `run.bat` (double-click)
2. Choose option 3 (Debug Mode PowerShell)
3. Check the output for errors

## 📁 File Structure

```
quiz-master/
├── run.bat              # Main launcher (double-click this!)
├── start.ps1            # PowerShell startup
├── start_debug.ps1      # PowerShell debug startup
├── start.bat            # Command Prompt startup
├── start_debug.bat      # Command Prompt debug startup
├── debug_jwt.py         # JWT debugging tool
├── reset_db.py          # Database reset tool
└── TROUBLESHOOTING.md   # Troubleshooting guide
```

## 🚨 Common Issues

### **Issue: "The term 'start.ps1' is not recognized"**
**Solution:** You're in Command Prompt. Use PowerShell instead:
```powershell
.\start.ps1
```

### **Issue: "start.bat is not recognized"**
**Solution:** You're in PowerShell. Use Command Prompt instead:
```cmd
start.bat
```

### **Issue: Execution Policy Error**
**Solution:** Run this in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Issue: Port Already in Use**
**Solution:** Check what's using the ports:
```cmd
netstat -an | findstr :5001
netstat -an | findstr :8080
```

## ✅ Success Indicators

When everything works correctly, you should see:
- ✅ Python found: [version]
- ✅ Node.js found: [version]
- ✅ npm found: [version]
- ✅ Backend is responding
- ✅ Frontend: http://localhost:8080
- ✅ Backend: http://localhost:5001

## 🆘 Getting Help

If you still have issues:
1. Check `TROUBLESHOOTING.md`
2. Run `python debug_jwt.py`
3. Check the console output for specific error messages 