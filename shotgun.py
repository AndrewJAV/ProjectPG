from weapon import Weapon
import random, glm
from events import spawn_player_bullet

class Shotgun(Weapon): 
    def __init__(self, ctx, shader, player, scale=(1.0)):
        super().__init__(ctx, shader, "shotgun.obj", player, scale)
        self.fire_delay = 0.9  # Tiempo mínimo entre disparos en segundos
        
    def shoot_logic(self):
        for _ in range(8):
            spread = glm.vec3(
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05)
            )
            dir = glm.normalize(self.player.front + spread)
            spawn_player_bullet.send(self.player, position=self.player.pos, direction=dir)
        
        print("Escopeta dispara")
        self.camera.apply_recoil(3)  # Pistol tiene poco retroceso 