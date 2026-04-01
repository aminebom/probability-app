import streamlit as st
import math
import re
import itertools

# --- الدوال الرياضية ---
def C(n, p):
    if p > n or p < 0: return 0
    return math.factorial(n) // (math.factorial(p) * math.factorial(n - p))

def A(n, p):
    if p > n or p < 0: return 0
    return math.factorial(n) // math.factorial(n - p)

# --- واجهة التطبيق ---
st.set_page_config(page_title="ProbCalc Pro 67", page_icon="🎲")
st.title("🎲 Probability Master Pro")

if 'box_items' not in st.session_state:
    st.session_state.box_items = {"Red": 5, "Green": 3, "Yellow": 2}

# --- القائمة الجانبية ---
st.sidebar.header("📦 إعدادات الصندوق")
with st.sidebar.expander("إضافة لون جديد"):
    new_color = st.text_input("اسم اللون")
    new_count = st.number_input("العدد", min_value=1, value=1)
    if st.button("إضافة"):
        if new_color:
            st.session_state.box_items[new_color] = new_count
            st.rerun()

total_n = 0
for color, count in list(st.session_state.box_items.items()):
    col1, col2 = st.sidebar.columns([3, 1])
    val = col1.number_input(f"{color}", min_value=0, value=count, key=f"in_{color}")
    st.session_state.box_items[color] = val
    total_n += val
    if col2.button("🗑️", key=f"del_{color}"):
        del st.session_state.box_items[color]
        st.rerun()

st.divider()
col_a, col_b = st.columns(2)
with col_a:
    k = st.number_input("عدد الكرات المسحوبة (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=3)
with col_b:
    mode_display = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

mode = "1" if mode_display == "في آن واحد" else "2"
repl = "yes" if "مع الإرجاع" in mode_display else "no"

st.write("### 💡 الأسئلة المدعومة:")
st.caption("نفس اللون | مختلفة الألوان | على الأقل 1 Red | على الأكثر 2 Green | كرتين من نفس اللون")

question = st.text_input("اكتب سؤالك هنا:", placeholder="مثال: على الأقل 1 Red")

if st.button("⚡ احسب الاحتمال الآن", use_container_width=True):
    total_cases = C(total_n, k) if mode == "1" else ((total_n**k) if repl == "yes" else A(total_n, k))
    favorable = 0
    q = question.lower()
    
    def get_p(n, r): # دالة حساب السحب لعدد معين
        if mode == "1": return C(n, r)
        return (n**r) if repl == "yes" else A(n, r)

    # 1. نفس اللون (الكل من لون واحد)
    if "نفس" in q and "لون" in q:
        for count in st.session_state.box_items.values():
            favorable += get_p(count, k)

    # 2. مختلفة الألوان (واحدة من كل لون)
    elif "مختلف" in q:
        counts = list(st.session_state.box_items.values())
        if len(counts) >= k:
            combos = list(itertools.combinations(counts, k))
            favorable = sum(math.prod(c) for c in combos)
            if mode != "1": favorable *= math.factorial(k) # معامل الترتيب

    # 3. على الأقل (At least)
    elif "أقل" in q:
        target = next((c for c in st.session_state.box_items if c.lower() in q), None)
        num = int(re.findall(r'\d+', q)[0]) if re.findall(r'\d+', q) else 1
        if target:
            n_target = st.session_state.box_items[target]
            n_other = total_n - n_target
            for i in range(num, k + 1):
                if mode == "1":
                    favorable += C(n_target, i) * C(n_other, k - i)
                else:
                    favorable += C(k, i) * get_p(n_target, i) * get_p(n_other, k - i)

    # 4. على الأكثر (At most)
    elif "أكثر" in q:
        target = next((c for c in st.session_state.box_items if c.lower() in q), None)
        num = int(re.findall(r'\d+', q)[0]) if re.findall(r'\d+', q) else 1
        if target:
            n_target = st.session_state.box_items[target]
            n_other = total_n - n_target
            for i in range(0, num + 1):
                if mode == "1":
                    favorable += C(n_target, i) * C(n_other, k - i)
                else:
                    favorable += C(k, i) * get_p(n_target, i) * get_p(n_other, k - i)

    # 5. بالضبط (Exactly)
    elif "بالضبط" in q or any(c.lower() in q for c in st.session_state.box_items):
        target = next((c for c in st.session_state.box_items if c.lower() in q), None)
        num = int(re.findall(r'\d+', q)[0]) if re.findall(r'\d+', q) else 0
        if target:
            n_target = st.session_state.box_items[target]
            n_other = total_n - n_target
            if mode == "1":
                favorable = C(n_target, num) * C(n_other, k - num)
            else:
                favorable = C(k, num) * get_p(n_target, num) * get_p(n_other, k - num)

    if total_cases > 0:
        p = favorable / total_cases
        st.balloons()
        st.metric("الاحتمال P(A)", f"{p:.4f}", f"{p*100:.1f}%")
        st.info(f"**الحالات الموافقة:** {favorable} | **الحالات الكلية:** {total_cases}")

st.sidebar.markdown("---")
st.sidebar.write("© 2026 Developed by Amine | 67")
