# AutomatedSmelter - kludged - north

_Written by Source/briefs.py from MANIFEST.json. Re-run it; do not hand-edit._

Run from src/RimMandrake/WreckedMachines/. Donor file: `AutomatedSmelter_north.png` (512x640). Generate at **1120 x 1408**; fit_sprite.py brings it to the donor canvas.

## Attach, in this order

1. `art_source/AutomatedSmelter/wrecked/AutomatedSmelter_north.png`  (the FITTED Wrecked facing: run fit_sprite --apply on it first)

## Prompt (exactly what is sent; also in `KLUDGED_north.txt`)

```
Edit image 1. Image 1 is the north facing of the machine. Keep exactly this facing, orientation and position on the canvas.
It is a wrecked smelting furnace: a domed furnace on a square plinth with a heat ring round the dome, an intake belt at the top and three output belts along the bottom edge, a building from a top-down colony game. That description is of its south face. Image 1 is its north face, so every part stays exactly where image 1 has it.

Draw this same wreck brought back into service by scavengers with salvage:
- each hole of image 1 is closed with a bolted patch plate of a different metal, plainly a different colour and wear from the housing around it;
- hand-spliced cable runs, clamped and taped, lie flat across the body from one part to another;
- one plain bodge: a salvaged box or pump strapped onto the body, inside its outline;
- it is plainly working: the heat ring glows a dull working orange through its patched seams, and a few small added indicator lamps are lit;
- the conveyor belts and the intake are clear and running: their slats are clean and run the same way as in image 1, and the arrow mark beside each belt is bright and points exactly the way it points in image 1; the belts carry no other arrows or chevrons;
- bent frames stay bent and rust stays wherever no patch covers it.

The camera is the game's building camera: orthographic, looking down at about 35 degrees, the same as image 1.
The machine fills the same footprint as in image 1, at the same size and in the same place. Every edge of the machine sits on or inside the outline of image 1. Wherever image 1 is transparent, the output is transparent too: the notches and gaps in image 1's outline, such as the empty corners beside a belt that juts out, stay empty.
The background is fully transparent: only the machine's own pixels are drawn, and its edges are drawn the same way as the edges of image 1.
Output one image, 1120 x 1408 pixels, the same proportions as image 1.
```

## Commands

```bash
python3 ~/dev/MandrakeWorkflows/skills/generating-images/scripts/codex_image.py edit --out art_source/AutomatedSmelter/kludged/AutomatedSmelter_north.png --timeout 520 --prompt "$(cat art_source/AutomatedSmelter/briefs/KLUDGED_north.txt)" --image art_source/AutomatedSmelter/wrecked/AutomatedSmelter_north.png
python3 Source/fit_sprite.py AutomatedSmelter --tier kludged --facing north --inside --apply
python3 Source/check_sprite.py AutomatedSmelter --tier kludged
```

Then look at the fitted picture. One Codex call per run of the first command; redo a facing at most twice.
