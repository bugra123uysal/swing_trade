# 📈 Swing Trade Fırsat Tarayıcı

Qullamaggie tarzı momentum ve breakout stratejilerinden ilham alınarak geliştirilmiş profesyonel bir Swing Trade Tarama ve Analiz Platformu.

Bu proje, ABD hisse senetleri arasında güçlü momentum gösteren ve teknik olarak uygun swing trade fırsatlarını tespit etmek için geliştirilmiştir.

> ⚠️ Bu uygulama yalnızca eğitim ve analiz amaçlıdır. Yatırım tavsiyesi değildir.

---

# 🚀 Özellikler

## 📊 Akıllı Hisse Tarama Sistemi

Uygulama aşağıdaki filtreleri kullanarak güçlü hisseleri tespit eder:

* Minimum hisse fiyatı
* Günlük pozitif değişim
* Minimum market değeri
* Ortalama günlük hacim
* ADR (Average Daily Range)
* EMA21 üzeri fiyat
* EMA50 üzeri fiyat

---

## 🎯 Qullamaggie Tarzı Momentum Analizi

Her hisse için:

* 1 Aylık Momentum
* 3 Aylık Momentum
* 6 Aylık Momentum

hesaplanır ve sıralanır.

---

## 🚀 Breakout Tespiti

Sistem otomatik olarak:

* Son 20 günlük zirveye yakın hisseleri
* Hacim desteği alan hisseleri
* Trend yönünde hareket eden hisseleri

tespit ederek breakout adaylarını işaretler.

---

## 📈 Teknik Analiz

Her hisse için:

* EMA 21
* EMA 50
* ATR
* ADR

hesaplanır.

---

## 🛑 Otomatik Stop Loss Hesabı

Risk yönetimi amacıyla:

### Yöntem 1

Son 10 günlük dip seviyesi

### Yöntem 2

ATR tabanlı stop

Sistem daha güvenli olan stop seviyesini seçer.

---

## 🎯 Hedef Fiyat Hesabı

Her işlem için:

* Giriş Noktası
* Stop Loss
* 2R Hedefi
* 3R Hedefi

otomatik hesaplanır.

---

## ⚡ Canlı Fiyat Takibi

Finnhub WebSocket kullanılarak:

* Gerçek zamanlı fiyat güncellemeleri
* Canlı izleme paneli
* WebSocket bağlantı durumu

gösterilir.

---

## 📊 Profesyonel Dashboard

Dashboard üzerinde:

* Taranan hisse sayısı
* Filtreyi geçen hisse sayısı
* En yüksek hacimli hisse
* En güçlü momentum hissesi
* Breakout adayları

tek ekranda görüntülenebilir.

---

## 📉 Gelişmiş Grafikler

Her hisse için:

* Mum grafiği
* EMA21
* EMA50
* Hacim analizi
* Stop seviyeleri
* Hedef seviyeleri

interaktif olarak gösterilir.

---

# 🛠️ Kullanılan Teknolojiler

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* yFinance
* Finnhub API
* WebSocket
* Dotenv

---

# 📂 Kurulum

## Repository'i Klonla

```bash
git clone https://github.com/bugra123uysal/swing-trade-scanner.git
cd swing-trade-scanner
```

## Kütüphaneleri Kur

```bash
pip install -r requirements.txt
```

## API Key Oluştur

`.env`

```env
FINNHUB_API_KEY=YOUR_API_KEY
```

## Uygulamayı Çalıştır

```bash
streamlit run app.py
```

---

# 📋 Strateji Mantığı

Bu proje aşağıdaki prensiplere dayanır:

✅ Güçlü Trend

✅ Yüksek Hacim

✅ Pozitif Momentum

✅ Breakout Yakınlığı

✅ Risk / Ödül Oranı

Amaç:

> Düşük riskli ve yüksek potansiyelli swing trade fırsatlarını erken tespit etmek.

---

# 📌 Gelecek Güncellemeler

* S&P500 tam tarama
* Nasdaq tam tarama
* Relative Strength hesaplama
* VCP (Volatility Contraction Pattern) tespiti
* Earnings filtreleri
* Sektör rotasyon analizi
* Yapay zeka destekli hisse yorumları
* Telegram bildirimleri

---

# Arayüzü
<img width="1912" height="803" alt="Ekran görüntüsü 2026-06-13 003400" src="https://github.com/user-attachments/assets/e4d11a16-cc51-47c6-8bcc-af1624a0b5f4" />
<img width="1895" height="842" alt="Ekran görüntüsü 2026-06-13 003341" src="https://github.com/user-attachments/assets/250d78c8-d411-4399-a58f-1af5863238c9" />
<img width="1895" height="837" alt="Ekran görüntüsü 2026-06-13 003315" src="https://github.com/user-attachments/assets/4bb85eb7-1c94-416d-9744-dc27e2da1976" />
<img width="1901" height="677" alt="Ekran görüntüsü 2026-06-13 003258" src="https://github.com/user-attachments/assets/292b83a8-df05-419c-857c-0e89a374b487" />
<img width="1918" height="810" alt="Ekran görüntüsü 2026-06-13 003224" src="https://github.com/user-attachments/assets/5b7947e5-de68-41aa-aeec-b9aee92d16cf" />
<img width="1876" height="793" alt="Ekran görüntüsü 2026-06-13 003415" src="https://github.com/user-attachments/assets/7ecfa1a3-0f85-4f2b-87ad-21ca68bbb3b9" />




# 👨‍💻 Geliştirici

Buğra Uysal

GitHub:
https://github.com/bugra123uysal

LinkedIn:
https://www.linkedin.com/in/mesut-bu%C4%9Fra-uysal-16a1bb288/

---
