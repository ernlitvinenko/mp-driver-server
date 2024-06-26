from fastapi import APIRouter

from .auth import auth_router
from .tasks import tasks_router

router = APIRouter(prefix="/api/v1")

# Include your routers
router.include_router(auth_router)
router.include_router(tasks_router)
