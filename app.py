import streamlit as st
import pandas as pd

st.title("📊 投資回測數據看板")

# 1. 直接從 Secrets 讀取網址
try:
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # 2. 將標準試算表網址轉換成 CSV 下載連結（最穩定的抓取方式）
    csv_url = spreadsheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/edit?" in spreadsheet_url:
        # 處理沒有特定 gid 或網址帶有其他參數的情況
        csv_url = spreadsheet_url.split("/edit")[0] + "/export?format=csv"

    # 3. 直接用 pandas 讀取，繞過 st.connection
    df = pd.read_csv(csv_url)

    # 顯示原始資料表
    st.subheader("原始數據")
    st.dataframe(df)

except Exception as e:
    st.error(f"讀取資料時發生錯誤：{e}")
    st.info("請確認你的 .streamlit/secrets.toml 或 Streamlit 後台的 Secrets 設定格式是否正確。")
