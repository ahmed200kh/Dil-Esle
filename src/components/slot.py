class Slot:
    """
    Oyun tahtası üzerindeki belirli bir konumu (x, y) temsil eden Yuva sınıfı.
    Bu sınıf, seçilen taşların (Tile) geçici olarak tutulduğu veya eşleştirildiği
    alanların yönetiminden sorumludur.
    """
    def __init__(self, x: int, y: int):
        # Yuvanın ekran üzerindeki koordinat tanımlamaları
        self.x = x
        self.y = y
        # Yuva başlangıçta boş olarak başlatılır (henüz bir taş atanmamıştır)
        self.tile = None

    def place(self, tile):
        """
        Belirtilen oyun taşını (tile) bu yuvaya yerleştirir (referans ataması).
        """
        self.tile = tile

    def remove(self):
        """
        Mevcut taşı yuvadan çıkarır, yuvayı tekrar boş duruma getirir (None)
        ve çıkarılan taşı işlem yapılmak üzere geri döndürür.
        """
        t = self.tile
        self.tile = None
        return t