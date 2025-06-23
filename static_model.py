import trimesh
import glm, pyrr
import numpy as np
from model import Model
from obb import OBB

from trimesh import Trimesh

class StaticModel(Model):
    def intersects(self, obb):
        # Extraer vértices del OBB
        c = obb.center
        a = obb.axes
        h = glm.vec3(obb.half_size)
        corners = [
            c + dx * a[0] * h.x + dy * a[1] * h.y + dz * a[2] * h.z
            for dx in [-1, 1]
            for dy in [-1, 1]
            for dz in [-1, 1]
        ]
        points = np.array([[p.x, p.y, p.z] for p in corners], dtype='f4')

        for tri in self.trimesh_colliders:
            if tri.contains(points).any():
                return True
        return False
