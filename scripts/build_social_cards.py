"""Build the link-preview cards.

    python scripts/build_social_cards.py

Writes three 1200x630 PNGs into public/:

    og-image.png              the site's own og:image
    social/carrier-survival.png
    social/netflix-ads.png

The site had no og:image at all, so every share of gregchedwick.dev rendered as
a card with no picture — and the twitter:card tag promises a *large* image,
which made the empty result worse than a compact text card would have been.

The two project cards are for GitHub's Settings -> Social preview, and double as
the thumbnails LinkedIn accepts per Featured item. One asset per destination
keeps the link looking the same wherever it is posted.

Every number on these cards is read from the project's own output — metrics.json
and netflix-ads.json — rather than typed in here, so a card cannot quietly
disagree with the site it advertises.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

SITE = Path(__file__).resolve().parents[1]
OUT = SITE / "public"
METRICS = SITE.parent / "carrier-survival" / "docs" / "metrics.json"
NETFLIX = SITE / "src" / "data" / "netflix-ads.json"

# Straight from src/styles/tokens.css — the cards and the site share a palette.
PAGE = "#f9f9f7"
INK = "#0b0b0b"
INK2 = "#52514e"
INK3 = "#898781"
GRID = "#e1e0d9"
ACCENT = "#2a78d6"
ACCENT2 = "#eb6834"

# Segoe UI is what system-ui resolves to on Windows, so the cards match the site
# as rendered rather than as specified.
FAMILY = ["Segoe UI", "DejaVu Sans"]
MONO = ["Cascadia Mono", "Consolas", "DejaVu Sans Mono"]

W, H = 12.0, 6.3  # inches at dpi 100 -> 1200x630, the size every platform wants


def canvas():
    fig = plt.figure(figsize=(W, H), dpi=100)
    fig.patch.set_facecolor(PAGE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def save(fig, name: str) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor=PAGE, dpi=100)
    plt.close(fig)
    print(f"  {path.relative_to(SITE)}  ({path.stat().st_size // 1024} KB)")


def rule(ax, x, y, width, color=ACCENT, lw=3):
    ax.plot([x, x + width], [y, y], color=color, lw=lw, solid_capstyle="butt")


#: The text column stops here and the chart starts at CHART_L. Both cards ran
#: their headline straight under the plot before these were fixed.
TEXT_R = 0.50
CHART_L = 0.585


def chip(ax, x, y, value, label, color=ACCENT):
    """A figure and its caption, stacked."""
    ax.text(x, y, value, fontfamily=MONO, fontsize=20, color=color, va="bottom")
    ax.text(x, y - 0.052, label, fontfamily=FAMILY, fontsize=12, color=INK3, va="bottom")


# ---------------------------------------------------------------- site card ---
def site_card(profile_title: str) -> None:
    fig, ax = canvas()
    x = 0.075

    ax.text(x, 0.845, "GREGCHEDWICK.DEV", fontfamily=MONO, fontsize=13,
            color=INK3, va="bottom")
    rule(ax, x, 0.815, 0.075)

    ax.text(x, 0.615, "Greg Chedwick", fontfamily=FAMILY, fontsize=60,
            color=INK, va="bottom", fontweight="bold")
    ax.text(x, 0.525, profile_title + "  ·  Microsoft", fontfamily=FAMILY,
            fontsize=25, color=ACCENT, va="bottom")

    ax.text(x, 0.345, "Domain agnostic: I build the data models,", fontfamily=FAMILY,
            fontsize=22, color=INK2, va="bottom")
    ax.text(x, 0.275, "then the dashboards and automation people actually use.",
            fontfamily=FAMILY, fontsize=22, color=INK2, va="bottom")

    rule(ax, x, 0.185, 0.85, color=GRID, lw=1.5)
    for i, (value, label) in enumerate(
        [("20+ yrs", "data analytics"), ("4,300+", "hours automated / yr"),
         ("$3.2B", "portfolio in view"), ("0.889", "AUC, carrier model")]
    ):
        chip(ax, x + i * 0.215, 0.085, value, label)

    save(fig, "og-image.png")


# ------------------------------------------------------------- carrier card ---
def carrier_card(m: dict) -> None:
    fig, ax = canvas()
    x = 0.06
    gains = m["gains"]
    ten = round(gains["top_10pct"] * 100)

    ax.text(x, 0.855, "CARRIER SURVIVAL MODEL", fontfamily=MONO, fontsize=13,
            color=INK3, va="bottom")
    rule(ax, x, 0.825, 0.075)

    ax.text(x, 0.660, "Review the riskiest 10%,", fontfamily=FAMILY, fontsize=33,
            color=INK, va="bottom", fontweight="bold")
    ax.text(x, 0.565, f"catch {ten}% of the failures", fontfamily=FAMILY, fontsize=33,
            color=ACCENT, va="bottom", fontweight="bold")

    ax.text(x, 0.470, "Predicting whether a motor carrier\nis still operating twelve months\nout, from public FMCSA data.",
            fontfamily=FAMILY, fontsize=17, color=INK2, va="top", linespacing=1.6)

    for i, (value, label) in enumerate(
        [(f"{m['model']['auc']:.3f}", "AUC"),
         (f"{m['model']['lift']:.1f}x", "lift over base rate"),
         (f"{m['carriers'] / 1e6:.1f}M", "carriers")]
    ):
        chip(ax, x + i * 0.155, 0.115, value, label)

    ax.text(0.94, 0.055, "github.com/gregchedwick/carrier-survival", fontfamily=MONO,
            fontsize=13, color=INK3, ha="right", va="bottom")

    # Cumulative gains, drawn from the same numbers the README publishes.
    inner = fig.add_axes([CHART_L + 0.055, 0.30, 0.315, 0.50])
    inner.set_facecolor(PAGE)
    for side in ("top", "right"):
        inner.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        inner.spines[side].set_color(GRID)
    xs = [0] + [int(k.split("_")[1].rstrip("pct")) / 100 for k in
                ("top_5pct", "top_10pct", "top_20pct")] + [1]
    ys = [0] + [gains[k] for k in ("top_5pct", "top_10pct", "top_20pct")] + [1]
    inner.plot([0, 1], [0, 1], color=GRID, lw=1.6, ls="--")
    inner.plot(xs, ys, color=ACCENT, lw=3)
    inner.fill_between(xs, ys, color=ACCENT, alpha=0.10)
    inner.plot([0.10], [gains["top_10pct"]], "o", color=ACCENT, ms=9)
    inner.set_xlim(0, 1)
    inner.set_ylim(0, 1)
    inner.set_xticks([0, 0.5, 1])
    inner.set_yticks([0, 0.5, 1])
    inner.set_xticklabels(["0", "50%", "100%"], fontfamily=FAMILY, fontsize=11, color=INK3)
    inner.set_yticklabels(["0", "50%", "100%"], fontfamily=FAMILY, fontsize=11, color=INK3)
    inner.tick_params(length=3, color=GRID)
    inner.set_xlabel("carriers reviewed", fontfamily=FAMILY, fontsize=12, color=INK2)
    inner.set_ylabel("failures caught", fontfamily=FAMILY, fontsize=12, color=INK2)

    save(fig, "social/carrier-survival.png")


# ------------------------------------------------------------- netflix card ---
def netflix_card(d: dict) -> None:
    fig, ax = canvas()
    x = 0.06
    ranked = d["titleCount"]

    ax.text(x, 0.855, "NETFLIX AD INVENTORY ANALYTICS", fontfamily=MONO, fontsize=13,
            color=INK3, va="bottom")
    rule(ax, x, 0.825, 0.075, color=ACCENT2)

    ax.text(x, 0.660, "Where is ad inventory", fontfamily=FAMILY, fontsize=33,
            color=INK, va="bottom", fontweight="bold")
    ax.text(x, 0.565, "worth buying?", fontfamily=FAMILY, fontsize=33,
            color=ACCENT2, va="bottom", fontweight="bold")

    ax.text(x, 0.470, "A weighted opportunity score over\nthe global top 500 — hours viewed,\nstaying power, rating, recency.",
            fontfamily=FAMILY, fontsize=17, color=INK2, va="top", linespacing=1.6)

    for i, (value, label) in enumerate(
        [(f"{ranked}", "titles ranked"), ("32k+", "catalogue merged"), ("4", "scoring inputs")]
    ):
        chip(ax, x + i * 0.155, 0.115, value, label, color=ACCENT2)

    ax.text(0.94, 0.055, "github.com/gregchedwick/Netflix-Ads-Analytics", fontfamily=MONO,
            fontsize=13, color=INK3, ha="right", va="bottom")

    # Top titles by score. The leader runs about four times the runner-up, so the
    # axis stops above second place and the overrunning bar is drawn clipped —
    # the same treatment the live dashboard uses, for the same reason.
    titles = d["titles"][:5][::-1]
    scores = [t["score"] for t in titles]
    axis = sorted(scores)[-2] * 1.12
    inner = fig.add_axes([CHART_L + 0.115, 0.28, 0.255, 0.52])
    inner.set_facecolor(PAGE)
    for side in ("top", "right", "left"):
        inner.spines[side].set_visible(False)
    inner.spines["bottom"].set_color(GRID)
    for i, (t, s) in enumerate(zip(titles, scores)):
        inner.barh(i, min(s, axis), height=0.62, color=ACCENT2,
                   alpha=1.0 if s <= axis else 0.55)
    inner.set_yticks(range(len(titles)))
    inner.set_yticklabels(
        [t["title"][:16] + ("…" if len(t["title"]) > 16 else "") for t in titles],
        fontfamily=FAMILY, fontsize=12, color=INK2)
    inner.set_xlim(0, axis)
    inner.set_xticks([])
    inner.tick_params(length=0)
    inner.set_xlabel("opportunity score", fontfamily=FAMILY, fontsize=12, color=INK2)

    save(fig, "social/netflix-ads.png")


def main() -> None:
    metrics = json.loads(METRICS.read_text(encoding="utf8"))
    netflix = json.loads(NETFLIX.read_text(encoding="utf8"))
    resume = (SITE / "src" / "data" / "resume.ts").read_text(encoding="utf8")
    title = resume.split("title: '", 1)[1].split("'", 1)[0]

    print("building link-preview cards (1200x630):")
    site_card(title)
    carrier_card(metrics)
    netflix_card(netflix)
    print("\nUpload the two social/ cards to each repo under Settings -> Social preview,")
    print("and use the same files as LinkedIn Featured thumbnails.")


if __name__ == "__main__":
    main()
