# FormatLab Studio: 3-Minute Demo Script

**Target**: Judges, investors, FIBO community
**Duration**: 3 minutes
**Goal**: Show JSON-native workflow, controllability, export bundle

---

## Pre-Demo Setup (Do This Before)

```bash
# Terminal 1: Start backend
cd formatlab-studio/backend
source venv/bin/activate
python app/main.py
# Wait for "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2: Start frontend
cd formatlab-studio/frontend
npm run dev
# Wait for "▲ ready on http://localhost:3000"

# Browser: Open http://localhost:3000
```

**Ensure**:
- Both servers running without errors
- Browser at http://localhost:3000
- `.env` has `DEMO_MODE=True`

---

## Demo Flow (3 minutes)

### [0:00-0:30] **Introduction**

**Say**:
> "FormatLab Studio is a professional JSON-native console for controllable image generation with FIBO.
> We're showing three key capabilities: JSON editing, natural language translation, and professional exports."

**Show**:
- Point out the 4-panel layout:
  - Left: Controls + Upload + Instructions
  - Center: Live preview + Compare slider
  - Right: JSON editor
  - Bottom: Timeline

### [0:30-1:15] **Feature 1: Natural Language → JSON**

**Action**:
1. Click "Natural Language Bar" (left side)
2. Type: `"Make the lighting brighter and increase color saturation"`
3. Click "Translate"
4. **Highlight**: Right panel shows updated JSON + the patch

**Say**:
> "We automatically translate natural language into structured JSON Patches. This bridges the gap between human instructions and FIBO's JSON-native architecture. Notice the patch shows exactly what changed."

**Show**:
- Highlight the JSON changes in right panel
- Point to patch in "Patch Editor"

### [1:15-1:50] **Feature 2: JSON Editing & Live Preview**

**Action**:
1. In the "JSON SceneGraph" editor (right), find `"lighting"` → `"key"` → `"intensity"`
2. Change from `0.9` to `0.75` (click and edit)
3. Click "Apply"
4. **Highlight**: Preview updates instantly in center panel

**Say**:
> "Full JSON control. Adjust camera focal length, lighting angles, color temperature, constraints—all in structured JSON. The scene is completely reproducible with the same seed and patch."

**Show**:
- Point to before/after in center
- Click the compare slider to show difference

### [1:50-2:30] **Feature 3: Export Bundle & Timeline**

**Action**:
1. Click "Export Bundle" button (right side)
2. Wait 2 seconds
3. Browser downloads: `formatlab_export_<timestamp>.zip`
4. Open zip file in Finder/Explorer

**Say**:
> "Professional export includes everything: base scene JSON, patch operations, preview images, and a 16-bit TIFF master for print. Teams can reproduce changes by applying the patch to the base scene."

**Show Contents** (open zip):
- `scene.json` - Base SceneGraph
- `patch.json` - Applied edits
- `preview_0.png` - Generated image
- `master_16bit.tiff` - HDR master for color critical work
- `metadata.json` - Export timestamp and seed

**Point to Timeline** (bottom of screen):
> "Complete version history. Every generation is timestamped with the seed and key changes. Teams can revert or remix any previous version."

### [2:30-3:00] **Closing: Key Differentiators**

**Say**:
> "FormatLab wins on three fronts:
>
> **#1 Controllability**: Professional camera, lighting, color controls with constraint locks.
>
> **#2 JSON-Native Workflow**: Natural language → JSON translation, reproducible patches, agentic automation ready.
>
> **#3 Pro Tool UX**: Enterprise studio layout, real-time validation, 16-bit HDR exports, version timeline."

**Optional**: If time, show `http://localhost:8000/docs` (API documentation)

---

## If Something Goes Wrong

### Image Not Showing
- **Cause**: Pillow not installed or image generation failed
- **Fix**: `pip install pillow` and restart backend
- **Fallback**: Demo mode still returns valid JSON (see `"demo_output_*.json"` in outputs)

### Port Conflict
- **Cause**: Port 8000 or 3000 already in use
- **Fix**: Change in `.env` or `settings.py`
- **Quick**: `export PORT=8001`

### JSON Not Updating
- **Cause**: Frontend cache
- **Fix**: Open DevTools → Network → disable cache → refresh

---

## Key Points for Judges

✅ **JSON-First Architecture**: All generation flows through structured JSON (even with natural language input)

✅ **Reproducibility**: Same base + seed + patch = identical output (fundamental for enterprise)

✅ **Professional Tools**: Camera lens control, lighting angles, color temp, constraint locks

✅ **16-bit Export**: Beyond standard 8-bit; prepared for color-critical workflows and future HDR models

✅ **Ready for FIBO**: One-line config change to enable real API; demo mode proves the entire architecture works

✅ **Agentic Ready**: JSON Patch format + history timeline = automation-friendly API

---

## Questions Judges Might Ask

**Q: Why JSON instead of natural language?**
> "JSON is deterministic and reproducible. Two prompts might generate different images; the same JSON + seed always produces the same output. Essential for professional workflows and multi-agent automation."

**Q: What happens without FIBO API keys?**
> "Demo mode generates placeholder images, but the entire workflow is real. Judges can test translate, patch, export, timeline—everything except the actual image generation. Swap one function and it's live FIBO."

**Q: How do teams use this?**
> "1. Upload reference image → extract scene
> 2. Give natural language feedback → translate to JSON
> 3. Iterate with live preview
> 4. Export reproducible bundle
> 5. Share scene.json + patch.json for collaboration
> All operations are deterministic (same seed = same output)."

**Q: 16-bit TIFF export?**
> "Prepared for professional color workflows. Current pipeline upsamples 8-bit to 16-bit demonstration; with native HDR models, this preserves full color depth for print/display."

---

## Timing Tips

⏱️ **0:00-0:30**: Quick intro + layout (don't dwell)
⏱️ **0:30-1:15**: Natural language demo (show JSON change)
⏱️ **1:15-1:50**: JSON editing + preview update
⏱️ **1:50-2:30**: Export zip (open and show contents)
⏱️ **2:30-3:00**: Key differentiators + close

**If running short**: Skip the timeline detail, focus on translate + export.
**If running long**: Cut the JSON editing section, emphasize natural language + export.

---

## Files for Judges to Review

After demo, point judges to:

1. **`/schemas`**: JSON Schema files (show they're FIBO-compatible)
2. **`/examples`**: Sample scene.json and patch.json files
3. **`README.md`**: Full technical documentation
4. **`/backend/app/routers`**: API endpoints (show `translate.py` and `generate.py`)

---

## Success Criteria

✅ Natural language translates to JSON
✅ JSON updates appear in preview
✅ Export ZIP contains valid JSON + images
✅ Demo runs without errors
✅ Judges understand JSON-native advantage

**You're ready! 🚀**
