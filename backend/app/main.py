from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import time
import logging
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import auth, users, empresas, clientes, productos, facturas, contabilidad, nomina, admin, backup, file_upload
from app.utils.security import verify_token
from app.utils.backup import schedule_midnight_backup

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/contaec/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("ContaEC iniciando...")
    # Aquí se podría iniciar el scheduler de backups
    yield
    # Shutdown
    logger.info("ContaEC deteniendo...")

app = FastAPI(
    title="ContaEC API",
    description="API para sistema contable y facturación electrónica",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/api/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://conta.tymtechnology.shop", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["conta.tymtechnology.shop", "10.0.1.20", "localhost"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(empresas.router, prefix="/api/empresas", tags=["Empresas"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(productos.router, prefix="/api/productos", tags=["Productos"])
app.include_router(facturas.router, prefix="/api/facturas", tags=["Facturas"])
app.include_router(contabilidad.router, prefix="/api/contabilidad", tags=["Contabilidad"])
app.include_router(nomina.router, prefix="/api/nomina", tags=["Nómina"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administrador"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backups"])
app.include_router(file_upload.router, prefix="/api/upload", tags=["Archivos"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "ContaEC", "version": "1.0.0"}

@app.get("/api")
async def root():
    return {
        "app": "ContaEC",
        "author": "T&M Technology Ec",
        "contact": "0960068866",
        "support": "info@tymtechnology.shop",
        "domain": "conta.tymtechnology.shop"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
