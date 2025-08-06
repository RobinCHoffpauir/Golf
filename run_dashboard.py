#!/usr/bin/env python3
"""
Simple script to run the Streamlit dashboard
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit dashboard"""
    try:
        # Change to the project directory
        os.chdir('/home/project')
        
        # Run streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'dashboard.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ])
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error running dashboard: {e}")

if __name__ == "__main__":
    main()