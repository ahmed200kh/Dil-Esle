import pygame
import sys
from src.settings import SCALER, COLORS, DESIGN_W, DESIGN_H
from src.screens.menu_screen import MenuScreen
from src.screens.game_screen import GameScreen
from src.systems.audio import AudioSystem

class MahjongGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Dil Eşle")
        
        # Pencere ayarları
        self.screen = pygame.display.set_mode((SCALER.screen_w, SCALER.screen_h), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Sistemler
        self.audio = AudioSystem()
        self.audio.play_music("water_ambience")
        
        # Ekranlar
        self.screens = {
            "menu": MenuScreen(self),
            "game": GameScreen(self)
        }
        self.current_screen = self.screens["menu"]

    def change_screen(self, screen_name):
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    w, h = event.w, event.h
                    self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                    SCALER.update_dimensions(w, h)
                
                if self.current_screen:
                    self.current_screen.handle_event(event)

            if self.current_screen:
                self.current_screen.update(dt)
                self.current_screen.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = MahjongGame()
    app.run()
