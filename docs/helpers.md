# Helper commands

```bash
pip install fastapi uvicorn python-multipart pandas
cd frontend
npm install
npm run build
uvicorn main:app --reload
python -m cleaner.classifier
uvicorn backend.main:app --reload
uvicorn backend.main:app --reload --log-level debug
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

uvicorn cleaner.classifier:app --reload --workers 8
uvicorn cleaner.matcher:app --reload --workers 8
uvicorn cleaner.viewer:app --reload --workers 8
uvicorn cleaner.cluster:app --reload --workers 8

# no need for the following, use npm run dev.
npm run build && npm run preview


# vite
npm run dev
# http://localhost:5173/

# if you open http://localhost:8000/ routing worn't work correctly!

# Run on server
npx vite --host
```
