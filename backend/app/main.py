from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, decks, games, statistics, admin

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="API for Cantonese Word Game - A pronunciation learning game",
)

# Debug: Print CORS origins
print(f"CORS Origins configured: {settings.cors_origins}")
print(f"CORS Origins type: {type(settings.cors_origins)}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(decks.router, prefix=settings.api_v1_prefix)
app.include_router(games.router, prefix=settings.api_v1_prefix)
app.include_router(statistics.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Cantonese Word Game API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


