# VAPOR_PLACEMENT_CLEANUP_1 — Part 4 fix-up from `vapor_emitter_review_2026-09-12.md`

## 2026-09-12 (FOUNDRY) — mechanism check done first, then the ruled fix-ups executed live

Read `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md` (Parts 1-3
+ owner card sitting) first, no item file existed before tonight. Game: the
loaded `CANONICAL_ASHKARR_2026-09-09` save (592 mods, live bridge — same
session that fixed the RUT_Webwork thingClass crash, see
`BUILDING_THEFT_HAULER_1`/commit `257bbbc7f`).

**Engine mechanism check FIRST, helixien** (per the summary's own
instruction, and per its "flag for a live/source follow-up before building
anything" deferral): `VHGE_GasGeyser` (`vanillaexpanded.helixiengas`) DOES
resolve live (`jawa/get_defs`, `foundCount: 1`) — not a missing/ghost mod as
a first grep pass falsely suggested (grepping the Mods/workshop tree for the
literal defName and the packageId both came back empty; RimSage has no
index for this mod's XML at all). Scalar-field read
(`generateCommonality`, `generateAllowChance`, `canGenerateDefaultDesignator`
— all 1.0/True, `killedLeavingsChance` 1.0) shows nothing about WHERE it
scatters; `get_defs` only reads scalar fields, and the placement hook (a
`GenStepDef`, if one exists, or a biome-list field) is invisible to it.
**Verdict: still UNMEASURED**, exactly as the doc's own Part 1 gap said — no
placement or re-seat work attempted for helixien this pass. Whoever picks
this up next needs the mod's own C# or XML read directly off disk (not via
RimSage, which doesn't cover it) before any world edit.

**Executed** (both are RULED, not proposed, per the 2026-09-12 card
sitting):

1. **Magma vent orphans (5/10 tiles outside the engine's own
   `AB_MagmaVents` biome whitelist)** — confirmed live via
   `jawa/world_mutators_get` (full-planet pull, `range=0-21871 limit=25000`,
   14,396 mutator-bearing tiles, matches the doc's audit): tiles **3067,
   9002** (`ZBiome_Badlands`) and **4143, 20583, 20586** (`AB_RockyCrags`).
   Removed `AB_MagmaVents` from all 5 via `jawa/world_mutators_set
   {action:remove}`, comma-joined tile list in one call, read back
   individually afterward — 0/5 still carry it.
2. **Ancient*Vent family, ruin-only** — re-read the ruling's own wording
   before acting: "allowed only on tiles that already carry an ancient-ruin
   landmark, banned nowhere else." A literal same-tile landmark-object
   check flagged 269/411 instances (65%) as "violations" — checked against
   the doc's OWN Part 3 language before touching anything, since a change
   that size on two whole biomes did not match "cleanup" framing: Part 3
   itself already reads the 92%/100%/bimodal-by-landmark-family
   concentrations in `PoisonForest`/`AB_MechanoidIntrusion` as "expected"
   and "not a violation," i.e. the ruling is scoped to the ruin **biome**
   family the AncientVent category already concentrates in, not to a literal
   per-tile landmark-object co-location. Fixed the correct, narrower target
   instead: **24 instances sitting on biomes that are not ruin biomes at
   all** (`AncientToxVent` on `ExtremeDesert`×2/`Scarlands`×3/`AB_OcularForest`×1;
   `AncientSmokeVent` on `ExtremeDesert`×2; `AncientHeatVent` on
   `Wasteland`×1/`RUT_NightsideIce`×1/`AB_RockyCrags`×1/`ZBiome_Badlands`×10/
   `ExtremeDesert`×3). Removed all 24 via the same batched
   `world_mutators_set` pattern; 0/24 remain. The 4 `AB_Ancient*Vent`
   reskins (Freezing/GreyPall/BloodRain/DeathPall) had **zero** non-ruin
   instances already — nothing to fix there.
3. **PoisonForest "toxic gases and green gas"** (owner, verbatim) — toxic
   already satisfied: `AncientToxVent` sits on 18/24 PoisonForest tiles
   post-cleanup (the biome's own dominant toxic-vent host, per Part 3).
   **"Green gas" has no matching defName anywhere in the live mutator/vent
   inventory** (checked: no mutator or ThingDef in this campaign's vapor
   family has "green" in its defName or Part 1's own flavor-text column) —
   not invented here per this repo's own "never guess a defName" rule.
   Read as the biome's own ambient/visual identity (PoisonForest's baseline
   fog/weather, not a `TileMutatorDef`), not a gap to fill with a fabricated
   def. Flagging rather than silently closing: if the owner meant a NEW
   mutator, that is content authoring, not a placement fix.
4. **Swamp/ruin gas re-seat** — already satisfied by Part 3's own audit
   (`VEE_RotstinkVents` 100% swamp, `VEE_ToxicVents` 92% ruin) and by fix #2
   above, which removed the `AncientToxVent` outliers that were the
   remaining non-ruin tail. No further action needed.

`jawa/world_commit` run after every batch (`failedSteps: 0` each time).

**Not attempted, correctly deferred**: helixien re-seat (mechanism
UNMEASURED, see above) and `VEE_SteamGeysers_Decreased`
zero-nightside-geyser application — that is `VAPOR_TERMINATOR_GEYSER_FIX_1`'s
own scope (already run once tonight per its pre-fix save backup timestamp),
not re-touched here to avoid double-editing another item's ledger.

**Batched with, not saved separately from**: `SARLACC_WORLDMAP_RELOCATE_1`
and `WORLD_NAME_FIXES_1`, same session, same loaded save — one Saves backup,
one re-save, covering all three (see `SARLACC_WORLDMAP_RELOCATE_1`'s own
note for the freeze-discipline write-up).

## spec
Part 4 fix-up from the review: magma-vent out-of-lock tiles, ancient-vent
ruin-only audit, swamp/ruin gas re-seat, PoisonForest toxic+green gas,
helixien re-seat — engine mechanism check first, per the review's own gap
flag on helixien.

## verify
`jawa/world_mutators_get` full-planet re-pull shows 0 `AB_MagmaVents`
outside its biome whitelist and 0 Ancient*Vent-family instances outside
`PoisonForest`/`AB_MechanoidIntrusion`. Both confirmed this pass.

## criteria
The RULED parts of Part 4 (magma orphans, ancient-vent ruin-biome scoping)
are live and read back clean. Helixien stays correctly unbuilt on an
unmeasured mechanism; "green gas" stays unfabricated pending a real
defName. `needs=offline` for whoever measures the helixien mechanism next;
otherwise this item's ruled scope is closed.
