import pandas as pd
import xlsxwriter
from datetime import datetime
import os
import io
import csv

from app.models import models
from app.database import SessionLocal

def importar_excel(file_bytes: bytes, tipo: str, empresa_id: int, db: SessionLocal):
    """Importa datos desde un archivo Excel"""
    df = pd.read_excel(io.BytesIO(file_bytes))
    return _procesar_dataframe(df, tipo, empresa_id, db)

def importar_csv(file_bytes: bytes, tipo: str, empresa_id: int, db: SessionLocal):
    """Importa datos desde un archivo CSV"""
    df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8')
    return _procesar_dataframe(df, tipo, empresa_id, db)

def _procesar_dataframe(df, tipo: str, empresa_id: int, db: SessionLocal):
    """Procesa un DataFrame según el tipo de importación"""
    resultados = {"creados": 0, "errores": []}
    
    if tipo == "inventario":
        for _, row in df.iterrows():
            try:
                producto = models.Producto(
                    codigo=str(row.get('CÓDIGO', row.get('codigo', ''))),
                    nombre=str(row.get('NOMBRE', row.get('nombre', ''))),
                    descripcion=str(row.get('DESCRIPCIÓN', row.get('descripcion', ''))),
                    categoria=str(row.get('CATEGORÍA', row.get('categoria', ''))),
                    precio_compra=float(row.get('PRECIO COMPRA', row.get('precio_compra', 0))),
                    precio_venta=float(row.get('PRECIO VENTA', row.get('precio_venta', 0))),
                    stock=float(row.get('STOCK', row.get('stock', 0))),
                    stock_minimo=float(row.get('STOCK MÍNIMO', row.get('stock_minimo', 0))),
                    unidad_medida=str(row.get('UNIDAD', row.get('unidad_medida', 'UNIDAD'))),
                    tiene_iva=bool(row.get('IVA', row.get('tiene_iva', True))),
                    empresa_id=empresa_id,
                )
                db.add(producto)
                resultados["creados"] += 1
            except Exception as e:
                resultados["errores"].append(str(e))
    
    elif tipo == "clientes":
        for _, row in df.iterrows():
            try:
                cliente = models.Cliente(
                    tipo_identificacion=str(row.get('TIPO ID', row.get('tipo_identificacion', 'RUC'))),
                    identificacion=str(row.get('IDENTIFICACIÓN', row.get('identificacion', ''))),
                    razon_social=str(row.get('RAZÓN SOCIAL', row.get('razon_social', ''))),
                    direccion=str(row.get('DIRECCIÓN', row.get('direccion', ''))),
                    telefono=str(row.get('TELÉFONO', row.get('telefono', ''))),
                    email=str(row.get('EMAIL', row.get('email', ''))),
                    empresa_id=empresa_id,
                )
                db.add(cliente)
                resultados["creados"] += 1
            except Exception as e:
                resultados["errores"].append(str(e))
    
    elif tipo == "empleados":
        for _, row in df.iterrows():
            try:
                empleado = models.Empleado(
                    nombres=str(row.get('NOMBRES', row.get('nombres', ''))),
                    apellidos=str(row.get('APELLIDOS', row.get('apellidos', ''))),
                    cedula=str(row.get('CÉDULA', row.get('cedula', ''))),
                    cargo=str(row.get('CARGO', row.get('cargo', ''))),
                    departamento=str(row.get('DEPARTAMENTO', row.get('departamento', ''))),
                    salario_base=float(row.get('SALARIO BASE', row.get('salario_base', 0))),
                    empresa_id=empresa_id,
                )
                db.add(empleado)
                resultados["creados"] += 1
            except Exception as e:
                resultados["errores"].append(str(e))
    
    db.commit()
    return resultados

def exportar_excel(tipo: str, empresa_id: int, user_id: int, db: SessionLocal) -> str:
    """Exporta datos a Excel"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/export_{tipo}_{timestamp}.xlsx"
    
    if tipo == "inventario":
        productos = db.query(models.Producto).filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active == True
        ).all()
        
        data = {
            'CÓDIGO': [p.codigo for p in productos],
            'NOMBRE': [p.nombre for p in productos],
            'DESCRIPCIÓN': [p.descripcion for p in productos],
            'CATEGORÍA': [p.categoria for p in productos],
            'PRECIO COMPRA': [float(p.precio_compra) for p in productos],
            'PRECIO VENTA': [float(p.precio_venta) for p in productos],
            'STOCK': [float(p.stock) for p in productos],
            'STOCK MÍNIMO': [float(p.stock_minimo) for p in productos],
            'UNIDAD': [p.unidad_medida for p in productos],
            'IVA': ['Sí' if p.tiene_iva else 'No' for p in productos],
        }
    
    elif tipo == "clientes":
        clientes = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa_id
        ).all()
        
        data = {
            'TIPO ID': [c.tipo_identificacion for c in clientes],
            'IDENTIFICACIÓN': [c.identificacion for c in clientes],
            'RAZÓN SOCIAL': [c.razon_social for c in clientes],
            'DIRECCIÓN': [c.direccion for c in clientes],
            'TELÉFONO': [c.telefono for c in clientes],
            'EMAIL': [c.email for c in clientes],
            'ESTADO': ['Activo' if c.is_active else 'Inactivo' for c in clientes],
        }
    
    elif tipo == "empleados":
        empleados = db.query(models.Empleado).filter(
            models.Empleado.empresa_id == empresa_id
        ).all()
        
        data = {
            'NOMBRES': [e.nombres for e in empleados],
            'APELLIDOS': [e.apellidos for e in empleados],
            'CÉDULA': [e.cedula for e in empleados],
            'CARGO': [e.cargo for e in empleados],
            'DEPARTAMENTO': [e.departamento for e in empleados],
            'SALARIO BASE': [float(e.salario_base) for e in empleados],
            'FECHA INGRESO': [e.fecha_ingreso for e in empleados],
            'ESTADO': [e.estado for e in empleados],
        }
    
    elif tipo == "facturas":
        facturas = db.query(models.Factura).filter(
            models.Factura.empresa_id == empresa_id
        ).all()
        
        data = {
            'NÚMERO': [f.numero_factura for f in facturas],
            'CLIENTE': [f.cliente.razon_social for f in facturas],
            'FECHA': [f.fecha_emision for f in facturas],
            'SUBTOTAL': [float(f.subtotal_sin_impuestos) for f in facturas],
            'IVA': [float(f.total_iva) for f in facturas],
            'TOTAL': [float(f.total) for f in facturas],
            'ESTADO': [f.estado for f in facturas],
        }
    
    else:
        data = {}
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, engine='xlsxwriter')
    
    return filename

def exportar_csv(tipo: str, empresa_id: int, user_id: int, db: SessionLocal) -> str:
    """Exporta datos a CSV"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/export_{tipo}_{timestamp}.csv"
    
    # Reutilizar la lógica de Excel pero exportar a CSV
    excel_file = exportar_excel(tipo, empresa_id, user_id, db)
    
    # Convertir Excel a CSV
    df = pd.read_excel(excel_file)
    df.to_csv(filename, index=False, encoding='utf-8')
    
    # Eliminar archivo Excel temporal
    if os.path.exists(excel_file):
        os.remove(excel_file)
    
    return filename

def exportar_pdf(tipo: str, empresa_id: int, user_id: int, db: SessionLocal) -> str:
    """Exporta datos a PDF"""
    
    # Para PDF, generamos un reporte con los datos
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.enums import TA_CENTER
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/export_{tipo}_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()
    
    title = Paragraph(f"REPORTE DE {tipo.upper()}", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Obtener datos
    excel_file = exportar_excel(tipo, empresa_id, user_id, db)
    df = pd.read_excel(excel_file)
    
    # Crear tabla
    data = [df.columns.tolist()] + df.values.tolist()
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d5d8dc')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9f9'), white]),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    # Limpiar archivo temporal
    if os.path.exists(excel_file):
        os.remove(excel_file)
    
    return filename

def exportar_roles_pago(roles, periodo: str, formato: str) -> str:
    """Exporta roles de pago"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    data = {
        'EMPLEADO': [f"{r.empleado.nombres} {r.empleado.apellidos}" for r in roles],
        'CÉDULA': [r.empleado.cedula for r in roles],
        'CARGO': [r.empleado.cargo for r in roles],
        'SALARIO BASE': [float(r.sueldo_base) for r in roles],
        'HORAS EXTRAS': [float(r.horas_extras_valor) for r in roles],
        'BONIFICACIONES': [float(r.bonificaciones) for r in roles],
        'COMISIONES': [float(r.comisiones) for r in roles],
        'TOTAL INGRESOS': [float(r.total_ingresos) for r in roles],
        'IESS': [float(r.aporte_iess) for r in roles],
        'IMPUESTO RENTA': [float(r.impuesto_renta) for r in roles],
        'PRÉSTAMOS': [float(r.prestamos) for r in roles],
        'ANTICIPOS': [float(r.anticipos) for r in roles],
        'TOTAL DESCUENTOS': [float(r.total_descuentos) for r in roles],
        'TOTAL NETO': [float(r.total_neto) for r in roles],
    }
    
    df = pd.DataFrame(data)
    
    if formato == "excel":
        filename = f"/tmp/roles_pago_{periodo}_{timestamp}.xlsx"
        df.to_excel(filename, index=False, engine='xlsxwriter')
    elif formato == "csv":
        filename = f"/tmp/roles_pago_{periodo}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8')
    elif formato == "pdf":
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.colors import HexColor, black, white
        
        filename = f"/tmp/roles_pago_{periodo}_{timestamp}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"ROLES DE PAGO - PERÍODO {periodo}", styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d5d8dc')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9f9'), white]),
        ]))
        
        elements.append(table)
        doc.build(elements)
    
    return filename
