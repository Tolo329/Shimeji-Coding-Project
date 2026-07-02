from datetime import datetime
from database.conexion import get_session
from database.modelos import MascotaModel, ActividadModel


class BaseDatos:

    def guardar_mascota(self, nombre):
        session = get_session()
        try:
            mascota = MascotaModel(nombre=nombre)
            session.add(mascota)
            session.commit()
            return mascota.id
        finally:
            session.close()

    def obtener_mascota(self, mascota_id):
        session = get_session()
        try:
            mascota = session.query(MascotaModel).filter_by(id=mascota_id).first()
            return mascota
        finally:
            session.close()

    def obtener_todas_mascotas(self):
        session = get_session()
        try:
            return session.query(MascotaModel).all()
        finally:
            session.close()

    def actualizar_mascota(self, mascota_id, **kwargs):
        session = get_session()
        try:
            session.query(MascotaModel).filter_by(id=mascota_id).update(kwargs)
            session.commit()
        finally:
            session.close()

    def eliminar_mascota(self, mascota_id):
        session = get_session()
        try:
            mascota = session.query(MascotaModel).filter_by(id=mascota_id).first()
            if mascota:
                session.delete(mascota)
                session.commit()
        finally:
            session.close()

    def registrar_actividad(self, mascota_id, tipo_actividad, descripcion=""):
        session = get_session()
        try:
            actividad = ActividadModel(
                mascota_id=mascota_id,
                tipo_actividad=tipo_actividad,
                descripcion=descripcion,
                fecha=datetime.now()
            )
            session.add(actividad)
            session.commit()
            return actividad.id
        finally:
            session.close()

    def obtener_actividades(self, mascota_id, limite=20):
        session = get_session()
        try:
            return (
                session.query(ActividadModel)
                .filter_by(mascota_id=mascota_id)
                .order_by(ActividadModel.fecha.desc())
                .limit(limite)
                .all()
            )
        finally:
            session.close()
