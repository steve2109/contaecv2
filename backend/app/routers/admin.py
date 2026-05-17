from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user, get_current_admin
from app.utils.security import sanitize_input
from app.utils.backup import create_system_backup

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/dashboard")
async def admin_dashboard(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Estadísticas generales
    total_users = db.query(models.User).count()
    total_empresas = db.query(models.Empresa).count()
    total_facturas = db.query(models.Factura).count()
    total_empleados = db.query(models.Empleado).count()
    
    # Licencias por estado
    licencias_activas = db.query(models.Licencia).filter(
        models.Licencia.estado == models.EstadoLicenciaEnum.activa
    ).count()
    licencias_vencidas = db.query(models.Licencia).filter(
        models.Licencia.estado == models.EstadoLicenciaEnum.vencida
    ).count()
    licencias_pendientes = db.query(models.Licencia).filter(
        models.Licencia.estado == models.EstadoLicenciaEnum.pendiente
    ).count()
    
    # Usuarios con licencias próximas a vencer (7 días)
    proximos_a_vencer = db.query(models.Licencia).filter(
        models.Licencia.estado == models.EstadoLicenciaEnum.activa,
        models.Licencia.fecha_fin <= datetime.utcnow() + timedelta(days=7)
    ).all()
    
    return {
        "resumen": {
            "total_usuarios": total_users,
            "total_empresas": total_empresas,
            "total_facturas_emitidas": total_facturas,
            "total_empleados_registrados": total_empleados,
            "licencias_activas": licencias_activas,
            "licencias_vencidas": licencias_vencidas,
            "licencias_pendientes": licencias_pendientes
        },
        "proximos_a_vencer": [
            {
                "user_id": l.user_id,
                "email": l.user.email,
                "nombre": l.user.nombre,
                "fecha_fin": l.fecha_fin,
                "dias_restantes": (l.fecha_fin - datetime.utcnow()).days if l.fecha_fin else 0
            }
            for l in proximos_a_vencer
        ]
    }

@router.get("/system-health")
async def system_health(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    import psutil
    import os
    
    # Información del sistema
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Información de la base de datos
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Logs recientes (últimas 100 líneas)
    logs = []
    log_file = "/var/log/contaec/app.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]
    
    return {
        "servidor": {
            "cpu_uso_porcentaje": cpu_percent,
            "memoria_total_gb": round(memory.total / (1024**3), 2),
            "memoria_usada_gb": round(memory.used / (1024**3), 2),
            "memoria_libre_gb": round(memory.available / (1024**3), 2),
            "memoria_porcentaje": memory.percent,
            "disco_total_gb": round(disk.total / (1024**3), 2),
            "disco_usado_gb": round(disk.used / (1024**3), 2),
            "disco_libre_gb": round(disk.free / (1024**3), 2),
            "disco_porcentaje": disk.percent
        },
        "base_de_datos": db_status,
        "ultimos_logs": logs[-20:]
    }

@router.get("/usuarios")
async def list_usuarios_admin(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()
    
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "telefono": u.telefono,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "licencia": {
                "tipo": u.licencia.tipo.value if u.licencia else None,
                "estado": u.licencia.estado.value if u.licencia else None,
                "fecha_inicio": u.licencia.fecha_inicio if u.licencia else None,
                "fecha_fin": u.licencia.fecha_fin if u.licencia else None,
                "dias_restantes": (u.licencia.fecha_fin - datetime.utcnow()).days if u.licencia and u.licencia.fecha_fin else None
            },
            "total_empresas": len(u.empresas)
        }
        for u in users
    ]

@router.put("/usuarios/{user_id}/licencia")
async def update_licencia(
    user_id: int,
    tipo: schemas.TipoLicenciaEnum,
    meses: int = 1,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    licencia = db.query(models.Licencia).filter(
        models.Licencia.user_id == user_id
    ).first()
    
    if not licencia:
        licencia = models.Licencia(user_id=user_id)
        db.add(licencia)
    
    licencia.tipo = tipo
    licencia.estado = models.EstadoLicenciaEnum.activa
    licencia.fecha_inicio = datetime.utcnow()
    licencia.fecha_fin = datetime.utcnow() + timedelta(days=30 * meses)
    
    db.commit()
    db.refresh(licencia)
    
    return {
        "message": f"Licencia actualizada correctamente",
        "user_id": user_id,
        "tipo": tipo.value,
        "fecha_fin": licencia.fecha_fin,
        "dias_restantes": (licencia.fecha_fin - datetime.utcnow()).days
    }

@router.get("/seguridad")
async def security_dashboard(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Logs de actividad sospechosa
    logs = db.query(models.LogActividad).order_by(
        models.LogActividad.created_at.desc()
    ).limit(100).all()
    
    # Intentos de login fallidos (simulado - en producción se necesita tabla específica)
    
    # Usuarios con actividad reciente
    usuarios_activos = db.query(models.User).filter(
        models.User.is_active == True
    ).all()
    
    return {
        "total_logs": db.query(models.LogActividad).count(),
        "ultimos_logs": [
            {
                "fecha": l.created_at,
                "usuario": l.user.nombre if l.user else "Sistema",
                "accion": l.accion,
                "modulo": l.modulo,
                "descripcion": l.descripcion,
                "ip": l.ip_address
            }
            for l in logs
        ],
        "usuarios_activos": len(usuarios_activos),
        "usuarios_inactivos": db.query(models.User).filter(
            models.User.is_active == False
        ).count()
    }

@router.post("/backup-manual")
async def manual_backup(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    backup_path = create_system_backup()
    
    return {
        "message": "Backup creado correctamente",
        "path": backup_path,
        "timestamp": datetime.utcnow()
    }
