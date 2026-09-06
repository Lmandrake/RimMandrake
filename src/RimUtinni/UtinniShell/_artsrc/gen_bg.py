#!/usr/bin/env python3
"""
RimUtinni Shell — evocative art PROVENANCE (menu background + tactical loader).

The two large pieces are image-gen (Codex built-in $imagegen, chatgpt auth);
the atlases are procedural (see gen_textures.py). This file records the exact
prompts (provenance == the prompt, per project law) and the deterministic
downstream step (crop/upscale to the shipped canvas). Re-run REGENERATES the
raw art (image gen is non-deterministic — a re-run will differ); the prompts
below are the contract.

Raws land in _artsrc/raw/ (gitignored). Finals ship to:
  Textures/UI/Backgrounds/utinni_menu_1.png     2560x1440  (VBE menu background = Ishko gate)
  RimThemes/Utinni Shell/Loader/BGLoader.jpg    2560x1440  (RimThemes cold-load screen)

Generate the raws (Windows-visible cwd required, /mnt/d ok):
  python3 ../../../.claude/skills/generating-images/scripts/codex_image.py generate \
     --out raw/menu_ishko_raw.png --prompt "$MENU_PROMPT" --timeout 140
  python3 ... generate --out raw/loader_tactical_raw.png --prompt "$LOADER_PROMPT" --timeout 140
Then:  python3 gen_bg.py   # crops+upscales the raws to the shipped finals
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MOD  = os.path.dirname(HERE)
RAW  = os.path.join(HERE, "raw")
BG_OUT     = os.path.join(MOD, "Textures", "UI", "Backgrounds", "utinni_menu_1.png")
LOADER_OUT = os.path.join(MOD, "RimThemes", "Utinni Shell", "Loader", "BGLoader.jpg")

MENU_PROMPT = (
    "Cinematic wide establishing shot for a video game main menu, deep indigo-black "
    "night. A weathered desert temple gateway built from an ancient, lovingly-maintained "
    "starship hull section, half-buried in dune sand, dominates the lower center — "
    "aged grey-green gunmetal plating, riveted seams, NOT rusted or oxidised brown. "
    "Deep inside the black doorway, two burning amber-orange eyes glow like embers, the "
    "only bright light in the frame. Thin white vector-line schematic markings and small "
    "glowing amber instrument clusters are faintly visible embedded in the gunmetal "
    "door frame, like an old ship console built into the stone. Above and behind, a vast "
    "Star Wars desert night sky: faint dust, one enormous dim ringed planet low on the "
    "horizon, scattered cold stars. Mysterious, sacred, ominous, painterly concept art, "
    "high detail, atmospheric haze, strong negative space of dark sky in the upper two "
    "thirds for menu text. No characters, no text, no watermark."
)
LOADER_PROMPT = (
    "Wide full-screen loading screen for a Star Wars game, an amber-on-black tactical "
    "navigation display glowing on deep black, housed in a worn grey-green gunmetal "
    "instrument frame with visible rivets and thin white vector-line bracket corners. "
    "Concentric thin brass and amber orbital rings, radar sweep arcs, fine tick-mark "
    "scales around the rim, a small schematic wireframe starship in the upper left "
    "corner, faint blue trajectory lines crossing the center, glowing amber "
    "Aurebesh-style alien glyph labels scattered around the edges (decorative, "
    "unreadable). Everything drawn in luminous amber, brass gold and a little "
    "warning-red on pure black, like a holographic cockpit read-out on an ancient but "
    "well-kept ship's helm. Dark vignette edges, subtle scanline glow, high detail, "
    "atmospheric. No humans, no readable English text, no watermark."
)

def crop_to_16x9_and_upscale(src, dst, w=2560, h=2160 * 0 + 1440, jpg=False):
    im = Image.open(src).convert("RGB")
    # center-crop to 16:9 then Lanczos to the shipped canvas
    tw, th = w / h, im.width / im.height
    if th > tw:  # too wide
        nw = int(im.height * tw); x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:        # too tall
        nh = int(im.width / tw); y = (im.height - nh) // 2
        im = im.crop((0, y, im.width, y + nh))
    im = im.resize((w, h), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if jpg:
        im.save(dst, "JPEG", quality=92)
    else:
        im.save(dst, "PNG")
    print(f"{os.path.relpath(dst, MOD)}: {im.size}")

if __name__ == "__main__":
    crop_to_16x9_and_upscale(os.path.join(RAW, "menu_ishko_raw.png"), BG_OUT, jpg=False)
    crop_to_16x9_and_upscale(os.path.join(RAW, "loader_tactical_raw.png"), LOADER_OUT, jpg=True)
