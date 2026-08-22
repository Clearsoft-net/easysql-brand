# EasySQL — Logo Specification

> Guia de uso da marca · Versão 1.0
> Produto Clearsoft

---

## 1. Paleta de Cores

### Monograma "E" (tile de gradiente)

| Elemento | Início | Fim |
|---|---|---|
| Tile do monograma | `#F97316` (laranja) | `#F472B6` (rosa) |
| **E** (dentro do tile) | `#FFFFFF` (branco) | — |

O gradiente laranja→rosa é o mesmo acento Clearsoft, fechando a conexão com a holding.

### Texto

| Elemento | Dark mode | Light mode |
|---|---|---|
| "EasySQL" | `#F1F5F9` | `#0F172A` |
| Subtitle | `#94A3B8` | `#64748B` |

### Fundos

| Contexto | Cor |
|---|---|
| Fundo escuro do produto | `#0F2B3D` (azul petróleo) |
| Fundo claro | `#FFFFFF` |
| Anel do ícone (light bg, 08) | `#E2E8F0` |

---

## 2. Tipografia

| Elemento | Fonte | Peso | Detalhes |
|---|---|---|---|
| **E** (monograma) | Inter | Extra Bold (800) | white |
| "EasySQL" (logotipo) | Inter | Extra Bold (800) | — |
| Subtitle | Inter | Regular (400) | uppercase, letter-spacing amplo |

**Fonte principal:** [Inter](https://rsms.me/inter/) (open source, Google Fonts)
**Fallback:** `system-ui, -apple-system, sans-serif`
**Mono (código/contexto SQL):** `JetBrains Mono`, `Fira Code`

---

## 3. Proporções do logotipo

### Horizontal (01 / 02) — viewBox 340×120

```
←————————————— 340px —————————————→
┌─────────────────────────────────────┐
│                                     │
│  [E]   EasySQL                      │
│  tile   ↑                           │
│  72px   36px                        │
│                                     │
│        NATURAL LANGUAGE → SQL       │  ← 10px
└─────────────────────────────────────┘
```

| Elemento | Tamanho | Referência |
|---|---|---|
| Tile do monograma | 72×72 | gradiente, rx=16 |
| **E** | 46px | centralizado no tile |
| "EasySQL" | 36px | ~78% do tile |
| Subtitle | 10px | uppercase, tracking +3 |

### Stacked (03 / 04) — viewBox 210×170

```
┌───────── 210px ─────────┐
│                          │
│          [E]             │  ← tile 72×72, centralizado
│                          │
│       EasySQL            │  ← 30px, Extra Bold
│                          │
│ NATURAL LANGUAGE → SQL   │  ← 9px
└──────────────────────────┘
       170px altura
```

### Text only (05 / 06) — viewBox 200×88

```
←———— 200px ————→
┌──────────────────────────┐
│         ◆               │  ← losango gradiente
│      EasySQL             │  ← 38px Extra Bold
│  NATURAL LANGUAGE → SQL  │  ← 9.5px
└──────────────────────────┘
       88px altura
```

### Icon only (07 / 08) — 80×80

```
┌───── 80px ─────┐
│                 │
│      [E]        │  ← tile 72×72, E white 44px
│                 │
└─────────────────┘
```

08 (light) adiciona um anel `#E2E8F0` ao redor do tile para assentar em fundos claros.

---

## 4. Área de segurança (clear space)

- Ao redor do logotipo, mantenha espaçamento mínimo equivalente à altura de uma letra do wordmark.
- Nenhum elemento (texto, ícone, borda) deve invadir essa área.

---

## 5. Tamanho mínimo

| Variação | Mínimo recomendado |
|---|---|
| Horizontal (01/02) | 180px largura |
| Stacked (03/04) | 100px largura |
| Text only (05/06) | 120px largura |
| Icon only (07/08) | 24px (favicon) |

Abaixo desses tamanhos, usar apenas o ícone (07/08).

---

## 6. O que NÃO fazer

- ❌ Não esticar ou distorcer o logotipo
- ❌ Não alterar as cores do gradiente laranja→rosa
- ❌ Não adicionar sombras ou efeitos ao monograma
- ❌ Não usar o tile de gradiente com outra cor de fundo diferente da paleta
- ❌ Não usar fontes diferentes da Inter (exceto mono para SQL)
- ❌ Não escrever "Easy SQL" com espaço — é "EasySQL"
- ❌ Não usar o gradiente Clearsoft como cor de fundo principal (só em detalhes/acessórios)

---

## 7. Arquivos

| Arquivo | Descrição |
|---|---|
| `01-dark-horizontal.svg` | Logo completo — fundo escuro |
| `02-light-horizontal.svg` | Logo completo — fundo claro |
| `03-dark-stacked.svg` | Vertical — fundo escuro |
| `04-light-stacked.svg` | Vertical — fundo claro |
| `05-dark-text-only.svg` | Apenas texto + losango — fundo escuro |
| `06-light-text-only.svg` | Apenas texto + losango — fundo claro |
| `07-dark-icon-only.svg` | Apenas monograma E — fundo escuro |
| `08-light-icon-only.svg` | Apenas monograma E — fundo claro (anel #E2E8F0) |

> O ícone temático final (balão→DB, E-prompt, ou ?→tabela) é definido em Fase posterior. Por ora o monograma "E" é o marcador oficial (favicon/app icon).