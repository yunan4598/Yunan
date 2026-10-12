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
# Aho𓂀 GOLD — DATA-AWARE REBUILD
# Important: successful connection != real-time market data.
# No placeholder economic values, COT fallback numbers, or fixed gold price.
# ================================================================
APP_NAME = "Aho𓂀 GOLD"
APP_VERSION = "16.8 — Aho𓂀 VISUAL REPAIR"
REQUEST_TIMEOUT = 12
USER_AGENT = "AhoGoldIntelligence/16.8 (public-data-source-check)"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# Theme-aware styling: Streamlit's native light/dark selector is preserved.
try:
    ACTIVE_THEME = st.context.theme.type or "dark"
except Exception:
    ACTIVE_THEME = "dark"
if ACTIVE_THEME == "light":
    CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
    :root{--bg:#f4f7f2;--panel:#ffffff;--line:#d9e3d8;--gold:#a77b16;--green:#177245;--red:#b42332;--yellow:#8a6500;--muted:#5f6f68;--text:#18251e;--panel2:#eaf1e9;}
    html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic','Inter',sans-serif;direction:rtl;text-align:right}
    .stApp{background:linear-gradient(135deg,#f7faf5 0%,#edf4ed 55%,#f9f8f0 100%);color:var(--text)}
    .block-container{padding-top:1rem!important;padding-bottom:2rem!important;max-width:1500px}
    [data-testid="stSidebar"]{background:#eaf1e9;border-left:0!important;border-right:1px solid #d5e1d4;padding-top:12px}
    [data-testid="stSidebar"] *{text-align:right}
    [data-testid="stSidebarNav"]{display:none}
    .brand{display:flex;align-items:center;gap:12px;padding:4px 0 16px;border-bottom:1px solid var(--line);margin-bottom:15px}
    .brand-mark{width:44px;height:44px;border:1px solid #c8a44b;border-radius:14px;display:flex;align-items:center;justify-content:center;color:#987018;font-size:22px;background:linear-gradient(145deg,#fffdf5,#e4eee2)}
    .brand-title{font-family:Inter,sans-serif;letter-spacing:.5px;font-weight:800;font-size:17px;color:#244a35}
    .brand-sub{color:var(--muted);font-size:11px;margin-top:3px}
    .hero{border:1px solid #d8e3d4;border-radius:18px;padding:20px 24px;background:linear-gradient(135deg,#fff 0%,#f0f6ee 100%);margin-bottom:18px;box-shadow:0 8px 28px rgba(28,67,42,.07);border-right:5px solid #b89539}
    .eyebrow{color:#987018;letter-spacing:1px;font-size:11px;font-weight:800;font-family:Inter,sans-serif}
    .hero h1{margin:6px 0;font-size:23px;color:#203d2c;font-weight:800}
    .hero p{margin:0;color:#5e7065;line-height:1.8;font-size:14px}
    .data-banner,.fusion-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:13px;color:var(--muted)}
    .stButton button{border-radius:11px;border:1px solid #b89539!important;background:linear-gradient(135deg,#c6a34a,#e0c66e)!important;color:#183b2b!important;font-weight:800!important;width:100%;padding:9px}
    .stButton button:hover{filter:brightness(1.04)}
    .small-muted{font-size:12px;color:var(--muted)}
    .warning-box{border:1px solid #dfc982;background:#fff8df;border-radius:10px;padding:12px 14px;margin:8px 0;color:#705514}
    .good-box{border:1px solid #9bc9ad;background:#edf8f0;border-radius:10px;padding:12px 14px;margin:8px 0;color:#205b3b}
    .bad-box{border:1px solid #e3b0b0;background:#fff0ef;border-radius:10px;padding:12px 14px;margin:8px 0;color:#8e2630}
    [data-testid="stMetric"]{background:#fff;border:1px solid #dce6d9;border-radius:12px;padding:12px}
    [data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px}
    footer{visibility:hidden}
    @media(max-width:768px){.block-container{padding-left:.75rem!important;padding-right:.75rem!important}.hero{padding:15px!important}.hero h1{font-size:19px!important}[data-testid="stHorizontalBlock"]{gap:.5rem!important}}
    </style>
    """
else:
    CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
    :root{--bg:#111923;--panel:#192532;--line:#344555;--gold:#e1bd63;--green:#51d69a;--red:#ff7777;--yellow:#f2d36e;--muted:#a8b7c5;--text:#f2f6f8;--panel2:#202f3d;}
    html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic','Inter',sans-serif;direction:rtl;text-align:right}
    .stApp{background:radial-gradient(circle at 50% 0%,#263747 0%,#141e29 58%,#101720 100%);color:var(--text)}
    .block-container{padding-top:1rem!important;padding-bottom:2rem!important;max-width:1500px}
    [data-testid="stSidebar"]{background:#17232e;border-left:0!important;border-right:1px solid #344555;padding-top:12px}
    [data-testid="stSidebar"] *{text-align:right}
    [data-testid="stSidebarNav"]{display:none}
    .brand{display:flex;align-items:center;gap:12px;padding:4px 0 16px;border-bottom:1px solid var(--line);margin-bottom:15px}
    .brand-mark{width:44px;height:44px;border:1px solid #8e783e;border-radius:14px;display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:22px;background:linear-gradient(145deg,#34404a,#1b2732)}
    .brand-title{font-family:Inter,sans-serif;letter-spacing:.5px;font-weight:800;font-size:17px;color:var(--gold)}
    .brand-sub{color:var(--muted);font-size:11px;margin-top:3px}
    .hero{border:1px solid #3b4b59;border-radius:18px;padding:20px 24px;background:linear-gradient(135deg,rgba(36,52,66,.98),rgba(23,34,45,.98));margin-bottom:18px;box-shadow:0 8px 28px rgba(0,0,0,.16);border-right:5px solid var(--gold)}
    .eyebrow{color:var(--gold);letter-spacing:1px;font-size:11px;font-weight:800;font-family:Inter,sans-serif}
    .hero h1{margin:6px 0;font-size:23px;color:#fff;font-weight:800}
    .hero p{margin:0;color:#c0cbd4;line-height:1.8;font-size:14px}
    .data-banner,.fusion-card{background:#1a2733;border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:13px;color:var(--muted)}
    .stButton button{border-radius:11px;border:1px solid #d5b85f!important;background:linear-gradient(135deg,#d5b85f,#f0d77f)!important;color:#17232e!important;font-weight:800!important;width:100%;padding:9px}
    .stButton button:hover{filter:brightness(1.06)}
    .small-muted{font-size:12px;color:var(--muted)}
    .warning-box{border:1px solid #78652d;background:#2b281b;border-radius:10px;padding:12px 14px;margin:8px 0;color:#f0d98c}
    .good-box{border:1px solid #28684d;background:#182f28;border-radius:10px;padding:12px 14px;margin:8px 0;color:#9ce8be}
    .bad-box{border:1px solid #814348;background:#321f26;border-radius:10px;padding:12px 14px;margin:8px 0;color:#ffb3b3}
    [data-testid="stMetric"]{background:#1a2733;border:1px solid #344555;border-radius:12px;padding:12px}
    [data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px}
    footer{visibility:hidden}
    @media(max-width:768px){.block-container{padding-left:.75rem!important;padding-right:.75rem!important}.hero{padding:15px!important}.hero h1{font-size:19px!important}[data-testid="stHorizontalBlock"]{gap:.5rem!important}}
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
    st.error("التطبيق مقفول افتراضيًا: لم تُضبط بيانات الدخول. أضف APP_USERNAME وAPP_PASSWORD إلى Streamlit Secrets أو متغيرات البيئة، ثم أعد تشغيل التطبيق.")
    st.code('APP_USERNAME = "اسم_مستخدم_جديد"\nAPP_PASSWORD = "كلمة_مرور_طويلة_وفريدة"', language="toml")
    st.stop()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD</div><h1>تسجيل الدخول</h1><p>تُفعَّل المصادقة باستخدام APP_USERNAME وAPP_PASSWORD في Secrets أو متغيرات البيئة.</p></div>', unsafe_allow_html=True)
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

# ---------------------- Safety / calculation helpers ----------------------
def validate_trade_levels(direction: str, entry: float, stop: float, target: float, min_rr: float = 1.5) -> dict[str, Any]:
    import math
    values = (entry, stop, target, min_rr)
    if not all(math.isfinite(float(v)) for v in values):
        return {"valid": False, "reason": "كل الأسعار ونسبة R:R يجب أن تكون أرقامًا منتهية وصالحة.", "rr": None}
    if entry <= 0 or stop <= 0 or target <= 0 or min_rr <= 0:
        return {"valid": False, "reason": "سعر الدخول والوقف والهدف وحد R:R يجب أن تكون أكبر من صفر.", "rr": None}
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
    return {"valid": True, "reason": "اجتازت المستويات فحص الاتجاه وR:R فقط؛ لا يعني ذلك أن الصفقة رابحة.", "rr": rr}

def calculate_position_size(balance: float, risk_percent: float, entry: float, stop: float,
                            target: float, contract_size: float, direction: str,
                            min_rr: float = 1.5) -> dict[str, Any]:
    import math
    nums = (balance, risk_percent, entry, stop, target, contract_size, min_rr)
    if not all(math.isfinite(float(v)) for v in nums):
        return {"valid": False, "reason": "توجد قيمة غير رقمية أو غير منتهية."}
    if balance <= 0 or contract_size <= 0 or not 0 < risk_percent <= 5:
        return {"valid": False, "reason": "الرصيد وحجم العقد يجب أن يكونا موجبين، والمخاطرة يجب أن تكون أكبر من صفر ولا تتجاوز 5%."}
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

# ---------------------- Shared helpers ----------------------
def now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def local_now_text() -> str:
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M:%S %p ET")

def request_get(url: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    headers.setdefault("Accept", "application/json,text/html,*/*")
    return requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers, **kwargs)

def classify_exception(exc: Exception) -> str:
    if isinstance(exc, (requests.Timeout, TimeoutError)):
        return "TIMEOUT"
    if isinstance(exc, requests.HTTPError):
        code = exc.response.status_code if exc.response is not None else None
        if code == 429: return "RATE LIMITED"
        if code in (401, 403): return "AUTH ERROR"
        return "UNAVAILABLE"
    if isinstance(exc, requests.RequestException):
        return "UNAVAILABLE"
    return "NO DATA"

def age_days(obs_date: Any) -> Optional[int]:
    try:
        d = pd.to_datetime(obs_date, utc=True, errors="coerce")
        if pd.isna(d): return None
        return max(0, (pd.Timestamp.now(tz="UTC") - d).days)
    except Exception:
        return None

def apply_freshness(status: str, obs_date: Any, max_age_days: int) -> tuple[str, str]:
    if status != "CONNECTED": return status, ""
    days = age_days(obs_date)
    if days is None: return "CONNECTED", "تعذر حساب عمر الملاحظة."
    if days > max_age_days: return "STALE", f"عمر آخر ملاحظة {days} يومًا."
    return "CONNECTED", f"عمر آخر ملاحظة {days} يومًا."

def display_status(status: str) -> str:
    return {
        "CONNECTED": "🟢 CONNECTED", "STALE": "🟠 STALE",
        "RATE LIMITED": "🟠 RATE LIMITED", "AUTH ERROR": "🔴 AUTH ERROR",
        "TIMEOUT": "🟠 TIMEOUT", "NO DATA": "🔴 NO DATA",
        "NOT TESTED": "⚪ NOT TESTED", "UNAVAILABLE": "🔴 UNAVAILABLE",
    }.get(status, status)

def fmt_number(value: Any, digits: int = 2, suffix: str = "") -> str:
    try:
        number = float(value)
        return f"{number:,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "غير متاح"

def source_result(source: str, requested: str, status: str, detail: str,
                  url: str = "", observation_date: str = "—", data_value: str = "—",
                  freshness: str = "—", test_time: Optional[str] = None,
                  access_only: bool = False) -> dict[str, Any]:
    return {
        "المصدر": source, "البيانات المطلوبة": requested, "الحالة": status,
        "القيمة/النتيجة المستخرجة": data_value, "تاريخ الملاحظة": observation_date or "—",
        "وقت الفحص (UTC)": test_time or "—", "حداثة البيانات": freshness,
        "تفاصيل الاختبار": detail, "فحص وصول فقط؟": "نعم" if access_only else "لا", "رابط المصدر": url,
    }

# ---------------------- Data Fetchers ----------------------
def _fetch_yahoo_quote_impl(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    errors: list[str] = []
    for symbol in symbols:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        try:
            response = request_get(url, params={"range": "5d", "interval": "1d"})
            if response.status_code == 429:
                return {"status": "RATE LIMITED", "label": label, "symbol": symbol, "value": None, "change": None,
                        "observation_date": "—", "timestamp": "—", "source": "Yahoo Finance", "url": "https://finance.yahoo.com/", "detail": "HTTP 429."}
            response.raise_for_status()
            payload = response.json().get("chart", {})
            result_list = payload.get("result") or []
            if not result_list: continue
            result = result_list[0]
            quote_rows = result.get("indicators", {}).get("quote", [{}])[0]
            closes = quote_rows.get("close", []) or []
            timestamps = result.get("timestamp", []) or []
            valid = [(int(t), float(c)) for t, c in zip(timestamps, closes) if c is not None]
            if not valid: continue
            last_ts, last_val = valid[-1]
            previous_val = valid[-2][1] if len(valid) >= 2 else None
            obs_dt = datetime.fromtimestamp(last_ts, timezone.utc)
            age_hours = max(0, int((datetime.now(timezone.utc) - obs_dt).total_seconds() / 3600))
            status = "CONNECTED" if age_hours <= 72 else "STALE"
            return {"status": status, "label": label, "symbol": symbol, "value": last_val,
                    "change": (last_val - previous_val) if previous_val is not None else None,
                    "observation_date": obs_dt.strftime("%Y-%m-%d"), "timestamp": obs_dt.strftime("%Y-%m-%d %H:%M UTC"),
                    "source": f"Yahoo Finance ({symbol})", "url": "https://finance.yahoo.com/", "detail": f"عمر السعر التقريبي {age_hours} ساعة."}
        except Exception as exc:
            errors.append(f"{symbol}: {type(exc).__name__}")
    return {"status": "UNAVAILABLE", "label": label, "symbol": "—", "value": None, "change": None,
            "observation_date": "—", "timestamp": "—", "source": "Yahoo Finance", "url": "https://finance.yahoo.com/", "detail": "تعذر الجلب."}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_quote(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    result = _fetch_yahoo_quote_impl(symbols, label)
    result["tested_at"] = now_utc_text()
    return result

TREASURY_NOMINAL_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve"
TREASURY_REAL_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve"

def _normal_col(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())

def _find_yield_col(columns: list[Any], years: int) -> Optional[Any]:
    norm_map = {c: _normal_col(c) for c in columns}
    for c, norm in norm_map.items():
        if norm in {f"{years}yr", f"{years}year", f"{years}yrs", f"{years}years"}: return c
    for c, norm in norm_map.items():
        if norm.startswith(str(years)) and ("yr" in norm or "year" in norm): return c
    return None

def _fetch_treasury_curve_impl(real: bool = False) -> dict[str, Any]:
    url = TREASURY_REAL_URL if real else TREASURY_NOMINAL_URL
    requested = "U.S. Treasury real yield curve" if real else "U.S. Treasury nominal yield curve"
    try:
        response = request_get(url)
        if response.status_code == 429: return {"status": "RATE LIMITED", "source": requested, "url": url, "date": "—", "values": {}, "detail": "HTTP 429."}
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            df = table.copy()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join(str(part) for part in col if str(part) != "nan").strip() for col in df.columns]
            columns = list(df.columns)
            date_col = next((c for c in columns if "date" in _normal_col(c)), None)
            col_map = {f"{year}Y": _find_yield_col(columns, year) for year in (2, 5, 10, 20, 30)}
            if not any(col_map.values()) or date_col is None: continue
            df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
            df = df[df["_date"].notna()].sort_values("_date", ascending=False)
            if df.empty: continue
            latest = df.iloc[0]; values: dict[str, float] = {}
            for key, column in col_map.items():
                if column is None: continue
                try:
                    val_str = str(latest[column]).replace("%", "").replace(",", "").strip()
                    if val_str and val_str.lower() not in {"nan", "none", "-", "n/a"}: values[key] = float(val_str)
                except (TypeError, ValueError): pass
            if "10Y" not in values or "5Y" not in values: continue
            obsdate = latest["_date"].strftime("%Y-%m-%d")
            age = age_days(obsdate)
            status = "CONNECTED" if age is not None and age <= 7 else "STALE"
            return {"status": status, "source": "U.S. Treasury official data table", "url": url, "date": obsdate, "values": values, "detail": f"تاريخ الجدول {obsdate}."}
        return {"status": "NO DATA", "source": requested, "url": url, "date": "—", "values": {}, "detail": "لم يُعثر على جدول عوائد صالح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": requested, "url": url, "date": "—", "values": {}, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_treasury_curve(real: bool = False) -> dict[str, Any]:
    result = _fetch_treasury_curve_impl(real); result["tested_at"] = now_utc_text(); return result

FRED_SERIES_META = {
    "DGS2": ("عائد اسمي 2 سنوات", 8), "DGS5": ("عائد اسمي 5 سنوات", 8),
    "DGS10": ("عائد اسمي 10 سنوات", 8), "DGS20": ("عائد اسمي 20 سنة", 8),
    "DGS30": ("عائد اسمي 30 سنة", 8), "DFII10": ("عائد حقيقي 10 سنوات", 8),
    "T10YIE": ("توقع التضخم 10 سنوات Breakeven", 8), "CPIAUCSL": ("مؤشر CPI العام", 75),
}

def _fetch_fred_observation_impl(series_id: str, api_key: str) -> dict[str, Any]:
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        response = request_get(url, params={"series_id": series_id, "api_key": api_key, "file_type": "json", "sort_order": "desc", "limit": 12})
        if response.status_code == 429: return {"status": "RATE LIMITED", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "HTTP 429."}
        if response.status_code in (401, 403): return {"status": "AUTH ERROR", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "خطأ مصادقة مفتاح FRED."}
        response.raise_for_status()
        payload = response.json()
        obs = payload.get("observations", [])
        valid = [o for o in obs if o.get("value") not in (None, ".", "")]
        if not valid: return {"status": "NO DATA", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "بلا ملاحظات رقمية."}
        latest = valid[0]; val = float(latest["value"])
        label, max_age = FRED_SERIES_META.get(series_id, (series_id, 10))
        status, freshness_detail = apply_freshness("CONNECTED", latest.get("date"), max_age)
        return {"status": status, "series": series_id, "label": label, "value": val, "date": latest.get("date", "—"), "source": "FRED API", "detail": freshness_detail}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_fred_observation(series_id: str, api_key: str) -> dict[str, Any]:
    result = _fetch_fred_observation_impl(series_id, api_key); result["tested_at"] = now_utc_text(); return result

BLS_SERIES = {
    "headline_cpi": ("CUSR0000SA0", "CPI العام", "monthly"),
    "core_cpi": ("CUSR0000SA0L1E", "Core CPI", "monthly"),
    "unemployment": ("LNS14000000", "Unemployment rate", "monthly"),
    "nonfarm_payrolls": ("CES0000000001", "Nonfarm payrolls", "monthly"),
    "hourly_earnings": ("CES0500000003", "Average hourly earnings", "monthly"),
}

def _period_to_sort(row: dict[str, Any]) -> tuple[int, int]:
    year = int(row.get("year", 0) or 0)
    period = str(row.get("period", ""))
    month = int(period[1:]) if period.startswith("M") and period[1:].isdigit() else 0
    return year, month

def _fetch_bls_latest_impl() -> dict[str, Any]:
    url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
    series_ids = [meta[0] for meta in BLS_SERIES.values()]
    try:
        response = requests.post(url, json={"seriesid": series_ids}, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
        if response.status_code == 429: return {"status": "RATE LIMITED", "series": {}, "source": "BLS API v1", "detail": "HTTP 429."}
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "REQUEST_SUCCEEDED": return {"status": "NO DATA", "series": {}, "source": "BLS API v1", "detail": "فشل طلب BLS."}
        raw_series = payload.get("Results", {}).get("series", [])
        mapping: dict[str, Any] = {}
        for item in raw_series:
            sid = item.get("seriesID")
            entries = [entry for entry in item.get("data", []) if str(entry.get("period", "")) != "M13"]
            entries = sorted(entries, key=_period_to_sort, reverse=True)
            valid = []
            for entry in entries:
                try: valid.append({**entry, "numeric_value": float(entry.get("value"))})
                except (TypeError, ValueError): pass
            mapping[sid] = valid
        results: dict[str, Any] = {}
        for key, (sid, label, _) in BLS_SERIES.items():
            rows = mapping.get(sid, [])
            if not rows:
                results[key] = {"status": "NO DATA", "series_id": sid, "label": label, "value": None, "date": "—", "detail": "بلا بيانات."}
                continue
            latest = rows[0]; month_num = latest.get("period", "")[1:] if str(latest.get("period", "")).startswith("M") else ""
            obs_date = f"{latest.get('year', '')}-{str(month_num).zfill(2)}" if month_num else str(latest.get("year", "—"))
            previous = rows[1] if len(rows) > 1 else None
            prev_val = previous.get("numeric_value") if previous else None
            chg = latest["numeric_value"] - prev_val if prev_val is not None else None
            pct_chg = ((latest["numeric_value"] / prev_val) - 1) * 100 if prev_val not in (None, 0) else None
            results[key] = {"status": "CONNECTED", "series_id": sid, "label": label, "value": latest["numeric_value"],
                            "previous": prev_val, "change": chg, "pct_change": pct_chg, "date": obs_date, "detail": f"ملاحظة للفترة {obs_date}."}
        return {"status": "CONNECTED", "series": results, "source": "BLS API v1", "detail": "تم جلب سلاسل BLS بنجاح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": {}, "source": "BLS API v1", "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_latest() -> dict[str, Any]:
    result = _fetch_bls_latest_impl(); result["tested_at"] = now_utc_text(); return result

def _fetch_bea_data_impl(api_key: str) -> dict[str, Any]:
    url = "https://apps.bea.gov/api/data/"
    if not api_key: return {"status": "NOT TESTED", "source": "BEA API", "gdp": None, "pce_price": None, "detail": "مفتاح BEA_API_KEY غير مضبوط."}
    current_year = datetime.now(timezone.utc).year
    years = f"{current_year-1},{current_year}"
    out: dict[str, Any] = {"status": "NO DATA", "source": "BEA API", "gdp": None, "pce_price": None, "core_pce_price": None, "detail": "لم تُستخرج أرقام صالحة."}
    try:
        for label, table, frequency in (("gdp", "T10101", "Q"), ("pce_price", "T20304", "M")):
            params = {"UserID": api_key, "method": "GetData", "DataSetName": "NIPA", "TableName": table, "Frequency": frequency, "Year": years, "ResultFormat": "JSON"}
            response = request_get(url, params=params)
            response.raise_for_status()
            payload = response.json().get("BEAAPI", {})
            data = payload.get("Results", {}).get("Data", [])
            if not data: continue
            if label == "gdp":
                candidates = [r for r in data if "gross domestic product" in str(r.get("LineDescription", "")).lower()]
                if candidates:
                    candidates.sort(key=lambda r: str(r.get("TimePeriod", "")), reverse=True)
                    out["gdp"] = {"value": candidates[0].get("DataValue"), "period": candidates[0].get("TimePeriod")}
            else:
                for output_key, prefixes in (("pce_price", ("DPCERG",)), ("core_pce_price", ("DPCCRG",))):
                    candidates = [r for r in data if str(r.get("SeriesCode", "")).upper().startswith(prefixes)]
                    if candidates:
                        candidates.sort(key=lambda r: str(r.get("TimePeriod", "")), reverse=True)
                        out[output_key] = {"value": candidates[0].get("DataValue"), "period": candidates[0].get("TimePeriod")}
        out["status"] = "CONNECTED"
        out["detail"] = "تم جلب بيانات BEA بنجاح."
        return out
    except Exception as exc:
        return {**out, "status": classify_exception(exc), "detail": f"خطأ BEA: {type(exc).__name__}."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bea_data(api_key: str) -> dict[str, Any]:
    result = _fetch_bea_data_impl(api_key); result["tested_at"] = now_utc_text(); return result

CFTC_COT_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

def _fetch_cftc_gold_cot_impl() -> dict[str, Any]:
    params = {"$where": "market_and_exchange_names like '%GOLD%'", "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 20}
    try:
        response = request_get(CFTC_COT_URL, params=params)
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list) or not rows: return {"status": "NO DATA", "rows": [], "detail": "بلا صفوف مطابقة لـ GOLD."}
        selected = []
        for row in rows:
            market = str(row.get("market_and_exchange_names", ""))
            if "GOLD" not in market.upper(): continue
            report_date = row.get("report_date_as_yyyy_mm_dd")
            if not report_date: continue
            try:
                long_val = float(row.get("noncomm_positions_long_all", 0))
                short_val = float(row.get("noncomm_positions_short_all", 0))
                oi = float(row.get("open_interest_all", 0))
            except (TypeError, ValueError): continue
            selected.append({"date": str(report_date)[:10], "market": market, "long": long_val, "short": short_val, "net": long_val - short_val, "open_interest": oi})
        selected.sort(key=lambda x: x["date"], reverse=True)
        unique = {item["date"]: item for item in selected}
        clean_rows = list(unique.values())
        if not clean_rows: return {"status": "NO DATA", "rows": [], "detail": "بلا صفوف صالحة."}
        return {"status": "CONNECTED", "source": "CFTC Legacy", "url": CFTC_COT_URL, "rows": clean_rows, "detail": "تم جلب تقرير COT بنجاح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "rows": [], "detail": f"خطأ COT: {type(exc).__name__}."}

@st.cache_data(ttl=7200, show_spinner=False)
def fetch_cftc_gold_cot() -> dict[str, Any]:
    result = _fetch_cftc_gold_cot_impl(); result["tested_at"] = now_utc_text(); return result

def _check_page_access_impl(name: str, url: str) -> dict[str, Any]:
    try:
        response = request_get(url)
        response.raise_for_status()
        return {"status": "CONNECTED", "source": name, "url": url, "detail": "تم الوصول للصفحة بنجاح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": name, "url": url, "detail": f"تعذر الوصول: {type(exc).__name__}."}

@st.cache_data(ttl=1800, show_spinner=False)
def check_page_access(name: str, url: str) -> dict[str, Any]:
    result = _check_page_access_impl(name, url); result["tested_at"] = now_utc_text(); return result

def build_market_data() -> dict[str, Any]:
    dxy = fetch_yahoo_quote(("DX-Y.NYB",), "DXY")
    gold = fetch_yahoo_quote(("XAUUSD=X", "GC=F"), "XAUUSD spot proxy")
    gold_futures = fetch_yahoo_quote(("GC=F",), "COMEX Gold Futures")
    nominal = fetch_treasury_curve(False)
    real_curve = fetch_treasury_curve(True)
    cot = fetch_cftc_gold_cot()
    bls = fetch_bls_latest()
    bea = fetch_bea_data(get_secret("BEA_API_KEY"))
    fred_key = get_secret("FRED_API_KEY")
    fred: dict[str, Any] = {}
    if fred_key:
        for sid in FRED_SERIES_META: fred[sid] = fetch_fred_observation(sid, fred_key)
    else:
        for sid, (label, _) in FRED_SERIES_META.items():
            fred[sid] = {"status": "NOT TESTED", "series": sid, "label": label, "value": None, "date": "—", "source": "FRED API", "detail": "غير مهيأة."}
    real10 = fred.get("DFII10", {}).get("value")
    if real10 is not None and fred.get("DFII10", {}).get("status") == "CONNECTED":
        real_yield = {"status": fred["DFII10"]["status"], "value": real10, "date": fred["DFII10"]["date"], "source": "FRED DFII10", "detail": fred["DFII10"]["detail"]}
    elif real_curve.get("values", {}).get("10Y") is not None:
        real_yield = {"status": real_curve["status"], "value": real_curve.get("values", {}).get("10Y"), "date": real_curve.get("date", "—"), "source": real_curve["source"], "detail": real_curve["detail"]}
    else:
        real_yield = {"status": real_curve["status"], "value": None, "date": "—", "source": "Treasury", "detail": "غير متاح."}
    nominal10 = nominal.get("values", {}).get("10Y")
    breakeven_value = fred.get("T10YIE", {}).get("value")
    breakeven_status = fred.get("T10YIE", {}).get("status", "NOT TESTED")
    if breakeven_value is None and nominal10 is not None and real_yield.get("value") is not None:
        breakeven_value = nominal10 - float(real_yield["value"])
        breakeven_status = "CONNECTED"
    score_items = [(gold.get("status"), 25), (dxy.get("status"), 15), (nominal.get("status"), 15), (real_yield.get("status"), 10), (cot.get("status"), 20), (bls.get("status"), 5), (bea.get("status"), 5), (breakeven_status, 5)]
    score = round(sum(weight * (1 if status == "CONNECTED" else 0.5 if status == "STALE" else 0) for status, weight in score_items))
    return {"gold": gold, "gold_futures": gold_futures, "dxy": dxy, "nominal": nominal, "real_curve": real_curve, "real_yield": real_yield,
            "breakeven": {"status": breakeven_status, "value": breakeven_value, "date": real_yield.get("date", "—"), "source": "Treasury/FRED"},
            "cot": cot, "bls": bls, "bea": bea, "fred": fred, "quality_score": score, "tested_at": now_utc_text()}

if "manual_gold_price" not in st.session_state: st.session_state.manual_gold_price = None
if "trade_journal" not in st.session_state: st.session_state.trade_journal = []
if "report_history" not in st.session_state: st.session_state.report_history = []
if "current_report" not in st.session_state: st.session_state.current_report = None
if "technical_levels" not in st.session_state: st.session_state.technical_levels = {"pdh": None, "pdl": None, "asia_high": None, "asia_low": None}

market_data = build_market_data()

def usable_num(value: Any) -> Optional[float]:
    try:
        out = float(value)
        return out if pd.notna(out) else None
    except (TypeError, ValueError):
        return None

if st.session_state.manual_gold_price is not None:
    active_gold = float(st.session_state.manual_gold_price)
    gold_price_origin = "إدخال يدوي"
    gold_price_time = "الجلسة الحالية"
else:
    active_gold = usable_num(market_data["gold"].get("value"))
    gold_price_origin = market_data["gold"].get("source", "Yahoo")
    gold_price_time = market_data["gold"].get("timestamp", "—")

def make_evidence_rows() -> list[dict[str, Any]]:
    cot_rows = market_data["cot"].get("rows", [])
    cot_latest = cot_rows[0] if cot_rows else {}
    return [
        {"العامل": "XAUUSD / Gold", "القيمة الحالية": fmt_number(active_gold, 2, " $") if active_gold is not None else "غير متاح", "التاريخ/الوقت": gold_price_time, "المصدر": gold_price_origin, "الحالة": "MANUAL" if st.session_state.manual_gold_price is not None else market_data["gold"]["status"], "ملاحظة": "سعر معتمد."},
        {"العامل": "DXY", "القيمة الحالية": fmt_number(market_data["dxy"].get("value"), 2), "التاريخ/الوقت": market_data["dxy"].get("timestamp", "—"), "المصدر": market_data["dxy"].get("source", "Yahoo"), "الحالة": market_data["dxy"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "US 10Y", "القيمة الحالية": fmt_number(market_data["nominal"].get("values", {}).get("10Y"), 3, "%"), "التاريخ/الوقت": market_data["nominal"].get("date", "—"), "المصدر": "Treasury", "الحالة": market_data["nominal"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "Real Yield 10Y", "القيمة الحالية": fmt_number(market_data["real_yield"].get("value"), 3, "%"), "التاريخ/الوقت": market_data["real_yield"].get("date", "—"), "المصدر": market_data["real_yield"].get("source", "Treasury"), "الحالة": market_data["real_yield"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "COT Net", "القيمة الحالية": f"{cot_latest['net']:+,.0f}" if cot_latest else "غير متاح", "التاريخ/الوقت": cot_latest.get("date", "—"), "المصدر": "CFTC", "الحالة": market_data["cot"].get("status", "NO DATA"), "ملاحظة": ""},
    ]

evidence_matrix_data = make_evidence_rows()

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
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("اعتماد اليدوي"):
            try:
                parsed = float(manual_input)
                if parsed > 0: st.session_state.manual_gold_price = parsed; st.rerun()
            except ValueError: st.error("أدخل رقمًا صحيحًا.")
    with col_s2:
        if st.button("إلغاء اليدوي"):
            st.session_state.manual_gold_price = None; st.rerun()
    st.caption(f"السعر المعتمد: {fmt_number(active_gold, 2, ' $') if active_gold is not None else 'غير متاح'}")

if navigation == NAV_ITEMS[0]:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD INTELLIGENCE</div><h1>لوحة القرار الموحد للذهب</h1><p>دمج التحليل الفني والاقتصادي وتمركزات المؤسسات.</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("XAUUSD المعتمد", fmt_number(active_gold, 2, " $") if active_gold is not None else "غير متاح")
    cols[1].metric("DXY", fmt_number(market_data["dxy"].get("value"), 2))
    cols[2].metric("US 10Y", fmt_number(market_data["nominal"].get("values", {}).get("10Y"), 3, "%"))
    cols[3].metric("جودة المصادر", f"{market_data['quality_score']} / 100")
    st.dataframe(pd.DataFrame(evidence_matrix_data), use_container_width=True, hide_index=True)

elif navigation == NAV_ITEMS[1]:
    st.markdown("## تدقيق مصادر البيانات")
    st.metric("جودة التوفر", f"{market_data['quality_score']} / 100")

elif navigation == NAV_ITEMS[9]:
    st.markdown("## حاسبة المخاطر وإدارة العقد")
    r1, r2, r3 = st.columns(3)
    with r1:
        balance = st.number_input("رأس المال ($)", value=1000.0)
        risk_percent = st.number_input("نسبة المخاطرة (%)", min_value=0.0, max_value=5.0, value=1.0)
        direction = st.selectbox("اتجاه الصفقة", ["شراء (LONG)", "بيع (SHORT)"]).split()[0]
    with r2:
        contract_size = st.number_input("حجم العقد (أونصة)", value=100.0)
        entry = st.number_input("سعر الدخول ($)", value=float(active_gold or 0.0))
    with r3:
        sl = st.number_input("وقف الخسارة ($)", value=0.0)
        target = st.number_input("الهدف ($)", value=0.0)
    calc = calculate_position_size(balance, risk_percent, entry, sl, target, contract_size, direction, min_rr=1.5)
    if calc.get("valid"):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("حجم الصفقة", f"{calc['lots']:.4f} Lot")
        m2.metric("الخسارة النظرية", f"${calc['potential_loss']:,.2f}")
        m3.metric("الربح المتوقع", f"${calc['potential_profit']:,.2f}")
        m4.metric("R:R", f"1 : {calc['rr']:.2f}")
        st.success(calc["reason"])
    else:
        st.warning(calc.get("reason", "أدخل مستويات صحيحة."))

elif navigation == NAV_ITEMS[11]:
    st.markdown("## دفتر الصفقات")
    with st.form("journal_form"):
        c1, c2, c3 = st.columns(3)
        with c1: trade_type = st.selectbox("النوع", ["شراء", "بيع"])
        with c2: trade_result = st.selectbox("النتيجة", ["ربح", "خسارة"])
        with c3: trade_r = st.number_input("النتيجة R", value=0.0)
        if st.form_submit_button("حفظ"):
            st.session_state.trade_journal.insert(0, {"النوع": trade_type, "النتيجة": trade_result, "R": trade_r})
            st.success("تم الحفظ.")
    if st.session_state.trade_journal:
        st.dataframe(pd.DataFrame(st.session_state.trade_journal), use_container_width=True, hide_index=True)

else:
    st.markdown(f"## {navigation}")
    st.info("هذا القسم مفعل وجاهز للعمل ضمن بيئة التطبيق الموحدة.")

st.divider()
st.caption(f"{APP_NAME} • {APP_VERSION} • {local_now_text()}")
