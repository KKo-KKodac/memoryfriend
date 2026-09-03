import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="중고 PC 매입 가액 계산기", layout="wide")

# 1. 시세 데이터 불러오기 (캐시 적용)
@st.cache_data(ttl=3600)
def load_price_data():
    if os.path.exists("prices.json"):
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

price_data = load_price_data()

st.title("💻 중고 PC 매입 가액 계산기")

if not price_data:
    st.error("⚠️ 시세 데이터(prices.json)를 불러올 수 없습니다. GitHub Actions 크롤링 상태를 확인해주세요.")
    st.stop()

# 가격 데이터 추출
prices = price_data.get("prices", {})
updated_at = price_data.get("updated_at", "알 수 없음")

st.caption(f"📅 최근 시세 업데이트: **{updated_at}** (총 {len(prices):,}개 단가 반영 중)")

# 세션 상태 초기화
if "cart" not in st.session_state:
    st.session_state.cart = []

st.subheader("1. 부품 선택 및 추가")

# 표준 품목 구분
CATEGORY_LIST = ["전체", "CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드", "파워"]

col1, col2, col3, col4 = st.columns([1.5, 3, 1, 1])

# 1. 품목 선택
with col1:
    selected_category = st.selectbox("품목 구분", CATEGORY_LIST)

# 2. 상품 리스트 구성 (빈 리스트 방지 로직)
all_products = list(prices.keys())

# 품목이 '전체'가 아니면 검색어로 필터링, 검색 결과가 없으면 전체 목록 사용
if selected_category != "전체":
    filtered_products = [p for p in all_products if selected_category.lower() in p.lower()]
    # 만약 필터링된 결과가 없으면 전체 목록을 보여주어 No options 방지
    if not filtered_products:
        filtered_products = all_products
else:
    filtered_products = all_products

# 상품 목록이 혹시라도 비어있을 경우 예외 처리
if not filtered_products:
    filtered_products = ["등록된 상품이 없습니다"]

with col2:
    selected_product = st.selectbox("상품 (월드메모리 단가표)", filtered_products)

# 단가 가져오기
unit_price = prices.get(selected_product, 0)

with col3:
    st.markdown(f"**단가:** {unit_price:,} 원")
    quantity = st.number_input("수량", min_value=1, value=1, step=1)

with col4:
    st.write("")
    st.write("")
    if st.button("➕ 품목 추가", use_container_width=True):
        if selected_product != "등록된 상품이 없습니다":
            st.session_state.cart.append({
                "품목": selected_category if selected_category != "전체" else "기타",
                "상품": selected_product,
                "단가": unit_price,
                "수량": quantity,
                "금액": unit_price * quantity
            })
            st.success("추가되었습니다!")
            st.rerun()

st.divider()

# --- 하단 견적서 리스트 ---
st.subheader("2. 매입 계산 내역")

if not st.session_state.cart:
    st.info("상단에서 품목과 상품을 선택한 후 **[➕ 품목 추가]** 버튼을 눌러주세요.")
else:
    df = pd.DataFrame(st.session_state.cart)

    edited_df = st.data_editor(
        df,
        column_config={
            "품목": st.column_config.TextColumn("품목", disabled=True),
            "상품": st.column_config.TextColumn("상품", disabled=True),
            "단가": st.column_config.NumberColumn("단가 (원)", format="%d 원", disabled=True),
            "수량": st.column_config.NumberColumn("수량", min_value=1, max_value=99, step=1),
            "금액": st.column_config.NumberColumn("금액 (원)", format="%d 원", disabled=True),
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    # 수량 변경 시 금액 재계산
    edited_df["금액"] = edited_df["단가"] * edited_df["수량"]
    st.session_state.cart = edited_df.to_dict("records")

    total_amount = edited_df["금액"].sum()

    st.markdown("---")
    c1, c2 = st.columns([2, 1])

    with c1:
        if st.button("🗑️ 전체 초기화"):
            st.session_state.cart = []
            st.rerun()

    with c2:
        st.markdown(f"### 💵 **총 매입 금액:** <span style='color:red;'>{total_amount:,} 원</span>", unsafe_allow_html=True)
