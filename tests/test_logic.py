import pytest
from src.systems.vocab_loader import VocabLoader
from src.settings import get_scale

def test_load_sample_vocab():
    """
    VocabLoader sınıfının örnek veri yükleme işlevini (mock data) test eder.
    Dönen veri yapısının bir sözlük (dictionary) olduğunu ve beklenen
    anahtar kelimeleri (örn: 'hello') içerip içermediğini doğrular.
    """
    vocab = VocabLoader.load_sample()
    assert isinstance(vocab, dict)
    assert "hello" in vocab

def test_scale_default():
    """
    Varsayılan ekran çözünürlüğü senaryosunda (800x600) ölçekleme hesaplamasını test eder.
    Hesaplanan ölçek faktörünün, kayan noktalı sayı toleransı (float tolerance)
    dahilinde 1.0 değerine eşit olup olmadığını kontrol eder.
    """
    s = get_scale((800,600))
    assert s == pytest.approx(1.0)
