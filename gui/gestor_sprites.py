import os
from PySide6.QtGui import QPixmap, QColor


class GestorSprites:
    SPRITES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
    _cache = {}

    SPRITE_MAP = {
        "feliz": "feliz.png",
        "triste": "triste.png",
        "hambriento": "hambriento.png",
        "insatisfecho": "insatisfecho.png",
        "muy_feliz": "muy_feliz.png",
    }

    @classmethod
    def obtener(cls, nombre):
        if nombre in cls._cache:
            return cls._cache[nombre]
        archivo = cls.SPRITE_MAP.get(nombre)
        if not archivo:
            archivo = "feliz.png"
        ruta = os.path.join(cls.SPRITES_DIR, archivo)
        if os.path.exists(ruta):
            pixmap = QPixmap(ruta)
            cls._cache[nombre] = pixmap
            return pixmap
        return cls._crear_fallback()

    @classmethod
    def _crear_fallback(cls, size=120):
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))
        return pixmap

    @classmethod
    def limpiar_cache(cls):
        cls._cache.clear()
