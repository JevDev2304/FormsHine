from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.child import ChildResponse, ChildCreate
from app.services.child_service import ChildService
from app.models.child import Children as Child
from app.services.exam_service import ExamService
from app.services.section_service import SectionService
from app.services.item_service import ItemService
from app.schemas.section import CreateSection
from app.schemas.item import CreateItem
from app.auth.auth_utils import get_current_user

router = APIRouter()
service = ChildService()
service2 = ExamService()
service3 = SectionService()
service4= ItemService()

@router.get("/", response_model=List[ChildResponse])
async def get_children(current_user: dict = Depends(get_current_user)):
    return service.get_all_children()

@router.get("/{child_id}", response_model=ChildResponse)
async def get_child_by_id(child_id: str, current_user: dict = Depends(get_current_user)):
    child = service.get_child_by_id(child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return child

@router.post("/", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(child: ChildCreate, current_user: dict = Depends(get_current_user)):
    return service.create_child(child)

@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(child_id: str, child: Child, current_user: dict = Depends(get_current_user)):
    updated_child = service.update_child(child_id, child)
    if updated_child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return updated_child

@router.delete("/{child_id}", response_model=dict)
async def delete_child(child_id: str, current_user: dict = Depends(get_current_user)):
    success = service.soft_delete_child(child_id)
    if not success:
        raise HTTPException(status_code=404, detail="Child not found")
    return {"detail": "Child deleted"}

