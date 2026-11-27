# AutomatedSmelter - wrecked - south

_Written by Source/briefs.py from MANIFEST.json. Re-run it; do not hand-edit._

Run from src/RimMandrake/WreckedMachines/. Donor file: `AutomatedSmelter_south.png` (512x640). Generate at **1120 x 1408**; fit_sprite.py brings it to the donor canvas.

## Attach, in this order

1. `art_source/AutomatedSmelter/restored/AutomatedSmelter_south.png`

## Prompt (exactly what is sent; also in `WRECKED_south.txt`)

```
Edit image 1. Image 1 is the south facing of the machine. Keep exactly this facing, orientation and position on the canvas.
It is a smelting furnace: a domed furnace on a square plinth with a heat ring round the dome, an intake belt at the top and three output belts along the bottom edge, a building from a top-down colony game.

Draw this machine as a dead wreck, abandoned for decades:
- every lamp, screen and heat window is dark and cold; the metal is grey-brown, rusted and grimed;
- panels and plates are missing, so the dark inside shows through the gaps; corners are broken off; frames are bent; cables end in short cut stubs;
- the heat ring is cold black metal and the dome is rust-streaked with a section of its cap gone;
- the damage takes material away: the wreck is the original shape with pieces gone;
- the conveyor ends stay in their places, dusty and still.

The camera is the game's building camera: orthographic, looking down at about 35 degrees, the same as image 1.
The machine fills the same footprint as in image 1, at the same size and in the same place. Every edge of the machine sits on or inside the outline of image 1. Wherever image 1 is transparent, the output is transparent too: the notches and gaps in image 1's outline, such as the empty corners beside a belt that juts out, stay empty.
The background is fully transparent: only the machine's own pixels are drawn, and its edges are drawn the same way as the edges of image 1.
Output one image, 1120 x 1408 pixels, the same proportions as image 1.
```

## Commands

```bash
python3 ~/dev/MandrakeWorkflows/skills/generating-images/scripts/codex_image.py edit --out art_source/AutomatedSmelter/wrecked/AutomatedSmelter_south.png --timeout 520 --prompt "$(cat art_source/AutomatedSmelter/briefs/WRECKED_south.txt)" --image art_source/AutomatedSmelter/restored/AutomatedSmelter_south.png
python3 Source/fit_sprite.py AutomatedSmelter --tier wrecked --facing south --inside --apply
python3 Source/check_sprite.py AutomatedSmelter --tier wrecked
```

Then look at the fitted picture. One Codex call per run of the first command; redo a facing at most twice.
