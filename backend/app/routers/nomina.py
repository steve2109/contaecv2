from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

# Parámetros de nómina Ecuador
SALARIO_BASICO_2024 = Decimal("460.00")
HORAS_MENSUALES = Decimal("240")
DIAS_LABORABLES_MES = Decimal("30")
DIAS_LABORABLES_ANO = Decimal("360")
PORCENTAJE_IESS = Decimal("0.0945")
PORCENTAJE_IESS_PATRONAL = Decimal("0.1115")

def calcular_horas_extras(salario_base: Decimal, horas: Decimal, tipo: str = "100%") -> Decimal:
    """Calcula valor de horas extras"""
    valor_hora = salario_base / HORAS_MENSUALES
    
    if tipo == "100%":
        return (valor_hora * Decimal("2")) * horas
    elif tipo == "50%":
        return (valor_hora * Decimal("1.5")) * horas
    return Decimal("0")

def calcular_décimo_tercero(salario_base: Decimal, dias: Decimal = DIAS_LABORABLES_MES) -> Decimal:
    """Calcula décimo tercero mensualizado"""
    return (salario_base / DIAS_LABORABLES_ANO) * dias

def calcular_décimo_cuarto(salario_base: Decimal, dias: Decimal = DIAS_LABORABLES_MES) -> Decimal:
    """Calcula décimo cuarto mensualizado (sierra/costa)"""
    return (SALARIO_BASICO_2024 / DIAS_LABORABLES_ANO) * dias

def calcular_fondos_reserva(salario_base: Decimal, dias: Decimal = DIAS_LABORABLES_MES) -> Decimal:
    """Calcula fondos de reserva mensualizados"""
    return (salario_base / DIAS_LABORABLES_ANO) * dias

def calcular_aporte_iess(total_ingresos: Decimal) -> Decimal:
    """Calcula aporte al IESS"""
    return total_ingresos * PORCENTAJE_IESS

def calcular_impuesto_renta(proyeccion_anual: Decimal) -> Decimal:
    """Calcula impuesto a la renta según tabla progresiva SRI"""
    # Tabla progresiva 2024
    if proyeccion_anual <= Decimal("11722"):
        return Decimal("0")
    elif proyeccion_anual <= Decimal("14930"):
        excedente = proyeccion_anual - Decimal("11722")
        return (excedente * Decimal("0.05")) / Decimal("12")
    elif proyeccion_anual <= Decimal("19385"):
        excedente = proyeccion_anual - Decimal("14930")
        return (Decimal("160.40") + (excedente * Decimal("0.10"))) / Decimal("12")
    elif proyeccion_anual <= Decimal("25638"):
        excedente = proyeccion_anual - Decimal("19385")
        return (Decimal("605.90") + (excedente * Decimal("0.12"))) / Decimal("12")
    elif proyeccion_anual <= Decimal("33738"):
        excedente = proyeccion_anual - Decimal("25638")
        return (Decimal("1356.00") + (excedente * Decimal("0.15"))) / Decimal("12")
    elif proyeccion_anual <= Decimal("44721"):
        excedente = proyeccion_anual - Decimal("33738")
        return (Decimal("3571.00") + (excedente * Decimal("0.20"))) / Decimal("12")
    elif proyeccion_anual <= Decimal("59537"):
        excedente = proyeccion_anual - Decimal("44721")
        return (Decimal("5775.00") + (excedente * Decimal("0.25"))) / Decimal("12")
    elif proyeccion_anual <= Decimal("79388"):
        excedente = proyeccion_anual - Decimal("59537")
        return (Decimal("9479.00") + (excedente * Decimal("0.30"))) / Decimal("12")
    else:
        excedente = proyeccion_anual - Decimal("79388")
        return (Decimal("14429.00") + (excedente * Decimal("0.35"))) / Decimal("12")

@router.get("/empresa/{empresa_id}/empleados", response_model=List[schemas.EmpleadoResponse])
async def list_empleados(
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
    
    return db.query(models.Empleado).filter(
        models.Empleado.empresa_id == empresa_id
    ).all()

@router.post("/empresa/{empresa_id}/empleados", response_model=schemas.EmpleadoResponse)
async def create_empleado(
    empresa_id: int,
    empleado: schemas.EmpleadoCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    db_empleado = models.Empleado(
        empresa_id=empresa_id,
        nombres=empleado.nombres,
        apellidos=empleado.apellidos,
        cedula=empleado.cedula,
        fecha_nacimiento=empleado.fecha_nacimiento,
        fecha_ingreso=empleado.fecha_ingreso,
        cargo=empleado.cargo,
        departamento=empleado.departamento,
        salario_base=empleado.salario_base,
        tipo_contrato=empleado.tipo_contrato,
        jornada=empleado.jornada,
        afiliado_iess=empleado.afiliado_iess,
        numero_cuenta_bancaria=empleado.numero_cuenta_bancaria,
        banco=empleado.banco
    )
    
    db.add(db_empleado)
    db.commit()
    db.refresh(db_empleado)
    
    return db_empleado

@router.post("/empresa/{empresa_id}/calcular-rol/{empleado_id}")
async def calcular_rol_pago(
    empresa_id: int,
    empleado_id: int,
    periodo: str,  # YYYY-MM
    dias_laborados: int = 30,
    horas_extras: Decimal = Decimal("0"),
    horas_suplementarias: Decimal = Decimal("0"),
    bonificaciones: Decimal = Decimal("0"),
    comisiones: Decimal = Decimal("0"),
    anticipos: Decimal = Decimal("0"),
    prestamos: Decimal = Decimal("0"),
    otros_descuentos: Decimal = Decimal("0"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    empleado = db.query(models.Empleado).filter(
        models.Empleado.id == empleado_id,
        models.Empleado.empresa_id == empresa_id
    ).first()
    
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # Cálculos
    sueldo_base = empleado.salario_base
    
    # Horas extras
    horas_extras_valor = calcular_horas_extras(sueldo_base, horas_extras, "100%")
    horas_suplementarias_valor = calcular_horas_extras(sueldo_base, horas_suplementarias, "50%")
    
    # Beneficios
    decimo_tercero = calcular_décimo_tercero(sueldo_base, Decimal(str(dias_laborados)))
    decimo_cuarto = calcular_décimo_cuarto(sueldo_base, Decimal(str(dias_laborados)))
    fondos_reserva = calcular_fondos_reserva(sueldo_base, Decimal(str(dias_laborados)))
    
    # Total ingresos
    total_ingresos = (
        sueldo_base + 
        horas_extras_valor + 
        horas_suplementarias_valor + 
        bonificaciones + 
        comisiones + 
        decimo_tercero + 
        decimo_cuarto + 
        fondos_reserva
    )
    
    # Descuentos
    aporte_iess = calcular_aporte_iess(total_ingresos) if empleado.afiliado_iess else Decimal("0")
    
    # Proyección anual para impuesto a la renta
    proyeccion_anual = total_ingresos * Decimal("12")
    impuesto_renta = calcular_impuesto_renta(proyeccion_anual)
    
    total_descuentos = aporte_iess + impuesto_renta + prestamos + anticipos + otros_descuentos
    
    # Total neto
    total_neto = total_ingresos - total_descuentos
    
    # Fechas del periodo
    año, mes = map(int, periodo.split("-"))
    fecha_inicio = date(año, mes, 1)
    if mes == 12:
        fecha_fin = date(año + 1, 1, 1)
    else:
        fecha_fin = date(año, mes + 1, 1)
    
    db_rol = models.RolPago(
        empleado_id=empleado_id,
        periodo=periodo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        dias_laborados=dias_laborados,
        horas_extras=horas_extras,
        horas_suplementarias=horas_suplementarias,
        sueldo_base=sueldo_base,
        horas_extras_valor=horas_extras_valor,
        horas_suplementarias_valor=horas_suplementarias_valor,
        bonificaciones=bonificaciones,
        comisiones=comisiones,
        decimo_tercero_mensual=decimo_tercero,
        decimo_cuarto_mensual=decimo_cuarto,
        fondos_reserva_mensual=fondos_reserva,
        total_ingresos=total_ingresos,
        aporte_iess=aporte_iess,
        impuesto_renta=impuesto_renta,
        prestamos=prestamos,
        anticipos=anticipos,
        otros_descuentos=otros_descuentos,
        total_descuentos=total_descuentos,
        total_neto=total_neto,
        estado="calculado"
    )
    
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    
    # Generar asiento contable automático
    # ... (lógica para crear asiento contable de nómina)
    
    return {
        "rol_id": db_rol.id,
        "empleado": f"{empleado.nombres} {empleado.apellidos}",
        "periodo": periodo,
        "sueldo_base": float(sueldo_base),
        "ingresos": {
            "horas_extras": float(horas_extras_valor),
            "horas_suplementarias": float(horas_suplementarias_valor),
            "bonificaciones": float(bonificaciones),
            "comisiones": float(comisiones),
            "decimo_tercero": float(decimo_tercero),
            "decimo_cuarto": float(decimo_cuarto),
            "fondos_reserva": float(fondos_reserva),
            "total_ingresos": float(total_ingresos)
        },
        "descuentos": {
            "aporte_iess": float(aporte_iess),
            "impuesto_renta": float(impuesto_renta),
            "prestamos": float(prestamos),
            "anticipos": float(anticipos),
            "otros": float(otros_descuentos),
            "total_descuentos": float(total_descuentos)
        },
        "total_neto": float(total_neto)
    }

@router.get("/empresa/{empresa_id}/roles/{periodo}")
async def get_roles_periodo(
    empresa_id: int,
    periodo: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    roles = db.query(models.RolPago).join(models.Empleado).filter(
        models.Empleado.empresa_id == empresa_id,
        models.RolPago.periodo == periodo
    ).all()
    
    return roles

@router.post("/empresa/{empresa_id}/exportar-roles/{periodo}")
async def exportar_roles(
    empresa_id: int,
    periodo: str,
    formato: str = "excel",  # excel, csv, pdf
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.utils.export import exportar_roles_pago
    
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    roles = db.query(models.RolPago).join(models.Empleado).filter(
        models.Empleado.empresa_id == empresa_id,
        models.RolPago.periodo == periodo
    ).all()
    
    file_path = exportar_roles_pago(roles, periodo, formato)
    
    return {"file_path": file_path, "formato": formato}

@router.get("/empresa/{empresa_id}/empleado/{empleado_id}/liquidacion")
async def calcular_liquidacion(
    empresa_id: int,
    empleado_id: int,
    fecha_salida: date,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empleado = db.query(models.Empleado).filter(
        models.Empleado.id == empleado_id,
        models.Empleado.empresa_id == empresa_id
    ).first()
    
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # Cálculo de liquidación
    dias_trabajados = (fecha_salida - empleado.fecha_ingreso).days
    años_trabajados = Decimal(str(dias_trabajados)) / Decimal("365")
    
    salario_base = empleado.salario_base
    
    # Desahucio (25% último salario por año)
    desahucio = salario_base * Decimal("0.25") * años_trabajados
    
    # Indemnización si aplica
    indemnizacion = Decimal("0")
    if empleado.tipo_contrato == "indefinido" and años_trabajados >= 3:
        indemnizacion = salario_base * (años_trabajados - Decimal("3"))  # Simplificado
    
    # Vacaciones proporcionales
    dias_vacaciones = Decimal("15") * años_trabajados
    vacaciones = (salario_base / Decimal("30")) * dias_vacaciones
    
    # Décimo tercero proporcional
    dias_año = dias_trabajados % 365
    decimo_tercero = (salario_base / Decimal("360")) * Decimal(str(dias_año))
    
    # Décimo cuarto proporcional
    decimo_cuarto = (SALARIO_BASICO_2024 / Decimal("360")) * Decimal(str(dias_año))
    
    total_liquidacion = desahucio + indemnizacion + vacaciones + decimo_tercero + decimo_cuarto
    
    return {
        "empleado": f"{empleado.nombres} {empleado.apellidos}",
        "fecha_ingreso": empleado.fecha_ingreso,
        "fecha_salida": fecha_salida,
        "dias_trabajados": dias_trabajados,
        "años_trabajados": float(años_trabajados),
        "desahucio": float(desahucio),
        "indemnizacion": float(indemnizacion),
        "vacaciones_proporcionales": float(vacaciones),
        "decimo_tercero": float(decimo_tercero),
        "decimo_cuarto": float(decimo_cuarto),
        "total_liquidacion": float(total_liquidacion)
    }
