# QUICKTEST_VISUAL_ROUND_1 — half answered, and the other half cannot be reached this way

**CHECK, 2026-08-21 ~17:50 PDT. 578 mods, dev-quicktest map.**

## Subject 1: the GRiNDTerra animals — ADULTS draw clean, JUVENILES are UNMEASURED

30 spawned: 15 `GRimTortoise` + 15 `GRimPinkbird` (GRiNDTerra Biomes), camera moved onto
them, ticks advanced so they render.

    jawa/drain_log contains="GRimTortoise"  -> 0 lines
    jawa/drain_log contains="GRimPinkbird"  -> 0 lines
    ...and the same for "Tortoise" / "Pinkbird" / lowercase

**No exception, no error, no warning naming either animal.** ✅ Adults draw.

🔴 **But the item is about JUVENILES, and all 16 sampled came back `Adult`** — tortoises
aged 13–103, pinkbirds 1–4. `jawa/spawn_pawn` has no age parameter, so the bridge's spawn
path cannot produce the juvenile the item asks about.

⛔ **And forcing one would not count.** `jawa/set_pawn_age` warns in its own description that
aging DOWN needs `allowBackwards`, which "uses the raw setter and SKIPS every birthday" —
leaving "a pawn in a state nothing produced". A draw failure on such a pawn would not be
evidence about the juvenile art, and a draw *success* would not be either.

⇒ **Recorded UNMEASURED, not passed.** Routes that might work, for whoever picks this up:
hatch an egg and tick, use RimWorld's own debug pawn-spawn tool through
`rimworld/execute_debug_action` if it exposes an age, or add an age argument to
`jawa/spawn_pawn` in the companion (needs the game down).

## Subject 2: the ash storm over a stormy-savanna tile — NOT ATTEMPTED
This map is `ExtremeDesert`-flavoured scratch terrain, not a stormy savanna tile, and no
weather was driven in this window. Untouched.

## Note on the screenshot trap
No screenshots were taken, so the trap did not bite — but it stands:
`rimworld/screenshot_cell_rect` photographs the **top window**, not the map, and has
returned four byte-identical PNGs of the Debug log across four `success: true` calls.
**Hash every screenshot before believing it.**

## Incidental: the log is full of gender-mismatch warnings
While ticking, the error buffer filled with

    Tried to calculate chance for father with gender "Female".
    Tried to calculate chance for mother with gender "Male".

repeating steadily. Consistent with the `Gestor`/`Phallor` finding in
`../rakata/README.md` — the same mod family, now visibly costing log volume every tick.
Filed there, not here.
