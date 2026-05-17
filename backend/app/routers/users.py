from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user
from app.utils.security import sanitize_input, encrypt_data

router = APIRouter()

@router.get("/configuracion", response_model=schemas.ConfiguracionUsuarioResponse)
async def get_configuracion(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    config = db.query(models.ConfiguracionUsuario).filter(
        models.ConfiguracionUsuario.user_id == current_user.id
    ).first()
    
    if not config:
        config = models.ConfiguracionUsuario(user_id=current_user.id)
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config

@router.put("/configuracion", response_model=schemas.ConfiguracionUsuarioResponse)
async def update_configuracion(
    config_data: schemas.ConfiguracionUsuarioCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    config = db.query(models.ConfiguracionUsuario).filter(
        models.ConfiguracionUsuario.user_id == current_user.id
    ).first()
    
    if not config:
        config = models.ConfiguracionUsuario(user_id=current_user.id)
        db.add(config)
    
    # Actualizar campos
    if config_data.smtp_host:
        config.smtp_host = sanitize_input(config_data.smtp_host)
    if config_data.smtp_port:
        config.smtp_port = config_data.smtp_port
    if config_data.smtp_user:
        config.smtp_user = sanitize_input(config_data.smtp_user)
    if config_data.smtp_pass:
        config.smtp_pass = encrypt_data(config_data.smtp_pass)
    if config_data.smtp_tls is not None:
        config.smtp_tls = config_data.smtp_tls
    if config_data.idioma:
        config.idioma = config_data.idioma
    if config_data.tema:
        config.tema = config_data.tema
    if config_data.backup_key:
        config.backup_key = encrypt_data(config_data.backup_key)
    
    db.commit()
    db.refresh(config)
    return config

@router.put("/password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.utils.security import verify_password, get_password_hash
    
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}
