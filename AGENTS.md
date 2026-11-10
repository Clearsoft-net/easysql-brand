# AGENTS.md

Project instructions for AI agents working in this repository.

## What this is

EasySQL brand kit: logo and icon assets, usage rules, and the pipeline that
generates every raster and container export. A Clearsoft product.

Full brand guide: [`docs/logo-specification.md`](docs/logo-specification.md).
The README is the public index.

All assets are governed by the Clearsoft Brand & Trademark License
([`LICENSE`](LICENSE)); do not redistribute outside its terms.

## Layout

```
README.md                       Public brand kit index
AGENTS.md                       This file
LICENSE                         Clearsoft Brand & Trademark License
Makefile                        Export pipeline
docs/logo-specification.md      Brand usage guide
logo/
  source/                       Editable text SVGs (masters)
  exports/svg/                  Outlined distribution SVGs
  exports/png/{1x,2x,3x}/       Logo rasters
icon/
  source/                       Editable icon SVGs (standard + 16/24 cut)
  exports/svg/                  Outlined distribution SVGs
  exports/png/<size>x<size>/    16-1024 px rasters
  exports/ico/                  Windows ICO (16-256)
  exports/web/                  favicon, PWA, Apple touch, Android
  exports/macos/AppIcon.icns    macOS icon
scripts/export.py               PNG/ICO/ICNS export pipeline
scripts/outline.py              Text-to-path step (source -> exports/svg)
index.html                      Local brand showcase (not part of the published kit)
```

`variants/` is gitignored scratch for design comparisons; do not commit it.

## Build

```sh
make              # regenerate all exports from the outlined SVGs and run check
make outline      # rebuild logo/exports/svg/ and icon/exports/svg/ from source/
make logos        # logo PNGs 1x/2x/3x
make icons        # icon PNGs 16-1024
make ico          # Windows ICOs
make platform     # favicon/PWA/Apple/Android set
make macos        # AppIcon.icns
make check        # validate raster dimensions and ICO/ICNS frame sets
make clean        # delete generated exports (run make outline afterwards)
```

- `make` requires ImageMagick 7 with librsvg and Python 3.8+.
- `make outline` additionally requires HarfBuzz (`hb-shape`), fontTools, and
  Inter, Space Grotesk and Geist installed. It resolves fonts with `fc-match`
  and fails when the family does not match.
- Exports are byte-reproducible; PNG date chunks are excluded.

## Source vs exports

- Edit only `*/source/`. `*/exports/` is generated; never hand-edit it.
- `source/` SVGs use live text and require the fonts above.
- `exports/svg/` SVGs are outlined and self-contained; they are the files
  linked from the README and the input for every export.
- After editing a source, run `make outline`, then `make`.

## Brand hard constraints

- The name is `EasySQL` — one word, no space, no dot/slash separator.
- The wordmark pairs Space Grotesk Bold 700 ("Easy") with Geist Bold 700
  ("SQL"). "Easy" uses the text color; "SQL" uses `#F97316`.
- The "yS" seam carries a -1 px optical adjustment (`dx="-1"`); keep it.
- Monochrome lockups (`*-mono.svg`) are the fallback for one-color
  reproduction, small sizes and light backgrounds. Do not use the orange
  "SQL" at small sizes on white.
- The tile gradient is `#F97316` → `#F472B6`; do not recolor, distort or add
  effects. The monogram "E" stays Inter ExtraBold.
- 16/24 px icons use the small cut (`icon/source/*-small.svg`); 32 px and up
  use the standard icon. Do not use the standard icon for 16/24.
- The logo has no subtitle or tagline.

## Conventions

- Documentation, code comments and commit messages: English.
- Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`), imperative.
- Do not commit `variants/` or hand-edit generated exports.
- Do not push or tag without the owner's instruction.