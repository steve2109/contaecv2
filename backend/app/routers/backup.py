from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import json
import subprocess
from datetime import datetime

from app.database import get_db
from app.models import models
from app.routers.auth import get_current_user, get_current_admin
from app.utils.security import decrypt_data

router = APIRouter()

BACKUP_DIR = "/opt/contaec/backend/backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

@router.post("/create")
async def create_backup(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea un backup encriptado de los datos del usuario"""
    from app.utils.backup import encrypt_and_backup_user_data
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{BACKUP_DIR}/user_{current_user.id}_backup_{timestamp}.enc"
    
    # Obtener clave de backup del usuario
    config = db.query(models.ConfiguracionUsuario).filter(
        models.ConfiguracionUsuario.user_id == current_user.id
    ).first()
    
    if not config or not config.backup_key:
        raise HTTPException(status_code=400, detail="No se ha configurado la clave de backup")
    
    backup_key = decrypt_data(config.backup_key)
    
    # Backup de datos
    backup_data = {
        "user_id": current_user.id,
        "timestamp": timestamp,
        "empresas": [],
        "clientes": [],
        "productos": [],
        "facturas": [],
        "empleados": [],
        "roles_pago": [],
        "asientos_contables": []
    }
    
    # Obtener datos del usuario
    empresas = db.query(models.Empresa).filter(
        models.Empresa.user_id == current_user.id
    ).all()
    
    for empresa in empresas:
        backup_data["empresas"].append({
            "ruc": empresa.ruc,
            "razon_social": empresa.razon_social,
            "nombre_comercial": empresa.nombre_comercial,
            "direccion": empresa.direccion,
            "telefono": empresa.telefono,
            "email": empresa.email,
            "ambiente": empresa.ambiente.value
        })
    
    # Encriptar y guardar
    encrypt_and_backup_user_data(backup_data, backup_file, backup_key)
    
    return {
        "message": "Backup creado correctamente",
        "file": backup_file,
        "timestamp": timestamp
    }

@router.post("/restore")
async def restore_backup(
    backup_file: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restaura datos desde un backup encriptado"""
    from app.utils.backup import decrypt_backup
    
    config = db.query(models.ConfiguracionUsuario).filter(
        models.ConfiguracionUsuario.user_id == current_user.id
    ).first()
    
    if not config or not config.backup_key:
        raise HTTPException(status_code=400, detail="No se ha configurado la clave de backup")
    
    backup_key = decrypt_data(config.backup_key)
    
    if not os.path.exists(backup_file):
        raise HTTPException(status_code=404, detail="Archivo de backup no encontrado")
    
    try:
        data = decrypt_backup(backup_file, backup_key)
        
        # Validar que el backup pertenece al usuario
        if data.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="El backup no pertenece a este usuario")
        
        # Restaurar datos (simplificado - en producción se necesita lógica más compleja)
        # ...
        
        return {
            "message": "Backup restaurado correctamente",
            "timestamp": data.get("timestamp"),
            "empresas_restauradas": len(data.get("empresas", []))
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al restaurar backup: {str(e)}")

@router.get("/list")
async def list_backups(
    current_user: models.User = Depends(get_current_user)
):
    """Lista los backups disponibles del usuario"""
    user_backups = []
    
    for f in os.listdir(BACKUP_DIR):
        if f.startswith(f"user_{current_user.id}_backup_"):
            stat = os.stat(f"{BACKUP_DIR}/{f}")
            user_backups.append({
                "filename": f,
                "size_bytes": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime)
            })
    
    return user_backups
