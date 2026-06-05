import json
import os
from fastapi import APIRouter, Depends
from app.core.config import settings

router = APIRouter()

@router.get("/policy")
async def get_policy():
    """
    Returns the JSON loaded from settings.POLICY_TERMS_PATH.
    If the file is not found, returns an empty dictionary.
    """
    if not settings.POLICY_TERMS_PATH or not os.path.exists(settings.POLICY_TERMS_PATH):
        return {}
    try:
        with open(settings.POLICY_TERMS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@router.get("/health")
async def get_health():
    """
    Returns API health and version details.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "engine": "ClaimIQ Adjudication API"
    }
