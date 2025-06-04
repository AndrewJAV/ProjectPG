# bullet.py
import numpy as np
from model import Model

class Bullet:
    def __init__(self, model_path, position, direction, rotation, speed=10.0, scale=0.8):
        self.model = Model(model_path, position=position, scale=scale)
        self.position = np.array(position, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)
        self.direction = self.direction / np.linalg.norm(self.direction)  # Normalizar
        self.speed = speed

        # Aplicar rotación directa de la cámara (pitch, yaw, roll)
        self.model.rotation = (rotation[0], -rotation[1], rotation[2])

    def update(self, dt):
        self.position += self.direction * self.speed * dt
        self.model.position = tuple(self.position)

    def draw(self):
        self.model.draw()
