# Mutation modifiers survey — `MUTATION_MODIFIERS_SURVEY_1`

Feeds `the_contagion.md` §7's Contagion-touched deck (owner ruling: **"It never just
upgrades you. You do not want this."**) and the Unfinished's random-limb spawner
(same part-addition mechanism, still owed as C#).

**Dump used:** `defs.sqlite`, mods=596/cec112bad2152f47, captured 2026-09-05T14:41:26Z
(via `measure` — `~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py`).
The dump has no `statBases`/no `stages` on most defs (a known blind spot — see
`rimworld-def-dump-blind-spots.md`), so every stat/stage/hediffGiver claim below is
sourced from the **live mod XML on disk**, not the dump; `measure` is cited only where
it answered (existence/absence, defName spelling). Per-row source is given in the table.

## Sources read

| system | path |
|---|---|
| Biotech genes | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Biotech\Defs\GeneDefs\GeneDefs_Misc.xml`, `GeneDefs_Sanguophage.xml` |
| Biotech xenogerm hediffs | RimSage `search_source`/`get_def_details` against the decompiled C# + HediffDefOf (no XML "rejection" hediff exists — see finding below) |
| Anomaly shambler/ghoul | `...\RimWorld\Data\Anomaly\Defs\HediffDefs\Hediffs_Mutants.xml` |
| Anomaly biomutation lance | `...\RimWorld\Data\Anomaly\Defs\ThingDefs_Misc\Apparel_Utility.xml` |
| More Consumables & Mutagens | `design/Jawa/worldbuilding/genepack_mods_plunder.md` (reused per spec) + `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2042709249\1.6\Defs\Drugs\HM_Slurry.xml`, `Crystal_Ursa.xml`, `Crystal_Igni.xml` (re-derived only where the plunder doc didn't have defNames/stat numbers — the `SlurryHigh` roll table and two paired hediffs) |
| Alpha Biomes (Ocular Forest) | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1841354677\1.6\Defs\ThingDefs_Plants\Plants_OcularForest.xml` |
| Alpha Animals | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1541721856\1.6\Defs\HediffDefs\Hediffs_Local_AddedParts.xml`, `Defs\ThingDefs_Races\Races_InfectedAerofleet.xml` |
| Vanilla luciferium | `...\RimWorld\Data\Core\Defs\Drugs\Luciferium.xml` |

## Classification table

Legend — **class**: G genetic / S somatic / P part-addition / B behavioral.
**Rev.**: reversible? **Net−**: net-negative guaranteed (by the def itself, not by
narrative)? **Vis.**: visible on the pawn (art/render, not just a tooltip)?

| system | defName(s) | class | rev. | net− | vis. | notes / source |
|---|---|:-:|:-:|:-:|:-:|---|
| Biotech instability genes | `Instability_Mild`, `Instability_Major` | G | no (gene stays until removed) | **no** — pairs `biostatMet +2/+4` (cheaper to run) against `LifespanFactor 0.8/0.6`, `CancerRate ×3/×5`, `ImmunityGainSpeed 0.96/0.92` in the SAME def | no | live XML `GeneDefs_Misc.xml:282-315`. Exemplar of "every roll pairs a cost" — the model to copy. |
| Biotech archite genes | e.g. `ArchiteMetabolism` (`biostatCpx 6`, `biostatMet 6`, `biostatArc 2`) + Sanguophage/ability archite genes | G | no | **no — pure positive** on the body; the only cost is genome-complexity budget (a meta-resource, not a body debuff) | no | live XML `GeneDefs_Sanguophage.xml:259-270`. Cited as a NEGATIVE example: archite genes are the vanilla "unambiguous upgrade" — the Contagion deck must never resemble this shape. |
| Biotech xenogerm implant | `XenogerminationComa`, `XenogermReplicating` | S | yes (both `HediffCompProperties_Disappears`) | **no** — pure debuff (temp Consciousness cap), no lasting change once it disappears | yes (bedridden/incapacitated) | RimSage source read: `GeneUtility.cs:185,199,237`, `HediffDefOf.cs:267,276`. No "rejection" mechanic exists in Biotech at all — searched `[Rr]ejection` across the decompiled source, only hits are unrelated (ritual/creepjoiner systems). **Spec bullet "xenogerm rejection" is UNMEASURED/absent — there is no such mechanic to survey; noting the negative finding rather than inventing one.** |
| Anomaly — Shambler | `Shambler` (hediffClass `Hediff_Shambler`) | B (whole-pawn state, not a modifier) | no (`everCurableByItem false`; dies of metabolic exhaustion in ~4.2–4.8 days, `HediffCompProperties_DisappearsAndKills`) | **yes, total** — Talking ×0, Consciousness ×0.7, no natural healing, no pain | yes | live XML `Hediffs_Mutants.xml:7-50`. Too extreme/whole-pawn for a modifier deck; cited as the severity ceiling. |
| Anomaly — Ghoul | `Ghoul` | B/P hybrid (archotech shard implant) | no (`everCurableByItem false`, `keepOnBodyPartRestoration`) | **yes, total** — can't work, forced raw-meat diet, disturbing to others | yes | live XML `Hediffs_Mutants.xml:113-`. Same ceiling note as Shambler. |
| Anomaly — biomutation lance | `Apparel_BiomutationLance` → target becomes a fleshbeast-type creature | whole-body **transformation**, not a modifier | no | n/a (total replacement) | yes | live XML `Apparel_Utility.xml:311-`. Not a per-stat mutation system — full creature swap. Relevant only as the naming precedent for "biomutation" as in-universe vocabulary. |
| More Consumables — part mutations | `Igni{Furnace,Arm,Core,Speed}`, `Sil{Eyes,Skin,Degraded}`, `Ursa{Claws,Horns,Fur,Wild,Slow,Disfigured}`, `Midia{Smart,Absent,Rough,Keen,Blur}`, `Myrol{Myrolsis,Lung}` | S/P (mixed — some `Hediff_AddedPart` w/ melee verbs, some pure stat hediffs) | no (permanent hediffs, no removal item) | **NO — not guaranteed.** e.g. `UrsaClaws` (0.65-efficiency claw, `Verb_MeleeAttack` dmg 14) has **zero listed downside**; `SlurryStrong` (`CarryingCapacity +10`, `MeleeHitChance +0.1`, `MiningSpeed +0.1`) likewise pure gain. Costs (`UrsaDisfigured` −0.35 SocialImpact, `SlurryStagnant` −0.1 melee hit/dodge) are SEPARATE independent rolls in the same table, not attached to the gains. | yes (part-addition ones; stat-only ones no) | live XML `Crystal_Ursa.xml:83-113`, `HM_Slurry.xml:181-225`, `genepack_mods_plunder.md`. **Key finding — see "What surprised" below.** |
| More Consumables — `SlurryHigh` roll engine | `SlurryHigh` (hediffClass `HediffWithComps`, `HediffCompProperties_SeverityPerDay −0.30`) drives 19× `HediffGiver_Random` (`mtbDays` 13–26, several with `partsToAffect`+`countToAffect`) while active (~3 days) | S (delivery mechanism) | the delivery hediff itself decays (`severityPerDay −0.30`) but every mutation it rolls is permanent | n/a (roll table, see rows above) | n/a | live XML `HM_Slurry.xml:242-424`. **This IS the mechanism to reuse for Contagion exposure** — a timed reaction hediff whose `HediffGiver_Random` list rolls sub-hediffs onto random parts. |
| More Consumables — `CatalystSerum`/`CMSlime` | hatcher item → creature | P (creates a new organism, not a pawn mutation) | n/a | n/a | n/a | `genepack_mods_plunder.md` — reused, not re-derived. Relevant to the Unfinished spawner as a "grows into something" precedent, not to the pawn-modifier deck. |
| Alpha Biomes — half-transformed tree | `AB_HalfAlienTree` (a wild `ThingDef`, not a hediff) | **not a modifier system at all — a static def variant** | n/a (it's a separate plant def, no transition mechanic) | n/a | yes (that's the point) | live XML `Plants_OcularForest.xml:153`. "A strange infection seems to be transforming this regular oak into an ocular tree" — the transformation is AUTHORED as a fixed intermediate def, never a runtime process. Confirms the item spec's "half-transformed tree pattern" is a content-authoring trick, not code to survey. |
| Alpha Animals — infected variants | `AA_InfectedAerofleet` (own `ThingDef`/race, already the Contagion's Infected Aerofleet per `the_contagion.md` §4) | same as above — a separate race def, not a hediff transform | n/a | n/a | yes | live XML `Races_InfectedAerofleet.xml:4`. Already in play as Contagion fauna; not a modifier mechanism to reuse for pawns. |
| Alpha Animals — added-part mutations | `AA_MutantLeg`, `AA_MutantArm` (+ 6 eye variants) | S/P (`Hediff_AddedPart`, `isBad=false` on the abstract base) | no (no removal path found; `spawnThingOnRemoved` only covers surgical removal, not natural reversal) | **no** — each pairs a small capacity gain (`Moving +0.05` / `Manipulation +0.05`, `AA_MutantArm` also grants a fist-tool melee verb) against `PsychicSensitivity +0.1..0.15` and `ToxicResistance −0.1..−0.15` **in the same hediff** | yes | live XML `Hediffs_Local_AddedParts.xml:1-80`. **Second exemplar of cost-paired-in-one-def**, alongside vanilla `Instability_*` — closest existing pattern to what the Contagion deck needs. |
| Vanilla — luciferium | `LuciferiumHigh` (pure positive: Consciousness/Moving/Sight/BloodFiltration/BloodPumping/Metabolism/Breathing all up, `HealPermanentWounds` comp) + `LuciferiumAddiction` (separate hediff, `everCurableByItem false`, berserk + `deathMtbDays 10` on withdrawal) | S | **no** — first dose is permanent per the flavor text ("no way to get the mechanites out, ever"); `LuciferiumAddiction` itself never clears | **no, and this is the cautionary case**: the boon hediff alone is a strict upgrade; the cost lives entirely in a SEPARATE hediff a min-maxer can service by never running out. | no (no visual tell) | live XML `Luciferium.xml`. Explicit anti-pattern for the Contagion deck: **do not split boon and cost into two hediffs** — a well-stocked player evades the cost forever. Pair them in one hediff, as `Instability_*` and `AA_Mutant*` do. |
| Vanilla — permanent scars | old-wound/chronic hediffs (generic engine behavior: an unhealed injury converts to a permanent low-severity chronic hediff) | S | no | no (pure downside, small) | yes (scar art) | Not a bespoke def — this is base-game injury-permanence behavior, not a named mutation system. Cited for completeness per the spec bullet; no single defName names it. |
| Anomaly containment/mutation research context | n/a | — | — | — | — | `ANOMALY_EXCEPTION_ACCESS_1` confirmed DONE/closed — Anomaly content (incl. the above two hediffs) is readable and usable; access is by Memory-Core event, not research, per that item's ruling. No blocker to citing it here. |
| The Unfinished (random-limb spawner) | **not yet built** — no defName exists | P | — | — | — | Per `the_contagion.md` "Owed": "the C# spawner (random stats, random `Hediff_AddedPart` limbs, short lifespan, goo-corpse)" is still outstanding. This survey supplies its mechanism precedent (`AA_Mutant*`, `SlurryHigh`'s `HediffGiver_Random` engine) but **cannot inventory a defName that doesn't exist yet** — flagged, not guessed. |

## What surprised

1. **"Xenogerm rejection" does not exist.** Grepped the decompiled Biotech/RimWorld
   source for `[Rr]ejection` — every hit is ritual-target or creepjoiner code, nothing
   gene-related. The actual xenogerm-implant cost is two temporary hediffs
   (`XenogerminationComa`, `XenogermReplicating`) that just gate timing, not a rejection
   risk. If the owner meant something else by "xenogerm rejection," it needs naming —
   this survey reports the absence rather than substituting a guess.
2. **The two mods with the richest mutation content (More Consumables, Alpha Animals)
   do NOT reliably pair cost with gain.** `UrsaClaws` and `SlurryStrong` are bare
   upgrades in their own defs; the game only "balances" the roll table statistically
   across many independent rolls, not per-outcome. If the Contagion deck copied this
   pattern directly it would violate the item's own title. The two defs that DO pair
   cost in the same hediff — vanilla `Instability_Mild/Major` and Alpha Animals'
   `AA_MutantLeg/Arm` — are the actual templates to copy.
3. **Luciferium is the textbook anti-pattern**: splitting the boon (`LuciferiumHigh`,
   pure positive) from the cost (`LuciferiumAddiction`, a separate hediff serviced by
   stockpiling) lets a resourced player carry zero risk. The Contagion's "never an
   upgrade" guarantee only holds if boon and cost live in ONE hediff, never two.
4. **Alpha Biomes/Alpha Animals' "transformation" content isn't code** — the
   half-transformed tree and the infected Aerofleet are both static alternate `ThingDef`s
   placed by hand/mapgen, not a hediff-driven mutation process. The item spec named
   them as a "pattern" to survey; the finding is that the pattern is **authoring**, not
   **mechanism** — nothing to wire up, just a naming/placement convention already in use
   in `the_contagion.md` §4.

## Proposed Contagion-touched deck

Per the item's spec ("weighted toward somatic/part mutations and instability, with the
never-upgrade guarantee enforced by construction (every roll pairs at least one cost)")
and `the_contagion.md` §7's ruling that it "starts much larger, more random mutations…
It never just upgrades you."

**Mechanism**: reuse `SlurryHigh`'s shape — one delivery hediff
(`RSW_ContagionExposure` or similar, not yet authored) with a `HediffCompProperties_SeverityPerDay`
decay and a `HediffGiver_Random` list of **20-ish sub-hediffs, each of which must itself
carry both a gain and a cost** (never a bare-gain sub-hediff like `UrsaClaws`/`SlurryStrong`
were found to be). Enforcement is at authoring time, by construction, exactly as the
item's spec demands — not by a runtime "must pick one good + one bad" roller, which is
more code for the same guarantee a hand-written table already gives for free.

**Weighting** (of the ~20 slots):
- **9–10 somatic/part-addition mutations**, modeled directly on `AA_MutantLeg/Arm` and
  the More Consumables `Igni/Sil/Ursa/Midia/Myrol` families: each grants one small
  capacity/verb benefit and pairs it with `PsychicSensitivity` up / `ToxicResistance`
  down / a `SocialImpact` or similar hit, all in the same def (never split like
  `UrsaDisfigured` vs `UrsaClaws`).
- **6–7 instability-flavored genetic/metabolic slots**, modeled on `Instability_Mild/Major`:
  cheaper upkeep (a resource-cost break, matching the Contagion's "genetic lottery" loot
  framing in §7) paired with `LifespanFactor` down, `CancerRate` up, `ImmunityGainSpeed`
  down.
- **3–4 behavioral/consciousness slots**, modeled on `XenogerminationComa`'s temporary
  capacity cap (recurring bouts of reduced Consciousness/Manipulation during a Burn,
  thematically "the mutation engine idling") — reversible in the sense the cap lifts,
  but the underlying part-addition stays.
- **0 archite-gene-style slots and 0 luciferium-style split hediffs** — both are
  explicitly excluded by the anti-pattern findings above.

**Never-upgrade enforcement, concretely**:
- Every sub-hediff def gets both a `statOffsets`/`capMods` gain block AND a cost block
  in the SAME `<li>` — the `Instability_*`/`AA_Mutant*` shape, never the
  `UrsaClaws`/`SlurryStrong` shape.
- No sub-hediff may be `everCurableByItem` or removable by ordinary means (matches
  §7's cure ruling: "arrest, not reversal — what already changed stays").
- The delivery hediff's decay (`severityPerDay`) governs EXPOSURE ending, never the
  mutations it already rolled — mirroring `SlurryHigh` exactly (the drug fades; the
  19 hediffs it seeded do not).

## 5 best Contagion-touched candidate templates (by source def, ranked)

1. **`Instability_Mild`/`Instability_Major`** (`GeneDefs_Misc.xml:282-315`) — the
   cleanest existing "cost baked into the same def as the benefit" pattern in the whole
   stack; directly portable as a hediff-flavored reskin (metabolic cheapness ↔
   lifespan/cancer/immunity cost).
2. **`AA_MutantArm`** (`Hediffs_Local_AddedParts.xml:40-80`) — part-addition +
   verb-giver + paired cost, all in one def; the closest thing to a ready-made
   Contagion mutation.
3. **`SlurryHigh`'s `HediffGiver_Random` engine** (`HM_Slurry.xml:242-424`) — the
   delivery/roll MECHANISM (not its individual sub-hediffs, which fail the pairing
   test) to reuse wholesale for a `RSW_ContagionExposure` hediff.
4. **`XenogerminationComa`** (vanilla `HediffDefOf.cs`/decompiled Biotech) — temporary,
   guaranteed-negative capacity cap; template for the "Burn-triggered idling" behavioral
   slots.
5. **`MidiaSmart`/`MidiaAbsent`-style mind mutations** (More Consumables,
   `genepack_mods_plunder.md`) — provided the pairing is rebuilt (source shows them as
   independent rolls, per finding #2 above) rather than copied verbatim, they're the
   best-fitting flavor match for a "mind cycles between half-conscious stupor and
   [something]" Contagion tell.

## Spec bullets NOT completed

- **"xenogerm rejection"** — searched and found absent as a named mechanic (see
  "What surprised" #1). Reported as a measured negative, not invented.
- **The Unfinished's own defName inventory** — cannot be surveyed because the C#
  spawner and its hediffs are not yet built (`the_contagion.md` "Owed" still lists it).
  This survey supplies the mechanism precedent it should draw from instead.
- **A specific vanilla "mechanites" system separate from luciferium** — checked; vanilla
  RimWorld has no standalone mechanite/nanite hediff outside luciferium's flavor text
  and the unrelated Biotech mechanitor/mechlink equipment (which is not a mutation
  system — it's mech-control hardware). Folded into the luciferium row rather than
  listed as a separate miss, since it appears the spec bullet intended luciferium.
