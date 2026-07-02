from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QTransform, QColor

from gui.gestor_sprites import GestorSprites


class WidgetMascota(QLabel):
    """Widget que muestra el sprite de la mascota con animaciones"""

    SIZE = 120  # Tamaño en pixeles

    def __init__(self, parent=None):
        super().__init__(parent)

        self.sprite_actual = "feliz"
        self.mirando_izquierda = False

        self.tiempo = 0
        self.parpadeando = False
        self.parpadeo_frames = 0
        self.accion_animacion = None
        self.accion_tiempo = 0

        self.setFixedSize(self.SIZE, self.SIZE)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Timer principal de animacion (cada 30ms)
        self.timer_animacion = QTimer(self)
        self.timer_animacion.timeout.connect(self._actualizar)
        self.timer_animacion.start(30)

        # Timer para parpadeo (cada 3.5 segundos)
        self.timer_parpadeo = QTimer(self)
        self.timer_parpadeo.timeout.connect(self._iniciar_parpadeo)
        self.timer_parpadeo.start(3500)

    def cambiar_sprite(self, nombre):
        """Cambia la imagen de la mascota segun el estado"""
        if nombre != self.sprite_actual:
            self.sprite_actual = nombre

    def establecer_mirando(self, izquierda):
        """Cambia la direccion a la que mira la mascota"""
        self.mirando_izquierda = izquierda

    def mostrar_accion(self, accion):
        """Activa la animacion correspondiente a una accion"""
        self.accion_animacion = accion
        self.accion_tiempo = 0

    def _iniciar_parpadeo(self):
        self.parpadeando = True
        self.parpadeo_frames = 0

    def _actualizar(self):
        """Actualiza el estado de las animaciones y redibuja"""
        self.tiempo += 1

        # Control del parpadeo (dura ~5 frames)
        if self.parpadeando:
            self.parpadeo_frames += 1
            if self.parpadeo_frames > 5:
                self.parpadeando = False

        # Control de animacion de accion (dura ~40 frames)
        if self.accion_animacion:
            self.accion_tiempo += 1
            if self.accion_tiempo > 40:
                self.accion_animacion = None

        self.update()

    def _calcular_bob(self):
        """Movimiento suave arriba/abajo (respiración)"""
        return int(self.tiempo % 40 - 20) // 10

    def paintEvent(self, event):
        """Dibuja el sprite con las animaciones aplicadas"""
        pixmap = GestorSprites.obtener(self.sprite_actual)
        if pixmap.isNull():
            return

        # Redimensionar al tamaño del widget
        img = pixmap.scaled(
            self.SIZE, self.SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Animacion de parpadeo (opacidad reducida)
        if self.parpadeando and self.parpadeo_frames < 3:
            img = self._cambiar_opacidad(img, 0.2)

        # Animacion de dormir (opacidad reducida)
        elif self.accion_animacion == "dormir":
            img = self._cambiar_opacidad(img, 0.5)

        # Animacion de comer/jugar (escala que pulsa)
        elif self.accion_animacion in ("comer", "jugar"):
            pulso = self.accion_tiempo % 10
            if pulso < 5:
                escala = 1.0 + 0.08 * pulso
            else:
                escala = 1.0 + 0.08 * (10 - pulso)
            w = int(img.width() * escala)
            h = int(img.height() * escala)
            img = img.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Voltear horizontalmente si mira a la izquierda
        if self.mirando_izquierda:
            img = img.transformed(QTransform().scale(-1, 1))

        offset_y = self._calcular_bob()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        x = (self.width() - img.width()) // 2
        y = (self.height() - img.height()) // 2 + offset_y
        painter.drawPixmap(x, y, img)

        # Mostrar "Z" cuando duerme
        if self.accion_animacion == "dormir":
            painter.setPen(QColor(180, 180, 255))
            fuente = painter.font()
            fuente.setPointSize(14)
            painter.setFont(fuente)
            painter.drawText(self.rect().adjusted(0, -15, 0, 0),
                             Qt.AlignTop | Qt.AlignCenter, "Z Z Z")

        painter.end()

    def _cambiar_opacidad(self, pixmap, opacidad):
        """Crea una copia del pixmap con la opacidad indicada"""
        resultado = QPixmap(pixmap.size())
        resultado.fill(Qt.transparent)
        painter = QPainter(resultado)
        painter.setOpacity(opacidad)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return resultado
