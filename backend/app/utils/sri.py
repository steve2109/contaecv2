from datetime import datetime
from typing import Optional
import hashlib
import xml.etree.ElementTree as ET
from lxml import etree
import httpx

from app.models import models

# URLs del SRI Ecuador
SRI_RECEPCION_PRUEBAS = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
SRI_AUTORIZACION_PRUEBAS = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
SRI_RECEPCION_PRODUCCION = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
SRI_AUTORIZACION_PRODUCCION = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

def generar_clave_acceso(empresa: models.Empresa, cliente: models.Cliente, fecha: datetime) -> str:
    """Genera la clave de acceso para un comprobante electrónico"""
    
    # Fecha en formato DDMMAAAA
    fecha_str = fecha.strftime("%d%m%Y")
    
    # Tipo de comprobante (01 = factura)
    tipo_comprobante = "01"
    
    # RUC de la empresa
    ruc = empresa.ruc
    
    # Ambiente (1 = pruebas, 2 = producción)
    ambiente = empresa.ambiente.value
    
    # Serie (001001)
    serie = "001001"
    
    # Secuencial (9 dígitos)
    # En producción, esto vendría de la base de datos
    secuencial = "000000001"
    
    # Código numérico (8 dígitos aleatorios)
    import random
    codigo_numerico = str(random.randint(10000000, 99999999))
    
    # Tipo de emisión (1 = normal)
    tipo_emision = "1"
    
    # Concatenar todos los campos
    clave_sin_dv = (
        fecha_str +
        tipo_comprobante +
        ruc +
        ambiente +
        serie +
        secuencial +
        codigo_numerico +
        tipo_emision
    )
    
    # Calcular dígito verificador (módulo 11)
    digito_verificador = calcular_digito_verificador_modulo11(clave_sin_dv)
    
    # Clave completa
    clave_acceso = clave_sin_dv + str(digito_verificador)
    
    return clave_acceso

def calcular_digito_verificador_modulo11(cadena: str) -> int:
    """Calcula el dígito verificador usando módulo 11"""
    # Pesos para módulo 11
    pesos = [7, 6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    # Invertir la cadena para procesar de derecha a izquierda
    cadena_reversa = cadena[::-1]
    
    suma = 0
    for i, digito in enumerate(cadena_reversa):
        peso = pesos[i % len(pesos)]
        suma += int(digito) * peso
    
    residuo = suma % 11
    
    if residuo == 0:
        return 0
    else:
        digito = 11 - residuo
        if digito == 11:
            return 0
        elif digito == 10:
            return 1
        return digito

def generar_xml_factura(factura: models.Factura) -> str:
    """Genera el XML de una factura según el esquema del SRI"""
    
    nsmap = {
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    # Crear elemento raíz
    factura_xml = etree.Element("factura", attrib={
        "id": "comprobante",
        "version": "1.1.0"
    }, nsmap=nsmap)
    
    # Info Tributaria
    info_tributaria = etree.SubElement(factura_xml, "infoTributaria")
    etree.SubElement(info_tributaria, "ambiente").text = factura.ambiente.value
    etree.SubElement(info_tributaria, "tipoEmision").text = "1"
    etree.SubElement(info_tributaria, "razonSocial").text = factura.empresa.razon_social
    etree.SubElement(info_tributaria, "nombreComercial").text = factura.empresa.nombre_comercial or ""
    etree.SubElement(info_tributaria, "ruc").text = factura.empresa.ruc
    etree.SubElement(info_tributaria, "claveAcceso").text = factura.clave_acceso
    etree.SubElement(info_tributaria, "codDoc").text = "01"
    etree.SubElement(info_tributaria, "estab").text = "001"
    etree.SubElement(info_tributaria, "ptoEmi").text = "001"
    etree.SubElement(info_tributaria, "secuencial").text = "000000001"
    etree.SubElement(info_tributaria, "dirMatriz").text = factura.empresa.direccion or ""
    
    # Info Factura
    info_factura = etree.SubElement(factura_xml, "infoFactura")
    etree.SubElement(info_factura, "fechaEmision").text = factura.fecha_emision.strftime("%d/%m/%Y")
    etree.SubElement(info_factura, "dirEstablecimiento").text = factura.empresa.direccion or ""
    etree.SubElement(info_factura, "obligadoContabilidad").text = "SI" if factura.empresa.obligado_contabilidad else "NO"
    etree.SubElement(info_factura, "tipoIdentificacionComprador").text = factura.cliente.tipo_identificacion
    etree.SubElement(info_factura, "razonSocialComprador").text = factura.cliente.razon_social
    etree.SubElement(info_factura, "identificacionComprador").text = factura.cliente.identificacion
    etree.SubElement(info_factura, "totalSinImpuestos").text = str(factura.subtotal_sin_impuestos)
    etree.SubElement(info_factura, "totalDescuento").text = str(factura.total_descuento)
    
    # Total con impuestos
    total_con_impuestos = etree.SubElement(info_factura, "totalConImpuestos")
    total_impuesto = etree.SubElement(total_con_impuestos, "totalImpuesto")
    etree.SubElement(total_impuesto, "codigo").text = "2"  # IVA
    etree.SubElement(total_impuesto, "codigoPorcentaje").text = "4"  # 12%
    etree.SubElement(total_impuesto, "baseImponible").text = str(factura.subtotal_sin_impuestos)
    etree.SubElement(total_impuesto, "valor").text = str(factura.total_iva)
    
    etree.SubElement(info_factura, "propina").text = "0.00"
    etree.SubElement(info_factura, "importeTotal").text = str(factura.total)
    etree.SubElement(info_factura, "moneda").text = "DOLAR"
    
    # Detalles
    detalles = etree.SubElement(factura_xml, "detalles")
    for det in factura.detalles:
        detalle = etree.SubElement(detalles, "detalle")
        etree.SubElement(detalle, "codigoPrincipal").text = det.codigo_principal or ""
        etree.SubElement(detalle, "descripcion").text = det.descripcion
        etree.SubElement(detalle, "cantidad").text = str(det.cantidad)
        etree.SubElement(detalle, "precioUnitario").text = str(det.precio_unitario)
        etree.SubElement(detalle, "descuento").text = str(det.descuento)
        etree.SubElement(detalle, "precioTotalSinImpuesto").text = str(det.total_sin_impuestos)
        
        impuestos = etree.SubElement(detalle, "impuestos")
        impuesto = etree.SubElement(impuestos, "impuesto")
        etree.SubElement(impuesto, "codigo").text = "2"
        etree.SubElement(impuesto, "codigoPorcentaje").text = "4"
        etree.SubElement(impuesto, "tarifa").text = "12"
        etree.SubElement(impuesto, "baseImponible").text = str(det.total_sin_impuestos)
        etree.SubElement(impuesto, "valor").text = str(det.iva_valor)
    
    # Info Adicional
    info_adicional = etree.SubElement(factura_xml, "infoAdicional")
    if factura.observaciones:
        campo = etree.SubElement(info_adicional, "campoAdicional", nombre="Observaciones")
        campo.text = factura.observaciones
    
    # Convertir a string
    xml_string = etree.tostring(factura_xml, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    
    return xml_string.decode("utf-8")

def firmar_xml(xml_content: str, firma_path: str, firma_clave: str) -> str:
    """Firma el XML con la firma electrónica"""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    import base64
    
    # En producción, esto usaría la firma electrónica real
    # Simplificado para el ejemplo
    
    # Parsear XML
    root = etree.fromstring(xml_content.encode())
    
    # Crear nodo de firma
    # En implementación real, se usaría xmlsec o similar
    
    return xml_content

def enviar_sri(xml_firmado: str, ambiente: str) -> dict:
    """Envía el comprobante al SRI"""
    
    if ambiente == "1":  # Pruebas
        url_recepcion = SRI_RECEPCION_PRUEBAS
    else:  # Producción
        url_recepcion = SRI_RECEPCION_PRODUCCION
    
    # En producción, se haría una llamada SOAP real
    # Simplificado para el ejemplo
    
    return {
        "estado": "RECIBIDA",
        "mensajes": ["Comprobante recibido correctamente"]
    }

def consultar_autorizacion(clave_acceso: str, ambiente: str) -> dict:
    """Consulta la autorización de un comprobante"""
    
    if ambiente == "1":  # Pruebas
        url_autorizacion = SRI_AUTORIZACION_PRUEBAS
    else:  # Producción
        url_autorizacion = SRI_AUTORIZACION_PRODUCCION
    
    # En producción, se haría una llamada SOAP real
    # Simplificado para el ejemplo
    
    return {
        "estado": "AUTORIZADO",
        "numeroAutorizacion": clave_acceso,
        "fechaAutorizacion": datetime.now().isoformat(),
        "ambiente": "PRUEBAS" if ambiente == "1" else "PRODUCCION"
    }

def consultar_ruc_sri(ruc: str) -> dict:
    """Consulta información de un RUC en el SRI"""
    
    # En producción, se haría una llamada al servicio web del SRI
    # o se usaría web scraping para obtener la información
    
    # URL de consulta del SRI
    url = f"https://srienlinea.sri.gob.ec/sri-catastro-web/rest/ConsulRucWs/consulta/ruc/{ruc}"
    
    try:
        # Simulación - en producción usar httpx para hacer la petición real
        # response = httpx.get(url, timeout=10)
        # data = response.json()
        
        # Datos simulados para desarrollo
        return {
            "ruc": ruc,
            "razonSocial": "EMPRESA DE EJEMPLO S.A.",
            "nombreComercial": "EJEMPLO",
            "estado": "ACTIVO",
            "direccion": "GUAYAQUIL",
            "tipoContribuyente": "PERSONA NATURAL",
            "obligadoContabilidad": True,
            "contribuyenteEspecial": "",
            "actividadEconomica": "ACTIVIDADES DE CONSULTORÍA INFORMÁTICA",
            "found": True
        }
    except Exception as e:
        return {
            "ruc": ruc,
            "found": False,
            "error": str(e)
        }
