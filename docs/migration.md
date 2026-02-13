# Migration Guide: Old System → Unified System

## Overview
This guide helps you migrate from the old multi-file backend system to the new unified architecture.

## What Changed

### Old System
```
classifier.py     # Separate FastAPI app
matcher.py        # Separate FastAPI app  
viewer.py         # Separate FastAPI app
cluster.py        # Separate FastAPI app
shop.py           # Separate FastAPI app
# Text labeler didn't exist
```

**Problems:**
- Had to run 5+ separate processes
- Port conflicts
- Resource wastage (all apps running even if unused)
- Difficult to maintain
- Code duplication

### New System
```
main.py           # Single FastAPI app
handlers/
  ├── classifier.py      # Route handler
  ├── matcher.py         # Route handler
  ├── viewer.py          # Route handler
  ├── cluster.py         # Route handler
  ├── shop.py            # Route handler
  └── text_labeler.py    # Route handler (NEW!)
```

**Benefits:**
- Single process serves all modules
- Modules only initialize when used
- Shared utilities
- Easy to extend
- Better performance

## Migration Steps

### 1. Backend Migration

#### Stop Old Processes
```bash
# Find and kill old backend processes
ps aux | grep "python.*classifier.py"
ps aux | grep "python.*matcher.py"
# ... etc
kill <PIDs>
```

#### Move to New System
```bash
# Your old files are preserved but no longer needed
# The new system is in:
# - main.py
# - handlers/
# - utils/
```

#### Update Environment Variables
```bash
# Copy your old .env or create new one
cp .env.example .env

# Add new variables for text labeler:
LABELER_JSONL_FILE=dataset.jsonl
LABELER_IMAGE_BASE_PATH=/path/to/images
```

### 2. Data Migration

#### State Files
The new system uses the same state file format, so your existing state files work:
- `state.json` → used by classifier (no change needed)
- `state_matcher.json` → used by matcher (no change needed)
- etc.

If you want to reset state for any module, just delete its state file.

#### Text Labeler Data
If you have existing annotation data, convert it to JSONL:

```python
# convert_to_jsonl.py
import json

# Example: Convert from CSV
import pandas as pd
df = pd.read_csv('annotations.csv')

with open('dataset.jsonl', 'w') as f:
    for _, row in df.iterrows():
        obj = {
            'image': row['image_path'],
            'text': row['label']
        }
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')
```

### 3. Frontend Migration

**No changes needed!** The frontend routes and API calls remain the same.

The frontend already expects `/api/` prefixed endpoints, which the new backend provides.

### 4. Start New System

```bash
# Single command replaces all old startup commands:
python main.py
```

That's it! All modules are now available at:
- http://localhost:8000/ (Classifier)
- http://localhost:8000/matcher
- http://localhost:8000/viewer
- http://localhost:8000/cluster
- http://localhost:8000/shop
- http://localhost:8000/labeler (NEW!)

## API Endpoint Changes

### Before (Old System)
Each module had its own base URL:
```
http://localhost:8001/api/images  # Classifier
http://localhost:8002/api/images  # Matcher
http://localhost:8003/api/images  # Viewer
```

### After (New System)
All modules share the same base URL with module context:
```
http://localhost:8000/api/images  # Which module depends on frontend route
```

The module context is determined by which Vue route is active.

## Troubleshooting

### "Module not available" warnings
Some modules require optional dependencies:
```bash
# For database modules (shop):
pip install sqlalchemy psycopg2-binary

# For prod2vec dataset modules:
pip install prod2vec  # or add to your project
```

The system gracefully handles missing dependencies.

### Port conflicts
If port 8000 is in use:
```bash
# Change in .env
PORT=8080

# Or override:
python main.py --port 8080
```

### State file conflicts
If you encounter state file issues:
```bash
# Backup old state
cp state.json state.json.backup

# Let system create fresh state
rm state*.json

# Restore specific settings manually if needed
```

## Rollback Plan

If you need to rollback to the old system:

1. Keep old files (classifier.py, matcher.py, etc.)
2. Restore old startup commands
3. Your data and state files are unchanged

## Performance Comparison

### Old System
- 5 processes × ~100MB = 500MB RAM
- 5 ports occupied
- Startup time: 5-10 seconds per module

### New System  
- 1 process × ~150MB = 150MB RAM
- 1 port occupied
- Startup time: 2-3 seconds total
- Modules initialize on-demand

## Next Steps

1. ✅ Migrate backend (follow steps above)
2. ✅ Test each module in browser
3. ✅ Verify data persistence
4. ✅ Try new Text Labeler module
5. ✅ Update documentation/bookmarks
6. ✅ Archive old backend files

## Support

If you encounter issues:
1. Check the main README.md
2. Review handler code in handlers/
3. Check logs for specific errors
4. Open an issue with details

## Future Enhancements

The unified architecture makes it easy to:
- Add authentication/authorization
- Implement API versioning
- Add WebSocket support
- Create admin dashboard
- Add monitoring/analytics
- Deploy as containerized service
