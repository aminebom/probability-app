import streamlit as st
import math
import re
import itertools
import google.generativeai as genai
from PIL import Image

# --- 1. إعدادات الذكاء الاصطناعي (Gemini) ---
try:
    # جلب المفتاح من Secrets التي وضعتها في Streamlit Cloud
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
    ai_available = True
except Exception:
    ai_available = False

# --- 2. الدوال الرياضية الأساسية ---
def C(n, p):
    if p > n or p < 0: return 0
    return math.factorial(n) // (math.factorial(p) * math.factorial(n - p))

def A(n, p):
    if p > n or p < 0: return 0
    return math.factorial(n) // math.factorial(n - p)

# --- 3. واجهة المستخدم ---
st.set_page_config(page_title="ProbCalc Pro 67", page_icon="🎲", layout="wide")

st.title("🎲 Probability Master Pro | خبير الاحتمالات الذكي")
st.markdown("---")

# القائمة الجانبية لإعداد الصندوق
st.sidebar.header("📦 إعدادات الصندوق (يدوياً)")
if 'box_items' not in st.session_state:
    st.session_state.box_items = {"Red": 5, "Green": 3, "Yellow": 2}

# إضافة لون جديد
with st.sidebar.expander("➕ إضافة لون جديد"):
    new_color = st.text_input("اسم اللون (مثلاً: أبيض)")
    new_count = st.number_input("العدد", min_value=1, value=1)
    if st.button("إضافة"):
        if new_color:
            st.session_state.box_items[new_color] = new_count
            st.rerun()

# عرض وتعديل الألوان الحالية
total_n = 0
for color, count in list(st.session_state.box_items.items()):
    col1, col2 = st.sidebar.columns([3, 1])
    val = col1.number_input(f"{color}", min_value=0, value=count, key=f"in_{color}")
    st.session_state.box_items[color] = val
    total_n += val
    if col2.button("🗑️", key=f"del_{color}"):
        del st.session_state.box_items[color]
        st.rerun()

# --- 4. قسم تصوير التمرين (AI) ---
st.subheader("📸 حل تمرين بالذكاء الاصطناعي (صورة)")
if not ai_available:
    st.warning("⚠️ ميزة الذكاء الاصطناعي معطلة. يرجى إضافة GEMINI_API_KEY في إعدادات Secrets.")
else:
    uploaded_file = st.file_uploader("ارفع صورة التمرين (كتاب أو ورقة)", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption='التمرين المرفوع', width=400)
        if st.button("🪄 تحليل وحل التمرين فوراً"):
            with st.spinner("جاري قراءة الصورة والحل..."):
                try:
                    prompt = "أنت خبير رياضيات. اقرأ تمرين الاحتمالات في الصورة وحله خطوة بخطوة باللغة العربية، موضحاً نوع السحب والقوانين المستخدمة."
                    response = ai_model.generate_content([prompt, img])
                    st.success("✅ اكتمل الحل!")
                    st.markdown("### 📝 الحل المقترح:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطأ في الاتصال: {e}")

st.markdown("---")

# --- 5. قسم الحساب اليدوي (Logic) ---
st.subheader("🧮 الحساب اليدوي السريع")
col_k, col_mode = st.columns(2)
with col_k:
    k = st.number_input("عدد الكرات المسحوبة (k)", min_value=1, max_value=total_n if total_n > 0 else 1, value=1)
with col_mode:
    mode_display = st.selectbox("نوع السحب", ["في آن واحد", "على التوالي بدون إرجاع", "على التوالي مع الإرجاع"])

# تحويل النص لنوع السحب برمجياً
mode = "1" if mode_display == "في آن واحد" else "2"
repl = "yes" if "مع الإرجاع" in mode_display else "no"

question = st.text_input("اكتب سؤالك (مثال: على الاقل 1 Red، نفس اللون، مختلفة الالوان)")

# زر الشرح والأخطاء
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("❓ شرح"):
        st.info("اكتب 'نفس اللون' للكرات المتشابهة، أو 'على الاقل X' للحد الأدنى. تأكد من تطابق أسماء الألوان!")

# كشف الأخطاء قبل الحساب
if total_n == 0:
    st.error("❌ الصندوق فارغ! أضف كرات من القائمة الجانبية أولاً.")
elif k > total_n and mode_display != "على التوالي مع الإرجاع":
    st.error(f"❌ لا يمكنك سحب {k} كرات من أصل {total_n} بدون إرجاع!")
else:
    if st.button("⚡ احسب الآن", use_container_width=True):
        total_cases = C(total_n, k) if mode == "1" else ((total_n**k) if repl == "yes" else A(total_n, k))
        favorable = 0
        # تنظيف النص من الهمزات لمرونة البحث
        q = question.lower().replace("أ", "ا").replace("إ", "ا")
        
        def get_p(n, r):
            if mode == "1": return C(n, r)
            return (n**r) if repl == "yes" else A(n, r)

        # منطق الحالات المختلفة
        if "نفس" in q:
            for count in st.session_state.box_items.values():
                favorable += get_p(count, k)
        elif "مختلف" in q:
            counts = list(st.session_state.box_items.values())
            if len(counts) >= k:
                combos = list(itertools.combinations(counts, k))
                favorable = sum(math.prod(c) for c in combos)
                if mode != "1": favorable *= math.factorial(k)
        elif "اقل" in q:
            target = next((c for c in st.session_state.box_items if c.lower() in q), None)
            num = int(re.findall(r'\d+', q)[0]) if re.findall(r'\d+', q) else 1
            if target:
                n_t, n_o = st.session_state.box_items[target], total_n - st.session_state.box_items[target]
                for i in range(num, k + 1):
                    favorable += (C(n_t, i) * C(n_o, k-i)) if mode=="1" else (C(k, i) * get_p(n_t, i) * get_p(n_o, k-i))
        elif "اكثر" in q:
            target = next((c for c in st.session_state.box_items if c.lower() in q), None)
            num = int(re.findall(r'\d+', q)[0]) if re.findall(r'\d+', q) else 1
            if target:
                n_t, n_o = st.session_state.box_items[target], total_n - st.session_state.box_items[target]
                for i in range(0, num + 1):
                    favorable += (C(n_t, i) * C(n_o, k-i)) if mode=="1" else (C(k, i) * get_p(n_t, i) * get_p(n_o, k-i))

        if total_cases > 0:
            p = favorable / total_cases
            st.balloons()
            st.metric("الاحتمال النهائي P(A)", f"{p:.4f}", f"{p*100:.2f}%")
            st.info(f"عدد الحالات الممكنة: {total_cases} | الحالات المواتية: {favorable}")

st.sidebar.markdown("---")
st.sidebar.write("© 2026 Developed by Amine | 67")
