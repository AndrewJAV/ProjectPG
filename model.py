import moderngl
import numpy as np
import glm
import logging, trimesh
from obb import OBB
from aabb import AABB
from pywavefront import Wavefront
logging.getLogger('pywavefront').setLevel(logging.ERROR)

class Model:
    def __init__(self, ctx, program, model_path, position=(0,0,0), rotation=(0,0,0), scale=(1.0,1.0,1.0), size=1.0, name="model", visible=True):
        self.ctx = ctx
        self.position = glm.vec3(position[0], position[1], position[2])
        self.rotation = glm.vec3(rotation[0], rotation[1], rotation[2]) 
        self.scale = glm.vec3(scale[0], scale[1], scale [2])
        self.visible = visible
        self.name = name
        
        if size != 1.0:
            self.scale = glm.vec3(size, size, size)
        
        path = f"models/{model_path}"
        self.load_model(path, program)
        
    def __str__(self):
        return self.name

    def compute_aabb(self, vertices_np):
        reshaped = vertices_np.reshape(-1, 3)
        min_corner = reshaped.min(axis=0)
        max_corner = reshaped.max(axis=0)
        self.aabb = AABB(min_corner, max_corner)
    
    def get_obb(self, custom_position=None):
        # Centro y tamaño local del modelo (basado en AABB)
        local_center = (self.aabb.min + self.aabb.max) * 0.5
        size = (self.aabb.max - self.aabb.min) * self.scale  # Escala afecta tamaño

        # Base position: posición actual o personalizada
        base_position = custom_position if custom_position else self.position

        # Matriz de transformación total
        model_mat = glm.mat4(1.0)
        model_mat = glm.translate(model_mat, base_position)
        model_mat = glm.rotate(model_mat, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        model_mat = glm.rotate(model_mat, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        model_mat = glm.rotate(model_mat, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        model_mat = glm.scale(model_mat, self.scale)

        # Centro en espacio global
        rotated_center = glm.vec3(model_mat * glm.vec4(local_center, 1.0))

        # Ejes orientados
        axis_x = glm.vec3(model_mat * glm.vec4(1, 0, 0, 0))
        axis_y = glm.vec3(model_mat * glm.vec4(0, 1, 0, 0))
        axis_z = glm.vec3(model_mat * glm.vec4(0, 0, 1, 0))

        return OBB(rotated_center, size, [axis_x, axis_y, axis_z])


    def load_model(self, path, program):
        self.colliders = []
        scene = Wavefront(path, collect_faces=True, parse=True)
        vertices = []
        normals = []
        colors = []

        for name, mesh in scene.meshes.items():
            mat_color = (1.0, 1.0, 1.0)
            if mesh.materials:
                material = mesh.materials[0]
                if hasattr(material, 'diffuse'):
                    mat_color = material.diffuse[:3]

            mesh_vertices = []

            for face in mesh.faces:
                v0 = glm.vec3(scene.vertices[face[0]][:3])
                v1 = glm.vec3(scene.vertices[face[1]][:3])
                v2 = glm.vec3(scene.vertices[face[2]][:3])

                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = glm.normalize(glm.cross(edge1, edge2))

                for vertex_i in face:
                    vertex = scene.vertices[vertex_i]
                    vertices.extend(vertex[:3])
                    normals.extend(normal)
                    colors.extend(mat_color)
                    mesh_vertices.append(vertex[:3])

            # Si el nombre del mesh es collider, lo registramos como OBB separado
            if name.lower().startswith("collision_") and mesh_vertices:
                mesh_np = np.array(mesh_vertices, dtype='f4').reshape(-1, 3)
                min_corner = mesh_np.min(axis=0)
                max_corner = mesh_np.max(axis=0)
                local_center = (min_corner + max_corner) * 0.5
                
                size = max_corner - min_corner

                # Aplicar grosor mínimo a planos
                min_thickness = 0.2
                for i in range(3):
                    if size[i] < min_thickness:
                        size[i] = min_thickness

                # Aplicar la escala del modelo
                size *= self.scale

                # Rotación total del modelo
                rot_x = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
                rot_y = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
                rot_z = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
                rot = rot_z * rot_y * rot_x

                axis_x = glm.vec3(rot * glm.vec4(1, 0, 0, 0))
                axis_y = glm.vec3(rot * glm.vec4(0, 1, 0, 0))
                axis_z = glm.vec3(rot * glm.vec4(0, 0, 1, 0))

                rotated_center = glm.vec3(rot * glm.vec4(local_center * self.scale, 1.0))
                world_center = self.position + rotated_center

                obb = OBB(world_center, size, [axis_x, axis_y, axis_z])
                self.colliders.append(obb)
                
        
            

        vertices_np = np.array(vertices, dtype='f4')
        normals_np = np.array(normals, dtype='f4')
        colors_np = np.array(colors, dtype='f4')

        data = np.hstack([
            vertices_np.reshape(-1, 3),
            normals_np.reshape(-1, 3),
            colors_np.reshape(-1, 3)
        ]).astype('f4')

        vbo = self.ctx.buffer(data.tobytes())
        self.vao = self.ctx.vertex_array(
            program,
            [(vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')]
        )
        self.vertex_count = len(vertices) // 3
        self.compute_aabb(vertices_np)
        
        if self.colliders == []:
            self.colliders = [self.get_obb()]

    
    def draw(self, program, proj, view, camera_position):
        
        if not self.visible: return
        
        model_mat = glm.mat4(1.0)
        model_mat = glm.translate(model_mat, self.position)
        model_mat = glm.rotate(model_mat, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        model_mat = glm.rotate(model_mat, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        model_mat = glm.rotate(model_mat, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        model_mat = glm.scale(model_mat, self.scale)

        program['model'].write(model_mat.to_bytes())
        program['view'].write(view.to_bytes())
        program['proj'].write(proj.to_bytes())
        program['view_position'].write(camera_position.to_bytes())  # Solo esto es necesario
        
        self.vao.render()
        
    def draw_obb(self, shader, proj, view):
        obbs_to_draw = self.colliders if self.colliders else [self.get_obb()]

        mvp = proj * view
        shader['mvp'].write(mvp.to_bytes())

        for obb in obbs_to_draw:
            c = obb.center
            a = obb.axes
            h = glm.vec3(obb.half_size)


            corners = []
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    for dz in [-1, 1]:
                        corner = c + dx * a[0] * h.x + dy * a[1] * h.y + dz * a[2] * h.z
                        corners.append([corner.x, corner.y, corner.z])

            corners = np.array(corners, dtype='f4')

            edges = [
                0,1, 1,3, 3,2, 2,0,  # base
                4,5, 5,7, 7,6, 6,4,  # top
                0,4, 1,5, 2,6, 3,7   # verticales
            ]

            edge_vertices = corners[edges]
            vbo = self.ctx.buffer(edge_vertices.astype('f4').tobytes())
            vao = self.ctx.vertex_array(shader, [(vbo, '3f', 'in_position')])
            vao.render(mode=moderngl.LINES)
            
    def remove_colliders(self):
        self.colliders = []
        if hasattr(self, 'aabb'):
            del self.aabb

        