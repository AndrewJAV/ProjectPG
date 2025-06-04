import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from model import Model
from camera import Camera
from skybox import Skybox
from weaponview import WeaponView
from axes import draw_axes 
from bullet import Bullet


models = [
    Model("rfloor.obj", position=(0,-3, 0), scale=4.0),
    Model("pistol.obj", position=(1, 0, 0), scale=1.2),
    Model("bullet.obj", position=(2, 0, 0), scale=1.0),
    #Model("shotgun.obj", position=(2, 0, 0), scale=1.2),
    #Model("rifle.obj", position=(3, 0, 0), scale=1.2),
    #Model("GreenDrone.obj", position=(5, 0, 0), scale=1.0),
    #Model("BlueDrone.obj", position=(7, 0, 0), scale=1.2),
    #Model("WhiteDrone.obj", position=(7, 0, 0), scale=1.2),
]
bullets = []

def main(): 
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("UNI RedCode")
    camera = Camera(models=models)
    skybox = Skybox()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)          # Habilita iluminación
    glEnable(GL_LIGHT0)            # Habilita una fuente de luz
    glShadeModel(GL_SMOOTH)        # Sombreado suave
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Color de fondo
    glClearColor(0.52, 0.63, 0.90, 1)

    # Configuración de la proyección
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (800 / 600), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW) 
    clock = pygame.time.Clock()

    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    weapon = WeaponView("rifle.obj", scale=1.0)

    # Propiedades de la luz
    light_pos = [10.0, 5.0, -2.0, 1.0]  # Posición (último valor 1.0 = posicional)
    light_color = [1.0, 1.0, 1.0, 1.0]  # Luz blanca
    light_ambient = [0.2, 0.2, 0.2, 1.0]

    can_shoot = True
    
    while True:
        dt = clock.tick(60) / 1000.0
        camera.handle_inputs(dt)
        
        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0]:  # clic izquierdo
            if can_shoot:
                bullet_position = (
                    camera.position[0] + 0.4,
                    camera.position[1] - 0.3,
                    camera.position[2] - 1.5
                )
                bullet_direction = camera.get_forward_vector()  # o como lo tengas implementado
                bullet_rotation = camera.get_rotation()  # pitch, yaw, roll

                bullet = Bullet("bullet.obj", position=bullet_position,
                                direction=bullet_direction, rotation=bullet_rotation)
                bullets.append(bullet)
                can_shoot = False

        else:
            can_shoot = True


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        camera.apply_view()

        # Establecer luz en cada frame (debe ir después del view)
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

        skybox.draw(camera.position)
        draw_axes()
        
        glColor3f(1.0, 1.0, 1.0)
        for model in models:
            model.draw()
            
        for bullet in bullets:
            bullet.update(dt)
            bullet.draw()
        
        weapon.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()
