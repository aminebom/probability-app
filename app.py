import streamlit as st
import math
import re
from itertools import combinations, permutations, product
from fractions import Fraction

# --- 1. إصلاح أخطاء AttributeError: تهيئة الحالة فوراً ---
if 'items' not in st.session_state:
    st.session_state['items'] = {"حمراء": 5, "خضراء": 3, "صفراء": 2}

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="ProbMaster Pro 7.0", page_icon="🎲", layout="wide")

st.markdown("""
    <style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button:first-child {
        background-color: #0066cc; color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
    .result-box {
        padding: 20px; border-radius: 10px; background-color: #f0f7ff; 
        border-right: 8px solid #0066cc; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. المحرك الرياضي ---
class MathEngine:
    @staticmethod
    def get_space(n, k, mode):
        if mode == "في آن واحد": return math.comb(n, k)
        if mode == "على التوالي بدون إرجاع": return math.perm(n, k)
        return n ** k

    @staticmethod
    def get_ordering_factor(k, r_list):
        denom = 1
        for r in r_list: denom *= math.factorial(r)
        return math.factorial(k) // denom

# --- 4. Sidebar: إدارة الصندوق (معالجة أخطاء الحذف) ---
with st.sidebar:
    st.header("📦 محتوى الصندوق")
    with st.expander("✨ إضافة عنصر جديد"):
        new_name = st.text_input("الاسم/الرقم")
        new_val = st.number_input("العدد", 1, 100, 1)
        if st.button("إضافة"):
            if new_name:
                st.session_state['items'][new_name] = new_val
                st.rerun()

    st.write("---")
    # تحويل القيم إلى قائمة محلية لتجنب RuntimeError عند الحذف
    current_items = st.session_state['items']
    for name in list(current_items.keys()):
        c1, c2 = st.columns([3, 1])
        current_items[name] = c1.number_input(f"{name}", 0, 100, current_items[name], key=f"inp_{name}")
        if c2.button("🗑️", key=f"btn_{name}"):
            del st.session_state['items'][name]
            st.rerun()
            
    total_n = sum(current_items.values())
    st.metric("إجمالي العناصر (n)", total_n)

# --- 5. الواجهة الرئيسية ---
st.title("🎲 Probability Master Pro | 7.0")
st.write(f"Developed by Amine | 67")

tab1, tab2 = st.tabs(["📊 الحساب اليدوي", "ℹ️ تعليمات"])

with tab1:
    col_k, col_m = st.columns(2)
    with col_k: k_pulls = st.number_input("عدد السحبات (k)", 1, total_n if total_n > 0 else 1, 3)
    with col_m: mode = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])
    
    query = st.text_input("💬 اكتب مطلوبك (مثال: كرتين حمراء، مختلفة الألوان، نفس اللون)")

    if st.button("🚀 احسب الآن"):
        if total_n == 0:
            st.error("الصندوق فارغ!")
        elif total_n < k_pulls and mode != "على التوالي مع الإرجاع":
            st.error("عدد الكرات غير كافٍ لهذا النوع من السحب.")
        else:
            # تنظيف النص
            q = query.lower().replace("أ","ا").replace("إ","ا").replace("ة","ه").replace("ى","ي")
            total_space = MathEngine.get_space(total_n, k_pulls, mode)
            fav = 0
            
            # أ. نفس اللون
            if any(w in q for w in ["نفس", "متماثل"]):
                for count in current_items.values():
                    fav += MathEngine.get_space(count, k_pulls, mode)
            
            # ب. مختلفة الألوان مثنى مثنى
            elif "مختلف" in q:
                for combo in combinations(current_items.values(), k_pulls):
                    ways = math.prod(combo)
                    if mode != "في آن واحد": ways *= math.factorial(k_pulls)
                    fav += ways
            
            # ج. كرات محددة (حمراء، خضراء...)
            else:
                target = next((name for name in current_items if name in q), list(current_items.keys())[0])
                n_i = current_items[target]
                n_o = total_n - n_i
                
                # استخراج الرقم المطلوب (مثلاً: 2 حمراء)
                nums = re.findall(r'\d+', q)
                # إصلاح خطأ SyntaxError الظاهر في الصورة 7
                if nums:
                    x = int(nums[0])
                else:
                    x = 1
                
                # النطاق (بالضبط، على الأقل، على الأكثر)
                if "اقل" in q: rng = range(x, k_pulls + 1)
                elif "اكثر" in q: rng = range(0, x + 1)
                else: rng = [x]
                
                for r in rng:
                    ways = math.comb(n_i, r) * math.comb(n_o, k_pulls - r)
                    if mode != "في آن واحد":
                        ways *= MathEngine.get_ordering_factor(k_pulls, [r, k_pulls - r])
                    fav += ways

            # عرض النتائج
            if total_space > 0:
                p = fav / total_space
                frac = Fraction(fav, total_space).limit_denominator()
                st.markdown(f"""
                <div class="result-box">
                    <h3>🎯 النتيجة النهائية: {p:.5f}</h3>
                    <h4>الكسر المبسط: {frac.numerator} / {frac.denominator}</h4>
                </div>
                """, unsafe_allow_html=True)
                st.latex(rf"P(A) = \frac{{{fav}}}{{{total_space}}} = {p:.4f}")
                st.balloons()
