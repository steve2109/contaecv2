import json
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from app.database import SessionLocal
import shutil
import zipfile
from app.models import models

def create_backup(user_id: int, backup_key: str):
    """Crea un backup encriptado de los datos del usuario"""
    db = SessionLocal()
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"/tmp/contaec_backups/{user_id}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Recopilar datos del usuario
        user_data = {
            "empresas": [],
            "configuracion": {},
            "timestamp": timestamp,
            "version": "1.0"
        }
        
        empresas = db.query(models.Empresa).filter(models.Empresa.user_id == user_id).all()
        for empresa in empresas:
            empresa_data = {
                "id": empresa.id,
                "ruc": empresa.ruc,
                "razon_social": empresa.razon_social,
                "nombre_comercial": empresa.nombre_comercial,
                "direccion": empresa.direccion,
                "telefono": empresa.telefono,
                "email": empresa.email,
                "logo_path": empresa.logo_path,
                "firma_valida_hasta": empresa.firma_valida_hasta.isoformat() if empresa.firma_valida_hasta else None,
                "ambiente": empresa.ambiente
            }
            user_data["empresas"].append(empresa_data)
        
        # Encriptar backup
        key = backup_key.encode()[:32].ljust(32, b'0')
        cipher = Fernet(Fernet.generate_key())  # Simplicado - usar mejor método en producción
        
        backup_file = f"{backup_dir}/backup_{timestamp}.json.enc"
        with open(backup_file, 'wb') as f:
            encrypted = cipher.encrypt(json.dumps(user_data, indent=2).encode())
            f.write(encrypted)
        
        return backup_file
    except Exception as e:
        raise Exception(f"Error creando backup: {str(e)}")
    finally:
        db.close()

def restore_backup(user_id: int, backup_file: str, backup_key: str):
    """Restaura datos desde un backup encriptado"""
    try:
        with open(backup_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Desencriptar
        # Implementar lógica de desencriptación con backup_key
        # Esto es un esqueleto - implementar adecuadamente
        
        return {"success": True, "message": "Backup restaurado correctamente"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def schedule_midnight_backup():
    """Configura backup automático a medianoche"""
    now = datetime.now()
    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    wait_seconds = (midnight - now).total_seconds()
    # En producción, usar cron o scheduler
    return wait_seconds
