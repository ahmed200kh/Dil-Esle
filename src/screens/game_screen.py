import pygame
import math
import random
import os
from src.settings import DESIGN_W, DESIGN_H, COLORS, SCALER
from src.components.tile import Tile
from src.components.particle import Particle
from src.systems.vocab_loader import VocabLoader
from src.systems.save_manager import SaveManager
from src.systems.tts_manager import TTSManager

class GameScreen:
    """
    Oyunun ana mantığını ve akışını yöneten ekran sınıfı.
    Kullanıcı etkileşimleri, oyun döngüsü, seviye yönetimi ve
    görsel bileşenlerin (Tile, UI) render işlemlerinden sorumludur.
    """
    def __init__(self, manager):
        # Bağımlılık Enjeksiyonu (Dependency Injection) ile ekran yöneticisi alınır
        self.manager = manager
        
        # Alt sistemlerin başlatılması (Facade Pattern)
        self.vocab_loader = VocabLoader()
        self.save_manager = SaveManager()
        self.tts = TTSManager()
        
        # Oyun durumu (State) değişkenleri
        self.tiles = []  # Sahnedeki aktif taşların listesi
        self.reserve_slots = [None] * 4  # Aşağıdaki eşleştirme yuvaları (Buffer)
        self.shake_timers = {}  # Hatalı hamlelerde titreme efekti için zamanlayıcılar
        
        self.animating_matches = []  # Eşleşme animasyonu oynatılan taşlar
        self.particles = []  # Parçacık efektleri sistemi
        self.dragging_tile = None  # O an sürüklenen taş referansı
        self.drag_start_mouse_pos = (0, 0)
        
        # Oyun kontrol bayrakları
        self.game_over = False
        self.game_won = False
        self.move_history = []  # "Geri Al" (Undo) fonksiyonu için hamle geçmişi yığını (Stack)
        self.hinted_tiles = []  # İpucu ile vurgulanan taşlar
        self.hint_timer = 0
        self.is_shuffling = False  # Karıştırma animasyonu durumu
        self.shuffle_timer = 0.0
        
        self.state = "intro"  # Mevcut oyun durumu (intro, playing, paused, game_over)
        self.state_timer = 0.0
        self.level_message = ""
        self.tutorial_text = ""
        self.current_level_num = 1 
        self.show_helpers = True 

        # --- Arka Plan Tema Ayarları ---
        self.bg_themes = [
            {"top": (30, 100, 60), "bot": (10, 60, 35), "name": "Yeşil "},
            {"top": (30, 60, 100), "bot": (10, 20, 60), "name": "Mavi "},
            {"top": (100, 70, 40), "bot": (60, 40, 20), "name": "Ahşap "},
            {"top": (60, 60, 65),  "bot": (30, 30, 35), "name": "Gri "},
            {"top": (80, 40, 90),  "bot": (40, 20, 50), "name": "Mor "}
        ]
        self.current_bg_index = 0
        
        # Dinamik Font Yükleme (Varlık Yönetimi)
        font_path = os.path.join("assets", "fonts", "game_font.ttf")
        self.font = pygame.font.Font(font_path, 22) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 24, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 30, bold=True)
        
        # UI Butonlarının çarpışma alanları (Rect)
        self.btn_shuffle_rect = None
        self.btn_hint_rect = None
        self.btn_undo_rect = None
        
        self.icons = {}
        self.load_icons()

    def load_icons(self):
        """
        Oyun içi ikonları (karıştır, ipucu, geri al) önbelleğe yükler.
        """
        icon_files = {"shuffle": "shuffle.png", "hint": "hint.png", "undo": "undo.png"}
        for key, filename in icon_files.items():
            path = os.path.join("assets", "images", filename)
            if os.path.exists(path):
                self.icons[key] = pygame.image.load(path).convert_alpha()

    def set_config(self, native_lang, target_lang, diff, vocab_lvl, ui_lang="en", show_helpers=True):
        """
        Oyun yapılandırma ayarlarını uygular ve seviyeyi başlatır.
        
        Args:
            native_lang: Kullanıcının ana dili.
            target_lang: Öğrenilen hedef dil.
            diff: Oyun zorluk seviyesi.
            vocab_lvl: Kelime zorluk seviyesi (A1-C2).
            ui_lang: Arayüz dili.
            show_helpers: Görsel yardımcıların durumu.
        """
        self.native_lang = native_lang
        self.target_lang = target_lang
        self.difficulty = diff
        self.vocab_level = vocab_lvl
        self.ui_lang = ui_lang
        self.show_helpers = show_helpers 
        self.init_level()

    def toggle_helpers(self):
        """Yardımcı şekillerin (symbol helpers) görünürlüğünü anlık olarak değiştirir."""
        self.show_helpers = not self.show_helpers
        # Değişikliği sahnedeki tüm taşlara uygula
        for t in self.tiles:
            t.show_helpers = self.show_helpers

    def generate_unique_symbols(self, pair_count):
        """
        Eşleşen taş çiftleri için benzersiz görsel semboller (şekil + renk) üretir.
        Bu, renk körü kullanıcılar veya görsel hafıza desteği için kullanılır.
        """
        shapes = [
            'circle', 'square', 'triangle', 'diamond', 'cross', 'star', 
            'pentagon', 'hexagon', 'ring', 'inv_triangle', 'hourglass', 
            'box_cross', 'plus', 'target', 'bar', 'moon', 'rhombus', 'grid'
        ]
        colors = [
            (255, 0, 0),      # Red
            (0, 102, 204),    # Blue
            (0, 204, 102),    # Green
            (255, 255, 0),    # Yellow
            (255, 153, 0),    # Orange
            (255, 102, 178),  # Pink
            (153, 51, 255),   # Purple
            (0, 0, 0),        # Black
            (255, 255, 255),  # White
            (101, 67, 33)     # Brown
        ]
        # Tüm olası kombinasyonları oluştur (Cartesian Product)
        all_combinations = []
        for s in shapes:
            for c in colors:
                all_combinations.append({'shape': s, 'color': c})
        
        # Rastgelelik sağlamak için karıştır
        random.shuffle(all_combinations)
        
        # İstenilen sayıda sembolü döndür (yetmezse döngüsel olarak tekrarla)
        if pair_count > len(all_combinations): 
            return all_combinations + all_combinations[:pair_count-len(all_combinations)]
        return all_combinations[:pair_count]

    def init_level(self):
        """
        Yeni bir oyun seviyesini başlatır.
        Verileri yükler, taşları prosedürel olarak yerleştirir ve oyun durumunu sıfırlar.
        """
        self.save_manager.load()
        self.manager.audio.play_sound("start")
        
        # Sahneyi temizle
        self.tiles.clear()
        self.reserve_slots = [None] * 4
        self.shake_timers.clear()
        self.animating_matches.clear()
        self.particles.clear()
        self.move_history = [] 
        self.hinted_tiles = []
        self.game_over = False
        self.game_won = False
        self.is_shuffling = False
        self.dragging_tile = None
        
        current_level = self.save_manager.get_level()
        self.current_level_num = current_level 
        word_index = self.save_manager.get_word_index()
        
        # Giriş animasyonu durumu
        self.state = "intro"
        self.state_timer = 2.0
        self.level_message = f"SEVİYE {current_level}"
        self.tutorial_text = ""
        
        w, h = Tile.WIDTH, Tile.HEIGHT
        gap = -5
        start_y = 200
        
        # İlk seviyeler için özel (Tutorial) düzenlemeler
        if current_level == 1:
            pair_count = 1
            review_count = 0
            self.tutorial_text = "Eşleşen taşları seçin!"
            start_y = 350
            layers = [{"rows": 1, "cols": 2, "ox": 0, "oy": 0}]
        elif current_level == 2:
            pair_count = 2
            review_count = 0
            self.tutorial_text = "Yanları kapalı taşlar seçilemez!"
            start_y = 350
            layers = [{"rows": 1, "cols": 4, "ox": 0, "oy": 0}] 
        else:
            # İleri seviyeler için dinamik zorluk artışı
            pair_count = min(60, int(8 + (current_level * 2)))
            review_count = int(pair_count * 0.3) # %30 eski kelime tekrarı (Spaced Repetition)
            layers = self.generate_complex_layout(pair_count)

        # Kelime verisinin uygun çiftleri, kullanılan kelimeler hariç tutularak çek
        used_word_ids = self.save_manager.get_used_word_ids()
        selected_level = getattr(self, "vocab_level", None)
        self.current_pairs, self.new_words_count, new_ids = self.vocab_loader.get_level_pairs(pair_count, word_index, review_count, used_word_ids, start_level=selected_level)
        # Kullanılan kelimeler listesini güncelle
        self.save_manager.add_used_word_ids(new_ids)
        
        # Sembolleri kelime ID'lerine eşle
        unique_ids = []
        seen = set()
        for p in self.current_pairs:
            if p['entry_id'] not in seen:
                unique_ids.append(p['entry_id'])
                seen.add(p['entry_id'])
        unique_symbols = self.generate_unique_symbols(len(unique_ids))
        id_to_symbol = {uid: sym for uid, sym in zip(unique_ids, unique_symbols)}

        # Yerleşim düzenini hesapla (Layout Calculation)
        if layers:
            base_cols = layers[0]["cols"]
            total_width = base_cols * (w + gap)
            start_x = (DESIGN_W - total_width) // 2
        else:
            start_x = 100

        current_pair_idx = 0
        layout_pos = []
        
        # 3D katmanlı yapıyı oluştur (Z-index yönetimi)
        for l_idx, cfg in enumerate(layers):
            layer_width = cfg["cols"] * (w + gap)
            center_offset_x = (total_width - layer_width) // 2
            elevation_y = - (l_idx * 12) # Derinlik efekti için Y ekseni kaydırma
            
            for r in range(cfg["rows"]):
                for c in range(cfg["cols"]):
                    if current_pair_idx >= len(self.current_pairs): break
                    real_x = start_x + center_offset_x + (c * (w + gap))
                    real_y = start_y + (r * (h - 12)) + elevation_y
                    layout_pos.append((real_x, real_y, l_idx))
                    current_pair_idx += 1

        # Kelimeleri karıştırarak pozisyonlara dağıt
        words_shuffled = self.current_pairs.copy()
        random.shuffle(words_shuffled)

        for i, pos in enumerate(layout_pos):
            if i < len(words_shuffled):
                data = words_shuffled[i]
                sym_data = id_to_symbol.get(data['entry_id'])
                
                t = Tile(data['entry_id'], data['text'], data['lang'], pos[0], pos[1], pos[2], sym_data, show_helpers=self.show_helpers)
                
                # Başlangıç animasyonu (yukarıdan düşme efekti)
                t.x = random.randint(-100, DESIGN_W + 100)
                t.y = -500
                t.return_x = pos[0]
                t.return_y = pos[1]
                t.return_layer = pos[2]
                self.tiles.append(t)

        self.update_blocked_status()

    def generate_complex_layout(self, pair_count):
        """
        Mahjong benzeri, üst üste binen karmaşık taş düzenlerini prosedürel olarak üretir.
        
        Args:
            pair_count: Toplam eşleşme çifti sayısı.
        Returns:
            layers: Katman konfigürasyon listesi.
        """
        total_tiles = pair_count * 2
        layers = []
        remaining = total_tiles
        layer_idx = 0
        MAX_COLS = 7
        MAX_ROWS = 7 
        LAYER_CAPACITY = MAX_COLS * MAX_ROWS
        
        while remaining > 0:
            if layer_idx == 0:
                count = min(remaining, LAYER_CAPACITY)
                if count % 2 != 0 and count < remaining: count += 1
                elif count % 2 != 0 and count == remaining: pass
                
            elif layer_idx == 1:
                count = min(remaining, 36) # İkinci katman daha küçük
            else:
                count = remaining # Piramit yapısı için kalanlar

            # Kareye yakın en uygun matris boyutunu hesapla
            side = math.ceil(math.sqrt(count))
            cols = min(side, MAX_COLS)
            rows = math.ceil(count / cols)
            
            if rows > MAX_ROWS:
                rows = MAX_ROWS
                cols = math.ceil(count / rows)
                
            layers.append({"rows": rows, "cols": cols, "ox": 0, "oy": 0})
            layer_capacity_used = rows * cols
            if remaining <= layer_capacity_used:
                remaining = 0
            else:
                remaining -= layer_capacity_used
            
            layer_idx += 1
            if layer_idx > 5: break # Güvenlik sınırı
            
        return layers

    def get_slot_rects(self):
        """Aşağıdaki 4'lü eşleştirme yuvasının koordinatlarını hesaplar."""
        slot_w = Tile.WIDTH   
        slot_h = Tile.HEIGHT  
        slot_gap = 15         
        total_w = (4 * slot_w) + (3 * slot_gap)
        start_x = (DESIGN_W - total_w) // 2
        start_y = 60 
        rects = []
        for i in range(4):
            x = start_x + (i * (slot_w + slot_gap))
            rects.append(pygame.Rect(x, start_y, slot_w, slot_h))
        return rects

    def get_logic_rect(self, tile):
        """Taşın mantıksal (çarpışma) dikdörtgenini döndürür."""
        return pygame.Rect(tile.base_x, tile.base_y, tile.WIDTH, tile.HEIGHT)

    def find_blockers(self, target_tile):
        """
        Bir taşın seçimini engelleyen diğer taşları (üzerinde veya yanında olanlar) bulur.
        Mahjong kuralları gereği, bir taşın seçilebilmesi için 'serbest' olması gerekir.
        """
        blockers = []
        my_rect = self.get_logic_rect(target_tile)
        tol = 10 # Tolerans payı (hassasiyet)
        for other in self.tiles:
            if other == target_tile or other.removed or other.in_slot or other in self.animating_matches:
                continue
            other_rect = self.get_logic_rect(other)
            
            # Üst katmandaki taşlar engelliyor mu? (Z ekseni kontrolü)
            if other.layer > target_tile.layer:
                intersect = my_rect.clip(other_rect)
                if intersect.width > tol and intersect.height > tol:
                    blockers.append(other)
            
            # Aynı katmandaki taşlar yanlardan engelliyor mu? (X ekseni kontrolü)
            elif other.layer == target_tile.layer:
                if abs(other.base_y - target_tile.base_y) < (target_tile.HEIGHT * 0.8):
                    if abs(other.base_x + other.WIDTH - target_tile.base_x) < tol:
                        blockers.append(other) # Sol engel
                    if abs(target_tile.base_x + target_tile.WIDTH - other.base_x) < tol:
                        blockers.append(other) # Sağ engel
        return blockers

    def update_blocked_status(self):
        """Sahnedeki tüm taşların kilitli/serbest durumunu günceller."""
        for t in self.tiles:
            if t.removed or t.in_slot or t in self.animating_matches:
                t.is_blocked = False
                continue
            blockers = self.find_blockers(t)
            is_covered_by_top = any(b.layer > t.layer for b in blockers)
            has_left = False
            has_right = False
            tol = 10
            for b in blockers:
                if b.layer == t.layer:
                    if abs(b.base_x + b.WIDTH - t.base_x) < tol: has_left = True
                    if abs(t.base_x + t.WIDTH - b.base_x) < tol: has_right = True
            
            # Kural: Üstü kapalıysa VEYA (hem sağı hem solu kapalıysa) bloklanmıştır.
            if is_covered_by_top or (has_left and has_right):
                t.is_blocked = True
            else:
                t.is_blocked = False

    def use_hint(self):
        """İpucu algoritması: Serbest olan eşleşen bir çifti bulur ve vurgular."""
        if self.hint_timer > 0 or self.state != "playing": return 
        self.manager.audio.play_sound("hint")
        available_tiles = [t for t in self.tiles if not t.removed and not t.in_slot and not t.is_blocked]
        match_found = False
        for i in range(len(available_tiles)):
            for j in range(i + 1, len(available_tiles)):
                t1 = available_tiles[i]
                t2 = available_tiles[j]
                if t1.entry_id == t2.entry_id:
                    self.hinted_tiles = [t1, t2]
                    self.hint_timer = 2.0 
                    match_found = True
                    break
            if match_found: break
        if not match_found: print("No matches!")

    def undo_last_move(self):
        """
        Son yapılan hamleyi geri alır (Stack pop işlemi).
        Yuvadaki taşı eski yerine geri gönderir.
        """
        if self.state != "playing": return
        self.manager.audio.play_sound("undo")
        while len(self.move_history) > 0:
            target_tile = self.move_history.pop()
            if target_tile.removed: continue
            if target_tile in self.animating_matches: continue 
            if target_tile.in_slot:
                try:
                    idx = self.reserve_slots.index(target_tile)
                    self.reserve_slots[idx] = None
                    target_tile.in_slot = False
                    target_tile.base_x = target_tile.return_x
                    target_tile.base_y = target_tile.return_y
                    target_tile.layer = target_tile.return_layer
                    self.update_blocked_status()
                    self.game_over = False
                    self.hinted_tiles = []
                    return 
                except ValueError: continue

    def shuffle_board(self):
        """
        Oyun kilitlendiğinde veya kullanıcı istediğinde kalan taşları yeniden karıştırır.
        """
        if self.state != "playing": return
        self.manager.audio.play_sound("shuffle")
        board_tiles = [t for t in self.tiles if not t.removed and not t.in_slot and t not in self.animating_matches]
        if not board_tiles: return
        positions = [(t.base_x, t.base_y, t.layer) for t in board_tiles]
        random.shuffle(positions)
        for i, t in enumerate(board_tiles):
            new_pos = positions[i]
            t.base_x = new_pos[0]; t.base_y = new_pos[1]; t.layer = new_pos[2]
            t.return_x = t.base_x; t.return_y = t.base_y; t.return_layer = t.layer
        self.is_shuffling = True; self.shuffle_timer = 1.5 
        self.update_blocked_status(); self.hinted_tiles = []; self.move_history.clear()

    def toggle_bg(self):
        """Arka plan temasını değiştirir."""
        self.current_bg_index = (self.current_bg_index + 1) % len(self.bg_themes)

    def toggle_tts(self):
        """Metin okuma (TTS) özelliğini açıp kapatır."""
        self.tts.toggle()

    def toggle_sfx(self):
        """Ses efektlerini (SFX) açıp kapatır."""
        self.manager.audio.toggle_sfx()

    def check_options_button(self, mx, my):
        """Ayarlar butonuna tıklama kontrolü."""
        opt_btn_rect = pygame.Rect(DESIGN_W - 80, 20, 60, 60)
        if opt_btn_rect.collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            return True
        return False

    def handle_pause_menu_click(self, mx, my):
        """Duraklatma menüsündeki buton etkileşimlerini yönetir."""
        center_x, center_y = DESIGN_W // 2, DESIGN_H // 2
        start_y = center_y - 80
        
        # Butonlar listesi (Draw fonksiyonu ile eşleşmeli)
        # 1. Arka Plan
        r1 = pygame.Rect(center_x - 150, start_y, 300, 50)
        if r1.collidepoint(mx, my):
            self.toggle_bg(); self.manager.audio.play_sound("click"); return
            
        # 2. TTS (Seslendirme)
        r2 = pygame.Rect(center_x - 150, start_y + 70, 300, 50)
        if r2.collidepoint(mx, my):
            self.toggle_tts(); self.manager.audio.play_sound("click"); return
            
        # 3. SFX (Ses Efektleri)
        r3 = pygame.Rect(center_x - 150, start_y + 140, 300, 50)
        if r3.collidepoint(mx, my):
            self.toggle_sfx()
            if self.manager.audio.sfx_enabled: self.manager.audio.play_sound("click")
            return
            
        # 4. Şekiller (Erişilebilirlik)
        r4 = pygame.Rect(center_x - 150, start_y + 210, 300, 50)
        if r4.collidepoint(mx, my):
            self.toggle_helpers(); self.manager.audio.play_sound("click"); return
            
        # 5. Devam Et
        r5 = pygame.Rect(center_x - 150, start_y + 300, 300, 60)
        if r5.collidepoint(mx, my):
            self.state = "playing"; self.manager.audio.play_sound("click"); return

    def handle_event(self, event):
        """Pygame olay döngüsü (Event Loop) işleyicisi."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = SCALER.to_design(event.pos[0], event.pos[1])
                
                if self.state == "paused":
                    self.handle_pause_menu_click(mx, my)
                    return 

                if self.check_menu_button(mx, my): return
                if self.check_options_button(mx, my): 
                    self.state = "paused"
                    return

                if self.state == "playing":
                    # Oyun içi buton kontrolleri
                    if self.btn_shuffle_rect and self.btn_shuffle_rect.collidepoint(mx, my):
                        self.shuffle_board(); return
                    if self.btn_hint_rect and self.btn_hint_rect.collidepoint(mx, my):
                        self.use_hint(); return
                    if self.btn_undo_rect and self.btn_undo_rect.collidepoint(mx, my):
                        self.undo_last_move(); return
                    self.handle_mouse_down(event.pos)
                
                elif self.state in ["game_over", "level_complete"]:
                    action_rect = pygame.Rect(0, 0, 250, 60)
                    action_rect.center = (SCALER.screen_w//2, SCALER.screen_h//2 + 120)
                    if action_rect.collidepoint(SCALER.to_screen(mx, my)):
                       self.init_level()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.state == "playing":
                self.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.state == "playing":
                self.handle_mouse_motion(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "playing": self.state = "paused"
                elif self.state == "paused": self.state = "playing"

    def check_menu_button(self, mx, my):
        btn_rect = pygame.Rect(20, 20, 140, 50) 
        if btn_rect.collidepoint(mx, my):
            self.manager.audio.play_sound("click")
            self.manager.change_screen("menu")
            return True
        return False

    def handle_mouse_down(self, pos):
        """Taş seçimi ve sürükleme başlatma mantığı."""
        # Tıklama önceliği için taşları Z-sırasına göre (üstten alta) sırala
        sorted_tiles = sorted(self.tiles, key=lambda x: (x.layer, x.y, x.x), reverse=True)
        for t in sorted_tiles:
            if t.removed or t.in_slot or t in self.animating_matches: continue
            if t.click_check(pos):
                if t.is_blocked:
                    # Kilitli taşa tıklanırsa hata geri bildirimi ver
                    self.manager.audio.play_sound("error")
                    self.shake_timers[t] = 0.4
                    t.trigger_flash((255, 0, 0))
                    blockers = self.find_blockers(t)
                    for b in blockers: b.trigger_flash((255, 255, 255), duration=0.5)
                else:
                    # Sürüklenebilir taş seçildi
                    self.dragging_tile = t
                    self.dragging_tile.is_dragging = True
                    mx, my = SCALER.to_design(pos[0], pos[1])
                    self.drag_start_mouse_pos = (mx, my)
                    self.hinted_tiles = [] 
                    self.manager.audio.play_sound("click")
                    self.tts.speak(t.text, t.lang) # Kelimeyi seslendir
                return

    def handle_mouse_motion(self, pos):
        """Sürükleme sırasındaki taş hareketini günceller."""
        if self.dragging_tile:
            mx, my = SCALER.to_design(pos[0], pos[1])
            start_mx, start_my = self.drag_start_mouse_pos
            self.dragging_tile.drag_offset_x = mx - start_mx
            self.dragging_tile.drag_offset_y = my - start_my

    def handle_mouse_up(self, pos):
        """Taş bırakıldığında (Drop) yapılacak işlemleri yönetir."""
        if not self.dragging_tile: return
        t = self.dragging_tile
        dist = math.hypot(t.drag_offset_x, t.drag_offset_y)
        mx, my = SCALER.to_design(pos[0], pos[1])
        slot_rects = self.get_slot_rects()
        
        # Taşın bırakıldığı yer yuvalar mı?
        if slot_rects:
            slots_area = pygame.Rect(slot_rects[0].x, slot_rects[0].y, slot_rects[-1].right - slot_rects[0].x, slot_rects[0].height)
            dropped_on_slots = slots_area.collidepoint(mx, my)
        else: dropped_on_slots = False
        
        # Eğer yeterince sürüklendiyse veya yuvaya bırakıldıysa taşı oraya taşı
        if dist < 5 or dropped_on_slots: self.move_to_slot(t)
        
        t.is_dragging = False
        t.drag_offset_x = 0; t.drag_offset_y = 0; self.dragging_tile = None

    def move_to_slot(self, tile):
        """Seçilen taşı boş bir yuvaya yerleştirir."""
        try:
            slot_index = self.reserve_slots.index(None)
            self.reserve_slots[slot_index] = tile
            tile.in_slot = True
            slot_rects = self.get_slot_rects()
            target_rect = slot_rects[slot_index]
            
            # Geri alma işlemi için eski pozisyonu kaydet
            tile.return_x = tile.base_x; tile.return_y = tile.base_y; tile.return_layer = tile.layer 
            tile.base_x = target_rect.x; tile.base_y = target_rect.y; tile.layer = 100 
            
            self.move_history.append(tile); self.update_blocked_status()
        except ValueError:
            # Yuvalar doluysa hata ver
            self.shake_timers[tile] = 0.5; self.manager.audio.play_sound("error")

    def check_game_status(self):
        """
        Oyun döngüsünde sürekli çağrılır. Eşleşmeleri, oyun sonunu (Win/Lose) kontrol eder.
        """
        if self.state != "playing": return
        
        # Animasyonlar bitmeden kontrol yapma
        active_tiles = [t for t in self.reserve_slots if t is not None]
        for t in active_tiles:
            if abs(t.x - t.base_x) > 5 or abs(t.y - t.base_y) > 5: return 
            
        # Eşleşme kontrolü (Aynı ID'ye sahip taşlar)
        to_remove = []
        for i in range(len(active_tiles)):
            for j in range(i + 1, len(active_tiles)):
                t1, t2 = active_tiles[i], active_tiles[j]
                if t1.entry_id == t2.entry_id:
                    to_remove.extend([t1, t2]); break 
            if to_remove: break
            
        if to_remove:
            self.manager.audio.play_sound("match")
            # Taşları yuvalardan temizle ve animasyon listesine al
            for t in to_remove:
                if t in self.reserve_slots: self.reserve_slots[self.reserve_slots.index(t)] = None
                t.in_slot = False 
                if t not in self.animating_matches: self.animating_matches.append(t)
            
            # Boşlukları kaydırarak düzenle (Slot management)
            new_slots = [t for t in self.reserve_slots if t is not None]
            while len(new_slots) < 4: new_slots.append(None)
            self.reserve_slots = new_slots
            
            slot_rects = self.get_slot_rects()
            for i, t in enumerate(self.reserve_slots):
                if t: t.base_x = slot_rects[i].x; t.base_y = slot_rects[i].y
            
            # Eşleşenleri ortada birleştir (Görsel Efekt)
            t1, t2 = to_remove[0], to_remove[1]
            mid_x = (t1.x + t2.x) / 2; mid_y = 50 + (Tile.HEIGHT // 2) 
            for t in to_remove: t.base_x = mid_x; t.base_y = mid_y; t.layer = 200

        # Kaybetme kontrolü (Yuvalar dolu ve eşleşme yok)
        if not self.game_over:
            if all(s is not None for s in self.reserve_slots):
                self.game_over = True; self.state = "game_over"; self.manager.audio.play_sound("game_over")
                
        # Kazanma kontrolü (Tüm taşlar temizlendi)
        if not self.game_won:
            remaining = [t for t in self.tiles if not t.removed and t not in self.animating_matches]
            if not remaining and not self.animating_matches:
                self.game_won = True; self.state = "level_complete"; self.state_timer = 2.0; self.manager.audio.play_sound("win")
                self.save_manager.advance_word_index(self.new_words_count); self.save_manager.next_level()

    def spawn_explosion(self, x, y):
        """Eşleşme anında parçacık efekti (Particle System) oluşturur."""
        colors = [(255, 255, 255), (255, 255, 255), (255, 255, 240), (255, 215, 0), (200, 200, 200)]
        for _ in range(30): 
            col = random.choice(colors)
            self.particles.append(Particle(x + random.randint(0, 80), y + random.randint(0, 100), col))

    def update(self, dt):
        """
        Oyunun her karesinde (frame) durumu günceller.
        Animasyonlar, zamanlayıcılar ve fiziksel hareketler burada işlenir.
        """
        if self.state == "intro":
            self.state_timer -= dt
            if self.state_timer <= 0: self.state = "playing"; self.manager.audio.play_sound("start")
            
        self.check_game_status()
        
        # Bileşen güncellemeleri
        for t in self.tiles: t.update(dt) 
        for p in self.particles[:]:
            p.update(); 
            if p.life <= 0: self.particles.remove(p)
            
        # Eşleşme animasyonu hareketi
        for t in self.animating_matches[:]:
            dx = t.base_x - t.x; dy = t.base_y - t.y; dist = math.sqrt(dx*dx + dy*dy)
            if dist > 10: t.x += dx * 5 * dt; t.y += dy * 5 * dt
            else: self.spawn_explosion(t.x, t.y); t.removed = True; self.animating_matches.remove(t)
        
        # Titreme efekti zamanlayıcısı
        keys_to_del = []
        for t, timer in self.shake_timers.items():
            timer -= dt; self.shake_timers[t] = timer
            if timer <= 0: keys_to_del.append(t); t.drag_offset_x = 0
            else: t.drag_offset_x = random.randint(-5, 5)
        for k in keys_to_del: del self.shake_timers[k]
        
        # Diğer zamanlayıcılar
        if self.hint_timer > 0: self.hint_timer -= dt; 
        if self.hint_timer <= 0: self.hinted_tiles = []
        if self.is_shuffling: self.shuffle_timer -= dt; 
        if self.shuffle_timer <= 0: self.is_shuffling = False
        
        # Taşların hedeflerine doğru yumuşak hareketi (Lerp benzeri)
        base_speed = 3.0 if self.is_shuffling else 25.0; anim_speed = base_speed * dt 
        for t in self.tiles:
            if not t.is_dragging and not t.removed and t not in self.animating_matches:
                diff_x = t.base_x - t.x
                if abs(diff_x) > 0.5: t.x += diff_x * anim_speed
                else: t.x = t.base_x
                diff_y = t.base_y - t.y
                if abs(diff_y) > 0.5: t.y += diff_y * anim_speed
                else: t.y = t.base_y

    def draw_wood_button(self, surface, rect, text, is_hover):
        """Özel ahşap temalı UI butonu çizimi."""
        fill_color = COLORS["wood_light"] if is_hover else COLORS["wood_mid"]
        border_color = COLORS["wood_dark"]
        shadow_rect = rect.move(4, 4)
        
        # Gölge ve Ana Gövde
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=15)
        pygame.draw.rect(surface, fill_color, rect, border_radius=15)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)
        
        # Parlama efekti (Highlight)
        highlight_rect = pygame.Rect(rect.x + 5, rect.y + 5, rect.width - 10, rect.height // 2)
        s = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 30), s.get_rect(), border_radius=10)
        surface.blit(s, highlight_rect)
        
        # Metin
        text_surf = self.font_btn.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        shadow_text = self.font_btn.render(text, True, (60, 40, 20))
        shadow_text_rect = text_rect.move(2, 2)
        surface.blit(shadow_text, shadow_text_rect)
        surface.blit(text_surf, text_rect)

    def draw_bottom_buttons(self, surface):
        """Ekranın altındaki yuvarlak kontrol butonlarını çizer."""
        center_x = DESIGN_W // 2
        bottom_y = DESIGN_H - 80
        radius = 40
        gap = 20
        self.btn_shuffle_rect = pygame.Rect(center_x - radius*3 - gap, bottom_y - radius, radius*2, radius*2)
        self.btn_hint_rect = pygame.Rect(center_x - radius, bottom_y - radius, radius*2, radius*2)
        self.btn_undo_rect = pygame.Rect(center_x + radius + gap, bottom_y - radius, radius*2, radius*2)
        buttons = [
            {"rect": self.btn_shuffle_rect, "img_key": "shuffle", "color": COLORS["wood_mid"]},
            {"rect": self.btn_hint_rect, "img_key": "hint", "color": COLORS["wood_mid"]},
            {"rect": self.btn_undo_rect, "img_key": "undo", "color": COLORS["wood_mid"]}
        ]
        for btn in buttons:
            sx, sy = SCALER.to_screen(btn["rect"].centerx, btn["rect"].centery)
            s_radius = SCALER.scale(radius)
            pygame.draw.circle(surface, (0,0,0,80), (sx+2, sy+4), s_radius)
            pygame.draw.circle(surface, btn["color"], (sx, sy), s_radius)
            pygame.draw.circle(surface, COLORS["wood_dark"], (sx, sy), s_radius, 3)
            img = self.icons.get(btn["img_key"])
            if img:
                icon_size = int(s_radius * 1.2) 
                scaled_icon = pygame.transform.smoothscale(img, (icon_size, icon_size))
                icon_rect = scaled_icon.get_rect(center=(sx, sy))
                surface.blit(scaled_icon, icon_rect)
            else:
                fallback_txt = btn["img_key"][0].upper()
                txt_surf = self.font_btn.render(fallback_txt, True, (255,255,255))
                txt_rect = txt_surf.get_rect(center=(sx, sy))
                surface.blit(txt_surf, txt_rect)

    def draw(self, surface):
        """
        Tüm sahneyi (Arka plan, UI, Taşlar, Efektler) render eder.
        """
        # Arka plan gradyanı
        theme = self.bg_themes[self.current_bg_index]
        surface.fill(theme["bot"])
        for y in range(0, SCALER.screen_h, 2): 
            ratio = y / SCALER.screen_h
            r = int(theme["top"][0] * (1-ratio) + theme["bot"][0] * ratio)
            g = int(theme["top"][1] * (1-ratio) + theme["bot"][1] * ratio)
            b = int(theme["top"][2] * (1-ratio) + theme["bot"][2] * ratio)
            pygame.draw.line(surface, (r,g,b), (0, y), (SCALER.screen_w, y), 2)

        # Üst UI (Menü Butonu)
        design_btn_rect = pygame.Rect(20, 20, 140, 50) 
        mx, my = pygame.mouse.get_pos()
        design_mx, design_my = SCALER.to_design(mx, my)
        is_hover = design_btn_rect.collidepoint(design_mx, design_my)
        sx, sy = SCALER.to_screen(design_btn_rect.x, design_btn_rect.y)
        sw = SCALER.scale(design_btn_rect.width)
        sh = SCALER.scale(design_btn_rect.height)
        screen_btn_rect = pygame.Rect(sx, sy, sw, sh)
        self.draw_wood_button(surface, screen_btn_rect, "MENÜ", is_hover)
        
        # Ayarlar Butonu (Hamburger Menü İkonu)
        opt_btn_rect = pygame.Rect(DESIGN_W - 80, 20, 60, 60) 
        is_hover_opt = opt_btn_rect.collidepoint(design_mx, design_my)
        sx, sy = SCALER.to_screen(opt_btn_rect.x, opt_btn_rect.y)
        sw, sh = SCALER.scale(opt_btn_rect.width), SCALER.scale(opt_btn_rect.height)
        screen_opt_rect = pygame.Rect(sx, sy, sw, sh)
        self.draw_wood_button(surface, screen_opt_rect, "", is_hover_opt) 
        cx, cy = screen_opt_rect.centerx, screen_opt_rect.centery
        line_w = SCALER.scale(30)
        line_h = SCALER.scale(5)
        spacing = SCALER.scale(10)
        icon_col = (60, 40, 20) 
        pygame.draw.rect(surface, icon_col, (cx - line_w//2, cy - line_h//2, line_w, line_h), border_radius=2)
        pygame.draw.rect(surface, icon_col, (cx - line_w//2, cy - line_h//2 - spacing, line_w, line_h), border_radius=2)
        pygame.draw.rect(surface, icon_col, (cx - line_w//2, cy - line_h//2 + spacing, line_w, line_h), border_radius=2)
        
        # Seviye Bilgisi
        lvl = self.current_level_num
        lvl_txt = self.font_ui.render(f"Level: {lvl}", True, (255, 255, 255))
        surface.blit(lvl_txt, (SCALER.screen_w - 220, 35))

        # Öğretici Metin
        if self.tutorial_text:
            tut_surf = self.font_btn.render(self.tutorial_text, True, (255, 255, 200))
            tut_rect = tut_surf.get_rect(center=(SCALER.screen_w // 2, 220))
            bg_rect = tut_rect.inflate(20, 10)
            pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect, border_radius=10)
            surface.blit(tut_surf, tut_rect)
        
        # Eşleştirme Yuvaları (Slots)
        slot_rects = self.get_slot_rects()
        for i, rect in enumerate(slot_rects):
            sx, sy = SCALER.to_screen(rect.x, rect.y)
            sw, sh = SCALER.scale(rect.width), SCALER.scale(rect.height)
            pygame.draw.rect(surface, COLORS["wood_mid"], (sx, sy, sw, sh), border_radius=Tile.RADIUS)
            inset = 4
            pygame.draw.rect(surface, COLORS["wood_shadow"], (sx+inset, sy+inset, sw-(inset*2), sh-(inset*2)), border_radius=Tile.RADIUS)
            pygame.draw.rect(surface, COLORS["wood_dark"], (sx, sy, sw, sh), 3, border_radius=Tile.RADIUS)

        self.draw_bottom_buttons(surface)

        # Taşların Çizimi (Z-Order ile sıralı)
        draw_order = sorted(self.tiles, key=lambda x: (x.in_slot, x.layer, x.y, x.x))
        for t in draw_order:
            if t != self.dragging_tile and t not in self.animating_matches:
                t.draw(surface, self.font)
        
        # Efektler ve Üst Katmanlar
        for t in self.animating_matches: t.draw(surface, self.font)
        for p in self.particles: p.draw(surface)
        
        for t in self.hinted_tiles:
            if not t.removed and not t.in_slot:
                sx, sy = SCALER.to_screen(t.x, t.y)
                sw, sh = SCALER.scale(Tile.WIDTH), SCALER.scale(Tile.HEIGHT)
                hint_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
                pygame.draw.rect(hint_surf, (255, 255, 150, 120), (0, 0, sw, sh), border_radius=Tile.RADIUS)
                pygame.draw.rect(hint_surf, (255, 255, 0), (0, 0, sw, sh), 4, border_radius=Tile.RADIUS)
                surface.blit(hint_surf, (sx, sy))
                
        if self.dragging_tile: self.dragging_tile.draw(surface, self.font)
            
        # Arayüz Katmanları (Overlays)
        if self.state == "intro":
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0,0))
            txt = self.font_big.render(self.level_message, True, (255, 255, 255))
            rect = txt.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h//2))
            surface.blit(txt, rect)
            
        elif self.state == "paused":
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0,0))
            
            center_x, center_y = DESIGN_W // 2, DESIGN_H // 2
            start_y = center_y - 80
            
            title_surf = self.font_big.render("AYARLAR", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h//2 - 150))
            surface.blit(title_surf, title_rect)
            
            btns = [
                ("Arkaplan: " + theme["name"], pygame.Rect(center_x - 150, start_y, 300, 50)),
                (f"Seslendirme: {'AÇIK' if self.tts.enabled else 'KAPALI'}", pygame.Rect(center_x - 150, start_y + 70, 300, 50)),
                (f"Oyun Sesi: {'AÇIK' if self.manager.audio.sfx_enabled else 'KAPALI'}", pygame.Rect(center_x - 150, start_y + 140, 300, 50)),
                (f"Şekiller: {'AÇIK' if self.show_helpers else 'KAPALI'}", pygame.Rect(center_x - 150, start_y + 210, 300, 50)),
                ("Devam Et", pygame.Rect(center_x - 150, start_y + 300, 300, 60))
            ]
            
            for txt, rect in btns:
                sx, sy = SCALER.to_screen(rect.x, rect.y)
                sw, sh = SCALER.scale(rect.width), SCALER.scale(rect.height)
                screen_r = pygame.Rect(sx, sy, sw, sh)
                m_screen_x, m_screen_y = pygame.mouse.get_pos()
                is_h = screen_r.collidepoint(m_screen_x, m_screen_y)
                self.draw_wood_button(surface, screen_r, txt, is_h)

        elif self.state in ["game_over", "level_complete"]:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0,0))
            
            if self.state == "level_complete":
                msg = "TEBRİKLER!"
                sub_msg = f"Level {lvl} Tamamlandı!"
                btn_msg = "Sonraki Seviye"
                color = (100, 255, 100)
            else:
                msg = "OYUN BİTTİ!"
                sub_msg = "Tekrar Dene"
                btn_msg = "Yeniden Başlat"
                color = (255, 80, 80)
                
            txt_surf = self.font_big.render(msg, True, color)
            txt_rect = txt_surf.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h//2 - 40))
            surface.blit(txt_surf, txt_rect)
            
            sub_surf = self.font_ui.render(sub_msg, True, (220, 220, 220))
            sub_rect = sub_surf.get_rect(center=(SCALER.screen_w//2, SCALER.screen_h//2 + 30))
            surface.blit(sub_surf, sub_rect)
            
            action_rect = pygame.Rect(0, 0, 280, 70)
            action_rect.center = (SCALER.screen_w//2, SCALER.screen_h//2 + 130)
            
            pygame.draw.rect(surface, COLORS["wood_mid"], action_rect, border_radius=15)
            pygame.draw.rect(surface, COLORS["wood_light"], action_rect, 4, border_radius=15)
            
            btn_txt_surf = self.font_btn.render(btn_msg, True, (255, 255, 255))
            btn_txt_rect = btn_txt_surf.get_rect(center=action_rect.center)
            surface.blit(btn_txt_surf, btn_txt_rect)