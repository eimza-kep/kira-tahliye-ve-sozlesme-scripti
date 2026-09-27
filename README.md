# Kira Sözleşmesi, Yasal Artış ve Tahliye Taahhütnamesi Portalı

[![CI Test Suite](https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti/actions/workflows/ci.yml)
[![Canlı Demo](https://img.shields.io/badge/Demo-Canl%C4%B1%20Test%20Et-brightgreen.svg)](https://eimza-kep.github.io/kira-tahliye-ve-sozlesme-scripti/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)

Ev sahipleri, kiracılar, emlak danışmanları, hukuk büroları ve mülk yönetim şirketleri için; 6098 sayılı Türk Borçlar Kanunu (TBK m. 344 ve 352) hükümleri doğrultusunda **kira sözleşmelerini arşivleyen**, **TÜFE oranlı yasal tavan kira artışını anlık hesaplayan** ve **hukuken geçerli resmi Tahliye Taahhütnamesi basan** açık kaynaklı mülk yönetim yazılımı.

---

## 🎯 Temel Yetenekler

- **TBK 344 Yasal TÜFE Kira Artış Hesaplayıcı:** Konut ve çatılı işyerleri için 12 aylık ortalama TÜFE tavan artış oranına göre yeni dönem kira bedelini ve artış farkını anında hesaplar.
- **TBK 352 Uyumlu Resmi Tahliye Taahhütnamesi Çıktısı:** Yargıtay içtihatları gereğince kira sözleşmesi başlangıcından sonraki bir tanzim tarihini esas alan, cebri icra ve tahliye taahhüdünü içeren yazdırılabilir veya PDF olarak saklanabilir resmi belge üretir.
- **Kira ve Mülk Portföy Yönetim Paneli (`/admin`):**
  - Tüm kiracıların, mülk sahiplerinin ve kira bedellerinin tek ekranda takibi.
  - **Yaklaşan Tahliye / Artış Dönemi Alarmı:** Önümüzdeki 45 gün içinde kira dönemi yenilenecek veya tahliyesi taahhüt edilen taşınmazları listeleme.
  - Durum takibi: "Sözleşme Aktif", "Kira Artış Dönemi", "İhtar Çekildi (Temerrüt)", "Tahliye Edildi".
  - Aylık toplam kira gelir portföyü analitiği.
  - Excel uyumlu UTF-8 BOM destekli tek tıkla **CSV Dışa Aktarımı**.
- **Sıfır Bağımlılık (Zero-Dependency):**
  - **Python Motoru:** Dahili SQLite veritabanı ile tek tıkla lokalde veya sunucuda çalışır (`server.py`).
  - **PHP Motoru:** Paylaşımlı hosting ve cPanel için hazır JSON REST backend (`api.php`).
  - **Offline Mod:** İnternetsiz çalışma ve tarayıcı yerel hafızası (`localStorage`) desteği.

---

## 🚀 Hızlı Başlangıç

### Windows (Tek Tıkla Çalıştır)
1. Repoyu klonlayın veya indirin.
2. `Baslat.bat` dosyasına çift tıklayın.
3. Otomatik olarak açılır:
   - Kira & Taahhüt Formu: `http://localhost:8092`
   - Mülk Yönetim Paneli: `http://localhost:8092/admin`

### Linux & macOS
```bash
git clone https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti.git
cd kira-tahliye-ve-sozlesme-scripti
chmod +x baslat.sh
./baslat.sh
```

### PHP / Paylaşımlı Hosting
Dosyaları sunucunuzdaki `/kira/` veya `/emlak/` dizinine yükleyin. `api.php` otomatik olarak JSON veritabanını oluşturup yönetecektir.

---

## 📊 Mimari ve Dosya Yapısı

```
kira-tahliye-ve-sozlesme-scripti/
├── index.html              # Kira formu, TÜFE hesaplayıcı ve tahliye taahhütnamesi çıktısı
├── admin.html              # Mülk ve kira portföy takip paneli
├── server.py               # Standalone Python SQLite HTTP sunucusu (Port 8092)
├── api.php                 # PHP tabanlı REST backend
├── Baslat.bat              # Windows tek tıkla başlatıcı
├── baslat.sh               # Linux / macOS başlatıcı
├── scripts/
│   └── test_kira.py        # Otomatik test paketi
├── .github/
│   └── workflows/ci.yml    # GitHub Actions CI testi
└── README.md               # Dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

```bash
python scripts/test_kira.py
```

---

## 🌐 LegalTech & E-Dönüşüm Açık Kaynak Ekosistemi

Bu kira yönetim ve tahliye portali, [@eimza-kep](https://github.com/eimza-kep) açık kaynak ekosisteminin gayrimenkul hukuku modülüdür. İlgili diğer araçlar:

* ⚖️ [avukat-arabuluculuk-basvuru-scripti](https://github.com/eimza-kep/avukat-arabuluculuk-basvuru-scripti) - 7445 sayılı Kanun uyarınca kira tahliye ve tespit davalarında zorunlu arabuluculuk portali.
* 📊 [avukat-hukuk-excel-hesaplamalari](https://github.com/eimza-kep/avukat-hukuk-excel-hesaplamalari) - Kira artış TÜFE oranları, faiz ve tahliye icra masraf hesaplayıcıları.
* 📨 [kep-adresi-dogrulayici](https://github.com/eimza-kep/kep-adresi-dogrulayici) - Kira fesih ve temerrüt ihtarnamelerinde resmi KEP adresi sözdizim doğrulayıcı.
* 📄 [python-pdf-eimza-dogrulayici](https://github.com/eimza-kep/python-pdf-eimza-dogrulayici) - Dijital imzalı kira sözleşmeleri ve tahliye taahhütnameleri doğrulama kütüphanesi.
* 🌟 [awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum) - Türkiye e-Dönüşüm açık kaynak araçları ve kütüphaneleri kürasyonu.

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmuştur.

