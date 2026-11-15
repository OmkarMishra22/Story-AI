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

# Import direct Flask application instance
from app import app

@app.errorhandler(500)
def handle_internal_error(e):
    import traceback
    return f"<h2>Story AL — Internal Server Error</h2><pre>{traceback.format_exc()}</pre>", 500

if __name__ == "__main__":
    app.run()
