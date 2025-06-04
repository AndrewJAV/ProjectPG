import numpy as np
from model import Model

class Bullet:
    def __init__(self, model_path, position, direction, speed=5.0, scale=0.8):
        self.model = Model(model_path, position=position, scale=scale)
        self.position = np.array(position, dtype=np.float32)

        # Normalizar la dirección
        self.direction = np.array(direction, dtype=np.float32)
        self.direction = self.direction / np.linalg.norm(self.direction)
        self.speed = speed

        dx, dy, dz = self.direction

        # Yaw corregido: invertir signo para que coincida con la cámara
        yaw = -np.degrees(np.arctan2(dx, -dz))

        # Pitch: inclinación vertical
        pitch = np.degrees(np.arctan2(dy, np.sqrt(dx**2 + dz**2)))

        roll = 0  # Puedes animarlo si deseas

        self.model.rotation = (pitch, yaw, roll)

    def update(self, dt):
        self.position += self.direction * self.speed * dt
        self.model.position = tuple(self.position)

    def draw(self):
        self.model.draw()
