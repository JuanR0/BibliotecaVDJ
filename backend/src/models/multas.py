from config.database import Base
from sqlalchemy import Column, Integer, String, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Multa(Base):
    __tablename__ = "multas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones principales 
    usuario_multa_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_multado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Seguimiento multa
    estado_multa_id = Column(Integer, ForeignKey("estados_multa.id"), nullable=False)
    fecha_multa = Column(TIMESTAMP, nullable=False, server_default=func.now())
    usuario_ultimo_cambio_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())

    # Detalles multa
    tipo_pago_id = Column(Integer, ForeignKey("tipos_pago.id"), nullable=False)
    tipo_recurso_multa_id = Column(Integer, ForeignKey("tipos_recurso_multa.id"), nullable=False)
    
    costo_monetario = Column(Numeric(10, 2), default=0)  # Usé NUMERIC con precisión
    detalles_costo_en_especie = Column(Text)
    observaciones = Column(Text)

    # Relaciones
    usuario_multa = relationship(
        "Usuario", 
        foreign_keys=[usuario_multa_id],
        back_populates="multas_realizadas"
    )
    
    usuario_multado = relationship(
        "Usuario", 
        foreign_keys=[usuario_multado_id],
        back_populates="multas_recibidas"
    )
    
    estado_multa = relationship("EstadoMulta", back_populates="multas")
    
    tipo_pago = relationship("TipoPago", back_populates="multas")
    
    tipo_recurso_multa = relationship("TipoRecursoMulta", back_populates="multas")
    
    usuario_ultimo_cambio = relationship(
        "Usuario", 
        foreign_keys=[usuario_ultimo_cambio_id],
        back_populates="cambios_estado_multas"
    )