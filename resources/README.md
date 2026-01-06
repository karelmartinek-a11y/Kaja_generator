# Font assets
This folder now ships with `montserrat_regular.ttf` and `montserrat_bold.ttf` (Montserrat Regular + Bold). Those files are generated from the Google Fonts checkout under `fonts-repo/ofl/montserrat` so `main.py` can register the exact weight and style that the design language mandates; no further downloads are required.

If you later refresh `fonts-repo` or want to regenerate the static files, install `fonttools` (`pip install fonttools`) and run:

```
python scripts/regenerate_montserrat.py
```

The helper script copies the base font for the regular weight and rewrites the metadata for the bold weight so PySide6 can distinguish both styles without relying on system fonts.
