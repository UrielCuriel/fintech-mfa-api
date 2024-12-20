from fastapi import APIRouter

from app.api.routes import login, auth, users

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])