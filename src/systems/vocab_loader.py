import json
import os
import random

class VocabLoader:
    """
    JSON tabanlı kelime veri paketlerini diskten yükleyen, CEFR seviyelerine göre (A1-C2)
    sıralayan ve oyun mekaniği için gerekli kelime çiftlerini (yeni + tekrar) hazırlayan
    veri yönetim sınıfı.
    """
    def __init__(self, data_path="data/vocab"):
        self.data_path = data_path
        self.vocab_list = []
        # Başlangıçta tüm kelime paketlerini yükle ve zorluk seviyesine göre sırala
        self.load_and_sort_packs()

    def load_and_sort_packs(self):
        """
        Belirtilen veri yolundaki tüm JSON dosyalarını okur, içerikleri tek bir listede
        birleştirir ve dil seviyesine göre (A1 -> C2) sıralar.
        """
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            return

        # Tüm dosyaların yüklenmesi ve verilerin birleştirilmesi
        all_words = []
        for filename in os.listdir(self.data_path):
            if filename.endswith(".json"):
                full_path = os.path.join(self.data_path, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_words.extend(data)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        # Kelimelerin pedagojik sıraya (CEFR standartları) göre dizilmesi
        level_order = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}
        # Seviyesi belirtilmemiş kelimeler varsayılan olarak A1 kabul edilir
        self.vocab_list = sorted(all_words, key=lambda x: level_order.get(x.get("level", "A1"), 0))

    def get_level_pairs(self, count, start_index, review_count=0, used_word_ids=None):
        """
        Oyun turu için gerekli kelime çiftlerini oluşturur.
        Aralıklı tekrar (Spaced Repetition) prensibini uygulayarak yeni kelimelerle
        eski kelimeleri harmanlar.

        Args:
            count: Toplam oluşturulacak çift sayısı.
            start_index: Yeni kelimelerin alınmaya başlanacağı indeks (İlerleme durumu).
            review_count: Önceki kelimelerden kaç tanesinin tekrar edileceği.
           used_word_ids: Daha before used (kullanılan kelime kimliklerinin listesi)
        """
        total_available = len(self.vocab_list)
        if total_available == 0: return []

        # 1. Yeni öğrenilecek kelime sayısının hesaplanması
        new_words_needed = count - review_count
        if new_words_needed < 0: new_words_needed = 0
        
        # Daha önce kullanılan kelimeleri hariç tut
        if used_word_ids is None:
            used_word_ids = set()
        else:
            used_word_ids = set(used_word_ids)
        end_index = min(start_index + new_words_needed, total_available)
        selected_entries = []
        used_ids = set(used_word_ids)
        for i in range(start_index, end_index):
            entry = self.vocab_list[i]
            if entry['id'] not in used_ids:
                selected_entries.append(entry)
                used_ids.add(entry['id'])
        
        # 2. Gerekli sayı yeterli değilse, kelimeleri baştan başlayarak sırayla (tekrar etmeden) tamamlayın.
        if len(selected_entries) < count:
            # Kelimeleri sırayla (baştan başlayarak) gözden geçirin
            review_candidates = [w for w in self.vocab_list if w['id'] not in used_ids]
            needed = count - len(selected_entries)
            selected_entries.extend(review_candidates[:needed])

        # Oyun motoru için çiftlerin (İngilizce - Türkçe) oluşturulması
        pairs = []
        for entry in selected_entries:
            pairs.append({'entry_id': entry['id'], 'text': entry["en"], 'lang': "en"})
            pairs.append({'entry_id': entry['id'], 'text': entry["tr"], 'lang': "tr"})

        # Taşların oyun tahtasına rastgele dağılması için karıştır
        random.shuffle(pairs)
        return pairs, len(selected_entries), [entry['id'] for entry in selected_entries] # Çiftler, İlerleme, Yeni Kelime Kimlikleri