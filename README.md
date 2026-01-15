# VRP Model V2 - Modüler Araç Rotalama ve Konumlandırma Paketi

Bu proje, Heterojen Filo Araç Rotalama Problemi (HVRP) ve İki Aşamalı Konum-Rotalama Problemini (2E-LRP) çözmek için geliştirilmiş modüler bir Python kütüphanesidir. Gurobi optimizasyon motorunu kullanarak farklı senaryoları ve stratejileri analiz etmenize olanak tanır.

## Proje Yapısı

Kod tabanı `src/` klasörü altında modüler bir yapıda organize edilmiştir:

- **`main.py`**: Tekil deneyleri çalıştırmak için ana giriş noktasıdır.
- **`run_all.py`**: Akademik çalışmalar için tüm olası senaryo kombinasyonlarını (yaklaşık 48 adet) otomatik olarak çalıştıran toplu işlem scriptidir.
- **`modules/`**:
  - `locators.py`: Depo yer seçimi stratejileri (Fixed, P-Median, Centroid).
  - `routers.py`: Matematiksel modellerin (VRP ve LRP) Gurobi uygulamaları.
- **`common/`**:
  - `vehicles.py`: Filo tanımları (E-Bike, E-Car vb.).
  - `plotting.py`: Rota görselleştirme araçları.
  - `data_gen.py`: Sentetik veri üretimi ve Solomon veri seti yükleyicisi.
  - `runner.py`: Deney yürütme ve raporlama modülü.

## Kurulum ve Gereksinimler

Bu proje, modern Python paket yöneticisi **`uv`** ile çalışacak şekilde yapılandırılmıştır. Ayrıca optimizasyon için **Gurobi Optimizer** lisansı gereklidir.

1. **Gereksinimler**:
    - Python 3.10+
    - `uv` (Universal Viewer / Package Manager)
    - Gurobi License (`gurobipy`)

2. **Çalıştırma**:
    Sanal ortamı kurmanıza gerek yoktur, `uv run` komutu gerekli bağımlılıkları otomatik olarak yönetir.

## Kullanım

Proje iki temel şekilde kullanılabilir: Tekil senaryo çalıştırma veya toplu deney yürütme.

### 1. Tekil Senaryo Çalıştırma (`main.py`)

Belirli bir konfigürasyonu test etmek için kullanılır.

**Temel Parametreler:**

- `--scenario`: Senaryo ID (0=Baz, 1=Dinamik, 2=Parametrik, 3=LRP)
- `--locator`: Depo seçim stratejisi (`fixed`, `p-median`, `centroid`)
- `--fleet`: Filo karışımı (`homog`, `mix_1`, `mix_2`)
- `--loop-type`: Rota tipi (`closed`, `open`) - Sadece Senaryo 2 için etkilidir.
- `--candidates`: Senaryo 3 için aday depo sayısı (Varsayılan: 4).

**Veri Parametreleri:**

- `--data-mode`: Veri üretim modu (`uniform`, `clustered`, `solomon`)
- `--data-file`: Solomon modu için dosya yolu (örn. `c101.txt`).

**Örnek Komutlar:**

```bash
# Senaryo 3: LRP, P-Median Stratejisi, Karışık Filo 1 (Varsayılan Uniform Veri)
uv run python src/main.py --scenario 3 --locator p-median --fleet mix_1 --candidates 4

# Senaryo 1: Dinamik Konum (Kütle Merkezi), Homojen Filo
uv run python src/main.py --scenario 1 --locator centroid --fleet homog

# Senaryo 2: Açık Çevrim Rota (Open Loop), Kümelenmiş Veri
uv run python src/main.py --scenario 2 --fleet mix_2 --loop-type open --data-mode clustered

# Solomon Veri Seti Kullanımı (c101 ve Senaryo 0)
uv run python src/main.py --scenario 0 --data-mode solomon --data-file c101.txt
```

### 2. Toplu Deney Yürütme

Tüm varyasyonları tek seferde çalıştırmak veya paralel çalıştırmak için seçenekler mevcuttur.

- **Otomatik Script (`run_all.py`)**: Tüm kombinasyonları (S0-S3 ve tüm veri modları için tanımlanmışsa) sırayla çalıştırır.

  ```bash
  uv run python src/run_all.py
  ```

- **Paralel Çalıştırma**: Farklı terminallerde eş zamanlı çalıştırmak için `parallel_commands.md` dosyasındaki hazır komut bloklarını kullanabilirsiniz.

## Deneysel Sonuçlar (Uniform Data)

Aşağıdaki tablo, "Uniform" veri modu ile yapılan kapsamlı deneylerin sonuçlarını göstermektedir.

| Senaryo | Strateji | Filo | Rota Tipi | Toplam Amaç (Obj) | Kamyon Mesafe | İkincil Maliyet | Süre | Gap | Kapasite Kullanımı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **S0** | Fixed | Homog | Closed | 536.71 | 33.01 | 503.70 | >27000s | 47.85% | 16.7% |
| | | | | | | | | | |
| **S1** | Centroid | Homog | Closed | 342.96 | 73.75 | 269.22 | 1597 s | 0.00% | 16.7% |
| **S1** | P-Median | Homog | Closed | 364.16 | 72.16 | 292.00 | >26000s | 3.76% | 16.7% |
| | | | | | | | | | |
| **S2** | Centroid | Homog | Closed | 342.96 | 73.75 | 269.22 | 1628 s | 0.00% | 16.7% |
| **S2** | Centroid | Homog | Open | **253.88** | 73.75 | 180.13 | 23 s | 0.00% | 16.7% |
| **S2** | Centroid | Mix 1 | Closed | 342.96 | 73.75 | 269.22 | >26000s | 4.08% | 31.7% |
| **S2** | Centroid | Mix 1 | Open | **253.88** | 73.75 | 180.13 | 38 s | 0.00% | 32.7% |
| **S2** | Centroid | Mix 2 | Closed | 387.43 | 73.75 | 313.68 | >26000s | 0.02% | 68.0% |
| **S2** | Centroid | Mix 2 | Open | 280.62 | 73.75 | 206.88 | 1009 s | 0.00% | 50.0% |
| | | | | | | | | | |
| **S2** | P-Median | Homog | Closed | 364.16 | 72.16 | 292.00 | >26000s | 3.76% | 16.7% |
| **S2** | P-Median | Homog | Open | 244.44 | 72.16 | 172.28 | 81 s | 0.00% | 16.7% |
| **S2** | P-Median | Mix 1 | Closed | 364.16 | 72.16 | 292.00 | >26000s | 4.24% | 35.4% |
| **S2** | P-Median | Mix 1 | Open | 244.44 | 72.16 | 172.28 | 370 s | 0.00% | 30.4% |
| **S2** | P-Median | Mix 2 | Closed | 387.23 | 72.16 | 315.07 | >26000s | 0.03% | 72.0% |
| **S2** | P-Median | Mix 2 | Open | 258.86 | 72.16 | 186.71 | 112 s | 0.01% | 56.7% |
| | | | | | | | | | |
| **S3** | LRP (P-Median) | Homog | Closed | 307.27 | 110.68 | 196.59 | 23974 s | 0.00% | 66.7% |
| **S3** | LRP (P-Median) | Mix 1 | Closed | 226.85 | 110.68 | 116.17 | >27000s | 7.93% | 64.2% |
| **S3** | LRP (P-Median) | **Mix 2** | Closed | **202.79** | 110.68 | 92.11 | >27000s | 17.06% | 78.0% |

## Veri Üretim Modları

Proje üç farklı veri kaynağını destekler:

1. **Uniform (Düzgün Dağılım)**: Müşteriler ve depolar harita üzerinde rastgele düzgün dağılır. Temel kıyaslamalar için varsayılandır.
2. **Clustered (Kümelenmiş)**: Müşteriler belirli merkezler etrafında öbeklenir (cluster). Gerçekçi şehir yapısını (mahalleler, iş merkezleri) simüle eder.
3. **Solomon Instance**: Akademik literatürde standart olan Solomon VRPTW veri setlerini (örn. `c101.txt`) yükler. Müşteri koordinatlarını ve taleplerini dosyadan okur.

## Senaryoların Detayları

Çalışma dört ana senaryo üzerinden kurgulanmıştır:

### Senaryo 0: Baz Durum (Baseline)

Mevcut durumda 4 adet sabit depo ve homojen bir filo (E-Car) kullanıldığı varsayılmıştır. Bu senaryo, optimizasyon yapılmadan önceki "As-Is" durumunu temsil eder.

### Senaryo 1: Dinamik Tek Depo (Dynamic Single Depot)

Tüm müşterilere hizmet verecek **tek bir optimal depo yerinin** belirlendiği senaryodur.

- **Centroid**: Ağırlık merkezi.
- **P-Median**: Müşteri noktalarından biri seçilir.

### Senaryo 2: Parametrik Rotalama (Parametric)

Tek depo varsayımı altında, "Açık Çevrim" (Open Loop) ve farklı "Filo Karışımları"nın etkisi incelenir. Dönüş zorunluluğunun kalkması maliyetleri nasıl etkiler?

### Senaryo 3: İki Aşamalı LRP (2-Echelon Location-Routing)

En gelişmiş modeldir. Ana depodan uydu depolara (fırsatçı şarj istasyonları veya mikro-hublar) ve oradan müşterilere dağıtım yapılan hiyerarşik bir ağdır. Hem depo yerleri hem de rotalar eş zamanlı optimize edilir.

## Akademik Gerekçelendirmeler ve Notlar

### Açık Çevrim Mantığı (Senaryo 2)

Açık Çevrim (Open Loop) senaryosunda, araçlar depoya geri dönmemektedir. Bu model, bağımsız kuryelerin (örn. UberEats, Amazon Flex) son teslimat noktasında mesailerini bitirdikleri veya kişisel işlerine geçtikleri **Kitlesel Kaynaklı Dağıtım (Gig Economy)** paradigmasına dayanmaktadır. Bu varsayım, dönüş maliyetini ortadan kaldırarak operasyonel maliyetleri düşürür.

### Optimallik ve Ölçeklenebilirlik (MIP Gap)

Çözüm raporlarında (`summary.txt`), **MIP Gap** değeri raporlanır. Bu değer, bulunan çözümün teorik en iyi çözümden en fazla ne kadar uzak olduğunu yüzdesel olarak gösterir.

- **Kapasite Kullanımı**: Raporlar artık her aracın ve filonun ortalama kapasite kullanım oranlarını (Capacity Utilization) da içermektedir.

## Çıktılar

Sonuçlar `solutions/` klasöründe saklanır. Klasör isimleri, kullanılan veri ve parametrelere göre otomatik oluşturulur:
Örn: `scen_3_p-median_mix_1_clustered_1736...`

Her klasör şunları içerir:

- **`summary.txt`**: Deney konfigürasyonu, çözüm süresi, maliyetler, araç yükleri ve detaylı rota raporu.
- **`result.json`**: Ham sayısal veriler (programatik analiz için).
- **`plot.png`**: Rotaların ve depo yerleşimlerinin görsel haritası.
