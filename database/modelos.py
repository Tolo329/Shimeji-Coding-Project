from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.conexion import Base


class MascotaModel(Base):
    __tablename__ = "mascota"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    hambre = Column(Integer, default=50)
    felicidad = Column(Integer, default=50)
    energia = Column(Integer, default=50)
    higiene = Column(Integer, default=50)
    fecha_creacion = Column(DateTime, default=datetime.now)

    actividades = relationship("ActividadModel", back_populates="mascota", cascade="all, delete-orphan")


class ActividadModel(Base):
    __tablename__ = "actividad"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mascota_id = Column(Integer, ForeignKey("mascota.id"), nullable=False)
    tipo_actividad = Column(String(50), nullable=False)
    descripcion = Column(String(200), default="")
    fecha = Column(DateTime, default=datetime.now)

    mascota = relationship("MascotaModel", back_populates="actividades")
