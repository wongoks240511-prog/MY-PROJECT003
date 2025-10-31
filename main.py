import streamlit as st
import pandas as pd
import os
import subprocess
import sys

st.set_page_config(page_title="주민등록 인구 및 세대 현황 (Plotly)", layout="wide")
st.title("📊 주민등록 인구 및 세대 현황 시각화 대시보드")

# --- Plotly 설치 확인 및 자동 설치 ---
try:
    import plotly.express as px
except ModuleNotFoundError:
    with st.spinner("📦 Plotly 라이브러리가 설치되어 있지 않습니다. 자동 설치를 시도 중입니다..."):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px

# --- 데이터 불러오기 함수 ---
@st.cache_data
def load_data():
    encodings = ["utf-8", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            return pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding=enc)
        except Exception:
            continue
    st.error("CSV 파일을 읽는 중 문제가 발생했습니다. 인코딩을 확인하세요.")
    st.stop()

# --- 데이터 로드 ---
if not os.path.exists("202509_202509_주민등록인구및세대현황_월간.csv"):
    uploaded = st.file_uploader("📂 CSV 파일을 업로드하세요", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        st.warning("CSV 파일이 필요합니다. 업로드하거나 리포지토리에 추가하세요.")
        st.stop()
else:
    df = load_data()

# --- 데이터 미리보기 ---
st.subheader("📋 데이터 미리보기")
st.dataframe(df.head())

# --- 기본 컬럼 탐색 ---
cols = df.columns.tolist()
region_col = next((c for c in cols if "행정구역" in c or "지역" in c), None)
if not region_col:
    region_col = st.selectbox("지역(행정구역) 컬럼을 선택하세요:", cols)

numeric_cols = df.select_dtypes(include=["int", "float"]).columns.tolist()
if not numeric_cols:
    st.warning("수치형 컬럼이 없습니다. 숫자로 변환 가능한 컬럼을 선택하세요.")
    numeric_cols = [c for c in cols if df[c].astype(str).str.isnumeric().any()]

target_col = st.selectbox("시각화할 지표 선택:", numeric_cols)
regions = st.multiselect("시각화할 지역 선택:", df[region_col].unique(), default=df[region_col].unique()[:5])
filtered_df = df[df[region_col].isin(regions)]

# --- Plotly 시각화 ---
st.subheader("📊 지역별 인구 비교 (Bar Chart)")
fig_bar = px.bar(
    filtered_df,
    x=region_col,
    y=target_col,
    color=region_col,
    text=target_col,
    title=f"{target_col} 지역별 비교"
)
fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

# --- 기간별 추이 ---
date_cols = [c for c in cols if "년" in c or "월" in c or "기간" in c]
if date_cols:
    date_col = date_cols[0]
    st.subheader("📆 기간별 추이 (Line Chart)")
    fig_line = px.line(
        filtered_df,
        x=date_col,
        y=target_col,
        color=region_col,
        markers=True,
        title=f"{target_col} 기간별 추이"
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.success("✅ Plotly 시각화 완료!")
