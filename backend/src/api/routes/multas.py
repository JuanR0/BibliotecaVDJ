from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from config.database import get_db
from models.multas import Multa
from models.usuarios import Usuario
from models.base import EstadoMulta, TipoPago, TipoRecursoMulta
from schemas.multas import (
    MultaCreate, 
    MultaResponse,
    MultaConRelaciones,
    MultaUpdate,
    MultaLiquidacion,
    MultaCambioEstado,
    FiltrosMulta,
    ResumenMultas
)
from core.security import (
    obtener_usuario_actual,
    requerir_puede_consultar, 
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/multas", tags=["Multas"])

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_usuario_activo(db: AsyncSession, usuario_id: int) -> Usuario:
    """
    Verificar que el usuario existe y está activo
    """
    result = await db.execute(
        select(Usuario).filter(
            and_(
                Usuario.id == usuario_id,
                Usuario.esta_activo == True
            )
        )
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no válido para multa"
        )
    return usuario

async def obtener_multa_con_relaciones(db: AsyncSession, multa_id: int) -> Multa:
    """
    Obtener una multa con todas sus relaciones cargadas
    """
    result = await db.execute(
        select(Multa)
        .options(
            selectinload(Multa.usuario_multa),
            selectinload(Multa.usuario_multado),
            selectinload(Multa.usuario_ultimo_cambio),
            selectinload(Multa.estado_multa),
            selectinload(Multa.tipo_pago),
            selectinload(Multa.tipo_recurso_multa)
        )
        .filter(Multa.id == multa_id)
    )
    return result.scalar_one_or_none()

def actualizar_campos_auditoria(multa: Multa, usuario_actual: Usuario):
    """
    Actualizar campos de auditoría automáticamente
    """
    multa.usuario_ultimo_cambio_id = usuario_actual.id
    multa.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)

# =============================================
# ENDPOINTS DE CONSULTA (LISTAR)
# =============================================

@router.get("/", response_model=List[MultaConRelaciones])
async def listar_multas(
    skip: int = 0,
    limit: int = 100,
    estado_multa_id: Optional[int] = Query(None, description="Filtrar por estado de multa"),
    usuario_multado_id: Optional[int] = Query(None, description="Filtrar por usuario multado"),
    tipo_pago_id: Optional[int] = Query(None, description="Filtrar por tipo de pago"),
    tipo_recurso_multa_id: Optional[int] = Query(None, description="Filtrar por tipo de recurso"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar todas las multas con filtros opcionales
    """
    try:
        # Construir query base con TODAS las relaciones necesarias
        query = select(Multa).options(
            selectinload(Multa.usuario_multa),
            selectinload(Multa.usuario_multado),
            selectinload(Multa.usuario_ultimo_cambio),
            selectinload(Multa.estado_multa),
            selectinload(Multa.tipo_pago),
            selectinload(Multa.tipo_recurso_multa)
        )
        
        # Aplicar filtros
        if estado_multa_id:
            query = query.where(Multa.estado_multa_id == estado_multa_id)
        if usuario_multado_id:
            query = query.where(Multa.usuario_multado_id == usuario_multado_id)
        if tipo_pago_id:
            query = query.where(Multa.tipo_pago_id == tipo_pago_id)
        if tipo_recurso_multa_id:
            query = query.where(Multa.tipo_recurso_multa_id == tipo_recurso_multa_id)
        
        # Ordenar por fecha más reciente primero
        query = query.order_by(Multa.fecha_multa.desc())
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar query
        result = await db.execute(query)
        multas = result.scalars().all()
        
        # Construir respuesta con datos relacionados
        resultado = []
        for multa in multas:
            resultado.append({
                "id": multa.id,
                "usuario_multa_id": multa.usuario_multa_id,
                "usuario_multado_id": multa.usuario_multado_id,
                "estado_multa_id": multa.estado_multa_id,
                "fecha_multa": multa.fecha_multa,
                "usuario_ultimo_cambio_id": multa.usuario_ultimo_cambio_id,
                "fecha_ultimo_cambio_estado": multa.fecha_ultimo_cambio_estado,
                "tipo_pago_id": multa.tipo_pago_id,
                "tipo_recurso_multa_id": multa.tipo_recurso_multa_id,
                "costo_monetario": multa.costo_monetario,
                "detalles_costo_en_especie": multa.detalles_costo_en_especie,
                "observaciones": multa.observaciones,
                
                # Campos relacionados
                "usuario_multa_nombre": multa.usuario_multa.nombre_completo if multa.usuario_multa else None,
                "usuario_multado_nombre": multa.usuario_multado.nombre_completo if multa.usuario_multado else None,
                "usuario_ultimo_cambio_nombre": multa.usuario_ultimo_cambio.nombre_completo if multa.usuario_ultimo_cambio else None,
                "estado_multa_nombre": multa.estado_multa.estado if multa.estado_multa else None,
                "tipo_pago_nombre": multa.tipo_pago.tipo if multa.tipo_pago else None,
                "tipo_recurso_multa_nombre": multa.tipo_recurso_multa.tipo if multa.tipo_recurso_multa else None,
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar multas: {str(e)}"
        )

@router.get("/pendientes", response_model=List[MultaConRelaciones])
async def listar_multas_pendientes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar solo multas pendientes (estado_multa_id = 1)
    """
    return await listar_multas(
        skip=skip, 
        limit=limit, 
        estado_multa_id=1,  # Pendiente
        usuario_multado_id=None,
        tipo_pago_id=None,
        tipo_recurso_multa_id=None,
        db=db, 
        usuario_actual=usuario_actual
    )

@router.get("/liquidadas", response_model=List[MultaConRelaciones])
async def listar_multas_liquidadas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar solo multas liquidadas (estado_multa_id = 2)
    """
    return await listar_multas(
        skip=skip, 
        limit=limit, 
        estado_multa_id=2,  # Liquidada
        usuario_multado_id=None,
        tipo_pago_id=None,
        tipo_recurso_multa_id=None,
        db=db, 
        usuario_actual=usuario_actual
    )

@router.get("/{multa_id}", response_model=MultaConRelaciones)
async def obtener_multa(
    multa_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener una multa específica por ID
    """
    multa = await obtener_multa_con_relaciones(db, multa_id)
    
    if not multa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Multa no encontrada"
        )
    
    return {
        "id": multa.id,
        "usuario_multa_id": multa.usuario_multa_id,
        "usuario_multado_id": multa.usuario_multado_id,
        "estado_multa_id": multa.estado_multa_id,
        "fecha_multa": multa.fecha_multa,
        "usuario_ultimo_cambio_id": multa.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": multa.fecha_ultimo_cambio_estado,
        "tipo_pago_id": multa.tipo_pago_id,
        "tipo_recurso_multa_id": multa.tipo_recurso_multa_id,
        "costo_monetario": multa.costo_monetario,
        "detalles_costo_en_especie": multa.detalles_costo_en_especie,
        "observaciones": multa.observaciones,
        
        # Campos relacionados
        "usuario_multa_nombre": multa.usuario_multa.nombre_completo if multa.usuario_multa else None,
        "usuario_multado_nombre": multa.usuario_multado.nombre_completo if multa.usuario_multado else None,
        "usuario_ultimo_cambio_nombre": multa.usuario_ultimo_cambio.nombre_completo if multa.usuario_ultimo_cambio else None,
        "estado_multa_nombre": multa.estado_multa.estado if multa.estado_multa else None,
        "tipo_pago_nombre": multa.tipo_pago.tipo if multa.tipo_pago else None,
        "tipo_recurso_multa_nombre": multa.tipo_recurso_multa.tipo if multa.tipo_recurso_multa else None,
    }

# =============================================
# ENDPOINTS DE CREACIÓN (POST)
# =============================================

@router.post("/", response_model=MultaResponse)
async def crear_multa(
    multa_data: MultaCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear una nueva multa
    """
    try:
        # 1. Verificar que el usuario multado existe y está activo
        usuario_multado = await verificar_usuario_activo(db, multa_data.usuario_multado_id)
        
        # 2. Crear la multa
        nueva_multa = Multa(
            usuario_multa_id=usuario_actual.id,
            usuario_multado_id=multa_data.usuario_multado_id,
            estado_multa_id=1,  # "Pendiente" por defecto
            fecha_multa=datetime.utcnow() - timedelta(hours=6),
            usuario_ultimo_cambio_id=usuario_actual.id,
            fecha_ultimo_cambio_estado=datetime.utcnow() - timedelta(hours=6),
            tipo_pago_id=multa_data.tipo_pago_id,
            tipo_recurso_multa_id=multa_data.tipo_recurso_multa_id,
            costo_monetario=multa_data.costo_monetario,
            detalles_costo_en_especie=multa_data.detalles_costo_en_especie,
            observaciones=multa_data.observaciones
        )
        
        db.add(nueva_multa)
        await db.commit()
        await db.refresh(nueva_multa)
        
        return nueva_multa
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear multa: {str(e)}"
        )

# =============================================
# ENDPOINTS DE ACTUALIZACIÓN (PUT/PATCH)
# =============================================

@router.patch("/{multa_id}", response_model=MultaResponse)
async def actualizar_multa(
    multa_id: int,
    multa_update: MultaUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar una multa (campos editables)
    """
    try:
        # 1. Obtener la multa
        result = await db.execute(
            select(Multa).filter(Multa.id == multa_id)
        )
        multa = result.scalar_one_or_none()
        
        if not multa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Multa no encontrada"
            )
        
        # 2. Actualizar campos si están presentes en la solicitud
        update_data = multa_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(multa, field, value)
        
        # 3. Actualizar campos de auditoría automáticamente
        actualizar_campos_auditoria(multa, usuario_actual)
        
        await db.commit()
        await db.refresh(multa)
        
        return multa
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar multa: {str(e)}"
        )

@router.patch("/{multa_id}/liquidar", response_model=MultaResponse)
async def liquidar_multa(
    multa_id: int,
    liquidacion_data: MultaLiquidacion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Liquidar una multa (cambiar estado a Liquidada)
    """
    try:
        # 1. Obtener la multa
        result = await db.execute(
            select(Multa).filter(Multa.id == multa_id)
        )
        multa = result.scalar_one_or_none()
        
        if not multa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Multa no encontrada"
            )
        
        # 2. Verificar que esté pendiente
        if multa.estado_multa_id == 2:  # Ya está liquidada
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La multa ya está liquidada"
            )
        
        # 3. Actualizar campos específicos de liquidación si se proporcionan
        if liquidacion_data.tipo_pago_id is not None:
            multa.tipo_pago_id = liquidacion_data.tipo_pago_id
        
        if liquidacion_data.costo_monetario is not None:
            multa.costo_monetario = liquidacion_data.costo_monetario
        
        if liquidacion_data.detalles_costo_en_especie is not None:
            multa.detalles_costo_en_especie = liquidacion_data.detalles_costo_en_especie
        
        # 4. Cambiar estado a Liquidada
        multa.estado_multa_id = 2  # Liquidada
        
        # 5. Actualizar campos de auditoría y observaciones
        actualizar_campos_auditoria(multa, usuario_actual)
        
        if liquidacion_data.observaciones:
            # Agregar observaciones de liquidación a las existentes
            if multa.observaciones:
                multa.observaciones += f"\n--- LIQUIDACIÓN ---\n{liquidacion_data.observaciones}"
            else:
                multa.observaciones = f"LIQUIDACIÓN: {liquidacion_data.observaciones}"
        
        await db.commit()
        await db.refresh(multa)
        
        return multa
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al liquidar multa: {str(e)}"
        )

@router.patch("/{multa_id}/cambiar-estado", response_model=MultaResponse)
async def cambiar_estado_multa(
    multa_id: int,
    cambio_estado: MultaCambioEstado,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Cambiar el estado de una multa
    """
    try:
        # 1. Obtener la multa
        result = await db.execute(
            select(Multa).filter(Multa.id == multa_id)
        )
        multa = result.scalar_one_or_none()
        
        if not multa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Multa no encontrada"
            )
        
        # 2. Cambiar estado
        multa.estado_multa_id = cambio_estado.estado_multa_id
        
        # 3. Actualizar campos de auditoría
        actualizar_campos_auditoria(multa, usuario_actual)
        
        # 4. Agregar observaciones si se proporcionan
        if cambio_estado.observaciones:
            if multa.observaciones:
                multa.observaciones += f"\n--- CAMBIO ESTADO ---\n{cambio_estado.observaciones}"
            else:
                multa.observaciones = f"CAMBIO ESTADO: {cambio_estado.observaciones}"
        
        await db.commit()
        await db.refresh(multa)
        
        return multa
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado de multa: {str(e)}"
        )

# =============================================
# ENDPOINTS DE CONSULTAS ESPECIALES
# =============================================

@router.get("/usuario/{usuario_id}", response_model=List[MultaConRelaciones])
async def listar_multas_usuario(
    usuario_id: int,
    solo_pendientes: bool = Query(True, description="Mostrar solo multas pendientes"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar multas de un usuario específico
    """
    query = select(Multa).options(
        selectinload(Multa.usuario_multa),
        selectinload(Multa.usuario_multado),
        selectinload(Multa.estado_multa),
        selectinload(Multa.tipo_pago),
        selectinload(Multa.tipo_recurso_multa)
    ).filter(Multa.usuario_multado_id == usuario_id)
    
    if solo_pendientes:
        query = query.where(Multa.estado_multa_id == 1)  # Solo pendientes
    
    # Ordenar por fecha más reciente
    query = query.order_by(Multa.fecha_multa.desc())
    
    result = await db.execute(query)
    multas = result.scalars().all()
    
    # Construir respuesta
    resultado = []
    for multa in multas:
        resultado.append({
            "id": multa.id,
            "usuario_multa_id": multa.usuario_multa_id,
            "usuario_multado_id": multa.usuario_multado_id,
            "estado_multa_id": multa.estado_multa_id,
            "fecha_multa": multa.fecha_multa,
            "usuario_ultimo_cambio_id": multa.usuario_ultimo_cambio_id,
            "fecha_ultimo_cambio_estado": multa.fecha_ultimo_cambio_estado,
            "tipo_pago_id": multa.tipo_pago_id,
            "tipo_recurso_multa_id": multa.tipo_recurso_multa_id,
            "costo_monetario": multa.costo_monetario,
            "detalles_costo_en_especie": multa.detalles_costo_en_especie,
            "observaciones": multa.observaciones,
            
            "usuario_multa_nombre": multa.usuario_multa.nombre_completo if multa.usuario_multa else None,
            "usuario_multado_nombre": multa.usuario_multado.nombre_completo if multa.usuario_multado else None,
            "estado_multa_nombre": multa.estado_multa.estado if multa.estado_multa else None,
            "tipo_pago_nombre": multa.tipo_pago.tipo if multa.tipo_pago else None,
            "tipo_recurso_multa_nombre": multa.tipo_recurso_multa.tipo if multa.tipo_recurso_multa else None,
        })
    
    return resultado

@router.get("/resumen/estadisticas", response_model=ResumenMultas)
async def obtener_resumen_multas(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener resumen estadístico de multas
    """
    try:
        # Total multas
        result_total = await db.execute(select(func.count(Multa.id)))
        total_multas = result_total.scalar() or 0
        
        # Multas pendientes
        result_pendientes = await db.execute(
            select(func.count(Multa.id)).where(Multa.estado_multa_id == 1)
        )
        multas_pendientes = result_pendientes.scalar() or 0
        
        # Multas liquidadas
        result_liquidadas = await db.execute(
            select(func.count(Multa.id)).where(Multa.estado_multa_id == 2)
        )
        multas_liquidadas = result_liquidadas.scalar() or 0
        
        # Total recaudado (solo multas liquidadas)
        result_recaudado = await db.execute(
            select(func.coalesce(func.sum(Multa.costo_monetario), 0))
            .where(Multa.estado_multa_id == 2)
        )
        total_recaudado = result_recaudado.scalar() or Decimal('0.00')
        
        # Por tipo de recurso
        result_tipo_recurso = await db.execute(
            select(
                TipoRecursoMulta.tipo,
                func.count(Multa.id).label('cantidad'),
                func.coalesce(func.sum(Multa.costo_monetario), 0).label('total')
            )
            .join(Multa, Multa.tipo_recurso_multa_id == TipoRecursoMulta.id)
            .group_by(TipoRecursoMulta.id, TipoRecursoMulta.tipo)
        )
        por_tipo_recurso = [
            {"tipo": row.tipo, "cantidad": row.cantidad, "total": row.total}
            for row in result_tipo_recurso.all()
        ]
        
        # Por tipo de pago
        result_tipo_pago = await db.execute(
            select(
                TipoPago.tipo,
                func.count(Multa.id).label('cantidad'),
                func.coalesce(func.sum(Multa.costo_monetario), 0).label('total')
            )
            .join(Multa, Multa.tipo_pago_id == TipoPago.id)
            .group_by(TipoPago.id, TipoPago.tipo)
        )
        por_tipo_pago = [
            {"tipo": row.tipo, "cantidad": row.cantidad, "total": row.total}
            for row in result_tipo_pago.all()
        ]
        
        return {
            "total_multas": total_multas,
            "multas_pendientes": multas_pendientes,
            "multas_liquidadas": multas_liquidadas,
            "total_recaudado": total_recaudado,
            "por_tipo_recurso": por_tipo_recurso,
            "por_tipo_pago": por_tipo_pago
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen: {str(e)}"
        )