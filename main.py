import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from model import Model
from camera import Camera
from axes import draw_axes

models = [
    Model("rfloor.obj", position=(0,-3, 0), scale=4.0),
    Model("pistol.obj", position=(1, 0, 0), scale=1.2),
    Model("shotgun.obj", position=(2, 0, 0), scale=1.2),
    Model("rifle.obj", position=(3, 0, 0), scale=1.2),
]

def main(): 
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("UNI RedCode")
    camera = Camera(models=models)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glClearColor(0.2, 0.2, 0.2, 1)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (800 / 600), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW) 
    clock = pygame.time.Clock()

    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)

    while True:
        dt = clock.tick(60) / 1000.0
        camera.handle_inputs(dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        camera.apply_view()
        draw_axes()
        for model in models:
            model.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()
