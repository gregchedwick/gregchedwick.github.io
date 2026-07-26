"""Trim the Netflix Ads Analytics output into a compact JSON payload for the website.

The processed CSV is only ~500 rows, so the whole ranked list can ship to the
browser and be filtered client-side — no API, no backend.

Run from the site repo root:
    python scripts/export_web_data.py

Reads from the sibling Netflix-Ads-Analytics repo and writes
src/data/netflix-ads.json. Re-run whenever the analysis is updated.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd

SITE_ROOT = Path(__file__).resolve().parents[1]
NETFLIX_REPO = SITE_ROOT.parent / "Netflix-Ads-Analytics"
FINAL_CSV = NETFLIX_REPO / "Data" / "Processed" / "netflix_ads_analytics_final.csv"
GENRES_CSV = NETFLIX_REPO / "Data" / "Processed" / "netflix_ads_genres_exploded.csv"
OUT_PATH = SITE_ROOT / "src" / "data" / "netflix-ads.json"

# Only titles that actually ranked carry an ad-inventory signal worth charting.
TOP_N_TITLES = 60
MIN_TITLES_PER_GENRE = 5


def clean(value, default=None):
    """pandas gives back NaN for blanks; JSON has no NaN."""
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    return value


def main() -> None:
    if not FINAL_CSV.exists():
        raise SystemExit(
            f"Could not find {FINAL_CSV}.\n"
            "Expected the Netflix-Ads-Analytics repo to sit alongside this one."
        )

    df = pd.read_csv(FINAL_CSV)
    df = df.sort_values("ad_opportunity_score", ascending=False)

    titles = []
    for _, row in df.head(TOP_N_TITLES).iterrows():
        titles.append(
            {
                "title": str(row["title"]).strip(),
                "year": int(clean(row.get("release_year"), 0)) or None,
                "score": round(float(row["ad_opportunity_score"]), 1),
                "hoursViewed": int(clean(row.get("total_hours_viewed"), 0)),
                "weeksInTop10": int(clean(row.get("weeks_in_top10"), 0)),
                "voteAverage": round(float(clean(row.get("vote_average"), 0)), 1) or None,
                "runtime": int(clean(row.get("duration_minutes"), 0)) or None,
                "rank": int(clean(row.get("overall_rank"), 0)) or None,
            }
        )

    # Genre aggregates come from the exploded table, where one row = one
    # title-genre pair, so a multi-genre title counts toward each of its genres.
    genres = []
    if GENRES_CSV.exists():
        gdf = pd.read_csv(GENRES_CSV)
        genre_col = "genres" if "genres" in gdf.columns else "genre"
        gdf = gdf[gdf[genre_col].notna() & gdf["ad_opportunity_score"].notna()]

        buckets: dict[str, list[float]] = defaultdict(list)
        hours: dict[str, list[float]] = defaultdict(list)
        weeks: dict[str, list[float]] = defaultdict(list)
        for _, row in gdf.iterrows():
            name = str(row[genre_col]).strip()
            if not name or name.lower() == "nan":
                continue
            buckets[name].append(float(row["ad_opportunity_score"]))
            hours[name].append(float(clean(row.get("total_hours_viewed"), 0)))
            weeks[name].append(float(clean(row.get("weeks_in_top10"), 0)))

        for name, scores in buckets.items():
            if len(scores) < MIN_TITLES_PER_GENRE:
                continue
            genres.append(
                {
                    "genre": name,
                    "avgScore": round(sum(scores) / len(scores), 1),
                    "titleCount": len(scores),
                    # Totals for hours, averages for weeks: hours measure the
                    # size of the inventory a genre represents, while weeks
                    # measure how long a typical title in it holds attention.
                    "totalHours": int(sum(hours[name])),
                    "avgWeeks": round(sum(weeks[name]) / len(weeks[name]), 1),
                }
            )
        genres.sort(key=lambda g: g["avgScore"], reverse=True)

    # Per-title genre tags, so the chart can filter without a second request.
    if GENRES_CSV.exists():
        tag_map: dict[str, set[str]] = defaultdict(set)
        for _, row in gdf.iterrows():
            tag_map[str(row["title"]).strip()].add(str(row[genre_col]).strip())
        for entry in titles:
            entry["genres"] = sorted(tag_map.get(entry["title"], []))
    else:
        for entry in titles:
            entry["genres"] = []

    # Most 2025–26 chart-toppers postdate the metadata catalog they'd join
    # against, so they carry no genre tags. Surfacing that number beats
    # quietly shipping a genre filter that hides two-thirds of the titles.
    tagged = sum(1 for entry in titles if entry["genres"])

    payload = {
        "generated": pd.Timestamp.now("UTC").strftime("%Y-%m-%d"),
        "titleCount": int(len(df)),
        "genreCoverage": {"tagged": tagged, "total": len(titles)},
        "titles": titles,
        "genres": genres,
        # The weighting model behind the score. Percentages are the midpoints of
        # the ranges documented in the project README.
        "weights": [
            {"component": "Total hours viewed", "weight": 75, "rationale": "Strongest predictor of ad inventory value"},
            {"component": "Weeks in Top 10", "weight": 13, "rationale": "Measures sustained cultural relevance"},
            {"component": "Vote average", "weight": 8, "rationale": "Higher-rated titles hold attention longer"},
            {"component": "Release year", "weight": 4, "rationale": "Newer content attracts more viewers"},
        ],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUT_PATH.relative_to(SITE_ROOT)} — {len(titles)} titles, "
          f"{len(payload['genres'])} genres, {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
