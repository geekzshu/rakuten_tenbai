#!/usr/bin/env python3
"""Rakuten scraper using Playwright.

This script searches Rakuten for a given keyword and extracts product URL,
product name and store name from the search results. After collection, items
from stores containing a specified exclusion term are removed. Progress is
logged to stdout. The scraped results are saved into ``result.csv``.

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

# Configure logging to output detailed progress information
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

@dataclass
class Product:
    url: str
    name: str
    shop: str

async def scrape_page(page: Page, keyword: str) -> List[Product]:
    """Scrape Rakuten search results for ``keyword``."""
    query = urllib.parse.quote(keyword)
    url = SEARCH_URL.format(query=query)
    logging.info("Opening %s", url)
    await page.goto(url)
    await page.wait_for_selector("div.searchresultitem")
    items = await page.query_selector_all("div.searchresultitem")
    products: List[Product] = []
    logging.info("Found %d items", len(items))
    for idx, item in enumerate(items, 1):
        logging.info("Processing item %d/%d", idx, len(items))
        link = await item.query_selector("h2 > a")
        # Store name link is wrapped in an anchor with class '_ellipsis'
        shop_el = await item.query_selector("a._ellipsis")
        if not link or not shop_el:
            logging.warning("Missing link or shop element; skipping item %d", idx)
            continue
        name = (await link.inner_text()).strip()
        href = await link.get_attribute("href")
        shop = (await shop_el.inner_text()).strip()
        products.append(Product(url=href or "", name=name, shop=shop))
        logging.info("Collected %s from %s", name, shop)
    logging.info("Finished scraping %d products", len(products))
    return products

async def run(keyword: str, skip_shop: str) -> List[Product]:
    logging.info("Starting run with keyword=%s skip_shop=%s", keyword, skip_shop)
    async with async_playwright() as p:
        logging.info("Launching browser")
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        logging.info("Browser launched")
        products = await scrape_page(page, keyword)
        await browser.close()
        logging.info("Browser closed")

    if skip_shop:
        filtered: List[Product] = []
        for p in products:
            if skip_shop in p.shop:
                logging.info("Excluding %s from %s", p.name, p.shop)
                continue
            filtered.append(p)
        logging.info(
            "Filtered products: %d -> %d", len(products), len(filtered)
        )
        return filtered
    else:
        logging.info("Collected %d products", len(products))
        return products

def save_csv(products: List[Product], path: str) -> None:
    logging.info("Saving results to %s", path)
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


    products = asyncio.run(run(keyword, skip_shop))
    save_csv(products, "result.csv")
    print(f"Saved {len(products)} products to result.csv")

if __name__ == "__main__":
    main()

