import streamlit as st
import pandas as pd
import plotly.express as px

# 網頁標題
st.set_page_config(page_title="凱基證券 vs 競品社群觀測站", layout="wide")
st.title("📊 證券品牌社群影響力觀測站 (18-29歲 TA)")

# 讀取爬蟲抓下來的資料
try:
    df = pd.read_csv('competitor_data.csv')
    
    # --- 頂部概覽卡片 ---
    st.subheader("🔥 今日聲量概況")
    col1, col2, col3 = st.columns(3)
    
    total_posts = len(df)
    top_brand = df['brand'].value_counts().idxmax()
    avg_likes = round(df['likeCount'].mean(), 1)
    
    col1.metric("總監測篇數", f"{total_posts} 篇")
    col2.metric("聲量冠軍", top_brand)
    col3.metric("平均按讚數", avg_likes)

    # --- 圖表區 ---
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.write("### 各品牌聲量佔比 (Share of Voice)")
        fig_pie = px.pie(df, names='brand', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.write("### 互動數對比 (Likes vs Comments)")
        fig_bar = px.bar(df, x='brand', y=['likeCount', 'commentCount'], 
                         barmode='group', title="社群互動強度")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 詳細資料表 ---
    st.write("### 📥 最新熱門討論內容")
    st.dataframe(df[['collect_date', 'brand', 'title', 'likeCount']].sort_values(by='likeCount', ascending=False))

except FileNotFoundError:
    st.warning("目前還沒有資料喔！請先確認你的 GitHub Actions 爬蟲是否已成功跑出 competitor_data.csv。")
