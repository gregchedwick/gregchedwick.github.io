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

# 4:5 crop against the 1056x976 master, using the full height of the source.
#
# The top edge sits at row 0 on purpose. The master itself already clips the top
# of his hair — row 0 carries ~276 hair pixels across x 347-622 — so this is as
# much hair as the photograph contains; there is nothing above it to recover.
#
# Horizontally the box is centred on the head, which spans x 153-802, leaving
# 66px of backdrop on the left and 65px on the right. Taking the full height
# does put the eye line at ~46% rather than the more conventional 40%, which is
# the trade for keeping the hair intact.
#
# Aspect must remain 4:5 to match the frame in Hero.astro.
CROP_BOX = (87, 0, 867, 976)


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
