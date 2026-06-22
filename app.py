import streamlit as st
import pandas as pd

st.set_page_config(page_title="投資回測數據看板", page_icon="📊", layout="wide")
st.title("📊 投資回測數據看板")

try:
    # 1. 讀取 Secrets 網址
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    else:
        st.error("❌ 未在 Streamlit 後台設定 Secrets")
        st.stop()

    # 2. 轉換網址
    csv_url = spreadsheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/edit?" in spreadsheet_url:
        csv_url = spreadsheet_url.split("/edit")[0] + "/export?format=csv"

    # 3. 讀取資料（跳過前兩行現價與損益，直接以第三行當標頭）
    df = pd.read_csv(csv_url, header=2)

    # 清除完全是空值的欄位與列
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)

    # 4. 智慧型欄位重命名
    rename_dict = {}
    for col in df.columns:
        col_str = str(col).strip()
        if "日期" in col_str:
            rename_dict[col] = "日期"
        elif "正二" in col_str and "損益" in col_str:
            rename_dict[col] = "正二當日損益"
        elif "原型" in col_str and "損益" in col_str:
            rename_dict[col] = "原型當日損益"

    df = df.rename(columns=rename_dict)

    # 建立左右兩個區塊
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 原始回測數據")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 損益走勢曲線圖")
        
        if "日期" in df.columns and "正二當日損益" in df.columns and "原型當日損益" in df.columns:
            
            chart_df = df[["日期", "正二當日損益", "原型當日損益"]].copy()
            chart_df = chart_df.dropna(subset=["日期"])
            
            # 🌟 修正：只清除文字中的 % 與空白，直接轉成原本的數值，不再除以 100
            for col in ["正二當日損益", "原型當日損益"]:
                chart_df[col] = chart_df[col].astype(str).str.replace('%', '', regex=False).str.strip()
                chart_df[col] = pd.to_numeric(chart_df[col], errors='coerce')
            
            chart_df = chart_df.dropna(subset=["正二當日損益", "原型當日損益"])
            chart_df = chart_df.set_index("日期")
            
            if not chart_df.empty:
                # 繪製曲線圖
                st.line_chart(chart_df, use_container_width=True)
            else:
                st.warning("⚠️ 數據經清理後無有效數值可繪製圖表。")
            
        else:
            st.warning("⚠️ 無法自動對齊欄位，請檢查試算表標頭。")

except Exception as e:
    st.error(f"🚨 程式執行時發生錯誤：{e}")
