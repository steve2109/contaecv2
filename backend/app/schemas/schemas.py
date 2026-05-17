from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class AmbienteEnum(str, Enum):
    pruebas = "1"
    produccion = "2"

class TipoLicenciaEnum(str, Enum):
    mensual = "mensual"
    trimestral = "trimestral"
    semestral = "semestral"
    anual = "anual"

class EstadoLicenciaEnum(str, Enum):
    activa = "activa"
    vencida = "vencida"
    suspendida = "suspendida"
    pendiente = "pendiente"

class UserBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ConfiguracionUsuarioBase(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_tls: Optional[bool] = True
    imap_host: Optional[str] = None
    imap_port: Optional[int] = 993
    pop_host: Optional[str] = None
    pop_port: Optional[int] = 995
    idioma: Optional[str] = "es_EC"
    tema: Optional[str] = "claro"

class ConfiguracionUsuarioCreate(ConfiguracionUsuarioBase):
    backup_key: str = Field(..., min_length=8)

class ConfiguracionUsuarioResponse(ConfiguracionUsuarioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmpresaBase(BaseModel):
    ruc: str = Field(..., min_length=13, max_length=13)
    razon_social: str = Field(..., min_length=3, max_length=200)
    nombre_comercial: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    contribuyente_especial: Optional[str] = None
    obligado_contabilidad: Optional[bool] = True
    ambiente: Optional[AmbienteEnum] = AmbienteEnum.pruebas

class EmpresaCreate(EmpresaBase):
    firma_path: Optional[str] = None
    firma_clave: Optional[str] = None

class EmpresaResponse(EmpresaBase):
    id: int
    user_id: int
    logo_path: Optional[str]
    firma_valida_hasta: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClienteBase(BaseModel):
    tipo_identificacion: str = Field(default="05", max_length=2)
    identificacion: str = Field(..., max_length=20)
    razon_social: str = Field(..., min_length=3, max_length=200)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    empresa_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., min_length=2, max_length=200)
    descripcion: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=100)
    precio_compra: Optional[Decimal] = Decimal("0")
    precio_venta: Optional[Decimal] = Decimal("0")
    stock: Optional[Decimal] = Decimal("0")
    stock_minimo: Optional[Decimal] = Decimal("0")
    unidad_medida: Optional[str] = "UNIDAD"
    tiene_iva: Optional[bool] = True
    porcentaje_iva: Optional[Decimal] = Decimal("12")

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int
    empresa_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DetalleFacturaBase(BaseModel):
    producto_id: Optional[int] = None
    codigo_principal: Optional[str] = Field(None, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=200)
    cantidad: Decimal = Decimal("1")
    precio_unitario: Decimal = Decimal("0")
    descuento: Optional[Decimal] = Decimal("0")

class DetalleFacturaCreate(DetalleFacturaBase):
    pass

class DetalleFacturaResponse(DetalleFacturaBase):
    id: int
    factura_id: int
    total_sin_impuestos: Decimal
    iva_valor: Decimal
    
    class Config:
        from_attributes = True

class FacturaBase(BaseModel):
    cliente_id: int
    tipo_comprobante: Optional[str] = "01"
    forma_pago: Optional[str] = "01"
    observaciones: Optional[str] = None

class FacturaCreate(FacturaBase):
    detalles: List[DetalleFacturaCreate]
    ambiente: Optional[AmbienteEnum] = AmbienteEnum.pruebas

class FacturaResponse(BaseModel):
    id: int
    empresa_id: int
    cliente_id: int
    numero_factura: Optional[str]
    serie: Optional[str]
    fecha_emision: datetime
    tipo_comprobante: str
    estado: str
    clave_acceso: Optional[str]
    subtotal_sin_impuestos: Decimal
    total_descuento: Decimal
    total_iva: Decimal
    total: Decimal
    forma_pago: str
    observaciones: Optional[str]
    detalles: List[DetalleFacturaResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AsientoContableBase(BaseModel):
    numero_asiento: str
    fecha: date
    concepto: str
    tipo: Optional[str] = "ingreso"

class MovimientoContableBase(BaseModel):
    cuenta_codigo: str = Field(..., max_length=20)
    cuenta_nombre: str = Field(..., max_length=100)
    debe: Optional[Decimal] = Decimal("0")
    haber: Optional[Decimal] = Decimal("0")

class AsientoContableCreate(AsientoContableBase):
    movimientos: List[MovimientoContableBase]

class AsientoContableResponse(AsientoContableBase):
    id: int
    empresa_id: int
    estado: str
    total_debe: Decimal
    total_haber: Decimal
    created_at: datetime
    movimientos: List[MovimientoContableBase]
    
    class Config:
        from_attributes = True

class EmpleadoBase(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    cedula: str = Field(..., max_length=10)
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: date
    cargo: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    salario_base: Optional[Decimal] = Decimal("0")
    tipo_contrato: Optional[str] = "indefinido"
    jornada: Optional[str] = "completa"
    afiliado_iess: Optional[bool] = True
    numero_cuenta_bancaria: Optional[str] = Field(None, max_length=20)
    banco: Optional[str] = Field(None, max_length=50)

class EmpleadoCreate(EmpleadoBase):
    pass

class EmpleadoResponse(EmpleadoBase):
    id: int
    empresa_id: int
    estado: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RolPagoBase(BaseModel):
    periodo: str = Field(..., max_length=7)
    fecha_inicio: date
    fecha_fin: date

class RolPagoCreate(RolPagoBase):
    dias_laborados: Optional[int] = 30
    horas_extras: Optional[Decimal] = Decimal("0")
    horas_suplementarias: Optional[Decimal] = Decimal("0")
    bonificaciones: Optional[Decimal] = Decimal("0")
    comisiones: Optional[Decimal] = Decimal("0")

class RolPagoResponse(BaseModel):
    id: int
    empleado_id: int
    periodo: str
    sueldo_base: Decimal
    total_ingresos: Decimal
    total_descuentos: Decimal
    total_neto: Decimal
    estado: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LicenciaBase(BaseModel):
    tipo: TipoLicenciaEnum

class LicenciaCreate(LicenciaBase):
    pass

class LicenciaResponse(LicenciaBase):
    id: int
    user_id: int
    estado: EstadoLicenciaEnum
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_empresas: int
    total_clientes: int
    total_productos: int
    total_facturas: int
    total_ventas_mes: Decimal
    total_empleados: int
    licencia_dias_restantes: Optional[int]

class LogActividadBase(BaseModel):
    accion: str
    modulo: str
    descripcion: Optional[str] = None

class LogActividadResponse(LogActividadBase):
    id: int
    user_id: Optional[int]
    empresa_id: Optional[int]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    scan_result: Optional[dict] = None
