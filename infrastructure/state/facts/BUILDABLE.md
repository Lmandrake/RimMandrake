# BUILDABLE — what the game and our mods can do. BUILD writes. DECIDE reads.

## Constraints that decide designs

- **Ocean is an elevation rule written at worldgen step 0.** No slider touches it.
  The generator gives 43–55% scattered ocean against a spec of ~25% in three bodies,
  which is why worldgen is held. `JawaSeaShaper.dll` is our intervention and it is
  **not deployed** — every sea reading so far is the sea WITHOUT it.
- **`PlanetTypeDef.elevationRange`**: only one such def can be active at a time.
- **A `WorldGenStepDef` absent from `PlanetLayerDef/worldGenSteps` loads, validates,
  and never runs**, with no log line. Registration is silent both ways.
- **`isJunk` on a scatter def multiplies its count by the product of every
  `TileMutatorDef.junkDensityFactor` on the tile.** Five live mutators are ZERO —
  `Dunes`, `Iceberg`, `VEE_DetachedIceberg`, `VEE_IceAndFire`, `VEE_QuicksandDunes`
  — so a scatter step silently places nothing on those tiles.
- **`ThrusterBase` is `holdsRoof true` + `fillPercent 1`** — a thruster seals a room
  exactly as the wall it replaces. It costs one hull cell, not a deck re-lay.
  ⚠️ `design/Jawa/worldbuilding/gravship_flight_invariants.md` §11 is **wrong on
  both branches** and has been driving planning.
- **`PreferredXenotype` is chosen at ideo-generation time, not in XML.** There is no
  FactionDef path to it; per-faction composition goes through `PawnKindDef`.
- **`GravshipExport` has no roof field** — roofs regenerate at import by flood-fill.
- **`Jawa_ScatterScrapfields` is the only GenStepDef scattering `ChunkSlagSteel`** in the
  live 585-mod set. Its one map-gen competitor on a plain colony tile is the
  `AB_DerelictBioLab` mutator (Alpha Biomes, 0.5%, flat tiles, via KCSG); `AncientGarrison`
  and `AncientWarehouse` are landmark-only, and every other layout route is site-map-only.

## Tooling that exists

- `validate_patch.py` — offline patch verification. ⚠️ Must be **scoped** to the
  active mod list or it silently checks 1,271 installed mods instead of 585.
  The last scoped sweep: 72 files, **0 errors**, 1,608 warnings across four
  structural classes. **Read the classes, not the count** — the total is dominated
  by an intentional idiom and recurs at the same magnitude every run.
- `deploy_custom_mods.py --mod <name> --plan|--apply`. A `--mod`-scoped apply that
  ends `VERIFIED in sync` is a positive statement about **every** file in that mod,
  not only the ones it wrote.
- `refresh.py` rebuilds the offline def dump. `package_skill.py --all` rebuilds skill
  zips — read its exit code, not the directory listing.

- **Cherry Picker's removal list is a plain offline-editable file**, not a UI-only
  setting: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`,
  one `<li>DefType/defName</li>` per entry under `<keys>`. It is NOT in the repo, so an
  edit is unversioned, and the running game rewrites the file when the settings window
  closes — edit it with the game DOWN or lose it.
- **`ParentName` resolves a def's `Name=` attribute, never a defName.** A ParentName that
  resolves to nothing DISCARDS the def at load and logs nothing. `validate_patch.py`
  catches it; a cold load does not.

## Ours, deployed

20 mod folders, 15 active in `ModsConfig.xml`, 4 assemblies
(`JawaIonWeapons`, `JawaSeaShaper`, `RimDefDump`, `JawaBench.BridgeTools`).
`StrandedQuest` is built but deliberately not enabled — `[v2]`, v1 gets one
`QuestScriptDef` and row 3 fills it.
