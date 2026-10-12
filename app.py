# ================================================================
# YUNAN GOLD INTELLIGENCE — v16.0 FINAL (SINGLE-FILE BUILD)
# ================================================================
from __future__ import annotations
import os, re, json as _json, hmac, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta, date
from io import StringIO
from typing import Any, Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
import streamlit as st
import bcrypt

APP_NAME = "YUNAN GOLD INTELLIGENCE"
APP_VERSION = "16.0 — FINAL INTEGRATED BUILD"
REQUEST_TIMEOUT = 15
USER_AGENT = "YunanGoldIntelligence/16.0"

st.set_page_config(page_title=APP_NAME, page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

# ================================================================
# CSS (مختصر)
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#06090f;--panel:#0d131d;--line:#1e2c3d;--gold:#d9b56d;
--green:#00e676;--red:#ff5252;--yellow:#ffeb3b;--muted:#8b9bb4;--text:#eef2f7}
html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic','Inter',sans-serif;direction:rtl;text-align:right}
.stApp{background:radial-gradient(circle at 50% 0%,#111b29 0%,var(--bg) 60%);color:var(--text)}
.block-container{padding-top:1.2rem!important;max-width:1550px}
[data-testid="stSidebar"]{background:#070b12;border-left:1px solid var(--line)}
[data-testid="stSidebar"] *{text-align:right}
.brand{display:flex;align-items:center;gap:12px;padding:4px 0 16px;border-bottom:1px solid var(--line);margin-bottom:14px}
.brand-mark{width:42px;height:42px;border:1px solid #7a643b;border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:21px;background:linear-gradient(145deg,#221c13,#0d121a)}
.brand-title{font-family:Inter,sans-serif;letter-spacing:1px;font-weight:800;font-size:15px;color:#f4f0e7}
.brand-sub{color:var(--muted);font-size:10px;margin-top:2px}
.hero{border:1px solid #233142;border-radius:16px;padding:20px 24px;background:linear-gradient(135deg,rgba(17,25,38,.95),rgba(8,12,18,.95));margin-bottom:16px}
.eyebrow{color:var(--gold);letter-spacing:1.4px;font-size:11px;font-weight:700;font-family:Inter,sans-serif}
.hero h1{margin:6px 0;font-size:22px;color:#f7f5ef;font-weight:700}
.hero p{margin:0;color:#9fb0c6;line-height:1.7;font-size:13px}
.fusion-card{background:#0b111a;border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:12px}
.fusion-card h4{color:var(--gold);margin:0 0 8px;font-size:14px}
.stButton button{border-radius:10px;border:1px solid #d9b56d!important;background:linear-gradient(135deg,#d9b56d,#b3914a)!important;color:#06090f!important;font-weight:800!important;width:100%;padding:9px}
.warning-box{border:1px solid #7a5c22;background:#1b170d;border-radius:10px;padding:12px 14px;margin:8px 0;color:#f3d89b;font-size:13px}
.signal-bull{border:1px solid #1a6b3a;background:#0a1f12;border-radius:10px;padding:14px;margin:8px 0}
.signal-bear{border:1px solid #6b1a1a;background:#1f0a0a;border-radius:10px;padding:14px;margin:8px 0}
.signal-neutral{border:1px solid #6b5a1a;background:#1f1a0a;border-radius:10px;padding:14px;margin:8px 0}
.signal-no-trade{border:1px solid #444;background:#111;border-radius:10px;padding:14px;margin:8px 0}
footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

# ================================================================
# SECRETS & HELPERS
# ================================================================
def get_secret(name: str) -> str:
    v = ""
    try: v = st.secrets.get(name, "")
    except Exception: pass
    if not v: v = os.getenv(name, "")
    return str(v).strip() if v else ""

def now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def request_get(url: str, **kw) -> requests.Response:
    h = kw.pop("headers", {})
    h.setdefault("User-Agent", USER_AGENT)
    h.setdefault("Accept", "application/json,text/html,*/*")
    return requests.get(url, timeout=REQUEST_TIMEOUT, headers=h, **kw)

def classify_exception(exc: Exception) -> str:
    if isinstance(exc, (requests.Timeout, TimeoutError)): return "TIMEOUT"
    if isinstance(exc, requests.HTTPError):
        c = exc.response.status_code if exc.response is not None else None
        if c == 429: return "RATE LIMITED"
        if c in (401, 403): return "AUTH ERROR"
        return "UNAVAILABLE"
    if isinstance(exc, requests.RequestException): return "UNAVAILABLE"
    return "NO DATA"

def fmt_number(v: Any, d: int = 2, s: str = "") -> str:
    try: return f"{float(v):,.{d}f}{s}"
    except (TypeError, ValueError): return "غير متاح"

def safe_float(v: Any) -> Optional[float]:
    try:
        x = float(v)
        return x if pd.notna(x) else None
    except (TypeError, ValueError): return None

def display_status(s: str) -> str:
    return {
        "CONNECTED": "🟢 CONNECTED", "STALE": "🟠 STALE",
        "RATE LIMITED": "🟠 RATE LIMITED", "AUTH ERROR": "🔴 AUTH ERROR",
        "TIMEOUT": "🟠 TIMEOUT", "NO DATA": "🔴 NO DATA",
        "NOT TESTED": "⚪ NOT TESTED", "UNAVAILABLE": "🔴 UNAVAILABLE",
    }.get(s, s)

# ================================================================
# FRESHNESS SYSTEM
# ================================================================
FRESHNESS_PROFILES = {
    "intraday":  {"max_age_hours": 6,   "label": "لحظي"},
    "daily":     {"max_age_hours": 48,  "label": "يومي"},
    "weekly":    {"max_age_days": 10,   "label": "أسبوعي"},
    "monthly":   {"max_age_days": 75,   "label": "شهري"},
    "quarterly": {"max_age_days": 150,  "label": "ربع سنوي"},
}

def assess_freshness(obs_date: Any, profile: str) -> dict[str, Any]:
    cfg = FRESHNESS_PROFILES[profile]
    d = pd.to_datetime(obs_date, utc=True, errors="coerce")
    if pd.isna(d):
        return {"age": None, "usable": False,
                "detail": "تاريخ غير صالح.", "profile": profile}
    delta = pd.Timestamp.now(tz="UTC") - d
    if "max_age_hours" in cfg:
        age = delta.total_seconds() / 3600
        usable = age <= cfg["max_age_hours"]
        detail = f"عمر {age:.1f} ساعة (الحد {cfg['max_age_hours']}س)."
    else:
        age = delta.days
        usable = age <= cfg["max_age_days"]
        detail = f"عمر {age} يوم (الحد {cfg['max_age_days']} يوم)."
    return {"age": age, "usable": usable, "detail": detail, "profile": profile}

# ================================================================
# RBAC — bcrypt + 4 roles
# ================================================================
def _get_users() -> dict[str, dict]:
    raw = get_secret("APP_USERS")
    if raw:
        try: return _json.loads(raw)
        except Exception: pass
    u = get_secret("APP_USERNAME"); p = get_secret("APP_PASSWORD")
    if u and p:
        return {u: {"pw_hash": bcrypt.hashpw(p.encode(), bcrypt.gensalt(rounds=12)).decode(), "role": "admin"}}
    return {}

def _verify_password(pw: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception: return False

def _verify_credentials(user: str, pw: str) -> Optional[dict]:
    users = _get_users()
    if user not in users: return None
    if _verify_password(pw, users[user].get("pw_hash", "")):
        return {"username": user, "role": users[user].get("role", "viewer")}
    return None

# ================================================================
# AUDIT LOG
# ================================================================
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

def log_action(category: str, action: str, old_value: Any = None,
               new_value: Any = None, reason: str = "") -> None:
    st.session_state.audit_log.append({
        "time": now_utc_text(),
        "user": st.session_state.get("user", {}).get("username", "—"),
        "role": st.session_state.get("user", {}).get("role", "—"),
        "category": category, "action": action,
        "old_value": old_value, "new_value": new_value,
        "reason": reason,
    })

# ================================================================
# NOTIFICATIONS — Telegram + Gmail
# ================================================================
def send_telegram(text: str) -> dict[str, Any]:
    token = get_secret("TELEGRAM_BOT_TOKEN")
    chat = get_secret("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return {"status": "NOT TESTED", "detail": "Telegram غير مضبوط."}
    try:
        r = request_get(
            f"https://api.telegram.org/bot{token}/sendMessage",
            params={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
        )
        r.raise_for_status()
        return {"status": "CONNECTED", "detail": "تم الإرسال."}
    except Exception as exc:
        return {"status": classify_exception(exc),
                "detail": f"Telegram: {type(exc).__name__}."}

def send_email(subject: str, body: str, to_addr: str) -> dict[str, Any]:
    user = get_secret("GMAIL_USER")
    pw = get_secret("GMAIL_APP_PASSWORD")
    if not user or not pw or not to_addr:
        return {"status": "NOT TESTED", "detail": "Gmail SMTP غير مضبوط."}
    try:
        msg = MIMEMultipart()
        msg["From"] = user; msg["To"] = to_addr; msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as srv:
            srv.login(user, pw)
            srv.send_message(msg)
        return {"status": "CONNECTED", "detail": "تم الإرسال."}
    except Exception as exc:
        return {"status": "UNAVAILABLE",
                "detail": f"SMTP: {type(exc).__name__}."}

# ================================================================
# YAHOO FINANCE
# ================================================================
def _yahoo_quote_impl(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    errors = []
    for sym in symbols:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
        try:
            r = request_get(url, params={"range": "5d", "interval": "1d"})
            if r.status_code == 429:
                return {"status": "RATE LIMITED", "label": label,
                        "symbol": sym, "value": None, "change": None,
                        "observation_date": "—", "timestamp": "—",
                        "source": "Yahoo Finance",
                        "url": "https://finance.yahoo.com/",
                        "detail": "HTTP 429."}
            r.raise_for_status()
            res = (r.json().get("chart", {}).get("result") or [None])[0]
            if not res: continue
            q = (res.get("indicators", {}).get("quote") or [{}])[0]
            closes = q.get("close", []) or []
            ts = res.get("timestamp", []) or []
            valid = [(int(t), float(c)) for t, c in zip(ts, closes) if c is not None]
            if not valid: continue
            last_ts, last_v = valid[-1]
            prev_v = valid[-2][1] if len(valid) >= 2 else None
            obs = datetime.fromtimestamp(last_ts, timezone.utc)
            fr = assess_freshness(obs, "intraday")
            status = "CONNECTED" if fr["usable"] else "STALE"
            return {"status": status, "label": label, "symbol": sym,
                    "value": last_v, "change": (last_v - prev_v) if prev_v else None,
                    "observation_date": obs.strftime("%Y-%m-%d"),
                    "timestamp": obs.strftime("%Y-%m-%d %H:%M UTC"),
                    "freshness_detail": fr["detail"],
                    "source": f"Yahoo Finance ({sym})",
                    "url": "https://finance.yahoo.com/",
                    "detail": f"{fr['detail']} • {sym}"}
        except Exception as exc:
            errors.append(f"{sym}: {type(exc).__name__}")
    return {"status": "UNAVAILABLE", "label": label, "symbol": "—",
            "value": None, "change": None, "observation_date": "—",
            "timestamp": "—", "source": "Yahoo Finance",
            "url": "https://finance.yahoo.com/",
            "detail": "تعذر الجلب: " + " | ".join(errors[:3])}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_quote(symbols: tuple[str, ...], label: str) -> dict[str, Any]:
    res = _yahoo_quote_impl(symbols, label)
    res["tested_at"] = now_utc_text()
    return res

# ================================================================
# OHLC ENGINE (Yahoo chart endpoint)
# ================================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_gold_ohlc(range_: str = "6mo", interval: str = "1d") -> dict[str, Any]:
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
    try:
        r = request_get(url, params={"range": range_, "interval": interval})
        if r.status_code == 429:
            return {"status": "RATE LIMITED", "df": None, "detail": "HTTP 429."}
        r.raise_for_status()
        res = (r.json().get("chart", {}).get("result") or [None])[0]
        if not res: return {"status": "NO DATA", "df": None, "detail": "لا نتائج."}
        ts = res.get("timestamp", []) or []
        q = (res.get("indicators", {}).get("quote") or [{}])[0]
        O, H, L, C, V = (q.get(k, []) or [] for k in ("open","high","low","close","volume"))
        rows = []
        for i in range(min(len(ts), len(O), len(H), len(L), len(C))):
            if None in (O[i], H[i], L[i], C[i]): continue
            rows.append({"timestamp": datetime.fromtimestamp(ts[i], timezone.utc),
                         "open": float(O[i]), "high": float(H[i]),
                         "low": float(L[i]), "close": float(C[i]),
                         "volume": float(V[i]) if i < len(V) and V[i] is not None else 0.0})
        if not rows: return {"status": "NO DATA", "df": None, "detail": "أعمدة فارغة."}
        df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
        last = df.iloc[-1]
        fr = assess_freshness(last["timestamp"], "intraday")
        return {"status": "CONNECTED" if fr["usable"] else "STALE", "df": df,
                "source": "Yahoo Finance (GC=F)",
                "url": "https://finance.yahoo.com/",
                "observation_date": last["timestamp"].strftime("%Y-%m-%d"),
                "freshness_detail": fr["detail"],
                "detail": f"{len(df)} شمعة • {fr['detail']}"}
    except Exception as exc:
        return {"status": classify_exception(exc), "df": None,
                "detail": f"خطأ: {type(exc).__name__}."}

# ================================================================
# TECHNICAL INDICATORS
# ================================================================
def compute_indicators(df: pd.DataFrame) -> dict[str, Any]:
    if df is None or len(df) < 20:
        return {"status": "NO DATA", "detail": "OHLC غير كافٍ."}
    close = df["close"].astype(float); high = df["high"].astype(float); low = df["low"].astype(float)
    log_ret = np.log(close / close.shift()).dropna()

    def atr(period):
        tr = pd.concat([high - low, (high - close.shift()).abs(),
                        (low - close.shift()).abs()], axis=1).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1])

    sma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
    trend = "UP" if sma50 and sma20.iloc[-1] > sma50 else "DOWN" if sma50 else "FLAT"
    highs, lows = high.values, low.values
    swing_h, swing_l = [], []
    for i in range(2, len(df) - 2):
        if highs[i] == max(highs[i-2:i+3]): swing_h.append(highs[i])
        if lows[i] == min(lows[i-2:i+3]): swing_l.append(lows[i])

    def cluster(levels, tol=0.5):
        if not levels: return []
        levels = sorted(levels); groups = [[levels[0]]]
        for lv in levels[1:]:
            if abs(lv - groups[-1][-1]) / groups[-1][-1] * 100 < tol:
                groups[-1].append(lv)
            else: groups.append([lv])
        return [round(sum(g)/len(g), 2) for g in groups if len(g) >= 2]

    return {
        "status": "OK",
        "atr14": round(atr(14), 2), "atr7": round(atr(7), 2),
        "vol20": round(float(log_ret.tail(20).std() * np.sqrt(252) * 100), 2),
        "vol60": round(float(log_ret.tail(60).std() * np.sqrt(252) * 100), 2),
        "bb_upper": round(float((sma20 + 2*std20).iloc[-1]), 2),
        "bb_mid": round(float(sma20.iloc[-1]), 2),
        "bb_lower": round(float((sma20 - 2*std20).iloc[-1]), 2),
        "year_high": round(float(high.tail(252).max()), 2) if len(df) >= 252 else round(float(high.max()), 2),
        "year_low": round(float(low.tail(252).min()), 2) if len(df) >= 252 else round(float(low.min()), 2),
        "supports": cluster(swing_l)[:3], "resistances": cluster(swing_h)[-3:],
        "trend": trend, "bars": len(df),
    }

# ================================================================
# SMC/ICT ENGINE v2
# ================================================================
def detect_swings(df, left=2, right=2):
    if df is None or len(df) < left + right + 1: return {"highs": [], "lows": []}
    h, l = df["high"].values, df["low"].values
    sh, sl = [], []
    for i in range(left, len(df) - right):
        if h[i] == max(h[i-left:i+right+1]): sh.append((i, float(h[i])))
        if l[i] == min(l[i-left:i+right+1]): sl.append((i, float(l[i])))
    return {"highs": sh, "lows": sl}

def detect_bos_choch(df, swings):
    out = {"structure": "UNDEFINED", "last_bos": None}
    if not swings["highs"] or not swings["lows"]: return out
    if len(swings["highs"]) >= 2 and len(swings["lows"]) >= 2:
        ph = swings["highs"][-2]; pl = swings["lows"][-2]
        lc = float(df["close"].iloc[-1])
        if lc > ph[1]: out["last_bos"] = ("BULLISH", ph[1]); out["structure"] = "BULLISH_BOS"
        elif lc < pl[1]: out["last_bos"] = ("BEARISH", pl[1]); out["structure"] = "BEARISH_BOS"
        else:
            rh, rl = swings["highs"][-1], swings["lows"][-1]
            mid = (rh[1] + rl[1]) / 2
            out["structure"] = "RANGE" if abs(lc - mid) < (rh[1] - rl[1]) * 0.3 else "TRENDING"
    return out

def detect_sweeps(df, swings, atr):
    sweeps = []
    if df is None or atr is None: return sweeps
    last = df.iloc[-1]
    for _, lvl in swings["highs"][-5:]:
        if last["high"] > lvl and last["close"] < lvl:
            sweeps.append({"type": "BEARISH_SWEEP", "level": lvl,
                           "detail": f"اختراق قمة {lvl:.2f} ثم إغلاق أسفلها."})
    for _, lvl in swings["lows"][-5:]:
        if last["low"] < lvl and last["close"] > lvl:
            sweeps.append({"type": "BULLISH_SWEEP", "level": lvl,
                           "detail": f"اختراق قاع {lvl:.2f} ثم إغلاق أعلاه."})
    return sweeps

def analyze_smc_ict_v2(ohlc_res):
    df = ohlc_res.get("df")
    out = {"status": ohlc_res.get("status", "NO DATA"),
           "structure": "UNDEFINED", "bias": "NEUTRAL",
           "signals": [], "sweeps": [], "atr": None,
           "pdh": None, "pdl": None,
           "source": ohlc_res.get("source", "—")}
    if df is None or len(df) < 10:
        out["signals"].append("⚠️ لا OHLC كافٍ.")
        return out
    if len(df) >= 2:
        y = df.iloc[-2]; out["pdh"] = float(y["high"]); out["pdl"] = float(y["low"])
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(),
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    out["atr"] = float(tr.rolling(14).mean().iloc[-1])
    sw = detect_swings(df, 2, 2)
    bi = detect_bos_choch(df, sw)
    out["structure"] = bi["structure"]
    out["signals"].append(f"البنية: {bi['structure']}")
    if bi["last_bos"]:
        side, lvl = bi["last_bos"]
        out["bias"] = "BULLISH" if side == "BULLISH" else "BEARISH"
        out["signals"].append(f"BOS {side} عند {lvl:.2f}")
    out["sweeps"] = detect_sweeps(df, sw, out["atr"])
    for s in out["sweeps"]: out["signals"].append(f"🚨 {s['detail']}")
    out["signals"].append(f"ATR(14): {out['atr']:.2f}")
    return out

# ================================================================
# TREASURY CURVE (CSV)
# ================================================================
def _norm_col(v): return re.sub(r"[^a-z0-9]", "", str(v).lower())

def _find_yield_col(cols, years):
    norm = {c: _norm_col(c) for c in cols}
    for c, n in norm.items():
        if n in {f"{years}yr", f"{years}year", f"{years}yrs", f"{years}years", f"{years}y", f"{years}mo"}:
            return c
    for c, n in norm.items():
        if n.startswith(str(years)) and ("yr" in n or "year" in n or n.endswith("y")): return c
    return None

def _treasury_impl(real: bool = False):
    t = "daily_treasury_real_yield_curve" if real else "daily_treasury_yield_curve"
    year = datetime.now(timezone.utc).year
    url = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type={t}&field_tdr_date_value={year}&page&_format=csv"
    name = "U.S. Treasury real yield curve" if real else "U.S. Treasury nominal yield curve"
    try:
        r = request_get(url)
        if r.status_code == 429:
            return {"status": "RATE LIMITED", "source": name, "url": url,
                    "date": "—", "values": {}, "detail": "HTTP 429."}
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        if df.empty: return {"status": "NO DATA", "source": name, "url": url, "date": "—", "values": {}, "detail": "فارغ."}
        date_col = next((c for c in df.columns if "date" in _norm_col(c)), None)
        df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
        df = df[df["_date"].notna()].sort_values("_date", ascending=False)
        if df.empty: return {"status": "NO DATA", "source": name, "url": url, "date": "—", "values": {}, "detail": "لا تواريخ."}
        latest = df.iloc[0]; vals = {}
        for y in (2, 5, 10, 20, 30):
            c = _find_yield_col(list(df.columns), y)
            if c is None: continue
            raw = str(latest[c]).replace("%", "").replace(",", "").strip()
            if raw and raw.lower() not in {"nan", "none", "-", "n/a"}:
                try: vals[f"{y}Y"] = float(raw)
                except ValueError: pass
        if "10Y" not in vals:
            return {"status": "NO DATA", "source": name, "url": url, "date": "—", "values": {}, "detail": "10Y مفقود."}
        obs = latest["_date"].strftime("%Y-%m-%d")
        fr = assess_freshness(obs, "daily")
        return {"status": "CONNECTED" if fr["usable"] else "STALE",
                "source": "U.S. Treasury official data", "url": url,
                "date": obs, "values": vals, "freshness_detail": fr["detail"],
                "detail": f"نجح • {fr['detail']}"}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": name, "url": url,
                "date": "—", "values": {}, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_treasury_curve(real: bool = False):
    r = _treasury_impl(real); r["tested_at"] = now_utc_text(); return r

# ================================================================
# FRED — observations + releases
# ================================================================
FRED_SERIES_META = {
    "DGS2": ("عائد 2Y", 8, "daily"), "DGS5": ("عائد 5Y", 8, "daily"),
    "DGS10": ("عائد 10Y", 8, "daily"), "DGS20": ("عائد 20Y", 8, "daily"),
    "DGS30": ("عائد 30Y", 8, "daily"), "DFII10": ("عائد حقيقي 10Y", 8, "daily"),
    "T10YIE": ("تضخم متوقع 10Y", 8, "daily"), "CPIAUCSL": ("CPI", 75, "monthly"),
}

def _fred_obs_impl(sid: str, key: str):
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        r = request_get(url, params={"series_id": sid, "api_key": key,
                                     "file_type": "json", "sort_order": "desc", "limit": 12})
        if r.status_code == 429:
            return {"status": "RATE LIMITED", "series": sid, "value": None, "date": "—", "source": "FRED API", "detail": "HTTP 429."}
        r.raise_for_status()
        obs = [o for o in r.json().get("observations", []) if o.get("value") not in (None, ".", "")]
        if not obs: return {"status": "NO DATA", "series": sid, "value": None, "date": "—", "source": "FRED API", "detail": "فارغ."}
        lt = obs[0]; lbl, _, prof = FRED_SERIES_META.get(sid, (sid, 10, "daily"))
        fr = assess_freshness(lt.get("date"), prof)
        return {"status": "CONNECTED" if fr["usable"] else "STALE",
                "series": sid, "label": lbl, "value": float(lt["value"]),
                "date": lt.get("date", "—"), "source": "FRED API",
                "detail": fr["detail"], "freshness_detail": fr["detail"]}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": sid, "value": None,
                "date": "—", "source": "FRED API", "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_fred_obs(sid: str, key: str):
    r = _fred_obs_impl(sid, key); r["tested_at"] = now_utc_text(); return r

FRED_RELEASES = {10: ("CPI", "🔴", "BLS"), 50: ("Nonfarm Payrolls", "🔴", "BLS"),
                 53: ("GDP", "🔴", "BEA"), 54: ("PCE / Personal Income", "🔴", "BEA"),
                 9: ("Retail Sales", "🟠", "Census Bureau")}

FOMC_DATES_2026 = ["2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
                   "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09"]

@st.cache_data(ttl=21600, show_spinner=False)
def fetch_fred_release_dates(rid: int, key: str):
    url = "https://api.stlouisfed.org/fred/release/dates"
    try:
        r = request_get(url, params={"release_id": rid, "api_key": key,
                                     "file_type": "json",
                                     "include_release_dates_with_no_data": "true",
                                     "sort_order": "asc", "limit": 12})
        r.raise_for_status()
        dates = r.json().get("release_dates", [])
        return {"status": "CONNECTED", "dates": [d.get("date") for d in dates if d.get("date")],
                "detail": f"{len(dates)} موعدًا."}
    except Exception as exc:
        return {"status": classify_exception(exc), "dates": [], "detail": f"خطأ: {type(exc).__name__}."}

def build_news_calendar(key: str) -> pd.DataFrame:
    events = []; now = datetime.now(timezone.utc).date()
    for rid, (name, imp, src) in FRED_RELEASES.items():
        if not key: break
        res = fetch_fred_release_dates(rid, key)
        if res.get("status") != "CONNECTED": continue
        for d in res.get("dates", []):
            try: dt = pd.to_datetime(d).date()
            except Exception: continue
            if dt < now: continue
            events.append({"date": str(dt), "event": name, "importance": imp,
                           "source": src, "url": f"https://fred.stlouisfed.org/release?rid={rid}"})
    year = now.year
    for d in (FOMC_DATES_2026 if year == 2026 else []):
        try: dt = pd.to_datetime(d).date()
        except Exception: continue
        if dt < now: continue
        events.append({"date": str(dt), "event": "FOMC Meeting", "importance": "🔴",
                       "source": "Federal Reserve",
                       "url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"})
    if not events: return pd.DataFrame()
    df = pd.DataFrame(events).sort_values("date").reset_index(drop=True)
    df.columns = ["التاريخ", "الحدث", "الأهمية", "المصدر", "الرابط"]
    return df

# ================================================================
# BLS v2
# ================================================================
BLS_SERIES = {
    "headline_cpi": ("CUSR0000SA0", "CPI العام", "monthly"),
    "core_cpi": ("CUSR0000SA0L1E", "Core CPI", "monthly"),
    "unemployment": ("LNS14000000", "البطالة", "monthly"),
    "nonfarm_payrolls": ("CES0000000001", "الوظائف", "monthly"),
    "hourly_earnings": ("CES0500000003", "الأجور", "monthly"),
}

def compute_bls_changes(rows):
    if not rows: return {"mom_pct": None, "yoy_pct": None, "latest_level": None}
    try: lt = float(rows[0]["value"])
    except (KeyError, ValueError): return {"mom_pct": None, "yoy_pct": None, "latest_level": None}
    def back(n):
        y = int(rows[0]["year"]); m = int(rows[0]["period"][1:]) - n
        while m <= 0: m += 12; y -= 1
        for r in rows:
            if int(r["year"]) == y and int(r["period"][1:]) == m:
                try: return float(r["value"])
                except ValueError: return None
        return None
    pm, py = back(1), back(12)
    return {"latest_level": lt,
            "mom_pct": round((lt/pm - 1)*100, 2) if pm else None,
            "yoy_pct": round((lt/py - 1)*100, 2) if py else None}

def _bls_v2_impl(key: str = ""):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    cy = datetime.now(timezone.utc).year
    payload = {"seriesid": [m[0] for m in BLS_SERIES.values()],
               "startyear": str(cy-2), "endyear": str(cy),
               "catalog": False, "calculations": False, "annualaverage": False}
    if key: payload["registrationkey"] = key
    try:
        r = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT,
                          headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
        if r.status_code == 429:
            return {"status": "RATE LIMITED", "series": {}, "source": "BLS API v2", "url": url, "detail": "HTTP 429."}
        r.raise_for_status()
        b = r.json()
        if b.get("status") != "REQUEST_SUCCEEDED":
            return {"status": "NO DATA", "series": {}, "source": "BLS API v2", "url": url,
                    "detail": "BLS: " + "; ".join((b.get("message") or [])[:3])}
        raw = b.get("Results", {}).get("series", [])
        mapping = {}
        for it in raw:
            sid = it.get("seriesID")
            mapping[sid] = sorted([e for e in it.get("data", []) if str(e.get("period", "")) != "M13"],
                                  key=lambda x: (int(x.get("year", 0)),
                                                 int(x.get("period", "M0")[1:]) if str(x.get("period", "")).startswith("M") else 0),
                                  reverse=True)
        results = {}
        for k, (sid, lbl, _) in BLS_SERIES.items():
            rows = mapping.get(sid, [])
            if not rows:
                results[k] = {"status": "NO DATA", "series_id": sid, "label": lbl,
                              "level": None, "mom_pct": None, "yoy_pct": None, "date": "—", "detail": "بلا بيانات."}
                continue
            lt = rows[0]; ch = compute_bls_changes(rows)
            fr = assess_freshness(f"{lt.get('year')}-{lt.get('period')}", "monthly")
            results[k] = {"status": "CONNECTED" if fr["usable"] else "STALE",
                          "series_id": sid, "label": lbl, "level": ch["latest_level"],
                          "mom_pct": ch["mom_pct"], "yoy_pct": ch["yoy_pct"],
                          "date": f"{lt.get('year')}-{lt.get('period')}",
                          "freshness_detail": fr["detail"], "detail": fr["detail"]}
        req = {"headline_cpi", "unemployment", "nonfarm_payrolls"}
        if all(results.get(k, {}).get("status") == "CONNECTED" for k in req): ov = "CONNECTED"
        elif any(results.get(k, {}).get("status") == "CONNECTED" for k in req): ov = "STALE"
        else: ov = "NO DATA"
        return {"status": ov, "series": results, "source": "BLS API v2", "url": url,
                "detail": "تم الجلب.", "v2_key_used": bool(key)}
    except Exception as exc:
        return {"status": classify_exception(exc), "series": {}, "source": "BLS API v2",
                "url": url, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_v2(key: str = ""):
    r = _bls_v2_impl(key); r["tested_at"] = now_utc_text(); return r

# ================================================================
# BEA
# ================================================================
def _bea_impl(key: str):
    url = "https://apps.bea.gov/api/data/"
    if not key:
        return {"status": "NOT TESTED", "source": "BEA API",
                "url": "https://apps.bea.gov/api/signup/", "detail": "لا مفتاح.", "value": None, "date": "—"}
    try:
        r = request_get(url, params={"UserID": key, "method": "GetData", "DataSetName": "NIPA",
                                     "TableName": "T10101", "Frequency": "Q", "Year": "X", "ResultFormat": "JSON"})
        if r.status_code == 429: return {"status": "RATE LIMITED", "source": "BEA API", "url": url, "detail": "HTTP 429.", "value": None, "date": "—"}
        r.raise_for_status()
        res = (r.json().get("BEAAPI") or {}).get("Results") or {}
        if isinstance(res, dict) and "Error" in res:
            e = res["Error"]; msg = e.get("APIErrorDescription") if isinstance(e, dict) else str(e)
            return {"status": "NO DATA", "source": "BEA API", "url": url, "detail": f"BEA: {msg}", "value": None, "date": "—"}
        data = res.get("Data") if isinstance(res, dict) else None
        if not data: return {"status": "NO DATA", "source": "BEA API", "url": url, "detail": "لا صفوف.", "value": None, "date": "—"}
        lt = max(data, key=lambda x: (x.get("TimePeriod", ""), x.get("LineNumber", "")))
        try: v = float(str(lt.get("DataValue", "")).replace(",", ""))
        except ValueError: v = None
        return {"status": "CONNECTED", "source": "BEA API", "url": url, "value": v,
                "date": lt.get("TimePeriod", "—"), "detail": f"استخراج: {lt.get('LineDescription','')}."}
    except Exception as exc:
        return {"status": classify_exception(exc), "source": "BEA API", "url": url,
                "detail": f"خطأ: {type(exc).__name__}.", "value": None, "date": "—"}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bea(key: str):
    r = _bea_impl(key); r["tested_at"] = now_utc_text(); return r

# ================================================================
# CFTC COT — Legacy + Disaggregated
# ================================================================
CFTC_LEGACY = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
CFTC_DISAGG = "https://publicreporting.cftc.gov/resource/kh3c-gbw2.json"
GOLD_CODE = "088691"

def _cot_legacy_impl():
    try:
        r = request_get(CFTC_LEGACY, params={"$where": f"cftc_contract_market_code='{GOLD_CODE}'",
                                             "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 12})
        if r.status_code == 429: return {"status": "RATE LIMITED", "rows": [], "source": "CFTC Legacy", "url": CFTC_LEGACY, "detail": "HTTP 429."}
        r.raise_for_status()
        raw = r.json()
        if not raw: return {"status": "NO DATA", "rows": [], "source": "CFTC Legacy", "url": CFTC_LEGACY, "detail": "لا صفوف."}
        req = ("noncomm_positions_long_all", "noncomm_positions_short_all",
               "open_interest_all", "report_date_as_yyyy_mm_dd")
        rows = []
        for x in raw:
            if not all(k in x for k in req): continue
            try: l = float(x["noncomm_positions_long_all"]); s = float(x["noncomm_positions_short_all"]); oi = float(x["open_interest_all"])
            except (TypeError, ValueError): continue
            rows.append({"date": str(x["report_date_as_yyyy_mm_dd"])[:10],
                         "long": l, "short": s, "net": l-s, "open_interest": oi,
                         "market": x.get("market_and_exchange_names", "")})
        if not rows: return {"status": "NO DATA", "rows": [], "source": "CFTC Legacy", "url": CFTC_LEGACY, "detail": "حقول مفقودة."}
        rows.sort(key=lambda z: z["date"], reverse=True)
        lt = rows[0]; pv = rows[1] if len(rows) > 1 else None
        lt["net_change_wow"] = (lt["net"] - pv["net"]) if pv else None
        lt["oi_change_wow"] = (lt["open_interest"] - pv["open_interest"]) if pv else None
        fr = assess_freshness(lt["date"], "weekly")
        return {"status": "CONNECTED" if fr["usable"] else "STALE",
                "rows": rows, "latest": lt, "source": "CFTC Legacy",
                "url": CFTC_LEGACY, "freshness_detail": fr["detail"],
                "detail": f"آخر تقرير {lt['date']} • {fr['detail']}"}
    except Exception as exc:
        return {"status": classify_exception(exc), "rows": [], "source": "CFTC Legacy", "url": CFTC_LEGACY, "detail": f"خطأ: {type(exc).__name__}."}

def _cot_disagg_impl():
    try:
        r = request_get(CFTC_DISAGG, params={"$where": f"cftc_contract_market_code='{GOLD_CODE}'",
                                             "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 12})
        if r.status_code == 429: return {"status": "RATE LIMITED", "rows": [], "source": "CFTC Disaggregated", "url": CFTC_DISAGG, "detail": "HTTP 429."}
        r.raise_for_status()
        raw = r.json()
        if not raw: return {"status": "NO DATA", "rows": [], "source": "CFTC Disaggregated", "url": CFTC_DISAGG, "detail": "لا صفوف."}
        req = ("prod_merc_positions_long", "prod_merc_positions_short",
               "swap_positions_long_all", "swap__positions_short_all",
               "m_money_positions_long_all", "m_money_positions_short_all",
               "open_interest_all", "report_date_as_yyyy_mm_dd")
        rows = []
        for x in raw:
            if not all(k in x for k in req): continue
            try:
                pml = float(x["prod_merc_positions_long"]); pms = float(x["prod_merc_positions_short"])
                swl = float(x["swap_positions_long_all"]); sws = float(x["swap__positions_short_all"])
                mml = float(x["m_money_positions_long_all"]); mms = float(x["m_money_positions_short_all"])
                oi = float(x["open_interest_all"])
            except (TypeError, ValueError): continue
            rows.append({"date": str(x["report_date_as_yyyy_mm_dd"])[:10],
                         "prod_merc_net": pml-pms, "swap_net": swl-sws,
                         "managed_money_net": mml-mms, "managed_money_long": mml,
                         "managed_money_short": mms, "open_interest": oi,
                         "market": x.get("market_and_exchange_names", "")})
        if not rows: return {"status": "NO DATA", "rows": [], "source": "CFTC Disaggregated", "url": CFTC_DISAGG, "detail": "حقول مفقودة."}
        rows.sort(key=lambda z: z["date"], reverse=True)
        lt = rows[0]; pv = rows[1] if len(rows) > 1 else None
        for k in ("managed_money_net", "swap_net", "open_interest"):
            lt[f"{k}_change_wow"] = (lt[k] - pv[k]) if pv else None
        fr = assess_freshness(lt["date"], "weekly")
        return {"status": "CONNECTED" if fr["usable"] else "STALE",
                "rows": rows, "latest": lt, "source": "CFTC Disaggregated (Combined)",
                "url": CFTC_DISAGG, "freshness_detail": fr["detail"],
                "detail": f"آخر تقرير {lt['date']} • {fr['detail']}"}
    except Exception as exc:
        return {"status": classify_exception(exc), "rows": [], "source": "CFTC Disaggregated", "url": CFTC_DISAGG, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=7200, show_spinner=False)
def fetch_cot_legacy():
    r = _cot_legacy_impl(); r["tested_at"] = now_utc_text(); return r

@st.cache_data(ttl=7200, show_spinner=False)
def fetch_cot_disagg():
    r = _cot_disagg_impl(); r["tested_at"] = now_utc_text(); return r

# ================================================================
# GOLD MULTI-SOURCE (Yahoo GC=F primary, gold-api fallback)
# ================================================================
def _goldapi_impl():
    url = "https://api.gold-api.com/price/XAU"
    try:
        r = request_get(url); r.raise_for_status()
        d = r.json(); p = d.get("price"); up = d.get("updatedAt", "")
        if p is None: return {"status": "NO DATA", "value": None, "source": "gold-api", "url": url, "detail": "لا سعر."}
        fr = assess_freshness(up or datetime.now(timezone.utc), "intraday")
        return {"status": "CONNECTED" if fr["usable"] else "STALE", "value": float(p),
                "source": "gold-api.com", "url": url,
                "observation_date": (up or "")[:10] or "—",
                "timestamp": up or "—", "freshness_detail": fr["detail"],
                "detail": f"gold-api • {fr['detail']}"}
    except Exception as exc:
        return {"status": classify_exception(exc), "value": None, "source": "gold-api", "url": url, "detail": f"خطأ: {type(exc).__name__}."}

@st.cache_data(ttl=120, show_spinner=False)
def fetch_gold_multi():
    yahoo = _yahoo_quote_impl(("GC=F",), "GOLD")
    goldapi = _goldapi_impl()
    candidates = [("yahoo_gcf", yahoo), ("gold-api", goldapi)]
    for n, c in candidates:
        if c.get("status") == "CONNECTED":
            c["verified_by"] = n
            c["all_sources"] = {k: {"status": v.get("status"), "value": v.get("value")} for k, v in candidates}
            c["tested_at"] = now_utc_text(); return c
    for n, c in candidates:
        if c.get("status") == "STALE":
            c["verified_by"] = n
            c["all_sources"] = {k: {"status": v.get("status"), "value": v.get("value")} for k, v in candidates}
            c["tested_at"] = now_utc_text(); return c
    return {"status": "UNAVAILABLE", "value": None, "source": "multi (all failed)",
            "detail": " | ".join(f"{n}: {c.get('detail', '—')}" for n, c in candidates),
            "all_sources": {k: {"status": v.get("status"), "value": v.get("value")} for k, v in candidates},
            "tested_at": now_utc_text()}

# ================================================================
# CROSS-SOURCE CONSISTENCY
# ================================================================
CONSISTENCY_THRESHOLDS = {"gold": 0.5, "nominal_10y": 0.05, "real_10y": 0.05, "breakeven_10y": 0.10}

def check_consistency(label, va, vb, sa, sb, th, is_pct=True):
    out = {"metric": label, "source_a": sa, "source_b": sb, "value_a": va, "value_b": vb,
           "consistent": None, "diff": None, "diff_pct": None, "threshold": th, "detail": ""}
    if va is None or vb is None:
        out["detail"] = "مصدر واحد أو أكثر غير متاح."; return out
    d = abs(va - vb)
    base = max(abs(va), abs(vb), 1e-9)
    dp = (d / base * 100) if is_pct else d
    out["diff"] = round(d, 4); out["diff_pct"] = round(dp, 3)
    if dp <= th:
        out["consistent"] = True; out["detail"] = f"✅ متسق ({dp:.3f}%، الحد {th}%)."
    else:
        out["consistent"] = False; out["detail"] = f"🚨 عدم اتساق ({dp:.3f}% > {th}%)."
    return out

def run_consistency(market):
    checks = []
    checks.append(check_consistency("الذهب (GC=F vs gold-api)",
                                    market.get("gold", {}).get("value"),
                                    _goldapi_impl().get("value"),
                                    "Yahoo GC=F", "gold-api", CONSISTENCY_THRESHOLDS["gold"]))
    nom_t = market.get("nominal", {}).get("values", {}).get("10Y")
    nom_f = market.get("fred", {}).get("DGS10", {}).get("value")
    checks.append(check_consistency("العائد الاسمي 10Y", nom_t, nom_f, "Treasury", "FRED DGS10",
                                    CONSISTENCY_THRESHOLDS["nominal_10y"], is_pct=False))
    real_f = market.get("fred", {}).get("DFII10", {}).get("value")
    checks.append(check_consistency("العائد الحقيقي 10Y", real_f,
                                    market.get("treasury_real", {}).get("values", {}).get("10Y"),
                                    "FRED DFII10", "Treasury Real",
                                    CONSISTENCY_THRESHOLDS["real_10y"], is_pct=False))
    be_calc = (nom_f - real_f) if (nom_f is not None and real_f is not None) else None
    checks.append(check_consistency("Breakeven 10Y", be_calc,
                                    market.get("fred", {}).get("T10YIE", {}).get("value"),
                                    "محسوب", "FRED T10YIE",
                                    CONSISTENCY_THRESHOLDS["breakeven_10y"], is_pct=False))
    return checks

# ================================================================
# CONSENSUS (يدوي أساسًا)
# ================================================================
if "manual_consensus" not in st.session_state:
    st.session_state.manual_consensus = {}

def analyze_consensus(events):
    out = {"signals": [], "bias": "NEUTRAL", "confidence": 0}
    for e in events:
        act, cons = e.get("actual"), e.get("consensus")
        if act is None or cons is None: continue
        try: act, cons = float(act), float(cons)
        except (TypeError, ValueError): continue
        ev = e.get("event", "?"); diff = act - cons
        if abs(diff) < 1e-6:
            out["signals"].append(f"⬜ {ev}: مطابق للمتوقع"); continue
        d = "أعلى" if diff > 0 else "أقل"
        out["signals"].append(f"📊 {ev}: {act} ({d} من {cons})")
        if any(k in ev for k in ("CPI", "PCE")):
            out["bias"] = "BEARISH_GOLD" if diff > 0 else "BULLISH_GOLD"
            out["confidence"] += 15
        if any(k in ev for k in ("Nonfarm", "Payrolls")):
            out["bias"] = "BEARISH_GOLD" if diff > 0 else "BULLISH_GOLD"
            out["confidence"] += 10
    out["confidence"] = min(out["confidence"], 60); return out

# ================================================================
# QUALITY SCORE
# ================================================================
def source_quality_score(src):
    s = 0.0
    st_ = src.get("status")
    if st_ == "CONNECTED": s += 40
    elif st_ == "STALE": s += 20
    if src.get("value") is not None or src.get("rows") or src.get("series"): s += 25
    if src.get("freshness_detail") is not None: s += 20
    if any(k in (src.get("source") or "") for k in ("Treasury", "FRED", "CFTC", "BLS", "BEA", "official")): s += 15
    return min(s, 100.0)

def aggregate_quality(market):
    srcs = [market.get("gold", {}), market.get("dxy", {}), market.get("nominal", {}),
            market.get("real_yield", {}), market.get("cot_disagg", {}),
            market.get("bls", {}), market.get("bea", {})]
    ws = [25, 10, 15, 10, 20, 10, 10]
    total = sum(w * source_quality_score(s) / 100 for s, w in zip(srcs, ws))
    return round(total)

# ================================================================
# ECONOMIC ANALYSIS
# ================================================================
def analyze_economics(market):
    out = {"bias": "NEUTRAL", "confidence": 0, "signals": [], "warnings": []}
    bls = market.get("bls", {}).get("series", {}); fred = market.get("fred", {})
    cpi = bls.get("headline_cpi", {}); core = bls.get("core_cpi", {})
    if cpi.get("yoy_pct") is not None:
        if cpi["yoy_pct"] > 3.0:
            out["signals"].append(f"تضخم مرتفع ({cpi['yoy_pct']}% سنويًا) → ضغط على الذهب")
            out["bias"] = "BEARISH_GOLD"; out["confidence"] += 15
        elif cpi["yoy_pct"] < 2.0:
            out["signals"].append(f"تضخم منخفض ({cpi['yoy_pct']}%) → دعم للذهب")
            out["bias"] = "BULLISH_GOLD"; out["confidence"] += 15
        else: out["signals"].append(f"تضخم معتدل ({cpi['yoy_pct']}%)")
    if core.get("yoy_pct") is not None: out["signals"].append(f"Core CPI: {core['yoy_pct']}% سنويًا")
    une = bls.get("unemployment", {})
    if une.get("level") is not None:
        if une["level"] > 4.5:
            out["signals"].append(f"بطالة مرتفعة ({une['level']}%) → دعم"); out["confidence"] += 10
        elif une["level"] < 3.8:
            out["signals"].append(f"بطالة منخفضة ({une['level']}%) → ضغط"); out["confidence"] += 10
    nfp = bls.get("nonfarm_payrolls", {})
    if nfp.get("level") is not None: out["signals"].append(f"الوظائف: {nfp['level']:,.0f} ألف")
    r10 = fred.get("DFII10", {}).get("value")
    if r10 is not None:
        if r10 > 2.0:
            out["signals"].append(f"عائد حقيقي مرتفع ({r10}%) → ضغط"); out["bias"] = "BEARISH_GOLD"; out["confidence"] += 20
        elif r10 < 1.0:
            out["signals"].append(f"عائد حقيقي منخفض ({r10}%) → دعم"); out["bias"] = "BULLISH_GOLD"; out["confidence"] += 20
        else: out["signals"].append(f"عائد حقيقي معتدل ({r10}%)")
    be = fred.get("T10YIE", {}).get("value")
    if be is not None:
        if be > 2.5: out["signals"].append(f"تضخم متوقع مرتفع ({be}%) → دعم"); out["confidence"] += 10
        else: out["signals"].append(f"تضخم متوقع {be}%")
    out["confidence"] = min(out["confidence"], 100)
    if out["confidence"] < 25:
        out["bias"] = "NO_TRADE"; out["warnings"].append("بيانات اقتصادية غير كافية.")
    return out

# ================================================================
# FUSION
# ================================================================
def build_fusion(market, ohlc_res):
    econ = analyze_economics(market)
    smc = analyze_smc_ict_v2(ohlc_res)
    cot = market.get("cot_disagg", {}).get("latest", {})
    cot_bias = "NEUTRAL"; cot_signals = []
    if cot:
        mm = cot.get("managed_money_net", 0); chg = cot.get("managed_money_net_change_wow")
        if mm > 150_000: cot_bias = "BULLISH"; cot_signals.append(f"MM صافي طويل ({mm:,.0f})")
        elif mm < 50_000: cot_bias = "BEARISH"; cot_signals.append(f"MM صافي قصير/محايد ({mm:,.0f})")
        else: cot_signals.append(f"MM متوازن ({mm:,.0f})")
        if chg is not None: cot_signals.append(f"التغير الأسبوعي: {chg:+,.0f}")
    votes = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0}
    ws = {"econ": 0.35, "smc": 0.30, "cot": 0.25, "dxy": 0.10}
    eb = econ["bias"].replace("_GOLD", "")
    if eb in votes: votes[eb] += ws["econ"] * 100
    if smc["bias"] in votes: votes[smc["bias"]] += ws["smc"] * 100
    if cot_bias in votes: votes[cot_bias] += ws["cot"] * 100
    dxy = market.get("dxy", {})
    if dxy.get("change") is not None:
        votes["BULLISH" if dxy["change"] < 0 else "BEARISH"] += ws["dxy"] * 100
    fb = max(votes, key=votes.get); conf = votes[fb]
    reasons = []
    if econ["bias"] == "NO_TRADE": reasons.append("بيانات اقتصادية غير كافية")
    if smc["structure"] == "UNDEFINED": reasons.append("لا OHLC كافٍ")
    if market.get("quality_score", 0) < 40: reasons.append(f"جودة منخفضة ({market['quality_score']}/100)")
    if conf < 40: reasons.append(f"ثقة منخفضة ({conf:.0f}%)")
    return {"final_bias": "NO_TRADE" if reasons else fb,
            "confidence": round(conf, 1),
            "votes": {k: round(v, 1) for k, v in votes.items()},
            "econ": econ, "smc": smc, "cot_bias": cot_bias,
            "cot_signals": cot_signals, "no_trade_reasons": reasons}

# ================================================================
# TRADE VALIDATOR + RISK
# ================================================================
def validate_trade(trade, fusion, market):
    checks = []; ok = True; d = trade.get("direction", "LONG")
    e, sl, tp = trade.get("entry"), trade.get("stop_loss"), trade.get("take_profit")
    fb = fusion["final_bias"]
    if fb == "NO_TRADE": checks.append(("🔴", "الفيوجن NO TRADE", False)); ok = False
    elif fb == "BULLISH" and d == "SHORT": checks.append(("🟠", "اتجاه معاكس", False)); ok = False
    elif fb == "BEARISH" and d == "LONG": checks.append(("🟠", "اتجاه معاكس", False)); ok = False
    else: checks.append(("🟢", "الاتجاه متوافق", True))
    if all(x is not None for x in (e, sl, tp)):
        risk = abs(e - sl); rr = abs(tp - e) / risk if risk > 0 else 0
        if rr >= 2.0: checks.append(("🟢", f"R:R جيد ({rr:.2f})", True))
        elif rr >= 1.5: checks.append(("🟠", f"R:R مقبول ({rr:.2f})", True))
        else: checks.append(("🔴", f"R:R ضعيف ({rr:.2f})", False)); ok = False
    else: checks.append(("🟠", "مستويات ناقصة", False)); ok = False
    q = market.get("quality_score", 0)
    if q >= 70: checks.append(("🟢", f"جودة عالية ({q})", True))
    elif q >= 40: checks.append(("🟠", f"جودة متوسطة ({q})", True))
    else: checks.append(("🔴", f"جودة منخفضة ({q})", False)); ok = False
    if fusion["cot_bias"] != "NEUTRAL":
        aligned = (fusion["cot_bias"] == "BULLISH" and d == "LONG") or (fusion["cot_bias"] == "BEARISH" and d == "SHORT")
        checks.append(("🟢" if aligned else "🟠", "COT " + ("يدعم" if aligned else "معاكس"), aligned))
    return {"valid": ok, "checks": checks, "direction": d}

def calc_risk(bal, pct, e, sl, tp, cs=100.0):
    risk = bal * pct / 100; sld = abs(e - sl); tpd = abs(tp - e)
    if sld == 0: return {"error": "SL = Entry"}
    ps = risk / (sld * cs); rr = tpd / sld
    return {"risk_amount": round(risk, 2), "position_size_lots": round(ps, 4),
            "position_size_units": round(ps * cs, 2), "rr_ratio": round(rr, 2),
            "expected_profit": round(ps * tpd * cs, 2),
            "sl_distance": round(sld, 2), "tp_distance": round(tpd, 2)}

# ================================================================
# BACKTEST (with slippage)
# ================================================================
def backtest_smc_signals(df, atr_mult_sl=1.5, atr_mult_tp=3.0, lookback=20,
                         slippage_usd=0.5, max_bars: Optional[int] = None):
    if df is None or len(df) < 60: return {"status": "NO DATA", "detail": "OHLC غير كافٍ."}
    df = df.reset_index(drop=True).copy()
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()
    trades = []; pos = None
    for i in range(lookback + 5, len(df)):
        row = df.iloc[i]
        if pd.isna(row["atr"]) or row["atr"] <= 0: continue
        if pos is not None:
            hit_sl = (row["low"] <= pos["sl"]) if pos["dir"] == "LONG" else (row["high"] >= pos["sl"])
            hit_tp = (row["high"] >= pos["tp"]) if pos["dir"] == "LONG" else (row["low"] <= pos["tp"])
            bh = i - pos["entry_idx"]
            if hit_sl:
                pos["exit"] = pos["sl"] - slippage_usd if pos["dir"] == "LONG" else pos["sl"] + slippage_usd
                pos["result"] = -1.0; pos["bars"] = bh; trades.append(pos); pos = None
            elif hit_tp:
                pos["exit"] = pos["tp"] - slippage_usd if pos["dir"] == "LONG" else pos["tp"] + slippage_usd
                pos["result"] = atr_mult_tp / atr_mult_sl; pos["bars"] = bh; trades.append(pos); pos = None
            elif max_bars and bh >= max_bars:
                pnl_r = ((row["close"] - pos["entry"]) / (pos["entry"] - pos["sl"])) if pos["dir"] == "LONG" \
                        else ((pos["entry"] - row["close"]) / (pos["sl"] - pos["entry"]))
                pos["exit"] = float(row["close"]); pos["result"] = float(pnl_r); pos["bars"] = bh
                trades.append(pos); pos = None
            continue
        wh = df["high"].iloc[i-lookback:i].max(); wl = df["low"].iloc[i-lookback:i].min()
        price = row["close"]; atr = row["atr"]
        if price > wh:
            e = price + slippage_usd
            pos = {"entry_idx": i, "entry": float(e), "dir": "LONG",
                   "sl": float(e - atr_mult_sl * atr), "tp": float(e + atr_mult_tp * atr),
                   "entry_time": row["timestamp"]}
        elif price < wl:
            e = price - slippage_usd
            pos = {"entry_idx": i, "entry": float(e), "dir": "SHORT",
                   "sl": float(e + atr_mult_sl * atr), "tp": float(e - atr_mult_tp * atr),
                   "entry_time": row["timestamp"]}
    if not trades:
        return {"status": "OK", "trades": [], "total": 0, "wins": 0, "losses": 0,
                "win_rate": 0.0, "avg_r": 0.0, "expectancy_r": 0.0, "max_dd_r": 0.0,
                "detail": "لا صفقات."}
    res = [t["result"] for t in trades]
    w = sum(1 for r in res if r > 0); l = sum(1 for r in res if r <= 0)
    eq = np.cumsum(res); peak = np.maximum.accumulate(eq); dd = eq - peak
    return {"status": "OK", "trades": trades, "total": len(trades), "wins": w, "losses": l,
            "win_rate": round(w / len(trades) * 100, 1), "avg_r": round(sum(res) / len(res), 3),
            "expectancy_r": round(sum(res) / len(res), 3), "max_dd_r": round(float(dd.min()), 2),
            "detail": f"{len(trades)} صفقة عبر {len(df)} شمعة."}

# ================================================================
# MARKET DATA
# ================================================================
@st.cache_data(ttl=600, show_spinner=False)
def build_market_data():
    dxy = fetch_yahoo_quote(("DX-Y.NYB",), "DXY")
    gold = fetch_gold_multi()
    nominal = fetch_treasury_curve(False)
    real_curve = fetch_treasury_curve(True)
    cot_leg = fetch_cot_legacy()
    cot_dis = fetch_cot_disagg()
    bls = fetch_bls_v2(get_secret("BLS_API_KEY"))
    bea = fetch_bea(get_secret("BEA_API_KEY"))
    fred_key = get_secret("FRED_API_KEY")
    fred = {sid: fetch_fred_obs(sid, fred_key) for sid in FRED_SERIES_META} if fred_key else {}
    r10 = fred.get("DFII10", {}).get("value")
    if r10 is not None and fred.get("DFII10", {}).get("status") == "CONNECTED":
        real_yield = {"status": fred["DFII10"]["status"], "value": r10,
                      "date": fred["DFII10"]["date"], "source": "FRED DFII10",
                      "freshness_detail": fred["DFII10"].get("freshness_detail")}
    else:
        real_yield = {"status": real_curve["status"], "value": real_curve.get("values", {}).get("10Y"),
                      "date": real_curve.get("date", "—"), "source": real_curve["source"],
                      "freshness_detail": real_curve.get("freshness_detail")}
    be_v = fred.get("T10YIE", {}).get("value")
    m = {"gold": gold, "dxy": dxy, "nominal": nominal,
         "treasury_real": real_curve, "real_yield": real_yield,
         "breakeven": {"status": fred.get("T10YIE", {}).get("status", "NOT TESTED"), "value": be_v},
         "cot": cot_leg, "cot_disagg": cot_dis, "bls": bls, "bea": bea, "fred": fred,
         "tested_at": now_utc_text()}
    m["quality_score"] = aggregate_quality(m)
    return m

# ================================================================
# AUTH GATE
# ================================================================
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user" not in st.session_state: st.session_state.user = None

users = _get_users()
if users and not st.session_state.authenticated:
    st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>تسجيل الدخول</h1></div>', unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة المرور", type="password")
        ok = st.form_submit_button("دخول")
    if ok:
        s = _verify_credentials(u, p)
        if s:
            st.session_state.authenticated = True; st.session_state.user = s
            log_action("auth", "login_success")
            st.rerun()
        else:
            st.error("بيانات غير صحيحة.")
    st.stop()

current_user = st.session_state.user or {"username": "local", "role": "admin"}
current_role = current_user["role"]

# ================================================================
# SESSION STATE
# ================================================================
for k, v in {"manual_gold_price": None, "trade_journal": [], "report_history": [],
             "current_report": None, "seen_observations": {}}.items():
    if k not in st.session_state: st.session_state[k] = v

# ================================================================
# LOAD DATA
# ================================================================
with st.spinner("⏳ تحميل البيانات..."):
    market_data = build_market_data()
with st.spinner("⏳ تحميل OHLC..."):
    ohlc_res = fetch_gold_ohlc("6mo", "1d")

# ================================================================
# UPDATE NOTIFICATIONS
# ================================================================
def detect_new(market):
    alerts = []
    pairs = [("COT Disaggregated", market.get("cot_disagg", {}).get("latest", {}).get("date")),
             ("COT Legacy", market.get("cot", {}).get("latest", {}).get("date")),
             ("BLS CPI", market.get("bls", {}).get("series", {}).get("headline_cpi", {}).get("date")),
             ("BLS NFP", market.get("bls", {}).get("series", {}).get("nonfarm_payrolls", {}).get("date")),
             ("Treasury 10Y", market.get("nominal", {}).get("date")),
             ("FRED DGS10", market.get("fred", {}).get("DGS10", {}).get("date"))]
    seen = st.session_state.seen_observations
    for name, obs in pairs:
        if not obs or obs == "—": continue
        if seen.get(name) != obs:
            alerts.append({"source": name, "old": seen.get(name, "—"), "new": obs, "is_first": name not in seen})
            seen[name] = obs
    return alerts

new_alerts = detect_new(market_data)

# ================================================================
# SIDEBAR + RBAC
# ================================================================
NAV_ITEMS = [
    ("🔥 MAIN DASHBOARD", {"admin", "analyst", "viewer", "auditor"}),
    ("📊 DATA SOURCES", {"admin", "analyst", "viewer", "auditor"}),
    ("📅 ECONOMIC CALENDAR", {"admin", "analyst", "viewer", "auditor"}),
    ("📈 ECONOMIC ANALYSIS", {"admin", "analyst", "viewer", "auditor"}),
    ("💵 YIELDS & DOLLAR", {"admin", "analyst", "viewer", "auditor"}),
    ("📋 COT & OI", {"admin", "analyst", "viewer", "auditor"}),
    ("🧠 SMC/ICT", {"admin", "analyst", "auditor"}),
    ("📉 TECHNICAL INDICATORS", {"admin", "analyst", "auditor"}),
    ("🔗 CONSISTENCY", {"admin", "analyst", "viewer", "auditor"}),
    ("🔍 EVIDENCE MATRIX", {"admin", "analyst", "auditor"}),
    ("✅ TRADE VALIDATOR", {"admin", "analyst", "auditor"}),
    ("🛡️ RISK MANAGEMENT", {"admin", "analyst", "auditor"}),
    ("🧪 BACKTESTING", {"admin", "analyst", "auditor"}),
    ("📄 WEEKLY REPORT", {"admin", "analyst"}),
    ("📜 REPORT HISTORY", {"admin", "analyst", "auditor"}),
    ("📓 TRADING JOURNAL", {"admin", "analyst", "auditor"}),
    ("🔎 AUDIT LOG", {"admin", "auditor"}),
    ("⚙️ ADMIN", {"admin"}),
]

def allowed_nav(role):
    return [n for n, roles in NAV_ITEMS if role in roles]

def can_export(): return current_role in {"admin", "analyst"}
def can_modify(): return current_role in {"admin", "analyst"}

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">TERMINAL v16</div></div></div>', unsafe_allow_html=True)
    nav_items = allowed_nav(current_role)
    navigation = st.radio("القائمة", nav_items, label_visibility="collapsed")
    role_label = {"admin": "🔑 مدير", "analyst": "📊 محلل",
                  "auditor": "🔍 مدقق", "viewer": "👁️ قارئ"}.get(current_role, current_role)
    st.caption(f"**{current_user['username']}** • {role_label}")
    if st.button("🚪 تسجيل الخروج"):
        log_action("auth", "logout")
        st.session_state.authenticated = False; st.session_state.user = None; st.rerun()
    st.divider()
    if st.button("↻ تحديث البيانات"):
        st.cache_data.clear(); st.rerun()
    st.caption(f"آخر تحديث: {market_data['tested_at']}")

# ================================================================
# ACTIVE GOLD
# ================================================================
if st.session_state.manual_gold_price is not None:
    active_gold = float(st.session_state.manual_gold_price)
else:
    active_gold = safe_float(market_data["gold"].get("value"))

# ================================================================
# UPDATE BANNER
# ================================================================
fresh_alerts = [a for a in new_alerts if not a["is_first"]]
if fresh_alerts:
    st.markdown('<div class="warning-box">🔔 <b>بيانات جديدة منذ آخر زيارة:</b><br>' +
                "<br>".join(f"• {a['source']}: {a['old']} → {a['new']}" for a in fresh_alerts) +
                '</div>', unsafe_allow_html=True)

# ================================================================
# PAGES
# ================================================================
def page_dashboard():
    st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>لوحة القرار الموحد</h1></div>', unsafe_allow_html=True)
    cols = st.columns(6)
    cols[0].metric("XAUUSD", fmt_number(active_gold, 2, " $") if active_gold else "—")
    cols[1].metric("DXY", fmt_number(market_data["dxy"].get("value"), 2))
    cols[2].metric("US 10Y", fmt_number(market_data["nominal"].get("values", {}).get("10Y"), 3, "%"))
    cols[3].metric("Real 10Y", fmt_number(market_data.get("real_yield", {}).get("value"), 3, "%"))
    cols[4].metric("Breakeven", fmt_number(market_data.get("breakeven", {}).get("value"), 2, "%"))
    cols[5].metric("جودة", f"{market_data['quality_score']}/100")

    fusion = build_fusion(market_data, ohlc_res)
    fb = fusion["final_bias"]
    card = {"BULLISH": ("signal-bull", "🟢", "تحيز صاعد"),
            "BEARISH": ("signal-bear", "🔴", "تحيز هابط"),
            "NO_TRADE": ("signal-no-trade", "⛔", "لا تداول"),
            }.get(fb, ("signal-neutral", "🟡", "حياد"))
    st.markdown(f'<div class="{card[0]}"><h3 style="margin:0 0 8px;">{card[1]} {card[2]} (ثقة: {fusion["confidence"]}%)</h3>' +
                ("<p style='color:#ff8a8a;'>" + " • ".join(fusion["no_trade_reasons"]) + "</p>" if fusion["no_trade_reasons"] else "") +
                '</div>', unsafe_allow_html=True)

    v = fusion["votes"]; vc = st.columns(3)
    vc[0].metric("صاعد", f"{v.get('BULLISH', 0):.0f}%")
    vc[1].metric("هابط", f"{v.get('BEARISH', 0):.0f}%")
    vc[2].metric("حياد", f"{v.get('NEUTRAL', 0):.0f}%")

    st.markdown("### 🎯 السيناريوهات")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="fusion-card"><h4>صاعد</h4><p>• اختراق PDH<br>• تراجع العائد الحقيقي<br>• MM Net متزايد<br><b>تأكيد:</b> إغلاق 4H فوق PDH<br><b>إبطال:</b> عودة تحته</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="fusion-card"><h4>هابط</h4><p>• كسر PDL<br>• ارتفاع العائد الحقيقي<br>• MM Net متراجع<br><b>تأكيد:</b> إغلاق 4H تحت PDL<br><b>إبطال:</b> عودة فوقه</p></div>', unsafe_allow_html=True)

def page_data_sources():
    st.markdown("## 📊 تدقيق مصادر البيانات")
    rows = []
    for name, src, req in [("الذهب", market_data["gold"], "XAUUSD (GC=F)"),
                           ("الدولار", market_data["dxy"], "DXY"),
                           ("العائد الاسمي", market_data["nominal"], "Treasury"),
                           ("العائد الحقيقي", market_data["real_yield"], "Real 10Y"),
                           ("COT Legacy", market_data["cot"], "Legacy"),
                           ("COT Disaggregated", market_data["cot_disagg"], "Managed Money"),
                           ("BLS", market_data["bls"], "CPI/Jobs"),
                           ("BEA", market_data["bea"], "GDP/NIPA")]:
        rows.append({"المصدر": name, "المطلوب": req,
                     "الحالة": display_status(src.get("status", "NO DATA")),
                     "القيمة": fmt_number(src.get("value"), 2) if src.get("value") is not None else "—",
                     "تاريخ": src.get("observation_date", src.get("date", "—")),
                     "حداثة": src.get("freshness_detail", "—"),
                     "جودة": f"{round(source_quality_score(src), 1)}/100",
                     "التفصيل": src.get("detail", "—")})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.metric("الجودة الإجمالية", f"{market_data['quality_score']}/100")

def page_calendar():
    st.markdown("## 📅 الأجندة الاقتصادية")
    cal = build_news_calendar(get_secret("FRED_API_KEY"))
    if cal.empty:
        st.warning("لا أجندة — تحقق من FRED_API_KEY.")
    else:
        st.dataframe(cal, use_container_width=True, hide_index=True)

    st.markdown("### 📝 Consensus يدوي")
    with st.form("cons_form"):
        c1, c2, c3, c4 = st.columns(4)
        ev = c1.text_input("الحدث")
        co = c2.number_input("المتوقع", value=0.0)
        pv = c3.number_input("السابق", value=0.0)
        ac = c4.number_input("الفعلي", value=0.0)
        if st.form_submit_button("💾 حفظ") and ev:
            st.session_state.manual_consensus[ev] = {"event": ev, "consensus": co, "previous": pv,
                                                      "actual": ac if ac != 0 else None}
            log_action("manual_input", "add_consensus", new_value=ev)
            st.success("تم.")

    if st.session_state.manual_consensus:
        analysis = analyze_consensus(list(st.session_state.manual_consensus.values()))
        for s in analysis["signals"]: st.markdown(f"- {s}")
        st.markdown(f"**التحيز:** {analysis['bias']} • **الثقة:** {analysis['confidence']}%")

def page_econ():
    st.markdown("## 📈 التحليل الاقتصادي")
    econ = analyze_economics(market_data)
    st.markdown(f"**التحيز:** {econ['bias']} • **الثقة:** {econ['confidence']}%")
    bls = market_data.get("bls", {}).get("series", {})
    if bls:
        rows = [{"المؤشر": s.get("label", k), "المستوى": fmt_number(s.get("level"), 2),
                 "MoM %": fmt_number(s.get("mom_pct"), 2),
                 "YoY %": fmt_number(s.get("yoy_pct"), 2),
                 "التاريخ": s.get("date", "—"),
                 "الحالة": display_status(s.get("status", "NO DATA"))} for k, s in bls.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    fred = market_data.get("fred", {})
    if fred:
        rows = [{"السلسلة": k, "الوصف": v.get("label", k), "القيمة": fmt_number(v.get("value"), 3),
                 "التاريخ": v.get("date", "—")} for k, v in fred.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    for s in econ["signals"]: st.markdown(f"- {s}")

def page_yields():
    st.markdown("## 💵 العوائد والدولار")
    vals = market_data.get("nominal", {}).get("values", {})
    if vals:
        cols = st.columns(len(vals))
        for i, (k, v) in enumerate(sorted(vals.items())): cols[i].metric(k, fmt_number(v, 3, "%"))
    st.metric("Real 10Y", fmt_number(market_data.get("real_yield", {}).get("value"), 3, "%"))
    st.metric("Breakeven", fmt_number(market_data.get("breakeven", {}).get("value"), 2, "%"))
    dxy = market_data.get("dxy", {})
    dc = st.columns(3)
    dc[0].metric("DXY", fmt_number(dxy.get("value"), 2))
    dc[1].metric("التغير", f"{dxy.get('change', 0):+.2f}" if dxy.get("change") else "—")
    dc[2].metric("آخر تحديث", dxy.get("timestamp", "—"))

def page_cot():
    st.markdown("## 📋 COT & Open Interest")
    cot_d = market_data.get("cot_disagg", {})
    lt = cot_d.get("latest", {})
    if lt:
        st.markdown(f"### Managed Money — {lt.get('date', '—')}")
        cc = st.columns(4)
        cc[0].metric("MM Net", f"{lt['managed_money_net']:,.0f}")
        chg = lt.get("managed_money_net_change_wow")
        cc[1].metric("التغير", f"{chg:+,.0f}" if chg is not None else "—")
        cc[2].metric("Swap Net", f"{lt['swap_net']:,.0f}")
        cc[3].metric("OI", f"{lt['open_interest']:,.0f}")
        mm = lt["managed_money_net"]
        if mm > 150_000: st.success(f"MM صافي طويل بقوة ({mm:,.0f}).")
        elif mm < 50_000: st.info(f"MM محايد/قصير ({mm:,.0f}).")
        else: st.warning(f"MM في منطقة انتقالية ({mm:,.0f}).")
        hist = pd.DataFrame(cot_d.get("rows", []))[["date", "managed_money_net", "swap_net", "open_interest"]]
        hist.columns = ["التاريخ", "MM Net", "Swap Net", "OI"]
        st.dataframe(hist, use_container_width=True, hide_index=True)
    else:
        st.warning("بيانات COT Disaggregated غير متاحة.")

    with st.expander("📜 COT Legacy"):
        cot = market_data.get("cot", {}); ll = cot.get("latest", {})
        if ll:
            cc = st.columns(4)
            cc[0].metric("Long", f"{ll['long']:,.0f}"); cc[1].metric("Short", f"{ll['short']:,.0f}")
            cc[2].metric("Net", f"{ll['net']:,.0f}"); cc[3].metric("OI", f"{ll['open_interest']:,.0f}")
            hist = pd.DataFrame(cot.get("rows", []))[["date", "long", "short", "net", "open_interest"]]
            hist.columns = ["التاريخ", "Long", "Short", "Net", "OI"]
            st.dataframe(hist, use_container_width=True, hide_index=True)

def page_smc():
    st.markdown("## 🧠 SMC/ICT")
    smc = analyze_smc_ict_v2(ohlc_res)
    st.markdown(f"**البنية:** {smc['structure']} • **التحيز:** {smc['bias']}")
    if smc["pdh"]: st.markdown(f"PDH: {smc['pdh']:.2f} • PDL: {smc['pdl']:.2f} • ATR: {smc['atr']:.2f}")
    for s in smc["signals"]: st.markdown(f"- {s}")
    for s in smc["sweeps"]: st.warning(s["detail"])

def page_tech():
    st.markdown("## 📉 المؤشرات الفنية")
    df = ohlc_res.get("df")
    if df is None: st.error("OHLC غير متاح."); return
    ind = compute_indicators(df)
    if ind.get("status") != "OK": st.warning(ind.get("detail")); return
    c = st.columns(4)
    c[0].metric("ATR(14)", f"${ind['atr14']:.2f}")
    c[1].metric("Vol20", f"{ind['vol20']:.1f}%")
    c[2].metric("Vol60", f"{ind['vol60']:.1f}%")
    c[3].metric("اتجاه", ind["trend"])
    c = st.columns(3)
    c[0].metric("BB Upper", f"${ind['bb_upper']:.2f}")
    c[1].metric("BB Mid", f"${ind['bb_mid']:.2f}")
    c[2].metric("BB Lower", f"${ind['bb_lower']:.2f}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**دعوم**")
        for s in ind["supports"]: st.markdown(f"- ${s:,.2f}")
    with c2:
        st.markdown("**مقاومات**")
        for r in ind["resistances"]: st.markdown(f"- ${r:,.2f}")

def page_consistency():
    st.markdown("## 🔗 الاتساق بين المصادر")
    checks = run_consistency(market_data)
    rows = []
    for c in checks:
        flag = "🟢" if c["consistent"] else ("🔴" if c["consistent"] is False else "⚪")
        rows.append({"المقياس": c["metric"], "A": f"{c['source_a']}={fmt_number(c['value_a'], 4)}",
                     "B": f"{c['source_b']}={fmt_number(c['value_b'], 4)}",
                     "فرق%": fmt_number(c["diff_pct"], 3), "الحد": c["threshold"],
                     "الحالة": flag, "التفصيل": c["detail"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def page_evidence():
    st.markdown("## 🔍 مصفوفة الأدلة")
    fusion = build_fusion(market_data, ohlc_res)
    evidence = []
    for e in fusion["econ"]["signals"]: evidence.append({"الفئة": "اقتصادي", "الدليل": e, "الاتجاه": fusion["econ"]["bias"]})
    for e in fusion["smc"]["signals"]: evidence.append({"الفئة": "SMC/ICT", "الدليل": e, "الاتجاه": fusion["smc"]["bias"]})
    for e in fusion["cot_signals"]: evidence.append({"الفئة": "COT", "الدليل": e, "الاتجاه": fusion["cot_bias"]})
    if evidence: st.dataframe(pd.DataFrame(evidence), use_container_width=True, hide_index=True)
    st.markdown(f"**القرار:** {fusion['final_bias']} • **الثقة:** {fusion['confidence']}%")

def page_validator():
    st.markdown("## ✅ فاحص الصفقات")
    fusion = build_fusion(market_data, ohlc_res)
    with st.form("trade_form"):
        d = st.selectbox("الاتجاه", ["LONG", "SHORT"])
        e = st.number_input("الدخول", value=0.0)
        sl = st.number_input("SL", value=0.0)
        tp = st.number_input("TP", value=0.0)
        if st.form_submit_button("🔍 فحص"):
            r = validate_trade({"direction": d, "entry": e, "stop_loss": sl, "take_profit": tp},
                               fusion, market_data)
            st.success("✅ يجتاز") if r["valid"] else st.error("🔴 لا يجتاز")
            for ic, msg, _ in r["checks"]: st.markdown(f"{ic} {msg}")

def page_risk():
    st.markdown("## 🛡️ حاسبة المخاطر")
    with st.form("risk_form"):
        c1, c2 = st.columns(2)
        bal = c1.number_input("الرصيد ($)", value=10000.0)
        rp = c1.number_input("المخاطرة %", value=1.0, min_value=0.1, max_value=10.0)
        e = c1.number_input("الدخول", value=0.0)
        sl = c2.number_input("SL", value=0.0)
        tp = c2.number_input("TP", value=0.0)
        cs = c2.number_input("حجم العقد", value=100.0)
        if st.form_submit_button("📊 حساب"):
            r = calc_risk(bal, rp, e, sl, tp, cs)
            if "error" in r: st.error(r["error"])
            else:
                st.metric("مخاطرة", f"${r['risk_amount']:,.2f}")
                c = st.columns(3)
                c[0].metric("حجم (لوت)", f"{r['position_size_lots']:.4f}")
                c[1].metric("R:R", f"{r['rr_ratio']:.2f}")
                c[2].metric("ربح", f"${r['expected_profit']:,.2f}")

def page_backtest():
    st.markdown("## 🧪 Backtesting")
    st.markdown('<div class="warning-box">⚠️ إشارات سعرية فقط (BOS+ATR) مع slippage 0.5$. لا يشمل COT/عوائد/أخبار.</div>', unsafe_allow_html=True)
    c = st.columns(3)
    r = c[0].selectbox("الفترة", ["1y", "2y", "5y", "max"], index=1)
    slm = c[1].slider("ATR SL ×", 0.5, 3.0, 1.5, 0.1)
    tpm = c[2].slider("ATR TP ×", 1.0, 6.0, 3.0, 0.1)
    max_b = st.slider("حد أقصى للصفقة (شمعة) — 0 = مفتوح", 0, 200, 0, 10)
    mb = None if max_b == 0 else max_b
    if st.button("▶️ تشغيل"):
        with st.spinner("جاري..."):
            o = fetch_gold_ohlc(r, "1d")
        if o.get("df") is None: st.error("OHLC غير كافٍ."); return
        res = backtest_smc_signals(o["df"], slm, tpm, 20, 0.5, mb)
        m = st.columns(5)
        m[0].metric("صفقات", res["total"])
        m[1].metric("ربح%", f"{res['win_rate']}%")
        m[2].metric("Avg R", f"{res['avg_r']:+.2f}")
        m[3].metric("Expectancy", f"{res['expectancy_r']:+.2f}R")
        m[4].metric("Max DD", f"{res['max_dd_r']:.1f}R")
        if res["trades"]:
            t = pd.DataFrame(res["trades"])[["entry_time", "dir", "entry", "sl", "tp", "exit", "result", "bars"]]
            t.columns = ["الوقت", "الاتجاه", "الدخول", "SL", "TP", "الخروج", "R", "شمعات"]
            st.dataframe(t.tail(50), use_container_width=True, hide_index=True)

def generate_weekly_report(market):
    fusion = build_fusion(market, ohlc_res)
    now = now_utc_text()
    md = [f"# 📊 تقرير YUNAN GOLD الأسبوعي", f"**التوليد:** {now}",
          f"**المستخدم:** {current_user['username']} ({current_role})", "", "---", "",
          "## 1️⃣ الأسعار"]
    md.append(f"- **XAUUSD:** {fmt_number(market['gold'].get('value'), 2, ' $')}")
    md.append(f"- **DXY:** {fmt_number(market['dxy'].get('value'), 2)}")
    md.append(f"- **US 10Y:** {fmt_number(market['nominal'].get('values', {}).get('10Y'), 3, '%')}")
    md.append(f"- **Real 10Y:** {fmt_number(market.get('real_yield', {}).get('value'), 3, '%')}")
    md.append(f"- **Breakeven:** {fmt_number(market.get('breakeven', {}).get('value'), 2, '%')}")
    md.append(""); md.append("## 2️⃣ COT Disaggregated")
    cd = market.get("cot_disagg", {}).get("latest", {})
    if cd:
        md.append(f"- **MM Net:** {cd.get('managed_money_net', 0):,.0f}")
        chg = cd.get("managed_money_net_change_wow")
        if chg is not None: md.append(f"- **تغير WoW:** {chg:+,.0f}")
        md.append(f"- **OI:** {cd.get('open_interest', 0):,.0f}")
    md.append(""); md.append("## 3️⃣ الاقتصاد")
    for k, lbl in [("headline_cpi", "CPI"), ("core_cpi", "Core CPI"), ("unemployment", "البطالة"), ("nonfarm_payrolls", "الوظائف")]:
        s = market.get("bls", {}).get("series", {}).get(k, {})
        if s.get("level") is not None:
            line = f"- **{lbl}:** {fmt_number(s['level'], 2)}"
            if s.get("yoy_pct") is not None: line += f" • YoY {s['yoy_pct']:+.2f}%"
            md.append(line)
    md.append(""); md.append("## 4️⃣ الاتساق")
    for c in run_consistency(market):
        ic = "🟢" if c["consistent"] else ("🔴" if c["consistent"] is False else "⚪")
        md.append(f"- {ic} **{c['metric']}**: {c['detail']}")
    md.append(""); md.append("## 5️⃣ الفيوجن")
    md.append(f"- **التحيز:** {fusion['final_bias']} • **الثقة:** {fusion['confidence']}%")
    md.append(f"- **جودة البيانات:** {market.get('quality_score', 0)}/100")
    if fusion["no_trade_reasons"]: md.append(f"- **أسباب NO TRADE:** " + " • ".join(fusion["no_trade_reasons"]))
    md.append(""); md.append("## 6️⃣ الإشارات")
    for s in fusion["econ"]["signals"]: md.append(f"- {s}")
    for s in fusion["smc"]["signals"]: md.append(f"- {s}")
    md.append(""); md.append(f"*{APP_NAME} • {APP_VERSION}*")
    return "\n".join(md)

def page_weekly():
    st.markdown("## 📄 التقرير الأسبوعي")
    if st.button("📝 توليد"):
        with st.spinner("..."):
            st.session_state.current_report = generate_weekly_report(market_data)
        log_action("report", "generate_weekly")
    if st.session_state.current_report:
        with st.expander("👁️ معاينة", expanded=True):
            st.markdown(st.session_state.current_report)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        if can_export():
            c = st.columns(2)
            c[0].download_button("⬇️ Markdown", data=st.session_state.current_report.encode("utf-8"),
                                 file_name=f"weekly_{ts}.md", mime="text/markdown")
            csv = pd.DataFrame([{"date": now_utc_text()[:10], "gold": market_data["gold"].get("value"),
                                 "dxy": market_data["dxy"].get("value"),
                                 "quality": market_data.get("quality_score")}]).to_csv(index=False).encode("utf-8-sig")
            c[1].download_button("⬇️ CSV", data=csv, file_name=f"weekly_{ts}.csv", mime="text/csv")
        if st.button("📤 إرسال عبر Telegram"):
            r = send_telegram(st.session_state.current_report[:4000])
            st.info(r["detail"])
        with st.form("email_form"):
            to = st.text_input("إرسال إلى (بريد)")
            if st.form_submit_button("📧 إرسال Email") and to:
                r = send_email(f"Weekly Report {now_utc_text()}", st.session_state.current_report, to)
                st.info(r["detail"])
        if not can_export():
            st.info("🔒 دورك لا يسمح بالتصدير.")

def page_history():
    st.markdown("## 📜 سجل التقارير")
    if st.button("💾 حفظ التقرير الحالي"):
        fusion = build_fusion(market_data, ohlc_res)
        st.session_state.report_history.append({"time": now_utc_text(),
                                                "bias": fusion["final_bias"],
                                                "confidence": fusion["confidence"],
                                                "quality": market_data["quality_score"],
                                                "gold": active_gold})
        log_action("report", "save_snapshot")
    if st.session_state.report_history:
        st.dataframe(pd.DataFrame(st.session_state.report_history[::-1]), use_container_width=True, hide_index=True)

def page_journal():
    st.markdown("## 📓 سجل الصفقات")
    with st.form("journal_form"):
        c1, c2 = st.columns(2)
        d = c1.selectbox("الاتجاه", ["LONG", "SHORT"])
        e = c1.number_input("الدخول", value=0.0)
        sl = c1.number_input("SL", value=0.0)
        tp = c2.number_input("TP", value=0.0)
        res = c2.selectbox("النتيجة", ["OPEN", "WIN", "LOSS", "BE"])
        notes = st.text_area("ملاحظات")
        if st.form_submit_button("➕ إضافة") and can_modify():
            st.session_state.trade_journal.append({"time": now_utc_text(), "direction": d,
                                                    "entry": e, "sl": sl, "tp": tp,
                                                    "result": res, "notes": notes})
            log_action("journal", "add_trade", new_value=f"{d}@{e}")
    if st.session_state.trade_journal:
        st.dataframe(pd.DataFrame(st.session_state.trade_journal[::-1]), use_container_width=True, hide_index=True)
        w = sum(1 for t in st.session_state.trade_journal if t["result"] == "WIN")
        l = sum(1 for t in st.session_state.trade_journal if t["result"] == "LOSS")
        if w + l > 0: st.metric("نسبة الربح", f"{w/(w+l)*100:.1f}%")

def page_audit():
    if current_role not in {"admin", "auditor"}: st.error("🔒 للمدقق/المدير فقط."); return
    st.markdown("## 🔎 سجل التدقيق")
    if not st.session_state.audit_log: st.info("لا سجلات."); return
    df = pd.DataFrame(st.session_state.audit_log[::-1])
    st.dataframe(df, use_container_width=True, hide_index=True)
    if can_export():
        st.download_button("⬇️ CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"audit_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

def page_admin():
    if current_role != "admin": st.error("🔒 للمدير فقط."); return
    st.markdown("## ⚙️ Admin")
    st.markdown("### حالة المفاتيح")
    for k in ["FRED_API_KEY", "BLS_API_KEY", "BEA_API_KEY",
              "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
              "GMAIL_USER", "GMAIL_APP_PASSWORD"]:
        has = bool(get_secret(k))
        st.markdown(f"- {k}: {'🟢 مضبوط' if has else '🔴 مفقود'}")
    st.markdown("### حالة المصادر")
    for name, s in [("Gold", market_data["gold"]), ("DXY", market_data["dxy"]),
                    ("Treasury", market_data["nominal"]), ("COT Legacy", market_data["cot"]),
                    ("COT Disagg", market_data["cot_disagg"]), ("BLS", market_data["bls"]),
                    ("BEA", market_data["bea"])]:
        st.markdown(f"- {name}: {display_status(s.get('status', 'NO DATA'))}")
    st.metric("الجودة الإجمالية", f"{market_data['quality_score']}/100")
    if st.button("🧹 تصفير الكاش"): st.cache_data.clear(); st.rerun()

# ================================================================
# ROUTING
# ================================================================
routes = {
    "🔥 MAIN DASHBOARD": page_dashboard,
    "📊 DATA SOURCES": page_data_sources,
    "📅 ECONOMIC CALENDAR": page_calendar,
    "📈 ECONOMIC ANALYSIS": page_econ,
    "💵 YIELDS & DOLLAR": page_yields,
    "📋 COT & OI": page_cot,
    "🧠 SMC/ICT": page_smc,
    "📉 TECHNICAL INDICATORS": page_tech,
    "🔗 CONSISTENCY": page_consistency,
    "🔍 EVIDENCE MATRIX": page_evidence,
    "✅ TRADE VALIDATOR": page_validator,
    "🛡️ RISK MANAGEMENT": page_risk,
    "🧪 BACKTESTING": page_backtest,
    "📄 WEEKLY REPORT": page_weekly,
    "📜 REPORT HISTORY": page_history,
    "📓 TRADING JOURNAL": page_journal,
    "🔎 AUDIT LOG": page_audit,
    "⚙️ ADMIN": page_admin,
}
handler = routes.get(navigation)
if handler: handler()
else: st.info(f"{navigation} قيد التطوير.")

st.divider()
st.caption(f"{APP_NAME} • {APP_VERSION} • {now_utc_text()}")
