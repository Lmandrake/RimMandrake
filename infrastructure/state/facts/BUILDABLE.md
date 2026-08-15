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

## Ours, deployed

20 mod folders, 15 active in `ModsConfig.xml`, 4 assemblies
(`JawaIonWeapons`, `JawaSeaShaper`, `RimDefDump`, `JawaBench.BridgeTools`).
`StrandedQuest` is built but deliberately not enabled — `[v2]`, v1 gets one
`QuestScriptDef` and row 3 fills it.
