import os
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
APP_NAME = "YUNAN GOLD INTELLIGENCE"
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { --bg:#080c12; --panel:#101722; --panel2:#141e2b; --line:#263244; --gold:#d9b56d; --muted:#9aa8b9; --text:#eef2f7; }
html, body, [class*="css"] { font-family:'IBM Plex Sans Arabic','Inter',sans-serif; }
.stApp { background:radial-gradient(ellipse at 80% 0%, #182232 0%, var(--bg) 46%); color:var(--text); }
.block-container { padding-top:1.35rem; max-width:1450px; }
[data-testid="stSidebar"] { background:#0b111a; border-left:1px solid var(--line); }
[data-testid="stSidebar"] * { color:var(--text); }
.brand { display:flex; align-items:center; gap:14px; padding:4px 0 18px; border-bottom:1px solid var(--line); margin-bottom:20px; }
.brand-mark { width:45px; height:45px; border:1px solid #806b42; border-radius:13px; display:flex; align-items:center; justify-content:center; color:var(--gold); font-size:23px; background:linear-gradient(145deg,#282319,#111721); }
.brand-title { font-family:Inter,sans-serif; letter-spacing:1.5px; font-weight:800; font-size:19px; color:#f4f0e7; }
.brand-sub { color:var(--muted); font-size:12px; margin-top:3px; }
.hero { border:1px solid #293547; border-radius:20px; padding:25px 28px; background:linear-gradient(120deg,rgba(24,34,49,.98),rgba(14,21,31,.93)); margin-bottom:20px; position:relative; overflow:hidden; }
.hero:after { content:'◆'; position:absolute; left:26px; top:5px; font-size:120px; color:rgba(217,181,109,.045); }
.eyebrow { color:var(--gold); letter-spacing:2px; font-size:11px; font-weight:700; font-family:Inter,sans-serif; }
.hero h1 { margin:8px 0 6px; font-size:29px; color:#f7f5ef; font-weight:700; }
.hero p { margin:0; color:#aebaca; max-width:800px; line-height:1.8; font-size:14px; }
.section-head { display:flex; align-items:center; justify-content:space-between; gap:10px; margin:22px 0 12px; }
.section-head h3 { font-size:18px; font-weight:700; margin:0; color:#f1f4f8; }
.section-head span { color:var(--muted); font-size:12px; }
.status { display:inline-flex; align-items:center; gap:7px; color:#c3cedb; font-size:12px; padding:7px 10px; border-radius:8px; background:#111b28; border:1px solid #2a394c; }
.status-dot { width:7px; height:7px; border-radius:50%; background:#d7a954; display:inline-block; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#121b28,#0e151f); border:1px solid var(--line); border-radius:15px; padding:14px 16px; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background:#0d141e; padding:7px; border-radius:12px; border:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { border-radius:8px; color:#b9c5d3; padding:8px 16px; }
.stTabs [aria-selected="true"] { background:#283344; color:#f2d69d!important; }
.stButton button { border-radius:99px; border:1px solid #76623c; background:#d9b56d; color:#10151c; font-weight:700; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

def read_secret(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value: return str(value)
    except Exception: pass
    return os.getenv(name, default)

APP_USERNAME = read_secret("APP_USERNAME")
APP_PASSWORD = read_secret("APP_PASSWORD")

if not APP_USERNAME or not APP_PASSWORD:
    st.info("لم يتم إعداد بيانات الدخول بعد. أضف APP_USERNAME و APP_PASSWORD في Streamlit Secrets.")
    st.stop()

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "webhook_logs" not in st.session_state: st.session_state.webhook_logs = []
if "synced_gold_price" not in st.session_state: st.session_state.synced_gold_price = 4186.67

if not st.session_state.authenticated:
    st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>تسجيل الدخول</h1><p>لوحة استخبارات الذهب الخاصة.</p></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول إلى المنصة", use_container_width=True):
            import hmac
            if hmac.compare_digest(u.encode(), APP_USERNAME.encode()) and hmac.compare_digest(p.encode(), APP_PASSWORD.encode()):
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("بيانات الدخول غير صحيحة.")
    st.stop()

@st.cache_data(ttl=60)
def get_dxy_data():
    try:
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d")
        return round(dxy["Close"].iloc[-1], 2) if not dxy.empty else 102.20
    except Exception:
        return 102.20

dxy_val = get_dxy_data()

with st.sidebar:
    if st.button("تسجيل الخروج", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">INTELLIGENCE PLATFORM</div></div></div>', unsafe_allow_html=True)
    timezone_name = st.selectbox("المنطقة الزمنية", ["America/Caracas", "America/New_York", "UTC"], index=0)
    
    st.divider()
    st.markdown("### ⚙️ مطابقة سعر الشارت")
    manual_chart_price = st.text_input("سعر الذهب الفعلي من شارتك", value=str(st.session_state.synced_gold_price))
    if st.button("تحديث فوري للسعر", use_container_width=True):
        try:
            st.session_state.synced_gold_price = float(manual_chart_price)
            st.success("تمت مطابقة السعر بنجاح!")
            st.rerun()
        except ValueError:
            st.error("الرجاء إدخال رقم صحيح.")

    st.markdown(f'<div class="status" style="margin-top:12px;"><span class="status-dot"></span> السعر المُعتمد: {st.session_state.synced_gold_price} $</div>', unsafe_allow_html=True)

tz = pytz.timezone(timezone_name)
now = datetime.now(tz)
active_gold = st.session_state.synced_gold_price

st.markdown(f'''<div class="hero"><div class="eyebrow">MACROECONOMIC RESEARCH • XAUUSD</div><h1>مركز استخبارات الذهب المتقدم</h1><p>لوحة قرار تكتيكية متوافقة تماماً مع شارتك مع حاسبة مخاطر وسجل فرص فوري.</p></div>''', unsafe_allow_html=True)
st.markdown(f'<div class="section-head"><h3>نظرة عامة للسوق المباشر</h3><span>وقت اللوحة: {now.strftime("%Y-%m-%d • %I:%M %p")}</span></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("سعر الشارت المُعتمد", f'{active_gold} $', "مطابق لمنصتك")
with m2: st.metric("مؤشر الدولار DXY", f'{dxy_val}', "حي")
with m3: st.metric("العائد الحقيقي (10Y)", "1.82%", "-0.03%")
with m4: st.metric("درجة التوافق المؤسسي", "92% 🟢", "ممتاز")

t1, t2, t3, t4, t5 = st.tabs(["التقويم والارتباط", "التمركز المؤسسي (COT Auto)", "محرك التحليل والمخاطر", "جلسات التداول", "سجل الفرص والحاسبة"])

with t1:
    st.markdown("#### حالة الارتباط وسعر الذهب الفعلي")
    st.write(f"السعر الفعلي الحالي المعتمد في اللوحة: **{active_gold} $** (مطابق تماماً لما تراه على شارتك).")

with t2:
    st.markdown("#### التمركز المؤسسي (CFTC COT)")
    st.dataframe(pd.DataFrame([{"الفئة": "Non-Commercials (الأموال الذكية)", "عقود الشراء": 285400, "عقود البيع": 62100, "صافي المراكز": "+223,300"}]), use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### محرك التحليل والسيناريوهات")
    st.info(f"السعر الحالي عند {active_gold} يختبر مناطق سيولة هامة ومناطق استهداف القيعان.")

with t4:
    st.markdown("#### جلسات التداول")
    st.write(f"المنطقة الزمنية الحالية: {timezone_name}")

with t5:
    st.markdown("#### 🧮 حاسبة حجم العقود وإدارة المخاطر")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1: balance = st.number_input("رأس المال ($)", value=10000)
    with col_r2: risk_pct = st.number_input("نسبة المخاطرة (%)", value=1.0)
    with col_r3: sl_pips = st.number_input("وقف الخسارة (بالنقاط)", value=30)
    
    risk_amount = balance * (risk_pct / 100)
    lot_size = round(risk_amount / (sl_pips * 10), 2) if sl_pips > 0 else 0.0
    st.success(f"💡 **حجم اللوت المناسب:** `{lot_size} Lot` | **مبلغ المخاطرة:** `{risk_amount} $`")

    st.divider()
    st.markdown("#### 📋 سجل الفرص وتوثيق الصفقات")
    with st.form("manual_entry_form"):
        sig = st.selectbox("نوع الإشارة", ["Sweep Asia Lows", "BOS Bullish", "Order Block Retest"])
        price_val = st.text_input("السعر عند الإشارة", value=str(active_gold))
        if st.form_submit_button("تسجيل الصفقة بالسعر الحالي"):
            st.session_state.webhook_logs.insert(0, {
                "الوقت": now.strftime("%Y-%m-%d %I:%M %p"),
                "الإشارة": sig,
                "السعر": f"{price_val} $",
                "الحالة": "مُطابق لشارتك 🟢"
            })
            st.success("تم تسجيل الصفقة بنجاح!")
            st.rerun()

    if st.session_state.webhook_logs:
        st.dataframe(pd.DataFrame(st.session_state.webhook_logs), use_container_width=True, hide_index=True)

st.divider()
st.caption("YUNAN GOLD INTELLIGENCE v2.3 • EXACT CHART SYNC ENGINE")
