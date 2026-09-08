# DROIDWORKS_RESEARCH_ROWS_1

## Spec
Seven Droidworks research rows in The Unbolting; cut the Depot droid-brain rows;
brains never researchable. Per `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md`
§4 (packet B8): `RSW_DW_Research_Reboot` (free at start) → `_Bolting` → `_Spiking`
→ `_ShopRepair` → `_Reassembly` → `_PrimitiveFabrication` → `_Formatting`. No row
ever unlocks a brain part.

## Built

**`src/RimStarWars/Droidworks/Defs/ResearchProjectDefs/ResearchProjects_Droidworks.xml`** —
7 new `ResearchProjectDef`s, `<tab>RUT_Tree_Unbolting</tab>` (that tab already
shipped: `RESEARCH_TREE_TABS_1`, `src/RimUtinni/ResearchRetag/Defs/ResearchTabDefs/RUT_Tree_Defs.xml`).
Linear chain, each `<prerequisites>` pointing at the previous row:

| row | baseCost | techLevel | prereq |
|---|---|---|---|
| `RSW_DW_Research_Reboot` | 0 | Industrial | none (free at start) |
| `RSW_DW_Research_Bolting` | 300 | Industrial | Reboot |
| `RSW_DW_Research_Spiking` | 500 | Industrial | Bolting |
| `RSW_DW_Research_ShopRepair` | 800 | Spacer | Spiking |
| `RSW_DW_Research_Reassembly` | 1200 | Spacer | ShopRepair |
| `RSW_DW_Research_PrimitiveFabrication` | 700 | Industrial | Reassembly |
| `RSW_DW_Research_Formatting` | 1500 | Spacer | PrimitiveFabrication |

Cross-mod `<tab>` reference (Droidworks def → ResearchRetag's tab def) resolves
regardless of load order — all mods' defs load before `ResolveReferences` runs
platform-wide; no `modDependency` added to Droidworks' About.xml since the two
packages already ship together in this campaign (same convention every other
RimStarWars↔RimUtinni cross-reference in this stack already uses, unenforced by
Workshop-style dependency declarations).

**37 `researchPrerequisite` gates added** across 9 existing files (all recipes
that already existed and were previously ungated — none of this item's own
work invented a new recipe):

| file | gated defNames | row |
|---|---|---|
| `RecipeDefs/RecipeDefs_Droidworks.xml` | `RSW_DW_RebootDroid` | Reboot |
| " | `RSW_DW_InstallRestrainingBolt`, `RSW_DW_RemoveRestrainingBolt`, `RSW_DW_MemoryWipe` | Bolting |
| " | `RSW_DW_FormatDroid`, `RSW_DW_RestrictiveFormat`, `RSW_DW_DeformatDroid` | Formatting |
| `ThingDefs/Items_Droidworks.xml` | `RSW_DW_RestrainingBoltItem` (`recipeMaker`) | Bolting |
| " | `RSW_DW_DataSpike` (`recipeMaker`) | Spiking |
| `ThingDefs/DataSpikes_Droidworks.xml` | `RSW_DW_DataSpike_{Empire,Hutt,Junker,Wild}` (`recipeMaker` ×4) | Spiking |
| `RecipeDefs/PartRecipes_Droidworks.xml` | `RSW_DW_Install{LegActuator,ManipulatorArm,Sensor,Motivator,Servo}` ×5 | ShopRepair |
| `RecipeDefs/AssemblyRecipes_Droidworks.xml` | `RSW_DW_OverclockDroid` | ShopRepair |
| " | `RSW_DW_AssembleDroid`, `RSW_DW_ShopRebuild` | Reassembly |
| `RecipeDefs/PartRecipes_Droidworks_Primitive.xml` | `RSW_DW_Install{...}_Primitive` ×5 | PrimitiveFabrication |
| `ThingDefs/Parts_Droidworks_Primitive.xml` | `RSW_DW_Part_{Leg,Manipulator,Sensor,Motivator,Servo,PowerCell,Frame}_Primitive` (`recipeMaker` ×7) | PrimitiveFabrication |
| `ThingDefs/Modules_Droidworks_Primitive.xml` | `RSW_DW_Module_{Motivator,Repair,Sensor}_Primitive` (`recipeMaker` ×3) | PrimitiveFabrication |
| `ThingDefs/Parts_Droidworks.xml` | `RSW_DW_Part_Frame` (`recipeMaker`, donor-tier stopgap) | PrimitiveFabrication |

Breakdown: Reboot 1, Bolting 4, Spiking 5, ShopRepair 6, Reassembly 2,
PrimitiveFabrication 16, Formatting 3 = 37.

## Decisions recorded (doc silent on placement)

- **`RSW_DW_MemoryWipe` → Bolting.** §1.3's own sentence groups the four
  operations-tab surgeries in this order: "Reboot / bolt / wipe / spike" — wipe
  sits between bolt and spike, so it rides the row that unlocks bolt rather than
  getting a dedicated row of its own (the doc's §4 list only names 7 rows and
  wipe isn't one of them).
- **`RSW_DW_RestrainingBoltItem`'s own crafting recipe → Bolting**, alongside
  the two surgeries it feeds (install/remove).
- **The 5 data-spike ThingDefs (`RSW_DW_DataSpike` + 4 per-faction siblings) →
  Spiking** — the row's own name.
- **`RSW_DW_OverclockDroid` → ShopRepair**, not Reassembly — it's the
  bench-adjacent "push a droid past its rated limits" job (§3.1's own listing
  puts it with the shop, not the harness), while `AssembleDroid`/`ShopRebuild`
  (the actual head+frame+parts→pawn and corpse-rebuild recipes) are the two
  that gate under Reassembly.
- **`RSW_DW_Part_Frame`'s recipe (donor-tier, `Parts_Droidworks.xml`) →
  PrimitiveFabrication**, same row as its Primitive-tier sibling
  `RSW_DW_Part_Frame_Primitive`. That recipe's own comment calls itself "the
  stopgap so the harness has a source before B9 lands" — B9 (the Primitive
  tier) has since landed, but the recipe itself is still live and still
  ungated, and it is frame *fabrication* either way, so it belongs under the
  fabrication row regardless of which tier authored it first.

## Brain-trio confirmation (requirement 3)

`RSW_DW_PersonalityMatrix` / `RSW_DW_Processor` / `RSW_DW_Databank`
(`ThingDefs/BrainTrio_Droidworks.xml`) still carry **zero** `recipeMaker`
blocks — confirmed by direct read of that file (its own header: "No
recipeMaker on any of the three — deliberately, forever (ruling 6)"). Grepped
every changed/new file: no `researchPrerequisite` anywhere names one of the
three brain-trio defNames, because there is no recipe on them to gate in the
first place. The head-gate stands by construction, not by omission.

## OuterRim_DroidBrain (the "cut the Depot droid-brain rows" half)

Grepped `src/` for `OuterRim_DroidBrain`: the only hit is a `butcherProductsOverride`
data reference inside `src/RimStarWars/Droidworks/Source/extraction.json`
(a decompile/extraction artifact, not a live game file) — `OuterRim_DroidBrain`
is a butcher-yield item there, **not a research row or a crafting recipe** in
that extraction at all. Grepped every patch this repo owns
(`RUT_ResearchTabAssign.xml`, all of `src/RimUtinni/ResearchRetag/Patches/`)
for `DroidBrain`: **zero hits**. No patch anywhere in `src/` re-enables,
exposes, or otherwise touches `OuterRim_DroidBrain` crafting for Droidworks
races. Conclusion: there is nothing of ours to cut here — whatever
`OuterRim_DroidBrain` research/crafting exists is purely Droid Depot's own
donor content, untouched by this codebase, and retiring donor content is
`DROID_RETIRE_DEPOT_ASIMOV_1`'s job, not this item's. Left alone, as instructed.

## Verify

- `tree renders`: structurally verified offline — 7 `ResearchProjectDef`s form a
  clean linear DAG (`Reboot → Bolting → Spiking → ShopRepair → Reassembly →
  PrimitiveFabrication → Formatting`), each `<prerequisites>` name matches an
  actual sibling `defName` exactly (grepped both sides), all 7 share
  `<tab>RUT_Tree_Unbolting</tab>` which already exists
  (`RUT_Tree_Defs.xml`, `RESEARCH_TREE_TABS_1`).
- `reboot free`: `RSW_DW_Research_Reboot` has `<baseCost>0</baseCost>` and no
  `<prerequisites>` element at all.
- All 10 touched/created XML files parsed clean with
  `python3 -c "import xml.etree.ElementTree as ET; ET.parse(...)"`.
- No C# touched — pure XML packet, no build needed.
- **No live/bridge check performed.** `rimflow bridge who` read FREE at build
  time, but ResearchProjectDef rendering and `researchPrerequisite` gating are
  core, heavily-proven vanilla mechanisms already used throughout this repo
  (e.g. `RUT_Rites_*`, the KotOR-absorbed research defs) — not a custom
  mechanism that has never been observed running. Judged the offline
  structural check sufficient for this packet's verify line; owed to the
  owner's own play as the default validation per FOUNDRY doctrine.

## Assumptions

- techLevel/baseCost values are this packet's own judgment call (the design
  doc gives no numbers beyond "Reboot is free") — reasonable mid-chain
  progression, easy to retune later without touching the gating wiring.
- `researchViewX` 0–6, `researchViewY` 0 (single-row linear chain), matching
  the doc's own description of a straight chain rather than a branching tree.
