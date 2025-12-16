# n8n Workflow Setup for FormatLab Studio

## Overview

FormatLab Studio uses **n8n** for workflow orchestration:
- **Analyze**: Image upload → FIBO analysis → SceneGraph JSON
- **Translate**: NL instruction → Cerebras LLM → JSON Patch
- **Generate**: Scene JSON → FIBO API → Images (with async polling)
- **Export**: Compile scene, patch, images → ZIP bundle

**Architecture**:
```
Lovable Frontend
    ↓
FastAPI Backend (http://localhost:8000)
    ↓
n8n Workflows (https://rkabota.app.n8n.cloud)
    ↓
External APIs (Bria FIBO, Cerebras LLM)
```

---

## Setup Instructions

### Step 1: Access n8n Dashboard

Go to: **https://rkabota.app.n8n.cloud**

Login with your credentials.

### Step 2: Import Workflows

In n8n, you can import workflows as JSON files:

1. Click **"New"** → **"Workflow"**
2. Click **"..."** (menu) → **"Import from file"**
3. Upload each workflow JSON file from `/n8n-workflows/`:
   - `analyze-workflow.json`
   - `translate-workflow.json`
   - `generate-workflow.json`
   - `export-workflow.json`

**OR** manually create workflows (see "Manual Setup" below).

### Step 3: Set Environment Variables in n8n

In n8n, go to **Settings** → **Environment Variables**:

```
FIBO_API_KEY=ab286c91d68c417191ee03c697f1e45f
CEREBRAS_API_KEY=csk-dpvv4653fh4rk2k9y2p2nyhjvy8jw6wyp66xcrykvj33nkj4
```

Or add them directly in each workflow's HTTP Request nodes.

### Step 4: Configure Webhooks

Each workflow needs a webhook trigger:

1. **Analyze Workflow**:
   - Webhook path: `/analyze`
   - Method: POST
   - Response: "Wait for response"

2. **Translate Workflow**:
   - Webhook path: `/translate`
   - Method: POST
   - Response: "Wait for response"

3. **Generate Workflow**:
   - Webhook path: `/generate`
   - Method: POST
   - Response: "Wait for response"

4. **Export Workflow**:
   - Webhook path: `/export`
   - Method: POST
   - Response: "Wait for response"

### Step 5: Activate All Workflows

In n8n:
1. Open each workflow
2. Click the **"Active"** toggle (top right)
3. Confirm activation

### Step 6: Test Workflows

#### Test Analyze Workflow:
```bash
curl -X POST https://rkabota.app.n8n.cloud/webhook/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "file_name": "test.jpg",
    "file_size": 50000
  }'
```

Expected response: `{"upload_id": "...", "scene_graph": {...}}`

#### Test Translate Workflow:
```bash
curl -X POST https://rkabota.app.n8n.cloud/webhook/translate \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "brighten the key light",
    "current_scene": {
      "version": "1.0",
      "id": "test",
      "lighting": {"key": {"intensity": 0.8}}
    }
  }'
```

Expected response: `{"translation_id": "...", "patch": [...], "updated_scene": {...}}`

#### Test Generate Workflow:
```bash
curl -X POST https://rkabota.app.n8n.cloud/webhook/generate \
  -H "Content-Type: application/json" \
  -d '{
    "base_scene": {...},
    "seed": 42,
    "num_variants": 1
  }'
```

Expected response: `{"run_id": "...", "output_urls": [...]}`

---

## Manual Workflow Setup

If you prefer to create workflows manually instead of importing JSON:

### Analyze Workflow Structure:

```
Webhook (POST /analyze)
  ↓
Process Upload (Code)
  ↓
Call FIBO Analyze (HTTP Request)
  ↓
Transform to SceneGraph (Code)
  ↓
Respond (Webhook Response)
```

### Translate Workflow Structure:

```
Webhook (POST /translate)
  ↓
Prepare LLM Prompt (Code)
  ↓
Call Cerebras LLM (HTTP Request)
  ↓
Parse Translation (Code)
  ↓
Respond (Webhook Response)
```

### Generate Workflow Structure:

```
Webhook (POST /generate)
  ↓
Prepare Generation (Code)
  ↓
Loop Variants
  ↓
Submit FIBO Request (HTTP Request)
  ↓
Poll FIBO Status (Code - polling loop)
  ↓
Download Image (HTTP Request)
  ↓
Collect Outputs (Code)
  ↓
Respond (Webhook Response)
```

### Export Workflow Structure:

```
Webhook (POST /export)
  ↓
Prepare Export (Code)
  ↓
Prepare Images (Code)
  ↓
Create ZIP (Code - uses jszip library)
  ↓
Respond (Webhook Response)
```

---

## Backend Configuration

The FastAPI backend is already configured to call n8n workflows.

### Environment Variables (backend/.env):

```ini
# n8n Integration
N8N_ENABLED=True
N8N_BASE_URL=https://rkabota.app.n8n.cloud
N8N_WEBHOOK_BASE=https://rkabota.app.n8n.cloud/webhook
N8N_API_KEY=your_jwt_token
```

### API Calls:

The backend calls n8n via webhooks (no authentication required for public webhooks):

```
POST /v1/analyze      → https://rkabota.app.n8n.cloud/webhook/analyze
POST /v1/translate    → https://rkabota.app.n8n.cloud/webhook/translate
POST /v1/generate     → https://rkabota.app.n8n.cloud/webhook/generate
POST /v1/export       → https://rkabota.app.n8n.cloud/webhook/export
```

---

## Troubleshooting

### Webhook Returns 404

1. Verify webhook path is correct (without leading slash)
2. Check workflow is **Active** (toggle enabled)
3. Verify webhook node has correct path configured

### HTTP Request Fails (401/403)

1. Check API key is correct in environment variables
2. Verify header name: FIBO uses `api_token`, Cerebras uses `Authorization: Bearer`
3. Test API key directly: `curl -H "api_token: YOUR_KEY" https://api.bria.ai/fibo/status/test`

### Generation Timeout

1. Increase timeout in `n8n_client.py` - currently 180 seconds
2. Check FIBO API status: https://bria.ai/status
3. Verify async polling loop in workflow is correct

### Memory Issues with Large Images

1. Resize images before uploading
2. Use `scale` parameter in image analysis code
3. Stream ZIP file instead of loading entirely in memory

### Network Issues

1. Verify firewall allows connections to rkabota.app.n8n.cloud
2. Test connectivity: `curl https://rkabota.app.n8n.cloud`
3. Check n8n logs for errors

---

## Performance Tips

1. **Caching**: Add caching layer for frequently analyzed images
2. **Batch Processing**: Use n8n's batch processing for multiple images
3. **Error Handling**: Add error handlers in workflows to retry failed operations
4. **Logging**: Enable execution logging in n8n for debugging

---

## Security

### Public Webhooks

n8n webhooks are currently **public** (no authentication).

To secure:
1. Add Basic Auth to webhook node
2. Add query parameter check
3. Deploy behind reverse proxy with rate limiting

### API Keys

Store API keys as **Environment Variables** in n8n, NOT hardcoded in workflows.

---

## Next Steps

1. ✅ Create n8n account and access dashboard
2. ✅ Import or create the 4 workflows
3. ✅ Set environment variables (FIBO_API_KEY, CEREBRAS_API_KEY)
4. ✅ Activate all workflows
5. ✅ Test each workflow independently
6. ✅ Test FastAPI backend with Lovable frontend
7. ✅ Monitor execution logs for errors

---

**Questions?** Check n8n documentation: https://docs.n8n.io/
