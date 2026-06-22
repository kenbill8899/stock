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

    # 4. 智慧型欄位搜尋（模糊比對）
    date_col = None
    leverage_profit_col = None
    underlying_profit_col = None

    for col in df.columns:
        col_str = str(col).strip()
        if "日期" in col_str:
            date_col = col
        elif "正二" in col_str and "損益" in col_str:
            leverage_profit_col = col
        elif "原型" in col_str and "損益" in col_str:
            underlying_profit_col = col

    # 顯示原始數據方便排錯
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 原始回測數據")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 損益走勢曲線圖")
        
        if date_col and leverage_profit_col and underlying_profit_col:
            
            # 建立要畫圖的 DataFrame
            chart_df = pd.DataFrame({
                "日期": df[date_col],
                "正二當日損益": df[leverage_profit_col],
                "原型當日損益": df[underlying_profit_col]
            })
            
            # 清除日期或數據為空的無效列
            chart_df = chart_df.dropna(subset=["日期"])
            
            # 🌟 核心修正：強力清除所有非數字雜質，強制轉為 float 數字
            for col in ["正二當日損益", "原型當日損益"]:
                # 先把欄位轉為純字串，拔掉 % 符號、去除前後空白
                chart_df[col] = chart_df[col].astype(str).str.replace('%', '', regex=False).str.strip()
                # 強制轉換成數字，遇到真的無法轉換的文字就變成 NaN
                chart_df[col] = pd.to_numeric(chart_df[col], errors='coerce')
            
            # 再次確保沒有 NaN 導致斷線
            chart_df = chart_df.dropna(subset=["正二當日損益", "原型當日損益"])

            # 設定 X 軸
            chart_df = chart_df.set_index("日期")
            
            # 檢查是否還有剩餘數據可畫
            if not chart_df.empty:
                # 繪製曲線圖
                st.line_chart(chart_df, use_container_width=True)
            else:
                st.warning("数据經清理後皆非有效數值，無法繪圖。")
            
        else:
            st.warning("⚠️ 無法自動對齊欄位，請檢查試算表標頭。")

except Exception as e:
    st.error(f"🚨 程式執行時發生錯誤：{e}")
