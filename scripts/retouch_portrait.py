"""Build src/assets/portrait.jpeg from the untouched master photo.

Everything done to the portrait lives here, so the asset is reproducible and the
master is never modified in place. Run from the site repo root:

    python scripts/retouch_portrait.py

Steps, in order:
  1. Crop to 4:5, framing the eyes on the 40% line
  2. Even out the shadow falloff on the left temple (viewer's right)
  3. Recolour the white shirt collar to charcoal
  4. Downsample to 1280x1600 and save

Work happens at crop resolution and is downsampled last — that keeps mask edges
from showing.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

SITE_ROOT = Path(__file__).resolve().parents[1]
MASTER = Path.home() / "OneDrive" / "Pictures" / "Greg 3.jpeg"
OUT = SITE_ROOT / "src" / "assets" / "portrait.jpeg"

# Chosen by inspection against the 3000x2760 master: puts the eyes on the 40%
# line and centres the face left-to-right.
CROP_BOX = (406, 250, 2414, 2760)
FINAL_SIZE = (1280, 1600)

# Charcoal the collar is mapped to. Slightly cool so it sits with the palette.
CHARCOAL_LOW = 0.20   # deepest fold
CHARCOAL_HIGH = 0.37  # brightest highlight
CHARCOAL_TINT = np.array([0.94, 0.97, 1.00])


def to_hsv_parts(rgb: np.ndarray):
    """Value, saturation, and blue-minus-red, all from one pass."""
    value = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    saturation = np.where(value > 0, (value - minimum) / np.maximum(value, 1e-6), 0.0)
    coolness = rgb[:, :, 2] - rgb[:, :, 0]
    return value, saturation, coolness


def feather(mask: np.ndarray, radius: float) -> np.ndarray:
    """Soften a hard 0/1 mask so edits blend instead of showing a seam."""
    img = Image.fromarray((mask * 255).astype(np.uint8), mode="L")
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0


def soften_temple_shadow(rgb: np.ndarray) -> np.ndarray:
    """Lift the shadow falloff across the left temple.

    Only a partial lift: the darkening is partly real form shading, and flattening
    it completely reads as obviously retouched. This closes most of the gap to the
    surrounding skin and evens out the mottling, leaving the modelling intact.
    """
    height, width, _ = rgb.shape
    value, _, coolness = to_hsv_parts(rgb)

    # Soft ellipse over the shaded temple.
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    cx, cy = width * 0.797, height * 0.237
    rx, ry = width * 0.205, height * 0.155
    dist = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    region = np.clip(1.0 - dist, 0.0, 1.0)
    region = region * region * (3.0 - 2.0 * region)  # smoothstep

    # Skin only — warm pixels. Keeps the lift off the grey background and hair.
    skin = ((coolness < -0.02) & (value > 0.35)).astype(np.float32)
    mask = feather(region * skin, radius=width * 0.02)

    # Reference: well-lit forehead on the other side of the same face.
    ref = rgb[int(height * 0.16):int(height * 0.28), int(width * 0.34):int(width * 0.52)]
    ref_value = float(np.median(ref.max(axis=2)))

    target_value = np.median(value[mask > 0.5]) if (mask > 0.5).any() else ref_value
    lift = (ref_value - target_value) * 0.6
    if lift <= 0:
        return rgb

    # Flatten the blotchiness slightly, then blend both changes through the mask.
    blurred = np.asarray(
        Image.fromarray((rgb * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(width * 0.012)
        ),
        dtype=np.float32,
    ) / 255.0
    evened = rgb * 0.72 + blurred * 0.28

    out = evened + lift * mask[:, :, None]
    return np.clip(rgb * (1 - mask[:, :, None]) + out * mask[:, :, None], 0.0, 1.0)


def recolour_collar(rgb: np.ndarray) -> np.ndarray:
    """Map the white shirt to charcoal, preserving folds and fabric texture."""
    height, width, _ = rgb.shape
    value, saturation, coolness = to_hsv_parts(rgb)

    # The shirt is the only thing in frame that is bright AND neutral: background
    # is darker and bluish (b-r >= +0.047), skin is warm (b-r negative).
    is_shirt = (value > 0.85) & (saturation < 0.05) & (np.abs(coolness) < 0.031)

    # Restricted to the bottom of the frame so teeth — also bright and neutral —
    # are never caught.
    band = np.zeros((height, width), dtype=bool)
    band[int(height * 0.60):, :] = True
    is_shirt &= band

    if not is_shirt.any():
        return rgb

    # Morphological close. Specular highlights on the fabric blow out past the
    # neutrality test and leave pinholes in the mask, which show up as white
    # speckles in the recoloured collar. Dilate then erode fills them without
    # moving the outer edge.
    solid = Image.fromarray((is_shirt * 255).astype(np.uint8), mode="L")
    solid = solid.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    is_shirt = np.asarray(solid, dtype=np.float32) / 255.0 > 0.5

    mask = feather(is_shirt.astype(np.float32), radius=max(1.0, width * 0.0022))

    # Normalise the shirt's own tonal range, then remap onto charcoal so folds
    # and shadows survive the change.
    low, high = np.percentile(value[is_shirt], [2, 98])
    t = np.clip((value - low) / max(high - low, 1e-6), 0.0, 1.0)
    mapped = CHARCOAL_LOW + t * (CHARCOAL_HIGH - CHARCOAL_LOW)

    # Re-add fine detail the tonal remap flattens (weave, stitching).
    blurred_v = np.asarray(
        Image.fromarray((value * 255).astype(np.uint8), mode="L").filter(
            ImageFilter.GaussianBlur(max(1.0, width * 0.004))
        ),
        dtype=np.float32,
    ) / 255.0
    mapped = np.clip(mapped + (value - blurred_v) * 0.55, 0.0, 1.0)

    charcoal = mapped[:, :, None] * CHARCOAL_TINT[None, None, :]
    return np.clip(rgb * (1 - mask[:, :, None]) + charcoal * mask[:, :, None], 0.0, 1.0)


def build() -> Image.Image:
    master = Image.open(MASTER).convert("RGB")
    cropped = master.crop(CROP_BOX)

    rgb = np.asarray(cropped, dtype=np.float32) / 255.0
    rgb = soften_temple_shadow(rgb)
    rgb = recolour_collar(rgb)

    edited = Image.fromarray((rgb * 255.0 + 0.5).astype(np.uint8), mode="RGB")
    return edited.resize(FINAL_SIZE, Image.LANCZOS)


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"Master photo not found at {MASTER}")

    out = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, quality=90, optimize=True, subsampling=1)
    print(f"Wrote {OUT.relative_to(SITE_ROOT)} — {out.size[0]}x{out.size[1]}, "
          f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
