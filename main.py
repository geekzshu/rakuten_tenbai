#!/usr/bin/env python3
"""Simple Rakuten scraper.

This script searches Rakuten for a given keyword and extracts product URL,
product name and store name from the search results.
Results from a specific store can be skipped.
The collected data is stored into ``result.csv`` which can be
imported into Google Spreadsheet manually.

The actual scraping might not work without network access or if Rakuten
changes their HTML structure.
"""

import csv
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import List

@dataclass
class Product:
    url: str
    name: str
    shop: str

SEARCH_URL = "https://search.rakuten.co.jp/search/mall/{query}/"

PRODUCT_RE = re.compile(
    r'<a[^>]+href="(?P<url>[^"]+)"[^>]*>(?P<name>[^<]+)</a>.*?'  # product link
    r'<span[^>]*class=".*?searchresultitem__shop.*?"[^>]*>'
    r'(?P<shop>[^<]+)</span>',
    re.S,
)


def fetch_html(keyword: str) -> str:
    query = urllib.parse.quote(keyword)
    url = SEARCH_URL.format(query=query)
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8", "ignore")


def parse_products(html: str) -> List[Product]:
    products: List[Product] = []
    for match in PRODUCT_RE.finditer(html):
        url = match.group("url")
        name = match.group("name").strip()
        shop = match.group("shop").strip()
        products.append(Product(url=url, name=name, shop=shop))
    return products


def save_csv(products: List[Product], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["商品名", "店舗名", "URL"])
        for p in products:
            writer.writerow([p.name, p.shop, p.url])


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
