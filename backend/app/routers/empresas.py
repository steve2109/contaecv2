from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user
from app.utils.security import sanitize_input, validate_ruc
from app.utils.antivirus import AntivirusScanner

router = APIRouter()

UPLOAD_DIR = "/opt/contaec/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[schemas.EmpresaResponse])
async def list_empresas(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Empresa).filter(
        models.Empresa.user_id == current_user.id
    ).all()

@router.post("/", response_model=schemas.EmpresaResponse)
async def create_empresa(
    empresa: schemas.EmpresaCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validar RUC
    if not validate_ruc(empresa.ruc):
        raise HTTPException(status_code=400, detail="RUC inválido")
    
    # Sanitizar inputs
    empresa.razon_social = sanitize_input(empresa.razon_social)
    empresa.nombre_comercial = sanitize_input(empresa.nombre_comercial)
    
    # Verificar RUC único para este usuario
    existing = db.query(models.Empresa).filter(
        models.Empresa.user_id == current_user.id,
        models.Empresa.ruc == empresa.ruc
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una empresa con este RUC")
    
    db_empresa = models.Empresa(
        user_id=current_user.id,
        ruc=empresa.ruc,
        razon_social=empresa.razon_social,
        nombre_comercial=empresa.nombre_comercial,
        direccion=sanitize_input(empresa.direccion),
        telefono=sanitize_input(empresa.telefono),
        email=empresa.email,
        contribuyente_especial=empresa.contribuyente_especial,
        obligado_contabilidad=empresa.obligado_contabilidad,
        ambiente=empresa.ambiente
    )
    
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    
    return db_empresa

@router.get("/{empresa_id}", response_model=schemas.EmpresaResponse)
async def get_empresa(
    empresa_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return empresa

@router.put("/{empresa_id}", response_model=schemas.EmpresaResponse)
async def update_empresa(
    empresa_id: int,
    empresa_data: schemas.EmpresaCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    empresa.razon_social = sanitize_input(empresa_data.razon_social)
    empresa.nombre_comercial = sanitize_input(empresa_data.nombre_comercial)
    empresa.direccion = sanitize_input(empresa_data.direccion)
    empresa.telefono = sanitize_input(empresa_data.telefono)
    empresa.email = empresa_data.email
    empresa.contribuyente_especial = empresa_data.contribuyente_especial
    empresa.obligado_contabilidad = empresa_data.obligado_contabilidad
    empresa.ambiente = empresa_data.ambiente
    
    db.commit()
    db.refresh(empresa)
    return empresa

@router.post("/{empresa_id}/logo")
async def upload_logo(
    empresa_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    # Validar tipo de archivo
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPEG, PNG o GIF")
    
    # Guardar temporalmente
    temp_path = f"{UPLOAD_DIR}/temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Escanear
    scan_result = await AntivirusScanner.scan_file(temp_path)
    if not scan_result["clean"]:
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail=f"Archivo rechazado: {scan_result['message']}")
    
    # Guardar definitivamente
    ext = file.filename.split('.')[-1]
    logo_path = f"{UPLOAD_DIR}/logos/{empresa_id}_logo.{ext}"
    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
    shutil.move(temp_path, logo_path)
    
    empresa.logo_path = logo_path
    db.commit()
    
    return {"message": "Logo actualizado correctamente", "path": logo_path}

@router.post("/{empresa_id}/firma")
async def upload_firma(
    empresa_id: int,
    clave: str,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    if file.content_type != "application/x-pkcs12":
        raise HTTPException(status_code=400, detail="La firma debe ser un archivo .p12")
    
    temp_path = f"{UPLOAD_DIR}/temp_firma_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    scan_result = await AntivirusScanner.scan_file(temp_path)
    if not scan_result["clean"]:
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail=f"Archivo rechazado: {scan_result['message']}")
    
    # Guardar firma
    firma_path = f"{UPLOAD_DIR}/firmas/{empresa_id}_firma.p12"
    os.makedirs(os.path.dirname(firma_path), exist_ok=True)
    shutil.move(temp_path, firma_path)
    
    # Encriptar y guardar clave
    from app.utils.security import encrypt_data
    empresa.firma_path = firma_path
    empresa.firma_clave = encrypt_data(clave)
    
    # Extraer fecha de validez (simplificado - en producción usar cryptography)
    # Aquí se debería extraer del certificado
    empresa.firma_valida_hasta = datetime.now().date() + timedelta(days=365)
    
    db.commit()
    
    return {
        "message": "Firma electrónica cargada correctamente",
        "valida_hasta": empresa.firma_valida_hasta
    }

@router.get("/{empresa_id}/switch-ambiente")
async def switch_ambiente(
    empresa_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    # Alternar entre pruebas y producción
    if empresa.ambiente == models.AmbienteEnum.pruebas:
        empresa.ambiente = models.AmbienteEnum.produccion
    else:
        empresa.ambiente = models.AmbienteEnum.pruebas
    
    db.commit()
    
    return {
        "message": "Ambiente cambiado correctamente",
        "ambiente": empresa.ambiente.value,
        "ambiente_texto": "Pruebas" if empresa.ambiente == models.AmbienteEnum.pruebas else "Producción"
    }
