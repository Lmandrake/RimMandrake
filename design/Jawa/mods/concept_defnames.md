> "Faction Filter" never existed; the live equivalents are **Sensible Factions** (3531306011) and **Faction Control** (2882785581).

# concept_defnames.md — verified defName / ID vocabulary (companion to concept.md)

_A portable reference of defNames, packageIds, and Workshop IDs we've **confirmed from actual files** during design. Companion to `concept.md`. **Discipline: every entry below must still be re-confirmed against the user's actually-installed 1.6 mods before it is used in a patch or save-edit** — mods rename defs between versions, and a wrong defName in a save's thing-ID graph is unforgiving. Treat this as "known-good starting guesses," not ground truth._

**Snapshot date:** 2026-08-03. **Legend:** ✅ read from local source this campaign · 🔎 confirm in-game before relying on it.

---

## packageIds (mod identity — for `PatchOperationFindMod` / load checks)
- `brrainz.harmony` — Harmony ✅
- `VanillaExpanded.HelixienGas` — Vanilla Helixien Gas Expanded, Workshop `2877699803` 🔎 ADOPTED 2026-08-10, **not yet installed**; re-confirm packageId from About.xml once subscribed
- `OskarPotocki.VanillaFactionsExpanded.Core` — Vanilla Expanded Framework (VEF Core) ✅
- `VanillaExpanded.VFEFactory` — Vanilla Furniture Expanded – Factory ✅
- `vanillaexpanded.gravship` — Vanilla Gravship Expanded (VGE) ✅ _(used as `MayRequire` target by VFE-Factory)_
- `VanillaExpanded.VEE` — Vanilla Events Expanded ✅
- `VanillaExpanded.VWEMS` — Vanilla Weapons Expanded – Makeshift ✅
- `neronix17.toolbox` — Neronix17 Toolbox / "Tabula Rasa" (hard dep of all Outer Rim) ✅
- `Neronix17.Asimov` — Asimov auto-crafter framework (dep of Droid Depot) ✅
- `Neronix17.Outland.Genetics` — Outland Genetics ✅
- `Mlie.ReinforcedMechanoid2` — Reinforced Mechanoids 2 ✅
- `Krkr.rule56` — CAI-5000 (Advanced AI + Fog Of War) ✅
- `lwm.deepstorage` — LWM's Deep Storage ✅
- `mandrake.jawa.patches` — our custom local compat mod (loads LAST) ✅ _(our own id)_

## Research project defNames (gates)
- `VFE_BasicFactories` — VFE-Factory basic tier (prereq Machining) ✅
- `VFE_ComplexFactories` — VFE-Factory complex tier (prereqs BasicFactories + Fabrication) ✅
- `RM_ReinforcedMechanoids` — Reinforced Mechanoids 2 Gestalt Engine research (leave UNRESEARCHED to keep enemy-side-only) ✅
- Odyssey `Basic Gravtech` / `Advanced Gravtech` — vanilla gravship research 🔎 _(confirm exact defNames; also note the Configurable-Techprints "no defName ending in a digit" engine limit)_

## VFE-Factory building / process defNames ✅
- `VFEFactory_AutomatedSmelter` — the salvage→metal building (in the `VFEFactory_Factories` architect tab)
- `VFEFactory_SmeltWeapon` — process: broken/unwanted weapons → 10 steel each
- `VFEFactory_SmeltApparel` — process: apparel → 10 steel each
- `VFEFactory_AlloyGravlite` — Alloy Forge recipe making gravlite (⚠️ design tension: a second route to gravlite independent of Advanced Gravtech research — gate BOTH if gating gravlite)
- `VFEFactory_AstrofuelFromChemfuel` — VFE-Factory's astrofuel process; **outputs `VGE_Astrofuel`** and is gated `MayRequire="vanillaexpanded.gravship"`
- `ResultWorker_Smelt` — worker governing smelter yield (tune recipe results/count down if returns feel too generous)

## VGE (gravship) defNames ✅
- `VGE_Astrofuel` — astrofuel ThingDef (VGE's own; the intended flight/generator fuel)
- `VGE_Make_AstrofuelFromChemfuel` — VGE's own astrofuel recipe (70 chemfuel → 35 astrofuel, 2:1 loss, 5000 work, BiofuelRefinery, gated behind BasicGravtech)

## Outer Rim / Droid Depot / Asimov ✅
- `OuterRim_DroidBrain` — the scarce component every buildable droid costs (self-limit lever: keep RARE/salvage-gated so droids stay elite, not a workforce)
- `Asimov.Building_AutoCrafter` — the buildable Droid Factory building class
- `CompProperties_AutoCrafter` / `WorkGiver_FillAutoCrafter` — Asimov auto-crafter comp + workgiver
- ⚠️ humanlike combat droids (Battle/SuperBattle/Commando/MagnaGuard/Tactical/SuperTactical/KX/HK/Protocol/ImperialLabor) all carry `enableAllWorkTypes=true` (they labor too — "build only soldiers" ≠ combat-only)

## Lightsaber (quest-only containment) ✅
- `CompDeflector` with `baseDeflectChance = 0.99` + `deflectRatePerSkillPoint 0.015` — the arms-race vector on lightsabers (high-Melee wielder ~bulletproof vs ranged). Blade melee ~26 edge @ cooldown 2.5 = plasteel-tier only. Containment = quest-earned only + craft recipe disabled (do NOT inject as generic loot).

## Vanilla-save structure landmarks (for save-editing) ✅
- `<game><scenario>` — entire scenario baked here (name/summary/parts)
- Scenario part types seen: `ConfigureStartingPawns`, `StartingResearch`, `StartingThing_Defined` (with counts), `PlayerPawnsArriveMethod` (=Gravship), `GameStartDialog`, and modded `LoanMod.ScenPart_Loan`
- Player faction `GravshipCrew` — starting crew live here; each pawn has `<story>` (childhood/adulthood/traits/appearance) + `<skills>` (12 skills, level + passion); xenotype referenced by mod defName; `customXenotypeDatabase` empty when the xenotype is a mod def
- Save is plain human-readable XML; legible low-linkage nodes (scenario, pawn story+skills, faction names) are safe to hand-edit; the **thing-ID reference graph and raw map cell data are the fragile region** (relevant to Tier 2b live-map enrichment)

## Workshop IDs (quick lookup — see concept.md §4 for full context)
VFE-Factory deps aside, key WS IDs: Makeshift 2419690698 · Nomad Scavenger 3132099594 · SW Xenotypes 2915192253 · Outer Rim Toolbox/Tabula Rasa 1660622094 · Outland Genetics 2910172297 · KotOR Ships VGE 3614012898 · Gravship Blueprints 3575162262 · CAI-5000 (continued) 3673768803 · Reinforced Mechanoids 2 (via Mlie) · Configurable Techprints 2876747024 · Cherry Picker 3521312241 · Sensible Factions 3531306011 · Choose Biome Commonality 2582875043 · Map Designer 2111424996 · Backstory Constructor 2907131508 · No Durability 3260461453 · MultipleTraders 2070709529 · Trading Options 2876541977 (1.6 update 3524414310) · Ideology Scavenger Role 3565039115.

_(These IDs were captured from search/About.xml during design; a few were 429-blocked and inferred — re-confirm the exact ID in RimSort/Workshop before subscribing. Full provenance and caveats live in the campaign's context.md.)_
