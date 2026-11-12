#!/usr/bin/env python3
"""Render the three AgariluxPrime pictures side by side, read from the commit before the change (two no longer exist in src)."""
import io, subprocess, sys
from PIL import Image, ImageDraw
C = subprocess.run(["git", "log", "-1", "--format=%H", "--grep=AGARILUX_PRIME_COPIES_RECONCILE_SPLIT: TheRot owns"], capture_output=True, text=True).stdout.strip()
fs = [("drawn: TheRot RotSpecies/AgariluxPrime 4096 (survivor)", "src/RimMandrake/TheRot/Textures/RotSpecies/AgariluxPrime.png"),
      ("never drawn: TheRot Things/Plants/AB_ 256 (gptredo ACCEPT, retired)", "src/RimMandrake/TheRot/Textures/Things/Plants/AB_AgariluxPrime.png"),
      ("never drawn: UtinniPatches Things/Plants/AB_ 384 (gptredo REGEN, retired)", "src/RimUtinni/UtinniPatches/Textures/Things/Plants/AB_AgariluxPrime.png")]
S = 480; out = Image.new("RGB", (S * 3 + 40, S + 40), (60, 70, 60)); d = ImageDraw.Draw(out)
for i, (lab, f) in enumerate(fs):
    data = subprocess.run(["git", "show", f"{C}^:{f}"], capture_output=True).stdout
    im = Image.open(io.BytesIO(data)).convert("RGBA").resize((S, S), Image.LANCZOS)
    bg = Image.new("RGBA", (S, S), (110, 120, 100, 255)); bg.alpha_composite(im)
    out.paste(bg.convert("RGB"), (10 + i * (S + 10), 30)); d.text((10 + i * (S + 10), 8), lab, fill=(255, 255, 255))
out.save(sys.argv[1])
