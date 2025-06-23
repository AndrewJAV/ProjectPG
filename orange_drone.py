from drone import Drone
import glm
import random

class BlueDrone(Drone):
    def __init__(self, ctx, program, position, bullet_manager):
        super().__init__(ctx, program, "BlueDrone.obj", position=position, speed=1.0)
        self.bullet_manager = bullet_manager
        self.original_rotation = glm.vec3(self.rotation)
        self.alert_radius = 5.0
        self.player_in_range = False
        self.rotation_speed = 270.0
        self.target_position = None
        self.move_speed = 25.0
        self.moving = False
        self.move_timer = 0.0
        self.move_interval = 0.5  # segundos
        self.bob_timer = 0.0
        self.bob_amplitude = 2.0     # grados máximos de inclinación
        self.bob_frequency = 3.0     # ciclos por segundo
        self.shoot_interval = 1.0  # cada 5 segundos
        self.shoot_timer = 0.0
        self.shoot_spread = 0.12  # leve desviación
        
     
    def update(self, dt, player_position, obstacles): 
        if self.health <= 0 and not self.dying:
            self.start_die_animation()
        
        if self.dying:
            self.update_die_animation(dt, obstacles)
            return
        
        self.colliders = [self.get_obb()]
        direction = player_position - self.position
        distance = glm.length(direction)

        if distance <= self.alert_radius and not self.player_in_range:
            self.player_in_range = True
            self.move_timer = 0.0
            self.choose_random_target()

        if self.player_in_range:
            self.face_player(player_position, dt)
            self.move_towards_target(dt, obstacles)

            self.move_timer += dt
            self.shoot_timer += dt
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0.0
                self.shoot_at_player(player_position)
            
            if self.move_timer >= self.move_interval:
                self.choose_random_target()
                self.move_timer = 0.0

            # Aquí calculamos inclinación según movimiento
            if self.moving and self.target_position:
                movement_dir = glm.normalize(self.target_position - self.position)
                
                # Máxima inclinación en grados
                max_pitch = 15.0  # eje X (adelante/atrás)
                max_roll = 15.0   # eje Z (costados)

                # Inclinar hacia adelante/atrás (pitch, eje X)
                # Invertimos el signo para que avanzar incline hacia adelante (rot X negativa)
                target_pitch = -movement_dir.z * max_pitch

                # Inclinar hacia los lados (roll, eje Z)
                # positivo movement_dir.x => inclinación a la derecha => rot Z negativa
                target_roll = movement_dir.x * max_roll

                # Interpolamos suavemente la rotación en X y Z
                interp_speed = 5.0  # cuánto se suaviza

                self.rotation.x += (target_pitch - self.rotation.x) * dt * interp_speed
                self.rotation.z += (target_roll - self.rotation.z) * dt * interp_speed

            else:
                # Cuando no se mueve, vuelve a rotación neutral en X y Z
                interp_speed = 5.0
                self.rotation.x += (0 - self.rotation.x) * dt * interp_speed
                self.rotation.z += (0 - self.rotation.z) * dt * interp_speed

        else:
            self.smooth_rotate_yaw_to(self.original_rotation.y, dt)
            self.smooth_rotate_pitch_to(self.original_rotation.x, dt)
            # Reset inclinaciones
            interp_speed = 5.0
            self.rotation.x += (0 - self.rotation.x) * dt * interp_speed
            self.rotation.z += (0 - self.rotation.z) * dt * interp_speed
    
    
    def face_player(self, player_position, dt):
        direction = player_position - self.position
        distance = glm.length(direction)

        target_yaw = (glm.degrees(glm.atan(direction.x, direction.z)) + 180.0) % 360.0
        self.smooth_rotate_yaw_to(target_yaw, dt)

        target_pitch = glm.degrees(glm.asin(glm.clamp(direction.y / distance, -1.0, 1.0)))
        self.smooth_rotate_pitch_to(target_pitch, dt)

    def smooth_rotate_yaw_to(self, target_yaw, dt):
        current_yaw = self.rotation.y
        angle_diff = ((target_yaw - current_yaw + 180.0) % 360.0) - 180.0

        max_step = self.rotation_speed * dt
        step = glm.clamp(angle_diff, -max_step, max_step)
        self.rotation.y = (current_yaw + step) % 360.0

    def smooth_rotate_pitch_to(self, target_pitch, dt):
        current_pitch = self.rotation.x
        angle_diff = target_pitch - current_pitch

        max_step = self.rotation_speed * dt
        step = glm.clamp(angle_diff, -max_step, max_step)
        self.rotation.x = current_pitch + step

    def choose_random_target(self):
        # Dirección aleatoria tridimensional (esfera unitaria)
        theta = random.uniform(0, 2 * glm.pi())     # ángulo en XZ
        phi = random.uniform(-glm.pi()/4, glm.pi()/4)  # inclinación vertical controlada
        
        direction = glm.vec3(
            glm.cos(phi) * glm.cos(theta),
            glm.sin(phi),
            glm.cos(phi) * glm.sin(theta)
        )

        self.target_position = self.position + direction * 2.0
        self.moving = True

    def move_towards_target(self, dt, obstacles):
        if not self.moving or self.target_position is None:
            return

        direction = self.target_position - self.position
        distance = glm.length(direction)

        if distance < 0.05:
            self.position = self.target_position
            self.moving = False
            return

        direction = glm.normalize(direction)
        proposed_position = self.position + direction * self.move_speed * dt
        proposed_obb = self.get_obb(proposed_position)

        collision = any(
            obstacle is not self and
            any(proposed_obb.intersects(c) for c in obstacle.colliders)
            for obstacle in obstacles
        )

        if not collision:
            self.position = proposed_position
        else:
            # Si hay colisión, detener el movimiento
            self.moving = False

        
    def shoot_at_player(self, player_position):
        direction = glm.normalize(player_position - self.position)

        # Aplicar una pequeña desviación aleatoria
        spread = glm.vec3(
            random.uniform(-self.shoot_spread, self.shoot_spread),
            random.uniform(-self.shoot_spread, self.shoot_spread),
            random.uniform(-self.shoot_spread, self.shoot_spread)
        )
        direction += spread
        direction = glm.normalize(direction)

        # Llama a tu bullet_manager para disparar
        self.bullet_manager.spawn_enemy_bullet(self, position=self.position, direction=direction)

