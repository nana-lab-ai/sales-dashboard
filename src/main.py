import customtkinter as ctk
from ui_overview import setup_overview_tab, refresh_overview_table
from ui_monthly import setup_monthly_tab
from ui_category_edit import setup_category_tab
from ui_sales_entry import setup_sales_entry_tab
from utils import get_products_df

def launch_view_mode(products_df):
    app = ctk.CTk()
    app.title("売上ダッシュボード")
    app.geometry("1000x700")

    tabview = ctk.CTkTabview(app)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)

    # 売上一覧
    tab_overview = tabview.add("売上一覧")
    setup_overview_tab(tab_overview, products_df)

    # 月別売上
    tab_monthly = tabview.add("月別売上")
    setup_monthly_tab(tab_monthly, products_df) 

    # カテゴリ編集
    tab_category = tabview.add("カテゴリ編集")
    setup_category_tab(tab_category, products_df)

    # 売上登録（← 保存後に一覧更新するため、refresh関数を渡す）
    tab_sales = tabview.add("売上登録")
    setup_sales_entry_tab(tab_sales, refresh_overview_table)

    app.mainloop()

if __name__ == "__main__":
    print("productsマスタ読み込み中...")
    products_df = get_products_df()
    print("読み込み結果:", type(products_df), products_df.shape)
    launch_view_mode(products_df)
