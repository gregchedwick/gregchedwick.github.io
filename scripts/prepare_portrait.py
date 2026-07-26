"""Build src/assets/portrait.jpeg from the untouched master photo.

Run from the site repo root:

    python scripts/prepare_portrait.py

This is a crop and nothing else. The master is already evenly lit with a
charcoal jacket and a neutral backdrop, so no colour work is needed — an
earlier headshot required temple-cast correction and a garment recolour, and
that code is gone rather than left lying around unused. Recover it from git
history if a future photo ever needs it.

The crop is deliberately NOT upscaled: the master is 1056x976, so a 4:5 crop
tops out around 725x907. Astro generates 320/480/640-wide variants from this
file, all of which are downscales — resampling up to a rounder number here
would just soften the result.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

SITE_ROOT = Path(__file__).resolve().parents[1]
MASTER = Path.home() / "OneDrive" / "Pictures" / "Greg.jpg"
OUT = SITE_ROOT / "src" / "assets" / "portrait.jpeg"

# 4:5 crop chosen by inspection against the 1056x976 master: eyes land just
# above the 42% line, the head keeps its margins, and the jacket stays in frame
# at the bottom left. Aspect must remain 4:5 to match the frame in Hero.astro.
CROP_BOX = (102, 68, 827, 975)


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"Master photo not found at {MASTER}")

    master = Image.open(MASTER).convert("RGB")
    out = master.crop(CROP_BOX)

    width, height = out.size
    ratio = width / height
    if abs(ratio - 0.8) > 0.005:
        raise SystemExit(f"Crop is {ratio:.3f}, expected 4:5 (0.800)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, quality=92, optimize=True, subsampling=1)
    print(f"Wrote {OUT.relative_to(SITE_ROOT)} — {width}x{height}, "
          f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
