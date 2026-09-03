import os
import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="중고 PC 매입 가액 계산기", layout="wide")

@st.cache_data(ttl=3600)
def load_price_data():
    if os.path.exists("prices.json"):
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

price_data = load_price_data()

st.title("💻 중고 PC 매입 가액 계산기")

if not price_data:
    st.error("⚠️ 시세 데이터(prices.json)를 불러올 수 없습니다. GitHub Actions를 확인해 주세요.")
    st.stop()

items = price_data.get("items", [])
prices_map = price_data.get("prices", {})
updated_at = price_data.get("updated_at", "알 수 없음")
total_count = price_data.get("count", len(prices_map))

st.caption(f"📅 최근 시세 업데이트: **{updated_at}** (월드메모리 연동 **{total_count:,}개** 수집 중)")

if "cart" not in st.session_state:
    st.session_state.cart = []

# --- 1. 부품 검색 및 선택 ---
st.subheader("1. 부품 검색 및 선택")

# DF화하여 필터링 편의 제공
df_items = pd.DataFrame(items) if items else pd.DataFrame(columns=["category", "sub", "detail", "name", "price"])

# 1차 필터: 카테고리 (CPU, 메인보드, 메모리 등)
categories = ["전체"] + list(df_items["category"].unique()) if not df_items.empty else ["전체"]
col_cat, col_sub, col_detail = st.columns(3)

with col_cat:
    selected_cat = st.selectbox("1. 품목 선택", categories)

filtered = df_items.copy()
if selected_cat != "전체":
    filtered = filtered[filtered["category"] == selected_cat]

# 2차 필터: 제조사/제조구분 (INTEL, AMD, NVIDIA 등)
subs = ["전체"] + list(filtered["sub"].unique()) if not filtered.empty else ["전체"]
with col_sub:
    selected_sub = st.selectbox("2. 제조사 / 구분", subs)

if selected_sub != "전체":
    filtered = filtered[filtered["sub"] == selected_sub]

# 3차 필터: 세대 / 소켓 (14세대, 12세대, DDR4, RTX30 등)
details = ["전체"] + list(filtered["detail"].unique()) if not filtered.empty else ["전체"]
with col_detail:
    selected_detail = st.selectbox("3. 세대 / 소켓 / 분류", details)

if selected_detail != "전체":
    filtered = filtered[filtered["detail"] == selected_detail]

st.divider()

# 선택된 항목에 따른 최종 제품 선택 dropdown
if not filtered.empty:
    product_options = filtered["name"].tolist()
else:
    product_options = list(prices_map.keys())

c_prod, c_price, c_qty, c_add = st.columns([3.5, 1.5, 1, 1])

with c_prod:
    selected_product = st.selectbox("상품 선택 (검색 가능)", product_options)

unit_price = prices_map.get(selected_product, 0)

with c_price:
    st.write("**매입 단가**")
    st.markdown(f"<h4 style='margin:0; color:#1E88E5;'>{unit_price:,} 원</h4>", unsafe_allow_html=True)

with c_qty:
    quantity = st.number_input("수량", min_value=1, max_value=99, value=1, step=1)

with c_add:
    st.write("")
    st.write("")
    if st.button("➕ 품목 추가", use_container_width=True):
        st.session_state.cart.append({
            "품목": selected_cat,
            "상품": selected_product,
            "단가": unit_price,
            "수량": quantity,
            "금액": unit_price * quantity
        })
        st.success("견적에 추가되었습니다!")
        st.rerun()

st.divider()

# --- 2. 하단 견적 내역 ---
st.subheader("2. 매입 계산 내역")

if not st.session_state.cart:
    st.info("상단에서 부품을 선택한 후 **[➕ 품목 추가]** 버튼을 누르면 견적서가 생성됩니다.")
else:
    cart_df = pd.DataFrame(st.session_state.cart)
    
    edited_df = st.data_editor(
        cart_df,
        column_config={
            "품목": st.column_config.TextColumn("품목", disabled=True),
            "상품": st.column_config.TextColumn("상품", disabled=True),
            "단가": st.column_config.NumberColumn("단가", format="%d 원", disabled=True),
            "수량": st.column_config.NumberColumn("수량", min_value=1, max_value=99, step=1),
            "금액": st.column_config.NumberColumn("금액", format="%d 원", disabled=True),
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    edited_df["금액"] = edited_df["단가"] * edited_df["수량"]
    st.session_state.cart = edited_df.to_dict("records")
    
    total_amount = edited_df["금액"].sum()
    
    c_reset, c_total = st.columns([2, 2])
    with c_reset:
        if st.button("🗑️ 견적서 전체 초기화"):
            st.session_state.cart = []
            st.rerun()
            
    with c_total:
        st.markdown(
            f"<div style='text-align: right; background-color: #f0f2f6; padding: 15px; border-radius: 10px;'>"
            f"<h3 style='margin:0;'>총 매입 예상 금액: <span style='color:#E53935;'>{total_amount:,} 원</span></h3>"
            f"</div>",
            unsafe_allow_html=True
        )
