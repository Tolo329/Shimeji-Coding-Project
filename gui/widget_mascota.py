import math
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QPainter, QTransform, QColor

from gui.gestor_sprites import GestorSprites


class WidgetMascota(QLabel):
    SIZE = 120
    BOB_AMPLITUDE = 4
    BOB_SPEED = 0.003

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sprite_actual = "feliz"
        self._mirando_izquierda = False
        self._tiempo = 0
        self._parpadeando = False
        self._parpadeo_frames = 0
        self._accion_anim = None
        self._accion_tiempo = 0

        self.setFixedSize(self.SIZE, self.SIZE)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self._timer_bob = QTimer(self)
        self._timer_bob.timeout.connect(self._actualizar_animacion)
        self._timer_bob.start(30)

        self._timer_parpadeo = QTimer(self)
        self._timer_parpadeo.timeout.connect(self._iniciar_parpadeo)
        self._timer_parpadeo.start(3500)

    def cambiar_sprite(self, nombre):
        if nombre != self._sprite_actual:
            self._sprite_actual = nombre

    def establecer_mirando(self, izquierda):
        self._mirando_izquierda = izquierda

    def mostrar_accion(self, accion):
        self._accion_anim = accion
        self._accion_tiempo = 0

    def _iniciar_parpadeo(self):
        self._parpadeando = True
        self._parpadeo_frames = 0

    def _actualizar_animacion(self):
        self._tiempo += 1
        if self._parpadeando:
            self._parpadeo_frames += 1
            if self._parpadeo_frames > 4:
                self._parpadeando = False
        if self._accion_anim:
            self._accion_tiempo += 1
            if self._accion_tiempo > 40:
                self._accion_anim = None
        self.update()

    def _obtener_offset_bob(self):
        return int(math.sin(self._tiempo * self.BOB_SPEED) * self.BOB_AMPLITUDE)

    def paintEvent(self, event):
        pixmap = GestorSprites.obtener(self._sprite_actual)
        if pixmap.isNull():
            return

        img = pixmap.scaled(
            self.SIZE, self.SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        if self._parpadeando and self._parpadeo_frames < 3:
            img = self._aplicar_efecto(img, 0.2)
        elif self._accion_anim == "dormir":
            img = self._aplicar_efecto(img, 0.5)
        elif self._accion_anim in ("comer", "jugar"):
            factor = 1.0 + 0.1 * math.sin(self._accion_tiempo * 0.3)
            w, h = int(img.width() * factor), int(img.height() * factor)
            img = img.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        if self._mirando_izquierda:
            img = img.transformed(QTransform().scale(-1, 1))

        offset_y = self._obtener_offset_bob()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        x = (self.width() - img.width()) // 2
        y = (self.height() - img.height()) // 2 + offset_y
        painter.drawPixmap(x, y, img)

        if self._accion_anim == "dormir":
            painter.setPen(QColor(180, 180, 255))
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(0, -20, 0, 0), Qt.AlignTop | Qt.AlignCenter, "💤")

        painter.end()

    def _aplicar_efecto(self, pixmap, opacidad):
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setOpacity(opacidad)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return result
