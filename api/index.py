import os
import sys

# Forward directly to root index.py app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from index import app

if __name__ == "__main__":
    app.run()
