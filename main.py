import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="주민등록 인구 및 세대 현황 대시보드", layout="wide")

st.title("📊 주민등록 인구 및 세대 현황 시각화 대시보드")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="utf-8")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"CSV 파일을 불러오는 중 오류 발생: {e}")
    st.stop()

st.subheader("데이터 미리보기")
st.dataframe(df.head())

# 기본 정보 요약
st.subheader("데이터 요약 정보")
st.write(df.describe(include="all"))

# 컬럼 선택
cols = df.columns.tolist()
if "행정구역" in cols:
    region_col = "행정구역"
else:
    region_col = st.selectbox("지역(행정구역) 컬럼을 선택하세요:", cols)

# 선택 옵션
regions = st.multiselect("시각화할 지역을 선택하세요:", df[region_col].unique(), default=df[region_col].unique()[:5])

filtered_df = df[df[region_col].isin(regions)]

# 인구 관련 컬럼 탐색
numeric_cols = df.select_dtypes(include=["int", "float"]).columns.tolist()
target_col = st.selectbox("시각화할 지표(예: 총인구수, 세대수 등)", numeric_cols)

# Altair 차트
st.subheader("📈 지역별 인구 현황")
chart = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x=alt.X(region_col, sort="-y"),
        y=alt.Y(target_col),
        tooltip=[region_col, target_col]
    )
    .properties(width=800, height=500)
)
st.altair_chart(chart, use_container_width=True)

# 시계열 차트 (기간 컬럼 있을 경우)
date_cols = [c for c in cols if "년" in c or "월" in c or "기간" in c]
if date_cols:
    date_col = date_cols[0]
    st.subheader("📆 기간별 추이")
    line_chart = (
        alt.Chart(filtered_df)
        .mark_line(point=True)
        .encode(
            x=date_col,
            y=target_col,
            color=region_col,
            tooltip=[region_col, target_col, date_col]
        )
        .properties(width=800, height=400)
    )
    st.altair_chart(line_chart, use_container_width=True)

# 지도 시각화 (위도/경도 컬럼 있으면)
if "위도" in cols and "경도" in cols:
    st.subheader("🗺️ 지역별 인구 지도")
    st.map(filtered_df.rename(columns={"위도": "lat", "경도": "lon"}))

st.success("✅ 시각화가 완료되었습니다!")
