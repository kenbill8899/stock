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

    # 3. 讀取資料（關鍵：header=2 代表跳過前兩行現價與損益，直接以第三行當標頭）
    df = pd.read_csv(csv_url, header=2)

    # 4. 去除空白行與無效資料（避免對帳單最底下的空白列影響畫圖）
    df = df.dropna(subset=["正二投入日期"])

    # 建立左右兩個區塊，左邊放表格，右邊放曲線圖
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 原始回測數據")
        # 顯示處理後的資料表
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 損益走勢曲線圖")

        # 檢查需要的對照欄位是否存在
        required_columns = ["正二投入日期", "正二當日損益", "原型當日損益"]
        if all(col in df.columns for col in required_columns):
            
            # 複製一份乾淨的資料來畫圖
            chart_df = df[required_columns].copy()
            
            # 自動清理資料：如果損益欄位帶有 "%" 符號字串，將它轉成浮點數小數
            for col in ["正二當日損益", "原型當日損益"]:
                if chart_df[col].dtype == 'object':
                    # 移除 %、去除前後空白、轉換為 float
                    chart_df[col] = chart_df[col].astype(str).str.rstrip('%').str.strip()
                    chart_df[col] = pd.to_numeric(chart_df[col], errors='coerce') / 100.0
            
            # 將「正二投入日期」設定為 X 軸的索引
            chart_df = chart_df.set_index("正二投入日期")
            
            # 繪製折線圖
            st.line_chart(chart_df, use_container_width=True)
            
        else:
            st.warning("⚠️ 找不到繪圖對應的欄位，請確認試算表第三行的標頭名稱。")
            st.write("目前程式幫您抓到的標頭欄位有：", list(df.columns))

except Exception as e:
    st.error(f"🚨 程式執行時發生錯誤：{e}")
    st.info("提示：請確認您的 Google 試算表是否已開啟『知道連結的任何人皆可檢視』權限。")
