import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="글로벌 주식 비교", layout="wide")

st.title("📈 한국 vs 미국 주요 주식 비교 대시보드")

# 기본 티커 리스트
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS"
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Nvidia": "NVDA"
}

# 사이드바 선택
st.sidebar.header("📌 옵션 설정")

market = st.sidebar.radio("시장 선택", ["한국", "미국"])

if market == "한국":
    stocks = KR_STOCKS
else:
    stocks = US_STOCKS

selected_stocks = st.sidebar.multiselect(
    "종목 선택",
    list(stocks.keys()),
    default=list(stocks.keys())[:2]
)

period = st.sidebar.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=3
)

# 데이터 가져오기
@st.cache_data
def load_data(tickers, period):
    data = yf.download(tickers, period=period)["Adj Close"]
    return data

if selected_stocks:
    tickers = [stocks[name] for name in selected_stocks]
    data = load_data(tickers, period)

    # 컬럼 이름 바꾸기
    data.columns = selected_stocks

    st.subheader("📊 주가 데이터")
    st.dataframe(data.tail())

    # 수익률 계산
    returns = (data.iloc[-1] / data.iloc[0] - 1) * 100
    returns = returns.sort_values(ascending=False)

    st.subheader("💰 수익률 (%)")
    st.bar_chart(returns)

    # 차트
    st.subheader("📈 주가 비교 차트")

    fig, ax = plt.subplots(figsize=(10, 5))

    # 정규화 (비교 쉽게)
    normalized = data / data.iloc[0] * 100
    normalized.plot(ax=ax)

    ax.set_ylabel("기준값 (100)")
    ax.set_title("상대 수익률 비교")

    st.pyplot(fig)

else:
    st.warning("종목을 선택해주세요.")
