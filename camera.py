import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
import math



def aabb_intersect(a_min, a_max, b_min, b_max):
    return all(a_min[i] <= b_max[i] and a_max[i] >= b_min[i] for i in range(3))

def check_camera_collision(camera_aabb, model_aabb, padding=0.0):
    cam_min, cam_max = camera_aabb
    mod_min, mod_max = model_aabb
    mod_min -= padding
    mod_max += padding
    return aabb_intersect(cam_min, cam_max, mod_min, mod_max)

def normalize(v):
    length = math.sqrt(sum(i**2 for i in v))
    return [i/length for i in v] if length > 0 else [0, 0, 0]

class Camera:
    def __init__(self, position=(0.0, 0.0, 6.0), sensitivity=0.2, speed=5.0, models=[]):
        self.position = list(position)
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.sensitivity = sensitivity
        self.speed = speed
        self.mouse_locked = False
        self.models = models  # 🔥 se guarda la referencia a los modelos    
        self.vertical_velocity = 0.0
        self.gravity = -9.8  # metros/segundo²
        self.jump_strength = 5.0
        self.is_on_ground = False

        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        
    def get_rotation(self):
        return (self.pitch, self.yaw, self.roll)

    def get_direction(self):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        return normalize([
            math.cos(pitch_rad) * math.sin(yaw_rad),
            math.sin(pitch_rad),
            -math.cos(pitch_rad) * math.cos(yaw_rad)
        ])

    def get_right(self):
        yaw_rad = math.radians(self.yaw)
        return normalize([
            math.sin(yaw_rad - math.pi/2),
            0,
            -math.cos(yaw_rad - math.pi/2)
        ])

    def get_up(self, direction, right):
        return [
            right[1]*direction[2] - right[2]*direction[1],
            right[2]*direction[0] - right[0]*direction[2],
            right[0]*direction[1] - right[1]*direction[0]
        ]

    def can_move_to(self, new_pos):
        # Simula mover la cámara a la nueva posición, y calcula su AABB en esa posición
        old_pos = self.position
        self.position = new_pos
        camera_aabb = self.get_aabb()
        self.position = old_pos  # Restaura posición real

        for model in self.models:
            aabb = model.get_aabb()
            if aabb and check_camera_collision(camera_aabb, aabb):
                return False
        return True

    def handle_inputs(self, dt):
        move = self.speed * dt
        right = self.get_right()
        full_direction = self.get_direction()
        direction = [full_direction[0], 0.0, full_direction[2]]  # solo XZ
        direction = normalize(direction)
        
        up = self.get_up(direction, right)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.mouse_locked = False
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and not self.mouse_locked:
                self.mouse_locked = True
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
            elif event.type == MOUSEMOTION and self.mouse_locked:
                dx, dy = event.rel
                self.yaw += dx * self.sensitivity
                self.pitch -= dy * self.sensitivity
                self.pitch = max(-89, min(89, self.pitch))

        keys = pygame.key.get_pressed()

        def try_move(offset):
            new_pos = [self.position[i] + offset[i] for i in range(3)]
            if self.can_move_to(new_pos):
                self.position = new_pos

        if keys[K_w]:
            try_move([direction[i] * move for i in range(3)])
        if keys[K_s]:
            try_move([-direction[i] * move for i in range(3)])
        if keys[K_a]:
            try_move([right[i] * move for i in range(3)])
        if keys[K_d]:
            try_move([-right[i] * move for i in range(3)])
        if keys[K_LCTRL] or keys[K_RCTRL]:
            try_move([0, -move, 0])
            
        # Lógica de salto
        if keys[K_SPACE] and self.is_on_ground:
            self.vertical_velocity = self.jump_strength
            self.is_on_ground = False

        # Siempre aplicar gravedad al final del frame
        self.apply_gravity(dt)

    
    def apply_view(self):
        direction = self.get_direction()
        target = [self.position[i] + direction[i] for i in range(3)]
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            target[0], target[1], target[2],
            0.0, 1.0, 0.0
        )

    def get_aabb(self):
        # Define un paralelepípedo vertical, más alto que ancho/profundo.
        half_size = [0.25, 2.0, 0.25]  # ancho (X), alto (Y), profundidad (Z)
        min_corner = [self.position[i] - half_size[i] for i in range(3)]
        max_corner = [self.position[i] + half_size[i] for i in range(3)]
        return (np.array(min_corner), np.array(max_corner))

    def apply_gravity(self, dt):
        # Aplicar gravedad y colisiones verticales
        self.vertical_velocity += self.gravity * dt
        vertical_move = self.vertical_velocity * dt
        new_pos = self.position.copy()
        new_pos[1] += vertical_move

        if self.can_move_to(new_pos):
            self.position[1] = new_pos[1]
            self.is_on_ground = False
        else:
            # Detecta colisión con el suelo, detiene caída
            self.vertical_velocity = 0.0
            self.is_on_ground = True

    def get_forward_vector(self):
        # Usando yaw y pitch para calcular la dirección frontal
        from math import radians, cos, sin
        yaw_rad = radians(self.yaw)
        pitch_rad = radians(self.pitch)

        x = cos(pitch_rad) * sin(yaw_rad)
        y = sin(pitch_rad)
        z = -cos(pitch_rad) * cos(yaw_rad)

        return (x, y, z)
