import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(page_title="주민등록 인구 및 세대 현황 대시보드", layout="wide")

st.title("📊 주민등록 인구 및 세대 현황 시각화")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # CSV 파일 읽기
    df = pd.read_csv(uploaded_file, encoding="utf-8")
    
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    # 컬럼명 확인
    st.write("📋 컬럼 목록:", list(df.columns))
    
    # 특정 컬럼 선택해서 시각화
    st.subheader("📈 시각화")
    
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    category_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if len(numeric_cols) > 0:
        selected_y = st.selectbox("Y축 (숫자형 데이터 선택)", numeric_cols)
        selected_x = st.selectbox("X축 (범주형 데이터 선택)", category_cols if len(category_cols) > 0 else numeric_cols)

        fig, ax = plt.subplots(figsize=(10, 6))
        df.groupby(selected_x)[selected_y].sum().plot(kind='bar', ax=ax)
        ax.set_xlabel(selected_x)
        ax.set_ylabel(selected_y)
        ax.set_title(f"{selected_x}별 {selected_y} 분포")
        st.pyplot(fig)
    else:
        st.warning("시각화 가능한 숫자형 데이터가 없습니다.")
else:
    st.info("먼저 CSV 파일을 업로드해주세요.")

st.markdown("---")
st.caption("© 2025 Streamlit 인구 데이터 시각화 데모 by ChatGPT")
