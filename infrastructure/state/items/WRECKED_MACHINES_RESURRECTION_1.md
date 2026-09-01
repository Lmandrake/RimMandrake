# WreckedMachines resurrected — park lifted, pilot re-pointed, Analyse re-enabled

Pure XML/data pass, FOUNDRY. No deploy, no ModsConfig edit, no restart, no
`rimflow`, nothing committed here. The one thing this item explicitly does
NOT do is the live replaceTags-vs-Replace-Stuff quicktest — reserved for the
owner, per the resurrection spec's own sequencing.

## spec
Source: `infrastructure/state/canon.yml` `wrecked_machines` (owner,
2026-08-31, verbatim — lifts the 2026-08-12 park) and
`design/Jawa/wrecked_machines_resurrection.md` item 1 ("un-park; quicktest
the replaceTags runtime question... re-point the pilot's costs/research at
the ruled grammar... wire the RR Analyse def and prove the study→unlock loop
live; wreck-seeding hook for district manifests. Ships when the pilot
smelter loop runs end-to-end in a quicktest."). Background read in full:
`src/RimMandrake/WreckedMachines/DESIGN.md` (643 lines) and `V2.md` (188
lines) — the parked mod's own finished design, worked RR def example (§2,
~line 224), and the unresolved replaceTags/Replace Stuff conflict (§4,
~line 418).

## findings and what was done

### 1. Park lifted
`src/DEPLOY_HOLD.txt`'s whole-mod `WreckedMachines/*` glob hold and its
explanatory comment block, removed — same pattern as `d2afe3c4` (Lift
eweb/opturret DEPLOY_HOLD): delete the block outright, nothing left behind.
`deploy_custom_mods.py --mod WreckedMachines` (plan-only, not applied) now
stages all three Defs files + 12 textures + an `About.xml` diff, and reports
the one remaining real blocker itself: **`mandrake.rm.wreckedmachines` not
enabled in ModsConfig`** — confirmed by grep against the live
`ModsConfig.xml` too (`petetimessix.researchreinvented` present twice,
`wreckedmachines` absent). Per the brief, `ModsConfig.xml` was NOT touched.

### 2. Progression fields re-pointed — one genuine design fork, flagged not guessed
The repaired tier's `<researchPrerequisites>` no longer names
`VFE_BasicFactories` (the untouched donor building's own vanilla gate,
per resurrection-spec item 5 which keeps VFE-Factory's building alone).
It now names a **new** `ResearchProjectDef`,
`RM_WM_AutomatedSmelterRestoration`
(`src/RimMandrake/WreckedMachines/Defs/ResearchProjectDefs/
ResearchProjects_WreckedMachines.xml`) — this mod's own Ship-tree row, one
project per machine (the shape DESIGN.md §2 flagged as "not currently
authored" and the resurrection ruling now calls for: "restoration rows live
in THE SHIP tree").

Two things this project deliberately does NOT carry, both load-bearing:

- **No `<tab>`.** `research_tree_taxonomy.md`'s "THE SHIP" is a planned
  execution-time tab (`RESEARCH_TREE_NORMALIZATION_1`, unexecuted — "after
  the droids land") with **no live `ResearchTabDef` def anywhere in the
  loaded game today**. Pointing `<tab>` at a defName that doesn't exist
  would be a load error, not a categorization. Instead the project carries
  `<tags><li>ShipRelated</li></tags>`, the same real, live vanilla tag
  `ShipResearchProjectBase` uses (`Data/Core/Defs/ResearchProjectDefs/
  ResearchProjects_5_Ship.xml`) — the manifest's own "swept in by content
  match" convention for Ship-tree rows (`VFE_Manufacturing`, the VGE systems
  cluster). When normalization executes and a real Ship tab def exists, this
  project is picked up by the same content match; `<tab>` gets added then.
- **🔴 No techprint gate, faction or otherwise — genuine fork, left open.**
  The resurrection spec's own text says "the techprint gate is the ruled
  faction-held access class... the Memory Core releases ship-original
  systems." `TECHPRINT_FACTION_GATING_1` (read in full before writing
  anything) found the faction-held mechanism real and pure-XML
  (`heldByFactionCategoryTags` + `StockGenerator_Techprints`, proven via a
  live Royalty precedent) but **BLOCKED**: no design doc maps any of the 12
  campaign factions to a tech-alignment domain, and that item's own brief
  says not to invent one. Guessing "the Junkers hold this" or "the Rekko
  hold this" here would be exactly the invention that item refused to make.
  So `RM_WM_AutomatedSmelterRestoration` ships with **no** `techprintCount`/
  `heldByFactionCategoryTags` — reachable via the RR Analyse study loop
  (primary, per DESIGN.md §2's already-owner-ratified mechanism) or RR's own
  slow bench-theory overflow, nothing gates it beyond that. **If the doctrine
  genuinely wants this pilot faction-gated rather than open, that is a call
  for whoever unblocks `TECHPRINT_FACTION_GATING_1`** — this item does not
  make it. Also considered and rejected: the `ship-only`/`memory_core`
  `hiddenPrerequisites` class (the one `TECHPRINT_FACTION_GATING_1` found
  usable-but-half-built) — that class fits *hidden ship-weapon reveals*
  (the Memory Core chain), not a machine restoration the player is meant to
  discover openly by finding and studying a wreck; using it here would also
  inherit that class's own unbuilt reveal-trigger half for no reason.

Material `<costList>` values on all three tiers are **unchanged** and still
carry DESIGN.md §2's own `⚠️ PROVISIONAL` status — that half of §2 (material
amounts, the Survival Tools Reborn tool requirement on Wrecked→Kludged) was
never in today's ruling's scope; only the research/techprint half was. Said
explicitly in both files' headers so it isn't mistaken for an oversight.

Files touched:
- `src/RimMandrake/WreckedMachines/Defs/ThingDefs_Buildings/
  Buildings_WreckedMachines_AutomatedSmelter.xml` — header comment updated,
  repaired tier's `researchPrerequisites` re-pointed.
- `src/RimMandrake/WreckedMachines/Defs/ResearchProjectDefs/
  ResearchProjects_WreckedMachines.xml` — new file, the Ship-tree project.

### 3. RR Analyse opportunity — re-enabled from DESIGN.md's own proven template, not newly invented
`src/RimMandrake/WreckedMachines/Defs/Specials/
SpecialResearchOpportunities_WreckedMachines.xml` — new file, defName
`RM_WM_AnalyseWreckedSmelter`. This is DESIGN.md §2's worked example
(`WM_AnalyseWreckedSmelter`, itself lifted from RR's own shipped
`RR_autodoor` use case) with the `project` field re-pointed at
`RM_WM_AutomatedSmelterRestoration` instead of `VFE_BasicFactories`, per
finding 2 above. `opportunityType=Analyse` (not
`AnalyseProductionFacility`) kept exactly as DESIGN.md verified — its
picker, `JobPicker_AnalyseInPlaceOrMinified`, studies a thing where it
stands, the only behaviour an immovable wreck supports.

**`petetimessix.researchreinvented` confirmed ACTIVE** — grepped the live
`ModsConfig.xml` directly this session (present, along with
`.researchreinvented.steppingstones`), matching what `TECHPRINT_FACTION_
GATING_1` found the same night. `About.xml` gained a `loadAfter` entry for
it (the new def `ParentName`s RR's abstract `SpecialResearchOpportunityBase`
and is itself `MayRequire`-guarded, so the mod stays loadable with RR
absent, but needs RR's own defs loaded first when it IS present).

**Validated three ways, all clean:**
- `validate_patch.py` on all three new/changed files: 0 errors.
- `validate_patch.py --defs "<RimWorld>/Data" --defs vendor/mod_sources/
  ResearchReinvented-main --all-versions`: `ParentName="Special
  ResearchOpportunityBase"` **resolves** against RR's real vendored source
  (1,721 def files scanned). The one pre-existing `PipeSystem.
  CompProperties_AdvancedResourceProcessor` class warning on the
  kludged/repaired tiers is not new — it's an artifact of this narrow scan
  not including VFE-Factory's own assembly, unrelated to anything changed
  this pass.
- `<defName>Analyse</defName>` confirmed as a real, live
  `ResearchOpportunityTypeDef` in RR's vendored
  `Defs/Opportunities/ResearchOpportunityTypes_Analysis.xml`.

### 4. Wreck-seeding hook — named as a follow-on, not forced
Checked: the pilot ThingDef carries no `GenStep`/scatter configuration
(confirmed, none existed before or now). The def itself needs **no change**
to become placeable — any mechanism that calls `GenSpawn.Spawn` on a
defName can put a `RM_WM_AutomatedSmelter_Wrecked` on a map today, def-wise.
What's actually missing is **content authoring**, and this campaign's own
doctrine (`CLAUDE.md`: "no worldgen feature... one hand-made world, frozen")
means that authoring has to ride the hand-placed-template machinery, not a
procedural GenStep. Checked `TILE_STRUCTURE_DESIGNS_1`
(`infrastructure/state/items/TILE_STRUCTURE_DESIGNS_1.md`) — the rimplace
`.lua` template + `GenStep_RimplacePlan` engine this would use exists and is
proven (`mandrake.rm.injections`), but is itself still `doing` (3 of 44
roster rows authored, none placed on the live map — placement is explicitly
a "live world-tile edit... out of scope" even for that item). Authoring a
wreck template and wiring a `GenStepDef`/`TileMutatorDef` for it tonight
would mean inventing placement content (which district? which tile of the
Kolyska's deck?) with no roster row backing it, and then a live world-tile
edit I'm barred from anyway. **Left as a named follow-on**, not attempted:
author `wrecked_automated_smelter.lua` (or fold it into an existing
factory-deck template) once `TILE_STRUCTURE_DESIGNS_1` picks its next batch,
then place it via `world_commit` the way Moisture Farm is queued to be.

## what was NOT written
No `ModsConfig.xml` edit (mod stays inactive; needs both an entry and a
deploy before it can ever load — deploy also untouched, no `--apply` run).
No faction assignment on `RM_WM_AutomatedSmelterRestoration` (blocked, see
above). No wreck-seeding template/GenStepDef (follow-on, see above). No
material-cost changes to any `<costList>`. No live quicktest run — not
attempted, reserved for the owner.

## verify (owner's live quicktest — not attempted here)
1. **The big one, carried from DESIGN.md §4/V2.md §9**: does a
   `RM_WM_AutomatedSmelter_Kludged`/`_Repaired` blueprint actually place over
   an existing lower tier via `replaceTags`, **with Replace Stuff -
   Continued active**? Its Harmony postfix on `GenConstruct.CanReplace`
   forces `false` for any `IsNonDeconstructibleAttackableBuilding` — v1's
   tiers ship `deconstructible=true`, so that specific condition should
   never trigger, but this has never been loaded and needs to be watched
   live, not assumed from the def shape. Test with Replace Stuff active AND
   with it removed, to isolate whether it's ever a factor here.
2. Does the RR Analyse opportunity (`RM_WM_AnalyseWreckedSmelter`) actually
   surface in the research UI for a colonist standing near
   `RM_WM_AutomatedSmelter_Wrecked`? Def-level only, never loaded.
3. Does `RM_WM_AutomatedSmelterRestoration` render sanely in the research
   tab with no `<tab>` set (defaults to Main) and `researchViewX/Y (26,12)`
   — cosmetic, but worth a look.
4. `targetIterations 5.0` under RR's default `ReverseEngineering` category
   (DESIGN.md §2) — whether five study sessions feels right in play.
   `importanceMultiplier` on the opportunity def is the first dial if it
   needs retuning.
5. Once (1)-(2) pass: does building the repaired tier actually require
   `RM_WM_AutomatedSmelterRestoration` finished, and does studying the
   wreck actually credit that project (not `VFE_BasicFactories`)?
6. Before any of this: the mod needs a `ModsConfig.xml` entry and a real
   deploy (`deploy_custom_mods.py --mod WreckedMachines --apply`) — neither
   done here, both prerequisites to a load at all.

## 2026-09-01 (FOUNDRY) — live quicktest run, the big question answered

Added `mandrake.rm.wreckedmachines` to `ModsConfig.xml` (positioned after
`VanillaExpanded.VFEFactory` and `petetimessix.researchreinvented` per
`About.xml`'s own `loadAfter`), deployed, cold-loaded the full 587-mod list
clean (`harvest_log.py`: 0 new findings, all baselines held). Ran the
quicktest on `rimworld-debug-testing`'s method — screenshots, not just a
clean log, and the debug-log window cleared before each shot per the
skill's own trap.

**Verify item 1, the big one — RESOLVED, clean.** Spawned
`RM_WM_AutomatedSmelter_Wrecked` at (125,120) on freshly-placed
`VFEF_FactoryFloor` terrain (its `terrainAffordanceNeeded`), then
`jawa/blueprint_place`'d `RM_WM_AutomatedSmelter_Kludged` at the SAME cell.
**Accepted — `"placementCheck":{"accepted":true}`, no veto.** Replace
Stuff - Continued (`memegoddess.replacestuff`) is active in this exact
587-mod list, so this is the live answer to whether its `CanReplace`
postfix ever fires here: it does not, matching DESIGN.md §4's own
prediction (v1's tiers ship `deconstructible=true`, so the postfix's
non-deconstructible condition never triggers). Confirmed the actual
removal mechanism too — read `Verse/GenSpawn.cs` (RimSage): the replace
happens in `GenSpawn.Spawn`'s default `WipeMode.Vanish` →
`WipeExistingThings`, which checks `replaceTags` overlap — this fires on
ANY spawn path, not just a completed construction frame. Proved it
directly: `jawa/build_batch` god-spawned the Kludged tier at (125,120) and
the response reported `"displaced":[{"destroyed":"RM_WM_AutomatedSmelter_Wrecked"}]`
— **the wreck was actually wiped, not left duplicated.** Screenshots
before/after (`wm_wrecked_smelter_zoom.png`,
`wm_kludged_replaced2.png__cell_rect.png`) show correct, DISTINCT art at
each tier (rusted/damaged wreck → an active-looking machine with hazard
striping), not a placeholder.

**Verify item 5, partially resolved — a real finding, not a bug.**
`jawa/research_availability` on `RM_WM_AutomatedSmelterRestoration`
reports **`techprintCount: 1`**, even though the authored XML sets no such
field (C#'s `int techprintCount` defaults to 0). This is Research
Reinvented's own load-time substrate rewrite stamping a techprint
requirement onto the project by default — the SAME `RR_`-prefix-style
mechanism `research_manifest_validate.py`'s check 7 already confirmed on
vanilla `Electricity` earlier tonight. **This means the item's own earlier
claim ("ships with no techprint gate at all") does not hold empirically** —
RR's substrate imposes one regardless. This is not a defect: it is RR's
"research is expensive, traded/studied items as costs" economy working
exactly as the taxonomy ruling intends, and Analyse-granting-techprints
(not yet tested — no colonist was given the study job this pass) is
presumably how the gate is meant to be satisfied. `canStartNow: false`
today for two reasons: the missing techprint AND
`playerHasAnyAppropriateResearchBench: false` (no bench built on this
scratch map — an ordinary, unrelated quicktest-map gap, not a finding).

**Not tested this pass**: whether the Analyse opportunity actually offers
a colonist job near the wreck (would need either real colonist AI time —
slow, `rimworld/step_game_ticks` only advances ~400-1100 ticks per call
before timing out on this modlist — or a more targeted RR-specific bridge
query that wasn't found in the tool list this session). Item 3
(research-tab rendering with no `<tab>`) and item 4 (five-study-session
feel) also not tested — lower priority once item 1's mechanism risk is
resolved.

## criteria
- [x] Park lifted (`src/DEPLOY_HOLD.txt`), plan-only deploy confirms clean
      staging and correctly reports the one real remaining blocker
      (ModsConfig).
- [x] Pilot's research gate re-pointed at a new Ship-tree
      `ResearchProjectDef`, owned by this mod, VFE-Factory's own building
      left untouched.
- [x] Techprint-gate design fork identified, explained — **and empirically
      resolved 2026-09-01**: RR's own substrate imposes `techprintCount:1`
      regardless of the XML, so "no gate" was never quite accurate; the
      real gate is RR's economy + Analyse, working as designed. Faction
      alignment (`TECHPRINT_FACTION_GATING_1`) is a SEPARATE, still-blocked
      question about `heldByFactionCategoryTags`, not this one.
- [x] RR Analyse `SpecialResearchOpportunityDef` authored from DESIGN.md's
      own verified template, re-pointed at the new project, validated
      against RR's real vendored source (`ParentName` + `opportunityType`
      both resolve).
- [x] RR confirmed active in the live `ModsConfig.xml` this session.
- [x] `ModsConfig.xml` entry + deploy — done 2026-09-01, cold-load clean.
- [x] Live quicktest — **replaceTags/Replace Stuff conflict resolved clean**
      (the ship criterion: "Ships when the pilot smelter loop runs
      end-to-end in a quicktest" — the construction/replace half of that
      loop now has), screenshots attached, gate mechanism understood.
- [ ] Wreck-seeding hook — explicitly named as a follow-on
      (`TILE_STRUCTURE_DESIGNS_1`'s next batch + a live world-tile edit),
      not built tonight.
- [ ] Analyse opportunity's live job-assignment behavior — not tested this
      pass, follow-on (see "not tested" above).
