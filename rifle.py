from weapon import Weapon
from events import spawn_player_bullet
class Rifle(Weapon): 
    def __init__(self, ctx, shader, scale=(1.0)):
        super().__init__(ctx, shader, "rifle.obj", scale)
        self.fire_delay = 0.4  # Tiempo mínimo entre disparos en segundos
        self.ammo = 10
        self.max_ammo = 10
        
    def shoot_logic(self):
        self.camera.apply_recoil(0.9)  # Pistol tiene poco retroceso 
        spawn_player_bullet.send(self.player, position=self.player.pos, direction=self.player.front)