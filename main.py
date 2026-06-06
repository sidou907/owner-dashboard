import flet as ft
import os
from fiche import get_connection

def main(page: ft.Page):
    # إعدادات صفحة الهاتف
    page.title = "لوحة المالك - ISO SYSTEM"
    page.window_width = 400
    page.window_height = 700
    page.bgcolor = "#F3F4F6"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT

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
            # 1. التعديل الأول: جلب بيانات الثني من قاعدة البيانات
            cur.execute("""
                SELECT item_id, customer_name, deadline, designation, quantity, 
                       COALESCE(progress_cnc, 0), COALESCE(progress_welding, 0), 
                       COALESCE(progress_painting, 0), COALESCE(progress_packaging, 0),
                       COALESCE(progress_lamellas, 0), COALESCE(progress_profiles, 0)
                FROM order_items 
                ORDER BY item_id DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for row in rows:
                # 2. التعديل الثاني: استقبال البيانات الجديدة في متغيرات
                item_id, cust_name, deadline, desig, qty, p_cnc, p_weld, p_paint, p_pack, p_lamellas, p_profiles = row
                
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
                                    # 3. التعديل الثالث: جعلنا width=75 للكل ليتسع للكلمات الجديدة، وأضفنا أشرطة الثني
                                    ft.Row([
                                        ft.Text("CNC", width=75, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_cnc or 0)/100, color="blue", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_cnc or 0)}%", size=12, width=35, text_align="right", color="blue")
                                    ]),
                                    ft.Row([
                                        ft.Text("اللحام", width=75, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_weld or 0)/100, color="orange", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_weld or 0)}%", size=12, width=35, text_align="right", color="orange")
                                    ]),
                                    ft.Row([
                                        ft.Text("الصباغة", width=75, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_paint or 0)/100, color="red", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_paint or 0)}%", size=12, width=35, text_align="right", color="red")
                                    ]),
                                    ft.Row([
                                        ft.Text("التغليف", width=75, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_pack or 0)/100, color="green", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_pack or 0)}%", size=12, width=35, text_align="right", color="green")
                                    ]),
                                    ft.Row([
                                        ft.Text("ثني اللامات", width=75, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_lamellas or 0)/100, color="teal", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_lamellas or 0)}%", size=12, width=35, text_align="right", color="teal")
                                    ]),
                                    ft.Row([
                                        ft.Text("ثني البروفيل", width=75, size=12, weight="bold", color="#374151"), 
                                        ft.ProgressBar(value=float(p_profiles or 0)/100, color="purple", bgcolor="#E5E7EB", expand=True, height=8), 
                                        ft.Text(f"{int(p_profiles or 0)}%", size=12, width=35, text_align="right", color="purple")
                                    ])
                                ]
                            )
                        ]
                    )
                )
                cards_column.controls.append(card)
        except Exception as ex:
            print("Error loading data:", ex)
            cards_column.controls.append(ft.Text("تعذر جلب البيانات من السيرفر", color="red"))
            
        page.update()
    # زر تحديث نهائي ومضمون
    page.floating_action_button = ft.FloatingActionButton(
        content=ft.Text("تحديث", color="white", weight="bold"),
        bgcolor="#1E3A8A",
        on_click=load_data
    )

    page.add(header, cards_column)
    load_data()
port = int(os.environ.get("PORT", 8080))
ft.app(target=main, host="0.0.0.0", port=port, view=ft.AppView.WEB_BROWSER)