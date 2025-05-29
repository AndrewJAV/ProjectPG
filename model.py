import os
import numpy as np
from OpenGL.GL import *
from PIL import Image

class Model:
    def __init__(self, obj_path, position=(0, 0, 0), scale=1.0, rotation=(0, 0, 0)):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.materials = {}
        self.current_material = None
        self.textures = {}

        self.position = np.array(position, dtype=np.float32)
        self.scale = scale
        self.rotation = np.array(rotation, dtype=np.float32)

        full_path = os.path.join("models", obj_path)
        self.load_obj(full_path)
        
    def get_aabb(self):
        """Devuelve los extremos del bounding box en coordenadas globales"""
        if not self.vertices:
            return None

        scaled_vertices = np.array(self.vertices) * self.scale
        min_local = np.min(scaled_vertices, axis=0)
        max_local = np.max(scaled_vertices, axis=0)

        min_world = self.position + min_local
        max_world = self.position + max_local

        return min_world, max_world

    

    def load_obj(self, path):
        dir_path = os.path.dirname(path)
        with open(path, 'r') as file:
            for line in file:
                if line.startswith('mtllib'):
                    mtl_file = line.split()[1]
                    self.load_mtl(os.path.join(dir_path, mtl_file))
                elif line.startswith('v '):
                    self.vertices.append(list(map(float, line.split()[1:4])))
                elif line.startswith('vn '):
                    self.normals.append(list(map(float, line.split()[1:4])))
                elif line.startswith('vt '):
                    self.texcoords.append(list(map(float, line.split()[1:3])))
                elif line.startswith('usemtl'):
                    self.current_material = line.split()[1]
                elif line.startswith('f '):
                    face = []
                    for v in line.split()[1:]:
                        vals = v.split('/')
                        v_idx = int(vals[0]) - 1
                        vt_idx = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else None
                        vn_idx = int(vals[2]) - 1 if len(vals) > 2 and vals[2] else None
                        face.append((v_idx, vt_idx, vn_idx))
                    self.faces.append((face, self.current_material))

    def load_mtl(self, path):
        current_material = None
        with open(path, 'r') as file:
            for line in file:
                if line.startswith('newmtl'):
                    current_material = line.split()[1]
                    self.materials[current_material] = {'Kd': [0.8, 0.8, 0.8], 'map_Kd': None}
                elif line.startswith('Kd') and current_material:
                    self.materials[current_material]['Kd'] = list(map(float, line.split()[1:4]))
                elif line.startswith('map_Kd') and current_material:
                    texture_file = line.split()[1]
                    full_path = os.path.join(os.path.dirname(path), texture_file)
                    self.materials[current_material]['map_Kd'] = full_path
                    self.textures[current_material] = self.load_texture(full_path)

    def load_texture(self, file_path):
        image = Image.open(file_path).transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(image, dtype=np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture_id

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.scale, self.scale, self.scale)

        glEnable(GL_TEXTURE_2D)

        last_texture = None

        for face, material_name in self.faces:
            material = self.materials.get(material_name, None)
            if material:
                glColor3f(*material['Kd'])

                # Cambiar textura solo si es diferente
                if material['map_Kd']:
                    tex_id = self.textures[material_name]
                    if tex_id != last_texture:
                        glBindTexture(GL_TEXTURE_2D, tex_id)
                        last_texture = tex_id
                else:
                    if last_texture is not None:
                        glBindTexture(GL_TEXTURE_2D, 0)
                        last_texture = None

            glBegin(GL_TRIANGLES)
            for v_idx, vt_idx, vn_idx in face:
                if vt_idx is not None:
                    glTexCoord2f(*self.texcoords[vt_idx])
                if vn_idx is not None:
                    glNormal3f(*self.normals[vn_idx])
                glVertex3f(*self.vertices[v_idx])
            glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
