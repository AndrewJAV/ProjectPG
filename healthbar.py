# healthbar_renderer.py
import numpy as np
import glm

# healthbar_renderer.py
import numpy as np
import glm

class HealthBarRenderer:
    def __init__(self, ctx, shader):
        self.ctx = ctx
        self.shader = shader

        # Vértices desde 0 a 1 en X (para alinear a la izquierda)
        health_vertices = np.array([
            [0.0, 0.0],
            [0.0, 0.1],
            [1.0, 0.0],
            [1.0, 0.1],
        ], dtype='f4')

        # Vértices centrados en X (de -0.5 a 0.5) para el fondo
        background_vertices = np.array([
            [-0.5, 0.0],
            [-0.5, 0.1],
            [ 0.5, 0.0],
            [ 0.5, 0.1],
        ], dtype='f4')

        indices = np.array([0, 1, 2, 2, 1, 3], dtype='i4')

        # Barra de vida
        self.vbo_health = ctx.buffer(health_vertices.tobytes())
        self.vao_health = ctx.vertex_array(
            shader, [(self.vbo_health, '2f', 'in_position')],
            ctx.buffer(indices.tobytes())
        )

        # Fondo gris
        self.vbo_background = ctx.buffer(background_vertices.tobytes())
        self.vao_background = ctx.vertex_array(
            shader, [(self.vbo_background, '2f', 'in_position')],
            ctx.buffer(indices.tobytes())
        )

    def draw(self, proj, view, entity, player_position, base_width=0.8, base_height=0.64, color=(0, 1, 0)):
        pos_world = entity.position + glm.vec3(0, 0.5, 0)
        pos_clip = proj * view * glm.vec4(pos_world, 1.0)

        if pos_clip.w <= 0 or not entity.visible:
            return

        ndc = glm.vec2(pos_clip.x / pos_clip.w, pos_clip.y / pos_clip.w)
        distance = glm.length(player_position - entity.position)
        scale = glm.clamp(1.5 / distance, 0.3, 1.0)

        health_ratio = max(0.0, min(1.0, entity.health / entity.max_health))
        scaled_width = base_width * scale
        scaled_height = base_height * scale

        # --- 2. Barra de salud (alineada a la izquierda) ---
        self.shader['offset'].value = (ndc.x - (scaled_width / 2.0), ndc.y)
        self.shader['size'].value = (scaled_width * health_ratio, scaled_height)
        self.shader['color'].value = color
        self.vao_health.render()
        
        # --- 1. Fondo gris (centrado) ---
        self.shader['offset'].value = (ndc.x, ndc.y)
        self.shader['size'].value = (scaled_width, scaled_height)
        self.shader['color'].value = (0.2, 0.2, 0.2)
        self.vao_background.render()

        
