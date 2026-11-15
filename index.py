"""
Story AL — Production Flask Entrypoint for Vercel
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
lorekeeper_dir = os.path.join(BASE_DIR, "lorekeeper")
if lorekeeper_dir not in sys.path:
    sys.path.insert(0, lorekeeper_dir)

os.environ["VERCEL"] = "1"

from app import app

# Vercel looks for 'app' as the WSGI callable
if __name__ == "__main__":
    app.run()
