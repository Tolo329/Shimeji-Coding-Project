import os
from PySide6.QtGui import QPixmap, QColor


class GestorSprites:
    """Carga y guarda en memoria los sprites de la mascota"""

    # Carpeta donde estan los archivos PNG
    CARPETA_SPRITES = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets", "sprites"
    )

    cache = {}

    @classmethod
    def obtener(cls, nombre):
        """Devuelve el QPixmap del sprite indicado"""
        if nombre in cls.cache:
            return cls.cache[nombre]

        archivo = f"{nombre}.png"
        ruta = os.path.join(cls.CARPETA_SPRITES, archivo)

        if os.path.exists(ruta):
            pixmap = QPixmap(ruta)
            cls.cache[nombre] = pixmap
            return pixmap

        # Si no existe el archivo, usar feliz como fallback
        ruta_fallback = os.path.join(cls.CARPETA_SPRITES, "feliz.png")
        if os.path.exists(ruta_fallback):
            pixmap = QPixmap(ruta_fallback)
            cls.cache[nombre] = pixmap
            return pixmap

        # Ultimo recurso: imagen vacia
        pixmap = QPixmap(120, 120)
        pixmap.fill(QColor(0, 0, 0, 0))
        return pixmap
