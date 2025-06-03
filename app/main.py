
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.routers.child_router import router as child_router
from app.routers.hine_exam import router as hine_exam_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Incluir los routers
app.include_router(child_router, prefix="/children", tags=["Children"])
app.include_router(hine_exam_router, prefix="/hineExam", tags=["Hine Exam"])
