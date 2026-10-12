# ================================================================
# Aho𓂀 GOLD — v16.7 (FULL v16 + VISUAL REPAIR)
# ================================================================
from __future__ import annotations
import os, re, json, hmac, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta, date
from io import StringIO
from typing import Any, Optional
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, requests, streamlit as st, bcrypt

APP_NAME = "Aho𓂀 GOLD"
APP_VERSION = "16.7 — FULL INTEGRATED + VISUAL REPAIR"
TIMEOUT = 15
UA = "AhoGoldIntelligence/16.7"

st.set_page_config(page_title="Aho𓂀 GOLD", page_icon="𓂀",
                   layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state: st.session_state.theme = "light"

# ================================================================
# THEME
# ================================================================
def theme_css(t: str) -> str:
    P = {
        "light": dict(bg="#f4f1ea", card="#fdfbf6", soft="#ede8dd", bd="#e0d9c8",
                      bd2="#cfc6b0", e1="#0d4a35", e2="#1a6b4a", e3="#2d8b62",
                      esoft="#e6f2eb", gold="#b8935a", gold2="#d4af7a",
                      goldd="#8a6e40", tx="#1e2620", txs="#4d5548", txd="#7a8279",
                      green="#16a34a", red="#dc2626", amber="#d97706",
                      shadow="0 2px 10px rgba(13,74,53,.06)",
                      btn_tx="#fdfbf6",
                      btn="linear-gradient(135deg,#0d4a35,#1a6b4a)",
                      btnh="linear-gradient(135deg,#1a6b4a,#2d8b62)",
                      sb="linear-gradient(180deg,#0d4a35,#0a3a29)",
                      sb_tx="#e8e4dc", sb_mu="#b8c4bc", sb_dm="#7a8a7f",
                      hero="linear-gradient(135deg,#fdfbf6,#f8f5ed)",
                      ambient="radial-gradient(ellipse at 10% 0%,rgba(13,74,53,.05),transparent 50%),"
                              "radial-gradient(ellipse at 90% 100%,rgba(184,147,90,.08),transparent 50%),#f4f1ea",
                      bull="linear-gradient(135deg,rgba(22,163,74,.10),rgba(22,163,74,.02))",
                      bear="linear-gradient(135deg,rgba(220,38,38,.10),rgba(220,38,38,.02))",
                      neut="linear-gradient(135deg,rgba(217,119,6,.10),rgba(217,119,6,.02))",
                      ntrade="#ede8dd",
                      warn_bg="linear-gradient(135deg,rgba(217,119,6,.10),rgba(217,119,6,.03))",
                      warn_tx="#8a5a00",
                      info_bg="linear-gradient(135deg,rgba(13,74,53,.05),rgba(13,74,53,.01))",
                      info_tx="#0d4a35"),
        "dark":  dict(bg="#1a1f2e", card="#232937", soft="#2b3140", bd="#333b4c",
                      bd2="#414a5c", e1="#4ade80", e2="#2ecc71", e3="#6ee7a3",
                      esoft="#1e3a2c", gold="#e8c98a", gold2="#f0d49a",
                      goldd="#b39a5f", tx="#ebe9e3", txs="#b8c0cc", txd="#8896a8",
                      green="#4ade80", red="#f87171", amber="#fbbf24",
                      shadow="0 2px 12px rgba(0,0,0,.25)",
                      btn_tx="#0d1420",
                      btn="linear-gradient(135deg,#e8c98a,#c9a961)",
                      btnh="linear-gradient(135deg,#f0d49a,#d9b972)",
                      sb="linear-gradient(180deg,#131824,#0f131e)",
                      sb_tx="#e8e4dc", sb_mu="#a8b2c0", sb_dm="#7a8598",
                      hero="linear-gradient(135deg,rgba(35,41,55,.95),rgba(26,31,46,.85))",
                      ambient="radial-gradient(ellipse at 10% 0%,rgba(46,204,113,.05),transparent 50%),"
                              "radial-gradient(ellipse at 90% 100%,rgba(232,201,138,.06),transparent 50%),#1a1f2e",
                      bull="linear-gradient(135deg,rgba(74,222,128,.12),rgba(74,222,128,.03))",
                      bear="linear-gradient(135deg,rgba(248,113,113,.12),rgba(248,113,113,.03))",
                      neut="linear-gradient(135deg,rgba(251,191,36,.12),rgba(251,191,36,.03))",
                      ntrade="#2b3140",
                      warn_bg="linear-gradient(135deg,rgba(251,191,36,.12),rgba(251,191,36,.03))",
                      warn_tx="#f5dc9a",
                      info_bg="linear-gradient(135deg,rgba(46,204,113,.08),rgba(46,204,113,.02))",
                      info_tx="#6ee7a3"),
    }[t]
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root{{--bg:{P['bg']};--card:{P['card']};--soft:{P['soft']};--bd:{P['bd']};--bd2:{P['bd2']};
--e1:{P['e1']};--e2:{P['e2']};--e3:{P['e3']};--esoft:{P['esoft']};--gold:{P['gold']};--gold2:{P['gold2']};
--goldd:{P['goldd']};--tx:{P['tx']};--txs:{P['txs']};--txd:{P['txd']};--green:{P['green']};
--red:{P['red']};--amber:{P['amber']};--shadow:{P['shadow']};
--font:'IBM Plex Sans Arabic','Inter',sans-serif;--fontn:'Inter','IBM Plex Sans Arabic',sans-serif}}
html,body,[class*="css"]{{font-family:var(--font);direction:rtl;text-align:right;color:var(--tx)}}
.stApp{{background:{P['ambient']};color:var(--tx);overflow-x:hidden!important}}
.block-container{{padding-top:1.3rem!important;padding-bottom:2.5rem!important;max-width:1550px;width:100%!important}}
[data-testid="stSidebar"]{{background:{P['sb']};border-left:none!important;border-right:none!important;box-shadow:none!important;outline:none!important;padding-top:14px}}
[data-testid="stSidebar"] *{{text-align:right;color:{P['sb_tx']}}}
[data-testid="stSidebar"] .stRadio label{{color:{P['sb_mu']}!important}}
[data-testid="stSidebar"] hr{{border-color:rgba(201,169,110,.15)!important}}
[data-testid="stSidebar"] .stCaption,[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{{color:{P['sb_dm']}!important}}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] h4{{color:var(--gold2)!important}}
[data-testid="stSidebar"]>div:first-child{{height:auto!important;min-height:100vh!important;overflow-y:auto!important}}
[data-testid="stSidebarNav"] a{{color:{P['sb_mu']}!important;border-radius:8px!important;padding:8px 10px!important;font-size:13.5px;margin:2px 0;transition:all .15s}}
[data-testid="stSidebarNav"] a:hover{{background:rgba(201,169,110,.12)!important;color:var(--gold2)!important}}
[data-testid="stSidebarNav"] a[aria-current="page"]{{background:linear-gradient(90deg,rgba(201,169,110,.20),rgba(201,169,110,.05))!important;color:var(--gold2)!important;font-weight:700!important;border-right:3px solid var(--gold)!important}}
[data-testid="stSidebarNav"] svg{{color:var(--gold)!important;width:18px!important;height:18px!important}}
/* إخفاء مقبض السحب الرأسي فقط — لا نخفي أزرار الفتح/الإغلاق */
[data-testid="stSidebarResizeHandle"],
[data-testid="stSidebarResizeHandle"] > div,
[data-testid="stSidebarResizeHandle"]::before,
[data-testid="stSidebarResizeHandle"]::after,
[data-testid="stSidebar"] > div[role="separator"],
[data-testid="stSidebar"] > div[role="separator"]::before,
[data-testid="stSidebar"] > div[role="separator"]::after,
[data-testid="stSidebar"] > div[aria-orientation="vertical"]{{
display:none!important;visibility:hidden!important;opacity:0!important;
width:0!important;min-width:0!important;max-width:0!important;height:0!important;
padding:0!important;margin:0!important;border:none!important;
background:transparent!important;box-shadow:none!important;pointer-events:none!important}}
/* إزالة الحدود الداخلية من الشريط */
[data-testid="stSidebar"] > div,[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"],[data-testid="stSidebarUserContent"],
[data-testid="stSidebarHeader"]{{border-left:none!important;border-right:none!important;border-top:none!important;border-bottom:none!important;box-shadow:none!important;outline:none!important}}
/* إزالة خطوط الفصل العمودية */
[data-testid="stHorizontalBlock"],[data-testid="stHorizontalBlock"] > div,
[data-testid="stVerticalBlock"],div[data-aria-orientation="horizontal"]{{border:none!important;border-right:none!important;border-left:none!important;box-shadow:none!important}}
/* على الجوال: أزرار الفتح/الإغلاق ظاهرة */
@media(max-width:900px){{
[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"],
button[aria-label="Open sidebar"],button[aria-label="Close sidebar"],
[data-testid="stSidebarCollapseButton"]{{display:flex!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;z-index:1000!important}}
section[data-testid="stSidebar"],section[data-testid="stSidebar"][aria-expanded="true"],
section[data-testid="stSidebar"][aria-expanded="false"]{{border-left:none!important;border-right:none!important;box-shadow:none!important}}
.block-container{{padding-left:.8rem!important;padding-right:.8rem!important;padding-top:1rem!important;max-width:100%!important}}
.hero{{padding:18px}}.hero h1{{font-size:20px}}
[data-testid="stMetricValue"]{{font-size:20px!important}}
[data-testid="stMetricLabel"]{{font-size:11px!important}}
[data-testid="stMetric"]{{padding:12px 13px}}}}
.brand{{display:flex;align-items:center;gap:12px;padding:6px 4px 16px;border-bottom:1px solid rgba(201,169,110,.2);margin-bottom:12px}}
.brand-mark{{width:46px;height:46px;border:1.5px solid var(--gold);border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:24px;font-weight:700;background:rgba(201,169,110,.08);box-shadow:0 0 22px rgba(201,169,110,.2)}}
.brand-title{{font-family:var(--fontn);letter-spacing:1.4px;font-weight:800;font-size:18px;color:var(--gold2);text-shadow:0 0 20px rgba(201,169,110,.3)}}
.brand-sub{{color:{P['sb_dm']};font-size:10.5px;margin-top:3px;letter-spacing:1.2px}}
.hero{{border:1px solid var(--bd);border-radius:16px;padding:22px 26px;background:{P['hero']};margin-bottom:18px;box-shadow:var(--shadow);border-right:4px solid var(--gold)}}
.eyebrow{{color:var(--e2);letter-spacing:1.8px;font-size:11.5px;font-weight:700;font-family:var(--fontn)}}
.hero h1{{margin:8px 0;font-size:26px;color:var(--e1);font-weight:700}}
.hero p{{margin:0;color:var(--txs);line-height:1.75;font-size:13.5px}}
[data-testid="stMetric"]{{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:15px 17px;box-shadow:var(--shadow);transition:all .2s}}
[data-testid="stMetric"]:hover{{border-color:var(--gold);transform:translateY(-1px)}}
[data-testid="stMetricLabel"]{{color:var(--txs)!important;font-size:12.5px!important}}
[data-testid="stMetricValue"]{{color:var(--e1)!important;font-size:24px!important;font-weight:700!important;font-family:var(--fontn);font-variant-numeric:tabular-nums;white-space:nowrap!important;overflow:visible!important}}
.fusion-card{{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:18px;margin-bottom:12px;box-shadow:var(--shadow);border-top:3px solid var(--gold)}}
.fusion-card h4{{color:var(--e1);margin:0 0 10px;font-size:14.5px;font-weight:700}}
.fusion-card p{{color:var(--txs);font-size:13px;line-height:1.85}}
.signal-bull{{border:1px solid rgba(46,204,113,.4);background:{P['bull']};border-radius:12px;padding:16px 18px;margin:10px 0;border-right:5px solid var(--green)}}
.signal-bear{{border:1px solid rgba(231,76,60,.4);background:{P['bear']};border-radius:12px;padding:16px 18px;margin:10px 0;border-right:5px solid var(--red)}}
.signal-neutral{{border:1px solid rgba(243,156,18,.4);background:{P['neut']};border-radius:12px;padding:16px 18px;margin:10px 0;border-right:5px solid var(--amber)}}
.signal-no-trade{{border:1px solid var(--bd);background:{P['ntrade']};border-radius:12px;padding:16px 18px;margin:10px 0;border-right:5px solid var(--txd)}}
.signal-bull h3,.signal-bear h3,.signal-neutral h3,.signal-no-trade h3{{color:var(--e1)!important;margin:0 0 6px;font-size:16px;font-weight:700}}
.warning-box{{border:1px solid rgba(243,156,18,.4);background:{P['warn_bg']};border-radius:10px;padding:13px 16px;margin:10px 0;color:{P['warn_tx']};font-size:13px;line-height:1.7;border-right:4px solid var(--amber)}}
.info-box{{border:1px solid rgba(13,74,53,.25);background:{P['info_bg']};border-radius:10px;padding:13px 16px;margin:10px 0;color:{P['info_tx']};font-size:13px;line-height:1.7;border-right:4px solid var(--e2)}}
.stButton button{{border-radius:10px;border:1.5px solid var(--gold)!important;background:{P['btn']}!important;color:{P['btn_tx']}!important;font-weight:700!important;width:100%;padding:10px;transition:all .2s}}
.stButton button:hover{{background:{P['btnh']}!important;transform:translateY(-1px);border-color:var(--gold2)!important}}
.stDownloadButton button{{border-radius:10px;border:1.5px solid var(--bd2)!important;background:var(--card)!important;color:var(--e1)!important;font-weight:600!important}}
.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"]>div,.stTextArea textarea{{background:var(--card)!important;border:1px solid var(--bd2)!important;color:var(--tx)!important;border-radius:8px!important}}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{{border-color:var(--e2)!important;box-shadow:0 0 0 3px rgba(46,204,113,.15)!important}}
.stRadio label{{padding:8px 12px!important;border-radius:8px;color:var(--txs)}}
[data-testid="stDataFrame"]{{border:1px solid var(--bd);border-radius:10px;overflow:hidden;background:var(--card)}}
.streamlit-expanderHeader,details>summary{{background:var(--card)!important;border-radius:10px!important;color:var(--e1)!important;font-weight:600!important;border:1px solid var(--bd)!important}}
h1,h2,h3,h4,h5{{color:var(--e1)!important}}h2{{font-size:21px!important}}h3{{font-size:17px!important}}
.stCaption,[data-testid="stCaptionContainer"]{{color:var(--txd)!important;font-size:11.5px!important}}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{{color:var(--txs)}}
hr{{border-color:var(--bd)!important;margin:1.2rem 0!important}}
footer{{visibility:hidden}}
</style>"""

st.markdown(theme_css(st.session_state.theme), unsafe_allow_html=True)

# ================================================================
# HELPERS
# ================================================================
def sec(name):
    try: v = st.secrets.get(name, "")
    except: v = ""
    return str(v or os.getenv(name, "")).strip()

def utc(): return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def local_now(): return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M:%S %p ET")

def req(url, **kw):
    h = kw.pop("headers", {}); h.setdefault("User-Agent", UA)
    h.setdefault("Accept", "application/json,text/html,*/*")
    return requests.get(url, timeout=TIMEOUT, headers=h, **kw)

def err_cls(e):
    if isinstance(e, (requests.Timeout, TimeoutError)): return "TIMEOUT"
    if isinstance(e, requests.HTTPError):
        c = e.response.status_code if e.response is not None else None
        return "RATE LIMITED" if c == 429 else ("AUTH ERROR" if c in (401, 403) else "UNAVAILABLE")
    if isinstance(e, requests.RequestException): return "UNAVAILABLE"
    return "NO DATA"

def fnum(v, d=2, s=""):
    try: return f"{float(v):,.{d}f}{s}"
    except: return "غير متاح"

def sflt(v):
    try: x = float(v); return x if pd.notna(x) else None
    except: return None

def disp(s):
    return {"CONNECTED":"🟢 CONNECTED","STALE":"🟠 STALE","RATE LIMITED":"🟠 RATE LIMITED",
            "AUTH ERROR":"🔴 AUTH ERROR","TIMEOUT":"🟠 TIMEOUT","NO DATA":"🔴 NO DATA",
            "NOT TESTED":"⚪ NOT TESTED","UNAVAILABLE":"🔴 UNAVAILABLE"}.get(s, s)

def hero(t, sub=""):
    p = sub or "منصة قرار موحدة لتحليل الذهب — بيانات رسمية، تحقق متقاطع، وقرار قابل للتتبع."
    st.markdown(f'<div class="hero"><div class="eyebrow">Aho𓂀 GOLD • INTELLIGENCE</div>'
                f'<h1>{t}</h1><p>{p}</p></div>', unsafe_allow_html=True)

def box_warn(t): st.markdown(f'<div class="warning-box">{t}</div>', unsafe_allow_html=True)
def box_info(t): st.markdown(f'<div class="info-box">{t}</div>', unsafe_allow_html=True)

# ================================================================
# FRESHNESS
# ================================================================
FRESH = {"intraday":{"h":6}, "daily":{"h":48}, "weekly":{"d":10},
         "monthly":{"d":75}, "quarterly":{"d":150}}

def fresh(obs, prof):
    cfg = FRESH[prof]
    d = pd.to_datetime(obs, utc=True, errors="coerce")
    if pd.isna(d): return {"ok": False, "detail": "تاريخ غير صالح."}
    delta = pd.Timestamp.now(tz="UTC") - d
    if "h" in cfg:
        a = delta.total_seconds() / 3600; ok = a <= cfg["h"]
        det = f"عمر {a:.1f} ساعة (الحد {cfg['h']}س)."
    else:
        a = delta.days; ok = a <= cfg["d"]
        det = f"عمر {a} يوم (الحد {cfg['d']})."
    return {"ok": ok, "detail": det}

# ================================================================
# RBAC + AUDIT
# ================================================================
def users():
    raw = sec("APP_USERS")
    if raw:
        try: return json.loads(raw)
        except: pass
    u, p = sec("APP_USERNAME"), sec("APP_PASSWORD")
    if u and p:
        return {u: {"pw_hash": bcrypt.hashpw(p.encode(), bcrypt.gensalt(12)).decode(), "role": "admin"}}
    return {}

def vpw(pw, h):
    try: return bcrypt.checkpw(pw.encode(), h.encode())
    except: return False

def vauth(u, pw):
    us = users()
    if u not in us: return None
    if vpw(pw, us[u].get("pw_hash", "")):
        return {"username": u, "role": us[u].get("role", "viewer")}
    return None

if "audit_log" not in st.session_state: st.session_state.audit_log = []

def log(cat, act, old=None, new=None, reason=""):
    usr = st.session_state.get("user") or {}
    st.session_state.audit_log.append({
        "time": utc(), "user": usr.get("username", "—"),
        "role": usr.get("role", "—"), "category": cat, "action": act,
        "old_value": old, "new_value": new, "reason": reason})

# ================================================================
# NOTIFICATIONS
# ================================================================
def tg_send(text):
    tk, ch = sec("TELEGRAM_BOT_TOKEN"), sec("TELEGRAM_CHAT_ID")
    if not (tk and ch): return {"detail": "Telegram غير مضبوط."}
    try:
        r = req(f"https://api.telegram.org/bot{tk}/sendMessage",
                params={"chat_id": ch, "text": text, "parse_mode": "Markdown"})
        r.raise_for_status(); return {"detail": "تم الإرسال."}
    except Exception as e: return {"detail": f"Telegram: {type(e).__name__}"}

def em_send(subj, body, to):
    u, pw = sec("GMAIL_USER"), sec("GMAIL_APP_PASSWORD")
    if not (u and pw and to): return {"detail": "Gmail SMTP غير مضبوط."}
    try:
        m = MIMEMultipart(); m["From"] = u; m["To"] = to; m["Subject"] = subj
        m.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
            s.login(u, pw); s.send_message(m)
        return {"detail": "تم الإرسال."}
    except Exception as e: return {"detail": f"SMTP: {type(e).__name__}"}

# ================================================================
# DATA SOURCES
# ================================================================
def yahoo_chart(sym, rng="5d", iv="1d"):
    try:
        r = req(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                params={"range": rng, "interval": iv})
        r.raise_for_status()
        return r.json().get("chart", {}).get("result", [None])[0]
    except Exception as e:
        return {"__err__": type(e).__name__}

def _quote(symbols, label):
    errs = []
    for sym in symbols:
        res = yahoo_chart(sym)
        if res is None: continue
        if isinstance(res, dict) and "__err__" in res:
            errs.append(f"{sym}:{res['__err__']}"); continue
        try:
            q = res["indicators"]["quote"][0]
            closes = q.get("close") or []; ts = res.get("timestamp") or []
            v = [(int(t), float(c)) for t, c in zip(ts, closes) if c is not None]
            if not v: continue
            lt, lv = v[-1]; pv = v[-2][1] if len(v) >= 2 else None
            obs = datetime.fromtimestamp(lt, timezone.utc)
            f = fresh(obs, "intraday")
            return {"status": "CONNECTED" if f["ok"] else "STALE", "label": label,
                    "symbol": sym, "value": lv, "change": (lv-pv) if pv else None,
                    "observation_date": obs.strftime("%Y-%m-%d"),
                    "timestamp": obs.strftime("%Y-%m-%d %H:%M UTC"),
                    "freshness_detail": f["detail"],
                    "source": f"Yahoo ({sym})",
                    "url": "https://finance.yahoo.com/",
                    "detail": f"{f['detail']} • {sym}"}
        except Exception as e: errs.append(f"{sym}:{type(e).__name__}")
    return {"status": "UNAVAILABLE", "label": label, "symbol": "—", "value": None,
            "change": None, "observation_date": "—", "timestamp": "—",
            "source": "Yahoo Finance", "url": "https://finance.yahoo.com/",
            "detail": "تعذر: " + " | ".join(errs[:3])}

@st.cache_data(ttl=300, show_spinner=False)
def q_yahoo(symbols, label):
    r = _quote(symbols, label); r["tested_at"] = utc(); return r

@st.cache_data(ttl=900, show_spinner=False)
def gold_ohlc(rng="6mo", iv="1d"):
    res = yahoo_chart("GC=F", rng, iv)
    if res is None or (isinstance(res, dict) and "__err__" in res):
        return {"status": "UNAVAILABLE", "df": None, "detail": "تعذر جلب OHLC."}
    try:
        ts = res.get("timestamp") or []
        q = res["indicators"]["quote"][0]
        O,H,L,C,V = (q.get(k, []) or [] for k in ("open","high","low","close","volume"))
        rows = []
        for i in range(min(len(ts), len(O), len(H), len(L), len(C))):
            if None in (O[i], H[i], L[i], C[i]): continue
            rows.append({"timestamp": datetime.fromtimestamp(ts[i], timezone.utc),
                         "open": float(O[i]), "high": float(H[i]),
                         "low": float(L[i]), "close": float(C[i]),
                         "volume": float(V[i]) if i < len(V) and V[i] is not None else 0.0})
        if not rows: return {"status": "NO DATA", "df": None, "detail": "أعمدة فارغة."}
        df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
        lt = df.iloc[-1]; f = fresh(lt["timestamp"], "intraday")
        return {"status": "CONNECTED" if f["ok"] else "STALE", "df": df,
                "source": "Yahoo GC=F", "url": "https://finance.yahoo.com/",
                "observation_date": lt["timestamp"].strftime("%Y-%m-%d"),
                "freshness_detail": f["detail"],
                "detail": f"{len(df)} شمعة • {f['detail']}"}
    except Exception as e:
        return {"status": err_cls(e), "df": None, "detail": f"{type(e).__name__}"}

def _norm(v): return re.sub(r"[^a-z0-9]", "", str(v).lower())

def _ycol(cols, y):
    nm = {c: _norm(c) for c in cols}
    for c, n in nm.items():
        if n in {f"{y}yr", f"{y}year", f"{y}yrs", f"{y}years", f"{y}y", f"{y}mo"}: return c
    for c, n in nm.items():
        if n.startswith(str(y)) and ("yr" in n or "year" in n or n.endswith("y")): return c
    return None

def _treasury(real=False):
    t = "daily_treasury_real_yield_curve" if real else "daily_treasury_yield_curve"
    y = datetime.now(timezone.utc).year
    url = (f"https://home.treasury.gov/resource-center/data-chart-center/"
           f"interest-rates/daily-treasury-rates.csv/{y}/all?"
           f"type={t}&field_tdr_date_value={y}&page&_format=csv")
    nm = "U.S. Treasury real yield" if real else "U.S. Treasury nominal yield"
    try:
        r = req(url); r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        dc = next((c for c in df.columns if "date" in _norm(c)), None)
        df["_d"] = pd.to_datetime(df[dc], errors="coerce")
        df = df[df["_d"].notna()].sort_values("_d", ascending=False)
        if df.empty: return {"status": "NO DATA", "source": nm, "values": {}, "date": "—", "detail": "لا تواريخ."}
        lt = df.iloc[0]; vals = {}
        for yy in (2,5,10,20,30):
            c = _ycol(list(df.columns), yy)
            if c is None: continue
            raw = str(lt[c]).replace("%", "").replace(",", "").strip()
            if raw and raw.lower() not in {"nan","none","-","n/a"}:
                try: vals[f"{yy}Y"] = float(raw)
                except: pass
        if "10Y" not in vals: return {"status": "NO DATA", "source": nm, "values": {}, "date": "—", "detail": "10Y مفقود."}
        obs = lt["_d"].strftime("%Y-%m-%d"); f = fresh(obs, "daily")
        return {"status": "CONNECTED" if f["ok"] else "STALE",
                "source": "U.S. Treasury official", "url": url, "date": obs,
                "values": vals, "freshness_detail": f["detail"], "detail": f["detail"]}
    except Exception as e:
        return {"status": err_cls(e), "source": nm, "values": {}, "date": "—",
                "detail": f"{type(e).__name__}"}

@st.cache_data(ttl=1800, show_spinner=False)
def treasury(real=False):
    r = _treasury(real); r["tested_at"] = utc(); return r

FRED_META = {"DGS2":("عائد 2Y",8,"daily"), "DGS5":("عائد 5Y",8,"daily"),
             "DGS10":("عائد 10Y",8,"daily"), "DGS20":("عائد 20Y",8,"daily"),
             "DGS30":("عائد 30Y",8,"daily"), "DFII10":("عائد حقيقي 10Y",8,"daily"),
             "T10YIE":("تضخم متوقع 10Y",8,"daily"), "CPIAUCSL":("CPI",75,"monthly")}

@st.cache_data(ttl=900, show_spinner=False)
def fred(sid, key):
    if not key: return {"status": "NOT TESTED", "series": sid, "value": None, "date": "—",
                        "source": "FRED", "detail": "لا مفتاح."}
    try:
        r = req("https://api.stlouisfed.org/fred/series/observations",
                params={"series_id": sid, "api_key": key, "file_type": "json",
                        "sort_order": "desc", "limit": 12})
        r.raise_for_status()
        obs = [o for o in r.json().get("observations", []) if o.get("value") not in (None, ".", "")]
        if not obs: return {"status": "NO DATA", "series": sid, "value": None, "date": "—",
                            "source": "FRED", "detail": "فارغ."}
        lt = obs[0]; lbl, _, prof = FRED_META.get(sid, (sid, 10, "daily"))
        f = fresh(lt.get("date"), prof)
        return {"status": "CONNECTED" if f["ok"] else "STALE", "series": sid, "label": lbl,
                "value": float(lt["value"]), "date": lt.get("date", "—"),
                "source": "FRED", "detail": f["detail"], "freshness_detail": f["detail"],
                "tested_at": utc()}
    except Exception as e:
        return {"status": err_cls(e), "series": sid, "value": None, "date": "—",
                "source": "FRED", "detail": f"{type(e).__name__}"}

FRED_REL = {10:("CPI","🔴","BLS"), 50:("Nonfarm Payrolls","🔴","BLS"),
            53:("GDP","🔴","BEA"), 54:("PCE","🔴","BEA"),
            9:("Retail Sales","🟠","Census")}

FOMC = {2025:["2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-11-05","2025-12-17"],
        2026:["2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16","2026-10-28","2026-12-09"],
        2027:[]}

@st.cache_data(ttl=21600, show_spinner=False)
def fred_releases(rid, key):
    if not key: return []
    try:
        r = req("https://api.stlouisfed.org/fred/release/dates",
                params={"release_id": rid, "api_key": key, "file_type": "json",
                        "include_release_dates_with_no_data": "true",
                        "sort_order": "asc", "limit": 12})
        r.raise_for_status()
        return [d.get("date") for d in r.json().get("release_dates", []) if d.get("date")]
    except: return []

def calendar(key):
    ev = []; now = datetime.now(timezone.utc).date()
    for rid, (nm, imp, src) in FRED_REL.items():
        for d in fred_releases(rid, key):
            try: dt = pd.to_datetime(d).date()
            except: continue
            if dt < now: continue
            ev.append({"date": str(dt), "event": nm, "importance": imp, "source": src})
    y = now.year; fomc = FOMC.get(y, []) or FOMC.get(y+1, [])
    for d in fomc:
        try: dt = pd.to_datetime(d).date()
        except: continue
        if dt < now: continue
        ev.append({"date": str(dt), "event": "FOMC", "importance": "🔴", "source": "Fed"})
    if not ev: return pd.DataFrame()
    df = pd.DataFrame(ev).sort_values("date").reset_index(drop=True)
    df.columns = ["التاريخ", "الحدث", "الأهمية", "المصدر"]
    return df

BLS_S = {"headline_cpi":("CUSR0000SA0","CPI","monthly"),
         "core_cpi":("CUSR0000SA0L1E","Core CPI","monthly"),
         "unemployment":("LNS14000000","البطالة","monthly"),
         "nonfarm_payrolls":("CES0000000001","الوظائف","monthly"),
         "hourly_earnings":("CES0500000003","الأجور","monthly")}

def _bls_chg(rows):
    if not rows: return {"mom_pct":None,"yoy_pct":None,"level":None}
    try: lt = float(rows[0]["value"])
    except: return {"mom_pct":None,"yoy_pct":None,"level":None}
    def back(n):
        y = int(rows[0]["year"]); m = int(rows[0]["period"][1:]) - n
        while m <= 0: m += 12; y -= 1
        for r in rows:
            if int(r["year"]) == y and int(r["period"][1:]) == m:
                try: return float(r["value"])
                except: return None
        return None
    pm, py = back(1), back(12)
    return {"level": lt, "mom_pct": round((lt/pm-1)*100,2) if pm else None,
            "yoy_pct": round((lt/py-1)*100,2) if py else None}

@st.cache_data(ttl=3600, show_spinner=False)
def bls_v2(key=""):
    cy = datetime.now(timezone.utc).year
    pl = {"seriesid": [m[0] for m in BLS_S.values()], "startyear": str(cy-2),
          "endyear": str(cy), "catalog": False, "calculations": False, "annualaverage": False}
    if key: pl["registrationkey"] = key
    try:
        r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=pl,
                          timeout=TIMEOUT, headers={"User-Agent": UA, "Content-Type": "application/json"})
        r.raise_for_status()
        b = r.json()
        if b.get("status") != "REQUEST_SUCCEEDED":
            return {"status": "NO DATA", "series": {}, "source": "BLS v2",
                    "detail": "; ".join((b.get("message") or [])[:3])}
        mp = {}
        for it in b.get("Results", {}).get("series", []):
            mp[it.get("seriesID")] = sorted(
                [e for e in it.get("data", []) if str(e.get("period", "")) != "M13"],
                key=lambda x: (int(x.get("year", 0)),
                               int(x.get("period", "M0")[1:]) if str(x.get("period", "")).startswith("M") else 0),
                reverse=True)
        out = {}
        for k, (sid, lbl, _) in BLS_S.items():
            rows = mp.get(sid, [])
            if not rows: out[k] = {"status": "NO DATA", "label": lbl, "level": None,
                                    "mom_pct": None, "yoy_pct": None, "date": "—"}; continue
            lt = rows[0]; c = _bls_chg(rows); f = fresh(f"{lt.get('year')}-{lt.get('period')}", "monthly")
            out[k] = {"status": "CONNECTED" if f["ok"] else "STALE", "label": lbl,
                      "level": c["level"], "mom_pct": c["mom_pct"], "yoy_pct": c["yoy_pct"],
                      "date": f"{lt.get('year')}-{lt.get('period')}", "detail": f["detail"]}
        req_s = {"headline_cpi", "unemployment", "nonfarm_payrolls"}
        ok_n = sum(1 for k in req_s if out.get(k, {}).get("status") == "CONNECTED")
        ov = "CONNECTED" if ok_n == len(req_s) else ("STALE" if ok_n > 0 else "NO DATA")
        return {"status": ov, "series": out, "source": "BLS v2",
                "detail": "تم.", "tested_at": utc()}
    except Exception as e:
        return {"status": err_cls(e), "series": {}, "source": "BLS v2", "detail": f"{type(e).__name__}"}

@st.cache_data(ttl=3600, show_spinner=False)
def bea(key):
    if not key: return {"status": "NOT TESTED", "source": "BEA", "detail": "لا مفتاح.", "value": None}
    try:
        r = req("https://apps.bea.gov/api/data/",
                params={"UserID": key, "method": "GetData", "DataSetName": "NIPA",
                        "TableName": "T10101", "Frequency": "Q", "Year": "X", "ResultFormat": "JSON"})
        r.raise_for_status()
        res = (r.json().get("BEAAPI") or {}).get("Results") or {}
        if isinstance(res, dict) and "Error" in res:
            return {"status": "NO DATA", "source": "BEA", "detail": str(res["Error"])[:100]}
        data = res.get("Data") if isinstance(res, dict) else None
        if not data: return {"status": "NO DATA", "source": "BEA", "detail": "لا صفوف."}
        lt = max(data, key=lambda x: (x.get("TimePeriod", ""), x.get("LineNumber", "")))
        try: v = float(str(lt.get("DataValue", "")).replace(",", ""))
        except: v = None
        return {"status": "CONNECTED", "source": "BEA", "value": v,
                "date": lt.get("TimePeriod", "—"),
                "detail": lt.get("LineDescription", ""), "tested_at": utc()}
    except Exception as e:
        return {"status": err_cls(e), "source": "BEA", "detail": f"{type(e).__name__}"}

CFTC_LEG = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
CFTC_DIS = "https://publicreporting.cftc.gov/resource/kh3c-gbw2.json"
GOLD = "088691"

def _cot(url, fields, source):
    try:
        r = req(url, params={"$where": f"cftc_contract_market_code='{GOLD}'",
                             "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 12})
        r.raise_for_status()
        raw = r.json()
        if not raw: return {"status": "NO DATA", "rows": [], "source": source, "detail": "لا صفوف."}
        rows = []
        for x in raw:
            try:
                row = {"date": str(x["report_date_as_yyyy_mm_dd"])[:10]}
                for k, fld in fields.items(): row[k] = float(x[fld])
                rows.append(row)
            except (KeyError, TypeError, ValueError): continue
        if not rows: return {"status": "NO DATA", "rows": [], "source": source, "detail": "حقول ناقصة."}
        rows.sort(key=lambda z: z["date"], reverse=True)
        lt = rows[0]; pv = rows[1] if len(rows) > 1 else None
        for k in fields:
            if k in ("date",): continue
            lt[f"{k}_wow"] = (lt[k] - pv[k]) if pv else None
        f = fresh(lt["date"], "weekly")
        return {"status": "CONNECTED" if f["ok"] else "STALE", "rows": rows, "latest": lt,
                "source": source, "detail": f"{lt['date']} • {f['detail']}",
                "freshness_detail": f["detail"], "tested_at": utc()}
    except Exception as e:
        return {"status": err_cls(e), "rows": [], "source": source, "detail": f"{type(e).__name__}"}

@st.cache_data(ttl=7200, show_spinner=False)
def cot_legacy():
    return _cot(CFTC_LEG, {"long": "noncomm_positions_long_all",
                           "short": "noncomm_positions_short_all",
                           "oi": "open_interest_all"}, "CFTC Legacy")

@st.cache_data(ttl=7200, show_spinner=False)
def cot_disagg():
    d = _cot(CFTC_DIS, {"mm_long": "m_money_positions_long_all",
                        "mm_short": "m_money_positions_short_all",
                        "swap_long": "swap_positions_long_all",
                        "swap_short": "swap__positions_short_all",
                        "oi": "open_interest_all"}, "CFTC Disaggregated")
    if d.get("rows"):
        for r in d["rows"]:
            r["mm_net"] = r["mm_long"] - r["mm_short"]
            r["swap_net"] = r["swap_long"] - r["swap_short"]
        lt = d["latest"]
        lt["mm_net"] = lt["mm_long"] - lt["mm_short"]
        lt["swap_net"] = lt["swap_long"] - lt["swap_short"]
        pv = d["rows"][1] if len(d["rows"]) > 1 else None
        lt["mm_net_wow"] = (lt["mm_net"] - pv["mm_net"]) if pv else None
    return d

def _goldapi():
    try:
        r = req("https://api.gold-api.com/price/XAU"); r.raise_for_status()
        d = r.json(); p = d.get("price"); up = d.get("updatedAt", "")
        if p is None: return {"status": "NO DATA", "value": None, "source": "gold-api", "detail": "لا سعر."}
        f = fresh(up or datetime.now(timezone.utc), "intraday")
        return {"status": "CONNECTED" if f["ok"] else "STALE", "value": float(p),
                "source": "gold-api.com", "detail": f["detail"],
                "observation_date": (up or "")[:10] or "—", "timestamp": up or "—",
                "freshness_detail": f["detail"]}
    except Exception as e:
        return {"status": err_cls(e), "value": None, "source": "gold-api", "detail": f"{type(e).__name__}"}

@st.cache_data(ttl=120, show_spinner=False)
def gold_multi():
    y = _quote(("GC=F",), "GOLD"); g = _goldapi()
    cands = [("yahoo_gcf", y), ("gold-api", g)]
    for n, c in cands:
        if c.get("status") == "CONNECTED":
            c["verified_by"] = n
            c["all_sources"] = {k: {"status": v.get("status"), "value": v.get("value")} for k, v in cands}
            c["tested_at"] = utc(); return c
    for n, c in cands:
        if c.get("status") == "STALE":
            c["verified_by"] = n
            c["all_sources"] = {k: {"status": v.get("status"), "value": v.get("value")} for k, v in cands}
            c["tested_at"] = utc(); return c
    return {"status": "UNAVAILABLE", "value": None, "source": "multi",
            "detail": " | ".join(f"{n}:{c.get('detail','—')}" for n, c in cands),
            "all_sources": {k: {"status": v.get("status"), "value": v.get("value")} for k, v in cands},
            "tested_at": utc()}

# ================================================================
# QUALITY + CONSISTENCY
# ================================================================
def q_score(s):
    p = 0
    if s.get("status") == "CONNECTED": p += 40
    elif s.get("status") == "STALE": p += 20
    if s.get("value") is not None or s.get("rows") or s.get("series"): p += 25
    if s.get("freshness_detail"): p += 20
    if any(k in (s.get("source") or "") for k in ("Treasury","FRED","CFTC","BLS","BEA","official")): p += 15
    return min(p, 100)

def quality(m):
    srcs = [m.get("gold",{}), m.get("dxy",{}), m.get("nominal",{}),
            m.get("real_yield",{}), m.get("cot_disagg",{}), m.get("bls",{}), m.get("bea",{})]
    ws = [25,10,15,10,20,10,10]
    return round(sum(w*q_score(s)/100 for s, w in zip(srcs, ws)))

def _cons(lbl, va, vb, sa, sb, th, pct=True):
    o = {"metric": lbl, "a": sa, "b": sb, "va": va, "vb": vb, "th": th, "consistent": None, "detail": ""}
    if va is None or vb is None: o["detail"] = "مصدر واحد غير متاح."; return o
    d = abs(va - vb); dp = (d/max(abs(va),abs(vb),1e-9)*100) if pct else d
    if dp <= th: o["consistent"] = True; o["detail"] = f"✅ {dp:.3f}%"
    else: o["consistent"] = False; o["detail"] = f"🚨 {dp:.3f}% > {th}"
    return o

def consistency(m):
    return [
        _cons("الذهب", m.get("gold",{}).get("value"), _goldapi().get("value"),
              "Yahoo", "gold-api", 0.5),
        _cons("US 10Y", m.get("nominal",{}).get("values",{}).get("10Y"),
              m.get("fred",{}).get("DGS10",{}).get("value"), "Treasury", "FRED", 0.05, False),
        _cons("Real 10Y", m.get("fred",{}).get("DFII10",{}).get("value"),
              m.get("treasury_real",{}).get("values",{}).get("10Y"),
              "FRED", "Treasury", 0.05, False),
    ]

# ================================================================
# ENGINES
# ================================================================
def indicators(df):
    if df is None or len(df) < 20: return {"status": "NO DATA", "detail": "OHLC غير كافٍ."}
    c, h, l = df["close"].astype(float), df["high"].astype(float), df["low"].astype(float)
    lr = np.log(c / c.shift()).dropna()
    def atr(p):
        tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
        return float(tr.rolling(p).mean().iloc[-1])
    s20, sd20 = c.rolling(20).mean(), c.rolling(20).std()
    s50 = float(c.rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
    trend = "UP" if s50 and s20.iloc[-1] > s50 else ("DOWN" if s50 else "FLAT")
    return {"status": "OK", "atr14": round(atr(14),2), "atr7": round(atr(7),2),
            "vol20": round(float(lr.tail(20).std()*np.sqrt(252)*100),2),
            "vol60": round(float(lr.tail(60).std()*np.sqrt(252)*100),2),
            "bb_u": round(float((s20+2*sd20).iloc[-1]),2),
            "bb_m": round(float(s20.iloc[-1]),2),
            "bb_l": round(float((s20-2*sd20).iloc[-1]),2),
            "trend": trend, "bars": len(df)}

def _swings(df, l=2, r=2):
    if df is None or len(df) < l+r+1: return {"h": [], "l": []}
    hs, ls = df["high"].values, df["low"].values; H, L = [], []
    for i in range(l, len(df)-r):
        if hs[i] == max(hs[i-l:i+r+1]): H.append((i, float(hs[i])))
        if ls[i] == min(ls[i-l:i+r+1]): L.append((i, float(ls[i])))
    return {"h": H, "l": L}

def _bos(df, sw):
    o = {"structure": "UNDEFINED", "bos": None}
    if not sw["h"] or not sw["l"]: return o
    if len(sw["h"]) >= 2 and len(sw["l"]) >= 2:
        ph, pl = sw["h"][-2], sw["l"][-2]; lc = float(df["close"].iloc[-1])
        if lc > ph[1]: o["bos"] = ("BULLISH", ph[1]); o["structure"] = "BULLISH_BOS"
        elif lc < pl[1]: o["bos"] = ("BEARISH", pl[1]); o["structure"] = "BEARISH_BOS"
        else: o["structure"] = "RANGE"
    return o

def smc_engine(ohlc):
    df = ohlc.get("df")
    o = {"structure": "UNDEFINED", "bias": "NEUTRAL", "signals": [], "sweeps": [],
         "pdh": None, "pdl": None, "atr": None}
    if df is None or len(df) < 10:
        o["signals"].append("⚠️ لا OHLC كافٍ."); return o
    if len(df) >= 2:
        y = df.iloc[-2]; o["pdh"] = float(y["high"]); o["pdl"] = float(y["low"])
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    o["atr"] = float(tr.rolling(14).mean().iloc[-1])
    sw = _swings(df, 2, 2); bi = _bos(df, sw); o["structure"] = bi["structure"]
    if bi["bos"]:
        side, lv = bi["bos"]
        o["bias"] = "BULLISH" if side == "BULLISH" else "BEARISH"
        o["signals"].append(f"BOS {side} عند {lv:.2f}")
    return o

def econ_engine(m):
    o = {"bias": "NEUTRAL", "confidence": 0, "signals": []}
    bls = m.get("bls", {}).get("series", {}); fr = m.get("fred", {})
    cpi = bls.get("headline_cpi", {})
    if cpi.get("yoy_pct") is not None:
        if cpi["yoy_pct"] > 3: o["bias"] = "BEARISH_GOLD"; o["confidence"] += 15
        elif cpi["yoy_pct"] < 2: o["bias"] = "BULLISH_GOLD"; o["confidence"] += 15
        o["signals"].append(f"CPI YoY: {cpi['yoy_pct']}%")
    r10 = fr.get("DFII10", {}).get("value")
    if r10 is not None:
        if r10 > 2: o["bias"] = "BEARISH_GOLD"; o["confidence"] += 20
        elif r10 < 1: o["bias"] = "BULLISH_GOLD"; o["confidence"] += 20
        o["signals"].append(f"Real 10Y: {r10}%")
    if o["confidence"] < 25: o["bias"] = "NO_TRADE"
    return o

def fusion(m, ohlc):
    ec = econ_engine(m); sm = smc_engine(ohlc); cot = m.get("cot_disagg", {}).get("latest", {})
    cot_b = "NEUTRAL"
    if cot:
        mm = cot.get("mm_net", 0)
        if mm > 150_000: cot_b = "BULLISH"
        elif mm < 50_000: cot_b = "BEARISH"
    v = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0}
    w = {"econ": 0.35, "smc": 0.30, "cot": 0.25, "dxy": 0.10}
    eb = ec["bias"].replace("_GOLD", "")
    if eb in v: v[eb] += w["econ"] * 100
    if sm["bias"] in v: v[sm["bias"]] += w["smc"] * 100
    if cot_b in v: v[cot_b] += w["cot"] * 100
    dx = m.get("dxy", {})
    if dx.get("change") is not None:
        v["BULLISH" if dx["change"] < 0 else "BEARISH"] += w["dxy"] * 100
    fb = max(v, key=v.get); conf = v[fb]
    reasons = []
    if ec["bias"] == "NO_TRADE": reasons.append("بيانات اقتصادية غير كافية")
    if sm["structure"] == "UNDEFINED": reasons.append("لا OHLC كافٍ")
    if m.get("quality_score", 0) < 40: reasons.append("جودة بيانات منخفضة")
    if conf < 40: reasons.append("ثقة منخفضة")
    return {"final": "NO_TRADE" if reasons else fb, "confidence": round(conf, 1),
            "votes": {k: round(x, 1) for k, x in v.items()}, "econ": ec, "smc": sm,
            "cot_bias": cot_b, "reasons": reasons}

def validate(t, fus, m):
    chk = []; ok = True
    fb = fus["final"]; d = t.get("direction", "LONG")
    if fb == "NO_TRADE": chk.append(("🔴", "الفيوجن NO TRADE", False)); ok = False
    elif (fb == "BULLISH" and d == "SHORT") or (fb == "BEARISH" and d == "LONG"):
        chk.append(("🟠", "اتجاه معاكس", False)); ok = False
    else: chk.append(("🟢", "الاتجاه متوافق", True))
    e, sl, tp = t.get("entry"), t.get("stop_loss"), t.get("take_profit")
    if all(x is not None for x in (e, sl, tp)):
        rr = abs(tp - e) / abs(e - sl) if abs(e - sl) > 0 else 0
        if rr >= 2: chk.append(("🟢", f"R:R {rr:.2f}", True))
        elif rr >= 1.5: chk.append(("🟠", f"R:R {rr:.2f}", True))
        else: chk.append(("🔴", f"R:R ضعيف {rr:.2f}", False)); ok = False
    q = m.get("quality_score", 0)
    if q >= 70: chk.append(("🟢", f"جودة {q}", True))
    elif q >= 40: chk.append(("🟠", f"جودة {q}", True))
    else: chk.append(("🔴", f"جودة منخفضة {q}", False)); ok = False
    return {"valid": ok, "checks": chk}

def risk_calc(bal, pct, e, sl, tp, cs=100):
    r = bal * pct / 100; sld = abs(e - sl); tpd = abs(tp - e)
    if sld == 0: return {"error": "SL = Entry"}
    ps = r / (sld * cs); return {"risk": round(r, 2), "lots": round(ps, 4),
                                  "rr": round(tpd/sld, 2), "profit": round(ps*tpd*cs, 2)}

def backtest(df, slm=1.5, tpm=3.0, lb=20, slip=0.5, mb=None):
    if df is None or len(df) < 60: return {"status": "NO DATA", "detail": "OHLC غير كافٍ."}
    df = df.reset_index(drop=True).copy()
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()
    trades = []; pos = None
    for i in range(lb+5, len(df)):
        row = df.iloc[i]
        if pd.isna(row["atr"]) or row["atr"] <= 0: continue
        if pos:
            hit_sl = row["low"] <= pos["sl"] if pos["dir"] == "LONG" else row["high"] >= pos["sl"]
            hit_tp = row["high"] >= pos["tp"] if pos["dir"] == "LONG" else row["low"] <= pos["tp"]
            bh = i - pos["ei"]
            if hit_sl: pos["result"] = -1; pos["bars"] = bh; trades.append(pos); pos = None
            elif hit_tp: pos["result"] = tpm/slm; pos["bars"] = bh; trades.append(pos); pos = None
            elif mb and bh >= mb:
                pnl = (row["close"]-pos["e"])/(pos["e"]-pos["sl"]) if pos["dir"] == "LONG" else (pos["e"]-row["close"])/(pos["sl"]-pos["e"])
                pos["result"] = float(pnl); pos["bars"] = bh; trades.append(pos); pos = None
            continue
        wh = df["high"].iloc[i-lb:i].max(); wl = df["low"].iloc[i-lb:i].min()
        p = row["close"]; a = row["atr"]
        if p > wh:
            e = p + slip
            pos = {"ei": i, "e": e, "dir": "LONG", "sl": e-slm*a, "tp": e+tpm*a, "t": row["timestamp"]}
        elif p < wl:
            e = p - slip
            pos = {"ei": i, "e": e, "dir": "SHORT", "sl": e+slm*a, "tp": e-tpm*a, "t": row["timestamp"]}
    if not trades: return {"status": "OK", "trades": [], "total": 0, "win_rate": 0, "avg_r": 0, "max_dd": 0}
    res = [t["result"] for t in trades]; wins = sum(1 for r in res if r > 0)
    eq = np.cumsum(res); peak = np.maximum.accumulate(eq); dd = eq - peak
    return {"status": "OK", "trades": trades, "total": len(trades),
            "win_rate": round(wins/len(trades)*100, 1), "avg_r": round(sum(res)/len(res), 3),
            "max_dd": round(float(dd.min()), 2), "detail": f"{len(trades)} صفقة."}

# ================================================================
# MARKET DATA
# ================================================================
@st.cache_data(ttl=600, show_spinner=False)
def market():
    dxy = q_yahoo(("DX-Y.NYB",), "DXY")
    g = gold_multi()
    nom = treasury(False); real = treasury(True)
    cl = cot_legacy(); cd = cot_disagg()
    bls = bls_v2(sec("BLS_API_KEY")); b = bea(sec("BEA_API_KEY"))
    fk = sec("FRED_API_KEY")
    f = {sid: fred(sid, fk) for sid in FRED_META} if fk else {}
    r10 = f.get("DFII10", {}).get("value")
    ry = {"status": f.get("DFII10", {}).get("status", real["status"]),
          "value": r10 if r10 is not None else real.get("values", {}).get("10Y"),
          "date": f.get("DFII10", {}).get("date", real.get("date", "—")),
          "source": "FRED DFII10" if r10 is not None else real["source"]}
    m = {"gold": g, "dxy": dxy, "nominal": nom, "treasury_real": real,
         "real_yield": ry, "breakeven": {"value": f.get("T10YIE", {}).get("value")},
         "cot": cl, "cot_disagg": cd, "bls": bls, "bea": b, "fred": f,
         "tested_at": utc()}
    m["quality_score"] = quality(m)
    return m
  
# ================================================================
# AUTH GATE
# ================================================================
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user" not in st.session_state: st.session_state.user = None

us = users()
if us and not st.session_state.authenticated:
    hero("تسجيل الدخول", "أدخل بياناتك للوصول.")
    with st.form("login"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        ok = st.form_submit_button("دخول")
    if ok:
        s = vauth(u, p)
        if s:
            st.session_state.authenticated = True
            st.session_state.user = s
            log("auth", "login")
            st.rerun()
        else:
            st.error("بيانات غير صحيحة.")
    st.stop()

current_user = st.session_state.user or {"username": "local", "role": "admin"}
current_role = current_user["role"]

for k, v in {"manual_gold_price": None, "trade_journal": [], "report_history": [],
             "current_report": None, "seen_observations": {},
             "manual_consensus": {}}.items():
    if k not in st.session_state: st.session_state[k] = v

with st.spinner("جاري تحميل البيانات..."): mdata = market()
with st.spinner("جاري تحميل OHLC..."): ohlc = gold_ohlc("6mo", "1d")

active_gold = (float(st.session_state.manual_gold_price)
               if st.session_state.manual_gold_price is not None
               else sflt(mdata["gold"].get("value")))

def can_export(): return current_role in {"admin", "analyst"}

def detect_new(m):
    alerts = []
    pairs = [
        ("COT Disaggregated", m.get("cot_disagg", {}).get("latest", {}).get("date")),
        ("COT Legacy", m.get("cot", {}).get("latest", {}).get("date")),
        ("BLS CPI", m.get("bls", {}).get("series", {}).get("headline_cpi", {}).get("date")),
        ("BLS NFP", m.get("bls", {}).get("series", {}).get("nonfarm_payrolls", {}).get("date")),
        ("Treasury 10Y", m.get("nominal", {}).get("date")),
        ("FRED DGS10", m.get("fred", {}).get("DGS10", {}).get("date")),
    ]
    seen = st.session_state.seen_observations
    for name, obs in pairs:
        if not obs or obs == "—": continue
        if seen.get(name) != obs:
            alerts.append({"source": name, "old": seen.get(name, "—"),
                           "new": obs, "is_first": name not in seen})
            seen[name] = obs
    return alerts

new_alerts = detect_new(mdata)

# ================================================================
# PAGES
# ================================================================
def pg_dashboard():
    hero("لوحة القرار الموحد")
    c = st.columns(3)
    c[0].metric("XAUUSD (GC=F)", fnum(active_gold, 2, " $") if active_gold else "—")
    c[1].metric("DXY", fnum(mdata["dxy"].get("value"), 2))
    c[2].metric("US 10Y", fnum(mdata["nominal"].get("values", {}).get("10Y"), 3, "%"))
    c = st.columns(3)
    c[0].metric("Real 10Y", fnum(mdata.get("real_yield", {}).get("value"), 3, "%"))
    c[1].metric("Breakeven", fnum(mdata.get("breakeven", {}).get("value"), 2, "%"))
    c[2].metric("جودة البيانات", f"{mdata['quality_score']}/100")

    fus = fusion(mdata, ohlc)
    fb = fus["final"]
    cls = {
        "BULLISH": ("signal-bull", "🟢", "تحيز صاعد"),
        "BEARISH": ("signal-bear", "🔴", "تحيز هابط"),
        "NO_TRADE": ("signal-no-trade", "⛔", "لا تداول"),
    }.get(fb, ("signal-neutral", "🟡", "حياد"))
    rh = ("<p style='color:#E74C3C;margin:6px 0 0;font-size:13px;font-weight:700;'>"
          + " • ".join(fus["reasons"]) + "</p>") if fus["reasons"] else ""
    st.markdown(f'<div class="{cls[0]}"><h3>{cls[1]} {cls[2]} — ثقة {fus["confidence"]}%</h3>{rh}</div>',
                unsafe_allow_html=True)

    v = fus["votes"]
    vc = st.columns(3)
    vc[0].metric("صاعد", f"{v.get('BULLISH', 0):.0f}%")
    vc[1].metric("هابط", f"{v.get('BEARISH', 0):.0f}%")
    vc[2].metric("حياد", f"{v.get('NEUTRAL', 0):.0f}%")

    st.markdown("### 🎯 السيناريوهات")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="fusion-card"><h4>صاعد</h4>'
                    '<p>• اختراق PDH<br>• تراجع العائد الحقيقي<br>'
                    '• MM Net متزايد<br><b>تأكيد:</b> إغلاق 4H فوق PDH<br>'
                    '<b>إبطال:</b> عودة تحته</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="fusion-card"><h4>هابط</h4>'
                    '<p>• كسر PDL<br>• ارتفاع العائد الحقيقي<br>'
                    '• MM Net متراجع<br><b>تأكيد:</b> إغلاق 4H تحت PDL<br>'
                    '<b>إبطال:</b> عودة فوقه</p></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔍 التحقق المتقاطع لسعر الذهب")
    all_src = mdata.get("gold", {}).get("all_sources", {})
    if all_src:
        rows = []
        for name, info in all_src.items():
            val = info.get("value")
            rows.append({"المصدر": name,
                         "الحالة": disp(info.get("status", "NO DATA")),
                         "القيمة": fnum(val, 2, " $") if val is not None else "—"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"المصدر المعتمد: **{mdata.get('gold', {}).get('verified_by', '—')}** • "
                   f"{mdata.get('gold', {}).get('detail', '')}")

def pg_sources():
    hero("تدقيق مصادر البيانات")
    rows = []
    for name, src, req_name in [
        ("الذهب", mdata["gold"], "XAUUSD (GC=F)"),
        ("الدولار", mdata["dxy"], "DXY"),
        ("العائد الاسمي", mdata["nominal"], "Treasury"),
        ("العائد الحقيقي", mdata["real_yield"], "Real 10Y"),
        ("COT Legacy", mdata["cot"], "Legacy"),
        ("COT Disaggregated", mdata["cot_disagg"], "Managed Money"),
        ("BLS", mdata["bls"], "CPI/Jobs"),
        ("BEA", mdata["bea"], "GDP/NIPA"),
    ]:
        rows.append({
            "المصدر": name, "المطلوب": req_name,
            "الحالة": disp(src.get("status", "NO DATA")),
            "القيمة": fnum(src.get("value"), 2) if src.get("value") is not None else "—",
            "تاريخ": src.get("observation_date", src.get("date", "—")),
            "جودة": f"{q_score(src)}/100",
            "التفصيل": src.get("detail", "—"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.metric("الجودة الإجمالية", f"{mdata['quality_score']}/100")

    st.divider()
    if st.button("🔍 فحص الوصول للمصادر الرسمية"):
        OFFICIAL = [
            ("CFTC", "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"),
            ("Fed", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"),
            ("BLS", "https://www.bls.gov/cpi/"),
            ("BEA", "https://www.bea.gov/"),
            ("Treasury", "https://home.treasury.gov/"),
            ("FRED", "https://fred.stlouisfed.org/"),
            ("Yahoo", "https://finance.yahoo.com/quote/GC=F"),
        ]
        out = []
        for nm, url in OFFICIAL:
            try:
                r = req(url)
                out.append({"المصدر": nm,
                            "الحالة": "🟢 متاح" if r.status_code < 400 else f"🔴 HTTP {r.status_code}",
                            "الرابط": url})
            except Exception as e:
                out.append({"المصدر": nm, "الحالة": f"🔴 {type(e).__name__}", "الرابط": url})
        st.dataframe(pd.DataFrame(out), use_container_width=True, hide_index=True)
        box_info("⚠️ <b>ملاحظة:</b> نجاح الاتصال <b>لا يعني</b> نجاح استخراج الأرقام.")

def pg_calendar():
    hero("الأجندة الاقتصادية")
    fk = sec("FRED_API_KEY")
    cal = calendar(fk)
    if cal.empty:
        box_warn("لا أجندة متاحة — تحقق من FRED_API_KEY أو من تواريخ FOMC.")
    else:
        st.dataframe(cal, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 📝 Consensus يدوي")
    with st.form("cons_form"):
        c1, c2, c3, c4 = st.columns(4)
        ev = c1.text_input("الحدث")
        co = c2.number_input("المتوقع", value=0.0)
        pv = c3.number_input("السابق", value=0.0)
        ac = c4.number_input("الفعلي", value=0.0)
        if st.form_submit_button("💾 حفظ") and ev:
            st.session_state.manual_consensus[ev] = {
                "event": ev, "consensus": co, "previous": pv,
                "actual": ac if ac != 0 else None}
            log("manual_input", "add_consensus", new_value=ev)
            st.success("تم الحفظ.")
    if st.session_state.manual_consensus:
        rows = []
        for e in st.session_state.manual_consensus.values():
            act = e.get("actual"); cons = e.get("consensus")
            if act is not None and cons is not None:
                diff = act - cons
                verdict = "⬜ مطابق" if abs(diff) < 1e-6 else (
                    f"📊 الفعلي أعلى ({diff:+.2f})" if diff > 0 else f"📊 الفعلي أقل ({diff:+.2f})")
            else:
                verdict = "⏳ في الانتظار"
            rows.append({"الحدث": e["event"], "المتوقع": cons,
                         "السابق": e.get("previous"), "الفعلي": act,
                         "التحليل": verdict})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def pg_econ():
    hero("التحليل الاقتصادي")
    ec = econ_engine(mdata)
    st.markdown(f"**التحيز:** {ec['bias']} • **الثقة:** {ec['confidence']}%")
    st.divider()
    st.markdown("### 📊 BLS")
    bls = mdata.get("bls", {}).get("series", {})
    if bls:
        rows = [{"المؤشر": s.get("label", k),
                 "المستوى": fnum(s.get("level"), 2),
                 "MoM": fnum(s.get("mom_pct"), 2),
                 "YoY": fnum(s.get("yoy_pct"), 2),
                 "التاريخ": s.get("date", "—"),
                 "الحالة": disp(s.get("status", "NO DATA"))} for k, s in bls.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        box_warn("بيانات BLS غير متاحة — تحقق من BLS_API_KEY.")
    st.divider()
    st.markdown("### 📊 FRED")
    fr = mdata.get("fred", {})
    if fr:
        rows = [{"السلسلة": k, "الوصف": v.get("label", k),
                 "القيمة": fnum(v.get("value"), 3),
                 "التاريخ": v.get("date", "—"),
                 "الحالة": disp(v.get("status", "NO DATA"))} for k, v in fr.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        box_warn("FRED غير مضبوط — أضف FRED_API_KEY.")
    st.divider()
    st.markdown("### 🔔 الإشارات")
    for s in ec["signals"]:
        st.markdown(f"- {s}")

def pg_yields():
    hero("العوائد والدولار")
    vals = mdata.get("nominal", {}).get("values", {})
    if vals:
        cols = st.columns(len(vals))
        for i, (k, v) in enumerate(sorted(vals.items())):
            cols[i].metric(k, fnum(v, 3, "%"))
    else:
        box_warn("منحنى العائد الاسمي غير متاح.")

    st.divider()
    c = st.columns(2)
    c[0].metric("Real 10Y", fnum(mdata.get("real_yield", {}).get("value"), 3, "%"))
    c[1].metric("Breakeven", fnum(mdata.get("breakeven", {}).get("value"), 2, "%"))

    st.divider()
    st.markdown("### 💵 مؤشر الدولار")
    d = mdata.get("dxy", {})
    dc = st.columns(3)
    dc[0].metric("DXY", fnum(d.get("value"), 2))
    dc[1].metric("التغير", f"{d.get('change', 0):+.2f}" if d.get("change") else "—")
    dc[2].metric("آخر تحديث", d.get("timestamp", "—"))

def pg_cot():
    hero("COT & Open Interest")
    st.markdown("### 📋 Disaggregated (Managed Money)")
    cot_d = mdata.get("cot_disagg", {})
    lt = cot_d.get("latest", {})
    if lt:
        cc = st.columns(4)
        cc[0].metric("MM Net", f"{lt.get('mm_net', 0):,.0f}")
        cc[1].metric("التغير الأسبوعي", f"{lt.get('mm_net_wow') or 0:+,.0f}")
        cc[2].metric("Swap Net", f"{lt.get('swap_net', 0):,.0f}")
        cc[3].metric("Open Interest", f"{lt.get('oi', 0):,.0f}")
        mm = lt.get("mm_net", 0)
        if mm > 150_000: st.success(f"MM صافي طويل بقوة ({mm:,.0f}).")
        elif mm < 50_000: st.info(f"MM محايد/قصير ({mm:,.0f}).")
        else: st.warning(f"MM في منطقة انتقالية ({mm:,.0f}).")
        hist = pd.DataFrame(cot_d.get("rows", []))
        if not hist.empty:
            cols = [c for c in ["date", "mm_net", "swap_net", "oi"] if c in hist.columns]
            st.dataframe(hist[cols], use_container_width=True, hide_index=True)
    else:
        box_warn("بيانات COT Disaggregated غير متاحة.")

    st.divider()
    st.markdown("### 📜 Legacy")
    cot = mdata.get("cot", {}); ll = cot.get("latest", {})
    if ll:
        cc = st.columns(4)
        cc[0].metric("Long", f"{ll.get('long', 0):,.0f}")
        cc[1].metric("Short", f"{ll.get('short', 0):,.0f}")
        cc[2].metric("Net", f"{ll.get('long', 0) - ll.get('short', 0):,.0f}")
        cc[3].metric("OI", f"{ll.get('oi', 0):,.0f}")
        hist = pd.DataFrame(cot.get("rows", []))
        if not hist.empty:
            cols = [c for c in ["date", "long", "short", "oi"] if c in hist.columns]
            st.dataframe(hist[cols], use_container_width=True, hide_index=True)
    else:
        box_warn("بيانات COT Legacy غير متاحة.")

def pg_smc():
    hero("SMC/ICT Analysis")
    s = smc_engine(ohlc)
    st.markdown(f"**البنية:** {s['structure']} • **التحيز:** {s['bias']}")
    if s["pdh"]:
        c = st.columns(3)
        c[0].metric("PDH", fnum(s["pdh"], 2))
        c[1].metric("PDL", fnum(s["pdl"], 2))
        c[2].metric("ATR(14)", fnum(s["atr"], 2))
    st.divider()
    for x in s["signals"]:
        st.markdown(f"- {x}")

def pg_tech():
    hero("المؤشرات الفنية")
    ind = indicators(ohlc.get("df"))
    if ind.get("status") != "OK":
        box_warn(ind.get("detail", "OHLC غير متاح.")); return
    c = st.columns(4)
    c[0].metric("ATR(14)", f"${ind['atr14']:.2f}")
    c[1].metric("Vol 20d", f"{ind['vol20']:.1f}%")
    c[2].metric("Vol 60d", f"{ind['vol60']:.1f}%")
    c[3].metric("الاتجاه", ind["trend"])
    c = st.columns(3)
    c[0].metric("BB Upper", f"${ind['bb_u']:.2f}")
    c[1].metric("BB Mid", f"${ind['bb_m']:.2f}")
    c[2].metric("BB Lower", f"${ind['bb_l']:.2f}")

def pg_consistency():
    hero("الاتساق بين المصادر")
    checks = consistency(mdata)
    rows = []
    for c in checks:
        flag = "🟢" if c["consistent"] else ("🔴" if c["consistent"] is False else "⚪")
        rows.append({"المقياس": c["metric"],
                     "A": f"{c['a']}={fnum(c['va'], 4)}",
                     "B": f"{c['b']}={fnum(c['vb'], 4)}",
                     "الحالة": flag,
                     "التفصيل": c["detail"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def pg_evidence():
    hero("مصفوفة الأدلة")
    fus = fusion(mdata, ohlc)
    ev = []
    for s in fus["econ"]["signals"]:
        ev.append({"الفئة": "اقتصادي", "الدليل": s, "الاتجاه": fus["econ"]["bias"]})
    for s in fus["smc"]["signals"]:
        ev.append({"الفئة": "SMC/ICT", "الدليل": s, "الاتجاه": fus["smc"]["bias"]})
    for s in fus["votes"]:
        ev.append({"الفئة": "تصويت", "الدليل": f"{s}: {fus['votes'][s]}%", "الاتجاه": s})
    if ev:
        st.dataframe(pd.DataFrame(ev), use_container_width=True, hide_index=True)
    st.markdown(f"**القرار:** {fus['final']} • **الثقة:** {fus['confidence']}%")

def pg_validator():
    hero("فاحص الصفقات")
    fus = fusion(mdata, ohlc)
    with st.form("vf"):
        d = st.selectbox("الاتجاه", ["LONG", "SHORT"])
        e = st.number_input("الدخول", value=float(active_gold or 0.0))
        sl = st.number_input("SL", value=0.0)
        tp = st.number_input("TP", value=0.0)
        if st.form_submit_button("🔍 فحص"):
            r = validate({"direction": d, "entry": e, "stop_loss": sl, "take_profit": tp},
                         fus, mdata)
            st.success("✅ يجتاز") if r["valid"] else st.error("🔴 لا يجتاز")
            for ic, msg, _ in r["checks"]:
                st.markdown(f"{ic} {msg}")

def pg_risk():
    hero("حاسبة المخاطر")
    with st.form("rf"):
        c = st.columns(2)
        bal = c[0].number_input("الرصيد ($)", value=10000.0)
        rp = c[0].number_input("المخاطرة %", value=1.0)
        e = c[0].number_input("الدخول ($)", value=float(active_gold or 0.0))
        sl = c[1].number_input("SL ($)", value=0.0)
        tp = c[1].number_input("TP ($)", value=0.0)
        cs = c[1].number_input("حجم العقد", value=100.0)
        if st.form_submit_button("📊 حساب"):
            r = risk_calc(bal, rp, e, sl, tp, cs)
            if "error" in r: st.error(r["error"])
            else:
                st.metric("المخاطرة", f"${r['risk']:,.2f}")
                cc = st.columns(3)
                cc[0].metric("حجم (لوت)", f"{r['lots']:.4f}")
                cc[1].metric("R:R", f"{r['rr']:.2f}")
                cc[2].metric("ربح متوقع", f"${r['profit']:,.2f}")

def pg_backtest():
    hero("Backtesting")
    box_warn("⚠️ إشارات سعرية فقط (BOS+ATR) مع slippage 0.5$. لا يشمل COT أو العوائد.")
    c = st.columns(3)
    rng = c[0].selectbox("الفترة", ["1y", "2y", "5y", "max"], index=1)
    slm = c[1].slider("ATR SL مضاعف", 0.5, 3.0, 1.5, 0.1)
    tpm = c[2].slider("ATR TP مضاعف", 1.0, 6.0, 3.0, 0.1)
    mb = st.slider("حد أقصى (شمعة) — 0 = مفتوح", 0, 200, 0, 10)
    if st.button("▶️ تشغيل"):
        with st.spinner("..."): o = gold_ohlc(rng, "1d")
        if o.get("df") is None:
            st.error("OHLC غير متاح."); return
        res = backtest(o["df"], slm, tpm, 20, 0.5, None if mb == 0 else mb)
        c = st.columns(4)
        c[0].metric("صفقات", res["total"])
        c[1].metric("نسبة الربح", f"{res['win_rate']}%")
        c[2].metric("Avg R", f"{res['avg_r']:+.2f}")
        c[3].metric("Max DD", f"{res['max_dd']:.1f}R")
        if res.get("trades"):
            t = pd.DataFrame(res["trades"])
            cols = [x for x in ["t", "dir", "e", "sl", "tp", "result", "bars"] if x in t.columns]
            st.dataframe(t[cols].tail(50), use_container_width=True, hide_index=True)

def pg_weekly():
    hero("التقرير الأسبوعي")
    if st.button("📝 توليد"):
        fus = fusion(mdata, ohlc)
        rep = [
            f"# 𓂀 Aho — تقرير الذهب الأسبوعي",
            f"**التوليد:** {utc()}",
            f"**المستخدم:** {current_user['username']} ({current_role})",
            "", "---", "", "## 1️⃣ الأسعار",
            f"- XAUUSD: {fnum(active_gold, 2, ' $')}",
            f"- DXY: {fnum(mdata['dxy'].get('value'), 2)}",
            f"- US 10Y: {fnum(mdata['nominal'].get('values', {}).get('10Y'), 3, '%')}",
            f"- Real 10Y: {fnum(mdata.get('real_yield', {}).get('value'), 3, '%')}",
            f"- Breakeven: {fnum(mdata.get('breakeven', {}).get('value'), 2, '%')}",
            "", "## 2️⃣ COT",
        ]
        cd = mdata.get("cot_disagg", {}).get("latest", {})
        if cd:
            rep.append(f"- MM Net: {cd.get('mm_net', 0):,.0f}")
            rep.append(f"- تغير WoW: {cd.get('mm_net_wow') or 0:+,.0f}")
        rep += ["", "## 3️⃣ الاقتصاد"]
        for k, lbl in [("headline_cpi", "CPI"), ("core_cpi", "Core CPI"),
                       ("unemployment", "البطالة"), ("nonfarm_payrolls", "الوظائف")]:
            s = mdata.get("bls", {}).get("series", {}).get(k, {})
            if s.get("level") is not None:
                line = f"- {lbl}: {fnum(s['level'], 2)}"
                if s.get("yoy_pct") is not None: line += f" • YoY {s['yoy_pct']:+.2f}%"
                rep.append(line)
        rep += ["", "## 4️⃣ الاتساق"]
        for c in consistency(mdata):
            ic = "🟢" if c["consistent"] else ("🔴" if c["consistent"] is False else "⚪")
            rep.append(f"- {ic} {c['metric']}: {c['detail']}")
        rep += ["", "## 5️⃣ الفيوجن",
                f"- التحيز: {fus['final']} • الثقة: {fus['confidence']}%",
                f"- جودة البيانات: {mdata.get('quality_score', 0)}/100"]
        if fus["reasons"]:
            rep.append(f"- أسباب NO TRADE: {' • '.join(fus['reasons'])}")
        rep += ["", "## 6️⃣ الإشارات"]
        for s in fus["econ"]["signals"]: rep.append(f"- {s}")
        for s in fus["smc"]["signals"]: rep.append(f"- {s}")
        rep.append(""); rep.append(f"*Aho𓂀 • {APP_VERSION}*")
        st.session_state.current_report = "\n".join(rep)
        log("report", "generate_weekly")
    if st.session_state.current_report:
        with st.expander("👁️ معاينة", expanded=True):
            st.markdown(st.session_state.current_report)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        if can_export():
            c = st.columns(2)
            c[0].download_button("⬇️ Markdown",
                                 data=st.session_state.current_report.encode("utf-8"),
                                 file_name=f"aho_weekly_{ts}.md", mime="text/markdown")
            csv = pd.DataFrame([{"date": utc()[:10], "gold": active_gold,
                                 "dxy": mdata["dxy"].get("value"),
                                 "quality": mdata.get("quality_score")}]).to_csv(index=False).encode("utf-8-sig")
            c[1].download_button("⬇️ CSV", data=csv,
                                 file_name=f"aho_weekly_{ts}.csv", mime="text/csv")
        if st.button("📤 إرسال عبر Telegram"):
            r = tg_send(st.session_state.current_report[:4000]); st.info(r["detail"])
        with st.form("em"):
            to = st.text_input("إرسال إلى (بريد)")
            if st.form_submit_button("📧 إرسال Email") and to:
                r = em_send(f"Aho Weekly {utc()}", st.session_state.current_report, to)
                st.info(r["detail"])
        if not can_export():
            box_info("🔒 دورك لا يسمح بالتصدير.")

def pg_history():
    hero("سجل التقارير")
    if st.button("💾 حفظ التقرير الحالي"):
        fus = fusion(mdata, ohlc)
        st.session_state.report_history.append({
            "time": utc(), "bias": fus["final"], "confidence": fus["confidence"],
            "quality": mdata["quality_score"], "gold": active_gold})
        log("report", "save_snapshot")
    if st.session_state.report_history:
        st.dataframe(pd.DataFrame(st.session_state.report_history[::-1]),
                     use_container_width=True, hide_index=True)
    else:
        box_info("لا تقارير محفوظة بعد.")

def pg_journal():
    hero("دفتر الصفقات")
    with st.form("jf"):
        c = st.columns(2)
        d = c[0].selectbox("الاتجاه", ["LONG", "SHORT"])
        e = c[0].number_input("الدخول", value=float(active_gold or 0.0))
        sl = c[0].number_input("SL", value=0.0)
        tp = c[1].number_input("TP", value=0.0)
        res = c[1].selectbox("النتيجة", ["OPEN", "WIN", "LOSS", "BE"])
        notes = st.text_area("ملاحظات")
        if st.form_submit_button("➕ إضافة") and can_export():
            st.session_state.trade_journal.append({
                "time": utc(), "direction": d, "entry": e,
                "sl": sl, "tp": tp, "result": res, "notes": notes})
            log("journal", "add_trade", new_value=f"{d}@{e}")
    if st.session_state.trade_journal:
        st.dataframe(pd.DataFrame(st.session_state.trade_journal[::-1]),
                     use_container_width=True, hide_index=True)
        w = sum(1 for t in st.session_state.trade_journal if t["result"] == "WIN")
        l = sum(1 for t in st.session_state.trade_journal if t["result"] == "LOSS")
        if w + l > 0:
            st.metric("نسبة الربح", f"{w/(w+l)*100:.1f}%")
    else:
        box_info("لا صفقات مسجلة.")

def pg_audit():
    if current_role not in {"admin", "auditor"}:
        st.error("🔒 هذه الصفحة للمدقق والمدير فقط."); return
    hero("سجل التدقيق")
    if not st.session_state.audit_log:
        box_info("لا سجلات بعد."); return
    df = pd.DataFrame(st.session_state.audit_log[::-1])
    st.dataframe(df, use_container_width=True, hide_index=True)
    if can_export():
        st.download_button("⬇️ CSV",
                           data=df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"aho_audit_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv")

def pg_admin():
    if current_role != "admin":
        st.error("🔒 للمدير فقط."); return
    hero("Admin")
    st.markdown("### حالة المفاتيح")
    keys = ["FRED_API_KEY", "BLS_API_KEY", "BEA_API_KEY",
            "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
            "GMAIL_USER", "GMAIL_APP_PASSWORD"]
    rows = [{"المفتاح": k, "الحالة": "🟢 مضبوط" if sec(k) else "🔴 مفقود"} for k in keys]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("### حالة المصادر")
    for name, s in [("Gold", mdata["gold"]), ("DXY", mdata["dxy"]),
                    ("Treasury", mdata["nominal"]), ("COT Legacy", mdata["cot"]),
                    ("COT Disagg", mdata["cot_disagg"]), ("BLS", mdata["bls"]),
                    ("BEA", mdata["bea"])]:
        st.markdown(f"- {name}: {disp(s.get('status', 'NO DATA'))}")
    st.metric("الجودة الإجمالية", f"{mdata['quality_score']}/100")
    if st.button("🧹 تصفير الكاش"): st.cache_data.clear(); st.rerun()

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown(
        '<div class="brand">'
        '<div class="brand-mark">𓂀</div>'
        '<div>'
        '<div class="brand-title">Aho𓂀 GOLD</div>'
        '<div class="brand-sub">GOLD INTELLIGENCE</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    tlabel = st.radio("المظهر", ["فاتح ☀️", "غامق 🌙"],
                      index=0 if st.session_state.theme == "light" else 1,
                      horizontal=True, key="theme_toggle")
    nt = "light" if "فاتح" in tlabel else "dark"
    if nt != st.session_state.theme:
        st.session_state.theme = nt
        st.rerun()

    st.divider()
    rl = {"admin": "🔑 مدير", "analyst": "📊 محلل",
          "auditor": "🔍 مدقق", "viewer": "👁️ قارئ"}.get(current_role, current_role)
    st.caption(f"**{current_user['username']}** • {rl}")
    c = st.columns(2)
    with c[0]:
        if st.button("↻ تحديث", key="sb_rf"):
            st.cache_data.clear(); st.rerun()
    with c[1]:
        if st.button("🚪 خروج", key="sb_lo"):
            log("auth", "logout")
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    st.divider()
    st.markdown("### 💰 السعر اليدوي")
    mi = st.text_input("سعر الذهب ($)",
                       value="" if st.session_state.manual_gold_price is None
                       else str(st.session_state.manual_gold_price))
    c = st.columns(2)
    with c[0]:
        if st.button("اعتماد"):
            try:
                p = float(mi)
                if p > 0:
                    st.session_state.manual_gold_price = p; st.rerun()
            except ValueError: st.error("رقم غير صحيح")
    with c[1]:
        if st.button("إلغاء"):
            st.session_state.manual_gold_price = None; st.rerun()
    st.caption(f"آخر تحديث: {mdata['tested_at']}")

# ================================================================
# UPDATE BANNER
# ================================================================
fresh_alerts = [a for a in new_alerts if not a["is_first"]]
if fresh_alerts:
    box_warn("🔔 <b>بيانات جديدة منذ آخر زيارة:</b><br>"
             + "<br>".join(f"• {a['source']}: {a['old']} → {a['new']}" for a in fresh_alerts))

# ================================================================
# NAVIGATION
# ================================================================
PAGE_DEFS = [
    ("dashboard",    pg_dashboard,   "لوحة القيادة",       ":material/dashboard:",      {"admin", "analyst", "viewer", "auditor"}),
    ("sources",      pg_sources,     "مصادر البيانات",     ":material/database:",       {"admin", "analyst", "viewer", "auditor"}),
    ("calendar",     pg_calendar,    "الأجندة الاقتصادية", ":material/calendar_month:", {"admin", "analyst", "viewer", "auditor"}),
    ("econ",         pg_econ,        "التحليل الاقتصادي",  ":material/trending_up:",    {"admin", "analyst", "viewer", "auditor"}),
    ("yields",       pg_yields,      "العوائد والدولار",   ":material/payments:",       {"admin", "analyst", "viewer", "auditor"}),
    ("cot",          pg_cot,         "COT & OI",           ":material/bar_chart:",      {"admin", "analyst", "viewer", "auditor"}),
    ("smc",          pg_smc,         "SMC/ICT",            ":material/architecture:",   {"admin", "analyst", "auditor"}),
    ("tech",         pg_tech,        "المؤشرات الفنية",    ":material/show_chart:",     {"admin", "analyst", "auditor"}),
    ("consistency",  pg_consistency, "الاتساق",            ":material/compare_arrows:", {"admin", "analyst", "viewer", "auditor"}),
    ("evidence",     pg_evidence,    "مصفوفة الأدلة",      ":material/grid_view:",      {"admin", "analyst", "auditor"}),
    ("validator",    pg_validator,   "فاحص الصفقات",       ":material/verified:",       {"admin", "analyst", "auditor"}),
    ("risk",         pg_risk,        "إدارة المخاطر",      ":material/shield:",         {"admin", "analyst", "auditor"}),
    ("backtest",     pg_backtest,    "Backtesting",        ":material/science:",        {"admin", "analyst", "auditor"}),
    ("weekly",       pg_weekly,      "التقرير الأسبوعي",   ":material/description:",    {"admin", "analyst"}),
    ("history",      pg_history,     "سجل التقارير",       ":material/history:",        {"admin", "analyst", "auditor"}),
    ("journal",      pg_journal,     "دفتر الصفقات",       ":material/menu_book:",      {"admin", "analyst", "auditor"}),
    ("audit",        pg_audit,       "سجل التدقيق",        ":material/search:",         {"admin", "auditor"}),
    ("admin",        pg_admin,       "Admin",              ":material/settings:",       {"admin"}),
]

pages = [st.Page(fn, title=t, icon=ic, url_path=k)
         for k, fn, t, ic, roles in PAGE_DEFS if current_role in roles]
if not pages:
    st.error("لا توجد صفحات متاحة لدورك الحالي."); st.stop()
st.navigation(pages, position="sidebar").run()

# ================================================================
# FOOTER
# ================================================================
st.divider()
st.caption(f"Aho𓂀 GOLD  •  {APP_VERSION}  •  {local_now()}")
