# WatchDrop
Full GitHub Pages front end for a UK watch-deal finder.

## Features
- Responsive deal dashboard
- Search
- Price, discount, style, movement and water-resistance filters
- Brand filters generated from the data
- Best-deal / price / discount / saving sorting
- In-stock-only results
- Watchlist stored in the visitor's browser
- Deal statistics
- GitHub Actions refresh framework

## GitHub Pages
Repository → Settings → Pages → Deploy from branch → `main` → `/ (root)`.

## Live data
`data/watches.json` is deliberately separate from the interface. Connect authorised
retailer or affiliate product feeds to the GitHub Action before using automated
collection. Do not put private API keys in the website.
