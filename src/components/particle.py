import pygame
import random

class Particle:
    """
    Görsel efektler (patlama, kıvılcım vb.) için kullanılan Parçacık sınıfı.
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        # X ve Y eksenlerinde rastgele yayılma hızı (Dağılım efekti için)
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-6, 6)
        self.life = 1.0 
        self.color = color
        # Görünürlüğü artırmak için rastgele boyut aralığı
        self.size = random.randint(6, 12)
        self.gravity = 0.25 # Yerçekimi ivmesi

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity 
        # Sönümleme: Efektin ekranda daha uzun süre kalması için yavaşça azaltılır
        self.life -= 0.015 

    def draw(self, surface):
        if self.life > 0:
            # Yaşam süresine bağlı dinamik şeffaflık (Alpha) hesaplaması
            alpha = int(self.life * 255)
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            # Daha estetik bir görünüm için kare yerine daire çizimi
            pygame.draw.circle(s, (*self.color, alpha), (self.size//2, self.size//2), self.size//2)
            surface.blit(s, (self.x, self.y))