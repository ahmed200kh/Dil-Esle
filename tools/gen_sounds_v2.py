import wave
import math
import struct
import os
import random

def save_wav(filename, data, sample_rate=44100):
    """
    Oluşturulan ham ses verisini (PCM) standart WAV formatında diske kaydeder.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(data)

def generate_stone_click(duration=0.1, sample_rate=44100):
    """
    Mahjong taşlarının birbirine çarpma sesini simüle eder.
    Yüksek frekanslı gürültü (Noise Burst) ve hızlı sönümlenme (Fast Decay) kullanır.
    """
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        # Rastgele gürültü üretimi (Taş dokusu için)
        value = random.uniform(-1, 1)
        
        # Zarf (Envelope) Uygulaması:
        # Hızlı atak (Attack) ve hızlı sönümlenme (Decay) ile sert bir çarpma hissi verilir.
        if i < 100: amp = i / 100
        else: amp = math.exp(-(i-100) / (sample_rate * 0.015))
        
        # Alçak geçiren filtre (Low pass filter) etkisi simülasyonu
        # Doğrudan ham gürültüyü sönümlendirerek "taş" sesi elde edilir.
        
        value *= amp * 0.8
        packed_value = struct.pack('h', int(value * 32767.0))
        data.append(packed_value)
    return b''.join(data)

def generate_water_ambience(duration=5.0, sample_rate=44100):
    """
    Arka plan için su akışı/nehir sesi (Ambience) üretir.
    Pembe/Kahverengi gürültü (Pink/Brown Noise) yaklaşımı kullanılarak,
    beyaz gürültünün entegre edilmesiyle daha yumuşak ve doğal bir ses elde edilir.
    """
    n_samples = int(sample_rate * duration)
    data = []
    
    last_val = 0
    for i in range(n_samples):
        white = random.uniform(-1, 1)
        # Kahverengi Gürültü (Brownian Noise): Beyaz gürültünün integrali
        # Sesin daha bas ve boğuk (suyun altı gibi) duyulmasını sağlar.
        brown = (last_val + (0.02 * white)) / 1.02
        last_val = brown
        
        # Genlik Modülasyonu (AM):
        # Dalga hareketini ve su akışındaki düzensizliği simüle etmek için
        # düşük frekanslı sinüs dalgaları kullanılır.
        t = float(i) / sample_rate
        mod = 0.8 + 0.2 * math.sin(2 * math.pi * 0.2 * t) + 0.1 * math.sin(2 * math.pi * 0.5 * t)
        
        final_val = brown * mod * 0.5 # Arka plan olduğu için ses seviyesi düşürülür
        
        # Kırpma (Clipping) koruması: Değerleri -1 ile 1 arasında tut
        final_val = max(-1, min(1, final_val))
        
        packed_value = struct.pack('h', int(final_val * 32767.0))
        data.append(packed_value)
    return b''.join(data)

def generate_chime(freqs, duration=1.0, sample_rate=44100):
    """
    Melodik ses efektleri (başarı, hata vb.) için polifonik çan sesi üretir.
    Birden fazla frekansın (Harmonikler) sinüs dalgaları toplanarak akor oluşturulur.
    """
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = 0
        # Belirtilen tüm frekansları üst üste bindir (Additive Synthesis)
        for f in freqs:
            val += math.sin(2 * math.pi * f * t)
        
        # Normalizasyon: Genliği frekans sayısına bölerek bozulmayı önle
        val /= len(freqs)
        
        # Zarf (Envelope): Yumuşak bir başlangıç ve doğal sönümlenme
        if i < 500: amp = i / 500
        else: amp = math.exp(-(i-500) / (sample_rate * 0.3))
        
        val *= amp * 0.6
        packed_value = struct.pack('h', int(val * 32767.0))
        data.append(packed_value)
    return b''.join(data)

def main():
    """
    Ana prosedür: Tüm ses varlıklarını (Assets) sırayla oluşturur ve kaydeder.
    """
    assets_dir = "assets/sounds"
    
    # Taş Tıklama Sesi (Mekanik, sert)
    save_wav(f"{assets_dir}/click.wav", generate_stone_click())
    
    # Su Ambiyansı (Döngüsel çalmaya uygun)
    save_wav(f"{assets_dir}/water_ambience.wav", generate_water_ambience(10.0))
    
    # Eşleşme Sesi (Hoş bir akor - Do Majör)
    save_wav(f"{assets_dir}/match.wav", generate_chime([523.25, 659.25, 783.99])) # C Major
    
    # Hata Sesi (Uyumsuz/Dissonant tonlar)
    save_wav(f"{assets_dir}/error.wav", generate_chime([100, 105], duration=0.3))
    
    # Kazanma Sesi (Tantanlı/Fanfare bitiş)
    save_wav(f"{assets_dir}/win.wav", generate_chime([523.25, 659.25, 783.99, 1046.50], duration=2.0))

if __name__ == "__main__":
    main()