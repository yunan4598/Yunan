import os
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

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
    st.markdown(f'<div class="status"><span class="status-dot"></span> FRED: {"مُعدّ" if os.getenv("FRED_API_KEY", "").strip() else "مفتاح غير مضاف"}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="status"><span class="status-dot"></span> التقويم: {"مُعدّ" if read_secret("FINNHUB_API_KEY") else "غير متصل"}</div>', unsafe_allow_html=True)
    st.caption("البيانات غير المتصلة لا تُستبدل بأرقام تخمينية.")

st.markdown('''<div class="hero"><div class="eyebrow">MACROECONOMIC RESEARCH • XAUUSD</div><h1>مركز استخبارات الذهب</h1><p>من الأخبار الاقتصادية إلى العوائد الحقيقية والتمركز المؤسسي، ثم إلى سلوك السعر.</p><span class="pill">XAUUSD</span><span class="pill">FED & TREASURY</span><span class="pill">COT + OPEN INTEREST</span><span class="pill">PRICE ACTION</span></div>''', unsafe_allow_html=True)

now = datetime.now(ZoneInfo(timezone_name))
st.markdown(f'<div class="section-head"><h3>نظرة عامة</h3><span>وقت اللوحة: {now.strftime("%Y-%m-%d • %I:%M %p")} ({timezone_name})</span></div>', unsafe_allow_html=True)

fred_key = read_secret("FRED_API_KEY").strip()
finnhub_key = read_secret("FINNHUB_API_KEY").strip()

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

def get_calendar(api_key, start, end):
    url = "https://finnhub.io/api/v1/calendar/economic"
    params = {"token": api_key, "from": start.isoformat(), "to": end.isoformat()}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        events = data.get("economicCalendar", [])
    elif isinstance(data, list):
        events = data
    else:
        raise ValueError("صيغة رد التقويم غير متوقعة")
    return events

def num(v):
    try:
        if v is None or str(v).strip() in ("", "None", "nan"): return None
        return float(str(v).replace(",", ""))
    except (ValueError, TypeError): return None

def interpret_event(row):
    name = " ".join(str(row.get(k, "")) for k in ["Category", "Event", "event", "name"]).lower()
    actual = num(row.get("Actual", row.get("actual", row.get("ActualValue"))))
    forecast = num(row.get("Forecast", row.get("estimate", row.get("ForecastValue", row.get("TEForecast")))))
    if actual is None or forecast is None:
        return "المقارنة غير مكتملة؛ راقب رد فعل العوائد والدولار بعد صدور الخبر."
    diff = actual - forecast
    if abs(diff) < 1e-10: return "قريب من التوقع؛ راقب المراجعات ورد فعل السوق."
    inflation = any(x in name for x in ["cpi", "inflation", "pce", "price index"])
    jobs = any(x in name for x in ["nonfarm", "non-farm", "payroll", "employment change", "job creation"])
    unemp = "unemployment rate" in name
    claims = "jobless claims" in name or "initial claims" in name
    growth = any(x in name for x in ["gdp", "ism", "pmi", "retail sales"])
    stronger = diff > 0
    if inflation:
        return ("التضخم أعلى من التوقع؛ قد يضغط على الذهب إذا ارتفعت العوائد الحقيقية والدولار." if stronger else "التضخم أقل من التوقع؛ قد يدعم الذهب إذا تراجعت العوائد الحقيقية والدولار.")
    if jobs:
        return ("القراءة العددية أعلى من التوقع؛ افحص مكونات التقرير والمراجعات وتسعير الفائدة." if stronger else "القراءة العددية أقل من التوقع؛ افحص مكونات التقرير والمراجعات وتسعير الفائدة.")
    if unemp:
        return ("البطالة أعلى من التوقع؛ قد تعكس ضعف العمل، لكن يلزم تأكيد السوق." if stronger else "البطالة أقل من التوقع؛ قد تعكس قوة العمل، لكن يلزم تأكيد السوق.")
    if claims:
        return ("المطالبات أعلى من التوقع؛ قد تشير إلى ضعف سوق العمل." if stronger else "المطالبات أقل من التوقع؛ قد تشير إلى قوة سوق العمل.")
    if growth:
        return "مفاجأة في بيانات النمو؛ لا تحدد اتجاه الذهب قبل فحص العوائد والدولار."
    return "توجد مفاجأة رقمية؛ افحص طبيعة المؤشر والمراجعات ورد فعل السوق."

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

st.markdown('<div class="section-head"><h3>مكوّنات المنظومة</h3><span>واجهة أولية — حالة الربط موضحة لكل وحدة</span></div>', unsafe_allow_html=True)
t1,t2,t3,t4,t5=st.tabs(["التقويم الاقتصادي","العوائد والتضخم","COT و Open Interest","الدولار والذهب","منهجية القرار"])
with t1:
    st.markdown("#### الأخبار الأمريكية: الفعلي مقابل المتوقع والسابق")
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="card"><div class="card-label">الأولوية</div><div class="card-value gold">CPI / PCE</div><div class="card-foot">التضخم وتوقعات الفائدة</div></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="card"><div class="card-label">سوق العمل</div><div class="card-value">NFP / Claims</div><div class="card-foot">قوة التوظيف والأجور والبطالة</div></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="card"><div class="card-label">النمو والسياسة</div><div class="card-value">GDP / ISM / FOMC</div><div class="card-foot">النشاط الاقتصادي ومسار الفائدة</div></div>',unsafe_allow_html=True)
    today=date.today(); start=today-timedelta(days=days_back); end=today+timedelta(days=days_forward)
    if not finnhub_key:
        st.markdown('<div class="placeholder"><b>التقويم غير متصل بعد.</b><br>تحتاج هذه الوحدة إلى مفتاح Finnhub API صالح في إعدادات Secrets.</div>',unsafe_allow_html=True)
    else:
        try:
            events=get_calendar(finnhub_key,start,end)
            df=pd.DataFrame(events)
            if not df.empty:
                rename_map = {"time": "Date", "event": "Event", "actual": "Actual", "estimate": "Forecast", "prev": "Previous", "impact": "Importance", "country": "Country"}
                df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
                
                if "Country" in df.columns: 
                    df=df[df["Country"].astype(str).str.upper().isin(["US", "USA", "UNITED STATES"])]
                
                tz=ZoneInfo(timezone_name)
                def local_time(v):
                    try:
                        dt=datetime.fromisoformat(str(v).replace("Z","+00:00"))
                        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
                        return dt.astimezone(tz).strftime("%Y-%m-%d %I:%M %p")
                    except Exception: return str(v)
                
                if "Date" in df.columns: df["الوقت المحلي"]=df["Date"].apply(local_time)
                for col in ["Actual","Forecast","Previous"]:
                    if col not in df.columns: df[col]=""
                df["قراءة أولية"]=df.apply(interpret_event,axis=1)
                cols=[c for c in ["الوقت المحلي","Importance","Event","Actual","Forecast","Previous","قراءة أولية"] if c in df.columns]
                st.dataframe(df[cols],use_container_width=True,hide_index=True)
            else: st.info("لم يُرجع المزود أحداثًا في النطاق المختار.")
        except Exception as e: st.error(f"تعذر تحميل التقويم: {e}")
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
    st.markdown("#### تمركز العقود الآجلة")
    st.markdown('<div class="placeholder"><b>الوحدة مصممة ولم يتم ربطها بمصدر حي بعد.</b></div>',unsafe_allow_html=True)
with t4:
    st.markdown("#### DXY و XAUUSD")
    a,b=st.columns(2)
    with a: st.markdown('<div class="placeholder"><b>مؤشر الدولار DXY</b></div>',unsafe_allow_html=True)
    with b: st.markdown('<div class="placeholder"><b>السعر والبنية الفنية للذهب</b></div>',unsafe_allow_html=True)
with t5:
    st.markdown("#### ترتيب التحليل المعتمد")
    st.markdown("""
1. **COT — التحيز الأوسع**
2. **Open Interest — سياق المشاركة**
3. **التقويم الاقتصادي — المحفز والتوقيت**
4. **العوائد الاسمية والحقيقية وتعويض التضخم**
5. **DXY — التحقق من الدولار**
6. **Price Action والسيولة**
7. **قرار نهائي**
""")

if source_errors:
    with st.expander("أخطاء مصادر البيانات"):
        for err in source_errors: st.write(err)

st.divider()
st.markdown('<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#718096;font-size:11px"><span>YUNAN GOLD INTELLIGENCE · WEBSITE PROTOTYPE v1.0</span><span>مصادر غير متصلة = لا توجد أرقام مخمّنة · ليست توصية تداول</span></div>',unsafe_allow_html=True)
