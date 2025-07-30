# Quiz Master Troubleshooting Guide

## Common Issues and Solutions

### 1. 422 Errors (JWT Token Issues)

**Symptoms:**
- Getting 422 errors when accessing protected endpoints
- Dashboard not loading properly
- Authentication issues

**Solutions:**

#### Option A: Reset Database and JWT Tokens
```bash
# Windows
python reset_db.py
python seed_data.py

# Mac/Linux
python3 reset_db.py
python3 seed_data.py
```

#### Option B: Clear Browser Storage
1. Open browser developer tools (F12)
2. Go to Application/Storage tab
3. Clear localStorage and sessionStorage
4. Refresh the page

#### Option C: Debug JWT Tokens
```bash
# Run the debug script
python debug_jwt.py
```

### 2. Startup Issues

**Symptoms:**
- Scripts not working on Windows
- Port conflicts
- Missing dependencies

**Solutions:**

#### Use Debug Scripts
```bash
# Windows
start_debug.bat

# Mac/Linux
chmod +x start_debug.sh
./start_debug.sh
```

#### Check Port Availability
```bash
# Check if ports are in use
netstat -an | findstr :5001  # Windows
lsof -i :5001                 # Mac/Linux
```

#### Manual Startup
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
npm run serve

# Terminal 3: Celery Worker (if Redis available)
python celery_worker.py
```

### 3. Database Issues

**Symptoms:**
- Database not found
- Migration errors
- Data corruption

**Solutions:**

#### Reset Database
```bash
python reset_db.py
python seed_data.py
```

#### Check Database File
```bash
# Verify database exists
ls -la quizmaster.db
```

### 4. Redis/Celery Issues

**Symptoms:**
- Background tasks not working
- Celery worker errors

**Solutions:**

#### Install Redis
```bash
# Mac
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Download from https://redis.io/download
```

#### Test Redis Connection
```bash
redis-cli ping
# Should return "PONG"
```

### 5. Frontend Issues

**Symptoms:**
- Vue app not loading
- API calls failing
- CORS errors

**Solutions:**

#### Clear Node Modules
```bash
rm -rf node_modules package-lock.json
npm install
```

#### Check API URL
Verify `src/services/api.js` has correct base URL:
```javascript
baseURL: 'http://localhost:5001/api'
```

### 6. Environment Issues

**Symptoms:**
- Python path issues
- Virtual environment problems
- Missing dependencies

**Solutions:**

#### Recreate Virtual Environment
```bash
# Windows
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Check Python Version
```bash
python --version  # Should be 3.8+
```

### 7. JWT Token Debugging

**Common JWT Issues:**
1. Token expiration
2. Invalid token format
3. Missing claims
4. Secret key mismatch

**Debug Steps:**
1. Run `python debug_jwt.py`
2. Check browser network tab for 401/422 responses
3. Verify token in localStorage
4. Check server logs for JWT errors

### 8. Platform-Specific Issues

#### Windows
- Use `start_debug.bat` instead of `start.bat`
- Ensure Python and Node.js are in PATH
- Run as Administrator if needed

#### Mac/Linux
- Use `start_debug.sh` instead of `start.sh`
- Make scripts executable: `chmod +x *.sh`
- Check file permissions

### 9. Performance Issues

**Symptoms:**
- Slow loading
- Timeout errors
- Memory issues

**Solutions:**

#### Optimize Database
```bash
# Recreate database with proper indexes
python reset_db.py
python seed_data.py
```

#### Check Resource Usage
```bash
# Monitor processes
top
htop
```

### 10. Logging and Debugging

#### Enable Debug Mode
```bash
export FLASK_DEBUG=1
python app.py
```

#### Check Logs
- Backend logs: Console output
- Frontend logs: Browser developer tools
- Network tab: API requests/responses

### Quick Fix Checklist

1. ✅ Reset database: `python reset_db.py && python seed_data.py`
2. ✅ Clear browser storage
3. ✅ Use debug startup scripts
4. ✅ Check all services are running
5. ✅ Verify ports are available
6. ✅ Test with debug script: `python debug_jwt.py`

### Emergency Reset

If nothing works, perform a complete reset:

```bash
# 1. Stop all processes
# 2. Reset database
python reset_db.py
python seed_data.py

# 3. Clear browser data
# 4. Restart with debug script
./start_debug.sh  # or start_debug.bat
```

### Support

If issues persist:
1. Check the logs for specific error messages
2. Run the debug script and share output
3. Verify all dependencies are installed
4. Test on a different browser/device 