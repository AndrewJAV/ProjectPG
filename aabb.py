import glm

class AABB:
    def __init__(self, min_corner, max_corner):
        self.min = glm.vec3(min_corner)
        self.max = glm.vec3(max_corner)

    @classmethod
    def from_center_half_size(cls, center, half_size):
        min_corner = center - half_size
        max_corner = center + half_size
        return cls(min_corner, max_corner)

    def intersects(self, other):
        return (
            self.min.x <= other.max.x and self.max.x >= other.min.x and
            self.min.y <= other.max.y and self.max.y >= other.min.y and
            self.min.z <= other.max.z and self.max.z >= other.min.z
        )

    def __repr__(self):
        return f"AABB(min={self.min}, max={self.max})"
