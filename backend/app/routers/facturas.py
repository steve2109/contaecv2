from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal
import xml.etree.ElementTree as ET

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user
from app.utils.security import sanitize_input
from app.utils.sri import generar_clave_acceso, firmar_xml, enviar_sri, consultar_autorizacion

router = APIRouter()

@router.get("/empresa/{empresa_id}", response_model=List[schemas.FacturaResponse])
async def list_facturas(
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
    
    return db.query(models.Factura).filter(
        models.Factura.empresa_id == empresa_id
    ).order_by(models.Factura.fecha_emision.desc()).all()

@router.post("/empresa/{empresa_id}/generar", response_model=schemas.FacturaResponse)
async def create_factura(
    empresa_id: int,
    factura: schemas.FacturaCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == factura.cliente_id,
        models.Cliente.empresa_id == empresa_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Calcular totales
    subtotal = Decimal("0")
    total_iva = Decimal("0")
    total_descuento = Decimal("0")
    
    detalles_db = []
    for detalle in factura.detalles:
        cantidad = detalle.cantidad
        precio_unitario = detalle.precio_unitario
        descuento = detalle.descuento or Decimal("0")
        
        total_sin_imp = (cantidad * precio_unitario) - descuento
        iva_valor = total_sin_imp * Decimal("0.12") if empresa.obligado_contabilidad else Decimal("0")
        
        subtotal += total_sin_imp
        total_iva += iva_valor
        total_descuento += descuento
        
        detalle_db = models.DetalleFactura(
            producto_id=detalle.producto_id,
            codigo_principal=detalle.codigo_principal,
            descripcion=sanitize_input(detalle.descripcion),
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            descuento=descuento,
            total_sin_impuestos=total_sin_imp,
            iva_valor=iva_valor
        )
        detalles_db.append(detalle_db)
    
    total = subtotal + total_iva
    
    # Generar clave de acceso
    clave_acceso = generar_clave_acceso(empresa, cliente, datetime.now())
    
    db_factura = models.Factura(
        empresa_id=empresa_id,
        cliente_id=factura.cliente_id,
        clave_acceso=clave_acceso,
        ambiente=factura.ambiente or empresa.ambiente,
        tipo_comprobante=factura.tipo_comprobante,
        forma_pago=factura.forma_pago,
        subtotal_sin_impuestos=subtotal,
        total_descuento=total_descuento,
        total_iva=total_iva,
        total=total,
        observaciones=sanitize_input(factura.observaciones),
        estado="PENDIENTE"
    )
    db.add(db_factura)
    db.commit()
    db.refresh(db_factura)
    
    for detalle in detalles_db:
        detalle.factura_id = db_factura.id
        db.add(detalle)
    
    db.commit()
    db.refresh(db_factura)
    
    return db_factura

@router.post("/{factura_id}/firmar")
async def firmar_factura(
    factura_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    factura = db.query(models.Factura).join(models.Empresa).filter(
        models.Factura.id == factura_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    empresa = factura.empresa
    
    # Generar XML
    xml_content = generar_xml_factura(factura)
    
    # Firmar con la firma electrónica
    xml_firmado = firmar_xml(xml_content, empresa.firma_path, empresa.firma_clave)
    
    factura.xml_firmado = xml_firmado
    factura.estado = "FIRMADA"
    db.commit()
    
    return {"message": "Factura firmada correctamente", "estado": factura.estado}

@router.post("/{factura_id}/enviar-sri")
async def enviar_factura_sri(
    factura_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    factura = db.query(models.Factura).join(models.Empresa).filter(
        models.Factura.id == factura_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if not factura.xml_firmado:
        raise HTTPException(status_code=400, detail="La factura debe ser firmada primero")
    
    # Enviar al SRI
    respuesta = enviar_sri(factura.xml_firmado, factura.ambiente)
    
    factura.respuesta_sri = str(respuesta)
    
    if respuesta.get("estado") == "RECIBIDA":
        factura.estado = "AUTORIZADA"
    elif respuesta.get("estado") == "DEVUELTA":
        factura.estado = "RECHAZADA"
    else:
        factura.estado = "ENVIADA"
    
    db.commit()
    
    return {
        "message": f"Factura enviada al SRI: {respuesta.get('estado')}",
        "estado": factura.estado,
        "respuesta": respuesta
    }

@router.get("/{factura_id}/pdf")
async def generar_pdf(
    factura_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.utils.pdf import generar_pdf_factura
    
    factura = db.query(models.Factura).join(models.Empresa).filter(
        models.Factura.id == factura_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    pdf_path = generar_pdf_factura(factura)
    
    return {"pdf_url": pdf_path}

@router.post("/{factura_id}/anular")
async def anular_factura(
    factura_id: int,
    motivo: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    factura = db.query(models.Factura).join(models.Empresa).filter(
        models.Factura.id == factura_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if factura.estado not in ["AUTORIZADA", "FIRMADA"]:
        raise HTTPException(status_code=400, detail="Solo se pueden anular facturas autorizadas o firmadas")
    
    # Generar nota de crédito o anulación
    # ... (lógica de anulación SRI)
    
    factura.estado = "ANULADA"
    factura.observaciones += f"\nANULADA: {sanitize_input(motivo)}"
    db.commit()
    
    return {"message": "Factura anulada correctamente"}

def generar_xml_factura(factura: models.Factura) -> str:
    """Genera el XML de la factura según especificaciones del SRI"""
    # Implementación según normativa SRI
    pass
