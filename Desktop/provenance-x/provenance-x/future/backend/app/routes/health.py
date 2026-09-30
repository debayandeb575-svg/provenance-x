from fastapi import APIRouter

from ..schemas import HealthResponse


router = APIRouter(
    tags=["system"]
)


@router.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return HealthResponse(

        status="ok",

        service="provenance-x-backend",

        version="1.0.0",
    )