import random
import math
from PySide6.QtWidgets import QWidget, QApplication, QMenu, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QMouseEvent, QKeyEvent, QAction

from dominio.mascota import Mascota
from gui.widget_mascota import WidgetMascota
from gui.panel_control import PanelControl


class VentanaPrincipal(QWidget):

    def __init__(self, mascota, repositorio, mascota_id):
        super().__init__()
        self.mascota = mascota
        self.repo = repositorio
        self.mascota_id = mascota_id

        # Variables para mover la ventana arrastrando
        self._arrastrando = False
        self._offset_arrastre = QPoint(0, 0)

        # Variables de movimiento de la mascota
        self._modo = "idle"          # idle o siguiendo
        self._direccion = 1          # 1 = derecha, -1 = izquierda
        self._pausa_restante = 0     # milisegundos de pausa antes de caminar

        self._configurar_ventana()
        self._crear_widgets()
        self._iniciar_timers()

    def _configurar_ventana(self):
        """Ventana sin bordes, transparente, siempre encima"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(WidgetMascota.SIZE, WidgetMascota.SIZE)

        # Aparecer en una posicion aleatoria de la pantalla
        pantalla = QApplication.primaryScreen().availableGeometry()
        x = random.randint(50, pantalla.width() - WidgetMascota.SIZE - 50)
        y = pantalla.height() - WidgetMascota.SIZE - 80
        self.move(x, y)

    def _crear_widgets(self):
        self.mascota_widget = WidgetMascota(self)
        self.mascota_widget.move(0, 0)
        self.panel_control = PanelControl(callback_accion=self._ejecutar_accion)

    def _iniciar_timers(self):
        self.timer_decaimiento = QTimer(self)
        self.timer_decaimiento.timeout.connect(self._decaer)
        self.timer_decaimiento.start(4000)  # cada 4 segundos baja atributos

        self.timer_movimiento = QTimer(self)
        self.timer_movimiento.timeout.connect(self._caminar)
        self.timer_movimiento.start(30)      # ~30 fps para movimiento suave

        self.timer_seguir = QTimer(self)
        self.timer_seguir.timeout.connect(self._revisar_raton)
        self.timer_seguir.start(200)

    def _decaer(self):
        """Baja los atributos de la mascota con el tiempo"""
        self.mascota.decrementar_atributos()
        self._actualizar_sprite()
        if self.panel_control.isVisible():
            self.panel_control.actualizar(self.mascota)

    def _actualizar_sprite(self):
        sprite = self.mascota.obtener_sprite()
        self.mascota_widget.cambiar_sprite(sprite)

    def _caminar(self):
        """La mascota camina sola cuando esta en modo idle"""
        if self._modo != "idle":
            return

        pantalla = QApplication.primaryScreen().availableGeometry()

        # Si esta en pausa, esperar
        if self._pausa_restante > 0:
            self._pausa_restante -= self.timer_movimiento.interval()
            return

        # A veces cambiar de direccion aleatoriamente
        if random.random() < 0.005:  # ~0.5% por frame
            self._direccion = random.choice([-1, 1])
            self._pausa_restante = random.randint(1000, 4000)

        x = self.x()
        nuevo_x = x + 1.5 * self._direccion

        # Si llega al borde de la pantalla, dar la vuelta
        if nuevo_x < 0 or nuevo_x > pantalla.width() - WidgetMascota.SIZE:
            self._direccion *= -1
            self._pausa_restante = random.randint(500, 2000)
            nuevo_x = x + 1.5 * self._direccion

        self.mascota_widget.establecer_mirando(self._direccion < 0)
        self.move(int(nuevo_x), self.y())

    def _revisar_raton(self):
        """Si el raton esta cerca, la mascota lo sigue"""
        if self._arrastrando:
            return

        cursor = self.cursor().pos()
        centro = self.geometry().center()
        dx = cursor.x() - centro.x()
        dy = cursor.y() - centro.y()
        distancia = math.sqrt(dx * dx + dy * dy)

        if distancia < 200:  # radio de seguimiento
            self._modo = "siguiendo"
            self._seguir_raton(cursor, dx, dy, distancia)
        else:
            if self._modo == "siguiendo":
                self._modo = "idle"

    def _seguir_raton(self, cursor, dx, dy, distancia):
        """Mueve la mascota hacia el cursor"""
        pantalla = QApplication.primaryScreen().availableGeometry()
        x = self.x()
        y = self.y()

        if distancia > 30:
            factor = min(1.0, (200 - distancia) / 200)
            velocidad = 3.0 * factor
            mover_x = (dx / distancia) * velocidad
            mover_y = (dy / distancia) * velocidad
            nuevo_x = int(x + mover_x)
            nuevo_y = int(y + mover_y)
            # No salirse de la pantalla
            nuevo_x = max(0, min(nuevo_x, pantalla.width() - WidgetMascota.SIZE))
            nuevo_y = max(0, min(nuevo_y, pantalla.height() - WidgetMascota.SIZE - 40))
            self.move(nuevo_x, nuevo_y)
            self.mascota_widget.establecer_mirando(dx < 0)

    # --- Eventos del raton ---

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._arrastrando = True
            self._offset_arrastre = event.pos()
        elif event.button() == Qt.RightButton:
            self._mostrar_menu(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._arrastrando:
            self.move(self.mapToGlobal(event.pos() - self._offset_arrastre))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._arrastrando:
            self._arrastrando = False
            self._modo = "idle"

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._abrir_o_cerrar_panel()

    # --- Menu contextual (clic derecho) ---

    def _mostrar_menu(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(255,255,255,240);
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 6px;
                font-size: 12px;
            }
            QMenu::item:selected {
                background: rgba(0,0,0,0.08);
            }
        """)

        # Opciones del menu
        accion_comer = QAction("🍽  Alimentar", self)
        accion_comer.triggered.connect(lambda: self._ejecutar_accion("comer"))
        menu.addAction(accion_comer)

        accion_jugar = QAction("🎾  Jugar", self)
        accion_jugar.triggered.connect(lambda: self._ejecutar_accion("jugar"))
        menu.addAction(accion_jugar)

        accion_dormir = QAction("💤  Dormir", self)
        accion_dormir.triggered.connect(lambda: self._ejecutar_accion("dormir"))
        menu.addAction(accion_dormir)

        accion_banar = QAction("🚿  Bañar", self)
        accion_banar.triggered.connect(lambda: self._ejecutar_accion("banar"))
        menu.addAction(accion_banar)

        menu.addSeparator()

        accion_estado = QAction("📊  Estadísticas", self)
        accion_estado.triggered.connect(self._abrir_o_cerrar_panel)
        menu.addAction(accion_estado)

        accion_reiniciar = QAction("🔄  Nueva Mascota", self)
        accion_reiniciar.triggered.connect(self._reiniciar_mascota)
        menu.addAction(accion_reiniciar)

        menu.addSeparator()

        accion_salir = QAction("❌  Salir", self)
        accion_salir.triggered.connect(self.close)
        menu.addAction(accion_salir)

        menu.exec(event.globalPosition().toPoint())

    def _ejecutar_accion(self, accion):
        if accion == "comer":
            actividad = self.mascota.comer()
        elif accion == "jugar":
            actividad = self.mascota.jugar()
        elif accion == "dormir":
            actividad = self.mascota.dormir()
        elif accion == "banar":
            actividad = self.mascota.banar()
        else:
            return

        actividad.registrar(self.repo, self.mascota_id)
        self._guardar_estado()
        self._actualizar_sprite()
        self.mascota_widget.mostrar_accion(accion)
        if self.panel_control.isVisible():
            self.panel_control.actualizar(self.mascota)

    # --- Panel de estado ---

    def _abrir_o_cerrar_panel(self):
        if self.panel_control.isVisible():
            self.panel_control.hide()
        else:
            self.panel_control.actualizar(self.mascota)
            self.panel_control.mostrar_cerca_de(self)

    # --- RF-08: Reiniciar mascota ---

    def _reiniciar_mascota(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Nueva Mascota")
        msg.setText("¿Estás seguro de que quieres reiniciar?\nSe borrará la mascota actual.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        if msg.exec() != QMessageBox.Yes:
            return

        nombre, ok = QInputDialog.getText(self, "Nueva Mascota", "Nombre de la nueva mascota:")
        if not ok or not nombre.strip():
            return

        # Borrar mascota actual de la BD
        self.repo.eliminar_mascota(self.mascota_id)

        # Crear nueva mascota
        nuevo_id = self.repo.guardar_mascota(nombre.strip())
        modelo = self.repo.obtener_mascota(nuevo_id)
        self.mascota = Mascota.copiar_desde_modelo(modelo)
        self.mascota_id = nuevo_id

        self._actualizar_sprite()
        if self.panel_control.isVisible():
            self.panel_control.actualizar(self.mascota)

    # --- Guardar y cerrar ---

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
        self.repo.registrar_actividad(self.mascota_id, "cierre", "Sesion finalizada")
        super().closeEvent(event)
