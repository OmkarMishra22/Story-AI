"""
Story AL — GitHub Push Utility
Helps you push your local repository to GitHub.

Usage:
    python push_to_github.py https://github.com/<your-username>/<your-repo-name>.git
"""

import sys
import os

try:
    from dulwich.repo import Repo
    from dulwich import porcelain
except ImportError:
    print("[Error] dulwich library is required. Run: pip install dulwich")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("Story AL — Push to GitHub Guide")
        print("=" * 70)
        print("To push this repository to GitHub:")
        print()
        print("Step 1. Create a new empty repository at https://github.com/new")
        print("        (Leave 'Add a README' unchecked)")
        print()
        print("Step 2. Run:")
        print("        python push_to_github.py https://github.com/<YOUR_USER>/<REPO>.git")
        print()
        print("Alternatively, if you have Git installed, run:")
        print("        git remote add origin https://github.com/<YOUR_USER>/<REPO>.git")
        print("        git branch -M main")
        print("        git push -u origin main")
        print("=" * 70)
        return

    remote_url = sys.argv[1].strip()
    repo = Repo(".")

    try:
        # Add or update origin
        config = repo.get_config()
        config.set(("remote", "origin"), "url", remote_url.encode("utf-8"))
        config.write_to_path()
        print(f"[OK] Configured remote origin: {remote_url}")

        print("[...] Pushing branch 'main' to GitHub...")
        porcelain.push(repo, remote_url, refspecs=[b"refs/heads/main"])
        print("[SUCCESS] Repository successfully pushed to GitHub!")
        print(f"View your repository at: {remote_url.replace('.git', '')}")
    except Exception as e:
        print(f"[!] Push error: {e}")
        print("\nNote: GitHub requires a Personal Access Token (PAT) for HTTPS authentication.")
        print("Format: https://<TOKEN>@github.com/<YOUR_USER>/<REPO>.git")
        print("Or use GitHub Desktop: File -> Add Local Repository -> Select this folder -> Publish Repository.")

if __name__ == "__main__":
    main()
