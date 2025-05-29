class AABB:
    def __init__(self, min_corner, max_corner):
        self.min = min_corner  # [x_min, y_min, z_min]
        self.max = max_corner  # [x_max, y_max, z_max]

    def intersects(self, point):
        return (self.min[0] <= point[0] <= self.max[0] and
                self.min[1] <= point[1] <= self.max[1] and
                self.min[2] <= point[2] <= self.max[2])
