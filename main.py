import streamlit as st
from datetime import datetime
from fiche import get_connection

# ================= إعدادات الصفحة الاحترافية =================
st.set_page_config(
    page_title="ISO SYSTEM - لوحة المالك",
    page_icon="👑",
    layout="centered", # تصميم أنيق في المنتصف
)

# تخصيص CSS متقدم لجعل الواجهة باللغة العربية وفائقة الجمال
st.markdown("""
<style>
    /* تغيير الاتجاه والخط */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* إخفاء القوائم العلوية المزعجة */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تجميل أشرطة التقدم بلون متدرج (Gradient) */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4f46e5 , #818cf8);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= العنوان وزر التحديث =================
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("👑 لوحة المالك - ISO SYSTEM")
with col_btn:
    st.write("") # لضبط المحاذاة
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.rerun()

st.markdown("---")

# ================= جلب البيانات =================
def fetch_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT item_id, customer_name, deadline, designation, quantity, 
               COALESCE(progress_cnc, 0), 
               COALESCE(progress_bending, 0), 
               COALESCE(progress_bending_profiles, 0), 
               COALESCE(progress_welding, 0), 
               COALESCE(progress_painting, 0), 
               COALESCE(progress_packaging, 0),
               is_delivered
        FROM order_items 
        ORDER BY item_id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

try:
    rows = fetch_data()
    active_orders = []
    delivered_count = 0
    
    for row in rows:
        if row[11] == True:
            delivered_count += 1
        else:
            active_orders.append(row)
            
    active_count = len(active_orders)
    
    # الحسابات الذكية
    today = datetime.now()
    overdue_count = new_count = in_progress_count = ready_count = 0

    for row in active_orders:
        item_id, cust, dead_str, desig, qty, p_cnc, p_bend_lames, p_bend_profs, p_weld, p_paint, p_pack, is_deliv = row
        
        if dead_str and dead_str != "غير محدد":
            try:
                if (datetime.strptime(str(dead_str), "%Y-%m-%d") - today).days < 0:
                    overdue_count += 1
            except: pass

        total_prog = float(p_cnc) + float(p_bend_lames) + float(p_weld) + float(p_paint)
        if float(p_pack) >= 100:
            ready_count += 1
        elif total_prog > 0:
            in_progress_count += 1
        else:
            new_count += 1

    # ================= البطاقات العلوية الذكية (KPIs) =================
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="⚙️ قيد التصنيع", value=active_count, delta=f"{new_count} طلب جديد", delta_color="normal")
    kpi2.metric(label="✅ أرشيف المسلّم", value=delivered_count)
    kpi3.metric(label="⚠️ طلبات متأخرة", value=overdue_count, delta="يحتاج تدخلك", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= تبويبات الصفحات (Tabs) =================
    tab_quick, tab_detailed = st.tabs(["📱 المتابعة السريعة", "📊 الإدارة التفصيلية (الأقسام)"])

    # ---------------- 1. شاشة المتابعة السريعة ----------------
    with tab_quick:
        # إحصائيات سريعة
        c_n, c_p, c_r = st.columns(3)
        c_n.info(f"📥 طلب جديد: {new_count}")
        c_p.warning(f"🛠️ قيد الإنجاز: {in_progress_count}")
        c_r.success(f"✅ جاهز للتسليم: {ready_count}")
        
        st.write("")
        if not active_orders:
            st.success("المصنع فارغ، لا توجد طلبات قيد التصنيع!")

        for row in active_orders:
            item_id, cust, dead_str, desig, qty, p_cnc, p_bend_lames, p_bend_profs, p_weld, p_paint, p_pack, is_deliv = row
            total_prog = float(p_cnc) + float(p_bend_lames) + float(p_weld) + float(p_paint)
            
            if float(p_pack) >= 100:
                status, hex_c, bg_c = "جاهز للتسليم ✅", "#10b981", "#d1fae5"
            elif total_prog > 0:
                status, hex_c, bg_c = "قيد الإنجاز 🛠️", "#f59e0b", "#fef3c7"
            else:
                status, hex_c, bg_c = "طلب جديد 📥", "#3b82f6", "#dbeafe"

            # تصميم بطاقة فخمة عبر HTML مدمج
            st.markdown(f"""
            <div style="padding:20px; border-radius:15px; border-right: 6px solid {hex_c}; background-color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #f1f5f9;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h4 style="margin:0; color:#0f172a; font-weight:900;">#{item_id} | {desig}</h4>
                    <span style="color:{hex_c}; font-weight:bold; font-size:13px; background-color:{bg_c}; padding:5px 12px; border-radius:20px;">{status}</span>
                </div>
                <div style="color:#64748b; font-size:15px; font-weight:bold;">
                    👤 العميل: <span style="color:#334155;">{cust}</span> &nbsp;&nbsp;|&nbsp;&nbsp; 📦 الكمية: <span style="color:#334155;">{qty}</span> &nbsp;&nbsp;|&nbsp;&nbsp; ⏳ التسليم: <span style="color:#ef4444;">{dead_str or 'غير محدد'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- 2. شاشة الإدارة التفصيلية ----------------
    with tab_detailed:
        for row in active_orders:
            item_id, cust, dead_str, desig, qty, p_cnc, p_bend_lames, p_bend_profs, p_weld, p_paint, p_pack, is_deliv = row
            
            # القوائم المنسدلة الأنيقة
            with st.expander(f"⚙️ تفاصيل الطلب #{item_id} | {desig}", expanded=False):
                st.write(f"**العميل:** {cust} | **الكمية:** {qty}")
                
                st.write(f"**CNC** ({int(float(p_cnc))}%)")
                st.progress(int(float(p_cnc)) / 100)
                
                if "grille" in str(desig).lower():
                    st.write(f"**ثني اللامات** ({int(float(p_bend_lames))}%)")
                    st.progress(int(float(p_bend_lames)) / 100)
                    st.write(f"**ثني البروفيل** ({int(float(p_bend_profs))}%)")
                    st.progress(int(float(p_bend_profs)) / 100)
                else:
                    st.write(f"**الثني** ({int(float(p_bend_lames))}%)")
                    st.progress(int(float(p_bend_lames)) / 100)
                    
                st.write(f"**اللحام** ({int(float(p_weld))}%)")
                st.progress(int(float(p_weld)) / 100)
                
                st.write(f"**الصباغة** ({int(float(p_paint))}%)")
                st.progress(int(float(p_paint)) / 100)
                
                st.write(f"**التغليف** ({int(float(p_pack))}%)")
                st.progress(int(float(p_pack)) / 100)

except Exception as e:
    st.error(f"خطأ: {e}")