import glm

class Light():
    def __init__(self, position, color=(1.0, 1.0, 1.0), 
                 ambient_strength=0.2, diffuse_strength=0.9, 
                 specular_strength=0.5):
        
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        self.ambient_strength = ambient_strength
        self.diffuse_strength = diffuse_strength
        self.specular_strength = specular_strength
    
    @staticmethod
    def insert_lights(shader, lights, camera_position):
        
        shader['num_lights'].value = len(lights)
        for i, light in enumerate(lights):
            shader[f'lights[{i}].position'].value = tuple(light.position)
            shader[f'lights[{i}].color'].value = tuple(light.color)
            shader[f'lights[{i}].ambient_strength'].value = light.ambient_strength
            shader[f'lights[{i}].diffuse_strength'].value = light.diffuse_strength
            shader[f'lights[{i}].specular_strength'].value = light.specular_strength
        
        shader['view_position'].value = tuple(camera_position)
        