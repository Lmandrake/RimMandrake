# Brief 2 of 3 — KLUDGED

_Generated from the live ThingDef. Do not hand-edit; re-run `Source/briefs.py`._

**Attach: the image you produced in Brief 1 (the wrecked sheet).** Not the original intact machine — this step modifies the *wreck*.

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

Scavengers have dragged this wreck back into service. Not repaired it — **forced it to work**, crudely, with whatever was to hand.

**Keep the wreck underneath.** Every hole, tear and corroded surface from Brief 1 is still there. You are adding *on top of* it, not cleaning it up. If a panel was missing, it is still missing — there is now something jury-rigged bridging the gap.

Add, generously and crudely:

- Salvaged pipes and conduit strapped across the body.
- Cable looms and hoses lashed on with clamps, wire and tape.
- Mismatched boxes, tanks, pumps and improvised housings bolted on.
- Bracing and props holding bent structure in place.
- Weld scars, patch plates over the smaller holes.

### 🔥 The signature of this step

**Openly escaping flame.** This machine is running when it should not be. Show fire venting from gaps it was never meant to vent from — flame licking out of a split seam, a torn panel, a broken joint. Some heat glow and a little smoke are right too.

This is the first step where the machine has power again, so a few improvised indicator lights are appropriate — but they should look *added*, not original.

⚠️ Flame and smoke count as part of the machine for rule 3: **they must not extend past the outline.** Keep plumes short and inside the shape.

It should look alarming — like it works, and like standing next to it is a bad idea.

## What to return

**One image.** Same dimensions, same 2x2 layout, all four facings modified consistently.

## After you deliver it

_(For the human, not the model.)_ Save the returned image, then:

```bash
python Source/sheet.py split AutomatedSmelter --tier kludged --sheet <the-returned-file> --then-fit
python Source/check_sprite.py AutomatedSmelter --tier kludged
```

`split` cuts the sheet into four facings, `fit_sprite` conforms each one to its own reference canvas and pose, and `check_sprite` refuses anything that would waste a game load. The cut does not need to be pixel-perfect — the fitter registers each facing against the original afterwards.
