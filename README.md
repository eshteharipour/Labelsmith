# Image Dataset Management System

A unified, modular web application for managing, labeling, and organizing image datasets. This system provides multiple specialized views for different dataset management tasks.

## Features

### 🎯 Classifier
- Image classification and labeling with custom statuses
- Grid and row view modes
- Batch classification with status tracking
- Group mode for cluster-based classification
- Auto-save functionality

### 🔗 Matcher
- Product matching interface
- Source-target pair evaluation
- Highlight matching for easy comparison
- RTL/LTR text support for multilingual datasets
- Batch and individual save options

### 👁️ Viewer
- Image similarity visualization
- Display nearest neighbors using different metrics
- Side-by-side comparison view

### 📊 Cluster
- Clustered image viewing
- Support for both local and server-hosted images
- Toggle between local and remote image sources
- Group images by cluster ID

### 🏪 Shop
- Product reference matching
- Database-backed product management
- Recommendation approval workflow
- CORS-friendly image proxying

### ✏️ Text Labeler
- JSONL dataset text labeling
- Image-text pair management
- Per-item and batch save modes
- Progress tracking and statistics
- Auto-backup on save

## Architecture

### Unified Backend
All modules are now handled by a single FastAPI application, eliminating the need to run multiple separate backends.

```
main.py                 # Main FastAPI application
├── handlers/           # Modular route handlers
│   ├── classifier.py
│   ├── matcher.py
│   ├── viewer.py
│   ├── cluster.py
│   ├── shop.py
│   └── text_labeler.py
└── utils/             # Shared utilities
    └── common.py
```

### Frontend
Vue.js 3 application with routing for different views:
- `/` - Classifier
- `/matcher` - Matcher
- `/viewer` - Viewer
- `/cluster` - Cluster
- `/shop` - Shop
- `/labeler` - Text Labeler

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Clone the repository
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install fastapi uvicorn python-dotenv pandas pydantic httpx
# Optional: For database features
pip install sqlalchemy psycopg2-binary
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Frontend Setup

1. Install dependencies
```bash
cd cleaner
npm install
```

2. Build frontend
```bash
npm run build
```

## Usage

### Running the Application

**Single command to start everything:**
```bash
python main.py
```

The application will be available at `http://localhost:8000`

### Development Mode

For backend development with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

For frontend development:
```bash
cd cleaner
npm run dev
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `PORT`: Server port (default: 8000)
- `*_PAGE_SIZE`: Items per page for each module
- `LABELER_JSONL_FILE`: Path to JSONL dataset
- `DB_URL_*`: Database connection strings

### Module-Specific Configuration

Each handler can be independently configured through environment variables with module-specific prefixes (e.g., `LABELER_*`, `CLASSIFIER_*`).

## Text Labeler Usage

### JSONL Format

The text labeler expects a JSONL file where each line is a JSON object:

```jsonl
{"image": "path/to/image1.jpg", "text": "label text"}
{"image": "path/to/image2.jpg", "text": "another label"}
```

### Workflow

1. Navigate to `/labeler`
2. View paginated images with current labels
3. Edit labels by typing and pressing Enter
4. Labels auto-save on each edit
5. Use "Save Page (Batch)" to force-save all changes
6. View statistics via the `/api/stats` endpoint

### API Endpoints

#### Text Labeler
- `GET /api/images?page=0` - Get paginated items
- `POST /api/images/update` - Update single item
- `POST /api/sync_page` - Batch save current page
- `GET /api/stats` - Get labeling statistics
- `POST /api/reload` - Reload dataset from disk
- `GET /api/images/file?image_path=...` - Serve image file

#### Common Endpoints (All Modules)
- `GET /api/load_settings` - Load user settings
- `POST /api/save_settings` - Save user settings
- `GET /api/health` - Health check

## Data Persistence

### State Files
Each module maintains its own state file:
- `state_classifier.json`
- `state_matcher.json`
- `state_viewer.json`
- `state_cluster.json`
- `state_shop.json`
- `state_labeler.json`

State files store:
- User preferences (last page, view mode, etc.)
- Module-specific settings
- Classification/labeling progress

### Backups
The text labeler automatically creates `.backup` files before saving changes.

## Extending the System

### Adding a New Module

1. Create a new handler in `handlers/`:
```python
# handlers/my_module.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

2. Register in `handlers/__init__.py`:
```python
from .my_module import router as my_module_router
__all__ = [..., "my_module_router"]
```

3. Include in `main.py`:
```python
app.include_router(my_module_router, prefix="/api", tags=["my_module"])
```

4. Create corresponding Vue component in `src/views/`

5. Add route in `src/router/index.js`

## Troubleshooting

### Module Not Available Warnings
If you see warnings about modules not being available, ensure you have installed the required dependencies for that module. The system is designed to gracefully handle missing dependencies and will only enable modules with satisfied requirements.

### Image Loading Issues
- Check `IMAGE_BASE_PATH` in `.env`
- Verify image paths in your dataset
- For external images, ensure the proxy endpoint is working

### Database Connection Issues
- Verify database URLs in `.env`
- Ensure database servers are running
- Check credentials and permissions

## Performance Tips

1. **Pagination**: Adjust `*_PAGE_SIZE` based on your needs
2. **Caching**: Images are cached for 24 hours via Cache-Control headers
3. **Database**: Use connection pooling for better performance
4. **Frontend**: Build frontend in production mode for better performance

## Security Considerations

- The application allows CORS from all origins (`allow_origins=["*"]`)
- Image paths are validated to prevent directory traversal
- Database credentials should be kept secure
- Consider adding authentication for production use

## License

MIT

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or contributions, please open an issue on GitHub.
