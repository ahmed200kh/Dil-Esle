"""
Seviye Atlama Yardımcısı (Level Jump Helper)
Farklı seviyeleri kolayca denemek için ayrı bir dosya
Oyun geliştirme süreci bittikten sonra silinebilir
"""

import json
import os
from src.systems.save_manager import SaveManager

class LevelJumper:
    """
    Seviyeleri atlamak ve doğrudan herhangi bir seviyeye geçmek için araç
    """
    def __init__(self, save_file="save_data.json"):
        self.save_manager = SaveManager(save_file)
        self.save_manager.load()
    
    def jump_to_level(self, level_num):
        """
        Belirli bir seviyeye geçiş yap
        
        Args:
            level_num: Geçilmek istenen seviye numarası (1 veya üzeri)
        """
        if level_num < 1:
            print(f"❌ Hata: Seviye numarası 1 veya daha yüksek olmalıdır")
            return False
        
        self.save_manager.data["current_level"] = level_num
        self.save_manager.data["unlocked_levels"] = level_num
        self.save_manager.save()
        
        print(f"✅ {level_num}. seviyeye geçildi")
        self.show_status()
        return True
    
    def jump_to_level_with_words(self, level_num, word_index=0):
        """
        Kelime konumunu ayarlayarak belirli bir seviyeye geçiş
        
        Args:
            level_num: Seviye numarası
            word_index: Veritabanındaki kelime konumu (0 = başlangıç)
        """
        if level_num < 1 or word_index < 0:
            print(f"❌ Hata: Girdiler geçersiz")
            return False
        
        self.save_manager.data["current_level"] = level_num
        self.save_manager.data["unlocked_levels"] = level_num
        self.save_manager.data["words_learned_index"] = word_index
        self.save_manager.save()
        
        print(f"✅ {level_num}. seviyeye geçildi")
        print(f"   Kelime konumu: {word_index}")
        self.show_status()
        return True
    
    def show_status(self):
        """Mevcut oyun durumunu göster"""
        print("\n📊 Oyun Durumu:")
        print(f"   Mevcut Seviye: {self.save_manager.data.get('current_level', 1)}")
        print(f"   Açılan En Yüksek Seviye: {self.save_manager.data.get('unlocked_levels', 1)}")
        print(f"   Kelime Konumu: {self.save_manager.data.get('words_learned_index', 0)}")
        print()
    
    def reset_progress(self):
        """İlerlemeyi başa sıfırla"""
        self.save_manager.reset_progress()
        print("✅ İlerleme başa sıfırlandı")
        self.show_status()
    
    def list_presets(self):
        """Bazı popüler seviyeleri listele"""
        presets = {
            "Başlangıç": 1,
            "Seviye 5": 5,
            "Seviye 10": 10,
            "Seviye 20": 20,
            "Seviye 50": 50,
            "Seviye 100": 100,
        }
        print("📌 Mevcut Hazır Ayarlar:")
        for name, level in presets.items():
            print(f"   {name}: jump_to_level({level})")
        print()


# ============ Doğrudan Kullanım ============
if __name__ == "__main__":
    jumper = LevelJumper()
    
    # Seçenekleri göster
    print("=" * 50)
    print("🎮 Seviye Atlama Aracı")
    print("=" * 50)
    jumper.show_status()
    jumper.list_presets()
    
    # Kullanım örneği
    while True:
        try:
            choice = input("Bir seçenek belirleyin:\n1️⃣ Seviyeye Git\n2️⃣ Sıfırla\n3️⃣ Durumu Göster\n4️⃣ Çıkış\n\nSeçiminiz: ").strip()
            
            if choice == "1":
                level = int(input("Seviye numarasını girin: "))
                jumper.jump_to_level(level)
            elif choice == "2":
                confirm = input("Emin misiniz? (y/n): ").lower()
                if confirm == "y":
                    jumper.reset_progress()
            elif choice == "3":
                jumper.show_status()
            elif choice == "4":
                print("👋 Güle güle!")
                break
            else:
                print("❌ Geçersiz seçenek")
        except ValueError:
            print("❌ Lütfen geçerli bir sayı girin")
        except Exception as e:
            print(f"❌ Hata: {e}")