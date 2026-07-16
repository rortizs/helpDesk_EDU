from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import current_user
from app.models import User
from app.schemas.assistance import AssistanceIn, AssistanceOut
from app.services.assistance import AssistanceService

router = APIRouter()


@router.post("/api/assistance", response_model=AssistanceOut)
def suggest(body: AssistanceIn, _: Annotated[User, Depends(current_user)]) -> dict:
    return AssistanceService().suggest(body)