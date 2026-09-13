import os

# 1. Create requirements.txt for Render Cloud
reqs = """fastapi>=0.100.0
uvicorn[standard]>=0.20.0
python-socketio>=5.10.0
pydantic>=2.0.0
networkx>=3.0
scikit-learn>=1.3.0
numpy>=1.24.0
requests>=2.31.0
python-multipart>=0.0.6
"""
with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\requirements.txt", "w", encoding="utf-8") as f:
    f.write(reqs)

# 2. Update backend/app/main.py to serve React Frontend build in production
with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

spa_mount = """
# ── SERVE FRONTEND SPA IN PRODUCTION ──
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
"""

if "from fastapi.staticfiles import StaticFiles" not in code:
    code = code + "\n" + spa_mount
    with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "w", encoding="utf-8") as f:
        f.write(code)

# 3. Create render.yaml deployment configuration
render_yaml = """services:
  - type: web
    name: crimenet-ai
    env: python
    buildCommand: "cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT"
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
"""
with open(r"c:\Users\Aditya\Downloads\SIH 2026\render.yaml", "w", encoding="utf-8") as f:
    f.write(render_yaml)

print("Cloud Production deployment files created successfully!")
