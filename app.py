import streamlit as st
import math
import google.generativeai as genai
from PIL import Image

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ProbMaster Pro 67", page_icon="🎲", layout="wide")

# محاولة جلب المفتاح (إذا فشل، سيعمل المحرك اليدوي وحده)
ai_available = False
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_available = True
    except: ai_available = False

# --- 2. محرك الرياضيات المتقدم ---
class ProbEngine:
    @staticmethod
    def nCr(n, r):
        if r < 0 or r > n: return 0
        return math.comb(n, r)
    
    @staticmethod
    def nPr(n, r):
        if r < 0 or r > n: return 0
        return math.perm(n, r)

    @staticmethod
    def get_total(n, k, mode):
        if mode == "في آن واحد": return ProbEngine.nCr(n, k)
        if mode == "على التوالي بدون إرجاع": return ProbEngine.nPr(n, k)
        return n**k

# --- 3. تصميم الواجهة ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #0d47a1; color: white; font-weight: bold; }
    .res-box { padding: 20px; border-radius: 15px; background-color: #f0f4f8; border: 2px solid #0d47a1; color: #0d47a1; }
    .step-box { background-color: #ffffff; padding: 10px; border-radius: 5px; margin-top: 10px; border-left: 5px solid #ffab00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Probability Master Pro | الإصدار 2.2")
st.write("Developed by **Amine | 67**")

# --- 4. إدارة الصندوق (Sidebar) ---
with st.sidebar:
    st.header("📦 محتوى الصندوق")
    if 'items' not in st.session_state:
        st.session_state.items = {"حمراء": 5, "خضراء": 3, "بيضاء": 2}
    
    with st.expander("➕ إضافة كرات جديدة"):
        name = st.text_input("اللون أو الرقم")
        val = st.number_input("العدد", min_value=1, value=1)
        if st.button("إضافة"):
            if name: st.session_state.items[name] = val; st.rerun()

    total_n = sum(st.session_state.items.values())
    for n, c in list(st.session_state.items.items()):
        col1, col2 = st.columns([3, 1])
        st.session_state.items[n] = col1.number_input(f"{n}", value=c, key=f"i_{n}")
        if col2.button("🗑️", key=f"d_{n}"): del st.session_state.items[n]; st.rerun()
    st.divider()
    st.metric("الإجمالي (n)", total_n)

# --- 5. المحرك اليدوي الذكي (فهم الكلمات المفتاحية) ---
st.subheader("🧮 المحرك اليدوي الفائق")
c1, c2 = st.columns(2)
with c1: k = st.number_input("عدد المسحوبات (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=3)
with c2: mode = st.selectbox("أسلوب السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

user_q = st.text_input("اكتب سؤالك هنا (مثلاً: نفس اللون، على الأقل كرتين حمراوين، مختلفة...)")

if st.button("🚀 تحليل وحساب"):
    if total_n == 0:
        st.error("الصندوق فارغ!")
    else:
        total_cases = ProbEngine.get_total(total_n, k, mode)
        fav_cases = 0
        explanation = ""
        q = user_q.replace("أ", "ا").replace("إ", "ا") # تنظيف النص

        # 1. حالة: نفس اللون
        if "نفس" in q:
            explanation = "جمع احتمالات سحب k كرة من كل لون موجود."
            for count in st.session_state.items.values():
                if count >= k or mode == "على التوالي مع الإرجاع":
                    fav_cases += ProbEngine.get_total(count, k, mode)

        # 2. حالة: على الأقل (At least) - مثال "حمراء"
        elif "اقل" in q:
            target_color = next((c for c in st.session_state.items if c in q), list(st.session_state.items.keys())[0])
            n_target = st.session_state.items[target_color]
            n_others = total_n - n_target
            # الحساب بالحدث العكسي (1 - احتمال عدم سحب أي كرة من هذا اللون)
            explanation = f"استخدام الحدث العكسي لحساب '{q}'."
            fav_cases = total_cases - ProbEngine.get_total(n_others, k, mode)

        # 3. حالة: مختلفة الألوان (مثنى مثنى)
        elif "مختلفه" in q:
            explanation = "سحب كرة واحدة من كل لون مختلف متاح."
            from itertools import combinations
            for combo in combinations(st.session_state.items.values(), k):
                prod = 1
                for val in combo: prod *= val
                fav_cases += prod
            if mode != "في آن واحد": fav_cases *= math.factorial(k)

        # عرض النتائج بشكل احترافي
        if fav_cases > 0:
            prob = fav_cases / total_cases
            st.markdown(f"""
            <div class="res-box">
                <h3>الاحتمال: {prob:.4f}</h3>
                <p><b>عدد الحالات المواتية:</b> {fav_cases}</p>
                <p><b>إجمالي الحالات:</b> {total_cases}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='step-box'><b>💡 الشرح:</b> {explanation}</div>", unsafe_allow_html=True)
            st.latex(rf"P(A) = \frac{{{fav_cases}}}{{{total_cases}}}")
            st.balloons()
        else:
            st.warning("لم أفهم السؤال يدوياً. جرب كلمات مثل 'نفس'، 'اقل'، 'مختلفه'.")

# --- 6. حماية من انهيار الـ API ---
st.divider()
st.subheader("📸 حل المسائل بالصور (إذا توفر الـ API)")
up = st.file_uploader("ارفع الصورة هنا", type=['png', 'jpg', 'jpeg'])
if up:
    if ai_available:
        if st.button("🪄 حل الصورة"):
            with st.spinner("جاري الحل..."):
                try:
                    res = model.generate_content(["حل بالتفصيل بالعربية", Image.open(up)])
                    st.write(res.text)
                except: st.error("عذراً، خادم الذكاء الاصطناعي مشغول حالياً.")
    else:
        st.error("ميزة الصور تحتاج لمفتاح API فعال في الإعدادات.")
