from fastapi import APIRouter, Depends, status

from app.auth.auth_utils import get_current_user
from app.schemas.advisor import AdvisorCreate, AdvisorResponse
from app.services.advisor_service import AdvisorService


router = APIRouter()
service = AdvisorService()

@router.post("/", response_model=AdvisorResponse,status_code=status.HTTP_201_CREATED)
async def create_advisor(advisor:AdvisorCreate, current_user: dict = Depends(get_current_user)):
	return service.create_advisor(advisor)