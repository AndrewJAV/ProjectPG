import glm
import pygame
import random
from obb import OBB

class Camera:
    def __init__(self, position):
        self.position = glm.vec3(position)
        self.yaw = -90.0
        self.pitch = 0.0
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.cross(self.front, self.up)
        self.world_up = glm.vec3(0, 1.1, 0)
        self.speed = 0.07
        self.sensitivity = 0.1
        self.recoil_offset = 0.0
        self.recoil_decay = 10.0
        self.update_vectors()
        self.colliders = []
        self.rotation_x = 0.0  # rotación extra para animación muerte
        self.rotation_z = 0.0

        self.is_dead = False
        self.death_anim_duration = 0.5  # segundos que dura la animación
        self.death_anim_elapsed = 0.0
        
        self.velocity = glm.vec3(0)        # Velocidad de movimiento totalw
        self.gravity = -0.008               # Fuerza de gravedad (ajustable)
        self.jump_strength = 0.15          # Fuerza del salto
        self.on_ground = False     
        
        
    # Método para iniciar animación muerte
    def start_death_animation(self):
        self.is_dead = True
        self.death_anim_elapsed = 0.0
        self.rotation_x = 0.0
        self.rotation_z = 0.0

    def update(self, dt):
        if self.is_dead:
            self.death_anim_elapsed += dt
            t = min(self.death_anim_elapsed / self.death_anim_duration, 1.0)
            # Interpolamos rotaciones de 0 a 90 grados hacia la derecha
            self.rotation_x = glm.mix(0.0, 90.0, t)
            self.rotation_z = glm.mix(0.0, 90.0, t)
            # Opcional: al terminar la animación, podrías hacer algo más
            # if t >= 1.0:
            #     print("Animación de muerte terminada")

    def apply_recoil(self, vertical_amount=1.5, horizontal_shake=1.0):
        self.pitch += vertical_amount
        self.yaw += random.uniform(-horizontal_shake, horizontal_shake)
        self.pitch = max(-89.0, min(89.0, self.pitch))  # clamp

    def update_vectors(self):
        rad_yaw = glm.radians(self.yaw)
        rad_pitch = glm.radians(self.pitch + self.recoil_offset)  # Aplica retroceso aquí
        front = glm.vec3(
            glm.cos(rad_yaw) * glm.cos(rad_pitch),
            glm.sin(rad_pitch),
            glm.sin(rad_yaw) * glm.cos(rad_pitch)
        )
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))
    
    def update_recoil(self, dt):
        # Decae suavemente el retroceso
        if abs(self.recoil_offset) > 0.0001:
            direction = -glm.sign(self.recoil_offset)
            decay = self.recoil_decay * dt * direction
            self.recoil_offset += decay
            if glm.sign(self.recoil_offset) != direction:
                self.recoil_offset = 0.0  # Clamp cuando cruza 0
        else:
            self.recoil_offset = 0.0

    def handle_mouse_motion(self, dx, dy):
        
        if not self.is_dead:
            self.yaw += dx * self.sensitivity
            self.pitch -= dy * self.sensitivity
            self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_vectors()

    def handle_keyboard(self, keys, models):
        
        if self.is_dead: return
        move = glm.vec3(0)

        if keys[pygame.K_w]:
            move += glm.vec3(self.front.x, 0, self.front.z)
        if keys[pygame.K_s]:
            move -= glm.vec3(self.front.x, 0, self.front.z)
        if keys[pygame.K_a]:
            move -= glm.vec3(self.right.x, 0, self.right.z)
        if keys[pygame.K_d]:
            move += glm.vec3(self.right.x, 0, self.right.z)

        move = glm.normalize(move) if glm.length(move) > 0 else move
        move *= self.speed

        # Intento de movimiento inicial
        proposed_position = self.position + glm.vec3(move.x, 0, move.z)
        proposed_obb = self.get_obb(proposed_position)

        # Detectar colisiones con cualquier collider de cada modelo
        colliding_models = [m for m in models if any(proposed_obb.intersects(c) for c in m.colliders)]

        if not colliding_models:
            self.position.x = proposed_position.x
            self.position.z = proposed_position.z
        else:
            # Calcular normal promedio de colisión
            avg_normal = glm.vec3(0)
            for model in colliding_models:
                diff = self.position - model.position
                if glm.length(diff) > 0:
                    avg_normal += glm.normalize(diff)
            avg_normal = glm.normalize(avg_normal)

            # Proyección del movimiento sobre el plano tangente
            projected_move = move - glm.dot(move, avg_normal) * avg_normal

            # Segundo intento de movimiento
            if glm.length(projected_move) > 0.001:
                adjusted_position = self.position + glm.vec3(projected_move.x, 0, projected_move.z)
                adjusted_obb = self.get_obb(adjusted_position)
                if not any(any(adjusted_obb.intersects(c) for c in m.colliders) for m in models):
                    self.position.x = adjusted_position.x
                    self.position.z = adjusted_position.z

        # Salto
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity.y = self.jump_strength
            self.on_ground = False

    
    def get_view_matrix(self, keys, mx, my, models=[]):
        self.handle_keyboard(keys, models)
        self.apply_physics(models)
        self.update_recoil(1.0)
        self.handle_mouse_motion(mx, my)
        
     
        view = glm.lookAt(self.position, self.position + self.front, self.up)

        if self.is_dead:
            rot = glm.mat4(1.0)
            rot = glm.rotate(rot, glm.radians(self.rotation_x), glm.vec3(1, 0, 0))
            rot = glm.rotate(rot, glm.radians(self.rotation_z), glm.vec3(0, 0, 1))
            return rot * view
        else:
            return view
    
    def get_obb(self, custom_position=None):
        center = custom_position if custom_position else self.position
        size = glm.vec3(1.0, 1.8, 1.0)  # higher hitbox

        # Yaw rotation
        yaw_rad = glm.radians(self.yaw)
        rot = glm.rotate(glm.mat4(1.0), yaw_rad, glm.vec3(0, 1, 0))

        axis_x = glm.vec3(rot * glm.vec4(1, 0, 0, 0))
        axis_y = glm.vec3(0, 1, 0)  # sin rotación en Y
        axis_z = glm.vec3(rot * glm.vec4(0, 0, 1, 0))

        return OBB(center, size, [axis_x, axis_y, axis_z])

    def apply_physics(self, models):
        # Aply gravity
        self.velocity.y += self.gravity

        # Calculate new pos
        new_position = self.position + self.velocity

        # OBB with new pos
        new_obb = self.get_obb(new_position)

        # Revisar colisión contra el suelo y objetos
        collided = False
        for model in models:
            if any(new_obb.intersects(collider) for collider in model.colliders):
                collided = True
                break

        if collided:
            if self.velocity.y < 0:  # Solo lo bloquea si está cayendo
                self.velocity.y = 0
                self.on_ground = True
            else:
                self.velocity.y = 0
            return  # No se mueve en Y
        else:
            self.position = new_position
            self.on_ground = False