import streamlit as st
import pandas as pd
import sys

st.set_page_config(page_title="주민등록 인구 및 세대 현황 (Plotly)", layout="wide")
st.title("📊 주민등록 인구 및 세대 현황 시각화 (Plotly)")

# ---- 안전한 plotly 임포트: 없으면 친절한 안내 ----
try:
    import plotly.express as px
except Exception as e:
    st.error(
        "필수 라이브러리 `plotly` 를 찾을 수 없습니다.\n\n"
        "해결 방법:\n"
        "1) 로컬에서 실행 중이면 터미널(또는 가상환경)에서:\n"
        "   pip install -r requirements.txt\n\n"
        "2) Streamlit Cloud에 배포했다면 리포지토리 루트에 `requirements.txt` 파일을 추가한 후 앱을 재배포하세요.\n\n"
        f"오류 상세: {e}"
    )
    # 상세 로그를 보려면 아래 주석을 해제 (디버깅 용도)
    # st.write(sys.exc_info())
    st.stop()

# ---- CSV 불러오기 (자동 인코딩 시도) ----
@st.cache_data
def load_csv_try(path):
    # 여러 인코딩 시도 (utf-8, cp949)
    encodings = ["utf-8", "cp949", "euc-kr"]
    last_exc = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            return df
        except Exception as e:
            last_exc = e
    # 모두 실패하면 최종 예외 발생
    raise last_exc

# 파일 업로드 UI (파일이 리포지토리에 없을 경우 대비)
st.sidebar.header("데이터 로드")
use_uploaded = st.sidebar.checkbox("파일 업로드로 데이터 불러오기", value=False)

df = None
if use_uploaded:
    uploaded = st.sidebar.file_uploader("CSV 파일을 업로드하세요", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
        except Exception:
            # 재시도: 인코딩 자동 시도
            uploaded.seek(0)
            try:
                df = pd.read_csv(uploaded, encoding="cp949")
            except Exception as e:
                st.sidebar.error(f"업로드한 CSV를 읽는 중 오류: {e}")
else:
    # 기본적으로 리포에 포함된 파일 이름을 시도
    DEFAULT_CSV = "202509_202509_주민등록인구및세대현황_월간.csv"
    try:
        df = load_csv_try(DEFAULT_CSV)
    except FileNotFoundError:
        st.warning(
            f"기본 CSV 파일({DEFAULT_CSV})을 찾을 수 없습니다. 사이드바에서 '파일 업로드'를 체크해 업로드하거나 리포지토리에 파일을 추가하세요."
        )
    except Exception as e:
        st.error(f"CSV 로드 실패: {e}")

if df is None:
    st.stop()

# ---- 데이터 미리보기 & 요약 ----
st.subheader("데이터 미리보기")
st.dataframe(df.head())

st.subheader("기본 정보")
st.write(f"행 개수: {len(df)}  /  열 개수: {len(df.columns)}")
st.write(df.dtypes)

# ---- 컬럼 자동 선택(행정구역, 기간, 수치형) ----
cols = df.columns.tolist()

# 행정구역 컬럼 찾기 시도
region_candidates = [c for c in cols if any(k in c for k in ["행정구역", "시군구", "지역", "구군", "읍면동"])]
region_col = region_candidates[0] if region_candidates else None
if not region_col:
    region_col = st.selectbox("지역(행정구역) 컬럼을 선택하세요:", cols)

# 기간 컬럼 후보
date_candidates = [c for c in cols if any(k in c for k in ["년", "월", "기간", "날짜", "date"])]
date_col = date_candidates[0] if date_candidates else None
if date_candidates:
    date_col = st.selectbox("기간(연/월) 컬럼을 선택하세요 (선택적):", ["(선택 안함)"] + date_candidates)
    if date_col == "(선택 안함)":
        date_col = None

# 수치형 컬럼
numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
if not numeric_cols:
    # 숫자로 보이는 문자열 컬럼을 강제 변환 시도
    maybe_numeric = []
    for c in cols:
        try:
            converted = pd.to_numeric(df[c].astype(str).str.replace(",",""), errors="coerce")
            if converted.notna().sum() > 0:
                maybe_numeric.append(c)
        except Exception:
            pass
    numeric_cols = maybe_numeric

if not numeric_cols:
    st.error("숫자형(시각화 가능한) 컬럼이 없습니다. CSV 구조를 확인해주세요.")
    st.stop()

target_col = st.selectbox("시각화할 지표(수치형) 선택:", numeric_cols)

# ---- 지역 선택 필터 ----
if region_col:
    unique_regions = df[region_col].dropna().unique().tolist()
    default_regions = unique_regions[:5] if len(unique_regions) > 0 else []
    regions = st.multiselect("시각화할 지역 선택:", unique_regions, default=default_regions)
    if regions:
        df_plot = df[df[region_col].isin(regions)].copy()
    else:
        df_plot = df.copy()
else:
    df_plot = df.copy()

# ---- Plotly 차트: 지역별 막대 ----
st.subheader("📍 지역별 비교 (막대 그래프)")
try:
    fig_bar = px.bar(
        df_plot,
        x=region_col if region_col else df_plot.index,
        y=target_col,
        color=region_col if region_col else None,
        text=target_col,
        title=f"{target_col} - 지역 비교"
    )
    fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)
except Exception as e:
    st.error(f"막대 그래프 생성 중 오류: {e}")

# ---- 기간별 추이 (있을 때) ----
if date_col:
    st.subheader("📆 기간별 추이")
    try:
        # 가능하면 기간을 datetime 변환 시도
        try:
            df_plot[date_col + "_parsed"] = pd.to_datetime(df_plot[date_col], errors="coerce")
            xcol = date_col + "_parsed"
            # 만약 모두 NaT라면 원래 문자열 사용
            if df_plot[xcol].notna().sum() == 0:
                xcol = date_col
        except Exception:
            xcol = date_col

        fig_line = px.line(
            df_plot.sort_values(by=xcol),
            x=xcol,
            y=target_col,
            color=region_col if region_col else None,
            markers=True,
            title=f"{target_col} - 기간별 추이"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    except Exception as e:
        st.error(f"기간별 추이 그래프 생성 중 오류: {e}")

# ---- 성별 비교 자동 감지 (남/여 컬럼이 있으면) ----
gender_cols = [c for c in cols if any(k in c for k in ["남", "여", "남자", "여자", "M", "F"])]
if len(gender_cols) >= 2:
    st.subheader("👫 성별 비교")
    try:
        # melt 형태로 변환
        melt_cols = [region_col] + gender_cols if region_col else gender_cols
        gender_df = df_plot[melt_cols].melt(id_vars=[region_col] if region_col else None, var_name="성별", value_name="인구수")
        # drop NA region if region_col missing handled
        if region_col:
            fig_gender = px.bar(gender_df, x=region_col, y="인구수", color="성별", barmode="group", title="성별 인구 비교")
        else:
            fig_gender = px.bar(gender_df, x="성별", y="인구수", title="성별 인구 비교")
        st.plotly_chart(fig_gender, use_container_width=True)
    except Exception as e:
        st.error(f"성별 비교 그래프 생성 중 오류: {e}")

st.success("시각화 완료 ✅")
