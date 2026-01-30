from fastapi import FastAPI

from app.routers import product, quotation, waiting_product


def create_app(context_path: str = "") -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ERP API",
        description="ERP System REST API (Python)",
        version="1.0.0",
        root_path=context_path,
    )

    app.include_router(product.router)
    app.include_router(quotation.router)
    app.include_router(waiting_product.router)

    return app
