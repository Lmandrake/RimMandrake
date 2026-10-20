#!/usr/bin/env python3
"""game_art.py — does a review sheet show GAME ART? Decided from the pictures themselves, never from the sheet's say-so.

Owner, by question card 2026-10-11 ("Hybrid fix"): any sheet showing game art is refused without its true-scale panels
wherever it is delivered — served (serve_gated.py), committed (.githooks/pre-commit), or published to the phone
(sheet_to_artifact.py). A sheet cannot opt out by declaring itself non-art: `sheet_conflicts_review_2026-10-09` declared
`non-art` while showing 311 game sprites.

    python3 game_art.py classify <sheet.html>...     GAME-ART / NOT-ART per sheet, with the evidence
    python3 game_art.py deliver  <sheet.html>...     exit 0 only if each sheet may be delivered (see delivery_check)
    python3 game_art.py precommit [<repo>]           the commit chokepoint (infrastructure/githooks/pre-commit)

A picture is game art when EITHER
  * its path says so: a mod `Textures/` folder, the artpipe state (`<data root>/artpipe`, `_artsrc`), the art store (`<data root>/artstore`),
    the vanilla `bundle_textures` inventory, or a texPath-shaped name (`Things/…`, `UI/Icons/…`), a facing sprite's file
    name (`X_east.png`), or a file named after a ThingDef/PawnKindDef/TerrainDef in the def dump; or
  * its pixels say so: a cut-out sprite — PNG/WebP/GIF with an alpha channel holding both fully transparent and opaque
    pixels. Screenshots, scale panels (saved RGB) and canon reference photos have no cut-out alpha.
Copied images keep no folder provenance (every sheet copies into its own img folder) and flattened thumbnails lose their
alpha, so the two tests cover each other: the name test catches a flattened or missing picture, the pixel test a
renamed one (a content-hashed `img/<sha>.webp`).

delivery_check: a sheet with no game art may go anywhere. A sheet WITH game art must carry a valid scaled-review-gate
stamp (scaled_review_gate.verify_stamp) — only art_sheet.py --biome / --subjects can produce one, and they put a scale
panel on every row whose def has a world size.
"""
from __future__ import annotations

import base64
import re
import sys
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

IMG_EXT = (".png", ".webp", ".gif", ".jpg", ".jpeg")
REF_RE = re.compile(r"""["'(=]\s*([^"'()<>\s]{1,400}?\.(?:png|webp|gif|jpe?g))(?:\?[^"'()<>\s]*)?\s*["')]""", re.I)
DATA_RE = re.compile(r"data:image/(?:png|webp|gif);base64,([A-Za-z0-9+/=]{200,})")
PATH_MARKS = re.compile(r"(?:^|/)(?:Textures|_artpipe|_artsrc|_artstore|rimmandrake/artpipe|rimmandrake/artstore|bundle_textures)/|(?:^|/)(?:Things|UI/Icons|UI/Commands)/", re.I)
NOT_ART_NAME = re.compile(r"(?:^|/)scale_[^/]*\.png$|(?:^|/)(?:canon|refs?)/", re.I)   # our own scale panels; canon refs
FACING_RE = re.compile(r"_(?:north|south|east|west)m?(?:_r?\d+)?\.(?:png|webp|gif)$", re.I)   # a facing sprite's file name
STRIP_RE = re.compile(r"(?:_(?:north|south|east|west)m?|_v\d+|_\d+|_(?:old|new|current|render|nooutline|outline))+$", re.I)
MAX_PROBE = 60          # pixel-test at most this many distinct images per sheet (enough: one positive decides)
TRANSPARENT_MIN = 0.03  # share of fully transparent pixels a cut-out sprite has at least
OPAQUE_MIN = 0.01       # … and of opaque ones


def sprite_reason(data_or_path) -> str:
    """'' if the image is not a cut-out sprite (or unreadable), else a short description of why it is one."""
    try:
        from PIL import Image
        im = Image.open(BytesIO(data_or_path) if isinstance(data_or_path, (bytes, bytearray)) else data_or_path)
        im.load()
    except Exception:                               # noqa: BLE001  unreadable is not evidence either way
        return ""
    if "A" not in im.getbands() and not (im.mode == "P" and "transparency" in im.info):
        return ""
    a = im.convert("RGBA").getchannel("A")
    a.thumbnail((128, 128))
    hist = a.histogram()
    n = sum(hist) or 1
    clear, solid = hist[0] / n, sum(hist[200:]) / n
    if clear >= TRANSPARENT_MIN and solid >= OPAQUE_MIN:
        return f"{im.width}×{im.height} cut-out sprite ({clear:.0%} transparent, {solid:.0%} opaque)"
    return ""


_DEFNAMES: set | None = None


def def_names() -> set:
    """ThingDef + PawnKindDef + TerrainDef names in the offline def dump (empty when the dump is unreadable)."""
    global _DEFNAMES
    if _DEFNAMES is None:
        try:
            import sqlite3
            import scale_panel
            db = sqlite3.connect(str(scale_panel.DB))
            _DEFNAMES = {n for (n,) in db.execute(
                "select def_name from defs where def_type in ('ThingDef','PawnKindDef','TerrainDef')")}
        except Exception:                           # noqa: BLE001
            _DEFNAMES = set()
    return _DEFNAMES


def def_name_of(ref: str) -> str:
    """The def a picture's FILE NAME names ('RM_Sollak_east.png' -> 'RM_Sollak'; 'swanimals_Grank_Grank.png' -> 'Grank'),
    or ''. Flattened thumbnails lose their alpha, so a file named after a def is the evidence that survives."""
    stem = STRIP_RE.sub("", Path(ref.replace("\\", "/")).stem)
    names = def_names()
    toks = stem.split("_")
    for i in range(len(toks)):
        cand = "_".join(toks[i:])
        if len(cand) >= 4 and cand in names:
            return cand
    return ""


def image_refs(html: str) -> list[str]:
    out = []
    for m in REF_RE.finditer(html):
        r = m.group(1)
        if r.startswith(("http://", "https://")) or "${" in r:
            continue
        if r not in out:
            out.append(r)
    return out


def _resolve(ref: str, base: Path) -> Path | None:
    ref = ref.replace("\\", "/")
    for cand in (base / ref, Path(ref)):
        try:
            if cand.is_file():
                return cand
        except OSError:
            pass
    if "/" not in ref:              # a bare name a script joins to an image folder at run time
        for d in [base / "img"] + [p for p in base.glob("*") if p.is_dir() and p.name.endswith(("_img", "img", "images"))][:20]:
            if (d / ref).is_file():
                return d / ref
    return None


def classify(html: str, html_path: Path | None = None) -> dict:
    """{'game_art': bool, 'evidence': [str], 'probed': int, 'refs': int}."""
    base = Path(html_path).resolve().parent if html_path else Path.cwd()
    refs = image_refs(html)
    ev, probed = [], 0
    for r in refs:
        if NOT_ART_NAME.search(r):
            continue
        if PATH_MARKS.search(r.replace("\\", "/")):
            ev.append(f"{r}: game-art path")
            break
        if FACING_RE.search(r):
            ev.append(f"{r}: a facing sprite's file name")
            break
        d = def_name_of(r)
        if d:
            ev.append(f"{r}: named after def {d}")
            break
    if not ev:
        for r in refs:
            if probed >= MAX_PROBE:
                break
            if NOT_ART_NAME.search(r):
                continue
            p = _resolve(r, base)
            if p is None:
                continue
            probed += 1
            why = sprite_reason(p)
            if why:
                ev.append(f"{r}: {why}")
                break
    if not ev:
        for m in list(DATA_RE.finditer(html))[:20]:
            probed += 1
            try:
                why = sprite_reason(base64.b64decode(m.group(1)))
            except ValueError:
                continue
            if why:
                ev.append(f"embedded data: image: {why}")
                break
    return {"game_art": bool(ev), "evidence": ev, "probed": probed, "refs": len(refs)}


def delivery_check(path) -> tuple[bool, str]:
    """(ok, message). ok when the sheet shows no game art, or shows it and carries a valid scaled-review-gate stamp."""
    import scaled_review_gate as SG
    path = Path(path)
    html = path.read_text(errors="replace")
    c = classify(html, path)
    if not c["game_art"]:
        return True, f"no game art ({c['probed']} of {c['refs']} pictures probed)"
    ok, msg = SG.verify_stamp(html)
    if ok:
        return True, f"game art, gate-stamped ({msg})"
    return False, (f"{path.name} shows GAME ART ({c['evidence'][0]}) but has no valid scaled-review-gate stamp ({msg}). "
                   "Game art is reviewed only on a gated sheet with true-scale panels: build it with "
                   "`python3 src/RimMandrake/Utils/art/art_sheet.py --subjects <defName>... --name <name>` "
                   "(or `--biome <RM_X>`). Declaring the sheet non-art does not exempt it. Skill: rimworld-review-sheets.")


def staged_sheets(repo: Path) -> list[Path]:
    """HTML files the commit in progress adds or modifies (honours the temporary index of `git commit <paths>`)."""
    import subprocess
    r = subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--name-only", "--diff-filter=AM", "-z", "--", "*.html"],
                       capture_output=True, text=True)
    return [repo / n for n in r.stdout.split("\0") if n]


def precommit(repo: Path) -> int:
    """The commit chokepoint: refuse a commit that adds/changes a game-art sheet without a valid gate stamp."""
    bad = []
    for p in staged_sheets(repo):
        if not p.is_file():
            continue
        html = p.read_text(errors="replace")
        if 'id="ITEMS"' not in html and "<img" not in html:
            continue            # not a review sheet / picture page
        ok, msg = delivery_check(p)
        if not ok:
            bad.append(msg)
    for m in bad:
        print("pre-commit REFUSED: " + m, file=sys.stderr)
    return 1 if bad else 0


def main(argv) -> int:
    if argv[:1] == ["precommit"]:
        try:
            return precommit(Path(argv[1]) if len(argv) > 1 else Path.cwd())
        except Exception as e:  # noqa: BLE001  a crashing guard fails OPEN (the hook says so)
            print(f"game_art precommit crashed: {type(e).__name__}: {e}", file=sys.stderr)
            return 3
    if len(argv) < 2 or argv[0] not in ("classify", "deliver"):
        print(__doc__)
        return 2
    rc = 0
    for s in argv[1:]:
        p = Path(s)
        if argv[0] == "classify":
            c = classify(p.read_text(errors="replace"), p)
            print(("GAME-ART " if c["game_art"] else "NOT-ART  ") + f"{s}  ({c['probed']}/{c['refs']} probed)"
                  + (f"  {c['evidence'][0]}" if c["evidence"] else ""))
        else:
            ok, msg = delivery_check(p)
            print(("OK      " if ok else "REFUSED ") + msg)
            rc |= 0 if ok else 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
