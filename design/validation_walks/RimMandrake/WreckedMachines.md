# WreckedMachines — validation walk
subject: src/RimMandrake/WreckedMachines  (packageId mandrake.rm.wreckedmachines)
deps: VanillaExpanded.VFEFactory (hard modDependency, "Vanilla Furniture Expanded - Factory" — donor of `VFEFactory_AutomatedSmelter`, left untouched); soft loadAfter on `OskarPotocki.VanillaFactionsExpanded.Core` and `petetimessix.researchreinvented` (MayRequire-guarded, mod loads fine without it)
list: full   # VFEFactory is not in the minimal list
status-hint: three-tier restoration ladder for a wrecked VFE-Factory automated smelter — WRECKED (dead rubble) → KLUDGED (bodged, 3 recipes only) → REPAIRED (full function, cosmetically distinct) — built over each other via vanilla's `replaceTags`, v1 pilot: both this mod's and the donor's buildings coexist in the build menu on purpose.

## must be true
- Three `ThingDef`s exist, sharing `replaceTags: WM_AutomatedSmelter` so each can be built directly over another: `RM_WM_AutomatedSmelter_Wrecked`, `RM_WM_AutomatedSmelter_Kludged`, `RM_WM_AutomatedSmelter_Repaired` (`WreckedMachines/Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml`).
- WRECKED: `costList Steel 30`, `deconstructible true` (v1 — "Sacred Scrap" non-deconstructible is deliberately deferred), no comps at all (no power, no heat, no `CompProperties_Explosive` — "POWER DENSITY explodes, not the fact it's a machine" ruling), `MaxHitPoints 450`, `Beauty -30`.
- KLUDGED: `costList Steel 120 + ComponentIndustrial 3`, `constructionSkillPrerequisite 4`, `MaxHitPoints 300`, `VEF_BuildingBreakdownFactor 6` (donor's is implicitly 1× — this is twice as breakdown-prone), `basePowerConsumption 360` (donor draws 300), `CompProperties_AdvancedResourceProcessor.canOverclock false`, and exactly THREE processes: `VFEFactory_SmeltMetalFromSlag`, `VFEFactory_SmeltMetalFromMechSlag`, `VFEFactory_SmeltWeapon` (donor's fourth/fifth/sixth — `SmeltApparel`, `SmeltMetalFromChunk`, `SmeltMechanoid` — deliberately absent).
- REPAIRED: `costList Steel 260 + ComponentIndustrial 7`, `constructionSkillPrerequisite 6`, `MaxHitPoints 450`, `basePowerConsumption 300`, `canOverclock true`, all SIX processes present (mechanically identical to the donor except texPath/defName/label/description), `researchPrerequisites: RM_WM_AutomatedSmelterRestoration` — NOT `VFE_BasicFactories` (the donor's own untouched gate).
- `ResearchProjectDef RM_WM_AutomatedSmelterRestoration` exists: `baseCost 2000`, `techLevel Industrial`, `tags: ShipRelated`, ships with NO techprint gate (deliberately — `TECHPRINT_FACTION_GATING_1` is blocked) (`WreckedMachines/Defs/ResearchProjectDefs/ResearchProjects_WreckedMachines.xml`).
- `SpecialResearchOpportunityDef RM_WM_AnalyseWreckedSmelter` (`ParentName="SpecialResearchOpportunityBase" MayRequire="petetimessix.researchreinvented"`) points `project` at `RM_WM_AutomatedSmelterRestoration` and `things` at `RM_WM_AutomatedSmelter_Wrecked`, `opportunityType Analyse` (`WreckedMachines/Defs/Specials/SpecialResearchOpportunities_WreckedMachines.xml`) — resolves only when Research Reinvented is present; absent it, the def is simply skipped (MayRequire), not an error.
- The donor's own `VFEFactory_AutomatedSmelter` is hidden from the build menu via
  `Patches/WreckedMachines_HideDonorSmelter.xml` (`PatchOperationFindMod`-guarded, clears
  its `designationCategory`) — owner ruling 2026-09-16, verbatim *"remove the VFE factory,
  not the manual one"* (`WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1`). This patch shipped inert
  from 2026-09-17 to 2026-09-21 because it sat under `Defs/Patches/` instead of the mod's
  top-level `Patches/`, where RimWorld's def loader silently discarded it; relocated by
  `PATCH_FILES_UNDER_DEFS_INERT_1`. It is no longer "a known, accepted v1 cost" — the
  coexistence was never intended and About.xml/DESIGN.md called it a testing arrangement.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.wreckedmachines" and no XML error naming any WreckedMachines Def   # load-time; with Research Reinvented ABSENT, also confirm no error about the MayRequire-guarded `SpecialResearchOpportunityDef` — it should just not exist, not fail
2. [D] def read-back: `ThingDef RM_WM_AutomatedSmelter_Wrecked` exists; `costList.Steel` = 30; `building.deconstructible` = true; no `CompProperties_Explosive` in `comps`
3. [D] def read-back: `ThingDef RM_WM_AutomatedSmelter_Kludged` exists; `comps[CompProperties_AdvancedResourceProcessor].processes` contains exactly `VFEFactory_SmeltMetalFromSlag`, `VFEFactory_SmeltMetalFromMechSlag`, `VFEFactory_SmeltWeapon` and NOT `VFEFactory_SmeltApparel`/`SmeltMetalFromChunk`/`SmeltMechanoid`
4. [D] def read-back: `ThingDef RM_WM_AutomatedSmelter_Repaired` exists; `researchPrerequisites` contains `RM_WM_AutomatedSmelterRestoration` and does NOT contain `VFE_BasicFactories`
5. [D] def read-back: `ResearchProjectDef RM_WM_AutomatedSmelterRestoration` exists; `baseCost` = 2000; `tags` contains `ShipRelated`; no `techprintCount`/`heldByFactionCategoryTags` field present
6. [B] `jawa/spawn_thing {defName: "RM_WM_AutomatedSmelter_Wrecked"}` on `FactoryFloor` terrain → success, then `jawa/list_things` confirms it exists with 0 comps and `deconstructible=true`
7. [B] `jawa/research_finish_project {defName: "RM_WM_AutomatedSmelterRestoration"}`, then attempt to build `RM_WM_AutomatedSmelter_Repaired` over the spawned wreck's cell (the `replaceTags` build-over) — confirm the build succeeds and the wreck is replaced, not stacked; this is DESIGN.md/the item file's own flagged "NOT VERIFIED AT RUNTIME" risk (Replace Stuff - Continued's Harmony postfix forcing `CanReplace=false` on non-deconstructible buildings — does not apply here since v1 ships `deconstructible=true`, but confirm live rather than trusting that reasoning)
8. [B] (only if Research Reinvented is active) confirm `RM_WM_AnalyseWreckedSmelter` actually surfaces as a study option in the research UI for a colonist standing near the wrecked-tier building — flagged as unverified in the def's own header comment
X. [S] (human pass) compare the WRECKED/KLUDGED/REPAIRED art against each other and the donor's own smelter sprite — ⬇️ **superseded as the authority by the `## north star` section below**, which makes this a binding bar rather than a deferred concern.

## north star
state: VALIDATED
validated-hash: 70881b98e8c1c01754802ea14a6db3e7650d9ac9dd502a246c95fa7f9ea9806c

The `state:` line above is authoritative; `design/RimMandrake/north_star_validation_spec.md`
defines what each state means and §6 covers staleness. Ruled in the owner's sitting of
2026-09-16 — his three rulings are marked 🔴 inline. Amend only in another sitting with
him: the recorded hash covers this whole section, so any edit reverts it to DRAFT until he
re-validates.

### the experience  (OWNER'S WORDS — verbatim)

2026-09-01, filing `WRECKED_MACHINES_RESURRECTION_1`:

> *"And then there's the speck for the Wrecked Machines mod... let's ressurect that
> now! Fix it. Make it work in the new regime."*

2026-09-15, filing `RAKATAN_ARCHOTECH_MACHINES_1` — the vision quote:

> *"It becomes a core Rakatan tech trait: it's ROBUST. It SURVIVES. It degrades
> gracefully whenever possible. Their ships are ancient and still somewhat
> functional. Their batteries just slowly lose capacity over millenia yet still work.
> And if we could refurbish them, they would exceed modern technology even in a still
> kludged manner. The existing mod is about repairing big machines in place, and
> that's excellent. […] Defunct, weakly functional, or semi-functional versions will
> be found in the game and added to the ship by the player as a form of sacred loot."*

📄 The mod's own About.xml is already written as vision prose, and is treated here as
part of the experience statement:

> *"Holy wreckage. The Kolyska's factory did not fail politely. Its machines are still
> bolted to the deck where they died — split open, scavenged, corroded, half-buried in
> their own slag. […] WRECKED — Dead. […] Occupies its tiles, does nothing, cannot be
> removed. Scenery and reproach. […] REPAIRED — holes filled with metal that does not
> match, cabling routed almost neatly, a few improvised vents still smoking. Full
> function. **It will never look factory-fresh again.**"*

🔑 Through-line: **a machine that died in place and survived dying.** Not rubble, not a
fresh build — a thing that endured, and shows it.

### must show

**The three tiers, told apart**
- [ ] `tiers_distinguishable_at_glance` — wrecked, kludged and repaired are told apart
      at play zoom with no tooltip and no click. 🔴 **Owner ruling, 2026-09-16**: kept
      as ONE line judging all three together. I challenged it — rendered at true play
      zoom (drawSize 4×5 → 256×320 px), wrecked-vs-repaired is instant via the lit
      ring, but wrecked-vs-kludged takes a beat since both are grey-brown domes and the
      difference is voids-versus-patches. He looked and ruled the read sufficient. His
      eye is the authority on whether art reads.
- [ ] `wrecked_reads_as_dead` — a WRECKED machine reads as dead: split open, missing
      chunks, nothing lit. *"Scenery and reproach."*
- [ ] `kludged_reads_as_bodged` — a KLUDGED machine reads as bodged, not finished:
      mismatched plate and exposed cabling visible on the sprite.
- [ ] `repaired_reads_as_running` — a REPAIRED machine reads as running. The lit amber
      ring is the tell the art already has, and the clearest in its family.
- [ ] `repaired_never_factory_fresh` — even REPAIRED still shows its scars. Its own
      About: *"It will never look factory-fresh again."*
- [ ] `wrecked_degraded_not_absent` — a wreck reads as a machine that SURVIVED in a
      degraded state, not as rubble or an empty footprint.

**Placement in the world**
- [ ] `wreck_occupies_its_tiles` — a wreck fills its own 3×4 footprint and reads as
      bolted in place, not as a small prop in a large empty rectangle.
- [ ] `wreck_reads_as_worth_saving` — a wreck reads as something a scavenger would
      want, not as trash to clear. His *"sacred loot"*, *"Holy wreckage."*

**The Rakatan reinterpretation**

🔴 **Owner ruling, 2026-09-16**: these four lines are included NOW, with the cost
accepted explicitly — they judge content that does not yet exist, because
`RAKATAN_ARCHOTECH_MACHINES_1` is an unstarted design session. He chose to bind his
freshest vision while it is still in his head rather than wait. Expect them to refuse
this mod until that design lands; that is intended, not a defect.

- [ ] `rakatan_reads_as_ancient` — a wreck reads as ANCIENT technology, not as
      recently-broken industrial kit. *"Their ships are ancient and still somewhat
      functional."*
- [ ] `degradation_reads_as_graceful` — a partly-functional machine reads as working at
      reduced capacity, not as broken-and-inert. *"It degrades gracefully whenever
      possible… batteries just slowly lose capacity over millenia yet still work."*
- [ ] `refurbished_reads_beyond_modern` — a refurbished Rakatan machine reads as BETTER
      than its modern equivalent while still visibly kludged. *"They would exceed modern
      technology even in a still kludged manner."* ⚠️ The hardest line here: "better than
      modern" has no established visual vocabulary in this repo yet.
- [ ] `rakatan_reads_as_sacred` — a Rakatan machine reads as venerable, something a Jawa
      clan would revere rather than merely salvage. *"A form of sacred loot."*

### cannot show

- [ ] `never_two_identical_smelters` — ours and the donor's smelter appearing
      indistinguishably in the build menu or on the map. `WRECKEDMACHINES_VFE_SMELTER_
      REMOVAL_1` closed source-side 2026-09-17: `Defs/Patches/WreckedMachines_
      HideDonorSmelter.xml` clears `VFEFactory_AutomatedSmelter`'s
      `<designationCategory>` (PatchOperationFindMod-guarded on the donor mod, same
      technique as `RSW_Armoury/Patches/Warcasket_BuildPathCut.xml`), per owner ruling
      2026-09-16 verbatim *"remove the VFE factory, not the manual one"* — vanilla's
      `ElectricSmelter` ("the manual one") is untouched. Live verify still owed: a
      game-up load must confirm Architect > Factories no longer offers the donor
      smelter and no new "Could not resolve cross-reference" appears.
- [ ] `never_reads_as_donor_machine` — a tier that reads as the donor's intact VFE
      smelter rather than as our wreck.

### known non-visual blocker
**This mod ships no Mod Settings at all** — no `ModSettings` or
`DoSettingsWindowContents` anywhere under `src/RimMandrake/WreckedMachines/` (MEASURED
2026-09-16). That violates the owner's every-mod-ships-settings ruling and will block a
GREEN independently of every line above. → `WRECKEDMACHINES_MOD_SETTINGS_1`.
