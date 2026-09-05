## spec
Full ruling: `design/Jawa/ownership_settlement_spec.md` (owner sitting 2026-08-31),
item 8: "a library of authored Lua district templates (market row, cantina block,
dwelling cluster, workshop yard, depot, shrine, scrapyard…) + a per-settlement
manifest... composed through the rimplace machinery," item 10: "Pilot town:
Junkers." Sequenced execution item 3: "Lua district templates through rimplace
(layout-layers lint applies); Junkers set first: scrapyard, dwelling cluster,
cantina block, depot. Security props vocabulary."

`SETTLEMENT_VISIT_LOOP_1` (built and committed this session) already ships The
Claim Jump's manifest naming exactly these four district slots by label:
`scrapyard`, `dwelling cluster`, `cantina block`, `depot`
(`src/RimUtinni/AshkarrInhabited/Defs/SettlementManifestDefs/SettlementManifestDefs_TheClaimJump.xml`).
Its compose step (`GenStep_ComposeSettlementDistrict.cs`) currently reads only
`districts[0]` and places nothing — this item builds the four real templates and
wires composition to actually place them.

Tooling: `src/RimMandrake/Utils/rimplace` — a Lua template compiles offline to a
`BuildPlan` (things/terrain/roof/rooms), lints, renders as ASCII, and compiles to
`jawa/*` bridge calls, all with ZERO game/bridge access
(`src/RimMandrake/Utils/rimplace/README.md`). `design/Jawa/templates/dwelling.lua`
is a working worked example — copy its shape (helpers, `build(ctx)` entry point,
role-by-occupant-count logic) rather than inventing the Lua idiom from scratch.
Read `skills/rimworld-layout-layers/references/rimplace-gaps.md` in full before
writing anything — it names real gaps (no power/pipe net modeling at all, `Room.doors`
never populated so rule 4's reachability check is not real reachability, rule 6's
roof-support approximation, the `door()`/`wall_mount()` replace-not-stack trap).

Scope for this pass:
1. **Four Lua templates**, one per Junkers district label, at
   `design/Jawa/templates/junkers_scrapyard.lua`,
   `junkers_dwelling_cluster.lua`, `junkers_cantina_block.lua`,
   `junkers_depot.lua`. Low-security/scavenger flavor (per the manifest's own
   description: "forgiving," low security) — reused vanilla furniture/structure
   defs and Droidworks/Jawa-flavor stuff where it already exists, no new art.
   **No power/pipe network content** — the rimplace IR cannot model one yet
   (see the gaps doc), and nothing here needs one: these are NPC-inhabited
   flavor districts for a visit loop, not player-operated infrastructure.
2. **Security props vocabulary**: whatever a district template can place that
   reads as "this place has eyes" (a fixed camera-like prop, a watchtower, or —
   for Junkers specifically, since their manifest sets `searchesLeavers=false`
   — deliberately NONE.  The Claim Jump is the wrong pilot for proving this
   vocabulary has teeth; note that honestly rather than forcing security props
   onto a low-security settlement for the sake of coverage).
3. **Wire composition**: extend (do not replace) `GenStep_ComposeSettlementDistrict.cs`
   so it resolves each `districts[]` slot's label to a template file/module and
   actually runs it via rimplace's Python compile step or a C#-side equivalent
   — **read `GenStep_RimplacePlan.cs`/`RimplacePlan.cs` under
   `src/RimMandrake/StructureInjections/Source/` first, that is almost
   certainly the existing C#-side consumer of a compiled BuildPlan and this
   item should call into it rather than reinvent how a plan becomes map
   changes.** If composing all four districts in one map generation is out of
   reach this pass, composing `districts[0]` for real (replacing the current
   placeholder-log stub) with the rest still stubbed is an acceptable v1 — say
   so explicitly rather than silently shipping a partial loop as if it were
   whole.

Explicitly OUT of this pass: crime/commerce/social verb jobs
(`SETTLEMENT_VERBS_WAVE_1`), any non-Junkers settlement/faction's districts,
any change to `RM_Property` or the manifest/casing schema itself.

## verify
- `$P -m rimplace lint <template> --rect ...` clean (0 ERROR) for all four
  templates, run offline, no game needed.
- `$P -m rimplace render <template> --rect ...` — ASCII output attached/quoted
  in the build report so a human can eyeball the layout without a load.
- `$P -m rimplace verify <template>` if a live def dump is available (checks
  every defName against it) — UNMEASURED is an acceptable answer if the dump
  is stale/absent, never treat UNMEASURED as a pass.
- `validate_patch.py` clean on any new XML (manifest/security-prop defs, if
  any are added).
- Live-quicktest-observed (FOUNDRY, not the build agent): generating a map for
  The Claim Jump actually places at least one real district's geometry
  (walls/floor/furniture visible via `take_screenshot` or `jawa/list_things`),
  not just the placeholder log line.

## criteria
A correct v1: four lintable, renderable Junkers district templates exist and
at least one is wired into real map composition for The Claim Jump, replacing
the placeholder stub for that slot. Full four-district composition in one
map is a stretch goal, not a requirement — an honest partial (one real
district, three still stubbed) is an acceptable, clearly-labeled v1.

## 2026-09-02 (FOUNDRY) — found already mostly built; finished wiring the resolver

**Stale-item trap avoided**: this file read as if nothing existed yet. It
didn't — `git log` showed `e0671e1e` ("DISTRICT_TEMPLATE_LIBRARY_1: four
Junkers district templates, wire scrapyard live") had already authored all
four `.lua` templates (`junkers_scrapyard/_dwelling_cluster/_cantina_block/
_depot.lua`, all in `design/Jawa/templates/`) AND already built the security
props vocabulary (a `maybe_place_security()` sketch in `junkers_depot.lua`,
gated on a param the Junkers pilot never sets — proven inert by construction,
not omission) AND already wired `GenStep_ComposeSettlementDistrict.cs`'s
`TemplateFiles` resolver with `scrapyard` live. Checked `git status` first —
nothing mid-edit on these paths, this was a genuinely completed prior pass
the item file just never recorded.

**What this pass actually did:**
- Re-verified all four templates at their manifest `approxSize`s (scrapyard
  30x30, dwelling cluster 22x22, cantina block 16x16, depot 18x18, faction
  `Jawa_Junkers`, tech `Neolithic`): `lint` 0 findings on three; **caught and
  fixed a real bug** in `junkers_depot.lua` — an 18-wide floor bay put its own
  centre >6 cells from any wall (vanilla's roof-support radius), which
  `lint`'s `roof-unsupported` check correctly flagged. Fixed by placing one
  `WALL`-role support pillar near the geometric centre, searching outward
  cell-by-cell for the first unoccupied spot so it never lands on a shelf the
  grid loop already placed. Re-lint: 0 findings.
- `rimplace verify`: still UNMEASURED (def dump unreadable at
  `DefDump/defs.sqlite` this session) — not a pass, correctly reported as such,
  same as every other rimplace pass tonight.
- Exported the three unwired templates to the runtime flat-plan format
  (`rimplace export ... --out src/RimMandrake/Inhabited/Templates/*.txt`) and
  added all three to `TemplateFiles`, so the resolver now covers all four
  Junkers district labels, not just `scrapyard`. **Composing more than
  `districts[0]` per visit is still not built** (no spatial multi-district
  layout exists in `GenStep_ComposeSettlementDistrict.Generate` — genuinely
  out of scope for this pass, a real engineering project of its own, left as
  the stated stretch goal) — but the resolver itself is now complete, ready
  for whichever future pass builds multi-district composition or a settlement
  whose manifest orders its districts differently.
- `dotnet build Inhabited.csproj -c Release`: 0 warnings, 0 errors.
- Deployed: the three new `Templates/*.txt` files landed clean
  (`deploy_custom_mods.py --mod Inhabited --apply`, confirmed via a second
  plan-only run showing them no longer as drift). `Assemblies/Inhabited.dll`
  hit the expected Windows file-lock (`OSError: [Errno 22]`) — the game is up
  and mid-restart elsewhere this session; the compiled DLL is ready and will
  deploy clean on the next shutdown window.
- No new XML/defs added this pass, so `validate_patch.py` is N/A per the
  item's own verify wording.

**Still open, honestly**: live-quicktest-observed placement (any of the four
districts actually generating real geometry on a map) is still owed to a
future restart+bridge session — not attempted this pass, no bridge held.
Full four-district spatial composition remains the stretch goal, unbuilt.
Not closing.

## 2026-09-05 (design, Fable subagent) — all four Junkers districts reworked to the owner's bar; three more faction sets

Owner's mandate tonight: "expand out the settlement maps used for faction
settlements... examine Visit Settlements... but then we will likely wrap our own.
Go crazy with this and do real work." Research already done and NOT to be
redone: `ninagoblin.visitsettlements` and `mlie.largefactionbases` contain no
authored room/district content (the first reuses vanilla base gen for friendly
visits, the second scales base size/manpower numerically). This item IS the
"wrap our own"; there was nothing to port.

Binding bar: `TILE_STRUCTURE_REVIEW_SAVE_1`'s live verdict ("pretty horrible...
not accept any rooms yet") on three axes — FLOORING, no REGULAR GRIDS, secondary
CLUTTER — plus aisle-thinning named for `junkers_depot`.

**Engine (`src/RimMandrake/Utils/rimplace/`, commit `a00fafd0` + follow-ups):**
- `Thing.overlay` + `ctx:place_overlay` / `ctx:wall_attach` / `ctx:role_at`.
  Non-edifice things (wall lamps, floor decals, Aurebesh signs) share a cell;
  verified against `GenSpawn.SpawningWipes` and `Placeworker_AttachedToWall`
  (a wall lamp sits on the floor cell IN FRONT of its wall, rot toward it).
  Lint rules 1/1b skip overlays; render draws them only on empty cells.
- `prelude.lua`, loaded under the sandbox before every template, hash on
  `meta.prelude_sha256`: `R/inner/corners`, `shuffle/jitter`, `try_place/
  try_near/scatter/along_wall/seat_around/wall_lights/dress`, `shell`
  (REFUSES a room with no named floor), `floor_patch/floor_worn`,
  `support_columns` (four columns when an interior exceeds 12x12 — the roof
  lint's real threshold, derived, not guessed), `LAST_PLACED`.
- `palette.json`: clutter tier (STOOL CRATE BARREL SHELF_SMALL END_TABLE
  DRESSER PLANT_POT WALL_LIGHT GAME PILLAR FENCE BARRICADE), floor tiers
  (FLOOR_FINE/_WORK/_YARD/_PLATE/_WET/_CELL, RUG), and faction blocks for
  Jawa_Junkers (filled out), Jawa_HuttCartel, Jawa_FreeDroidEnclaves,
  Jawa_DeepwaterCompact carrying their props (THRONE, DECAL, HOLO, CHARGER,
  REFINERY, WATER_TANK, HOSPITAL_BED, TRAP...). Every defName checked by
  `measure get` before use; `rimplace verify` MEASURED afterwards.
- selftest 41/41 (5 new: overlay coexists, wall_attach refuses without a
  wall, wall_attach places, prelude helpers, shell needs a floor); the old
  hardcoded `(16,14)` scrapyard assertion now reads the template's own
  declaration.

**Junkers rework (`9f6ba81b`)**: every interior floored by name (salvaged
plating/grating/tile — the tech default was `Gravel` = stony soil, i.e.
bare ground, which is exactly the complaint); zero fixed-step loops; `dress()`
in every room; depot shelving = wall runs + two loose island rows with a
kept-clear centre aisle; scrapyard gets real wrecks (`AncientPodCar`,
`AncientRustedCar`), `KOTOR_MineableJunk` heaps, slag, a fire pit, an
unfinished fence, and a boss's shack; cantina gets a bar counter with stools,
a carpet under the seating, pazaak, a bandfill.

**New sets (`2f04d3cd`, `f0fa7ed1`)**, each with a manifest in
`src/RimUtinni/AshkarrInhabited/Defs/SettlementManifestDefs/`, a gate posture
in `SecurityProfileDefs_District2.xml`, and an engine-tier archetype in
`Places_Inhabited.xml`:
- **Hutt Cartel — Gorga the Immense's Palace** (CSV row 28, tile 15088):
  `hutt_palace_hall` (colonnade, dais throne, red runway, clan decal, band
  corner, holo-dancers, lord's chamber, vestibule, majordomo's office),
  `hutt_spicehouse` (den on rugs + drug lab), `hutt_holding_pens` (cell row
  off a corridor, guardroom with barricades, a turret, barracks),
  `hutt_cistern_court` (unroofed walled court: tank cluster, well, fountain,
  troughs, warden's hut, sandbags + turret at the gate).
- **Free Droid Enclaves — The Cracking Yard** (row 107, tile 13177):
  `droid_charging_hall` (wall charging bays, heavy rechargers, gonks,
  reactor alcove, speakers' holo-table; NO beds/chairs/stove by palette),
  `droid_cracking_works` (7x7 fuel refinery in a walled yard, tank farm,
  control shed, one turret), `droid_fabrication_room`, `droid_battery_bunker`
  (double wall, battery banks, reactor).
- **Deepwater Compact — Deepwater Hold** (row 24, tile 2919):
  `deepwater_cistern_hall` (columned, tanks/fountains on mosaic, intake
  well, casks, warden's office), `deepwater_gate_bastion` (two staggered
  gates, sandbag lines, EMP traps, 3 turrets, guardhouse — the security
  vocabulary with teeth the depot sketch stood in for), `deepwater_hospital_
  ward` (monitored beds, surgery, scrub room), `deepwater_hydroponics_bay`
  (lamp clusters, a wall-mounted cooler, columns).

**Verification**: `lint` 0 findings on all 16 at manifest size; `verify`
MEASURED 0 MISSING on all 16 (sqlite rebuilt with `measure build` for the
2026-09-05T04-49-08Z capture); `validate_patch.py --live --defs` 7 files
0 errors 0 warnings; `dotnet build Inhabited.csproj -c Release` 0/0;
`rimplace selftest` 41/41. Renders reviewed by eye (Transient/
district_renders.txt, regenerate with Transient/district_lint.sh render).
All 16 exported to `src/RimMandrake/Inhabited/Templates/` and wired in
`TemplateFiles` (`b18edcac`).

**NOT done, deliberately**: no deploy, no ModsConfig change, no restart, no
bridge — same discipline as every prior batch. Owed to a live pass:
deploy `Inhabited` + `AshkarrInhabited`; a review SAVEGAME per the owner's
2026-09-02 ruling — one quicktest map, all 16 districts on a grid with
>=6-cell pitch (largest is 30x30), a grid-key item file, keeper saves backed
up first and `jawa/list_things` per cell before calling it a review; then
his verdict per room. Still only `districts[0]` composes per visit. Other
factions (Wildsteam, Foundry Hive, Trade Moot, Helix) have roster material
but no set yet; Trade Moot's is thinnest (no "Technology and economy"
section in the roster).
