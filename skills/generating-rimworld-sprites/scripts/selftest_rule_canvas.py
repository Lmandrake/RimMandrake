#!/usr/bin/env python3
"""selftest_rule_canvas.py — validate_sprite.py accepts an exact-multiple canvas ONLY when it is the def's rule canvas
(ARTEVAL_VALIDATOR_FIX_REFUSES_HIRES_REDRAW, 2026-10-24).

The owner asked for higher-resolution redraws of Vexxiss D/E (512 px art, drawSize 7 -> rule canvas 1024). The
renders were exactly twice the reference and were refused on "canvas != reference" and "+100% width". With
--drawsize the validator derives the rule canvas exactly as the pipeline's size code does
(artpipe.common.canvas_for_cells) and, when the candidate sits on that canvas at an exact integer multiple (or
divisor) of the reference, judges geometry against the reference SCALED to the candidate's canvas. Every other
size stays refused, and every geometry check still bites on the scaled reference. artpiped passes the job's
drawsize through. Synthetic fixtures; no repo art read.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_sprite.py"
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1] / "generating-images" / "scripts"))
import pnglib  # noqa: E402

FAILS = []


def check(cond, msg, extra=""):
    print(("PASS " if cond else "FAIL ") + msg + (f"  [{extra}]" if (extra and not cond) else ""))
    if not cond:
        FAILS.append(msg)


def blob(w, h, x0, y0, bw, bh):
    """An opaque two-tone creature-ish block on a transparent canvas (antialias-free, so scaling is exact)."""
    px = bytearray(w * h * 4)
    for y in range(y0, y0 + bh):
        for x in range(x0, x0 + bw):
            i = (y * w + x) * 4
            px[i:i + 4] = bytes((120, 80, 40, 255)) if (x - x0) < bw // 2 else bytes((90, 110, 60, 255))
    return px


def write(d: Path, name, w, h, px):
    p = d / f"{name}.png"
    pnglib.write_rgba(str(p), w, h, px)
    return p


def validate(ref, cand, *extra):
    proc = subprocess.run([sys.executable, str(VALIDATOR), "--reference", str(ref), "--candidate", str(cand), *extra],
                          capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def main():
    d = Path(tempfile.mkdtemp(prefix="rule-canvas-"))
    # reference 128 px, subject 60x40 at (30,50); drawSize 2 -> rule canvas 256 (ceil_pow2(2*128)), 2x the reference
    ref = write(d, "ref128", 128, 128, blob(128, 128, 30, 50, 60, 40))
    up2 = write(d, "up2_256", 256, 256, blob(256, 256, 60, 100, 120, 80))           # exact 2x redraw

    rc, out = validate(ref, up2)
    check(rc == 1 and "canvas is 256x256" in out, "no --drawsize: a 2x canvas is still refused (unchanged)", out[-200:])

    rc, out = validate(ref, up2, "--drawsize", "2")
    check(rc == 0, "--drawsize 2 (rule 256): an exact 2x redraw on the rule canvas passes", out[-300:])
    check("rule canvas" in out.lower(), "…and says it judged against the rule canvas", out[-300:])

    rc, out = validate(ref, up2, "--drawsize", "7")
    check(rc == 1 and "canvas" in out, "--drawsize 7 (rule 1024): a 256 canvas is NOT the rule canvas -> refused",
          out[-200:])

    # wrong size art is not weakened
    same_px = write(d, "notscaled_256", 256, 256, blob(256, 256, 30, 50, 60, 40))   # canvas grew, subject did not
    rc, out = validate(ref, same_px, "--drawsize", "2")
    check(rc == 1 and "subject width" in out, "rule canvas but subject NOT scaled: refused on span", out[-300:])

    shifted = write(d, "shifted_256", 256, 256, blob(256, 256, 140, 100, 120, 80))
    rc, out = validate(ref, shifted, "--drawsize", "2")
    check(rc == 1 and "origin" in out, "rule canvas, scaled subject, moved: refused on origin", out[-300:])

    over = write(d, "over_256", 256, 256, blob(256, 256, 60, 100, 150, 80))
    rc, out = validate(ref, over, "--drawsize", "2")
    check(rc == 1 and "exceeds the reference" in out, "rule canvas, subject 25% too wide: refused", out[-300:])

    ref96 = write(d, "ref96", 96, 96, blob(96, 96, 20, 30, 50, 30))
    rc, out = validate(ref96, up2, "--drawsize", "2")
    check(rc == 1 and "canvas" in out, "rule canvas but NOT an exact multiple of the reference (96 -> 256): refused",
          out[-200:])

    rect_ref = write(d, "ref128x64", 128, 64, blob(128, 64, 30, 10, 60, 40))
    rc, out = validate(rect_ref, up2, "--drawsize", "2")
    check(rc == 1 and "canvas" in out, "unequal scale per axis (128x64 -> 256x256): refused", out[-200:])

    # downscale onto the rule canvas: reference 512 (2x the rule for drawSize 2), candidate 256
    ref512 = write(d, "ref512", 512, 512, blob(512, 512, 120, 200, 240, 160))
    rc, out = validate(ref512, up2, "--drawsize", "2")
    check(rc == 0, "a reference at 2x the rule, candidate exactly on the rule canvas (1/2): passes", out[-300:])

    rc, out = validate(ref, up2, "--drawsize", "abc")
    check(rc == 2, "an unparseable --drawsize is unusable input (exit 2), never a verdict", out[-200:])

    # the real Vexxiss shape: drawSize 7 -> 1024, reference 512
    ref_v = write(d, "refv512", 512, 512, blob(512, 512, 35, 60, 441, 300))
    cand_v = write(d, "candv1024", 1024, 1024, blob(1024, 1024, 70, 120, 882, 600))
    rc, out = validate(ref_v, cand_v, "--drawsize", "7")
    check(rc == 0, "Vexxiss shape: 512 reference, drawSize 7, exact 2x 1024 redraw passes", out[-300:])

    # artpiped passes the job's drawsize through
    sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils" / "artpipe"))
    import artpiped
    stub = d / "stub_validator.py"
    stub.write_text("import sys\nprint(' '.join(sys.argv[1:]))\nsys.exit(0)\n")
    try:
        verdict, findings = artpiped.run_validator(stub, str(ref), up2, drawsize=7.0)
    except TypeError as e:
        verdict, findings = "TypeError", [str(e)]
    check(verdict == "pass" and any("--drawsize 7.0" in f for f in findings),
          "artpiped.run_validator passes --drawsize to the validator", str(findings)[:200])
    verdict, findings = artpiped.run_validator(stub, str(ref), up2)
    check(verdict == "pass" and not any("--drawsize" in f for f in findings),
          "…and omits it when the job has none", str(findings)[:200])

    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
