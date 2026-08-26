# STRAY_COLONISTS_IN_JAWA_FACTIONS_1 — not extra pawns, and not reproducible

2026-08-26, seat CHECK, live Ash'karr, full 582-mod list, same map and session as the sighting.

## ⚠️ First, a correction to my own filing: they were SUBSTITUTIONS, not additions

I filed this as *"the map gained 5 pawns that were never requested"*. The arithmetic says
otherwise, and it is exact:

```
requested Jawa_Tribal_Scavenger : 6 + 6 + 8 = 20
on the map afterwards           : Jawa_Tribal_Scavenger 16  +  Colonist/"Jawa Trade Moot" 4  = 20
requested Jawa_Geonosian_Grunt  : 2
on the map afterwards           : Jawa_Geonosian_Grunt   1  +  Colonist/"Geonosian Foundry Hive" 1 = 2
```

⇒ **Nothing extra appeared.** 5 of 22 requested pawns came out as kind `Colonist`, xenotype
`Baseliner`, in the right faction. Per call: run 1 gave 3 of 6, run 2 gave 5 of 6, run 3 gave
8 of 8.

## Controlled re-run: 19 spawns, ZERO substitutions

```
10 x count=1  Jawa_Tribal_Scavenger  -> reported 1, appeared 1, unasked 0   (every run)
 2 x count=6  Jawa_Tribal_Scavenger  -> reported 6, appeared 6, unasked 0
 1 x count=2  Jawa_Geonosian_Grunt   -> reported 2, appeared 2, unasked 0
```

Full `jawa/list_pawns` census immediately before and after each spawn, ids diffed against the
tool's own reported ids. **19 for 19 correct.** The substitution did not recur in any shape —
neither the `count=1` shape nor the `count=6` shape that produced it.

## What it is NOT — measured, so nobody re-derives it

`jawa/spawn_pawn` calls `PawnGenerator.GeneratePawn(kind, fac)` **verbatim, with no fallback kind**
(`JawaBenchTerrainTools.cs:1806`); a generation that throws is caught into an `ok:false` row and
no pawn spawns. On run 3 its own per-pawn rows came back **8 `ok:true` with 8 ids**, and every id
read back as `Jawa_Tribal_Scavenger`/`MandrakeJawa`. The tool is not substituting and is not
miscounting.

## Verdict

🔑 **UNMEASURED as to cause, and honestly so.** 5 substitutions in 22 spawns early in the session,
0 in 19 spawns afterwards, on the same map, same faction, same kind, same paused tick. I have no
mechanism and I am not shipping a theory. The observation is recorded with its arithmetic so a
future sighting can be recognised rather than re-derived.

⚙️ **If it recurs:** the row to capture is `jawa/spawn_pawn`'s own `pawns[]` — if a row reports
`ok:true` with an id that later reads back as `Colonist`, the substitution is inside
`PawnGenerator` and the next step is `Player.log` across that exact window for the mod that did it
(**Isekai Forge** is hooked into pawn generation on this list and logs by pawn name). If instead the
reported id is simply absent from the map, the problem is in the tool.
