import flet as ft
import threading
from datetime import datetime
from fiche import get_connection

def main(page: ft.Page):
    page.title = "ISO SYSTEM - لوحة المالك (الإدارة العليا)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f1f5f9" 
    page.padding = 20
    page.window_width = 1200
    page.window_height = 800

    def show_snack(message, color="red"):
        snack = ft.SnackBar(content=ft.Text(message, color="white", weight="bold"), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # ================= عناصر الواجهة =================
    loading_ring = ft.ProgressRing(visible=False, color="#4f46e5")
    
    # بطاقات الإحصائيات (KPIs)
    active_orders_text = ft.Text("0", size=32, weight="bold", color="#1e3a8a")
    delivered_orders_text = ft.Text("0", size=32, weight="bold", color="#10b981")
    overdue_orders_text = ft.Text("0", size=32, weight="bold", color="#ef4444")
    
    # قائمة الطلبيات
    orders_list = ft.ListView(expand=True, spacing=15)

    def create_kpi_card(title, value_control, emoji_text, bg_color):
        return ft.Card(
            expand=True,
            elevation=3,
            content=ft.Container(
                padding=20,
                bgcolor="white",
                border_radius=10,
                content=ft.Row([
                    ft.Container(
                        padding=15,
                        bgcolor=bg_color,
                        border_radius=50,
                        content=ft.Text(emoji_text, size=28) 
                    ),
                    ft.Column([
                        ft.Text(title, size=14, color="grey", weight="bold"),
                        value_control
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0)
                ], alignment=ft.MainAxisAlignment.START)
            )
        )

    kpi_row = ft.Row([
        create_kpi_card("الطلبيات قيد التصنيع", active_orders_text, "⚙️", "#dbeafe"),
        create_kpi_card("إجمالي المسلّم (الأرشيف)", delivered_orders_text, "✅", "#d1fae5"),
        create_kpi_card("الطلبيات المتأخرة ⚠️", overdue_orders_text, "⏳", "#fee2e2"),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

   # ================= جلب البيانات =================
    def fetch_dashboard_data():
        orders_list.controls.clear()
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM order_items WHERE is_delivered = FALSE OR is_delivered IS NULL")
            active_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM order_items WHERE is_delivered = TRUE")
            delivered_count = cur.fetchone()[0]

            # التعديل 1: أضفنا جلب بيانات progress_bending_profiles من قاعدة البيانات
            cur.execute("""
                SELECT item_id, customer_name, deadline, designation, quantity, 
                       progress_cnc, progress_bending, progress_bending_profiles, progress_welding, progress_painting, progress_packaging 
                FROM order_items 
                WHERE is_delivered = FALSE OR is_delivered IS NULL
                ORDER BY item_id DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            overdue_count = 0
            today = datetime.now()
            
            active_orders_text.value = str(active_count)
            delivered_orders_text.value = str(delivered_count)

            if not rows:
                orders_list.controls.append(
                    ft.Container(
                        padding=50, alignment=ft.alignment.center,
                        content=ft.Text("المصنع فارغ حالياً! لا توجد طلبيات قيد التصنيع 🌟", size=20, color="grey", weight="bold")
                    )
                )

            for row in rows:
                # التعديل 2: استقبال المتغير الجديد p_bend_profs
                item_id, cust, dead_str, desig, qty, p_cnc, p_bend_lames, p_bend_profs, p_weld, p_paint, p_pack = row

                is_overdue = False
                if dead_str and dead_str != "غير محدد":
                    try:
                        if (datetime.strptime(dead_str, "%Y-%m-%d") - today).days < 0:
                            is_overdue = True
                            overdue_count += 1
                    except: pass

                def create_progress_row(label, value_str, color):
                    try: val = float(value_str) if value_str else 0.0
                    except: val = 0.0
                    return ft.Row([
                        ft.Text(label, width=90, weight="bold", size=13),
                        ft.ProgressBar(value=val/100, color=color, expand=True, height=8),
                        ft.Text(f"{int(val)}%", width=40, text_align="right", color="grey", size=12)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

                # التعديل 3: بناء محتوى البطاقة بذكاء (إظهار البروفيل فقط إذا كانت Grille)
                desig_lower = str(desig).lower()
                is_grille = "grille" in desig_lower

                card_controls = [
                    ft.Row([
                        ft.Text(f"طلب #{item_id} | {desig}", size=18, weight="bold", color="#d97706"),
                        ft.Container(
                            padding=5, bgcolor="#ef4444" if is_overdue else "#f8fafc", border_radius=5,
                            content=ft.Text(f"التسليم: {dead_str or 'غير محدد'}", color="white" if is_overdue else "black", size=12, weight="bold")
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"الزبون: {cust} | الكمية: {qty}", size=14, weight="bold", color="grey"),
                    ft.Divider(height=10),
                    create_progress_row("CNC", p_cnc, "blue"),
                ]

                # فحص الثني
                if is_grille:
                    card_controls.append(create_progress_row("ثني اللامات", p_bend_lames, "purple"))
                    card_controls.append(create_progress_row("ثني البروفيل", p_bend_profs, "purple")) # يظهر فقط للـ Grille
                else:
                    card_controls.append(create_progress_row("الثني", p_bend_lames, "purple")) # للقطع العادية

                # تكملة باقي الأقسام
                card_controls.extend([
                    create_progress_row("اللحام", p_weld, "orange"),
                    create_progress_row("الصباغة", p_paint, "red"),
                    create_progress_row("التغليف", p_pack, "green"),
                    create_progress_row("التسليم", "0", "teal"),
                ])

                card = ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=20, bgcolor="#fee2e2" if is_overdue else "white", border_radius=10,
                        content=ft.Column(card_controls)
                    )
                )
                orders_list.controls.append(card)

            overdue_orders_text.value = str(overdue_count)

        except Exception as e:
            show_snack(f"خطأ في الاتصال بقاعدة البيانات: {e}", "red")
        finally:
            loading_ring.visible = False
            page.update()

    def refresh_data(e=None):
        loading_ring.visible = True
        page.update()
        threading.Thread(target=fetch_dashboard_data, daemon=True).start()

    # ================= الهيكل النهائي للصفحة =================
    page.add(
        ft.Column([
            ft.Row([
                ft.Text("👑 لوحة تحكم المالك", size=28, weight="bold", color="#1e293b"),
                ft.Row([loading_ring, ft.ElevatedButton(content=ft.Text("🔄 تحديث البيانات", color="white", weight="bold"), bgcolor="#4f46e5", on_click=refresh_data)])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            kpi_row, # عرض البطاقات العلوية
            ft.Container(height=15),
            ft.Text("🏭 مراقبة خطوط الإنتاج الحالية:", size=20, weight="bold", color="#334155"),
            orders_list # عرض قائمة الطلبيات النشطة
        ], expand=True)
    )

    refresh_data()

if __name__ == "__main__":
    ft.app(target=main)