# Biome owed-work audit — 9 sheets (2026-09-20)

Sheets assigned: the_rot.md, the_lantern_deeps.md, the_pyrelands.md,
the_twilight_deep.md, the_grey_deep.md, the_propane_lakes.md, the_webwork.md,
the_contagion.md, assailant_weapon_remnants.md

Method: extract Owed-style section(s) per sheet, split into individual work
items, classify FILED / UNFILED / DONE-BUT-UNRECORDED against
`infrastructure/state/items/*.md` and `infrastructure/state/items/closed/*.md`
plus defs/art/C# on disk.

Status: IN PROGRESS — filling section by section.

## the_rot.md

Owed section (§ after "## Owed") has one heading holding 6 bullets; the
"Engine feasibility pass" bullet is itself 7 sub-items. Examined 11 individual
work items total (5 top-level bullets + 6 engine sub-items; the "def tails
check" bullet is marked ✅ CLOSED in the sheet itself, not counted as owed).

1. **Heat-generating gene** — FILED/DONE (CONFIRMED). `ROT_WARM_MAT_1`
   (closed at `f4d8dbf2b`) built `RUT_Gene_Furnaceblood`
   (`src/RimUtinni/RotSporeKit/Defs/GeneDefs/RUT_RotSporeKit_Furnaceblood.xml`),
   `RM_MapComponent_WarmGround`, and `RUT_GrownFurnace`. Sheet's Owed line is
   stale — the gene existed before this audit.
2. **Guardian repertoire concretized per tea species** — UNCERTAIN (leaning
   UNFILED). Searched: "guardian repertoire", "tea species", "Wildsteam" +
   "guardian". No item or design-doc section found expanding the §7 tea-guard
   menu per species. `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (closed) covers
   general fauna/flora assignment sittings, not this specific expansion —
   its own prose doesn't mention guardians or tea species.
3. **Engine feasibility pass — health-share comp (C#, two variants)** —
   UNFILED (CONFIRMED no such comp exists). Searched: "health-share",
   "HealthShare", "SharedHealth", "Symbiont" (found only hediff/recipe defs,
   no shared-health C# comp), "CompHealthShare". No item names it either.
4. **...live-item viability clock (dies refrigerated, dies delayed)** —
   FILED/DONE (CONFIRMED). `ROT_LIVE_PREPARATIONS_1` (closed at `f4d8dbf2b`):
   `RM_Patch_LivePrepViability.cs` +
   `RUT_RotSporeKit_LivePreparations.xml` (vanilla `CompTemperatureRuinable`
   + `CompLifespan` on every live-prep item, with a strict/lenient Mod
   Settings toggle per ban 4).
5. **...heat-pushing produce comp** — FILED/DONE, same as #1
   (`RUT_GrownFurnace`, `ROT_WARM_MAT_1`).
6. **...milk ponds as terrain (donor Marsh patches re-skinned to not-water
   milk)** — UNFILED (CONFIRMED not built). Searched: "MilkPond", "milk
   pond" (TerrainDefs), "Marsh" reskin. `RUT_RotSporeKit_Terrain.xml` ships
   `RUT_MushroomFloor/Bridge/HeavyBridge/MoonlessCarpet/MycelialSoil/
   MycelialMatting` — mushroom bridges reference milk ponds as the thing
   they're built OVER, but no milk-pond terrain def exists anywhere in
   `src/RimUtinni`. `WATER_KINDS_TAXONOMY_1` and `FISH_BY_BIOME_1` (both
   closed) only classify milk ponds in DESIGN prose ("not-water"); neither
   builds the terrain. **The Rot has no rot-tagged standing liquid at all** —
   this is the closest analog to the Blue Desert pattern found in this set:
   a ratified design element (milk ponds, referenced by name in 4+ places)
   with no engine artifact.
7. **...Sheen weather def + compatibility hediff** — FILED/DONE (CONFIRMED).
   `RUT_RotSporeKit_SheenWeathers.xml` (205 lines),
   `RUT_RotSporeKit_SheenHediffs.xml` (109 lines),
   `RUT_HediffComp_SheenExposure.cs`, `RUT_SheenExposureLock.xml` game
   condition all exist and are substantial, referenced across several other
   items (`BMT_FAUNA_ABSORPTION_1`, `CAVERNS_PARITY_BUILD_1`,
   `MIASMA_MECHANICS_1`).
8. **...the rot-rate map condition** — UNFILED (CONFIRMED not built).
   Searched: "rot-rate", "RotRate", "rot clock", "RotClock". The sheet's own
   §3 "The rot clock" describes instant composting as a service, but no
   GameConditionDef or MapComponent implementing a map-wide rot-rate exists
   in `src/RimUtinni` or `src/RimMandrake`; no item names it.
9. **...the pale tree as a Royalty anima reskin with a restricted vanilla
   psycast set** — FILED but STALE STATE (flag). `ROT_PALE_TREE_1` shows
   `ready` (not closed) in rimflow, but `RUT_PaleTree.xml` is fully built
   (verified field-for-field against `Plant_TreeAnima` per its own header),
   art landed 2026-09-20 per `ROT_FLORA_FAUNA_VERDICTS_1`, and `rimflow show`
   itself warns 3 commits cite the item with none touching its item file —
   the ledger row appears to lag real state. The "restricted vanilla
   psycast set" audit is explicitly declined by an owner card baked into the
   XML comment ("No power whitelist: declined... needs C#, not built") —
   so that clause of the Owed bullet is correctly still open, but is a
   ruled-out non-goal, not an oversight.
10. **Roster admission tests at `BIOME_FAUNA_ASSIGNMENT_SITTING_1`** —
    FILED/DONE via that item (closed) plus the subsequent
    `ROT_FLORA_FAUNA_VERDICTS_1` (proposed/in-flight) which names hybrid
    verdicts explicitly.
11. **Wildsteam wiring — the sacred-grove relationship into
    `FACTION_SPEC.md`** — UNFILED (CONFIRMED). Searched: "sacred grove",
    "Wildsteam" + "Rot"/"MycoticJungle", grep of `FACTION_SPEC.md` itself for
    "sacred grove"/"Rot"/"MycoticJungle"/"pale tree" — zero hits. The 611-line
    `FACTION_SPEC.md` never mentions the Rot's sacred-grove relationship at
    all. `FACTION_ART_SPEC.md` and other docs reference Wildsteam's palette
    and lore generically, not this specific relationship.

## the_lantern_deeps.md

Owed section: 8 bullets, one splits into two (mindstone race naming vs. the
actual race build). Examined 9 items total.

1. `LANTERN_DEEPS_INJECTION_1` — FILED/DONE (closed `2eb08d1a4`).
2. `HORRORWASTES_BIOME_DISSOLVE_1` — FILED/DONE (closed `bb437a16`).
3. `CRYSTAL_MODS_INGEST_1` — FILED, superseded by `CRYSTAL_INGEST_EXECUTION_1`,
   which is itself FILED/DONE (closed `406dd95f4`). Chain intact.
4. `MECHANOID_ORIGIN_CANON_1` — FILED/DONE (closed 2026-09-11) — but this item's
   own `verify` clause is explicitly CANON/NAMING ONLY ("names ruled... design
   reviewed"), not a build. See #7 below for the gap this leaves.
5. `KYBER_TRADE_PLOT_1` — FILED, `ready`/BLOCKED (design spec written,
   implementation genuinely still owed per the item's own blocked reason:
   "Heat/Hutt-Interest GM blackboard (M4) unbuilt"). Matches the sheet's own
   "implementation still owed" note — not a discrepancy, sheet is accurate.
6. **Names ruling** — FILED/DONE via `MECHANOID_ORIGIN_CANON_1`
   (`RUT_Mindstone` kept, new race named `RUT_Kindled`, Forgotten Sentinels
   canon) — this is a NAMING ruling only, confirmed closed.
7. **Crystal-life authoring (art + C#: piezo/light-draw, Creep's accretion,
   Cleavers' fracture movement, Shard-mind animating dead gear)** — UNFILED
   (CONFIRMED). `LANTERN_DEEPS_INJECTION_1` itself states explicitly: "the
   crystal-life cast (Lantern, Creep, Cleavers, Chorus, Shard-minds,
   mindstone) is authored content — art + C# scoped separately" — i.e. it was
   deliberately deferred to a future item that was never filed. Searched:
   "Crystal-life authoring", "piezo", "Creep" + "accretion", "Cleaver" +
   "fracture", "ShardMind"/"Shard-mind", "RUT_Kindled", "RUT_Mindstone" —
   zero defs, zero C#, zero items beyond the deferral note itself. **The
   Kindled race that `MECHANOID_ORIGIN_CANON_1` ratified by name does not
   exist as a def anywhere in `src/RimUtinni` or `src/RimMandrake`** — no
   pawnkind, no mindstone findable item, no droid-mind crafting recipe. This
   is the sheet's largest playability gap: a named, owner-ratified new
   sapient race with zero engine representation.
8. **Roster admission for the non-crystal cave fauna at the sitting** —
   UNCERTAIN. `LANTERN_DEEPS_INJECTION_1` defers this to "the sitting"
   (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`, closed), but that item's own prose
   only proves general sheet review + assignment-prep infrastructure, not
   that Lantern Deeps' specific non-crystal fauna roster was actually
   admitted. Searched: "non-crystal cave fauna", "Lantern Deeps" inside
   `BIOME_FAUNA_ASSIGNMENT_SITTING_1.md` and `_assignment_prep.md` — did not
   open `_assignment_prep.md` (611 lines, another agent's territory/frozen
   prep doc) to confirm a per-species row; flagging as uncertain rather than
   claiming UNFILED without that read.

## the_pyrelands.md

(pending)

## the_twilight_deep.md

(pending)

## the_grey_deep.md

(pending)

## the_propane_lakes.md

(pending)

## the_webwork.md

(pending)

## the_contagion.md

(pending)

## assailant_weapon_remnants.md

(pending)
