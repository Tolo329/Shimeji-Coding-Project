from datetime import datetime


class Actividad:
    def __init__(self, tipo, descripcion="", fecha=None):
        self.tipo = tipo
        self.descripcion = descripcion
        self.fecha = fecha or datetime.now()

    def registrar(self, repositorio, mascota_id):
        return repositorio.registrar_actividad(
            mascota_id=mascota_id,
            tipo_actividad=self.tipo,
            descripcion=self.descripcion
        )

    def __str__(self):
        return f"[{self.fecha.strftime('%H:%M')}] {self.tipo}: {self.descripcion}"
