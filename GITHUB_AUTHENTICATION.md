# GitHub Authentication & Push Instructions

## Issue
Git needs to authenticate with GitHub to push the repository.

## Solution: Use GitHub Personal Access Token (Easiest)

### Step 1: Create GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: `formatlab-studio-push`
4. Select scope: **repo** (Full control of private repositories)
5. Click "Generate token"
6. **COPY the token** (you won't see it again!)

### Step 2: Push with Token
Replace `YOUR_TOKEN` with the token you just created:

```bash
cd /Users/macminim4pro/formatlab-studio

git push -u origin main
# When prompted for password, paste your token instead
```

### Step 3: Save Credentials (Optional but recommended)
To avoid re-entering the token every time:

```bash
# Store credentials (macOS)
git config --global credential.helper osxkeychain

# Then push (it will ask for username/token once, then remember)
git push -u origin main
```

When prompted:
- Username: `rkabota`
- Password: `YOUR_TOKEN`

---

## Alternative: SSH Key (If you have SSH configured)

If you have an SSH key set up:

```bash
# Update remote to SSH
git remote set-url origin git@github.com:rkabota/formatlab-studio.git

# Push
git push -u origin main
```

---

## Alternative: GitHub CLI (If installed)

```bash
# Authenticate
gh auth login

# Select HTTPS or SSH
# Then it handles authentication automatically

# Push
git push -u origin main
```

---

## After Successful Push

You'll see:
```
 * [new branch]      main -> main
Branch 'main' is set up to track remote branch 'main' from 'origin'.
```

Then your repo will be at:
**https://github.com/rkabota/formatlab-studio**

---

## Troubleshooting

### "fatal: could not read Username"
- Means authentication isn't cached
- Use token method above

### "fatal: 'origin' does not appear to be a 'git' repository"
- Make sure you're in `/Users/macminim4pro/formatlab-studio`
- Run: `pwd` and `git remote -v`

### "403 Forbidden"
- Token doesn't have right permissions
- Make sure "repo" scope is selected
- Generate a new token

### "Repository not found"
- Make sure you created the repository on GitHub first
- Go to: https://github.com/new
- Create public repository: `formatlab-studio`
- Then push

---

## Quick Step-by-Step

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `formatlab-studio-push`
4. Check: `repo` (full scope)
5. Generate and COPY the token
6. Run in terminal:
   ```bash
   cd /Users/macminim4pro/formatlab-studio
   git push -u origin main
   ```
7. Username: `rkabota`
8. Password: Paste your token
9. Done! 🎉

---

Your repo will be at: https://github.com/rkabota/formatlab-studio
