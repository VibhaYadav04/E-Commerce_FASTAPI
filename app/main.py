from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi # for swagger implementation

from app.auth import models as auth_models
from app.core.database import engine # engine to connect to database

from app.auth.routes import router as auth_router
from app.products.routes import router as product_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as order_router
from app.checkout.routes import router as checkout_router

# Create tables
auth_models.Base.metadata.create_all(bind=engine) #base..- create table query, bind=engine -- connect to database

# Initialize FastAPI
app = FastAPI(title="E-commerce API", version="1.0")

# Include routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(product_router, prefix="", tags=["Products"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(checkout_router, prefix="/checkout", tags=["Checkout"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])

@app.get("/")
def root():
    return {"message": "E-commerce backend running..."}

# Customize Swagger UI to show single Bearer field
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="E-commerce API",
        version="1.0",
        description="FastAPI E-commerce backend with JWT authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}] # Add BearerAuth to all routes

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
