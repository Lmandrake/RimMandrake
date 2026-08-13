# Brief 1 of 3 — WRECKED

_Generated from the live ThingDef. Do not hand-edit; re-run `Source/briefs.py`._

**Attach:** `sheets/SOURCE_SHEET.png` — the intact machine.

## The image you are working on

One image, **1416 x 1416**, containing the same machine drawn from four directions in a 2x2 grid:

```
    +-----------------+-----------------+
    |     NORTH       |      EAST       |
    +-----------------+-----------------+
    |     SOUTH       |      WEST       |
    +-----------------+-----------------+
```

**Modify all four. They must agree with each other.** This is one physical machine seen from four sides — a hole torn in its left flank appears on the north view *and* on the south view, from the other side. Damage that exists in only one panel is the single most obvious way this fails.

The machine is an industrial **automated smelter** from a top-down colony game. It is seen from directly above at a slight angle.

## Rules that are not negotiable

**1. Return exactly the same image dimensions: 1416 x 1416.** Not larger, not cropped, not re-framed. Same 2x2 layout, same cell positions.

**2. Each machine must stay the same size within its cell.** Do not shrink the machine to make room for anything. Do not zoom in. If you overlay the result on the original, every machine should still cover the same area of its cell.

**3. ⛔ Nothing may extend beyond the machine's outline.** No hoses, cables, pipes, vents, antennae, smoke plumes or debris reaching outside the shape you were given.

   This is how the game works, not a style preference. The machine owns a fixed block of floor tiles — this one occupies **(3,4)** — and anything drawn outside that block overlaps whatever the player built next to it. It is also self-defeating: the art gets scaled back to the original footprint, so every pixel of cable sticking out shrinks the *machine itself* to make room. Measured on a first attempt at this machine, projecting cables cost the body 14% of its size.

   Everything you add must be bolted **onto the body, inside its existing outline**. Damage must be **subtractive** — chunks torn out, panels missing, corners blown away.

**4. Transparent background.** If you cannot produce transparency, use flat pure black `#000000` and nothing else — no gradient, no vignette, no shadow. Say which you did.

**5. Keep the art style.** Same rendering style, same palette family, same level of detail as the image supplied. This must look like it shipped in the same game.

## What to draw

Take this machine and make it a **long-dead wreck**. It has sat abandoned for a very long time. Nobody has maintained it, and scavengers have been at it.

- Heavy corrosion and rust across every surface.
- **Chunks missing.** Panels torn away, plating peeled back, corners broken off, holes punched through. Take material *out* of the outline — this is where the damage should read from a distance.
- Deformation: bent frames, sagging structure, buckled housings.
- Evidence of scavenging: fixtures stripped, access panels removed, cabling cut back to stubs.

### ⚡ The one absolute for this step

**NO lights. NO power signatures. NOTHING glowing, anywhere.**

The original has lit indicator strips and glowing status lamps. Every one of them must be **dark, dead, cracked or missing**. No orange glow, no green telltales, no illuminated panels, no residual heat, no sparks, no embers. This machine has had no power for years and must read as completely inert at a glance.

It should look like a monument, not a machine.

## What to return

**One image.** Same dimensions, same 2x2 layout, all four facings modified consistently.

## After you deliver it

_(For the human, not the model.)_ Save the returned image, then:

```bash
python Source/sheet.py split AutomatedSmelter --tier wrecked --sheet <the-returned-file> --then-fit
python Source/check_sprite.py AutomatedSmelter --tier wrecked
```

`split` cuts the sheet into four facings, `fit_sprite` conforms each one to its own reference canvas and pose, and `check_sprite` refuses anything that would waste a game load. The cut does not need to be pixel-perfect — the fitter registers each facing against the original afterwards.
