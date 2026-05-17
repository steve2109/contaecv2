# ContaEC - Sistema Contable y Facturación Electrónica

**Desarrollado por:** T&M Technology Ec  
**Contacto:** 0960068866 | info@tymtechnology.shop  
**Dominio:** conta.tymtechnology.shop  
**Servidor:** 10.0.1.20 (Proxmox LXC)

## Descripción

ContaEC es un sistema contable integral diseñado específicamente para Ecuador, con soporte para facturación electrónica SRI, manejo de inventario, contabilidad, nómina/RRHH, gestión multiempresa y administración de licencias.

## Arquitectura

- **Backend:** FastAPI (Python 3.10+)
- **Frontend:** React 18 + Material-UI + Redux
- **Base de datos:** PostgreSQL
- **Servidor web:** Uvicorn + Nginx Proxy Manager

## Estructura del Proyecto

```
contaec/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Aplicación FastAPI principal
│   │   ├── database.py          # Configuración SQLAlchemy
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py        # Modelos de base de datos
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── auth.py          # Autenticación JWT
│   │   │   ├── users.py         # Gestión de usuarios
│   │   │   ├── empresas.py      # CRUD empresas + consulta RUC
│   │   │   ├── clientes.py      # Clientes/proveedores
│   │   │   ├── productos.py     # Inventario
│   │   │   ├── facturas.py      # Facturación electrónica SRI
│   │   │   ├── contabilidad.py  # Cuentas, asientos, balances
│   │   │   ├── nomina.py        # RRHH y nómina
│   │   │   ├── admin.py         # Panel de administración
│   │   │   ├── backup.py        # Backups automáticos
│   │   │   └── file_upload.py   # Importación/Exportación
│   │   └── utils/
│   │       ├── security.py      # JWT, bcrypt, encriptación
│   │       ├── backup.py        # Backups encriptados
│   │       ├── antivirus.py     # ClamAV + VirusTotal
│   │       ├── sri.py           # Integración SRI Ecuador
│   │       ├── pdf.py           # Generación PDFs
│   │       └── export.py        # Excel, CSV, ZIP exports
│   ├── .env.example             # Variables de entorno de ejemplo
│   ├── requirements.txt         # Dependencias Python
│   └── alembic.ini             # Configuración Alembic (migraciones)
│
└── frontend/
    ├── public/
    │   ├── index.html
    │   └── manifest.json
    ├── src/
    │   ├── index.js               # Punto de entrada
    │   ├── App.js                 # Rutas principales
    │   ├── theme.js               # Tema claro/oscuro
    │   ├── i18n.js                # Traducciones i18next
    │   ├── store.js               # Redux store
    │   ├── api/
    │   │   └── axiosConfig.js     # Configuración Axios + interceptores
    │   ├── features/
    │   │   ├── authSlice.js       # Estado de autenticación
    │   │   ├── empresaSlice.js    # Estado de empresas
    │   │   └── uiSlice.js         # Estado UI (tema, sidebar)
    │   └── components/
    │       ├── auth/
    │       │   ├── Login.jsx      # Login + selector idioma/tema
    │       │   └── PrivateRoute.jsx
    │       ├── layout/
    │       │   └── Layout.jsx     # Sidebar + AppBar + navegación
    │       ├── dashboard/
    │       │   └── Dashboard.jsx  # Dashboard con gráficos
    │       ├── empresas/
    │       │   └── Empresas.jsx   # CRUD empresas + firma electrónica
    │       ├── inventario/
    │       │   └── Inventario.jsx # Productos + importación
    │       ├── facturas/
    │       │   └── Facturas.jsx   # Facturación SRI
    │       ├── admin/
    │       │   └── AdminPanel.jsx # Panel admin + licencias
    │       ├── configuracion/
    │       │   └── Configuracion.jsx # Email, backups, tema, idioma
    │       └── common/
    │           └── NotFound.jsx
    └── package.json
```

## Instalación en Servidor (Proxmox LXC - Ubuntu/Debian)

### 1. Preparar el servidor

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar dependencias
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx clamav clamav-daemon

# Instalar Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Iniciar y habilitar servicios
systemctl enable postgresql
systemctl start postgresql
systemctl enable clamav-daemon
systemctl start clamav-daemon
```

### 2. Configurar PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE contaec_db;
CREATE USER contaec_user WITH ENCRYPTED PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE contaec_db TO contaec_user;
\q
```

### 3. Clonar y configurar el proyecto

```bash
# Clonar el proyecto (reemplazar con tu repositorio)
git clone https://github.com/tu-repo/contaec.git /opt/contaec
cd /opt/contaec

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copiar y configurar .env
cp .env.example .env
nano .env  # Editar con tus credenciales

# Crear tablas
alembic upgrade head
# o si no usas alembic:
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Frontend
cd ../frontend
npm install
npm run build
```

### 4. Configurar Gunicorn + Uvicorn (systemd)

Crear `/etc/systemd/system/contaec.service`:

```ini
[Unit]
Description=ContaEC FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/contaec/backend
Environment="PATH=/opt/contaec/backend/venv/bin"
Environment="PYTHONPATH=/opt/contaec/backend"
ExecStart=/opt/contaec/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 3

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable contaec
systemctl start contaec
```

### 5. Configurar Nginx

```bash
# Configurar sitio
nano /etc/nginx/sites-available/contaec
```

```nginx
server {
    listen 80;
    server_name conta.tymtechnology.shop;

    # Frontend (React build)
    location / {
        root /opt/contaec/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Archivos estáticos y uploads
    location /uploads {
        alias /opt/contaec/backend/uploads;
    }

    # Backups (protegido)
    location /backups {
        alias /opt/contaec/backups;
        internal;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/contaec /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Certificado SSL (Let's Encrypt)
certbot --nginx -d conta.tymtechnology.shop
```

### 6. Cron Jobs (Backups automáticos)

```bash
# Backup diario a medianoche
crontab -e
```

Agregar:
```
0 0 * * * cd /opt/contaec/backend && /opt/contaec/backend/venv/bin/python -c "from app.utils.backup import crear_backup_automatico; crear_backup_automatico()"

# Actualizar ClamAV diariamente
0 2 * * * /usr/bin/freshclam
```

## Características Principales

### Seguridad
- ✅ Autenticación JWT con expiración
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Sanitización de entradas con bleach
- ✅ Rate limiting en rutas sensibles
- ✅ Encriptación de datos sensibles (Fernet)
- ✅ Escaneo antivirus con ClamAV
- ✅ Escaneo opcional con VirusTotal API

### Multiempresa
- ✅ Un usuario puede manejar múltiples empresas
- ✅ Aislamiento completo de datos por empresa
- ✅ Configuración por empresa (firma, ambiente, SMTP)
- ✅ Logotipo por empresa

### Facturación Electrónica (SRI Ecuador)
- ✅ Generación XML según normativa SRI
- ✅ Firma electrónica con .p12
- ✅ Envío a webservices SRI
- ✅ Consulta de autorización
- ✅ Visualización y descarga de facturas
- ✅ Ambiente de pruebas y producción

### Contabilidad
- ✅ Plan de cuentas configurable
- ✅ Asientos contables automáticos
- ✅ Libro Diario, Mayor, Balance
- ✅ Estados financieros
- ✅ Cierre de periodos

### Inventario
- ✅ Productos con código, precio, stock
- ✅ Stock mínimo (alertas)
- ✅ Movimientos de entrada/salida
- ✅ Categorías y unidades de medida
- ✅ Importación desde Excel/CSV

### Nómina / RRHH
- ✅ Registro de empleados
- ✅ Cálculo de sueldos, horas extras
- ✅ Décimos, vacaciones, utilidades
- ✅ Rubros personalizables
- ✅ Roles de pago PDF/Excel
- ✅ Exportación para bancos

### Administración
- ✅ Dashboard con estadísticas
- ✅ Gestión de licencias (mensual, trimestral, semestral, anual)
- ✅ Alertas de vencimiento de licencias
- ✅ WhatsApp para renovaciones
- ✅ Panel de salud del sistema
- ✅ Logs de seguridad

### Configuración
- ✅ Modo claro/oscuro
- ✅ Idioma español (Ecuador) + inglés
- ✅ Email SMTP configurable por empresa
- ✅ Backups encriptados automáticos
- ✅ Restauración de backups

## Licenciamiento

El sistema incluye un sistema de licenciamiento con las siguientes modalidades:
- Mensual
- Trimestral
- Semestral
- Anual

Solo el administrador (`steve.mejia@tymtechnology.shop`) puede gestionar licencias.

## Desarrollo Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend
npm install
npm start  # Puerto 3000
```

## API Documentation

Una vez desplegado, la documentación automática está disponible en:
- Swagger UI: `http://10.0.1.20/api/docs`
- ReDoc: `http://10.0.1.20/api/redoc`

## Variables de Entorno Importantes

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://user:pass@localhost/db` |
| `SECRET_KEY` | Clave JWT | Generar con `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | Clave Fernet | Generar con `Fernet.generate_key()` |
| `ADMIN_USER` | Email admin | `steve.mejia@tymtechnology.shop` |
| `ADMIN_PASS` | Password admin (cambiar en producción) | Encriptar con bcrypt |
| `CLAMAV_ENABLED` | Activar escaneo ClamAV | `true` |
| `VIRUSTOTAL_API_KEY` | API key VT (opcional) | `abc123...` |

## Soporte

- **Teléfono:** 0960068866
- **Email:** info@tymtechnology.shop
- **WhatsApp:** Click en "Renovar Licencia" dentro del sistema

## Notas de Seguridad

1. **Cambiar las credenciales por defecto** inmediatamente después del primer despliegue
2. **No exponer el archivo `.env`** - debe estar fuera del alcance público
3. **Generar nuevas claves secretas** para producción
4. **Configurar firewall** para permitir solo puertos necesarios (80, 443, 22)
5. **Habilitar fail2ban** para protección contra ataques de fuerza bruta
6. **Actualizar ClamAV** regularmente con `freshclam`

---

Este repositorio contiene el código fuente de ContaEC, propiedad de T&M TECHNOLOGY EC.
El software está sujeto a licenciamiento comercial y no puede ser utilizado sin una licencia válida.
Para licencias comerciales, contacte a T&M TECHNOLOGY EC.

---

© 2024 T&M Technology Ec - Todos los derechos reservados
