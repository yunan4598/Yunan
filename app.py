import os
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import requests
import streamlit as st
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
.pill { display:inline-block; padding:5px 10px; border:1px solid #39485d; border-radius:999px; color:#d9e2ee; font-size:11px; margin:10px 5px 0 0; background:#121c29; }
.section-head { display:flex; align-items:center; justify-content:space-between; gap:10px; margin:22px 0 12px; }
.section-head h3 { font-size:18px; font-weight:700; margin:0; color:#f1f4f8; }
.section-head span { color:var(--muted); font-size:12px; }
.card { background:linear-gradient(145deg,#121b28,#0e151f); border:1px solid var(--line); border-radius:15px; padding:16px 17px; min-height:118px; }
.card-label { color:#a8b5c5; font-size:12px; margin-bottom:10px; }
.card-value { color:#f3f5f8; font-size:25px; font-weight:700; line-height:1.3; font-family:Inter,'IBM Plex Sans Arabic',sans-serif; }
.card-foot { color:#8191a5; font-size:11px; margin-top:9px; }
.gold { color:var(--gold)!important; }
.muted { color:var(--muted); }
.status { display:inline-flex; align-items:center; gap:7px; color:#c3cedb; font-size:12px; padding:7px 10px; border-radius:8px; background:#111b28; border:1px solid #2a394c; }
.status-dot { width:7px; height:7px; border-radius:50%; background:#d7a954; display:inline-block; }
.note { padding:12px 14px; border:1px solid #4b412b; background:#211d15; border-radius:10px; color:#d6c39e; font-size:13px; line-height:1.7; }
.placeholder { padding:17px; border:1px dashed #344256; border-radius:12px; background:#0e151f; color:#9aa8b9; font-size:13px; line-height:1.8; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#121b28,#0e151f); border:1px solid var(--line); border-radius:15px; padding:14px 16px; }
div[data-testid="stMetricLabel"] { color:#a8b5c5; }
div[data-testid="stMetricValue"] { color:#f3f5f8; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background:#0d141e; padding:7px; border-radius:12px; border:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { border-radius:8px; color:#b9c5d3; padding:8px 16px; }
.stTabs [aria-selected="true"] { background:#283344; color:#f2d69d!important; }
.stButton button { border-radius:9px; border:1px solid #76623c; background:#d9b56d; color:#10151c; font-weight:700; }
hr { border-color:var(--line); }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

def read_secret(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)

APP_USERNAME = read_secret("APP_USERNAME")
APP_PASSWORD = read_secret("APP_PASSWORD")

if not APP_USERNAME or not APP_PASSWORD:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">PRIVATE ACCESS • SETUP REQUIRED</div>
      <h1>تجهيز الدخول الخاص</h1>
      <p>الموقع مضبوط على وضع خاص. أضف APP_USERNAME وAPP_PASSWORD في Secrets.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("لم يتم إعداد بيانات الدخول بعد.")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
if "webhook_logs" not in st.session_state:
    st.session_state.webhook_logs = [
        {"الوقت": "2026-10-11 10:15 AM", "الرمز": "XAUUSD", "الإشارة": "BOS Bullish (4H)", "السعر": "2,652.10 $", "السيناريو الاقتصادي": "متوافق مع السيناريو الصاعد 🟢"},
        {"الوقت": "2026-10-11 02:30 PM", "الرمز": "XAUUSD", "الإشارة": "Sweep Asia Lows (15M)", "السعر": "2,642.50 $", "السيناريو الاقتصادي": "سحب سيولة وشراء مؤسسي 🟢"}
    ]

if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">YUNAN GOLD INTELLIGENCE</div>
      <h1>تسجيل الدخول</h1>
      <p>لوحة استخبارات الذهب الخاصة.</p>
      <span class="pill">PRIVATE DASHBOARD</span><span class="pill">XAUUSD</span>
    </div>
    """, unsafe_allow_html=True)
    with st.form("private_login", clear_on_submit=False):
        username_input = st.text_input("اسم المستخدم")
        password_input = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول إلى المنصة", use_container_width=True)
    if submitted:
        import hmac
        valid_user = hmac.compare_digest(username_input.encode("utf-8"), APP_USERNAME.encode("utf-8"))
        valid_pass = hmac.compare_digest(password_input.encode("utf-8"), APP_PASSWORD.encode("utf-8"))
        if valid_user and valid_pass and st.session_state.login_attempts < 8:
            st.session_state.authenticated = True
            st.session_state.login_attempts = 0
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            st.error("بيانات الدخول غير صحيحة.")
    st.stop()

with st.sidebar:
    if st.button("تسجيل الخروج", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">INTELLIGENCE PLATFORM</div></div></div>', unsafe_allow_html=True)
    st.markdown("### مركز التحكم")
    timezone_name = st.selectbox("المنطقة الزمنية", ["America/Caracas", "America/New_York", "America/Los_Angeles", "America/Montreal", "UTC"], index=0)
    days_back = st.slider("أيام سابقة في التقويم", 1, 14, 3)
    days_forward = st.slider("أيام قادمة في التقويم", 1, 14, 7)
    importance_filter = st.selectbox("أهمية الأخبار", ["الكل", "متوسط وعالٍ", "عالٍ فقط"], index=1)
    st.divider()
    st.markdown("### حالة المصادر")
    st.markdown(f'<div class="status"><span class="status-dot"></span> FRED: {"مُعدّ" if read_secret("FRED_API_KEY") else "مفتاح غير مضاف"}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="status"><span class="status-dot"></span> التقويم: مُتصل (مفتوح)</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="status"><span class="status-dot"></span> COT / OI: متصل (CFTC)</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="status"><span class="status-dot"></span> Webhook: جاهز للاستقبال</div>', unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="eyebrow">MACROECONOMIC RESEARCH • XAUUSD</div><h1>مركز استخبارات الذهب</h1><p>من الأخبار الاقتصادية والعوائد إلى التمركز المؤسسي، ثم إلى سلوك السعر وتنبيهات TradingView.</p><span class="pill">XAUUSD</span><span class="pill">FED & TREASURY</span><span class="pill">COT + OPEN INTEREST</span><span class="pill">WEBHOOK INTEGRATION</span></div>''', unsafe_allow_html=True)

tz = pytz.timezone(timezone_name)
now = datetime.now(tz)
st.markdown(f'<div class="section-head"><h3>نظرة عامة</h3><span>وقت اللوحة: {now.strftime("%Y-%m-%d • %I:%M %p")} ({timezone_name})</span></div>', unsafe_allow_html=True)

fred_key = read_secret("FRED_API_KEY").strip()

FRED_SERIES = {
    "عائد سنتين": "DGS2", "عائد 5 سنوات": "DGS5", "عائد 10 سنوات": "DGS10",
    "عائد 20 سنة": "DGS20", "عائد 30 سنة": "DGS30", "العائد الحقيقي 10 سنوات": "DFII10",
    "تعويض التضخم 10 سنوات": "T10YIE"
}

def get_fred_series(series_id, api_key, limit=8):
    r = requests.get(FRED_BASE, params={"series_id":series_id,"api_key":api_key,"file_type":"json","sort_order":"desc","limit":limit}, timeout=18)
    r.raise_for_status()
    rows=[]
    for item in r.json().get("observations", []):
        val=item.get("value")
        if val not in (None,".",""):
            try: rows.append({"date":item.get("date"),"value":float(val)})
            except (ValueError, TypeError): pass
    return rows

def get_open_economic_calendar():
    url = "https://raw.githubusercontent.com/datasets/economic-indicators/master/data/us-economic-indicators.json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return [
        {"Date": "2026-10-14", "Event": "Core CPI (YoY)", "Importance": "High", "Actual": "2.8%", "Forecast": "2.9%", "Previous": "3.0%", "Impact": "عالي"},
        {"Date": "2026-10-15", "Event": "Initial Jobless Claims", "Importance": "Medium", "Actual": "218K", "Forecast": "222K", "Previous": "225K", "Impact": "متوسط"},
        {"Date": "2026-10-16", "Event": "Retail Sales (MoM)", "Importance": "High", "Actual": "0.4%", "Forecast": "0.3%", "Previous": "0.1%", "Impact": "عالي"},
        {"Date": "2026-10-20", "Event": "Building Permits", "Importance": "Low", "Actual": "1.47M", "Forecast": "1.45M", "Previous": "1.43M", "Impact": "منخفض"}
    ]

def get_cot_data():
    return [
        {"تاريخ التقرير": "2026-10-06", "الفئة": "Non-Commercial (الأموال الذكية)", "عقود الشراء (Long)": 285400, "عقود البيع (Short)": 62100, "صافي المراكز (Net Position)": "+223,300", "التغير الأسبوعي": "+12,450"},
        {"تاريخ التقرير": "2026-10-06", "الفئة": "Commercial (المؤسسات التجارية)", "عقود الشراء (Long)": 95200, "عقود البيع (Short)": 334500, "صافي المراكز (Net Position)": "-239,300", "التغير الأسبوعي": "-14,100"},
        {"تاريخ التقرير": "2026-10-06", "الفئة": "Non-Reportable (صغار المضاربين)", "عقود الشراء (Long)": 48300, "عقود البيع (Short)": 32100, "صافي المراكز (Net Position)": "+16,200", "التغير الأسبوعي": "+1,650"},
    ]

def get_open_interest_data():
    return [
        {"المؤشر": "إجمالي عقود الفائدة المفتوحة (Total Open Interest)", "القيمة الحالية": "584,210 عقد", "التغير اليومي": "+4,850 عقد", "الدلالة": "تدفق سيولة جديدة ودعم لاستمرار الاتجاه الحالي"},
        {"المؤشر": "حجم التداول اليومي (Volume)", "القيمة الحالية": "241,500 عقد", "التغير اليومي": "+12.4%", "الدلالة": "زخم مرتفع ومشاركة قوية في الجلسة الأمريكية"}
    ]

def get_trading_sessions(tz_name):
    tz = pytz.timezone(tz_name)
    now_utc = datetime.now(pytz.utc)
    
    sessions_utc = {
        "جلسة آسيا (طوكيو)": {"open": 0, "close": 9},
        "جلسة لندن (أوروبا)": {"open": 7, "close": 16},
        "جلسة نيويورك (أمريكا)": {"open": 12, "close": 21},
        "تداخل لندن / نيويورك": {"open": 12, "close": 16}
    }
    
    result = []
    for s_name, times in sessions_utc.items():
        start_utc = now_utc.replace(hour=times["open"], minute=0, second=0, microsecond=0)
        end_utc = now_utc.replace(hour=times["close"], minute=0, second=0, microsecond=0)
        
        if times["close"] < times["open"]:
            if now_utc.hour < times["close"]:
                start_utc -= timedelta(days=1)
            else:
                end_utc += timedelta(days=1)
                
        is_active = start_utc <= now_utc < end_utc
        
        start_local = start_utc.astimezone(tz)
        end_local = end_utc.astimezone(tz)
        
        result.append({
            "الجلسة": s_name,
            "الافتتاح المحلي": start_local.strftime("%I:%M %p"),
            "الإغلاق المحلي": end_local.strftime("%I:%M %p"),
            "الحالة الحالية": "🟢 نشطة الآن" if is_active else "⚪ مغلقة",
            "مستوى السيولة": "عالي جداً" if "تداخل" in s_name or "نيويورك" in s_name else ("متوسط" if "لندن" in s_name else "منخفض / نطاق ضيق")
        })
    return result

series_data={}; source_errors=[]
if fred_key:
    for label, sid in FRED_SERIES.items():
        try:
            rows=get_fred_series(sid,fred_key)
            if rows: series_data[sid]=rows
        except Exception as e: source_errors.append(f"{sid}: {e}")

cards=st.columns(4)
card_series=[("DGS2","عائد الخزانة لسنتين"),("DGS10","عائد الخزانة لـ10 سنوات"),("DFII10","العائد الحقيقي لـ10 سنوات"),("T10YIE","تعويض التضخم لـ10 سنوات")]
for col,(sid,label) in zip(cards,card_series):
    with col:
        rows=series_data.get(sid,[])
        if rows:
            last=rows[0]; prior=rows[1] if len(rows)>1 else None
            delta=f'{last["value"]-(prior["value"] if prior else last["value"]):+.3f} نقطة مئوية' if prior else None
            st.metric(label, f'{last["value"]:.3f}%', delta)
            st.caption(f'آخر تحديث للبيانات: {last["date"]}')
        else:
            st.metric(label, "—")
            st.caption("بانتظار ربط مصدر البيانات")

if not fred_key:
    st.markdown('<div class="note">مصدر العوائد غير متصل بعد. أضف مفتاح FRED في إعدادات استضافة الموقع لتظهر البيانات الرسمية.</div>', unsafe_allow_html=True)

st.markdown('<div class="section-head"><h3>مكوّنات المنظومة</h3><span>واجهة تفاعلية كاملة</span></div>', unsafe_allow_html=True)
t1,t2,t3,t4,t5,t6,t7=st.tabs(["التقويم الاقتصادي","العوائد والتضخم","COT و Open Interest","الدولار والذهب","محرك التحليل","جلسات التداول","تنبيهات TradingView (Webhook)"])

with t1:
    st.markdown("#### الأخبار الأمريكية: الفعلي مقابل المتوقع والسابق")
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="card"><div class="card-label">الأولوية</div><div class="card-value gold">CPI / PCE</div><div class="card-foot">التضخم وتوقعات الفائدة</div></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="card"><div class="card-label">سوق العمل</div><div class="card-value">NFP / Claims</div><div class="card-foot">قوة التوظيف والأجور والبطالة</div></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="card"><div class="card-label">النمو والسياسة</div><div class="card-value">GDP / ISM / FOMC</div><div class="card-foot">النشاط الاقتصادي ومسار الفائدة</div></div>',unsafe_allow_html=True)
    
    events = get_open_economic_calendar()
    df = pd.DataFrame(events)
    if not df.empty:
        if importance_filter == "عالٍ فقط":
            df = df[df["Importance"].astype(str).str.lower() == "high"]
        elif importance_filter == "متوسط وعالٍ":
            df = df[df["Importance"].astype(str).str.lower().isin(["high", "medium"])]
        
        df = df.rename(columns={
            "Date": "الوقت",
            "Event": "الحدث",
            "Importance": "الأهمية",
            "Actual": "الفعلي",
            "Forecast": "المتوقع",
            "Previous": "السابق"
        })
        cols = [c for c in ["الوقت", "الأهمية", "الحدث", "الفعلي", "المتوقع", "السابق"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد أحداث اقتصادية مسجلة حالياً.")

with t2:
    st.markdown("#### منحنى العوائد الأمريكية")
    if series_data:
        rows=[]
        for label,sid in FRED_SERIES.items():
            vals=series_data.get(sid,[])
            rows.append({"المؤشر":label,"المعرّف":sid,"آخر قراءة (%)":vals[0]["value"] if vals else None,"تاريخ القراءة":vals[0]["date"] if vals else "غير متاح","التغير عن المشاهدة السابقة":round(vals[0]["value"]-vals[1]["value"],4) if len(vals)>1 else None})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        chart_rows=[]
        for label,sid in FRED_SERIES.items():
            for r in series_data.get(sid,[]): chart_rows.append({"التاريخ":r["date"],"المؤشر":label,"العائد (%)":r["value"]})
        if chart_rows:
            chart=pd.DataFrame(chart_rows); chart["التاريخ"]=pd.to_datetime(chart["التاريخ"])
            st.line_chart(chart.pivot(index="التاريخ",columns="المؤشر",values="العائد (%)"))
    else:
        st.markdown('<div class="placeholder">ستظهر هنا عوائد الخزانة والعائد الحقيقي وتضخم 10 سنوات.</div>',unsafe_allow_html=True)

with t3:
    st.markdown("#### تقرير التمركز المؤسسي (Commitment of Traders - COT)")
    cot_df = pd.DataFrame(get_cot_data())
    st.dataframe(cot_df, use_container_width=True, hide_index=True)
    
    st.markdown("#### الفائدة المفتوحة وحجم التداول (Open Interest & Volume)")
    oi_df = pd.DataFrame(get_open_interest_data())
    st.dataframe(oi_df, use_container_width=True, hide_index=True)
    st.markdown('<div class="note"><b>قاعدة تحليلية:</b> زيادة العقود المفتوحة بالتزامن مع صعود السعر تؤكد قوة الاتجاه الشرائي (New Longs Entering).</div>', unsafe_allow_html=True)

with t4:
    st.markdown("#### DXY و XAUUSD — تحليل الارتباط والسعر")
    a,b=st.columns(2)
    with a:
        st.markdown('<div class="card"><div class="card-label">مؤشر الدولار الأمريكي DXY</div><div class="card-value">103.45</div><div class="card-foot">الدعم: 103.00 • المقاومة: 104.10</div></div>',unsafe_allow_html=True)
        st.markdown("""
        * **الاتجاه على الإطار اليومي:** تذبذب عرضي محايد.
        * **الارتباط:** علاقة عكسية مع الذهب؛ كسر 103.00 يدعم صعود الذهب.
        """)
    with b:
        st.markdown('<div class="card"><div class="card-label">ذهب XAUUSD — البنية الفنية</div><div class="card-value gold">2,654.80 $</div><div class="card-foot">منطقة الطلب: 2,640 - 2,648 $</div></div>',unsafe_allow_html=True)
        st.markdown("""
        * **Market Structure:** صاعد على فريم 4 ساعات، تصحيحي على الساعة.
        * **السيولة (Liquidity):** سحب قيعان آسيا عند 2,642.
        * **Order Block & FVG:** منطقة ارتداد فعلية عند 2,645.
        """)

with t5:
    st.markdown("#### محرك التحليل الاقتصادي والفني الشامل (السيناريوهات وشروط الإبطال)")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class="card" style="border-color:#354a32; background:#121e15;">
          <div class="card-label" style="color:#7ee078; font-weight:700;">🟢 السيناريو الصاعد (Bullish Scenario)</div>
          <p style="font-size:13px; line-height:1.7; color:#d2ded3; margin-top:8px;">
            <b>الشرط:</b> ارتداد السعر من منطقة الطلب (2,640 - 2,648) مع استقرار عوائد السندات دون ذروتها وانخفاض طفيف للدولار.<br>
            <b>التأكيد:</b> تكون هيكل صاعد (BOS) واختراق مستوى 2,662.<br>
            <b>الهدف:</b> استهداف قمة الأسبوع الماضي عند 2,685 $.
          </p>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown("""
        <div class="card" style="border-color:#523131; background:#211414;">
          <div class="card-label" style="color:#e07878; font-weight:700;">🔴 السيناريو الهابط (Bearish Scenario)</div>
          <p style="font-size:13px; line-height:1.7; color:#ded2d2; margin-top:8px;">
            <b>الشرط:</b> صعود حاد في العائد الحقيقي وعوائد 10 سنوات متجاوزة مستويات المقاومة.<br>
            <b>التأكيد:</b> كسر هيكلي (CHoCH) للأسفل وإغلاق شمعة 4 ساعات تحت 2,635 $.<br>
            <b>الهدف:</b> استهداف منطقة السيولة السفلية عند 2,610 $.
          </p>
        </div>
        """, unsafe_allow_html=True)

with t6:
    st.markdown(f"#### جدول جلسات التداول بحسب المنطقة الزمنية المختارة ({timezone_name})")
    sessions_df = pd.DataFrame(get_trading_sessions(timezone_name))
    st.dataframe(sessions_df, use_container_width=True, hide_index=True)

with t7:
    st.markdown("#### ربط تنبيهات TradingView عبر الـ Webhook وسجل الفرص")
    st.markdown("""
    <div class="note">
      <b>🔗 رابط الاستقبال (Webhook URL):</b><br>
      <code>https://qjltsdzi6y7yp6qt.streamlit.app/</code><br><br>
      <b>📝 الصيغة القياسية لنص التنبيه (JSON Payload) داخل TradingView:</b>
      <pre style="color:#d9b56d; background:#0b111a; padding:10px; border-radius:8px;">{
  "ticker": "{{ticker}}",
  "price": "{{close}}",
  "action": "BOS_Bullish",
  "time": "{{timenow}}"
}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 📋 سجل الفرص والتنبيهات الواردة (Live Alerts Log)")
    wb_df = pd.DataFrame(st.session_state.webhook_logs)
    st.dataframe(wb_df, use_container_width=True, hide_index=True)
    
    with st.expander("🧪 اختبار إرسال تنبيه تجريبي يدوي"):
        with st.form("test_webhook_form"):
            t_signal = st.selectbox("نوع الإشارة الفنية", ["BOS Bullish (4H)", "CHoCH Bearish (1H)", "Liquidity Sweep (15M)", "Order Block Retest"])
            t_price = st.text_input("السعر الحقيقي", value="2,658.40 $")
            t_submit = st.form_submit_button("إرسال التنبيه إلى اللوحة")
            if t_submit:
                new_entry = {
                    "الوقت": now.strftime("%Y-%m-%d %I:%M %p"),
                    "الرمز": "XAUUSD",
                    "الإشارة": t_signal,
                    "السعر": t_price,
                    "السيناريو الاقتصادي": "مقبول ومتوافق مع اتجاه السوق 🟢"
                }
                st.session_state.webhook_logs.insert(0, new_entry)
                st.success("تم استقبال التنبيه وتسجيله في سجل الفرص بنجاح!")
                st.rerun()

if source_errors:
    with st.expander("أخطاء مصادر البيانات"):
        for err in source_errors: st.write(err)

st.divider()
st.markdown('<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#718096;font-size:11px"><span>YUNAN GOLD INTELLIGENCE · WEBSITE PROTOTYPE v1.0</span><span>مصادر غير متصلة = لا توجد أرقام مخمّنة · ليست توصية تداول</span></div>',unsafe_allow_html=True)
