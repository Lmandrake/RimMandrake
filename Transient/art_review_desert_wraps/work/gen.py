#!/usr/bin/env python3
"""Generate desert-wrap + devolved-head candidates via codex imagegen.

ORIGINAL ART: every prompt below is written from the WRITTEN design capture
(design/Jawa/desert_wraps_design_capture.md). No third-party image is passed
as an input to any call.
"""
import subprocess, sys, os, time
from pathlib import Path

ROOT = Path("/mnt/d/Luke/dev/Rimworld")
OUT = ROOT / "Transient/art_review_desert_wraps/raw"
OUT.mkdir(parents=True, exist_ok=True)
CODEX = ROOT / "skills/generating-images/scripts/codex_image.py"

BODY_STYLE = (
    "A single video-game sprite asset for a top-down colony-sim game, drawn as flat "
    "vector clip art. Viewed from directly overhead at a steep top-down pawn camera "
    "angle, so the figure reads as a compact rounded mass of shoulders and torso seen "
    "from above and slightly in front. NO HEAD, no face, no hair, no feet, no ground, "
    "no shadow cast on the ground, no scenery, no text, no border, no frame. "
    "The subject is centred and fills most of the image with a small even margin. "
    "Every pixel not covered by the subject is a perfectly flat uniform pure magenta "
    "#FF00FF, right out to all four edges. "
    "RENDERING STYLE, follow exactly: absolutely flat 2D vector illustration. One "
    "thick solid pure-black outer contour stroke of even weight traces the entire "
    "outer silhouette. Inside that contour, a smooth soft radial value gradient runs "
    "from a light grey highlight near the upper centre out to darker grey toward the "
    "edges. STRICTLY ACHROMATIC: every pixel of the subject is neutral grey with red, "
    "green and blue exactly equal - no tan, no beige, no warmth, no tint, no colour of "
    "any kind anywhere on the garment. No photographic texture, no fabric weave, no "
    "canvas grain, no noise, no speckle, no cross-hatching, no paper texture. "
    "Every element of the drawing terminates flush inside the outer contour; nothing "
    "projects past the silhouette. "
)

HEAD_STYLE = (
    "A single video-game sprite asset for a top-down colony-sim game: a bare humanoid "
    "head, front-facing, drawn as flat vector clip art. Viewed from a steep top-down "
    "pawn camera angle so the head is seen from slightly above and in front. "
    "NO neck, no shoulders, no body, no hair, no ears, no nose, no mouth, no teeth, "
    "no mask, no goggles, no helmet, no hood, no wrapping, no jewellery, no ground, "
    "no shadow cast on the ground, no scenery, no text, no border, no frame. "
    "The head is centred and fills most of the image with a small even margin. "
    "Every pixel not covered by the head is a perfectly flat uniform pure magenta "
    "#FF00FF, right out to all four edges. "
    "RENDERING STYLE, follow exactly: absolutely flat 2D vector illustration. One "
    "thick solid pure-black outer contour stroke of even weight traces the entire "
    "head silhouette. Inside it, a smooth soft radial value gradient runs from a light "
    "grey highlight near the upper centre out to darker grey toward the edges. "
    "STRICTLY ACHROMATIC: every pixel is neutral grey with red, green and blue exactly "
    "equal - no skin tone, no warmth, no tint, no colour of any kind. No photographic "
    "texture, no pores, no noise, no grain, no cross-hatching. "
)

JOBS = {
"wrap_A_bound": BODY_STYLE + (
    "SUBJECT: a desert nomad's full-body cloth wrap garment, worn on a body, in a "
    "deliberately sparse and minimal treatment. The silhouette is ONE continuous "
    "rounded bucket - a wide, softly rounded shoulder line across the top, narrowing "
    "smoothly and symmetrically to a broad rounded hem at the bottom, taller than it "
    "is wide. The arms are wrapped into the same continuous mass, so no limb is "
    "separated out and no hands are visible. SURFACE: exactly three thin mid-grey "
    "stroked seam lines, each a single smooth curve, sweep diagonally across the wrap "
    "and converge on one point about one third up from the bottom of the silhouette, "
    "reading as wrap bands spiralling around the body and cinching low at the hip. "
    "Nothing else at all: no belt, no buckle, no strap, no fringe, no stitching, no "
    "patch, no pattern, no fold lines, no highlights other than the base gradient."),

"wrap_B_coil": BODY_STYLE + (
    "SUBJECT: a desert nomad's full-body cloth wrap garment, worn on a body, in a dense "
    "tightly-wound treatment. OUTER SILHOUETTE, this is critical: ONE WIDE ROUNDED "
    "BUCKET. Broad rounded shoulders across the top, sides that bulge gently OUTWARD in "
    "a smooth convex curve and taper only slightly toward a broad rounded hem at the "
    "bottom. Proportion is about four units wide to five units tall - a stocky barrel, "
    "not a slim column. There is absolutely NO pinched waist, NO hourglass, NO figure-of-"
    "eight, NO spool shape; neither side of the outline ever curves inward. The arms are "
    "wrapped into the same continuous mass. SURFACE: the whole body is wound in eleven or "
    "twelve TIGHT parallel wrap bands that spiral continuously around the torso from the "
    "shoulders down to the hem, like a bandage roll wound around a body. Each band is "
    "separated from the next by a thin dark grey seam line and carries its own gentle "
    "light-to-dark shading across its width so it reads as a rounded ridge of cloth. The "
    "bands crowd closer together and narrow toward a convergence point about one third up "
    "from the bottom. The bands lie flat against the body and never bulge the outer "
    "silhouette in or out. No belt, no buckle, no fringe, no patch."),

"wrap_C_cowl": BODY_STYLE + (
    "SUBJECT: a desert nomad's layered cloth wrap garment, worn on a body, built as TWO "
    "clearly separate garment layers. UPPER LAYER: a broad rounded shoulder mantle or "
    "cowl of heavy cloth covering both shoulders and the upper third of the torso, drawn "
    "with its OWN thick black outlined hem cutting a shallow scalloped curve across the "
    "chest, with a soft dark grey shadow immediately beneath that hem where it overhangs "
    "the layer below; a raised cowl collar rises as a rounded hump at the top centre of "
    "the silhouette behind the shoulders. LOWER LAYER: beneath the mantle the under-wrap "
    "continues down to a broad rounded hem, carrying three thin mid-grey stroked seam "
    "lines that converge on a point about one third up from the bottom. The overall "
    "silhouette is noticeably wider and squarer across the shoulders than at the hem, a "
    "clear trapezoid rather than a smooth bucket. No buckle, no fringe, no pattern."),

"wrap_D_weathered": BODY_STYLE + (
    "SUBJECT: a desert nomad's full-body cloth wrap garment, worn on a body, heavily "
    "weathered and field-repaired. The silhouette is a rounded bucket - wide rounded "
    "shoulders narrowing to the hem - but the BOTTOM HEM IS RAGGED: four short torn "
    "tongues of cloth and frayed notches interrupt the bottom edge, each still traced by "
    "the same thick black contour. SURFACE: five wrap bands of uneven width cross the "
    "torso and converge about one third up from the bottom; one band has partly unwound "
    "and its loose end curls away across the chest as a separate outlined strip that "
    "still stays entirely inside the silhouette. Two or three small patches of slightly "
    "lighter grey mark where the cloth has been rubbed thin, and one darker grey repair "
    "panel sits across the flank, its edge marked by a short dashed line of stitch "
    "marks. No buckle, no pattern, no colour."),

"head_H1_pot": HEAD_STYLE + (
    "SUBJECT: a blunt, primitive, devolved humanoid skull, front view. SILHOUETTE: a "
    "pot or bucket shape, slightly taller than it is wide. The crown is FLAT and SQUARED "
    "straight across the very top with only a short tight arc at each top corner; from "
    "there the sides run almost perfectly straight down - the cranium is exactly as wide "
    "as the mid-face - through the upper two thirds of the head; then the outline "
    "narrows abruptly in one short curve into a small blunt jaw at the very bottom. This "
    "is emphatically NOT an egg or oval. EYES: two plain solid dark-grey filled circles, "
    "small, set wide apart in the upper middle of the face - no eyelid, no eyelash, no "
    "brow mark, no pupil, no white, no highlight, just two flat dots. Below the eyes the "
    "face is completely blank except for ONE broad soft darker-grey shadow mass filling "
    "the lower third of the head, about a third of the head's width and centred, reading "
    "as a heavy fused jowl rather than a modelled chin."),

"head_H2_browridge": HEAD_STYLE + (
    "SUBJECT: a BARE primitive devolved humanoid SKULL, front view, nothing worn on it. "
    "There is no hat, no cap, no brim, no hood, no helmet, no headband and no separate "
    "object of any kind resting on the head - the heavy brow described below is BONE, "
    "continuous with the skull itself, with no gap, seam, rim or outline separating it "
    "from the cranium above it. SILHOUETTE: a downward-widening wedge, the inverse of an "
    "egg. The cranium is LOW, NARROW and SHORT and slopes backward; the outline then "
    "swells outward at brow height into a heavy bony ridge, and continues widening below "
    "into a blunt, wide, massive lower face, finishing on a wide gently-curved blunt "
    "bottom edge with no pointed chin at all. The whole outline is one single unbroken "
    "black contour from crown to jaw with no internal object boundaries crossing it. "
    "EYES: two small solid dark-grey filled dots set deep and close together beneath the "
    "brow swell - no eyelid, no brow mark, no pupil, no white, no highlight. A soft broad "
    "band of darker grey shading lies horizontally across the eyes where the bony ridge "
    "overhangs them. Below that band the lower face is completely blank."),
}


def run(name, prompt, attempts=3, timeout=240):
    dest = OUT / f"{name}.png"
    for i in range(1, attempts + 1):
        t0 = time.time()
        cmd = [sys.executable, str(CODEX), "generate", "--out", str(dest),
               "--prompt", prompt, "--timeout", str(timeout), "--force"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        el = time.time() - t0
        if dest.exists() and dest.stat().st_size > 20000:
            print(f"OK   {name}  {el:.0f}s  {dest.stat().st_size//1024}KB", flush=True)
            return True
        print(f"FAIL {name} attempt {i}  {el:.0f}s  rc={p.returncode} "
              f"{(p.stderr or p.stdout)[-200:].strip()}", flush=True)
    return False


if __name__ == "__main__":
    want = sys.argv[1:] or list(JOBS)
    bad = [n for n in want if not run(n, JOBS[n])]
    print("MISSING:", bad if bad else "none")
