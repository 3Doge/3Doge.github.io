"""
WatchDrop feed importer.

This version is intentionally feed-first: put authorised product-feed URLs in
the environment variable AWIN_FEEDS (comma-separated). GitHub Actions supplies
the secret. The importer keeps watches that are in stock and discounted.

Do not put API keys or private feed URLs directly in this file.
"""
import csv, io, json, os, urllib.request
from pathlib import Path

OUT=Path("data/watches.json")
feeds=[x.strip() for x in os.getenv("AWIN_FEEDS","").split(",") if x.strip()]

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"WatchDrop/1.0"})
    with urllib.request.urlopen(req,timeout=45) as r: return r.read()

def money(v):
    try: return float(str(v).replace("£","").replace(",","").strip())
    except: return None

def norm(row):
    price=money(row.get("search_price") or row.get("store_price") or row.get("price"))
    old=money(row.get("rrp_price") or row.get("product_price_old") or row.get("base_price"))
    if price is None: return None
    stock=str(row.get("in_stock","")).lower() in {"1","true","yes"} or str(row.get("stock_status","")).lower() in {"in stock","available"}
    brand=(row.get("brand_name") or row.get("brand") or "").strip()
    name=(row.get("product_name") or row.get("name") or "").strip()
    if not name: return None
    disc=round((old-price)/old*100) if old and old>price else 0
    cat=(row.get("merchant_category") or row.get("category_name") or "").lower()
    style="Diver" if "diver" in cat else "Chronograph" if "chrono" in cat else "Dress" if "dress" in cat else "Sport" if "sport" in cat else "Watch"
    return {"brand":brand,"name":name,"price":price,"rrp":old,"discount_percent":disc,"style":style,
            "movement":"","water_resistance":"","retailer":row.get("merchant_name",""),
            "url":row.get("merchant_deep_link") or row.get("deep_link") or row.get("purl",""),
            "image_url":row.get("large_image") or row.get("imgurl",""),"in_stock":stock}

items={}
for url in feeds:
    raw=get(url)
    # Awin CSV feeds are commonly gzip-compressed; Python's urllib may expose
    # compressed bytes depending on the URL. Handle plain CSV here.
    text=raw.decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(io.StringIO(text))
    for row in reader:
        x=norm(row)
        if x and x["in_stock"] and x["discount_percent"]>0 and x["url"]:
            key=(x["brand"],x["name"],x["retailer"])
            items[key]=x

# Keep starter data if no feeds are configured.
if items:
    OUT.write_text(json.dumps(list(items.values()),indent=2,ensure_ascii=False),encoding="utf-8")
else:
    print("No feeds configured or no qualifying products returned; existing data retained.")
