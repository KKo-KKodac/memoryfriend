import streamlit as st
import json
import os

st.set_page_config(page_title="중고 PC 매입가 계산기", layout="wide")

# 캐싱 적용: 1시간 내 복수 접속시 메모리에서 즉시 리턴
@st.cache_data(ttl=3600)
def load_price_data():
    if os.path.exists("prices.json"):
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

price_info = load_price_data()

st.title("💻 중고 PC 매입가 계산기")

if price_info:
    st.success(f"📅 시세 업데이트 기준: **{price_info['updated_at']}** (총 {price_info['count']}개 부품 시세 반영 중)")
    prices = price_info["prices"]

    # -------------------------------------------------------------
    # 기존 계산기 선택창 및 계산 로직 위치
    # 예시:
    # cpu_selected = st.selectbox("CPU 선택", list(prices.keys()))
    # cpu_price = prices.get(cpu_selected, 0)
    # st.write(f"매입 단가: {cpu_price:,} 원")
    # -------------------------------------------------------------

else:
    st.warning("⚠️ 시세 데이터(prices.json)를 불러올 수 없습니다. 관리자 수동 업데이트 또는 크롤링 상태를 확인하세요.")