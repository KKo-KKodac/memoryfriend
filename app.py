import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="중고 PC 매입 가액 계산기", layout="wide")


# 1. 시세 데이터 로드
@st.cache_data(ttl=60)
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

items = price_data.get("items", [])
prices_map = price_data.get("prices", {})
updated_at = price_data.get("updated_at", "알 수 없음")
total_count = price_data.get("count", len(prices_map))

st.caption(
    f"📅 최근 시세 업데이트: **{updated_at}** (월드메모리 연동 **{total_count:,}개**"
    " 수집 중)"
)

# 세션 상태 초기화 (장바구니)
if "cart" not in st.session_state:
  st.session_state.cart = []

df_items = (
    pd.DataFrame(items)
    if items
    else pd.DataFrame(columns=["category", "sub", "detail", "name", "price"])
)

# --- 1. 부품 검색 및 선택 ---
st.subheader("1. 부품 검색 및 선택")

search_query = st.text_input(
    "🔍 **전체 품목 검색** (모델명이나 스펙 입력 ex: 14900, 3070, DDR4 16G)",
    placeholder="검색어를 입력하면 대분류와 관계없이 전체 부품에서 즉시 검색됩니다.",
)

st.write("")

# 대분류
FIXED_CATEGORIES = [
    "CPU",
    "메인보드",
    "메모리",
    "SSD",
    "HDD",
    "그래픽카드",
    "파워",
]

# 화면 노출용 세대/소켓 정렬 순서
ORDERED_DETAILS = [
    "전체",
    "16세대",
    "15세대",
    "14세대",
    "13세대",
    "12세대",
    "11세대",
    "10세대",
    "9세대",
    "8세대",
    "7세대",
    "6세대",
    "4세대",
    "3세대",
    "2세대",
    "1세대",
    "AMD(AM5)",
    "AMD(AM4)",
    "AM5",
    "AM4",
]

if search_query.strip():
  st.markdown(f"#### 🔎 **'{search_query}'** 전체 검색 결과")
  df_filtered = df_items[
      df_items["name"].str.contains(search_query, case=False, na=False)
  ]
else:
  # 1) 품목 대분류 선택
  selected_cat = st.radio("【 품목 대분류 】", FIXED_CATEGORIES, horizontal=True)

  df_cat = df_items[df_items["category"] == selected_cat]

  # 2) 선택된 대분류에 해당하는 세부구분(detail) 추출
  raw_details = (
      [d for d in df_cat["detail"].unique() if d] if not df_cat.empty else []
  )

  if raw_details:
    # 정렬 순서에 맞춰 나열
    sorted_details = sorted(
        raw_details,
        key=lambda x: (
            ORDERED_DETAILS.index(x) if x in ORDERED_DETAILS else 999,
            x,
        ),
    )
    # 선택 메뉴에 '전체' 옵션 제공
    detail_options = ["전체"] + sorted_details

    selected_detail = st.radio(
        "【 세대 / 소켓 / 세부구분 】",
        detail_options,
        horizontal=True,
        key=f"detail_radio_{selected_cat}",
    )

    if selected_detail == "전체":
      df_filtered = df_cat
    else:
      df_filtered = df_cat[df_cat["detail"] == selected_detail]
  else:
    df_filtered = df_cat

# --- 2. 단가표 테이블 출력 ---
if not df_filtered.empty:
  st.markdown("---")

  h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1.5, 4.5, 2, 1.5, 1.5])
  with h_col1:
    st.markdown("**분류**")
  with h_col2:
    st.markdown("**상품명**")
  with h_col3:
    st.markdown("**매입 단가**")
  with h_col4:
    st.markdown("**수량**")
  with h_col5:
    st.markdown("**추가**")

  st.markdown("---")

  for idx, row in df_filtered.iterrows():
    col1, col2, col3, col4, col5 = st.columns([1.5, 4.5, 2, 1.5, 1.5])

    with col1:
      st.write(f"[{row.get('detail', '일반')}]")
    with col2:
      st.write(f"**{row['name']}**")
    with col3:
      st.write(f"{row['price']:,} 원")
    with col4:
      qty = st.number_input(
          "수량",
          min_value=1,
          max_value=99,
          value=1,
          key=f"qty_{idx}",
          label_visibility="collapsed",
      )
    with col5:
      if st.button("➕ 추가", key=f"btn_{idx}", use_container_width=True):
        st.session_state.cart.append({
            "품목": row.get("category", "부품"),
            "상품": row["name"],
            "단가": row["price"],
            "수량": qty,
            "금액": row["price"] * qty,
        })
        st.toast(f"'{row['name']}' 추가 완료!", icon="✅")
        st.rerun()
else:
  st.info("해당 카테고리에 등록된 부품 시세 데이터가 없습니다.")

st.divider()

# --- 3. 하단 매입 계산 내역 ---
st.subheader("2. 매입 계산 내역")

if not st.session_state.cart:
  st.info(
      "상단 단가표에서 원하는 부품의 **[➕ 추가]** 버튼을 누르면 매입"
      " 견적표가 작성됩니다."
  )
else:
  cart_df = pd.DataFrame(st.session_state.cart)

  edited_df = st.data_editor(
      cart_df,
      column_config={
          "품목": st.column_config.TextColumn("품목", disabled=True),
          "상품": st.column_config.TextColumn("상품명", disabled=True),
          "단가": st.column_config.NumberColumn(
              "단가", format="%d 원", disabled=True
          ),
          "수량": st.column_config.NumberColumn(
              "수량", min_value=1, max_value=99, step=1
          ),
          "금액": st.column_config.NumberColumn(
              "합계 금액", format="%d 원", disabled=True
          ),
      },
      num_rows="dynamic",
      use_container_width=True,
      hide_index=True,
  )

  edited_df["금액"] = edited_df["단가"] * edited_df["수량"]
  st.session_state.cart = edited_df.to_dict("records")

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
