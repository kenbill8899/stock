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

    # 4. 🧠 智慧型欄位重命名（在最源頭就正名，徹底避免 KeyError）
    rename_dict = {}
    for col in df.columns:
        col_str = str(col).strip()
        if "日期" in col_str:
            rename_dict[col] = "日期"
        elif "正二" in col_str and "損益" in col_str:
            rename_dict[col] = "正二當日損益"
        elif "原型" in col_str and "損益" in col_str:
            rename_dict[col] = "原型當日損益"

    # 執行重命名
    df = df.rename(columns=rename_dict)

    # 顯示原始數據方便排錯
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 原始回測數據")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 損益走勢曲線圖")
        
        # 5. 檢查正名後的關鍵欄位是否都存在
        if "日期" in df.columns and "正二當日損益" in df.columns and "原型當日損益" in df.columns:
            
            # 建立要畫圖的乾淨 DataFrame
            chart_df = df[["日期", "正二當日損益", "原型當日損益"]].copy()
            
            # 清除日期為空的無效列
            chart_df = chart_df.dropna(subset=["日期"])
            
            # 🌟 核心數值清理：扒光 % 符號、去除前後空白，轉換成數字
            for col in ["正二當日損益", "原型當日損益"]:
                # 統一轉成字串進行文字清理
                chart_df[col] = chart_df[col].astype(str).str.replace('%', '', regex=False).str.strip()
                # 強制轉換成數字，遇到怪字元就變成 NaN
                chart_df[col] = pd.to_numeric(chart_df[col], errors='coerce')
            
            # 濾除轉換失敗的 NaN 列，確保圖表連續
            chart_df = chart_df.dropna(subset=["正二當日損益", "原型當日損益"])

            # 設定 X 軸為日期
            chart_df = chart_df.set_index("日期")
            
            # 確保有數據才畫圖
            if not chart_df.empty:
                st.line_chart(chart_df, use_container_width=True)
            else:
                st.warning("⚠️ 數據經清理後無有效數值可繪製圖表。")
            
        else:
            st.warning("⚠️ 無法自動對齊欄位，請檢查試算表第三行的文字是否包含『日期』、『正二...損益』、『原型...損益』。")
            st.write("目前偵測到的標頭欄位有：", list(df.columns))

except Exception as e:
    st.error(f"🚨 程式執行時發生錯誤：{e}")
