#!/usr/bin/env python
"""
Script to run chat performance tests.

Usage:
    python run_chat_performance_tests.py
"""

import os
import sys
import django
import asyncio

# Setup Django with test database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

# Setup test database
from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
from django.core.management import call_command

# Import after Django setup
from services.chat.test_chat_performance import main

if __name__ == '__main__':
    try:
        # Setup test environment
        setup_test_environment()
        
        # Create test database
        old_db_name = connection.settings_dict['NAME']
        connection.creation.create_test_db(verbosity=0, autoclobber=True, keepdb=False)
        
        try:
            # Run tests
            results = asyncio.run(main())
            # Exit code 0 if critical tests passed (concurrent and load tests)
            # Cache test is informational only
            exit_code = 0 if results['all_passed'] else 1
        finally:
            # Destroy test database
            connection.creation.destroy_test_db(old_db_name, verbosity=0, keepdb=False)
            teardown_test_environment()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
