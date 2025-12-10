import pygame
import sys
import os
from src.settings import SCALER, COLORS
from src.systems.save_manager import SaveManager

class MenuScreen:
    """
    Oyunun giriş ve ayarlar menüsünü yöneten sınıf.
    Kullanıcı arayüzü (UI) bileşenlerini çizer, kullanıcı girdilerini (Input) işler
    ve oyun konfigürasyonunu (Dil, Zorluk, Seviye) yönetir.
    """
    def __init__(self, manager):
        # Bağımlılık Enjeksiyonu (Dependency Injection) ile ekran yöneticisi alınır
        self.manager = manager
        # Kayıt yönetim sistemi (Save Manager) başlatılır
        self.save_manager = SaveManager()
        
        # Dinamik Font Yükleme (Responsive Typography)
        self.font_title = pygame.font.SysFont("Arial", 80, bold=True) 
        self.font_btn = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        # Menü durum makinesi (State Machine: 'main' veya 'settings')
        self.current_state = "main"
        
        # Sıfırlama işlemi için geçici geri bildirim değişkenleri
        self.show_reset_msg = False
        self.reset_msg_timer = 0.0
        
        # Varsayılan Oyun Ayarları (veya kayıttan yükle)
        self.settings = {
            "ui_lang": "en",       # Arayüz Dili
            "target_lang": "tr",   # Öğrenilecek Dil
            "vocab_level": self.save_manager.get_vocab_level(),   # Kaydedilmiş kelime seviyesi
            "game_diff": "Normal"  # Oyun Zorluğu
        }
        
        # Ayar Seçenekleri Listesi
        self.options_vocab = ["A1", "A2", "B1", "B2", "C1", "C2"]
        self.options_diff = ["Easy", "Normal", "Hard"]
        self.options_ui_lang = ["en", "tr"]
        self.options_target_lang = ["en", "tr"]

        # Çoklu Dil Desteği (Localization) Sözlüğü
        self.texts = {
            "en": {
                "title": "LinguaMatch",
                "start": "START GAME",
                "settings": "SETTINGS",
                "exit": "EXIT",
                "lbl_ui": "Interface Language:",
                "lbl_target": "Learning Language:",
                "lbl_vocab": "Vocabulary Level:",
                "lbl_diff": "Game Difficulty:",
                "reset": "RESET PROGRESS",
                "reset_done": "Progress Reset!", # Geri bildirim mesajı
                "back": "BACK"
            },
            "tr": {
                "title": "LinguaMatch",
                "start": "OYUNU BAŞLAT",
                "settings": "AYARLAR",
                "exit": "ÇIKIŞ",
                "lbl_ui": "Arayüz Dili:",
                "lbl_target": "Öğrenilen Dil:",
                "lbl_vocab": "Kelime Seviyesi:",
                "lbl_diff": "Oyun Zorluğu:",
                "reset": "İLERLEMEYİ SIFIRLA",
                "reset_done": "İlerleme Sıfırlandı!", # Geri bildirim mesajı
                "back": "GERİ"
            }
        }

        self.banner_img = None
        self.load_assets()

    def load_assets(self):
        """
        Menü arka plan görselini (banner) diskten yükler.
        Hata durumunda (Exception Handling) konsola bilgi verir.
        """
        path = os.path.join("assets", "images", "menu_banner.png")
        if not os.path.exists(path):
            path = os.path.join("assets", "images", "menu_banner.jpg")

        if os.path.exists(path):
            try:
                self.banner_img = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Error loading banner: {e}")
                self.banner_img = None

    def get_text(self, key):
        """
        Mevcut arayüz diline (ui_lang) göre ilgili metni sözlükten döndürür.
        """
        lang = self.settings["ui_lang"]
        return self.texts[lang].get(key, key)

    def handle_event(self, event):
        """
        Kullanıcı giriş olaylarını (Mouse Click) işler ve ilgili durum yöneticisine yönlendirir.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            if self.current_state == "main":
                self.handle_main_menu_click(mx, my)
            elif self.current_state == "settings":
                self.handle_settings_click(mx, my)

    def handle_main_menu_click(self, mx, my):
        """Ana menü butonlarının tıklama etkileşimlerini yönetir."""
        # 1. Başlat Butonu
        if self.get_rect(0).collidepoint(mx, my):
            # Hedef dile göre ana dili otomatik belirle (Tersi mantığı)
            native = "tr" if self.settings["target_lang"] == "en" else "en"
            # Oyun ekranına konfigürasyonu aktar
            self.manager.screens["game"].set_config(
                native_lang=native,
                target_lang=self.settings["target_lang"],
                diff=self.settings["game_diff"],
                vocab_lvl=self.settings["vocab_level"]
            )
            self.manager.change_screen("game")

        # 2. Ayarlar Butonu
        elif self.get_rect(1).collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.current_state = "settings"
            self.show_reset_msg = False # Mesajı sıfırla

        # 3. Çıkış Butonu
        elif self.get_rect(2).collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            pygame.quit()
            sys.exit()

    def handle_settings_click(self, mx, my):
        """Ayarlar menüsündeki buton ve toggle etkileşimlerini yönetir."""
        # Arayüz Dili Değiştirme
        if self.get_setting_rect(0).collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.toggle_setting("ui_lang", self.options_ui_lang)

        # Hedef Dil Değiştirme
        elif self.get_setting_rect(1).collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.toggle_setting("target_lang", self.options_target_lang)
            
        # Kelime Seviyesi Değiştirme
        elif self.get_setting_rect(2).collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.toggle_setting("vocab_level", self.options_vocab)
            
        # Zorluk Seviyesi Değiştirme
        elif self.get_setting_rect(3).collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.toggle_setting("game_diff", self.options_diff)
            
        # İlerlemeyi Sıfırla Butonu (Kritik İşlem)
        elif self.get_reset_rect().collidepoint(mx, my):
            self.manager.audio.play_sound("match") # Onay sesi
            self.save_manager.reset_progress()
            self.show_reset_msg = True
            self.reset_msg_timer = 2.0 # Bildirim süresi
            
        # Geri Dön Butonu
        elif self.get_back_rect().collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.current_state = "main"

    def toggle_setting(self, key, options_list):
        """
        Belirtilen ayar için seçenekler listesinde döngüsel (cyclic) geçiş yapar.
        """
        current_val = self.settings[key]
        try:
            idx = options_list.index(current_val)
            new_idx = (idx + 1) % len(options_list)
            self.settings[key] = options_list[new_idx]
        except ValueError:
            self.settings[key] = options_list[0]
        # Eğer kelime seviyesi değiştiyse, kaydet
        if key == "vocab_level":
            self.save_manager.set_vocab_level(self.settings["vocab_level"])

    # --- UI Layout Hesaplama Metotları (Responsive Design) ---
    
    def get_rect(self, index):
        """Ana menü butonlarının dinamik konumunu hesaplar."""
        center_x = SCALER.screen_w // 2
        start_y = int(SCALER.screen_h * 0.65) 
        return pygame.Rect(center_x - 150, start_y + (index * 90), 300, 70)
    
    def get_setting_rect(self, index):
        """Ayar butonlarının dinamik konumunu hesaplar."""
        center_x = SCALER.screen_w // 2
        start_y = SCALER.screen_h // 2 - 120
        return pygame.Rect(center_x + 20, start_y + (index * 70), 220, 55)

    def get_reset_rect(self):
        """Sıfırlama butonunun konumunu hesaplar."""
        center_x = SCALER.screen_w // 2
        start_y = SCALER.screen_h // 2 - 120
        return pygame.Rect(center_x - 125, start_y + (4 * 70) + 20, 250, 60)

    def get_back_rect(self):
        """Geri dön butonunun konumunu hesaplar."""
        center_x = SCALER.screen_w // 2
        return pygame.Rect(center_x - 100, SCALER.screen_h - 100, 200, 60)

    def update(self, dt):
        """Zamanlayıcıları ve animasyon durumlarını günceller."""
        if self.show_reset_msg:
            self.reset_msg_timer -= dt
            if self.reset_msg_timer <= 0:
                self.show_reset_msg = False

    def draw_wood_button(self, surface, rect, text, is_hover, is_danger=False):
        """
        Özel temalı (Ahşap dokulu) UI butonu çizer.
        
        Args:
            is_hover: Fare üzerindeyse vurgu rengi uygular.
            is_danger: Kritik butonlar (Sıfırla vb.) için kırmızı tema kullanır.
        """
        if is_danger:
            fill_color = (180, 70, 70) if is_hover else (150, 50, 50)
            border_color = (80, 20, 20)
        else:
            fill_color = COLORS["wood_light"] if is_hover else COLORS["wood_mid"]
            border_color = COLORS["wood_dark"]
        
        shadow_rect = rect.move(4, 4)
        
        # Çizim Katmanları: Gölge -> Dolgu -> Kenarlık -> Parlama -> Metin
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=15)
        pygame.draw.rect(surface, fill_color, rect, border_radius=15)
        pygame.draw.rect(surface, border_color, rect, 4, border_radius=15)
        
        # Parlama efekti (Highlight)
        highlight_rect = pygame.Rect(rect.x + 5, rect.y + 5, rect.width - 10, rect.height // 2)
        s = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 30), s.get_rect(), border_radius=10)
        surface.blit(s, highlight_rect)

        text_surf = self.font_btn.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        
        # Metin gölgesi
        shadow_text = self.font_btn.render(text, True, (60, 40, 20) if not is_danger else (40, 10, 10))
        shadow_text_rect = text_rect.move(2, 2)
        surface.blit(shadow_text, shadow_text_rect)
        surface.blit(text_surf, text_rect)

    def draw(self, surface):
        """Ekranın tamamını (Arka plan ve UI elemanları) render eder."""
        # Degrade Arka Plan Çizimi
        surface.fill(COLORS["bg_gradient_bot"])
        for y in range(0, SCALER.screen_h, 2): 
            ratio = y / SCALER.screen_h
            r = int(COLORS["bg_gradient_top"][0] * (1-ratio) + COLORS["bg_gradient_bot"][0] * ratio)
            g = int(COLORS["bg_gradient_top"][1] * (1-ratio) + COLORS["bg_gradient_bot"][1] * ratio)
            b = int(COLORS["bg_gradient_top"][2] * (1-ratio) + COLORS["bg_gradient_bot"][2] * ratio)
            pygame.draw.line(surface, (r,g,b), (0, y), (SCALER.screen_w, y), 2)
        
        # Duruma göre içerik çizimi
        if self.current_state == "main":
            # Banner veya Başlık
            if self.banner_img:
                target_width = int(SCALER.screen_w * 0.5)
                aspect_ratio = self.banner_img.get_height() / self.banner_img.get_width()
                target_height = int(target_width * aspect_ratio)
                scaled_banner = pygame.transform.smoothscale(self.banner_img, (target_width, target_height))
                banner_rect = scaled_banner.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h * 0.35))
                surface.blit(scaled_banner, banner_rect)
            else:
                title_txt = self.get_text("title")
                title = self.font_title.render(title_txt, True, COLORS["tile_selected"])
                title_rect = title.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h//3))
                surface.blit(title, title_rect)

            self.draw_main_menu(surface)
        else:
            # Ayarlar Başlığı
            title_txt = self.get_text("settings")
            title = self.font_title.render(title_txt, True, COLORS["tile_selected"])
            title_rect = title.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h * 0.12))
            surface.blit(title, title_rect)
            
            self.draw_settings_menu(surface)
            
            # Geri Bildirim Mesajı (Overlay)
            if self.show_reset_msg:
                msg_txt = self.get_text("reset_done")
                msg_surf = self.font_btn.render(msg_txt, True, (100, 255, 100))
                
                reset_btn_rect = self.get_reset_rect()
                msg_rect = msg_surf.get_rect(center=(reset_btn_rect.centerx, reset_btn_rect.top - 30))
                
                # Mesaj arka planı (Okunabilirlik için)
                bg_rect = msg_rect.inflate(20, 10)
                pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=10)
                surface.blit(msg_surf, msg_rect)

    def draw_main_menu(self, surface):
        """Ana menü butonlarını çizer."""
        labels = ["start", "settings", "exit"]
        for i, key in enumerate(labels):
            rect = self.get_rect(i)
            text = self.get_text(key)
            mouse_pos = pygame.mouse.get_pos()
            is_hover = rect.collidepoint(mouse_pos)
            self.draw_wood_button(surface, rect, text, is_hover)

    def draw_settings_menu(self, surface):
        """Ayarlar menüsünü (Etiketler ve Toggle Butonları) çizer."""
        items = [
            ("lbl_ui", "ui_lang"),
            ("lbl_target", "target_lang"),
            ("lbl_vocab", "vocab_level"),
            ("lbl_diff", "game_diff")
        ]
        
        start_y = SCALER.screen_h // 2 - 120
        center_x = SCALER.screen_w // 2
        
        for i, (label_key, settings_key) in enumerate(items):
            # Etiket Çizimi
            label_txt = self.get_text(label_key)
            lbl_surf = self.font_btn.render(label_txt, True, (240, 240, 240))
            lbl_rect = lbl_surf.get_rect(right=center_x - 20, centery=start_y + (i * 70) + 27)
            
            lbl_shadow = self.font_btn.render(label_txt, True, (0, 0, 0))
            surface.blit(lbl_shadow, lbl_rect.move(2, 2))
            surface.blit(lbl_surf, lbl_rect)
            
            # Buton Çizimi
            btn_rect = self.get_setting_rect(i)
            mouse_pos = pygame.mouse.get_pos()
            is_hover = btn_rect.collidepoint(mouse_pos)
            
            val_txt = self.settings[settings_key]
            if settings_key in ["ui_lang", "target_lang"]:
                val_txt = "English" if val_txt == "en" else "Türkçe"
            
            self.draw_wood_button(surface, btn_rect, val_txt, is_hover)

        # Sıfırlama Butonu
        reset_rect = self.get_reset_rect()
        mouse_pos = pygame.mouse.get_pos()
        is_hover = reset_rect.collidepoint(mouse_pos)
        reset_txt = self.get_text("reset")
        self.draw_wood_button(surface, reset_rect, reset_txt, is_hover, is_danger=True)

        # Geri Butonu
        back_rect = self.get_back_rect()
        is_hover_back = back_rect.collidepoint(mouse_pos)
        back_txt = self.get_text("back")
        self.draw_wood_button(surface, back_rect, back_txt, is_hover_back)