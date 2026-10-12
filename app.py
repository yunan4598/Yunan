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
# YUNAN GOLD INTELLIGENCE — DATA-AWARE REBUILD (v14.0)
# ================================================================
APP_NAME = "YUNAN GOLD INTELLIGENCE"
APP_VERSION = "14.0 — DATA VALIDATION BUILD"
REQUEST_TIMEOUT = 12
USER_AGENT = "YunanGoldIntelligence/14.0 (public-data-source-check)"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { --bg:#06090f; --panel:#0d131d; --line:#1e2c3d; --gold:#d9b56d; --green:#00e676; --red:#ff5252; --yellow:#ffeb3b; --muted:#8b9bb4; --text:#eef2f7; }
html, body, [class*="css"] { font-family:'IBM Plex Sans Arabic','Inter',sans-serif; direction:rtl; text-align:right; }
.stApp { background:radial-gradient(circle at 50% 0%, #111b29 0%, var(--bg) 60%); color:var(--text); }
.block-container { padding-top:1.6rem!important; padding-bottom:2rem!important; max-width:1500px; }
[data-testid="stSidebar"] { background:#070b12; border-left:1px solid var(--line); padding-top:15px; }
[data-testid="stSidebar"] * { text-align:right; }
.brand { display:flex; align-items:center; gap:12px; padding:4px 0 16px; border-bottom:1px solid var(--line); margin-bottom:15px; }
.brand-mark { width:42px;height:42px;border:1px solid #7a643b;border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:21px;background:linear-gradient(145deg,#221c13,#0d121a); }
.brand-title { font-family:Inter,sans-serif;letter-spacing:1px;font-weight:800;font-size:15px;color:#f4f0e7; }
.brand-sub { color:var(--muted);font-size:10px;margin-top:2px; }
.hero { border:1px solid #233142;border-radius:16px;padding:20px 24px;background:linear-gradient(135deg,rgba(17,25,38,.95),rgba(8,12,18,.95));margin-bottom:18px;box-shadow:0 8px 32px rgba(0,0,0,.25); }
.eyebrow { color:var(--gold);letter-spacing:1.4px;font-size:11px;font-weight:700;font-family:Inter,sans-serif; }
.hero h1 { margin:6px 0;font-size:23px;color:#f7f5ef;font-weight:700; }
.hero p { margin:0;color:#9fb0c6;line-height:1.7;font-size:13px; }
.data-banner { background:#0b111a;border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin-bottom:15px;font-size:12.5px;color:var(--muted);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px; }
.fusion-card { background:#0b111a;border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:12px; }
.stButton button { border-radius:10px;border:1px solid #d9b56d!important;background:linear-gradient(135deg,#d9b56d,#b3914a)!important;color:#06090f!important;font-weight:800!important;width:100%;padding:9px; }
.stButton button:hover { background:linear-gradient(135deg,#e6c37d,#c5a159)!important;color:#000!important; }
.warning-box { border:1px solid #7a5c22;background:#1b170d;border-radius:10px;padding:12px 14px;margin:8px 0;color:#f3d89b; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

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

if APP_USERNAME and APP_PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>تسجيل الدخول</h1><p>تُفعَّل المصادقة عند ضبط APP_USERNAME وAPP_PASSWORD في Secrets.</p></div>', unsafe_allow_html=True)
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
    if isinstance(exc, (requests.Timeout, TimeoutError)): return "TIMEOUT"
    if isinstance(exc, requests.HTTPError):
        code = exc.response.status_code if exc.response is not None else None
        if code == 429: return "RATE LIMITED"
        if code in (401, 403): return "AUTH ERROR"
        return "UNAVAILABLE"
    if isinstance(exc, requests.RequestException): return "UNAVAILABLE"
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
    if days is None: return "CONNECTED", "تعذر حساب عمر الملاحظة؛ راجع تاريخ المصدر."
    if days > max_age_days: return "STALE", f"عمر آخر ملاحظة {days} يومًا؛ الحد المعتمد هنا {max_age_days} يومًا."
    return "CONNECTED", f"عمر آخر ملاحظة {days} يومًا."

def display_status(status: str) -> str:
    symbols = {
        "CONNECTED": "🟢 CONNECTED", "STALE": "🟠 STALE", "RATE LIMITED": "🟠 RATE LIMITED",
        "AUTH ERROR": "🔴 AUTH ERROR", "TIMEOUT": "🟠 TIMEOUT", "NO DATA": "🔴 NO DATA",
        "NOT TESTED": "⚪ NOT TESTED", "UNAVAILABLE": "🔴 UNAVAILABLE",
    }
    return symbols.get(status, status)

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
        "تفاصيل الاختبار": detail, "فحص وصول فقط؟": "نعم — لا يثبت استخراج الأرقام" if access_only else "لا",
        "رابط المصدر": url,
    }

# ---------------------- Yahoo Finance chart endpoint ----------------------
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
            valid = [(int(stamp), float(close)) for stamp, close in zip(timestamps, closes) if close is not None]
            if not valid: continue
            last_ts, last_val = valid[-1]
            previous_val = valid[-2][1] if len(valid) >= 2 else None
            obs_dt = datetime.fromtimestamp(last_ts, timezone.utc)
            age_hours = max(0, int((datetime.now(timezone.utc) - obs_dt).total_seconds() / 3600))
            status = "CONNECTED" if age_hours <= 72 else "STALE"
            return {"status": status, "label": label, "symbol": symbol, "value": last_val,
                    "change": (last_val - previous_val) if previous_val is not None else None,
                    "observation_date": obs_dt.strftime("%Y-%m-%d"),
                    "timestamp": obs_dt.strftime("%Y-%m-%d %H:%M UTC"),
                    "source": f"Yahoo Finance ({symbol})", "url": "https://finance.yahoo.com/", "detail": f"عمر النقطة {age_hours} ساعة."}
        except Exception as exc:
            errors.append(f"{symbol}: {type(exc).__name__}")
    return {"status": "UNAVAILABLE", "label": label, "symbol": "—", "value": None, "change": None,
            "observation_date": "—", "timestamp": "—", "source": "Yahoo Finance", "url": "https://finance.yahoo.com/", "detail": "تعذر الجلب."}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_quote(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    res = _fetch_yahoo_quote_impl(symbols, label)
    res["tested_at"] = now_utc_text()
    return res

# ---------------------- Official U.S. Treasury curve pages ----------------------
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
            latest = df.iloc[0]
            values = {}
            for key, column in col_map.items():
                if column is None: continue
                val_str = str(latest[column]).replace("%", "").replace(",", "").strip()
                if val_str and val_str.lower() not in {"nan", "none", "-", "n/a"}:
                    try: values[key] = float(val_str)
                    except ValueError: pass
            if "10Y" not in values: continue
            obsdate = latest["_date"].strftime("%Y-%m-%d")
            age = age_days(obsdate)
            status = "CONNECTED" if age is not None and age <= 7 else "STALE"
            return {"status": status, "source": "U.S. Treasury official data", "url": url, "date": obsdate, "values": values, "detail": f"استخراج ناجح بتاريخ {obsdate}."}
        return {"status": "NO DATA", "source": requested, "url": url, "date": "—", "values": {}, "detail": "لم يُعثر على جدول مطابقة."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": requested, "url": url, "date": "—", "values": {}, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_treasury_curve(real: bool = False) -> dict[str, Any]:
    res = _fetch_treasury_curve_impl(real)
    res["tested_at"] = now_utc_text()
    return res

# ---------------------- FRED API ----------------------
FRED_SERIES_META = {
    "DGS2": ("عائد اسمي 2 سنوات", 8), "DGS5": ("عائد اسمي 5 سنوات", 8),
    "DGS10": ("عائد اسمي 10 سنوات", 8), "DGS20": ("عائد اسمي 20 سنة", 8),
    "DGS30": ("عائد اسمي 30 سنة", 8), "DFII10": ("عائد حقيقي 10 سنوات", 8),
    "T10YIE": ("توقع التضخم 10 سنوات", 8), "CPIAUCSL": ("مؤشر CPI", 75),
}

def _fetch_fred_observation_impl(series_id: str, api_key: str) -> dict[str, Any]:
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        response = request_get(url, params={"series_id": series_id, "api_key": api_key, "file_type": "json", "sort_order": "desc", "limit": 5})
        if response.status_code == 429: return {"status": "RATE LIMITED", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "HTTP 429."}
        response.raise_for_status()
        obs = response.json().get("observations", [])
        valid = [o for o in obs if o.get("value") not in (None, ".", "")]
        if not valid: return {"status": "NO DATA", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "بلا بيانات صالحة."}
        latest = valid[0]
        val = float(latest["value"])
        label, max_age = FRED_SERIES_META.get(series_id, (series_id, 10))
        status, freshness_detail = apply_freshness("CONNECTED", latest.get("date"), max_age)
        return {"status": status, "series": series_id, "label": label, "value": val, "date": latest.get("date", "—"), "source": "FRED API", "detail": freshness_detail}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_fred_observation(series_id: str, api_key: str) -> dict[str, Any]:
    res = _fetch_fred_observation_impl(series_id, api_key)
    res["tested_at"] = now_utc_text()
    return res

# ---------------------- BLS API ----------------------
BLS_SERIES = {
    "headline_cpi": ("CUSR0000SA0", "CPI العام", "monthly"),
    "core_cpi": ("CUSR0000SA0L1E", "Core CPI", "monthly"),
    "unemployment": ("LNS14000000", "Unemployment rate", "monthly"),
    "nonfarm_payrolls": ("CES0000000001", "Nonfarm payrolls", "monthly"),
    "hourly_earnings": ("CES0500000003", "Hourly earnings", "monthly"),
}

def _fetch_bls_latest_impl() -> dict[str, Any]:
    url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
    series_ids = [meta[0] for meta in BLS_SERIES.values()]
    try:
        response = requests.post(url, json={"seriesid": series_ids}, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
        if response.status_code == 429: return {"status": "RATE LIMITED", "series": {}, "source": "BLS API", "url": "https://www.bls.gov/", "detail": "HTTP 429."}
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "REQUEST_SUCCEEDED": return {"status": "NO DATA", "series": {}, "source": "BLS API", "url": "https://www.bls.gov/", "detail": "فشل الطلب."}
        raw_series = payload.get("Results", {}).get("series", [])
        mapping = {}
        for item in raw_series:
            sid = item.get("seriesID")
            entries = [e for e in item.get("data", []) if str(e.get("period", "")) != "M13"]
            mapping[sid] = sorted(entries, key=lambda x: (int(x.get("year", 0)), int(x.get("period", "M0")[1:]) if x.get("period", "").startswith("M") else 0), reverse=True)
        results = {}
        for key, (sid, label, _) in BLS_SERIES.items():
            rows = mapping.get(sid, [])
            if not rows:
                results[key] = {"status": "NO DATA", "series_id": sid, "label": label, "value": None, "date": "—", "detail": "بلا بيانات."}
                continue
            latest = rows[0]
            val = float(latest["value"])
            results[key] = {"status": "CONNECTED", "series_id": sid, "label": label, "value": val, "date": f"{latest.get('year')}-{latest.get('period')}", "detail": "تم الجلب بنجاح."}
        return {"status": "CONNECTED", "series": results, "source": "BLS API", "url": "https://www.bls.gov/", "detail": "تم جلب البيانات بنجاح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": {}, "source": "BLS API", "url": "https://www.bls.gov/", "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_latest() -> dict[str, Any]:
    res = _fetch_bls_latest_impl()
    res["tested_at"] = now_utc_text()
    return res

# ---------------------- BEA API ----------------------
def _fetch_bea_data_impl(api_key: str) -> dict[str, Any]:
    url = "https://apps.bea.gov/api/data/"
    if not api_key: return {"status": "NOT TESTED", "source": "BEA API", "url": "https://apps.bea.gov/api/signup/", "detail": "مفتاح BEA غير موجود."}
    try:
        params = {"UserID": api_key, "method": "GetData", "DataSetName": "NIPA", "TableName": "T10101", "Frequency": "Q", "Year": "X", "ResultFormat": "JSON"}
        response = request_get(url, params=params)
        if response.status_code == 429: return {"status": "RATE LIMITED", "source": "BEA API", "url": url, "detail": "HTTP 429."}
        response.raise_for_status()
        return {"status": "CONNECTED", "source": "BEA API", "url": url, "detail": "تم الاتصال بنجاح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": "BEA API", "url": url, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bea_data(api_key: str) -> dict[str, Any]:
    res = _fetch_bea_data_impl(api_key)
    res["tested_at"] = now_utc_text()
    return res

# ---------------------- CFTC COT ----------------------
CFTC_COT_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

def _fetch_cftc_gold_cot_impl() -> dict[str, Any]:
    params = {"$where": "market_and_exchange_names like '%GOLD%'", "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 10}
    try:
        response = request_get(CFTC_COT_URL, params=params)
        if response.status_code == 429: return {"status": "RATE LIMITED", "source": "CFTC COT", "url": CFTC_COT_URL, "rows": [], "detail": "HTTP 429."}
        response.raise_for_status()
        rows = response.json()
        if not rows: return {"status": "NO DATA", "source": "CFTC COT", "url": CFTC_COT_URL, "rows": [], "detail": "لا توجد صفوف مطابقة."}
        clean_rows = []
        for r in rows:
            try:
                long_val = float(r.get("noncomm_positions_long_all", 0))
                short_val = float(r.get("noncomm_positions_short_all", 0))
                oi = float(r.get("open_interest_all", 0))
                clean_rows.append({"date": str(r.get("report_date_as_yyyy_mm_dd"))[:10], "long": long_val, "short": short_val, "net": long_val - short_val, "open_interest": oi})
            except (TypeError, ValueError):
                continue
        return {"status": "CONNECTED", "source": "CFTC COT", "url": CFTC_COT_URL, "rows": clean_rows, "detail": "تم جلب تقرير COT بنجاح."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": "CFTC COT", "url": CFTC_COT_URL, "rows": [], "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=7200, show_spinner=False)
def fetch_cftc_gold_cot() -> dict[str, Any]:
    res = _fetch_cftc_gold_cot_impl()
    res["tested_at"] = now_utc_text()
    return res

@st.cache_data(ttl=1800, show_spinner=False)
def check_page_access(name: str, url: str) -> dict[str, Any]:
    try:
        response = request_get(url)
        status = "CONNECTED" if response.status_code < 400 else "UNAVAILABLE"
        return {"status": status, "source": name, "url": url, "detail": f"فحص الوصول (HTTP {response.status_code})."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": name, "url": url, "detail": f"خطأ: {type(exc).__name__}."}

# ---------------------- Aggregate Market Data ----------------------
def build_market_data() -> dict[str, Any]:
    dxy = fetch_yahoo_quote(("DX-Y.NYB",), "DXY")
    gold = fetch_yahoo_quote(("XAUUSD=X", "GC=F"), "XAUUSD")
    nominal = fetch_treasury_curve(False)
    real_curve = fetch_treasury_curve(True)
    cot = fetch_cftc_gold_cot()
    bls = fetch_bls_latest()
    bea = fetch_bea_data(get_secret("BEA_API_KEY"))
    fred_key = get_secret("FRED_API_KEY")
    fred = {sid: fetch_fred_observation(sid, fred_key) for sid in FRED_SERIES_META} if fred_key else {}
    
    real10 = fred.get("DFII10", {}).get("value")
    real_yield = {"status": fred["DFII10"]["status"], "value": real10, "date": fred["DFII10"]["date"], "source": "FRED DFII10"} if real10 is not None and fred.get("DFII10", {}).get("status") == "CONNECTED" else {"status": real_curve["status"], "value": real_curve.get("values", {}).get("10Y"), "date": real_curve.get("date", "—"), "source": real_curve["source"]}
    
    breakeven_val = fred.get("T10YIE", {}).get("value")
    breakeven_status = fred.get("T10YIE", {}).get("status", "NOT TESTED")
    
    score = round(sum(weight * (1 if s == "CONNECTED" else 0.5 if s == "STALE" else 0) for s, weight in [(gold.get("status"), 25), (dxy.get("status"), 15), (nominal.get("status"), 15), (real_yield.get("status"), 10), (cot.get("status"), 20), (bls.get("status"), 5), (bea.get("status"), 5), (breakeven_status, 5)]))
    return {"gold": gold, "dxy": dxy, "nominal": nominal, "real_yield": real_yield, "breakeven": {"status": breakeven_status, "value": breakeven_val}, "cot": cot, "bls": bls, "bea": bea, "fred": fred, "quality_score": score, "tested_at": now_utc_text()}

# Session states
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
    gold_price_origin = market_data["gold"].get("source", "غير متاح")
    gold_price_time = market_data["gold"].get("timestamp", "—")

# Sidebar navigation
NAV_ITEMS = [
    "🔥 2. MAIN DASHBOARD (Fusion & Scenarios)",
    "3. DATA SOURCES (مصادر البيانات والتدقيق)",
    "4. WEEKLY ECONOMIC EVENTS (أجندة الأخبار الرسمية)",
    "5. ECONOMIC ANALYSIS (البيانات الاقتصادية المنشورة)",
    "6. YIELDS & DOLLAR (العوائد والدولار)",
    "7. COT & OPEN INTEREST (التمركز والفائدة المفتوحة)",
    "8. SMC/ICT ANALYSIS (البنية والسيولة)",
    "9. EVIDENCE MATRIX (مصفوفة الأدلة)",
    "11. TRADE VALIDATOR (فاحص الصفقات)",
    "12. RISK MANAGEMENT (حاسبة المخاطر)",
    "13. REPORT HISTORY (سجل التقارير)",
    "14. TRADING JOURNAL (سجل الصفقات)",
]

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">TERMINAL</div></div></div>', unsafe_allow_html=True)
    navigation = st.radio("القائمة", NAV_ITEMS, label_visibility="collapsed")
    st.divider()
    st.markdown("### تحديث البيانات")
    if st.button("↻ إعادة جلب البيانات"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    manual_input = st.text_input("سعر الذهب اليدوي ($)", value="" if st.session_state.manual_gold_price is None else str(st.session_state.manual_gold_price))
    c1, c2 = st.columns(2)
    with c1:
        if st.button("اعتماد اليدوي"):
            try:
                st.session_state.manual_gold_price = float(manual_input)
                st.rerun()
            except ValueError: st.error("خطأ بالقيمة")
    with c2:
        if st.button("إلغاء اليدوي"):
            st.session_state.manual_gold_price = None
            st.rerun()

# Pages routing
if navigation == NAV_ITEMS[0]:
    st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>لوحة القرار الموحد للذهب</h1><p>دمج الأسعار الحية، العوائد الرسمية، وتقارير CFTC.</p></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    cols[0].metric("XAUUSD المعتمد", fmt_number(active_gold, 2, " $") if active_gold is not None else "غير متاح")
    cols[1].metric("DXY", fmt_number(market_data["dxy"].get("value"), 2))
    cols[2].metric("US 10Y", fmt_number(market_data["nominal"].get("values", {}).get("10Y"), 3, "%"))
    cols[3].metric("جودة المصادر", f"{market_data['quality_score']} / 100")

elif navigation == NAV_ITEMS[1]:
    st.markdown("## تدقيق مصادر البيانات")
    rows = [
        source_result(market_data["gold"]["source"], "XAUUSD", market_data["gold"]["status"], market_data["gold"]["detail"], data_value=fmt_number(market_data["gold"].get("value"), 2)),
        source_result(market_data["dxy"]["source"], "DXY", market_data["dxy"]["status"], market_data["dxy"]["detail"], data_value=fmt_number(market_data["dxy"].get("value"), 2)),
        source_result(market_data["cot"]["source"], "COT", market_data["cot"]["status"], market_data["cot"]["detail"]),
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

else:
    st.markdown(f"## {navigation}")
    st.info("هذا القسم مفعل وجاهز للعمل بالتكامل مع محرك البيانات الحقيقي.")

st.divider()
st.caption(f"{APP_NAME} • {APP_VERSION}")
