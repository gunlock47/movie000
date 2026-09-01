# 영화 데이터 그래프 도감 1 - 시간
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    # 1년치(365일) 일별 박스오피스 10위권 기록을 불러옵니다.
    df = pd.read_csv(DATA_URL)
    # 여덟 자리 숫자로 된 날짜 열을 진짜 날짜로 바꿉니다.
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df


df = load_data()

# ── 그래프 1. 영화 하나의 흥행 곡선 ──────────────────────────
st.header("1. 한 영화의 흥행 곡선")

# 드롭다운으로 영화를 고릅니다.
movie_list = sorted(df["영화명"].unique())
movie = st.selectbox("영화를 고르세요", movie_list)

one = df[df["영화명"] == movie].sort_values("날짜")
fig = px.line(one, x="날짜", y="일관객", markers=True)
fig.update_traces(hovertemplate="날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra></extra>")
st.plotly_chart(fig, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 2. 일관객 합계 상위 5편 비교 ──────────────────────
st.header("2. 일관객 합계 상위 5편 비교")

# 영화별 일관객 합계를 구해 상위 5편을 고릅니다.
top5 = df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index
five = df[df["영화명"].isin(top5)].sort_values("날짜")

fig2 = px.line(five, x="날짜", y="일관객", color="영화명", markers=True)
fig2.update_traces(
    hovertemplate="날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(legend_title_text="영화명 (클릭하여 켜고 끄기)")
st.plotly_chart(fig2, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 3. 날짜별 10위권 전체 관객 흐름 ──────────────────
st.header("3. 날짜별 10위권 전체 관객 흐름")

# 날짜별로 10위권 영화들의 일관객을 모두 더합니다.
daily_total = df.groupby("날짜")["일관객"].sum().reset_index()

fig3 = px.area(daily_total, x="날짜", y="일관객")
fig3.update_traces(hovertemplate="날짜 %{x|%Y-%m-%d}<br>합계 관객 %{y:,}명<extra></extra>")

# 합계가 가장 컸던 3일을 찾아 표시합니다.
top3_days = daily_total.sort_values("일관객", ascending=False).head(3)

fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers",
    marker=dict(color="red", size=10),
    name="상위 3일",
    hovertemplate="날짜 %{x|%Y-%m-%d}<br>합계 관객 %{y:,}명<extra></extra>",
)

for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=row["날짜"].strftime("%Y-%m-%d"),
        showarrow=True,
        arrowhead=1,
        yshift=10,
    )

st.plotly_chart(fig3, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 4. 일관객 합계 TOP 10 ─────────────────────────────
st.header("4. 일관객 합계 TOP 10")

# 영화별 일관객 합계와, 10위권에 든 날수(=데이터에 등장한 날수)를 함께 구합니다.
top10 = (
    df.groupby("영화명")
    .agg(합계일관객=("일관객", "sum"), 상위권일수=("날짜", "count"))
    .sort_values("합계일관객", ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top10,
    x="합계일관객",
    y="영화명",
    orientation="h",
    custom_data=["상위권일수"],
)
# 관객이 많은 영화가 위로 오도록 순서를 지정합니다.
fig4.update_layout(yaxis=dict(categoryorder="total ascending"))
fig4.update_traces(
    hovertemplate=(
        "%{y}<br>합계 관객 %{x:,}명<br>10위권 등장 %{customdata[0]}일<extra></extra>"
    )
)

st.plotly_chart(fig4, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 5. 월 × 요일별 관객 히트맵 ────────────────────────
st.header("5. 월 × 요일별 관객 히트맵")

# 날짜에서 월과 요일을 뽑습니다.
heat_df = df.copy()
heat_df["월"] = heat_df["날짜"].dt.month
weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
weekday_map = dict(zip(range(7), weekday_order))
heat_df["요일"] = heat_df["날짜"].dt.weekday.map(weekday_map)

# 월 × 요일별 일관객 합계를 구해 표 형태로 바꿉니다.
pivot = (
    heat_df.groupby(["월", "요일"])["일관객"]
    .sum()
    .reset_index()
    .pivot(index="월", columns="요일", values="일관객")
    .reindex(columns=weekday_order)
)

fig5 = px.imshow(
    pivot,
    color_continuous_scale="Reds",
    labels=dict(x="요일", y="월", color="일관객 합계"),
    aspect="auto",
)
fig5.update_traces(hovertemplate="%{y}월 %{x}요일<br>합계 관객 %{z:,}명<extra></extra>")
fig5.update_yaxes(dtick=1)

st.plotly_chart(fig5, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 앞으로 그래프가 이 아래에 추가됩니다 ──────────
