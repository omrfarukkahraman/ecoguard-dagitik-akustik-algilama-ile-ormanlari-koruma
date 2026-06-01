# EcoGuard - Dağıtık Akustik Algılama ile Ormanları Koruma Simülasyonu

Bu proje, **Necmettin Erbakan Üniversitesi Bilgisayar Mühendisliği Bölümü - Kablosuz Ağlar Dersi** kapsamında geliştirilmiş, kablosuz sensör ağları (WSN - Wireless Sensor Networks) ve dağıtık akustik algılama (DAS) prensiplerini görselleştiren interaktif bir 2.5D simülasyondur.

* **Öğrenci Adı:** Ömer Faruk Kahraman
* **Öğrenci Numarası:** 21370031058

---

## 🌟 Proje Özellikleri

1. **Dağıtık Akustik Algılama (DAS) Simülasyonu:**
   Orman zeminine yerleştirilmiş **24 adet sensör düğümü**, etrafta oluşan akustik dalgaları (motorlu testere, silah sesi, kaçak araç) algılama menzilleri doğrultusunda gerçek zamanlı olarak izler.

2. **Dinamik Ses Yayılım Modellemesi:**
   Haritaya tıklayarak oluşturulan ses olayları, farklı hız ve menzillerde (silah sesi çok hızlı ve geniş, motorlu testere orta, kaçak araç yavaş ve dar menzilli) dairesel dalgalar halinde yayılır.

3. **Çok Sıçramalı (Multi-hop) Yönlendirme ve Mesh Ağ Topolojisi:**
   Sensörler, merkezi baz istasyonuna (Gateway) doğrudan veya komşuları üzerinden aktarmalı olarak bağlanır. En kısa yol bulma algoritması (BFS tabanlı Routing) ile her sensörün Gateway'e giden en verimli kablosuz rotası otomatik çizilir.

4. **Veri Paketlerinin Görsel İletimi:**
   Ses tespit edildiğinde sensörler kırmızı renkte alarm verir ve sarı parlayan **veri paketlerini (paket parçacıkları)** kablosuz link hatları üzerinden komşudan komşuya sıçratarak Gateway'e ulaştırır. Gateway paketi aldığında alarm durumu ve tahmini olay konumu haritada işaretlenir.

5. **Dinamik Rota Onarımı (Self-Healing Network):**
   Veri paketi ileten veya aktif duran düğümlerin bataryası tükenebilir. Bataryası biten düğümler "Ölü (DEAD)" duruma geçer. Sistem, kablosuz şebekenin kopmaması için **rotaları gerçek zamanlı olarak otomatik onarır** (ölen düğümün üzerinden geçen hatlar başka aktif komşulara yönlendirilir).

6. **İnteraktif Dashboard:**
   Sağ panelde WSN şebeke bağlantı sağlığı (yüzdesel olarak), ortalama hop count derinliği, merkeze ulaşan paket sayısı, batarya durumları ve olay türlerine göre alarm geçmişi canlı olarak gösterilir.

---

## 🛠️ Gereksinimler ve Kurulum

Simülasyonu çalıştırmak için sisteminizde **Python 3** ve **Pygame** kütüphanesinin kurulu olması gerekmektedir.

### Pygame Kurulumu:
Konsol veya terminal üzerinden aşağıdaki komutla gerekli kütüphaneyi kurun:
```bash
pip install pygame
```

---

## 🚀 Simülasyonu Çalıştırma

Proje klasörünün içerisindeyken aşağıdaki komutu çalıştırarak simülasyonu başlatabilirsiniz:
```bash
python ecoguard_simulation.py
```

---

## ⌨️ Simülasyon Kontrolleri (Klavye & Fare Kılavuzu)

| Kontrol | Açıklama |
|---|---|
| **`[Sol Fare Tık]`** | Tıklanan noktada **Ağaç Kesim Sesi (Chainsaw)** dalgası üretir. (Turuncu dalga). |
| **`[Sağ Fare Tık]`** | Tıklanan noktada avcı **Silah Sesi (Gunshot)** dalgası üretir. (Kırmızı dalga - en hızlı ve uzak). |
| **`[Orta Fare Tık / C]`** | Fare imlecinin olduğu yerde **Kaçak Araç Sesi (Vehicle)** dalgası üretir. (Sarı dalga). |
| **`[SPACE]`** | Simülasyonu duraklatır veya devam ettirir. |
| **`[R]`** | Tüm ağ yapısını sıfırlar, sensör düğümlerini yeniden dağıtır ve bataryaları %100 yapar. |
| **`[H]`** | Düğümler arasındaki mavi/yeşil kablosuz haberleşme link yollarını gösterir / gizler. |
| **`[V]`** | Her sensörün algılama ve haberleşme sınır halkalarını gösterir / gizler. |

---

## 🎥 Tanıtım ve Demo Videosu

Simülasyonun çalışmasını gösteren örnek ekran kaydına, proje klasöründeki şu video dosyasından ulaşabilirsiniz:
* `NEÜ Kablosuz Ağlar - EcoGuard DAS Orman Koruma (21370031058) 2026-06-01 15-29-02.mp4`

---
*Bu proje akademik değerlendirme amacıyla hazırlanmıştır.*
