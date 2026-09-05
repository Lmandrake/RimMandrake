#!/usr/bin/env python3
"""One command: Codex generate/edit -> rembg alpha cutout -> (optional) conform.

Replaces the old three-step chroma-key dance. Runs the two stages in the right
interpreters automatically (Codex via system python, rembg via the rwgfx venv).

  # fresh generation
  python3 skills/generating-images/scripts/make_sprite.py \
      --prompt "a rusty derelict smelter, top-down game sprite" \
      --out out/smelter.png

  # edit/variant from a hero image (reference-conditioned)
  python3 .../make_sprite.py --edit-image hero_south.png \
      --prompt "same machine, east side view, top-down" --out out/east.png

  # conform to a reference sprite's canvas/registration (RimWorld facings)
  python3 .../make_sprite.py --prompt "..." --out final.png \
      --reference original_south.png

Flags: --tight (crop to subject), --keep-raw (keep the pre-cutout image),
--chroma HEX (background key for generation, default #10e010 — a green the
subject is unlikely to contain; rembg removes it regardless).
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODEX = os.path.join(HERE, "codex_image.py")
REMBG_CUT = os.path.join(HERE, "rembg_cut.py")
CONFORM = os.path.join(REPO, "skills", "generating-rimworld-sprites", "scripts", "conform_sprite.py")
RWGFX_PY = os.path.expanduser("~/.venvs/rwgfx/bin/python")


def run(cmd):
    print("+ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("step failed (%d): %s" % (r.returncode, cmd[1] if len(cmd) > 1 else cmd[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--edit-image", action="append", help="reference image(s) for an edit; repeatable")
    ap.add_argument("--reference", help="conform the cutout to this sprite's canvas/registration")
    ap.add_argument("--chroma", default="#10e010")
    ap.add_argument("--tight", action="store_true")
    ap.add_argument("--keep-raw", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(RWGFX_PY):
        sys.exit("rwgfx venv missing at %s — create it and pip install rembg" % RWGFX_PY)

    base = os.path.splitext(a.out)[0]
    raw = base + ".raw.png"
    cut = a.out if not a.reference else base + ".cut.png"

    # 1. Codex generate or edit
    if a.edit_image:
        cmd = ["python3", CODEX, "edit", "--out", raw, "--prompt", a.prompt]
        for img in a.edit_image:
            cmd += ["--image", img]
    else:
        cmd = ["python3", CODEX, "generate", "--out", raw, "--prompt", a.prompt, "--chroma-key", a.chroma]
    run(cmd)

    # 2. rembg cutout (rwgfx venv)
    cmd = [RWGFX_PY, REMBG_CUT, "--input", raw, "--out", cut]
    if a.tight:
        cmd.append("--tight")
    run(cmd)

    # 3. optional conform to a reference sprite
    if a.reference:
        run(["python3", CONFORM, "--reference", a.reference, "--input", cut, "--out", a.out])
        if not a.keep_raw:
            for f in (raw, cut):
                try: os.remove(f)
                except OSError: pass
    elif not a.keep_raw:
        try: os.remove(raw)
        except OSError: pass

    print("DONE -> %s" % a.out)


if __name__ == "__main__":
    main()
