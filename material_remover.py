import bpy

# Paso 1: Quitar materiales de todos los objetos tipo MESH
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.data.materials.clear()

# Paso 2: Eliminar todos los materiales del archivo
for material in bpy.data.materials:
    bpy.data.materials.remove(material, do_unlink=True)

print("✔ Todos los materiales han sido eliminados. Solo queda la geometría.")
