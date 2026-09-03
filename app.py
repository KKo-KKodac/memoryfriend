import streamlit as st
import json
import os

st.set_page_config(page_title="중고 PC 매입 가액 계산기", layout="wide")

# 1. prices.json 파일 읽어오기 (캐시 처리로 접속 시 0.1초 만에 즉시 로딩)
@st.cache_data(ttl=3600)  # 1시간 동안 메모리에 보관
def load_price_data():
    if os.path.exists("prices.json"):
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# 데이터 로드
price_data = load_price_data()

st.title("💻 중고 PC 매입 가액 계산기")

if price_data:
    updated_at = price_data.get("updated_at", "알 수 없음")
    total_count = price_data.get("count", 0)
    prices = price_data.get("prices", {})

    # 업데이트 시간 및 수집 건수 상단 표시
    st.info(f"📅 최근 시세 업데이트: **{updated_at}** (총 {total_count:,}개 부품 시세 반영 중)")

    st.subheader("🔍 부품별 매입 시세 조회 및 계산")

    # 예시: 부품 검색 및 매입가 조회 인터페이스
    search_term = st.text_input("부품명을 입력하세요 (예: RTX, i5, DDR4)", "")

    # 검색어 filtering
    filtered_items = {k: v for k, v in prices.items() if search_term.lower() in k.lower()}

    if search_term:
        st.write(f"검색 결과 ({len(filtered_items)}건):")
        for item_name, price in filtered_items.items():
            st.write(f"- **{item_name}**: {price:,} 원")
    else:
        # 전체 드롭다운 선택 예시
        selected_item = st.selectbox("전체 부품 목록에서 선택하세요:", list(prices.keys()))
        if selected_item:
            st.markdown(f"### 💰 매입 단가: **{prices[selected_item]:,} 원**")

    # -------------------------------------------------------------
    # 💡 기존에 만드셨던 CPU / RAM / GPU / SSD 종합 견적 계산기 UI가 있다면
    #    'prices' 변수를 활용해 연결해 주시면 됩니다.
    # -------------------------------------------------------------

else:
    st.error("⚠️ 시세 데이터(prices.json)를 불러올 수 없습니다. GitHub Actions에서 크롤링이 정상적으로 완료되었는지 확인해 주세요.")
