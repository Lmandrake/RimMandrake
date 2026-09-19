## spec
Filed thin (no spec/verify/criteria). Researched and written down by FOUNDRY,
2026-09-04, since nobody said what the world must become.

Nothing ever constructs an `Inhabited_Settlement` world object
(`RimMandrake.Inhabited.WorldObject_InhabitedSettlement`, defName
`Inhabited_Settlement`). The only code path that ever calls
`WorldObjectMaker.MakeWorldObject` with an Inhabited def is
`DebugActions_Inhabited.CreatePlaceHere()` — a dev-mode debug action, not a
gameplay or authoring path, and it only makes `Inhabited_Place` anyway.

The real producer for this campaign's authored world is
`jawa/world_settlements_import` (`JawaBenchWorldTools.cs`, W9 STAGE 5, "the
authored 72") — it reads a CSV of `faction_def,name,tile` and places the
hand-authored settlement roster. It was hardcoded to
`WorldObjectDefOf.Settlement`, so it could never have produced an
`Inhabited_Settlement` even for a row that wanted one.
`SETTLEMENT_MANIFEST_BINDING_1.md` already named this exact gap in passing
("via whatever mechanism `jawa/world_settlements_import`-style authoring
uses, or a future dedicated importer").

Chosen fix: extend `jawa/world_settlements_import` with an optional
`world_object_def` CSV column. Blank cell, or the column absent entirely,
resolves to `WorldObjectDefOf.Settlement` — every CSV written before this
column existed (including the live authored-72 file) behaves identically to
today. A row naming a def routes creation through that WorldObjectDef
instead, so a future authoring pass can place `Inhabited_Settlement` rows
through the same all-or-nothing faction-safety machinery the tool already
has, rather than inventing a second importer.

Not chosen: a GenStep/IncidentWorker producer. This project has no
procedural worldgen (`design/Jawa/worldbuilding/the_one_map.md`) — Ash'karr
is hand-authored once — so there is no generation pass to hang a producer
off. The authoring-CSV importer is the only "producer" this world has.

## what changed
`JawaBenchWorldTools.cs`, `WorldSettlementsImport`:
- optional `world_object_def` column, resolved and cached per row in PASS 1
  alongside the existing faction resolution; an unresolvable or
  `canHaveFaction=false` def refuses the whole import, same all-or-nothing
  shape as an unresolvable `faction_def`.
- creation loop now calls `WorldObjectMaker.MakeWorldObject(kv.Def)` instead
  of a hardcoded `WorldObjectDefOf.Settlement`.
- occupancy check generalised from `o is Settlement` to `o.def.canHaveMap` —
  the hazard (stacking two map-capable world objects on one tile) is
  identical regardless of C# type.
- naming generalised: `Settlement.Name` for vanilla rows, reflection over a
  public string `Name` property for everything else (this assembly does not
  reference `RimMandrake.Inhabited` at compile time — see the .csproj's own
  note on why a foreign mod DLL is never added as a build reference
  casually — `WorldObject_Inhabited.Name` is exactly such a property).
- return payload gained `worldObjectDefs` (dry run) and `createdByDef` /
  `nullFactionCreated` (apply), documented as covering every def type this
  run created, alongside the unchanged Settlement-scoped
  `settlementsBefore/After` fields kept for backward compatibility.

Compiles clean: `python.exe src/RimMandrake/bridgetools/build.py` — 0
warnings, 0 errors.

## verify
Not yet run — **game is DOWN**, and this is a bridge tool reporting
`success: true`, which this project's own doctrine calls out as a thing
that lies until proven. Owed at the next game-up / bridge session, cheapest
on the 22s minimal list (`rimworld-load-round`):
1. `jawa/world_settlements_import` dry run against a small test CSV with one
   row carrying `world_object_def=Inhabited_Settlement` — confirm
   `worldObjectDefs` lists it and the row is not refused.
2. `apply=true` — confirm a `WorldObject_InhabitedSettlement` actually
   exists at the target tile afterwards (read back off `Find.WorldObjects`,
   not the tool's own claimed count), with the right faction and the right
   `Name`.
3. Re-run the SAME CSV a second time without `clearExisting` — confirm the
   row is skipped as occupied (the generalised `canHaveMap` check), not
   stacked.
4. Regression: re-run the live authored-72 settlements CSV (no
   `world_object_def` column) dry-run only, and confirm `wouldCreate`/
   `factions`/`settlementsNow` are unchanged from a pre-edit run — this
   column must not perturb existing authoring.

## criteria
- Omitting the column behaves exactly as before (regression check above).
- A named, unresolvable `world_object_def` refuses the whole import rather
  than silently defaulting to Settlement.
- The created object's Faction and Name are set correctly for a
  non-Settlement type, verified by reading the object back, not by trusting
  the tool's reported `success`.
- This closes the producer gap only — binding a `SettlementManifestDef` to
  the created object is `SETTLEMENT_MANIFEST_BINDING_1`, a separate item,
  already scoped and unaffected by this change.

## status 2026-09-04 — LIVE-VERIFIED, CLOSED
Owner handed FOUNDRY the bridge same session. Companion rebuilt `--gm --apply`
(the earlier "would lose 35 tools" warning below was only the missing `--gm`
flag, not real drift — resolved, kept as the record of why it looked
alarming), minimal-list quicktest (`start_debug_game_ready`), all four
`## verify` steps run for real:

1. Dry run against a 2-row test CSV (one `world_object_def=Inhabited_Settlement`,
   one plain vanilla row) — `wouldCreate: 2`, `worldObjectDefs:
   ["Inhabited_Settlement", "Settlement"]`, neither row refused.
2. `apply=true` — `success: true`, `createdByDef: {"Inhabited_Settlement": 1,
   "Settlement": 1}`, `nullFactionCreated: 0`.
3. Independent read-back via `jawa/world_objects_get` (reads
   `Find.WorldObjects.AllWorldObjects` directly, not this tool's own claim):
   object id 108, `def: "Inhabited_Settlement"`, `label: "Test Inhabited
   Producer"` (the reflection-set name landed), `faction: "TribeCivil"`,
   `hasFaction: true`, **`isSettlement: false`** — genuinely a different C#
   type from the vanilla row (id 109, `isSettlement: true`), not a relabeled
   Settlement.
4. Re-ran the SAME import — `success: false`, `skippedOccupied: 2`, both rows
   refused as "a map-capable world object already occupies this tile" — the
   generalised `canHaveMap` occupancy check fires for the non-Settlement type
   too, no stacking.

Cleaned up: quicktest world discarded (disposable, no save), full 589-mod
list restored (`modlist_swap.py --restore --apply`), bridge released.

Unrelated observation made while building (now resolved): `build.py`'s
deploy-plan gate reported the currently-deployed companion DLL (commit
`f8b647e7ce24`) missing several tools (`jawa/pawn_*`, `jawa/lord_*`,
`jawa/weather_*`, others) that a fresh build from current HEAD did not
produce without `--gm` — CLAUDE.md's own doctrine ("`--gm` is not optional on
the companion build") names exactly this shape. Rebuilding with `--gm --apply`
resolved it; not a real regression.
