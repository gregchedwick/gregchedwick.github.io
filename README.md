# gregchedwick.dev

Personal portfolio site — an interactive resume and a home for the analytics projects I build
outside work. Live at **[gregchedwick.dev](https://gregchedwick.dev)**.

The idea: rather than a resume page that links to projects, the resume *is* a dashboard. Career
impact renders as live data visualization, and the Netflix Ads Analytics project ships as a real
filterable chart driven by the project's actual output — not a screenshot.

## Stack

| | |
|---|---|
| Framework | [Astro](https://astro.build) 7, static output |
| Language | TypeScript (strict) |
| Charts | Hand-rolled HTML/CSS/SVG — no chart library |
| Hosting | GitHub Pages via GitHub Actions |

Total payload is ~155 KB including the portrait, of which ~12 KB is JavaScript.

**Why no chart library.** Every chart here is a horizontal bar. Chart.js would have added ~70 KB
of canvas to draw rectangles that CSS draws for free — and canvas is invisible to screen readers
and doesn't react to a theme switch without a manual redraw. Plain elements are lighter,
accessible by default, and pick up the theme through CSS custom properties.

## Local development

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # static output to dist/
npm run preview      # serve the built output
npx astro check      # type-check
```

## Project layout

```
src/
  data/
    resume.ts          Career history, metrics, skills — single source of truth
    projects.ts        Project cards
    netflix-ads.json   Generated; see below
  assets/portrait.jpeg
  components/          Hero, ImpactMetrics, CareerTimeline, SkillsMatrix,
                       Projects, NetflixDashboard, Contact
  layouts/Base.astro   Head, nav, theme toggle, footer
  styles/tokens.css    Design tokens — color, type scale, spacing
scripts/
  export_web_data.py   Netflix CSV to compact JSON
```

To update the resume, edit `src/data/resume.ts`. Nothing is duplicated into markup.

## Refreshing the Netflix data

`src/data/netflix-ads.json` is generated from the sibling
[Netflix-Ads-Analytics](https://github.com/gregchedwick/Netflix-Ads-Analytics) repo, which must be
checked out alongside this one:

```bash
python scripts/export_web_data.py
```

The JSON is committed so this repo builds standalone — the source CSVs are large and gitignored
over there.

## Color and accessibility

The palette is shared between page chrome and charts, and the categorical slots were run through a
colorblind-separation validator in both light and dark mode:

| Mode | Worst adjacent CVD ΔE | Normal-vision ΔE | Contrast |
|------|----------------------|------------------|----------|
| Light | 9.1 | 22.9 | 2 slots below 3:1 → direct labels required |
| Dark | 8.4 | 19.8 | all slots ≥ 3:1 |

The two light-mode slots below 3:1 carry visible direct labels wherever they appear. Dark mode is
a selected set of steps chosen against the dark surface, not an inversion. Animations are
suppressed under `prefers-reduced-motion`, and every count-up renders its true value server-side
so the figures are correct without JavaScript.

## Deployment

Every push to `main` triggers `.github/workflows/deploy.yml`, which builds and publishes to GitHub
Pages.

### Custom domain

`gregchedwick.dev` is registered through Cloudflare, which also serves its DNS:

| Type | Name | Value |
|---|---|---|
| A | `@` | `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` |
| CNAME | `www` | `gregchedwick.github.io` |

Two things about this setup are load-bearing:

- **The DNS records are unproxied** (Cloudflare grey cloud). Proxied, the ACME challenge never
  reaches GitHub and the certificate silently never issues. Turning the proxy on later requires
  SSL/TLS mode **Full (strict)**, or requests loop between Cloudflare and GitHub.
- **`public/CNAME` ships in the build.** This repo publishes from an Actions artifact, so a custom
  domain set only in the repo settings would be cleared on the next deploy.

`.dev` is HSTS-preloaded across the whole TLD, so HTTPS is mandatory rather than advisory — a
missing certificate makes the site unreachable, not merely insecure. Enforce HTTPS is on and the
Let's Encrypt certificate renews automatically.
