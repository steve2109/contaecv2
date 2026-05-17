from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user
from app.utils.security import sanitize_input

router = APIRouter()

@router.get("/empresa/{empresa_id}", response_model=List[schemas.ClienteResponse])
async def list_clientes(
    empresa_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que la empresa pertenece al usuario
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa_id
    ).all()

@router.post("/empresa/{empresa_id}", response_model=schemas.ClienteResponse)
async def create_cliente(
    empresa_id: int,
    cliente: schemas.ClienteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    # Sanitizar
    cliente.razon_social = sanitize_input(cliente.razon_social)
    cliente.direccion = sanitize_input(cliente.direccion)
    
    db_cliente = models.Cliente(
        empresa_id=empresa_id,
        tipo_identificacion=cliente.tipo_identificacion,
        identificacion=cliente.identificacion,
        razon_social=cliente.razon_social,
        direccion=cliente.direccion,
        telefono=sanitize_input(cliente.telefono),
        email=cliente.email
    )
    
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    
    return db_cliente

@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
async def update_cliente(
    cliente_id: int,
    cliente_data: schemas.ClienteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cliente = db.query(models.Cliente).join(models.Empresa).filter(
        models.Cliente.id == cliente_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente.razon_social = sanitize_input(cliente_data.razon_social)
    cliente.direccion = sanitize_input(cliente_data.direccion)
    cliente.telefono = sanitize_input(cliente_data.telefono)
    cliente.email = cliente_data.email
    
    db.commit()
    db.refresh(cliente)
    return cliente

@router.delete("/{cliente_id}")
async def delete_cliente(
    cliente_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cliente = db.query(models.Cliente).join(models.Empresa).filter(
        models.Cliente.id == cliente_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente.is_active = False
    db.commit()
    
    return {"message": "Cliente desactivado correctamente"}
