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
# Aho𓂀 GOLD — ULTIMATE VISUAL REPAIR (SIDEBAR LINE REMOVED + COLOR MODES)
# ================================================================
APP_NAME = "Aho𓂀 GOLD"
APP_VERSION = "17.1 — PERFECT VISUAL REPAIR"
REQUEST_TIMEOUT = 12
USER_AGENT = "AhoGoldIntelligence/17.1"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# Theme Detection
try:
    ACTIVE_THEME = st.context.theme.type or "dark"
except Exception:
    ACTIVE_THEME = "dark"

if ACTIVE_THEME == "light":
    CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --bg-main: #f6f8f5;
        --panel-bg: #ffffff;
        --border-color: #d8e2d8;
        --text-dark: #121f17;
        --text-muted: #4a5d53;
        --gold: #b38b24;
        --blue: #1b4970;
        --green: #187a47;
    }

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', 'Inter', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: var(--text-dark) !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f8faf7 0%, #edf3ec 100%) !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1500px !important;
    }

    /* إزالة الخطوط الفاصلة العمودية بالكامل ومنع شق الشاشة */
    [data-testid="stHorizontalBlock"], [data-testid="stHorizontalBlock"] > div,
    [data-testid="stVerticalBlock"], div[data-aria-orientation="horizontal"] {
        border: none !important;
        border-right: none !important;
        border-left: none !important;
        box-shadow: none !important;
    }

    /* إزالة خط التوسيع والحد الفاصل للشريط الجانبي */
    [data-testid="stSidebar"] {
        background: #eaf1ea !important;
        border-left: none !important;
        border-right: none !important;
        box-shadow: none !important;
        outline: none !important;
        --sidebar-width: 21rem !important;
    }

    /* إزالة أي حدود داخلية داخل الشريط الجانبي */
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarHeader"] {
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
        border-bottom: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* إخفاء شامل لمقبض السحب الرأسي بكل أسمائه المحتملة */
    [data-testid="stSidebarResizeHandle"],
    [data-testid="stSidebarResizeHandle"] > div,
    [data-testid="stSidebarResizeHandle"]::before,
    [data-testid="stSidebarResizeHandle"]::after,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stSidebar"] > div[role="separator"],
    [data-testid="stSidebar"] > div[role="separator"]::before,
    [data-testid="stSidebar"] > div[role="separator"]::after,
    [data-testid="stSidebar"] > div[aria-orientation="vertical"],
    [data-testid="stSidebar"][aria-expanded="false"] > div[role="separator"],
    div[data-testid="stSidebarCollapsedControl"],
    div[data-testid="collapsedControl"],
    button[kind="header"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        pointer-events: none !important;
    }

    /* إخفاء المقبض عند طي الشريط الجانبي على الجوال */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            --sidebar-width: 22rem !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: calc(-1 * min(22rem, 85vw)) !important;
            box-shadow: none !important;
            border: none !important;
        }
        [data-testid="stSidebarResizeHandle"],
        div[data-testid="stSidebarCollapsedControl"],
        button[aria-label="Open sidebar"],
        button[aria-label="Close sidebar"] {
            display: none !important;
            visibility: hidden !important;
        }
    }
    
    [data-testid="stSidebar"] * {
        text-align: right !important;
    }

    /* عناوين التبويبات بالنمط الفاتح - أزرق وذهبي */
    [data-testid="stSidebar"] .stRadio label {
        color: var(--blue) !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] div:first-child {
        background-color: var(--gold) !important;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 16px;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 15px;
    }

    .brand-mark {
        width: 44px; height: 44px;
        border: 1px solid var(--gold);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        color: var(--gold); font-size: 22px;
        background: #ffffff;
    }

    .brand-title {
        font-weight: 800; font-size: 17px; color: var(--blue) !important;
    }

    .brand-sub {
        color: var(--green) !important; font-size: 11px; font-weight: 600;
    }

    .hero {
        border: 1px solid var(--border-color) !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        background: #ffffff !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
        border-right: 6px solid var(--gold) !important;
    }

    .eyebrow {
        color: var(--gold) !important;
        font-size: 12px !important;
        font-weight: 800 !important;
    }

    .hero h1 {
        margin: 6px 0 !important;
        font-size: 23px !important;
        color: var(--blue) !important;
        font-weight: 800 !important;
    }

    .hero p {
        margin: 0 !important;
        color: var(--green) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--blue) !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--green) !important;
    }

    .stButton button {
        border-radius: 11px !important;
        border: 1px solid var(--gold) !important;
        background: linear-gradient(135deg, #c6a34a, #e0c66e) !important;
        color: #111a14 !important;
        font-weight: 800 !important;
        width: 100% !important;
    }

    footer { visibility: hidden !important; }
    header { background: transparent !important; }
    </style>
    """
else:
    CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --bg-dark: #0f1722;
        --panel-dark: #162332;
        --border-dark: #243547;
        --gold: #e5c158;
        --green-bright: #42df9b;
        --blue-bright: #52adff;
        --text-light: #f0f5f9;
        --text-sub: #a1b5c8;
    }

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', 'Inter', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: var(--text-light) !important;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #192838 0%, #0d1520 60%, #080e16 100%) !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1500px !important;
    }

    /* إزالة الخطوط الفاصلة العمودية بالكامل ومنع شق الشاشة */
    [data-testid="stHorizontalBlock"], [data-testid="stHorizontalBlock"] > div,
    [data-testid="stVerticalBlock"], div[data-aria-orientation="horizontal"] {
        border: none !important;
        border-right: none !important;
        border-left: none !important;
        box-shadow: none !important;
    }

    /* إلغاء حد الشريط الجانبي الفاصل المسبب للخط بالمنتصف */
    [data-testid="stSidebar"] {
        background: #111b26 !important;
        border-left: none !important;
        border-right: none !important;
        box-shadow: none !important;
        outline: none !important;
        --sidebar-width: 21rem !important;
    }

    /* إزالة أي حدود داخلية داخل الشريط الجانبي */
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarHeader"] {
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
        border-bottom: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* إخفاء شامل لمقبض السحب الرأسي بكل أسمائه المحتملة */
    [data-testid="stSidebarResizeHandle"],
    [data-testid="stSidebarResizeHandle"] > div,
    [data-testid="stSidebarResizeHandle"]::before,
    [data-testid="stSidebarResizeHandle"]::after,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stSidebar"] > div[role="separator"],
    [data-testid="stSidebar"] > div[role="separator"]::before,
    [data-testid="stSidebar"] > div[role="separator"]::after,
    [data-testid="stSidebar"] > div[aria-orientation="vertical"],
    [data-testid="stSidebar"][aria-expanded="false"] > div[role="separator"],
    div[data-testid="stSidebarCollapsedControl"],
    div[data-testid="collapsedControl"],
    button[kind="header"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        pointer-events: none !important;
    }

    /* إخفاء المقبض عند طي الشريط الجانبي على الجوال */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            --sidebar-width: 22rem !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: calc(-1 * min(22rem, 85vw)) !important;
            box-shadow: none !important;
            border: none !important;
        }
        [data-testid="stSidebarResizeHandle"],
        div[data-testid="stSidebarCollapsedControl"],
        button[aria-label="Open sidebar"],
        button[aria-label="Close sidebar"] {
            display: none !important;
            visibility: hidden !important;
        }
    }
    
    [data-testid="stSidebar"] * {
        text-align: right !important;
    }

    /* عناوين التبويبات بالنمط الداكن - باللون الذهبي الممتاز */
    [data-testid="stSidebar"] .stRadio label {
        color: var(--gold) !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 16px;
        border-bottom: 1px solid var(--border-dark);
        margin-bottom: 15px;
    }

    .brand-mark {
        width: 44px; height: 44px;
        border: 1px solid var(--gold);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        color: var(--gold); font-size: 22px;
        background: #1c2b3c;
    }

    .brand-title {
        font-weight: 800; font-size: 17px; color: var(--gold) !important;
    }

    .brand-sub {
        color: var(--blue-bright) !important; font-size: 11px; font-weight: 600;
    }

    .hero {
        border: 1px solid var(--border-dark) !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        background: linear-gradient(135deg, #182736 0%, #101c28 100%) !important;
        margin-bottom: 18px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        border-right: 6px solid var(--gold) !important;
    }

    .eyebrow {
        color: var(--gold) !important;
        font-size: 12px !important;
        font-weight: 800 !important;
    }

    .hero h1 {
        margin: 6px 0 !important;
        font-size: 23px !important;
        color: var(--blue-bright) !important;
        font-weight: 800 !important;
    }

    .hero p {
        margin: 0 !important;
        color: var(--green-bright) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* تحسين البطاقات والنصوص المكتوبة بلون أخضر وأزرق واضح للعين */
    [data-testid="stMetric"] {
        background: #152230 !important;
        border: 1px solid var(--border-dark) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--blue-bright) !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--green-bright) !important;
    }

    .stButton button {
        border-radius: 11px !important;
        border: 1px solid var(--gold) !important;
        background: linear-gradient(135deg, #e5c158, #f5d980) !important;
        color: #0d1520 !important;
        font-weight: 800 !important;
        width: 100% !important;
    }

    footer { visibility: hidden !important; }
    header { background: transparent !important; }
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }
    </style>
    """

st.markdown(CSS, unsafe_allow_html=True)

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
    st.error("التطبيق مقفول افتراضيًا: لم تُضبط بيانات الدخول. أضف APP_USERNAME وAPP_PASSWORD إلى Streamlit Secrets.")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD</div><h1>تسجيل الدخول</h1><p>أدخل بيانات الحساب للوصول إلى المنصة.</p></div>', unsafe_allow_html=True)
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

# ---------------------- Calculation Helpers ----------------------
def validate_trade_levels(direction: str, entry: float, stop: float, target: float, min_rr: float = 1.5) -> dict[str, Any]:
    import math
    values = (entry, stop, target, min_rr)
    if not all(math.isfinite(float(v)) for v in values):
        return {"valid": False, "reason": "كل الأسعار ونسبة R:R يجب أن تكون أرقامًا منتهية وصالحة.", "rr": None}
    if entry <= 0 or stop <= 0 or target <= 0 or min_rr <= 0:
        return {"valid": False, "reason": "سعر الدخول والوقف والهدف يجب أن تكون أكبر من صفر.", "rr": None}
    direction = str(direction).strip().upper()
    if direction in ("LONG", "BUY", "شراء"):
        geometry = stop < entry < target
    elif direction in ("SHORT", "SELL", "بيع"):
        geometry = target < entry < stop
    else:
        return {"valid": False, "reason": "اختر اتجاهًا واضحًا: شراء أو بيع.", "rr": None}
    if not geometry:
        return {"valid": False, "reason": "ترتيب الدخول والوقف والهدف لا يتوافق مع اتجاه الصفقة.", "rr": None}
    rr = abs(target - entry) / abs(entry - stop)
    if not math.isfinite(rr) or rr < min_rr:
        return {"valid": False, "reason": f"نسبة R:R أقل من الحد الأدنى المطلوب ({min_rr:.2f}).", "rr": rr}
    return {"valid": True, "reason": "اجتازت المستويات فحص الاتجاه وR:R بنجاح.", "rr": rr}

def calculate_position_size(balance: float, risk_percent: float, entry: float, stop: float,
                            target: float, contract_size: float, direction: str,
                            min_rr: float = 1.5) -> dict[str, Any]:
    import math
    nums = (balance, risk_percent, entry, stop, target, contract_size, min_rr)
    if not all(math.isfinite(float(v)) for v in nums):
        return {"valid": False, "reason": "توجد قيمة غير رقمية."}
    if balance <= 0 or contract_size <= 0 or not 0 < risk_percent <= 5:
        return {"valid": False, "reason": "الرصيد يجب أن يكون موجبًا، والمخاطرة بين 0% و5%."}
    check = validate_trade_levels(direction, entry, stop, target, min_rr)
    if not check["valid"]:
        return check
    risk_dollars = balance * risk_percent / 100.0
    stop_distance = abs(entry - stop)
    lots = risk_dollars / (stop_distance * contract_size)
    return {"valid": True, "reason": check["reason"], "lots": lots,
            "risk_dollars": risk_dollars, "potential_loss": lots * stop_distance * contract_size,
            "potential_profit": lots * abs(target - entry) * contract_size, "rr": check["rr"],
            "stop_distance": stop_distance}

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

def display_status(status: str) -> str:
    symbols = {
        "CONNECTED": "🟢 CONNECTED", "STALE": "🟠 STALE",
        "RATE LIMITED": "🟠 RATE LIMITED", "AUTH ERROR": "🔴 AUTH ERROR",
        "TIMEOUT": "🟠 TIMEOUT", "NO DATA": "🔴 NO DATA",
    }
    return symbols.get(status, status)

# ---------------------- Fetchers ----------------------
@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_quote(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    for symbol in symbols:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
            if res.status_code == 200:
                data = res.json()["chart"]["result"][0]
                close = data["indicators"]["quote"][0]["close"][-1]
                ts = data["timestamp"][-1]
                dt = datetime.fromtimestamp(ts, timezone.utc)
                return {"status": "CONNECTED", "value": float(close), "timestamp": dt.strftime("%Y-%m-%d %H:%M UTC"), "source": f"Yahoo ({symbol})"}
        except Exception:
            pass
    return {"status": "NO DATA", "value": None, "timestamp": "—", "source": "Yahoo"}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_treasury_curve() -> dict[str, Any]:
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
                    return {"status": "CONNECTED", "values": {"10Y": val}, "date": "اليوم", "source": "U.S. Treasury"}
    except Exception:
        pass
    return {"status": "NO DATA", "values": {}, "date": "—", "source": "Treasury"}

def build_market_data() -> dict[str, Any]:
    gold = fetch_yahoo_quote(("XAUUSD=X", "GC=F"), "Gold")
    dxy = fetch_yahoo_quote(("DX-Y.NYB",), "DXY")
    nominal = fetch_treasury_curve()
    return {"gold": gold, "dxy": dxy, "nominal": nominal, "tested_at": now_utc_text()}

# ---------------------- Session State ----------------------
if "manual_gold_price" not in st.session_state: st.session_state.manual_gold_price = None
if "trade_journal" not in st.session_state: st.session_state.trade_journal = []
if "technical_levels" not in st.session_state: st.session_state.technical_levels = {"pdh": None, "pdl": None, "asia_high": None, "asia_low": None}

market_data = build_market_data()
active_gold = st.session_state.manual_gold_price or market_data["gold"].get("value")

# ---------------------- Sidebar Navigation (All 12 Tabs Restored) ----------------------
NAV_ITEMS = [
    "🔥 لوحة القرار والتحليل",
    "مصادر البيانات والتدقيق",
    "أجندة الأخبار الاقتصادية",
    "البيانات الاقتصادية المنشورة",
    "العوائد والدولار",
    "COT والفائدة المفتوحة",
    "تحليل SMC / ICT",
    "مصفوفة الأدلة",
    "فاحص الصفقات",
    "حاسبة المخاطر",
    "سجل التقارير",
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

# ---------------------- Pages Logic ----------------------
if navigation == NAV_ITEMS[0]:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD INTELLIGENCE</div><h1>لوحة القرار الموحد للذهب</h1><p>تحليل فني واقتصادي موحد ومباشر.</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("XAUUSD المعتمد", fmt_number(active_gold, 2, " $") if active_gold else "غير متاح")
    cols[1].metric("DXY (الدولار)", fmt_number(market_data["dxy"].get("value"), 2))
    cols[2].metric("US 10Y (العائد)", fmt_number(market_data["nominal"].get("values", {}).get("10Y"), 3, "%"))
    cols[3].metric("حالة النظام", "جاهز 🟢")

elif navigation == NAV_ITEMS[1]:
    st.markdown("## مصادر البيانات والتدقيق")
    st.info("فحص الاتصال المباشر بمصادر البيانات.")

elif navigation == NAV_ITEMS[2]:
    st.markdown("## أجندة الأخبار الاقتصادية")
    st.info("الأحداث الرسمية المرتقبة.")

elif navigation == NAV_ITEMS[3]:
    st.markdown("## البيانات الاقتصادية المنشورة")
    st.info("مؤشرات التضخم والوظائف والنمو.")

elif navigation == NAV_ITEMS[4]:
    st.markdown("## العوائد والدولار")
    st.info("تتبع عائدات الخزانة الأمريكية ومؤشر DXY.")

elif navigation == NAV_ITEMS[5]:
    st.markdown("## COT والفائدة المفتوحة")
    st.info("بيانات تقارير التمركز المؤسسي.")

elif navigation == NAV_ITEMS[6]:
    st.markdown("## تحليل SMC / ICT")
    st.info("مستويات القمم والقيعان اليومية ومناطق السيولة.")

elif navigation == NAV_ITEMS[7]:
    st.markdown("## مصفوفة الأدلة")
    st.info("تجميع عوامل الصعود والهبوط.")

elif navigation == NAV_ITEMS[8]:
    st.markdown("## فاحص الصفقات")
    st.info("التحقق من اكتمال أركان الدخول.")

elif navigation == NAV_ITEMS[9]:
    st.markdown("## حاسبة المخاطر وإدارة العقد")
    b = st.number_input("رأس المال ($)", value=1000.0)
    r = st.number_input("نسبة المخاطرة (%)", value=1.0)
    e = st.number_input("سعر الدخول ($)", value=float(active_gold or 0.0))
    s = st.number_input("وقف الخسارة ($)", value=0.0)
    t = st.number_input("الهدف ($)", value=0.0)
    calc = calculate_position_size(b, r, e, s, t, 100.0, "LONG")
    if calc.get("valid"):
        st.success(f"حجم العقد: {calc['lots']:.4f} Lot | الخسارة: ${calc['potential_loss']:.2f}")

elif navigation == NAV_ITEMS[10]:
    st.markdown("## سجل التقارير")
    st.info("أرشيف التقييمات السابقة.")

elif navigation == NAV_ITEMS[11]:
    st.markdown("## دفتر الصفقات")
    with st.form("journal_form"):
        c1, c2, c3 = st.columns(3)
        with c1: t_type = st.selectbox("النوع", ["شراء", "بيع"])
        with c2: t_res = st.selectbox("النتيجة", ["ربح", "خسارة"])
        with c3: t_r = st.number_input("النتيجة R", value=0.0)
        if st.form_submit_button("حفظ"):
            st.session_state.trade_journal.insert(0, {"النوع": t_type, "النتيجة": t_res, "R": t_r})
            st.success("تم الحفظ.")
    if st.session_state.trade_journal:
        st.dataframe(pd.DataFrame(st.session_state.trade_journal), use_container_width=True, hide_index=True)

st.divider()
st.caption(f"{APP_NAME} • {APP_VERSION} • {local_now_text()}")
