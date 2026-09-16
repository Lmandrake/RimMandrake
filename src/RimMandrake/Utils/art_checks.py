#!/usr/bin/env python3
"""Deterministic pixel checks on sprite art. No ML, no vision model, no score.

Five checks, each emitting structured Findings. Severity is DATA: this module never
decides whether a finding rejects a sprite, and never aggregates findings into a
number. The owner killed a scoring gate once; the caller rules.

    python3 src/RimMandrake/Utils/art_checks.py <dir-or-file>... [--json]
    python3 src/RimMandrake/Utils/art_checks.py --selftest

🔴 Measure the VISIBLE silhouette, never the raw alpha bounding box. Pillow's
getbbox() counts any nonzero alpha, and this art carries a haze of alpha 1..16
(6% opacity, invisible at game draw size). FurnaceBeast_east.png holds 3901 such
pixels: its raw bbox is 460 px tall, its visible body 286 px. Every bbox in here
goes through visible_bbox().
"""
import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

REPO_ROOT = Path(__file__).resolve().parents[3]

# An alpha at or below this is invisible at the size the game draws a pawn, so it is
# not silhouette. MEASURED: raising the floor from 0 to 16 moves FurnaceBeast_east's
# bbox height from 460 px to 286 px — the 174 px difference is entirely alpha 1..16.
# Anything in 8..32 gives the same answer on all 57 Pyrelands facings; 16 is the middle.
ALPHA_VISIBLE = 16

# RGB under low alpha is undefined — exporters leave it black or leave it garbage.
# Only sample COLOUR where the pixel was actually painted. GUESS: 100/255 is a
# comfortable "really painted" line, not a measured one.
ALPHA_SOLID = 100

# transparency_real -------------------------------------------------------------
# A PNG whose alpha is essentially all-255 has no cutout at all — the subject is
# baked onto a matte. Not 1.0 exactly: a stray non-opaque pixel should not excuse it.
OPAQUE_ALPHA_FRAC = 0.995
# A matte often survives as an opaque ring on the canvas border even when the middle
# was cut out. GUESS at the fraction; any solid ring at all is suspicious.
BORDER_OPAQUE_FRAC = 0.90
# Border pixels this close together in each channel read as one flat colour.
BORDER_FLAT_TOL = 8
# Luminance bands that say "this matte is white paper" / "this matte is black".
# GUESS: eyeballed bands, no measurement behind them — no baked matte exists in the
# Pyrelands corpus to calibrate against (0 of 57 files trip this check).
MATTE_LUM_WHITE = 235
MATTE_LUM_BLACK = 20
# Sub-visible alpha dust (pixels in 1..ALPHA_VISIBLE) is UNIVERSAL in this painterly
# art: 52 of 71 Pyrelands files carry some, so a bare count flags almost everything and
# says nothing. Only the dust that DISPLACES the silhouette is a defect — it silently
# inflates every raw bbox downstream, which is exactly how FurnaceBeast's height
# mismatch got recorded as 1.03x. So the trigger is how far the raw-alpha bbox exceeds
# the visible one, as a fraction of canvas.
#
# GUESS at 2%, and a weak one: the measured spread over the corpus is CONTINUOUS
# (0.023, 0.031, 0.039, 0.041, 0.066, 0.094, 0.109, ... 0.422) with no gap to cut at,
# so no threshold here separates anything — it only sets how loud the check is. 2%
# flags 13 of 19 creature rows, 10% flags 8. That high rate is not the check
# misfiring: the ghost layer is a defect of the EXPORT PIPELINE, present across the
# whole wave, so it should be fixed there rather than triaged per sprite.
DUST_BBOX_SLACK_FRAC = 0.02

# boundaries_respected ---------------------------------------------------------
# Zero margin means the drawing is cut off by the canvas, not merely close to it.
MARGIN_TOUCH_PX = 0
# GUESS: 1% of the canvas (2 px at 256, 5 px at 512) as the "sane margin" floor.
# Advisory only — several accepted Pyrelands sprites sit at 1-2 px deliberately.
MARGIN_ADVISE_FRAC = 0.01

# facing_height_consistency ---------------------------------------------------
# An animal's HEIGHT does not change with viewing angle; its width legitimately does.
# So compare bbox height alone — never sqrt(w*h) and never area, both of which
# conflate aspect with scale and fire on every quadruped.
#
# GUESS at 1.35, informed but NOT settled by the corpus. On visible-alpha heights the
# owner-confirmed break (Anooba, "North is HUGE compared to east") measures 1.885 and
# the tightest accepted row (Nuna_f) 1.012 — but FurnaceBeast, which the owner kept,
# measures 1.636 and so is flagged here. See selftest()'s HEIGHT_CONFLICT: that row's
# "1.03x good" label came from the raw-bbox dust, and its real east/north mismatch is
# larger than four rows that were called bad. Only the owner can settle where the line
# goes; this constant is the one place to move it.
FACING_HEIGHT_MAX_RATIO = 1.35

# North and south are FRONT and REAR views (owner ruling 2026-09-15), which on a
# bilaterally symmetric animal makes them near-symmetric about the vertical axis.
# East/west are profiles and must NOT be. Bounds are real observations, not taste:
# Anooba's south scores 0.64 and the owner rejected it ("South isn't south"), while
# GreenGoo scores 0.89 and he praised it. 0.80 sits in that gap. Donor art that
# obeys the convention clusters 0.96-1.00.
SYMMETRY_MIN_NS = 0.80
# 🔴 KNOWN FALSE NEGATIVE, measured 2026-09-15. `Gizka_north.png` scores 0.845 —
# it PASSES this bound — and is an unmistakable side profile of a lizard facing
# right, one eye visible. Confirmed by looking, and a visual LLM judge returned
# NO with the correct reason in 17.8s. A blobby profile is symmetric by accident,
# so no value of this constant separates the two cases; raising it to 0.85 only
# starts failing genuinely round animals. Treat this check as evidence that
# north/south is WRONG, never as evidence that it is RIGHT. The defect class is
# ARTPIPE_FACING_COHERENCE_1; the instrument that catches it is a visual judge
# (design/RimMandrake/north_star_validation_spec.md §4a).
# A profile that reads as symmetric is not a profile. Weaker evidence than the
# north/south bound — no owner-confirmed case either way — so it is medium, and
# the threshold is set high to avoid punishing a genuinely round animal.
SYMMETRY_MAX_EW = 0.85

# outline_coherence -----------------------------------------------------------
# Luminance at or below this reads as a keyline against this art's midtones.
# GUESS: 90/255. Measured effect: 54 of 57 Pyrelands facings score 1.000 at this
# value, so it is not firing indiscriminately.
KEYLINE_DARK_LUM = 90
# How far inside the silhouette edge to look for the keyline, in px. A painterly
# keyline is a few px thick and sits under a soft alpha ramp, so a 1 px probe misses it.
KEYLINE_INSET_PX = 3
# GUESS: 95% of the silhouette edge must carry a keyline.
KEYLINE_MIN_FRAC = 0.95
# A single long break reads worse than the same total spread thinly, so it gets its
# own threshold: 2% of the silhouette perimeter. GUESS.
KEYLINE_MAX_GAP_FRAC = 0.02

FACING_RE = re.compile(r"^(?P<base>.+)_(?P<facing>east|west|north|south)$")
# Variants of one creature for duplicate purposes only. `_f`/`_m` are the sex splits;
# a trailing bare `W` (GizkaW) is merged ONLY when the stripped name is itself a
# creature in the same batch and directory, so this cannot invent a pairing.
SEX_SUFFIXES = ("_f", "_m")

SEVERITIES = ("high", "medium", "low")


@dataclass
class Finding:
    check: str
    severity: str
    subject: str
    measure: float
    instrument: str
    detail: str

    def line(self) -> str:
        return "%-6s %-26s %-42s %-11s %s [%s]" % (
            self.severity, self.check, self.subject,
            _fmt(self.measure), self.detail, self.instrument,
        )


def _fmt(v: float) -> str:
    return str(int(v)) if isinstance(v, int) or float(v).is_integer() else "%.3f" % v


@dataclass
class Sprite:
    path: Path
    size: tuple
    alpha_hist: list
    visible_bbox: tuple
    raw_bbox: tuple
    pixel_sha256: str
    mask: Image.Image | None = field(repr=False, default=None)
    lum: Image.Image | None = field(repr=False, default=None)
    alpha: Image.Image | None = field(repr=False, default=None)
    rgb: Image.Image | None = field(repr=False, default=None)

    @property
    def canvas(self) -> int:
        return max(self.size)

    @property
    def visible_h(self) -> int:
        return self.visible_bbox[3] - self.visible_bbox[1]

    @property
    def visible_w(self) -> int:
        return self.visible_bbox[2] - self.visible_bbox[0]


def load(path: Path) -> Sprite:
    im = Image.open(path).convert("RGBA")
    alpha = im.getchannel("A")
    mask = alpha.point(lambda v: 255 if v > ALPHA_VISIBLE else 0)
    vb = mask.getbbox()
    if vb is None:
        vb = (0, 0, 0, 0)
    return Sprite(
        path=path,
        size=im.size,
        alpha_hist=alpha.histogram(),
        visible_bbox=vb,
        raw_bbox=alpha.getbbox() or (0, 0, 0, 0),
        pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
        mask=mask,
        lum=im.convert("RGB").convert("L"),
        alpha=alpha,
        rgb=im.convert("RGB"),
    )


# --- 1. transparency_real ----------------------------------------------------

def transparency_real(s: Sprite) -> list:
    out = []
    name = s.path.name
    total = s.size[0] * s.size[1]
    opaque = s.alpha_hist[255] / total
    if opaque >= OPAQUE_ALPHA_FRAC:
        out.append(Finding(
            "transparency_real", "high", name, round(opaque, 4),
            "fraction of pixels with alpha==255 (alpha histogram)",
            "no cutout: alpha is effectively fully opaque, subject is baked onto a matte",
        ))
        out.extend(_matte_fill(s))
    ring = _border_ring(s)
    if ring is not None:
        frac, flat_rgb = ring
        if frac >= BORDER_OPAQUE_FRAC:
            out.append(Finding(
                "transparency_real", "high", name, round(frac, 4),
                "fraction of the 1px canvas border with alpha>%d" % ALPHA_VISIBLE,
                "solid border ring%s — matte edge left behind by the exporter" % (
                    " of flat colour rgb%s" % (flat_rgb,) if flat_rgb else ""),
            ))
    raw_h, raw_w = s.raw_bbox[3] - s.raw_bbox[1], s.raw_bbox[2] - s.raw_bbox[0]
    slack = max(raw_h - s.visible_h, raw_w - s.visible_w) / s.canvas
    if slack > DUST_BBOX_SLACK_FRAC:
        out.append(Finding(
            "transparency_real", "medium", name, round(slack, 4),
            "(raw-alpha bbox - visible bbox) / canvas, worst of height and width",
            "%d px of sub-visible alpha dust (0<alpha<=%d) sits outside the painted "
            "body, inflating the raw bbox to %dx%d against a real %dx%d — any tool "
            "reading getbbox() here measures the ghost"
            % (sum(s.alpha_hist[1:ALPHA_VISIBLE + 1]), ALPHA_VISIBLE,
               raw_w, raw_h, s.visible_w, s.visible_h),
        ))
    return out


def _border_ring(s: Sprite):
    w, h = s.size
    if w < 3 or h < 3:
        return None
    px = s.alpha.load()
    coords = ([(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
              + [(0, y) for y in range(1, h - 1)] + [(w - 1, y) for y in range(1, h - 1)])
    opaque = [c for c in coords if px[c] > ALPHA_VISIBLE]
    frac = len(opaque) / len(coords)
    flat = None
    if opaque:
        rgb = s.rgb.load()
        cols = [rgb[c] for c in opaque]
        lo = [min(c[i] for c in cols) for i in range(3)]
        hi = [max(c[i] for c in cols) for i in range(3)]
        if all(hi[i] - lo[i] <= BORDER_FLAT_TOL for i in range(3)):
            flat = tuple(lo)
    return frac, flat


def _matte_fill(s: Sprite) -> list:
    """Only meaningful once alpha is known dead — read the corners the subject misses."""
    w, h = s.size
    lum = s.lum.load()
    corners = [lum[(x, y)] for x, y in
               ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))]
    mean = sum(corners) / len(corners)
    if mean >= MATTE_LUM_WHITE:
        which = "near-WHITE"
    elif mean <= MATTE_LUM_BLACK:
        which = "near-BLACK"
    else:
        return []
    return [Finding(
        "transparency_real", "high", s.path.name, round(mean, 1),
        "mean luminance of the four canvas corners (ITU-R 601-2 luma)",
        "%s fill sits behind the subject where transparency should be" % which,
    )]


# --- 2. boundaries_respected -------------------------------------------------

def boundaries_respected(s: Sprite) -> list:
    w, h = s.size
    x0, y0, x1, y1 = s.visible_bbox
    margins = {"top": y0, "bottom": h - y1, "left": x0, "right": w - x1}
    detail = ", ".join("%s=%dpx(%.3f)" % (k, v, v / s.canvas)
                       for k, v in margins.items())
    worst_side = min(margins, key=lambda k: margins[k])
    worst = margins[worst_side]
    if worst <= MARGIN_TOUCH_PX:
        sides = [k for k, v in margins.items() if v <= MARGIN_TOUCH_PX]
        return [Finding(
            "boundaries_respected", "high", s.path.name, worst,
            "smallest visible-alpha bbox margin in px (alpha>%d)" % ALPHA_VISIBLE,
            "drawing touches the canvas edge on %s and is clipped; %s"
            % ("+".join(sides), detail),
        )]
    if worst / s.canvas < MARGIN_ADVISE_FRAC:
        return [Finding(
            "boundaries_respected", "low", s.path.name, round(worst / s.canvas, 4),
            "smallest visible-alpha bbox margin as a fraction of canvas (alpha>%d)"
            % ALPHA_VISIBLE,
            "margin on %s is under %.0f%% of canvas; %s"
            % (worst_side, 100 * MARGIN_ADVISE_FRAC, detail),
        )]
    return []


# --- 3. facing_height_consistency -------------------------------------------

def facing_height_consistency(creature: str, facings: dict) -> list:
    """facings: facing -> Sprite. Height only; width is allowed to vary by angle."""
    if len(facings) < 2:
        return []
    frac = {f: s.visible_h / s.canvas for f, s in facings.items()}
    if min(frac.values()) <= 0:
        return [Finding(
            "facing_height_consistency", "high", creature, 0,
            "visible-alpha bbox height / canvas (alpha>%d)" % ALPHA_VISIBLE,
            "a facing has no visible content at all: %s" % _hdetail(facings, frac),
        )]
    tallest = max(frac, key=lambda f: frac[f])
    shortest = min(frac, key=lambda f: frac[f])
    ratio = frac[tallest] / frac[shortest]
    if ratio <= FACING_HEIGHT_MAX_RATIO:
        return []
    return [Finding(
        "facing_height_consistency", "high", creature, round(ratio, 3),
        "max/min of visible-alpha bbox HEIGHT over the facing set "
        "(alpha>%d; height only, never area or sqrt(w*h))" % ALPHA_VISIBLE,
        "%s is %.2fx taller than %s — an animal's height does not change with "
        "viewing angle; %s" % (tallest, ratio, shortest, _hdetail(facings, frac)),
    )]


def _hdetail(facings: dict, frac: dict) -> str:
    return ", ".join("%s=%dpx/%d(%.3f)" % (f, facings[f].visible_h,
                                           facings[f].canvas, frac[f])
                     for f in sorted(facings))


# --- 4. outline_coherence ---------------------------------------------------

def facing_symmetry(creature: str, facings: dict) -> list:
    """North/south must be symmetric front/rear views; east/west must be profiles.

    Catches a profile used as a north, which no alpha, palette or outline test can
    see. It CANNOT catch a face in the north: a frontal face is symmetric, and
    Anooba's north scores 0.84 while showing teeth to camera.
    """
    out = []
    for facing, sp in sorted(facings.items()):
        if sp.mask is None or sp.visible_bbox == (0, 0, 0, 0):
            continue
        m = sp.mask.crop(sp.visible_bbox)
        flipped = m.transpose(Image.FLIP_LEFT_RIGHT)
        both = ImageChops.logical_and(m.convert("1"), flipped.convert("1"))
        cnt = lambda img: sum(1 for v in img.convert("L").get_flattened_data() if v)
        total = cnt(m)
        score = (cnt(both) / total) if total else 0.0
        inst = "mirror overlap of the visible silhouette about its own vertical axis"
        if facing in ("north", "south") and score < SYMMETRY_MIN_NS:
            out.append(Finding(
                check="facing_symmetry", severity="high",
                subject=f"{creature}:{facing}", measure=score, instrument=inst,
                detail=f"{facing} is not a symmetric front/rear view "
                       f"({score:.2f} < {SYMMETRY_MIN_NS}) — it reads as a profile"))
        elif facing in ("east", "west") and score > SYMMETRY_MAX_EW:
            out.append(Finding(
                check="facing_symmetry", severity="medium",
                subject=f"{creature}:{facing}", measure=score, instrument=inst,
                detail=f"{facing} is symmetric ({score:.2f} > {SYMMETRY_MAX_EW}) — "
                       f"a profile should not be"))
    return out


def outline_coherence(s: Sprite) -> list:
    boundary = ImageChops.subtract(s.mask, s.mask.filter(ImageFilter.MinFilter(3)))
    n_bnd = boundary.histogram()[255]
    if n_bnd == 0:
        return []
    # Look for the keyline only where the pixel is really painted; elsewhere 255
    # (bright) so it can never be mistaken for a dark line.
    cand = Image.new("L", s.size, 255)
    cand.paste(s.lum, mask=s.alpha.point(lambda v: 255 if v >= ALPHA_SOLID else 0))
    inner = cand.filter(ImageFilter.MinFilter(KEYLINE_INSET_PX * 2 + 1))
    dark = inner.point(lambda v: 255 if v <= KEYLINE_DARK_LUM else 0)
    keyed = ImageChops.multiply(boundary, dark)
    gap = ImageChops.subtract(boundary, keyed)
    frac = keyed.histogram()[255] / n_bnd
    max_gap = _largest_component(gap)
    gap_frac = max_gap / n_bnd
    inst = ("fraction of silhouette-boundary px (alpha>%d) with luminance<=%d within "
            "%dpx inside, sampled only where alpha>=%d"
            % (ALPHA_VISIBLE, KEYLINE_DARK_LUM, KEYLINE_INSET_PX, ALPHA_SOLID))
    out = []
    if frac < KEYLINE_MIN_FRAC:
        out.append(Finding(
            "outline_coherence", "medium", s.path.name, round(frac, 3), inst,
            "keyline covers only %.1f%% of the %d px silhouette edge"
            % (100 * frac, n_bnd),
        ))
    if gap_frac > KEYLINE_MAX_GAP_FRAC:
        out.append(Finding(
            "outline_coherence", "medium", s.path.name, max_gap,
            "largest 8-connected run of un-keylined boundary px, in px "
            "(approximates arc length along a %d px silhouette edge)" % n_bnd,
            "unbroken keyline gap of %d px = %.1f%% of the silhouette edge"
            % (max_gap, 100 * gap_frac),
        ))
    return out


def _largest_component(gap: Image.Image) -> int:
    bb = gap.getbbox()
    if bb is None:
        return 0
    crop = gap.crop(bb)
    w, h = crop.size
    live = {i for i, v in enumerate(crop.tobytes()) if v}
    best = 0
    while live:
        stack = [live.pop()]
        size = 0
        while stack:
            i = stack.pop()
            size += 1
            y, x = divmod(i, w)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        j = ny * w + nx
                        if j in live:
                            live.discard(j)
                            stack.append(j)
        best = max(best, size)
    return best


# --- 5. duplicate_facings ---------------------------------------------------

def duplicate_facings(variant_group: str, sprites: list) -> list:
    by_hash = defaultdict(list)
    for s in sprites:
        by_hash[s.pixel_sha256].append(s.path.name)
    out = []
    for digest, names in sorted(by_hash.items()):
        if len(names) < 2:
            continue
        out.append(Finding(
            "duplicate_facings", "high", variant_group, len(names),
            "sha256 of decoded RGBA pixel data (Image.tobytes)",
            "identical pixels in %d files: %s (sha256 %s)"
            % (len(names), ", ".join(sorted(names)), digest[:12]),
        ))
    return out


# --- grouping ---------------------------------------------------------------

def split_facing(stem: str):
    m = FACING_RE.match(stem)
    return (m.group("base"), m.group("facing")) if m else (stem, None)


def creature_key(path: Path) -> tuple:
    base, _ = split_facing(path.stem)
    return (path.parent.as_posix(), base)


def variant_key(key: tuple, all_bases: set) -> tuple:
    parent, base = key
    for suf in SEX_SUFFIXES:
        if base.endswith(suf):
            return (parent, base[: -len(suf)])
    # GizkaW -> Gizka, only when the stripped name is itself a creature here.
    if len(base) > 1 and base.endswith("W") and (parent, base[:-1]) in all_bases:
        return (parent, base[:-1])
    return key


# --- driver ----------------------------------------------------------------

def resolve_original(path: Path) -> Path:
    """Staged review thumbnails are named with '/' replaced by '__'. Prefer the 512px
    original those names encode — a 256px thumbnail's alpha has been through LANCZOS."""
    if "__" not in path.name:
        return path
    cand = REPO_ROOT / path.name.replace("__", "/")
    return cand if cand.is_file() else path


def collect(paths, originals=False) -> list:
    files = []
    for p in paths:
        p = Path(p)
        files.extend(sorted(p.rglob("*.png")) if p.is_dir() else [p])
    if originals:
        files = [resolve_original(f) for f in files]
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def run(paths, originals=False) -> list:
    files = collect(paths, originals=originals)
    sprites = {f: load(f) for f in files}
    findings = []
    for f in files:
        s = sprites[f]
        findings.extend(transparency_real(s))
        findings.extend(boundaries_respected(s))
        findings.extend(outline_coherence(s))

    creatures = defaultdict(dict)
    for f in files:
        base, facing = split_facing(f.stem)
        if facing:
            creatures[creature_key(f)][facing] = sprites[f]
    for key, facings in sorted(creatures.items()):
        findings.extend(facing_height_consistency(key[1], facings))
        findings.extend(facing_symmetry(key[1], facings))

    variants = defaultdict(list)
    bases = set(creatures)
    for key, facings in creatures.items():
        variants[variant_key(key, bases)].extend(facings.values())
    for key, group in sorted(variants.items()):
        findings.extend(duplicate_facings(key[1], group))
    return findings


def print_table(findings) -> None:
    if not findings:
        print("no findings")
        return
    order = {s: i for i, s in enumerate(SEVERITIES)}
    print("%-6s %-26s %-42s %-11s %s" % ("SEV", "CHECK", "SUBJECT", "MEASURE",
                                         "EXPLANATION [instrument]"))
    for fi in sorted(findings, key=lambda f: (order.get(f.severity, 9),
                                              f.check, f.subject)):
        print(fi.line())
    counts = defaultdict(int)
    for fi in findings:
        counts[fi.check] += 1
    print("\n%d finding(s): %s" % (len(findings), ", ".join(
        "%s=%d" % kv for kv in sorted(counts.items()))))


# --- selftest --------------------------------------------------------------

REVIEW_ART = REPO_ROOT / "Transient/pyrelands_art_review/art"

# Owner-confirmed or measurement-confirmed height breaks. Anooba is the only row the
# owner named out loud ("North is HUGE compared to east, and South isn't south").
HEIGHT_MUST_FLAG = {
    "Anooba_f", "Anooba_m", "Boomsnake", "Bolotaur", "AA_FireWasp",
    "Zeer", "GR_Mantistanis", "Dalgo",
}
HEIGHT_MUST_PASS = {"Nuna_f", "AA_GreenGoo", "Orray", "FireHawk"}

# 🔴 FurnaceBeast was handed to me as known-GOOD at 1.03x, and it is NOT. That 1.03x
# is the RAW alpha bbox, inflated by 3901 px of alpha 1..16 dust reaching to y=480
# while the painted body stops at y=400. Its real east/north visible mismatch is the
# ratio pinned below — larger than Dalgo/GR_Mantistanis/Zeer, all labelled bad. So it
# is flagged, deliberately, and pinned so that a threshold or art change fails loudly.
# Whether that flag should reject is the owner's call, not this module's.
HEIGHT_CONFLICT = {"FurnaceBeast": 1.636}

# MEASURED: 2 of 57 facings (FurnaceBeast_north, FireHawk_east) fall below
# KEYLINE_MIN_FRAC. Headroom of 2 so a real new break is not a selftest failure.
OUTLINE_MAX_FLAGGED_FILES = 4

DUPLICATE_MUST_FLAG = [
    ("Anooba", {"Anooba_f_east.png", "Anooba_m_east.png"}),
    ("Anooba", {"Anooba_f_north.png", "Anooba_m_north.png"}),
    ("Anooba", {"Anooba_f_south.png", "Anooba_m_south.png"}),
    ("Nuna", {"Nuna_f_north.png", "Nuna_m_north.png"}),
    ("Nuna", {"Nuna_f_south.png", "Nuna_m_south.png"}),
    ("Gizka", {"Gizka_north.png", "GizkaW_north.png"}),
    ("Gizka", {"Gizka_south.png", "GizkaW_south.png"}),
]


def selftest() -> int:
    if not REVIEW_ART.is_dir():
        print("FAIL  corpus missing: %s (Transient has a ~14 day shelf life; "
              "re-stage with build_pyrelands_art_sheet.py)" % REVIEW_ART)
        return 1
    findings = run([REVIEW_ART], originals=True)
    fails = []

    heights = {f.subject: f.measure for f in findings
               if f.check == "facing_height_consistency"}
    for name in sorted(HEIGHT_MUST_FLAG):
        if name not in heights:
            fails.append("facing_height_consistency did NOT flag known-bad %s "
                         "(threshold %.2f is too loose)"
                         % (name, FACING_HEIGHT_MAX_RATIO))
    for name in sorted(HEIGHT_MUST_PASS):
        if name in heights:
            fails.append("facing_height_consistency flagged known-good %s at %.3f "
                         "(threshold %.2f is too tight)"
                         % (name, heights[name], FACING_HEIGHT_MAX_RATIO))
    for name, pinned in sorted(HEIGHT_CONFLICT.items()):
        if name not in heights:
            fails.append("%s is no longer flagged — the documented ground-truth "
                         "conflict has changed and needs re-reporting to the owner"
                         % name)
        elif abs(heights[name] - pinned) > 0.01:
            fails.append("%s height ratio moved %.3f -> %.3f; the conflict note in "
                         "HEIGHT_CONFLICT cites the old number"
                         % (name, pinned, heights[name]))

    dups = [f for f in findings if f.check == "duplicate_facings"]
    for subject, names in DUPLICATE_MUST_FLAG:
        if not any(f.subject == subject and all(n in f.detail for n in names)
                   for f in dups):
            fails.append("duplicate_facings did NOT report %s as identical"
                         % ", ".join(sorted(names)))

    # The one keyline break in the corpus, confirmed by eye: FurnaceBeast north's
    # shoulder spikes are light grey with no dark edge.
    if not any(f.check == "outline_coherence" and "FurnaceBeast_north" in f.subject
               for f in findings):
        fails.append("outline_coherence did NOT flag FurnaceBeast_north.png, whose "
                     "shoulder-spike keyline gap was confirmed by eye")
    if any(f.check == "outline_coherence" and "Anooba" in f.subject for f in findings):
        fails.append("outline_coherence flagged an Anooba facing; its keyline "
                     "measures 1.000 and must stay clean")
    # A check that flags most of the corpus carries no information, so cap it: 2 of
    # 57 facings score below KEYLINE_MIN_FRAC today, and loosening DARK/MIN_FRAC until
    # everything trips must fail here rather than look like a productive sweep.
    keyed = {f.subject for f in findings if f.check == "outline_coherence"}
    if len(keyed) > OUTLINE_MAX_FLAGGED_FILES:
        fails.append("outline_coherence flagged %d files (%s); more than %d means the "
                     "keyline thresholds have stopped discriminating"
                     % (len(keyed), ", ".join(sorted(keyed)),
                        OUTLINE_MAX_FLAGGED_FILES))

    # Severity matters here: the low-severity margin advisory would keep catching this
    # file even if the touching/clipped rule were neutered, so require the high one.
    if not any(f.check == "boundaries_respected" and f.severity == "high"
               and "Nuna_f_east" in f.subject for f in findings):
        fails.append("boundaries_respected did NOT raise a HIGH finding on "
                     "Nuna_f_east.png, whose visible content touches the top edge "
                     "(top margin 0 px) and is clipped")

    n_creatures = len({f.subject for f in findings
                       if f.check == "facing_height_consistency"} | HEIGHT_MUST_PASS)
    for line in fails:
        print("FAIL  " + line)
    if fails:
        print("\n%d/%d assertion(s) failed over %d findings" % (
            len(fails), len(fails), len(findings)))
        return 1
    print("PASS  %d findings over %s" % (len(findings), REVIEW_ART))
    print("PASS  facing_height_consistency: %d flagged (%d required known-bad + %d "
          "documented conflict), %d known-good clean, threshold %.2f"
          % (len(heights), len(HEIGHT_MUST_FLAG), len(HEIGHT_CONFLICT),
             len(HEIGHT_MUST_PASS), FACING_HEIGHT_MAX_RATIO))
    print("PASS  duplicate_facings: all %d known-identical pairs reported"
          % len(DUPLICATE_MUST_FLAG))
    print("PASS  outline_coherence and boundaries_respected hit their confirmed cases")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="PNG files or directories")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--originals", action="store_true",
                    help="map staged '__' thumbnail names back to the repo originals")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.paths:
        ap.error("give at least one PNG or directory (or --selftest)")
    findings = run(a.paths, originals=a.originals)
    if a.as_json:
        print(json.dumps([asdict(f) for f in findings], indent=1))
    else:
        print_table(findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
