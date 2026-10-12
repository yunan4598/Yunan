from __future__ import annotations

import os
import re
import time
import hmac
from datetime import datetime, timezone, date
from io import StringIO
from typing import Any, Optional
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

# ================================================================
# Aho𓂀 GOLD — ULTIMATE VISUAL & MOBILE FIX
# ================================================================
APP_NAME = "Aho𓂀 GOLD"
APP_VERSION = "16.8 — FINAL VISUAL FIX"
REQUEST_TIMEOUT = 12
USER_AGENT = "AhoGoldIntelligence/16.8 (public-data-source-check)"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# CSS المطور لإلغاء خطوط المنتصف الفاصلة وتعديل الخلفيات كلياً
CSS_OVERRIDE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-dark: #111923;
    --panel-dark: #192532;
    --line-dark: #2a3a4b;
    --gold: #d9b56d;
    --text-dark: #f2f6f8;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans Arabic', 'Inter', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

.stApp {
    background: radial-gradient(circle at 50% 0%, #1a2736 0%, #0f1722 100%) !important;
    color: var(--text-dark) !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* إلغاء الخط الفاصل الشفاف أو أي حدود رأسيّة بالمنتصف */
[data-testid="stHorizontalBlock"] > div {
    border: none !important;
    box-shadow: none !important;
}

/* تحسين شكل البطاقات والمرئيات ومنع تداخل الخطوط */
[data-testid="stMetric"] {
    background: #182430 !important;
    border: 1px solid #2a3a4a !important;
    border-radius: 12px !important;
    padding: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

.hero {
    border: 1px solid #2d3e50 !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    background: linear-gradient(135deg, #1d2b3a 0%, #131e2b 100%) !important;
    margin-bottom: 16px !important;
    border-right: 5px solid var(--gold) !important;
}

.eyebrow {
    color: var(--gold) !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}

.hero h1 {
    margin: 4px 0 !important;
    font-size: 22px !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}

.hero p {
    margin: 0 !important;
    color: #9cb0c3 !important;
    font-size: 13px !important;
}

/* تنسيق الشريط الجانبي */
[data-testid="stSidebar"] {
    background: #131d27 !important;
    border-left: none !important;
    border-right: 1px solid #233242 !important;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 14px;
    border-bottom: 1px solid #233242;
    margin-bottom: 12px;
}

.brand-mark {
    width: 40px; height: 40px;
    border: 1px solid #8e783e;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    color: var(--gold); font-size: 20px;
    background: #202d3b;
}

.brand-title {
    font-weight: 800; font-size: 16px; color: var(--gold);
}

.brand-sub {
    color: #8a9ba8; font-size: 10px;
}

/* إخفاء القوائم والروابط الزائدة لتنظيف الواجهة */
footer { visibility: hidden !important; }
header { background: transparent !important; }

/* معالجة العرض على الهواتف */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .hero h1 { font-size: 18px !important; }
}
</style>
"""
st.markdown(CSS_OVERRIDE, unsafe_allow_html=True)

# ---------------------- Secrets / Authentication ----------------------
def get_secret(name: str) -> str:
    value = ""
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    if not value:
        value = os.getenv(name, "")
    return str(value).strip() if value else ""

APP_USERNAME = get_secret("APP_USERNAME")
APP_PASSWORD = get_secret("APP_PASSWORD")

if not APP_USERNAME or not APP_PASSWORD:
    st.error("لم تُضبط بيانات الدخول في Secrets.")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD</div><h1>تسجيل الدخول</h1><p>أدخل اسم المستخدم وكلمة المرور للمتابعة.</p></div>', unsafe_allow_html=True)
    with st.form("login"):
        username_input = st.text_input("اسم المستخدم")
        password_input = st.text_input("كلمة المرور", type="password")
        submit_login = st.form_submit_button("دخول")
    if submit_login:
        user_ok = hmac.compare_digest(username_input.encode(), APP_USERNAME.encode())
        pass_ok = hmac.compare_digest(password_input.encode(), APP_PASSWORD.encode())
        if user_ok and pass_ok:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة.")
    st.stop()

# ---------------------- Helpers ----------------------
def now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def local_now_text() -> str:
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M:%S %p ET")

def fmt_number(value: Any, digits: int = 2, suffix: str = "") -> str:
    try:
        number = float(value)
        return f"{number:,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "غير متاح"

# ---------------------- Data Fetching ----------------------
@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_quote(symbol: str) -> dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
        if res.status_code == 200:
            data = res.json()["chart"]["result"][0]
            close = data["indicators"]["quote"][0]["close"][-1]
            return {"status": "CONNECTED", "value": float(close)}
    except Exception:
        pass
    return {"status": "NO DATA", "value": None}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_treasury_10y() -> dict[str, Any]:
    url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve"
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
        if res.status_code == 200:
            tables = pd.read_html(StringIO(res.text))
            if tables:
                df = tables[0]
                col10 = [c for c in df.columns if "10" in str(c) and "yr" in str(c).lower()]
                if col10:
                    val = float(str(df[col10[0]].dropna().iloc[-1]).replace("%", ""))
                    return {"status": "CONNECTED", "value": val}
    except Exception:
        pass
    return {"status": "NO DATA", "value": None}

# ---------------------- Session state ----------------------
if "manual_gold_price" not in st.session_state:
    st.session_state.manual_gold_price = None

gold_data = fetch_yahoo_quote("XAUUSD=X")
if gold_data["value"] is None:
    gold_data = fetch_yahoo_quote("GC=F")

dxy_data = fetch_yahoo_quote("DX-Y.NYB")
treasury_data = fetch_treasury_10y()

active_gold = st.session_state.manual_gold_price if st.session_state.manual_gold_price else gold_data["value"]

# ---------------------- Sidebar ----------------------
NAV_ITEMS = [
    "🔥 لوحة القرار والتحليل",
    "حاسبة المخاطر",
    "دفتر الصفقات",
]

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">𓂀</div><div><div class="brand-title">Aho𓂀 GOLD</div><div class="brand-sub">TERMINAL</div></div></div>', unsafe_allow_html=True)
    navigation = st.radio("القائمة الرئيسية", NAV_ITEMS, label_visibility="collapsed")
    st.divider()
    st.markdown("### مطابقة سعر الذهب")
    manual_input = st.text_input("سعر المنصة ($)", value="" if st.session_state.manual_gold_price is None else str(st.session_state.manual_gold_price))
    c1, c2 = st.columns(2)
    with c1:
        if st.button("اعتماد اليدوي"):
            try:
                p = float(manual_input)
                if p > 0: st.session_state.manual_gold_price = p; st.rerun()
            except ValueError: st.error("رقم غير صحيح")
    with c2:
        if st.button("إلغاء اليدوي"):
            st.session_state.manual_gold_price = None; st.rerun()

# ---------------------- Pages ----------------------
if navigation == NAV_ITEMS[0]:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD INTELLIGENCE</div><h1>لوحة القرار الموحد للذهب</h1><p>دمج التحليل الفني والاقتصادي وتمركزات المؤسسات.</p></div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    cols[0].metric("XAUUSD المعتمد", fmt_number(active_gold, 2, " $") if active_gold else "غير متاح")
    cols[1].metric("DXY (الدولار)", fmt_number(dxy_data["value"], 2) if dxy_data["value"] else "غير متاح")
    cols[2].metric("US 10Y (العائد)", fmt_number(treasury_data["value"], 3, "%") if treasury_data["value"] else "غير متاح")
    cols[3].metric("حالة النظام", "جاهز")

elif navigation == NAV_ITEMS[1]:
    st.markdown("## حاسبة المخاطر وإدارة العقد")
    b = st.number_input("رأس المال ($)", value=1000.0)
    r = st.number_input("نسبة المخاطرة (%)", value=1.0)
    e = st.number_input("سعر الدخول", value=float(active_gold or 0.0))
    s = st.number_input("وقف الخسارة", value=0.0)
    
    if e > 0 and s > 0 and e != s:
        dist = abs(e - s)
        loss = b * (r / 100.0)
        lots = loss / (dist * 100.0)
        st.success(f"حجم العقد المناسب: {lots:.2f} Lot (خسارة متوقعة: ${loss:.2f})")

elif navigation == NAV_ITEMS[2]:
    st.markdown("## دفتر الصفقات")
    st.info("سجل صفقاتك اليومي مجاني ومحفوظ في الجلسة.")

st.divider()
st.caption(f"{APP_NAME} • {APP_VERSION} • {local_now_text()}")
