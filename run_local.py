"""Civic_AI — Streamlined Single-Command Application Launcher.

Launches both backend (FastAPI on :8000) and frontend (Vite React on :5173)
concurrently with graceful shutdown on Ctrl+C and zero-friction setup.

Usage:
    python run_local.py              # Starts both backend + frontend
    python run_local.py --backend    # Starts backend only (port 8000)
    python run_local.py --frontend   # Starts frontend only (port 5173)
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

backend_dir = PROJECT_ROOT / "backend"
frontend_dir = PROJECT_ROOT / "frontend"
data_dir = PROJECT_ROOT / "data"
data_dir.mkdir(exist_ok=True)

# 1. Zero-Friction: Ensure .env exists from template if missing
env_file = PROJECT_ROOT / ".env"
env_example = PROJECT_ROOT / ".env.example"
if not env_file.exists() and env_example.exists():
    print("ℹ️  .env not found. Creating default .env from .env.example...")
    shutil.copy(env_example, env_file)

# Ensure backend directory is in sys.path
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def ensure_frontend_deps():
    """Ensure frontend dependencies are installed if node_modules is missing."""
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies (one-time setup)...")
        shell = sys.platform == "win32"
        subprocess.run("npm install", cwd=str(frontend_dir), shell=shell, check=True)


def run_backend():
    """Run FastAPI Uvicorn backend synchronously."""
    import uvicorn
    print("🚀 Starting Civic_AI Backend on http://localhost:8000...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=str(backend_dir),
    )


def run_frontend():
    """Run Vite frontend dev server."""
    ensure_frontend_deps()
    print("✨ Starting Civic_AI Frontend on http://localhost:5173...")
    cmd = "npm run dev"
    shell = sys.platform == "win32"
    subprocess.run(cmd, cwd=str(frontend_dir), shell=shell)


def run_both():
    """Run both backend and frontend concurrently."""
    ensure_frontend_deps()

    print("=" * 68)
    print("  🏛️  Civic_AI — Digital Public Governance & Citizen Intelligence")
    print("=" * 68)
    print("  Frontend Web App:  http://localhost:5173")
    print("  Backend REST API:  http://localhost:8000")
    print("  Interactive Docs:  http://localhost:8000/docs")
    print("  Health Status:     http://localhost:8000/health")
    print("=" * 68)
    print("  Press CTRL+C at any time to gracefully stop all services.\n")

    shell = sys.platform == "win32"
    python_exe = sys.executable

    # 1. Start backend process
    backend_proc = subprocess.Popen(
        [python_exe, "run_local.py", "--backend"],
        cwd=str(PROJECT_ROOT),
    )

    # Allow backend to bind port
    time.sleep(1.5)

    # 2. Start frontend process
    frontend_proc = subprocess.Popen(
        "npm run dev",
        cwd=str(frontend_dir),
        shell=shell,
    )

    def shutdown(sig, frame):
        print("\n🛑 Gracefully shutting down Civic_AI...")
        for proc in [frontend_proc, backend_proc]:
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)])
                else:
                    proc.terminate()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Wait for either process to terminate
    while True:
        if backend_proc.poll() is not None:
            print("Backend process exited.")
            shutdown(None, None)
        if frontend_proc.poll() is not None:
            print("Frontend process exited.")
            shutdown(None, None)
        time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Civic_AI Launcher")
    parser.add_argument("--backend", action="store_true", help="Start only backend")
    parser.add_argument("--frontend", action="store_true", help="Start only frontend")
    args = parser.parse_args()

    if args.backend:
        run_backend()
    elif args.frontend:
        run_frontend()
    else:
        run_both()
