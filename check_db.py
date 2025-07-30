#!/usr/bin/env python3
"""
Database check script for Quiz Master application
"""

from init_db import check_database

if __name__ == "__main__":
    print("🔍 Checking database status...")
    print("=" * 40)
    check_database() 