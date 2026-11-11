# AGENTS.md

Project instructions for AI agents working in this repository.

## What this is

EasySQL brand kit: logo, icon, platform, social and loader assets, usage rules,
and the pipeline that generates every raster, container export, platform layer and
loader poster. A Clearsoft product.

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
  exports/svg/                  Outlined distribution SVGs (cropped)
  exports/png/{1x,2x,3x}/       Logo rasters
icon/
  source/                       Editable icon SVGs (standard, 16/24, one-color, platform)
  exports/svg/                  Outlined distribution SVGs
  exports/png/<size>x<size>/    16-1024 px rasters
  exports/ico/                  Windows ICO (16-256)
  exports/web/                  favicon, PWA, maskable, adaptive, themed, Apple touch, Android
  exports/macos/AppIcon.icns    macOS icon
loaders/                        Animated SVG loaders (dark/light variants)
  static/                       Generated reduced-motion posters
  exports/{gif,webp}/          Generated animated compatibility exports
social/
  exports/                      Generated Open Graph card and social avatar (SVG/PNG)
scripts/export.py               Raster, platform and social export pipeline
scripts/loaders.json            Loader dimensions/durations for animated exports
scripts/loaders.py              Static loader poster generation
scripts/loaders_animated.mjs    Chrome/FFmpeg animated export
scripts/check_animated.py       Animated loader validation
scripts/outline.py              Text-to-path step (source -> exports/svg)
index.html                      Static brand showcase (site entry point; includes the loader preview)
```

`variants/` is gitignored scratch for design comparisons; do not commit it.

The repository is served as a static site from the root, with `index.html` as
the entry point. Download links use relative paths; each one gets a copy-URL
button that resolves the absolute URL at runtime, so keep new asset links
relative to preserve the hosting origin in copied URLs.

## Build

```sh
make              # regenerate all exports and loader posters, then run check
make outline      # rebuild logo/exports/svg/ and icon/exports/svg/ from source/
make loaders      # generate the static loader posters in loaders/static/
make animated     # export GIF/WebP into loaders/exports/
make logos        # logo PNGs 1x/2x/3x
make icons        # icon PNGs 16-1024
make ico          # Windows ICOs
make platform     # favicon/PWA/maskable/adaptive/themed/Apple/Android set
make macos        # AppIcon.icns
make social       # Open Graph card and social avatar in social/exports/
make check        # validate rasters, platform layers, social cards, ICO/ICNS frames, and loader structure/posters
make check-animated # validate animated loader dimensions, frames, loops and alpha
make clean        # delete generated exports, social cards, loader posters and animated formats (run make outline and make loaders afterwards)
```

- `make` requires ImageMagick 7 with librsvg and Python 3.8+.
- `make animated` requires Node 22+, Chrome/Chromium and FFmpeg;
  `make check-animated` requires `ffprobe`.
- `make outline` additionally requires HarfBuzz (`hb-shape`), fontTools, and
  Inter, Space Grotesk and Geist installed. It resolves fonts with `fc-match`
  and fails when the family does not match.
- Exports are byte-reproducible; PNG date chunks are excluded.

## Release

Manual, no CI: validate, then tag and publish with `gh`.

1. From a clean `main`, `make outline && make` must leave `git status` clean
   (exports are reproducible), and `make check` plus `make check-animated` must
   pass.
2. Tag and publish in one step, on the `main` commit, with the kit attached:

```sh
git archive --format=zip --prefix=brand-kit/ -o /tmp/easysql-brand-kit.zip \
  HEAD README.md LICENSE docs logo/exports icon/exports loaders social/exports
gh release create vX.Y.Z /tmp/easysql-brand-kit.zip --target <sha> \
  --title "EasySQL Brand Kit vX.Y.Z" --latest --notes-file -
```

- Tags are lightweight (`v1.0.0`, `v2.0.0`); `gh release create --target`
  creates the tag, so no separate `git push --tags`.
- Bump the major when a pinned asset changes shape or file: v2.0.0 was the
  identity refresh, not an additive change.
- The asset is always `easysql-brand-kit.zip` and carries distribution only:
  `README.md`, `LICENSE`, `docs/`, the `exports/` trees, `loaders/` and
  `social/`. Sources, `scripts/`, `Makefile` and `index.html` stay in the
  repository.
- Notes in English (what changed, what is included, build, download); publish
  the release, never leave it as a draft.
- `gh` must be authenticated with `repo` scope on `Clearsoft-net/easysql-brand`.

## Source vs exports

- Edit only `*/source/`. `*/exports/` is generated; never hand-edit it.
- `source/` SVGs use live text and require the fonts above.
- `exports/svg/` SVGs are outlined and self-contained; they are the files
  linked from the README and the input for every export.
- Logo `exports/svg/` files are cropped to the artwork with an 8 px
  transparent border at 1× (same canvas as the 1× PNG); icon SVGs keep the
  full canvas. The `-bg` sources use the distribution crop viewBox so the
  opaque canvas matches the export exactly.
- After editing a source, run `make outline`, then `make`.
- `loaders/*.svg` are the animated sources; `loaders/static/` is generated by
  `make loaders` and `loaders/exports/` by `make animated`. After editing a
  loader, run both.
- `social/exports/` is generated by `make social` from the outlined logo and
  icon. It contains no live text; do not hand-edit it.

## Brand hard constraints

- The name is `EasySQL` — one word, no space, no dot/slash separator.
- The wordmark pairs Space Grotesk Bold 700 ("Easy") with Geist Bold 700
  ("SQL"). "Easy" uses the text color; "SQL" uses `#F97316`.
- The "yS" seam carries a -1 px optical adjustment (`dx="-1"`); keep it.
- Monochrome lockups (`logo/source/*-mono.svg`) keep the gradient tile and are
  the fallback for one-color reproduction, small sizes and light backgrounds.
  The one-color icon cuts (`icon/source/*-mono.svg`, 07m/08m) knock the E out of
  a solid tile for true single-ink reproduction. Do not use the orange "SQL" at
  small sizes on white.
- Maskable and adaptive icons keep the E inside the platform safe zone; the
  adaptive foreground layer stays transparent (the gradient belongs to the
  background layer).
- The tile gradient is `#F97316` → `#F472B6`; do not recolor, distort or add
  effects. The monogram "E" stays Inter ExtraBold.
- Loaders animate only the gradient element or the E bars; never recolor,
  distort or rotate the monogram. Keep the E upright.
- Every animated loader ships with a static poster in `loaders/static/`; use
  `<picture>` (or a host motion check) for `prefers-reduced-motion`.
- Animated exports keep the same gradient and alpha. WebP is the default
  loader format (image semantics, native loop, alpha). GIF is a 1-bit-alpha
  compatibility fallback.
- Use one loader per view and pair it with a text status; never use the
  wordmark as a spinner.
- 16/24 px icons use the small cut (`icon/source/*-small*.svg`); 32 px and up
  use the standard icon. Do not use the standard icon for 16/24.
- The logo has no subtitle or tagline.

## Conventions

- Documentation, code comments and commit messages: English.
- Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`), imperative.
- Do not commit `variants/` or hand-edit generated exports (`*/exports/`, `loaders/static/`, `loaders/exports/`).
- Do not push or tag without the owner's instruction.