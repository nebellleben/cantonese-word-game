from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.routes import auth, decks, games, statistics, admin

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="API for Cantonese Word Game - A pronunciation learning game",
)

print(f"CORS Origins configured: {settings.cors_origins}")
print(f"CORS Origins type: {type(settings.cors_origins)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(decks.router, prefix=settings.api_v1_prefix)
app.include_router(games.router, prefix=settings.api_v1_prefix)
app.include_router(statistics.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/assets", StaticFiles(directory=static_path / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for all non-API routes."""
        file_path = static_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_path / "index.html")
else:

    @app.get("/")
    async def root():
        """Root endpoint (API-only mode)."""
        return {
            "message": "Cantonese Word Game API",
            "version": "1.0.0",
            "docs": "/docs",
        }
