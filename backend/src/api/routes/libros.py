from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload 
from typing import List, Optional
from decimal import Decimal

from config.database import get_db
from schemas.libros import (
    LibroCreate, 
    LibroResponse, 
    LibroUpdate,
    LibroListResponse,
    LibroConRelacionesResponse,
    LibroSearchFilters,
    EditorialResponse,
    AreaConocimientoResponse,
    EstadoLibroResponse,
    MetodoAdquisicionResponse,  # ← Nuevo import
    LibroCreateConEjemplares
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)
from models import Libro, Editorial, AreaConocimiento, EstadoLibro, Usuario, MetodoAdquisicion  # ← Nuevo import

router = APIRouter(prefix="/api/libros", tags=["libros"])

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def validar_codigo_decimal_en_rango(
    db: AsyncSession, 
    codigo_decimal: str, 
    area_conocimiento_id: int
) -> bool:
    """
    Valida que el código decimal esté dentro del rango del área de conocimiento
    """
    # Obtener el área de conocimiento
    result = await db.execute(
        select(AreaConocimiento).filter(AreaConocimiento.id == area_conocimiento_id)
    )
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Área de conocimiento no encontrada"
        )
    
    # Convertir a números para comparación
    try:
        codigo_num = float(codigo_decimal)
        rango_inicio = float(area.rango_inicio)
        rango_fin = float(area.rango_fin)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código decimal o rangos no son números válidos"
        )
    
    # Validar que esté en el rango
    if not (rango_inicio <= codigo_num <= rango_fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El código decimal {codigo_decimal} no está en el rango del área {area.nombre} ({area.rango_inicio}-{area.rango_fin})"
        )
    
    return True

async def verificar_unicidad_libro(
    db: AsyncSession,
    codigo_decimal: str,
    etiqueta: str, 
    numero_ejemplar: int,
    libro_id: Optional[int] = None  # Para updates, excluir el libro actual
) -> bool:
    """
    Verifica que no exista otro libro con la misma combinación única
    """
    query = select(Libro).filter(
        Libro.codigo_decimal == codigo_decimal,
        Libro.etiqueta == etiqueta,
        Libro.numero_ejemplar == numero_ejemplar
    )
    
    if libro_id:
        query = query.filter(Libro.id != libro_id)
    
    result = await db.execute(query)
    libro_existente = result.scalar_one_or_none()
    
    if libro_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un libro con esa combinación de código decimal, etiqueta y número de ejemplar"
        )
    
    return True

async def verificar_relaciones_libro(db: AsyncSession, libro_data: dict):
    """Verifica que existan las relaciones del libro"""
    relaciones = [
        (libro_data.get('editorial_id'), Editorial, "Editorial"),
        (libro_data.get('area_conocimiento_id'), AreaConocimiento, "Área de conocimiento"),
        (libro_data.get('estado_id'), EstadoLibro, "Estado de libro"),
        (libro_data.get('metodo_adquisicion_id'), MetodoAdquisicion, "Método de adquisición")  # ← Nueva verificación
    ]
    
    for valor, modelo, nombre in relaciones:
        if valor is not None:
            result = await db.execute(select(modelo).filter(modelo.id == valor))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{nombre} no encontrado"
                )

# =============================================
# ENDPOINTS DE CONSULTA (Todos los usuarios autenticados)
# =============================================

@router.get("/", response_model=LibroListResponse)
async def listar_libros(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    titulo: Optional[str] = Query(None, description="Filtrar por título"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    editorial_id: Optional[int] = Query(None, description="Filtrar por editorial"),
    area_conocimiento_id: Optional[int] = Query(None, description="Filtrar por área de conocimiento"),
    metodo_adquisicion_id: Optional[int] = Query(None, description="Filtrar por método de adquisición"),  # ← Nuevo filtro
    estado_id: Optional[int] = Query(None, description="Filtrar por estado"),
    es_prestable: Optional[bool] = Query(None, description="Filtrar por prestable"),
    incluir_retirados: bool = Query(False, description="Incluir libros retirados"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar),

    current_user: Usuario = Depends(obtener_usuario_actual),
):
    """
    Listar libros con filtros (todos los usuarios autenticados)
    """
    # Construir query base con joins para relaciones
    query = select(Libro).options(
        selectinload(Libro.editorial),
        selectinload(Libro.area_conocimiento),
        selectinload(Libro.estado),
        selectinload(Libro.usuario_registro),
        selectinload(Libro.metodo_adquisicion)  # ← Nueva relación
    )
    
    # Aplicar filtros
    if titulo:
        query = query.filter(Libro.titulo.ilike(f"%{titulo}%"))
    if autor:
        query = query.filter(Libro.autor.ilike(f"%{autor}%"))
    if editorial_id:
        query = query.filter(Libro.editorial_id == editorial_id)
    if area_conocimiento_id:
        query = query.filter(Libro.area_conocimiento_id == area_conocimiento_id)
    if metodo_adquisicion_id:  # ← Nuevo filtro
        query = query.filter(Libro.metodo_adquisicion_id == metodo_adquisicion_id)
    if estado_id:
        query = query.filter(Libro.estado_id == estado_id)
    if es_prestable is not None:
        query = query.filter(Libro.es_prestable == es_prestable)

    ##NO PERMITIR QUE USUARIO TIPO 1 PUEDA VER LIBROS RETIRADOS EN LISTADO
    if current_user.tipo_usuario_id == 1:
        query = query.where(Libro.estado_id != 4)
    
    ##EVITAR QUE PUEDA REALIZAR FILTRADO
    if estado_id is not None:
        # Validar que usuario tipo 1 no pueda filtrar por retirados
        if estado_id == 4 and current_user.tipo_usuario_id == 1:
            raise HTTPException(
                status_code=403,
                detail="No tiene permisos para ver libros retirados"
            )
        query = query.where(Libro.estado_id == estado_id)

    # Contar total
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    libros = result.scalars().all()
    
    # Construir respuesta con nombres de relaciones
    libros_con_relaciones = []
    for libro in libros:
        libro_dict = LibroConRelacionesResponse.model_validate(libro)
        libro_dict.editorial_nombre = libro.editorial.nombre
        libro_dict.area_conocimiento_nombre = libro.area_conocimiento.nombre
        libro_dict.estado_nombre = libro.estado.estado
        libro_dict.usuario_registro_nombre = libro.usuario_registro.nombre_completo
        libro_dict.metodo_adquisicion_nombre = libro.metodo_adquisicion.tipo  # ← Nuevo campo
        libros_con_relaciones.append(libro_dict)
    
    return LibroListResponse(
        libros=libros_con_relaciones,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{libro_id}", response_model=LibroConRelacionesResponse)
async def obtener_libro(
    libro_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener información detallada de un libro
    """
    result = await db.execute(
        select(Libro)
        .options(
            selectinload(Libro.editorial),
            selectinload(Libro.area_conocimiento),
            selectinload(Libro.estado),
            selectinload(Libro.usuario_registro),
            selectinload(Libro.metodo_adquisicion)  # ← Nueva relación
        )
        .filter(Libro.id == libro_id)
    )
    libro = result.scalar_one_or_none()
    
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    # Construir respuesta con nombres
    libro_response = LibroConRelacionesResponse.model_validate(libro)
    libro_response.editorial_nombre = libro.editorial.nombre
    libro_response.area_conocimiento_nombre = libro.area_conocimiento.nombre
    libro_response.estado_nombre = libro.estado.estado
    libro_response.usuario_registro_nombre = libro.usuario_registro.nombre_completo
    libro_response.metodo_adquisicion_nombre = libro.metodo_adquisicion.tipo  # ← Nuevo campo
    
    return libro_response

# =============================================
# ENDPOINTS DE GESTIÓN (Solo admin avanzado y super admin)
# =============================================

@router.post("/", response_model=LibroResponse)
async def crear_libro(
    libro_data: LibroCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear un solo ejemplar de libro
    """
    # Validar que el código decimal esté en el rango del área de conocimiento
    await validar_codigo_decimal_en_rango(db, libro_data.codigo_decimal, libro_data.area_conocimiento_id)
    
    # Verificar unicidad
    await verificar_unicidad_libro(db, libro_data.codigo_decimal, libro_data.etiqueta, libro_data.numero_ejemplar)
    
    # Verificar que las relaciones existan
    await verificar_relaciones_libro(db, libro_data.model_dump())
    
    # Crear nuevo libro
    nuevo_libro = Libro(
        **libro_data.model_dump(),
        usuario_registro_id=usuario_actual.id
    )
    
    db.add(nuevo_libro)
    await db.commit()
    await db.refresh(nuevo_libro)
    
    return nuevo_libro

@router.put("/{libro_id}", response_model=LibroResponse)
async def actualizar_libro(
    libro_id: int,
    libro_data: LibroUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar información de libro (solo admin avanzado y super admin)
    """
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro = result.scalar_one_or_none()
    
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    # Validar código decimal si se está actualizando
    update_data = libro_data.model_dump(exclude_unset=True)
    
    if 'codigo_decimal' in update_data or 'area_conocimiento_id' in update_data:
        codigo_decimal = update_data.get('codigo_decimal', libro.codigo_decimal)
        area_conocimiento_id = update_data.get('area_conocimiento_id', libro.area_conocimiento_id)
        await validar_codigo_decimal_en_rango(db, codigo_decimal, area_conocimiento_id)
    
    # Verificar unicidad si se actualizan campos únicos
    if any(field in update_data for field in ['codigo_decimal', 'etiqueta', 'numero_ejemplar']):
        codigo_decimal = update_data.get('codigo_decimal', libro.codigo_decimal)
        etiqueta = update_data.get('etiqueta', libro.etiqueta)
        numero_ejemplar = update_data.get('numero_ejemplar', libro.numero_ejemplar)
        await verificar_unicidad_libro(db, codigo_decimal, etiqueta, numero_ejemplar, libro_id)
    
    # Verificar relaciones si se están actualizando
    await verificar_relaciones_libro(db, update_data)
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(libro, field, value)
    
    await db.commit()
    await db.refresh(libro)
    
    return libro

# =============================================
# ENDPOINTS PARA DATOS AUXILIARES
# =============================================

@router.get("/auxiliares/editoriales", response_model=List[EditorialResponse])
async def listar_editoriales(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todas las editoriales"""
    result = await db.execute(select(Editorial).order_by(Editorial.nombre))
    editoriales = result.scalars().all()
    return editoriales

@router.get("/auxiliares/areas-conocimiento", response_model=List[AreaConocimientoResponse])
async def listar_areas_conocimiento(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todas las áreas de conocimiento"""
    result = await db.execute(select(AreaConocimiento).order_by(AreaConocimiento.nombre))
    areas = result.scalars().all()
    return areas

@router.get("/auxiliares/estados-libro", response_model=List[EstadoLibroResponse])
async def listar_estados_libro(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los estados de libro"""
    result = await db.execute(select(EstadoLibro).order_by(EstadoLibro.estado))
    estados = result.scalars().all()
    return estados

@router.get("/auxiliares/metodos-adquisicion", response_model=List[MetodoAdquisicionResponse])  # ← Nuevo endpoint
async def listar_metodos_adquisicion(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los métodos de adquisición"""
    result = await db.execute(select(MetodoAdquisicion).order_by(MetodoAdquisicion.tipo))
    metodos = result.scalars().all()
    return metodos

@router.post("/multiple", response_model=List[LibroResponse])
async def crear_libros_multiple(
    libro_data: LibroCreateConEjemplares,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear múltiples ejemplares del mismo libro
    """
    # Validar que el código decimal esté en el rango del área de conocimiento
    await validar_codigo_decimal_en_rango(db, libro_data.codigo_decimal, libro_data.area_conocimiento_id)
    
    # Verificar que las relaciones existan
    await verificar_relaciones_libro(db, libro_data.model_dump())
    
    # Preparar datos base (excluyendo campos específicos de múltiples ejemplares)
    datos_base = libro_data.model_dump(exclude={'cantidad_ejemplares', 'numero_ejemplar_inicial'})
    
    libros_creados = []
    ejemplares_con_error = []
    
    # Crear cada ejemplar
    for i in range(libro_data.cantidad_ejemplares):
        numero_ejemplar = libro_data.numero_ejemplar_inicial + i
        
        try:
            # Verificar que no exista ya este ejemplar
            await verificar_unicidad_libro(
                db, 
                libro_data.codigo_decimal, 
                libro_data.etiqueta, 
                numero_ejemplar
            )
            
            # Crear libro
            nuevo_libro = Libro(
                **datos_base,
                numero_ejemplar=numero_ejemplar,
                usuario_registro_id=usuario_actual.id
            )
            
            db.add(nuevo_libro)
            libros_creados.append(nuevo_libro)
            
        except HTTPException as e:
            ejemplares_con_error.append({
                "numero_ejemplar": numero_ejemplar,
                "error": e.detail
            })
    
    # Si hay errores pero también éxitos, commit parcial
    if ejemplares_con_error and libros_creados:
        await db.commit()
        
        # Refresh de los libros creados
        for libro in libros_creados:
            await db.refresh(libro)
        
        # Devolver respuesta con advertencia
        return {
            "libros_creados": libros_creados,
            "advertencia": {
                "message": "Algunos ejemplares no pudieron ser creados",
                "ejemplares_con_error": ejemplares_con_error
            }
        }
    
    # Si todos fallaron
    elif ejemplares_con_error and not libros_creados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ningún ejemplar pudo ser creado. Errores: {ejemplares_con_error}"
        )
    
    # Si todo salió bien
    await db.commit()
    for libro in libros_creados:
        await db.refresh(libro)
    
    return libros_creados

@router.patch("/{libro_id}/retirar", response_model=LibroResponse)
async def retirar_libro(
    libro_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Retirar libro (soft delete) - cambia estado a "Retirado" (4)
    """
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro = result.scalar_one_or_none()
    
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    if libro.estado_id == 4:  # Ya está retirado
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro ya está retirado"
        )
    
    # Cambiar estado a "Retirado" (4)
    libro.estado_id = 4
    libro.fecha_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(libro)
    
    return libro

@router.patch("/{libro_id}/reactivar", response_model=LibroResponse)
async def reactivar_libro(
    libro_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Reactivar libro retirado - cambia estado a "Disponible" (1)
    """
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro = result.scalar_one_or_none()
    
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    if libro.estado_id != 4:  # No está retirado
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro no está retirado"
        )
    
    # Cambiar estado a "Disponible" (1)
    libro.estado_id = 1
    libro.fecha_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(libro)
    
    return libro

@router.delete("/{libro_id}")
async def eliminar_libro(
    libro_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Eliminar libro (soft delete) - cambia estado a "Retirado"
    Este endpoint mantiene compatibilidad con DELETE tradicional
    """
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro = result.scalar_one_or_none()
    
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    if libro.estado_id == 4:  # Ya está retirado
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro ya está retirado"
        )
    
    # Soft delete: cambiar estado a "Retirado" (4)
    libro.estado_id = 4
    libro.fecha_cambio_estado = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Libro retirado exitosamente (soft delete)"}