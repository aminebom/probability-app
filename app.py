import streamlit as st
import math
import google.generativeai as genai
from PIL import Image

# --- 1. إعدادات الصفحة وحقوق الملكية ---
st.set_page_config(page_title="ProbMaster Pro 67", page_icon="🎲", layout="wide")

# --- 2. تهيئة الذاكرة (حل مشكلة AttributeError نهائياً) ---
if 'items' not in st.session_state:
    st.session_state['items'] = {"حمراء": 5, "خضراء": 3, "بيضاء": 2}

# محاولة جلب مفتاح Gemini
ai_available = False
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_available = True
    except: ai_available = False

# --- 3. محرك الرياضيات ---
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

# --- 4. تصميم الواجهة ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #0d47a1; color: white; font-weight: bold; }
    .res-box { padding: 20px; border-radius: 15px; background-color: #f0f4f8; border: 2px solid #0d47a1; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Probability Master Pro | الإصدار 2.3")
st.write("Developed by **Amine | 67**")
st.markdown("---")

# --- 5. إدارة الصندوق (Sidebar) ---
with st.sidebar:
    st.header("📦 محتوى الصندوق")
    
    with st.expander("➕ إضافة كرات جديدة"):
        name_input = st.text_input("اسم اللون أو الرقم")
        val_input = st.number_input("العدد", min_value=1, value=1)
        if st.button("إضافة"):
            if name_input: 
                st.session_state['items'][name_input] = val_input
                st.rerun()

    total_n = sum(st.session_state['items'].values())
    
    # عرض وتعديل العناصر بشكل آمن
    for name in list(st.session_state['items'].keys()):
        col1, col2 = st.columns([3, 1])
        st.session_state['items'][name] = col1.number_input(f"{name}", value=st.session_state['items'][name], key=f"inp_{name}")
        if col2.button("🗑️", key=f"btn_{name}"):
            del st.session_state['items'][name]
            st.rerun()
    
    st.divider()
    st.metric("الإجمالي (n)", total_n)

# --- 6. المحرك اليدوي المطور (فهم ذكي للكلمات) ---
st.subheader("🧮 المحرك اليدوي الذكي")
c1, c2 = st.columns(2)
with c1: k = st.number_input("عدد المسحوبات (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=3)
with c2: mode = st.selectbox("أسلوب السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

user_q = st.text_input("اكتب سؤالك (مثلاً: نفس اللون، على الأقل حمراء، مختلفة)")

if st.button("🚀 تحليل وحساب"):
    if total_n == 0:
        st.error("الصندوق فارغ!")
    else:
        total_cases = ProbEngine.get_total(total_n, k, mode)
        fav_cases = 0
        q = user_q.replace("أ", "ا").replace("إ", "ا")

        # منطق الحساب اليدوي (بدون API)
        if "نفس" in q:
            for count in st.session_state['items'].values():
                if count >= k or mode == "على التوالي مع الإرجاع":
                    fav_cases += ProbEngine.get_total(count, k, mode)
        
        elif "مختلفه" in q:
            from itertools import combinations
            for combo in combinations(st.session_state['items'].values(), k):
                prod = 1
                for val in combo: prod *= val
                fav_cases += prod
            if mode != "في آن واحد": fav_cases *= math.factorial(k)

        if fav_cases > 0:
            st.markdown(f"<div class='res-box'><h3>الاحتمال: {fav_cases/total_cases:.4f}</h3></div>", unsafe_allow_html=True)
            st.latex(rf"P(A) = \frac{{{fav_cases}}}{{{total_cases}}}")
            st.balloons()
        else:
            st.warning("يرجى استخدام كلمات مثل 'نفس' أو 'مختلفه' أو رفع صورة.")

# --- 7. قسم الصور ---
st.divider()
st.subheader("📸 حل المسائل بالصور")
up = st.file_uploader("ارفع الصورة", type=['png', 'jpg', 'jpeg'])
if up and ai_available:
    if st.button("🪄 حل الصورة"):
        try:
            res = model.generate_content(["حل بالتفصيل بالعربية", Image.open(up)])
            st.write(res.text)
        except: st.error("فشل الاتصال بالذكاء الاصطناعي.")
