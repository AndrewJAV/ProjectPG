import glfw
import moderngl
import numpy as np
from PIL import Image
import time
import subprocess
from PIL import ImageDraw, ImageFont

# Window configuration
WIDTH, HEIGHT = 800, 600

colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # Rojo, Verde, Azul


# Initialize GLFW and create window
if not glfw.init():
    raise Exception("GLFW couldn't be initialized")

window = glfw.create_window(WIDTH, HEIGHT, "UNI: RED CODE", None, None)
if not window:
    glfw.terminate()
    raise Exception("Window could not be created")

glfw.make_context_current(window)
ctx = moderngl.create_context()
ctx.viewport = (0, 0, WIDTH, HEIGHT)

# Load texture
def load_texture(ruta):
    img = Image.open(ruta).convert("RGB").transpose(Image.FLIP_TOP_BOTTOM)
    return ctx.texture(img.size, 3, img.tobytes())

image_paths = [
    "Imagenes/UNI.jpg",
    "Imagenes/Tomas Borges.jpg",
    "Imagenes/monetaria.jpg",
]
textures = [load_texture(ruta) for ruta in image_paths]

current_index = 0
next_index = 1
fade_start_time = time.time()
fade_duration = 2.5

# Quad creation function (unaltered aspect ratio)
def create_quad(x1, y1, x2, y2):
    return np.array([
        x1, y1, 0.0, 0.0,  # bottom-left
        x2, y1, 1.0, 0.0,  # bottom-right
        x1, y2, 0.0, 1.0,  # top-left
        x2, y2, 1.0, 1.0,  # top-right
    ], dtype='f4')

def create_quad2(x1, y1, x2, y2):
    return np.array([
        x1, y1,
        x2, y1,
        x1, y2,
        x2, y2,
    ], dtype='f4')

# --- Background shader setup ---
quad_background = ctx.buffer(create_quad(-1, -1, 1, 1).tobytes())
program_background = ctx.program(
    vertex_shader="""
    #version 330
    in vec2 in_vert;
    in vec2 in_tex;
    out vec2 v_tex;
    void main() {
        v_tex = in_tex;
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
    """,
    fragment_shader="""
    #version 330
    uniform sampler2D tex1;
    uniform sampler2D tex2;
    uniform float fade;
    in vec2 v_tex;
    out vec4 fragColor;

    vec4 blur(sampler2D tex, vec2 uv) {
        float offset = 1.0 / 300.0;
        vec4 col = texture(tex, uv) * 0.4;
        col += texture(tex, uv + vec2(-offset, 0.0)) * 0.15;
        col += texture(tex, uv + vec2(offset, 0.0)) * 0.15;
        col += texture(tex, uv + vec2(0.0, -offset)) * 0.15;
        col += texture(tex, uv + vec2(0.0, offset)) * 0.15;
        return col;
    }

    void main() {
        vec4 col1 = blur(tex1, v_tex);
        vec4 col2 = blur(tex2, v_tex);
        fragColor = mix(col1, col2, fade);
    }
    """
)
vao_background = ctx.simple_vertex_array(program_background, quad_background, 'in_vert', 'in_tex')
program_background['tex1'] = 0
program_background['tex2'] = 1

def draw_background():
    ctx.clear()
    vao_background.render(moderngl.TRIANGLE_STRIP)

# --- Button program and creation ---
button_program = ctx.program(
    vertex_shader="""
    #version 330
    in vec2 in_vert;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
    """,
    fragment_shader="""
    #version 330
    uniform vec3 color;
    out vec4 fragColor;
    void main() {
        fragColor = vec4(color, 1.0);
    }
    """
)

def create_buttons():
    button_vaos = []
    button_height = 0.2
    button_left = -0.9
    button_right = -0.6
    spacing = 0.5
    start_top = 0.7
    for i in range(3):
        top = start_top - i * spacing
        bottom = top - button_height
        quad = create_quad2(button_left, bottom, button_right, top)
        vbo = ctx.buffer(quad.tobytes())
        vao = ctx.simple_vertex_array(button_program, vbo, 'in_vert')
        button_vaos.append(vao)
    return button_vaos

button_vaos = create_buttons()

# Create right panel
panel_quad = create_quad2(0.5, -0.5, 0.95, 0.5)
panel_vbo = ctx.buffer(panel_quad.tobytes())
panel_vao = ctx.simple_vertex_array(button_program, panel_vbo, 'in_vert')

panel_visible = [False, False, False]

# Click detection for buttons
#def detect_click(x, y):
 #   x_ndc = (x / WIDTH) * 2 - 1
  #  y_ndc = -((y / HEIGHT) * 2 - 1)
   # for i in range(3):
    #    left, right = -0.95, -0.6
     #   top = 0.7 - i * 0.5
      #  bottom = top - 0.2
       # if left <= x_ndc <= right and bottom <= y_ndc <= top:
            # Close all panels
         #   for j in range(3):
        #        panel_visible[j] = False
            # Open only the selected panel
         #   panel_visible[i] = True
          #break
def create_text_texture(text, size=(256, 64), font_size=24):
    img = Image.new('RGB', size, color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    draw.text((10, 10), text, font=font, fill=(255, 255, 255))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return ctx.texture(size, 3, img.tobytes())
button_labels = ["Collisions and Camera", "Skybox", "Instructions"]
button_textures = [create_text_texture(label) for label in button_labels]


# Draw buttons and labels
for i, button in enumerate(button_vaos):
    button_program['color'].value = colors[i]
    button.render(moderngl.TRIANGLE_STRIP)

    # Draw text on button (you can adjust size/position)
    button_textures[i].use(0)
    ctx.screen.use()
    #ctx.copy_framebuffer(ctx.screen)
def detect_click(x, y):
    x_ndc = (x / WIDTH) * 2 - 1
    y_ndc = -((y / HEIGHT) * 2 - 1)
    for i in range(3):
        left, right = -0.95, -0.6
        top = 0.7 - i * 0.5
        bottom = top - 0.2
        if left <= x_ndc <= right and bottom <= y_ndc <= top:
            if i == 0:
                glfw.terminate()
                subprocess.Popen(["python", "modules/collisions_camera.py"])
                return
            elif i == 1:
                glfw.terminate()
                subprocess.Popen(["python", "modules/skybox.py"])
                return
            elif i == 2:
                for j in range(3):
                    panel_visible[j] = False
                panel_visible[i] = True
                return
instruction_text = """
Use WASD to move.
Mouse to look around.
Press ESC to quit.
Complete the objectives.
"""
instruction_texture = create_text_texture(instruction_text, size=(400, 300), font_size=16)


def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        xpos, ypos = glfw.get_cursor_pos(window)
        detect_click(xpos, ypos)

glfw.set_mouse_button_callback(window, mouse_button_callback)

# Colors for buttons and panels
colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

# Main loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    now = time.time()
    fade = min((now - fade_start_time) / fade_duration, 1.0)
    program_background['fade'].value = fade

    textures[current_index].use(0)
    textures[next_index].use(1)

    # Draw background
    draw_background()

    # Draw buttons
    for i, button in enumerate(button_vaos):
        button_program['color'].value = colors[i]
        button.render(moderngl.TRIANGLE_STRIP)

    # Draw panels if visible
    #for i in range(3):
     #   if panel_visible[i]:
      #      button_program['color'].value = colors[i]
       #     panel_vao.render(moderngl.TRIANGLE_STRIP)
    # Draw visible panels
    for i in range(3):
        if panel_visible[i]:
            button_program['color'].value = colors[i]
            panel_vao.render(moderngl.TRIANGLE_STRIP)
            if i == 2:
                instruction_texture.use(0)
                ctx.copy_framebuffer(ctx.screen)


    glfw.swap_buffers(window)

    if fade >= 1.0:
        current_index = next_index
        next_index = (current_index + 1) % len(textures)
        fade_start_time = now

glfw.terminate()
