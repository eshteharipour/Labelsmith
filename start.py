#!/usr/bin/env python3
"""
Startup script for Image Dataset Management System.

This script provides a convenient way to start the application with
various options and checks.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    required = ["fastapi", "uvicorn", "pandas"]
    optional = ["sqlalchemy", "httpx"]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False

    print("✅ All required dependencies installed")

    # Check optional dependencies
    missing_optional = []
    for package in optional:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)

    if missing_optional:
        print(f"⚠️  Optional packages not installed: {', '.join(missing_optional)}")
        print("Some features may be unavailable.")

    return True


def check_frontend():
    """Check if frontend is built."""
    dist_path = Path("cleaner/dist")
    if not dist_path.exists():
        print("⚠️  Frontend not built. Building now...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="cleaner", check=True)
            print("✅ Frontend built successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to build frontend")
            print("Run manually: cd cleaner && npm run build")
            return False
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js")
            return False
    else:
        print("✅ Frontend already built")

    return True


def load_env():
    """Load environment variables from .env file."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Using defaults.")
        print("Consider creating one: cp .env.example .env")
    else:
        print("✅ Loading configuration from .env")


def main():
    parser = argparse.ArgumentParser(
        description="Image Dataset Management System Launcher"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--skip-checks", action="store_true", help="Skip dependency and frontend checks"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Image Dataset Management System")
    print("=" * 60)
    print()

    # Run checks
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)

        if not check_frontend():
            sys.exit(1)

    load_env()

    print()
    print("=" * 60)
    print(f"Starting server on http://{args.host}:{args.port}")
    print("=" * 60)
    print()
    print("Available modules:")
    print(f"  → Classifier:    http://localhost:{args.port}/")
    print(f"  → Matcher:       http://localhost:{args.port}/matcher")
    print(f"  → Viewer:        http://localhost:{args.port}/viewer")
    print(f"  → Cluster:       http://localhost:{args.port}/cluster")
    print(f"  → Shop:          http://localhost:{args.port}/shop")
    print(f"  → Text Labeler:  http://localhost:{args.port}/labeler")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Start the server
    try:
        import uvicorn

        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            reload_dirs=["handlers", "utils"] if args.reload else None,
        )
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        print("Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
