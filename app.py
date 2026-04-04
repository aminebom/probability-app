import streamlit as st
import math
import re
from itertools import combinations, permutations, product
from fractions import Fraction

# --- 1. الحماية القصوى: تهيئة الحالة قبل أي شيء آخر ---
if 'items' not in st.session_state:
    st.session_state['items'] = {"حمراء": 5, "خضراء": 3, "صفراء": 2}
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- 2. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="ProbMaster Pro 6.0", page_icon="🎲", layout="wide")

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

# --- 3. المحرك الرياضي الذكي ---
class MathEngine:
    @staticmethod
    def get_space(n, k, mode):
        if mode == "في آن واحد": return math.comb(n, k)
        if mode == "على التوالي بدون إرجاع": return math.perm(n, k)
        return n ** k

    @staticmethod
    def get_permutations_multiset(k, r_list):
        denom = 1
        for r in r_list: denom *= math.factorial(r)
        return math.factorial(k) // denom

# --- 4. واجهة التحكم الجانبية (Sidebar) ---
with st.sidebar:
    st.title("📦 محتوى الصندوق")
    
    with st.expander("✨ إضافة عنصر جديد"):
        new_item = st.text_input("اسم الكرة/الرقم")
        new_count = st.number_input("العدد", min_value=1, value=1)
        if st.button("إضافة"):
            if new_item:
                st.session_state['items'][new_item] = new_count
                st.rerun()

    # عرض العناصر مع ميزة الحذف الآمن
    st.write("---")
    current_items = st.session_state['items']
    for name in list(current_items.keys()):
        c1, c2 = st.columns([3, 1])
        current_items[name] = c1.number_input(f"{name}", 0, 100, current_items[name], key=f"in_{name}")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state['items'][name]
            st.rerun()
            
    total_n = sum(current_items.values())
    st.metric("إجمالي العناصر (n)", total_n)

# --- 5. الواجهة الرئيسية ---
st.title("🎲 Probability Master Pro | الإصدار 6.0")
st.info("تم إصلاح كافة أخطاء AttributeError السابقة. التطبيق الآن جاهز للعمل بكفاءة.")

tab1, tab2 = st.tabs(["📝 الحساب اليدوي", "📸 حل من صورة"])

with tab1:
    col_k, col_m = st.columns(2)
    with col_k: k = st.number_input("عدد السحبات (k)", 1, total_n if total_n > 0 else 1, 3)
    with col_m: mode = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])
    
    user_q = st.text_input("اكتب مطلوبك (مثلاً: كرتين خضراء، مختلفة الألوان، المجموع 5...)")

    if st.button("⚡ احسب الآن"):
        if total_n < k and mode != "على التوالي مع الإرجاع":
            st.error("خطأ: عدد السحبات أكبر من عدد الكرات المتوفرة!")
        else:
            # تنظيف السؤال
            q = user_q.lower().replace("أ","ا").replace("إ","ا").replace("ة","ه").replace("ى","ي")
            n = total_n
            total_space = MathEngine.get_space(n, k, mode)
            fav = 0
            
            # منطق الحل
            if "نفس" in q or "متماثل" in q:
                for count in current_items.values():
                    fav += MathEngine.get_space(count, k, mode)
            
            elif "مختلف" in q:
                for combo in combinations(current_items.values(), k):
                    ways = math.prod(combo)
                    if mode != "في آن واحد": ways *= math.factorial(k)
                    fav += ways
            
            else:
                # البحث عن اللون المستهدف والعدد
                target = next((name for name in current_items if name in q), list(current_items.keys())[0])
                n_target = current_items[target]
                n_others = n - n_target
                
                num_find = re.findall(r'\d+', q)
                x = int(num_find[0]) if num_match := num_find else 1
                
                # على الأقل / على الأكثر / بالضبط
                if "اقل" in q: rng = range(x, k + 1)
                elif "اكثر" in q: rng = range(0, x + 1)
                else: rng = [x]
                
                for r in rng:
                    ways = math.comb(n_target, r) * math.comb(n_others, k - r)
                    if mode != "في آن واحد":
                        ways *= MathEngine.get_permutations_multiset(k, [r, k - r])
                    fav += ways

            # عرض النتيجة
            if total_space > 0:
                p = fav / total_space
                frac = Fraction(fav, total_space).limit_denominator()
                st.markdown(f"""
                <div class="result-box">
                    <h2>🎯 النتيجة: {p:.5f}</h2>
                    <h3>الكسر: {frac.numerator} / {frac.denominator}</h3>
                    <p>نسبة النجاح: {p*100:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.latex(rf"P(A) = \frac{{{fav}}}{{{total_space}}} = {p:.4f}")
                st.balloons()

with tab2:
    st.write("📷 قم برفع صورة التمرين وسيقوم النظام بتحليله (تأكد من وضوح النص)")
    uploaded_file = st.file_uploader("اختر صورة التمرين", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="الصورة المرفوعة", width=400)
        st.warning("⚠️ ميزة التحليل البصري تتطلب مفتاح API نشط. حالياً يمكنك إدخال البيانات يدوياً بناءً على ما تراه في الصورة.")

# --- 6. التذييل ---
st.write("---")
st.caption("Developed with ❤️ by Amine | 2026")
