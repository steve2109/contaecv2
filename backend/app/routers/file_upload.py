from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import shutil
import tempfile
from datetime import datetime

from app.database import get_db
from app.models import models
from app.routers.auth import get_current_user
from app.utils.antivirus import AntivirusScanner
from app.utils.import_export import importar_excel, importar_csv, exportar_excel, exportar_csv, exportar_pdf

router = APIRouter()

UPLOAD_DIR = "/tmp/contaec_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'excel': ['.xlsx', '.xls'],
    'csv': ['.csv'],
    'pdf': ['.pdf'],
    'zip': ['.zip'],
    'images': ['.jpg', '.jpeg', '.png', '.gif']
}

@router.post("/import")
async def upload_file(
    file: UploadFile = File(...),
    tipo: str = "auto",  # auto, inventario, clientes, empleados, contabilidad
    virus_total: bool = False,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sube y procesa un archivo con escaneo antivirus"""
    
    # Validar extensión
    ext = os.path.splitext(file.filename)[1].lower()
    all_extensions = [e for exts in ALLOWED_EXTENSIONS.values() for e in exts]
    
    if ext not in all_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida. Permitidas: {', '.join(all_extensions)}"
        )
    
    # Guardar temporalmente
    temp_path = f"{UPLOAD_DIR}/tmp_{current_user.id}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Escanear con ClamAV (obligatorio)
        scan_result = await AntivirusScanner.scan_file(temp_path)
        
        if not scan_result["clean"]:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=f"Archivo rechazado - Contiene malware: {scan_result['message']}"
            )
        
        # Escanear con VirusTotal (opcional)
        if virus_total:
            vt_result = await AntivirusScanner.scan_virustotal(temp_path)
            if vt_result.get("positives", 0) > 0:
                os.remove(temp_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo marcado como sospechoso por VirusTotal"
                )
        
        # Procesar según tipo
        result = None
        if ext in ALLOWED_EXTENSIONS['excel']:
            result = await importar_excel(temp_path, tipo, current_user.id, db)
        elif ext in ALLOWED_EXTENSIONS['csv']:
            result = await importar_csv(temp_path, tipo, current_user.id, db)
        else:
            result = {"message": "Archivo escaneado y guardado", "path": temp_path}
        
        # Eliminar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "filename": file.filename,
            "size": os.path.getsize(temp_path) if os.path.exists(temp_path) else 0,
            "scan_result": scan_result,
            "processed": result
        }
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@router.get("/export/{tipo}")
async def export_data(
    tipo: str,  # inventario, clientes, empleados, facturas, roles_pago, contabilidad
    formato: str = "excel",  # excel, csv, pdf
    empresa_id: int = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exporta datos a formato solicitado"""
    
    if empresa_id:
        # Verificar que la empresa pertenece al usuario
        empresa = db.query(models.Empresa).filter(
            models.Empresa.id == empresa_id,
            models.Empresa.user_id == current_user.id
        ).first()
        
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_{tipo}_{timestamp}"
    
    if formato == "excel":
        file_path = await exportar_excel(tipo, empresa_id, current_user.id, db)
        filename += ".xlsx"
    elif formato == "csv":
        file_path = await exportar_csv(tipo, empresa_id, current_user.id, db)
        filename += ".csv"
    elif formato == "pdf":
        file_path = await exportar_pdf(tipo, empresa_id, current_user.id, db)
        filename += ".pdf"
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado")
    
    # El archivo será eliminado automáticamente después de la descarga
    # (en producción, usar tarea programada para limpiar archivos viejos)
    
    return {
        "file_path": file_path,
        "filename": filename,
        "formato": formato,
        "message": "Archivo generado correctamente"
    }

@router.post("/validate")
async def validate_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """Solo valida un archivo sin procesarlo (para pre-check)"""
    
    ext = os.path.splitext(file.filename)[1].lower()
    temp_path = f"{UPLOAD_DIR}/validate_{current_user.id}_{file.filename}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    scan_result = await AntivirusScanner.scan_file(temp_path)
    
    # Eliminar archivo de validación
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return {
        "filename": file.filename,
        "extension": ext,
        "is_safe": scan_result["clean"],
        "scan_details": scan_result
    }
