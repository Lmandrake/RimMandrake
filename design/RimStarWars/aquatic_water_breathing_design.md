# Water-breathing for the aquatic xenotypes — design brief

_`AQUATIC_WATER_BREATHING_GENE_1`. RSW tier. Status: DESIGN — FOUNDRY builds from
this; two cards await the owner (§6). Nothing built. Engine facts below were MEASURED
through RimSage on 2026-09-18 against the 1.6 source (Core + Royalty + Ideology +
Biotech + Anomaly + Odyssey); "our own" facts by reading the repo._

## 1. What the engine does with a pawn in water today

**There is no drowning in RimWorld 1.6.** `drown` appears in the decompiled source
only as flavour text (beggar quest lines, a Labyrinth rule pack). Nothing in any DLC
damages, suffocates or downs a pawn for standing in water.

What water actually does, per `Core/TerrainDefs/Terrain_Water.xml` and the pathing code:

| terrain | passability | what happens to a humanlike |
|---|---|---|
| `WaterDeep`, `WaterOceanDeep` | **Impassable** (pathCost 300) | cannot enter at all. `forcePassableByFlyingPawns` opens it only for races with `def.flying`. Impassability is decided in `PathGridJob.CellIsPassable` from `pathGridDirect` BEFORE any per-pawn water cost is consulted, so **no gene or race field can open deep water** — that would need a new pathing context. |
| chest-deep, shallow, marsh | Walkable | movement `pathCost` 42 / 30; pathfinder adds `extraNonDraftedPerceivedPathCost` 180 (drafted 18) so pawns route around it; `traversedThought SoakingWet` (a memory, mood −) on wading. |

Two vanilla hooks already exist for "this pawn is at home in water", and both are
what this design keys on:

- **`GeneDef.waterCellCost` (int?)** — Biotech. `Pawn.WaterCellCost` takes the
  lowest value across active genes, else `RaceProperties.waterCellCost`.
  `PathFinderCostTuning.For(pawn)` copies it into `costWater`; `PathGridJob.CostForCell`
  then uses it INSTEAD of the terrain's pathCost and **skips the perceived cost** for
  water cells, and `Pawn_PathFollower` uses it as the actual move cost
  (`GetPawnCellBaseCostOverride`). Vanilla's `WebbedPhalanges` sets it to 1; Odyssey's
  otters, seals, walruses etc. set the race field. Effect: water is free ground for
  planning and movement. Humanlikes get no swimming sprite from it
  (`Pawn.DrawNonHumanlikeSwimmingGraphic` returns false for `Humanlike`) — no art owed.
- **`ThoughtDef.nullifyingGenes`** — `ThoughtUtility.ThoughtNullified` checks it for
  memories and situational thoughts alike. `SoakingWet` currently has none.

Odyssey's `GoSwimming` joy job (`SwimPathFinder`) walks *Standable* water cells only,
i.e. shallow water, and never deep — it is a mood activity, not a submersion model.

**Gene immunity does NOT block a hediff being added.** `GeneDef.makeImmuneTo` is read
by `ImmunityHandler.AnyGeneMakesFullyImmuneTo`, which is consulted only by
`DiseaseContractChanceFactor`, `GetImmunity` and the lung-rot comp. A direct
`HealthUtility.AdjustSeverity(...)` — which is how our pit adds drowning — ignores it.
So the immunity must be honoured by the caller (§3).

## 2. The only drowning that exists is ours

Repo-wide, exactly one mechanism drowns anyone: **FlowWorks' pit**.

- `RM_PitDrowning` (HediffDef, `src/RimMandrake/FlowWorks/Defs/Pits/HediffDefs/Pit_Hediffs.xml`):
  lethalSeverity 1.0, stages "treading water" → "exhausted" (consciousness −0.3). It is
  an exhaustion clock, not a breath clock.
- `CompPitFitting.OnStruggleInterval` (`.../Source/Pits/Fitting/CompPitFitting.cs`)
  adds `drowningSeverityPerInterval` (0.15) unless **`CanSwim(p)`** — which today is
  true for non-humanlike races with `swimmingGraphicData` on the life stage, or a body
  def whose name contains "aquatic" (matches nothing real). **No humanlike can ever pass
  it.** A Mon Calamari in a flooded pit drowns exactly like a Jawa.
- `PIT_SUPERDEEP_COLLAPSE_1` (owner ruling 2026-09-17) retires the `Water` fitting and
  moves the drowning trigger to "fill > 0 on a superdeep cell", explicitly keeping
  `RM_PitDrowning` and `CanSwim` ("REHOUSE", "do not re-break CanSwim"). That rework is
  filed, not built. This design adds one clause to `CanSwim` wherever it ends up living.

`DivingInteraction` (Scald dive jobs) is a timed wait on tagged terrain with no breath
model; `FloodedCanyon` floods terrain and touches no pawn. Neither needs a hook.

## 3. Mechanism: one plain GeneDef, honoured by FlowWorks

**Shape: a Gene.** Not a hediff, not C# of its own.

- It is how every other non-cosmetic species trait in this project is expressed
  (`RSW_Jawa_Skittish`, `RSW_Jawa_MiningDisabled`, `RSW_AbilityGene_JumpLegs`, 157 genes
  in `SW_Genes.xml`), it is per-pawn so it reaches enemy Deepwater pawns as well as
  colonists, it appears in the xenotype/gene UI with its own "Immune to: drowning" line
  (vanilla renders `makeImmuneTo` there), and it is inheritable and biostat-costed like
  the rest of the xenotype economy. A hediff would have to be applied by a generator
  hook, would show in the health tab as a condition, and would not travel with the
  germline.
- Every field it uses is vanilla XML. **Zero new C# for the gene itself.** The single
  code change is one added condition in FlowWorks' `CanSwim`.

### The gene

`RSW_WaterBreathing` — label "water-breathing", `displayCategory` the existing
`RSW_SWparts_Category`, in `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/` (a new file,
`RSW_Aquatic.xml`, with the project's standard WHY header). Fields:

| field | value | why |
|---|---|---|
| `waterCellCost` | `1` | swims: water is free ground for planning and movement (subsumes `WebbedPhalanges`; `Pawn_GeneTracker` takes the minimum, so both together is harmless) |
| `makeImmuneTo` | `<li MayRequire="mandrake.rm.flowworks">RM_PitDrowning</li>` | the immunity declaration FlowWorks reads (below); `MayRequire` so the gene loads with FlowWorks absent |
| `biostatCpx` / `biostatMet` | 1 / −2 | ability with no drawback; between `DarkVision` (−1) and `FireResistant` (−2), and it carries WebbedPhalanges' −1 inside it. FOUNDRY may retune; not an owner call |
| `symbolPack` | gill / deep / tide prefixes | name flavour, same as vanilla genes |
| `customEffectDescriptions` | "Never drowns. Moves through water as easily as land. Does not mind being soaked." | the tooltip line, since the effects are spread across three mechanisms |

Plus one `PatchOperationAdd` on `ThoughtDef[defName="SoakingWet"]/nullifyingGenes`
adding `RSW_WaterBreathing`, in the same mod. An aquatic species does not mind being
wet.

Why StarWarsRaces and not FlowWorks or a new RM-tier mod: StarWarsRaces already depends
on Biotech and ships the xenotypes that use it; FlowWorks does not depend on Biotech; and
a micro-mod for one def is gold plating. The gene is meaningful without FlowWorks
(movement + mood), and FlowWorks is meaningful without the gene, so neither depends on
the other — the `MayRequire` and the immunity-based lookup below are what keep it so. If
an RM-tier xenotype ever needs it, moving it is a rename, which the naming rulings treat
as owed work, not a gate.

### The FlowWorks side

`CompPitFitting.CanSwim(p)` gains, ahead of the existing checks:

> return true if `p.health?.immunity?.AnyGeneMakesFullyImmuneTo(RMPits_HediffDefOf.RM_PitDrowning)` is true.

That is a **vanilla public API**, references no StarWarsRaces def, and lets any future
gene or mod opt in by declaring immunity to `RM_PitDrowning` — no string matching, no
dependency. Do not key it on `WaterCellCost.HasValue`: that is the *swim* signal, and a
`WebbedPhalanges` baseliner still exhausts treading water in a pit; only a
water-breather does not. If `PIT_SUPERDEEP_COLLAPSE_1` has already rehoused `CanSwim`
when this is built, the clause goes wherever it landed; if not, it goes in today's
`CompPitFitting` and the pit rework carries it (add a line to that item's REHOUSE row
so it is not dropped).

Per `MOD_OPTIONS_RETROFIT_1`, FlowWorks' settings screen gets one toggle, "water-breathers
never drown in pits" (default on); the gene itself has no setting — a gene is a fact
about a pawn, not a feature.

### Wiring

Add `<li>RSW_WaterBreathing</li>` to the four xenotypes in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`. That file is
emitted by `gen_races_mod.py`, whose "shipped metadata wins" rule (MEASURED, FOUNDRY
note 2026-09-18 on `XENOTYPE_NONCOSMETIC_FIXES_1`) makes the emitted XML the fix path, as
with the description and nameMaker fixes at `24c71156` / `5d5a1657`. Nautolan already
has `DarkVision`; nothing conflicts.

Not touched, deliberately: the species' cosmetic genes (owner's cosmetic gate, ruling
2026-09-15), and Nautolan's inverted temperature genes (noted in
`XENOTYPE_CANON_CORRECTION_1`, a separate data fix).

## 4. What it grants — and what it does not

Grants, all of it in play today:

1. **Never drowns** in a FlowWorks pit (the only drowning that exists).
2. **Moves through water as if it were ground** — wading is no longer avoided or slowed.
   Tactically real on Ash'karr's canals and the three seas' shallows.
3. **No "soaking wet" mood hit** from wading or rain.

Does not grant, and cannot without engineering this brief does not recommend:

- **Crossing deep water.** Impassable is decided before any per-pawn cost (§1). Opening
  it would mean a per-pawn pathing context (a `PathingContext` beyond Normal /
  FenceBlocked), region rebuilds, reachability, and AI that knows some pawns can go where
  others cannot. Real engine work with a wide blast radius; card 2.
- **Combat, speed on land, or anything else.** Purely the water triad above.

## 5. The species

The four the item names, re-derived from `XENOTYPE_CANON_CORRECTION_1` pattern 4 and its
ruling table (2026-09-15), all confirmed present in `RimMandrakeXenotypes.xml` with no
water gene of any kind:

| xenotype defName | label | canon library says |
|---|---|---|
| `RSW_RimMandrakeMonCalamari` | Mon Calamari | "humanoid, aquatic species", class amphibious humanoid |
| `RSW_RimMandrakeNautolan` | Nautolan | "amphibious, capable of breathing both air and water" |
| `RSW_RimMandrakeGungan` | gungan | "amphibious with hardy lungs and long breath-hold" — a **breath-holder**, not a water-breather |
| `RSW_RimMandrakeSelkath` | Selkath | "aquatic species", habitat aquatic |

**One shared gene.** Nothing in the four's canon differs in a way the mechanism can
express; per-species variants would be four copies of one def. The Gungan question is
a roster question (card 1), not a variant question.

## 6. Cards for the owner

Two things are genuinely his. Everything else above is decided by default and FOUNDRY
builds it unless he says otherwise.

**Card 1 — who is on the list.** The item says four. The canon library's own text
disagrees at both edges:

| option | trade |
|---|---|
| A. The four as filed | matches the ruling; ships a Gungan that the library calls a breath-holder as a water-breather |
| B. The four plus **Quarren** | the library calls Quarren "natural swimmers, most comfortable underwater, preferring to be immersed", they are 0.222 of the Deepwater faction beside Mon Calamari — the faction "built around being aquatic" then has all three of its lead species covered |
| C. B minus **Gungan** | strictly what the library supports; Gungan gets `waterCellCost` (swims) but not the drowning immunity — which under one shared gene means Gungan gets nothing, or gets vanilla `WebbedPhalanges` instead |

Herglic is not proposed: the library says its waterborne ancestry "had been bred out"
and it breathes through a blowhole.

**Card 2 — deep water stays a wall.** Default: yes, this brief leaves deep water
impassable for everyone. If he wants aquatic pawns to swim the seas and deep canals —
an obvious thing to want on a water faction — that is a separate engineering item
(per-pawn pathing context), not a field on this gene, and it should be filed as one
rather than grow inside this build.

## 7. Verification FOUNDRY owes

- `MayRequire` on a `<li>` inside `makeImmuneTo` is skipped cleanly with FlowWorks
  absent (minimal list without FlowWorks: no red on load, gene present).
- Gene tab on a Mon Calamari shows the immunity line and the custom effect text.
- Quicktest: a water-breather and a baseliner in a flooded pit — after N struggle
  intervals the baseliner carries `RM_PitDrowning`, the water-breather does not.
- Wading: a drafted water-breather's path across shallow water is straight; a
  baseliner's detours. `SoakingWet` absent on the water-breather after wading.
- `validate_patch.py` on the ThoughtDef patch with both `--live` and `--defs`.
