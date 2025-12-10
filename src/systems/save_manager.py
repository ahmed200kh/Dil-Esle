import json
import os

class SaveManager:
    """
    Oyunun ilerleme durumunu (seviye, kilitler, kelime indeksi) disk üzerinde
    JSON formatında saklayan ve yöneten sınıf (Persistence Manager).
    """
    def __init__(self, filename="save_data.json"):
        # Kayıt dosyasının yolu ve varsayılan veri yapısı
        self.filename = filename
        self.data = {
            "current_level": 1,        # Mevcut oynanan seviye
            "unlocked_levels": 1,      # Kilidi açılmış maksimum seviye
            "words_learned_index": 0,  # Kelime listesindeki ilerleme durumu
            "used_word_ids": [],       # Kullanılan anahtar kelime tanımlayıcılarının listesi
            "vocab_level": "A1"       # Ekstra: Seçili kelime seviyesi
        }
        # Başlangıçta mevcut kayıt varsa yükle
        self.load()
    def get_vocab_level(self):
        """Kullanıcının seçtiği kelime seviyesini döndürür."""
        return self.data.get("vocab_level", "A1")

    def set_vocab_level(self, level):
        """Kullanıcının seçtiği kelime seviyesini kaydeder."""
        self.data["vocab_level"] = level
        self.save()

    def load(self):
        """
        Disk üzerindeki kayıt dosyasını okur ve oyun verilerini belleğe yükler.
        Dosya yoksa veya okuma hatası oluşursa varsayılan değerler korunur.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.data = json.load(f)
            except:
                # Dosya bozuksa veya okunamıyorsa hata mesajı bas
                print("Error loading save file")

    def save(self):
        """
        Mevcut oyun verilerini (self.data) JSON formatında diske yazar.
        """
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def get_level(self):
        """Kullanıcının kaldığı güncel seviyeyi döndürür."""
        return self.data.get("current_level", 1)

    def next_level(self):
        """
        Oyuncuyu bir sonraki seviyeye geçirir.
        Eğer oyuncu en son açılan seviyeyi geçtiyse, kilitli seviye sayısını da günceller.
        """
        self.data["current_level"] += 1
        if self.data["current_level"] > self.data["unlocked_levels"]:
            self.data["unlocked_levels"] = self.data["current_level"]
        self.save()
        
    def get_word_index(self):
        """Kelime veri tabanında kaçıncı indiste kalındığını döndürür."""
        return self.data.get("words_learned_index", 0)
    
    def advance_word_index(self, count):
        """
        Öğrenilen kelime sayacını belirtilen miktar (count) kadar ilerletir
        ve durumu kaydeder.
        """
        self.data["words_learned_index"] += count
        self.save()

    # --- İlerlemeyi Sıfırlama Fonksiyonu ---
    def add_used_word_ids(self, ids):
        """
       Yeni kullanılan kelime kimliklerini listeye ekler ve dosyayı günceller.
        """
        if "used_word_ids" not in self.data:
            self.data["used_word_ids"] = []
        for i in ids:
            if i not in self.data["used_word_ids"]:
                self.data["used_word_ids"].append(i)
        self.save()

    def get_used_word_ids(self):
        """
       Kullanılan kelime tanımlayıcılarının bir listesini döndürür.
        """
        return self.data.get("used_word_ids", [])

    def reset_progress(self):
        """
        Tüm oyun verilerini (seviye, kilitler, kelime ilerlemesi, kelime seviyesi)
        varsayılan başlangıç değerlerine döndürür ve dosyayı günceller.
        """
        self.data = {
            "current_level": 1,
            "unlocked_levels": 1,
            "words_learned_index": 0,
            "used_word_ids": [],
            "vocab_level": "A1"
        }
        self.save()