from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.security import HTTPBearer
from app.routers.advisor_router import router as advisor_router
from app.routers.child_router import router as child_router
from app.routers.hine_exam import router as hine_exam_router
from app.middleware.auth_middleware import verify_jwt_token
from app.auth.auth_utils import get_current_user

# Configurar el esquema de seguridad
security_scheme = HTTPBearer()

app = FastAPI(
    title="FormsHine API",
    description="API para gestión de formularios HINE con autenticación JWT",
    version="1.0.0",
    openapi_tags=[
        {"name": "Children", "description": "Operaciones relacionadas con niños"},
        {"name": "Hine Exam", "description": "Operaciones relacionadas con exámenes HINE"},
        {"name": "Advisor", "description": "Operaciones relacionadas con exámenes HINE"}
    ]
)

# Agregar middleware de autenticación JWT
app.middleware("http")(verify_jwt_token)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de prueba para verificar tokens
@app.get("/test-token")
async def test_token(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Token válido!",
        "user_data": current_user
    }

# Incluir los routers
app.include_router(child_router, prefix="/children", tags=["Children"])
app.include_router(hine_exam_router, prefix="/hineExam", tags=["Hine Exam"])
app.include_router(advisor_router, prefix="/advisors", tags=["Advisor"])
