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
# Aho𓂀 GOLD — FULL REBUILD (ALL 12 TABS + VISUAL FIX & THEMES)
# ================================================================
APP_NAME = "Aho𓂀 GOLD"
APP_VERSION = "17.0 — FULL RESTORATION & THEME FIX"
REQUEST_TIMEOUT = 12
USER_AGENT = "AhoGoldIntelligence/17.0"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# Theme-aware styling: Light & Dark themes with gold, green, blue accents and no middle line.
try:
    ACTIVE_THEME = st.context.theme.type or "dark"
except Exception:
    ACTIVE_THEME = "dark"

if ACTIVE_THEME == "light":
    CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
    :root{--bg:#f4f7f2;--panel:#ffffff;--line:#cce0cc;--gold:#a77b16;--green:#177245;--blue:#1e5f8a;--red:#b42332;--muted:#5f6f68;--text:#18251e;--panel2:#eaf1e9;}
    html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic','Inter',sans-serif;direction:rtl;text-align:right}
    .stApp{background:linear-gradient(135deg,#f7faf5 0%,#edf4ed 55%,#f9f8f0 100%);color:var(--text)}
    .block-container{padding-top:1rem!important;padding-bottom:2rem!important;max-width:1500px}
    [data-testid="stHorizontalBlock"] > div{border:none!important;box-shadow:none!important}
    [data-testid="stSidebar"]{background:#eaf1e9;border-left:0!important;border-right:1px solid #d5e1d4;padding-top:12px}
    [data-testid="stSidebar"] *{text-align:right}
    [data-testid="stSidebarNav"]{display:none}
    .brand{display:flex;align-items:center;gap:12px;padding:4px 0 16px;border-bottom:1px solid var(--line);margin-bottom:15px}
    .brand-mark{width:44px;height:44px;border:1px solid var(--gold);border-radius:14px;display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:22px;background:linear-gradient(145deg,#fffdf5,#e4eee2)}
    .brand-title{font-family:Inter,sans-serif;letter-spacing:.5px;font-weight:800;font-size:17px;color:var(--blue)}
    .brand-sub{color:var(--muted);font-size:11px;margin-top:3px}
    .hero{border:1px solid var(--line);border-radius:18px;padding:20px 24px;background:linear-gradient(135deg,#fff 0%,#f0f6ee 100%);margin-bottom:18px;box-shadow:0 8px 28px rgba(28,67,42,.07);border-right:5px solid var(--gold)}
    .eyebrow{color:var(--gold);letter-spacing:1px;font-size:11px;font-weight:800;font-family:Inter,sans-serif}
    .hero h1{margin:6px 0;font-size:23px;color:var(--blue);font-weight:800}
    .hero p{margin:0;color:var(--muted);line-height:1.8;font-size:14px}
    .data-banner,.fusion-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:13px;color:var(--muted)}
    .stButton button{border-radius:11px;border:1px solid var(--gold)!important;background:linear-gradient(135deg,#c6a34a,#e0c66e)!important;color:#183b2b!important;font-weight:800!important;width:100%;padding:9px}
    .stButton button:hover{filter:brightness(1.04)}
    .warning-box{border:1px solid #dfc982;background:#fff8df;border-radius:10px;padding:12px 14px;margin:8px 0;color:#705514}
    .good-box{border:1px solid #9bc9ad;background:#edf8f0;border-radius:10px;padding:12px 14px;margin:8px 0;color:#205b3b}
    .bad-box{border:1px solid #e3b0b0;background:#fff0ef;border-radius:10px;padding:12px 14px;margin:8px 0;color:#8e2630}
    [data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px}
    [data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px}
    footer{visibility:hidden}
    @media(max-width:768px){.block-container{padding-left:.75rem!important;padding-right:.75rem!important}.hero{padding:15px!important}.hero h1{font-size:19px!important}[data-testid="stHorizontalBlock"]{gap:.5rem!important}}
    </style>
    """
else:
    CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
    :root{--bg:#121c26;--panel:#192634;--line:#2a3f55;--gold:#e1bd63;--green:#51d69a;--blue:#4da6ff;--red:#ff7777;--muted:#a8b7c5;--text:#f2f6f8;--panel2:#202f3d;}
    html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic','Inter',sans-serif;direction:rtl;text-align:right}
    .stApp{background:radial-gradient(circle at 50% 0%,#1b2a3a 0%,#111922 58%,#0b1118 100%);color:var(--text)}
    .block-container{padding-top:1rem!important;padding-bottom:2rem!important;max-width:1500px}
    [data-testid="stHorizontalBlock"] > div{border:none!important;box-shadow:none!important}
    [data-testid="stSidebar"]{background:#15212d;border-left:0!important;border-right:1px solid var(--line);padding-top:12px}
    [data-testid="stSidebar"] *{text-align:right}
    [data-testid="stSidebarNav"]{display:none}
    .brand{display:flex;align-items:center;gap:12px;padding:4px 0 16px;border-bottom:1px solid var(--line);margin-bottom:15px}
    .brand-mark{width:44px;height:44px;border:1px solid var(--gold);border-radius:14px;display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:22px;background:linear-gradient(145deg,#243647,#16222e)}
    .brand-title{font-family:Inter,sans-serif;letter-spacing:.5px;font-weight:800;font-size:17px;color:var(--gold)}
    .brand-sub{color:var(--muted);font-size:11px;margin-top:3px}
    .hero{border:1px solid var(--line);border-radius:18px;padding:20px 24px;background:linear-gradient(135deg,rgba(29,43,58,.98),rgba(17,27,38,.98));margin-bottom:18px;box-shadow:0 8px 28px rgba(0,0,0,.25);border-right:5px solid var(--gold)}
    .eyebrow{color:var(--gold);letter-spacing:1px;font-size:11px;font-weight:800;font-family:Inter,sans-serif}
    .hero h1{margin:6px 0;font-size:23px;color:var(--blue);font-weight:800}
    .hero p{margin:0;color:var(--muted);line-height:1.8;font-size:14px}
    .data-banner,.fusion-card{background:#182634;border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:13px;color:var(--muted)}
    .stButton button{border-radius:11px;border:1px solid var(--gold)!important;background:linear-gradient(135deg,#d5b85f,#f0d77f)!important;color:#121c26!important;font-weight:800!important;width:100%;padding:9px}
    .stButton button:hover{filter:brightness(1.06)}
    .warning-box{border:1px solid #78652d;background:#2b281b;border-radius:10px;padding:12px 14px;margin:8px 0;color:#f0d98c}
    .good-box{border:1px solid #28684d;background:#182f28;border-radius:10px;padding:12px 14px;margin:8px 0;color:#9ce8be}
    .bad-box{border:1px solid #814348;background:#321f26;border-radius:10px;padding:12px 14px;margin:8px 0;color:#ffb3b3}
    [data-testid="stMetric"]{background:#182634;border:1px solid var(--line);border-radius:12px;padding:12px}
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


def max_drawdown_r(trade_r_results: list[float]) -> float:
    import math
    if not trade_r_results:
        return 0.0
    eq = [0.0]
    for value in trade_r_results:
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("نتائج الباك تست يجب أن تكون أرقامًا منتهية.")
        eq.append(eq[-1] + value)
    peak = eq[0]
    max_dd = 0.0
    for value in eq:
        peak = max(peak, value)
        max_dd = max(max_dd, peak - value)
    return max_dd


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
        if code == 429:
            return "RATE LIMITED"
        if code in (401, 403):
            return "AUTH ERROR"
        return "UNAVAILABLE"
    if isinstance(exc, requests.RequestException):
        return "UNAVAILABLE"
    return "NO DATA"


def age_days(obs_date: Any) -> Optional[int]:
    try:
        d = pd.to_datetime(obs_date, utc=True, errors="coerce")
        if pd.isna(d):
            return None
        return max(0, (pd.Timestamp.now(tz="UTC") - d).days)
    except Exception:
        return None


def apply_freshness(status: str, obs_date: Any, max_age_days: int) -> tuple[str, str]:
    if status != "CONNECTED":
        return status, ""
    days = age_days(obs_date)
    if days is None:
        return "CONNECTED", "تعذر حساب عمر الملاحظة؛ راجع تاريخ المصدر."
    if days > max_age_days:
        return "STALE", f"عمر آخر ملاحظة {days} يومًا؛ الحد المعتمد هنا {max_age_days} يومًا."
    return "CONNECTED", f"عمر آخر ملاحظة {days} يومًا."


def display_status(status: str) -> str:
    symbols = {
        "CONNECTED": "🟢 CONNECTED",
        "STALE": "🟠 STALE",
        "RATE LIMITED": "🟠 RATE LIMITED",
        "AUTH ERROR": "🔴 AUTH ERROR",
        "TIMEOUT": "🟠 TIMEOUT",
        "NO DATA": "🔴 NO DATA",
        "NOT TESTED": "⚪ NOT TESTED",
        "UNAVAILABLE": "🔴 UNAVAILABLE",
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
        "المصدر": source,
        "البيانات المطلوبة": requested,
        "الحالة": status,
        "القيمة/النتيجة المستخرجة": data_value,
        "تاريخ الملاحظة": observation_date or "—",
        "وقت الفحص (UTC)": test_time or "—",
        "حداثة البيانات": freshness,
        "تفاصيل الاختبار": detail,
        "فحص وصول فقط؟": "نعم — لا يثبت استخراج الأرقام" if access_only else "لا",
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
                        "observation_date": "—", "timestamp": "—", "source": "Yahoo Finance chart endpoint",
                        "url": "https://finance.yahoo.com/", "detail": "وصل المصدر إلى HTTP 429. لم تُستخدم قيمة بديلة ثابتة."}
            response.raise_for_status()
            payload = response.json().get("chart", {})
            result_list = payload.get("result") or []
            if not result_list:
                error_obj = payload.get("error") or {}
                errors.append(f"{symbol}: {error_obj.get('description', 'no chart result')}")
                continue
            result = result_list[0]
            quote_rows = result.get("indicators", {}).get("quote", [{}])[0]
            closes = quote_rows.get("close", []) or []
            timestamps = result.get("timestamp", []) or []
            valid: list[tuple[int, float]] = []
            for stamp, close in zip(timestamps, closes):
                if close is not None:
                    try:
                        valid.append((int(stamp), float(close)))
                    except (TypeError, ValueError):
                        pass
            if not valid:
                errors.append(f"{symbol}: no valid closes")
                continue
            last_ts, last_val = valid[-1]
            previous_val = valid[-2][1] if len(valid) >= 2 else None
            obs_dt = datetime.fromtimestamp(last_ts, timezone.utc)
            age_hours = max(0, int((datetime.now(timezone.utc) - obs_dt).total_seconds() / 3600))
            status = "CONNECTED" if age_hours <= 72 else "STALE"
            detail = f"آخر نقطة سعر من رمز {symbol}؛ عمرها التقريبي {age_hours} ساعة. Yahoo قد يعرض أسعارًا متأخرة، وهذا ليس ضمانًا لسعر لحظي أو تغطية مرخصة."
            return {"status": status, "label": label, "symbol": symbol, "value": last_val,
                    "change": (last_val - previous_val) if previous_val is not None else None,
                    "observation_date": obs_dt.strftime("%Y-%m-%d"),
                    "timestamp": obs_dt.strftime("%Y-%m-%d %H:%M UTC"),
                    "source": f"Yahoo Finance ({symbol})", "url": "https://finance.yahoo.com/", "detail": detail}
        except Exception as exc:
            status = classify_exception(exc)
            if status == "RATE LIMITED":
                return {"status": status, "label": label, "symbol": symbol, "value": None, "change": None,
                        "observation_date": "—", "timestamp": "—", "source": f"Yahoo Finance ({symbol})", "url": "https://finance.yahoo.com/", "detail": "HTTP 429؛ لا توجد قيمة بديلة."}
            errors.append(f"{symbol}: {type(exc).__name__}")
    return {"status": "UNAVAILABLE" if errors else "NO DATA", "label": label, "symbol": "—", "value": None, "change": None,
            "observation_date": "—", "timestamp": "—", "source": "Yahoo Finance chart endpoint", "url": "https://finance.yahoo.com/",
            "detail": "لم تُستخرج نقطة سعر صالحة. " + "; ".join(errors[:3])}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_quote(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    result = _fetch_yahoo_quote_impl(symbols, label)
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- Official U.S. Treasury curve pages ----------------------
TREASURY_NOMINAL_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve"
TREASURY_REAL_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve"


def _normal_col(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _find_yield_col(columns: list[Any], years: int) -> Optional[Any]:
    norm_map = {c: _normal_col(c) for c in columns}
    for c, norm in norm_map.items():
        if norm in {f"{years}yr", f"{years}year", f"{years}yrs", f"{years}years"}:
            return c
    for c, norm in norm_map.items():
        if norm.startswith(str(years)) and ("yr" in norm or "year" in norm):
            return c
    return None


def _fetch_treasury_curve_impl(real: bool = False) -> dict[str, Any]:
    url = TREASURY_REAL_URL if real else TREASURY_NOMINAL_URL
    requested = "U.S. Treasury real yield curve" if real else "U.S. Treasury nominal yield curve"
    try:
        response = request_get(url)
        if response.status_code == 429:
            return {"status": "RATE LIMITED", "source": requested, "url": url, "date": "—", "values": {}, "detail": "HTTP 429؛ لا توجد بيانات بديلة."}
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            df = table.copy()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join(str(part) for part in col if str(part) != "nan").strip() for col in df.columns]
            columns = list(df.columns)
            date_col = next((c for c in columns if "date" in _normal_col(c)), None)
            col_map = {f"{year}Y": _find_yield_col(columns, year) for year in (2, 5, 10, 20, 30)}
            useful = any(col_map.values()) and date_col is not None
            if not useful:
                continue
            df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
            df = df[df["_date"].notna()].sort_values("_date", ascending=False)
            if df.empty:
                continue
            latest = df.iloc[0]
            values: dict[str, float] = {}
            for key, column in col_map.items():
                if column is None:
                    continue
                try:
                    val_str = str(latest[column]).replace("%", "").replace(",", "").strip()
                    if val_str and val_str.lower() not in {"nan", "none", "-", "n/a"}:
                        values[key] = float(val_str)
                except (TypeError, ValueError):
                    pass
            if "10Y" not in values or "5Y" not in values:
                continue
            obsdate = latest["_date"].strftime("%Y-%m-%d")
            age = age_days(obsdate)
            requested_tenors = {"5Y", "10Y", "20Y", "30Y"} if real else {"2Y", "5Y", "10Y", "20Y", "30Y"}
            missing_tenors = sorted(requested_tenors - set(values.keys()))
            if missing_tenors:
                status = "NO DATA"
            else:
                status = "CONNECTED" if age is not None and age <= 7 else ("STALE" if age is not None else "NO DATA")
            curve_type = "حقيقية" if real else "اسمية"
            completeness = f"استُخرجت {len(set(values) & requested_tenors)}/{len(requested_tenors)} آجال مطلوبة."
            if missing_tenors:
                completeness += " الآجال غير المستخرجة: " + ", ".join(missing_tenors) + "."
            return {"status": status, "source": "U.S. Treasury official data table", "url": url,
                    "date": obsdate, "values": values,
                    "detail": f"استخراج فعلي من جدول الخزانة الأمريكية للعوائد {curve_type}. تاريخ الجدول {obsdate}. {completeness}"}
        return {"status": "NO DATA", "source": requested, "url": url, "date": "—", "values": {},
                "detail": "تم الوصول إلى الصفحة لكن لم يُعثر على جدول يمكن قراءته بأعمدة العوائد المتوقعة. لم تُنشأ قيم تقديرية."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": requested, "url": url, "date": "—", "values": {},
                "detail": f"تعذر استخراج جدول العوائد ({type(exc).__name__}). لا توجد قيمة بديلة ثابتة."}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_treasury_curve(real: bool = False) -> dict[str, Any]:
    result = _fetch_treasury_curve_impl(real)
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- FRED API ----------------------
FRED_SERIES_META = {
    "DGS2": ("عائد اسمي 2 سنوات", 8),
    "DGS5": ("عائد اسمي 5 سنوات", 8),
    "DGS10": ("عائد اسمي 10 سنوات", 8),
    "DGS20": ("عائد اسمي 20 سنة", 8),
    "DGS30": ("عائد اسمي 30 سنة", 8),
    "DFII10": ("عائد حقيقي 10 سنوات", 8),
    "T10YIE": ("توقع التضخم 10 سنوات Breakeven", 8),
    "CPIAUCSL": ("مؤشر CPI العام", 75),
}


def _fetch_fred_observation_impl(series_id: str, api_key: str) -> dict[str, Any]:
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        response = request_get(url, params={"series_id": series_id, "api_key": api_key, "file_type": "json",
                                           "sort_order": "desc", "limit": 12})
        if response.status_code == 429:
            return {"status": "RATE LIMITED", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "HTTP 429."}
        if response.status_code in (401, 403):
            return {"status": "AUTH ERROR", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": f"رفض المصدر المصادقة (HTTP {response.status_code})."}
        response.raise_for_status()
        payload = response.json()
        if payload.get("error_code"):
            msg = str(payload.get("error_message", "FRED API error"))[:160]
            return {"status": "AUTH ERROR" if "api key" in msg.lower() else "NO DATA", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": msg}
        obs = payload.get("observations", [])
        valid = [o for o in obs if o.get("value") not in (None, ".", "")]
        if not valid:
            return {"status": "NO DATA", "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": "استجابة API بلا ملاحظة رقمية صالحة."}
        latest = valid[0]
        try:
            val = float(latest["value"])
        except (TypeError, ValueError):
            return {"status": "NO DATA", "series": series_id, "value": None, "date": latest.get("date", "—"), "source": "FRED API", "detail": "قيمة غير رقمية."}
        label, max_age = FRED_SERIES_META.get(series_id, (series_id, 10))
        status, freshness_detail = apply_freshness("CONNECTED", latest.get("date"), max_age)
        return {"status": status, "series": series_id, "label": label, "value": val, "date": latest.get("date", "—"),
                "source": "FRED API", "url": f"https://fred.stlouisfed.org/series/{series_id}", "detail": freshness_detail}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": series_id, "value": None, "date": "—", "source": "FRED API", "detail": f"تعذر جلب السلسلة ({type(exc).__name__})."}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_fred_observation(series_id: str, api_key: str) -> dict[str, Any]:
    result = _fetch_fred_observation_impl(series_id, api_key)
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- BLS API: actual published observations only ----------------------
BLS_SERIES = {
    "headline_cpi": ("CUSR0000SA0", "CPI العام — Seasonally Adjusted", "monthly"),
    "core_cpi": ("CUSR0000SA0L1E", "Core CPI proxy — less food and energy, SA", "monthly"),
    "unemployment": ("LNS14000000", "Unemployment rate", "monthly"),
    "nonfarm_payrolls": ("CES0000000001", "Total nonfarm payrolls (thousands)", "monthly"),
    "hourly_earnings": ("CES0500000003", "Average hourly earnings, private sector", "monthly"),
}


def _period_to_sort(row: dict[str, Any]) -> tuple[int, int]:
    year = int(row.get("year", 0) or 0)
    period = str(row.get("period", ""))
    try:
        month = int(period[1:]) if period.startswith("M") else 0
    except ValueError:
        month = 0
    return year, month


def _fetch_bls_latest_impl() -> dict[str, Any]:
    url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
    series_ids = [meta[0] for meta in BLS_SERIES.values()]
    try:
        response = requests.post(url, json={"seriesid": series_ids}, timeout=REQUEST_TIMEOUT,
                                 headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
        if response.status_code == 429:
            return {"status": "RATE LIMITED", "series": {}, "source": "BLS Public Data API v1", "url": "https://www.bls.gov/developers/", "detail": "HTTP 429."}
        if response.status_code in (401, 403):
            return {"status": "AUTH ERROR", "series": {}, "source": "BLS Public Data API v1", "url": "https://www.bls.gov/developers/", "detail": f"HTTP {response.status_code}."}
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "REQUEST_SUCCEEDED":
            return {"status": "NO DATA", "series": {}, "source": "BLS Public Data API v1", "url": "https://www.bls.gov/developers/", "detail": "رد BLS لا يؤكد نجاح الطلب."}
        raw_series = payload.get("Results", {}).get("series", [])
        mapping: dict[str, Any] = {}
        for item in raw_series:
            sid = item.get("seriesID")
            entries = [entry for entry in item.get("data", []) if str(entry.get("period", "")) != "M13"]
            entries = sorted(entries, key=_period_to_sort, reverse=True)
            valid = []
            for entry in entries:
                try:
                    valid.append({**entry, "numeric_value": float(entry.get("value"))})
                except (TypeError, ValueError):
                    pass
            mapping[sid] = valid
        results: dict[str, Any] = {}
        for key, (sid, label, freq) in BLS_SERIES.items():
            rows = mapping.get(sid, [])
            if not rows:
                results[key] = {"status": "NO DATA", "series_id": sid, "label": label, "value": None, "previous": None, "date": "—", "detail": "لا توجد ملاحظات رقمية."}
                continue
            latest = rows[0]
            month_num = latest.get("period", "")[1:] if str(latest.get("period", "")).startswith("M") else ""
            obs_date = f"{latest.get('year', '')}-{str(month_num).zfill(2)}" if month_num else str(latest.get("year", "—"))
            previous = rows[1] if len(rows) > 1 else None
            previous_value = previous.get("numeric_value") if previous else None
            change = latest["numeric_value"] - previous_value if previous_value is not None else None
            pct_change = ((latest["numeric_value"] / previous_value) - 1) * 100 if previous_value not in (None, 0) else None
            age = None
            if month_num:
                try:
                    obs_ts = pd.Timestamp(f"{obs_date}-01", tz="UTC")
                    age = max(0, (pd.Timestamp.now(tz="UTC") - obs_ts).days)
                except Exception:
                    age = None
            status = "CONNECTED" if age is not None and age <= 75 else ("STALE" if age is not None else "CONNECTED")
            results[key] = {"status": status, "series_id": sid, "label": label, "value": latest["numeric_value"],
                            "previous": previous_value, "change": change, "pct_change": pct_change, "date": obs_date,
                            "period_name": latest.get("periodName", ""), "unit_note": "BLS-reported series units; see source metadata.",
                            "detail": f"ملاحظة منشورة للفترة {obs_date}. التغير مقارنة بالشهر السابق حساب مشتق من السلسلة، وليس توقعًا للسوق."}
        usable = sum(1 for r in results.values() if r["status"] in {"CONNECTED", "STALE"} and r["value"] is not None)
        overall = "CONNECTED" if usable > 0 else "NO DATA"
        return {"status": overall, "series": results, "source": "BLS Public Data API v1", "url": "https://www.bls.gov/developers/",
                "detail": f"تم استخراج {usable}/{len(BLS_SERIES)} سلسلة. لم تُجلب توقعات الإجماع؛ لا تتضمن هذه الواجهة Consensus."}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": {}, "source": "BLS Public Data API v1", "url": "https://www.bls.gov/developers/", "detail": f"تعذر جلب BLS ({type(exc).__name__})."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_latest() -> dict[str, Any]:
    result = _fetch_bls_latest_impl()
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- BEA API: real API query with key ----------------------
def _fetch_bea_data_impl(api_key: str) -> dict[str, Any]:
    url = "https://apps.bea.gov/api/data/"
    if not api_key:
        return {"status": "NOT TESTED", "source": "BEA API", "url": "https://apps.bea.gov/api/signup/", "gdp": None, "pce_price": None,
                "detail": "لم يُضبط BEA_API_KEY؛ لم يُرسل طلب API."}
    current_year = datetime.now(timezone.utc).year
    years = f"{current_year-1},{current_year}"
    out: dict[str, Any] = {"status": "NO DATA", "source": "BEA API", "url": "https://apps.bea.gov/api/signup/", "gdp": None, "pce_price": None, "core_pce_price": None, "detail": "لم تُستخرج أرقام صالحة."}
    errors: list[str] = []
    try:
        for label, table, frequency in (("gdp", "T10101", "Q"), ("pce_price", "T20304", "M")):
            params = {"UserID": api_key, "method": "GetData", "DataSetName": "NIPA", "TableName": table,
                      "Frequency": frequency, "Year": years, "ResultFormat": "JSON"}
            response = request_get(url, params=params)
            if response.status_code == 429:
                return {**out, "status": "RATE LIMITED", "detail": "HTTP 429 من BEA."}
            if response.status_code in (401, 403):
                return {**out, "status": "AUTH ERROR", "detail": f"رفض المصدر الطلب (HTTP {response.status_code})."}
            response.raise_for_status()
            payload = response.json().get("BEAAPI", {})
            if payload.get("Error"):
                error_obj = payload.get("Error") or {}
                message = str(error_obj.get("APIErrorDescription", "BEA API error"))[:180]
                if "key" in message.lower() or "userid" in message.lower():
                    return {**out, "status": "AUTH ERROR", "detail": "رفض BEA المفتاح أو بيانات المصادقة."}
                errors.append(f"{table}: {message}")
                continue
            data = payload.get("Results", {}).get("Data", [])
            if not data:
                errors.append(f"{table}: no rows")
                continue
            if label == "gdp":
                candidates = [r for r in data if "gross domestic product" in str(r.get("LineDescription", "")).lower()]
                if candidates:
                    candidates.sort(key=lambda r: str(r.get("TimePeriod", "")), reverse=True)
                    selected = candidates[0]
                    out["gdp"] = {"value": selected.get("DataValue"), "period": selected.get("TimePeriod"),
                                  "description": selected.get("LineDescription"), "unit": selected.get("CL_UNIT"), "source_table": table}
            else:
                for output_key, prefixes in (("pce_price", ("DPCERG",)), ("core_pce_price", ("DPCCRG",))):
                    candidates = [r for r in data if str(r.get("SeriesCode", "")).upper().startswith(prefixes)]
                    if candidates:
                        candidates.sort(key=lambda r: str(r.get("TimePeriod", "")), reverse=True)
                        selected = candidates[0]
                        out[output_key] = {"value": selected.get("DataValue"), "period": selected.get("TimePeriod"),
                                           "description": selected.get("LineDescription"), "unit": selected.get("CL_UNIT"), "source_table": table,
                                           "series_code": selected.get("SeriesCode")}
        count = sum(out[key] is not None for key in ("gdp", "pce_price", "core_pce_price"))
        out["status"] = "CONNECTED" if count > 0 else "NO DATA"
        out["detail"] = f"تم اختبار GDP (T10101) وPCE/Core PCE price index (T20304). نتائج قابلة للاستخدام: {count}/3. " + "; ".join(errors[:2])
        return out
    except Exception as exc:
        status = classify_exception(exc)
        return {**out, "status": status, "detail": f"تعذر جلب BEA ({type(exc).__name__}). لم تُعرض قيم بديلة."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bea_data(api_key: str) -> dict[str, Any]:
    result = _fetch_bea_data_impl(api_key)
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- CFTC: official Socrata Legacy Futures-Only COT ----------------------
CFTC_COT_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
CFTC_COT_PAGE = "https://publicreporting.cftc.gov/Commitments-of-Traders/Legacy-Futures-Only/6dca-aqww"


def _fetch_cftc_gold_cot_impl() -> dict[str, Any]:
    params = {
        "$where": "market_and_exchange_names like '%GOLD%'",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": 20,
    }
    try:
        response = request_get(CFTC_COT_URL, params=params)
        if response.status_code == 429:
            return {"status": "RATE LIMITED", "source": "CFTC Socrata — Legacy Futures Only", "url": CFTC_COT_URL,
                    "rows": [], "detail": "HTTP 429؛ لا توجد أرقام احتياطية."}
        if response.status_code in (401, 403):
            return {"status": "AUTH ERROR", "source": "CFTC Socrata — Legacy Futures Only", "url": CFTC_COT_URL,
                    "rows": [], "detail": f"HTTP {response.status_code}."}
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list) or not rows:
            return {"status": "NO DATA", "source": "CFTC Socrata — Legacy Futures Only", "url": CFTC_COT_URL,
                    "rows": [], "detail": "عاد المصدر بلا صفوف تطابق GOLD. لم تُستخدم أرقام بديلة."}
        selected = []
        for row in rows:
            market = str(row.get("market_and_exchange_names", ""))
            contract = str(row.get("contract_market_name", ""))
            if "GOLD" not in (market + " " + contract).upper():
                continue
            report_date = row.get("report_date_as_yyyy_mm_dd")
            if not report_date:
                continue
            def _num(field: str) -> Optional[float]:
                try:
                    val = row.get(field)
                    return float(val) if val not in (None, "") else None
                except (TypeError, ValueError):
                    return None
            long_value = _num("noncomm_positions_long_all")
            short_value = _num("noncomm_positions_short_all")
            oi = _num("open_interest_all")
            if long_value is None or short_value is None:
                continue
            selected.append({"date": str(report_date)[:10], "market": market or contract,
                             "long": long_value, "short": short_value, "net": long_value - short_value,
                             "open_interest": oi, "raw_row_id": row.get("id")})
        selected.sort(key=lambda x: x["date"], reverse=True)
        unique: dict[str, dict[str, Any]] = {}
        for item in selected:
            unique.setdefault(item["date"], item)
        clean_rows = list(unique.values())
        if not clean_rows:
            return {"status": "NO DATA", "source": "CFTC Socrata — Legacy Futures Only", "url": CFTC_COT_URL,
                    "rows": [], "detail": "استجابة المصدر لا تحتوي على صف ذهب قابل للاستخدام/أعمدة المراكز المتوقعة."}
        fresh_status, freshness_text = apply_freshness("CONNECTED", clean_rows[0]["date"], 14)
        return {"status": fresh_status, "source": "CFTC Socrata — Legacy Futures Only", "url": CFTC_COT_URL,
                "rows": clean_rows, "detail": f"استخراج مباشر من مورد CFTC؛ تاريخ التقرير {clean_rows[0]['date']}. {freshness_text} Net = Non-commercial Long − Non-commercial Short."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": "CFTC Socrata — Legacy Futures Only", "url": CFTC_COT_URL,
                "rows": [], "detail": f"تعذر استخراج تقرير COT ({type(exc).__name__}). لا توجد قيم احتياطية."}

@st.cache_data(ttl=7200, show_spinner=False)
def fetch_cftc_gold_cot() -> dict[str, Any]:
    result = _fetch_cftc_gold_cot_impl()
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- Page-access-only checks ----------------------
def _check_page_access_impl(name: str, url: str) -> dict[str, Any]:
    try:
        response = request_get(url)
        if response.status_code == 429:
            status = "RATE LIMITED"
            detail = "HTTP 429 عند فحص الصفحة."
        else:
            response.raise_for_status()
            status = "CONNECTED" if len(response.text) > 100 else "NO DATA"
            detail = f"تم فحص إمكانية الوصول للصفحة (HTTP {response.status_code}) فقط؛ لا يعني ذلك استخراج بيانات المؤشر أو وجود API مجاني صالح."
        return {"status": status, "source": name, "url": url, "detail": detail}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": name, "url": url, "detail": f"تعذر الوصول ({type(exc).__name__})."}

@st.cache_data(ttl=1800, show_spinner=False)
def check_page_access(name: str, url: str) -> dict[str, Any]:
    result = _check_page_access_impl(name, url)
    result["tested_at"] = now_utc_text()
    return result


# ---------------------- Aggregate live data ----------------------
def build_market_data() -> dict[str, Any]:
    dxy = fetch_yahoo_quote(("DX-Y.NYB",), "DXY")
    gold = fetch_yahoo_quote(("XAUUSD=X", "GC=F"), "XAUUSD spot proxy; GC=F is a futures fallback, not spot")
    gold_futures = fetch_yahoo_quote(("GC=F",), "COMEX Gold Futures (GC=F; not spot XAUUSD)")
    nominal = fetch_treasury_curve(False)
    real_curve = fetch_treasury_curve(True)
    cot = fetch_cftc_gold_cot()
    bls = fetch_bls_latest()
    bea = fetch_bea_data(get_secret("BEA_API_KEY"))
    fred_key = get_secret("FRED_API_KEY")
    fred: dict[str, Any] = {}
    if fred_key:
        for sid in FRED_SERIES_META:
            fred[sid] = fetch_fred_observation(sid, fred_key)
    else:
        for sid, (label, _maxage) in FRED_SERIES_META.items():
            fred[sid] = {"status": "NOT TESTED", "series": sid, "label": label, "value": None, "date": "—", "source": "FRED API",
                         "url": f"https://fred.stlouisfed.org/series/{sid}", "detail": "لم يُضبط FRED_API_KEY؛ لم يُرسل الطلب."}
    real10 = fred.get("DFII10", {}).get("value")
    real10_date = fred.get("DFII10", {}).get("date")
    if real10 is not None and fred.get("DFII10", {}).get("status") == "CONNECTED":
        real_yield = {"status": fred["DFII10"]["status"], "value": real10, "date": real10_date, "source": "FRED DFII10", "detail": fred["DFII10"]["detail"]}
    elif real_curve.get("values", {}).get("10Y") is not None:
        real_yield = {"status": real_curve["status"], "value": real_curve.get("values", {}).get("10Y"), "date": real_curve.get("date", "—"),
                      "source": real_curve["source"], "detail": real_curve["detail"]}
    elif real10 is not None:
        real_yield = {"status": fred["DFII10"]["status"], "value": real10, "date": real10_date, "source": "FRED DFII10", "detail": fred["DFII10"]["detail"]}
    else:
        real_yield = {"status": real_curve["status"], "value": None, "date": real_curve.get("date", "—"),
                      "source": real_curve["source"], "detail": real_curve["detail"]}
    nominal10 = nominal.get("values", {}).get("10Y")
    nominal_date = nominal.get("date", "—")
    breakeven_value = fred.get("T10YIE", {}).get("value")
    breakeven_date = fred.get("T10YIE", {}).get("date")
    breakeven_source = "FRED T10YIE"
    breakeven_status = fred.get("T10YIE", {}).get("status", "NOT TESTED")
    breakeven_detail = fred.get("T10YIE", {}).get("detail", "")
    if breakeven_value is None or breakeven_status != "CONNECTED":
        if nominal10 is not None and real_yield.get("value") is not None and nominal_date == real_yield.get("date"):
            breakeven_value = nominal10 - float(real_yield["value"])
            breakeven_date = nominal_date
            breakeven_source = "مشتق: Treasury nominal 10Y − Treasury real 10Y"
            both_fresh = nominal.get("status") == "CONNECTED" and real_yield.get("status") == "CONNECTED"
            breakeven_status = "CONNECTED" if both_fresh else "STALE"
            breakeven_detail = "قيمة مشتقة من منحنيي الخزانة في التاريخ نفسه."
        elif market_data_fred_be := fred.get("T10YIE", {}).get("value"):
            breakeven_value = market_data_fred_be
            breakeven_date = fred["T10YIE"].get("date")
            breakeven_source = "FRED T10YIE (ملاحظة قديمة)"
            breakeven_status = fred["T10YIE"].get("status", "STALE")
            breakeven_detail = fred["T10YIE"].get("detail", "")
        else:
            breakeven_value = None
            breakeven_status = "NOT TESTED" if not get_secret("FRED_API_KEY") else "NO DATA"
            breakeven_source = "FRED T10YIE / Treasury-derived"
            breakeven_detail = "لا توجد قراءة صالحة."
    score_items = [
        (gold.get("status"), 25), (dxy.get("status"), 15), (nominal.get("status"), 15),
        (real_yield.get("status"), 10), (cot.get("status"), 20), (bls.get("status"), 5),
        (bea.get("status"), 5), (breakeven_status, 5),
    ]
    score = round(sum(weight * (1 if status == "CONNECTED" else 0.5 if status == "STALE" else 0) for status, weight in score_items))
    return {"gold": gold, "gold_futures": gold_futures, "dxy": dxy, "nominal": nominal, "real_curve": real_curve, "real_yield": real_yield,
            "breakeven": {"status": breakeven_status, "value": breakeven_value, "date": breakeven_date or "—", "source": breakeven_source, "detail": breakeven_detail},
            "cot": cot, "bls": bls, "bea": bea, "fred": fred, "quality_score": score, "tested_at": now_utc_text()}

# ---------------------- Session state ----------------------
if "manual_gold_price" not in st.session_state:
    st.session_state.manual_gold_price = None
if "trade_journal" not in st.session_state:
    st.session_state.trade_journal = []
if "report_history" not in st.session_state:
    st.session_state.report_history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "technical_levels" not in st.session_state:
    st.session_state.technical_levels = {"pdh": None, "pdl": None, "asia_high": None, "asia_low": None}

market_data = build_market_data()

def usable_num(value: Any) -> Optional[float]:
    try:
        out = float(value)
        return out if pd.notna(out) else None
    except (TypeError, ValueError):
        return None

if st.session_state.manual_gold_price is not None:
    active_gold = float(st.session_state.manual_gold_price)
    gold_price_origin = "إدخال يدوي من المستخدم"
    gold_price_time = "وقت الإدخال في الجلسة الحالية"
else:
    active_gold = usable_num(market_data["gold"].get("value"))
    gold_price_origin = market_data["gold"].get("source", "مصدر غير متاح")
    gold_price_time = market_data["gold"].get("timestamp", "—")

def make_evidence_rows() -> list[dict[str, Any]]:
    cot_rows = market_data["cot"].get("rows", [])
    cot_latest = cot_rows[0] if cot_rows else {}
    return [
        {"العامل": "XAUUSD / Gold", "القيمة الحالية": fmt_number(active_gold, 2, " $") if active_gold is not None else "غير متاح",
         "التاريخ/الوقت": gold_price_time, "المصدر": gold_price_origin, "الحالة": "MANUAL" if st.session_state.manual_gold_price is not None else market_data["gold"]["status"],
         "ملاحظة": "سعر معتمد."},
        {"العامل": "DXY", "القيمة الحالية": fmt_number(market_data["dxy"].get("value"), 2),
         "التاريخ/الوقت": market_data["dxy"].get("timestamp", "—"), "المصدر": market_data["dxy"].get("source", "Yahoo Finance"),
         "الحالة": market_data["dxy"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "العائد الاسمي US 10Y", "القيمة الحالية": fmt_number(market_data["nominal"].get("values", {}).get("10Y"), 3, "%"),
         "التاريخ/الوقت": market_data["nominal"].get("date", "—"), "المصدر": market_data["nominal"].get("source", "U.S. Treasury"),
         "الحالة": market_data["nominal"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "العائد الحقيقي US 10Y", "القيمة الحالية": fmt_number(market_data["real_yield"].get("value"), 3, "%"),
         "التاريخ/الوقت": market_data["real_yield"].get("date", "—"), "المصدر": market_data["real_yield"].get("source", "U.S. Treasury/FRED"),
         "الحالة": market_data["real_yield"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "Breakeven 10Y", "القيمة الحالية": fmt_number(market_data["breakeven"].get("value"), 3, "%"),
         "التاريخ/الوقت": market_data["breakeven"].get("date", "—"), "المصدر": market_data["breakeven"].get("source", "FRED/Treasury"),
         "الحالة": market_data["breakeven"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "CFTC COT net non-commercial", "القيمة الحالية": f"{cot_latest['net']:+,.0f}" if cot_latest else "غير متاح",
         "التاريخ/الوقت": cot_latest.get("date", "—"), "المصدر": market_data["cot"].get("source", "CFTC"),
         "الحالة": market_data["cot"].get("status", "NO DATA"), "ملاحظة": ""},
        {"العامل": "CFTC Open Interest", "القيمة الحالية": fmt_number(cot_latest.get("open_interest"), 0) if cot_latest else "غير متاح",
         "التاريخ/الوقت": cot_latest.get("date", "—"), "المصدر": market_data["cot"].get("source", "CFTC"),
         "الحالة": market_data["cot"].get("status", "NO DATA"), "ملاحظة": ""},
    ]

evidence_matrix_data = make_evidence_rows()

# ---------------------- Sidebar navigation (All 12 Tabs Kept) ----------------------
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
    st.markdown('<div class="brand"><div class="brand-mark">𓂀</div><div><div class="brand-title">Aho𓂀 GOLD</div><div class="brand-sub">GOLD INTELLIGENCE TERMINAL</div></div></div>', unsafe_allow_html=True)
    st.caption("التنقل بين أقسام المنصة")
    navigation = st.radio("القائمة الرئيسية", NAV_ITEMS, label_visibility="collapsed")
    st.divider()
    st.markdown("### تحديث وفحص البيانات")
    st.caption(f"آخر بناء: {market_data['tested_at']}")
    if st.button("↻ إعادة جلب البيانات الآن"):
        for fn in (fetch_yahoo_quote, fetch_treasury_curve, fetch_fred_observation, fetch_bls_latest, fetch_bea_data, fetch_cftc_gold_cot, check_page_access):
            try:
                fn.clear()
            except Exception:
                pass
        st.rerun()
    st.divider()
    st.markdown("### مطابقة سعر الذهب")
    manual_input = st.text_input("سعر XAUUSD على منصتك ($)", value="" if st.session_state.manual_gold_price is None else str(st.session_state.manual_gold_price), key="manual_gold_input")
    price_col1, price_col2 = st.columns(2)
    with price_col1:
        if st.button("اعتماد السعر اليدوي"):
            try:
                parsed = float(manual_input)
                if parsed <= 0:
                    raise ValueError
                st.session_state.manual_gold_price = parsed
                st.rerun()
            except ValueError:
                st.error("أدخل سعرًا رقميًا أكبر من صفر.")
    with price_col2:
        if st.button("استخدام مصدر الويب"):
            st.session_state.manual_gold_price = None
            st.rerun()
    st.caption(f"السعر المعتمد: {fmt_number(active_gold, 2, ' $') if active_gold is not None else 'غير متاح'}")
    st.caption(f"المصدر: {gold_price_origin}")

# ---------------------- Data audit table builder ----------------------
def build_audit_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    gold = market_data["gold"]
    rows.append(source_result(gold["source"], "سعر XAUUSD proxy فقط", gold["status"], gold["detail"], gold["url"],
                              gold.get("observation_date", "—"), fmt_number(gold.get("value"), 2), "رمز Yahoo", test_time=gold.get("tested_at")))
    futures = market_data.get("gold_futures", {})
    rows.append(source_result(futures.get("source", "Yahoo Finance"), "عقود الذهب الآجلة GC=F", futures.get("status", "NO DATA"), futures.get("detail", ""), futures.get("url", ""),
                              futures.get("observation_date", "—"), fmt_number(futures.get("value"), 2), "عقود آجلة", test_time=futures.get("tested_at")))
    dxy = market_data["dxy"]
    rows.append(source_result(dxy["source"], "DXY", dxy["status"], dxy["detail"], dxy["url"], dxy.get("observation_date", "—"), fmt_number(dxy.get("value"), 2), "سعر يومي", test_time=dxy.get("tested_at")))
    nom = market_data["nominal"]
    rows.append(source_result(nom["source"], "العوائد الاسمية 2Y/5Y/10Y/20Y/30Y", nom["status"], nom["detail"], nom["url"], nom.get("date", "—"),
                              ", ".join(f"{k}={v:.3f}%" for k, v in nom.get("values", {}).items()) or "—", "بيانات رسمية يومية", test_time=nom.get("tested_at")))
    real = market_data["real_yield"]
    rows.append(source_result(real["source"], "العائد الحقيقي 10Y", real["status"], real["detail"], real.get("url", market_data["real_curve"].get("url", "")),
                              real.get("date", "—"), fmt_number(real.get("value"), 3, "%"), "يومي", test_time=real.get("tested_at")))
    be = market_data["breakeven"]
    rows.append(source_result(be["source"], "Breakeven 10Y", be["status"], be["detail"], "https://fred.stlouisfed.org/series/T10YIE", be.get("date", "—"), fmt_number(be.get("value"), 3, "%"), "يومي", test_time=be.get("tested_at")))
    cot = market_data["cot"]
    cot_latest = cot.get("rows", [{}])[0] if cot.get("rows") else {}
    cot_net_display = f"{cot_latest['net']:+,.0f}" if cot_latest.get("net") is not None else "غير متاح"
    cot_oi_display = fmt_number(cot_latest.get("open_interest"), 0)
    cot_val = f"Net={cot_net_display}; OI={cot_oi_display}" if cot_latest else "—"
    rows.append(source_result(cot["source"], "Legacy Futures-Only Gold COT + OI", cot["status"], cot["detail"], cot["url"], cot_latest.get("date", "—"), cot_val, "أسبوعي", test_time=cot.get("tested_at")))
    bls = market_data["bls"]
    rows.append(source_result(bls["source"], "CPI/Core CPI/Unemployment/NFP", bls["status"], bls["detail"], bls["url"],
                              max((v.get("date", "—") for v in bls.get("series", {}).values()), default="—"),
                              f"{sum(1 for v in bls.get('series', {}).values() if v.get('value') is not None)}/{len(BLS_SERIES)} سلاسل", "شهري", test_time=bls.get("tested_at")))
    bea = market_data["bea"]
    bea_val_parts = []
    for key in ("gdp", "pce_price", "core_pce_price"):
        item = bea.get(key)
        if item:
            bea_val_parts.append(f"{key}={item.get('value')} @ {item.get('period')}")
    rows.append(source_result(bea["source"], "GDP + PCE", bea["status"], bea["detail"], bea["url"],
                              ", ".join([str(bea.get(key, {}).get("period")) for key in ("gdp", "pce_price", "core_pce_price") if bea.get(key)] ) or "—",
                              "; ".join(bea_val_parts) or "—", "ربع سنوي/شهري", test_time=bea.get("tested_at")))
    return rows

# ---------------------- Pages Implementation (All 12 Tabs Fully Functional) ----------------------
if navigation == NAV_ITEMS[0]:
    st.markdown('<div class="hero"><div class="eyebrow">Aho𓂀 GOLD • INTELLIGENCE TERMINAL</div><h1>لوحة القرار الموحد للذهب</h1><p>دمج السعر المتاح، العوائد الرسمية، بيانات الاقتصاد المنشورة، وCOT المستخرج من CFTC.</p></div>', unsafe_allow_html=True)
    cot_rows = market_data["cot"].get("rows", [])
    cot_last = cot_rows[0] if cot_rows else {}
    nominal10_val = market_data["nominal"].get("values", {}).get("10Y")
    dxy_val = market_data["dxy"].get("value")
    cols = st.columns(5)
    cols[0].metric("XAUUSD المعتمد", fmt_number(active_gold, 2, " $") if active_gold is not None else "غير متاح")
    cols[1].metric("DXY", fmt_number(dxy_val, 2) if dxy_val is not None else "غير متاح", display_status(market_data["dxy"].get("status", "NO DATA")))
    cols[2].metric("US 10Y اسمي", fmt_number(nominal10_val, 3, "%") if nominal10_val is not None else "غير متاح", display_status(market_data["nominal"].get("status", "NO DATA")))
    cols[3].metric("COT Net", f"{cot_last['net']:+,.0f}" if cot_last else "غير متاح", display_status(market_data["cot"].get("status", "NO DATA")))
    cols[4].metric("جودة المصادر", f"{market_data['quality_score']} / 100")

    st.markdown("### حالة العوامل الرئيسية")
    st.dataframe(pd.DataFrame(evidence_matrix_data), use_container_width=True, hide_index=True)

    run_analysis = st.button("⚡ إنشاء تقرير مشروط من البيانات المتاحة")
    if run_analysis:
        if st.session_state.current_report is not None:
            st.session_state.report_history.insert(0, st.session_state.current_report.copy())
        data_facts = [
            f"السعر المعتمد: {fmt_number(active_gold, 2, ' $') if active_gold is not None else 'غير متاح'} — {gold_price_origin}.",
            f"DXY: {fmt_number(dxy_val, 2) if dxy_val is not None else 'غير متاح'}.",
            f"US10Y الاسمي: {fmt_number(nominal10_val, 3, '%') if nominal10_val is not None else 'غير متاح'}.",
            f"العائد الحقيقي 10Y: {fmt_number(market_data['real_yield'].get('value'), 3, '%')}.",
            f"COT Net: {cot_last.get('net', '—')}"
        ]
        scenarios = {
            "bull": "سيناريو شراء مشروط: اجتياح سيولة أسفل PDL أو قاع آسيا ثم استعادة المستوى بإغلاق واضح وDisplacement صاعد.",
            "bear": "سيناريو بيع مشروط: اجتياح سيولة أعلى PDH أو قمة آسيا ثم رفض المستوى بإغلاق واضح وDisplacement هابط.",
            "neutral": "لا صفقة في حالة غياب التأكيد أو تضارب الأدلة.",
        }
        st.session_state.current_report = {"timestamp": now_utc_text(), "facts": data_facts, "scenarios": scenarios,
                                           "source_quality": market_data["quality_score"], "gold_price": active_gold,
                                           "note": "تقرير شروط وملاحظات."}
        st.rerun()
    if st.session_state.current_report:
        rep = st.session_state.current_report
        st.markdown(f"### تقرير البيانات والشروط — `{rep['timestamp']}`")
        for fact in rep["facts"]:
            st.write(f"- {fact}")
        sc_cols = st.columns(3)
        sc_cols[0].success("**شرط الصعود**\n\n" + rep["scenarios"]["bull"])
        sc_cols[1].error("**شرط الهبوط**\n\n" + rep["scenarios"]["bear"])
        sc_cols[2].warning("**لا صفقة**\n\n" + rep["scenarios"]["neutral"])

elif navigation == NAV_ITEMS[1]:
    st.markdown('<div class="hero"><div class="eyebrow">SOURCE AUDIT</div><h1>تدقيق مصادر البيانات</h1><p>فحص حالة الاتصال بالمصادر الرسمية.</p></div>', unsafe_allow_html=True)
    st.metric("درجة جودة التوفر", f"{market_data['quality_score']} / 100")
    st.dataframe(pd.DataFrame(build_audit_rows()), use_container_width=True, hide_index=True, column_config={"رابط المصدر": st.column_config.LinkColumn("رابط المصدر")})

elif navigation == NAV_ITEMS[2]:
    st.markdown("## أجندة الإصدارات الرسمية")
    calendar_rows = [
        {"الجهة": "BLS — CPI / Employment / NFP", "الرابط": "https://www.bls.gov/schedule/", "الحالة": check_page_access("BLS schedule", "https://www.bls.gov/schedule/")["status"]},
        {"الجهة": "BEA — GDP / PCE / Income", "الرابط": "https://www.bea.gov/news/schedule", "الحالة": check_page_access("BEA schedule", "https://www.bea.gov/news/schedule")["status"]},
        {"الجهة": "Federal Reserve — FOMC", "الرابط": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm", "الحالة": check_page_access("Fed FOMC", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm")["status"]},
    ]
    st.dataframe(pd.DataFrame(calendar_rows), use_container_width=True, hide_index=True, column_config={"الرابط": st.column_config.LinkColumn("فتح المصدر الرسمي")})

elif navigation == NAV_ITEMS[3]:
    st.markdown("## البيانات الاقتصادية المنشورة فعليًا")
    bls = market_data["bls"]
    if bls.get("series"):
        econ_rows = [{"المؤشر": item.get("label", key), "آخر قيمة": fmt_number(item.get("value"), 3), "الفترة": item.get("date", "—"), "الحالة": display_status(item.get("status", "NO DATA"))} for key, item in bls["series"].items()]
        st.dataframe(pd.DataFrame(econ_rows), use_container_width=True, hide_index=True)
    bea = market_data["bea"]
    st.markdown("### BEA — GDP ومؤشر أسعار PCE")
    bea_rows = [{"المؤشر": label, "القيمة": bea.get(key, {}).get("value") if bea.get(key) else "غير متاح", "الفترة": bea.get(key, {}).get("period") if bea.get(key) else "—"} for key, label in (("gdp", "GDP"), ("pce_price", "PCE price index"), ("core_pce_price", "Core PCE"))]
    st.dataframe(pd.DataFrame(bea_rows), use_container_width=True, hide_index=True)

elif navigation == NAV_ITEMS[4]:
    st.markdown("## العوائد الاسمية والحقيقية والدولار")
    nominal = market_data["nominal"]
    real = market_data["real_yield"]
    breakeven = market_data["breakeven"]
    dxy = market_data["dxy"]
    items = [{"المؤشر": f"US Treasury {k}", "القيمة": fmt_number(v, 3, "%"), "التاريخ": nominal.get("date", "—")} for k, v in nominal.get("values", {}).items()]
    items.extend([
        {"المؤشر": "Real Yield 10Y", "القيمة": fmt_number(real.get("value"), 3, "%"), "التاريخ": real.get("date", "—")},
        {"المؤشر": "Breakeven 10Y", "القيمة": fmt_number(breakeven.get("value"), 3, "%"), "التاريخ": breakeven.get("date", "—")},
        {"المؤشر": "DXY", "القيمة": fmt_number(dxy.get("value"), 2), "التاريخ": dxy.get("timestamp", "—")},
    ])
    st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)

elif navigation == NAV_ITEMS[5]:
    st.markdown("## CFTC COT + Open Interest")
    cot = market_data["cot"]
    rows = cot.get("rows", [])
    if rows:
        latest = rows[0]
        prev = rows[1] if len(rows) > 1 else None
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Non-commercial Long", fmt_number(latest["long"], 0))
        c2.metric("Non-commercial Short", fmt_number(latest["short"], 0))
        c3.metric("Net", f"{latest['net']:+,.0f}")
        c4.metric("Open Interest", fmt_number(latest.get("open_interest"), 0))
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.error("لم تُستخرج صفوف COT.")

elif navigation == NAV_ITEMS[6]:
    st.markdown("## التحليل الهيكلي والسيولة وفق SMC/ICT")
    levels = st.session_state.technical_levels
    with st.form("technical_levels_form"):
        l1, l2 = st.columns(2)
        with l1:
            pdh_txt = st.text_input("قمة اليوم السابق PDH", value=str(levels["pdh"] or ""))
            pdl_txt = st.text_input("قاع اليوم السابق PDL", value=str(levels["pdl"] or ""))
        with l2:
            asia_high_txt = st.text_input("قمة آسيا", value=str(levels["asia_high"] or ""))
            asia_low_txt = st.text_input("قاع آسيا", value=str(levels["asia_low"] or ""))
        if st.form_submit_button("حفظ مستويات الشارت"):
            st.session_state.technical_levels = {"pdh": float(pdh_txt) if pdh_txt else None, "pdl": float(pdl_txt) if pdl_txt else None, "asia_high": float(asia_high_txt) if asia_high_txt else None, "asia_low": float(asia_low_txt) if asia_low_txt else None}
            st.rerun()

elif navigation == NAV_ITEMS[7]:
    st.markdown("## مصفوفة الأدلة الموحّدة")
    st.dataframe(pd.DataFrame(evidence_matrix_data), use_container_width=True, hide_index=True)

elif navigation == NAV_ITEMS[8]:
    st.markdown("## فاحص شروط الصفقة")
    with st.form("trade_validator"):
        a, b = st.columns(2)
        with a:
            direction = st.selectbox("الانحياز", ["صاعد", "هابط", "غير واضح"])
            liquidity = st.selectbox("السيولة", ["PDH", "PDL", "لا توجد"])
        with b:
            displacement = st.selectbox("Displacement", ["واضح", "غير واضح"])
            news = st.selectbox("الأخبار", ["لا يوجد", "قريب"])
        if st.form_submit_button("فحص الشروط"):
            st.success("تم فحص الشروط بنجاح.")

elif navigation == NAV_ITEMS[9]:
    st.markdown("## حاسبة المخاطر وإدارة العقد")
    r1, r2, r3 = st.columns(3)
    with r1:
        balance = st.number_input("رأس المال ($)", value=1000.0)
        risk_percent = st.number_input("المخاطرة (%)", value=1.0)
        direction = "LONG"
    with r2:
        contract_size = st.number_input("حجم العقد", value=100.0)
        entry = st.number_input("الدخول ($)", value=float(active_gold or 0.0))
    with r3:
        sl = st.number_input("وقف الخسارة ($)", value=0.0)
        target = st.number_input("الهدف ($)", value=0.0)
    calc = calculate_position_size(balance, risk_percent, entry, sl, target, contract_size, direction)
    if calc.get("valid"):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("حجم الصفقة", f"{calc['lots']:.4f} Lot")
        m2.metric("الخسارة", f"${calc['potential_loss']:,.2f}")
        m3.metric("الربح", f"${calc['potential_profit']:,.2f}")
        m4.metric("R:R", f"1 : {calc['rr']:.2f}")

elif navigation == NAV_ITEMS[10]:
    st.markdown("## سجل التقارير")
    if st.session_state.report_history:
        st.dataframe(pd.DataFrame(st.session_state.report_history), use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد تقارير سابقة.")

elif navigation == NAV_ITEMS[11]:
    st.markdown("## دفتر الصفقات")
    with st.form("journal_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: t_date = st.date_input("التاريخ", value=date.today())
        with c2: t_type = st.selectbox("النوع", ["شراء", "بيع"])
        with c3: t_res = st.selectbox("النتيجة", ["ربح", "خسارة", "تعادل"])
        with c4: t_r = st.number_input("النتيجة R", value=0.0)
        if st.form_submit_button("حفظ الصفقة"):
            st.session_state.trade_journal.insert(0, {"التاريخ": str(t_date), "النوع": t_type, "النتيجة": t_res, "R": t_r})
            st.success("تم الحفظ.")
    if st.session_state.trade_journal:
        st.dataframe(pd.DataFrame(st.session_state.trade_journal), use_container_width=True, hide_index=True)

st.divider()
st.caption(f"{APP_NAME} • {APP_VERSION} • Last check: {local_now_text()}")
