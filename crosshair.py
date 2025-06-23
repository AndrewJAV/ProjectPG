import moderngl
import numpy as np

class Crosshair:
    def __init__(self, ctx, program):
        self.program = program

        # 2 líneas que cruzan el centro (en coordenadas NDC)
        size = 0.05  # Tamaño de la cruz
        vertices = np.array([
            -size*0.8,  0.0,
             size*0.8,  0.0,
             0.0,  -size,
             0.0,   size
        ], dtype='f4')

        vbo = ctx.buffer(vertices)
        self.vao = ctx.simple_vertex_array(program, vbo, 'in_position')

    def draw(self):
        self.vao.render(mode=moderngl.LINES)
