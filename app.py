# ---------------------------------------------------------
# 모니모 리뷰 대시보드 — 개선 버전(애니메이션 WordCloud 포함)
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import re
import random
import requests
import os

# ---------------------------------------------------------
# 0. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="모니모 리뷰 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 1. 스타일 커스터마이징
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        /* 전체 가로폭 제한 + 중앙정렬 */
        .main-container {
            max-width: 1600px;
            margin: auto;
        }
        .block-container {
            padding-top: 2rem !important;
        }

        /* KPI 카드 스타일 개선 */
        .kpi-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 26px 32px;
            box-shadow: 0px 4px 18px rgba(0,0,0,0.07);
            text-align: center;
            transition: all 0.25s ease;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0px 8px 25px rgba(0,0,0,0.12);
        }
        .kpi-value {
            font-size: 34px;
            font-weight: 700;
        }
        .kpi-label {
            font-size: 15px;
            color: #666;
            margin-top: 6px;
        }

        /* 긍정 카드 — 파란색 강조 */
        .kpi-positive {
            background: linear-gradient(135deg, #d9ecff, #f1f7ff);
        }

        /* 섹션 간 여백 증가 */
        .section-spacing {
            margin-top: 40px;
            margin-bottom: 32px;
        }

        /* 앱 로고 사이즈 개선 */
        .app-logo {
            width: 90px;
            height: 90px;
            object-fit: contain;
            margin-right: 14px;
        }

        /* Solar icons (Duotone Bold) 크기 정의 */
        .solar-icon {
            width: 26px;
            height: 26px;
            cursor: pointer;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

CONTAINER_START = '<div class="main-container">'
CONTAINER_END = '</div>'
st.markdown(CONTAINER_START, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. 한글 폰트 다운로드
# ---------------------------------------------------------
FONT_PATH = "/tmp/NotoSansCJK-Regular.otf"

if not os.path.exists(FONT_PATH):
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJK-Regular.otf"
    r = requests.get(url)
    with open(FONT_PATH, "wb") as f:
        f.write(r.content)


# ---------------------------------------------------------
# 3. 불용어 + 토크나이저
# ---------------------------------------------------------
STOPWORDS = set([
    "모니모","삼성카드","앱","어플","사용","이","그","저","것","수","때","자꾸","왜","좀",
    "해","더","함","그리고","그냥","진짜","해서","하면","이번","최근","거의","계속","매우",
    "너무","하고","하기","다른","정말","무슨","다시",
    "이렇게","로","없고","누르면"
])

def tokenize(text):
    """한글 기반 단순 토크나이징"""
    text = re.sub(r"[^가-힣0-9\s]", " ", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    words = [w for w in words if len(w) >= 2 and w not in STOPWORDS]
    return words

def extract_keywords(series):
    counter = Counter()
    for t in series.dropna().astype(str):
        counter.update(tokenize(t))
    return counter


# ---------------------------------------------------------
# 4. 데이터 수집
# ---------------------------------------------------------
APP_ID = "net.ib.android.smcard"

@st.cache_data(ttl=3600)
def get_reviews(days=7):
    result, _ = reviews(
        APP_ID,
        lang="ko",
        country="kr",
        sort=Sort.NEWEST,
        count=300
    )
    df = pd.DataFrame(result)
    df["at"] = pd.to_datetime(df["at"])

    cutoff = datetime.now() - timedelta(days=days)
    return df[df["at"] >= cutoff]


# ---------------------------------------------------------
# 5. 상단 헤더 (앱 로고 + 타이틀 + 설정)
# ---------------------------------------------------------
cols_header = st.columns([0.12, 0.78, 0.10])

with cols_header[0]:
    st.markdown(
        f"""
        <img class="app-logo" src="https://play-lh.googleusercontent.com/g-tkfYaRAe0u_DqUAtk4ETg0nl3ZoJIrntTC_K-A4WmpeP-yQi80IHsugmpMEGm9qWCD82HbeeyI-tYQsH1YKg">
        """,
        unsafe_allow_html=True,
    )

with cols_header[1]:
    st.markdown("## 📱 모니모 플레이스토어 리뷰 분석 대시보드")

with cols_header[2]:
    if st.button("⚙️ 설정", key="settings_button"):
        st.session_state["show_settings"] = True


# ---------------------------------------------------------
# 6. 팝업 설정창
# ---------------------------------------------------------
if st.session_state.get("show_settings", False):
    with st.modal("🔧 분석 옵션 설정"):
        days_option = st.slider("최근 리뷰 수집 기간(일)", 3, 30, 7)
        if st.button("닫기"):
            st.session_state["show_settings"] = False


days = st.session_state.get("days_option", 7)

# ---------------------------------------------------------
# 7. 데이터 로드
# ---------------------------------------------------------
df = get_reviews(days)

if df.empty:
    st.warning("최근 리뷰가 부족합니다.")
    st.markdown(CONTAINER_END, unsafe_allow_html=True)
    st.stop()


# ---------------------------------------------------------
# 8. KPI 카드
# ---------------------------------------------------------
total_reviews = len(df)
avg_score = df["score"].mean()
positive_ratio = len(df[df["score"] >= 4]) / total_reviews * 100
negative_ratio = len(df[df["score"] <= 2]) / total_reviews * 100

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="kpi-card"><div class="kpi-value">'
                f"{avg_score:.2f} ⭐</div><div class='kpi-label'>평균 평점</div></div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="kpi-card"><div class="kpi-value">'
                f"{total_reviews} 건</div><div class='kpi-label'>총 리뷰 수</div></div>", unsafe_allow_html=True)

with c3:
    st.markdown('<div class="kpi-card kpi-positive"><div class="kpi-value">'
                f"{positive_ratio:.1f}%</div><div class='kpi-label'>긍정 리뷰 비율</div></div>", unsafe_allow_html=True)

with c4:
    st.markdown('<div class="kpi-card"><div class="kpi-value">'
                f"{negative_ratio:.1f}%</div><div class='kpi-label'>부정 리뷰 비율</div></div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 9. 그래프
# ---------------------------------------------------------
st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
st.subheader("📅 일별 평균 평점 추이")

daily_df = df.groupby(df["at"].dt.date)["score"].mean().reset_index()
fig = px.line(
    daily_df,
    x="at", y="score",
    markers=True,
    labels={"at": "날짜", "score": "평점"}
)
fig.update_yaxes(range=[1, 5])
st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# 10. 키워드 분석
# ---------------------------------------------------------
st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
st.subheader("🔑 주요 키워드 분석")

positive_reviews = df[df["score"] >= 4]["content"]
negative_reviews = df[df["score"] <= 2]["content"]

tab1, tab2 = st.tabs(["🔥 부정 리뷰 키워드", "🍀 긍정 리뷰 키워드"])

def render_wordcloud_and_keywords(text_series):
    keywords = extract_keywords(text_series)

    # 랜덤 상태 매번 변경 (애니메이션 느낌)
    random_state = random.randint(0, 99999)

    wc = WordCloud(
        font_path=FONT_PATH,
        background_color="white",
        width=1000,
        height=600,
        max_words=150,
        random_state=random_state,
        color_func=lambda *args, **kwargs: f"hsl({random.randint(0,360)}, 70%, 45%)",
    ).generate_from_frequencies(keywords)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    st.pyplot(fig)

    # Top 10 키워드 노출
    top10 = [k for k, v in keywords.most_common(10)]
    st.markdown(f"**Top 10 키워드:** {top10}")


with tab1:
    render_wordcloud_and_keywords(negative_reviews)

with tab2:
    render_wordcloud_and_keywords(positive_reviews)


# ---------------------------------------------------------
# 11. 리뷰 원문 (페이지네이션)
# ---------------------------------------------------------
st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
st.subheader("📝 리뷰 원문")

page_size = 15
total_pages = (len(df) - 1) // page_size + 1
page = st.number_input("페이지 선택", 1, total_pages, 1)

start = (page - 1) * page_size
end = start + page_size

st.dataframe(
    df[["at", "userName", "score", "content"]].sort_values("at", ascending=False).iloc[start:end],
    use_container_width=True
)

st.markdown(CONTAINER_END, unsafe_allow_html=True)
