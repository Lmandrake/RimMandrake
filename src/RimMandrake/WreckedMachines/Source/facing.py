#!/usr/bin/env python3
"""facing.py: make one facing of one tier in one command (MACHINES.md "How a picture is made"). Dev tooling, not shipped.

    python3 Source/facing.py <Short> <tier> <facing> --tag t1 [--root DIR] [--redo] [--no-call]
    python3 Source/facing.py <Short> view [--root DIR]      one sheet of every fitted facing: donor | wrecked | kludged

Run from src/RimMandrake/WreckedMachines/. <tier> is wrecked, kludged or icon; <facing> is north, south, east, west (an
icon or a machine that does not turn: the facing its brief is named for). It reads the brief
<root>/<Short>/briefs/<TIER>_<facing>.md, which Source/briefs.py wrote, and runs the brief's own three commands:

  1. the image call (one Codex call through the Codex door), unless --no-call (fit a raw picture that is already there);
  2. fit_sprite.py --apply;
  3. check_sprite.py for the tier.

Then it writes the look sheet <root>/<Short>/_view/<tier>_<facing>_<tag>.png: donor | fitted | overlay (the fitted picture
on grey, its pixels outside the donor outline grown by 2 px in magenta, the donor outline in cyan). For a kludged facing
the sheet has a fourth panel, the fitted Wrecked facing it was edited from.

--redo moves the facing's present fitted and raw picture to <tier>/_rejected/ (named with --tag) before the call. Without
--redo it refuses to draw over a fitted facing.

Each step's whole output is in <root>/<Short>/_log/<tier>_<facing>_<tag>.<step>.txt. The last line is the verdict:
  FACING <Short> <tier> <facing> <tag>: CALL ok|FAILED|skipped, FIT ok|REFUSED|not run, CHECK ok|warn|FAIL|not run, VIEW <path>
Exit 0 the fitted picture is there and the check did not FAIL; 1 a step failed (the line says which); 2 could not start
(no brief, a fitted facing in the way).
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
FACINGS = ("north", "south", "east", "west")
# Hang guards, not speed bars: the longest real call on record is 240 s (the door's own --timeout in the brief is 520 s);
# the longest fit on record is 95 s and the longest check 20 s (Autoloom pilot, 2026-11-27). Each guard is over 10 times
# the record, and the image door waits up to an hour for a free slot when five calls are out at once.
CALL_GUARD_S = 3600 + 2400
FIT_GUARD_S = 1800
CHECK_GUARD_S = 600


def root_of(arg):
    return os.path.abspath(arg or os.environ.get("WM_ART_ROOT") or os.path.join(MOD, "art_source"))


def brief_commands(path):
    """The three command lines of a brief: (call, fit, check)."""
    text = open(path, encoding="utf-8").read()
    call = re.search(r"^python3 \S*codex_image\.py edit .*$", text, re.M)
    fit = re.search(r"^python3 Source/fit_sprite\.py .*$", text, re.M)
    chk = re.search(r"^python3 Source/check_sprite\.py .*$", text, re.M)
    if not (call and fit and chk):
        raise SystemExit("COULD NOT START: %s does not hold the three commands (re-run Source/briefs.py)" % path)
    return call.group(0), fit.group(0), chk.group(0)


def run(cmd, log, guard):
    t = time.time()
    try:
        p = subprocess.run(["bash", "-c", "set -o pipefail; " + cmd], cwd=MOD, capture_output=True, text=True, timeout=guard)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = ((e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")) + \
            "\nUNMEASURED: stopped by facing.py's hang guard of %d s\n" % guard, 124
    with open(log, "w", encoding="utf-8") as f:
        f.write("$ %s\n%s\nrc=%d seconds=%.0f\n" % (cmd, out, rc, time.time() - t))
    return rc, out, time.time() - t


def _rgba(path):
    from PIL import Image
    return Image.open(path).convert("RGBA")


def _panel(im, bg=110):
    from PIL import Image
    base = Image.new("RGBA", im.size, (bg, bg, bg, 255))
    base.alpha_composite(im)
    return base


def _overlay(donor, fitted):
    import numpy as np
    from PIL import Image, ImageFilter
    d = np.asarray(donor)[..., 3] > 24
    f = np.asarray(fitted)[..., 3] > 24
    grown = np.asarray(Image.fromarray((d * 255).astype("uint8")).filter(ImageFilter.MaxFilter(5))) > 0
    out = np.asarray(_panel(fitted)).copy()
    out[grown & ~d] = (0, 255, 255, 255)
    out[f & ~grown] = (255, 0, 255, 255)
    return Image.fromarray(out)


def look_sheet(out, donor_path, fitted_path, extra=()):
    from PIL import Image
    donor, fitted = _rgba(donor_path), _rgba(fitted_path)
    panels = [_panel(donor), _panel(fitted)]
    if donor.size == fitted.size:
        panels.append(_overlay(donor, fitted))
    panels += [_panel(_rgba(p)) for p in extra if os.path.isfile(p)]
    w, h = sum(p.width for p in panels), max(p.height for p in panels)
    sheet = Image.new("RGBA", (w, h), (110, 110, 110, 255))
    x = 0
    for p in panels:
        sheet.paste(p, (x, 0))
        x += p.width
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.convert("RGB").save(out)
    return out


def donor_file(root, short, facing, stem=None):
    for name in ("%s_%s.png" % (stem or short, facing), "%s.png" % (stem or short)):
        p = os.path.join(root, short, "restored", name)
        if os.path.isfile(p):
            return p
    return None


def fitted_name(root, short, tier, facing):
    """The fitted file of a facing: <Short>_<facing>.png, or <Short>.png for a thing with one picture."""
    d = os.path.join(root, short, tier)
    for name in ("%s_%s.png" % (short, facing), "%s.png" % short):
        if os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    return os.path.join(d, "%s_%s.png" % (short, facing))


def whole_view(root, short):
    """Every fitted facing on one sheet: a row for each facing, donor | wrecked | kludged (or donor | icon)."""
    from PIL import Image
    rows = []
    for facing in FACINGS:
        donor = donor_file(root, short, facing)
        cells = [donor] + [fitted_name(root, short, t, facing) for t in ("wrecked", "kludged", "icon")]
        cells = [c for c in cells if c and os.path.isfile(c)]
        if len(cells) > 1 and cells not in rows:
            rows.append(cells)
    if not rows:
        raise SystemExit("COULD NOT LOOK: no fitted facing under %s" % os.path.join(root, short))
    ims = [[_panel(_rgba(c)) for c in r] for r in rows]
    w = max(sum(i.width for i in r) for r in ims)
    h = sum(max(i.height for i in r) for r in ims)
    sheet = Image.new("RGBA", (w, h), (110, 110, 110, 255))
    y = 0
    for r in ims:
        x = 0
        for i in r:
            sheet.paste(i, (x, y))
            x += i.width
        y += max(i.height for i in r)
    out = os.path.join(root, short, "_view", "ALL.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.convert("RGB").save(out)
    print("VIEW %s (%dx%d): %d row(s), each donor then the fitted tiers" % (out, w, h, len(rows)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("short")
    ap.add_argument("tier")
    ap.add_argument("facing", nargs="?")
    ap.add_argument("--tag", default="t1")
    ap.add_argument("--root")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--no-call", action="store_true")
    a = ap.parse_args()
    root = root_of(a.root)
    if a.tier == "view":
        whole_view(root, a.short)
        return 0
    if not a.facing:
        raise SystemExit("COULD NOT START: name the facing")
    brief = os.path.join(root, a.short, "briefs", "%s_%s.md" % (a.tier.upper(), a.facing))
    if not os.path.isfile(brief):
        raise SystemExit("COULD NOT START: no brief %s (run Source/grab_source_art.py for this machine with --root)" % brief)
    call, fit, chk = brief_commands(brief)
    out_m = re.search(r"--out (\S+)", call)
    target = out_m.group(1) if out_m else fitted_name(root, a.short, a.tier, a.facing)
    tdir = os.path.dirname(target)
    raw = os.path.join(tdir, "_raw", os.path.basename(target))
    logs = os.path.join(root, a.short, "_log")
    os.makedirs(logs, exist_ok=True)
    stem = os.path.join(logs, "%s_%s_%s" % (a.tier, a.facing, a.tag))
    if os.path.isfile(target) and not a.no_call:
        if not a.redo:
            print("COULD NOT START: %s is already there; pass --redo to move it to _rejected/ and draw again" % target)
            return 2
        rej = os.path.join(tdir, "_rejected")
        os.makedirs(rej, exist_ok=True)
        base = os.path.splitext(os.path.basename(target))[0]
        os.replace(target, os.path.join(rej, "%s_before_%s_fitted.png" % (base, a.tag)))
        if os.path.isfile(raw):
            os.replace(raw, os.path.join(rej, "%s_before_%s_raw.png" % (base, a.tag)))
    if a.no_call and os.path.isfile(raw):
        os.replace(raw, target)                       # fit again from the raw picture: fit_sprite reads it at the target path
    verdict = {"CALL": "skipped", "FIT": "not run", "CHECK": "not run"}
    rc = 0
    if not a.no_call:
        crc, cout, secs = run(call, stem + ".call.txt", CALL_GUARD_S)
        ok = crc == 0 and os.path.isfile(target)
        verdict["CALL"] = "ok (%.0f s)" % secs if ok else "FAILED rc %d: %s" % (crc, (cout.strip().splitlines() or ["no output"])[-1][:160])
        rc = 0 if ok else 1
    if rc == 0:
        frc, fout, _ = run(fit, stem + ".fit.txt", FIT_GUARD_S)
        for line in fout.splitlines():
            if re.search(r"inside|register|WROTE|REFUS|keyed|rim |skew|fitted,", line):
                print("  fit:", line.strip())
        wrote = "WROTE" in fout and frc == 0
        verdict["FIT"] = "ok" if wrote else "REFUSED (rc %d; see %s.fit.txt)" % (frc, stem)
        rc = 0 if wrote else 1
    if rc == 0:
        krc, kout, _ = run(chk, stem + ".check.txt", CHECK_GUARD_S)
        name = os.path.basename(target)
        block, on = [], False
        for line in kout.splitlines():
            if re.match(r"\s*\[", line):
                on = name in line
            if on and line.strip():
                block.append(line.strip())
            if line.startswith("read "):
                print("  check:", line.strip())
        for line in block:
            print("  check:", line[:400])
        head = block[0] if block else ""
        verdict["CHECK"] = "FAIL" if "FAIL" in head else "warn" if "warn" in head else "ok" if "ok" in head else "could not read (see %s.check.txt)" % stem
        rc = 0 if verdict["CHECK"] in ("ok", "warn") else 1
    view = "-"
    if os.path.isfile(target) and verdict["FIT"] == "ok":
        donor = donor_file(root, a.short, a.facing)
        extra = [fitted_name(root, a.short, "wrecked", a.facing)] if a.tier == "kludged" else []
        if donor:
            view = look_sheet(os.path.join(root, a.short, "_view", "%s_%s_%s.png" % (a.tier, a.facing, a.tag)), donor, target, extra)
    print("FACING %s %s %s %s: CALL %s, FIT %s, CHECK %s, VIEW %s" % (a.short, a.tier, a.facing, a.tag, verdict["CALL"], verdict["FIT"], verdict["CHECK"], view))
    return rc


if __name__ == "__main__":
    sys.exit(main())
