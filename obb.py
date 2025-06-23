import glm
import numpy as np
class OBB:
    def __init__(self, center, size, axes):
        self.center = center
        self.size = size
        self.half_size = size * 0.5
        self.axes = axes

    def intersects(self, other):
        EPSILON = 1e-5
        axes = self.axes + other.axes + [
            glm.cross(a, b) for a in self.axes for b in other.axes
        ]

        for axis in axes:
            if glm.length(axis) < EPSILON:
                continue  # Eje degenerado
            axis = glm.normalize(axis)

            def project(obb, axis):
                center_proj = glm.dot(obb.center, axis)
                r = sum(abs(glm.dot(a, axis)) * h for a, h in zip(obb.axes, obb.half_size))
                return (center_proj - r, center_proj + r)

            min1, max1 = project(self, axis)
            min2, max2 = project(other, axis)

            if max1 < min2 or max2 < min1:
                return False  # Separating axis found

        return True  # No separating axis found → collision
    
    def get_corners(self):
        c = self.center
        a = self.axes
        h = glm.vec3(self.half_size)

        corners = []
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                for dz in [-1, 1]:
                    corner = c + dx * a[0] * h.x + dy * a[1] * h.y + dz * a[2] * h.z
                    corners.append(np.array([corner.x, corner.y, corner.z]))
        return corners

        
        