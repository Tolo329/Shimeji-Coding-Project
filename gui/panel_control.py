from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QProgressBar, QLabel
from PySide6.QtCore import Qt


class PanelControl(QFrame):
    """Panel flotante que muestra las estadisticas y botones de accion"""

    def __init__(self, callback_accion=None, parent=None):
        super().__init__(parent)
        self.callback_accion = callback_accion

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Fondo blanco solido con bordes redondeados y sombra
        self.setStyleSheet("""
            PanelControl {
                background-color: #ffffff;
                border: 2px solid #555555;
                border-radius: 16px;
            }
        """)

        self._crear_interfaz()

    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 14, 18, 14)

        # Encabezado
        encabezado = QHBoxLayout()
        self.titulo = QLabel("Mi Mascota")
        self.titulo.setStyleSheet("color: #111111; font-size: 16px; font-weight: bold;")
        self.estado_label = QLabel("")
        self.estado_label.setStyleSheet("color: #333333; font-size: 13px;")
        encabezado.addWidget(self.titulo)
        encabezado.addStretch()
        encabezado.addWidget(self.estado_label)
        layout.addLayout(encabezado)

        # Barras de progreso
        self.barras = {}
        colores = {
            "hambre": "#FF4444",
            "felicidad": "#FFAA00",
            "energia": "#3399FF",
            "higiene": "#33CC66",
        }
        nombres = {
            "hambre": "Hambre",
            "felicidad": "Felicidad",
            "energia": "Energia",
            "higiene": "Higiene",
        }

        grid = QGridLayout()
        grid.setSpacing(8)

        for i, clave in enumerate(["hambre", "felicidad", "energia", "higiene"]):
            etiqueta = QLabel(nombres[clave])
            etiqueta.setStyleSheet("color: #222222; font-size: 13px; font-weight: bold;")

            barra = QProgressBar()
            barra.setRange(0, 100)
            barra.setValue(50)
            barra.setFixedHeight(18)
            barra.setTextVisible(True)
            barra.setFormat("%v")
            barra.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #999999;
                    border-radius: 9px;
                    background: #e0e0e0;
                    height: 18px;
                }}
                QProgressBar::chunk {{
                    border-radius: 9px;
                    background: {colores[clave]};
                }}
            """)
            self.barras[clave] = barra
            grid.addWidget(etiqueta, i, 0)
            grid.addWidget(barra, i, 1)

        layout.addLayout(grid)

        # Linea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("border: none; border-top: 2px solid #cccccc;")
        layout.addWidget(linea)

        # Botones de accion
        if self.callback_accion:
            botones_layout = QGridLayout()
            botones_layout.setSpacing(8)

            acciones = [
                ("comer", "Comer"),
                ("jugar", "Jugar"),
                ("dormir", "Dormir"),
                ("banar", "Banar"),
            ]
            for idx, (clave, texto) in enumerate(acciones):
                boton = QPushButton(texto)
                boton.setFixedHeight(36)
                boton.setCursor(Qt.PointingHandCursor)
                boton.setStyleSheet("""
                    QPushButton {
                        border: 2px solid #666666;
                        border-radius: 10px;
                        padding: 6px 16px;
                        background-color: #f5f5f5;
                        color: #111111;
                        font-size: 13px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #d0eaff;
                        border-color: #3399ff;
                    }
                    QPushButton:pressed {
                        background-color: #b0d0f0;
                    }
                """)
                boton.clicked.connect(lambda checked, k=clave: self.callback_accion(k))
                botones_layout.addWidget(boton, idx // 2, idx % 2)

            layout.addLayout(botones_layout)

        self.setFixedSize(self.sizeHint())

    def actualizar(self, mascota):
        self.barras["hambre"].setValue(100 - mascota.hambre)
        self.barras["felicidad"].setValue(mascota.felicidad)
        self.barras["energia"].setValue(mascota.energia)
        self.barras["higiene"].setValue(mascota.higiene)

        estados = {
            "muy_feliz": "Muy feliz",
            "feliz": "Feliz",
            "neutral": "Normal",
            "triste": "Triste",
            "enfermo": "Enfermo",
        }
        self.estado_label.setText(estados.get(mascota.obtener_estado_general(), ""))

    def mostrar_cerca_de(self, widget_origen):
        punto = widget_origen.mapToGlobal(widget_origen.rect().topLeft())
        x = punto.x() - self.width() // 2 + widget_origen.width() // 2
        y = punto.y() - 180
        self.move(x, y)
        self.show()
        self.activateWindow()
        self.setFocus()

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)
