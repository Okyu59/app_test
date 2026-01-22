import streamlit as st
import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os

# ---------------------------------------------------------
# 1. 페이지 설정 및 CSS 스타일링 (Lovable Design 적용)
# ---------------------------------------------------------
st.set_page_config(page_title="Monimo Review Dashboard", layout="wide", page_icon="📱")

# 커스텀 CSS 적용
st.markdown("""
<style>
    /* 전체 배경색 변경 */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* 카드 디자인 스타일 정의 */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E9ECEF;
    }
    
    /* 메트릭(KPI) 카드 스타일 */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #E9ECEF;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 14px;
        color: #6C757D;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #212529;
    }
    .metric-delta {
        font-size: 12px;
        color: #ADB5BD;
    }
    
    /* 차트 컨테이너 스타일 */
    .chart-container {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 헤더 스타일 */
    .dashboard-header {
        margin-bottom: 30px;
    }
    .dashboard-title {
        font-size: 2rem;
        font-weight: 800;
        color: #343A40;
    }
    .dashboard-subtitle {
        color: #6C757D;
    }
</style>
""", unsafe_allow_html=True)

APP_ID = 'net.ib.android.smcard'

# ---------------------------------------------------------
# 2. 데이터 수집 함수
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_reviews(days=7):
    try:
        result, _ = reviews(
            APP_ID,
            lang='ko', 
            country='kr', 
            sort=Sort.NEWEST, 
            count=1000  # 데이터 확보를 위해 넉넉히
        )
        
        df = pd.DataFrame(result)
        if df.empty:
            return pd.DataFrame()
            
        df['at'] = pd.to_datetime(df['at'])
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_df = df[df['at'] >= cutoff_date].copy()
        
        return recent_df
    except Exception as e:
        st.error(f"데이터 수집 중 오류: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# 3. 텍스트 분석 함수 (안정적인 Regex 방식)
# ---------------------------------------------------------
def extract_keywords_simple(text_series):
    """Java 의존성 없는 순수 파이썬 키워드 추출"""
    all_text = " ".join(text_series.tolist())
    # 한글과 공백만 남기기
    cleaned_text = re.sub(r'[^가-힣\s]', '', all_text)
    words = cleaned_text.split()
    
    # 불용어 리스트
    stopwords = [
        '앱', '어플', '사용', '이', '것', '저', '수', '때', '자꾸', '왜', '좀', 
        '해', '더', '함', '너무', '정말', '진짜', '해서', '하고', '입니다', '있는', 
        '업데이트', '후', '그냥', '다시', '안', '거', '오류', '로그인'
    ]
    # '로그인', '오류' 같은 핵심 키워드는 불용어에서 제외하고 싶다면 위 리스트에서 제거하세요.
    # 여기서는 "너무 일반적인 단어"만 제거합니다.
    stopwords = ['앱', '어플', '사용', '이', '것', '수', '때', '좀', '더', '함', '너무', '정말', '진짜', '해서', '하고', '입니다']
    
    valid_words = [w for w in words if len(w) > 1 and w not in stopwords]
    return Counter(valid_words)

# ---------------------------------------------------------
# 4. 메인 대시보드 UI
# ---------------------------------------------------------

# 상단 헤더
st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="dashboard-title">📱 Monimo Weekly Pulse</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-subtitle">Data Range: {datetime.now() - timedelta(days=7):%Y-%m-%d} ~ Present</div>', unsafe_allow_html=True)
with c2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 데이터 로드
df = get_reviews(7)

if df.empty:
    st.warning("데이터를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.")
else:
    # --- KPI Cards Section ---
    avg_score = df['score'].mean()
    total_reviews = len(df)
    neg_count = len(df[df['score'] <= 2])
    neg_ratio = (neg_count / total_reviews * 100) if total_reviews > 0 else 0
    
    # 별점 5점 만점 기준 색상
    score_color = "#28a745" if avg_score >= 4.0 else "#ffc107" if avg_score >= 3.0 else "#dc3545"

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value" style="color: {score_color}">{avg_score:.2f}</div>
            <div class="metric-delta">Last 7 days</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Reviews</div>
            <div class="metric-value">{total_reviews:,}</div>
            <div class="metric-delta">New feedbacks</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Negative Ratio (1-2★)</div>
            <div class="metric-value" style="color: #dc3545">{neg_ratio:.1f}%</div>
            <div class="metric-delta">{neg_count} reviews</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Charts Section (Trend & Distribution) ---
    st.markdown("<br>", unsafe_allow_html=True) # Spacer
    
    chart_c1, chart_c2 = st.columns([1, 1])
    
    with chart_c1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Daily Rating Trend")
        
        daily_df = df.groupby(df['at'].dt.date)['score'].mean().reset_index()
        fig_line = px.line(daily_df, x='at', y='score', markers=True)
        fig_line.update_traces(line_color='#007AFF', line_width=3, marker_size=8)
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=250,
            yaxis=dict(range=[0.5, 5.5], gridcolor='#F1F3F5'),
            xaxis=dict(gridcolor='#F1F3F5', title=None)
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_c2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⭐ Rating Distribution")
        
        score_counts = df['score'].value_counts().sort_index()
        colors = ['#dc3545', '#dc3545', '#ffc107', '#28a745', '#28a745'] # 1,2점(적), 3점(황), 4,5점(녹)
        
        fig_bar = px.bar(
            x=score_counts.index, 
            y=score_counts.values,
            text=score_counts.values
        )
        fig_bar.update_traces(marker_color=colors, textposition='outside')
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=250,
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(title=None, tickmode='linear')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Word Cloud Section ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 폰트 경로 확인 (같은 폴더에 NanumGothic.ttf가 있다고 가정)
    font_path = "NanumGothic.ttf" if os.path.exists("NanumGothic.ttf") else None
    if not font_path:
        # Mac 기본 폰트 시도
        if os.path.exists("/System/Library/Fonts/Supplemental/AppleGothic.ttf"):
            font_path = "AppleGothic"
        else:
            font_path = None # 시스템 기본값 사용

    c_wc1, c_wc2 = st.columns(2)
    
    # 부정 리뷰 키워드
    with c_wc1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("##### 🚨 Negative Keywords (1-2 Stars)")
        neg_reviews = df[df['score'] <= 2]['content']
        
        if not neg_reviews.empty:
            keywords = extract_keywords_simple(neg_reviews)
            if keywords:
                wc = WordCloud(
                    font_path=font_path,
                    background_color='white',
                    width=400, height=250,
                    colormap='Reds'
                ).generate_from_frequencies(keywords)
                
                fig, ax = plt.subplots(figsize=(5,3))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
                # Top 3 display
                top_k = keywords.most_common(3)
                st.markdown("**Top Issues:** " + ", ".join([f"`{k}`({v})" for k,v in top_k]))
            else:
                st.info("추출할 키워드가 부족합니다.")
        else:
            st.info("부정 리뷰가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 긍정 리뷰 키워드
    with c_wc2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("##### 🍀 Positive Keywords (4-5 Stars)")
        pos_reviews = df[df['score'] >= 4]['content']
        
        if not pos_reviews.empty:
            keywords_pos = extract_keywords_simple(pos_reviews)
            if keywords_pos:
                wc_pos = WordCloud(
                    font_path=font_path,
                    background_color='white',
                    width=400, height=250,
                    colormap='Teal'
                ).generate_from_frequencies(keywords_pos)
                
                fig, ax = plt.subplots(figsize=(5,3))
                ax.imshow(wc_pos, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
                # Top 3 display
                top_k = keywords_pos.most_common(3)
                st.markdown("**Top Praises:** " + ", ".join([f"`{k}`({v})" for k,v in top_k]))
            else:
                st.info("추출할 키워드가 부족합니다.")
        else:
            st.info("긍정 리뷰가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Raw Data Table ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Review Details")
    
    # 테이블 디자인 개선을 위한 설정
    st.dataframe(
        df[['at', 'score', 'content', 'userName']].sort_values(by='at', ascending=False),
        column_config={
            "at": "Date",
            "score": st.column_config.NumberColumn("Rating", format="%d ⭐"),
            "content": "Comment",
            "userName": "User"
        },
        use_container_width=True,
        hide_index=True,
        height=400
    )
