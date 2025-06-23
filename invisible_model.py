from model import Model
class InvisibleModel(Model):
    def __init__(self, ctx, program, model_path, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1), size=1, name=None):
        super().__init__(ctx, program, model_path, position, rotation, scale, size, name)
        
        def draw(self):
            pass