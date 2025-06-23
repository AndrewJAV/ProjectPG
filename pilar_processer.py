import numpy as np
from sklearn.decomposition import PCA

def load_obj(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    objects = {}
    current_object = None

    for line in lines:
        if line.startswith('o '):
            print(f"Pilar")
            current_object = line.strip().split(' ', 1)[1]
            objects[current_object] = []
        elif line.startswith('v ') and current_object is not None:
            parts = list(map(float, line.strip().split()[1:]))
            objects[current_object].append(parts)

    return objects

def compute_obb(vertices):
    points = np.array(vertices)
    pca = PCA(n_components=3)
    pca.fit(points)

    center = np.mean(points, axis=0)
    axes = pca.components_
    projected = (points - center) @ axes.T

    min_bounds = projected.min(axis=0)
    max_bounds = projected.max(axis=0)

    corners = []
    for dx in [0, 1]:
        for dy in [0, 1]:
            for dz in [0, 1]:
                corner = min_bounds + [
                    dx * (max_bounds[0] - min_bounds[0]),
                    dy * (max_bounds[1] - min_bounds[1]),
                    dz * (max_bounds[2] - min_bounds[2])
                ]
                world_corner = center + axes.T @ corner
                corners.append(world_corner.tolist())
    return corners

def save_obj(objects, filepath):
    with open(filepath, 'w') as f:
        vertex_counter = 1
        for name, verts in objects.items():
            f.write(f'o {name}\n')
            for v in verts:
                f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')

            # Crear caras del cubo (12 triángulos)
            faces = [
                (0,1,3), (0,3,2),
                (4,6,7), (4,7,5),
                (0,2,6), (0,6,4),
                (1,5,7), (1,7,3),
                (0,4,5), (0,5,1),
                (2,3,7), (2,7,6)
            ]
            for a, b, c in faces:
                f.write(f'f {a + vertex_counter} {b + vertex_counter} {c + vertex_counter}\n')
            vertex_counter += 8

def simplify_obj(input_path, output_path):
    obj_data = load_obj(input_path)
    simplified = {}
    for name, verts in obj_data.items():
        if len(verts) >= 3:
            obb_corners = compute_obb(verts)
            simplified[name] = obb_corners
    save_obj(simplified, output_path)

# === EJECUCIÓN ===
simplify_obj('models/pilars.obj', 'pilars_simplified.obj')
