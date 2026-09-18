#!/usr/bin/env python3
"""Full body-type x direction production matrix for DESERT_WRAPS_ART_COMMISSION_1.

ORIGINAL ART: every prompt is written from the WRITTEN design capture
(design/Jawa/desert_wraps_design_capture.md, prose+numbers only, no donor
pixels). No third-party image is passed as an input to any call.

Owner ruling 2026-09-10: all 4 wrap styles ship (A/B/C/D), both head shapes
ship as unwired StarWarsRaces options (H1/H2).

South-facing Male masters for all 6 subjects already exist and PASSED
validate_sprite against the candidate reference
(src/.../desert_wraps_candidates_2026-09-09/final/*.png) -- this script
covers everything else: the other 4 body types x 3 directions for each wrap
style (Female/Fat/Hulk/Thin), Male north/east, and head north/east (heads are
not body-type-scoped -- Male and Female HeadTypeDefs share art per the
design capture's own measurement of ~1% variance, so only 3 directions per
head style are generated, then duplicated for both genders when built into
the mod).
"""
import subprocess, sys, time
from pathlib import Path

ROOT = Path("/mnt/d/Luke/dev/Rimworld")
OUT = ROOT / "Transient/art_review_desert_wraps/matrix_raw"
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
    "head, drawn as flat vector clip art. Viewed from a steep top-down pawn camera "
    "angle so the head is seen from slightly above. "
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

# --- body-type silhouette modifiers, from design capture SS1.3 -------------
BODYTYPE_SIL = {
    "Male": (
        "BODY-TYPE SILHOUETTE: a rounded-shoulder, tapered-waist bucket outline - a "
        "wide, flat-ish top at the shoulders narrowing smoothly to a rounded bottom "
        "edge. This is the baseline proportion, average width and height."
    ),
    "Female": (
        "BODY-TYPE SILHOUETTE: the same bucket family but visibly WAISTED - the "
        "outline pinches inward around the vertical midpoint before flaring slightly "
        "again lower, giving a two-lobe figure-8/gourd silhouette rather than a single "
        "smooth curve. Drawn noticeably taller and narrower overall than an average "
        "male build, with no chest or bust modelling - the waist pinch is the only "
        "shape cue."
    ),
    "Fat": (
        "BODY-TYPE SILHOUETTE: the bucket silhouette scaled outward isotropically - "
        "shoulders AND waist both bulge outward, corners are rounder, NO waist pinch "
        "at all. Roughly 30% wider than an average build, reading as a plain dome/"
        "sphere sitting on a slightly narrower base."
    ),
    "Hulk": (
        "BODY-TYPE SILHOUETTE: the tallest and widest build. A flatter, squarer "
        "roofline across the top with pronounced trapezoidal shoulders and a "
        "straighter, less-tapered drop to the waist than an average build - a big "
        "bruiser silhouette occupying nearly the full canvas height."
    ),
    "Thin": (
        "BODY-TYPE SILHOUETTE: a slim vertical ellipse, almost a stick - the "
        "narrowest waist of the whole set, roughly half the width of an average "
        "build, but drawn to nearly the SAME torso height - same torso length, much "
        "narrower shoulders and waist, not a uniformly shrunk copy."
    ),
}

# --- direction modifiers, from design capture SS1.5 -------------------------
DIR_BODY = {
    "south": (
        "VIEW: front view, the wearer facing the camera. The seam-line pattern is "
        "roughly bilaterally symmetric, converging toward a point about one third up "
        "from the bottom. Darkest gradient sits at the very top (shoulder shadow) and "
        "along the bottom edge."
    ),
    "north": (
        "VIEW: rear view, the wearer's back facing the camera, seen from behind - no "
        "face, no front-of-body details, this is the BACK of the wrapped torso. Near-"
        "mirror of the front silhouette, but the seam lines shift to emphasise ONE "
        "long diagonal band crossing from upper-left to lower-right, as if a single "
        "long wrap-strip crosses the back. The gradient's lightest point sits slightly "
        "higher and more centred than the front view."
    ),
    "east": (
        "VIEW: side profile view, the wearer facing sideways (their right, toward the "
        "viewer's right). The silhouette narrows and loses bilateral symmetry - "
        "introduce a small lean or hook to one side, a small notch or bulge on the "
        "trailing edge - and the seam-band lines run steeply diagonal, near 45 "
        "degrees, reading as wrapping seen edge-on rather than face-on."
    ),
}
DIR_HEAD = {
    "south": "VIEW: front view, the head facing the camera, eyes toward the viewer.",
    "north": (
        "VIEW: rear view, the BACK of the head facing the camera, seen from behind - "
        "NO eyes, no face, this is the back of the skull: smooth continuous curve of "
        "the cranium with the same flat/square-crown or wedge-shaped silhouette as the "
        "front view but with no facial features drawn at all, since none are visible "
        "from behind."
    ),
    "east": (
        "VIEW: side profile view, the head facing sideways (its right, toward the "
        "viewer's right) - the same silhouette proportions seen edge-on; one eye dot "
        "is visible near the front of the profile, the jaw-shadow/brow-ridge mass "
        "reads as a profile bulge rather than a centred patch."
    ),
}

WRAP_SUBJECT = {
    "wrap_A_bound": (
        "SUBJECT: a desert nomad's full-body cloth wrap garment, worn on a body, in a "
        "deliberately sparse and minimal treatment. The arms are wrapped into the same "
        "continuous mass, so no limb is separated out and no hands are visible. "
        "SURFACE: exactly three thin mid-grey stroked seam lines, each a single smooth "
        "curve, sweep diagonally across the wrap. Nothing else at all: no belt, no "
        "buckle, no strap, no fringe, no stitching, no patch, no pattern, no fold "
        "lines, no highlights other than the base gradient."
    ),
    "wrap_B_coil": (
        "SUBJECT: a desert nomad's full-body cloth wrap garment, worn on a body, in a "
        "dense tightly-wound treatment. There is absolutely NO pinched waist beyond "
        "what the body-type silhouette below specifies; the coil bands themselves "
        "never bulge the outer silhouette in or out. The arms are wrapped into the "
        "same continuous mass. SURFACE: the whole body is wound in eleven or twelve "
        "TIGHT parallel wrap bands that spiral continuously around the torso from the "
        "shoulders down to the hem, like a bandage roll wound around a body. Each band "
        "is separated from the next by a thin dark grey seam line and carries its own "
        "gentle light-to-dark shading across its width so it reads as a rounded ridge "
        "of cloth. No belt, no buckle, no fringe, no patch."
    ),
    "wrap_C_cowl": (
        "SUBJECT: a desert nomad's layered cloth wrap garment, worn on a body, built "
        "as TWO clearly separate garment layers. UPPER LAYER: a broad rounded "
        "shoulder mantle or cowl of heavy cloth covering both shoulders and the upper "
        "third of the torso, drawn with its OWN thick black outlined hem cutting a "
        "shallow scalloped curve across the chest, with a soft dark grey shadow "
        "immediately beneath that hem where it overhangs the layer below; a raised "
        "cowl collar rises as a rounded hump at the top centre of the silhouette "
        "behind the shoulders. LOWER LAYER: beneath the mantle the under-wrap "
        "continues down to the hem, carrying three thin mid-grey stroked seam lines. "
        "The mantle makes the upper silhouette noticeably wider and squarer across "
        "the shoulders than the body-type's usual line. No buckle, no fringe, no "
        "pattern."
    ),
    "wrap_D_weathered": (
        "SUBJECT: a desert nomad's full-body cloth wrap garment, worn on a body, "
        "heavily weathered and field-repaired. The BOTTOM HEM IS RAGGED: four short "
        "torn tongues of cloth and frayed notches interrupt the bottom edge, each "
        "still traced by the same thick black contour. SURFACE: five wrap bands of "
        "uneven width cross the torso; one band has partly unwound and its loose end "
        "curls away across the chest as a separate outlined strip that still stays "
        "entirely inside the silhouette. Two or three small patches of slightly "
        "lighter grey mark where the cloth has been rubbed thin, and one darker grey "
        "repair panel sits across the flank, its edge marked by a short dashed line "
        "of stitch marks. No buckle, no pattern, no colour."
    ),
}

HEAD_SUBJECT = {
    "head_H1_pot": (
        "SUBJECT: a blunt, primitive, devolved humanoid skull. SILHOUETTE: a pot or "
        "bucket shape, slightly taller than it is wide. The crown is FLAT and "
        "SQUARED straight across the very top with only a short tight arc at each "
        "top corner; from there the sides run almost perfectly straight down - the "
        "cranium is exactly as wide as the mid-face - through the upper two thirds "
        "of the head; then the outline narrows abruptly in one short curve into a "
        "small blunt jaw at the very bottom. This is emphatically NOT an egg or "
        "oval. Below the eye line the face is completely blank except for ONE broad "
        "soft darker-grey shadow mass filling the lower third of the head, about a "
        "third of the head's width and centred, reading as a heavy fused jowl rather "
        "than a modelled chin."
    ),
    "head_H2_browridge": (
        "SUBJECT: a BARE primitive devolved humanoid SKULL, nothing worn on it. "
        "There is no hat, no cap, no brim, no hood, no helmet, no headband and no "
        "separate object of any kind resting on the head - the heavy brow described "
        "below is BONE, continuous with the skull itself, with no gap, seam, rim or "
        "outline separating it from the cranium above it. SILHOUETTE: a "
        "downward-widening wedge, the inverse of an egg. The cranium is LOW, NARROW "
        "and SHORT and slopes backward; the outline then swells outward at brow "
        "height into a heavy bony ridge, and continues widening below into a blunt, "
        "wide, massive lower face, finishing on a wide gently-curved blunt bottom "
        "edge with no pointed chin at all. The whole outline is one single unbroken "
        "black contour from crown to jaw with no internal object boundaries crossing "
        "it. A soft broad band of darker grey shading lies horizontally across the "
        "eye area where the bony ridge overhangs it. Below that band the lower face "
        "is completely blank."
    ),
}
EYES_BY_DIR = {
    "south": (
        " EYES (front view only): two plain solid dark-grey filled circles, small, "
        "set wide apart in the upper middle of the face - no eyelid, no eyelash, no "
        "brow mark, no pupil, no white, no highlight, just two flat dots."
    ),
    "north": "",
    "east": (
        " EYE (profile view): one plain solid dark-grey filled dot near the front of "
        "the profile, no eyelid, no brow mark, no pupil, no white, no highlight."
    ),
}

BODY_TYPES = ["Male", "Female", "Fat", "Hulk", "Thin"]
DIRECTIONS = ["south", "north", "east"]


def wrap_jobs():
    jobs = {}
    for style, subj in WRAP_SUBJECT.items():
        for bt in BODY_TYPES:
            for d in DIRECTIONS:
                if bt == "Male" and d == "south":
                    continue  # already have the validated candidate master
                name = f"{style}__{bt}_{d}"
                jobs[name] = (BODY_STYLE + subj + " " + BODYTYPE_SIL[bt] + " "
                              + DIR_BODY[d])
    return jobs


def head_jobs():
    jobs = {}
    for style, subj in HEAD_SUBJECT.items():
        for d in DIRECTIONS:
            if d == "south":
                continue  # already have the validated candidate master
            name = f"{style}__{d}"
            jobs[name] = HEAD_STYLE + subj + " " + DIR_HEAD[d] + EYES_BY_DIR[d]
    return jobs


ALL_JOBS = {}
ALL_JOBS.update(wrap_jobs())
ALL_JOBS.update(head_jobs())


def run(name, prompt, attempts=3, timeout=180):
    dest = OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 20000:
        print(f"SKIP {name}  (already exists)", flush=True)
        return True
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
    want = sys.argv[1:] or list(ALL_JOBS)
    print(f"TOTAL JOBS: {len(want)}", flush=True)
    bad = [n for n in want if not run(n, ALL_JOBS[n])]
    print("MISSING:", bad if bad else "none")
