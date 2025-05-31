import os
from OpenGL.GL import *
from PIL import Image
import numpy as np

class Skybox:
    def __init__(self, folder_path="textures/skybox"):
        self.folder_path = folder_path
        self.texture_id = glGenTextures(1)
        self.load_cubemap()

    def load_cubemap(self):
        face_files = [
            "right.jpg", "left.jpg", "top.jpg",
            "bottom.jpg", "back.jpg", "front.jpg"
        ]
        targets = [
            GL_TEXTURE_CUBE_MAP_POSITIVE_X, GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y, GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z, GL_TEXTURE_CUBE_MAP_NEGATIVE_Z
        ]

        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)
        for i in range(6):
            path = os.path.join(self.folder_path, face_files[i])
            image = Image.open(path).convert("RGB")
            img_data = np.array(image, dtype=np.uint8)
            glTexImage2D(targets[i], 0, GL_RGB, image.width, image.height, 0,
                         GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def draw(self, camera_position):
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        size = 50.0  # Tamaño grande para alejar las paredes

        glPushMatrix()
        glDepthMask(GL_FALSE)  # Desactiva la escritura en el z-buffer
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_CUBE_MAP)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)

        glTranslatef(*camera_position)

        glBegin(GL_QUADS)
        # +X
        glTexCoord3f(1, -1, -1); glVertex3f(size, -size, -size)
        glTexCoord3f(1, -1,  1); glVertex3f(size, -size, size)
        glTexCoord3f(1,  1,  1); glVertex3f(size, size, size)
        glTexCoord3f(1,  1, -1); glVertex3f(size, size, -size)
        # -X
        glTexCoord3f(-1, -1,  1); glVertex3f(-size, -size, size)
        glTexCoord3f(-1, -1, -1); glVertex3f(-size, -size, -size)
        glTexCoord3f(-1,  1, -1); glVertex3f(-size, size, -size)
        glTexCoord3f(-1,  1,  1); glVertex3f(-size, size, size)
        # +Y
        glTexCoord3f(-1, 1, -1); glVertex3f(-size, size, -size)
        glTexCoord3f(1, 1, -1);  glVertex3f(size, size, -size)
        glTexCoord3f(1, 1, 1);   glVertex3f(size, size, size)
        glTexCoord3f(-1, 1, 1);  glVertex3f(-size, size, size)
        # -Y
        glTexCoord3f(-1, -1, 1); glVertex3f(-size, -size, size)
        glTexCoord3f(1, -1, 1);  glVertex3f(size, -size, size)
        glTexCoord3f(1, -1, -1); glVertex3f(size, -size, -size)
        glTexCoord3f(-1, -1, -1);glVertex3f(-size, -size, -size)
        # -Z
        glTexCoord3f(1, -1, -1); glVertex3f(size, -size, -size)
        glTexCoord3f(1, 1, -1);  glVertex3f(size, size, -size)
        glTexCoord3f(-1, 1, -1); glVertex3f(-size, size, -size)
        glTexCoord3f(-1, -1, -1);glVertex3f(-size, -size, -size)
        # +Z
        glTexCoord3f(-1, -1, 1); glVertex3f(-size, -size, size)
        glTexCoord3f(-1, 1, 1);  glVertex3f(-size, size, size)
        glTexCoord3f(1, 1, 1);   glVertex3f(size, size, size)
        glTexCoord3f(1, -1, 1);  glVertex3f(size, -size, size)
        
        glEnd()

        glDisable(GL_TEXTURE_CUBE_MAP)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)    # Restaurar para los modelos
        glPopMatrix()
        glPopAttrib()
