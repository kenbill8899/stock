import streamlit as st
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="投資回測數據看板", page_icon="📊", layout="wide")

st.title("📊 投資回測數據看板")

try:
    # 1. 從 Secrets 讀取 Google 試算表網址
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    else:
        st.error("❌ 未在 Streamlit 後台設定 Secrets，請確認設定中包含 [connections.gsheets]")
        st.stop()

    # 2. 將標準網址轉換為 CSV 下載連結
    csv_url = spreadsheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/edit?" in spreadsheet_url:
        csv_url = spreadsheet_url.split("/edit")[0] + "/export?format=csv"

    # 3. 讀取資料（跳過前兩行現價與損益，直接以第三行當標頭）
    df = pd.read_csv(csv_url, header=2)

    # 4. 強制重新命名欄位名稱，解決欄位重複或點 .1 的問題
    # 對應試算表：A=日期, B=價格, C=股數, D=均價, E=正二當日尾盤, F=原型當日尾盤, G=原型均價, H=正二當日損益, I=原型當日損益
    # 這裡我們只取前 9 個主要欄位，並強制給予標準名稱
    if len(df.columns) >= 9:
        new_columns = list(df.columns)
        new_columns[0] = "正二投入日期"
        new_columns[7] = "正二當日損益"
        new_columns[8] = "原型當日損益"
        df.columns = new_columns

    # 5. 去除空白行（避免對帳單最底下的空白列影響畫圖）
    df = df.dropna(subset=["正二投入日期"])

    # 建立左右兩個區塊，左邊放表格，右邊放曲線圖
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 原始回測數據")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 損益走勢曲線圖")

        # 直接透過強制命名後的欄位來確保存在
        required_columns = ["正二投入日期", "正二當日損益", "原型當日損益"]
        
        # 複製一份乾淨的資料來畫圖
        chart_df = df[required_columns].copy()
        
        # 自動清理資料：將損益欄位（不論是字串帶%還是數字）一律轉成標準浮點數
        for col in ["正二當日損益", "原型當日損益"]:
            # 如果是字串型態且包含 %
            if chart_df[col].dtype == 'object':
                chart_df[col] = chart_df[col].astype(str).str.rstrip('%').str.strip()
                chart_df[col] = pd.to_numeric(chart_df[col], errors='coerce') / 100.0
            else:
                # 如果原本讀進來就已經是數字，但可能因為百分比放大了一百倍
                chart_df[col] = pd.to_numeric(chart_df[col], errors='coerce')
                # 判斷如果數字大於 1 或者是大於某些合理值，且你在試算表看它是百分比，可能需要除以 100
                # 如果圖表數值怪怪的，可以觀察這部分，通常 read_csv 讀取帶 % 的格子都會判定為字串物件(object)

        # 將「正二投入日期」設定為 X 軸的索引
        chart_df = chart_df.set_index("正二投入日期")
        
        # 繪製折線圖
        st.line_chart(chart_df, use_container_width=True)

except Exception as e:
    st.error(f"🚨 程式執行時發生錯誤：{e}")
    st.info("提示：請確認您的 Google 試算表是否已開啟『知道連結的任何人皆可檢視』權限。")
