import streamlit as st
import math
import google.generativeai as genai
from PIL import Image

# --- 1. إعدادات الصفحة والذكاء الاصطناعي ---
st.set_page_config(page_title="ProbMaster Pro 67", page_icon="🎲", layout="wide")

# إعداد Gemini مع نظام حماية من الانهيار
ai_available = False
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_available = True
    except Exception:
        ai_available = False

# --- 2. محرك الرياضيات ---
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
    def get_total_cases(n, k, mode):
        if mode == "في آن واحد": return ProbEngine.nCr(n, k)
        if mode == "على التوالي بدون إرجاع": return ProbEngine.nPr(n, k)
        return n**k

# --- 3. تصميم الواجهة ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1e88e5; color: white; font-weight: bold; }
    .explanation-box { padding: 15px; border-radius: 10px; background-color: #f1f8e9; border-right: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Probability Master Pro | الإصدار الاحترافي 2.0")
st.write("Developed by **Amine | 67**")
st.markdown("---")

# --- 4. إدارة الصندوق (Sidebar) ---
with st.sidebar:
    st.header("📦 إعدادات الصندوق")
    if 'items' not in st.session_state:
        st.session_state['items'] = {"حمراء": 5, "صفراء": 3, "خضراء": 2}

    with st.expander("➕ إضافة كرات جديدة"):
        new_name = st.text_input("اسم اللون/الرقم")
        new_val = st.number_input("العدد", min_value=1, value=1)
        if st.button("إضافة"):
            if new_name:
                st.session_state['items'][new_name] = new_val
                st.rerun()

    total_n = 0
    current_items = st.session_state.get('items', {})
    for name in list(current_items.keys()):
        col1, col2 = st.columns([3, 1])
        st.session_state['items'][name] = col1.number_input(f"{name}", min_value=0, value=current_items[name], key=f"e_{name}")
        total_n += st.session_state['items'][name]
        if col2.button("🗑️", key=f"d_{name}"):
            del st.session_state['items'][name]; st.rerun()
    st.divider()
    st.metric("إجمالي الكرات", total_n)

# --- 5. حل الصور (AI) مع حماية من الأخطاء ---
st.subheader("📸 حل تمرين مصور")
uploaded_file = st.file_uploader("ارفع صورة التمرين (مثل الذي صورته)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=500)
    if st.button("🪄 تحليل التمرين"):
        if ai_available:
            with st.spinner("جاري التواصل مع الذكاء الاصطناعي..."):
                try:
                    prompt = "حل تمرين الاحتمالات في الصورة بالتفصيل باللغة العربية مع القوانين."
                    response = model.generate_content([prompt, img])
                    st.markdown("### 📝 الحل التفصيلي:")
                    st.write(response.text)
                except Exception as e:
                    st.error("❌ فشل الاتصال بالخدمة. تأكد من مفتاح API أو جرب لاحقاً.")
        else:
            st.error("⚠️ ميزة الذكاء الاصطناعي غير مفعلة. تأكد من إضافة GEMINI_API_KEY في إعدادات Secrets.")

st.divider()

# --- 6. الحساب اليدوي ---
st.subheader("🧮 الحساب السريع للأحداث البسيطة")
c1, c2 = st.columns(2)
with c1: k = st.number_input("عدد الكرات المسحوبة (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=3)
with c2: mode = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

q = st.text_input("المطلوب (مثال: نفس اللون)")

if st.button("⚡ احسب الاحتمال"):
    if total_n == 0: st.error("الصندوق فارغ!")
    else:
        total_cases = ProbEngine.get_total_cases(total_n, k, mode)
        favorable = 0
        if "نفس" in q:
            for n_i in st.session_state['items'].values():
                favorable += ProbEngine.get_total_cases(n_i, k, mode)
            st.success(f"الاحتمال: {favorable/total_cases:.4f}")
            st.latex(rf"P(A) = \frac{{{favorable}}}{{{total_cases}}}")
            st.balloons()
