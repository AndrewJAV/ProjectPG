import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer

def main():
    pygame.init()
    size = (800, 600)
    pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL)

    imgui.create_context()
    impl = PygameRenderer()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            impl.process_event(event)

        impl.process_inputs()

        # Muy importante fijar el tamaño antes de new_frame
        imgui.get_io().display_size = pygame.display.get_surface().get_size()

        imgui.new_frame()

        imgui.begin("Ventana ImGui")
        if imgui.button("Salir"):
            running = False
        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()

    impl.shutdown()
    pygame.quit()

if __name__ == "__main__":
    main()
