import asyncio
import csv
from pathlib import Path
import sys

from main import run, save_csv, generate_csv_path, Product


def filter_by_shop(products, shop):
    """Return only products sold by ``shop``. If shop is falsy, return products."""
    if not shop:
        return products
    filtered = [p for p in products if shop in p.shop]
    return filtered


async def process_row(row):
    id_ = row.get("ID") or row.get("id")
    keyword = row.get("キーワード") or row.get("keyword")
    shop = row.get("店舗名") or row.get("shop")
    if not id_ or not keyword:
        print("Row is missing required columns:", row)
        return

    products = await run(keyword, "")
    products = filter_by_shop(products, shop)
    results_dir = Path("results") / str(id_)
    path = generate_csv_path(keyword, shop or "", results_dir)
    save_csv(products, path)
    print(f"Saved {len(products)} products to {path}")


async def process_csv(file_path):
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await process_row(row)


def main():
    if len(sys.argv) < 2:
        print("Usage: batch.py INPUT_CSV")
        return
    asyncio.run(process_csv(sys.argv[1]))


if __name__ == "__main__":
    main()
