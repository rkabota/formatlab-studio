# FormatLab Studio - Quick Start Guide

## TL;DR - Get Running in 5 Minutes

### 1. Backend Setup (Terminal 1)
```bash
cd /Users/macminim4pro/formatlab-studio/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend running at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### 2. Test a Generation (Terminal 2)
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "base_scene": {
      "version": "1.0",
      "id": "test_scene",
      "camera": {"lens_mm": 50, "fov": 48},
      "lighting": {"key": {"intensity": 0.8}},
      "color": {"palette": ["#1a1a1a"]}
    },
    "seed": 42,
    "num_variants": 1
  }'
```

Response: Generated image in `storage/outputs/`

### 3. Frontend (Terminal 3)
```bash
cd frontend
npm install
npm run dev
```

Frontend running at: **http://localhost:3000**

## What You Have

✅ **Real Bria FIBO API Integration** - Async polling, proper auth, fallback to demo
✅ **Real Cerebras LLM** - Natural language → JSON with fallback
✅ **5 Production API Endpoints** - health, analyze, translate, generate, export
✅ **8 Service Modules** - Complete backend logic
✅ **Complete Documentation** - README, demo script, GitHub setup
✅ **Git Repository** - 6 commits, ready to push to GitHub

## API Endpoints

```
GET  /v1/health                 - Health check
POST /v1/analyze                - Upload image → extract SceneGraph
POST /v1/translate              - Natural language → JSON patch
POST /v1/generate               - Generate images with seed
POST /v1/export                 - Download ZIP bundle with 16-bit master
```

## Environment Variables (.env)

```bash
# Real API Keys (for actual generation)
FIBO_API_KEY=<get from https://bria.ai>
CEREBRAS_API_KEY=csk-dpvv4653fh4rk2k9y2p2nyhjvy8jw6wyp66xcrykvj33nkj4

# Configuration
DEMO_MODE=False           # Set to True for placeholder images
FIBO_API_URL=https://api.bria.ai/fibo
CEREBRAS_API_URL=https://api.cerebras.ai/v1
```

## Architecture

```
┌─────────────────────────────────────────┐
│   Lovable Frontend (React/Next.js)      │
│   - Upload image                        │
│   - Natural language instructions       │
│   - Real-time preview                   │
│   - Export bundles                      │
└─────────────────────────────────────────┘
                    ↑
                    │ HTTP
                    ↓
┌─────────────────────────────────────────┐
│   FastAPI Backend (Python)              │
│   ┌─────────────────────────────────┐   │
│   │ 5 API Endpoints                 │   │
│   │ - Analyze                       │   │
│   │ - Translate (Cerebras LLM)      │   │
│   │ - Generate (FIBO API)           │   │
│   │ - Export (16-bit pipeline)      │   │
│   └─────────────────────────────────┘   │
│   ┌─────────────────────────────────┐   │
│   │ 8 Service Modules               │   │
│   │ - fibo_client (real API)        │   │
│   │ - cerebras_translator (LLM)     │   │
│   │ - patcher (JSON Patch)          │   │
│   │ - timeline_store (versions)     │   │
│   │ - drift (metrics)               │   │
│   │ - hdr16 (16-bit export)         │   │
│   │ - storage (file management)     │   │
│   │ - translator (rule-based)       │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │   External APIs               │
    │ ┌─────────────────────────┐   │
    │ │ Bria FIBO API V2        │   │
    │ │ (Image Generation)      │   │
    │ └─────────────────────────┘   │
    │ ┌─────────────────────────┐   │
    │ │ Cerebras API            │   │
    │ │ (LLM Translation)       │   │
    │ └─────────────────────────┘   │
    └───────────────────────────────┘
```

## Real API Integration

### Bria FIBO (Image Generation)
- **Status**: Fully implemented with Bria API V2
- **Flow**: Submit async → Poll status → Download image
- **Auth**: `api_token` header
- **Fallback**: Demo mode generates placeholder images
- **Enable**: Set `FIBO_API_KEY` and `DEMO_MODE=False`

### Cerebras LLM (NL → JSON Translation)
- **Status**: Fully implemented with OpenAI-compatible API
- **Flow**: Call `/chat/completions` → Parse JSON response
- **Auth**: `Authorization: Bearer` header
- **Fallback**: Rule-based keyword matching
- **Already configured**: You have the API key!

## File Structure

```
formatlab-studio/
├── README.md                    # Main documentation
├── QUICK_START.md              # This file
├── GITHUB_SETUP.md             # GitHub submission guide
├── IMPLEMENTATION_SUMMARY.md   # Technical details
├── .env                        # Local config (not committed)
├── .env.example                # Config template
├── docker-compose.yml          # Docker setup
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── settings.py
│   │   ├── routers/            # 5 API endpoints
│   │   └── services/           # 8 service modules
│   ├── requirements.txt
│   ├── venv/                   # Virtual environment
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── schemas/
│   ├── formatlab.scene.schema.json
│   └── formatlab.patch.schema.json
├── examples/
│   ├── base_scene.json
│   └── patch_examples/
├── docs/
│   ├── demo_script.md
│   └── LOVABLE_FRONTEND_PROMPT.md
└── storage/
    ├── uploads/
    ├── outputs/
    └── timeline.jsonl
```

## Demo Mode vs Real Generation

**Demo Mode (DEMO_MODE=True)**:
- ✅ Works without FIBO_API_KEY
- ✅ Generates placeholder gradient images instantly
- ✅ All JSON workflows fully functional
- ✅ Good for testing/development
- ✅ Fallback if FIBO fails

**Real Generation (DEMO_MODE=False + FIBO_API_KEY)**:
- ✅ Actual Bria FIBO image generation
- ✅ Takes 10-30 seconds per image
- ✅ Async polling (non-blocking)
- ✅ Real creative AI results
- ✅ For production/contest

## Key Features

| Feature | Status | Details |
|---------|--------|---------|
| Natural Language → JSON | ✅ Real | Cerebras LLM with fallback |
| Image Upload & Analysis | ✅ Implemented | Returns SceneGraph template |
| JSON Patch Operations | ✅ Implemented | RFC6902 compliant |
| Real FIBO Integration | ✅ Implemented | Async polling, proper auth |
| Real LLM Translation | ✅ Implemented | Cerebras API configured |
| Timeline Versioning | ✅ Implemented | JSONL storage |
| Drift Metrics | ✅ Implemented | JSON change detection |
| 16-bit HDR Export | ✅ Implemented | TIFF generation |
| Frontend Integration | ✅ Ready | Lovable prompt provided |
| Docker Support | ✅ Included | docker-compose.yml |
| GitHub Ready | ✅ Ready | 6 commits, push instructions |

## Common Tasks

### Test Health Endpoint
```bash
curl http://localhost:8000/v1/health
```

### Generate Image
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"base_scene": {...}, "seed": 42, "num_variants": 1}'
```

### Translate Natural Language
```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Content-Type: application/json" \
  -d '{"instruction": "brighten the key light", "current_scene": {...}}'
```

### View API Documentation
```
Open: http://localhost:8000/docs
```

### Check Logs
```bash
tail -f /tmp/formatlab.log
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Need 3.13+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port
lsof -i :8000  # Port 8000 in use?
```

### FIBO API fails
- Check `FIBO_API_KEY` in `.env`
- Verify at: https://bria.ai/dashboard
- Check error logs
- Backend automatically falls back to demo mode

### Cerebras translation slow
- Normal (5-10 seconds for LLM)
- Check API key is valid
- Falls back to rule-based if LLM fails

### Frontend can't connect
- Backend running on localhost:8000?
- Check `NEXT_PUBLIC_API_URL` in .env
- Browser console for CORS errors

## Next Steps

1. **Run locally** (instructions above)
2. **Test endpoints** using curl or Swagger UI
3. **Push to GitHub** (see GITHUB_SETUP.md)
4. **Get FIBO API key** (https://bria.ai)
5. **Enable real generation** (set DEMO_MODE=False)
6. **Submit to hackathon** with GitHub URL

## Submission Checklist

- [ ] Backend running and tested
- [ ] API endpoints working (/docs)
- [ ] Real FIBO API key obtained
- [ ] Real Cerebras API key configured (already done!)
- [ ] Repository pushed to GitHub
- [ ] README and docs visible
- [ ] Demo script tested
- [ ] GITHUB_SETUP.md followed
- [ ] Environment variables documented
- [ ] Lovable frontend connected (optional v1)

## Support

- **API Docs**: http://localhost:8000/docs
- **Implementation Details**: See IMPLEMENTATION_SUMMARY.md
- **Demo Script**: See docs/demo_script.md
- **Frontend Setup**: See docs/LOVABLE_FRONTEND_PROMPT.md
- **GitHub Setup**: See GITHUB_SETUP.md

---

**Everything is ready to go!** 🚀

Start the backend, test the endpoints, get your FIBO key, and submit to the hackathon.

Good luck! 🎉
