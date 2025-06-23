import glm
import pygame
import moderngl
from model import Model 
from events import *
import time

class Weapon:
    def __init__(self, ctx, shader, obj_path, player, scale=(1.0, 1.0, 1.0)):
        self.weapon_model = Model(ctx, shader, obj_path, position=(0, 0, 0))
        self.scale = glm.vec3(scale)
        self.rotation = glm.vec3(0, 0, 0)
        self.camera = player.camera
        self.player = player
        self.ammo = 10
        self.max_ammo = 10
        self.reloading = False 
        self.reload_start_time = 0

        self.offset_normal = glm.vec3(0.5, -0.3, -1.1)
        self.offset_aiming = glm.vec3(0.0, -0.3, -1.1)
        self.offset = glm.vec3(self.offset_normal)
        
        self.equip_start_offset = glm.vec3(0.5, -0.6, -1.1)
        self.equip_end_offset = glm.vec3(0.5, -0.3, -1.1)
        self.equip_duration = 1.0  # segundos
        self.equip_start_time = None
        self.equipping = False

        self.aiming = False
        self.aim_time = 0.0  # Rango de 0.0 a 1.0
        self.transition_speed = 15.0  # 1 segundo
        
        self.last_shot_time = -999.0
        self.recoil_time = 0.0
        self.recoil_duration = 0.1  # duración total del retroceso en segundos
        self.recoil_angle = 20.0  
        self.fire_delay = 0.4 
        
        self.reloading = False
        self.reload_time = 1.5  # total (visual + lógica) 

        self.reload_anim_time = 0.0
        self.reload_anim_phase = 0  # 0: start, 1: left, 2: right, 3: back
        self.reload_anim_duration_per_phase = self.reload_time / 6
        self.pending_reload = False
        self.force_stop_aiming = False
        
        self.reload_phase = None  # None = no recargando, 0..4 para fases 
        
        # Link methods to eventw
        player_shoot.connect(self.on_shoot)
        player_aim.connect(self.on_aim)
        player_stop_aim.connect(self.on_stop_aim)
        weapon_equip.connect(self.start_equip_animation)
    
    def shoot_logic(self):
        pass
        
    def on_aim(self, sender=None): 
        if self.can_aim():
            self.aiming = True

    def on_stop_aim(self, sender=None):
        self.aiming = False

    def on_shoot(self, sender, *, weapon):
        if self.can_shoot():
            self.rotation.z = 0.0  
            self.last_shot_time = time.time()
            self.recoil_time = self.recoil_duration

            if weapon is self:
                self.ammo -= 1
                if self.ammo == 0:
                    self.reload()
                self.shoot_logic()
                
    def start_reload(self):
        self.offset = glm.vec3(self.offset_normal)
        self.rotation = glm.vec3(0.0)
        self.reloading = True
        self.reload_start_time = time.time()
        self.reload_phase = 1  # empezamos animación rotación directamente
        self.reload_anim_time = 0.0

                
    def reload(self):
        if not self.reloading and not self.pending_reload and self.ammo < self.max_ammo:
            if self.aiming:
                # iniciar fase 0: dejar de apuntar para luego recargar
                self.pending_reload = True
                self.reload_phase = 0
                self.reload_anim_time = 0.0
                self.force_stop_aiming = True
            else:
                self.start_reload()


                

    def start_equip_animation(self, sender=None):
        self.equipping = True
        self.equip_start_time = time.time()
    
    def update(self, dt):
        if self.reload_phase is not None:
            self.reload_anim_time += dt
            phase_time = self.reload_anim_duration_per_phase

            if self.reload_phase == 0:
                # Animación de dejar de apuntar
                self.aim_time -= dt * self.transition_speed
                self.aim_time = max(0.0, self.aim_time)
                self.offset = glm.mix(self.offset_normal, self.offset_aiming, self.aim_time)

                if self.aim_time <= 0.0:
                    self.aiming = False
                    self.force_stop_aiming = False
                    self.pending_reload = False
                    self.reload_phase = 1
                    self.reload_anim_time = 0.0
                    self.reloading = True
                    self.reload_start_time = time.time()

            elif self.reload_phase == 1:
                # 0° a +90°
                t = min(self.reload_anim_time / phase_time, 1.0)
                self.rotation.z = glm.mix(0.0, 90.0, t)
                if t >= 1.0:
                    self.reload_phase = 2
                    self.reload_anim_time = 0.0

            elif self.reload_phase == 2:
                # +90° a -90°
                t = min(self.reload_anim_time / phase_time, 1.0)
                self.rotation.z = glm.mix(90.0, -90.0, t)
                if t >= 1.0:
                    self.reload_phase = 3
                    self.reload_anim_time = 0.0

            elif self.reload_phase == 3:
                # -90° a 0°
                t = min(self.reload_anim_time / phase_time, 1.0)
                self.rotation.z = glm.mix(-90.0, 0.0, t)
                if t >= 1.0:
                    self.reload_phase = 4
                    self.reload_anim_time = 0.0

            elif self.reload_phase == 4:
                # Esperar hasta completar el tiempo total de recarga
                self.rotation.z = 0.0
                if time.time() - self.reload_start_time >= self.reload_time:
                    self.reloading = False
                    self.ammo = self.max_ammo
                    self.reload_phase = None

        else:
            # Animaciones normales (equipar, apuntar, retroceso)
            if self.equipping:
                t = (time.time() - self.equip_start_time) / self.equip_duration
                if t >= 1.0:
                    t = 1.0
                    self.equipping = False
                self.offset = glm.mix(self.equip_start_offset, self.equip_end_offset, t)
            else:
                if self.aiming:
                    self.aim_time += dt * self.transition_speed
                else:
                    self.aim_time -= dt * self.transition_speed

                self.aim_time = max(0.0, min(1.0, self.aim_time))
                self.offset = glm.mix(self.offset_normal, self.offset_aiming, self.aim_time)

            # Retroceso
            if self.recoil_time > 0.0:
                t = 1.0 - (self.recoil_time / self.recoil_duration)
                self.rotation.x = self.recoil_angle * (1.0 - abs(2 * t - 1))
                self.recoil_time -= dt
            else:
                self.rotation.x = 0.0

    
        
    def can_shoot(self):
        current_time = time.time()
        if self.reloading:
            # Verifica si terminó la recarga
            if current_time - self.reload_start_time >= self.reload_time:
                self.reloading = False
                self.ammo = self.max_ammo
            else:
                return False  # Todavía recargando
        # Solo puede disparar si hay munición y no está equipando
        return (not self.equipping and 
                (current_time - self.last_shot_time) >= self.fire_delay and
                self.ammo > 0)
        
    def can_aim(self):
        return not self.equipping

    def draw(self, shader, proj, view):
        # Construye la base de orientación de la cámara usando right, up y -front
        cam_basis = glm.mat4(
            glm.vec4(self.camera.right, 0.0),
            glm.vec4(self.camera.up,    0.0),
            glm.vec4(-self.camera.front, 0.0),
            glm.vec4(0.0, 0.0, 0.0, 1.0)
        )

        # Matriz modelo para el arma
        model = glm.mat4(1.0)
        model = glm.translate(model, self.camera.position)  # Origen en la cámara
        model *= cam_basis                             # Aplica orientación de cámara
        model = glm.translate(model, self.offset)      # Offset de "arma en mano"
        model = glm.rotate(model, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        model = glm.scale(model, self.scale)

        # Pasar uniforms
        shader["model"].write(model.to_bytes())
        shader["view"].write(view.to_bytes())
        shader["proj"].write(proj.to_bytes())
        shader["view_position"].write(self.camera.position.to_bytes())

        # Dibujar
        self.weapon_model.vao.render(mode=moderngl.TRIANGLES, vertices=self.weapon_model.vertex_count)

