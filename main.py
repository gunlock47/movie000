import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    # 날짜 열(하이픈 없는 여덟 자리 숫자)을 진짜 날짜 타입으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df


df = load_data(DATA_URL)

# ------------------------------------------------------------
# 구역 1. 영화별 일관객 추이
# ------------------------------------------------------------
st.header("구역 1. 영화별 일관객 추이")

movie_list = sorted(df["영화명"].unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list, key="movie_select_1")

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"'{selected_movie}' 날짜별 일관객 변화",
    labels={"날짜": "날짜", "일관객": "일관객 수"},
)
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)
fig1.update_layout(hovermode="x unified")

st.plotly_chart(fig1, use_container_width=True)

st.info("이 그래프로 알 수 있는 것: (여기에 문구를 입력하세요)")

st.divider()

# ------------------------------------------------------------
# 구역 2. 일관객 합계 상위 5편 비교
# ------------------------------------------------------------
st.header("구역 2. 일관객 합계 상위 5편 비교")

top5_movies = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index
)
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객 변화",
    labels={"날짜": "날짜", "일관객": "일관객 수", "영화명": "영화명"},
)
fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(hovermode="x unified", legend_title_text="영화명 (클릭하여 켜고 끄기)")

st.plotly_chart(fig2, use_container_width=True)

st.info("이 그래프로 알 수 있는 것: (여기에 문구를 입력하세요)")

st.divider()

# ------------------------------------------------------------
# 구역 3. (다음 그래프를 위한 자리)
# ------------------------------------------------------------
st.header("구역 3. (추가 예정)")
st.caption("다음 그래프가 이 자리에 추가됩니다.")

# st.info("이 그래프로 알 수 있는 것: (여기에 문구를 입력하세요)")
