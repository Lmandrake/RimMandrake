# Biome mod unification — execution spec (BIOME_MOD_UNIFICATION_1)

Executes §7 Q17 of `design/RimMandrake/biome_mod_architecture.md`: all RM-tier biome
mods merge NOW into ONE player-facing mod, working name `RimMandrake.Biomes`,
packageId `mandrake.rm.biomes`, per-biome toggles in Mod Settings (AlphaBiomes shape).
Item: `infrastructure/state/items/BIOME_MOD_UNIFICATION_1.md`. Spec written 2026-09-27.

## 🔴 EXECUTED — all 3 waves closed 2026-09-28

`BAROQUE_BIOMES_WAVE1_JOIN_1` → `WAVE2_FOLD_1` → `WAVE3_RETARGET_1`, all closed,
FOUNDRY. **All 29 entries (§8's final roster) live inside `mandrake.rm.biomes` on
the owner's live list** — nothing left to fold. Live list 631 → 614 mods (one
ADD in wave 1, 17 packageIds retired in wave 2's single swap). Three clean cold
loads (Bridge token present, zero recovery/abort each time).

This section is the closing record §6's own plan asked for; §1–§8 below are
otherwise the plan AS WRITTEN 2026-09-27 and are left unedited (history, not
current-state prose) except where a stale defName reference was itself wrong
(the `RM_PropaneLake` → `RM_TheChill` rename, corrected separately).

- **Verify (item's own bar), both closed:** def-count match — 1,317 defs across
  the 29 src/ source folders vs 1,283 deployed, gap is exactly the 34 defs in
  TheSump's 9 pre-existing `DEPLOY_HOLD.txt` holds (no art yet), not a compose
  loss. Toggle-gating — `RM_BiomesGate`'s own startup log (`Player.log`) is the
  proof: `roster 29 entries ... 30 BiomeDef(s) mapped` with zero `NOT LOADED`,
  `worldgen gate applied (startup): all biomes on`. Wave 0's own header already
  scoped what a toggle gates *today* (worldgen placement only; the deeper
  per-mechanic gate is `RM_BiomesMod.cs`'s own documented "DEFERRED (spec §5 arm
  2)" — wired biome by biome, not by this item).
- **Fixed on the way, not pre-planned here:** `RUT_StrandedDeformation` defName
  clash between Miasma and the campaign patch layer (owner ruled via question
  card: kept Miasma's version); one dead orphaned def
  (`TerminalBiomes/Defs/ThingSetMakerDefs/RUT_RareGreyCatches.xml`, superseded
  by `RM_GreySeaRareCatch.xml` months ago and never deleted); ~270
  `MayRequire`/`PatchOperationFindMod` references across 168 files that named a
  now-folded packageId or mod display name (§4's own sweep undercounted this at
  design time because it only walked the RM-tier candidate set, not
  `RimUtinni/UtinniPatches`); one C# `ModsConfig.IsActive` guard in
  `RM_TerminalBiomesMod.cs` with the same failure shape, not caught by the XML
  sweep; RustCathedral's `GetSettings<T>()` double-read bug (three calls on one
  `Mod` instance — `Verse.Mod` tracks only one settings type per instance);
  `UtinniPatches/About.xml`'s own `loadAfter` still named 10 now-folded ids
  individually, consolidated to one `mandrake.rm.biomes` entry.
- **Left alone, on purpose:** two pre-existing defName collisions
  (`RUT_LampBlack`, `RUT_RarePropaneCatches`) are deliberately-deferred "Phase
  B" TerminalBiomes/UtinniPatches twins per their own file comments — already
  colliding today independent of this merge, not created or worsened by it.

## 1. Roster — every folder under src/RimMandrake/, IN / OUT / UNSURE

Classified from each About.xml `<name>` + `<description>` (read 2026-09-27, all 63
folders; 59 have an About.xml, 4 are repo tooling with none). Split: 25 IN / 29 OUT
/ 9 UNSURE. "On list" = present in
the newest snapshot, `infrastructure/state/modlists/ModsConfig_BACKUP_before_cryptoforge_retire_20260928T024312Z.xml`
(629 active). The live Windows `ModsConfig.xml` was not re-read for this table; where
on-list status decides a wave, treat the live file as authoritative and the snapshot
as evidence only.

**IN — 25 (23 biome mods + 2 sea-biome kits):**

| Folder | packageId | On list | Why IN |
|---|---|---|---|
| BlueDesert | mandrake.rm.bluedesert | yes (live file, 2026-09-27) | Biome (Phase A row 7) |
| Contagion | mandrake.rm.contagion | no | Biome (row 16) |
| FeverWood | mandrake.rm.feverwood | yes | Biome (row 22) |
| FloodedCanyon | mandrake.rm.floodedcanyon | no | Biome (flood-canyon standalone). NB its DLL compile-references FlowWorks — unified mod gains a HARD dep on `mandrake.rm.flowworks` |
| ForsakenCrags | mandrake.rm.forsakencrags | no | Biome (row 6) |
| GelatinousSlime | mandrake.rm.gelatinousslime | yes | Biome (Q14 donor-free) |
| Greentide | mandrake.rm.greentide | yes | Biome |
| LeaningScrub | mandrake.rm.leaningscrub | no | Biome (row 9) |
| LongShade | mandrake.rm.longshade | yes | Biome (row 2) |
| Miasma | mandrake.rm.miasma | no | Biome (row 19) |
| NightsideIce | mandrake.rm.nightsideice | yes | Biome (row 5) |
| PoisonForest | mandrake.rm.poisonforest | no | Biome (row 10) |
| Pyrelands | mandrake.rm.pyrelands | yes | Biome |
| RustCathedral | mandrake.rm.rustcathedral | no | Biome (row 12); carries 3 DLLs already — precedent for multi-DLL Assemblies |
| Scarlands | mandrake.rm.warscar | no | Biome (Warscar, row 20; folder name ≠ mod name) |
| SeaShores | mandrake.rm.seashores | yes | Sea-biome kit: coast behaviour for modded ocean biomes; consumed by TerminalBiomes XML |
| Stillsand | mandrake.rm.stillsand | yes | Biome (row 1) |
| TerminalBiomes | mandrake.rm.terminalbiomes | yes | Four terminal water biomes (Q1) |
| TheForge | mandrake.rm.theforge | no | Biome (row 21) |
| TheRot | mandrake.rm.therot | yes | Biome |
| TheSump | mandrake.rm.thesump | no | Biome (row 23). Depends on Vanilla Helixien Gas Expanded (Q16) — the unified mod inherits that dependency |
| Wasteland | mandrake.rm.wasteland | yes | Biome (row 4) |
| Webwork | mandrake.rm.webwork | no | Biome (row 17) |
| WeepingStones | mandrake.rm.weepingstones | no | Biome |
| DivingInteraction | mandrake.rm.divinginteraction | yes | Sea-biome kit: the ship-only dive hatch / underwater pocket maps; consumed by TerminalBiomes XML. (Its XML also names LanternDeeps classes — see UNSURE) |

**OUT — 29 folders (25 mods + 4 tooling dirs; frameworks, campaign wiring, non-biome content, dev tooling):**

| Folder | packageId | On list | Why OUT |
|---|---|---|---|
| Aftermath | mandrake.rm.aftermath | yes | Plot-mechanism engine (battle recorder) |
| FlowWorks | mandrake.rm.flowworks | yes | Fluid/canal engine — named OUT by the item; VALIDATED north star |
| Graffiti | mandrake.rm.graffiti | yes | Framework — named OUT by the item; VALIDATED north star |
| SacredGraffiti | mandrake.rm.sacredgraffiti | yes | Content on the Graffiti framework, not a biome |
| GravshipLanding | mandrake.rm.gravshiplanding | yes | Landing-reveal QoL engine |
| Inhabited | mandrake.rm.inhabited | yes | World-persistence engine |
| LoreStages | mandrake.rm.lorestages | yes* | Staged-description engine (*as `mandrake.rm.lorestages` — UNVERIFIED on snapshot, not load-bearing here) |
| MandrakePatches | mandrake.rm.patches | yes | Compatibility patch mod |
| Ninefold | mandrake.rm.ninefold | yes | Divine-satiation engine |
| Oracle | mandrake.rm.oracle | yes | LLM plumbing — named OUT by the item |
| ProximityHatch | mandrake.rm.proximityhatch | yes | Generic egg-hatch engine comp; no biome XML or csproj references it |
| RaidRedesigner | mandrake.rm.raidredesigner | no | Plot-mechanism engine |
| RimProperty | mandrake.rm.property | yes | Ownership fabric engine |
| RustChrome | mandrake.rm.rustchrome | no | UI skin |
| ShipVermin | mandrake.rm.shipvermin | yes | Ship-infesting creatures mod, biome-independent (its DLL references CreatureBehaviors — see §3) |
| StrandedQuest | mandrake.rm.strandedquest | yes | One quest |
| StructureInjections | mandrake.rm.injections | yes | BuildPlan replay engine |
| TheBazaar | mandrake.rm.bazaar | no | Trade overhaul — named OUT by the item |
| TitanicCreatures | mandrake.rm.titaniccreatures | no | Generic large-pawn engine; no biome references it |
| Visibility | mandrake.rm.visibility | yes | Colony-visibility engine |
| WeatherSuite | mandrake.rm.weathersuite | yes | Planet-geometry/terminator-band engine; ZERO biome XML references it (measured) — planet-scale framework, not a biome kit |
| WreckedMachines | mandrake.rm.wreckedmachines | yes | Wreckage content mod (own north star, DRAFT); not a biome |
| LoadTracer | mandrake.rm.loadtracer | yes | Dev diagnostic, not player-facing |
| PlanetPresetPrime | mandrake.rm.planetpresetprime | yes | Dev ergonomics, not player-facing |
| RimDefDump | mandrake.rm.rimdefdump | yes | Dev tooling |
| Utils / bridgetools / mapsynth / rimflow | (no About.xml) | — | Repo tooling, not mods |

**UNSURE — 9 (card agenda §8; WeatherSuite row below is a pointer back to its OUT ruling, not a tenth):**

| Folder | packageId | On list | The question |
|---|---|---|---|
| EnvironmentalHazards | mandrake.rm.environmentalhazards | yes | Kit consumed by 9+ biome mods (XML workers) and 3 biome DLLs at compile time — but also by ShipVermin-adjacent content. Fold IN, or stay a hard-required framework? §3 + card Q3 |
| CreatureBehaviors | mandrake.rm.creaturebehaviors | yes | Same shape: consumed by 10 biome mods' XML + FeverWood/EH DLLs, but ALSO by ShipVermin (OUT) and HostileFlora. Card Q3 |
| LanternDeeps | mandrake.rm.lanterndeeps | yes — `mandrake.rm.lanterndeeps` is active on the live file (2026-09-27); `mandrake.rut.lanterndeeps` is not | An underground biome layer (worldbuilding/biomes/) implemented as dungeon injection, and DivingInteraction's XML names its classes. Biome or dungeon framework? Card Q4 |
| ExplosiveGrowth | mandrake.rm.explosivegrowth | yes | Soaked-plant growth mechanic — generic RM engine used by wet biomes. Kit or framework? Card Q4 |
| HostileFlora | mandrake.rm.hostileflora | no | Mobile hostile plants (XML-only, rides CreatureBehaviors); cast spans biomes. Card Q4 |
| MovingDunes | mandrake.rm.movingdunes | yes | Moving sand — desert-biome kit in spirit, but works on any sandy map. Card Q4 |
| OasisMaker | mandrake.rm.oasismaker | no | Oasis-building machines — desert gameplay content, not a biome def. Card Q4 |
| LuminousPigment | mandrake.rm.luminouspigment | yes | Deepfire pigment economy — content mod with biome-sourced material. Card Q4 |
| Pyrinth | mandrake.rm.pyrinth | no | Absorbed ore/furniture family — content, arguably a biome's kit. Card Q4 |
| WeatherSuite | — | — | (listed OUT above on measured zero references; if the owner wants nightside/dayside weather inside the one mod, say so at the card — otherwise OUT stands) |

Also noted: `mandrake.rm.pits` is still on the active snapshot although the Pits mod
merged into FlowWorks at `cade628c1` and its folder holds no About.xml — a live
precedent for the exact stale-ModsConfig-entry failure §6 guards against. Not this
item's work; flagged for the FlowWorks side.

## 2. Packaging mechanism

Two candidates were compared:

**(a) Physical merge** — move every IN folder's content into one
`src/RimMandrake/Biomes/` mod folder, delete the per-biome folders.

**(b) Compose step** — per-biome dev folders stay exactly where they are in `src/`;
`deploy_custom_mods.py` grows a compose target that BUILDS the shipped
`RimMandrake.Biomes` folder from them at deploy time.

**Recommendation: (b) compose.** The per-biome folder is the unit of everything this
repo already does: per-biome sittings and review sheets, `code_review_status.py`
entries (content-hash per file path — a physical move dirties every file), the
per-csproj `.srchash` guard, modcheck checklist keys (Pyrelands has a DRAFT
checklist keyed to its folder; a physical merge orphans it, compose leaves it
valid), and four concurrent agents editing disjoint biome folders without
colliding. A physical merge converts all of that into one giant shared folder and
one giant review surface for zero player-visible gain. (a) is retained only as the
long-term end-state option if the compose step ever proves brittle.

**Shipped layout the compose step writes** (game Mods folder only — never in src/):

```
RimMandrake.Biomes/
  About/About.xml            ← generated: unified name/packageId, UNION of all IN
                                mods' modDependencies + loadAfter (dedup'd);
                                loadAfter entries pointing at folded-in packageIds dropped
  LoadFolders.xml            ← generated: "/" (root) first, then Biomes/<Name> per biome,
                                in a FIXED, committed order (see Patches note)
  Assemblies/                ← root: ONLY the new RM_BiomesMod settings assembly (§5)
  Biomes/<Name>/             ← verbatim copy of each IN mod minus its About/ folder:
    Defs/  Patches/  Textures/  Sounds/  Languages/  Assemblies/  (whatever it has)
```

Mechanics, per concern:

- **About.xml / loadFolders.** RimWorld treats every `LoadFolders.xml` entry as a
  content root (Defs/, Textures/, Assemblies/, Patches/, Languages/ each scanned
  per root — this is how versioned 1.5/, 1.6/ folders work). So each biome keeps
  its internal layout byte-identical; no file is renamed, no def file merged.
  Proven on wave 0's load (2026-09-27): per-root Assemblies load, including
  RustCathedral's three DLLs and their custom def types. ⚠️ A relative path shipped
  by two roots SHADOWS (decompiled `DirectXmlLoader.XmlAssetsInModFolder`: keyed by
  path relative to its root, `TryAdd`, roots walked in reverse LoadFolders order), so
  every content path must be unique across entries; the compose verb refuses otherwise.
- **Def file layout.** Untouched — collision risk is defName-level, and §4 measured
  it at zero.
- **Textures / texPath.** Textures bind by texPath, and texPaths are a global
  namespace already (all mods share it) — the merge changes nothing. Measured:
  0 duplicate texture relative paths across the 32-folder candidate set (516
  paths), so even a flattened copy would be safe; the per-biome subfolders make it
  moot.
- **Patches ordering.** Pre-merge, cross-mod patch order came from ModsConfig order;
  post-merge it comes from the LoadFolders.xml entry order, then filename. The
  compose step therefore writes loadFolders in a FIXED order committed to the repo
  (alphabetical by biome, kits like SeaShores/DivingInteraction last so they can
  see biome defs), and §4's sweep confirms no biome's Patches target another
  biome's defs (if one does, that pair's relative order becomes load-bearing and
  must be pinned with a comment).
- **Languages.** DefInjected/Keyed merge across load roots natively; DefInjected is
  keyed by defName (unique, measured) and Keyed keys carry per-mod prefixes by our
  convention. Sweep command in §4 anyway.
- **deploy_custom_mods.py changes.** New verb/flag (e.g. `--compose biomes`): reads a
  committed manifest `src/RimMandrake/Biomes.compose.json` (the IN list + loadFolders
  order + generated About fields), builds the unified folder in a temp dir, then
  hands it to the existing compare/copy path so plan-first/--apply, holds and
  shippable-file filtering all keep working. The manifest is the single source of
  truth for the roster; §1's table seeds it. The folded-in mods' individual deploy
  targets are then REMOVED from the tool's discovery (or refused with a pointer),
  so nobody redeploys `Greentide/` standalone by habit.

## 3. Assembly strategy

**Recommendation: keep per-biome DLLs, shipped inside each biome's own
`Biomes/<Name>/Assemblies/`, plus one new root assembly for the settings shell.**
One merged DLL is rejected. Evidence:

- **The `.srchash` guard is per-csproj, not per-mod.** `src/Directory.Build.targets`
  stamps `$(TargetPath).srchash` beside every DLL whose OutputPath lands under a
  folder literally named `Assemblies`, and
  `.claude/hooks/block_dll_source_mismatch.py` recomputes per project on push.
  Per-biome DLLs keep that guard exactly as granular as today with ZERO changes to
  the guard, the targets file, or `dll_source_stamp.py` — the compose step just
  copies each `.srchash` sidecar along with its DLL. A single merged DLL means one
  ~26-way csproj whose Compile list every agent edits concurrently
  (`RM_CreatureBehaviors.csproj` already proves the failure mode: 
  `EnableDefaultCompileItems=false` + a forgotten `<Compile Include>` = code that
  silently doesn't build).
- **Every biome mod measured already builds its own DLL** (25 of 25 IN candidates
  with C#; RustCathedral ships three in one Assemblies/ folder today, so multi-DLL
  per mod is a proven pattern in this repo, and RimWorld loads all
  `Assemblies/*.dll` per load root).
- **Cross-assembly type references.** Compile-time refs measured in csproj files:
  FeverWood → CreatureBehaviors + EnvironmentalHazards; LeaningScrub,
  TerminalBiomes → EnvironmentalHazards; EnvironmentalHazards → CreatureBehaviors;
  FloodedCanyon → FlowWorks; plus XML class refs from ~10 biome mods into CB/EH
  worker/comp classes, and TerminalBiomes XML → DivingInteraction/SeaShores. The
  failure class Q17 exists to kill — `RUT_BurnerAscendant`'s deathAction naming a
  BlueDesert type behind an unguardable `MayRequire` — dies two ways at once:
  (1) everything inside the one mod is always co-present, so intra-mod class refs
  are safe; (2) refs that cross the mod boundary (unified mod → FlowWorks,
  unified mod → CB/EH if they stay OUT, ShipVermin → CB) become **hard
  dependencies declared in the generated About.xml** (`modDependencies` +
  `loadAfter`), which are guardable and loud — the unguardable case was only ever
  the OPTIONAL cross-mod ref. No `MayRequire` on any class-bearing reference
  survives the merge; §4 sweeps for them.
- **Harmony containment.** 12 of the IN candidates instantiate Harmony
  (TerminalBiomes among them). Multiple Harmony instances with distinct IDs inside
  one mod are normal and safe; each biome's patches stay in its own assembly with
  its own ID — nothing consolidates, nothing re-IDs. The only rule the compose adds:
  a biome's Harmony patch must not assume its mod name (`modContentPack.Name`
  becomes "RimMandrake: Biomes" for all of them — §4 sweeps for code reading it).
- **Load order among sibling DLLs** is not relied on: the CLR resolves
  inter-assembly refs at JIT time and all DLLs in one mod are loaded together. The
  compose step ships CB/EH (if ruled IN) at a `Biomes/_Kits/<Name>` load root
  listed FIRST purely so their static constructors run first — cheap insurance,
  not a correctness requirement.

## 4. Collision sweep plan

Ran 2026-09-27 (this spec pass), over the 32-folder candidate set (25 IN + 10 UNSURE,
overlapping) and then over ALL src/RimMandrake mods:

- **Duplicate concrete defNames: 0.** 1,193 defs in the candidate set; widened to all
  60 mods: 1,833 defs, still 0 cross-mod collisions. (Sanity probes found
  `RM_Greatbole`→Greentide, `RM_TheChill`→TerminalBiomes, so the sweep can see.)
- **Duplicate abstract `Name=` bases: 0** (30 abstracts in the candidate set).
  ParentName resolution is global, so this needed checking even with unique defNames.
- **Duplicate texture relative paths: 0** (516 under the candidate set's Textures/).
- **Mod/ModSettings class names: all unique** — every biome has its own
  `RM_<Biome>Mod` + `RM_<Biome>Settings` (a few unprefixed: `SlimeMod`,
  `LanternDeepsMod`, `ExplosiveGrowthMod`, `MovingDunesOptionsMod` — unique anyway).
- **`LIQUID_TERRAIN_AUTHORED_TWICE_1` is NOT a defName collision and unification
  alone does NOT resolve it.** The double-authoring is FlowWorks
  (`RM_WaterBoiling*`, `RM_WaterBrine*`, `RM_Propane{Deep,Shallow}`) vs
  TerminalBiomes (`RM_Brine*`, `RM_TheChillDeep`, `RM_SolidPropane`) — same
  substances, DIFFERENT defNames, and FlowWorks is OUT of the merge. Resolving it
  is a cross-mod ownership ruling (card Q7), executed as: pick the surviving
  family per substance, retarget references, and delete the loser only when
  proven unreferenced by the shipped savegame (terrain grids store shortHashes —
  `rimworld-savegame` skill) — realistically at the world-remake window.

Commands the FOUNDRY wave re-runs before every load-prove (each is a short python
sweep, written as python because zsh loops don't word-split — do not shell-loop):

1. **defName + abstract Name sweep** — the script pattern above: walk
   `src/RimMandrake/<IN>/**/*.xml` under `/Defs/`, `ET.parse`, collect
   `(tag, defName)` and `Name=` attrs, print any key with >1 mod. MUST include a
   sanity probe (a def known to exist) so an empty result proves the sweep can see.
2. **texPath field sweep** — same walk, collect every `<texPath>`/`<texture>` text
   value across the IN set, report duplicates (file-path sweep already clean, but
   texPath is the binding key: `texture-binds-by-texpath-not-defname`).
3. **PatchOperationFindMod / mod-name sweep** — `grep -rn "PatchOperationFindMod" 
   src/RimMandrake UtinniPatches` then read each `<mods><li>` value: any patch
   (ours or the Utinni layer's) matching a folded-in mod's NAME ("RimMandrake:
   Greentide" etc.) goes dark after the merge, silently (FindMod returns true on
   no match, logs nothing). Every such entry must be retargeted to the unified
   mod's final name — this is the single most silent post-merge failure available.
4. **MayRequire-on-folded-ids sweep** — grep all XML for
   `MayRequire="mandrake.rm.<folded id>"`: each hit either becomes unconditional
   (now intra-mod) or is a latent inert guard (`PATCH_MAYREQUIRE_GUARD_INERT_1`
   family). None may survive naming a retired packageId.
5. **`modContentPack` self-name sweep** — grep IN mods' `Source/` for
   `.Name`, `PackageId`, `packageIdPlayerFacing` reads on their own ModContentPack;
   any code branching on its own mod identity breaks when identity becomes
   "RimMandrake: Biomes".
6. **Keyed-language sweep** — collect `Languages/**/Keyed/*.xml` key names across
   the IN set, report duplicates (DefInjected is defName-keyed and already proven
   unique).
7. **Settings-class collision re-check** (command as run above) after any UNSURE row
   is ruled IN.

## 5. Settings screen design

One new small assembly at the mod root: `RM_BiomesMod : Mod` +
`RM_BiomesSettings : ModSettings`. It owns the single settings category
("RimMandrake: Biomes") — the AlphaBiomes shape the owner named.

- **The master screen** is a scrollable list, one row per biome: checkbox toggle +
  biome name + one-line blurb + a `[settings…]` button where that biome has its own
  tunables. Defaults ALL ON (Mod Settings law: defaults = shipped behaviour).
- **Per-biome sub-screens reuse the existing classes.** Every biome already ships
  `RM_<Biome>Mod`/`RM_<Biome>Settings` (measured, §4). Each biome's `Mod` subclass
  is changed to return `""` from `SettingsCategory()` (hides its own entry in the
  mod-settings list) and the master's `[settings…]` button opens a dialog that
  delegates to that biome's existing `DoSettingsWindowContents`. Settings data,
  scribing and defaults stay in the per-biome classes — near-zero churn, and each
  biome's screen remains reviewable at its own sitting.
  ⚠️ Vanilla stores ModSettings in a config file named from the owning mod's
  identity + settings class; the re-homing changes that filename, so any settings
  saved against the standalone mods reset to defaults. Acceptable: defaults are
  all-on and nothing has shipped.
- **What a biome's toggle gates, exactly two things:**
  1. **Worldgen spawning** — the biome's `BiomeDef.Worker`/score returns
     never-place when toggled off, so NEW worlds a free player generates don't get
     it. Label on the row, verbatim per the Mod Settings law: *"affects world
     generation — takes effect on the next new world"*. On Ash'karr this arm is
     inert by construction (frozen world, workers never run) — which is correct,
     not a defect.
  2. **Mechanics** — each biome's MapComponents/GameComponents/comps early-out when
     the toggle is off (one static `RM_BiomesSettings.Enabled(biomeKey)` check at
     their entry points). This is the arm that does anything on an existing map,
     and it's what lets a biome-kit mechanic run in OTHER biomes when the biome
     itself is off (the CLAUDE.md biome-kit feature-gating law).
- **A toggle NEVER unloads defs.** Off = don't spawn, don't tick — the defs stay
  loaded so savegames referencing them (including the shipped campaign save) keep
  resolving. Say this in the setting's tooltip ("existing maps keep their terrain
  and creatures; this stops new placement and behaviour").
- **Kit toggles** (SeaShores, DivingInteraction, and any UNSURE row ruled IN) get
  their own rows in a "Mechanics" group under the biome rows, same two-arm gating.
- The per-biome fine tunables (numbers-as-experience) stay per-biome per the
  Mod Settings law; the master screen adds only the toggles and navigation.

## 6. Migration order

Waves, each independently load-provable, ordered so the owner's live list is touched
exactly once and last:

- **Wave 0 — compose + shell, off the live list.** Build the compose target, the
  generated About/LoadFolders, and the `RM_BiomesMod` settings shell. Compose ONLY
  the 12 off-list biomes (Contagion, FloodedCanyon, ForsakenCrags, LeaningScrub,
  Miasma, PoisonForest, RustCathedral, Warscar, TheForge, TheSump, Webwork,
  WeepingStones). BlueDesert is ON the live list and waits for wave 2, as do the
  four Q3/Q4 folds (CreatureBehaviors, EnvironmentalHazards, LanternDeeps,
  MovingDunes) — all four are active on the live file, so folding any of them
  earlier would load its defs and types twice. Load-prove on a minimal tier (`modset_builder.py`, all
  five DLC per the test-list law) — proves loadFolders content roots, per-root
  Assemblies loading, def counts per biome (`measure`, never grep), toggles gating.
  Zero risk: nothing here is on the live list.
- **Wave 1 — unified mod joins the full list.** One ADD, no removals (wave 0's
  content is all new to the list). Cold-load prove; first exception in Player.log,
  not the loudest.
- **Wave 2 — the on-list 12 fold in, ONE swap.** Add the on-list biome mods
  (FeverWood, GelatinousSlime, Greentide, LongShade, NightsideIce, Pyrelands,
  Stillsand, TerminalBiomes, TheRot, Wasteland) + SeaShores + DivingInteraction to
  the compose manifest; then a SINGLE ModsConfig swap that removes those 12
  packageIds in the same write in which the (already-present) unified mod's new
  compose is deployed. The item's warning is binding: entries removed in the SAME
  swap, or the game logs missing-mod noise — and `mandrake.rm.pits` on today's
  snapshot shows what a half-done retirement looks like. Sequence per
  `modset_builder.py`'s guard: kill the game FIRST, then swap (it refuses while
  Player.log is <3 min old). Cold-load prove + spot-check per-biome def counts
  against pre-merge counts (equal, measured).
- **Wave 3 — dependents and layers.** Re-run §4 sweeps 3–4; retarget UtinniPatches
  `PatchOperationFindMod` names and any `MayRequire` naming folded ids; confirm the
  RimUtinni layer's loadAfter now names `mandrake.rm.biomes`. Rule card Q3/Q4
  outcomes (kits) as their own mini-wave repeating this pattern.

**modcheck north stars.** FlowWorks, Graffiti and Pits — the VALIDATED checklists —
are NOT biome mods (FlowWorks/Graffiti OUT; Pits already merged into FlowWorks) and
are untouched. The only IN-set checklist is **Pyrelands (DRAFT, 10 lines)**. Under
compose (§2) the dev folder survives, so its key stays valid and nothing needs
`rename-key`; the checklist's must-shows are eventually re-pointed at the unified
mod's deployment when Pyrelands validates. If the owner instead rules physical
merge, `modcheck rename-key` (the `b110a7a2d` verbs) must run for Pyrelands in the
same sitting or it strands ORPHANED like Pits did. No re-validation is owed either
way — nothing VALIDATED is being folded.

**ModsConfig bookkeeping.** Snapshot each pre-swap list into
`infrastructure/state/modlists/` (existing convention). After wave 2, a sweep
confirms no doc/tooling still names the retired packageIds
(`grep -rl "mandrake.rm.greentide" infrastructure/ skills/ design/` etc. — stale
gates outlive their items; delete citations on sight).

## 7. Constraints that bind this merge

Verified against their sources, not re-derived:

1. **defNames do not change.** The shipped savegame references BiomeDefs (and
   terrain, things) by shortHash; a renamed def orphans frozen-world tiles
   (`biome-defname-deletion-must-check-live-tiles`). The compose mechanism (§2)
   renames NO def and NO file, so this holds by construction — any dedup that
   deletes a def (§4 liquid terrain) is separate, gated work.
2. **The RimUtinni patch layer stays separate and patches the ONE mod** (Q15's
   layering survives Q17 verbatim: "the ONE mod is the top level it patches").
   Its loadAfter/FindMod targets are retargeted in wave 3, nothing else moves.
3. **Q13 duplicate-then-diverge stays.** Content shared between two biomes remains
   two defs — now same-mod, still separate defs, still diverging. The merge is NOT
   a licence to dedupe them into a commons.
4. **Non-biome mods stay independent** (item, verbatim list: FlowWorks, Graffiti,
   Oracle, TheBazaar, …). §1's OUT column executes this.
5. **There is no worldgen feature, ever.** The per-biome worldgen toggle governs a
   FREE player's ordinary new-world generation; it builds nothing that produces
   alternative Ash'karrs and ships no worldgen capability for the campaign, whose
   players receive the frozen savegame.
6. **Every mod ships superb Mod Settings** (owner, 2026-09-12) — §5 is that law
   applied; biome-kit mechanics stay enableable without their biome.
7. **All test lists carry all five DLC** (owner, 2026-09-19); design assumes every
   DLC present (2026-09-25/26). No DLC-less proving round exists for any wave.
8. **A correction to the item:** `BIOME_MOD_UNIFICATION_1` says the double-authored
   liquid terrain "resolves by unification, one def survives." Measured (§4): the
   two authors are FlowWorks and TerminalBiomes, and FlowWorks is OUT — the merge
   does not co-house them, so resolution is the explicit ownership ruling in card
   Q7, not a free side effect.

## 8. Card agenda — the owner's sub-decisions

Decisions the evidence settles are stated above as spec and are NOT re-asked here
(zero-collision findings, toggle semantics, wave mechanics, modcheck handling).

🔴 **ALL EIGHT RULED 2026-09-27** (decisions taken by question card; Q1's name is the
owner's own typed coinage): **Q1** the mod is **"RimMandrake: Baroque Biomes"**
(packageId `mandrake.rm.biomes`) · **Q2** two Workshop pages in principle (biomes vs
campaign; nothing executes until a release is real) · **Q3** CreatureBehaviors AND
EnvironmentalHazards fold **IN** (overrides the recommendation — ShipVermin and
HostileFlora become hard-dependents of Baroque Biomes) · **Q4** LanternDeeps IN,
MovingDunes IN; ExplosiveGrowth, HostileFlora, OasisMaker, LuminousPigment, Pyrinth
OUT · **Q5** per-biome DLLs · **Q6** compose at deploy time from per-biome dev
folders · **Q7** FlowWorks owns generic liquid terrain — TerminalBiomes retargets
now, nothing deleted until the world-remake window · **Q8** waves, the live list
written once at wave 2. **Final IN roster: 29 mods** (the §1 25 + CB + EH +
LanternDeeps + MovingDunes). Execution: `BAROQUE_BIOMES_COMPOSE_1` (wave 1 tooling),
`TERMINALBIOMES_LIQUID_RETARGET_1` (Q7). The eight cards as asked, for the record:

**Q1 — Final mod name (and packageId stays `mandrake.rm.biomes`).**
 a) "RimMandrake: Biomes" — plain, matches every sibling mod's naming.
 b) A flavour name (e.g. "RimMandrake: Strange Lands") — reads better on a Workshop
    page, but breaks the tier-grammar pattern players will see across our mods.
 c) You write one in.
 *Recommend (a): the RimMandrake prefix is the brand; the biome names themselves
 carry the flavour.*

**Q2 — Workshop packaging: one page or two?**
 a) One Workshop item: RimMandrake.Biomes.
 b) Two items: the biomes mod + a separate campaign/scenario mod page later.
 *Recommend (b) in principle — the campaign ships a savegame and its own layers, a
 different audience — but nothing needs deciding until a Workshop release is real;
 choosing (b) now costs nothing.*

**Q3 — The two shared engines: CreatureBehaviors and EnvironmentalHazards, in or
out?** They are consumed by ~10 biome mods each (XML classes + three compile-time
DLL refs), but also by non-biome mods (ShipVermin; HostileFlora).
 a) OUT, as hard-required framework mods the one mod declares in About.xml — keeps
    ShipVermin and future non-biome consumers lean; two more entries on a player's
    mod list.
 b) IN, folded — one download, but every non-biome consumer (ShipVermin today)
    then hard-depends on the whole Biomes mod.
 *Recommend (a): a HARD dependency is guardable and loud — the failure class Q17
 kills was optional cross-mod refs, and none of these is optional.*

**Q4 — the UNSURE content rows (one card, checkboxes): LanternDeeps, ExplosiveGrowth,
HostileFlora, MovingDunes, OasisMaker, LuminousPigment, Pyrinth** — each either
joins the Biomes mod (a row + toggle on the settings screen) or stays its own mod.
 *Recommend IN: LanternDeeps (it is one of the planet's biomes in the design
 docs, just underground) and MovingDunes (desert-biome texture of the world).
 Recommend OUT: ExplosiveGrowth, HostileFlora, OasisMaker, LuminousPigment,
 Pyrinth — content/mechanic mods that happen to be used BY biomes; hard deps
 cover them.*

**Q5 — Assembly strategy.** (Item sub-decision 4; §3 argues it.)
 a) Per-biome DLLs inside the one mod — srchash guard unchanged, concurrent builds
    keep working, ~26 small DLLs.
 b) One merged DLL — one file, but one giant csproj every agent edits and one
    srchash covering everything (any biome's edit dirties the whole mod's stamp).
 *Recommend (a), strongly.*

**Q6 — Source strategy.** (Item sub-decision 3; §2 argues it.)
 a) Keep per-biome dev folders in src/, compose the shipped mod at deploy time —
    review, sittings, srchash, modcheck all keep their unit; one new deploy verb.
 b) Physically merge the folders now — simpler mental model, but every review
    artifact keyed by path dirties, and concurrent agents share one folder.
 *Recommend (a) — BENCH's stated lean at the ruling card, and every measured
 instrument (code_review_status, srchash, modcheck keys) points the same way.*

**Q7 — Liquid terrain ownership (LIQUID_TERRAIN_AUTHORED_TWICE_1).** Boiling
water/brine/propane terrain exists in FlowWorks AND TerminalBiomes under different
defNames; FlowWorks stays a separate mod, so the merge does not settle it.
 a) FlowWorks owns generic liquid terrain (it is the fluid engine and LiquidDef
    registry home); TerminalBiomes keeps only its biome-specific formations
    (SolidPropane, BrineChannel…) and retargets the rest.
 b) TerminalBiomes owns everything its seas use; FlowWorks keeps its family for
    canal output only. Two families persist, documented as deliberate.
 c) Defer the whole question to the world-remake window (nothing deletes until
    then anyway, since placed terrain pins shortHashes in the save).
 *Recommend (a), executed at the world-remake window — i.e. rule (a) now, delete
 nothing yet.*

**Q8 — Migration timing.** (Only because it touches the live list.)
 a) Waves per §6 — the live list is written once, in wave 2.
 b) Everything in one sitting/swap — fewer cold loads total, but the first live
    load carries 25 mods' worth of novelty at once.
 *Recommend (a).*
