# EasySQL — Logo Specification

> Brand usage guide · Version 1.2
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

> The dimensions above are the master viewBox in `logo/source/`. Distribution SVGs in `logo/exports/svg/` are cropped to the artwork with an 8 px transparent border at 1× — horizontal 261×88, stacked 145×130, text-only 181×70 — so the SVG and the 1× PNG share the same canvas. The PNGs use `-trim +repage -bordercolor none -border 8` at 1× (16 px at 2× and 24 px at 3×). Icons keep the full canvas because their sizes are absolute.

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

## 6. Border Radius & Corner Geometry

The corner radius of EasySQL brand elements derives from the official monogram tile geometry: **72×72 px** with **`rx = 16px`**, establishing the official **Tile Ratio** of **~22.2%** ($R \approx 0.222 \times \text{size}$).

### Brand Tile Ratio (Squircle Geometry)
For any square brand container, app icon, or tile:

| Tile Size | Corner Radius | Application |
|---|---|---|
| **16×16 px** | `3.5px` | Browser favicon (small-size cut) |
| **24×24 px** | `5px` | Compact menus, icon buttons |
| **32×32 px** | `7px` | Toolbar items, small avatars |
| **48×48 px** | `10px` | Integration cards, database connectors |
| **64×64 px** | `14px` | Feature highlights, dialogs |
| **72×72 px** | `16px` | **Official monogram tile (Logos 01–04, 07, 08)** |
| **128×128 px** | `28px` | Web store listing, splash screen |
| **256×256 px** | `56px` | Desktop app icon (macOS / Windows) |
| **512×512 px** | `112px` | PWA splash, App Store listing |

### UI Design System Scale

| Token | Value | Recommended Usage |
|---|---|---|
| `--radius-none` | `0px` | Dense SQL data tables, technical splitters, connected tabs |
| `--radius-xs` | `4px` | SQL type badges (`VARCHAR`, `INT`), compact tooltips, tree nodes |
| `--radius-sm` | `6px` / `8px` | Form inputs, select menus, secondary buttons, context menus |
| `--radius-md` | `10px` / `12px` | Primary buttons (CTAs), query editors, SQL code blocks |
| `--radius-lg` | `16px` | Main dashboard cards, side sheets, modal dialogs *(matches brand tile)* |
| `--radius-xl` | `24px` | Hero feature containers, marketing callout panels |
| `--radius-full` | `9999px` | Status badges, pills, circular action buttons |

### Concentric Nesting Rule
To prevent optical corner distortion when nesting rounded containers:
$$\text{Inner Radius} = \text{Outer Radius} - \text{Padding}$$

---

## 7. Don'ts

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

## 8. Files

Editable text sources: `logo/source/` (logos, with monochrome versions as `*-mono.svg`) and `icon/source/` (icons). Outlined distribution SVGs: `logo/exports/svg/` and `icon/exports/svg/`. Logo SVGs are cropped to the artwork with an 8 px transparent border at 1× (261×88 horizontal, 145×130 stacked, 181×70 text-only); icon SVGs keep the full canvas. These are the files linked and used by the exports. Logo PNGs ship at 1×/2×/3× in `logo/exports/png/` with the same crop and an 8 px border at 1× (16/24 px at 2×/3×); icon PNGs ship at absolute sizes (16x16 to 1024x1024) in `icon/exports/png/<size>x<size>/`; icons also have multi-resolution `.ico` files in `icon/exports/ico/`. Platform files (favicon, PWA, Apple touch, Android) live in `icon/exports/web/` and the macOS ICNS in `icon/exports/macos/`. Everything is generated by the `Makefile` (`make`); run `make outline` after editing a source.

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

---

## 8. Loaders

Loaders are transient UI states, not decoration. They may animate the gradient or reveal the E; they must not alter the mark.

### Construction

- The moving element uses the brand gradient `#F97316` → `#F472B6` only. Never recolor it.
- Bar tracks use `#F1F5F9` at 14% opacity on dark backgrounds and `#E2E8F0` on light backgrounds.
- Monogram loaders use the official 72×72 tile (`rx=16`) and the white Inter ExtraBold E. The light variants keep the `#E2E8F0` ring used by icon 08.
- No shadows, glows, blurs, bevels, extra colors, or filters.

### Motion

| Loader | Duration | Easing | Notes |
|---|---|---|---|
| 01 Orbit | 1.2 s | linear | Continuous rotation; gradient arc, no track. |
| 02 E-assemble | 1.8 s | ease-in-out | The tile stays static; the E stays whole and its arms brighten in sequence. |
| 03 Query bar | 1.4 s | cubic-bezier(.45, 0, .2, 1) | Indeterminate segment across a neutral track. |
| 04 Dots | 1.2 s | ease-in-out | 120 ms stagger. |
| 05 Splash | 1.4 s | cubic-bezier(.45, 0, .2, 1) | Tile + query bar; app boot only. |

- One loader per view. Do not bounce, overshoot, or use elastic easing.
- Keep the E upright. Never rotate or distort the monogram.
- Do not use the wordmark as a spinner.
- Pause the loader when the state resolves; do not leave an indeterminate animation running behind content.

### Formats

- **SVG** — the source and the resolution-independent choice. Transparent background, CSS animation, no fonts or scripts.
- **WebP** — 2×, 25 fps, animated WebP with alpha. **Default for loaders in UI**: works as `<img>`, loops natively and is supported in Safari 16+.
- **GIF** — 2×, 25 fps, transparent. 256 colors and 1-bit alpha; compatibility fallback only.

The animated formats do not carry the SVG's reduced-motion media query. Swap in the static poster with `<picture>` when `prefers-reduced-motion: reduce` matches. Generate with `make animated`; validate with `make check-animated`.

```html
<!-- Default: WebP with a static poster for reduced motion -->
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="loaders/static/01-orbit-static.svg">
  <img src="loaders/exports/webp/01-orbit.webp" width="96" height="96" alt="">
</picture>
```

### Reduced motion

Every animated loader has a static poster in `loaders/static/`. Use `<picture>` (or the host's motion check) to swap the poster when `prefers-reduced-motion: reduce` matches. The animated files also carry the media query, but browsers do not consistently apply it to SVG loaded as `<img>`. The GIF/WebP exports do not carry the media query; pause or swap them in the host.

```html
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="static/01-orbit-static.svg">
  <img src="01-orbit.svg" width="48" height="48" alt="">
</picture>
```

### Sizes and backgrounds

- 01 Orbit: 16–64 px; dark/product backgrounds. On white, use 02/05 or the monochrome lockup.
- 02 E-assemble: 48–160 px; light and dark (light variant with ring).
- 03 Query bar: full width; use the dark/light track.
- 04 Dots: 16–40 px tall; pair with text.
- 05 Splash: 120–240 px wide; app boot only.
- Minimum 16 px. Below that, use the static small-size icon cut instead.

### Files

| File | Description |
|---|---|
| `loaders/01-orbit.svg` | Gradient arc spinner |
| `loaders/02-e-assemble.svg` | E-assemble, dark |
| `loaders/02-e-assemble-light.svg` | E-assemble, light (ring) |
| `loaders/03-query-bar-dark.svg` | Query bar, dark track |
| `loaders/03-query-bar-light.svg` | Query bar, light track |
| `loaders/04-dots.svg` | Three-dot inline loader |
| `loaders/05-splash-dark.svg` | Splash composition, dark |
| `loaders/05-splash-light.svg` | Splash composition, light |
| `loaders/static/*.svg` | Static posters for reduced motion |
| `loaders/exports/gif/*.gif` | GIF exports (2×, 25 fps, 1-bit alpha) |
| `loaders/exports/webp/*.webp` | Animated WebP exports with alpha |

All loaders are validated by `make check` (structure, gradient, no text/scripts/filters, and static-poster freshness). The animated formats are validated by `make check-animated`.
