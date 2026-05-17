from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

from app.models import models

def generar_pdf_factura(factura: models.Factura) -> str:
    """Genera un PDF de la factura"""
    
    filename = f"/tmp/factura_{factura.clave_acceso}.pdf"
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1a5276'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#5d6d7e'),
        alignment=TA_LEFT
    )
    
    # Logo de la empresa (si existe)
    if factura.empresa.logo_path and os.path.exists(factura.empresa.logo_path):
        logo = Image(factura.empresa.logo_path, width=3*cm, height=3*cm)
        elements.append(logo)
    
    # Título
    elements.append(Paragraph("FACTURA ELECTRÓNICA", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Info de la empresa
    empresa_info = f"""
    <b>{factura.empresa.razon_social}</b><br/>
    RUC: {factura.empresa.ruc}<br/>
    {factura.empresa.direccion or ''}<br/>
    Tel: {factura.empresa.telefono or 'N/A'}
    """
    elements.append(Paragraph(empresa_info, header_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Info de la factura
    factura_info = [
        ["Clave de Acceso:", factura.clave_acceso],
        ["Número:", f"{factura.serie}-{factura.numero_factura}"],
        ["Fecha Emisión:", factura.fecha_emision.strftime("%d/%m/%Y")],
        ["Ambiente:", "PRUEBAS" if factura.ambiente.value == "1" else "PRODUCCIÓN"],
    ]
    
    factura_table = Table(factura_info, colWidths=[4*cm, 10*cm])
    factura_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d5d8dc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(factura_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Info del cliente
    cliente_info = f"""
    <b>CLIENTE:</b> {factura.cliente.razon_social}<br/>
    <b>Identificación:</b> {factura.cliente.identificacion}<br/>
    <b>Dirección:</b> {factura.cliente.direccion or 'N/A'}<br/>
    <b>Teléfono:</b> {factura.cliente.telefono or 'N/A'}
    """
    elements.append(Paragraph(cliente_info, header_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabla de detalles
    detalle_data = [['CÓDIGO', 'DESCRIPCIÓN', 'CANT.', 'P. UNIT.', 'DESC.', 'TOTAL']]
    for det in factura.detalles:
        detalle_data.append([
            det.codigo_principal or '',
            det.descripcion,
            str(det.cantidad),
            f"${det.precio_unitario:.2f}",
            f"${det.descuento:.2f}",
            f"${det.total_sin_impuestos:.2f}"
        ])
    
    detalle_table = Table(detalle_data, colWidths=[2.5*cm, 6*cm, 1.5*cm, 2*cm, 1.5*cm, 2*cm])
    detalle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('TEXTCOLOR', (0, 1), (-1, -1), black),
        ('ALIGN', (2, 1), (5, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d5d8dc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9f9'), white]),
    ]))
    elements.append(detalle_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Totales
    totales_data = [
        ['SUBTOTAL:', f"${factura.subtotal_sin_impuestos:.2f}"],
        ['DESCUENTO:', f"${factura.total_descuento:.2f}"],
        ['IVA 12%:', f"${factura.total_iva:.2f}"],
        ['TOTAL:', f"${factura.total:.2f}"],
    ]
    
    totales_table = Table(totales_data, colWidths=[12*cm, 4*cm])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, -1), (-1, -1), HexColor('#1a5276')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totales_table)
    
    # Pie de página
    elements.append(Spacer(1, 1*cm))
    footer = f"""
    <para alignment="center" fontSize="8" textColor="grey">
    Este documento es una representación impresa de una factura electrónica<br/>
    Generado por ContaEC - T&M Technology Ec<br/>
    {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    </para>
    """
    elements.append(Paragraph(footer, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    
    return filename

def generar_pdf_rol_pago(rol) -> str:
    """Genera un PDF del rol de pago"""
    
    filename = f"/tmp/rol_pago_{rol.empleado_id}_{rol.periodo}.pdf"
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1a5276'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("ROL DE PAGOS", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Info del empleado
    empleado = rol.empleado
    empleado_info = f"""
    <b>EMPLEADO:</b> {empleado.nombres} {empleado.apellidos}<br/>
    <b>CARGO:</b> {empleado.cargo or 'N/A'}<br/>
    <b>DEPARTAMENTO:</b> {empleado.departamento or 'N/A'}<br/>
    <b>CÉDULA:</b> {empleado.cedula}<br/>
    <b>PERIODO:</b> {rol.periodo}
    """
    elements.append(Paragraph(empleado_info, styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabla de ingresos
    ingresos_data = [['INGRESOS', 'VALOR']]
    ingresos_data.append(['Sueldo Base', f"${rol.sueldo_base:.2f}"])
    if rol.horas_extras_valor > 0:
        ingresos_data.append(['Horas Extras', f"${rol.horas_extras_valor:.2f}"])
    if rol.horas_suplementarias_valor > 0:
        ingresos_data.append(['Horas Suplementarias', f"${rol.horas_suplementarias_valor:.2f}"])
    if rol.bonificaciones > 0:
        ingresos_data.append(['Bonificaciones', f"${rol.bonificaciones:.2f}"])
    if rol.comisiones > 0:
        ingresos_data.append(['Comisiones', f"${rol.comisiones:.2f}"])
    if rol.decimo_tercero_mensual > 0:
        ingresos_data.append(['Décimo Tercero (Mensual)', f"${rol.decimo_tercero_mensual:.2f}"])
    if rol.decimo_cuarto_mensual > 0:
        ingresos_data.append(['Décimo Cuarto (Mensual)', f"${rol.decimo_cuarto_mensual:.2f}"])
    if rol.fondos_reserva_mensual > 0:
        ingresos_data.append(['Fondos de Reserva', f"${rol.fondos_reserva_mensual:.2f}"])
    ingresos_data.append(['TOTAL INGRESOS', f"${rol.total_ingresos:.2f}"])
    
    ingresos_table = Table(ingresos_data, colWidths=[10*cm, 6*cm])
    ingresos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f8f9f9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d5d8dc')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(ingresos_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # Tabla de descuentos
    descuentos_data = [['DESCUENTOS', 'VALOR']]
    if rol.aporte_iess > 0:
        descuentos_data.append(['Aporte IESS (9.45%)', f"${rol.aporte_iess:.2f}"])
    if rol.impuesto_renta > 0:
        descuentos_data.append(['Impuesto a la Renta', f"${rol.impuesto_renta:.2f}"])
    if rol.prestamos > 0:
        descuentos_data.append(['Préstamos', f"${rol.prestamos:.2f}"])
    if rol.anticipos > 0:
        descuentos_data.append(['Anticipos', f"${rol.anticipos:.2f}"])
    if rol.otros_descuentos > 0:
        descuentos_data.append(['Otros Descuentos', f"${rol.otros_descuentos:.2f}"])
    descuentos_data.append(['TOTAL DESCUENTOS', f"${rol.total_descuentos:.2f}"])
    
    descuentos_table = Table(descuentos_data, colWidths=[10*cm, 6*cm])
    descuentos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#922b21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f8f9f9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d5d8dc')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(descuentos_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # Total neto
    neto_data = [['TOTAL NETO A RECIBIR:', f"${rol.total_neto:.2f}"]]
    neto_table = Table(neto_data, colWidths=[10*cm, 6*cm])
    neto_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, -1), white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(neto_table)
    
    # Pie de página
    elements.append(Spacer(1, 1*cm))
    footer = f"""
    <para alignment="center" fontSize="8" textColor="grey">
    Generado por ContaEC - T&M Technology Ec<br/>
    {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    </para>
    """
    elements.append(Paragraph(footer, styles['Normal']))
    
    doc.build(elements)
    
    return filename
