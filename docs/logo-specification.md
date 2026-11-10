# EasySQL — Logo Specification

> Brand usage guide · Version 1.0
> A Clearsoft Product

---

## 1. Color Palette

### "E" Monogram (gradient tile)

| Element | Start | End |
|---|---|---|
| Monogram tile | `#F97316` (orange) | `#F472B6` (pink) |
| **E** (inside the tile) | `#FFFFFF` (white) | — |

The orange→pink gradient is the same Clearsoft accent, tying the brand to its parent company.

### Text

| Element | Dark mode | Light mode |
|---|---|---|
| "Easy" | `#F1F5F9` | `#0F172A` |
| "SQL" | `#F97316` | `#F97316` |

"SQL" uses the same orange in both modes; "Easy" follows the text color.

On light backgrounds, use the monochrome lockups for small sizes or one-color/print reproduction; the orange "SQL" is intended for display sizes.

### Backgrounds

| Context | Color |
|---|---|
| Product dark background | `#0F2B3D` (petroleum blue) |
| Light background | `#FFFFFF` |
| Icon ring (light bg, 08) | `#E2E8F0` |

---

## 2. Typography

| Element | Typeface | Weight | Details |
|---|---|---|---|
| **E** (monogram) | Inter | Extra Bold (800) | white |
| "EasySQL" (wordmark) | Space Grotesk ("Easy") + Geist ("SQL") | Bold (700) | "Easy" in the text color; "SQL" in `#F97316` |

**UI and monogram typeface:** [Inter](https://rsms.me/inter/) (open source, Google Fonts)
**Wordmark typefaces:** [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) Bold (700) for "Easy" and [Geist](https://fonts.google.com/specimen/Geist) Bold (700) for "SQL"
**Fallback:** `system-ui, -apple-system, sans-serif`
**Mono (code / SQL context):** `JetBrains Mono`, `Fira Code`

The shipped SVGs in `logo/exports/svg/` and `icon/exports/svg/` are outlined; the typefaces above are used to edit the sources in `source/`.

---

## 3. Logo Proportions

### Horizontal (01 / 02) — viewBox 286×120

```
←—————————— 286px ——————————→
┌────────────────────────────┐
│                            │
│  [E]   EasySQL             │
│  tile   ↑                  │
│  72px   37.4px             │
│                            │
└────────────────────────────┘
```

| Element | Size | Reference |
|---|---|---|
| Monogram tile | 72×72 | gradient, rx=16 |
| **E** | 46px | centered in the tile |
| "EasySQL" | "Easy" 37.4px · "SQL" 36.9px | "Easy" in the text color; "SQL" in `#F97316` |

> The "yS" seam carries a -1 px optical adjustment to balance the Space Grotesk → Geist transition.

### Stacked (03 / 04) — viewBox 210×137

```
┌───────── 210px ─────────┐
│                          │
│          [E]             │  ← tile 72×72, centered
│                          │
│       EasySQL            │  ← 31.2px, Bold
│                          │
└──────────────────────────┘
       137px height
```

### Text only (05 / 06) — viewBox 200×74

```
←———— 200px ————→
┌──────────────────────────┐
│         ◆               │  ← gradient diamond
│      EasySQL             │  ← 39.5px Bold
└──────────────────────────┘
       74px height
```

### Icon only (07 / 08) — 80×80

```
┌───── 80px ─────┐
│                 │
│      [E]        │  ← tile 72×72, E white 44px
│                 │
└─────────────────┘
```

08 (light) adds an `#E2E8F0` ring around the tile so it sits well on light backgrounds.

For 16 and 24 px there is a dedicated small-size cut: the tile fills the canvas and the E is drawn on a 2 px grid for legibility.

> The dimensions above are the SVG viewBox. Logo PNGs are cropped to the content with `-trim +repage -bordercolor none -border`, with a transparent border of 8 px at 1× (16 px at 2× and 24 px at 3×), so the exported PNG does not have the viewBox size. Icons keep the full canvas because their sizes are absolute.

---

## 4. Clear Space

- Keep a minimum spacing around the logo equal to the height of a letter in the wordmark.
- No element (text, icon, border) may enter that area.

---

## 5. Minimum Size

| Variation | Recommended minimum |
|---|---|
| Horizontal (01/02) | 180px width |
| Stacked (03/04) | 100px width |
| Text only (05/06) | 120px width |
| Icon only (07/08) | 24px (favicon) |

Below these sizes, use the icon only (07/08). The 16/24 px exports use the small-size cut.

---

## 6. Don'ts

- ❌ Don't stretch or distort the logo
- ❌ Don't change the orange→pink gradient colors
- ❌ Don't add shadows or effects to the monogram
- ❌ Don't use the gradient tile on a background color outside the palette
- ❌ Don't use another typeface for the monogram (Inter), "Easy" (Space Grotesk), or "SQL" (Geist)
- ❌ Don't write "Easy SQL" with a space — it is "EasySQL"
- ❌ Don't separate "Easy" and "SQL" with a dot, slash, or space — the distinction is color
- ❌ Don't invert the colors: "Easy" uses the text color and "SQL" uses `#F97316`
- ❌ Don't use the orange "SQL" at small sizes on light backgrounds — use the monochrome lockup
- ❌ Don't use the Clearsoft gradient as the main background color (accents only)

---

## 7. Files

Editable text sources: `logo/source/` (logos, with monochrome versions as `*-mono.svg`) and `icon/source/` (icons). Outlined distribution SVGs: `logo/exports/svg/` and `icon/exports/svg/`; these are the files linked and used by the exports. Logo PNGs ship at 1×/2×/3× in `logo/exports/png/`, cropped to the content with a transparent 8 px border at 1× (16/24 px at 2×/3×); icon PNGs ship at absolute sizes (16x16 to 1024x1024) in `icon/exports/png/<size>x<size>/`; icons also have multi-resolution `.ico` files in `icon/exports/ico/`. Platform files (favicon, PWA, Apple touch, Android) live in `icon/exports/web/` and the macOS ICNS in `icon/exports/macos/`. Everything is generated by the `Makefile` (`make`); run `make outline` after editing a source.

| File | Description |
|---|---|
| `logo/exports/svg/01-dark-horizontal.svg` | Full logo — dark background |
| `logo/exports/svg/02-light-horizontal.svg` | Full logo — light background |
| `logo/exports/svg/03-dark-stacked.svg` | Stacked — dark background |
| `logo/exports/svg/04-light-stacked.svg` | Stacked — light background |
| `logo/exports/svg/05-dark-text-only.svg` | Wordmark + diamond — dark background |
| `logo/exports/svg/06-light-text-only.svg` | Wordmark + diamond — light background |
| `logo/exports/svg/01-dark-horizontal-mono.svg` | Horizontal — monochrome, dark background |
| `logo/exports/svg/02-light-horizontal-mono.svg` | Horizontal — monochrome, light background |
| `logo/exports/svg/03-dark-stacked-mono.svg` | Stacked — monochrome, dark background |
| `logo/exports/svg/04-light-stacked-mono.svg` | Stacked — monochrome, light background |
| `logo/exports/svg/05-dark-text-only-mono.svg` | Wordmark only — monochrome, dark background |
| `logo/exports/svg/06-light-text-only-mono.svg` | Wordmark only — monochrome, light background |
| `icon/exports/svg/07-dark-icon-only.svg` | E monogram only — dark background |
| `icon/exports/svg/08-light-icon-only.svg` | E monogram only — light background (#E2E8F0 ring) |
| `icon/exports/svg/07-dark-icon-small.svg` | 16/24 px icon cut — dark background |
| `icon/exports/svg/08-light-icon-small.svg` | 16/24 px icon cut — light background |

> `logo/exports/svg/02-light-horizontal-bg.svg` is the 02 variant with a forced white background (outlined SVG; no raster exports). The editable text version is `logo/source/02-light-horizontal-bg.svg`.

> The final thematic icon (speech bubble→DB, E-prompt, or ?→table) is defined in a later phase. For now the "E" monogram is the official marker (favicon/app icon).