from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from config.database import get_db
from models.prestamos_libro import PrestamoLibro
from models.libros import Libro
from models.usuarios import Usuario
from models.base import EstadoPrestamo
from schemas.prestamos_libro import (
    PrestamoLibroCreate, 
    PrestamoLibroResponse,  # ✅ Cambiado
    PrestamoLibroConRelaciones,
    PrestamoLibroUpdate,
    PrestamoLibroDevolucion
)
from core.security import (
    obtener_usuario_actual,
    requerir_puede_consultar, 
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/prestamos-libros", tags=["Préstamos de Libros"])

# =============================================
# FUNCIONES AUXILIARES
# =============================================

def calcular_dias_excedidos(fecha_esperada: datetime, fecha_real: datetime) -> int:
    """
    Calcula los días excedidos entre fecha esperada y fecha real.
    Solo considera días completos, ignorando horas y minutos.
    Si es negativo (devolución temprana), retorna 0.
    """
    if not fecha_real:
        return 0
    
    # ✅ Convertir a date (ignorar horas y minutos)
    fecha_esperada_date = fecha_esperada.date()
    fecha_real_date = fecha_real.date()
    
    # Calcular diferencia en días
    diferencia = fecha_real_date - fecha_esperada_date
    dias_excedidos = diferencia.days
    
    # Si la devolución fue en la misma fecha o antes, no hay días excedidos
    if dias_excedidos <= 0:
        return 0
    
    return dias_excedidos

async def verificar_libro_disponible(db: AsyncSession, libro_id: int) -> Libro:
    """
    Verificar que el libro existe, está disponible Y es prestable
    """
    result = await db.execute(
        select(Libro).filter(Libro.id == libro_id)
    )
    libro = result.scalar_one_or_none()
    
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    if libro.estado_id != 1:  # No está disponible
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro no está disponible para préstamo (estado no disponible)"
        )
    
    if not libro.es_prestable:  # ✅ NUEVA VALIDACIÓN
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro no es prestable"
        )
    
    return libro

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
            detail="Usuario no válido para préstamo"
        )
    return usuario

# =============================================
# ENDPOINTS DE CONSULTA (LISTAR)
# =============================================

@router.get("/", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos(
    skip: int = 0,
    limit: int = 100,
    estado_prestamo_id: Optional[int] = Query(None, description="Filtrar por estado de préstamo"),
    libro_id: Optional[int] = Query(None, description="Filtrar por libro"),
    usuario_prestado_id: Optional[int] = Query(None, description="Filtrar por usuario prestado"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar todos los préstamos de libros con filtros opcionales
    """
    try:
        # Construir query base con joins
        query = select(PrestamoLibro).options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.usuario_ultimo_cambio)
        )
        
        # Aplicar filtros
        if estado_prestamo_id:
            query = query.where(PrestamoLibro.estado_prestamo_id == estado_prestamo_id)
        if libro_id:
            query = query.where(PrestamoLibro.libro_id == libro_id)
        if usuario_prestado_id:
            query = query.where(PrestamoLibro.usuario_prestado_id == usuario_prestado_id)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar query
        result = await db.execute(query)
        prestamos = result.scalars().all()
        
        # Construir respuesta con datos relacionados
        resultado = []
        for prestamo in prestamos:
            resultado.append({
                "id": prestamo.id,
                "libro_id": prestamo.libro_id,
                "usuario_presta_id": prestamo.usuario_presta_id,
                "usuario_prestado_id": prestamo.usuario_prestado_id,
                "estado_prestamo_id": prestamo.estado_prestamo_id,
                "fecha_prestamo": prestamo.fecha_prestamo,
                "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
                "fecha_devolucion_real": prestamo.fecha_devolucion_real,
                "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
                "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
                "observaciones": prestamo.observaciones,
                "libro_titulo": prestamo.libro.titulo if prestamo.libro else None,
                "libro_autor": prestamo.libro.autor if prestamo.libro else None,
                "libro_codigo_decimal": prestamo.libro.codigo_decimal if prestamo.libro else None,
                "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
                "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
                "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar préstamos: {str(e)}"
        )

@router.get("/vigentes", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos_vigentes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar solo préstamos vigentes (estado_prestamo_id = 1)
    """
    return await listar_prestamos(
        skip=skip, 
        limit=limit, 
        estado_prestamo_id=1,  # Vigente
        libro_id=None,        
        usuario_prestado_id=None,
        db=db, 
        usuario_actual=usuario_actual
    )

@router.get("/{prestamo_id}", response_model=PrestamoLibroConRelaciones)
async def obtener_prestamo(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener un préstamo específico por ID
    """
    result = await db.execute(
        select(PrestamoLibro)
        .options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.usuario_ultimo_cambio)
        )
        .filter(PrestamoLibro.id == prestamo_id)
    )
    prestamo = result.scalar_one_or_none()
    
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    return {
        "id": prestamo.id,
        "libro_id": prestamo.libro_id,
        "usuario_presta_id": prestamo.usuario_presta_id,
        "usuario_prestado_id": prestamo.usuario_prestado_id,
        "estado_prestamo_id": prestamo.estado_prestamo_id,
        "fecha_prestamo": prestamo.fecha_prestamo,
        "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
        "fecha_devolucion_real": prestamo.fecha_devolucion_real,
        "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones": prestamo.observaciones,
        "libro_titulo": prestamo.libro.titulo if prestamo.libro else None,
        "libro_autor": prestamo.libro.autor if prestamo.libro else None,
        "libro_codigo_decimal": prestamo.libro.codigo_decimal if prestamo.libro else None,
        "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
        "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
    }

# =============================================
# ENDPOINTS DE CREACIÓN (POST)
# =============================================

@router.post("/", response_model=PrestamoLibroResponse)  # ✅ Cambiado a PrestamoLibroResponse
async def crear_prestamo(
    prestamo_data: PrestamoLibroCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear un nuevo préstamo de libro
    """
    try:
        # 1. Verificar que el libro existe y está disponible
        libro = await verificar_libro_disponible(db, prestamo_data.libro_id)
        
        # 2. Verificar que el usuario prestado existe y está activo
        usuario_prestado = await verificar_usuario_activo(db, prestamo_data.usuario_prestado_id)
        
        # 3. INICIAR TRANSACCIÓN
        # 3.1 Cambiar estado del libro a "Prestado" (estado_id = 2)
        libro.estado_id = 2  # Prestado
        libro.fecha_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # 3.2 Crear el préstamo
        nuevo_prestamo = PrestamoLibro(
            libro_id=prestamo_data.libro_id,
            usuario_presta_id=usuario_actual.id,
            usuario_prestado_id=prestamo_data.usuario_prestado_id,
            estado_prestamo_id=1,  # "Vigente"
            fecha_prestamo=datetime.utcnow() - timedelta(hours=6),
            fecha_devolucion_esperada=prestamo_data.fecha_devolucion_esperada,
            usuario_ultimo_cambio_id=usuario_actual.id,
            fecha_ultimo_cambio_estado=datetime.utcnow() - timedelta(hours=6),
            observaciones=prestamo_data.observaciones
        )
        
        db.add(nuevo_prestamo)
        await db.commit()
        await db.refresh(nuevo_prestamo)  # ✅ Esto carga el ID generado
        
        return nuevo_prestamo  # ✅ Ahora tiene ID y coincide con PrestamoLibroResponse
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear préstamo: {str(e)}"
        )

# =============================================
# ENDPOINTS DE ACTUALIZACIÓN (PUT/PATCH)
# =============================================

@router.patch("/{prestamo_id}/devolver", response_model=PrestamoLibroResponse)
async def devolver_prestamo(
    prestamo_id: int,
    devolucion_data: PrestamoLibroDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Registrar devolución de un préstamo
    """
    try:
        # 1. Obtener el préstamo
        result = await db.execute(
            select(PrestamoLibro).filter(PrestamoLibro.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()
        
        if not prestamo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Préstamo no encontrado"
            )
        
        if prestamo.estado_prestamo_id != 1:  # Si no está vigente
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden devolver préstamos vigentes"
            )
        
        # 2. INICIAR TRANSACCIÓN
        # 2.1 Cambiar estado del libro a "Disponible"
        result_libro = await db.execute(
            select(Libro).filter(Libro.id == prestamo.libro_id)
        )
        libro = result_libro.scalar_one_or_none()
        
        if libro:
            libro.estado_id = 1  # Disponible
            libro.fecha_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # 2.2 Actualizar préstamo
        prestamo.estado_prestamo_id = 3  # Terminado
        prestamo.fecha_devolucion_real = datetime.utcnow() - timedelta(hours=6)
        prestamo.usuario_ultimo_cambio_id = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # ✅ CALCULAR DÍAS EXCEDIDOS (solo días completos)
        prestamo.dias_excedidos = calcular_dias_excedidos(
            prestamo.fecha_devolucion_esperada,
            datetime.utcnow() - timedelta(hours=6)  # Usamos la misma hora de devolución
        )
        
        if devolucion_data.observaciones:
            prestamo.observaciones = devolucion_data.observaciones
        
        await db.commit()
        await db.refresh(prestamo)
        
        return prestamo
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar devolución: {str(e)}"
        )
    
@router.get("/usuario/{usuario_id}", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos_usuario(
    usuario_id: int,
    solo_vigentes: bool = Query(True, description="Mostrar solo préstamos vigentes"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar préstamos de un usuario específico
    """
    query = select(PrestamoLibro).options(
        selectinload(PrestamoLibro.libro),
        selectinload(PrestamoLibro.usuario_presta),
        selectinload(PrestamoLibro.usuario_prestado),
        selectinload(PrestamoLibro.estado_prestamo)
    ).filter(PrestamoLibro.usuario_prestado_id == usuario_id)
    
    if solo_vigentes:
        query = query.where(PrestamoLibro.estado_prestamo_id == 1)  # Solo vigentes
    
    result = await db.execute(query)
    prestamos = result.scalars().all()
    
    # Construir respuesta con datos relacionados
    resultado = []
    for prestamo in prestamos:
        resultado.append({
            "id": prestamo.id,
            "libro_id": prestamo.libro_id,
            "usuario_presta_id": prestamo.usuario_presta_id,
            "usuario_prestado_id": prestamo.usuario_prestado_id,
            "estado_prestamo_id": prestamo.estado_prestamo_id,
            "fecha_prestamo": prestamo.fecha_prestamo,
            "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
            "fecha_devolucion_real": prestamo.fecha_devolucion_real,
            "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
            "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
            "observaciones": prestamo.observaciones,
            "libro_titulo": prestamo.libro.titulo if prestamo.libro else None,
            "libro_autor": prestamo.libro.autor if prestamo.libro else None,
            "libro_codigo_decimal": prestamo.libro.codigo_decimal if prestamo.libro else None,
            "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
            "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
            "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
        })
    
    return resultado