#!/usr/bin/env python
"""
Development server launcher
Starts FastAPI with SQLite (no Docker required)
"""
import uvicorn
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting AYDN Backend in Development Mode")
    print("=" * 60)
    print("")
    print("📦 Database: SQLite (aydn_reviews.db)")
    print("🌐 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("")
    print("⚠️  Note: Celery workers disabled in dev mode")
    print("   Manual HTML upload will work, scraping won't.")
    print("")
    print("=" * 60)
    print("")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
