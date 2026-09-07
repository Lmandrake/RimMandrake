#!/usr/bin/env python3
"""One command: Codex generate/edit -> (optional) conform to a reference canvas.

There is no cutout stage any more. The built-in $imagegen tool emits a real
alpha channel when the prompt asks for one (MEASURED 2026-09-06: 1448x1086
RGBA, 55.7% alpha-0, all four corners (0,0,0,0), 0.28% mid-alpha, no rim or
halo), which is cleaner than either the chroma-key cut or the rembg cut that
used to sit here - and it removes both of the failure modes that have destroyed
subjects on this project: a key colour that was also in the art, and an
auto-detected "key" that was really banked alpha.

Ask for transparency IN THE PROMPT. `conform_sprite.py` stays mandatory,
because the tool still ignores the size you ask for.

  # fresh generation
  python3 skills/generating-images/scripts/make_sprite.py \
      --prompt "a rusty derelict smelter, top-down game sprite, genuinely
                transparent background, real alpha channel, no floor, no shadow" \
      --out out/smelter.png

  # edit/variant from a hero image (reference-conditioned)
  python3 .../make_sprite.py --edit-image hero_south.png \
      --prompt "same machine, east side view, top-down" --out out/east.png

  # conform to a reference sprite's canvas/registration (RimWorld facings)
  python3 .../make_sprite.py --prompt "..." --out final.png \
      --reference original_south.png

Flags: --keep-raw (keep the pre-conform image), --codex-home DIR (isolate this
call's CODEX_HOME so parallel workers cannot collide), --timeout S.

For a channel with NO native alpha - `gemini_image.py` - cut the background
locally with `rembg_cut.py` under ~/.venvs/rwgfx instead.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODEX = os.path.join(HERE, "codex_image.py")
CONFORM = os.path.join(REPO, "skills", "generating-rimworld-sprites", "scripts", "conform_sprite.py")


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
    ap.add_argument("--reference", help="conform the result to this sprite's canvas/registration")
    ap.add_argument("--codex-home", help="isolate this call's CODEX_HOME (parallel workers)")
    ap.add_argument("--timeout", help="seconds before the wrapper stops waiting")
    ap.add_argument("--keep-raw", action="store_true")
    a = ap.parse_args()

    base = os.path.splitext(a.out)[0]
    raw = a.out if not a.reference else base + ".raw.png"

    # 1. Codex generate or edit
    if a.edit_image:
        cmd = ["python3", CODEX, "edit", "--out", raw, "--prompt", a.prompt]
        for img in a.edit_image:
            cmd += ["--image", img]
    else:
        cmd = ["python3", CODEX, "generate", "--out", raw, "--prompt", a.prompt]
    if a.codex_home:
        cmd += ["--codex-home", a.codex_home]
    if a.timeout:
        cmd += ["--timeout", a.timeout]
    run(cmd)

    # 2. optional conform to a reference sprite
    if a.reference:
        run(["python3", CONFORM, "--reference", a.reference, "--input", raw, "--out", a.out])
        if not a.keep_raw:
            try: os.remove(raw)
            except OSError: pass

    print("DONE -> %s" % a.out)


if __name__ == "__main__":
    main()
