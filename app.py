import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📊 投資回測數據看板")

# 建立 Google Sheets 連線
conn = st.connection("gsheets", type="sheets")

# 讀取數據（可以指定工作表名稱，例如 worksheet="工作表1"）
# ttl="10m" 代表快取 10 分鐘，避免頻繁抓取導致速度變慢
df = conn.read(worksheet="Sheet1", ttl="10m")

# 顯示原始資料表
st.subheader("原始數據")
st.dataframe(df)

# 💡 進階：如果你想在 Streamlit 重現你圖表中的「正二與原型當日損益」折線圖
if "正二當日損益" in df.columns and "正一當日損益" in df.columns:
    st.subheader("損益走勢圖")
    # 將日期設為索引方便畫圖
    chart_data = df.set_index("正二投入日期")[["正二當日損益", "原型當日損益"]]
    st.line_chart(chart_data)
