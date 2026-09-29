# CAULDRON_FULL_RENAME_1 — Full rename PoisonForest → Cauldron, down to the defs

Owner-typed 2026-09-28 at the bedazzle sitting: "Rename all to the cauldron all
the way down to the defs." and "Poison ground gets renamed to this biome."
(Rename itself first ruled owner-typed 2026-09-27, program row 5.)
Precedent/shape: `CRACKEDLANDS_FULL_RENAME_1`. The measured census — every target
with counts — is `design/Jawa/worldbuilding/biomes/cauldron_bedazzle_review_2026-09-28.md`
§Rename census (MEASURED 2026-09-28): RM_PoisonForest 117×/41 files,
RUT_PoisonForest 702×/52, packageId 16×/10, namespace 7×/5, soils 18×/6,
`poison_forest` strings 409×/106.

## spec

- Scope is EVERYTHING the census names, including defNames and the soils
  (`RM_PoisonSoil`/`Rich` → cauldron naming). BENCH read "all" as including the
  frozen `RUT_PoisonForest` twin; the owner saw that reading at volley turn 3 and
  did not correct it at turn 4.
- 🔴 **The live-tile/savegame shortHash check gates every defName change**
  (`BIOME_DEFNAME_DELETION` precedent — a grep of the `.rws` lies; tileBiome is
  shortHash-encoded). Run it FIRST and record the blast radius; the old canonical
  save carrying a dead name is acceptable per world-remake-is-the-last-step
  doctrine, but it is recorded, never silent.
- C# namespace/assembly rename ⇒ rebuild; DLL + `.srchash` sidecar push together
  (`DLL_SOURCE_STAMP_GUARD_1`). workerClass string in the BiomeDef moves in the
  SAME commit as the C# type or the def dies silently.
- Mod folder rename ⇒ deploy-tool unique-name collision check; packageId
  `mandrake.rm.poisonforest` → `mandrake.rm.cauldron` (compose manifest too;
  merges into `RimMandrake.Biomes` per `BIOME_MOD_UNIFICATION_1` regardless).
- Canonical roster/sheet files rename with a one-line successor pointer;
  freeze headers carry over.
- ⛔ NOT targets: `world/**` exports (records, never edited back), `observed/`,
  `research/`, closed items, handoffs — history stays history.
- Sequence with `CAULDRON_RULED_CONTENT_1`/`_MECHANICS_BUILD_1`: rename first is
  cleanest; if content lands first it lands under old names and this item sweeps
  them.

## criteria

- Zero live `PoisonForest` references outside the NOT-targets list
  (`git grep` sweep with a sanity probe on a name known present).
- Game loads the renamed mod on the minimal list; biome def resolves; no
  cross-reference errors in Player.log.
- Live-tile check result recorded on this item before the defName commit.
