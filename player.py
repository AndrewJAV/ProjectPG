from camera import Camera
import glm
import pygame 
from events import *
from rifle import Rifle
from pistol import Pistol
from shotgun import Shotgun
import random

class Player():
    def __init__(self, position):
        self.camera = Camera(position) 
        self.health = 100
        self.max_health = 100
        self.move_speed = 5.0
        self.shoot_cooldown = 0.5
        self.last_shot_time = -999.0
        self.input_enabled = True
        self.heldweapon = None
        self.dying = False
        self.death_timer = 0.0
        self.death_duration = 2.0  # segundos
        self.death_rotation_speed_x = 60.0  # grados/segundo
        self.death_rotation_speed_z = 90.0
        self.weapons = []
        
    @property
    def pos(self):
        return self.camera.position
    
    @property
    def front(self):
        return self.camera.front
    
    def handle_input(self, tn, events):
        # clic derecho            
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.heldweapon and self.heldweapon.can_shoot():
                        player_shoot.send(None, weapon=self.heldweapon) 
                        #spawn_player_bullet.send(None, position=self.pos, direction=self.front, )
                            
                elif event.button == 3:
                    player_aim.send()    # Emitir señal de apuntado
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    player_stop_aim.send()  # Dejar de apuntar
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and self.heldweapon != self.weapons[0]:
                    self.heldweapon = self.weapons[0]
                    weapon_equip.send()
                elif event.key == pygame.K_2 and self.heldweapon != self.weapons[1]:
                    self.heldweapon = self.weapons[1]
                    weapon_equip.send()
                elif event.key == pygame.K_3 and self.heldweapon != self.weapons[2]:
                    self.heldweapon = self.weapons[2]
                    weapon_equip.send() 
                elif event.key == pygame.K_r and self.heldweapon:
                    self.heldweapon.reload()
                    
            elif event.type == pygame.MOUSEWHEEL:
                weapon_num = self.weapons.index(self.heldweapon)
                if event.y > 0:
                    weapon_num -= 1
                elif event.y < 0:
                    weapon_num += 1
                    
                if weapon_num < 0:
                    weapon_num = 2
                elif weapon_num > 2:
                    weapon_num = 0
                
                self.heldweapon = self.weapons[weapon_num]
                weapon_equip.send() 
    
    def update_death_animation(self, dt):
        if not self.dying:
            return

        self.death_timer += dt

        # Aplicar rotaciones hacia la derecha en X y Z
        self.camera.rotation.x += self.death_rotation_speed_x * dt
        self.camera.rotation.z += self.death_rotation_speed_z * dt

        if self.death_timer >= self.death_duration:
            self.input_enabled = False  # Bloquear controles
            print("¡El jugador ha muerto!")           

    def reduce_health(self, amount=10):
        self.health -= amount
        if self.health <= 0 and not self.camera.is_dead:
            self.camera.start_death_animation()
            self.input_enabled = False  # opcional: deshabilitar input
    