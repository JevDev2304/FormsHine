from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class QuestionResponse(BaseModel):
    questionId: str
    selectedValue: int
    leftAsymmetry: bool
    rightAsymmetry: bool
    comment: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class BehaviorResponse(BaseModel):
    questionId: str
    selectedValue: int
    comment: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ModuleResponse(BaseModel):
    moduleId: str
    obtainedScore: int
    responses: List[QuestionResponse]
    model_config = ConfigDict(from_attributes=True)

class AnalysisData(BaseModel):
    modules: List[ModuleResponse]
    totalScore: int
    maxPossibleScore: int
    generalComments: List[str]
    totalRightAsymmetries: int
    totalLeftAsymmetries: int
    model_config = ConfigDict(from_attributes=True)

class MotorMilestoneData(BaseModel):
    responses: List[QuestionResponse]
    generalComments: List[str]
    model_config = ConfigDict(from_attributes=True)


class BehaviorData(BaseModel):
    responses: List[BehaviorResponse]
    generalComments: List[str]
    model_config = ConfigDict(from_attributes=True)


class HineExam(BaseModel):
    examId: Optional[UUID]=None
    patientId: str
    userId: str
    doctorName: Optional[str] = None
    examDate: str
    analysis: AnalysisData
    motorMilestones: MotorMilestoneData
    behavior: BehaviorData
    gestationalAge:str
    cronologicalAge:str
    correctedAge:str
    headCircumference:str
    model_config = ConfigDict(from_attributes=True)

