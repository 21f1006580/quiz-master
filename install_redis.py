#!/usr/bin/env python3
"""
Redis installation script for Quiz Master application
"""

import os
import sys
import platform
import subprocess
import shutil

def detect_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "mac"
    elif system == "linux":
        # Try to detect Linux distribution
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "ubuntu" in content or "debian" in content:
                    return "ubuntu"
                elif "centos" in content or "rhel" in content or "fedora" in content:
                    return "centos"
                else:
                    return "linux"
        except:
            return "linux"
    else:
        return "unknown"

def check_redis_installed():
    """Check if Redis is already installed"""
    return shutil.which("redis-cli") is not None

def install_redis_windows():
    """Install Redis on Windows"""
    print("🔄 Installing Redis on Windows...")
    
    # Check if chocolatey is available
    if shutil.which("choco"):
        print("📦 Using Chocolatey to install Redis...")
        try:
            subprocess.run(["choco", "install", "redis-64", "-y"], check=True)
            print("✅ Redis installed successfully via Chocolatey!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Redis via Chocolatey")
    
    # Check if winget is available
    if shutil.which("winget"):
        print("📦 Using winget to install Redis...")
        try:
            subprocess.run(["winget", "install", "Redis.Redis", "--accept-package-agreements"], check=True)
            print("✅ Redis installed successfully via winget!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Redis via winget")
    
    print("⚠️  Automatic installation failed. Please install Redis manually:")
    print("   1. Download from https://redis.io/download")
    print("   2. Or install Chocolatey: https://chocolatey.org/install")
    print("   3. Then run: choco install redis-64")
    return False

def install_redis_mac():
    """Install Redis on macOS"""
    print("🔄 Installing Redis on macOS...")
    
    # Check if Homebrew is available
    if shutil.which("brew"):
        print("📦 Using Homebrew to install Redis...")
        try:
            subprocess.run(["brew", "install", "redis"], check=True)
            subprocess.run(["brew", "services", "start", "redis"], check=True)
            print("✅ Redis installed and started successfully via Homebrew!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Redis via Homebrew")
    
    print("⚠️  Homebrew not found. Please install Homebrew first:")
    print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    print("   Then run: brew install redis && brew services start redis")
    return False

def install_redis_ubuntu():
    """Install Redis on Ubuntu/Debian"""
    print("🔄 Installing Redis on Ubuntu/Debian...")
    
    try:
        # Update package list
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        
        # Install Redis
        subprocess.run(["sudo", "apt-get", "install", "-y", "redis-server"], check=True)
        
        # Start Redis service
        subprocess.run(["sudo", "systemctl", "start", "redis-server"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "redis-server"], check=True)
        
        print("✅ Redis installed and started successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Redis: {e}")
        return False

def install_redis_centos():
    """Install Redis on CentOS/RHEL/Fedora"""
    print("🔄 Installing Redis on CentOS/RHEL/Fedora...")
    
    try:
        # Install Redis
        subprocess.run(["sudo", "yum", "install", "-y", "redis"], check=True)
        
        # Start Redis service
        subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "redis"], check=True)
        
        print("✅ Redis installed and started successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Redis: {e}")
        return False

def install_redis_linux():
    """Install Redis on generic Linux"""
    print("🔄 Installing Redis on Linux...")
    
    # Try different package managers
    package_managers = [
        ("apt-get", ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", "redis-server"]),
        ("yum", ["sudo", "yum", "install", "-y", "redis"]),
        ("dnf", ["sudo", "dnf", "install", "-y", "redis"]),
        ("pacman", ["sudo", "pacman", "-S", "--noconfirm", "redis"]),
    ]
    
    for manager, command in package_managers:
        if shutil.which(manager):
            print(f"📦 Using {manager} to install Redis...")
            try:
                subprocess.run(command, check=True)
                print(f"✅ Redis installed successfully via {manager}!")
                return True
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install Redis via {manager}")
    
    print("⚠️  Could not find a supported package manager.")
    print("   Please install Redis manually for your distribution.")
    return False

def install_redis():
    """Install Redis based on platform"""
    print("🔍 Detecting platform...")
    platform_name = detect_platform()
    print(f"📍 Platform detected: {platform_name}")
    
    if check_redis_installed():
        print("✅ Redis is already installed!")
        return True
    
    print("📦 Redis not found. Installing...")
    
    if platform_name == "windows":
        return install_redis_windows()
    elif platform_name == "mac":
        return install_redis_mac()
    elif platform_name == "ubuntu":
        return install_redis_ubuntu()
    elif platform_name == "centos":
        return install_redis_centos()
    elif platform_name == "linux":
        return install_redis_linux()
    else:
        print("❌ Unsupported platform for automatic Redis installation")
        print("   Please install Redis manually from https://redis.io")
        return False

def test_redis():
    """Test if Redis is working"""
    print("🧪 Testing Redis connection...")
    try:
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis is working correctly!")
            return True
        else:
            print("❌ Redis is not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Failed to test Redis: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Redis Installation for Quiz Master")
    print("=" * 40)
    
    # Check if Redis is already working
    if check_redis_installed() and test_redis():
        print("✅ Redis is already installed and working!")
        return True
    
    # Install Redis
    if install_redis():
        # Test the installation
        if test_redis():
            print("🎉 Redis installation completed successfully!")
            return True
        else:
            print("⚠️  Redis installed but not responding. Please start the Redis service manually.")
            return False
    else:
        print("❌ Redis installation failed. Please install manually.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 