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
    if s.visible_bbox == (0, 0, 0, 0):
        # No visible content at all: margins computed from an empty bbox would
        # read as top=0/left=0 and get reported as "touches the canvas edge,
        # clipped" — the wrong diagnosis for a blank/fully-transparent file.
        # transparency_real() and facing_height_consistency() already flag an
        # empty sprite on their own terms; this check has nothing to say here.
        return []
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

# ART_SELFTEST_CORPUS_IN_TRANSIENT_1: the corpus used to be a staged copy under
# Transient/pyrelands_art_review/art, which the ~14-day Transient sweep would
# delete out from under this gate, AND whose staged filenames secretly decided
# what got tested (`originals=True` mapped them back to these same repo files).
# Declaring the roster here removes Transient/ from the loop entirely: new art
# placed under any of these directories is automatically in scope, nothing
# needs re-staging, and the roster survives any sweep because it IS the repo.
# Equivalent-or-broader coverage of the 71 files staged 2026-09-16: every
# ArtOverride mod that contributed a facing set, plus the two donor-mod
# subdirectories (SWBestiary's Bolotaur, UtinniPatches' Pyrelands animals) and
# the two Pyrelands item/plant directories that rounded out that staging.
SELFTEST_ROSTER = (
    REPO_ROOT / "src/RimStarWars/AnoobaArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/DalgoArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/GizkaArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/IriazArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/NunaArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/OrrayArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/ZeerArtOverride/Textures",
    REPO_ROOT / "src/RimUtinni/BarbslingerArtOverride/Textures",
    REPO_ROOT / "src/RimUtinni/BoomsnakeArtOverride/Textures",
    REPO_ROOT / "src/RimUtinni/FireWaspArtOverride/Textures",
    REPO_ROOT / "src/RimUtinni/GreenGooArtOverride/Textures",
    REPO_ROOT / "src/RimUtinni/MantistanisArtOverride/Textures",
    REPO_ROOT / "src/RimUtinni/RazorjackArtOverride/Textures",
    REPO_ROOT / "src/RimStarWars/SWBestiary/Textures/swanimals/Bolotaur",
    REPO_ROOT / "src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands",
    REPO_ROOT / "src/RimMandrake/Pyrelands/Textures/Things/Item/Resource",
    REPO_ROOT / "src/RimMandrake/Pyrelands/Textures/Things/Plant",
)

#  RECALIBRATED 2026-09-18, SELFTEST_FAILURE_TRIAGE_1. The approved Pyrelands
#  render wave (9e7e773a0) and the Gizka dino_v5 lock (bd9a1b8ee) both landed
#  2026-09-17 and REPLACED the art these fixtures were pinned against on
#  2026-09-15/16, so several pins described files that no longer exist. Every
#  number below was re-measured against the art on disk; the two that moved for
#  the WRONG reason are pinned separately as regressions rather than deleted.

# Owner-confirmed or measurement-confirmed height breaks. Anooba is the only row the
# owner named out loud ("North is HUGE compared to east, and South isn't south").
#
# ⭐ Orray is the one row here the owner has ruled ACCEPTABLE while still flagged —
# 2026-09-18, verbatim, having looked at the facings himself: "New Orray art is
# vastly better than old. North and east are good. South needs regen it is 'fat'
# somehow. Older art is horrible. Discard." Its south was regenerated on that
# ruling; the remaining ratio is north (a near-full-length rear view) against east
# (a low side profile), i.e. legitimate camera-angle variety in art he approved by
# eye. It stays in this set because the check must keep flagging it honestly, NOT
# because the art is bad. ⛔ Do not "fix" this row by loosening
# FACING_HEIGHT_MAX_RATIO. Item: ORRAY_FACING_HEIGHT_REGRESSION_1.
HEIGHT_MUST_FLAG = {
    "Anooba_f", "Anooba_m", "Boomsnake", "Bolotaur", "AA_FireWasp",
    "GR_Mantistanis", "Dalgo", "Orray",
}
# ✅ Zeer moved FLAG -> PASS: the 2026-09-17 wave genuinely fixed it. MEASURED
# 1.480 on the pre-wave blob (`9e7e773a0^`) against 1.024 now (east 0.990,
# north 0.967, south 0.980 of canvas) — it is now the cleanest row in the
# corpus, so it anchors the pass side instead of the flag side.
HEIGHT_MUST_PASS = {"Nuna_f", "AA_GreenGoo", "FireHawk", "Zeer"}

# Height ratios that moved for the WRONG reason and are pinned to an exact number
# so the selftest fails loudly whether they worsen OR are quietly "fixed" by moving
# a threshold. Empty: the one entry this set was built for (Orray, 2.488 after the
# 2026-09-17 wave) was settled by the owner on 2026-09-18 — south regenerated, the
# rest of the set approved by eye — and now sits in HEIGHT_MUST_FLAG.
HEIGHT_REGRESSION = {}

# 🔴 FurnaceBeast was handed to me as known-GOOD at 1.03x, and it is NOT. That 1.03x
# is the RAW alpha bbox, inflated by 3901 px of alpha 1..16 dust reaching to y=480
# while the painted body stops at y=400. Its real east/north visible mismatch is the
# ratio pinned below — larger than Dalgo/GR_Mantistanis/Zeer, all labelled bad. So it
# is flagged, deliberately, and pinned so that a threshold or art change fails loudly.
# Whether that flag should reject is the owner's call, not this module's.
HEIGHT_CONFLICT = {"FurnaceBeast": 1.636}

# RE-MEASURED 2026-09-19 against SELFTEST_ROSTER (ART_SELFTEST_CORPUS_IN_TRANSIENT_1):
# walking the real Pyrelands FireHawk directory picks up its _Body_/_Wing_ part
# textures too, which the old 71-file staging did not include. 3 of 88 files
# (FurnaceBeast_north, FireHawk_east, FireHawk_Wing_east) now fall below
# KEYLINE_MIN_FRAC. Headroom of 2 so a real new break is not a selftest failure.
OUTLINE_MAX_FLAGGED_FILES = 5

# Facings whose visible content touches a canvas edge and is clipped, re-measured
# 2026-09-18. The previous pin, `Nuna_f_east.png`, is GONE and legitimately so —
# the 2026-09-17 wave replaced that file and its top margin is no longer 0.
BOUNDARY_MUST_FLAG_HIGH = [
    # Pre-existing and stable: unchanged since 2026-09-14, clipped on the right
    # in both the current file and the pre-`bd9a1b8ee` blob. This is the anchor
    # that does not move, so the check stays covered even if the other is fixed.
    ("GizkaW_south.png", "right margin 0 px, unchanged since 2026-09-14"),
]

# The other side of the same check, and it is the side that decays silently: three
# facings were REPAIRED 2026-09-18 (ZEER_EAST_TOP_CLIP_1) by insetting or shifting
# the body inside its existing canvas, never by rescaling the facing set — the
# 2026-09-17 wave's ~0.98-of-canvas scaling is exactly what clipped them, and
# Zeer's hard-won 1.024 height ratio had to survive the fix (it reads 1.035 now).
# A regen that re-clips any of these is a regression, so pin them: a "must flag"
# list alone cannot tell a fix from a file that stopped being measured.
BOUNDARY_MUST_NOT_FLAG_HIGH = [
    ("Zeer_east.png", "inset 512->490 and re-centred; top margin 11 px"),
    ("Iriaz_south.png", "inset 256->249 and re-centred; top margin 3 px"),
    ("GR_Mantistanis_south.png", "shifted down 21 px into its own bottom slack; "
                                 "top margin 21 px, height untouched so the pinned "
                                 "2.095 facing-height ratio is undisturbed"),
]

# 🔑 duplicate_facings is now proven SYNTHETICALLY, and that is the point.
# This used to pin 7 real pairs (3 Anooba, 2 Nuna, 2 Gizka/GizkaW). All 7 are
# gone, because making them distinct was the DECLARED PURPOSE of the 2026-09-17
# wave — 9e7e773a0's own message says the overrides are "now distinct on every
# facing". So the corpus now contains zero identical pairs and the check had
# nothing left covering it: it would have passed this selftest while being
# completely broken. A check whose only fixtures are defects someone is actively
# fixing is a check that goes dark the moment they succeed. The fixture below
# cannot go dark — it builds its own positive AND negative case from two copies
# of one real sprite, so art churn can never silence it.
DUPLICATE_FIXTURE_SRC = (REPO_ROOT / "src/RimUtinni/RazorjackArtOverride/Textures"
                         "/Things/Pawn/Animal/AA_Razorjack/AA_Razorjack_east.png")


def _duplicate_facings_proof() -> list:
    """-> list of failure strings. Proves the check both fires and discriminates."""
    import shutil
    import tempfile
    if not DUPLICATE_FIXTURE_SRC.is_file():
        return ["duplicate_facings fixture source missing: %s"
                % DUPLICATE_FIXTURE_SRC]
    fails = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # Positive: _f/_m are merged into one variant group by variant_key, so
        # two byte-identical copies MUST be reported.
        shutil.copyfile(DUPLICATE_FIXTURE_SRC, d / "SynthDup_f_east.png")
        shutil.copyfile(DUPLICATE_FIXTURE_SRC, d / "SynthDup_m_east.png")
        # Negative control: same pairing, one pixel changed. A check that
        # reports this too is matching on names, not on pixels.
        shutil.copyfile(DUPLICATE_FIXTURE_SRC, d / "SynthUniq_f_east.png")
        im = Image.open(DUPLICATE_FIXTURE_SRC).convert("RGBA")
        im.putpixel((0, 0), (255, 0, 255, 255))
        im.save(d / "SynthUniq_m_east.png")
        dups = {f.subject for f in run([d]) if f.check == "duplicate_facings"}
    if "SynthDup" not in dups:
        fails.append("duplicate_facings did NOT report two byte-identical "
                     "copies of one sprite — the check is dead, not the corpus")
    if "SynthUniq" in dups:
        fails.append("duplicate_facings reported a pair differing by one pixel "
                     "— it is matching names, not pixel data")
    return fails


def selftest() -> int:
    missing = [d for d in SELFTEST_ROSTER if not d.is_dir()]
    if missing:
        print("FAIL  corpus director%s missing from SELFTEST_ROSTER (renamed or "
              "deleted mod?): %s" % ("y" if len(missing) == 1 else "ies",
                                     ", ".join(str(d) for d in missing)))
        return 1
    findings = run(SELFTEST_ROSTER)
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
    for label, pins in (("HEIGHT_CONFLICT", HEIGHT_CONFLICT),
                        ("HEIGHT_REGRESSION", HEIGHT_REGRESSION)):
        for name, pinned in sorted(pins.items()):
            if name not in heights:
                fails.append("%s is no longer flagged — the %s entry describes art "
                             "that has changed and needs re-reporting to the owner"
                             % (name, label))
            elif abs(heights[name] - pinned) > 0.01:
                fails.append("%s height ratio moved %.3f -> %.3f; the note in %s "
                             "cites the old number"
                             % (name, pinned, heights[name], label))

    fails.extend(_duplicate_facings_proof())

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
    for name, why in BOUNDARY_MUST_FLAG_HIGH:
        if not any(f.check == "boundaries_respected" and f.severity == "high"
                   and name in f.subject for f in findings):
            fails.append("boundaries_respected did NOT raise a HIGH finding on "
                         "%s — %s" % (name, why))
    # A "must not flag" pin passes for two different reasons — the file is clean, or
    # the file is gone — so name the roster rather than inferring it from findings.
    # `Nuna_f_east.png` sat in the must-flag list describing art that had already
    # been replaced; without this the same silence would hide a deleted repair.
    roster = {f.name for f in collect(SELFTEST_ROSTER)}
    for name, why in BOUNDARY_MUST_FLAG_HIGH + BOUNDARY_MUST_NOT_FLAG_HIGH:
        if name not in roster:
            fails.append("boundaries_respected pin names %s, which is not in the "
                         "corpus at all — the pin describes art that has moved or "
                         "been deleted (%s)" % (name, why))
    for name, why in BOUNDARY_MUST_NOT_FLAG_HIGH:
        if any(f.check == "boundaries_respected" and f.severity == "high"
               and name in f.subject for f in findings):
            fails.append("boundaries_respected raised a HIGH finding on %s, which "
                         "was repaired and must stay repaired — %s" % (name, why))

    for line in fails:
        print("FAIL  " + line)
    if fails:
        print("\n%d/%d assertion(s) failed over %d findings" % (
            len(fails), len(fails), len(findings)))
        return 1
    print("PASS  %d findings over %d files in %d in-repo directories"
          % (len(findings), len(roster), len(SELFTEST_ROSTER)))
    print("PASS  facing_height_consistency: %d flagged (%d required known-bad + %d "
          "documented conflict + %d pinned regression), %d known-good clean, "
          "threshold %.2f"
          % (len(heights), len(HEIGHT_MUST_FLAG), len(HEIGHT_CONFLICT),
             len(HEIGHT_REGRESSION), len(HEIGHT_MUST_PASS),
             FACING_HEIGHT_MAX_RATIO))
    print("PASS  duplicate_facings fires on byte-identical copies and does NOT "
          "fire on a one-pixel difference (synthetic fixture, corpus-independent)")
    print("PASS  outline_coherence, and boundaries_respected on %d pinned clipped "
          "facings + %d pinned repaired facings, all %d present in the corpus"
          % (len(BOUNDARY_MUST_FLAG_HIGH), len(BOUNDARY_MUST_NOT_FLAG_HIGH),
             len(BOUNDARY_MUST_FLAG_HIGH) + len(BOUNDARY_MUST_NOT_FLAG_HIGH)))
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
