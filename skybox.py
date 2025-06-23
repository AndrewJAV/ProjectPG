import glm
import os
import numpy as np
import moderngl
from PIL import Image

class Skybox:
    def __init__(self, ctx, program, folder_path="textures/skybox"):
        self.ctx = ctx
        self.program = program
        self.texture = self.load_cubemap(folder_path)
        self.cube = self.create_cube()

    def load_cubemap(self, folder_path):
        face_files = [
            "right.jpg", "left.jpg", "top.jpg",
            "bottom.jpg", "back.jpg", "front.jpg"
        ]

        images = []
        width = height = None

        for face in face_files:
            path = os.path.join(folder_path, face)
            img = Image.open(path).convert("RGB")
            
            # Verifica o ajusta tamaño
            if width is None:
                width, height = img.size
            else:
                img = img.resize((width, height))

            images.append(np.array(img, dtype=np.uint8))

        # Crear textura cubemap
        texture = self.ctx.texture_cube((width, height), 3)
        for i in range(6):
            texture.write(face=i, data=images[i])

        texture.build_mipmaps()
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        texture.use(location=0)
        return texture

    def create_cube(self):
        # Vértices de un cubo unitario centrado en el origen
        vertices = np.array([
            -1,  1, -1,  -1, -1, -1,   1, -1, -1,   1, -1, -1,   1,  1, -1,  -1,  1, -1,  # back
            -1, -1,  1,  -1, -1, -1,  -1,  1, -1,  -1,  1, -1,  -1,  1,  1,  -1, -1,  1,  # left
             1, -1, -1,   1, -1,  1,   1,  1,  1,   1,  1,  1,   1,  1, -1,   1, -1, -1,  # right
            -1, -1,  1,  -1,  1,  1,   1,  1,  1,   1,  1,  1,   1, -1,  1,  -1, -1,  1,  # front
            -1,  1, -1,   1,  1, -1,   1,  1,  1,   1,  1,  1,  -1,  1,  1,  -1,  1, -1,  # top
            -1, -1, -1,  -1, -1,  1,   1, -1, -1,   1, -1, -1,  -1, -1,  1,   1, -1,  1   # bottom
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        vao = self.ctx.simple_vertex_array(self.program, vbo, 'in_position')
        return vao

    def draw(self, proj, view):
        # Eliminar la traslación para que la skybox siga a la cámara
        view_no_translation = glm.mat4(glm.mat3(view))

        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.depth_func = '<='  # O `LEQUAL` para evitar errores de profundidad en la skybox

        self.texture.use(location=0)
        self.program['projection'].write(proj.to_bytes())
        self.program['view'].write(view_no_translation.to_bytes())
        self.cube.render(moderngl.TRIANGLES)

        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.depth_func = '<'  # Restaurar profundidad para otros objetos

