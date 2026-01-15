"""API V1 Endpoints Package"""

from fastapi import APIRouter
from app.api.v1.endpoints import kyc, rules

api_router = APIRouter()

# Include domain-specific routers
api_router.include_router(kyc.router)
api_router.include_router(rules.router)

# Future routers
# api_router.include_router(aml.router)
# api_router.include_router(credit.router)
