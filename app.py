import os
import re
import math
from collections import Counter
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google_play_scraper import Sort, reviews
from wordcloud import WordCloud

# ---------------------------------------------------------
# 1. 기본 설정 & 페이지 구성
# ---------------------------------------------------------
st.set_page_config(
    page_title="Review Pulse - Monimo",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="💬"
)

APP_ID = "net.ib.android.smcard"  # 모니모 패키지명

# ---------------------------------------------------------
# 2. Lovable 스타일 CSS (Tailwind 느낌 구현)
# ---------------------------------------------------------
st.markdown(
    """
    <!-- Google Fonts & Iconify -->
    <link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css" rel="stylesheet">
    <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>

    <style>
    /* Global Reset & Font */
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }
    
    /* Background */
    .stApp {
        background-color: #F8FAFC; /* Slate-50 */
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Header Styling */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    .header-title h1 {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    .header-title p {
        font-size: 14px;
        color: #64748B;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Metric Cards (Lovable Style) */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .kpi-label {
        font-size: 14px;
        font-weight: 600;
        color: #64748B;
    }
    .kpi-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    /* Icon Background Colors */
    .bg-blue { background: #EFF6FF; color: #3B82F6; }
    .bg-purple { background: #F5F3FF; color: #8B5CF6; }
    .bg-green { background: #ECFDF5; color: #10B981; }
    .bg-red { background: #FEF2F2; color: #EF4444; }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.25rem;
    }
    .kpi-desc {
        font-size: 13px;
        color: #94A3B8;
    }

    /* Content Cards */
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        height: 100%;
    }
    .card-title {
        font-size: 16px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid transparent;
    }
    .badge-pos { background: #ECFDF5; color: #059669; border-color: #A7F3D0; }
    .badge-neg { background: #FEF2F2; color: #DC2626; border-color: #FECACA; }

    /* Review List Styling */
    .review-item {
        padding: 1rem;
        border-bottom: 1px solid #F1F5F9;
        transition: background 0.15s;
    }
    .review-item:last-child { border-bottom: none; }
    .review-item:hover { background: #F8FAFC; }
    
    .review-top {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
    }
    .review-user {
        font-size: 13px;
        font-weight: 600;
        color: #334155;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .review-stars { color: #F59E0B; font-size: 12px; }
    .review-date { font-size: 12px; color: #94A3B8; }
    .review-text {
        font-size: 14px;
        color: #475569;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* Pagination */
    .pagination-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-top: 10px;
        color: #64748B;
        font-size: 14px;
    }

    /* Tabs Styling Hack */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border: none;
        color: #64748B;
        font-weight: 600;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        color: #6366F1 !important; /* Indigo-500 */
        border-bottom: 2px solid #6366F1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 3. 데이터 로직 (캐시 적용)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_reviews(days: int = 7) -> pd.DataFrame:
    result, _ = reviews(
        APP_ID,
        lang="ko",
        country="kr",
        sort=Sort.NEWEST,
        count=300,
    )
    df = pd.DataFrame(result)
    df["at"] = pd.to_datetime(df["at"])
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_df = df[df["at"] >= cutoff_date].copy()
    return recent_df

# 불용어 및 토큰화
KOREAN_STOPWORDS = {
    "모니모", "삼성카드", "앱", "어플", "사용", "이", "그", "저", "것", "수", "때",
    "자꾸", "왜", "좀", "해", "더", "함", "정도", "그리고", "그냥", "진짜", "보고",
    "해서", "하면", "이번", "최근", "거의", "계속", "매우", "이후", "이후로", "이후에",
    "다시", "너무", "하고", "하기", "다른", "정말", "무슨", "이렇게", "없고", "누르면",
    "업데이트", "로그인", "실행", "화면", "접속", "문제", "설치", "지금", "자체", "오늘"
}

def tokenize_korean(text: str):
    text = re.sub(r"[^가-힣0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    tokens = text.split()
    return [t for t in tokens if len(t) >= 2 and t not in KOREAN_STOPWORDS and not t.isdigit()]

def extract_unigrams(text_series: pd.Series) -> Counter:
    all_tokens = []
    for t in text_series.dropna().astype(str):
        all_tokens.extend(tokenize_korean(t))
    return Counter(all_tokens)

# 폰트 경로 찾기
def get_korean_font_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "NanumGothic.ttf"),
        os.path.join(base_dir, "NotoSansKR-Regular.otf"),
        "/System/Library/Fonts/AppleGothic.ttf",
        "malgun.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None
FONT_PATH = get_korean_font_path()

# ---------------------------------------------------------
# 4. 컴포넌트 렌더링 함수
# ---------------------------------------------------------
def render_header(days):
    html = f"""
    <div class="header-container">
        <div class="header-title">
            <h1>Review Pulse</h1>
            <p>모니모 앱 사용자 반응 분석 대시보드 (최근 {days}일)</p>
        </div>
        <div style="display:flex; align-items:center;">
            <!-- Placeholder for Streamlit widgets if needed -->
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_kpi(avg_score, total_reviews, negative_ratio, positive_ratio):
    # Lovable 스타일: 흰색 카드, 왼쪽 상단 아이콘
    html = f"""
    <div class="kpi-grid">
        <!-- Card 1: Total Reviews -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">수집된 리뷰</span>
                <div class="kpi-icon bg-blue">
                    <iconify-icon icon="solar:chat-round-line-duotone"></iconify-icon>
                </div>
            </div>
            <div class="kpi-value">{total_reviews:,}</div>
            <div class="kpi-desc">선택 기간 내 신규 리뷰</div>
        </div>

        <!-- Card 2: Avg Score -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">평균 평점</span>
                <div class="kpi-icon bg-purple">
                    <iconify-icon icon="solar:stars-minimalistic-bold-duotone"></iconify-icon>
                </div>
            </div>
            <div class="kpi-value">{avg_score:.2f}</div>
            <div class="kpi-desc">5.0 만점 기준</div>
        </div>

        <!-- Card 3: Positive -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">긍정 비율 (4-5점)</span>
                <div class="kpi-icon bg-green">
                    <iconify-icon icon="solar:smile-circle-bold-duotone"></iconify-icon>
                </div>
            </div>
            <div class="kpi-value">{positive_ratio:.1f}%</div>
            <div class="kpi-desc">전체 대비 긍정 리뷰 비중</div>
        </div>

        <!-- Card 4: Negative -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">부정 비율 (1-2점)</span>
                <div class="kpi-icon bg-red">
                    <iconify-icon icon="solar:danger-circle-bold-duotone"></iconify-icon>
                </div>
            </div>
            <div class="kpi-value">{negative_ratio:.1f}%</div>
            <div class="kpi-desc">집중 관리가 필요한 리뷰</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_keyword_badges(counter_obj, positive=True):
    if not counter_obj:
        st.caption("데이터가 부족합니다.")
        return
    
    style_class = "badge-pos" if positive else "badge-neg"
    items = counter_obj.most_common(12)
    
    badges_html = "".join(
        f"<span class='badge {style_class}'>{word} {count}</span>"
        for word, count in items
    )
    st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)

def render_review_list_item(row):
    stars = "★" * int(row['score']) + "☆" * (5 - int(row['score']))
    html = f"""
    <div class="review-item">
        <div class="review-top">
            <div class="review-user">
                <iconify-icon icon="solar:user-circle-bold" style="color:#CBD5E1; font-size:18px;"></iconify-icon>
                {row['userName']}
            </div>
            <span class="review-date">{row['at'].strftime('%Y-%m-%d')}</span>
        </div>
        <div style="margin-bottom:6px;">
            <span class="review-stars">{stars}</span>
        </div>
        <div class="review-text">{row['content']}</div>
    </div>
    """
    return html

# ---------------------------------------------------------
# 5. 메인 로직
# ---------------------------------------------------------
def main():
    # Session State
    if "days" not in st.session_state:
        st.session_state["days"] = 7
    if "page" not in st.session_state:
        st.session_state["page"] = 1

    # 상단 컨트롤 (우측 상단에 배치된 느낌을 주기 위해 컬럼 활용)
    # 실제로는 Header 렌더링 후 아래에 옵션 바 배치
    
    # 1. Custom Header
    render_header(st.session_state["days"])

    # 2. Controls & Data Load
    col_opt, _ = st.columns([0.3, 0.7])
    with col_opt:
        days_new = st.slider("분석 기간 설정 (일)", 3, 30, st.session_state["days"])
        if days_new != st.session_state["days"]:
            st.session_state["days"] = days_new
            st.session_state["page"] = 1
            st.rerun()

    with st.spinner("데이터를 분석하고 있습니다..."):
        try:
            df = get_reviews(st.session_state["days"])
        except Exception as e:
            st.error(f"오류: {e}")
            return

    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 3. KPI Calculations
    avg_score = df["score"].mean()
    total = len(df)
    neg_cnt = len(df[df["score"] <= 2])
    pos_cnt = len(df[df["score"] >= 4])
    neg_ratio = (neg_cnt / total) * 100
    pos_ratio = (pos_cnt / total) * 100

    # 4. Render KPI Cards
    render_kpi(avg_score, total, neg_ratio, pos_ratio)

    # 5. Main Content Grid (Left: Charts/Analysis, Right: Review Feed)
    col_left, col_right = st.columns([1.3, 1], gap="medium")

    # [Left Column]
    with col_left:
        # A. Trend Chart Container
        st.markdown("""
        <div class="content-card">
            <div class="card-title">
                <iconify-icon icon="solar:graph-up-bold-duotone" style="color:#6366F1; font-size:20px;"></iconify-icon>
                일별 평점 추이
            </div>
        """, unsafe_allow_html=True)
        
        daily = df.groupby(df["at"].dt.date)["score"].mean().reset_index()
        fig = px.area(daily, x="at", y="score", height=280)
        fig.update_traces(
            line_color="#6366F1", 
            fill_color="rgba(99, 102, 241, 0.1)",
            mode='lines+markers'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0.5, 5.2], gridcolor="#F1F5F9"),
            xaxis=dict(gridcolor="#F1F5F9"),
            font=dict(family="Pretendard", color="#64748B")
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        # B. Keywords Container
        st.markdown("""
        <div class="content-card">
            <div class="card-title">
                <iconify-icon icon="solar:tag-bold-duotone" style="color:#6366F1; font-size:20px;"></iconify-icon>
                주요 키워드 분석
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["긍정 키워드", "부정 키워드"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            pos_reviews = df[df["score"] >= 4]["content"]
            pos_uni = extract_unigrams(pos_reviews)
            render_keyword_badges(pos_uni, positive=True)
            
            if pos_uni and FONT_PATH:
                wc = WordCloud(font_path=FONT_PATH, background_color="white", 
                               width=600, height=250, colormap="Greens").generate_from_frequencies(pos_uni)
                fig_wc, ax = plt.subplots(figsize=(8,3))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            neg_reviews = df[df["score"] <= 2]["content"]
            neg_uni = extract_unigrams(neg_reviews)
            render_keyword_badges(neg_uni, positive=False)

            if neg_uni and FONT_PATH:
                wc = WordCloud(font_path=FONT_PATH, background_color="white", 
                               width=600, height=250, colormap="Reds").generate_from_frequencies(neg_uni)
                fig_wc, ax = plt.subplots(figsize=(8,3))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc)
        
        st.markdown("</div>", unsafe_allow_html=True)


    # [Right Column] - Review Feed
    with col_right:
        st.markdown("""
        <div class="content-card" style="padding-bottom: 1rem;">
            <div class="card-title">
                <iconify-icon icon="solar:chat-line-bold-duotone" style="color:#6366F1; font-size:20px;"></iconify-icon>
                실시간 리뷰 피드
            </div>
            <div style="height: 600px; overflow-y: auto; padding-right: 5px;">
        """, unsafe_allow_html=True)

        # Pagination Logic
        df_sorted = df.sort_values(by="at", ascending=False)
        PAGE_SIZE = 10
        max_page = math.ceil(len(df_sorted) / PAGE_SIZE)
        
        current_start = (st.session_state["page"] - 1) * PAGE_SIZE
        current_end = current_start + PAGE_SIZE
        page_data = df_sorted.iloc[current_start:current_end]

        for _, row in page_data.iterrows():
            st.markdown(render_review_list_item(row), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True) # End scroll area

        # Pagination Controls
        col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
        with col_p1:
            if st.button("◀ 이전", disabled=st.session_state["page"] <= 1, use_container_width=True):
                st.session_state["page"] -= 1
                st.rerun()
        with col_p3:
            if st.button("다음 ▶", disabled=st.session_state["page"] >= max_page, use_container_width=True):
                st.session_state["page"] += 1
                st.rerun()
        with col_p2:
            st.markdown(
                f"<div class='pagination-container'>{st.session_state['page']} / {max_page}</div>",
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True) # End card

if __name__ == "__main__":
    main()
