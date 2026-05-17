from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Date, DECIMAL, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum

class AmbienteEnum(enum.Enum):
    pruebas = "1"
    produccion = "2"

class TipoLicenciaEnum(enum.Enum):
    mensual = "mensual"
    trimestral = "trimestral"
    semestral = "semestral"
    anual = "anual"

class EstadoLicenciaEnum(enum.Enum):
    activa = "activa"
    vencida = "vencida"
    suspendida = "suspendida"
    pendiente = "pendiente"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telefono = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    empresas = relationship("Empresa", back_populates="owner", cascade="all, delete-orphan")
    licencia = relationship("Licencia", back_populates="user", uselist=False)
    configuracion = relationship("ConfiguracionUsuario", back_populates="user", uselist=False)

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ruc = Column(String(13), nullable=False, index=True)
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(200))
    direccion = Column(Text)
    telefono = Column(String(20))
    email = Column(String(100))
    logo_path = Column(String(500))
    firma_path = Column(String(500))
    firma_clave = Column(Text)  # Encriptado
    firma_valida_hasta = Column(Date)
    ambiente = Column(SQLEnum(AmbienteEnum), default=AmbienteEnum.pruebas)
    contribuyente_especial = Column(String(10))
    obligado_contabilidad = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    owner = relationship("User", back_populates="empresas")
    clientes = relationship("Cliente", back_populates="empresa", cascade="all, delete-orphan")
    productos = relationship("Producto", back_populates="empresa", cascade="all, delete-orphan")
    facturas = relationship("Factura", back_populates="empresa", cascade="all, delete-orphan")
    empleados = relationship("Empleado", back_populates="empresa", cascade="all, delete-orphan")
    asientos = relationship("AsientoContable", back_populates="empresa", cascade="all, delete-orphan")

class ConfiguracionUsuario(Base):
    __tablename__ = "configuracion_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    smtp_host = Column(String(100))
    smtp_port = Column(Integer, default=587)
    smtp_user = Column(String(100))
    smtp_pass = Column(Text)  # Encriptado
    smtp_tls = Column(Boolean, default=True)
    imap_host = Column(String(100))
    imap_port = Column(Integer, default=993)
    pop_host = Column(String(100))
    pop_port = Column(Integer, default=995)
    backup_key = Column(Text)  # Encriptado
    idioma = Column(String(10), default="es_EC")
    tema = Column(String(20), default="claro")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="configuracion")

class Licencia(Base):
    __tablename__ = "licencias"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    tipo = Column(SQLEnum(TipoLicenciaEnum), nullable=False)
    estado = Column(SQLEnum(EstadoLicenciaEnum), default=EstadoLicenciaEnum.pendiente)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime)
    fecha_creacion = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="licencia")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    tipo_identificacion = Column(String(2), default="05")  # 04=RUC, 05=Cédula, 06=Pasaporte, 08=Identificación del exterior
    identificacion = Column(String(20), nullable=False)
    razon_social = Column(String(200), nullable=False)
    direccion = Column(Text)
    telefono = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    empresa = relationship("Empresa", back_populates="clientes")
    facturas = relationship("Factura", back_populates="cliente")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    codigo = Column(String(50), nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    categoria = Column(String(100))
    precio_compra = Column(DECIMAL(12, 2), default=0)
    precio_venta = Column(DECIMAL(12, 2), default=0)
    stock = Column(DECIMAL(12, 2), default=0)
    stock_minimo = Column(DECIMAL(12, 2), default=0)
    unidad_medida = Column(String(20), default="UNIDAD")
    tiene_iva = Column(Boolean, default=True)
    porcentaje_iva = Column(DECIMAL(5, 2), default=12)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    empresa = relationship("Empresa", back_populates="productos")
    detalles_factura = relationship("DetalleFactura", back_populates="producto")

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    numero_factura = Column(String(50), unique=True)
    serie = Column(String(10))
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    tipo_comprobante = Column(String(2), default="01")  # 01=factura, 04=nota de crédito, 05=nota de débito, 06=guía remisión, 07=retención
    estado = Column(String(20), default="PENDIENTE")  # PENDIENTE, FIRMADA, AUTORIZADA, RECHAZADA, ANULADA
    clave_acceso = Column(String(49))
    ambiente = Column(SQLEnum(AmbienteEnum), default=AmbienteEnum.pruebas)
    subtotal_sin_impuestos = Column(DECIMAL(12, 2), default=0)
    total_descuento = Column(DECIMAL(12, 2), default=0)
    total_iva = Column(DECIMAL(12, 2), default=0)
    total_irbp = Column(DECIMAL(12, 2), default=0)
    total_ice = Column(DECIMAL(12, 2), default=0)
    total = Column(DECIMAL(12, 2), default=0)
    forma_pago = Column(String(2), default="01")  # 01=efectivo, 16=tarjeta, 20=transferencia
    observaciones = Column(Text)
    xml_firmado = Column(Text)
    respuesta_sri = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    empresa = relationship("Empresa", back_populates="facturas")
    cliente = relationship("Cliente", back_populates="facturas")
    detalles = relationship("DetalleFactura", back_populates="factura", cascade="all, delete-orphan")

class DetalleFactura(Base):
    __tablename__ = "detalles_factura"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    codigo_principal = Column(String(50))
    descripcion = Column(String(200), nullable=False)
    cantidad = Column(DECIMAL(12, 2), default=1)
    precio_unitario = Column(DECIMAL(12, 4), default=0)
    descuento = Column(DECIMAL(12, 2), default=0)
    total_sin_impuestos = Column(DECIMAL(12, 2), default=0)
    iva_valor = Column(DECIMAL(12, 2), default=0)
    
    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_factura")

class AsientoContable(Base):
    __tablename__ = "asientos_contables"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    numero_asiento = Column(String(20), nullable=False)
    fecha = Column(Date, nullable=False)
    concepto = Column(Text, nullable=False)
    tipo = Column(String(50))  # ingreso, egreso, ajuste, depreciacion, etc.
    estado = Column(String(20), default="BORRADOR")  # BORRADOR, VALIDADO, ANULADO
    total_debe = Column(DECIMAL(12, 2), default=0)
    total_haber = Column(DECIMAL(12, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    empresa = relationship("Empresa", back_populates="asientos")
    movimientos = relationship("MovimientoContable", back_populates="asiento", cascade="all, delete-orphan")

class MovimientoContable(Base):
    __tablename__ = "movimientos_contables"

    id = Column(Integer, primary_key=True, index=True)
    asiento_id = Column(Integer, ForeignKey("asientos_contables.id"), nullable=False)
    cuenta_codigo = Column(String(20), nullable=False)
    cuenta_nombre = Column(String(100), nullable=False)
    debe = Column(DECIMAL(12, 2), default=0)
    haber = Column(DECIMAL(12, 2), default=0)
    
    asiento = relationship("AsientoContable", back_populates="movimientos")

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(10), nullable=False)
    fecha_nacimiento = Column(Date)
    fecha_ingreso = Column(Date, nullable=False)
    fecha_salida = Column(Date)
    cargo = Column(String(100))
    departamento = Column(String(100))
    salario_base = Column(DECIMAL(12, 2), default=0)
    tipo_contrato = Column(String(20), default="indefinido")  # indefinido, fijo, ocasional
    jornada = Column(String(20), default="completa")  # completa, parcial
    afiliado_iess = Column(Boolean, default=True)
    numero_cuenta_bancaria = Column(String(20))
    banco = Column(String(50))
    estado = Column(String(20), default="activo")
    created_at = Column(DateTime, server_default=func.now())
    
    empresa = relationship("Empresa", back_populates="empleados")
    roles_pago = relationship("RolPago", back_populates="empleado", cascade="all, delete-orphan")

class RolPago(Base):
    __tablename__ = "roles_pago"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    periodo = Column(String(7), nullable=False)  # YYYY-MM
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    dias_laborados = Column(Integer, default=30)
    horas_extras = Column(DECIMAL(8, 2), default=0)
    horas_suplementarias = Column(DECIMAL(8, 2), default=0)
    sueldo_base = Column(DECIMAL(12, 2), default=0)
    horas_extras_valor = Column(DECIMAL(12, 2), default=0)
    horas_suplementarias_valor = Column(DECIMAL(12, 2), default=0)
    bonificaciones = Column(DECIMAL(12, 2), default=0)
    comisiones = Column(DECIMAL(12, 2), default=0)
    decimo_tercero_mensual = Column(DECIMAL(12, 2), default=0)
    decimo_cuarto_mensual = Column(DECIMAL(12, 2), default=0)
    fondos_reserva_mensual = Column(DECIMAL(12, 2), default=0)
    total_ingresos = Column(DECIMAL(12, 2), default=0)
    aporte_iess = Column(DECIMAL(12, 2), default=0)
    impuesto_renta = Column(DECIMAL(12, 2), default=0)
    prestamos = Column(DECIMAL(12, 2), default=0)
    anticipos = Column(DECIMAL(12, 2), default=0)
    otros_descuentos = Column(DECIMAL(12, 2), default=0)
    total_descuentos = Column(DECIMAL(12, 2), default=0)
    total_neto = Column(DECIMAL(12, 2), default=0)
    estado = Column(String(20), default="calculado")  # calculado, pagado, anulado
    created_at = Column(DateTime, server_default=func.now())
    
    empleado = relationship("Empleado", back_populates="roles_pago")

class LogActividad(Base):
    __tablename__ = "log_actividades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    accion = Column(String(50), nullable=False)
    modulo = Column(String(50), nullable=False)
    descripcion = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
