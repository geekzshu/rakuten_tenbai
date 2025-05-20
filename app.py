"""Streamlit interface for Rakuten scraper."""
import asyncio
import streamlit as st

from main import run, save_csv, Product

st.title("Rakuten Scraper")
keyword = st.text_input("検索キーワード")
skip_shop = st.text_input("除外店舗名")
run_button = st.button("検索")

if run_button and keyword:
    st.write("Running scraper...")
    products = asyncio.run(run(keyword, skip_shop))
    if products:
        st.write(f"{len(products)} 商品が見つかりました")
        # Display table
        st.table([{"商品名": p.name, "店舗名": p.shop, "URL": p.url} for p in products])
        csv_path = "result.csv"
        save_csv(products, csv_path)
        st.success("result.csv を保存しました")
        with open(csv_path, "rb") as f:
            st.download_button(
                "CSV をダウンロード",
                f,
                file_name="result.csv",
                mime="text/csv",
            )
    else:
        st.write("該当する商品がありませんでした")
