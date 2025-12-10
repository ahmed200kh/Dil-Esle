import pygame

# Oyunun referans alınan temel tasarım çözünürlüğü (1080p)
DESIGN_W, DESIGN_H = 1920, 1080

COLORS = {
    # --- Arka Plan Renk Paleti ---
    "bg_gradient_top": (30, 100, 60),  # Üst kısım: Zengin çim yeşili
    "bg_gradient_bot": (10, 60, 35),   # Alt kısım: Daha koyu, derinlik veren yeşil tonu
    
    # --- Taş (Tile) Renkleri ---
    "tile_body": (245, 245, 240),      # Taşın ana gövde rengi
    "tile_border": (200, 200, 190),    # Taş kenarlıkları
    "tile_selected": (255, 215, 0),    # Seçili olma durumu (Vurgu)
    "tile_blocked": (180, 180, 180),   # Kilitli/Seçilemez durum
    "text": (20, 20, 20),              # Ana metin rengi
    "text_light": (240, 240, 240),     # Açık renk metinler
    
    # --- Ahşap Doku Teması (UI Elemanları) ---
    "wood_dark": (101, 67, 33),        # Koyu ahşap (Kenarlıklar)
    "wood_mid": (160, 82, 45),         # Orta ton (Düğme gövdeleri - Sıcak kahve)
    "wood_light": (205, 133, 63),      # Açık ahşap (Vurgular)
    "wood_shadow": (60, 30, 10),       # Ahşap gölgelendirmesi
    
    # --- Yuva (Slot) Alanı ---
    "slot_empty": (20, 50, 30),        # Boş yuva arkaplanı
    "slot_border": (60, 120, 80),      # Yuva çerçevesi
    
    # --- Geri Bildirim Renkleri ---
    "success": (100, 200, 100),        # Başarılı eşleşme (Yeşil)
    "error": (220, 80, 80),            # Hatalı hamle (Kırmızı)
}

class ScaleManager:
    """
    Farklı ekran çözünürlüklerinde oyunun en-boy oranını (aspect ratio) koruyarak
    düzgün görüntülenmesini sağlayan ölçekleme yöneticisi.
    """
    def __init__(self):
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.screen_w = DESIGN_W
        self.screen_h = DESIGN_H

    def update_dimensions(self, w, h):
        """
        Pencere boyutu değiştiğinde ölçek faktörünü ve ofsetleri yeniden hesaplar.
        Görüntüyü merkeze alarak 'Letterboxing' uygular.
        """
        self.screen_w = w
        self.screen_h = h
        scale_w = w / DESIGN_W
        scale_h = h / DESIGN_H
        # En ve boy oranlarından küçük olanı baz alarak taşmayı engelle
        self.scale_factor = min(scale_w, scale_h)
        
        # Görüntüyü ekrana ortalamak için gerekli boşlukları (ofset) hesapla
        self.offset_x = (w - (DESIGN_W * self.scale_factor)) / 2
        self.offset_y = (h - (DESIGN_H * self.scale_factor)) / 2

    def scale(self, value):
        """Tekil bir sayısal değeri (örn. font boyutu) ölçek faktörüyle çarpar."""
        return int(value * self.scale_factor)

    def to_screen(self, x, y):
        """
        Tasarım koordinatlarını (Mantıksal) gerçek ekran koordinatlarına (Fiziksel) dönüştürür.
        Çizim (Rendering) işlemleri için kullanılır.
        """
        return (self.offset_x + x * self.scale_factor, 
                self.offset_y + y * self.scale_factor)

    def to_design(self, x, y):
        """
        Gerçek ekran koordinatlarını tasarım koordinatlarına dönüştürür.
        Fare tıklamaları (Input handling) için kullanılır.
        """
        return ((x - self.offset_x) / self.scale_factor, 
                (y - self.offset_y) / self.scale_factor)

# Global ölçekleme yöneticisi örneği (Singleton)
SCALER = ScaleManager()