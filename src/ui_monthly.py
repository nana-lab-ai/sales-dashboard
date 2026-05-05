import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import pandas as pd
import os
from utils import detect_date_columns, SALES_CSV
from utils import detect_date_columns

monthly_table = None
monthly_total_label = None
products_df = None  # 外部からセットされる前提

# --- 月別売上タブ設定 ---
def setup_monthly_tab(tab_frame, loaded_products_df):
    global monthly_table, monthly_total_label, products_df
    products_df = loaded_products_df

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    monthly_table = ttk.Treeview(
        frame, show="headings", style="Custom.Treeview",
        yscrollcommand=vsb.set, xscrollcommand=hsb.set
    )
    vsb.config(command=monthly_table.yview)
    hsb.config(command=monthly_table.xview)

    monthly_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    monthly_total_label = ctk.CTkLabel(tab_frame, text="月別売上ビュー", font=("Arial", 18, "bold"))
    monthly_total_label.pack(pady=5)

    refresh_monthly_table()

# --- 月別売上表更新 ---
def refresh_monthly_table():
    global products_df
    if products_df is None or not os.path.exists(SALES_CSV):
        return

    # 売上データ CSV 読み込み
    sales_df = pd.read_csv(SALES_CSV)
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")

    date_col = detect_date_columns(joined)[0]
    joined[date_col] = pd.to_datetime(joined[date_col], errors='coerce')
    joined['年月'] = joined[date_col].dt.to_period('M')
    monthly_summary = joined.groupby('年月')['金額'].sum().reset_index()
    monthly_summary['年月'] = monthly_summary['年月'].astype(str)

    monthly_table.delete(*monthly_table.get_children())
    monthly_table.configure(columns=["年月", "売上合計"])

    for col in ["年月", "売上合計"]:
        monthly_table.heading(col, text=col)
        monthly_table.column(col, width=200, anchor="center", stretch=False)

    for _, row in monthly_summary.iterrows():
        monthly_table.insert("", "end", values=[row["年月"], int(row["金額"])])

    monthly_total_label.configure(text=f"月別売上合計: {int(monthly_summary['金額'].sum())} 円")
