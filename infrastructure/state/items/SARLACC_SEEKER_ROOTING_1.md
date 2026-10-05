# SARLACC_SEEKER_ROOTING_1 — the sarlacc seeker quests for food and water, then roots

**Owner, 2026-10-04 (desert sheet, RM_GreatDevourer row):** *"It is now a life stage of the Sarlacc (see entry)
that quests until it finds rich food and a water source to claim. ... Lives at the RSW level."*

**Done already (LONGSHADE_SHEET_STRUCTURAL_RULINGS_1):** `RSW_GreatDevourer` relabelled "sarlacc seeker"
(defName kept), description rewritten as Stage I of `design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md` §2,
canon entry removed (`canon_references/NO_SOURCE.json` `not_canon_linked.GreatDevourer`).

**Mechanism that already exists:** `src/RimStarWars/Sarlacc/Source/CompSarlaccSwimmer.cs` — a birth-water reserve that
drains (faster when moving), seep detection (`seepMarkerDef` RSW_DeepDesertSeep, radius 4), rooting into
`RSW_SarlaccAnchored` at a seep or where it stands when the reserve runs dry (the "throats"), Mod Settings
`rootingInPlayEnabled`. Today only `RSW_SarlaccSwimmer` (the Devourer-shaped Stage I) carries it.

**What is missing, why it was not wired blind:**
1. The reserve tops up ONLY from a finished `CompDevourer` digestion. The seeker is an ordinary animal predator with no
   CompDevourer, so "rich food" never counts: wired as-is, every seeker would simply count down and root.
   Owed: a kill top-up for non-devourer swimmers (e.g. `Notify_KilledPawn` on the comp, gain scaled by victim body size).
2. "Quests until it finds rich food AND water" implies an order: feed until the reserve is high, THEN seek water
   (a seep, or the swimmer's-road dew ring, `RSW_SwimmerRoad.cs`), then root. Today seep-rooting fires at any reserve.
   Owed: a reserve threshold gate on seep-rooting, and a water-seeking job when above it.
3. Placement: rooting spawns a sarlacc pit on whatever map it is on. The seeker is cast wild at 0.5 in RUT_Desert
   (and RM_GreatDevourer in RM_LongShade, whose RM->RSW tier move is the parallel helper's work), so pits would appear
   on ordinary desert maps. Needs the owner's yes, or a biome gate like `RSW_SwimmerRoadExtension.biomes`.
4. Two Stage-I defs now exist (`RSW_SarlaccSwimmer`, Devourer-bodied; `RSW_GreatDevourer`, the worm with real art).
   Whether they merge into one is a judgement for the owner.

**Wiring when ruled:** `<li Class="RimMandrake.StarWars.Sarlacc.CompProperties_SarlaccSwimmer" MayRequire="mandrake.rsw.sarlacc">`
on RSW_GreatDevourer with `anchoredDef` RSW_SarlaccAnchored and `seepMarkerDef` RSW_DeepDesertSeep, plus (1)-(2) in C#
with a selftest in the Sarlacc suite.
