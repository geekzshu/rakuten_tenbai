#!/usr/bin/env python3
"""Rakuten scraper using Playwright.

This script searches Rakuten for a given keyword and extracts product URL,
product name and store name from the search results. Results from a
specified store can be skipped. Progress is logged to stdout. The scraped
results are saved into ``result.csv``.

Note: Network access might be blocked in this environment, so the scraper
may fail to fetch pages when executed here.
"""

import asyncio
import csv
import logging
import sys
import urllib.parse
from dataclasses import dataclass
from typing import List

from playwright.async_api import async_playwright, Page

SEARCH_URL = "https://search.rakuten.co.jp/search/mall/{query}/"

@dataclass
class Product:
    url: str
    name: str
    shop: str

async def scrape_page(page: Page, keyword: str, skip_shop: str) -> List[Product]:
    """Scrape Rakuten search results for ``keyword`` skipping ``skip_shop``."""
    query = urllib.parse.quote(keyword)
    url = SEARCH_URL.format(query=query)
    logging.info("Opening %s", url)
    await page.goto(url)
    await page.wait_for_selector("div.searchresultitem")
    items = await page.query_selector_all("div.searchresultitem")
    products: List[Product] = []
    logging.info("Found %d items", len(items))
    for item in items:
        link = await item.query_selector("h2 > a")
        shop_el = await item.query_selector(".searchresultitem__shop")
        if not link or not shop_el:
            continue
        name = (await link.inner_text()).strip()
        href = await link.get_attribute("href")
        shop = (await shop_el.inner_text()).strip()
        if shop == skip_shop:
            logging.info("Skipping %s from %s", name, shop)
            continue
        products.append(Product(url=href or "", name=name, shop=shop))
        logging.info("Collected %s from %s", name, shop)
    return products

async def run(keyword: str, skip_shop: str) -> List[Product]:
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        products = await scrape_page(page, keyword, skip_shop)
        await browser.close()
        return products

def save_csv(products: List[Product], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["商品名", "店舗名", "URL"])
        for p in products:
            writer.writerow([p.name, p.shop, p.url])

    logging.info("Saved %d products to %s", len(products), path)

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: main.py KEYWORD SKIP_SHOP")
        sys.exit(1)
    keyword = sys.argv[1]
    skip_shop = sys.argv[2]


    html = fetch_html(keyword)
    all_products = parse_products(html)
    filtered = [p for p in all_products if p.shop != skip_shop]
    save_csv(filtered, "result.csv")
    print(f"Saved {len(filtered)} products to result.csv")

if __name__ == "__main__":
    main()
