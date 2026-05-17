from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.auth import get_current_user
from app.utils.security import sanitize_input

router = APIRouter()

@router.get("/empresa/{empresa_id}", response_model=List[schemas.ProductoResponse])
async def list_productos(
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
    
    return db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active == True
    ).all()

@router.post("/empresa/{empresa_id}", response_model=schemas.ProductoResponse)
async def create_producto(
    empresa_id: int,
    producto: schemas.ProductoCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    producto.nombre = sanitize_input(producto.nombre)
    producto.descripcion = sanitize_input(producto.descripcion)
    
    db_producto = models.Producto(
        empresa_id=empresa_id,
        codigo=producto.codigo,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        categoria=producto.categoria,
        precio_compra=producto.precio_compra,
        precio_venta=producto.precio_venta,
        stock=producto.stock,
        stock_minimo=producto.stock_minimo,
        unidad_medida=producto.unidad_medida,
        tiene_iva=producto.tiene_iva,
        porcentaje_iva=producto.porcentaje_iva
    )
    
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    return db_producto

@router.put("/{producto_id}", response_model=schemas.ProductoResponse)
async def update_producto(
    producto_id: int,
    producto_data: schemas.ProductoCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    producto = db.query(models.Producto).join(models.Empresa).filter(
        models.Producto.id == producto_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.codigo = producto_data.codigo
    producto.nombre = sanitize_input(producto_data.nombre)
    producto.descripcion = sanitize_input(producto_data.descripcion)
    producto.categoria = producto_data.categoria
    producto.precio_compra = producto_data.precio_compra
    producto.precio_venta = producto_data.precio_venta
    producto.stock = producto_data.stock
    producto.stock_minimo = producto_data.stock_minimo
    producto.unidad_medida = producto_data.unidad_medida
    producto.tiene_iva = producto_data.tiene_iva
    producto.porcentaje_iva = producto_data.porcentaje_iva
    
    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/{producto_id}")
async def delete_producto(
    producto_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    producto = db.query(models.Producto).join(models.Empresa).filter(
        models.Producto.id == producto_id,
        models.Empresa.user_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.is_active = False
    db.commit()
    
    return {"message": "Producto desactivado correctamente"}

@router.get("/empresa/{empresa_id}/bajo-stock")
async def productos_bajo_stock(
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
    
    productos = db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active == True,
        models.Producto.stock <= models.Producto.stock_minimo
    ).all()
    
    return productos
