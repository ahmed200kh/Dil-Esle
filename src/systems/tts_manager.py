import pygame
import os
import threading
import tempfile
from gtts import gTTS 

class TTSManager:
    """
    Metin okuma (Text-to-Speech) işlevselliğini yöneten asenkron sınıf.
    Google TTS servisini kullanarak metinleri sese dönüştürür, performans için
    dosyaları önbelleğe (cache) alır ve oyun akışını kesmemek (non-blocking) için
    ayrı bir iş parçacığında (thread) çalışır.
    """
    def __init__(self):
        # Sistem geçici klasöründe (temp) önbellek dizini oluşturulması
        self.cache_dir = os.path.join(tempfile.gettempdir(), "linguamatch_tts_cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Seslendirme özelliğinin aktiflik durumu kontrolü
        self.enabled = True 

    def toggle(self):
        """
        TTS özelliğini açıp kapatır (Toggle Switch).
        """
        self.enabled = not self.enabled
        return self.enabled

    def speak(self, text, lang):
        """
        Metni seslendirme işlemini tetikler.
        Performans kaybını (FPS düşüşünü) önlemek için işlemi ana döngüden ayırarak (threading) çalıştırır.
        """
        # Özellik devre dışıysa işlem yapmadan çık
        if not self.enabled: return

        # Arka planda çalışacak iş parçacığını (Daemon Thread) başlat
        threading.Thread(target=self._speak_thread, args=(text, lang), daemon=True).start()

    def _speak_thread(self, text, lang):
        """
        Arka planda çalışan, ağ isteğini ve dosya oynatma işlemini yürüten işçi (worker) fonksiyon.
        Önbellek mekanizması (Caching) sayesinde aynı kelime için tekrar ağ isteği yapılmaz.
        """
        try:
            # Dosya adı güvenliği için metni temizle (sadece harf ve rakamlar)
            safe_text = "".join([c for c in text if c.isalpha() or c.isdigit()]).lower()
            filename = f"{lang}_{safe_text}.mp3"
            file_path = os.path.join(self.cache_dir, filename)

            # Dosya önbellekte yoksa Google TTS API'den indir ve kaydet
            if not os.path.exists(file_path):
                tts = gTTS(text=text, lang=lang)
                tts.save(file_path)
            
            # Sesi yükle ve oynat
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(1.0)
                sound.play()
            except pygame.error:
                pass 

        except Exception as e:
            # Ağ hatası veya dosya yazma hatası durumunda hata günlüğü (Log)
            print(f"TTS Warning: Could not generate audio (Check Internet connection). Error: {e}")