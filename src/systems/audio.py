import pygame
import os

class AudioSystem:
    """
    Oyunun ses efektlerini (SFX) ve arka plan müziğini yöneten merkezi ses sistemi.
    Pygame mixer kütüphanesini kullanarak ses varlıklarını yükler, önbelleğe alır ve oynatır.
    """
    def __init__(self, volume=0.5):
        # Ses seviyesi ve durum değişkenlerinin başlatılması
        self.volume = volume
        self.sounds = {}
        self.music_playing = False
        
        # Ses efektleri (SFX) için açma/kapama kontrol bayrağı
        self.sfx_enabled = True
        
        # Pygame ses modülünün başlatılıp başlatılmadığını kontrol et, değilse başlat
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.load_assets()

    def toggle_sfx(self):
        """
        Ses efektlerinin (SFX) durumunu tersine çevirir (Açık -> Kapalı veya tam tersi).
        """
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled

    def load_assets(self):
        """
        Disk üzerindeki ses dosyalarını (.wav) belleğe yükler ve bir sözlükte saklar.
        """
        sound_dir = "assets/sounds"
        files = {
            "click": "move.wav",         
            "match": "explode.wav",      
            "shuffle": "karıştır.wav",   
            "hint": "lamba.wav",         
            "undo": "geri al.wav",       
            "start": "start.wav",
            "game_over": "game over.wav", 
            "error": "error.wav",       
            "win": "win.wav",
            "water": "water_ambience.wav"
        }
        
        for name, filename in files.items():
            path = os.path.join(sound_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.volume)
                except Exception as e:
                    # Ses yükleme hatası durumunda sessizce devam et (Hata yönetimi)
                    pass

    def play_sound(self, name):
        """
        Belirtilen isimdeki ses efektini bir kez oynatır.
        Eğer SFX kapalıysa işlem yapmaz.
        """
        # SFX devre dışıysa, oynatma işlemini atla (Müzik hariç tutulabilir)
        if not self.sfx_enabled: return
        
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, name):
        """
        Arka plan müziğini döngüsel olarak oynatır.
        """
        # Ortam sesi için özel anahtar kontrolü (Ambience logic)
        # Müzik zaten çalıyorsa tekrar başlatmayı önler.
        key = "water" if name == "water_ambience" else name
        if key in self.sounds and not self.music_playing:
            self.sounds[key].play(loops=-1, fade_ms=2000)
            self.sounds[key].set_volume(self.volume * 0.3)
            self.music_playing = True

    def start_ambience(self):
        """Varsayılan ortam sesini (su sesi vb.) başlatır."""
        self.play_music("water")

    def stop_ambience(self):
        """
        Çalan ortam sesini yavaşça (fade-out) durdurur.
        """
        if "water" in self.sounds:
            self.sounds["water"].fadeout(1000)
            self.music_playing = False