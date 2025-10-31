import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 앱 제목
st.set_page_config(page_title="주민등록 인구 및 세대 현황 대시보드", layout="wide")
st.title("🏙️ 주민등록 인구 및 세대 현황 시각화")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # CSV 파일 읽기
    df = pd.read_csv(uploaded_file, encoding='utf-8')
    
    st.subheader("📄 데이터 미리보기")
    st.dataframe(df.head())

    # 기본 통계
    st.subheader("📊 데이터 요약")
    st.write(df.describe(include='all'))

    # 컬럼 선택
    st.subheader("📈 시각화 설정")
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    category_cols = df.select_dtypes(exclude='number').columns.tolist()

    x_col = st.selectbox("X축 선택", options=df.columns)
    y_col = st.selectbox("Y축 선택 (숫자형 컬럼만 표시)", options=numeric_cols)

    if st.button("그래프 보기"):
        fig, ax = plt.subplots(figsize=(10, 5))
        if x_col in category_cols:
            df.groupby(x_col)[y_col].sum().plot(kind='bar', ax=ax)
            ax.set_title(f"{x_col}별 {y_col} 현황")
        else:
            df.plot(x=x_col, y=y_col, kind='line', ax=ax)
            ax.set_title(f"{x_col} vs {y_col} 추이")

        st.pyplot(fig)
else:
    st.info("👆 CSV 파일을 업로드해주세요.")

# 푸터
st.markdown("---")
st.markdown("데이터 출처: 주민등록 인구 및 세대 현황 (행정안전부)")
