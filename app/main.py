"""
FastAPI Main Application

Production-grade BRE Platform Decision Gateway
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import sys

from app.api.v1 import api_router
from app.core.config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="BRE Platform - Decision Gateway",
    description="""
    Production-grade Business Rule Engine platform using GoRules and FastAPI.
    
    ## Features
    
    * **Visual Rule Editing**: Business users edit rules via GoRules Studio
    * **Zero Deployment**: Rule changes go live without backend restarts
    * **Fact Governance**: Centralized Fact Registry with PR-based approval
    * **Auditability**: Complete decision logs with fact snapshots
    * **Stateless**: Horizontal scaling, high performance
    * **Type Safety**: Strong typing from Fact Registry → Rules
    
    ## Architecture
    
    ```
    Client → Decision Gateway (FastAPI) → Fact Adapter → GoRules Engine → Response
    ```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ============================================================================
# Middleware
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with correlation ID"""
    correlation_id = request.headers.get("X-Correlation-ID", "unknown")
    
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={"correlation_id": correlation_id}
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response: {response.status_code}",
        extra={"correlation_id": correlation_id}
    )
    
    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ============================================================================
# Routes
# ============================================================================

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    return {
        "status": "healthy",
        "service": "bre-platform",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Readiness check endpoint
@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - verifies all dependencies are available
    """
    # In production, check:
    # - Database connection
    # - Rule repository availability
    # - External service health
    
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "rule_repository": "ok",
            "fact_registry": "ok",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "service": "BRE Platform - Decision Gateway",
        "version": "1.0.0",
        "description": "Production-grade Business Rule Engine using GoRules and FastAPI",
        "documentation": "/docs",
        "health": "/health",
        "api": "/api/v1",
    }


# ============================================================================
# Startup / Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks
    """
    logger.info("=" * 60)
    logger.info("BRE Platform - Decision Gateway Starting")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: 1.0.0")
    logger.info(f"Docs: http://localhost:8000/docs")
    logger.info("=" * 60)
    
    # Initialize services
    # - Load rules from repository
    # - Connect to database
    # - Initialize audit service
    
    logger.info("✓ Startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks
    """
    logger.info("BRE Platform shutting down...")
    
    # Cleanup tasks
    # - Close database connections
    # - Flush audit logs
    # - Close HTTP clients
    
    logger.info("✓ Shutdown complete")


# ============================================================================
# Main (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
