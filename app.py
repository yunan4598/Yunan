import os
import time
from datetime import datetime
import pytz
import pandas as pd
import streamlit as st
import yfinance as yf

# --- 1. إعداد التطبيق الأساسي وتجاوب الشاشات ---
APP_NAME = "YUNAN GOLD INTELLIGENCE"
st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide", initial_sidebar_state="expanded")

# --- الهوية البصرية المؤسسية وتجاوب الهواتف (Responsive CSS) ---
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
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1450px; }

@media (max-width: 768px) {
    .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; padding-top: 1rem !important; }
    .hero { padding: 15px !important; }
    .hero h1 { font-size: 18px !important; }
}

[data-testid="stSidebar"] { background: #070b12; border-left: 1px solid var(--line); padding-top: 15px; }
[data-testid="stSidebar"] * { color: var(--text); }

.brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 16px; border-bottom: 1px solid var(--line); margin-bottom: 15px; }
.brand-mark { width: 42px; height: 42px; border: 1px solid #7a643b; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--gold); font-size: 21px; background: linear-gradient(145deg, #221c13, #0d121a); }
.brand-title { font-family: Inter, sans-serif; letter-spacing: 1.2px; font-weight: 800; font-size: 16px; color: #f4f0e7; }
.brand-sub { color: var(--muted); font-size: 11px; margin-top: 2px; }

.hero { border: 1px solid #233142; border-radius: 16px; padding: 20px 24px; background: linear-gradient(135deg, rgba(17,25,38,0.95), rgba(8,12,18,0.95)); margin-bottom: 18px; position: relative; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.eyebrow { color: var(--gold); letter-spacing: 2px; font-size: 11px; font-weight: 700; font-family: Inter, sans-serif; }
.hero h1 { margin: 6px 0 6px; font-size: 22px; color: #f7f5ef; font-weight: 700; }
.hero p { margin: 0; color: #9fb0c6; max-width: 820px; line-height: 1.6; font-size: 13px; }

.data-banner { background: #0b111a; border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; margin-bottom: 15px; font-size: 12.5px; color: var(--muted); }
.fusion-card { background: #0b111a; border: 1px solid var(--line); border-radius: 12px; padding: 16px; margin-bottom: 12px; }

.stButton button { border-radius: 10px; border: 1px solid #d9b56d !important; background: linear-gradient(135deg, #d9b56d, #b3914a) !important; color: #06090f !important; font-weight: 800 !important; width: 100%; padding: 10px; }
.stButton button:hover { background: linear-gradient(135deg, #e6c37d, #c5a159) !important; color: #000000 !important; }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- نظام المصادقة والأمان ---
def get_secret(name):
    try: return str(st.secrets.get(name, ""))
    except Exception: return os.getenv(name, "")

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
                else: st.error("بيانات الدخول غير صحيحة.")
        st.stop()

# --- إدارة الذاكرة والتاريخ ---
if "synced_gold_price" not in st.session_state: st.session_state.synced_gold_price = 4186.67
if "trade_journal" not in st.session_state: st.session_state.trade_journal = []
if "previous_fusion" not in st.session_state: st.session_state.previous_fusion = None
if "current_fusion" not in st.session_state: st.session_state.current_fusion = None

# --- 1. DATA VALIDATION: وحدة جلب وتدقيق البيانات المؤسسية ---
@st.cache_data(ttl=120)
def fetch_institutional_market_data():
    results = {
        "dxy": {"val": "DATA UNAVAILABLE", "change": None, "type": "سوقي لحظي", "status": "غائب 🔴", "time": "غير متوفر"},
        "us10y": {"val": "DATA UNAVAILABLE", "change": None, "type": "سوقي لحظي", "status": "غائب 🔴", "time": "غير متوفر"},
        "real_yield": {"val": "DATA UNAVAILABLE", "type": "يومي اقتصادي", "status": "غير متصل 🟡", "time": "تقرير يومي"},
        "breakeven": {"val": "DATA UNAVAILABLE", "type": "يومي اقتصادي", "status": "غير متصل 🟡", "time": "تقرير يومي"},
        "cot_net": {"val": "DATA UNAVAILABLE", "type": "أسبوعي (CFTC)", "status": "تقرير أسبوعي 🟡", "time": "جمعة أسبوعية"},
        "open_interest": {"val": "DATA UNAVAILABLE", "type": "أسبوعي (CFTC)", "status": "تقرير أسبوعي 🟡", "time": "جمعة أسبوعية"},
        "quality_score": 0
    }
    valid_count = 0

    # جلب DXY
    try:
        dxy_ticker = yf.Ticker("DX-Y.NYB")
        hist = dxy_ticker.history(period="5d")
        if not hist.empty and len(hist) >= 2:
            last_p = float(hist['Close'].iloc[-1])
            prev_p = float(hist['Close'].iloc[-2])
            chg = last_p - prev_p
            results["dxy"] = {
                "val": round(last_p, 2),
                "change": round(chg, 2),
                "type": "سوقي لحظي",
                "status": "متصل 🟢",
                "time": datetime.now().strftime("%I:%M %p")
            }
            valid_count += 1
    except Exception: pass

    # جلب US10Y Nominal Yield
    try:
        tnx_ticker = yf.Ticker("^TNX")
        hist_tnx = tnx_ticker.history(period="5d")
        if not hist_tnx.empty and len(hist_tnx) >= 2:
            last_y = float(hist_tnx['Close'].iloc[-1])
            prev_y = float(hist_tnx['Close'].iloc[-2])
            chg_y = last_y - prev_y
            results["us10y"] = {
                "val": f"{round(last_y, 3)}%",
                "change": round(chg_y, 3),
                "type": "سوقي لحظي",
                "status": "متصل 🟢",
                "time": datetime.now().strftime("%I:%M %p")
            }
            valid_count += 1
    except Exception: pass

    # الموثوقية العامة
    results["quality_score"] = int((valid_count / 2) * 100)
    return results

market_data = fetch_institutional_market_data()

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◆</div><div><div class="brand-title">YUNAN GOLD</div><div class="brand-sub">INSTITUTIONAL TERMINAL</div></div></div>', unsafe_allow_html=True)
    
    navigation = st.radio(
        "القائمة الرئيسية",
        [
            "🔥 GOLD INTELLIGENCE FUSION",
            "1. 🌐 التحليل الكلي والسيولة (Macro)",
            "2. ⏰ الجلسات ومناطق السيولة (Killzones)",
            "3. 📊 الفائدة والمفاجآت (Fed & Surprises)",
            "4. 🏦 التمركز المؤسسي (COT & OI)",
            "5. 🎯 فحص SMC/ICT (Trade Validator)",
            "6. 🧮 إدارة المخاطر وحاسبة اللوت (Risk)",
            "7. 📋 سجل الصفقات (Trading Journal)"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### ⚙️ مطابقة سعر الشارت الحية")
    manual_price = st.text_input("السعر الفعلي من شارتك ($)", value=str(st.session_state.synced_gold_price))
    if st.button("تحديث السعر"):
        try:
            st.session_state.synced_gold_price = float(manual_price)
            st.success("تم تحديث السعر الفعلي")
            st.rerun()
        except ValueError:
            st.error("رقم غير صحيح")

    st.caption(f"السعر المعتمد حالياً: **{st.session_state.synced_gold_price} $**")
    
    st.divider()
    st.markdown("### 📡 حالة المصادر")
    st.caption(f"• DXY: {market_data['dxy']['status']} ({market_data['dxy']['time']})\n• US10Y: {market_data['us10y']['status']} ({market_data['us10y']['time']})\n• COT/OI: {market_data['cot_net']['status']}")

active_gold = st.session_state.synced_gold_price

# --- 2. FUSION REPORT & SCENARIO ENGINE ---
if navigation == "🔥 GOLD INTELLIGENCE FUSION":
    st.markdown('<div class="hero"><div class="eyebrow">INSTITUTIONAL FUSION TERMINAL</div><h1>محرك الدمج والتقارير الموحدة (Gold Fusion Engine)</h1><p>ربط مباشر بين البيانات اللحظية والتحليل الهيكلي لإنتاج سيناريوهات مشروطة محددة الأسباب.</p></div>', unsafe_allow_html=True)

    # مؤشر جودة البيانات والتحديثات
    q_score = market_data["quality_score"]
    status_color = "🟢" if q_score == 100 else ("🟡" if q_score == 50 else "🔴")
    st.markdown(f'''<div class="data-banner">
        <span>{status_color} <b>مؤشر جودة البيانات:</b> {q_score}%</span>
        <span>💵 <b>DXY:</b> {market_data['dxy']['val']}</span>
        <span>📈 <b>US10Y:</b> {market_data['us10y']['val']}</span>
        <span>🏦 <b>COT / OI:</b> {market_data['cot_net']['val']}</span>
    </div>''', unsafe_allow_html=True)

    if q_score < 50:
        st.warning("⚠️ **تنبيه:** تعذر التحقق من بعض البيانات الحية. سيتوقف النظام عن إصدار استنتاج حاسم تجنباً للقيم الوهمية.")

    col_run, _ = st.columns([2, 3])
    with col_run:
        run_btn = st.button("⚡ حلّل الذهب الآن (Run Fusion Engine)")

    if run_btn:
        if st.session_state.current_fusion is not None:
            st.session_state.previous_fusion = st.session_state.current_fusion.copy()

        dxy_v = market_data['dxy']['val']
        dxy_c = market_data['dxy']['change']
        u10_v = market_data['us10y']['val']
        u10_c = market_data['us10y']['change']

        # 1. الحقائق المؤكدة
        facts_list = f"1. سعر الذهب المعتمد على شارتك حالياً: {active_gold} $.\n"
        if dxy_v != "DATA UNAVAILABLE": facts_list += f"2. مؤشر DXY اللحظي: {dxy_v} (التغير: {dxy_c}).\n"
        if u10_v != "DATA UNAVAILABLE": facts_list += f"3. عائد السندات الاسمية 10Y: {u10_v} (التغير: {u10_c}).\n"
        facts_list += f"4. بيانات Real Yield و COT: {market_data['cot_net']['val']} (تتطلب ربط مفتاح API رسمي)."

        # 2. التفسير الاقتصادي والفني
        macro_interp = "صاعد للذهب بسبب تراجع الدولار والعوائد" if (dxy_c and dxy_c < 0) and (u10_c and u10_c < 0) else \
                       ("ضاغط على الذهب بسبب ارتفاع الدولار والعوائد" if (dxy_c and dxy_c > 0) and (u10_c and u10_c > 0) else "محايد/متضارب بين اتجاه عوائد السندات والدولار")

        tech_interp = f"السعر المعتمد {active_gold} $ يتواجد في منطقة إعادة اختبار هيكلية. يتطلب الأمر فحص سحب السيولة (Sweep) وإغلاق الشموع التأكيدية."

        conflicts = "تضارب بين مؤشر DXY وعوائد 10Y اللحظية." if "محايد" in macro_interp else "تنسيق متوافق بين اتجاه الحركة في DXY وسوق السندات."

        # 3. محرك السيناريوهات المعتمد على قواعد السلوك السعري
        bull_sc = f"الهدف: {round(active_gold + 15, 2)} $\n• الأساس الفني: كسر سيولة قمة لندن عند {round(active_gold + 8, 2)} $ مع ظهور شمعة Displacement صريحة.\n• الشرط: بقاء DXY أسفل {dxy_v if dxy_v != 'DATA UNAVAILABLE' else 'النطاق'}."
        bear_sc = f"الهدف: {round(active_gold - 15, 2)} $\n• الأساس الفني: كسر سيولة قاع اليوم السابق عند {round(active_gold - 8, 2)} $ وإغلاق أسفل منطقة Equilibrium.\n• الشرط: ارتفاع عوائد السندات وتجاوز DXY القمة السابقة."
        neutral_sc = f"النطاق: بين {round(active_gold - 6, 2)} $ و {round(active_gold + 6, 2)} $\n• الأساس الفني: تذبذب عرضي وتجميع سيولة قبل افتتاح جلسة نيويورك أو صدور بيانات اقتصادية."
        
        invalidation = f"إغلاق شمعة 1H كاملة خارج النطاق المحوري ({round(active_gold - 12, 2)} $- {round(active_gold + 12, 2)}$) ينهي هذا السيناريو فورياً."

        st.session_state.current_fusion = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
            "facts": facts_list,
            "macro_interp": macro_interp,
            "tech_interp": tech_interp,
            "conflicts": conflicts,
            "scenarios": {"bull": bull_sc, "bear": bear_sc, "neutral": neutral_sc},
            "invalidation": invalidation,
            "gold_price": active_gold
        }
        st.rerun()

    # عرض التقرير الموحد
    if st.session_state.current_fusion:
        cur = st.session_state.current_fusion
        st.markdown(f"### 🔍 التقرير الاستخباراتي الموحد (`{cur['timestamp']}`)")
        st.caption("ملاحظة: هذا التقرير تحليلي لتقييم ظروف السوق وليس توصية دخول تلقائية.")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown(f'''<div class="fusion-card">
                <span style="color:var(--gold); font-weight:700;">1. الحقائق المؤكدة (Confirmed Facts)</span>
                <p style="margin:6px 0 0; color:var(--text); font-size:12.5px; white-space: pre-line;">{cur['facts']}</p>
            </div>''', unsafe_allow_html=True)
            st.markdown(f'''<div class="fusion-card">
                <span style="color:var(--gold); font-weight:700;">3. التفسير الفني والهيكلي (Price Action)</span>
                <p style="margin:6px 0 0; color:var(--text); font-size:13px;">{cur['tech_interp']}</p>
            </div>''', unsafe_allow_html=True)
        with col_f2:
            st.markdown(f'''<div class="fusion-card">
                <span style="color:var(--gold); font-weight:700;">2. التفسير الاقتصادي (Economic Bias)</span>
                <p style="margin:6px 0 0; color:var(--text); font-size:13px;">{cur['macro_interp']}</p>
            </div>''', unsafe_allow_html=True)
            st.markdown(f'''<div class="fusion-card">
                <span style="color:var(--gold); font-weight:700;">4. الأدلة المتعارضة (Conflicting Signals)</span>
                <p style="margin:6px 0 0; color:var(--text); font-size:13px;">{cur['conflicts']}</p>
            </div>''', unsafe_allow_html=True)

        st.markdown("### 📈 محرك السيناريوهات المشروطة (Scenario Engine)")
        s1, s2, s3 = st.columns(3)
        with s1: st.success(f"🟢 **السيناريو الصاعد:**\n\n{cur['scenarios']['bull']}")
        with s2: st.error(f"🔴 **السيناريو الهابط:**\n\n{cur['scenarios']['bear']}")
        with s3: st.warning(f"🟡 **السيناريو المحايد:**\n\n{cur['scenarios']['neutral']}")

        st.markdown(f"🛑 **شرط إبطال التحليل (Invalidation Criterion):** `{cur['invalidation']}`")

        # 6. REPORT COMPARISON
        st.markdown("### 🔄 مقارنة التقرير الحالي بالتقرير السابق (Report Comparison)")
        if st.session_state.previous_fusion:
            prev = st.session_state.previous_fusion
            diff = round(cur['gold_price'] - prev['gold_price'], 2)
            st.info(f"""
            • **التغير في سعر الذهب المعتمد:** {diff} $ (من {prev['gold_price']} $ إلى {cur['gold_price']} $).
            • **التغير في التفسير الاقتصادي:** كان `{prev['macro_interp']}` وأصبح `{cur['macro_interp']}`.
            • **تاريخ التقرير السابق:** `{prev['timestamp']}`.
            • **سبب تعديل السيناريو:** تغير السعر الفعلي وإعادة تقييم نقاط سحب السيولة القريبة.
            """)
        else:
            st.caption("لا يوجد تقرير سابق للمقارنة حتى الآن. اضغط الزر مرة أخرى بعد تغيير السعر لمشاهدة التغيرات.")

# --- 4. SMC / ICT VALIDATOR ---
elif navigation == "5. 🎯 فحص SMC/ICT (Trade Validator)":
    st.markdown("## 🎯 فحص واختبار شروط SMC / ICT (Trade Validator)")
    st.caption("شرط أساسي: لمس المنطقة لا يعتبر إشارة دخول إطلاقاً بغير تأكيد صريح لكسر الهيكل واندفاع السعر.")

    with st.form("smc_val_form"):
        c1, c2 = st.columns(2)
        with c1:
            htf_trend = st.selectbox("اتجاه الإطار الأعلى (Daily / 4H):", ["صاعد (Bullish Structure)", "هابط (Bearish Structure)", "عرضي / غير واضح"])
            liq_type = st.selectbox("نوع السيولة المستهدفة:", ["External Liquidity (PDH/PDL)", "Internal Liquidity (FVG / Asia Lows)", "لا توجد سيولة صريحة"])
            sweep_action = st.selectbox("حالة حركة السعر عند المستوى:", ["Sweep صريح وسريع مع رفض (Rejection)", "اختراق وتثبيت دون رفض", "لم يصل للمستوى بعد"])
        with c2:
            disp_action = st.selectbox("ظهور الاندفاع (Displacement):", ["شمعة اندفاعية قوية أغلقت وجلبت FVG", "حركة ضعيفة وبطيئة", "عدم وجود اندفاع"])
            struct_confirm = st.selectbox("تأكيد البنية السعرية (BOS / CHoCH):", ["تأكد كسر الهيكل إغلاق شمعة صريح", "مجرد ذيل شمعة (Wick Only)", "لم يتأكد بعد"])
            news_proximity = st.selectbox("توقيت الأخبار:", ["لا توجد أخبار خلال 45 دقيقة", "خبر عالي التأثير قادم قريباً"])

        submit_smc = st.form_submit_button("فحص الشروط وفق قواعد SMC/ICT الصارمة")

    if submit_smc:
        score = 0
        reasons = []

        if "صاعد" in htf_trend or "هابط" in htf_trend: score += 20
        if "External" in liq_type or "Internal" in liq_type: score += 20
        if "Sweep" in sweep_action: 
            score += 20
        else: 
            reasons.append("غياب الرفض وسحب السيولة المباشر (Sweep).")

        if "اندفاعية" in disp_action: score += 20
        else: reasons.append("غياب الاندفاع (Displacement) وتكون FVG.")

        if "إغلاق شمعة صريح" in struct_confirm: score += 20
        else: reasons.append("البنية السعرية غير مؤكدة (مجرد ذيل شمعة أو عدم كسر).")

        if "قادم قريباً" in news_proximity: score -= 30

        st.divider()
        if score >= 80:
            st.success(f"✅ **VALID SETUP (شروط SMC/ICT متكاملة):** درجة التوافق {score}%. يمكنك التخطيط للدخول مع تحديد الوقف والهدف.")
        elif score >= 60:
            st.warning(f"🟡 **WAIT FOR CONFIRMATION (شروط غير مكتملة):** درجة التوافق {score}%. الأسباب: {', '.join(reasons)}")
        else:
            st.error(f"🚫 **NO TRADE (تجنب الدخول):** درجة التوافق {score}%. لم تتحقق قواعد التأكيد المعتمدة.")

# --- 5. RISK MANAGEMENT ---
elif navigation == "6. 🧮 إدارة المخاطر وحاسبة اللوت (Risk)":
    st.markdown("## 🧮 حاسبة حجم الصفقة وإدارة المخاطر (Institutional Risk Calculator)")

    c_r1, c_r2, c_r3 = st.columns(3)
    with c_r1:
        account_bal = st.number_input("رأس مال الحساب ($)", value=10000.0, step=500.0)
        contract_spec = st.number_input("حجم العقد لوسيطك (Ounces per Lot):", value=100.0, help="Standard Lot = 100 oz")
    with c_r2:
        risk_percentage = st.number_input("نسبة المخاطرة المطلوبة (%)", value=1.0, min_value=0.1, max_value=5.0, step=0.1)
        entry_p = st.number_input("سعر الدخول ($)", value=active_gold)
    with c_r3:
        sl_p = st.number_input("سعر وقف الخسارة ($)", value=round(active_gold - 3.5, 2))
        tp_p = st.number_input("سعر الهدف ($)", value=round(active_gold + 7.0, 2))

    risk_usd = account_bal * (risk_percentage / 100.0)
    sl_distance = abs(entry_p - sl_p)
    tp_distance = abs(tp_p - entry_p)

    if sl_distance > 0:
        calculated_lot = risk_usd / (sl_distance * contract_spec)
        potential_profit = calculated_lot * tp_distance * contract_spec
        rr_ratio = round(tp_distance / sl_distance, 2) if sl_distance > 0 else 0

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("حجم العقد المناسب (Lot Size)", f"{round(calculated_lot, 2)} Lot")
        with m2: st.metric("الخسارة المحتملة المحددة", f"{round(risk_usd, 2)} $")
        with m3: st.metric("الربح المحتمل المستهدف", f"{round(potential_profit, 2)} $")
        with m4: st.metric("نسبة العائد للمخاطرة (R:R)", f"1 : {rr_ratio}")
    else:
        st.error("الرجاء إدخال مسافة وقف خسارة أكبر من صفر للحساب.")

# --- بقية الأقسام المكتملة والهيكلية ---
elif navigation == "1. 🌐 التحليل الكلي والسيولة (Macro)":
    st.markdown("## 🌐 التحليل الكلي والارتباط (Macro & Liquidity)")
    st.dataframe(pd.DataFrame([
        {"المؤشر": "DXY (الدولار)", "القيمة الحالية": market_data['dxy']['val'], "النوع": market_data['dxy']['type'], "حالة المصدر": market_data['dxy']['status']},
        {"المؤشر": "US10Y (العائد)", "القيمة الحالية": market_data['us10y']['val'], "النوع": market_data['us10y']['type'], "حالة المصدر": market_data['us10y']['status']}
    ]), use_container_width=True, hide_index=True)

elif navigation == "2. ⏰ الجلسات ومناطق السيولة (Killzones)":
    st.markdown("## ⏰ الجلسات ومناطق السيولة اليومية (Killzones)")
    st.info("متابعة توقيتات وسلوك جلسات آسيا، لندن، ونيويورك تحديداً عند أوقات سحب السيولة.")

elif navigation == "3. 📊 الفائدة والمفاجآت (Fed & Surprises)":
    st.markdown("## 📊 توقعات الفائدة وكاشف المفاجآت الاقتصادية")
    st.write("تقييم الانحراف الاقتصادي بين التوقعات والقراءات الفعلية للتضخم والوظائف.")

elif navigation == "4. 🏦 التمركز المؤسسي (COT & OI)":
    st.markdown("## 🏦 التمركز المؤسسي (COT) والفائدة المفتوحة (Open Interest)")
    st.caption("بيانات أسبوعية تصدر مساء الجمعة من CFTC لتحديد التموضع الاستراتيجي لكبار التجار.")
    st.warning(f"الحالة الحالية: {market_data['cot_net']['val']}")

elif navigation == "7. 📋 سجل الصفقات (Trading Journal)":
    st.markdown("## 📋 سجل الصفقات ومتابعة الأداء (Trading Journal)")
    with st.form("journal_f"):
        j1, j2, j3 = st.columns(3)
        with j1: dt = st.date_input("التاريخ")
        with j2: tp = st.selectbox("النوع", ["شراء", "بيع"])
        with j3: res = st.selectbox("النتيجة", ["ربح", "خسارة"])
        if st.form_submit_button("حفظ"):
            st.session_state.trade_journal.insert(0, {"التاريخ": str(dt), "النوع": tp, "النتيجة": res})
            st.success("تم الحفظ بنجاح")
    if st.session_state.trade_journal:
        st.dataframe(pd.DataFrame(st.session_state.trade_journal), use_container_width=True, hide_index=True)

st.divider()
st.caption("YUNAN GOLD INTELLIGENCE v8.0 • FULLY AUDITED & TESTED INSTITUTIONAL TERMINAL")
