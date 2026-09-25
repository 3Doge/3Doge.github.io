# WatchDrop

A GitHub Pages watch-deal finder.

## GitHub Pages
Repository → Settings → Pages → Deploy from branch → `main` → `/ (root)`.

## Live product feeds
The project is designed to use authorised retailer/affiliate product feeds.
Awin provides publisher product feeds containing product names, prices, images,
stock and links. You need your own Awin publisher access/feed URLs.

Create a GitHub Actions repository secret:
`AWIN_FEEDS`

Value:
`feed_url_1,feed_url_2,feed_url_3`

Never commit API keys or private feed URLs into the repository.

The workflow refreshes every 6 hours and commits the resulting `data/watches.json`.
You can also run it manually from Actions → Refresh WatchDrop → Run workflow.

## Important
Only add feeds you are authorised to use and follow each retailer/network's
terms. The frontend is static, so GitHub Pages never needs your private API key.
