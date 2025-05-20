import streamlit as st
from main import fetch_html, parse_products

st.title("楽天スクレイパー")

keyword = st.text_input("検索キーワード")
skip_shop = st.text_input("除外したい店舗名")

if st.button("検索"):
    if not keyword:
        st.error("検索キーワードを入力してください")
    else:
        try:
            html = fetch_html(keyword)
            products = [p for p in parse_products(html) if p.shop != skip_shop]
            if products:
                st.success(f"{len(products)}件の結果")
                data = [{"商品名": p.name, "店舗名": p.shop, "URL": p.url} for p in products]
                st.dataframe(data)
            else:
                st.info("該当する商品が見つかりませんでした")
        except Exception as e:
            st.error(f"取得中にエラーが発生しました: {e}")
