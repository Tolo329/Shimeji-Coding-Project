import winsound
import threading


class GestorSonidos:
    """Reproduce sonidos simples usando el altavoz del sistema (Windows)"""

    SONIDOS = {
        "comer": (800, 150),    # frecuencia, duracion ms
        "jugar": (600, 200),
        "dormir": (400, 300),
        "banar": (1000, 100),
        "auto": (500, 100),
    }

    @classmethod
    def reproducir(cls, accion):
        """Reproduce el sonido de la accion indicada en un hilo aparte"""
        if accion not in cls.SONIDOS:
            return
        frecuencia, duracion = cls.SONIDOS[accion]
        hilo = threading.Thread(target=lambda: winsound.Beep(frecuencia, duracion))
        hilo.daemon = True
        hilo.start()
