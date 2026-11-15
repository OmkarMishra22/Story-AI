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

try:
    from dulwich.repo import Repo
    from dulwich import porcelain
except ImportError:
    print("[Error] dulwich library is required. Run: pip install dulwich")
    sys.exit(1)

def main():
    repo = Repo(".")

    if len(sys.argv) >= 2:
        remote_url = sys.argv[1].strip()
    else:
        print("=" * 70)
        print("  Story AL — Push to GitHub Helper")
        print("=" * 70)
        print("Before running, make sure you created an empty repo at:")
        print("https://github.com/new (Leave 'Add a README' unchecked)\n")
        
        user = input("GitHub Username [Press Enter for 'OmkarMishra22']: ").strip() or "OmkarMishra22"
        repo_name = input("Repository Name [Press Enter for 'Story-AI']: ").strip() or "Story-AI"

        print("\nGitHub requires a Personal Access Token (PAT) for command-line access.")
        print("Create one at: https://github.com/settings/tokens (select 'repo' scope)")
        token = input("Personal Access Token (PAT) [Leave blank if using SSH or credential manager]: ").strip()

        if token:
            remote_url = f"https://{token}@github.com/{user}/{repo_name}.git"
        else:
            remote_url = f"https://github.com/{user}/{repo_name}.git"

    try:
        # Add or update origin
        config = repo.get_config()
        config.set(("remote", "origin"), "url", remote_url.encode("utf-8"))
        config.write_to_path()
        safe_url = remote_url.split("@")[-1] if "@" in remote_url else remote_url
        print(f"\n[OK] Configured remote origin: https://{safe_url}")

        print("[...] Pushing complete codebase to GitHub branch 'main'...")
        porcelain.push(repo, remote_url, refspecs=[b"+refs/heads/main:refs/heads/main"])
        print("\n" + "=" * 70)
        print(" [SUCCESS] Complete codebase successfully pushed to GitHub!")
        print(f" View your repository at: https://github.com/{safe_url.replace('.git', '')}")
        print(" Vercel will now automatically trigger a successful build!")
        print("=" * 70)
    except Exception as e:
        print(f"\n[!] Push failed: {e}")
        print("\nTips:")
        print("1. If using HTTPS, ensure your GitHub Personal Access Token has 'repo' permissions.")
        print("2. You can also use GitHub Desktop:")
        print("   Download at https://desktop.github.com -> File -> Add Local Repository -> Publish Repository.")
        print("3. Or install Git for Windows at https://git-scm.com/download/win and run:")
        print("   git remote add origin https://github.com/<USERNAME>/<REPO>.git")
        print("   git push -u origin main")

if __name__ == "__main__":
    main()
