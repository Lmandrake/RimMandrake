#!/usr/bin/env python3
"""probe_png_wellformed.py — bulk, deterministic PNG well-formedness probe.

WHY: CLAUDE.md's "Code isn't clean until a review says so" policy applies to
every file the game loads, PNGs included — but a line-by-line LLM review of
pixel art is the wrong tool (owner ruling, 2026-09-24: binary content gets a
"quick probe that they are a well formed image file... done in bulk and
swiftly using deterministic tools", not the same review as code/text).

This is that probe. Pure stdlib (no Pillow — see pnglib.py's own header for
why none is installed here). It validates PNG STRUCTURE, not art content:
signature bytes, chunk length/type/CRC32 for every chunk, IHDR first and
IEND last, and non-zero width/height. A file that passes is proven not
truncated, not corrupted, and not a renamed non-PNG — nothing more, nothing
less. It says nothing about whether the ART is right; that's still a human's
call (or the artpipe validator's, for a fresh generation).

USAGE
    python3 src/RimMandrake/Utils/probe_png_wellformed.py <path> [<path> ...]
    python3 src/RimMandrake/Utils/probe_png_wellformed.py --dirty-from-status
        # reads infrastructure/state/CODE_REVIEW_STATUS.json's own `check`
        # output is NOT what this reads from (that's git-status-backed and
        # slow at scale) -- this flag instead globs every tracked .png and
        # calls `code_review_status.py check` in one batched subprocess,
        # keeping only the DIRTY rows, exactly the scaling fix that tool's
        # own doctrine (SCALING REWRITE, 2026-09-05) asks every caller to
        # respect: one call over many paths, not one call per path.
    python3 src/RimMandrake/Utils/probe_png_wellformed.py --dirty-from-status --mark-clean
        # same, then mark-clean every PASS via one subprocess per file
        # (mark-clean itself is not batched in the underlying tool; this is
        # the fastest correct way to drive it over many files)

Exit code 0 iff every probed file PASSED. A FAIL is a real finding -- report
it, do not silently skip it.
"""
import argparse
import struct
import subprocess
import sys
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
STATUS_SCRIPT = Path(__file__).resolve().parent / "code_review_status.py"
PNG_SIG = b"\x89PNG\r\n\x1a\n"


class PngProbeError(Exception):
    pass


def probe_one(path: Path) -> tuple[bool, str]:
    """(passed, detail). detail is a one-line reason on FAIL, or 'WxH' on PASS."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        return False, f"cannot read: {exc}"

    if len(data) < 8 or data[:8] != PNG_SIG:
        return False, "bad/missing PNG signature (not a real PNG, or truncated to nothing)"

    pos = 8
    n = len(data)
    first_type = None
    last_type = None
    width = height = None
    seen_ihdr = False
    while pos < n:
        if pos + 8 > n:
            return False, f"truncated chunk header at byte {pos} (file cut off mid-chunk)"
        length, ctype_b = struct.unpack(">I4s", data[pos:pos + 8])
        ctype = ctype_b.decode("ascii", errors="replace")
        if first_type is None:
            first_type = ctype
        data_start = pos + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > n:
            return False, f"chunk '{ctype}' at byte {pos} claims length {length} but file ends first (truncated)"
        chunk_data = data[data_start:data_end]
        (stored_crc,) = struct.unpack(">I", data[data_end:crc_end])
        computed_crc = zlib.crc32(ctype_b + chunk_data) & 0xFFFFFFFF
        if stored_crc != computed_crc:
            return False, f"chunk '{ctype}' at byte {pos} fails CRC32 (stored {stored_crc:#010x} != computed {computed_crc:#010x}) — corrupted"
        if ctype == "IHDR":
            if len(chunk_data) != 13:
                return False, f"IHDR chunk has wrong length {len(chunk_data)} (must be 13)"
            width, height = struct.unpack(">II", chunk_data[:8])
            seen_ihdr = True
        last_type = ctype
        pos = crc_end

    if first_type != "IHDR":
        return False, f"first chunk is '{first_type}', not IHDR (malformed structure)"
    if last_type != "IEND":
        return False, f"last chunk is '{last_type}', not IEND (file likely truncated before the real end)"
    if not seen_ihdr or not width or not height:
        return False, "no valid IHDR / zero width or height"
    return True, f"{width}x{height}"


def _tracked_dirty_pngs() -> list[str]:
    """PNG paths currently recorded DIRTY in CODE_REVIEW_STATUS.json, via one
    batched `check` call (never one subprocess per path — see module docstring)."""
    import json
    status = json.loads((REPO_ROOT / "infrastructure/state/CODE_REVIEW_STATUS.json").read_text())
    all_pngs = [p for p in status if p.endswith(".png")]
    if not all_pngs:
        return []
    # check's own exit code is 1 whenever ANY path is DIRTY -- that is the
    # expected, normal outcome here (we are LOOKING for the dirty ones), not
    # a tool failure, so this deliberately does not use check=True.
    out = subprocess.run(
        [sys.executable, str(STATUS_SCRIPT), "check", *all_pngs],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout
    dirty = []
    for line in out.splitlines():
        # cmd_check's own format: f"DIRTY  {rel}  ({detail})" -- state, two
        # spaces, path, two spaces, one parenthetical detail. NOT the same
        # shape as `list`'s output (which wraps the reason differently) --
        # do not reuse a parser written against `list` here.
        if not line.startswith("DIRTY  "):
            continue
        rest = line[len("DIRTY  "):]
        detail_start = rest.rfind("  (")
        path = rest[:detail_start] if detail_start != -1 else rest.strip()
        dirty.append(path.strip())
    return dirty


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--dirty-from-status", action="store_true",
                     help="probe every currently-DIRTY tracked .png instead of an explicit path list")
    ap.add_argument("--mark-clean", action="store_true",
                     help="mark-clean every file that PASSES (only meaningful with --dirty-from-status, "
                          "or when the given paths are already recorded and committed)")
    args = ap.parse_args()

    if args.dirty_from_status:
        paths = _tracked_dirty_pngs()
        print(f"probing {len(paths)} DIRTY .png file(s) from CODE_REVIEW_STATUS.json", file=sys.stderr)
    else:
        paths = args.paths
    if not paths:
        print("nothing to probe", file=sys.stderr)
        return 0

    failures = []
    passed = []
    for rel in paths:
        p = REPO_ROOT / rel
        ok, detail = probe_one(p)
        if ok:
            passed.append(rel)
            print(f"PASS  {rel}  ({detail})")
        else:
            failures.append((rel, detail))
            print(f"FAIL  {rel}  -- {detail}")

    print(f"\n{len(passed)} passed, {len(failures)} failed, {len(paths)} total", file=sys.stderr)

    if args.mark_clean and passed:
        marked = 0
        for rel in passed:
            r = subprocess.run(
                [sys.executable, str(STATUS_SCRIPT), "mark-clean", rel],
                cwd=REPO_ROOT, capture_output=True, text=True,
            )
            if r.returncode == 0:
                marked += 1
            else:
                print(f"mark-clean FAILED for {rel}: {r.stderr.strip()}", file=sys.stderr)
        print(f"mark-clean: {marked}/{len(passed)} succeeded", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
