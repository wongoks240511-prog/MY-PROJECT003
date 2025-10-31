import streamlit as st
import pandas as pd

st.set_page_config(page_title="주민등록 인구 및 세대 현황", layout="wide")
st.title("📊 주민등록 인구 및 세대 현황 (Matplotlib 없이)")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])
if uploaded_file is None:
    st.info("먼저 CSV 파일을 업로드해주세요.")
    st.stop()

# CSV 읽기 (인코딩 문제가 생기면 'cp949' 또는 'euc-kr' 시도)
try:
    df = pd.read_csv(uploaded_file, encoding="utf-8")
except Exception:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except Exception as e:
        st.error(f"CSV 읽기 실패: {e}")
        st.stop()

st.subheader("데이터 미리보기")
st.dataframe(df.head())

# 컬럼 타입 확인
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
all_cols = df.columns.tolist()

st.write("📋 컬럼 목록:", all_cols)
if not numeric_cols:
    st.warning("숫자형 컬럼이 없습니다 — 숫자형 컬럼이 있어야 차트를 그릴 수 있습니다.")
else:
    st.subheader("시각화 설정")
    # x축으로 사용할 컬럼(문자형/범주형 권장)
    x_candidates = [c for c in all_cols if df[c].dtype == "object" or df[c].nunique() < 50]
    if not x_candidates:
        x_candidates = all_cols  # 어쩔 수 없이 모든 컬럼 허용

    x_col = st.selectbox("X축(범주형 추천)", x_candidates)
    y_col = st.selectbox("Y축(숫자형)", numeric_cols)

    agg_func = st.selectbox("집계 방법", ["sum", "mean", "median", "count"])
    if agg_func == "sum":
        plot_df = df.groupby(x_col)[y_col].sum()
    elif agg_func == "mean":
        plot_df = df.groupby(x_col)[y_col].mean()
    elif agg_func == "median":
        plot_df = df.groupby(x_col)[y_col].median()
    else:
        plot_df = df.groupby(x_col)[y_col].count()

    st.write(f"## {x_col} 별 {y_col} ({agg_func})")
    # st.bar_chart은 pandas Series/DataFrame을 바로 받음
    st.bar_chart(plot_df)

    # 라인 차트 옵션
    if st.checkbox("라인 차트로 보기"):
        st.line_chart(plot_df)
