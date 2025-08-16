#!/usr/bin/env python3
"""
Main entry point for the analytics dashboard.

Run this script to start the Streamlit analytics dashboard.
"""

import os
import sys
import subprocess


def main():
    """Main entry point for the analytics dashboard."""
    # Get the path to the dashboard module
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(current_dir, "dashboard.py")

    # Launch Streamlit with the dashboard
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching Streamlit dashboard: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
