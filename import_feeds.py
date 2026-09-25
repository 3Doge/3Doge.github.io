#!/usr/bin/env python3
"""
WatchDrop feed importer.

Reads one or more authorised product-feed URLs from AWIN_FEEDS.
Supports CSV, TSV, and JSON feeds. It keeps watch products that are:
- in stock (when stock information is provided)
- discounted, or have an RRP higher than the current price

This script intentionally does not scrape retailer websites.
"""
from __future__ import annotations
import csv, io, json, os, re, sys
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from typing import Any

OUT = "data/watches.json"

def clean(v: Any) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()

def first(row, *keys):
    lowered = {str(k).strip().lower(): v for k, v in row.items()}
    for key in keys:
        value = lowered.get(key.lower())
        if value not in (None, ""):
            return value
    return ""

def money(v):
    if v is None:
        return None
    s = str(v).replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None

def truthy_stock(v):
    s = clean(v).lower()
    if not s:
        return True  # unknown stock is retained, but marked as unknown
    return not any(x in s for x in ["out of stock", "out-of-stock", "unavailable", "sold out", "false", "no"])

def parse_payload(raw, content_type=""):
    text = raw.decode("utf-8-sig", errors="replace")
    if "json" in content_type or text.lstrip().startswith(("[", "{")):
        obj = json.loads(text)
        if isinstance(obj, dict):
            for key in ("products", "items", "offers", "data"):
                if isinstance(obj.get(key), list):
                    return obj[key]
            return [obj]
        return obj
    dialect = csv.Sniffer().sniff(text[:10000], delimiters=",\t;")
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))

def fetch(url):
    req = Request(url, headers={"User-Agent": "WatchDrop-feed-importer/1.0"})
    with urlopen(req, timeout=60) as r:
        return parse_payload(r.read(), r.headers.get("content-type", ""))

def normalise(row, index):
    name = clean(first(row, "product_name", "name", "title", "product title"))
    brand = clean(first(row, "brand_name", "brand", "manufacturer"))
    price = money(first(row, "search_price", "price", "sale_price", "current_price"))
    rrp = money(first(row, "rrp_price", "rrp", "was_price", "original_price", "list_price"))
    stock_raw = first(row, "stock_status", "availability", "in_stock", "stock")
    url = clean(first(row, "merchant_deep_link", "deep_link", "product_url", "url", "link"))
    image = clean(first(row, "merchant_image_url", "image_url", "image", "image_link"))
    merchant = clean(first(row, "merchant_name", "merchant", "retailer", "store"))
    category = clean(first(row, "category", "product_type", "google_product_category"))
    description = clean(first(row, "description", "product_description"))
    sku = clean(first(row, "merchant_product_id", "product_id", "id", "ean", "gtin", "mpn"))

    haystack = " ".join([name, brand, category, description]).lower()
    watch_words = ["watch", "watches", "chronograph", "seastar", "diver", "automatic", "quartz", "casio", "tissot", "seiko", "rotary", "citizen", "orient", "bulova", "festina", "timex", "acc urist", "boss"]
    if not any(word in haystack for word in watch_words):
        return None
    if not name or price is None or not url:
        return None
    if not truthy_stock(stock_raw):
        return None

    discount = 0
    if rrp and rrp > price:
        discount = round((rrp - price) / rrp * 100)
    explicit_discount = money(first(row, "discount_percent", "discount", "sale_percentage"))
    if explicit_discount is not None and explicit_discount > discount:
        discount = round(explicit_discount)
    if discount <= 0:
        return None

    low = haystack
    style = "Sport"
    if any(x in low for x in ["diver", "diving", "seastar", "submariner"]):
        style = "Diver"
    elif "chronograph" in low:
        style = "Chronograph"
    elif any(x in low for x in ["dress", "classic", "formal"]):
        style = "Dress"
    elif "field" in low:
        style = "Field"

    movement = "Quartz"
    if any(x in low for x in ["automatic", "powermatic", "mechanical"]):
        movement = "Automatic" if "automatic" in low or "powermatic" in low else "Mechanical"
    elif "solar" in low:
        movement = "Solar"

    water = ""
    wm = re.search(r"(\d{2,4})\s*m(?:eter| metres| meters)?", low)
    if wm:
        water = wm.group(1) + "m"

    return {
        "id": f"feed-{sku or abs(hash(url))}",
        "brand": brand or "Unknown",
        "name": name,
        "price": round(price, 2),
        "rrp": round(rrp, 2) if rrp else round(price, 2),
        "discount_percent": discount,
        "style": style,
        "movement": movement,
        "water_resistance": water,
        "case_size": "",
        "retailer": merchant or "Affiliate retailer",
        "url": url,
        "image": image,
        "in_stock": True,
        "source": "authorised product feed",
        "last_checked": datetime.now(timezone.utc).isoformat()
    }

def main():
    urls = [x.strip() for x in os.getenv("AWIN_FEEDS", "").split(",") if x.strip()]
    if not urls:
        print("No AWIN_FEEDS configured; keeping existing catalogue.")
        return

    results, seen = [], set()
    for url in urls:
        try:
            rows = fetch(url)
            print(f"Loaded {len(rows)} rows from {url}")
            for i, row in enumerate(rows):
                item = normalise(row, i)
                if not item:
                    continue
                key = item["url"].split("?")[0].lower()
                if key in seen:
                    continue
                seen.add(key)
                results.append(item)
        except Exception as exc:
            print(f"Feed failed: {url}: {exc}", file=sys.stderr)

    results.sort(key=lambda x: (-x["discount_percent"], x["price"]))
    if results:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(results)} discounted watches to {OUT}")
    else:
        print("No valid discounted watches found; existing catalogue retained.")

if __name__ == "__main__":
    main()
