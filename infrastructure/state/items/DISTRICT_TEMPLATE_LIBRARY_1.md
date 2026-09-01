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
