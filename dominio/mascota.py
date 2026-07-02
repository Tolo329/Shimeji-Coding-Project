from dominio.actividad import Actividad


class Mascota:
    MIN_ATRIBUTO = 0
    MAX_ATRIBUTO = 100

    def __init__(self, nombre, hambre=50, felicidad=50, energia=50, higiene=50):
        self.nombre = nombre
        self.hambre = self._limitar(hambre)
        self.felicidad = self._limitar(felicidad)
        self.energia = self._limitar(energia)
        self.higiene = self._limitar(higiene)

    @staticmethod
    def _limitar(valor):
        return max(Mascota.MIN_ATRIBUTO, min(Mascota.MAX_ATRIBUTO, valor))

    def comer(self):
        self.hambre = self._limitar(self.hambre + 25)
        self.felicidad = self._limitar(self.felicidad + 5)
        self.energia = self._limitar(self.energia + 5)
        return Actividad("comer", "La mascota ha comido")

    def jugar(self):
        if self.energia >= 10:
            self.felicidad = self._limitar(self.felicidad + 20)
            self.energia = self._limitar(self.energia - 15)
            self.hambre = self._limitar(self.hambre + 10)
            self.higiene = self._limitar(self.higiene - 5)
            return Actividad("jugar", "La mascota ha jugado")
        return Actividad("jugar", "La mascota está muy cansada para jugar")

    def dormir(self):
        self.energia = self._limitar(self.energia + 30)
        self.hambre = self._limitar(self.hambre + 5)
        return Actividad("dormir", "La mascota ha descansado")

    def banar(self):
        self.higiene = self._limitar(self.higiene + 30)
        self.felicidad = self._limitar(self.felicidad + 5)
        self.energia = self._limitar(self.energia - 10)
        return Actividad("banar", "La mascota se ha bañado")

    def decrementar_atributos(self):
        self.hambre = self._limitar(self.hambre + 2)
        self.felicidad = self._limitar(self.felicidad - 1)
        self.energia = self._limitar(self.energia - 1)
        self.higiene = self._limitar(self.higiene - 1)

    @property
    def estado_general(self):
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

    @property
    def sprite_estado(self):
        if self.hambre <= 20:
            return "hambriento"
        if self.felicidad <= 20:
            return "triste"
        if self.higiene <= 20:
            return "insatisfecho"
        if self.estado_general == "muy_feliz":
            return "muy_feliz"
        if self.estado_general == "feliz":
            return "feliz"
        return "neutral"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "hambre": self.hambre,
            "felicidad": self.felicidad,
            "energia": self.energia,
            "higiene": self.higiene,
        }

    @classmethod
    def from_model(cls, modelo):
        return cls(
            nombre=modelo.nombre,
            hambre=modelo.hambre,
            felicidad=modelo.felicidad,
            energia=modelo.energia,
            higiene=modelo.higiene,
        )
