from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.utils.security import (
    verify_password, get_password_hash, create_access_token, 
    verify_token, sanitize_input
)
from app.utils.antivirus import AntivirusScanner

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Sanitizar inputs
    user.nombre = sanitize_input(user.nombre)
    user.email = sanitize_input(user.email.lower())
    
    # Verificar si email o nombre ya existe
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    existing_nombre = db.query(models.User).filter(
        models.User.nombre == user.nombre
    ).first()
    if existing_nombre:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    # Crear usuario
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        nombre=user.nombre,
        email=user.email,
        telefono=user.telefono,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear configuración por defecto
    config = models.ConfiguracionUsuario(
        user_id=db_user.id,
        idioma="es_EC",
        tema="claro"
    )
    db.add(config)
    
    # Crear licencia pendiente (requiere activación por admin)
    licencia = models.Licencia(
        user_id=db_user.id,
        tipo=models.TipoLicenciaEnum.mensual,
        estado=models.EstadoLicenciaEnum.pendiente
    )
    db.add(licencia)
    db.commit()
    
    return db_user

@router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username.lower()
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    # Verificar licencia
    licencia = db.query(models.Licencia).filter(
        models.Licencia.user_id == user.id
    ).first()
    
    if licencia and licencia.estado == models.EstadoLicenciaEnum.vencida:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Licencia vencida. Por favor renueve su licencia."
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "is_admin": user.is_admin},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "is_admin": user.is_admin,
            "idioma": user.configuracion.idioma if user.configuracion else "es_EC",
            "tema": user.configuracion.tema if user.configuracion else "claro"
        }
    }

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    return user

async def get_current_admin(
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores"
        )
    return current_user

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
