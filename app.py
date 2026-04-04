import streamlit as st
import math
import re
from itertools import combinations, permutations, product

# ---------- إعداد الصفحة ----------
st.set_page_config(
    page_title="ProbMaster PRO 4.0",
    page_icon="🎲",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
.main {direction: rtl; text-align: right;}
.block {background:#f5f5f5; padding:15px; border-radius:10px; margin:10px 0;}
</style>
""", unsafe_allow_html=True)

# ---------- ENGINE ----------
class Engine:
    @staticmethod
    def C(n, k):
        return math.comb(n, k) if 0 <= k <= n else 0

    @staticmethod
    def A(n, k):
        return math.perm(n, k) if 0 <= k <= n else 0

    @staticmethod
    def total(n, k, mode):
        if mode == "في آن واحد":
            return Engine.C(n, k)
        elif mode == "على التوالي بدون إرجاع":
            return Engine.A(n, k)
        return n ** k

# ---------- PARSER ----------
def clean(text):
    return text.lower().replace("أ","ا").replace("إ","ا").replace("ة","ه").replace("ى","ي")

def parse(q, items):
    q = clean(q)
    data = {"type":None,"target":None,"num":0}

    patterns = {
        "same": r"(نفس|متماثل)",
        "different": r"(مختلف)",
        "exact": r"(بالضبط)",
        "at_least": r"(على الاقل|اقل)",
        "at_most": r"(على الاكثر|اكثر)",
        "sum": r"(مجموع)",
        "prod": r"(جداء|ضرب)"
    }

    for t,pat in patterns.items():
        if re.search(pat, q):
            data["type"] = t
            break

    nums = re.findall(r'\d+', q)
    if nums:
        data["num"] = int(nums[0])

    for item in items:
        if item.lower() in q:
            data["target"] = item

    return data

# ---------- حماية الأداء ----------
MAX_SIM = 150000

def estimate(n,k,mode):
    if mode=="في آن واحد":
        return math.comb(n,k)
    elif mode=="على التوالي بدون إرجاع":
        return math.perm(n,k)
    return n**k

# ---------- UI ----------
st.title("🎲 ProbMaster PRO 4.0")

if "items" not in st.session_state:
    st.session_state.items = {"حمراء":5,"خضراء":3,"زرقاء":2}

# ---------- Sidebar ----------
with st.sidebar:
    st.header("📦 الصندوق")

    name = st.text_input("عنصر جديد")
    val = st.number_input("عدد",1,100,1)

    if st.button("➕ إضافة"):
        if name:
            st.session_state.items[name]=val
            st.rerun()

    total_n = 0
    for key in list(st.session_state.items.keys()):
        c1,c2 = st.columns([3,1])
        st.session_state.items[key] = c1.number_input(key,0,100,st.session_state.items[key])
        total_n += st.session_state.items[key]
        if c2.button("❌",key=f"del_{key}"):
            del st.session_state.items[key]
            st.rerun()

    st.metric("إجمالي العناصر", total_n)

# ---------- Inputs ----------
col1,col2 = st.columns(2)

with col1:
    k = st.number_input("عدد السحبات (k)",1,total_n if total_n>0 else 1,2)

with col2:
    mode = st.selectbox("نوع السحب",[
        "في آن واحد",
        "على التوالي بدون إرجاع",
        "على التوالي مع الإرجاع"
    ])

q = st.text_input("💬 اكتب سؤالك (مثال: على الأقل 2 حمراء)")

# ---------- Solve ----------
if st.button("🚀 احسب الآن"):
    if total_n == 0:
        st.error("الصندوق فارغ")
        st.stop()

    data = parse(q, st.session_state.items)

    if data["type"] is None:
        st.warning("⚠️ لم أفهم السؤال، حاول صياغة أخرى")
        st.stop()

    total_cases = Engine.total(total_n, k, mode)
    fav = 0
    steps = []
    method = "قانون رياضي"

    items = st.session_state.items

    # SAME
    if data["type"]=="same":
        for c in items.values():
            val = Engine.total(c,k,mode)
            fav += val
            steps.append(f"نحسب حالات كل عنصر: {val}")

    # DIFFERENT
    elif data["type"]=="different":
        keys = list(items.keys())
        for comb in combinations(keys,k):
            ways = 1
            for key in comb:
                ways *= items[key]
            if mode!="في آن واحد":
                ways *= math.factorial(k)
            fav += ways
        steps.append("اختيار عناصر مختلفة وضرب الاحتمالات")

    # EXACT / AT LEAST / AT MOST
    elif data["type"] in ["exact","at_least","at_most"] and data["target"]:
        n_i = items[data["target"]]
        n_o = total_n - n_i
        x = data["num"]

        if data["type"]=="exact":
            rng = [x]
        elif data["type"]=="at_least":
            rng = range(x,k+1)
        else:
            rng = range(0,x+1)

        for r in rng:
            ways = Engine.C(n_i,r)*Engine.C(n_o,k-r)
            if mode!="في آن واحد":
                ways *= math.comb(k,r)

            fav += ways
            steps.append(f"نختار {r} من {data['target']} و {k-r} من الباقي")

    # SUM / PROD
    elif data["type"] in ["sum","prod"]:
        nums = []
        for val,count in items.items():
            try:
                v=int(val)
            except:
                v=0
            nums += [v]*count

        size = estimate(total_n,k,mode)

        if size > MAX_SIM:
            st.warning("⚠️ الأعداد كبيرة، لا يمكن الحساب بدقة")
            st.stop()

        method = "محاكاة ذكية"

        if mode=="في آن واحد":
            space = combinations(nums,k)
        elif mode=="على التوالي بدون إرجاع":
            space = permutations(nums,k)
        else:
            space = product(nums, repeat=k)

        for s in space:
            val = sum(s) if data["type"]=="sum" else math.prod(s)
            if val == data["num"]:
                fav += 1

        steps.append("تم فحص جميع الحالات الممكنة")

    # ---------- Output ----------
    p = fav / total_cases

    st.success(f"🎯 الاحتمال = {p:.5f}")

    with st.expander("📘 شرح كامل"):
        st.write(f"**نوع السؤال:** {data['type']}")
        st.write(f"**العنصر المستهدف:** {data['target']}")
        st.write(f"**القيمة:** {data['num']}")
        st.write(f"**طريقة الحل:** {method}")
        st.write(f"الحالات المواتية = {fav}")
        st.write(f"الحالات الكلية = {total_cases}")

        st.markdown("### 🧠 خطوات الحل")
        for s in steps:
            st.info(s)

        st.latex(rf"P = \frac{{{fav}}}{{{total_cases}}} = {p:.5f}")
