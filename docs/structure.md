# Project File Structure

```
image-dataset-manager/
│
├── 📄 main.py                    # Main unified FastAPI application
├── 🚀 start.py                   # Convenient startup script
├── 📦 requirements.txt           # Python dependencies
├── ⚙️ .env.example               # Environment variables template
│
├── 📚 Documentation
│   ├── README.md                 # Comprehensive project documentation
│   ├── QUICKSTART.md            # Quick start guide (START HERE!)
│   ├── API.md                   # Complete API reference
│   ├── DEVELOPMENT.md           # Development guide
│   └── MIGRATION.md             # Migration from old system
│
├── 🎛️ handlers/                  # Modular route handlers
│   ├── __init__.py              # Handler package initialization
│   ├── classifier.py            # Image classification handler
│   ├── matcher.py               # Product matching handler
│   ├── viewer.py                # Image similarity viewer handler
│   ├── cluster.py               # Clustered image viewing handler
│   ├── shop.py                  # Product reference matching handler
│   └── text_labeler.py          # Text labeling handler (NEW!)
│
├── 🛠️ utils/                     # Shared utilities
│   ├── __init__.py              # Utils package initialization
│   └── common.py                # Common utility functions
│
├── 📝 dataset_sample.jsonl      # Sample dataset for testing
│
└── 📁 Runtime Files (created automatically)
    ├── state_classifier.json    # Classifier state
    ├── state_matcher.json       # Matcher state
    ├── state_viewer.json        # Viewer state
    ├── state_cluster.json       # Cluster state
    ├── state_shop.json          # Shop state
    ├── state_labeler.json       # Text labeler state
    └── dataset.jsonl.backup     # Auto-backup of dataset
```

## Frontend Structure (separate in your project)

```
cleaner/                         # Vue.js frontend (not included in this delivery)
├── src/
│   ├── components/
│   │   └── CustomInput.vue      # Reusable input component
│   ├── views/
│   │   ├── Classifier.vue       # Classifier view
│   │   ├── Matcher.vue          # Matcher view
│   │   ├── Viewer.vue           # Viewer view
│   │   ├── Cluster.vue          # Cluster view
│   │   ├── Shop.vue             # Shop view
│   │   └── TextLabeler.vue      # Text labeler view
│   ├── router/
│   │   └── index.js             # Vue Router configuration
│   ├── App.vue                  # Main app component
│   └── main.js                  # Vue app initialization
│
└── dist/                        # Built frontend (mount point for FastAPI)
    ├── index.html
    ├── assets/
    └── ...
```

## File Descriptions

### Core Application Files

#### `main.py` (98 lines)
The unified FastAPI application that brings everything together. Includes all routers, CORS middleware, health check endpoint, and serves the static frontend.

**Key features:**
- Lifespan management
- Modular router inclusion
- Health check endpoint
- Static file serving

#### `start.py` (158 lines)
Convenient startup script with dependency checking, frontend building, and configuration loading.

**Features:**
- Dependency validation
- Frontend build checking
- Environment loading
- CLI arguments for host/port/reload

#### `requirements.txt`
Python package dependencies with version constraints.

**Sections:**
- Core Framework (FastAPI, Uvicorn)
- Data Processing (Pandas, Pydantic)
- HTTP Client (httpx)
- Optional dependencies (SQLAlchemy, Pillow)
- Development tools (pytest, black, ruff)

### Handler Files

Each handler is a self-contained module that:
- Defines routes for one specific view
- Manages its own state
- Handles initialization gracefully
- Provides consistent API patterns

#### `handlers/classifier.py` (~230 lines)
Handles image classification with multiple statuses.

**Endpoints:**
- GET /api/images - Paginated images
- GET /api/groups - Grouped by cluster
- POST /api/images/update - Update classification
- POST /api/sync_classifications - Save to disk

#### `handlers/matcher.py` (~200 lines)
Handles source-target product matching.

**Endpoints:**
- GET /api/images - Matching pairs
- POST /api/images/update - Update match
- POST /api/sync_changes - Save changes
- POST /api/sync_page - Save page
- POST /api/sync_all - Save all

#### `handlers/viewer.py` (~110 lines)
Displays images with similarity metrics.

**Endpoints:**
- GET /api/images - Images with similarities
- POST /api/sync_page - Save page

#### `handlers/cluster.py` (~135 lines)
Displays clustered images with proxy support.

**Endpoints:**
- GET /api/images - Clustered images
- GET /api/proxy-image - Proxy external images

#### `handlers/shop.py` (~200 lines)
Product reference matching with database backend.

**Endpoints:**
- GET /api/images - Product pairs
- POST /api/images/update - Update reference
- GET /api/proxy-image - Proxy CDN images

#### `handlers/text_labeler.py` (~260 lines) ⭐ NEW!
JSONL-based text labeling for image datasets.

**Endpoints:**
- GET /api/images - Paginated items
- POST /api/images/update - Update label
- POST /api/sync_page - Batch save
- GET /api/stats - Dataset statistics
- POST /api/reload - Reload dataset

**Special features:**
- Auto-save on each edit
- Automatic backups
- Progress tracking
- JSONL format support

### Utility Files

#### `utils/common.py`
Shared utility functions used across handlers.

**Functions:**
- `save_json()` - Save dict as JSON
- `load_json()` - Load JSON with defaults
- `get_default_image_path()` - Get placeholder image
- `ensure_dir()` - Create directory if needed

### Documentation Files

#### `README.md` (280 lines)
Comprehensive project documentation covering:
- Features overview
- Architecture explanation
- Installation instructions
- Usage examples
- Configuration guide
- Troubleshooting tips

#### `QUICKSTART.md` (380 lines)
Fast-track guide to get started in 5 minutes:
- What is this system?
- Quick 3-step start
- Usage examples
- Common tasks
- Troubleshooting
- Comparison with alternatives

#### `API.md` (330 lines)
Complete API reference with:
- All endpoints documented
- Request/response examples
- Error codes
- Pagination patterns
- Caching information

#### `DEVELOPMENT.md` (420 lines)
Development guide including:
- Project structure
- Setup instructions
- Development workflow
- Adding new modules
- Testing guidelines
- Best practices

#### `MIGRATION.md` (200 lines)
Migration guide from old multi-file system:
- What changed and why
- Step-by-step migration
- Data migration
- Rollback plan
- Performance comparison

### Configuration Files

#### `.env.example`
Template for environment variables with:
- Server configuration
- Module-specific settings
- Database connections
- Feature flags

### Sample Data

#### `dataset_sample.jsonl`
Example JSONL dataset for testing the text labeler:
- 8 sample image-text pairs
- Mix of labeled and unlabeled items
- Demonstrates JSONL format

## Total Line Count

```
Main Application:     ~350 lines
Handlers:            ~1200 lines
Utils:               ~60 lines
Documentation:       ~1600 lines
Configuration:       ~50 lines
─────────────────────────────────
Total:               ~3260 lines
```

## Key Improvements Over Old System

1. **Single Process**: One app instead of 5+
2. **Lazy Loading**: Modules only initialize when used
3. **Shared Code**: Utils reduce duplication
4. **Better Errors**: Graceful degradation when dependencies missing
5. **Cleaner Structure**: Logical organization
6. **Easier Testing**: Modular design
7. **Better Documentation**: 1600+ lines of docs
8. **New Feature**: Text labeler added!

## Getting Started

1. Read `QUICKSTART.md` first (5 min)
2. Run `python start.py` (1 min)
3. Open browser to http://localhost:8000
4. Explore each module
5. Read `DEVELOPMENT.md` to extend

## Next Steps

- Customize for your use case
- Add authentication if needed
- Deploy to production
- Contribute improvements!
