import numpy as np
from OpenGL.GL import *
from model import Model  # Asumiendo que tu clase Model está en un archivo llamado model.py

class WeaponView:
    def __init__(self, obj_filename, scale=1.0):
        self.weapon_model = Model(obj_filename, scale=scale)
        self.offset = np.array([0.25, -0.3, -1.5], dtype=np.float32)  # Ajusta esto si lo ves muy lejos o cerca
        self.rotation = np.array([10, 0, 0], dtype=np.float32)     # Rotación típica para armas FPS

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Mover a la esquina inferior derecha
        glTranslatef(*self.offset)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        self.weapon_model.draw()

        glPopMatrix()
