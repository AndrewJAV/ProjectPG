from entity import Entity
from enum import Enum, auto
import glm
import time
import random

class DroneState(Enum):
    IDLE = auto()
    CHASE = auto()
    FLEE = auto()
    SUPPORT = auto()
    HUNT = auto()
    EXPLODE = auto()
    ATTACK = auto()
    
class Drone(Entity):
    def __init__(self, ctx, program, model_path, position=(0, 0, 0), speed=1.0):
        super().__init__(ctx, program, model_path, position=position, speed=speed)
        
        # Atributos comunes
        self.health = 100
        self.max_health = 100
        self.attack_range = 5.0
        self.alert_radius = 8.0
        self.attack_cooldown = 1.5  # segundos
        self.last_attack_time = -999.0
        
        self.rotation_speed = 180.0  # grados por segundo
        self.state = DroneState.IDLE
        self.target_position = None
        self.facing_target = None  # Para rotación suave hacia jugador u objetivo
        
        self.dying = False
        self.death_velocity = glm.vec3(
            random.uniform(-1.0, 1.0), 0.0, random.uniform(-1.0, 1.0)
        )  # velocidad aleatoria horizontal
        self.fall_speed = 0.0
        self.rotation_speed_die = glm.vec3(
            random.uniform(360, 720), random.uniform(360, 720), random.uniform(360, 720)
        )  # r
        
        self.death_timer = 0.0 
        self.visible = True 

        
    def start_die_animation(self):
        self.dying = True
        self.fall_speed = 0.0
        self.death_velocity = glm.vec3(
            random.uniform(-1.0, 1.0), 0.0, random.uniform(-1.0, 1.0)
        )
        self.rotation_speed_die = glm.vec3(
            random.uniform(360, 720),
            random.uniform(360, 720),
            random.uniform(0, 10)
        )
        
    def update_die_animation(self, dt, obstacles):
        if not self.dying:
            return

        self.death_timer += dt  # ← llevamos tiempo desde que empezó a morir

        # Rotación acelerada
        self.rotation += self.rotation_speed_die * dt

        # Aplicar gravedad acumulativa
        self.fall_speed += 10.8 * dt  # gravedad

        # Calcular nueva posición propuesta
        proposed_position = glm.vec3(self.position)
        proposed_position += self.death_velocity * dt
        proposed_position.y -= self.fall_speed * dt

        # Generar OBB propuesto en nueva posición
        proposed_obb = self.get_obb(proposed_position)

        # Detectar colisión con obstáculos
        collision = any(
            obstacle is not self and
            any(proposed_obb.intersects(c) for c in obstacle.colliders)
            for obstacle in obstacles
        )

        if not collision:
            self.position = proposed_position
        else:
            # Detener caída si colisiona (puedes ajustar esto)
            self.death_velocity = glm.vec3(0)
            self.fall_speed = 0

            # Restaurar rotación neutral (solo yaw mantiene orientación)
            self.rotation.x = 0
            self.rotation.z = 0
            self.visible = False

            # Hundirse mitad de su altura para verse asentado
            #self.position.y -= self.height * 0.5

            # Desactivar colisiones
            self.colliders = []

        # Desaparecer tras 2 segundos de animación
        if self.death_timer >= 1.0:
            self.visible = False  # debes verificar self.visible en .draw()

