# Dil Eşle: Yeni Nesil Dil Öğrenme Platformu 🎮📚

**Dil Eşle**, İngilizce ve Türkçe kelimeleri görsel hafıza ve stratejiyle öğrenmeyi amaçlayan, dinamik ve zorlu bir bulmaca oyunudur.
Her seviye, oyuncunun dil bilgisi gelişimine paralel olarak zorlaşır ve kalıcı öğrenmeyi destekler.

---

## 🚀 Temel Özellikler

- **🧠 Stratejik Görsel Hafıza:** Kelimeleri sadece okuyarak değil, 3 boyutlu bir düzlemde stratejik olarak eşleştirerek öğretir.
- **📈 Adaptif Zorluk Sistemi:** Kelime veritabanı, Avrupa Dilleri Ortak Çerçeve Programı'na (CEFR) göre **A1'den C2'ye** kadar sıralanmıştır ve oyuncunun ilerlemesine göre zorlaşır.
- **🔊 Akıllı Ses Sentezi (TTS):** Google TTS teknolojisini kullanarak kelimelerin telaffuzunu anlık oluşturur. Çoklu iş parçacığı sayesinde oyun akışı kesintiye uğramaz.
- **🎛️ Algoritmik Bölüm Tasarımı:** Her seviye, özel algoritmalarla sıfırdan oluşturulur; blokların dizilimi her oyunda farklıdır, ezberciliği önler.
- **📱 Duyarlı Arayüz:** Özel ölçeklendirme motoru ile oyun, her türlü ekran çözünürlüğüne otomatik uyum sağlar.

---

## 🎯 Oyun Seviyeleri ve İlerleme

- **Seviye Atlama:** Ekranı bloklardan temizleyerek bir sonraki seviyeye geçebilirsiniz.

---

## 🕹️ Nasıl Oynanır? (Oyun Mekaniği)

- **Etkileşim:** Blokları seçmek için sol tıklayın.
- **Eşleştirme Kuralı:** Üzerinde aynı kelimenin İngilizcesi ve Türkçesi yazan blokları eşleştirin.
- **Serbest Blok Kuralı:** Bir bloğu seçmek için:

  1. Üzerinde başka blok olmamalı.
  2. Sağ veya sol kenarlarından en az biri boş olmalı.
     _(Yanları ve üzeri kapalı bloklar kilitlidir, seçilemez.)_

**Yardımcı Araçlar:**

- **Karıştır (Shuffle):** Hamle kalmadığında blokları yeniden dizer.
- **İpucu (Hint):** Eşleşen bir çifti gösterir.
- **Geri Al (Undo):** Son hatayı geri alır.

---

## 📁 Proje Yapısı

```
Dil Eşle/
├── main.py                    # Uygulama giriş noktası (Entry Point)
├── requirements.txt           # Python bağımlılıkları
├── README.md                  # Bu dosya
├── save_data.json             # Oyuncu kaydı (Save Data)
├── data/
│   ├── user_settings.json     # Kullanıcı ayarları (Dil, Ses, vb.)
│   └── vocab/
│       └── sample_en_tr.json  # İngilizce-Türkçe kelime veri seti
├── src/
│   ├── main.py                # Ana oyun sınıfı (MahjongGame)
│   ├── settings.py            # Uygulama konfigürasyonu
│   ├── components/            # Oyun bileşenleri
│   │   ├── tile.py            # Kelime taşı sınıfı
│   │   ├── particle.py        # Parçacık efekt sistemi
│   │   └── slot.py            # Eşleştirme yuvası
│   ├── screens/               # Ekran yöneticisi
│   │   ├── menu_screen.py     # Ana menü ve ayarlar ekranı
│   │   ├── game_screen.py     # Oyun oynatma ekranı
│   │   └── screen_manager.py  # Ekran geçişleri
│   ├── systems/               # Sistem modülleri
│   │   ├── audio.py           # Ses yönetimi
│   │   ├── vocab_loader.py    # Kelime yükleme ve sıralama
│   │   ├── save_manager.py    # Oyun kaydı ve yükleme
│   │   └── tts_manager.py     # Metin okuma (Text-to-Speech)
│   └── utils/
│       └── text_utils.py      # Metin işleme yardımcı fonksiyonları
├── assets/
│   ├── fonts/                 # Yazı tipleri
│   ├── images/                # Görsel varlıkları
│   └── sounds/                # Ses dosyaları
└── tests/
    └── test_logic.py          # Birim testler

```

## ⚙️ Kurulum ve Başlangıç

1. **Gereksinimleri Yükleyin:**
   Python yüklü olduğundan emin olun ve terminalde çalıştırın:

   ```bash
   pip install -r requirements.txt
   ```

   _(Gerekli kütüphaneler: `pygame`, `gTTS`, `pytest`)_

2. **Oyunu Başlatın:**

   ```bash
   python main.py
   ```

---

İyi Eğlenceler! :)
