import random
import math
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent

from dominio.mascota import Mascota
from database.repositorio import BaseDatos
from gui.widget_mascota import WidgetMascota
from gui.panel_control import PanelControl


class VentanaPrincipal(QWidget):
    MASCOTA_SIZE = 120
    DECAY_INTERVAL = 4000
    MOVE_INTERVAL = 30
    FOLLOW_RADIUS = 200
    WALK_SPEED = 1.5
    FOLLOW_SPEED = 3.0

    def __init__(self, mascota, repositorio, mascota_id):
        super().__init__()
        self.mascota = mascota
        self.repo = repositorio
        self.mascota_id = mascota_id
        self._arrastrando = False
        self._offset_arrastre = QPoint(0, 0)
        self._menu_actual = None
        self._movimiento_x = 0
        self._modo = "idle"
        self._direccion = 1
        self._pausa_restante = 0

        self._setup_ventana()
        self._setup_widgets()
        self._setup_timers()

    def _setup_ventana(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setFixedSize(self.MASCOTA_SIZE, self.MASCOTA_SIZE)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            random.randint(100, screen.width() - self.MASCOTA_SIZE - 100),
            screen.height() - self.MASCOTA_SIZE - 80
        )

    def _setup_widgets(self):
        self.mascota_widget = WidgetMascota(self)
        self.mascota_widget.move(0, 0)
        self.panel_control = PanelControl()

    def _setup_timers(self):
        self.timer_decaimiento = QTimer(self)
        self.timer_decaimiento.timeout.connect(self._decaer)
        self.timer_decaimiento.start(self.DECAY_INTERVAL)

        self.timer_movimiento = QTimer(self)
        self.timer_movimiento.timeout.connect(self._actualizar_movimiento)
        self.timer_movimiento.start(self.MOVE_INTERVAL)

        self.timer_seguir = QTimer(self)
        self.timer_seguir.timeout.connect(self._revisar_raton)
        self.timer_seguir.start(200)

    def _decaer(self):
        self.mascota.decrementar_atributos()
        self._actualizar_sprite()
        self.panel_control.actualizar(self.mascota)

    def _actualizar_sprite(self):
        sprite = self.mascota.sprite_estado
        self.mascota_widget.cambiar_sprite(sprite)

    def _actualizar_movimiento(self):
        if self._modo == "idle":
            screen = QApplication.primaryScreen().availableGeometry()
            x = self.x()

            if self._pausa_restante > 0:
                self._pausa_restante -= self.MOVE_INTERVAL
                return

            if random.random() < 0.005:
                self._direccion = random.choice([-1, 1])
                self._pausa_restante = random.randint(1000, 4000)

            dx = self.WALK_SPEED * self._direccion
            nuevo_x = x + dx

            if nuevo_x < 0 or nuevo_x > screen.width() - self.MASCOTA_SIZE:
                self._direccion *= -1
                self._pausa_restante = random.randint(500, 2000)
                nuevo_x = x + self.WALK_SPEED * self._direccion

            self.mascota_widget.establecer_mirando(self._direccion < 0)
            self.move(int(nuevo_x), self.y())

    def _revisar_raton(self):
        if self._arrastrando:
            return
        cursor = self.cursor().pos()
        centro = self.geometry().center()
        dx = cursor.x() - centro.x()
        dy = cursor.y() - centro.y()
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.FOLLOW_RADIUS:
            self._modo = "siguiendo"
            self._seguir_raton(cursor, centro, dx, dy, dist)
        else:
            if self._modo == "siguiendo":
                self._modo = "idle"

    def _seguir_raton(self, cursor, centro, dx, dy, dist):
        screen = QApplication.primaryScreen().availableGeometry()
        x = self.x()
        y = self.y()

        factor = min(1.0, (self.FOLLOW_RADIUS - dist) / self.FOLLOW_RADIUS)
        vel = self.FOLLOW_SPEED * factor

        if dist > 30:
            move_x = (dx / dist) * vel
            move_y = (dy / dist) * vel
            nuevo_x = int(x + move_x)
            nuevo_y = int(y + move_y)
            nuevo_x = max(0, min(nuevo_x, screen.width() - self.MASCOTA_SIZE))
            nuevo_y = max(0, min(nuevo_y, screen.height() - self.MASCOTA_SIZE - 40))
            self.move(nuevo_x, nuevo_y)
            self.mascota_widget.establecer_mirando(dx < 0)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._arrastrando = True
            self._offset_arrastre = event.pos()
        elif event.button() == Qt.RightButton:
            self._mostrar_menu_contextual(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._arrastrando:
            self.move(self.mapToGlobal(event.pos() - self._offset_arrastre))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._arrastrando:
            self._arrastrando = False
            self._modo = "idle"

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._toggle_panel()

    def _toggle_panel(self):
        if self.panel_control.isVisible():
            self.panel_control.hide()
        else:
            self.panel_control.actualizar(self.mascota)
            self.panel_control.mostrar_cerca_de(self)

    def _mostrar_menu_contextual(self, event):
        menu = QWidget(None)
        menu.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,230);
                border: 1px solid #ccc;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(menu)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        for texto, accion in [
            ("🍽 Alimentar", "comer"),
            ("🎾 Jugar", "jugar"),
            ("💤 Dormir", "dormir"),
            ("🚿 Bañar", "banar"),
            ("📊 Estadísticas", "estado"),
            ("❌ Salir", "salir"),
        ]:
            btn = QPushButton(texto)
            btn.setStyleSheet("""
                QPushButton {
                    border: none; border-radius: 6px; padding: 6px 16px;
                    background: transparent; color: #333; font-size: 12px;
                    text-align: left;
                }
                QPushButton:hover { background: rgba(0,0,0,0.08); }
            """)
            btn.clicked.connect(lambda checked, a=accion: self._ejecutar_accion(a))
            layout.addWidget(btn)

        menu.adjustSize()
        punto = self.mapToGlobal(event.pos())
        menu.move(punto)
        menu.show()
        if self._menu_actual:
            self._menu_actual.close()
        self._menu_actual = menu

    def _ejecutar_accion(self, accion):
        if self._menu_actual:
            self._menu_actual.close()
            self._menu_actual = None

        if accion == "estado":
            self._toggle_panel()
            return
        if accion == "salir":
            self.close()
            return

        act = None
        if accion == "comer":
            act = self.mascota.comer()
        elif accion == "jugar":
            act = self.mascota.jugar()
        elif accion == "dormir":
            act = self.mascota.dormir()
        elif accion == "banar":
            act = self.mascota.banar()

        if act:
            act.registrar(self.repo, self.mascota_id)
            self._guardar_estado()
            self._actualizar_sprite()
            self.mascota_widget.mostrar_accion(accion)
            self.panel_control.actualizar(self.mascota)

    def _guardar_estado(self):
        self.repo.actualizar_mascota(
            self.mascota_id,
            hambre=self.mascota.hambre,
            felicidad=self.mascota.felicidad,
            energia=self.mascota.energia,
            higiene=self.mascota.higiene,
        )

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self._guardar_estado()
        self.repo.registrar_actividad(self.mascota_id, "cierre", "Sesión finalizada")
        super().closeEvent(event)
