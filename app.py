import os
import json
from datetime import datetime
import pytz
import pandas as pd
import streamlit as st

# --- إعداد التطبيق الأساسي ---
APP_NAME = "YUNAN GOLD INTELLIGENCE"
st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# --- الهوية البصرية المؤسسية ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { 
    --bg: #06090f; 
    --panel: #0d131d; 
    --line: #1e2c3d; 
    --gold: #d9b56d; 
    --green: #00e676; 
    --red: #ff5252;
    --muted: #8b9bb4; 
    --text: #eef2f7; 
}
html, body, [class*="css"] { font-family:'IBM Plex Sans Arabic','Inter',sans-serif; }
.stApp { background: radial-gradient(circle at 50% 0%, #111b29 0%, var(--bg) 60%); color: var(--text); }
.block-container { padding-top: 3.5rem !important; max-width: 1450px; }

[data-testid="stSidebar"] { background: #070b12; border-left: 1px solid var(--line); padding-top: 15px; }
[data-testid="stSidebar"] * { color: var(--text); }

.brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 16px; border-bottom: 1px solid var(--line); margin-bottom: 15px; }
.brand-mark { width: 42px; height: 42px; border: 1px solid #7a643b; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--gold); font-size: 21px; background: linear-gradient(145deg, #221c13, #0d121a); }
.brand-title { font-family: Inter, sans-serif; letter-spacing: 1.2px; font-weight: 800; font-size: 16px; color: #f4f0e7; }
.brand-sub { color: var(--muted); font-size: 11px; margin-top: 2px; }

.hero { border: 1px solid #233142; border-radius: 16px; padding: 20px 24px; background: linear-gradient(135deg, rgba(17,25,38,0.95), rgba(8,12,18,0.95)); margin-bottom: 18px; position: relative; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.eyebrow { color: var(--gold); letter-spacing: 2px; font-size: 11px; font-weight: 700; font-family: Inter, sans-serif; }
.hero h1 { margin: 6px 0 6px; font-size: 23px; color: #f7f5ef; font-weight: 700; }
.hero p { margin: 0; color: #9fb0c6; max-width: 820px; line-height: 1.7; font-size: 13.5px; }

div[data-testid="stMetric"] { background: linear-gradient(145deg, #0f1622, #0a0f17); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; }
div[data-testid="stMetric"] label { color: var(--muted)!important; font-size: 12px; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--gold)!important; font-size: 24px; font-weight: 700; }

.fusion-card { background: #0b111a; border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin-bottom: 15px; }
.fusion-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; margin-bottom: 8px; }
.badge-gold { background: rgba(217,181,109,0.15); color: var(--gold); border: 1px solid #544427; }
.badge-green { background: rgba(0,230,118,0.15); color: var(--green); border: 1px solid #135233; }

.stButton button { border-radius: 10px; border: 1px solid #d9b56d !important; background: linear-gradient(135deg, #d9b56d, #b3914a) !important; color: #06090f !important; font-weight: 800 !important; width: 100%; padding: 10px; }
.stButton button:hover { background: linear-gradient(135deg, #e6c37d, #c5a159) !important; color: #000000 !important; }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- إدارة الدخول ---
def read_secret(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value: return str(value)
    except Exception: pass
    return os.getenv(name, default)

APP_USERNAME = read_secret("APP_USERNAME")
APP_PASSWORD = read_secret("APP_PASSWORD")

if APP_USERNAME and APP_PASSWORD:
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>تسجيل الدخول المؤسسي</h1></div>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                import hmac
                if hmac.compare_digest(u.encode(), APP_USERNAME.encode()) and hmac.compare_digest(p.encode(), APP_PASSWORD.encode()):
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("بيانات غير صحيحة")
        st.stop()

# --- إدارة الذاكرة ---
if "synced_gold_price" not in st.session_state: st.session_state.synced_gold_price = 4186.67
if "trade_journal" not in st.session_state: st.session_state.trade_journal = []

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">INTELLIGENCE TERMINAL</div></div></div>', unsafe_allow_html=True)
    
    navigation = st.radio(
        "الوحدات الرئيسية للأنظمة:",
        [
            "محرك الذكاء الاقتصادي",
            "الفائدة الأمريكية والمفاجآت",
            "التمركز المؤسسي والسيولة",
            "فحص الصفقات وسلوك الجلسات",
            "مختبر الأداء وسجل الصفقات"
        ]
    )

    st.divider()
    manual_price = st.text_input("سعر الشارت الفعلي ($)", value=str(st.session_state.synced_gold_price))
    if st.button("تحديث السعر"):
        try:
            st.session_state.synced_gold_price = float(manual_price)
            st.success("تم تحديث السعر")
            st.rerun()
        except ValueError:
            st.error("رقم غير صحيح")

    st.caption(f"السعر المعتمد حالياً: {st.session_state.synced_gold_price} $")

active_gold = st.session_state.synced_gold_price

# --- 1. محرك الذكاء الاقتصادي ---
if navigation == "محرك الذكاء الاقتصادي":
    st.markdown('''<div class="hero"><div class="eyebrow">MACRO & FUSION ENGINE</div><h1>🧠 محرك الذكاء الاقتصادي للذهب (Gold Intelligence Engine)</h1><p>ربط محركات السوق بدلاً من اختزال التحليل. يوضح الأدلة المؤيدة والمعارضة والتفاصيل المسؤولة عن تحريك السعر حالياً.</p></div>''', unsafe_allow_html=True)

    st.markdown("### 📊 تحليل الأدلة المؤيدة والمعارضة للذهب (Evidence Matrix)")
    
    matrix_data = [
        {"العامل الاقتصادي / الفني": "العائد الحقيقي 10Y", "الحالة الحالية": "يرتفع (2.87%)", "التفسير المحتمل": "ضغط محتمل على الذهب", "التأثير على الاتجاه": "هبوطي 🔴"},
        {"العامل الاقتصادي / الفني": "مؤشر الدولار DXY", "الحالة الحالية": "يضعف (102.24)", "التفسير المحتمل": "دعم محتمل للذهب", "التأثير على الاتجاه": "صاعد 🟢"},
        {"العامل الاقتصادي / الفني": "تمركز COT المؤسسي", "الحالة الحالية": "تمركز شرائي مرتفع (+223.3K)", "التفسير المحتمل": "احتمال ازدحام المراكز الشرائية", "التأثير على الاتجاه": "محايد/تحذيري 🟡"},
        {"العامل الاقتصادي / الفني": "البنية الفنية (Price Action)", "الحالة الحالية": "صاعد على اليومي / إعادة اختبار", "التفسير المحتمل": "تجميع واستهاف سيولة القيعان", "التأثير على الاتجاه": "صاعد 🟢"}
    ]
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

    st.markdown("### 💡 الاستنتاج المؤسسي المحايد")
    st.info("⚖️ **النتيجة الحالية:** تضارب بين ارتفاع العوائد الحقيقية وتراجع الدولار؛ لذلك لا يُعتمد اتجاه أحادي دون انتظار سحب السيولة (Stop Run) عند افتتاح جلسة نيويورك.")

# --- 2. توقعات الفائدة والمفاجآت الاقتصادية ---
elif navigation == "الفائدة الأمريكية والمفاجآت":
    st.markdown('''<div class="hero"><div class="eyebrow">FED RATE & SURPRISE DETECTOR</div><h1>📊 لوحة توقعات الفائدة وكاشف المفاجآت الاقتصادية</h1><p>مراقبة قرارات الفيدرالي ومقارنة القراءات الفعلية للتضخم والوظائف بالتوقعات وقاعدة البيانات التاريخية.</p></div>''', unsafe_allow_html=True)

    col_fed1, col_fed2 = st.columns(2)
    with col_fed1:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-gold">توقعات الاجتماع القادم للفيدرالي</span>
            <h3 style="color:var(--gold); margin:5px 0;">82% خفض 25 نقطة أساس</h3>
            <p style="color:var(--muted); font-size:13px;">تراجع احتمالات التثبيت يدعم هبوط عوائد السندات قصيرة الأجل.</p>
        </div>''', unsafe_allow_html=True)
    with col_fed2:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-green">كاشف المفاجآت (Economic Surprise)</span>
            <h3 style="color:var(--green); margin:5px 0;">CPI أقل من التوقعات (-0.2%)</h3>
            <p style="color:var(--muted); font-size:13px;">المفاجأة أضعفت الدولار فورياً وأدت لارتفاع الذهب بـ 180 نقطة.</p>
        </div>''', unsafe_allow_html=True)

    st.markdown("### 🕵️ مقارنة القراءات الاقتصادية الأخيرة (Economic Surprise Table)")
    surprises = [
        {"الحدث الاقتصادي": "مؤشر أسعار المستهلك CPI", "الفعلية (Actual)": "2.9%", "التوقع (Forecast)": "3.1%", "السابقة (Previous)": "3.2%", "تأثير المفاجأة": "إيجابي للذهب 🟢"},
        {"الحدث الاقتصادي": "وظائف غير الزراعية NFP", "الفعلية (Actual)": "142K", "التوقع (Forecast)": "165K", "السابقة (Previous)": "114K", "تأثير المفاجأة": "إيجابي للذهب 🟢"},
        {"الحدث الاقتصادي": "مبيعات التجزئة Retail Sales", "الفعلية (Actual)": "0.1%", "التوقع (Forecast)": "0.3%", "السابقة (Previous)": "1.0%", "تأثير المفاجأة": "محايد 🟡"}
    ]
    st.dataframe(pd.DataFrame(surprises), use_container_width=True, hide_index=True)

# --- 3. التمركز المؤسسي والسيولة ---
elif navigation == "التمركز المؤسسي والسيولة":
    st.markdown('''<div class="hero"><div class="eyebrow">INSTITUTIONAL POSITIONING</div><h1>🏦 لوحة السيولة والتمركز المؤسسي (COT & Liquidity)</h1><p>متابعة تقارير COT الأسبوعية وتغير الفائدة المفتوحة (Open Interest) مع ربطها بمناطق السيولة الفنية.</p></div>''', unsafe_allow_html=True)

    col_cot1, col_cot2, col_cot3 = st.columns(3)
    with col_cot1: st.metric("صافي تمركز كبار كبار التجار (COT)", "+223,300 عقد", "+4,200 هذا الأسبوع")
    with col_cot2: st.metric("الفائدة المفتوحة (Open Interest)", "485,120 عقد", "-1.2% تغير أسبوعي")
    with col_cot3: st.metric("حجم التداول اليومي", "مستقر / طبيعي", "جلسة نيويورك")

    st.warning("⚠️ **تنبيه مؤسسي:** بيانات COT أسبوعية ومتأخرة نسبياً، واستخدامها يكون لتحديد التحيز الاستراتيجي وليس للتنفيذ اللحظي.")

# --- 4. فحص الصفقات وسلوك الجلسات ---
elif navigation == "فحص الصفقات وسلوك الجلسات":
    st.markdown('''<div class="hero"><div class="eyebrow">PRICE ACTION & VALIDATOR</div><h1>🎯 فحص الصفقات وسلوك الجلسات (Trade Setup Validator)</h1><p>فحص الشروط الفنية والمخاطر قبل الدخول لمنع القرارات العاطفية والتأكد من توافق الاتجاه.</p></div>''', unsafe_allow_html=True)

    with st.form("validator_form"):
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            h_trend = st.selectbox("الاتجاه على الفريم الكبير (Higher Timeframe):", ["صاعد صريح (Bullish Trend)", "هابط صريح (Bearish Trend)", "تذبذب عرضي (Range)"])
            sweep_status = st.selectbox("حالة سحب السيولة (Sweep):", ["تم سحب قيعان آسيا (Asia Low Sweep)", "تم سحب قمة يوم أمس (PDH Sweep)", "لم يتم سحب أي سيولة"])
        with col_v2:
            entry_model = st.selectbox("نموذج الدخول (Entry Model):", ["Order Block + Fair Value Gap (FVG)", "Displacement Breakout", "دخول عشوائي بدون نموذج"])
            risk_news = st.selectbox("القرب من الأخبار عالية التأثير:", ["لا توجد أخبار قريبة", "خبر مهم خلال أقل من 30 دقيقة"])

        submit_val = st.form_submit_button("إجراء الفحص المؤسسي لصفقتك")

    if submit_val:
        score = 0
        if "صاعد" in h_trend: score += 30
        if "Sweep" in sweep_status: score += 35
        if "Order Block" in entry_model: score += 35
        if "30 دقيقة" in risk_news: score -= 40

        st.divider()
        if score >= 70:
            st.success(f"✅ **VALID SETUP (صفقة صالحة للتنفيذ):** درجة التوافق {score}% عند سعر الشارت الحالي ({active_gold} $).")
        elif score >= 50:
            st.warning(f"🟡 **WAIT FOR CONFIRMATION (انتظر تأكيد إضافي):** درجة التوافق {score}%. تنبيه من تضارب الشروط.")
        else:
            st.error(f"🚫 **NO TRADE (تجنب الدخول):** درجة التوافق {score}%. المخاطرة عالية جداً ولا توجد شروط مكتملة.")

# --- 5. سجل الصفقات ومختبر الأداء ---
elif navigation == "مختبر الأداء وسجل الصفقات":
    st.markdown('''<div class="hero"><div class="eyebrow">PERFORMANCE LAB & JOURNAL</div><h1>🧪 سجل الصفقات ومختبر تقييم الأداء (Trading Journal)</h1><p>تسجيل كل فرصة وتحليل النتائج والتزامك بالخطة لمعرفة أي النماذج تحقق أعلى ربحية بكفاءة.</p></div>''', unsafe_allow_html=True)

    with st.form("journal_entry"):
        col_j1, col_j2, col_j3 = st.columns(3)
        with col_j1:
            j_date = st.date_input("تاريخ الصفقة")
            j_session = st.selectbox("الجلسة", ["London", "New York", "Asia"])
        with col_j2:
            j_type = st.selectbox("نوع الصفقة", ["شراء (Buy)", "بيع (Sell)"])
            j_price = st.text_input("سعر الدخول ($)", value=str(active_gold))
        with col_j3:
            j_sl = st.text_input("وقف الخسارة ($)")
            j_result = st.selectbox("النتيجة", ["ربح (Win)", "خسارة (Loss)", "تعادل (Break-Even)"])

        if st.form_submit_button("تسجيل الصفقة في السجل"):
            st.session_state.trade_journal.insert(0, {
                "التاريخ": str(j_date),
                "الجلسة": j_session,
                "النوع": j_type,
                "السعر": j_price,
                "النتيجة": j_result
            })
            st.success("تم الحفظ بنجاح!")
            st.rerun()

    if st.session_state.trade_journal:
        st.markdown("### 📋 الصفقات المسجلة")
        st.dataframe(pd.DataFrame(st.session_state.trade_journal), use_container_width=True, hide_index=True)

st.divider()
st.caption("YUNAN GOLD INTELLIGENCE v5.1 • STABLE DISPLAY FIX")
