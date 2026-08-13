# Brief 3 of 3 — REPAIRED

_Generated from the live ThingDef. Do not hand-edit; re-run `Source/briefs.py`._

**Attach: the image you produced in Brief 2 (the kludged sheet).** This step finishes the repair that Brief 2 started.

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

The crew has finished the job. This machine works properly now — but it was rebuilt by scavengers out of what they had, and it will never look factory-fresh again.

Starting from the kludged version:

- **Fill in every remaining hole with metal of a visibly different colour.** Patch plates and replacement panels in mismatched alloys — brighter, duller, differently weathered than the original housing. The repairs should be obvious as repairs.
- **Tidy the cabling.** The lashed-on hoses and cables from Brief 2 are now routed **semi-neatly, plugging from one part of the device to another** — proper runs between real connection points, clipped down, deliberate. Still clearly aftermarket, no longer chaos.
- **Keep some escaping smoke vents.** A few improvised exhausts still venting steam or smoke. This machine breathes through holes its designers did not put there.
- Remove the open flame. Nothing should be burning any more.
- Bring the indicator lights back to steady, working illumination.
- Clean up the worst corrosion where the crew has worked, but leave the machine visibly old and hard-used.

The read at a glance: **functional, cared for, and unmistakably rebuilt from a wreck.**

⚠️ Rule 3 still applies to the tidied cabling: routed **across the body**, never looping outside the outline.

## What to return

**One image.** Same dimensions, same 2x2 layout, all four facings modified consistently.

## After you deliver it

_(For the human, not the model.)_ Save the returned image, then:

```bash
python Source/sheet.py split AutomatedSmelter --tier repaired --sheet <the-returned-file> --then-fit
python Source/check_sprite.py AutomatedSmelter --tier repaired
```

`split` cuts the sheet into four facings, `fit_sprite` conforms each one to its own reference canvas and pose, and `check_sprite` refuses anything that would waste a game load. The cut does not need to be pixel-perfect — the fitter registers each facing against the original afterwards.
