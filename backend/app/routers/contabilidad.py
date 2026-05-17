from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

# Cuentas contables base para Ecuador
CUENTAS_CONTABLES = {
    "1": "ACTIVO",
    "11": "ACTIVO CORRIENTE",
    "111": "CAJA Y BANCOS",
    "1111": "CAJA",
    "1112": "BANCOS",
    "112": "CUENTAS POR COBRAR",
    "1121": "CLIENTES",
    "1122": "CUENTAS POR COBRAR EMPLEADOS",
    "12": "ACTIVO NO CORRIENTE",
    "121": "PROPIEDAD PLANTA Y EQUIPO",
    "2": "PASIVO",
    "21": "PASIVO CORRIENTE",
    "211": "CUENTAS POR PAGAR",
    "212": "OBLIGACIONES LABORALES",
    "22": "PASIVO NO CORRIENTE",
    "3": "PATRIMONIO",
    "31": "CAPITAL",
    "32": "RESERVAS",
    "4": "INGRESOS",
    "41": "INGRESOS ORDINARIOS",
    "411": "VENTAS",
    "42": "INGRESOS EXTRAORDINARIOS",
    "5": "GASTOS",
    "51": "GASTOS ADMINISTRATIVOS",
    "52": "GASTOS DE VENTA",
    "53": "GASTOS FINANCIEROS",
}

@router.get("/empresa/{empresa_id}/cuentas")
async def get_cuentas_contables(
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
    
    return [{"codigo": k, "nombre": v} for k, v in CUENTAS_CONTABLES.items()]

@router.get("/empresa/{empresa_id}/asientos", response_model=List[schemas.AsientoContableResponse])
async def list_asientos(
    empresa_id: int,
    fecha_desde: date = None,
    fecha_hasta: date = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    query = db.query(models.AsientoContable).filter(
        models.AsientoContable.empresa_id == empresa_id
    )
    
    if fecha_desde:
        query = query.filter(models.AsientoContable.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.AsientoContable.fecha <= fecha_hasta)
    
    return query.order_by(models.AsientoContable.fecha.desc()).all()

@router.post("/empresa/{empresa_id}/asientos", response_model=schemas.AsientoContableResponse)
async def create_asiento(
    empresa_id: int,
    asiento: schemas.AsientoContableCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    # Validar partida doble
    total_debe = sum(m.debe or Decimal("0") for m in asiento.movimientos)
    total_haber = sum(m.haber or Decimal("0") for m in asiento.movimientos)
    
    if total_debe != total_haber:
        raise HTTPException(
            status_code=400, 
            detail=f"La partida doble no cuadra: Debe={total_debe}, Haber={total_haber}"
        )
    
    # Generar número de asiento
    ultimo = db.query(models.AsientoContable).filter(
        models.AsientoContable.empresa_id == empresa_id
    ).order_by(models.AsientoContable.id.desc()).first()
    
    num = 1 if not ultimo else int(ultimo.numero_asiento.split("-")[-1]) + 1
    numero_asiento = f"AST-{asiento.fecha.year}-{str(num).zfill(6)}"
    
    db_asiento = models.AsientoContable(
        empresa_id=empresa_id,
        numero_asiento=numero_asiento,
        fecha=asiento.fecha,
        concepto=asiento.concepto,
        tipo=asiento.tipo,
        total_debe=total_debe,
        total_haber=total_haber
    )
    db.add(db_asiento)
    db.commit()
    db.refresh(db_asiento)
    
    for mov in asiento.movimientos:
        db_mov = models.MovimientoContable(
            asiento_id=db_asiento.id,
            cuenta_codigo=mov.cuenta_codigo,
            cuenta_nombre=CUENTAS_CONTABLES.get(mov.cuenta_codigo, mov.cuenta_nombre),
            debe=mov.debe,
            haber=mov.haber
        )
        db.add(db_mov)
    
    db.commit()
    db.refresh(db_asiento)
    
    return db_asiento

@router.get("/empresa/{empresa_id}/balance")
async def get_balance(
    empresa_id: int,
    fecha: date = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    if not fecha:
        fecha = date.today()
    
    # Calcular totales por tipo de cuenta
    movimientos = db.query(
        models.MovimientoContable.cuenta_codigo,
        models.MovimientoContable.cuenta_nombre
    ).join(models.AsientoContable).filter(
        models.AsientoContable.empresa_id == empresa_id,
        models.AsientoContable.fecha <= fecha,
        models.AsientoContable.estado == "VALIDADO"
    ).all()
    
    # ... (lógica de cálculo de balance)
    
    return {
        "fecha": fecha,
        "activo": 0,
        "pasivo": 0,
        "patrimonio": 0,
        "resultado": 0
    }

@router.get("/empresa/{empresa_id}/mayor/{cuenta_codigo}")
async def get_mayor(
    empresa_id: int,
    cuenta_codigo: str,
    fecha_desde: date = None,
    fecha_hasta: date = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    query = db.query(
        models.MovimientoContable,
        models.AsientoContable.fecha,
        models.AsientoContable.numero_asiento,
        models.AsientoContable.concepto
    ).join(models.AsientoContable).filter(
        models.AsientoContable.empresa_id == empresa_id,
        models.MovimientoContable.cuenta_codigo == cuenta_codigo
    )
    
    if fecha_desde:
        query = query.filter(models.AsientoContable.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.AsientoContable.fecha <= fecha_hasta)
    
    resultados = query.order_by(models.AsientoContable.fecha).all()
    
    return [
        {
            "fecha": r.fecha,
            "asiento": r.numero_asiento,
            "concepto": r.concepto,
            "debe": r.debe,
            "haber": r.haber
        }
        for r in resultados
    ]
