from fastapi import APIRouter

from .langgraph import router as langgraph_router
from .db import router as db_router

router = APIRouter(prefix="/api")
router.include_router(langgraph_router)
router.include_router(db_router)