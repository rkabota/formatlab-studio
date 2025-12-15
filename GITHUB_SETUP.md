# FormatLab Studio - GitHub Setup & Push Instructions

## Prerequisites

- GitHub account (create at https://github.com if needed)
- Git CLI installed (already verified: `/opt/homebrew/bin/git`)
- SSH key or GitHub Personal Access Token for authentication

## Step 1: Create Repository on GitHub

### Option A: Create via GitHub Web UI
1. Go to https://github.com/new
2. Repository name: `formatlab-studio`
3. Description: "JSON-native visual generation console for Bria FIBO hackathon"
4. Set to **Public** (required for hackathon visibility)
5. Do NOT initialize with README (you already have one)
6. Click "Create repository"

### Option B: Create via GitHub CLI (if installed)
```bash
gh repo create formatlab-studio --public --source=. --remote=origin --push
```

## Step 2: Add Remote & Push

### Using HTTPS (requires Personal Access Token):
```bash
cd /Users/macminim4pro/formatlab-studio

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/formatlab-studio.git

# Rename branch if needed (GitHub uses 'main' by default)
git branch -M main

# Push all commits
git push -u origin main
```

### Using SSH (recommended if SSH key configured):
```bash
cd /Users/macminim4pro/formatlab-studio

# Add GitHub as remote (SSH)
git remote add origin git@github.com:YOUR_USERNAME/formatlab-studio.git

# Push
git push -u origin main
```

## Step 3: Verify Push

```bash
git log --oneline
git remote -v  # Should show your GitHub URL
```

## Commit History to Push

You have **5 clean commits** ready:

```
8fe0cc8 Implement real Bria FIBO API V2 with async polling
78a1e13 Add real FIBO and Cerebras LLM integration
898a4f1 Add comprehensive implementation summary and status document
f3dca3f Add core services: patcher, timeline_store, drift meter
667f030 Initial commit: FormatLab Studio - JSON-native visual generation
```

## Files Being Pushed

**Total**: 37 files, ~6000 lines of code

### Backend (Python FastAPI)
- `backend/app/main.py` - FastAPI application
- `backend/app/settings.py` - Configuration
- `backend/app/routers/` - 5 API endpoints (health, analyze, translate, generate, export)
- `backend/app/services/` - 8 service modules:
  - `fibo_client.py` - **Real FIBO V2 API integration**
  - `cerebras_translator.py` - **Real Cerebras LLM translation**
  - `patcher.py` - JSON Patch operations
  - `timeline_store.py` - Version history
  - `drift.py` - Change metrics
  - `hdr16.py` - 16-bit export
  - `storage.py` - File management
  - `translator.py` - Rule-based fallback

### Frontend (React/TypeScript)
- `frontend/package.json`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/api.ts`
- `frontend/src/components/` - UI components

### Schemas
- `schemas/formatlab.scene.schema.json`
- `schemas/formatlab.patch.schema.json`

### Documentation
- `README.md` - 500+ lines
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `docs/demo_script.md` - 3-minute demo
- `docs/LOVABLE_FRONTEND_PROMPT.md` - Lovable integration
- `.env.example` - Configuration template
- `docker-compose.yml` - Docker orchestration

### Examples
- `examples/base_scene.json`
- `examples/patch_examples/edit_001.patch.json`

### Config
- `requirements.txt` - Python dependencies
- `backend/pyproject.toml`
- `.gitignore`
- `.env` (local only - NOT committed)

## What to do after pushing:

### 1. Add GitHub Topics
On your GitHub repo page:
- Settings → Topics
- Add: `hackathon`, `image-generation`, `json-native`, `fibo`, `bria`

### 2. Update README badges (optional)
Add to top of README.md:
```markdown
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black)](https://nextjs.org/)
```

### 3. Set as hackathon entry
- GitHub profile → "About" → Add link to repository
- Include: "Bria FIBO Hackathon Entry - JSON-native visual generation"

### 4. Enable GitHub Pages (optional)
- Settings → Pages
- Set source to `/docs` folder
- This makes demo_script.md accessible as website

## Environment Variables for Contest

When submitting to the contest, judges need:

**.env for Local Testing:**
```bash
# Get these from:
FIBO_API_KEY=<from https://bria.ai>
CEREBRAS_API_KEY=csk-dpvv4653fh4rk2k9y2p2nyhjvy8jw6wyp66xcrykvj33nkj4

# These are fine as-is:
FIBO_API_URL=https://api.bria.ai/fibo
CEREBRAS_API_URL=https://api.cerebras.ai/v1
DEMO_MODE=False  # Set to False for real generation
```

## Troubleshooting

### "fatal: not a git repository"
```bash
cd /Users/macminim4pro/formatlab-studio
git status  # Should work
```

### "Permission denied" when pushing via SSH
- Verify SSH key: `ssh -T git@github.com`
- If fails, generate new key: `ssh-keygen -t ed25519`
- Add to GitHub: https://github.com/settings/keys

### "remote: Repository not found"
- Check username is correct in URL
- Verify repository exists on GitHub
- Check you have push permissions

### "rejected: updates were rejected"
This shouldn't happen with a brand new repo, but if it does:
```bash
git pull origin main --rebase
git push -u origin main
```

## GitHub Submission Checklist

- [ ] Repository created and public
- [ ] All commits pushed
- [ ] README visible on GitHub
- [ ] Topics added
- [ ] GitHub profile links to repo
- [ ] Contains IMPLEMENTATION_SUMMARY.md
- [ ] Contains demo_script.md
- [ ] .env.example has all required variables
- [ ] No `.env` file committed (security)
- [ ] All Python dependencies in requirements.txt
- [ ] Clone & test locally works:
  ```bash
  git clone <your-repo>
  cd formatlab-studio/backend
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python -m uvicorn app.main:app
  ```

## Submit to Contest

Once pushed to GitHub:

1. **Get Repo URL**: `https://github.com/YOUR_USERNAME/formatlab-studio`
2. **Share with judges** via:
   - Direct GitHub link
   - Contest submission form
   - Email to hackathon organizers

3. **Include in submission**:
   - GitHub repository URL
   - Bria FIBO Hackathon Entry
   - Quick start: `cd backend && source venv/bin/activate && python -m uvicorn app.main:app`
   - Demo: `cd frontend && npm run dev`

## Real API Keys for Contest

When submitting with real generation:

1. **FIBO_API_KEY**
   - Register at https://bria.ai
   - Get API key from dashboard
   - Set in `.env`: `FIBO_API_KEY=your_key_here`

2. **CEREBRAS_API_KEY**
   - Already configured: `csk-dpvv4653fh4rk2k9y2p2nyhjvy8jw6wyp66xcrykvj33nkj4`
   - This enables real LLM translation
   - No additional setup needed

3. **Set DEMO_MODE=False**
   - Change in `.env` to enable real generation
   - Keep as `True` for testing without API keys

---

## Ready to Go! 🚀

Your repository is ready to push. Once on GitHub:

```bash
# Clone, test, and verify it works
git clone https://github.com/YOUR_USERNAME/formatlab-studio.git
cd formatlab-studio/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app

# Should see: "Uvicorn running on http://0.0.0.0:8000"
# Visit: http://localhost:8000/docs for API docs
```

**Happy submitting!** 🎉
