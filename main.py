import streamlit as st
import pandas as pd
import plotly.express as px

# 앱 제목
st.title("📊 주민등록 인구 및 세대 현황 시각화")

# 파일 업로드 또는 로컬 CSV 불러오기
st.write("CSV 파일을 업로드하거나 기본 데이터를 불러옵니다.")
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='utf-8')
else:
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding='utf-8')

# 데이터 확인
st.subheader("📋 데이터 미리보기")
st.dataframe(df.head())

# 컬럼 선택
st.subheader("📈 시각화 옵션 선택")
numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

x_axis = st.selectbox("X축 (범주형)", options=categorical_columns)
y_axis = st.selectbox("Y축 (수치형)", options=numeric_columns)

# 그래프 종류 선택
chart_type = st.radio(
    "그래프 유형 선택",
    ("막대그래프", "선그래프", "산점도")
)

# Plotly 시각화
if chart_type == "막대그래프":
    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{x_axis}별 {y_axis} 막대그래프")
elif chart_type == "선그래프":
    fig = px.line(df, x=x_axis, y=y_axis, title=f"{x_axis}별 {y_axis} 선그래프")
elif chart_type == "산점도":
    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis}별 {y_axis} 산점도")

st.plotly_chart(fig, use_container_width=True)

# 요약 통계
st.subheader("📊 요약 통계")
st.write(df.describe())
