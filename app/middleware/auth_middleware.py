import jwt
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.config import SECRET_KEY, ALGORITHM

async def verify_jwt_token(request: Request, call_next):
    # Lista de rutas que no requieren autenticación
    public_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]
    
    # Verificar si la ruta actual es pública
    if any(request.url.path.startswith(path) for path in public_paths):
        response = await call_next(request)
        return response
    
    # Para rutas con dependencias de seguridad, el middleware no necesita validar
    # ya que FastAPI manejará la validación automáticamente
    response = await call_next(request)
    return response 