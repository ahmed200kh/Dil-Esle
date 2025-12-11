import sys
import os

# Mevcut dosyanın bulunduğu dizini (proje kök dizinini) sistem yoluna ekler.
# Bu işlem, 'src' paketinin ve alt modüllerinin sorunsuz bir şekilde içe aktarılmasını sağlar.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import DilEsleGame

if __name__ == "__main__":
    """
    Uygulamanın giriş noktası (Entry Point).
    Ana oyun sınıfını örnekler (instance) ve oyun döngüsünü başlatır.
    """
    app = DilEsleGame()
    app.run()