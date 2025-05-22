# Rakuten Scraper

This repository contains a Playwright based scraper for Rakuten searches.

## Batch Processing

`batch.py` reads a CSV file with columns `ID`, `キーワード` (keyword), and `店舗名` (shop). For each row it performs a search and saves the results into a folder named after `ID` under `results/`.

Usage:

```bash
python batch.py INPUT_CSV
```

The script will create a CSV file for each row with a timestamp in the file name.
