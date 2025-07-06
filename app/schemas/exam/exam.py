from pydantic import BaseModel
from typing import List, Optional

class QuestionResponse(BaseModel):
    questionId: str
    selectedValue: int
    leftAsymmetry: bool
    rightAsymmetry: bool
    comment: Optional[str] = None

class BehaviorResponse(BaseModel):
    questionId: str
    selectedValue: int
    comment: Optional[str] = None

class ModuleResponse(BaseModel):
    moduleId: str
    obtainedScore: int
    responses: List[QuestionResponse]

class AnalysisData(BaseModel):
    modules: List[ModuleResponse]
    totalScore: int
    maxPossibleScore: int
    totalRightAsymmetries: int
    totalLeftAsymmetries: int

class MotorMilestoneData(BaseModel):
    responses: List[QuestionResponse]

class BehaviorData(BaseModel):
    responses: List[BehaviorResponse]

class HineExam(BaseModel):
    examId: str
    patientId: str
    userId: str
    examDate: str
    analysis: AnalysisData
    motorMilestones: MotorMilestoneData
    behavior: BehaviorData
