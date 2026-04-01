import streamlit as st
import math
import re

# --- الدوال الرياضية الأساسية ---
def C(n, p):
    if p > n or p < 0: return 0
    return math.factorial(n) // (math.factorial(p) * math.factorial(n - p))

def A(n, p):
    if p > n or p < 0: return 0
    return math.factorial(n) // math.factorial(n - p)

# --- إعدادات واجهة التطبيق ---
st.set_page_config(page_title="ProbCalc Pro", page_icon="🎲")
st.title("🎲 Probability Master Pro")

# --- استخدام session_state لتخزين البيانات ---
if 'box_items' not in st.session_state:
    st.session_state.box_items = {"Red": 5, "Green": 3}

# --- القائمة الجانبية ---
st.sidebar.header("📦 إعدادات الصندوق")

# إضافة لون جديد
with st.sidebar.expander("إضافة لون جديد"):
    new_color = st.text_input("اسم اللون")
    new_count = st.number_input("العدد", min_value=1, value=1, key="add_new")
    if st.button("إضافة"):
        if new_color:
            st.session_state.box_items[new_color] = new_count
            st.rerun()

# عرض وتعديل الألوان الحالية
st.sidebar.subheader("الألوان الحالية:")
total_n = 0
current_items = list(st.session_state.box_items.items())

for color, count in current_items:
    col1, col2 = st.sidebar.columns([3, 1])
    val = col1.number_input(f"{color}", min_value=0, value=count, key=f"input_{color}")
    st.session_state.box_items[color] = val
    total_n += val
    if col2.button("🗑️", key=f"del_{color}"):
        del st.session_state.box_items[color]
        st.rerun()

# --- واجهة الحساب الرئيسية ---
st.divider()
st.write(f"### المجموع الكلي للكرات: {total_n}")

col_a, col_b = st.columns(2)
with col_a:
    k = st.number_input("عدد العناصر المسحوبة (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=min(2, total_n) if total_n > 0 else 1)
with col_b:
    mode_display = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

if mode_display == "في آن واحد": mode, repl = "1", "no"
elif mode_display == "على التوالي مع الإرجاع": mode, repl = "2", "yes"
else: mode, repl = "2", "no"

question = st.text_input("اكتب سؤالك بالعربية (مثال: نفس اللون، بالضبط 1 Red)", placeholder="اكتب هنا...")

if st.button("⚡ احسب الآن", use_container_width=True):
    total_cases = 0
    favorable = 0
    
    if mode == "1":
        total_cases = C(total_n, k)
    else:
        total_cases = (total_n ** k) if repl == "yes" else A(total_n, k)
    
    def get_fav(n, r):
        if mode == "1": return C(n, r)
        return (n ** r) if repl == "yes" else A(n, r)

    q_clean = question.lower()
    if "نفس" in q_clean:
        for color, count in st.session_state.box_items.items():
            favorable += get_fav(count, k)
    
    elif "بالضبط" in q_clean or any(c.lower() in q_clean for c in st.session_state.box_items):
        target = next((c for c in st.session_state.box_items if c.lower() in q_clean), None)
        nums = re.findall(r'\d+', q_clean)
        x = int(nums[0]) if nums else 0
        
        if target:
            n_c = st.session_state.items[target]
            n_others = total_n - n_c
            if mode == "1": favorable = C(n_c, x) * C(n_others, k - x)
            else: favorable = C(k, x) * get_fav(n_c, x) * get_fav(n_others, k - x)

    if total_cases > 0:
        p = favorable / total_cases
        st.balloons()
        st.metric("الاحتمال P(A)", f"{p:.4f}", f"{p*100:.1f}%")
        
        c1, c2 = st.columns(2)
        c1.info(f"**الحالات الموافقة:** {favorable}")
        c2.success(f"**الحالات الكلية:** {total_cases}")
    else:
        st.error("تأكد من إدخال بيانات صحيحة!")

# --- إضافة حقوق الملكية والرمز 67 ---
st.sidebar.markdown("---") # خط فاصل
st.sidebar.markdown("<br><br>", unsafe_control_width=True) # مسافة إضافية للأسفل
st.sidebar.write("© 2026 Developed by Amine | 67") # النص المطلوب
st.sidebar.caption("All Rights Reserved")
