import streamlit as st
import math
import google.generativeai as genai
from PIL import Image
import re

# --- 1. إعدادات الصفحة والذكاء الاصطناعي ---
st.set_page_config(page_title="ProbMaster Pro 67", page_icon="🎲", layout="wide")

# محاولة جلب مفتاح Gemini من Secrets
ai_available = False
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_available = True
    except:
        ai_available = False

# --- 2. محرك الرياضيات الاحترافي ---
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
        return n**k  # مع الإرجاع

# --- 3. تصميم الواجهة ---
st.markdown("""
    <style>
    .reportview-container { direction: rtl; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2e7d32; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Probability Master Pro | الإصدار الاحترافي 2.0")
st.caption("Developed by Amine | 67")
st.markdown("---")

# --- 4. إدارة الصندوق (Sidebar) ---
with st.sidebar:
    st.header("📦 إعدادات الصندوق")
    
    # حل مشكلة AttributeError: التأكد من تهيئة المخزن
    if 'items' not in st.session_state:
        st.session_state.items = {"حمراء": 5, "خضراء": 3}

    with st.expander("➕ إضافة عنصر جديد (لون/رقم)"):
        new_name = st.text_input("الاسم")
        new_val = st.number_input("العدد", min_value=1, value=1)
        if st.button("إضافة"):
            if new_name:
                st.session_state.items[new_name] = new_val
                st.rerun()

    total_n = 0
    # عرض العناصر مع زر الحذف
    for name, count in list(st.session_state.items.items()):
        col1, col2 = st.columns([3, 1])
        st.session_state.items[name] = col1.number_input(f"{name}", min_value=0, value=count, key=f"e_{name}")
        total_n += st.session_state.items[name]
        if col2.button("🗑️", key=f"d_{name}"):
            del st.session_state.items[name]
            st.rerun()
    
    st.divider()
    st.metric("إجمالي العناصر", total_n)

# --- 5. قسم الذكاء الاصطناعي (حل الصور) ---
st.subheader("📸 حل تمرين مصور (AI)")
uploaded_file = st.file_uploader("ارفع صورة التمرين هنا", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=400, caption="التمرين المرفوع")
    if ai_available:
        if st.button("🪄 حل التمرين بالذكاء الاصطناعي"):
            with st.spinner("جاري التفكير والتحليل..."):
                prompt = "أنت خبير رياضيات. حل تمرين الاحتمالات في الصورة بالتفصيل باللغة العربية مع القوانين."
                response = model.generate_content([prompt, img])
                st.markdown("### 📝 الحل المقترح:")
                st.write(response.text)
    else:
        st.error("⚠️ مفتاح API غير مفعل في Secrets.")

st.divider()

# --- 6. الحساب اليدوي السريع ---
st.subheader("🧮 الحساب الرياضي الفوري")
c1, c2 = st.columns(2)
with c1:
    k = st.number_input("عدد السحبات (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=1)
with c2:
    mode = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

question = st.text_input("اكتب مطلوبك (مثال: نفس اللون، كرتين حمراوين)")

if st.button("⚡ احسب الآن"):
    if total_n == 0:
        st.error("❌ الصندوق فارغ!")
    else:
        total_cases = ProbEngine.get_total_cases(total_n, k, mode)
        favorable = 0
        q = question.replace("أ", "ا").replace("إ", "ا")

        # منطق "نفس اللون"
        if "نفس" in q:
            for n_i in st.session_state.items.values():
                favorable += ProbEngine.get_total_cases(n_i, k, mode)
            
            st.success(f"الاحتمال النهائي: {favorable/total_cases:.4f}")
            st.markdown("### 📝 الخطوات:")
            st.latex(rf"P(A) = \frac{{Cases_{{fav}}}}{{Cases_{{total}}}} = \frac{{{favorable}}}{{{total_cases}}}")
            st.balloons()
        else:
            st.info("استخدم قسم الصور للأسئلة المعقدة، أو اكتب 'نفس اللون' للحساب السريع.")

st.sidebar.markdown("---")
st.sidebar.caption("Probability Master Pro v2.0")
