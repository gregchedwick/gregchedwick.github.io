"""Build src/assets/portrait.jpeg from the untouched master photo.

Everything done to the portrait lives here, so the asset is reproducible and the
master is never modified in place. Run from the site repo root:

    python scripts/retouch_portrait.py

Steps, in order:
  1. Crop to 4:5, framing the eyes on the 40% line
  2. Colour-match the olive cast on the left temple to the surrounding skin
  3. Recolour the shirt and jacket to charcoal
  4. Downsample to 1280x1600 and save

Work happens at crop resolution and is downsampled last — that keeps mask edges
from showing.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SITE_ROOT = Path(__file__).resolve().parents[1]
MASTER = Path.home() / "OneDrive" / "Pictures" / "Greg 3.jpeg"
OUT = SITE_ROOT / "src" / "assets" / "portrait.jpeg"

# Chosen by inspection against the 3000x2760 master: puts the eyes on the 40%
# line and centres the face left-to-right.
CROP_BOX = (406, 250, 2414, 2760)
FINAL_SIZE = (1280, 1600)

# Charcoal the garment is mapped to, as a value range: deep folds to highlights.
CHARCOAL_LOW = 0.13
CHARCOAL_HIGH = 0.42
CHARCOAL_TINT = np.array([0.95, 0.97, 1.00])

# Hue correction is applied nearly in full — the olive tint is what reads as
# wrong. Brightness is only nudged: the temple really is turned away from the
# light, and matching it to the lit side puts a glow on the side of his head.
CAST_HUE_STRENGTH = 0.92
CAST_LUMA_STRENGTH = 0.70

LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def channels(rgb: np.ndarray):
    """Value, saturation, and blue-minus-red, from one pass."""
    value = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    saturation = np.where(value > 0, (value - minimum) / np.maximum(value, 1e-6), 0.0)
    return value, saturation, rgb[:, :, 2] - rgb[:, :, 0]


def blur(arr: np.ndarray, radius: float) -> np.ndarray:
    """Gaussian blur that round-trips float arrays of 1 or 3 channels."""
    mode = "L" if arr.ndim == 2 else "RGB"
    img = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8), mode=mode)
    out = np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0
    return out


def skin_mask(rgb: np.ndarray) -> np.ndarray:
    value, _, coolness = channels(rgb)
    return (coolness < -0.015) & (value > 0.30)


def match_temple_cast(rgb: np.ndarray) -> np.ndarray:
    """Neutralise the olive cast across the forehead.

    The patch on the left temple is not merely darker than the rest of the
    forehead — it is a different hue, olive against pink. A brightness lift
    leaves the cast in place, which is why this is a per-channel correction.

    The correction is a smooth gain field: the low-frequency colour of the
    forehead is pushed toward the colour of the well-lit side. Because the field
    is smooth and multiplicative, skin texture survives untouched, and where the
    tone already matches the reference the gain is ~1 and nothing happens. That
    makes it safe to apply across the whole forehead rather than inside a
    hand-placed ellipse.
    """
    height, width, _ = rgb.shape
    skin = skin_mask(rgb).astype(np.float32)

    # Local average colour of SKIN ONLY. A plain blur pulls dark hair into the
    # average near the hairline, which sends the gain sky-high and paints an
    # orange band across the brow — normalising by the blurred mask keeps hair
    # and backdrop out of the estimate entirely.
    radius = width * 0.05
    weight = blur(skin, radius)
    low = blur(rgb * skin[:, :, None], radius) / np.maximum(weight, 1e-3)[:, :, None]

    # Reference: the evenly lit forehead on the viewer's left, clear of the cast.
    ref_box = (
        slice(int(height * 0.14), int(height * 0.30)),
        slice(int(width * 0.30), int(width * 0.50)),
    )
    ref_skin = skin[ref_box] > 0.5
    if ref_skin.sum() < 500:
        return rgb
    reference = np.median(low[ref_box][ref_skin], axis=0)

    # Vertical window over the forehead, easing to zero at the brows and hairline
    # so the correction never ends on a visible line.
    rows = np.arange(height, dtype=np.float32)
    window = np.clip((rows - height * 0.06) / (height * 0.06), 0, 1) * np.clip(
        (height * 0.42 - rows) / (height * 0.09), 0, 1
    )
    # Soften inside the region, then gate hard on skin again so the correction
    # cannot bleed past the hairline.
    region = (blur(window[:, None] * skin, width * 0.008) * skin)[:, :, None]

    # Split the correction into hue and brightness so they can be dialled
    # separately. Ratios are taken against local luma, which makes them describe
    # tint alone, independent of how dark the area is.
    ref_luma = float(reference @ LUMA)
    ref_tint = reference / max(ref_luma, 1e-3)

    low_luma = np.maximum(low @ LUMA, 1e-3)[:, :, None]
    low_tint = np.maximum(low / low_luma, 1e-3)
    tint_gain = np.clip(ref_tint[None, None, :] / low_tint, 0.88, 1.14)

    corrected = rgb * (1.0 + (tint_gain - 1.0) * CAST_HUE_STRENGTH * region)

    # Hue change alone must not move brightness, so renormalise to the original
    # luma, then apply the small deliberate lift on top.
    before = np.maximum(rgb @ LUMA, 1e-4)
    after = np.maximum(corrected @ LUMA, 1e-4)
    corrected *= (before / after)[:, :, None]

    luma_gain = np.clip(ref_luma / np.maximum(low @ LUMA, 1e-3), 0.92, 1.22)[:, :, None]
    corrected *= 1.0 + (luma_gain - 1.0) * CAST_LUMA_STRENGTH * region

    return np.clip(corrected, 0.0, 1.0)


def garment_mask(rgb: np.ndarray) -> np.ndarray:
    """Everything the subject is wearing, as a boolean mask.

    Three-way split by hue: skin is warm (blue-red negative), the backdrop is
    cool, and the garment is the only neutral thing in frame. Brightness is
    deliberately not part of the test — the previous version keyed on it and
    dropped every shadowed fold and the whole second wedge below the far
    shoulder.

    Teeth and eye catchlights are neutral too, so the mask is then reduced to the
    components that reach the bottom edge of the frame. The garment does; a
    mouth in the middle of a face does not.
    """
    height, width, _ = rgb.shape
    _, _, coolness = channels(rgb)
    neutral = (coolness >= -0.015) & (coolness <= 0.035)

    # Bottom half only, as a cheap first cut before the connectivity pass.
    neutral[: int(height * 0.45), :] = False

    solid = Image.fromarray((neutral * 255).astype(np.uint8), mode="L")
    # Close small gaps so a fold shadow doesn't sever a region from the edge.
    solid = solid.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    filled = np.asarray(solid, dtype=np.uint8) > 127

    # Flood from every run of mask along the bottom edge; keep only what connects.
    # The .copy() is required: an image straight from Image.fromarray shares the
    # numpy buffer read-only, and ImageDraw.floodfill silently writes nothing.
    keep = Image.fromarray((filled * 255).astype(np.uint8), mode="L").copy()
    bottom = filled[-1, :]
    seeds: list[int] = []
    x = 0
    while x < width:
        if bottom[x]:
            start = x
            while x < width and bottom[x]:
                x += 1
            seeds.append((start + x - 1) // 2)
        else:
            x += 1

    for seed_x in seeds:
        ImageDraw.floodfill(keep, (int(seed_x), height - 1), 128)

    connected = np.asarray(keep, dtype=np.uint8) == 128
    return connected & filled


def recolour_garment(rgb: np.ndarray) -> np.ndarray:
    """Map the shirt and jacket to charcoal, preserving folds and fabric texture."""
    width = rgb.shape[1]
    value, _, _ = channels(rgb)
    is_garment = garment_mask(rgb)
    if not is_garment.any():
        return rgb

    mask = blur(is_garment.astype(np.float32), max(1.0, width * 0.0022))

    # Normalise the garment's own tonal range, then remap onto charcoal so folds
    # and shadows survive the change.
    low, high = np.percentile(value[is_garment], [2, 98])
    t = np.clip((value - low) / max(high - low, 1e-6), 0.0, 1.0)
    mapped = CHARCOAL_LOW + t * (CHARCOAL_HIGH - CHARCOAL_LOW)

    # Re-add the fine detail the tonal remap flattens (weave, stitching, edges).
    mapped = np.clip(mapped + (value - blur(value, max(1.0, width * 0.004))) * 0.55, 0.0, 1.0)

    charcoal = mapped[:, :, None] * CHARCOAL_TINT[None, None, :]
    return np.clip(rgb * (1 - mask[:, :, None]) + charcoal * mask[:, :, None], 0.0, 1.0)


def build() -> Image.Image:
    master = Image.open(MASTER).convert("RGB")
    rgb = np.asarray(master.crop(CROP_BOX), dtype=np.float32) / 255.0

    rgb = match_temple_cast(rgb)
    rgb = recolour_garment(rgb)

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
