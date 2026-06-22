import streamlit as st
import pandas as pd

st.title("📊 投資回測數據看板")

try:
    # 1. 讀取資料
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    csv_url = spreadsheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/edit?" in spreadsheet_url:
        csv_url = spreadsheet_url.split("/edit")[0] + "/export?format=csv"

    df = pd.read_csv(csv_url)

    # 顯示原始資料表（保留方便對帳，不需要也可以刪除）
    st.subheader("原始數據")
    st.dataframe(df)

    # ------------------ 📈 新增：畫出損益曲線圖 ------------------
    st.subheader("📈 損益走勢曲線圖")

    # 2. 資料前處理（確保欄位名稱跟試算表一致）
    # 假設你的欄位名稱分別是：'正二投入日期', '正二當日損益', '原型當日損益'
    
    # 檢查需要的欄位有沒有在資料表內
    required_columns = ["正二投入日期", "正二當日損益", "原型當日損益"]
    if all(col in df.columns for col in required_columns):
        
        # 複製一份資料來做圖表處理
        chart_df = df[required_columns].copy()
        
        # 如果試算表倒出來的百分比帶有 "%" 符號（變成字串），需要轉成數字
        for col in ["正二當日損益", "原型當日損益"]:
            if chart_df[col].dtype == 'object':
                chart_df[col] = chart_df[col].str.rstrip('%').astype('float') / 100.0
        
        # 將「正二投入日期」設定為 X 軸的索引
        chart_df = chart_df.set_index("正二投入日期")
        
        # 3. 繪製折線圖（曲線）
        st.line_chart(chart_df)
        
    else:
        st.warning("找不到對應的欄位，請確認試算表的標頭名稱是否為：正二投入日期、正二當日損益、原型當日損益")
        st.write("目前偵測到的欄位有：", list(df.columns))
    # -----------------------------------------------------------

except Exception as e:
    st.error(f"讀取資料或繪圖時發生錯誤：{e}")
