# VRP Model V2 - Modüler Araç Rotalama ve Konumlandırma Paketi

Bu proje, Heterojen Filo Araç Rotalama Problemi (HVRP) ve İki Aşamalı Konum-Rotalama Problemini (2E-LRP) çözmek için geliştirilmiş modüler bir Python kütüphanesidir. Gurobi optimizasyon motorunu kullanarak farklı senaryoları ve stratejileri analiz etmenize olanak tanır.

## Proje Yapısı

Kod tabanı `src/` klasörü altında modüler bir yapıda organize edilmiştir:

- **`main.py`**: Tekil deneyleri çalıştırmak için ana giriş noktasıdır.
- **`run_all.py`**: Akademik çalışmalar için **tüm olası senaryo kombinasyonlarını (16 adet)** otomatik olarak çalıştıran toplu işlem scriptidir.
- **`modules/`**:
  - `locators.py`: Depo yer seçimi stratejileri (Fixed, P-Median, Centroid).
  - `routers.py`: Matematiksel modellerin (VRP ve LRP) Gurobi uygulamaları.
- **`common/`**:
  - `vehicles.py`: Filo tanımları (E-Bike, E-Car vb.).
  - `plotting.py`: Rota görselleştirme araçları.
  - `data_gen.py`: Rastgele veri seti oluşturucu.

## Kurulum ve Gereksinimler

Bu proje, modern Python paket yöneticisi **`uv`** ile çalışacak şekilde yapılandırılmıştır. Ayrıca optimizasyon için **Gurobi Optimizer** lisansı gereklidir.

1. **Gereksinimler**:
    - Python 3.10+
    - `uv` (Universal Viewer / Package Manager)
    - Gurobi License (`gurobipy`)

2. **Çalıştırma**:
    Sanal ortamı kurmanıza gerek yoktur, `uv run` komutu gerekli bağımlılıkları otomatik olarak yönetir.

## Kullanım

### 1. Tekil Senaryo Çalıştırma (`main.py`)

Belirli bir senaryoyu ve parametre setini test etmek için `main.py` kullanılır.

**Parametreler:**

- `--scenario`: Senaryo 0-3 arası (0=Baz, 1=Dinamik, 2=Parametrik, 3=LRP)
- `--locator`: Depo seçim stratejisi (`fixed`, `p-median`, `centroid`)
- `--fleet`: Filo karışımı (`homog`, `mix_1`, `mix_2`)
- `--loop-type`: Rota tipi (`closed`, `open`) - Sadece Senaryo 2 için etkilidir.
- `--candidates`: Senaryo 3 için aday depo sayısı (Varsayılan: 4).

**Örnekler:**

```bash
# Senaryo 3: LRP, P-Median Stratejisi, Karışık Filo 1
uv run python src/main.py --scenario 3 --locator p-median --fleet mix_1 --candidates 4

# Senaryo 1: Dinamik Konum (Kütle Merkezi), Homojen Filo
uv run python src/main.py --scenario 1 --locator centroid --fleet homog

# Senaryo 2: Açık Çevrim Rota (Open Loop), Karışık Filo 2
uv run python src/main.py --scenario 2 --fleet mix_2 --loop-type open --locator p-median
```

### 2. Tüm Deneyleri Çalıştırma (`run_all.py`)

Akademik analizler için tanımlanmış tüm geçerli senaryo kombinasyonlarını tek seferde çalıştırmak için bu script kullanılır. Toplamda yaklaşık 16 farklı deney gerçekleştirir.

```bash
uv run python src/run_all.py
```

Bu komut:

1. Tüm kombinasyonları (S0, S1, S2, S3) sırayla çalıştırır.
2. Her deney için çözüm görsellerini (`plot.png`) ve detaylı JSON çıktılarını `comprehensive_results/` klasörüne kaydeder.
3. Tüm sonuçların özetini içeren `summary_table.csv` dosyasını oluşturur.

## Senaryo Analizi ve Detaylı Sonuçlar

Bu çalışmada dört ana senaryo (S0, S1, S2, S3) üzerinden farklı depo yerleşimi, filo yapısı ve rota stratejilerinin lojistik maliyetler üzerindeki etkisi incelenmiştir.

### Senaryo 0: Baz Durum (Baseline)

Mevcut durumda 4 adet sabit depo ve homojen bir filo (E-Car) kullanıldığı varsayılmıştır. Bu senaryo, optimizasyon yapılmadan önceki mevcut sistemin performansını temsil eder.

### Senaryo 1: Dinamik Tek Depo (Dynamic Single Depot)

Tüm müşterilere hizmet verecek **tek bir optimal depo yerinin** belirlendiği senaryodur.

- **Centroid (Kütle Merkezi)**: Müşterilerin coğrafi dağılımının ağırlık merkezi depo olarak seçilir.
- **P-Median**: Müşteri noktalarından biri depo olarak seçilir (toplam mesafeyi minimize edecek şekilde).
Bu senaryo, birden fazla sabit depo yerine stratejik konumlandırılmış tek bir merkezin verimliliğini test eder.

### Senaryo 2: Parametrik VRP (Parametric Single Depot)

Senaryo 1'in genişletilmiş halidir. Tek depo varsayımı altında şu parametrelerin etkisi incelenir:

- **Filo Karışımı (Fleet Mix)**:
  - `Homog`: Sadece E-Car.
  - `Mix 1`: Diesel Car, E-Car, E-Bike.
  - `Mix 2`: E-Scooter, E-Bike (Mikromobilite odaklı).
- **Rota Tipi (Loop Type)**:
  - `Closed`: Araçlar depoya dönmek zorundadır.
  - `Open`: Araçlar son müşteride rotayı bitirir (Depoya dönüş maliyeti yok).

### Senaryo 3: İki Aşamalı LRP (2-Echelon Location-Routing)

En gelişmiş modeldir. İki katmanlı bir dağıtım ağı tasarlanır:

1. **Birinci Katman**: Ana depodan, seçilen "mobil depolara" (uydu depolar) kamyonlarla büyük ölçekli taşıma.
2. **İkinci Katman**: Mobil depolardan müşterilere hafif veya mikromobilite araçlarıyla son kilometre (last-mile) dağıtımı.
Konum-Rotalama Problemi (LRP) çözülerek hangi aday noktaların mobil depo olacağı ve rotalar eş zamanlı optimize edilir.

---

## Deneysel Sonuçlar

Aşağıdaki tablo, tüm senaryoların çalışma sonuçlarını özetlemektedir. "Obj" (Objective), minimize edilen toplam maliyet/mesafe fonksiyonudur.

| Senaryo | Strateji | Filo | Rota Tipi | Durum | Toplam Amaç (Obj) | Kamyon Mesafe | İkincil Maliyet | Çözüm Süresi (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **S0** | Fixed | Homog | Closed | Solved | **536.71** | 33.01 | 503.70 | 10341.24 |
| | | | | | | | | |
| **S1** | Centroid | Homog | Closed | Solved | 342.96 | 73.75 | 269.22 | 1709.44 |
| **S1** | P-Median | Homog | Closed | Solved | 364.16 | 72.16 | 292.00 | 10310.77 |
| | | | | | | | | |
| **S2** | Centroid | Homog | Closed | Solved | 342.96 | 73.75 | 269.22 | 1735.73 |
| **S2** | Centroid | Homog | Open | Solved | **253.88** | 73.75 | 180.13 | 36.25 |
| **S2** | Centroid | Mix 1 | Closed | Solved | 342.96 | 73.75 | 269.22 | 10310.99 |
| **S2** | Centroid | Mix 1 | Open | Solved | **253.88** | 73.75 | 180.13 | 50.77 |
| **S2** | Centroid | Mix 2 | Closed | Solved | 387.43 | 73.75 | 313.68 | 10601.06 |
| **S2** | Centroid | Mix 2 | Open | Solved | 280.62 | 73.75 | 206.88 | 1049.77 |
| | | | | | | | | |
| **S2** | P-Median | Homog | Closed | Solved | 364.16 | 72.16 | 292.00 | 10309.52 |
| **S2** | P-Median | Homog | Open | Solved | 244.44 | 72.16 | 172.28 | 94.57 |
| **S2** | P-Median | Mix 1 | Closed | Solved | 364.16 | 72.16 | 292.00 | 10317.92 |
| **S2** | P-Median | Mix 1 | Open | Solved | 244.44 | 72.16 | 172.28 | 383.92 |
| **S2** | P-Median | Mix 2 | Closed | Solved | 387.23 | 72.16 | 315.07 | 10589.17 |
| **S2** | P-Median | Mix 2 | Open | Solved | 258.86 | 72.16 | 186.71 | 117.75 |
| | | | | | | | | |
| **S3** | LRP (P-Median) | Homog | Closed | Solved | 307.27 | 110.68 | 196.59 | 10308.05 |
| **S3** | LRP (P-Median) | Mix 1 | Closed | Solved | 226.85 | 110.68 | 116.17 | 10312.78 |
| **S3** | LRP (P-Median) | **Mix 2** | Closed | Solved | **202.79** | 110.68 | 92.11 | 10314.21 |

### Sonuçların Değerlendirilmesi

1. **Optimizasyonun Etkisi (S0 vs S1):**
    Mevcut sabit depolar yerine tek bir optimize edilmiş depo (Centroid) kullanılması, toplam maliyeti **536.71'den 342.96'ya (%36)** düşürmüştür. Bu, depo konumunun lojistik maliyetler üzerindeki kritik etkisini gösterir.

2. **Açık Çevrim Rota (Open Loop):**
    Senaryo 2'de görüldüğü üzere, araçların depoya dönme zorunluluğunun kaldırılması (Open Loop), maliyetlerde ciddi bir düşüş (yaklaşık **%25-30** ek kazanç) sağlamaktadır. Örneğin Centroid/Homog senaryosunda maliyet 342.96'dan 253.88'e inmiştir.

3. **Filo Karışımı ve Mikromobilite (Scenario 3):**
    En çarpıcı sonuçlar Senaryo 3 (LRP) altında gözlemlenmiştir.
    - Tek katmanlı sistemlerde (S2) "Mix 2" (mikromobilite araçları) bazen maliyeti artırırken (kısa menzil kısıtı veya kapasite nedeniyle), **çok katmanlı sistemde (S3) büyük avantaj sağlamıştır.**
    - S3 Mix 2, **202.79** toplam maliyet ile **tüm senaryoların en iyisidir.**
    - Mobil depoların müşterilere yaklaştırılması, kısa menzilli ancak düşük maliyetli E-Scooter/E-Bike kullanımını verimli hale getirmiş ve "son kilometre" teslimat maliyetlerini minimize etmiştir.

4. **Genel Kazanan:**
    **Senaryo 3 - Mix 2 (202.79 birim)**, başlangıç durumu olan **S0 (536.71 birim)**'a göre **%62'lik bir iyileşme** sağlamaktadır. Bu sonuç, modern şehir lojistiğinde hiyerarşik dağıtım ağlarının ve mikromobilite entegrasyonunun önemini kanıtlamaktadır.

## Çıktılar

Sonuçlar `solutions/` klasöründe her deney için ayrı alt klasörlerde saklanır:

- `result.json`: Sayısal veriler ve rota atamaları.
- `summary.txt`: Okunabilir özet rapor.
- `plot.png`: Rota görselleştirmesi.
