
def load_shader(path):
    with open(path, 'r') as f:
        return f.read()
    
def LoadShaderProgram(ctx, name):
    shader = ctx.program(
        vertex_shader=load_shader(f"shaders/{name}/shader.vert"),
        fragment_shader=load_shader(f"shaders/{name}/shader.frag"),
    )
    
    return shader