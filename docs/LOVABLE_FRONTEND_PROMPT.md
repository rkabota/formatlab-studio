# FormatLab Studio - Lovable Frontend Integration Prompt

Use this prompt with Lovable Cloud to generate the frontend that connects to the FormatLab Studio backend.

---

## Prompt for Lovable

```
You are building the frontend for FormatLab Studio, a professional JSON-native image generation console for the Bria FIBO hackathon.

## Architecture

Backend: FastAPI at http://localhost:8000 (configurable via NEXT_PUBLIC_API_URL)
Frontend: Next.js with Supabase integration (Lovable Cloud)
Connection: Direct HTTP API calls to backend endpoints

## UI Requirements

### 1. Main Studio Page (/studio)

**4-Panel Layout:**
- **Left Panel (25% width)**: Controls
  - Image upload (drag & drop)
  - Natural language instruction input (textarea)
  - Button: "Translate to JSON"
  - Current scene info display (read-only)

- **Center Panel (25% width)**: Preview
  - Display generated image
  - Before/after comparison slider (if available)
  - Loading state during generation

- **Right Panel (25% width)**: JSON Editor
  - Tabs: "Scene JSON" / "Patch JSON"
  - JSON editor with syntax highlighting (read-only for now)
  - Button: "Apply Scene"
  - Button: "Export Bundle"

- **Bottom Panel (100%, 120px)**: Timeline
  - Horizontal scrollable timeline of past generations
  - Each entry shows: timestamp, seed, preview thumbnail
  - Click to restore previous generation

### 2. Home Page (/)
- Hero section explaining JSON-native workflow
- Quick start instructions
- Links to demo and documentation
- CTA: "Start Creating"

## API Integration

### Backend Endpoints

All endpoints are at `${NEXT_PUBLIC_API_URL}/v1/`

#### 1. Health Check
```
GET /health
Response: { status, app, version, timestamp, environment }
```

#### 2. Analyze Image
```
POST /analyze
Content-Type: multipart/form-data
Body: file (image upload)

Response: {
  upload_id: string,
  file_path: string,
  scene_graph: SceneGraph
}
```

#### 3. Translate Natural Language
```
POST /translate
Content-Type: application/json

Request: {
  instruction: string,
  current_scene: SceneGraph,
  return_patch: boolean
}

Response: {
  translation_id: string,
  instruction: string,
  updated_scene: SceneGraph,
  patch: JsonPatch[],
  diff_summary: string,
  confidence: number (0-1)
}
```

#### 4. Generate Images
```
POST /generate
Content-Type: application/json

Request: {
  base_scene: SceneGraph,
  patch: JsonPatch[] (optional),
  seed: number (optional),
  num_variants: number (default: 1),
  apply_patch: boolean (default: true)
}

Response: {
  run_id: string,
  seed: number,
  num_variants: number,
  output_urls: string[],
  scene_used: SceneGraph,
  timestamp: string,
  demo_mode: boolean
}
```

#### 5. Export Bundle
```
POST /export
Content-Type: application/json

Request: {
  run_id: string,
  scene_json: SceneGraph,
  patch_json: JsonPatch[] (optional),
  output_urls: string[] (optional),
  include_16bit: boolean (default: true)
}

Response: Binary ZIP file download
```

## State Management

Use Zustand or React Context to manage:

```typescript
interface StudioState {
  currentScene: SceneGraph | null;
  lastGeneration: GenerateResponse | null;
  timeline: TimelineEntry[];
  loading: boolean;
  error: string | null;
}
```

## Component Breakdown

1. **StudioLayout** - Main 4-panel container
2. **UploadDropzone** - Image upload (calls /analyze)
3. **NaturalLanguageBar** - Text input + "Translate" button (calls /translate)
4. **JsonEditor** - Display scene/patch JSON (read-only for now)
5. **ImagePreview** - Display generated image
6. **Timeline** - Horizontal history of generations
7. **CompareSlider** - Before/after comparison
8. **ExportButton** - Download ZIP bundle (calls /export)

## User Flows

### Flow 1: Upload & Translate
1. User uploads image via UploadDropzone
2. Frontend calls POST /analyze
3. Displays extracted SceneGraph in JSON editor
4. User types natural language instruction
5. Clicks "Translate to JSON"
6. Frontend calls POST /translate with instruction + scene
7. Updates scene with returned updated_scene
8. Shows confidence score + explanation

### Flow 2: Generate
1. User clicks "Generate" or "Apply Scene"
2. Frontend calls POST /generate with scene + optional patch
3. Shows loading state
4. Displays output images when ready
5. Adds entry to timeline

### Flow 3: Export
1. User clicks "Export Bundle"
2. Frontend calls POST /export with scene + patch + outputs
3. Browser downloads ZIP file

## Styling

- **Theme**: Dark professional (dark background, cyan accents)
- **Color Scheme**:
  - Background: #0f0f0f
  - Panel: #1a1a1a
  - Border: #333333
  - Accent: #0ea5e9 (cyan)
- **Typography**: System fonts, clear hierarchy
- **Components**: Use shadcn/ui or similar professional UI library

## TypeScript Types

```typescript
interface Camera {
  lens_mm: number;
  fov: number;
  angle?: number;
  tilt?: number;
  depth_of_field?: number;
}

interface Light {
  angle?: number;
  intensity: number;
  color?: string;
  temperature?: number;
}

interface Lighting {
  key: Light;
  fill?: Light;
  rim?: Light;
  ambient?: number;
}

interface Color {
  palette: string[];
  temperature?: number;
  saturation?: number;
  contrast?: number;
  vibrance?: number;
}

interface Constraints {
  lock_subject_identity?: boolean;
  lock_composition?: boolean;
  lock_palette?: boolean;
  negative_constraints?: string[];
}

interface SceneGraph {
  version: string;
  id: string;
  name?: string;
  camera: Camera;
  lighting: Lighting;
  color: Color;
  subject?: {
    description: string;
    style: string;
    position?: { x: number; y: number; z: number };
  };
  constraints?: Constraints;
  metadata?: { tags?: string[]; notes?: string };
}

interface JsonPatch {
  op: "add" | "remove" | "replace" | "move" | "copy" | "test";
  path: string;
  value?: any;
  from?: string;
}

interface TimelineEntry {
  timestamp: string;
  run_id: string;
  seed: number;
  scene_snapshot: SceneGraph;
  patch_summary: string;
  output_urls: string[];
}
```

## Environment Variables

- NEXT_PUBLIC_API_URL: Backend URL (default: http://localhost:8000)
- NEXT_PUBLIC_API_TIMEOUT: Timeout in ms (default: 30000)

## Error Handling

- Show user-friendly error messages for:
  - Network errors
  - API validation errors
  - Missing scene/image data
  - Translation failures (show fallback to rule-based)
  - Generation failures

- Provide retry buttons for failed operations

## Performance

- Debounce JSON editor changes
- Show loading skeleton during API calls
- Cache scene history in timeline
- Lazy load previous generations
- Optimize image display (consider progressive loading)

## Features to Include

✓ Image upload with drag & drop
✓ Natural language → JSON translation with confidence score
✓ JSON viewer (read-only)
✓ Real-time generation with seed control
✓ Timeline with 5+ previous generations
✓ Before/after comparison slider
✓ Export bundle (ZIP download)
✓ Responsive design (mobile-friendly if possible)

## Features to Skip (for now)

- JSON editing (display only for v1)
- Real-time collaboration
- User authentication (assuming Lovable Cloud handles this)
- Advanced filtering/search in timeline

## Testing Checklist

- [ ] Upload image → extract scene
- [ ] Natural language translates → confidence score visible
- [ ] Generate image → seed visible
- [ ] Export works → ZIP file downloads
- [ ] Timeline shows past entries
- [ ] Comparison slider works
- [ ] Error messages display for API failures
- [ ] Responsive on mobile

---

**Important Notes:**

1. The backend is already built and running. Just connect to it.
2. Use environment variables for API URL (will differ in dev vs. production).
3. FIBO image generation may take 10-30 seconds; show loading states.
4. If DEMO_MODE is true, returns placeholder images instantly.
5. Cerebras LLM translation uses streaming; may take 5-10 seconds.
6. The export endpoint returns a ZIP file; handle blob download properly.

Ready to build! 🚀
```

---

## How to Use This Prompt

1. Copy the prompt section above
2. Paste into Lovable Cloud
3. Select "Create New Project" or update existing project
4. Customize styling if needed
5. Connect to backend at `http://localhost:8000`

## Backend Status

✅ Running locally at http://localhost:8000
✅ All 5 endpoints implemented and tested
✅ Real FIBO API integration (configure with FIBO_API_KEY)
✅ Real Cerebras LLM integration (configure with CEREBRAS_API_KEY)
✅ Demo mode fallback available
✅ API documentation at http://localhost:8000/docs

## Next Steps

1. Use the prompt above with Lovable to generate frontend
2. Set `.env` variables with real API keys:
   - FIBO_API_KEY (get from Bria)
   - CEREBRAS_API_KEY (you already have this)
3. Start backend: `cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload`
4. Run Lovable frontend
5. Test the complete workflow

---

**Happy building!** 🎨
