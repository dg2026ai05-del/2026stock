import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="한-미 주식 분석기", layout="wide", page_icon="📈")

st.title("📈 한-미 주요 주식 수익률 비교")
st.markdown("선택한 종목들의 시작일 대비 수익률 추이를 한눈에 비교합니다.")

# 1. 사이드바 설정
st.sidebar.header("🔍 종목 및 기간 설정")

# 기본 종목 리스트 업데이트 (한화, SK하이닉스 포함)
default_stocks = {
    "한화": "000880.KS",
    "SK하이닉스": "000660.KS",
    "삼성전자": "005930.KS",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "S&P 500 ETF": "SPY",
    "나스닥 100 ETF": "QQQ"
}

selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요",
    options=list(default_stocks.keys()),
    default=["한화", "SK하이닉스", "NVIDIA", "Apple"]
)

# 사용자 직접 입력 (티커 추가)
custom_ticker = st.sidebar.text_input("기타 티커 입력 (예: 035420.KS)")
if st.sidebar.button("리스트에 추가") and custom_ticker:
    # 티커가 이미 존재하는지 간단히 확인 후 추가
    default_stocks[custom_ticker] = custom_ticker
    if custom_ticker not in selected_names:
        selected_names.append(custom_ticker)

# 날짜 선택
start_date = st.sidebar.date_input("조회 시작일", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("조회 종료일", datetime.now())

# 2. 데이터 처리 및 시각화
if selected_names:
    tickers = [default_stocks[name] for name in selected_names]
    
    @st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
    def load_data(ticker_list, start, end):
        data = yf.download(ticker_list, start=start, end=end)['Close']
        return data

    df = load_data(tickers, start_date, end_date)

    if not df.empty:
        # 데이터가 Series(종목 1개)인 경우 DataFrame으로 변환
        if isinstance(df, pd.Series):
            df = df.to_frame()
            df.columns = tickers

        # 수익률 정규화 (첫 거래일 가격을 100으로 기준)
        df_norm = (df / df.iloc[0]) * 100

        # 차트 생성
        st.subheader("📊 상대 수익률 추이 (시작점 = 100)")
        fig = go.Figure()
        for col in df_norm.columns:
            # 티커 대신 이름으로 표시하기 위해 역매핑
            display_name = [k for k, v in default_stocks.items() if v == col]
            name_label = display_name[0] if display_name else col
            
            fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=name_label, mode='lines'))
        
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="날짜",
            yaxis_title="수익률 지수",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 3. 상세 지표 (Metrics)
        st.divider()
        st.subheader("📌 종목별 현재 상태")
        cols = st.columns(len(selected_names))
        
        for i, name in enumerate(selected_names):
            ticker = default_stocks[name]
            if ticker in df.columns:
                current_price = df[ticker].dropna().iloc[-1]
                prev_price = df[ticker].dropna().iloc[0]
                return_val = ((current_price - prev_price) / prev_price) * 100
                
                with cols[i]:
                    st.metric(label=name, value=f"{current_price:,.0f}" if ".KS" in ticker else f"${current_price:,.2f}", 
                              delta=f"{return_val:.2f}% (누적)")
    else:
        st.warning("선택한 기간에 대한 데이터가 없습니다.")
else:
    st.info("사이드바에서 분석할 종목을 선택해 주세요.")
