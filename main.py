import flet as ft
from fiche import get_connection

def main(page: ft.Page):
    # إعدادات صفحة الهاتف
    page.title = "لوحة المالك - ISO SYSTEM"
    page.window_width = 400
    page.window_height = 700
    page.bgcolor = "#F3F4F6"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT

    # محاولة ضبط التوجيه من اليمين لليسار
    try:
        page.rtl = True
    except:
        pass

    # عنوان التطبيق المضاد للرصاص
    header = ft.Container(
        content=ft.Row(
            controls=[ft.Text("📊 لوحة مراقبة الإنتاج", size=24, weight="bold", color="#1E3A8A")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=20
    )

    cards_column = ft.Column(spacing=15, expand=True)
    
    def load_data(e=None):
        cards_column.controls.clear()
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            # التعديل الأول: جلب الطلبيات غير المسلمة فقط ليتم إخفاء الطلبية تلقائياً عند تحديثها من تطبيق العمال
            cur.execute("""
                SELECT item_id, customer_name, deadline, designation, quantity, 
                       COALESCE(progress_cnc, 0), 
                       COALESCE(progress_bending, 0), 
                       COALESCE(progress_bending_profiles, 0),
                       COALESCE(progress_welding, 0), 
                       COALESCE(progress_painting, 0), 
                       COALESCE(progress_packaging, 0)
                FROM order_items 
                WHERE is_delivered = FALSE OR is_delivered IS NULL
                ORDER BY item_id DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for row in rows:
                item_id, cust_name, deadline, desig, qty, p_cnc, p_bend_lames, p_bend_profs, p_weld, p_paint, p_pack = row
                
                card = ft.Container(
                    bgcolor="white",
                    border_radius=15,
                    padding=20,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color="black12"),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"طلب #{item_id}", size=18, weight="bold", color="#D97706"),
                                    ft.Text(str(cust_name or "بدون اسم"), size=16, weight="bold", color="#1F2937"),
                                ]
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            ft.Text(f"📦 {desig}", size=15, weight="w600", color="#374151"),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"الكمية: {qty}", size=14, color="#4B5563"),
                                    ft.Text(
                                        f"التسليم: {deadline or 'غير محدد'}", 
                                        size=14, 
                                        color="red" if deadline else "#4B5563",
                                        weight="bold" if deadline else "normal"
                                    ),
                                ]
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Row([
                                        ft.Text("CNC", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_cnc or 0)/100, color="blue", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_cnc or 0)}%", size=12, width=35, text_align="right", color="blue")
                                    ]),
                                    ft.Row([
                                        ft.Text("ثني اللامات", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_bend_lames or 0)/100, color="purple", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_bend_lames or 0)}%", size=12, width=35, text_align="right", color="purple")
                                    ]),
                                    ft.Row([
                                        ft.Text("ثني البروفيل", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_bend_profs or 0)/100, color="purple", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_bend_profs or 0)}%", size=12, width=35, text_align="right", color="purple")
                                    ]),
                                    ft.Row([
                                        ft.Text("اللحام", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_weld or 0)/100, color="orange", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_weld or 0)}%", size=12, width=35, text_align="right", color="orange")
                                    ]),
                                    ft.Row([
                                        ft.Text("الصباغة", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_paint or 0)/100, color="red", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_paint or 0)}%", size=12, width=35, text_align="right", color="red")
                                    ]),
                                    ft.Row([
                                        ft.Text("التغليف", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_pack or 0)/100, color="green", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_pack or 0)}%", size=12, width=35, text_align="right", color="green")
                                    ]),
                                    # التعديل الثاني: إضافة قسم التسليم ثابت على 0% للمراقبة فقط وبدون أي أزرار للمالك
                                    ft.Row([
                                        ft.Text("التسليم", width=70, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=0.0, color="teal", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text("0%", size=12, width=35, text_align="right", color="teal")
                                    ]),
                                ]
                            )
                        ]
                    )
                )
                cards_column.controls.append(card)
        except Exception as ex:
            cards_column.controls.append(ft.Text(f"خطأ: {ex}", color="red", text_align="center"))

        page.update()

    # زر تحديث آمن باستخدام اسم الأيقونة مباشرة لمنع أخطاء إصدارات Flet
    page.floating_action_button = ft.FloatingActionButton(
        content=ft.Icon("refresh", color="white"),
        bgcolor="#1E3A8A",
        on_click=load_data
    )

    page.add(header, cards_column)
    load_data()

ft.app(target=main)