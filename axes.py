from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_axes():
    glBegin(GL_LINES)
    # Eje X - rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-100.0, 0.0, 0.0)
    glVertex3f(100.0, 0.0, 0.0)

    # Eje Y - verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -100.0, 0.0)
    glVertex3f(0.0, 100.0, 0.0)

    # Eje Z - azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -100.0)
    glVertex3f(0.0, 0.0, 100.0)
    glEnd()