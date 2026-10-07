# fairdraftstudio.fr-redirect

Fairdraft Studio is now Suivel (October 2026). This repository keeps every fairdraftstudio.fr address working: each page sends the visitor at once to the same address on https://suivel.fr, with its `?query` and `#anchor`.

GitHub Pages serves `docs/` (branch `main`, folder `/docs`) on the custom domain fairdraftstudio.fr. The pages are written by `build.py` from the main site's `sitemap.xml`; any other address gets `404.html`, which forwards the same way.

```
python build.py NEW_DOMAIN --cname
```

GitHub Pages can't send a server-side 301, so each page uses a script (keeps `?query` and `#anchor`), an instant meta refresh and a canonical link.
