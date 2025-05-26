from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.clientes import router as clientes_router
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.routers.users import router as users_router

from app.auth.deps import get_current_user

app = FastAPI(
    title="WhatsApp API",
    version="1.0.0"
)

# CORS middleware with secure, production-ready settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Change to your production domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Secure all routes with authentication
app.include_router(auth_router, prefix="/auth")
app.include_router(clientes_router, prefix="/clients", dependencies=[Depends(get_current_user)])
app.include_router(orders_router, prefix="/orders", dependencies=[Depends(get_current_user)])
app.include_router(products_router, prefix="/products", dependencies=[Depends(get_current_user)])
app.include_router(users_router, prefix="/users", dependencies=[Depends(get_current_user)])
