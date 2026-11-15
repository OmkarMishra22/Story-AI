"""
Story AL — Vercel Serverless Function Entrypoint
Routes incoming HTTP requests to the WSGI Flask application.
"""

import os
import sys

# Ensure lorekeeper directory is on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
lorekeeper_dir = os.path.join(root_dir, "lorekeeper")

if lorekeeper_dir not in sys.path:
    sys.path.insert(0, lorekeeper_dir)

# Ensure serverless environment flag is set
os.environ["VERCEL"] = "1"

from app import app

# Vercel looks for 'app' as the WSGI callable
if __name__ == "__main__":
    app.run()
