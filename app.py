import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="중고 PC 매입 가액 계산기", layout="wide")


# 1. prices.json 파일 로드 (캐시 처리)
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
      "⚠️ 시세 데이터(prices.json)를 불러올 수 없습니다. GitHub Actions"
      " 상태를 확인해주세요."
  )
  st.stop()

prices = price_data.get("prices", {})
updated_at = price_data.get("updated_at", "알 수 없음")
total_count = price_data.get("count", len(prices))

# 상단 안내 문구
st.caption(
    f"📅 최근 시세 업데이트: **{updated_at}** (월드메모리 실시간 **{total_count:,}개**"
    " 부품 시세 연동 중)"
)

# 세션 상태 초기화 (하단 견적서 저장소)
if "cart" not in st.session_state:
  st.session_state.cart = []

# --- 1. 상단: 부품 선택 영역 ---
st.subheader("1. 부품 검색 및 선택")

# 표준 품목 구분
CATEGORY_LIST = [
    "전체",
    "CPU",
    "메인보드",
    "메모리",
    "SSD",
    "HDD",
    "그래픽카드",
    "파워",
]

col1, col2, col3, col4 = st.columns([1.5, 3.5, 1.2, 1])

with col1:
  selected_category = st.selectbox("품목 구분", CATEGORY_LIST)

# 품목 필터링 로직
all_products = list(prices.keys())

if selected_category != "전체":
  # 선택한 품목 키워드로 필터링 (예: CPU 선택 시 관련 항목 검색)
  filtered_products = [
      p for p in all_products if selected_category.lower() in p.lower()
  ]
  if not filtered_products:
    filtered_products = all_products
else:
  filtered_products = all_products

with col2:
  selected_product = st.selectbox(
      "상품 선택 (월드메모리 단가표)",
      filtered_products,
      help="키보드로 부품명을 검색할 수 있습니다.",
  )

unit_price = prices.get(selected_product, 0)

with col3:
  st.write("**매입 단가**")
  st.markdown(
      f"<h4 style='margin:0; color:#1E88E5;'>{unit_price:,} 원</h4>",
      unsafe_allow_html=True,
  )
  quantity = st.number_input(
      "수량", min_value=1, max_value=99, value=1, step=1
  )

with col4:
  st.write("")
  st.write("")
  if st.button("➕ 품목 추가", use_container_width=True):
    st.session_state.cart.append({
        "품목": (
            selected_category
            if selected_category != "전체"
            else "기타/일반"
        ),
        "상품": selected_product,
        "단가": unit_price,
        "수량": quantity,
        "금액": unit_price * quantity,
    })
    st.success("견적서에 추가되었습니다!")
    st.rerun()

st.divider()

# --- 2. 하단: 계산기 항목 테이블 ---
st.subheader("2. 매입 계산 내역")

if not st.session_state.cart:
  st.info(
      "상단에서 부품을 선택한 후 **[➕ 품목 추가]** 버튼을 눌러 견적표를"
      " 작성해보세요."
  )
else:
  df = pd.DataFrame(st.session_state.cart)

  # 데이터 수정/관리 테이블 (수량 직접 수정 가능, 행 삭제 가능)
  edited_df = st.data_editor(
      df,
      column_config={
          "품목": st.column_config.TextColumn("품목", disabled=True),
          "상품": st.column_config.TextColumn("상품", disabled=True),
          "단가": st.column_config.NumberColumn(
              "단가", format="%d 원", disabled=True
          ),
          "수량": st.column_config.NumberColumn(
              "수량", min_value=1, max_value=99, step=1
          ),
          "금액": st.column_config.NumberColumn(
              "금액", format="%d 원", disabled=True
          ),
      },
      num_rows="dynamic",  # 좌측 체크박스로 개별 행 삭제 가능
      use_container_width=True,
      hide_index=True,
  )

  # 수량 변경 시 금액 자동 재계산
  edited_df["금액"] = edited_df["단가"] * edited_df["수량"]
  st.session_state.cart = edited_df.to_dict("records")

  # 총 금액 계산
  total_amount = edited_df["금액"].sum()

  st.markdown("---")
  c_reset, c_total = st.columns([2, 2])

  with c_reset:
    if st.button("🗑️ 견적서 전체 초기화"):
      st.session_state.cart = []
      st.rerun()

  with c_total:
    st.markdown(
        f"<div style='text-align: right; background-color: #f0f2f6; padding:"
        " 15px; border-radius: 10px;'>"
        f"<h3 style='margin:0;'>총 매입 예상 금액: <span"
        f" style='color:#E53935;'>{total_amount:,} 원</span></h3>"
        "</div>",
        unsafe_allow_html=True,
    )
