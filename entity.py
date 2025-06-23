# entity.py
import glm
from model import Model

class Entity(Model):
    def __init__(self, ctx, program, model_path, position=(0,0,0), rotation=(0,0,0), speed=1.0, scale=(1.0,1.0,1.0), **kwargs):
        super().__init__(ctx, program, model_path, position=position, rotation=rotation, scale=scale, **kwargs)
        self.speed = speed  
        health = 100
        max_health = 100

    def update(self, dt, camera_position):
        # Movimiento simple hacia adelante en su dirección local
        pass

    def on_hit(self, damage):
        # Sobrescribible: qué pasa si recibe daño
        pass

    def on_player_seen(self, player_position):
        # Sobrescribible: reacción al ver al jugador
        pass
    
    def reduce_health(self, amount=10):
        self.health -= amount
        
    def increase_health(self, amount=10):
        self.health += amount

    