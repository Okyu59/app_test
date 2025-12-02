import os
import re
from collections import Counter
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
from google_play_scraper import Sort, reviews
from wordcloud import WordCloud

# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="모니모 리뷰 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_ID = "net.ib.android.smcard"  # 모니모 패키지명

# ---------------------------------------------------------
# 전역 CSS – KPI 카드 / 키워드 뱃지 / 리뷰 카드 스타일
# ---------------------------------------------------------
st.markdown(
    """
<style>
body {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* KPI 카드 */
.kpi-wrapper {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}
.kpi-card {
    flex: 1;
    padding: 18px 20px;
    border-radius: 18px;
    color: #ffffff;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
    position: relative;
    overflow: hidden;
}
.kpi-title {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 6px;
}
.kpi-sub {
    font-size: 12px;
    opacity: 0.85;
}
.kpi-avg-score {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
}
.kpi-total-reviews {
    background: linear-gradient(135deg, #ec4899, #f97316);
}
.kpi-negative-ratio {
    background: linear-gradient(135deg, #f97373, #ef4444);
}

/* 카드 공통 */
.card {
    background: #ffffff;
    padding: 18px 22px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    margin-bottom: 18px;
}

/* 키워드 뱃지 */
.keyword-badge {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid transparent;
}
.badge-positive {
    background: #e5f6ea;
    color: #137333;
    border-color: rgba(19, 115, 51, 0.25);
}
.badge-negative {
    background: #feecec;
    color: #b80606;
    border-color: rgba(184, 6, 6, 0.25);
}

/* 리뷰 리스트 */
.review-list {
    max-height: 650px;
    overflow-y: auto;
    padding-right: 4px;
}
.review-card {
    background: #ffffff;
    padding: 14px 16px;
    border-radius: 14px;
    margin-bottom: 10px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
}
.review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    margin-bottom: 6px;
    color: #6b7280;
}
.review-user {
    font-weight: 600;
    color: #111827;
}
.review-score {
    font-weight: 600;
    color: #f59e0b;
}
.review-content {
    color: #374151;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 1. 데이터 수집 (캐시)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_reviews(days: int = 7) -> pd.DataFrame:
    """최근 N일간의 Google Play 리뷰를 수집."""
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

# ---------------------------------------------------------
# 2. 텍스트 분석 – 순수 파이썬 한국어 토큰나이저
# ---------------------------------------------------------
def extract_keywords(text_series: pd.Series) -> Counter:
    """
    리뷰 텍스트에서 한글 키워드를 추출해 빈도수 Counter로 반환.
    - 한글 2글자 이상 단어만 사용
    - 간단한 불용어 제거
    """
    all_text = " ".join(text_series.dropna().astype(str).tolist())

    # 한글 2글자 이상 토큰 추출
    tokens = re.findall(r"[가-힣]{2,}", all_text)

    stopwords = [
        "모니모", "삼성카드",
        "앱", "어플", "사용", "이", "것", "저", "수", "때",
        "자꾸", "왜", "좀", "해", "더", "함", "정도",
        "그리고", "그냥", "진짜", "보고", "해서", "하면",
    ]
    tokens = [t for t in tokens if t not in stopwords]

    return Counter(tokens)

# ---------------------------------------------------------
# 3. WordCloud용 폰트 경로 탐색
# ---------------------------------------------------------
def get_korean_font_path() -> str | None:
    candidates = [
        "/System/Library/Fonts/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "malgun.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

FONT_PATH = get_korean_font_path()

# ---------------------------------------------------------
# 4. UI 렌더링 함수들
# ---------------------------------------------------------
def render_kpi_cards(avg_score: float, total_reviews: int, negative_ratio: float) -> None:
    html = f"""
    <div class="kpi-wrapper">
        <div class="kpi-card kpi-avg-score">
            <div class="kpi-title">평균 평점</div>
            <div class="kpi-value">{avg_score:.2f} ⭐</div>
            <div class="kpi-sub">선택한 기간 기준 평균 앱 평점</div>
        </div>
        <div class="kpi-card kpi-total-reviews">
            <div class="kpi-title">총 리뷰 수</div>
            <div class="kpi-value">{total_reviews} 건</div>
            <div class="kpi-sub">선택한 기간 동안 수집된 리뷰 수</div>
        </div>
        <div class="kpi-card kpi-negative-ratio">
            <div class="kpi-title">부정 리뷰 비율</div>
            <div class="kpi-value">{negative_ratio:.1f}%</div>
            <div class="kpi-sub">1~2점 리뷰 비중</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_keyword_badges(counter_obj: Counter, positive: bool = True) -> None:
    style_class = "badge-positive" if positive else "badge-negative"

    if not counter_obj:
        st.write("키워드가 충분하지 않습니다.")
        return

    items = counter_obj.most_common(5)
    badges = "".join(
        f"<span class='keyword-badge {style_class}'>{k} ({v})</span>"
        for k, v in items
    )
    st.markdown(f"<div class='card'>{badges}</div>", unsafe_allow_html=True)

def render_review_list(df: pd.DataFrame) -> None:
    st.markdown("<div class='review-list'>", unsafe_allow_html=True)

    for _, row in df.sort_values(by="at", ascending=False).iterrows():
        user = row.get("userName", "익명 사용자") or "익명 사용자"
        score = row.get("score", "-")
        content = row.get("content", "")
        date_str = row["at"].strftime("%Y-%m-%d")

        card_html = f"""
        <div class="review-card">
            <div class="review-header">
                <span class="review-user">{user}</span>
                <span class="review-score">⭐ {score}</span>
            </div>
            <div class="review-header" style="margin-bottom:4px;">
                <span>{date_str}</span>
            </div>
            <div class="review-content">{content}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 메인 앱
# ---------------------------------------------------------
def main():
    st.title("📱 모니모 플레이스토어 리뷰 대시보드")
    st.caption("Google Play 리뷰를 기반으로 모니모 앱의 사용자 반응을 분석합니다.")

    # 사이드바 – 기간 선택
    with st.sidebar:
        st.header("⚙️ 분석 옵션")
        days = st.slider("최근 N일 기준", min_value=3, max_value=30, value=7, step=1)
        st.write("선택한 기간:", f"최근 {days}일")

    # 데이터 로드
    with st.spinner("Google Play 리뷰를 수집하는 중입니다..."):
        try:
            df = get_reviews(days)
        except Exception as e:
            st.error(f"데이터 수집 중 오류 발생: {e}")
            return

    if df.empty:
        st.warning("선택한 기간 동안 작성된 리뷰가 없거나 수집되지 않았습니다.")
        return

    # KPI
    avg_score = df["score"].mean()
    total_reviews = len(df)
    negative_ratio = len(df[df["score"] <= 2]) / total_reviews * 100

    render_kpi_cards(avg_score, total_reviews, negative_ratio)

    # 좌/우 레이아웃
    left_col, right_col = st.columns([0.6, 0.4], gap="large")

    # ----- 좌측: 추이 + 키워드 -----
    with left_col:
        st.subheader("📈 일별 평균 평점 추이")
        daily_df = (
            df.groupby(df["at"].dt.date)["score"].mean().reset_index(name="score")
        )
        daily_df.rename(columns={"at": "date"}, inplace=True)

        fig_line = px.line(
            daily_df,
            x="date",
            y="score",
            markers=True,
            labels={"date": "날짜", "score": "평점"},
        )
        fig_line.update_traces(line_shape="spline", line={"width": 4})
        fig_line.update_yaxes(range=[0.5, 5.5])
        fig_line.update_layout(
            height=320,
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=30, b=30),
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")
        st.subheader("🔑 주요 키워드 분석")

        positive_reviews = df[df["score"] >= 4]["content"]
        negative_reviews = df[df["score"] <= 2]["content"]

        tab_neg, tab_pos = st.tabs(["🔥 부정 리뷰", "🍀 긍정 리뷰"])

        with tab_neg:
            if not negative_reviews.empty:
                neg_keywords = extract_keywords(negative_reviews)
                st.markdown("**Top 5 부정 키워드**")
                render_keyword_badges(neg_keywords, positive=False)

                st.markdown("**Word Cloud**")
                if FONT_PATH is None:
                    st.info("한글 폰트를 찾을 수 없어 WordCloud가 깨져 보일 수 있습니다.")
                wc = WordCloud(
                    font_path=FONT_PATH,
                    background_color="white",
                    width=800,
                    height=300,
                ).generate_from_frequencies(neg_keywords)

                fig, ax = plt.subplots(figsize=(8, 3))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("부정 리뷰가 충분하지 않습니다.")

        with tab_pos:
            if not positive_reviews.empty:
                pos_keywords = extract_keywords(positive_reviews)
                st.markdown("**Top 5 긍정 키워드**")
                render_keyword_badges(pos_keywords, positive=True)

                st.markdown("**Word Cloud**")
                if FONT_PATH is None:
                    st.info("한글 폰트를 찾을 수 없어 WordCloud가 깨져 보일 수 있습니다.")
                wc_pos = WordCloud(
                    font_path=FONT_PATH,
                    background_color="white",
                    width=800,
                    height=300,
                ).generate_from_frequencies(pos_keywords)

                fig2, ax2 = plt.subplots(figsize=(8, 3))
                ax2.imshow(wc_pos, interpolation="bilinear")
                ax2.axis("off")
                st.pyplot(fig2)
                plt.close(fig2)
            else:
                st.info("긍정 리뷰가 충분하지 않습니다.")

    # ----- 우측: 리뷰 리스트 -----
    with right_col:
        st.subheader("📝 리뷰 원문 보기")
        render_review_list(df[["userName", "score", "content", "at"]])

if __name__ == "__main__":
    main()
