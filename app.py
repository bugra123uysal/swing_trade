"""
Swing Trade Fırsat Tarayıcı - Qullamaggie Tarzı Momentum/Breakout Screener
==========================================================================
Bu uygulama eğitim ve analiz amaçlıdır. Yatırım tavsiyesi değildir.
"""

import streamlit as st 
import pandas as pd 
import numpy as np 
import yfinance as yf 
import plotly.graph_objects as go 
from plotly.subplots import make_subplots 
import requests 
import os
import json
import threading
import time
from datetime import datetime, timedelta

# dotenv varsa yükle, yoksa geç
try:
    from dotenv import load_dotenv # type: ignore
    load_dotenv()
except ImportError:
    pass
    
# WebSocket desteği varsa yükle
try:
    import websocket # type: ignore
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

# ─────────────────────────────────────────────
# SAYFA AYARLARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Swing Trade Tarayıcı",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# ÖZEL CSS - TipRanks tarzı koyu tema
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Ana arka plan ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0d0f14 0%, #111520 50%, #0a0c10 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12151e 0%, #0e1018 100%);
    border-right: 1px solid #1e2535;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Genel metin ── */
html, body, [class*="css"] { color: #c8d0e0; font-family: 'Inter', 'Segoe UI', sans-serif; }

/* ── Büyük başlık ── */
.main-title {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #4fd1c5, #63b3ed, #9f7aea);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.subtitle {
    color: #6b7a99; font-size: 0.95rem; margin-bottom: 20px;
}

/* ── KPI kartları (3-D efekti) ── */
.kpi-card {
    background: linear-gradient(145deg, #1a1f2e, #161b28);
    border: 1px solid #2a3045;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 4px 4px 12px rgba(0,0,0,0.5), -1px -1px 4px rgba(255,255,255,0.03),
                inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 12px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 6px 8px 20px rgba(0,0,0,0.6), -1px -1px 4px rgba(255,255,255,0.04);
}
.kpi-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #5a6680; margin-bottom: 6px; }
.kpi-value { font-size: 1.9rem; font-weight: 700; color: #e2e8f0; line-height: 1; }
.kpi-sub   { font-size: 0.8rem; color: #4fd1c5; margin-top: 4px; }

/* ── Hisse kartları ── */
.stock-card {
    background: linear-gradient(145deg, #181d2b, #141824);
    border: 1px solid #232a3c;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
}
.stock-ticker { font-size: 1.3rem; font-weight: 700; color: #63b3ed; }
.stock-price  { font-size: 1.1rem; font-weight: 600; color: #e2e8f0; }
.change-pos   { color: #48bb78; font-weight: 600; }
.change-neg   { color: #fc8181; font-weight: 600; }
.breakout-badge {
    display: inline-block; background: linear-gradient(135deg,#2d6a4f,#1a472a);
    border: 1px solid #48bb78; color: #68d391; font-size: 0.7rem;
    padding: 2px 8px; border-radius: 20px; font-weight: 600; letter-spacing: 0.5px;
}

/* ── Açıklama kutusu ── */
.reason-box {
    background: linear-gradient(135deg, #1a2035, #161d30);
    border-left: 3px solid #4fd1c5;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #8899bb;
    margin-top: 10px;
    line-height: 1.6;
}

/* ── Stop/hedef göstergesi ── */
.trade-plan-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
.tp-box {
    background: #12151e;
    border: 1px solid #2a3045;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    min-width: 100px;
}
.tp-box .tp-label { color: #5a6680; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; }
.tp-box .tp-val   { font-weight: 600; font-size: 0.95rem; }

/* ── Canlı fiyat kutusu ── */
.live-box {
    background: linear-gradient(145deg, #0e1a14, #0a1610);
    border: 1px solid #2d6a4f;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 0 12px rgba(72,187,120,0.08);
}

/* ── Strateji sekme ── */
.strategy-block {
    background: linear-gradient(145deg, #141824, #111520);
    border: 1px solid #1e2535;
    border-radius: 12px;
    padding: 22px 26px;
    margin-bottom: 16px;
}
.strategy-block h3 { color: #63b3ed; font-size: 1rem; margin-bottom: 8px; }

/* ── Uyarı çubuğu ── */
.disclaimer {
    background: linear-gradient(90deg, #1a1205, #1a1510);
    border: 1px solid #3d2e10;
    border-radius: 8px;
    padding: 10px 16px;
    color: #c9a227;
    font-size: 0.8rem;
    margin-bottom: 20px;
}

/* ── Tablo ── */
.dataframe { background: #12151e !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a3045; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SABIT: Hisse evreni
# ─────────────────────────────────────────────
BASE_UNIVERSE = [
    "AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN","GOOGL","NFLX","PLTR",
    "COIN","MARA","SMCI","AVGO","MU","ARM","CRWD","SNOW","SHOP","UBER",
    "RBLX","SOFI","CELH","MSTR","CLSK","RIOT","HOOD","DKNG","NET","DDOG"
]

# ─────────────────────────────────────────────
# FONKSİYON: API anahtarını yükle
# ─────────────────────────────────────────────
def load_api_key() -> str:
    """
    Finnhub API anahtarını .env dosyasından veya sistem ortam değişkeninden okur.
    Güvenlik için anahtar kod içine yazılmaz.
    """
    key = os.environ.get("FINNHUB_API_KEY", "")
    return key

# ─────────────────────────────────────────────
# FONKSİYON: Hisse verisini indir
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)  # 5 dakika önbellekle
def get_stock_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    yfinance ile hisse verisi çeker.
    Hata olursa boş DataFrame döner.
    """
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        # Çoklu index varsa düzelt
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        return pd.DataFrame()

# ─────────────────────────────────────────────
# FONKSİYON: Teknik göstergeler hesapla
# ─────────────────────────────────────────────
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    EMA 21, EMA 50, son 20 günlük zirve, 10 günlük hacim ortalaması hesaplar.
    """
    if df.empty or len(df) < 50:
        return df

    close = df["Close"]
    df["EMA21"] = close.ewm(span=21, adjust=False).mean()
    df["EMA50"] = close.ewm(span=50, adjust=False).mean()
    df["High20"] = df["High"].rolling(20).max()    # son 20 günlük zirve
    df["AvgVol10"] = df["Volume"].rolling(10).mean()  # 10 günlük ort. hacim
    return df

# ─────────────────────────────────────────────
# FONKSİYON: ADR hesapla (Average Daily Range)
# ─────────────────────────────────────────────
def calculate_adr(df: pd.DataFrame, period: int = 10) -> float:
    """
    ADR: Son N günün yüksek/düşük farkının ortalaması (%).
    Volatilite ve trading uygunluğunu ölçer.
    """
    if df.empty or len(df) < period:
        return 0.0
    last = df.tail(period).copy()
    ranges = (last["High"] - last["Low"]) / last["Low"] * 100
    return float(ranges.mean())

# ─────────────────────────────────────────────
# FONKSİYON: ATR hesapla (Average True Range)
# ─────────────────────────────────────────────
def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """
    ATR: Gerçek fiyat aralığının ortalaması.
    Stop seviyesi için kullanılır.
    """
    if df.empty or len(df) < period + 1:
        return 0.0
    high  = df["High"]
    low   = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr) if not np.isnan(atr) else 0.0

# ─────────────────────────────────────────────
# FONKSİYON: Trade planı hesapla
# ─────────────────────────────────────────────
def calculate_trade_plan(df: pd.DataFrame, adr: float) -> dict:
    """
    Giriş, stop, 2R ve 3R hedeflerini hesaplar.
    Stop: Son 10 günlük düşüğün %1 altı (ATR tabanlı alternatifle karşılaştırılır).
    """
    if df.empty or len(df) < 10:
        return {}

    last_close = float(df["Close"].iloc[-1])
    atr        = calculate_atr(df)

    # Stop seviyesi: son 10 günlük en düşük - %1 tampon
    low10  = float(df["Low"].tail(10).min())
    stop1  = low10 * 0.99

    # ATR tabanlı alternatif stop
    stop2  = last_close - (1.5 * atr) if atr > 0 else stop1

    # Daha yakın olanı seç (daha koruyucu)
    stop   = max(stop1, stop2)
    risk   = last_close - stop

    # Risk sıfır veya negatifse planı boşalt
    if risk <= 0:
        return {}

    risk_pct = (risk / last_close) * 100

    # ADR'den çok geniş stop uyarısı
    stop_warning = risk_pct > adr * 1.5 if adr > 0 else False

    target_2r = last_close + (2 * risk)
    target_3r = last_close + (3 * risk)
    rr_ratio  = round(risk / risk * 2, 1)  # her zaman 2 (referans)

    return {
        "entry"       : round(last_close, 2),
        "stop"        : round(stop, 2),
        "target_2r"   : round(target_2r, 2),
        "target_3r"   : round(target_3r, 2),
        "risk_pct"    : round(risk_pct, 2),
        "stop_warning": stop_warning,
        "rr_2r"       : 2.0,
        "rr_3r"       : 3.0,
    }

# ─────────────────────────────────────────────
# FONKSİYON: Hisseyi tara ve filtrele
# ─────────────────────────────────────────────
def screen_stocks(
    tickers: list,
    min_price: float = 3.0,
    min_change_pct: float = 0.01,
    min_market_cap: float = 300e6,
    min_adr: float = 2.0,
    min_avg_vol: int = 500_000,
) -> pd.DataFrame:
    """
    Her hisse için veri çeker ve Qullamaggie filtrelerini uygular.
    Filtreyi geçen hisseler hacme göre sıralanır.
    """
    results = []
    progress_bar = st.progress(0, text="Hisseler taranıyor...")

    for i, ticker in enumerate(tickers):
        progress_bar.progress((i + 1) / len(tickers), text=f"Taranan: {ticker}")

        df = get_stock_data(ticker)
        if df.empty or len(df) < 60:
            continue

        df = calculate_indicators(df)
        if df.empty:
            continue

        last    = df.iloc[-1]
        prev    = df.iloc[-2]
        close   = float(last["Close"])
        volume  = float(last["Volume"])
        ema21   = float(last["EMA21"])
        ema50   = float(last["EMA50"])
        high20  = float(last["High20"]) if "High20" in last else close
        avg_vol = float(last["AvgVol10"]) if "AvgVol10" in last else volume

        # Günlük değişim %
        daily_change_pct = ((close - float(prev["Close"])) / float(prev["Close"])) * 100

        # ADR hesapla
        adr = calculate_adr(df)

        # Market cap: yfinance'den bilgi çek
        try:
            info = yf.Ticker(ticker).fast_info
            market_cap = float(getattr(info, "market_cap", 0) or 0)
        except Exception:
            market_cap = 0.0

        # ── FİLTRELER ──
        if close < min_price:           continue
        if daily_change_pct < min_change_pct: continue
        if market_cap < min_market_cap: continue
        if adr < min_adr:               continue
        if avg_vol < min_avg_vol:       continue
        if close <= ema21:              continue
        if close <= ema50:              continue

        # ── MOMENTUM (1 ay, 3 ay, 6 ay) ──
        def momentum_pct(days):
            if len(df) > days:
                past = float(df["Close"].iloc[-(days+1)])
                return round((close - past) / past * 100, 2) if past > 0 else 0.0
            return 0.0

        mom_1m = momentum_pct(21)
        mom_3m = momentum_pct(63)
        mom_6m = momentum_pct(126)

        # ── BREAKOUT ADAYI? ──
        near_high20  = close >= high20 * 0.98        # Son 20 günlük zirveye %2 yakın
        vol_above_avg = volume >= avg_vol * 1.0      # Hacim ortalamanın üstünde
        is_breakout  = near_high20 and vol_above_avg and (close > ema21) and (close > ema50)

        # ── TRADE PLANI ──
        plan = calculate_trade_plan(df, adr)

        results.append({
            "Ticker"       : ticker,
            "Fiyat ($)"    : round(close, 2),
            "Günlük Değ. %": round(daily_change_pct, 2),
            "ADR %"        : round(adr, 2),
            "Hacim"        : int(volume),
            "Ort. Hacim"   : int(avg_vol),
            "EMA21"        : round(ema21, 2),
            "EMA50"        : round(ema50, 2),
            "Mkt Cap ($M)" : round(market_cap / 1e6, 1),
            "Mom 1A %"     : mom_1m,
            "Mom 3A %"     : mom_3m,
            "Mom 6A %"     : mom_6m,
            "Breakout?"    : is_breakout,
            "Giriş"        : plan.get("entry", close),
            "Stop"         : plan.get("stop", 0),
            "Hedef 2R"     : plan.get("target_2r", 0),
            "Hedef 3R"     : plan.get("target_3r", 0),
            "Risk %"       : plan.get("risk_pct", 0),
            "Stop Uyarı"   : plan.get("stop_warning", False),
            "_df"          : df,  # grafik için sakla
        })

    progress_bar.empty()

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)
    result_df.sort_values("Hacim", ascending=False, inplace=True)
    result_df.reset_index(drop=True, inplace=True)
    return result_df

# ─────────────────────────────────────────────
# FONKSİYON: Seçilme gerekçesi üret
# ─────────────────────────────────────────────
def explain_reason(row: pd.Series) -> str:
    """
    Hissenin neden seçildiğini sade Türkçe açıklar.
    """
    parts = ["Bu hisse seçildi çünkü fiyat 21 ve 50 EMA üzerinde, hacim güçlü, ADR yüksek, günlük değişim pozitif."]

    if row.get("Breakout?", False):
        parts.append("Fiyat son 20 günlük zirveye yakın ve hacim ortalamanın üstünde — güçlü breakout adayı.")
    if row.get("Mom 1A %", 0) > 10:
        parts.append(f"Son 1 aylık momentum {row['Mom 1A %']:.1f}% ile oldukça güçlü.")
    if row.get("Mom 3A %", 0) > 20:
        parts.append(f"Son 3 aylık momentum {row['Mom 3A %']:.1f}% ile trend devam ediyor.")
    if row.get("Stop Uyarı", False):
        parts.append("⚠️ Stop seviyesi ADR'ye göre biraz geniş; pozisyon büyüklüğünü ayarlayın.")
    else:
        parts.append("Stop seviyesi son dip/ATR mantığına göre belirlenmiştir.")

    return " ".join(parts)

# ─────────────────────────────────────────────
# FONKSİYON: Hisse grafiği çiz
# ─────────────────────────────────────────────
def render_chart(ticker: str, df: pd.DataFrame, plan: dict):
    """
    Mum grafiği + EMA çizgileri + stop/hedef seviyeleri + hacim grafiği.
    """
    if df.empty:
        st.warning("Grafik için veri bulunamadı.")
        return

    df_plot = df.tail(90).copy()  # son 90 gün

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.72, 0.28],
        vertical_spacing=0.04
    )

    # ── Mum grafiği ──
    fig.add_trace(go.Candlestick(
        x=df_plot.index,
        open=df_plot["Open"], high=df_plot["High"],
        low=df_plot["Low"],   close=df_plot["Close"],
        name=ticker,
        increasing_line_color="#48bb78",
        decreasing_line_color="#fc8181",
        increasing_fillcolor="rgba(72,187,120,0.7)",
        decreasing_fillcolor="rgba(252,129,129,0.7)",
    ), row=1, col=1)

    # ── EMA çizgileri ──
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["EMA21"],
        name="EMA 21", line=dict(color="#f6ad55", width=1.5, dash="dot")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["EMA50"],
        name="EMA 50", line=dict(color="#9f7aea", width=1.5, dash="dot")
    ), row=1, col=1)

    # ── Stop, giriş, hedef yatay çizgileri ──
    if plan:
        x0, x1 = df_plot.index[0], df_plot.index[-1]
        lines = [
            (plan["stop"],      "#fc8181", "Stop"),
            (plan["entry"],     "#48bb78", "Giriş"),
            (plan["target_2r"], "#63b3ed", "Hedef 2R"),
            (plan["target_3r"], "#4fd1c5", "Hedef 3R"),
        ]
        for y_val, color, label in lines:
            fig.add_hline(
                y=y_val, line_dash="dash",
                line_color=color, line_width=1,
                annotation_text=f"  {label}: ${y_val}",
                annotation_font_color=color,
                row=1, col=1
            )

    # ── Hacim barları ──
    colors = ["#48bb78" if c >= o else "#fc8181"
              for c, o in zip(df_plot["Close"], df_plot["Open"])]
    fig.add_trace(go.Bar(
        x=df_plot.index, y=df_plot["Volume"],
        name="Hacim", marker_color=colors, opacity=0.7,
        showlegend=False
    ), row=2, col=1)

    # 10 günlük ort. hacim çizgisi
    if "AvgVol10" in df_plot.columns:
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot["AvgVol10"],
            name="Ort.Hacim", line=dict(color="#f6ad55", width=1, dash="dot"),
            showlegend=False
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#c8d0e0", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h", x=0, y=1.02,
            bgcolor="rgba(0,0,0,0)", font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
    )
    fig.update_xaxes(gridcolor="#1e2535", showgrid=True)
    fig.update_yaxes(gridcolor="#1e2535", showgrid=True)

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# FONKSİYON: Dashboard sekme
# ─────────────────────────────────────────────
def render_dashboard(results_df: pd.DataFrame, scanned_count: int):
    """
    KPI kartlarını ve özet bilgileri gösterir.
    """
    st.markdown('<div class="main-title">📈 Swing Trade Fırsat Tarayıcı</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Qullamaggie Tarzı Momentum & Breakout Screener — ABD Hisseleri</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer">⚠️ Bu uygulama yalnızca eğitim ve analiz amaçlıdır. Yatırım tavsiyesi değildir. Tüm yatırım kararlarınız kendi sorumluluğunuzdadır.</div>', unsafe_allow_html=True)

    passed   = len(results_df) if not results_df.empty else 0
    top_vol  = results_df.iloc[0]["Ticker"] if passed > 0 else "—"
    top_mom  = results_df.loc[results_df["Mom 1A %"].idxmax(), "Ticker"] if passed > 0 else "—"
    top_mom_val = results_df["Mom 1A %"].max() if passed > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Taranan Hisse</div>
            <div class="kpi-value">{scanned_count}</div>
            <div class="kpi-sub">Evren büyüklüğü</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Filtreyi Geçen</div>
            <div class="kpi-value">{passed}</div>
            <div class="kpi-sub">%{round(passed/max(scanned_count,1)*100,1)} başarı oranı</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">En Yüksek Hacim</div>
            <div class="kpi-value">{top_vol}</div>
            <div class="kpi-sub">Günlük hacim lideri</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">En Güçlü Momentum</div>
            <div class="kpi-value">{top_mom}</div>
            <div class="kpi-sub">+{top_mom_val:.1f}% (1 ay)</div>
        </div>""", unsafe_allow_html=True)

    if passed > 0:
        st.markdown("---")
        st.markdown("#### 🔥 Breakout Adayları")
        bo = results_df[results_df["Breakout?"] == True]
        if bo.empty:
            st.info("Şu an aktif breakout adayı yok.")
        else:
            for _, row in bo.head(5).iterrows():
                change_cls = "change-pos" if row["Günlük Değ. %"] >= 0 else "change-neg"
                badge = '<span class="breakout-badge">🚀 BREAKOUT</span>'
                st.markdown(f"""<div class="stock-card">
                    <span class="stock-ticker">{row['Ticker']}</span>
                    &nbsp;&nbsp;<span class="stock-price">${row['Fiyat ($)']}</span>
                    &nbsp;&nbsp;<span class="{change_cls}">{row['Günlük Değ. %']:+.2f}%</span>
                    &nbsp;&nbsp;{badge}
                    <br><small style="color:#5a6680">ADR: {row['ADR %']:.1f}% | Mom 1A: {row['Mom 1A %']:+.1f}% | Hacim: {row['Hacim']:,}</small>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# WebSocket yöneticisi (thread güvenli)
# ─────────────────────────────────────────────
class LivePriceManager:
    """
    Finnhub WebSocket ile canlı fiyat izleme.
    Thread güvenli dictionary ile fiyatları saklar.
    """
    def __init__(self):
        self.prices = {}
        self.connected = False
        self.ws = None
        self._lock = threading.Lock()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "trade":
                for trade in data.get("data", []):
                    sym = trade.get("s", "")
                    price = trade.get("p", 0)
                    with self._lock:
                        self.prices[sym] = round(float(price), 2)
        except Exception:
            pass

    def on_error(self, ws, error):
        self.connected = False

    def on_close(self, ws, *args):
        self.connected = False

    def on_open(self, ws, symbols):
        self.connected = True
        for sym in symbols:
            ws.send(json.dumps({"type": "subscribe", "symbol": sym}))

    def start(self, api_key: str, symbols: list):
        if not WEBSOCKET_AVAILABLE or not api_key:
            return
        try:
            url = f"wss://ws.finnhub.io?token={api_key}"
            self.ws = websocket.WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=lambda ws: self.on_open(ws, symbols)
            )
            t = threading.Thread(target=self.ws.run_forever, daemon=True)
            t.start()
        except Exception:
            pass

    def get_prices(self) -> dict:
        with self._lock:
            return dict(self.prices)

    def stop(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

# ─────────────────────────────────────────────
# MAIN UYGULAMA
# ─────────────────────────────────────────────
def main():
    api_key = load_api_key()

    # ── SOL SIDEBAR ──
    with st.sidebar:
        st.markdown("## ⚙️ Filtre Ayarları")
        st.markdown("---")

        min_price = st.slider("Min. Hisse Fiyatı ($)", 1.0, 50.0, 3.0, 0.5)
        min_change = st.slider("Min. Günlük Değişim (%)", 0.0, 5.0, 0.01, 0.01)
        min_mkt_cap = st.slider("Min. Market Cap ($M)", 100, 2000, 300, 50)
        min_adr = st.slider("Min. ADR (%)", 1.0, 10.0, 2.0, 0.5)
        min_vol = st.slider("Min. Ort. Hacim (K)", 100, 2000, 500, 100)

        st.markdown("---")
        st.markdown("#### 📋 Hisse Evreni")
        use_extended = st.checkbox("Finnhub ile genişletilmiş liste kullan", value=False)
        custom_tickers_raw = st.text_area(
            "Özel hisseler ekle (virgülle ayır)",
            placeholder="Örn: COIN,HOOD,MARA",
            height=80
        )

        st.markdown("---")
        st.markdown("#### 🔑 API Durumu")
        if api_key:
            st.success("✅ Finnhub key bulundu")
        else:
            st.warning("⚠️ .env'de FINNHUB_API_KEY yok\n\nBazı özellikler devre dışı.")

        run_scan = st.button("🔍 Taramayı Başlat", type="primary", use_container_width=True)

    # ── HISSE EVRENİNİ OLUŞTUR ──
    universe = list(BASE_UNIVERSE)

    # Özel hisseler ekle
    if custom_tickers_raw.strip():
        extras = [t.strip().upper() for t in custom_tickers_raw.split(",") if t.strip()]
        universe = list(set(universe + extras))

    # Finnhub ile genişlet (API key varsa)
    if use_extended and api_key:
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/stock/symbol",
                params={"exchange": "US", "token": api_key},
                timeout=10
            )
            if resp.status_code == 200:
                symbols_data = resp.json()
                # Sadece normal hisseleri al (ETF değil)
                extra_syms = [
                    s["symbol"] for s in symbols_data
                    if s.get("type") == "Common Stock" and "." not in s["symbol"]
                ][:200]
                universe = list(set(universe + extra_syms))
                st.sidebar.info(f"Finnhub: {len(extra_syms)} hisse eklendi")
        except Exception as e:
            st.sidebar.error(f"Finnhub liste alınamadı: {e}")

    # ── SEKMELERi OLUŞTUR ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "🔍 Screener Sonuçları",
        "📈 Hisse Detay",
        "⚡ Canlı İzleme",
        "📚 Strateji"
    ])

    # Session state ile sonuçları sakla
    if "results_df" not in st.session_state:
        st.session_state.results_df = pd.DataFrame()
    if "scanned_count" not in st.session_state:
        st.session_state.scanned_count = 0
    if "live_manager" not in st.session_state:
        st.session_state.live_manager = None

    # ── TARAMA ÇALIŞTIR ──
    if run_scan:
        with st.spinner("Hisseler taranıyor, lütfen bekleyin..."):
            df_results = screen_stocks(
                tickers=universe,
                min_price=min_price,
                min_change_pct=min_change,
                min_market_cap=min_mkt_cap * 1e6,
                min_adr=min_adr,
                min_avg_vol=min_vol * 1000,
            )
            st.session_state.results_df = df_results
            st.session_state.scanned_count = len(universe)

        # WebSocket başlat (filtreyi geçen ilk 10 hisse)
        if api_key and WEBSOCKET_AVAILABLE and not df_results.empty:
            top10 = df_results["Ticker"].head(10).tolist()
            if st.session_state.live_manager:
                st.session_state.live_manager.stop()
            mgr = LivePriceManager()
            mgr.start(api_key, top10)
            st.session_state.live_manager = mgr

    results_df     = st.session_state.results_df
    scanned_count  = st.session_state.scanned_count

    # ────────────────────────
    # SEKMESİ 1: Dashboard
    # ────────────────────────
    with tab1:
        render_dashboard(results_df, scanned_count)

        if results_df.empty and scanned_count == 0:
            st.info("👈 Sol taraftan filtrelerinizi ayarlayın ve **Taramayı Başlat** butonuna tıklayın.")

    # ────────────────────────
    # SEKMESİ 2: Screener
    # ────────────────────────
    with tab2:
        st.markdown("## 🔍 Screener Sonuçları")

        if results_df.empty:
            if scanned_count > 0:
                st.warning("Filtreyi geçen hisse bulunamadı. Filtreleri gevşetmeyi deneyin.")
            else:
                st.info("Taramayı başlatmak için sol paneli kullanın.")
        else:
            st.success(f"✅ {scanned_count} hisse tarandı, {len(results_df)} hisse filtreyi geçti.")

            # Tablo kolonlarını seç (dahili _df kolonunu gösterme)
            display_cols = [c for c in results_df.columns if c != "_df"]
            df_display = results_df[display_cols].copy()

            # Boolean'ı emoji ile göster
            df_display["Breakout?"] = df_display["Breakout?"].map({True: "🚀 Evet", False: "—"})
            df_display["Stop Uyarı"] = df_display["Stop Uyarı"].map({True: "⚠️ Geniş", False: "✅ Normal"})

            st.dataframe(
                df_display.style
                .format({
                    "Fiyat ($)": "${:.2f}", "Günlük Değ. %": "{:+.2f}%",
                    "ADR %": "{:.1f}%", "Mom 1A %": "{:+.1f}%",
                    "Mom 3A %": "{:+.1f}%", "Mom 6A %": "{:+.1f}%",
                    "Risk %": "{:.1f}%",
                })
                .background_gradient(subset=["Mom 1A %"], cmap="RdYlGn"),
                use_container_width=True, height=400
            )

            # ── Her hisse için kart ──
            st.markdown("---")
            st.markdown("### 📋 Detaylı Hisse Kartları")

            for _, row in results_df.iterrows():
                change_cls = "change-pos" if row["Günlük Değ. %"] >= 0 else "change-neg"
                badge = '<span class="breakout-badge">🚀 BREAKOUT</span>' if row["Breakout?"] == True or row.get("Breakout?") == True else ""
                reason = explain_reason(row)

                st.markdown(f"""<div class="stock-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="stock-ticker">{row['Ticker']}</span>
                            &nbsp;&nbsp;<span class="stock-price">${row['Fiyat ($)']:.2f}</span>
                            &nbsp;&nbsp;<span class="{change_cls}">{row['Günlük Değ. %']:+.2f}%</span>
                            &nbsp;&nbsp;{badge}
                        </div>
                        <div style="color:#5a6680;font-size:0.8rem">ADR: {row['ADR %']:.1f}%</div>
                    </div>
                    <div class="trade-plan-row">
                        <div class="tp-box"><div class="tp-label">Giriş</div><div class="tp-val" style="color:#48bb78">${row['Giriş']:.2f}</div></div>
                        <div class="tp-box"><div class="tp-label">Stop</div><div class="tp-val" style="color:#fc8181">${row['Stop']:.2f}</div></div>
                        <div class="tp-box"><div class="tp-label">Hedef 2R</div><div class="tp-val" style="color:#63b3ed">${row['Hedef 2R']:.2f}</div></div>
                        <div class="tp-box"><div class="tp-label">Hedef 3R</div><div class="tp-val" style="color:#4fd1c5">${row['Hedef 3R']:.2f}</div></div>
                        <div class="tp-box"><div class="tp-label">Risk/Ödül</div><div class="tp-val" style="color:#f6ad55">1:2 / 1:3</div></div>
                        <div class="tp-box"><div class="tp-label">Risk %</div><div class="tp-val">{row['Risk %']:.1f}%</div></div>
                    </div>
                    <div class="reason-box">💡 {reason}</div>
                </div>""", unsafe_allow_html=True)

    # ────────────────────────
    # SEKMESİ 3: Hisse Detay
    # ────────────────────────
    with tab3:
        st.markdown("## 📈 Hisse Detay Analizi")

        if results_df.empty:
            st.info("Önce tarama yapın.")
        else:
            ticker_options = results_df["Ticker"].tolist()
            selected = st.selectbox("Hisse seçin:", ticker_options)

            row = results_df[results_df["Ticker"] == selected].iloc[0]
            df_ticker = row.get("_df", pd.DataFrame())

            plan = {
                "entry"    : row["Giriş"],
                "stop"     : row["Stop"],
                "target_2r": row["Hedef 2R"],
                "target_3r": row["Hedef 3R"],
            }

            c1, c2, c3 = st.columns(3)
            with c1:
                chg_color = "green" if row["Günlük Değ. %"] >= 0 else "red"
                st.metric("Fiyat", f"${row['Fiyat ($)']:.2f}",
                          delta=f"{row['Günlük Değ. %']:+.2f}%")
            with c2:
                st.metric("ADR", f"{row['ADR %']:.1f}%")
            with c3:
                st.metric("Momentum (1A)", f"{row['Mom 1A %']:+.1f}%")

            render_chart(selected, df_ticker, plan)

            st.markdown(f"""<div class="reason-box">
                💡 {explain_reason(row)}
            </div>""", unsafe_allow_html=True)

    # ────────────────────────
    # SEKMESİ 4: Canlı İzleme
    # ────────────────────────
    with tab4:
        st.markdown("## ⚡ Canlı Fiyat İzleme")

        if not api_key:
            st.error("Canlı izleme için .env dosyasında FINNHUB_API_KEY gerekli.")
        elif not WEBSOCKET_AVAILABLE:
            st.warning("websocket-client kütüphanesi yüklü değil. `pip install websocket-client` komutuyla yükleyin.")
        elif results_df.empty:
            st.info("Önce tarama yapın. Filtreyi geçen ilk 10 hisse canlı izlenecek.")
        else:
            mgr = st.session_state.get("live_manager")
            top10 = results_df["Ticker"].head(10).tolist()

            st.markdown(f"**İzlenen hisseler:** {', '.join(top10)}")
            st.markdown("*(Veriler Finnhub WebSocket üzerinden akıyor)*")

            if mgr and mgr.connected:
                st.success("🟢 WebSocket bağlantısı aktif")
            else:
                st.warning("🟡 WebSocket bağlantısı bekleniyor veya yeniden bağlanıyor...")

            # Otomatik yenile (5 saniyede bir)
            auto_refresh = st.checkbox("Otomatik yenile (5s)", value=False)

            prices = mgr.get_prices() if mgr else {}

            cols = st.columns(5)
            for i, ticker in enumerate(top10):
                live_price = prices.get(ticker)
                ref_price  = float(results_df[results_df["Ticker"] == ticker]["Fiyat ($)"].values[0])

                if live_price:
                    diff = live_price - ref_price
                    diff_pct = (diff / ref_price) * 100
                    color = "#48bb78" if diff >= 0 else "#fc8181"
                    arrow = "▲" if diff >= 0 else "▼"
                    price_str = f"${live_price:.2f}"
                    change_str = f"{arrow} {diff_pct:+.2f}%"
                else:
                    color = "#5a6680"
                    price_str = f"${ref_price:.2f}"
                    change_str = "— canlı yok"

                with cols[i % 5]:
                    st.markdown(f"""<div class="live-box">
                        <div style="font-weight:700;color:#63b3ed">{ticker}</div>
                        <div style="font-size:1.2rem;font-weight:600;color:#e2e8f0">{price_str}</div>
                        <div style="font-size:0.8rem;color:{color}">{change_str}</div>
                    </div>""", unsafe_allow_html=True)

            if auto_refresh:
                time.sleep(5)
                st.rerun()

    # ────────────────────────
    # SEKMESİ 5: Strateji
    # ────────────────────────
    with tab5:
        st.markdown("## 📚 Strateji Açıklaması")

        blocks = [
            ("🎯 Qullamaggie Yaklaşımı Nedir?",
             "Kristjan Qullamaggie, yüksek momentum gösteren, güçlü trend içindeki hisseleri belirli bir volatilite genişlemesi (VCP - Volatility Contraction Pattern) veya breakout noktasında yakalayan bir swing trader'dır. "
             "Temel prensip: Güçlü trendde olan, düşük riskli giriş noktası sunan hisseleri seç."),

            ("📐 Giriş Kriterleri",
             "• Fiyat 21 EMA ve 50 EMA üzerinde (trend sağlığı)\n"
             "• ADR %2 ve üzeri (yeterli volatilite)\n"
             "• Ortalama hacim 500K ve üzeri (likidite)\n"
             "• Günlük değişim pozitif (momentum)\n"
             "• Market cap 300M+ (küçük cap riski yok)\n"
             "• Fiyat son 20 günlük zirveye %2 içinde (breakout yakın)"),

            ("🛑 Stop Loss Mantığı",
             "Stop seviyesi iki yöntemle hesaplanır:\n"
             "1. Son 10 günlük en düşük seviyenin %1 altı\n"
             "2. Son kapanıştan 1.5 ATR altı\n\n"
             "İki seviyeden daha yakın (koruyucu) olan seçilir. "
             "Stop yüzdesi ADR'nin 1.5 katından fazlaysa uyarı verilir."),

            ("🎯 Hedef Belirleme",
             "Risk/Ödül (R/R) hesaplaması:\n"
             "• Giriş − Stop = Risk (1R)\n"
             "• Hedef 1: Giriş + (2 × Risk) = 2R\n"
             "• Hedef 2: Giriş + (3 × Risk) = 3R\n\n"
             "Minimum 2:1 R/R oranı hedeflenir. Pozisyon yarısında 2R'de çıkış, kalanında trailing stop uygulanabilir."),

            ("📊 Momentum Filtresi",
             "1 aylık, 3 aylık ve 6 aylık momentum yüzdeleri hesaplanır. "
             "Güçlü momentum zinciri (6A > 3A > 1A pozitif) ideal tablodur. "
             "Bu, kurumsal alıcıların hisseye ilgisini gösterir."),

            ("⚠️ Risk Yönetimi",
             "• Portföy riski: tek pozisyon için toplam sermayenin %1-2'si\n"
             "• Korelasyon: aynı sektörden çok pozisyon açmaktan kaçın\n"
             "• Stop'a ulaşıldığında kesinlikle çık — 'bekle göreceğiz' yapma\n"
             "• Bu uygulama eğitim amaçlıdır, yatırım tavsiyesi değildir."),
        ]

        for title, content in blocks:
            st.markdown(f"""<div class="strategy-block">
                <h3>{title}</h3>
                <p style="color:#8899bb;font-size:0.87rem;line-height:1.7;white-space:pre-line">{content}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="disclaimer" style="margin-top:20px">
            ⚠️ <strong>Önemli Uyarı:</strong> Bu uygulama tamamen eğitim ve analiz amaçlıdır.
            Buradaki bilgiler yatırım tavsiyesi niteliği taşımaz. Tüm yatırım kararları kişinin
            kendi sorumluluğundadır. Geçmiş performans gelecek sonuçların garantisi değildir.
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ÇALIŞTIR
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
