import pygame
import os
import random
import math
from src.settings import COLORS, SCALER
from src.utils.text_utils import render_text_centered

class Tile:
    """
    Oyun tahtası üzerindeki her bir taşı (kutu/kart) temsil eden sınıf.
    Bu sınıf; taşın çizimi, pozisyonu, durumu (seçili, kilitli vb.) ve
    kullanıcı etkileşimlerini (tıklama, sürükleme) yönetir.
    """
    # Sabit Boyut ve Görsel Ayarlar
    WIDTH = 90        
    HEIGHT = 110      
    DEPTH = 12        
    RADIUS = 14       

    # Renk Paleti Tanımları
    COLOR_FACE_NORMAL = (245, 240, 225)
    COLOR_FACE_SELECTED = (255, 250, 210)
    COLOR_TEXT_EN = (0, 50, 100)
    COLOR_TEXT_TR = (140, 30, 30)
    COLOR_SHADOW = (0, 0, 0, 50)
    
    # (Not: Kilitli taşlar için koyu renk efekti devre dışı bırakılmıştır)

    _tile_image = None

    def __init__(self, entry_id, text, lang, real_x, real_y, layer, symbol_data, show_helpers=True):
        """
        Taşın başlangıç durumunu ve özelliklerini başlatır.
        
        Args:
            entry_id: Eşleşme kontrolü için benzersiz kelime ID'si.
            text: Taş üzerinde gösterilecek metin.
            lang: Dil kodu ('en' veya 'tr').
            real_x, real_y: Hedef (orijinal) koordinatlar.
            layer: Taşın bulunduğu katman (Z-index mantığı).
            symbol_data: Görsel yardım için şekil ve renk verisi.
            show_helpers: Yardımcı şekillerin gösterilip gösterilmeyeceği.
        """
        self.entry_id = entry_id
        self.text = text
        self.lang = lang
        
        # Görsel yardımcı ayarları
        self.symbol_data = symbol_data
        self.show_helpers = show_helpers
        
        # Pozisyon değişkenleri
        self.base_x = real_x
        self.base_y = real_y
        self.x = real_x
        self.y = real_y
        self.layer = layer
        
        # Geri dönüş ve animasyon referans noktaları
        self.return_x = real_x
        self.return_y = real_y
        self.return_layer = layer
        
        # Sürükleme mantığı değişkenleri
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_dragging = False
        
        # Oyun durumu bayrakları (Flags)
        self.is_blocked = False
        self.is_selected = False
        self.in_slot = False
        self.removed = False
        
        # Görsel geri bildirim (Flash efekti)
        self.flash_color = None
        self.flash_timer = 0.0
        
        # Resim yüklenemezse kullanılacak prosedürel ahşap dokusu için rastgele desen üretimi
        self.wood_pattern = []
        rng = random.Random(id(self)) 
        for _ in range(5):
            y_start = rng.randint(10, self.HEIGHT - 10)
            length = rng.randint(20, self.WIDTH - 20)
            x_start = rng.randint(5, self.WIDTH - length - 5)
            thickness = rng.randint(1, 2)
            self.wood_pattern.append((x_start, y_start, length, thickness))

        self.load_image()

    @classmethod
    def load_image(cls):
        """
        Taş arka plan görselini diskten belleğe yükler.
        Performans için sadece bir kez yüklenir (Singleton pattern).
        """
        if cls._tile_image is None:
            path = os.path.join("assets", "images", "tile.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    cls._tile_image = img
                except Exception as e:
                    print(f"Error loading tile image: {e}")
                    cls._tile_image = None

    def trigger_flash(self, color, duration=0.3):
        """
        Taşın üzerinde geçici bir renk parlaması (örneğin hata durumunda kırmızı) tetikler.
        """
        self.flash_color = color
        self.flash_timer = duration

    def update(self, dt):
        """
        Her karede (frame) çağrılır. Animasyon zamanlayıcılarını günceller.
        """
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer < 0:
                self.flash_timer = 0
                self.flash_color = None

    def draw_wood_texture(self, surface, rect):
        """
        Eğer ana görsel yüklenemezse, kod ile oluşturulmuş basit bir ahşap dokusu çizer.
        """
        base_wood = (245, 235, 220) 
        pygame.draw.rect(surface, base_wood, rect, border_radius=self.RADIUS)
        grain_color = (230, 220, 205)
        for (x, y, l, h) in self.wood_pattern:
            rx = rect.x + (x / self.WIDTH) * rect.width
            ry = rect.y + (y / self.HEIGHT) * rect.height
            rw = (l / self.WIDTH) * rect.width
            rh = max(1, (h / self.HEIGHT) * rect.height)
            pygame.draw.rect(surface, grain_color, (rx, ry, rw, rh), border_radius=1)

    def draw_symbol(self, surface, center_x, center_y, size):
        """
        Erişilebilirlik ve görsel eşleştirme kolaylığı için taşın köşelerine
        geometrik şekiller (daire, kare, üçgen vb.) çizer.
        """
        if not self.symbol_data: return

        shape = self.symbol_data['shape']
        color = self.symbol_data['color']
        
        # Metnin okunabilirliğini bozmamak için şeffaflık (Alpha) eklenir
        r, g, b = color
        icon_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        draw_col = (r, g, b, 180) # Yarı şeffaf
        
        # Çizim koordinatları (Merkezleme)
        cx, cy = size, size 
        radius = size / 2
        
        if shape == 'circle':
            pygame.draw.circle(icon_surf, draw_col, (cx, cy), radius)
        elif shape == 'square':
            pygame.draw.rect(icon_surf, draw_col, (cx - radius, cy - radius, size, size), border_radius=2)
        elif shape == 'triangle':
            points = [(cx, cy - radius), (cx - radius, cy + radius), (cx + radius, cy + radius)]
            pygame.draw.polygon(icon_surf, draw_col, points)
        elif shape == 'diamond':
            points = [(cx, cy - radius), (cx + radius, cy), (cx, cy + radius), (cx - radius, cy)]
            pygame.draw.polygon(icon_surf, draw_col, points)
        elif shape == 'star':
            # Basitleştirilmiş yıldız temsili
            pygame.draw.circle(icon_surf, draw_col, (cx, cy), radius)
            pygame.draw.circle(icon_surf, (255,255,255), (cx, cy), radius/2)
        else:
            # Varsayılan şekil
            pygame.draw.circle(icon_surf, draw_col, (cx, cy), radius)

        surface.blit(icon_surf, (center_x - size, center_y - size))

    def draw(self, surface, font):
        """
        Taşın tüm görsel bileşenlerini (Gölge, Arka Plan, Simgeler, Metin, Efektler)
        ekrana (surface) çizer.
        """
        if self.removed: return

        # Sürükleme ofsetini hesaba katarak anlık pozisyonu belirle
        current_x = self.x + self.drag_offset_x
        current_y = self.y + self.drag_offset_y
        
        # Ekran ölçeklemesine (Scaling) göre koordinat dönüşümü
        sx, sy = SCALER.to_screen(current_x, current_y)
        sw = SCALER.scale(self.WIDTH)
        sh = SCALER.scale(self.HEIGHT)
        tile_rect = pygame.Rect(sx, sy, sw, sh)

        # Gölge Çizimi (Derinlik hissi için)
        if not self.in_slot and not self.is_dragging:
            shadow_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, self.COLOR_SHADOW, (0,0,sw,sh), border_radius=self.RADIUS)
            surface.blit(shadow_surf, (sx + 4, sy + 4)) 

        # Taşın Gövdesi (Resim veya Desen)
        if self._tile_image:
            final_img = pygame.transform.smoothscale(self._tile_image, (sw, sh))
            surface.blit(final_img, (sx, sy))
        else:
            self.draw_wood_texture(surface, tile_rect)
            border_col = (160, 140, 120)
            pygame.draw.rect(surface, border_col, tile_rect, 2, border_radius=self.RADIUS)

        # Yardımcı Sembollerin Çizimi
        if self.show_helpers and self.symbol_data:
            symbol_size = int(sw * 0.15) 
            self.draw_symbol(surface, sx + sw - 15, sy + 15, symbol_size) # Sağ üst
            self.draw_symbol(surface, sx + 15, sy + sh - 15, symbol_size) # Sol alt

        # Hata Efekti (Kırmızı Parlama)
        if self.flash_timer > 0 and self.flash_color:
            flash_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            alpha = int((self.flash_timer / 0.3) * 150)
            flash_surf.fill((*self.flash_color, alpha))
            surface.blit(flash_surf, (sx, sy), special_flags=pygame.BLEND_RGBA_ADD)

        # Seçim Efekti (Sarı vurgu)
        if self.is_selected:
            sel_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            sel_surf.fill((255, 255, 0, 50))
            surface.blit(sel_surf, (sx, sy), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.rect(surface, (255, 200, 0), tile_rect, 3, border_radius=self.RADIUS)

        # Metin Render İşlemi (Dil bazlı renklendirme)
        text_color = self.COLOR_TEXT_EN if self.lang == "en" else self.COLOR_TEXT_TR
        
        # Metin gölgesi ve kendisinin çizimi
        shadow_rect = tile_rect.move(1, 1)
        render_text_centered(surface, self.text, font, shadow_rect, (210, 200, 190))
        render_text_centered(surface, self.text, font, tile_rect, text_color)

    def click_check(self, mouse_pos):
        """
        Verilen fare koordinatlarının (mouse_pos) bu taşın sınırları içinde
        olup olmadığını kontrol eder (Collision Detection).
        """
        if self.removed: return False
        current_x = self.x + self.drag_offset_x
        current_y = self.y + self.drag_offset_y
        sx, sy = SCALER.to_screen(current_x, current_y)
        sw = SCALER.scale(self.WIDTH)
        sh = SCALER.scale(self.HEIGHT)
        return pygame.Rect(sx, sy, sw, sh).collidepoint(mouse_pos)