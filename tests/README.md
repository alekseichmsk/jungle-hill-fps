# Tests
Requires: python3, `pip install pytest playwright && playwright install chromium`.
- Local: `npm run serve` (port 8931) in one terminal, then `npm test`.
- Live GitHub Pages: `npm run test:live`.
The game exposes `window.__test` helpers only when the URL contains `?test=1`.
