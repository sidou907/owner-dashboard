import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from fiche import get_connection

# ================= إعدادات الصفحة (شاشة عريضة) =================
st.set_page_config(page_title="ISO SYSTEM - المالك", page_icon="👑", layout="wide")

# ================= تنسيق CSS متقدم وآمن =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');
    
    /* التوجيه الكامل من اليمين لليسار */
    .stApp { direction: rtl; }
    
    p, h1, h2, h3, h4, h5, h6, label, div[data-testid="stMetricValue"], .stMarkdown {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to left, #818cf8, #4f46e5);
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; direction: rtl;}
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: transparent;
        border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px;
        font-size: 18px; font-weight: bold; color: #94a3b8;
    }
    .stTabs [aria-selected="true"] { color: #818cf8 !important; background-color: rgba(129, 140, 248, 0.1); border-bottom: 3px solid #818cf8;}
    
    /* ================= 🛠️ الإصلاح الآمن للقوائم 🛠️ ================= */
    [data-testid="stExpander"] { 
        background-color: #111827 !important; 
        border: 1px solid #1f2937 !important; 
        border-radius: 10px !important; 
        margin-bottom: 15px; 
    }
    
    /* إخفاء السهم الأصلي لمتصفح Streamlit فقط بأمان تام */
    [data-testid="stExpander"] details summary svg {
        display: none !important;
    }
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }
    
    /* تجميل خط عنوان الطلبية ليظهر بوضوح مع الإيموجي */
    [data-testid="stExpander"] details summary p {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #f8fafc !important;
        padding-right: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= العنوان والتحديث =================
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown('<h1 style="font-family: Tajawal, sans-serif; font-weight: 900; color: #f8fafc; margin-bottom: 0;">👑 لوحة القيادة <span style="color: #818cf8;">الاستراتيجية</span></h1>', unsafe_allow_html=True)
with col2:
    st.write("")
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ================= ⚡ شريط الماسح الضوئي (QR Scanner) ⚡ =================
st.markdown("""
<div style="background-color: #1e1b4b; padding: 10px; border-radius: 10px; border: 2px dashed #818cf8; text-align: center; margin-bottom: 10px;">
    <h4 style="color: #818cf8; font-family: 'Tajawal', sans-serif; margin: 0;">📷 ضع مؤشر الكتابة في الأسفل، ثم امسح الكود بجهاز HENEX</h4>
</div>
""", unsafe_allow_html=True)
search_query = st.text_input("إدخال الكود", label_visibility="collapsed", placeholder="انتظار المسح الضوئي...", key="scanner")
# ========================================================================

# ================= جلب البيانات =================
@st.cache_data(ttl=60)
def fetch_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT item_id, customer_name, deadline, designation, dimensions, quantity, 
               COALESCE(progress_cnc, 0), COALESCE(progress_bending, 0), 
               COALESCE(progress_bending_profiles, 0), COALESCE(progress_welding, 0), 
               COALESCE(progress_painting, 0), COALESCE(progress_packaging, 0), is_delivered
        FROM order_items ORDER BY item_id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

try:
    rows = fetch_data()
except Exception as e:
    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
    st.stop()

# تصفية الطلبيات النشطة تلقائياً
active_orders = [r for r in rows if not r[12]]

# 🎯 تطبيق فلتر الماسح الضوئي إذا تم قراءة كود
if search_query:
    # نبحث عن الكود الممسوح داخل الـ item_id (مثلاً 337 يطابق 337-1 و 337-2)
    active_orders = [r for r in active_orders if search_query.strip().lower() in str(r[0]).lower()]
    if len(active_orders) == 0:
        st.error(f"❌ لم يتم العثور على أي طلبيات غير مسلمة مطابقة لرقم الفاتورة: {search_query}")
    else:
        st.success(f"✅ تم العثور على {len(active_orders)} قطعة تابعة للفاتورة: {search_query}")

delivered_count = sum(1 for r in rows if r[12])
active_count = len(active_orders)

today = datetime.now()
overdue_count = new_count = in_progress_count = ready_count = 0

for row in active_orders:
    dead_str = row[2]
    if dead_str and dead_str != "غير محدد":
        try:
            if (datetime.strptime(str(dead_str), "%Y-%m-%d") - today).days < 0: overdue_count += 1
        except: pass

    total_prog = float(row[6]) + float(row[7]) + float(row[9]) + float(row[10])
    if float(row[11]) >= 100: ready_count += 1
    elif total_prog > 0: in_progress_count += 1
    else: new_count += 1

# ================= 1. المؤشرات السريعة (KPIs) =================
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("⚙️ قيد التصنيع", active_count, f"{new_count} طلب جديد", delta_color="normal")
kpi2.metric("✅ جاهز للتسليم", ready_count)
kpi3.metric("⚠️ متأخرة", overdue_count, "- يحتاج تدخل" if overdue_count > 0 else "", delta_color="inverse")
kpi4.metric("📦 أرشيف المسلّم", delivered_count)

st.write("")

# ================= 2. التبويبات الفخمة =================
tab_charts, tab_cards, tab_details = st.tabs(["📊 الرسوم البيانية", "📱 البطاقات السريعة", "⚙️ تفاصيل الإنتاج"])

# --- التبويب الأول: الرسوم البيانية ---
with tab_charts:
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("<h4 style='font-family: Tajawal, sans-serif; text-align: center; color: #cbd5e1; margin-bottom: 20px;'>توزيع حالة المصنع</h4>", unsafe_allow_html=True)
        labels = ['طلب جديد 📥', 'قيد الإنجاز 🛠️', 'جاهز للتسليم ✅']
        values = [new_count, in_progress_count, ready_count]
        colors = ['#3b82f6', '#f59e0b', '#10b981']
        
        if sum(values) > 0:
            fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=colors)])
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Tajawal", size=15, color="#f8fafc"), legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("لا توجد بيانات لعرضها.")
            
    with col_chart2:
        st.markdown("<h4 style='font-family: Tajawal, sans-serif; text-align: center; color: #cbd5e1; margin-bottom: 20px;'>أضخم 5 طلبيات قيد التصنيع</h4>", unsafe_allow_html=True)
        if active_orders:
            df = pd.DataFrame(active_orders, columns=['id', 'cust', 'dead', 'desig', 'dims', 'qty', 'c', 'b1', 'b2', 'w', 'p', 'pk', 'del'])
            df['qty'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0)
            df['label'] = "الطلب رقم " + df['id'].astype(str)
            df = df.sort_values(by='qty', ascending=False).head(5)
            
            fig2 = px.bar(df, x='label', y='qty', text='qty', color='qty', color_continuous_scale='purples')
            fig2.update_traces(textposition='outside', textfont=dict(size=14, color="#f8fafc"), marker_line_width=0)
            fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), xaxis_title="", yaxis_title="الكمية", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Tajawal", size=15, color="#f8fafc"), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("لا توجد بيانات لعرضها.")

# --- التبويب الثاني: البطاقات السريعة ---
with tab_cards:
    if not active_orders:
        st.success("المصنع فارغ، لا توجد طلبات قيد التصنيع!")
        
    cols = st.columns(3) 
    for i, row in enumerate(active_orders):
        item_id, cust, dead_str, desig, dims, qty = row[0], row[1], row[2], row[3], row[4], row[5]
        total_prog = float(row[6]) + float(row[7]) + float(row[9]) + float(row[10])
        
        if float(row[11]) >= 100: status, hex_c, bg_c = "جاهز للتسليم ✅", "#10b981", "rgba(16, 185, 129, 0.05)"
        elif total_prog > 0: status, hex_c, bg_c = "قيد الإنجاز 🛠️", "#f59e0b", "rgba(245, 158, 11, 0.05)"
        else: status, hex_c, bg_c = "طلب جديد 📥", "#3b82f6", "rgba(59, 130, 246, 0.05)"

        desig_safe = f"\u202A{desig}\u202C"

        with cols[i % 3]:
            st.markdown(f"""
            <div style="font-family: 'Tajawal', sans-serif; padding: 20px; border-radius: 12px; border: 1px solid {hex_c}40; border-top: 4px solid {hex_c}; background-color: {bg_c}; margin-bottom: 20px; height: auto;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <h5 style="margin: 0; color: #f8fafc; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">#{item_id} | <span style="color:#cbd5e1;">{desig_safe}</span></h5>
                </div>
                <div style="color: {hex_c}; font-weight: bold; font-size: 13px; margin-bottom: 12px; background-color: {hex_c}20; display: inline-block; padding: 4px 10px; border-radius: 20px;">{status}</div>
                <div style="color: #94a3b8; font-size: 13px; line-height: 1.8;">
                    👤 العميل: <span style="color: white;">{cust}</span><br>
                    📏 القياسات: <span style="color: #818cf8; font-weight: bold;">{dims}</span><br>
                    📦 الكمية: <span style="color: white;">{qty}</span> &nbsp;|&nbsp; ⏳ التسليم: <span style="color: #ef4444;">{dead_str or 'غير محدد'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- التبويب الثالث: تفاصيل الإنتاج ---
with tab_details:
    def draw_progress_row(label, val):
        try: val = min(max(int(float(val)), 0), 100)
        except: val = 0
            
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; direction: rtl; font-family: 'Tajawal', sans-serif;">
            <div style="width: 35%; color: #cbd5e1; font-weight: bold; font-size: 14px;">{label}</div>
            <div style="width: 50%; background-color: #1e293b; border-radius: 10px; height: 10px; overflow: hidden; margin: 0 10px;">
                <div style="width: {val}%; background-image: linear-gradient(to left, #818cf8, #4f46e5); height: 100%; border-radius: 10px;"></div>
            </div>
            <div style="width: 15%; color: #818cf8; font-weight: bold; font-size: 14px; text-align: left; direction: ltr;">{val}%</div>
        </div>
        """, unsafe_allow_html=True)

    for row in active_orders:
        item_id, desig, dims, qty = row[0], row[3], row[4], row[5]
        p_cnc, p_bend_lames, p_bend_profs, p_weld, p_paint, p_pack = row[6], row[7], row[8], row[9], row[10], row[11]
        
        # العنوان مع الإيموجي بأمان
        expander_title = f"🏭 الطلب رقم {item_id} ◀ {desig}"
        
        # 💡 الذكاء هنا: إذا قمنا بمسح كود، يتم فتح قائمة التفاصيل تلقائياً لتراها فوراً!
        with st.expander(expander_title, expanded=bool(search_query)):
            
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 10px 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 20px; text-align: center; border: 1px dashed #4f46e5;">
                <span style="color: #94a3b8; font-size: 14px;">📏 القياسات:</span> <strong style="color: #f8fafc; font-size: 16px;">{dims}</strong>
                &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;
                <span style="color: #94a3b8; font-size: 14px;">📦 الكمية:</span> <strong style="color: #f8fafc; font-size: 16px;">{qty}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            draw_progress_row("التخريم (CNC)", p_cnc)
            
            if "grille" in str(desig).lower():
                draw_progress_row("ثني اللامات", p_bend_lames)
                draw_progress_row("ثني البروفيل", p_bend_profs)
            else:
                draw_progress_row("عملية الثني", p_bend_lames)
                
            draw_progress_row("اللحام والتجميع", p_weld)
            draw_progress_row("الصباغة (الفرن)", p_paint)
            draw_progress_row("التغليف النهائي", p_pack)
            
            st.markdown("<hr style='border-color: #334155; margin: 15px 0;'>", unsafe_allow_html=True)
            draw_progress_row("التسليم للعميل 🚚", 0) 
            st.markdown("<br>", unsafe_allow_html=True)