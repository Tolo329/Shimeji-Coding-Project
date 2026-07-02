from dominio.actividad import Actividad


class Mascota:
    """Representa la mascota virtual con sus atributos y acciones"""

    def __init__(self, nombre, hambre=50, felicidad=50, energia=50, higiene=50):
        self.nombre = nombre
        self.hambre = self._limitar(hambre)
        self.felicidad = self._limitar(felicidad)
        self.energia = self._limitar(energia)
        self.higiene = self._limitar(higiene)

    def _limitar(self, valor):
        """Mantiene el valor entre 0 y 100"""
        if valor < 0:
            return 0
        if valor > 100:
            return 100
        return valor

    def comer(self):
        """Aumenta hambre (menos hambre), felicidad y energia"""
        self.hambre = self._limitar(self.hambre + 25)
        self.felicidad = self._limitar(self.felicidad + 5)
        self.energia = self._limitar(self.energia + 5)
        return Actividad("comer", "La mascota ha comido")

    def jugar(self):
        """Aumenta felicidad pero gasta energia y ensucia"""
        if self.energia >= 10:
            self.felicidad = self._limitar(self.felicidad + 20)
            self.energia = self._limitar(self.energia - 15)
            self.hambre = self._limitar(self.hambre + 10)
            self.higiene = self._limitar(self.higiene - 5)
            return Actividad("jugar", "La mascota ha jugado")
        return Actividad("jugar", "La mascota está muy cansada para jugar")

    def dormir(self):
        """Recupera energia pero aumenta un poco el hambre"""
        self.energia = self._limitar(self.energia + 30)
        self.hambre = self._limitar(self.hambre + 5)
        return Actividad("dormir", "La mascota ha descansado")

    def banar(self):
        """Limpia la mascota pero gasta un poco de energia"""
        self.higiene = self._limitar(self.higiene + 30)
        self.felicidad = self._limitar(self.felicidad + 5)
        self.energia = self._limitar(self.energia - 10)
        return Actividad("banar", "La mascota se ha bañado")

    def decrementar_atributos(self):
        """Baja los atributos con el paso del tiempo"""
        self.hambre = self._limitar(self.hambre + 2)
        self.felicidad = self._limitar(self.felicidad - 1)
        self.energia = self._limitar(self.energia - 1)
        self.higiene = self._limitar(self.higiene - 1)

    def obtener_estado_general(self):
        """Devuelve el estado general segun el promedio de atributos"""
        promedio = (self.hambre + self.felicidad + self.energia + self.higiene) / 4
        if promedio >= 80:
            return "muy_feliz"
        if promedio >= 60:
            return "feliz"
        if promedio >= 40:
            return "neutral"
        if promedio >= 20:
            return "triste"
        return "enfermo"

    def obtener_sprite(self):
        """Devuelve el nombre del sprite segun el estado de la mascota"""
        if self.hambre <= 20:
            return "hambriento"
        if self.felicidad <= 20:
            return "triste"
        if self.higiene <= 20:
            return "insatisfecho"
        estado = self.obtener_estado_general()
        if estado == "muy_feliz":
            return "muy_feliz"
        if estado == "feliz":
            return "feliz"
        return "neutral"

    @staticmethod
    def copiar_desde_modelo(modelo):
        """Crea una mascota a partir de un modelo de base de datos"""
        return Mascota(
            nombre=modelo.nombre,
            hambre=modelo.hambre,
            felicidad=modelo.felicidad,
            energia=modelo.energia,
            higiene=modelo.higiene,
        )
