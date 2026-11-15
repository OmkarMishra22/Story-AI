"""
Story AL — Production Flask Entrypoint for Vercel
"""

import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
lorekeeper_dir = os.path.join(BASE_DIR, "lorekeeper")
if lorekeeper_dir not in sys.path:
    sys.path.insert(0, lorekeeper_dir)

# Serverless environment flag
os.environ["VERCEL"] = "1"

try:
    from app import app as flask_app
except Exception as e:
    import_err = traceback.format_exc()
    from flask import Flask
    flask_app = Flask(__name__)
    
    @flask_app.route('/', defaults={'path': ''})
    @flask_app.route('/<path:path>')
    def catch_all(path):
        return f"<h2>Story AL — Startup Error on Vercel</h2><pre>{import_err}</pre>", 500

class ErrorCatchingWSGI:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, environ, start_response):
        try:
            return self.inner(environ, start_response)
        except Exception:
            err_text = traceback.format_exc()
            print("Serverless Error:", err_text)
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            start_response(status, headers)
            return [f"<h2>Story AL — Serverless Runtime Exception</h2><pre>{err_text}</pre>".encode('utf-8')]

app = ErrorCatchingWSGI(flask_app)

if __name__ == "__main__":
    flask_app.run()
