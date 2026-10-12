import os
from datetime import datetime
import pytz
import pandas as pd
import streamlit as st

# --- إعداد التطبيق الأساسي ---
APP_NAME = "YUNAN GOLD INTELLIGENCE"
st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# --- تنسيق التصميم المؤسسي ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { 
    --bg: #06090f; 
    --panel: #0d131d; 
    --line: #1e2c3d; 
    --gold: #d9b56d; 
    --green: #00e676; 
    --muted: #8b9bb4; 
    --text: #eef2f7; 
}
html, body, [class*="css"] { font-family:'IBM Plex Sans Arabic','Inter',sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
.block-container { padding-top: 3rem !important; max-width: 1450px; }

[data-testid="stSidebar"] { background: #070b12; border-left: 1px solid var(--line); padding-top: 15px; }
[data-testid="stSidebar"] * { color: var(--text); }

.brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 16px; border-bottom: 1px solid var(--line); margin-bottom: 15px; }
.brand-mark { width: 42px; height: 42px; border: 1px solid #7a643b; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--gold); font-size: 21px; background: #0d121a; }
.brand-title { font-weight: 800; font-size: 16px; color: #f4f0e7; }
.brand-sub { color: var(--muted); font-size: 11px; }

.hero { border: 1px solid #233142; border-radius: 16px; padding: 20px 24px; background: #0d131d; margin-bottom: 18px; }
.eyebrow { color: var(--gold); letter-spacing: 2px; font-size: 11px; font-weight: 700; }
.hero h1 { margin: 6px 0; font-size: 22px; color: #f7f5ef; }
.hero p { margin: 0; color: #9fb0c6; font-size: 13px; }

.fusion-card { background: #0b111a; border: 1px solid var(--line); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.alert-box { background: rgba(217,181,109,0.08); border-left: 4px solid var(--gold); padding: 12px; border-radius: 0 8px 8px 0; margin-bottom: 10px; font-size: 13px; }

.stButton button { border-radius: 10px; border: 1px solid #d9b56d !important; background: linear-gradient(135deg, #d9b56d, #b3914a) !important; color: #06090f !important; font-weight: 800 !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- المصادقة ---
def get_secret(name):
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return os.getenv(name, "")

APP_USERNAME = get_secret("APP_USERNAME")
APP_PASSWORD = get_secret("APP_PASSWORD")

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
                else:
                    st.error("بيانات غير صحيحة")
        st.stop()

# --- الحالة العامة ---
if "synced_gold_price" not in st.session_state: st.session_state.synced_gold_price = 4186.67
if "webhook_logs" not in st.session_state: st.session_state.webhook_logs = []

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">FUSION ENGINE</div></div></div>', unsafe_allow_html=True)
    
    navigation = st.radio(
        "القائمة",
        [
            "🔥 GOLD INTELLIGENCE FUSION",
            "1. 🌐 التحليل الكلي (Macro)",
            "2. ⏰ الجلسات والسيولة (Killzones)",
            "3. 📊 محرك التحليل (Analysis)",
            "4. 🧮 إدارة المخاطر (Risk)",
            "5. 📋 سجل الفرص (Journal)"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    manual_price = st.text_input("سعر الشارت الفعلي", value=str(st.session_state.synced_gold_price))
    if st.button("تحديث السعر"):
        try:
            st.session_state.synced_gold_price = float(manual_price)
            st.success("تم التحديث")
            st.rerun()
        except ValueError:
            st.error("رقم غير صحيح")

active_gold = st.session_state.synced_gold_price

# --- المحتوى الأساسي ---
if navigation == "🔥 GOLD INTELLIGENCE FUSION":
    st.markdown('<div class="hero"><div class="eyebrow">FUSION ENGINE</div><h1>لوحة القرار الاستخباراتي للذهب XAUUSD</h1><p>ربط الاقتصاد الكلي، السيولة، وسلوك المؤسسات بالبنية الفنية.</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="alert-box">⚖️ <b>حالة الاستقرار:</b> مؤشر DXY في نطاق تذبذب آمن، راقب سحب السيولة عند قيعان آسيا.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="fusion-card"><span style="color:var(--gold); font-weight:700;">التحيز الاقتصادي</span><p style="margin:5px 0 0; color:var(--muted);">محايد إلى صاعد دائم (دعم توقعات الفائدة).</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="fusion-card"><span style="color:var(--gold); font-weight:700;">الاتجاه الفني</span><p style="margin:5px 0 0; color:var(--muted);">صاعد هيكلياً / إعادة اختبار مناطق السيولة.</p></div>', unsafe_allow_html=True)

    st.markdown("### 🔍 حاسبة توافق الصفقة (SMC Confluence Tracker)")
    with st.expander("فحص الشروط الفنية والماكرو", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            structure = st.selectbox("هيكل السوق:", ["BOS Bullish", "CHoCH Bullish", "Consolidation"])
            liquidity = st.selectbox("منطقة السيولة المستهدفة:", ["Previous Day Low", "Asia Lows", "Equal Lows"])
        with c2:
            entry = st.selectbox("منطقة التنفيذ:", ["Order Block + FVG", "Discount Zone (<50%)"])
            news = st.selectbox("مخاطر الأخبار:", ["لا توجد أخبار قريبة", "خبر قادم خلال ساعة"])

        score = 50
        if "Bullish" in structure: score += 20
        if "Low" in liquidity: score += 15
        if "Order Block" in entry: score += 15
        if "ساعة" in news: score -= 25

        st.metric("درجة توافق الصفقة", f"{score}%")
        if score >= 70:
            st.success(f"🟢 إشارة ممتازة للتنفيذ عند السعر المعتمد ({active_gold} $).")
        else:
            st.warning("⚠️ نسبة التوافق منخفضة، يفضل الانتظار.")

elif "1. 🌐" in navigation:
    st.markdown("## 🌐 التحليل الكلي والارتباط")
    st.write(f"السعر المعتمد: **{active_gold} $**")
    st.dataframe(pd.DataFrame([
        {"المؤشر": "مؤشر الدولار (DXY)", "القيمة": "102.24", "الارتباط": "-0.84"},
        {"المؤشر": "العائد الحقيقي 10Y", "القيمة": "2.87%", "الارتباط": "-0.91"}
    ]), use_container_width=True, hide_index=True)

elif "2. ⏰" in navigation:
    st.markdown("## ⏰ الجلسات ومناطق السيولة (Killzones)")
    st.info("متابعة توقيتات لندن ونيويورك بدقة.")

elif "3. 📊" in navigation:
    st.markdown("## 📊 محرك التحليل والسيناريوهات")
    st.info("تحليل البنية السعرية والسيناريوهات البديلة.")

elif "4. 🧮" in navigation:
    st.markdown("## 🧮 إدارة المخاطر")
    bal = st.number_input("رأس المال ($)", value=10000)
    risk = st.number_input("المخاطرة (%)", value=1.0)
    sl = st.number_input("وقف الخسارة (نقاط)", value=30)
    lot = round((bal * (risk / 100)) / (sl * 10), 2)
    st.success(f"حجم اللوت المناسب: `{lot} Lot`")

elif "5. 📋" in navigation:
    st.markdown("## 📋 سجل الفرص والتوافق")
    with st.form("journal"):
        sig = st.selectbox("الإشارة", ["Sweep Asia Lows", "BOS Bullish"])
        if st.form_submit_button("تسجيل"):
            st.session_state.webhook_logs.insert(0, {"الوقت": datetime.now().strftime("%H:%M:%S"), "الإشارة": sig})
            st.success("تم الحفظ")
    if st.session_state.webhook_logs:
        st.dataframe(pd.DataFrame(st.session_state.webhook_logs), use_container_width=True, hide_index=True)

st.divider()
st.caption("YUNAN GOLD INTELLIGENCE v4.1 • ULTRA STABLE CORE")
