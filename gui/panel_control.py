from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QProgressBar, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

BAR_COLORS = {
    "hambre": QColor(255, 100, 100),
    "felicidad": QColor(255, 200, 50),
    "energia": QColor(100, 200, 255),
    "higiene": QColor(100, 255, 150),
}
NOMBRES = {
    "hambre": "Hambre",
    "felicidad": "Felicidad",
    "energia": "Energía",
    "higiene": "Higiene",
}


class PanelControl(QFrame):
    accion_solicitada = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet("""
            PanelControl {
                background: rgba(255, 255, 255, 235);
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 16px;
            }
            QLabel#titulo {
                color: #444; font-size: 14px; font-weight: bold;
            }
            QLabel#nombre_estado {
                color: #666; font-size: 11px;
            }
        """)
        self._build_ui()
        self._animando = False

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 12, 14, 12)

        encabezado = QHBoxLayout()
        self.titulo = QLabel("Mi Mascota")
        self.titulo.setObjectName("titulo")
        self.estado_label = QLabel("")
        self.estado_label.setObjectName("nombre_estado")
        encabezado.addWidget(self.titulo)
        encabezado.addStretch()
        encabezado.addWidget(self.estado_label)
        layout.addLayout(encabezado)

        grid = QGridLayout()
        grid.setSpacing(6)
        self.barras = {}
        for i, key in enumerate(["hambre", "felicidad", "energia", "higiene"]):
            lbl = QLabel(NOMBRES[key])
            lbl.setStyleSheet("color: #555; font-size: 11px;")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(50)
            bar.setFixedHeight(14)
            bar.setTextVisible(True)
            bar.setFormat("%v")
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #ddd; border-radius: 7px;
                    background: #f0f0f0; height: 14px;
                }}
                QProgressBar::chunk {{
                    border-radius: 7px;
                    background: {BAR_COLORS[key].name()};
                }}
            """)
            self.barras[key] = bar
            grid.addWidget(lbl, i, 0)
            grid.addWidget(bar, i, 1)
        layout.addLayout(grid)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("border: none; border-top: 1px solid #ddd;")
        layout.addWidget(sep)

        botones_layout = QGridLayout()
        botones_layout.setSpacing(6)

        acciones = [
            ("comer", "🍽 Comer"),
            ("jugar", "🎾 Jugar"),
            ("dormir", "💤 Dormir"),
            ("banar", "🚿 Bañar"),
        ]
        for idx, (key, texto) in enumerate(acciones):
            btn = QPushButton(texto)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ccc; border-radius: 8px; padding: 4px 12px;
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #fafafa, stop:1 #eee);
                    color: #333; font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e8e8e8, stop:1 #ddd);
                    border-color: #aaa;
                }
                QPushButton:pressed { background: #ccc; }
            """)
            btn.clicked.connect(lambda checked, k=key: self.accion_solicitada.emit(k))
            botones_layout.addWidget(btn, idx // 2, idx % 2)
        layout.addLayout(botones_layout)

        self.setFixedSize(self.sizeHint())

    def actualizar(self, mascota):
        self.barras["hambre"].setValue(100 - mascota.hambre)
        self.barras["felicidad"].setValue(mascota.felicidad)
        self.barras["energia"].setValue(mascota.energia)
        self.barras["higiene"].setValue(mascota.higiene)
        estado = mascota.estado_general
        nombres_estado = {
            "muy_feliz": "Muy feliz 😄",
            "feliz": "Feliz 😊",
            "neutral": "Normal 😐",
            "triste": "Triste 😢",
            "enfermo": "Enfermo 🤒",
        }
        self.estado_label.setText(nombres_estado.get(estado, ""))

    def mostrar_cerca_de(self, widget_origen, offset_y=-160):
        punto = widget_origen.mapToGlobal(widget_origen.rect().topLeft())
        self.move(punto.x() - self.width() // 2 + widget_origen.width() // 2,
                  punto.y() + offset_y)
        self.show()
        self.activateWindow()
        self.setFocus()

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)
