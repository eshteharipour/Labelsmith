# Development Guide

## Project Structure

```
.
├── main.py                 # Main FastAPI application
├── start.py               # Convenient startup script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # Main documentation
├── API.md                # API documentation
├── MIGRATION.md          # Migration guide
│
├── handlers/             # Route handlers (modular backends)
│   ├── __init__.py
│   ├── classifier.py
│   ├── matcher.py
│   ├── viewer.py
│   ├── cluster.py
│   ├── shop.py
│   └── text_labeler.py
│
├── utils/                # Shared utilities
│   ├── __init__.py
│   └── common.py
│
├── cleaner/              # Vue.js frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── views/        # Page components
│   │   ├── router/       # Vue Router config
│   │   ├── App.vue
│   │   └── main.js
│   ├── dist/            # Built frontend (created by npm build)
│   └── package.json
│
├── state*.json           # Module state files (created at runtime)
└── dataset*.jsonl        # Dataset files
```

## Setting Up Development Environment

### 1. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black ruff pytest pytest-asyncio
```

### 2. Frontend Environment

```bash
cd cleaner

# Install dependencies
npm install

# Run development server
npm run dev
```

### 3. Environment Configuration

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env  # or your preferred editor
```

## Development Workflow

### Backend Development

```bash
# Run with auto-reload
python start.py --reload

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload when you modify Python files.

### Frontend Development

```bash
cd cleaner

# Development server (with hot reload)
npm run dev

# This runs on a different port (usually 5173)
# Configure proxy in vite.config.js to point to backend
```

### Full Stack Development

**Terminal 1 - Backend:**
```bash
python start.py --reload
```

**Terminal 2 - Frontend:**
```bash
cd cleaner && npm run dev
```

Access the app at the frontend dev server URL (usually http://localhost:5173)

## Code Style

### Python

We use `black` for formatting and `ruff` for linting:

```bash
# Format code
black handlers/ utils/ main.py

# Lint code
ruff check handlers/ utils/ main.py

# Auto-fix linting issues
ruff check --fix handlers/ utils/ main.py
```

### JavaScript/Vue

```bash
cd cleaner

# Format code
npm run format

# Lint code
npm run lint
```

## Adding a New Module

### 1. Create Handler

Create `handlers/my_module.py`:

```python
"""
My Module Handler.

Description of what this module does.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Configuration
PAGE_SIZE = 100

# Global state
_data = []


def init_my_module():
    """Initialize module by loading data."""
    global _data
    # Load your data here
    _data = []
    print(f"Loaded {len(_data)} items")


# Initialize on module load
init_my_module()


@router.get("/my-endpoint")
async def my_endpoint():
    """Endpoint description."""
    return {"message": "Hello from my module"}
```

### 2. Register Handler

Edit `handlers/__init__.py`:

```python
from .my_module import router as my_module_router

__all__ = [
    # ... existing ...
    "my_module_router",
]
```

### 3. Include in Main App

Edit `main.py`:

```python
from handlers import (
    # ... existing ...
    my_module_router,
)

app.include_router(my_module_router, prefix="/api", tags=["my_module"])
```

### 4. Create Frontend View

Create `cleaner/src/views/MyModule.vue`:

```vue
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">My Module</h1>
    <!-- Your UI here -->
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'MyModule',
  data() {
    return {
      data: []
    }
  },
  async mounted() {
    const response = await axios.get('/api/my-endpoint')
    console.log(response.data)
  }
}
</script>
```

### 5. Add Route

Edit `cleaner/src/router/index.js`:

```javascript
import MyModule from "@/views/MyModule.vue";

const routes = [
  // ... existing ...
  { path: "/my-module", component: MyModule },
];
```

### 6. Add Navigation

Edit `cleaner/src/App.vue`:

```vue
<nav>
  <!-- ... existing ... -->
  <router-link to="/my-module">My Module</router-link>
</nav>
```

## Testing

### Backend Tests

Create `tests/test_my_module.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_my_endpoint():
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from my module"}


@pytest.mark.asyncio
async def test_async_endpoint():
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
```

Run tests:
```bash
pytest tests/
```

### Frontend Tests

```bash
cd cleaner

# Run unit tests
npm run test

# Run with coverage
npm run test:coverage
```

## Debugging

### Backend Debugging

Add print statements or use Python debugger:

```python
import pdb

@router.get("/debug")
async def debug_endpoint():
    pdb.set_trace()  # Breakpoint
    return {"debug": "info"}
```

Or use VS Code debugger with launch.json:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true
    }
  ]
}
```

### Frontend Debugging

Use Vue DevTools browser extension and:

```javascript
// In your component
console.log('Debug info:', this.data)

// Or add a watch
watch: {
  data(newVal, oldVal) {
    console.log('Data changed:', oldVal, '->', newVal)
  }
}
```

## Common Tasks

### Update Dependencies

```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
cd cleaner && npm update
```

### Build for Production

```bash
# Build frontend
cd cleaner && npm run build

# The built files will be in cleaner/dist/
```

### Check Application Health

```bash
# Health check endpoint
curl http://localhost:8000/api/health

# Or in browser
open http://localhost:8000/api/health
```

### View Logs

The application logs to stdout. Redirect to a file if needed:

```bash
python start.py > app.log 2>&1
```

## Performance Optimization

### Backend

1. **Use async for I/O operations:**
```python
async def load_large_file():
    async with aiofiles.open('file.txt', 'r') as f:
        return await f.read()
```

2. **Add caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_computation(param):
    # ...
```

3. **Database connection pooling:**
```python
engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20
)
```

### Frontend

1. **Lazy load components:**
```javascript
const MyModule = () => import('./views/MyModule.vue')
```

2. **Optimize images:**
```bash
# Use image compression
npm install --save-dev vite-plugin-imagemin
```

3. **Enable gzip compression:**
Already enabled in production builds.

## Troubleshooting

### Module not found errors

```bash
# Ensure you're in the right directory
pwd

# Check Python path
python -c "import sys; print(sys.path)"

# Install missing packages
pip install <package>
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill it
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Frontend build fails

```bash
cd cleaner

# Clear cache
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try build again
npm run build
```

## Best Practices

1. **Always use type hints in Python:**
```python
def process_image(path: str) -> Dict[str, Any]:
    ...
```

2. **Validate input with Pydantic:**
```python
class ImageUpdate(BaseModel):
    path: str
    text: str
```

3. **Handle errors gracefully:**
```python
try:
    result = risky_operation()
except SpecificError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

4. **Use environment variables for config:**
```python
PAGE_SIZE = int(os.getenv("PAGE_SIZE", "100"))
```

5. **Keep handlers focused:**
Each handler should manage one view/module only.

6. **Document your code:**
Use docstrings for all functions and classes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
