import glm 
from entity import Entity 
from bullet import Bullet
from events import spawn_player_bullet, spawn_enemy_bullet
from green_drone import GreenDrone
from drone import Drone

class BulletManager:
    def __init__(self, ctx, shader, player):
        self.ctx = ctx 
        self.shader = shader 
        self.player = player 
        self.player_bullets = [] 
        self.enemy_bullets = [] 
        self.fire_cooldown = 0.0 
        self.fire_delay = 0.1 
        
        spawn_player_bullet.connect(self.spawn_player_bullet)
        spawn_enemy_bullet.connect(self.spawn_enemy_bullet)

    def spawn_player_bullet(self, sender, *, position, direction):
        bullet = Bullet(
            self.ctx, 
            self.shader, 
            "bullet.obj", 
            position=position, 
            direction=direction,
            owner=sender
        )
        self.player_bullets.append(bullet)

    def spawn_enemy_bullet(self, sender, *, position, direction, heal=False):
        model = "green_bullet.obj" if heal else "bullet.obj"
        
        bullet = Bullet(
            self.ctx,
            self.shader,
            model,
            position=position,
            direction=direction,
            owner=sender
        )
        self.enemy_bullets.append(bullet)

    def update(self, dt, obstacles):
        for bullet in self.player_bullets:
            bullet.update(dt)
            for model in obstacles:
                if any(bullet.get_obb().intersects(collider) for collider in model.colliders):
                    bullet.alive = False
                    
                    if isinstance(model, Entity):
                        model.reduce_health(10)
                    break
        
        player_obb = self.player.camera.get_obb()
        for bullet in self.enemy_bullets:
            if bullet.get_obb().intersects(player_obb):
                bullet.alive = False
                self.player.reduce_health()
                print("¡El jugador fue alcanzado por una bala!")
                
        for bullet in self.enemy_bullets:
            bullet.update(dt)
            for obstacle in obstacles:
                if any(bullet.get_obb().intersects(collider) for collider in obstacle.colliders):
                    bullet.alive = False
                    if isinstance(bullet.owner, GreenDrone) and isinstance(obstacle, Drone):
                        obstacle.health +=5
                    break
                
        self.player_bullets = [b for b in self.player_bullets if b.alive and glm.length(b.position - self.player.camera.position) < 20]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive and glm.length(b.position - self.player.camera.position) < 20]

    def draw(self, proj, view, camera_position):
        for bullet in self.player_bullets + self.enemy_bullets:
            bullet.draw(self.shader, proj, view, camera_position)
