import tkinter as tk
import pandas as pd
from tkinter import ttk
from tkcalendar import DateEntry
import datetime
import customtkinter as ctk
from utils import SALES_CSV, CATEGORIES_CSV, get_products_df
import os

overview_table = None
overview_total_label = None
start_date_widget = None
end_date_widget = None
customer_filter_var = None
category_filter_var = None
default_start_date = None
default_end_date = None

LABEL_FONT = ("Yu Gothic UI", 14)
BUTTON_FONT = ("Yu Gothic UI", 14)
OPTION_FONT = ("Yu Gothic UI", 14)
TABLE_FONT = ("Yu Gothic UI", 13)
TABLE_HEADER_FONT = ("Yu Gothic UI", 14, "bold")

def save_filtered_sales():
    if overview_table is None:
        return

    rows = []
    for child in overview_table.get_children():
        row = overview_table.item(child)["values"]
        rows.append(row)

    if not rows:
        print("保存対象がありません。")
        return

    columns = ["販売日", "顧客名", "カテゴリ名", "商品名", "数量", "金額", "更新日"]
    df = pd.DataFrame(rows, columns=columns)

    os.makedirs("output", exist_ok=True)
    today_str = datetime.date.today().strftime("%Y%m%d")
    file_path = f"output/filtered_sales_{today_str}.csv"

    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"保存しました: {file_path}")

def refresh_overview_table():
    print("refresh_overview_table 実行中")
    products_df = get_products_df()
    
    try:
        # 売上データ CSV 読み込み
        sales_df = pd.read_csv(SALES_CSV)
        joined = pd.merge(sales_df, products_df, on="商品ID", how="left")
        joined["販売日"] = pd.to_datetime(joined["販売日"], errors="coerce")
    except Exception as e:
        print("読み込みエラー:", e)
        return

    start = start_date_widget.get_date()
    end = end_date_widget.get_date()
    joined = joined[(joined["販売日"] >= pd.to_datetime(start)) & (joined["販売日"] <= pd.to_datetime(end))]

    if customer_filter_var.get() != "すべて":
        joined = joined[joined["顧客名"] == customer_filter_var.get()]
    if category_filter_var.get() != "すべて":
        joined = joined[joined["カテゴリ名"] == category_filter_var.get()]

    overview_table.delete(*overview_table.get_children())
    columns = ["販売日", "顧客名", "カテゴリ名", "商品名", "数量", "金額", "更新日"]
    overview_table.configure(columns=columns)
    for col in columns:
        anchor = "w"
        if col in ["販売日", "更新日", "数量"]:
            anchor = "center"
        elif col == "金額":
            anchor = "e"
        overview_table.heading(col, text=col, anchor=anchor)
        overview_table.column(col, anchor=anchor)

    for _, row in joined.iterrows():
        values = [row.get(col, "") for col in columns]
        for date_col in ["販売日", "更新日"]:
            idx = columns.index(date_col)
            dt = pd.to_datetime(values[idx], errors="coerce")
            values[idx] = "" if pd.isna(dt) else dt.strftime("%Y-%m-%d")
        overview_table.insert("", "end", values=values)

    total = pd.to_numeric(joined["金額"], errors="coerce").sum()
    overview_total_label.configure(text=f"売上合計: {int(total)} 円")
    print("一覧更新完了")

def reset_filters():
    customer_filter_var.set("すべて")
    category_filter_var.set("すべて")
    start_date_widget.set_date(default_start_date)
    end_date_widget.set_date(default_end_date)
    refresh_overview_table()

def setup_overview_tab(tab_frame, products_df):
    global overview_table, overview_total_label
    global start_date_widget, end_date_widget
    global customer_filter_var, category_filter_var
    global default_start_date, default_end_date

    try:
        # 売上データ CSV 読み込み（フィルター候補用）
        sales_df = pd.read_csv("data/sales.csv")
        sales_df["販売日"] = pd.to_datetime(sales_df["販売日"], errors="coerce")
        customer_list = ["すべて"] + sorted(sales_df["顧客名"].dropna().unique().tolist())
    except:
        customer_list = ["すべて"]

    try:
        # カテゴリマスタ CSV 読み込み（フィルター候補用）
        categories_df = pd.read_csv("data/categories.csv")
        category_list = ["すべて"] + sorted(categories_df["カテゴリ名"].dropna().unique().tolist())
    except:
        category_list = ["すべて"]

    today = datetime.date.today()
    if today.month >= 4:
        default_start_date = datetime.date(today.year, 4, 1)
    else:
        default_start_date = datetime.date(today.year - 1, 4, 1)
    default_end_date = today

    filter_frame = ctk.CTkFrame(tab_frame)
    filter_frame.pack(fill="x", padx=12, pady=12)

    ctk.CTkLabel(filter_frame, text="期間（販売日）", font=LABEL_FONT).pack(side="left", padx=6)

    start_date_widget = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
    start_date_widget.set_date(default_start_date)
    start_date_widget.pack(side="left", padx=6, pady=2)

    end_date_widget = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
    end_date_widget.set_date(default_end_date)
    end_date_widget.pack(side="left", padx=6, pady=2)

    ctk.CTkLabel(filter_frame, text="顧客名", font=LABEL_FONT).pack(side="left", padx=6)
    customer_filter_var = tk.StringVar(value="すべて")
    customer_menu = ctk.CTkOptionMenu(
        filter_frame, variable=customer_filter_var, values=customer_list, font=OPTION_FONT, dropdown_font=OPTION_FONT
    )
    customer_menu.pack(side="left", padx=6)

    ctk.CTkLabel(filter_frame, text="カテゴリ", font=LABEL_FONT).pack(side="left", padx=6)
    category_filter_var = tk.StringVar(value="すべて")
    category_menu = ctk.CTkOptionMenu(
        filter_frame, variable=category_filter_var, values=category_list, font=OPTION_FONT, dropdown_font=OPTION_FONT
    )
    category_menu.pack(side="left", padx=6)

    search_button = ctk.CTkButton(filter_frame, text="検索", command=refresh_overview_table, font=BUTTON_FONT)
    search_button.pack(side="right", padx=6)

    reset_button = ctk.CTkButton(filter_frame, text="リセット", command=reset_filters, font=BUTTON_FONT)
    reset_button.pack(side="right", padx=6)

    save_button = ctk.CTkButton(filter_frame, text="保存", command=save_filtered_sales, font=BUTTON_FONT)
    save_button.pack(side="right", padx=6)

    table_frame = ctk.CTkFrame(tab_frame)
    table_frame.pack(fill="both", expand=True, padx=12, pady=12)

    vsb = ttk.Scrollbar(table_frame, orient="vertical")
    hsb = ttk.Scrollbar(table_frame, orient="horizontal")

    style = ttk.Style()
    style.configure("Overview.Treeview", font=TABLE_FONT, rowheight=30)
    style.configure("Overview.Treeview.Heading", font=TABLE_HEADER_FONT)
    overview_table = ttk.Treeview(
        table_frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set, style="Overview.Treeview"
    )
    vsb.config(command=overview_table.yview)
    hsb.config(command=overview_table.xview)
    overview_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    overview_total_label = ctk.CTkLabel(tab_frame, text="売上合計: 0 円", font=("Yu Gothic UI", 16, "bold"))
    overview_total_label.pack(pady=8)

    refresh_overview_table()
