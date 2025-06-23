import glm
import pygame
import moderngl
import numpy as np
from light import Light
from model import Model
from rifle import Rifle
from camera import Camera
from skybox import Skybox
from weapon import Weapon
from player import Player
from pistol import Pistol
from shotgun import Shotgun
from crosshair import Crosshair
from blue_drone import BlueDrone
from green_drone import GreenDrone
from orange_drone import OrangeDrone
from static_model import StaticModel
from shader import LoadShaderProgram
from healthbar import HealthBarRenderer
from invisible_model import InvisibleModel
from bullet_manager import BulletManager
from pygame.locals import DOUBLEBUF, OPENGL
from trimesh.collision import CollisionManager

def main():
    pygame.init()
    pygame.display.set_mode((1200, 900), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Event RedCode")
    pygame.event.set_grab(True)   # Hide and blocks cursor
    pygame.mouse.set_visible(False) 
    
    ctx = moderngl.create_context()
    ctx.enable(moderngl.DEPTH_TEST)
    
    shader = LoadShaderProgram(ctx, "polylight")
    crosshair_shader = LoadShaderProgram(ctx, "crosshair")
    healthbar_shader = LoadShaderProgram(ctx, "healthbar")
    skybox_shader = LoadShaderProgram(ctx, "skybox") 
    obb_shader = LoadShaderProgram(ctx, "obb") #debug only
    
    clock = pygame.time.Clock()
    width, height = pygame.display.get_surface().get_size()
    proj = glm.perspective(glm.radians(45.0), width / height, 0.1, 100.0) 
    
    player = Player((20, 2, 5))
    crosshair = Crosshair(ctx, crosshair_shader)
    skybox = Skybox(ctx, skybox_shader, folder_path="textures/skybox")
    bullet_manager = BulletManager(ctx, shader, player)
    health_renderer = HealthBarRenderer(ctx, healthbar_shader)
    
    static_models = [
        Model(ctx, shader, "UNI.obj", position=(20,0,0)),
        #Model(ctx, shader, "room.obj", position=(0,-1,0), name="room"), 
        Model(ctx, shader, "large_grass.obj", position=(20,0,0)),
        #Model(ctx, shader, "colored.obj", position=(20,0,0)), 
        Model(ctx, shader, "pilars.obj", position=(20,0,0)),
        Model(ctx, shader, "roof_floor.obj", position=(20,0,0), visible=False),
       # Model(ctx, shader, "walls.obj", position=(20,0,0), visible=False),
        #Model(ctx, shader, "walls.obj", position=(20,0,0)),
    ]
    
    static_models[0].remove_colliders()
    #static_models[2].remove_colliders()
    
    weapons = [
        Pistol(ctx, shader, player),
        Rifle(ctx, shader, player),
        Shotgun(ctx, shader, player), 
    ]
    
    lights = [
        Light(position=(20,1,0), color=(1,1,1), ambient_strength=0.2, specular_strength=0.9),
    ]
    
    drones = [
        OrangeDrone(ctx, shader, position=(8, 1, 0), bullet_manager=bullet_manager),
        GreenDrone(ctx, shader, position=(6, 1, 0), bullet_manager=bullet_manager,all_drones=[]),
        BlueDrone(ctx, shader, position=(0, 1, 3), bullet_manager=bullet_manager),
        BlueDrone(ctx, shader, position=(2, 1, 3), bullet_manager=bullet_manager),
        BlueDrone(ctx, shader, position=(4, 1, 3), bullet_manager=bullet_manager),
    ]
    
    drones[2].all_drones = drones
    
    player.weapons = weapons
    player.heldweapon = player.weapons[0]
    
    Light.insert_lights(shader, lights, player.pos)
    obstacles = static_models + drones #+ [player.camera]
    
    while True:
        dt = clock.tick(60) / 1000.0 # Delta Time
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
        
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_rel()
        
        tn = pygame.time.get_ticks() / 1000.0  # en segundos
        player.camera.update(dt)
        view = player.camera.get_view_matrix(keys, mx, my, obstacles)
        player.handle_input(tn, events) 
        
        ctx.clear(0.5, 0.8, 0.9)
        skybox.draw(proj, view)
        bullet_manager.update(dt, obstacles)
        bullet_manager.draw(proj, view, player.pos)
        
        crosshair.draw()
        player.heldweapon.update(dt)
        player.heldweapon.draw(shader, proj, view) 
        for model in static_models:
            model.draw(shader, proj, view, player.pos)
            #model.draw_obb(obb_shader, proj, view)
        for drone in drones:
            drone.update(dt, player.pos, obstacles)
            drone.draw(shader, proj, view, player.pos)
            health_renderer.draw(proj, view, drone, player.pos)
            #drone.draw_obb(obb_shader, proj, view) 
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    
