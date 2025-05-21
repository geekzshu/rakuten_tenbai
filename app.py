"""Streamlit interface for Rakuten scraper."""
import asyncio
import streamlit as st
from pathlib import Path

from main import run, save_csv, Product, generate_csv_path

st.title("Rakuten Scraper")
keyword = st.text_input("検索キーワード")
skip_shop = st.text_input("除外店舗名")
run_button = st.button("検索")

if run_button and keyword:
    st.write("Running scraper...")
    products = asyncio.run(run(keyword, skip_shop))
    if products:
        st.write(f"{len(products)} 商品が見つかりました")
        st.table([{"商品名": p.name, "店舗名": p.shop, "URL": p.url} for p in products])
        path = generate_csv_path(keyword, skip_shop)
        save_csv(products, path)
        st.success(f"{Path(path).name} を保存しました")
        with open(path, "rb") as f:
            st.download_button("CSVをダウンロード", f, file_name=Path(path).name)

    else:
        st.write("該当する商品がありませんでした")
