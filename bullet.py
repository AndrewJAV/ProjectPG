# bullet.py
import glm
from model import Model 

class Bullet(Model):
    def __init__(self, ctx, program, model_path, position, direction, speed=50.0, scale=(0.8, 0.8, 1.4), owner=None):
        # Normaliza la dirección
        direction = glm.normalize(glm.vec3(direction))
        self.direction = direction
        self.speed = speed
        self.alive = True
        self.owner = owner

        yaw = glm.degrees(glm.atan(direction.x, direction.z))  
        pitch = -glm.degrees(glm.asin(glm.clamp(direction.y, -1.0, 1.0)))

        super().__init__(ctx, program, model_path, position=position, rotation=(pitch, yaw, 0), scale=scale)

    def update(self, dt):
        if not self.alive:
            return
        self.position += self.direction * self.speed * dt 

    def check_collision(self, targets):
        bullet_obb = self.get_obb()
        for target in targets:
            if target is self.owner:
                continue
            if bullet_obb.intersects(target.get_obb()): 
                self.alive = False
                break
            
            
