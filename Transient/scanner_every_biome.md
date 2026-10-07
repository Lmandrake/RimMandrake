# GRAVSHIP_ACOUSTIC_SCANNER_1: payload on every owned biome (2026-10-06)

Owner decision by question card (2026-10-06): the payload goes on EVERY biome of ours.

## Biome list (derived from src/ XML)
62 concrete BiomeDefs, parsed as elements from every `<Defs>` file under `src/` (36 RM_, 26 RUT_).
Zero-tile biomes were not skipped. No owned content was repointed at a donor def.
Before: 3 carried a payload (RM_FloodedCanyon, RM_Stillsand, RUT_CrackedLands). After: 62 of 62.

## Payloads authored
- One FindMod-guarded patch per RM mod, in that mod's own `Patches/`, named
  `RM_AcousticPayload_<Mod>.xml` (unique, so the Baroque Biomes compose cannot shadow them):
  Abyss, BlueDesert, Cauldron, Contagion, FeverWood, GelatinousSlime, Greentide, LanternDeeps,
  LeaningScrub, LongShade (new Patches/), Miasma, NightsideIce, Pyrelands, RustCathedral, TheForge,
  TheRot, TheSump, Scarlands (RM_Warscar), Wasteland, Webwork, WeepingStones,
  TerminalBiomes (5 seas incl. the Chill crater), DivingInteraction (6 seabed floor biomes).
- `src/RimUtinni/UtinniPatches/Patches/AcousticPayload_UtinniBiomes.xml`: the 24 Utinni twins carry their
  RM twin's targets (RUT_ExtremeDesert copies the Stillsand payload verbatim, as RUT_CrackedLands
  already copied the Flooded Canyon one), and RUT_FuelSnows, RUT_Umbra and RUT_Jawa_BackgroundWater get their own.
- Targets come from each biome's own content: its wreck fields, landmark buildings (shard-mind,
  Coalescence, buried ordnance, middenshell, greatbole core...), its big or buried roster animals, and
  hidden caves. Every biome has a biome-specific quietText. Each biome's sitting may re-author its file.

## L0 proof
- `src/RimMandrake/AcousticScanner/validation.py` static_checks now globs every payload patch and fails if
  any owned BiomeDef lacks one, if a payload targets a non-owned BiomeDef, or if a target names a def
  that exists nowhere in src/ (8 allow-listed vanilla/donor names). Sanity probes: >=3 files, >=20 biomes.
  Result: STATIC PASS (62 owned, 62 targeted, 27 files).
- validate_patch.py on all 24 new files: 0 errors, 0 warnings (static). With `--defs src` it could not
  run the xpaths (our mods are not under an installed-mod root), so the xpath-to-BiomeDef match is
  carried by the validation.py owned-vs-targeted check instead.
- run_selftests.py: 211/214; the 3 failures are the known environmental ones (ledger_lint,
  tool_metadata, utinnipatches_dump on RUT_MindstoneMatrix/JOE_Landopus), none touching this work.
- biomes_compose_sweeps.py: 5 sweeps with findings, same as before the change; none name the payloads.

## Not proven (owed)
- L1: the extension resolves on a non-probe biome live (jawa/get_defs on a BiomeDef's modExtensions).
- L2: a pulse on a map of one of the new biomes hears its targets. L4: owner judges the feel.
