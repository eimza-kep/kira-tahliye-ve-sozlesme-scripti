# Kira Sözleşmesi, Yasal Artış ve Tahliye Taahhütnamesi Portalı

[![CI Test Suite](https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti/actions/workflows/ci.yml)
[![Canlı Demo](https://img.shields.io/badge/Demo-Canl%C4%B1%20Test%20Et-brightgreen.svg)](https://eimza-kep.github.io/kira-tahliye-ve-sozlesme-scripti/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)
[![Docker Support](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

Ev sahipleri, kiracılar, emlak danışmanları, hukuk büroları ve mülk yönetim şirketleri için; 6098 sayılı Türk Borçlar Kanunu (TBK m. 344 ve 352) ile 5070 sayılı Elektronik İmza Kanunu hükümleri doğrultusunda **kira sözleşmelerini arşivleyen**, **TÜİK 12 Aylık TÜFE ortalamasıyla yasal tavan kira artışını anlık hesaplayan**, **TBK m.352 Yargıtay geçerlilik denetimi yapan** ve **resmi Tahliye Taahhütnamesi basan** açık kaynaklı mülk yönetim yazılımı.

---

## 🎯 Temel Yetenekler ve Özellikler

- **📊 TÜİK 12 Aylık TÜFE Ortalaması API Entegrasyonu (TBK m.344):**
  - Sözleşme yenileme tarihine göre resmi TÜİK 12 aylık TÜFE ortalama artış tavanını otomatik çeker.
  - Yeni dönem yasal kira bedelini ve artış farkını anlık hesaplar.
  - Girilen artış oranı resmi TÜİK tavanını aşarsa TBK Madde 344/2 uyarınca hukuki tavan uyarısı görüntüler.
- **⚖️ TBK 352 Uyumlu Yargıtay Geçerlilik Denetim Motoru:**
  - Yargıtay Hukuk Genel Kurulu yerleşik içtihatları doğrultusunda, tahliye taahhüdünün kira sözleşmesi başlangıcından sonraki bir tarihte tanzim edilip edilmediğini kontrol eder.
  - Aynı gün veya kira tarihinden önce imzalanan taahhütlerde "baskı altında imza" ve geçersizlik risklerini anında raporlar.
- **🔏 5070 Sayılı Kanun Uyumlu E-İmza & PDF Doğrulama:**
  - e-Devlet veya Nitelikli Elektronik Sertifika (NES) ile imzalanmış PDF sözleşmelerin PAdES-LTV standartlarını, SHA-256 dijital mühürlerini ve RFC 3161 zaman damgalarını doğrular.
- **📑 Resmi Tahliye Taahhütnamesi Çıktısı:**
  - Takip numaralı (`KIRA-2026-XXXX`), TBK 352/1 metinli, icra muvafakatli ve yazdırılabilir / PDF kaydedilebilir resmi belge üretir.
- **🏠 Kira ve Mülk Portföy Yönetim Paneli (`admin.html`):**
  - Tüm kiracıların, mülk sahiplerinin ve kira bedellerinin tek ekranda takibi.
  - **Yaklaşan Tahliye / Artış Dönemi Alarmı:** Önümüzdeki 45 gün içinde kira dönemi yenilenecek veya tahliyesi taahhüt edilen taşınmazları listeleme.
  - E-İmza ve TBK 352 hukuki geçerlilik rozetleri (`⚖️ TBK 352 Geçerli`, `🔏 5070 E-İmzalı`).
  - İmzalı PDF evraklarını tek tıkla doğrudan indirme.
  - Excel uyumlu UTF-8 BOM destekli tek tıkla **CSV Dışa Aktarımı**.
- **Sıfır Bağımlılık (Zero-Dependency) Çift Motorlu Mimari:**
  - **Python Motoru:** Dahili SQLite veritabanı ile tek tıkla lokalde veya sunucuda çalışır (`server.py`).
  - **PHP Motoru:** Paylaşımlı hosting ve cPanel için hazır JSON REST backend (`api.php`).
  - **Offline Mod:** İnternetsiz çalışma ve tarayıcı yerel hafızası (`localStorage`) desteği.

---

## 🚀 Hızlı Başlangıç ve Kurulum Rehberi

### Seçenek 1: Windows (Tek Tıkla Çalıştır)
1. Repoyu klonlayın veya indirin:
   ```bash
   git clone https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti.git
   cd kira-tahliye-ve-sozlesme-scripti
   ```
2. `Baslat.bat` dosyasına çift tıklayın.
3. Tarayıcınızda otomatik olarak açılır:
   - Kira & Taahhüt Formu: `http://localhost:8092`
   - Mülk Yönetim Paneli: `http://localhost:8092/admin`

### Seçenek 2: Linux & macOS
```bash
git clone https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti.git
cd kira-tahliye-ve-sozlesme-scripti
chmod +x baslat.sh
./baslat.sh
```

### Seçenek 3: Docker ile Çalıştırma
```bash
# Docker imajını derleyin ve başlatın
docker build -t kira-tahliye-scripti .
docker run -d -p 8092:8092 --name kira-tahliye kira-tahliye-scripti

# Tarayıcıdan erişin:
# http://localhost:8092
```

### Seçenek 4: PHP / Paylaşımlı Hosting (cPanel / Plesk)
Dosyaları sunucunuzdaki `/kira/` veya `/emlak/` dizinine yükleyin. `api.php` otomatik olarak JSON veritabanını (`kira_sozlesmeler.json`) oluşturup yönetecektir.

---

## 🔌 REST API Referansı

| Metot | Uç Nokta (Endpoint) | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/api/kira-kaydet` | Yeni kira ve taahhüt kaydeder (`eimza_verified`, `pdf_doc_base64` destekli). |
| `GET` | `/api/kiralar` | Tüm kira sözleşmelerini JSON formatında döndürür. |
| `GET` | `/api/tufe-orani?tarih=YYYY-MM` | Seçilen tarihe ait TÜİK 12 aylık TÜFE tavan artış oranını döndürür. |
| `POST` | `/api/kira-hesapla` | Mevcut kira ve TÜFE oranına göre yasal tavan ve artış tutarını hesaplar. |
| `GET` | `/api/taahhut-gecerlilik` | TBK m.352 Yargıtay içtihadı uyarınca tanzim ve başlangıç tarihlerini test eder. |
| `POST` | `/api/eimza-dogrula` | PDF dosyasının 5070 E-İmza ve SHA-256 dijital mühür doğrulamasını yapar. |
| `POST` | `/api/durum-guncelle` | Sözleşme/tahliye durumunu günceller (`tracking_code`, `status`). |
| `GET` | `/health` | Servis sağlık durumunu ve port bilgisini döndürür. |

---

## 📊 Mimari ve Dosya Yapısı

```
kira-tahliye-ve-sozlesme-scripti/
├── index.html                    # Kira formu, TÜFE hesaplayıcı ve tahliye taahhütnamesi çıktısı
├── admin.html                    # Mülk ve kira portföy takip paneli (E-İmza & Geçerlilik rozetli)
├── server.py                     # Standalone Python SQLite HTTP sunucusu (Port 8092)
├── api.php                       # PHP tabanlı REST backend
├── Baslat.bat                    # Windows tek tıkla başlatıcı
├── baslat.sh                     # Linux / macOS başlatıcı
├── Dockerfile                    # Docker konteyner konfigürasyonu
├── scripts/
│   ├── tufe_kira_calculator.py   # TÜİK 12 aylık TÜFE ortalama artış tavanı hesaplama motoru
│   ├── kira_eimza_engine.py      # 5070 E-İmza ve TBK m.352 hukuki geçerlilik motoru
│   └── test_kira.py              # Otomatik birim test paketi
├── .github/
│   └── workflows/ci.yml          # GitHub Actions CI testi
└── README.md                     # Kapsamlı dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

Tüm doğrulama motoru ve veri tabanı akışları birim testlerle korunmaktadır:

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
