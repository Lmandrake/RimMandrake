# SCALD_WATER_AGITATION_FLECKS_1 — wreck shadow fix + ambient water agitation

Owner ruling, live SCALD_REVIEW walk 2026-09-25 (`--owner-said` on the filing
event has his verbatim words). Two things:

1. The three Scald wreck defs' shadows read as flat dark boxes on his walk.
   Root cause: all three inherit `ShipChunk`'s generic `shadowData.volume`
   (1.39,0.5,1.25) unmodified, despite having three distinct silhouettes of
   their own.
2. Margin-vs-shallow water is visually distinct but "faint" — noted, no
   change owed. He then asked for the boiling water to read more agitated,
   floated a walked-ripple-reuse idea himself, and gave a full three-way
   spec: margin calm, shallow lightly agitated, deep constantly agitated.

## done this pass
- **Wreck shadows**: measured each wreck's own alpha bbox
  (`RUT_ScaldWreckHull/Tank/Frame_A.png`, 256x256) — Hull 93%x80%, Tank
  96%x81%, Frame 93%x94% of canvas. Calibrated against `ShipChunk`'s own
  art-to-shadow ratio (its own art fills ~97-100% of its canvas for a
  (1.39,0.5,1.25) shadow on drawSize 2 → ~0.70x/0.63x of the sprite bbox) and
  applied that ratio per-wreck in `RUT_ScaldWrecks.xml`: Hull
  (1.30,0.5,1.01), Tank (1.34,0.5,1.02), Frame (1.30,0.5,1.18) — the taller,
  more-upright Frame now casts a visibly taller shadow than the two
  lying-flat wrecks, which was the actual defect (one box for three
  different silhouettes).
- **Ambient water agitation**: `RM_MapComponent_WaterAgitation`
  (`src/RimMandrake/EnvironmentalHazards/Source/`), generic and terrain-tag
  gated like every other mechanism in that kit — not Scald-hardcoded, any
  future biome's agitated water opts in with two tags. Reuses the ENGINE's
  own disturbance mote outright: `RimWorld.FleckMaker.WaterRipple(Vector3,
  Map, float)`, the exact call `Verse.PawnWaterRippleMaker` already fires
  every time a pawn wades through water (MEASURED against the decompiled
  engine before writing this, via RimSage — no new art, no new FleckDef, no
  new shader). Two new tags, `RM_WaterAgitationLight` /
  `RM_WaterAgitationHeavy`, added to `RUT_ScaldWater.xml`'s three shallow and
  three deep/chest-deep terrains respectively; `RUT_ScaldMargin` carries
  neither, so it stays calm. The component caches a per-tag cell list
  (hourly rescan, same cadence `RM_MapComponent_VaporColumns` uses) and rolls
  a random cell from each pool on its own randomized timer — light ~240-480
  ticks between ripples, heavy ~40-100 — INVENTED rates, the owner only said
  "a bit" vs "constant". New Mod Settings toggle #51,
  `waterAgitationEnabled` (default on, purely cosmetic either way, per the
  mod's own "every mechanism gets a master switch" law).
- Built clean (`dotnet build RM_EnvironmentalHazards.csproj -c Release`, 0
  warnings/0 errors). `TerminalBiomes` deployed and VERIFIED in sync.
  `EnvironmentalHazards`'s and `JawaRules`'s DLLs (the latter carries the
  already-built, previously-undeployed `JAWA_SWIM_HOOD_KEEP_1`, batched into
  the same restart per the standing "batch game-up work" rule) both FAILED
  to deploy — locked by the currently-running game process, expected and
  matches every other same-session DLL rebuild in this project's history.
  `JawaRules`'s XML patch half deployed clean; `StarWarsRaces` was already in
  sync.

## owed
- **Restart is required** — new assembly + new terrain tags only parse at
  load. Whoever restarts: after the game closes, re-run
  `deploy_custom_mods.py --mod EnvironmentalHazards --apply` and `--mod
  JawaRules --apply` to finish writing the two DLLs (currently only the XML/
  texture halves are deployed), THEN launch.
- **Live-verify owed, with the owner watching** (he was present for the
  ruling and is the one judging "does this read as boiling now"): confirm on
  a Scald map that (a) the three wreck shadows visibly differ in shape/height
  from each other and no longer read as one flat box, and (b) margin reads
  calm, shallow shows occasional ripples, deep shows near-constant ripples.
  Nothing here needs an unattended bridge hunt — it's a static visual +
  ambient effect, safe to check solo too if he isn't available; the flyer-
  specific "never unattended" rule does not apply to this mechanism.
- Not yet touched: `RUT_ScaldWaterOceanDeep`/`RUT_ScaldWaterMovingChestDeep`
  and `RUT_ScaldWaterOceanShallow`/`RUT_ScaldWaterMovingShallow` share the
  same tags as their plain siblings so they get the effect automatically —
  no separate work owed there, noted only so nobody re-checks it as a gap.

## watch out
- `RM_WaterAgitationLight`/`Heavy` are brand-new tags with no other reader
  yet — safe to reuse on any other biome's boiling/roiling water without
  touching this component again, exactly the point of keeping them
  Scald-independent.
- The rescan is hourly (2500 ticks), same as `RM_MapComponent_VaporColumns` —
  if a future pass lets Scald water terrain change mid-game (draining,
  refilling), the agitation pools lag up to an hour behind. Not a concern
  for the terrain as currently authored (static).
- `shadowData.volume`'s three components are (x width, y thickness, z depth
  in the sprite's vertical/screen sense) — the calibration ratio here
  (~0.70x/0.63x of the sprite's own alpha-bbox fraction) was derived from
  exactly one reference point (`ShipChunk`) and is a reasonable estimate, not
  an engine constant. If another building's shadow still reads wrong after a
  similar fix, don't assume the ratio transfers unchanged — re-measure.
