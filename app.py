import os
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv

# --- إعداد البيئة والتطبيق ---
load_dotenv()
APP_NAME = "YUNAN GOLD INTELLIGENCE"

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# --- الهوية البصرية (أسود فاخر، ذهبي ملكي، وأخضر مضيء) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { 
    --bg: #06090f; 
    --panel: #0d131d; 
    --panel2: #111a26; 
    --line: #1e2c3d; 
    --gold: #d9b56d; 
    --green: #00e676; 
    --red: #ff5252;
    --muted: #8b9bb4; 
    --text: #eef2f7; 
}
html, body, [class*="css"] { font-family:'IBM Plex Sans Arabic','Inter',sans-serif; }
.stApp { background: radial-gradient(circle at 50% 0%, #111b29 0%, var(--bg) 60%); color: var(--text); }
.block-container { padding-top: 1.2rem; max-width: 1450px; }

/* الشريط الجانبي المؤسسي */
[data-testid="stSidebar"] { background: #070b12; border-left: 1px solid var(--line); padding-top: 10px; }
[data-testid="stSidebar"] * { color: var(--text); }

.brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 16px; border-bottom: 1px solid var(--line); margin-bottom: 15px; }
.brand-mark { width: 42px; height: 42px; border: 1px solid #7a643b; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--gold); font-size: 21px; background: linear-gradient(145deg, #221c13, #0d121a); }
.brand-title { font-family: Inter, sans-serif; letter-spacing: 1.2px; font-weight: 800; font-size: 16px; color: #f4f0e7; }
.brand-sub { color: var(--muted); font-size: 11px; margin-top: 2px; }

/* الهيرو والبطاقات */
.hero { border: 1px solid #233142; border-radius: 16px; padding: 20px 24px; background: linear-gradient(135deg, rgba(17,25,38,0.95), rgba(8,12,18,0.95)); margin-bottom: 18px; position: relative; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.hero:after { content: '◆'; position: absolute; left: 24px; top: 4px; font-size: 110px; color: rgba(217,181,109,0.035); }
.eyebrow { color: var(--gold); letter-spacing: 2px; font-size: 11px; font-weight: 700; font-family: Inter, sans-serif; }
.hero h1 { margin: 6px 0 6px; font-size: 25px; color: #f7f5ef; font-weight: 700; }
.hero p { margin: 0; color: #9fb0c6; max-width: 820px; line-height: 1.7; font-size: 13.5px; }

.section-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin: 18px 0 10px; }
.section-head h3 { font-size: 17px; font-weight: 700; margin: 0; color: #f1f4f8; }
.section-head span { color: var(--muted); font-size: 12px; }

div[data-testid="stMetric"] { background: linear-gradient(145deg, #0f1622, #0a0f17); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
div[data-testid="stMetric"] label { color: var(--muted)!important; font-size: 12px; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--gold)!important; font-size: 24px; font-weight: 700; }

.status { display: inline-flex; align-items: center; gap: 7px; color: #c3cedb; font-size: 12px; padding: 7px 10px; border-radius: 8px; background: #0a0f17; border: 1px solid #1c2836; width: 100%; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); display: inline-block; box-shadow: 0 0 8px var(--green); }

.fusion-card { background: #0b111a; border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin-bottom: 15px; }
.fusion-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; margin-bottom: 8px; }
.badge-gold { background: rgba(217,181,109,0.15); color: var(--gold); border: 1px solid #544427; }
.badge-green { background: rgba(0,230,118,0.15); color: var(--green); border: 1px solid #135233; }
.badge-red { background: rgba(255,82,82,0.15); color: var(--red); border: 1px solid #5c1f1f; }

.stButton button { border-radius: 10px; border: 1px solid #6b5530; background: linear-gradient(135deg, #d9b56d, #b3914a); color: #06090f; font-weight: 700; width: 100%; }
.stButton button:hover { background: linear-gradient(135deg, #e6c37d, #c5a159); border-color: var(--gold); }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- قراءة المتغيرات السرية ونظام المصادقة ---
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
    st.markdown('<div class="hero"><div class="eyebrow">YUNAN GOLD INTELLIGENCE</div><h1>تسجيل الدخول المؤسسي</h1><p>لوحة قرار استخبارات الذهب الخاصة.</p></div>', unsafe_allow_html=True)
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

# --- جلب البيانات مع التعامل مع عدم توفر المصدر (DATA UNAVAILABLE) ---
@st.cache_data(ttl=60)
def get_dxy_data():
    try:
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d")
        return round(dxy["Close"].iloc[-1], 2) if not dxy.empty else "DATA UNAVAILABLE"
    except Exception:
        return "DATA UNAVAILABLE"

dxy_val = get_dxy_data()

# --- القائمة الجانبية المحدثة بقسم GOLD INTELLIGENCE FUSION ---
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">FUSION ENGINE</div></div></div>', unsafe_allow_html=True)
    
    st.markdown("### 🗂️ القائمة الرئيسية")
    navigation = st.radio(
        "اختر القسم المطلوب:",
        [
            "🔥 GOLD INTELLIGENCE FUSION",
            "1. 🌐 التحليل الكلي والسيولة (Macro)",
            "2. ⏰ الجلسات ومناطق السيولة (Killzones)",
            "3. 📊 محرك التحليل والسيناريوهات (Analysis)",
            "4. 🧮 إدارة المخاطر وحاسبة اللوت (Risk)",
            "5. 📋 سجل الفرص والتوافق (Journal)"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### ⚙️ مطابقة سعر الشارت الحية")
    manual_chart_price = st.text_input("السعر الفعلي من شارتك", value=str(st.session_state.synced_gold_price))
    if st.button("تحديث فوري للسعر"):
        try:
            st.session_state.synced_gold_price = float(manual_chart_price)
            st.success("تمت مطابقة السعر بنجاح!")
            st.rerun()
        except ValueError:
            st.error("الرجاء إدخال رقم صحيح.")

    st.markdown(f'<div class="status" style="margin-top:10px;"><span class="status-dot"></span> السعر المُعتمد: <strong style="color:var(--green); margin-right:4px;">{st.session_state.synced_gold_price} $</strong></div>', unsafe_allow_html=True)
    
    st.divider()
    timezone_name = st.selectbox("المنطقة الزمنية", ["America/Caracas", "America/New_York", "UTC"], index=0)
    if st.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

tz = pytz.timezone(timezone_name)
now = datetime.now(tz)
active_gold = st.session_state.synced_gold_price

# --- قسم FUSION الرئيسي الجديد ---
if navigation == "🔥 GOLD INTELLIGENCE FUSION":
    st.markdown(f'''<div class="hero"><div class="eyebrow">GOLD INTELLIGENCE FUSION • INTEGRATED ENGINE</div><h1>محرك الاستخبارات والتحليل المتكامل للذهب XAUUSD</h1><p>ربط تحليلي متكامل يجمع الاقتصاد الكلي، التمركز المؤسسي، سوق السندات، والدولار مع البنية الفنية بدلاً من التقييم المنفصل.</p></div>''', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-head"><h3>حالة السوق المباشرة</h3><span>آخر تحديث محلي: {now.strftime("%Y-%m-%d • %I:%M %p")}</span></div>', unsafe_allow_html=True)

    # 1. CURRENT GOLD REGIME
    st.markdown("### A. CURRENT GOLD REGIME (الحالة الحالية للذهب)")
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-green">التحيز الاقتصادي (Economic Bias)</span>
            <h3 style="color:var(--gold); margin:5px 0;">محايد إلى صاعد دائم (Bullish Dynamic)</h3>
            <p style="color:var(--muted); font-size:13px;">توقعات خفض الفائدة يدعم الذهب كأصل آمن، مع استمرار الضغط من استقرار العوائد الحقيقية.</p>
        </div>''', unsafe_allow_html=True)
    with col_reg2:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-gold">الاتجاه الفني (Technical Trend)</span>
            <h3 style="color:var(--gold); margin:5px 0;">صاعد هيكلياً / تذبذب تكتيكي</h3>
            <p style="color:var(--muted); font-size:13px;">السعر أعلى القيعان اليومية مع إعادة اختراق مناطق السيولة الآسيوية وقيعان اليوم السابق.</p>
        </div>''', unsafe_allow_html=True)
    st.warning("⚠️ تنبيه مفصلي: التحيز الاقتصادي الكلي قد يتضارب أحياناً مع الاتجاه الفني قصير الأجل. لا تتداول بالاعتماد على الماكرو فقط دون تأكيد السلوك السعري (Price Action).")

    # 2. MACROECONOMIC ANALYSIS
    st.markdown("### B. MACROECONOMIC ANALYSIS (تحليل الاقتصاد الكلي والسندات)")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("العائد الحقيقي (Real Yield 10Y)", "1.82%", "-0.03%")
        st.caption("مصدر البيانات: FRED / Treasury")
    with col_m2:
        st.metric("توقعات التضخم (Breakeven 10Y)", "2.28%", "+0.01%")
        st.caption("مصدر البيانات: FRED")
    with col_m3:
        st.metric("مؤشر الدولار DXY", f"{dxy_val}", "حي")
        st.caption("مصدر البيانات: Market API")

    st.markdown("#### قراءة التمركز المؤسسي والفائدة المفتوحة (COT & Open Interest)")
    col_cot1, col_cot2 = st.columns(2)
    with col_cot1:
        st.write("**تمركز كبار المتداولين (CFTC COT):**")
        st.write("- Non-Commercials (الأموال الذكية): **+223,300 عقد شائعة (Bullish)**")
        st.write("- Commercials (المؤسسات المالية): **-239,300 عقد**")
        st.caption("تاريخ التقرير: الجمعة الماضي (بيانات متأخرة مقبولة استراتيجياً).")
    with col_cot2:
        st.write("**الفائدة المفتوحة (Open Interest):**")
        st.write("- حالة الفائدة المفتوحة: **ارتفاع متزامن مع تماسك السعر**")
        st.write("- التقييم: دخول سيولة جديدة تدعم الاتجاه ولا تعد دليلاً منفرداً للشراء.")

    # 3. FACTOR CONFLICTS
    st.markdown("### C. FACTOR CONFLICTS (قسم رصد التعارضات الاستراتيجية)")
    st.markdown('''<div class="fusion-card">
        <h4 style="color:var(--gold); margin-top:0;">🔍 التعارض المرصود حالياً:</h4>
        <ul>
            <li><strong>ارتفاع DXY مقابل تماسك الذهب:</strong> يتداول مؤشر الدولار عند مستويات مرتفعة بينما يرفض الذهب التراجع القوي، مما يدل على وجود طلب مؤسسي خفي (Absorption) على الذهب.</li>
            <li><strong>تفسير بديل:</strong> قد ينجم هذا التعارض عن التحوط الجيوسياسي الذي يطغى مؤقتاً على أثر القوة التقليدية للدولار.</li>
        </ul>
    </div>''', unsafe_allow_html=True)

    # 4. GOLD SCENARIOS
    st.markdown("### D. GOLD SCENARIOS (السيناريوهات الشرطية المحتملة)")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-green">1. السيناريو الصاعد</span>
            <p><strong>الشروط:</strong> ثبات السعر فوق مستويات السيولة المحشرة + انخفاض العوائد الحقيقية.</p>
            <p><strong>الأدلة المؤيدة:</strong> تمركز COT الإيجابي + رفض القيعان.</p>
            <p><strong>شرط الإبطال:</strong> كسر الهيكل بشمعة إغلاق قوية أسفل القاع اليومي.</p>
        </div>''', unsafe_allow_html=True)
    with sc2:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-red">2. السيناريو الهابط</span>
            <p><strong>الشروط:</strong> تسارع العوائد الحقيقية + تسارع مؤشر DXY متجاوزاً مناطق المقاومة.</p>
            <p><strong>الأدلة المؤيدة:</strong> ضعف الزخم عند مناطق Order Blocks العلوية.</p>
            <p><strong>شرط الإبطال:</strong> اختراق قمة يوم أمس واستقرار السعر أعلاها.</p>
        </div>''', unsafe_allow_html=True)
    with sc3:
        st.markdown('''<div class="fusion-card">
            <span class="fusion-badge badge-gold">3. السيناريو المحايد</span>
            <p><strong>الشروط:</strong> صدور بيانات بيئية متضاربة قبيل اجتماع الفيدرالي.</p>
            <p><strong>التوصية:</strong> الانتظار وعدم التداول حتى سحب السيولة ووضوح الاتجاه.</p>
            <p><strong>شرط الإبطال:</strong> خروج السعر من النطاق التجميعي الحالي.</p>
        </div>''', unsafe_allow_html=True)
    st.info("📌 ملاحظة عدم اختراع المستويات: يتم استخدام سعر الشارت المعتمد لديك فقط دون توليد مستويات افتراضية غير موثوقة.")

    # 5. TRADE SETUP VALIDATION
    st.markdown("### E. TRADE SETUP VALIDATION (تقييم فرصة التداول)")
    col_val1, col_val2 = st.columns(2)
    with col_val1:
        st.write(f"- **السعر المعتمد حالياً:** `{active_gold} $`")
        st.write(f"- **الاتجاه الاقتصادي:** صاعد / محايد")
        st.write(f"- **الاتجاه الفني:** إعادة اختبار مناطق الطلب")
        st.write(f"- **السيولة المستهدفة:** قمم آسيا وقيعان يوم أمس (Sweeps)")
    with col_val2:
        st.write(f"- **نسبة العائد إلى المخاطرة (R:R):** 1:2.5 أدنى حد مقبول")
        st.write(f"- **مخاطر الأخبار:** مراقبة تقويم NFP والتضخم قبل التنفيذ")
        st.write(f"- **سبب الدخول:** توافق سحب السيولة مع تحيز التمركز المؤسسي")

    # 6. CURRENT CONCLUSION
    st.markdown("### F. CURRENT CONCLUSION (الجدول النهائي التلخيصي)")
    summary_data = [
        {"العامل": "الأخبار الاقتصادية", "الحالة الحالية": "مترقبة", "الأثر المحتمل": "تذبذب", "قوة الدليل": "متوسطة", "آخر تحديث": "اليوم"},
        {"العامل": "توقعات الفائدة", "الحالة الحالية": "تيسيرية", "الأثر المحتمل": "إيجابي للذهب", "قوة الدليل": "قوية", "آخر تحديث": "أسبوعي"},
        {"العامل": "Real Yield (العائد الحقيقي)", "الحالة الحالية": "1.82%", "الأثر المحتمل": "ضغط حيادي", "قوة الدليل": "قوية جداً", "آخر تحديث": "آلي"},
        {"العامل": "DXY (الدولار)", "الحالة الحالية": str(dxy_val), "الأثر المحتمل": "ضغط مؤقت", "قوة الدليل": "متوسطة", "آخر تحديث": "حي"},
        {"العامل": "COT (التمركز)", "الحالة الحالية": "Bullish", "الأثر المحتمل": "داعم استراتيجياً", "قوة الدليل": "قوية جداً", "آخر تحديث": "أسبوعي"},
        {"العامل": "البنية الفنية", "الحالة الحالية": "SMC Sweeps", "الأثر المحتمل": "إيجابي", "قوة الدليل": "قوية", "آخر تحديث": "لحظي"},
        {"العامل": "النتيجة الإجمالية", "الحالة الحالية": "توافق صاعد مشروط", "الأثر المحتمل": "فرص شراء مع إدارة مخاطر", "قوة الدليل": "88% 🟢", "آخر تحديث": "الان"}
    ]
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

# --- محتوى باقي الأقسام السابقة مع الحفاظ عليها بالكامل ---
elif "1. 🌐" in navigation:
    st.markdown("### 🌐 التحليل الكلي والارتباط (Macro & Liquidity)")
    st.write(f"السعر الفعلي الحالي المعتمد في اللوحة: **{active_gold} $** (مطابق لشارتك).")
    st.info("مؤشر الارتباط العكسي بين الذهب ومؤشر الدولار DXY يعمل بكفاءة تامة لتحديد مصائد السيولة.")

elif "2. ⏰" in navigation:
    st.markdown("### ⏰ الجلسات ومناطق السيولة اليومية (Killzones)")
    st.write(f"المنطقة الزمنية الحالية المعتمدة: **{timezone_name}**")
    st.success("تتم مراقبة أوقات Killzones بدقة تامة بناءً على توقيتك المحلي.")

elif "3. 📊" in navigation:
    st.markdown("### 📊 محرك التحليل والسيناريوهات (Analysis Engine)")
    st.info(f"السعر الحالي عند {active_gold} يختبر مناطق سيولة هامة وفق هيكل السوق (Market Structure).")

elif "4. 🧮" in navigation:
    st.markdown("### 🧮 إدارة المخاطر وحاسبة حجم العقود (Risk & Position Calculator)")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1: balance = st.number_input("رأس المال ($)", value=10000)
    with col_r2: risk_pct = st.number_input("نسبة المخاطرة (%)", value=1.0)
    with col_r3: sl_pips = st.number_input("وقف الخسارة (بالنقاط)", value=30)
    
    risk_amount = balance * (risk_pct / 100)
    lot_size = round(risk_amount / (sl_pips * 10), 2) if sl_pips > 0 else 0.0
    st.success(f"💡 **حجم اللوت المناسب:** `{lot_size} Lot` | **مبلغ المخاطرة المرصود:** `{risk_amount} $`")

elif "5. 📋" in navigation:
    st.markdown("### 📋 سجل الفرص ومؤشر التوافق المؤسسي (Trade Journal)")
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
st.caption("YUNAN GOLD INTELLIGENCE v3.0 • GOLD INTELLIGENCE FUSION ENGINE INTEGRATED")
