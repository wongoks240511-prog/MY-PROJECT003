import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(page_title="주민등록 인구 및 세대 현황 대시보드", layout="wide")
st.title("📊 주민등록 인구 및 세대 현황 시각화 대시보드 (Plotly 버전)")

# --- 데이터 불러오기 ---
@st.cache_data
def load_data():
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="utf-8")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"CSV 파일을 불러오는 중 오류 발생: {e}")
    st.stop()

# --- 데이터 확인 ---
st.subheader("데이터 미리보기")
st.dataframe(df.head())

st.subheader("데이터 기본 정보")
st.write(df.describe(include='all'))

# --- 주요 컬럼 식별 ---
cols = df.columns.tolist()
region_col = None

for c in cols:
    if "행정구역" in c or "지역" in c:
        region_col = c
        break

if not region_col:
    region_col = st.selectbox("지역(행정구역) 컬럼을 선택하세요:", cols)

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
if not numeric_cols:
    st.warning("수치형 컬럼이 없습니다. CSV 파일 구조를 확인해주세요.")
    st.stop()

# --- 지역 선택 ---
regions = st.multiselect("시각화할 지역을 선택하세요:", df[region_col].unique(), default=df[region_col].unique()[:5])
filtered_df = df[df[region_col].isin(regions)]

# --- 지표 선택 ---
target_col = st.selectbox("시각화할 지표(예: 총인구수, 세대수 등)", numeric_cols)

# --- 1️⃣ 막대 그래프 (지역별 인구 비교) ---
st.subheader("📍 지역별 인구 비교")
bar_fig = px.bar(
    filtered_df,
    x=region_col,
    y=target_col,
    color=region_col,
    text=target_col,
    title=f"지역별 {target_col} 비교",
)
bar_fig.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(bar_fig, use_container_width=True)

# --- 2️⃣ 시계열(월별/연도별) 그래프 ---
date_cols = [c for c in cols if "년" in c or "월" in c or "기간" in c]
if date_cols:
    date_col = st.selectbox("기간(연도/월) 컬럼을 선택하세요:", date_cols)
    st.subheader("📆 기간별 추이")
    line_fig = px.line(
        filtered_df,
        x=date_col,
        y=target_col,
        color=region_col,
        markers=True,
        title=f"{target_col} 기간별 추이",
    )
    st.plotly_chart(line_fig, use_container_width=True)

# --- 3️⃣ 성별 인구 비교 (선택적으로 표시) ---
gender_cols = [c for c in cols if "남" in c or "여" in c]
if len(gender_cols) >= 2:
    st.subheader("👫 성별 인구 비교")
    gender_data = filtered_df[[region_col] + gender_cols].melt(id_vars=region_col, var_name="성별", value_name="인구수")
    gender_fig = px.bar(
        gender_data,
        x=region_col,
        y="인구수",
        color="성별",
        barmode="group",
        text="인구수",
        title="성별 인구 비교",
    )
    st.plotly_chart(gender_fig, use_container_width=True)

st.success("✅ Plotly 기반 시각화 완료!")
