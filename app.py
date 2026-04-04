import streamlit as st
import math
import re
from itertools import combinations, permutations, product
from fractions import Fraction

# --- 1. تهيئة الحالة (يجب أن يكون في المقدمة لمنع AttributeError) ---
if 'items' not in st.session_state:
    st.session_state['items'] = {"حمراء": 5, "خضراء": 3, "صفراء": 2}

# --- 2. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="ProbMaster Ultimate 5.0", page_icon="🎲", layout="wide")

st.markdown("""
    <style>
    .main {direction: rtl; text-align: right;}
    .stButton>button {width: 100%; border-radius: 10px; background-color: #1a237e; color: white; height: 3em; font-weight: bold;}
    .res-card {padding: 20px; border-radius: 15px; background-color: #f8f9fa; border-right: 10px solid #1a237e; margin: 10px 0;}
    .step-info {background-color: #e8f5e9; padding: 10px; border-radius: 5px; border-right: 5px solid #2e7d32; margin-bottom: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. المحرك الرياضي ---
class ProbEngine:
    @staticmethod
    def nCr(n, r):
        return math.comb(n, r) if 0 <= r <= n else 0

    @staticmethod
    def nPr(n, r):
        return math.perm(n, r) if 0 <= r <= n else 0

    @staticmethod
    def get_total_space(n, k, mode):
        if mode == "في آن واحد": return ProbEngine.nCr(n, k)
        if mode == "على التوالي بدون إرجاع": return ProbEngine.nPr(n, k)
        return n ** k

    @staticmethod
    def get_ordering_factor(k, r_list):
        denom = 1
        for r in r_list:
            denom *= math.factorial(r)
        return math.factorial(k) // denom

# --- 4. واجهة المستخدم (Sidebar) ---
with st.sidebar:
    st.header("📦 إعدادات الصندوق")
    with st.expander("➕ إضافة عنصر جديد"):
        new_item = st.text_input("اسم الكرة (لون أو رقم)")
        new_count = st.number_input("العدد", min_value=1, value=1)
        if st.button("إضافة للصندوق"):
            if new_item:
                st.session_state['items'][new_item] = new_count
                st.rerun()

    total_n = 0
    # استخدام list(keys) لتجنب RuntimeError أثناء الحذف
    for name in list(st.session_state['items'].keys()):
        col_name, col_del = st.columns([3, 1])
        st.session_state['items'][name] = col_name.number_input(f"{name}", min_value=0, value=st.session_state['items'][name], key=f"val_{name}")
        if col_del.button("🗑️", key=f"del_{name}"):
            del st.session_state['items'][name]
            st.rerun()
    
    total_n = sum(st.session_state['items'].values())
    st.divider()
    st.metric("إجمالي الكرات (n)", total_n)

# --- 5. مدخلات السؤال ---
st.title("🎲 ProbMaster | الإصدار الشامل 5.0")
st.write("تم تطويره بواسطة **Amine | 67** - محرك احتمالات رياضي متكامل")

c1, c2 = st.columns(2)
with c1: k = st.number_input("عدد الكرات المسحوبة (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=3)
with c2: mode = st.selectbox("أسلوب السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

query = st.text_input("💬 اكتب سؤالك (مثلاً: كرتين حمراء، المجموع 10، نفس اللون، مختلفة...)")

# --- 6. معالجة السؤال والحساب ---
if st.button("🚀 احسب الاحتمال"):
    if total_n == 0:
        st.error("الرجاء إضافة كرات للصندوق أولاً!")
        st.stop()

    # تنظيف النص (Parser)
    q = query.lower().replace("أ","ا").replace("إ","ا").replace("ة","ه").replace("ى","ي")
    total_space = ProbEngine.get_total_space(total_n, k, mode)
    fav_cases = 0
    steps = []
    
    # تحديد نوع السؤال
    items = st.session_state['items']
    
    # أ. نفس اللون
    if any(w in q for w in ["نفس", "متماثل"]):
        for count in items.values():
            fav_cases += ProbEngine.get_total_space(count, k, mode)
        steps.append("تم حساب حالات (نفس اللون) لكل لون موجود في الصندوق وجمعها.")

    # ب. مختلفة الألوان (مثنى مثنى)
    elif "مختلف" in q:
        for combo in combinations(items.values(), k):
            ways = math.prod(combo)
            if mode != "في آن واحد": ways *= math.factorial(k)
            fav_cases += ways
        steps.append("تم حساب حالات سحب كرة واحدة من كل لون مختلف.")

    # ج. المجموع أو الجداء (المحاكاة)
    elif any(w in q for w in ["مجموع", "جداء", "ضرب"]):
        target = int(re.findall(r'\d+', q)[0]) if re.findall(r'\d+', q) else 0
        pool = []
        for val, count in items.items():
            try: v = int(val)
            except: v = 0
            pool.extend([v] * count)
        
        # محاكاة ذكية حسب نوع السحب
        if mode == "في آن واحد": space = combinations(pool, k)
        elif mode == "على التوالي بدون إرجاع": space = permutations(pool, k)
        else: space = product(list(set(pool)), repeat=k) # تبسيط للقيم الفريدة

        for s in space:
            res = sum(s) if "مجموع" in q else math.prod(s)
            if res == target: fav_cases += 1
        steps.append(f"تم فحص فضاء العينة للعثور على النتائج التي تحقق الشرط (القيمة = {target}).")

    # د. كرات محددة (بالضبط، على الأقل، على الأكثر)
    else:
        target_item = next((name for name in items if name in q), list(items.keys())[0])
        n_i = items[target_item]
        n_o = total_n - n_i
        num_match = re.findall(r'\d+', q)
        x = int(num_match[0]) if num_match else 1
        
        if "اقل" in q: rng = range(x, k + 1)
        elif "اكثر" in q: rng = range(0, x + 1)
        else: rng = [x]
        
        for r in rng:
            ways = ProbEngine.nCr(n_i, r) * ProbEngine.nCr(n_o, k - r)
            if mode != "في آن واحد":
                ways *= ProbEngine.get_ordering_factor(k, [r, k - r])
            fav_cases += ways
        steps.append(f"تم التحليل بناءً على عدد الكرات {target_item} المطلوبة.")

    # --- 7. عرض النتائج ---
    if total_space > 0:
        prob = fav_cases / total_space
        frac = Fraction(fav_cases, total_space).limit_denominator()
        
        st.markdown(f"""
        <div class="res-card">
            <h3>🎯 الاحتمال: {prob:.5f}</h3>
            <h4>الكسر المبسط: {frac.numerator} / {frac.denominator}</h4>
            <p><b>نسبة مئوية:</b> {prob*100:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📘 تفاصيل الحل والخطوات"):
            st.write(f"**عدد الحالات المواتية:** {fav_cases}")
            st.write(f"**إجمالي الحالات الممكنة:** {total_space}")
            for s in steps: st.markdown(f"<div class='step-info'>✔️ {s}</div>", unsafe_allow_html=True)
            st.latex(rf"P(A) = \frac{{{fav_cases}}}{{{total_space}}}")
        st.balloons()
