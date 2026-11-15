"""
Story AL — GitHub Push Utility
Helps you push your local repository to GitHub.

Usage:
    python push_to_github.py
    # or:
    python push_to_github.py https://github.com/<your-username>/<your-repo-name>.git
"""

import sys
import os
import urllib.request
import urllib.error
import json

try:
    from dulwich.repo import Repo
    from dulwich import porcelain
except ImportError:
    print("[Error] dulwich library is required. Run: pip install dulwich")
    sys.exit(1)

def verify_token_permissions(token: str, user: str, repo_name: str):
    """Check if token is valid and has push/write permissions."""
    test_url = f"https://api.github.com/repos/{user}/{repo_name}/git/blobs"
    req = urllib.request.Request(
        test_url,
        data=json.dumps({"content": "ping", "encoding": "utf-8"}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "Story-AL-Pusher",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req) as res:
            return True, "Write permissions verified."
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        if e.code == 401:
            return False, "Token is invalid or expired (401 Unauthorized)."
        elif e.code == 403 or e.code == 404:
            return False, (
                "Permission Denied (403/404): This token does NOT have write permissions.\n\n"
                "HOW TO FIX IN 15 SECONDS:\n"
                "1. Generate a 'Classic' token at: https://github.com/settings/tokens/new\n"
                "2. Give it a name (e.g. 'Story-AL')\n"
                "3. Check the single box: [x] repo (Full control of private repositories)\n"
                "4. Click 'Generate token' and paste it here.\n\n"
                "OR for Fine-Grained Tokens:\n"
                "In token settings -> Repository permissions -> 'Contents' -> Change to 'Read and write'."
            )
        return False, f"HTTP Error {e.code}: {err_body}"
    except Exception as ex:
        return False, f"Connection error: {ex}"

def main():
    repo = Repo(".")

    print("=" * 70)
    print("  Story AL — Push to GitHub Helper")
    print("=" * 70)
    
    user = input("GitHub Username [Press Enter for 'OmkarMishra22']: ").strip() or "OmkarMishra22"
    repo_name = input("Repository Name [Press Enter for 'Story-AI']: ").strip() or "Story-AI"

    print("\nGitHub requires a Personal Access Token with WRITE permissions.")
    print("Direct link to create one with correct permissions:")
    print(">>> https://github.com/settings/tokens/new (Check the '[x] repo' box)\n")
    
    token = input("Paste your Personal Access Token: ").strip()
    if not token:
        print("[!] Token cannot be empty. Please provide a token.")
        return

    print("\n[...] Verifying token permissions on GitHub...")
    ok, msg = verify_token_permissions(token, user, repo_name)
    if not ok:
        print(f"\n[!] Token Check Failed:\n{msg}")
        return

    print(f"[OK] {msg}")

    # Standard authenticated Git URL
    remote_url = f"https://{user}:{token}@github.com/{user}/{repo_name}.git"

    try:
        config = repo.get_config()
        config.set(("remote", "origin"), "url", f"https://github.com/{user}/{repo_name}.git".encode("utf-8"))
        config.write_to_path()

        print(f"\n[...] Pushing complete codebase to branch 'main'...")
        porcelain.push(repo, remote_url, refspecs=[b"+refs/heads/main:refs/heads/main"])
        
        print("\n" + "=" * 70)
        print(" [SUCCESS] Complete codebase successfully pushed to GitHub!")
        print(f" View repository: https://github.com/{user}/{repo_name}")
        print(" Vercel will automatically trigger a new build and deploy now!")
        print("=" * 70)
    except Exception as e:
        print(f"\n[!] Push failed: {e}")

if __name__ == "__main__":
    main()
