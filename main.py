import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="한-미 주식 비교 분석기", layout="wide")

st.title("📈 한-미 주요 주식 수익률 비교")
st.sidebar.header("설정")

# 1. 종목 선택 (사용자 입력 가능)
default_stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "S&P 500 ETF": "SPY"
}

selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요",
    options=list(default_stocks.keys()),
    default=["삼성전자", "Apple", "NVIDIA"]
)

# 사용자 직접 입력 기능
custom_ticker = st.sidebar.text_input("직접 티커 입력 (예: 005380.KS 또는 MSFT)")
if st.sidebar.button("추가") and custom_ticker:
    default_stocks[custom_ticker] = custom_ticker
    selected_names.append(custom_ticker)

# 2. 날짜 선택
start_date = st.sidebar.date_input("시작 날짜", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("종료 날짜", datetime.now())

if selected_names:
    tickers = [default_stocks[name] for name in selected_names if name in default_stocks]
    
    # 데이터 불러오기
    @st.cache_data
    def load_data(ticker_list, start, end):
        data = yf.download(ticker_list, start=start, end=end)['Close']
        return data

    df = load_data(tickers, start_date, end_date)

    if not df.empty:
        # 수익률 계산 (첫 날 가격 기준 100으로 정규화)
        # 종목이 하나일 경우 Series로 반환될 수 있어 처리
        if len(tickers) == 1:
            df = df.to_frame()
            df.columns = [selected_names[0]]
        
        # 정규화 (수익률 비교를 위함)
        df_norm = (df / df.iloc[0]) * 100

        # 3. 차트 시각화 (Plotly)
        st.subheader("📊 상대 수익률 비교 (시작일 = 100)")
        fig = go.Figure()
        for col in df_norm.columns:
            fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=col, mode='lines'))
        
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="날짜",
            yaxis_title="정규화된 가격",
            legend_title="종목"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 4. 데이터 요약 통계
        st.subheader("📝 종목별 요약")
        cols = st.columns(len(selected_names))
        for i, name in enumerate(selected_names):
            ticker = default_stocks[name]
            if ticker in df.columns:
                current_price = df[ticker].iloc[-1]
                first_price = df[ticker].iloc[0]
                return_pct = ((current_price - first_price) / first_price) * 100
                
                with cols[i]:
                    st.metric(label=name, value=f"{current_price:,.2f}", delta=f"{return_pct:.2f}%")
    else:
        st.error("데이터를 불러오지 못했습니다. 티커를 확인해 주세요.")
else:
    st.info("왼쪽 사이드바에서 종목을 선택해 주세요.")
