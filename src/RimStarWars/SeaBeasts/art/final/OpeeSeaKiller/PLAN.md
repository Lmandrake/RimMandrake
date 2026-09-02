<!-- SW_SEA_MONSTERS_ART_1 pilot — offline art only, no def written, nothing deployed.
     Source mockup: src/RimStarWars/SeaBeasts/art/mockups/opee_opt1.png (opee_opt1,
     roster: design/Jawa/worldbuilding/sea_beasts_roster.md, size 1.4). -->
# Opee sea killer — facing set validation plan

🔴 **The §2 LIES line below came true and is now ANSWERED.** `sea_beasts_def_spec.md`
§5.1 ships `RSW_OpeeSeaKiller` at **drawSize 2.25**, not the 1.4 this canvas was
budgeted from. 2.25 × 128 px/cell = 288 px ⇒ the correct canvas is **512x512**, and
these four PNGs are 256x256. Not a blocker: RimWorld scales the texture to
`drawSize`, so the sprite draws at the right footprint and is merely blockier than
its two siblings (`CrimsonOpee`, `ShaleGorger`, both 512). Rebuilding it is two
image calls through `../../tools/gen_sea_facings.py OpeeSeaKiller`; see
`../README.md` for why that is currently blocked.

Canvas: 256x256 per facing (1.4 cells x 128px/cell = 179.2px, rounded up to the
next power of two = 256). No prior shipped reference exists for this creature —
every check below is candidate-vs-candidate, not against a prior sprite.

## 1. Offline (done, this commit)

```
PROVE    validate_sprite.py --reference <facing>.png --describe, all four
         facings (south/east/north/west)
EXPECT   canvas 256x256, alpha yes, corners [0,0,0,0], fringe reach 0.0000,
         spill delta negative (no green bleed), fragment fraction 0.0000,
         mid-tone < 8%
LIES     describe() alone doesn't print spill/reach/fragment — a human
         glancing only at "coverage/alpha mix" could miss a rejected-grade
         defect; the numbers above were pulled via validate_sprite.measure()
         directly and all four passed clean (see recipe report).
```

Measured: south 25.8% coverage, east 20.6%, north 17.2%, west 20.6% (mirror of
east). All four: fringe reach 0.0000, spill delta -38.8 to -42.9 (well under
the +24 REJECT-adjacent threshold, and negative means no green residue),
fragment fraction 0.0000 (one connected mass, no stray blobs).

## 2. In-game — owed, not yet done (no ThingDef exists for this creature yet)

```
PROVE    spawn a ThingDef using OpeeSeaKiller_south/_east/_north/_west.png as
         its Graphic_Multi texPath set (defName TBD — SW_SEA_MONSTERS_ART_1 has
         not authored the def yet), rotate through all four facings at default
         zoom
EXPECT   a top-down armored crab-anglerfish silhouette that reads as ONE
         creature across all four rotations — mouth-forward on south, spiny
         dorsal ridge in profile on east/west (mirrored), armored back with
         antennae visible on north; no green fringe, no magenta, no
         Graphic_Multi invisibility
LIES     the bare-path fallback (Graphic_Multi.Init calls ContentFinder.Get on
         the path WITHOUT the _north/_south suffix before erroring) will
         silently draw one facing for all four if the deploy path is wrong —
         name the exact facing looked at, not "the creature looks right"
LIES     drawSize was taken directly from the roster's "size" column (1.4) per
         this task's instruction; if the def later ships a different drawSize
         than 1.4, this 256x256 canvas is the WRONG budget and must be
         recomputed (128px/cell, round up to power of two) before that def
         ships
```

## What is explicitly out of scope here

- No ThingDef/CompProperties authored — this is art only, per task scope.
- No deployment, no ModsConfig.xml touch, no commit/push — the parent handles
  that.
- Palette/style judgment ("is this GOOD") is Fable-tier review territory per
  the skill, not this pilot; this plan only proves the file is shippable.
