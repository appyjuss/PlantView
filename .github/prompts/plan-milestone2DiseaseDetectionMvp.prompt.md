# Milestone 2: Disease Detection MVP (Epic B) Implementation Plan

**TL;DR**: Transform PlantView from a working prototype into a production-ready disease detection system with <4s end-to-end latency, >90% accuracy, async processing, PWA offline support, treatment recommendations, comprehensive testing, and enhanced UI/UX. Currently at 45% completion with core detection working but missing async queue, treatment data, PWA, E2E tests, performance optimization, and streaming capabilities.

## Current Status Assessment (45% Complete)

### ✅ Working (Issues #18, #24 Partially):
- `/api/detect` endpoint with validation & structured logging
- JWT authentication enforced
- Multipart/form-data + signed URL support
- File validation (type, size, content-type)
- ML model inference (ResNet50, 38 disease classes)
- Supabase storage integration
- Frontend upload UI with results display
- Database schema for users & uploads

### ❌ Missing (Issues #30, #27, #26, #25, #23, #22, #21, #20, #19):
- Async job queue (RQ/Celery) for heavy workloads
- Treatment recommendation dataset & endpoint
- PWA manifest, service worker, offline caching
- Frontend detection UI improvements (confidence visualization, treatment display)
- E2E accuracy tests (>90% benchmark)
- Latency optimization (<4s target)
- Live stream ingestion & real-time inference
- Dockerized inference worker
- CI/CD pipeline with model checks & build artifacts
- Documentation for Milestone 2

---

## Implementation Steps

### 1. Add Async Job Queue Infrastructure (Issue #19, #27)
**Files**: `backend/tasks.py` (create), `backend/core/models.py`, `backend/routes/detect_routes.py`, `backend/requirements.txt`, `docker-compose.yml`

**Tasks**:
- Install RQ (Redis Queue) via `requirements.txt`: `rq==2.0.0`, `rq-dashboard==0.7.0`
- Create `DetectionJob` model in `backend/core/models.py` with fields: `id`, `user_id`, `file_key`, `status`, `result`, `created_at`, `completed_at`, `error_message`
- Implement `backend/tasks.py` with `detection_task()` function that downloads file, runs prediction, updates job status
- Modify `backend/routes/detect_routes.py` to add decision logic: sync if queue<5, else async with `job_id` response
- Add `GET /api/detect/{job_id}/status` endpoint returning `{status, result, progress}`
- Create `docker-compose.yml` service for RQ worker: `rq worker detection --url redis://redis:6379/0`
- Update `backend/app.py` to register new endpoints and initialize Redis connection
- Run migration: `flask db migrate -m "Add DetectionJob model"`

---

### 2. Create Treatment Recommendation Dataset & Endpoint (Issue #21)
**Files**: `models/treatment_recommendations.json` (create), `backend/routes/treatment_routes.py` (create), `backend/core/schemas.py`

**Tasks**:
- Research and compile treatment data for all 38 disease classes in `models/labels_mapping.json`
- Structure JSON with fields: `disease_name`, `crop`, `severity`, `symptoms`, `treatments[]` (organic/chemical options), `prevention_tips`, `references`
- Create `backend/routes/treatment_routes.py` with `GET /api/treatment/{class_id}` endpoint
- Add `TreatmentData` schema to `backend/core/schemas.py`
- Update `backend/routes/detect_routes.py` to include treatment URL in response: `treatment_url: "/api/treatment/{class_id}"`
- Write unit tests in `backend/tests/test_treatment.py` covering all 38 classes

---

### 3. Optimize End-to-End Latency to <4s (Issue #25)
**Files**: `backend/prediction.py`, `backend/routes/detect_routes.py`, `backend/core/utils.py` (create timing decorator)

**Tasks**:
- Add timing decorator `@measure_latency` in `backend/core/utils.py` to track each step: validation (target: 50ms), upload (target: 500ms), prediction (target: 2s), DB write (target: 100ms)
- Profile `backend/prediction.py`: move model loading to singleton, precompile transforms, optimize image resize
- Implement Redis caching for recent predictions (hash image bytes, cache result for 1 hour)
- Add response header `X-Detection-Latency-Ms` with total processing time
- Configure Supabase edge functions for CDN-accelerated file uploads
- Test on 3G network simulation: `tc qdisc add dev eth0 root netem delay 100ms 20ms` (Linux) to validate <4s

---

### 4. Build E2E Accuracy Tests (>90% Target) (Issue #26)
**Files**: `backend/tests/test_accuracy.py` (create), `backend/tests/fixtures/test_images/` (create directory)

**Tasks**:
- Curate test dataset: 5 images per disease class (190 total) from validation set, store in `backend/tests/fixtures/test_images/{class_name}/`
- Create `backend/tests/test_accuracy.py` with `test_model_accuracy_above_90()` that iterates all test images, runs inference, calculates accuracy
- Add confusion matrix visualization logged to `backend/tests/results/confusion_matrix.png`
- Implement per-class accuracy reporting to identify weak classes (<85%)
- Add latency benchmark: `test_inference_latency()` ensuring mean <2s, p95 <3s
- Run as part of CI: `pytest backend/tests/test_accuracy.py -v --tb=short`

---

### 5. Dockerize Inference Worker & Compose Dev Setup (Issue #27)
**Files**: `backend/Dockerfile.worker` (create), `docker-compose.yml`, `.dockerignore`

**Tasks**:
- Create `backend/Dockerfile.worker` based on `python:3.11-slim` with PyTorch CPU, install dependencies from `backend/requirements.txt`
- Copy model files: `models/resnet50_model.pth`, `models/labels_mapping.json` into worker image
- Update `docker-compose.yml` with services: `db` (postgres:16), `redis`, `backend`, `worker` (RQ), `rq-dashboard`
- Configure health checks for all services
- Add volume mounts: `./backend:/app/backend`, `./models:/app/models`
- Document startup: `docker-compose up -d` in `README.md`
- Test worker scaling: `docker-compose up --scale worker=3`

---

### 6. Implement PWA Offline Caching (Issue #23)
**Files**: `plantViewFrontend/public/manifest.json` (create), `plantViewFrontend/src/service-worker.ts` (create), `plantViewFrontend/vite.config.ts`, `plantViewFrontend/index.html`

**Tasks**:
- Install Vite PWA plugin: `npm install vite-plugin-pwa workbox-window -D` in `plantViewFrontend/`
- Create `public/manifest.json` with app metadata: name, icons (192x192, 512x512), theme_color, background_color, display: standalone
- Generate PWA icons from logo: `npx pwa-asset-generator logo.svg public/icons --background "#4CAF50"`
- Create `src/service-worker.ts` with Workbox caching strategies:
  - NetworkFirst for `/api/*` (detection results)
  - CacheFirst for static assets (JS, CSS, images)
  - StaleWhileRevalidate for model metadata
- Configure `plantViewFrontend/vite.config.ts` with `vite-plugin-pwa` options: registerType: 'autoUpdate', workbox precache manifest
- Update `plantViewFrontend/index.html` to link manifest: `<link rel="manifest" href="/manifest.json">`
- Add install prompt in `plantViewFrontend/src/pages/Dashboard.tsx`: detect `beforeinstallprompt` event, show "Install App" button

---

### 7. Enhance Frontend Detection UI (Issue #22)
**Files**: `plantViewFrontend/src/components/dashboard/DetectionCard.tsx` (create), `plantViewFrontend/src/components/dashboard/DetectionDetails.tsx`, `plantViewFrontend/src/components/dashboard/UploadForm.tsx`

**Tasks**:
- Create `DetectionCard.tsx` component with:
  - Confidence score visualization (progress bar, color-coded: >85% green, 70-85% yellow, <70% red)
  - Disease name with crop icon
  - Treatment preview (first 2 steps)
  - "View Full Treatment" button linking to treatment modal
- Update `DetectionDetails.tsx` to fetch treatment data from `/api/treatment/{class_id}`, display full recommendations
- Modify `UploadForm.tsx` to show loading state with progress indicator during async detection
- Add polling mechanism: if response contains `job_id`, poll `/api/detect/{job_id}/status` every 2s until `status: "completed"`
- Implement image preview with crop suggestion (highlight affected leaf area)

---

### 8. Add Structured Logging & Request Validation (Issue #24)
**Files**: `backend/core/utils.py`, `backend/routes/detect_routes.py`, `backend/app.py`

**Tasks**:
- Install `structlog`: add to `backend/requirements.txt`
- Configure JSON formatter in `backend/app.py`: `logging.basicConfig(format='%(message)s', handlers=[structlog.stdlib.render_json()])`
- Update all log statements in `backend/routes/detect_routes.py` to use structured logging: `logger.info("detection.request", request_id=..., user_id=..., file_size=...)`
- Create `backend/tests/test_logging.py` to verify log output contains required fields: `request_id`, `user_id`, `timestamp`, `file_key`, `latency_ms`
- Add request validation tests in `backend/tests/test_detect_validation.py`:
  - Invalid file type (returns 400)
  - File too large (returns 400)
  - Missing auth (returns 401)
  - Invalid URL (returns 400)

---

### 9. Implement Live Stream Ingestion (WebSocket) (Issue #30, #25)
**Files**: `backend/routes/stream_routes.py` (create), `backend/app.py`, `plantViewFrontend/src/lib/stream.ts` (create), `plantViewFrontend/src/pages/Dashboard.tsx`

**Tasks**:
- Install Flask-SocketIO: `flask-socketio==5.4.0`, `python-socketio==5.12.0` in `backend/requirements.txt`
- Create `backend/routes/stream_routes.py` with WebSocket handlers:
  - `@socketio.on('stream_frame')`: receive base64 frame, validate, queue detection task
  - `@socketio.emit('stream_result')`: emit result back to client when inference completes
- Implement frame buffering: drop frames if queue >10 (backpressure)
- Create `plantViewFrontend/src/lib/stream.ts` client with `startStream()`, `stopStream()`, event handlers
- Update `Dashboard.tsx`: add "Start Live Stream" button, camera access via `navigator.mediaDevices.getUserMedia()`, send frames every 500ms
- Add batch inference optimization in worker: accumulate 5-10 frames, run batch prediction (faster GPU utilization)

---

### 10. Update CI Pipeline for Model Checks & Artifacts (Issue #28)
**Files**: `.github/workflows/ci.yml` (create), `backend/tests/test_model.py` (create)

**Tasks**:
- Create `.github/workflows/ci.yml` with jobs:
  - `test-backend`: run `pytest backend/tests -v --cov=backend`
  - `test-model`: run `pytest backend/tests/test_accuracy.py` (requires model file)
  - `build-artifacts`: build Docker images, push to registry
  - `lint`: run `flake8 backend/` and `eslint plantViewFrontend/src/`
- Create `backend/tests/test_model.py` with sanity checks:
  - Model file exists at `models/resnet50_model.pth`
  - Model loads successfully
  - Output shape matches 38 classes
  - Single inference completes <5s
- Configure artifact storage: upload confusion matrix, latency report to GitHub Actions artifacts

---

### 11. Write Comprehensive Documentation (Issue #29)
**Files**: `docs/MILESTONE_2.md` (create), `docs/API.md` (update), `README.md` (update)

**Tasks**:
- Create `docs/MILESTONE_2.md` with:
  - Architecture diagram (request flow: upload → validate → queue → worker → result)
  - API reference for `/api/detect`, `/api/detect/{job_id}/status`, `/api/treatment/{class_id}`
  - Performance benchmarks (latency breakdown, accuracy metrics)
  - PWA installation guide
  - Docker deployment instructions
  - Troubleshooting common issues
- Update `README.md` with Milestone 2 completion status, demo GIFs, usage examples
- Add inline code comments in `backend/prediction.py`, `backend/tasks.py` explaining model inference pipeline

---

## Further Considerations

### 1. Database Migration Strategy
Run `flask db upgrade` in production before deploying new code with `DetectionJob` model. Consider adding indexes on `user_id`, `status`, `created_at` for query performance.

### 2. Model Version Management
Should we support multiple model versions (A/B testing)? Add `model_version` field to `DetectionJob` and `/api/detect` accepts optional `?model=resnet50-v1.1` parameter?

### 3. Treatment Data Source
Use PlantVillage dataset recommendations, academic papers, or crowdsource from agricultural extension offices? Need accuracy review by domain expert.

### 4. Monitoring & Alerting
Integrate Sentry for error tracking, Prometheus for metrics (detection throughput, queue length, p95 latency)? Set up alerts for accuracy drop >5%, queue backup >100 jobs.

### 5. Cost Optimization
Supabase free tier limits (1GB storage, 50k API requests/month). Monitor usage, consider upgrading or migrating to MinIO self-hosted storage if exceeding limits.

### 6. Mobile Optimization
Test on actual mobile devices (Android/iOS) with varying network conditions (3G, 4G, WiFi). Consider image compression before upload to reduce latency.

---

## Deliverables Summary

- ✅ TensorFlow/PyTorch inference pipeline (DONE - ResNet50)
- 🔄 `/api/detect` endpoint with async queue (PARTIAL - needs job queue)
- ❌ Treatment recommendation dataset & `/api/treatment` endpoint (TODO)
- 🔄 UI for image upload and results (PARTIAL - needs treatment display, confidence viz)
- ❌ PWA offline caching (TODO - manifest, service worker)
- 🔄 Logging + validation (PARTIAL - needs structured JSON logs, validation tests)
- ❌ E2E accuracy tests >90% (TODO)
- ❌ End-to-end latency <4s optimization (TODO - needs profiling, caching)
- ❌ Live stream ingestion (TODO - WebSocket implementation)
- ❌ Dockerized worker & CI pipeline (TODO)
- ❌ Comprehensive documentation (TODO)

## Acceptance Criteria Status

| Criterion | Status | Notes |
|-----------|--------|-------|
| Accuracy >90% for test dataset | ❌ TODO | Need test dataset & accuracy tests |
| End-to-end detection <4s on mobile | ⚠️ UNKNOWN | Need latency benchmarking |
| UI returns diagnosis, confidence, treatment | 🔄 PARTIAL | Has diagnosis/confidence, missing treatment |
| All inference requests validated & logged | 🔄 PARTIAL | Validation done, logs need structure |
| PWA offline support | ❌ TODO | No manifest or service worker |
| Async processing with job queue | ❌ TODO | Currently synchronous only |
| Treatment recommendations available | ❌ TODO | No dataset or endpoint |
| Live stream capability | ❌ TODO | WebSocket not implemented |
| Docker deployment ready | ❌ TODO | No docker-compose or worker image |
| CI/CD with model checks | ❌ TODO | No CI pipeline |

---

**Estimated Effort**: 8-12 weeks with 1 developer, or 4-6 weeks with 2 developers (1 backend, 1 frontend)

**Priority Order**: 
1. Async queue (#19) - unblocks scalability
2. Treatment data (#21) - core user value
3. Latency optimization (#25) - meets acceptance criteria
4. E2E tests (#26) - validates quality
5. Frontend UI (#22) - polish user experience
6. PWA (#23) - mobile experience
7. Dockerization (#27) - deployment readiness
8. Logging/validation tests (#24) - production hardening
9. CI pipeline (#28) - automation
10. Live stream (#30) - advanced feature
11. Documentation (#29) - knowledge transfer
