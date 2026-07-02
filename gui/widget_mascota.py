from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QTransform, QColor

from gui.gestor_sprites import GestorSprites


class WidgetMascota(QLabel):
    """Widget que muestra el sprite de la mascota con animaciones"""

    SIZE = 120

    def __init__(self, parent=None):
        super().__init__(parent)

        self.sprite_actual = "feliz"
        self.mirando_izquierda = False
        self.caminando = False  # True cuando la mascota se esta moviendo

        self.tiempo = 0
        self.parpadeando = False
        self.parpadeo_frames = 0
        self.accion_animacion = None
        self.accion_tiempo = 0

        self.setFixedSize(self.SIZE, self.SIZE)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer_animacion = QTimer(self)
        self.timer_animacion.timeout.connect(self._actualizar)
        self.timer_animacion.start(30)

        self.timer_parpadeo = QTimer(self)
        self.timer_parpadeo.timeout.connect(self._iniciar_parpadeo)
        self.timer_parpadeo.start(3500)

    def cambiar_sprite(self, nombre):
        if nombre != self.sprite_actual:
            self.sprite_actual = nombre

    def establecer_mirando(self, izquierda):
        self.mirando_izquierda = izquierda

    def establecer_caminando(self, activo):
        self.caminando = activo

    def mostrar_accion(self, accion):
        self.accion_animacion = accion
        self.accion_tiempo = 0

    def _iniciar_parpadeo(self):
        self.parpadeando = True
        self.parpadeo_frames = 0

    def _actualizar(self):
        self.tiempo += 1
        if self.parpadeando:
            self.parpadeo_frames += 1
            if self.parpadeo_frames > 5:
                self.parpadeando = False
        if self.accion_animacion:
            self.accion_tiempo += 1
            if self.accion_tiempo > 40:
                self.accion_animacion = None
        self.update()

    def _calcular_bob(self):
        """Movimiento arriba/abajo"""
        if self.caminando:
            # Bob mas rapido y notorio al caminar (paso)
            paso = self.tiempo % 12
            if paso < 6:
                return -3
            else:
                return 3
        else:
            # Bob suave al estar quieto (respiracion)
            return int(self.tiempo % 40 - 20) // 10

    def _calcular_inclinacion(self):
        """Ligera inclinacion al caminar"""
        if not self.caminando:
            return 0
        paso = self.tiempo % 12
        if paso < 3:
            return 3
        elif paso < 6:
            return -3
        elif paso < 9:
            return -3
        else:
            return 3

    def paintEvent(self, event):
        pixmap = GestorSprites.obtener(self.sprite_actual)
        if pixmap.isNull():
            return

        img = pixmap.scaled(
            self.SIZE, self.SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        if self.parpadeando and self.parpadeo_frames < 3:
            img = self._cambiar_opacidad(img, 0.2)
        elif self.accion_animacion == "dormir":
            img = self._cambiar_opacidad(img, 0.5)
        elif self.accion_animacion in ("comer", "jugar"):
            pulso = self.accion_tiempo % 10
            if pulso < 5:
                escala = 1.0 + 0.08 * pulso
            else:
                escala = 1.0 + 0.08 * (10 - pulso)
            w = int(img.width() * escala)
            h = int(img.height() * escala)
            img = img.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        if self.mirando_izquierda:
            img = img.transformed(QTransform().scale(-1, 1))

        offset_y = self._calcular_bob()
        inclinacion = self._calcular_inclinacion()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        centro_x = self.width() // 2
        centro_y = self.height() // 2 + offset_y
        x = (self.width() - img.width()) // 2
        y = (self.height() - img.height()) // 2

        # Sombra para que destaque sobre cualquier fondo
        sombra = self._cambiar_opacidad(img, 0.15)
        painter.drawPixmap(x + 2, y + offset_y + 2, sombra)

        # Sprite principal con rotacion e inclinacion
        painter.save()
        painter.translate(centro_x, centro_y)
        painter.rotate(inclinacion)
        painter.translate(-centro_x, -centro_y)
        painter.drawPixmap(x, y + offset_y, img)
        painter.restore()

        if self.accion_animacion == "dormir":
            painter.setPen(QColor(180, 180, 255))
            fuente = painter.font()
            fuente.setPointSize(14)
            painter.setFont(fuente)
            painter.drawText(self.rect().adjusted(0, -15, 0, 0),
                             Qt.AlignTop | Qt.AlignCenter, "Z Z Z")

        painter.end()

    def _cambiar_opacidad(self, pixmap, opacidad):
        resultado = QPixmap(pixmap.size())
        resultado.fill(Qt.transparent)
        painter = QPainter(resultado)
        painter.setOpacity(opacidad)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return resultado
