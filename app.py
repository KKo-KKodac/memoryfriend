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
    st.error(
        "⚠️ 시세 데이터(prices.json)를 불러올 수 없습니다. GitHub Actions 크롤링 상태를 확인해주세요."
    )
    st.stop()

# 상단 시세 정보 표시
prices = price_data.get("prices", {})
updated_at = price_data.get("updated_at", "알 수 없음")
st.caption(
    f"📅 최근 시세 업데이트: **{updated_at}** (총 {len(prices):,}개 단가 반영 중)"
)

# 세션 상태 초기화 (하단 견적서 저장용)
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- 1. 상단: 품목 및 상품 선택 영역 ---
st.subheader("1. 부품 선택 및 추가")

# 지정하신 표준 품목 리스트
CATEGORY_LIST = [
    "CPU",
    "메인보드",
    "메모리",
    "SSD",
    "HDD",
    "그래픽카드",
    "파워",
    "기타/직접선택",
]

col1, col2, col3, col4 = st.columns([1.5, 3, 1, 1])

with col1:
    selected_category = st.selectbox("품목 구분", CATEGORY_LIST)

# 품목별 필터링 또는 전체 목록 준비
all_product_names = list(prices.keys())

# 선택한 품목 이름이 상품명에 들어간 항목 우선 검색 (또는 전체 선택 가능)
filtered_products = [
    p for p in all_product_names if selected_category.lower() in p.lower()
]
if not filtered_products:
    filtered_products = all_product_names

with col2:
    selected_product = st.selectbox("상품 (월드메모리 단가표)", filtered_products)

unit_price = prices.get(selected_product, 0)

with col3:
    st.markdown(f"**단가:** {unit_price:,} 원")
    quantity = st.number_input("수량", min_value=1, value=1, step=1)

with col4:
    st.write("")  # 줄맞춤용
    st.write("")
    if st.button("➕ 품목 추가", use_container_width=True):
        # 견적서 목록에 추가
        st.session_state.cart.append(
            {
                "품목": selected_category,
                "상품": selected_product,
                "단가": unit_price,
                "수량": quantity,
                "금액": unit_price * quantity,
            }
        )
        st.success(f"{selected_product} 추가 완료!")
        st.rerun()

st.divider()

# --- 2. 하단: 견적서 계산기 테이블 ---
st.subheader("2. 매입 계산 내역")

if not st.session_state.cart:
    st.info(
        "상단에서 품목과 상품을 선택한 후 **[➕ 품목 추가]** 버튼을 눌러주세요."
    )
else:
    # 견적 데이터 변환
    df = pd.DataFrame(st.session_state.cart)

    # 데이터 수정 가능 테이블 (수량 변경 및 삭제 가능)
    edited_df = st.data_editor(
        df,
        column_config={
            "품목": st.column_config.TextColumn("품목", disabled=True),
            "상품": st.column_config.TextColumn("상품", disabled=True),
            "단가": st.column_config.NumberColumn(
                "단가 (원)", format="%d 원", disabled=True
            ),
            "수량": st.column_config.NumberColumn(
                "수량", min_value=1, max_value=99, step=1
            ),
            "금액": st.column_config.NumberColumn(
                "금액 (원)", format="%d 원", disabled=True
            ),
        },
        num_rows="dynamic",  # 행 삭제 가능 (마우스 클릭으로 삭제)
        use_container_width=True,
        hide_index=True,
    )

    # 수량 변경에 따른 금액 재계산
    edited_df["금액"] = edited_df["단가"] * edited_df["수량"]
    st.session_state.cart = edited_df.to_dict("records")

    # 총 금액 계산
    total_amount = edited_df["금액"].sum()

    st.markdown("---")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        if st.button("🗑️ 전체 초기화"):
            st.session_state.cart = []
            st.rerun()

    with col_right:
        st.markdown(f"### 💵 **총 매입 금액:** <span style='color:red;'>{total_amount:,} 원</span>", unsafe_allow_html=True)
