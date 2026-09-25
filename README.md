# WatchDrop — live-feed upgrade

This version keeps the WatchDrop interface and adds a more capable product-feed importer.

## Important

The catalogue becomes live only after you obtain authorised product-feed access.

A practical route is:
1. Join relevant retailer affiliate programmes, such as suitable watch programmes on Awin.
2. Create one or more watch product feeds in Awin.
3. Copy the feed URLs.
4. In GitHub, open **Settings → Secrets and variables → Actions**.
5. Create a repository secret named `AWIN_FEEDS`.
6. Put the feed URLs in one line, separated by commas.
7. Run **Actions → Refresh WatchDrop catalogue → Run workflow**.

The workflow then refreshes the catalogue every six hours.

The importer is feed-first and does not scrape retailer websites. It filters for watch-related products, discounts, product links, and available items where stock data is supplied.
