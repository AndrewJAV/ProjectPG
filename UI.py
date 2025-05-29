from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import OpenGL.GL as gl

class GLWidget(QOpenGLWidget):
    def initializeGL(self):
        gl.glClearColor(0.2, 0.3, 0.4, 1.0)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
gl_widget = GLWidget()
layout.addWidget(gl_widget)
window.setLayout(layout)
window.show()
app.exec_()