# Genepack mods plunder — GENEPACK_MODS_PLUNDER_1

Inventory of the two mods the owner subscribed 2026-09-06 (both INACTIVE, not in ModsConfig.xml).
Source read: mod XML + About.xml on disk; DLL internals from About text + keyed strings, not decompiled.

## Mod identities

| | Genepacks Injection | More Consumables and Mutagens (Continued) |
|---|---|---|
| packageId | `TommasoBelluzzo.GenepacksInjection` | `Mlie.MoreConsumablesAndMutagens` |
| workshop id | 3784789591 | 2042709249 |
| folder | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3784789591` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2042709249` |
| requires | Biotech | nothing (pre-Biotech design, 1.1–1.6) |
| shape | 1 patch + 1 JobDef + DLL (`GenepacksInjection.dll`) | pure XML: 13 drug files, slime animal, research tab |

### What each does mechanically

**Genepacks Injection**: patches vanilla `Genepack` ThingDef with `CompProperties_Usable`
(useJob `UseItem`, 150 ticks) + `GenepacksInjection.CompPropertiesGpi` +
`CompProperties_UseEffectDestroySelf`. A pawn injects a genepack into self, or administers
to prisoners/slaves (JobDef `GenepacksInjection_InjectGenepack`, driver `JobDriverGpi`).
Genes MERGE into the recipient's pool — only missing genes added, as xenogenes by default
or endogenes via mod setting (`useEndogenes`). Genepack consumed; recipient enters
xenogermination coma (per About text — coma behavior UNMEASURED, not decompiled).
No gene extractor, no xenogerm assembly, no building — the genepack itself is the syringe.

**More Consumables and Mutagens**: XML-only drug suite. Two cook-station drinks, two
DrugLab preparations, 4 trader-only mutagen pills, a craftable mutagen chain
(catalyst serum → hatches a slime → butcher/milk slime → brew slurry → drink → random
mutations as hediffs), plus `Oracalium` (neolithic psychite divination powder) and
`Ichorio` (5500-silver stacking power elixir).

## GeneDef table

**Neither mod defines a single GeneDef** (grep GeneDef across both: 0 hits — verified).
Genepacks Injection operates on whatever genepacks exist in the game (vanilla Biotech +
any gene mods); the consumables mod predates Biotech and uses hediffs, not genes.
**Consequence: there is no heat-generating GeneDef here.** The Rot's grown-heater
mushroom gene must come from vanilla/other mods or be authored ours (vanilla Biotech has
no heat-emitting gene — UNMEASURED, verify in the def dump before authoring). Nearest
thematic cousins here are hediffs: `IgniFurnace` (mutation: furnace — stomach furnace,
ComfyTempMin −8, eats more, rests less) and `IgniWarm` (ComfyTemp band shifted down).

## Consumable mechanics table (all defNames live in the 1.6 folder)

| item (defName) | made at | effect | reuse flag |
|---|---|---|---|
| `AmbrosiaTea` | stove ×2 Ambrosia → 2 | hediff `ATeaHigh`: pain ×0.85–0.9, BloodFiltration +, MB threshold −; own chemical/addiction chain, addictiveness 0 | **live-only prep**: `CompProperties_Rottable` daysToRotStart 4, rotDestroys — but rot PAUSES when refrigerated, so "dies if refrigerated" needs a custom comp; the 4-day clock is the model |
| `HearthBrew` | stove ×10 RawBerries → 3 | `HearthBrewHigh`: ComfyTempMin −6/−8, SocialImpact +, plus a real alcohol dose | live-only (rots in 4 d); a *warmth-in-a-cup* — The Rot's cold-nights drink |
| `HerbalTincture` | DrugLab ×4 herbal med | `HerbalTinctureHigh` 1 day: ImmunityGainSpeed +0.1, consciousness/sight/moving −0.10, restFall ×1.5; overdose risk | medical prep; good Rot apothecary item as-is |
| `Oracalium` | DrugLab, 6 psychoid + 1 herbal med, neolithic | `OracaliumHigh` (pain ×0.65, Sight +0.30) + accumulating `OracaliumLongTerm` "oracle psionic" (Sight up to +0.40, decays 0.01/day); 4% addictive, nasty withdrawal | **luciferium-lite bargain**: permanent-ish power that must be re-fed; also literally named for Oracles — Rot flavor gift |
| `Ichorio` | UNMEASURED recipe (WorkToMake set but no recipeMaker/recipe found) — trade/quest item | `IchorioHigh` stacks ×4: +5% manip/sight/moving per class, painFactor rises with class | **biosculpter-in-a-cup shape**: drink-to-ascend tiers; ideal rare vault loot |
| `MutagenSlurry` | DrugLab: 15 raw meat + 10 `SlimeGlob` + 1 industrial med (research `MutagenTwo`) | `SlurryHigh` ~3 days: heavy debuffs + vomiting while 19 random mutation hediffs roll | **the bargain drug**: suffer the reaction, keep permanent mutations |
| `CatalystSerum` | DrugLab: 15 raw meat + 2 neutroamine + 2 industrial med (research `MutagenOne`) | `CompProperties_Hatcher`: hatches a `CMSlime` in 1.5 d; temperature-ruinable −5..55 °C | **grow-your-own-organism**: an item that BECOMES a creature |
| `Igni`/`Sil`/`Ursa`/`Midia`/`Myrol` pills | not craftable (trader/loot only) | each = themed mutation roulette: Igni labor/heat (`IgniFurnace`, `IgniArm` weapon-part, `IgniCore` 1.5× heart), Sil flora/beauty (`SilEyes`, `SilSkin` armor, toxins), Ursa beast (claws/horns = melee verbs, `UrsaWild`), Midia mind (`MidiaSmart` +85% learning / `MidiaAbsent`), Myrol regen (`MyrolMyrolsis` heals permanent wounds) | war-era designer mutagens; loot-table ready |
| `SlimeGel`/`SlimeGlob`/`SlimePaste` | milk live slime / butcher slime (60 glob) / DrugLab 5 gel → 20 paste | resources; gel rots 40 d, glob 60 d, paste is 0.25-nutrition food | superorganism secretion model |
| `EggSlimeUnfertilized`/`EggSlimeFertilized` | laid by `CMSlime` (also milkable, egg-layer, predator, bodySize 3.5, healthScale 10) | fert. egg hatches slime 5.5 d, temp-ruinable | reactor-spawn model |

Mechanics of note: mutation hediffs use `makeImmuneTo` for mutually-exclusive pairs
(SilSkin↔UrsaFur↔SlurrySlimy, IgniSpeed↔UrsaSlow, etc.) and `HediffCompProperties_Immunizable`
so high immunity pawns can shrug mutations off; part mutations are `Hediff_AddedPart` with
melee verbs. Research: tab `MutagensAndConsumables`, projects `MutagenOne`/`MutagenTwo`
(hi-tech bench + multi-analyzer). No new workstations — everything uses stove/DrugLab.

## Genepack acquisition assessment (for AB_GelatinousSuperorganism)

Genepacks Injection **adds no acquisition route at all** — it is a CONSUMPTION mod
(vanilla routes remain: gene extractor, traders, quests). What it contributes to the
"living gene reactor" biome is the back half of the loop: **a genepack harvested from the
superorganism is directly usable, no gene bank / xenogerm lab / Biotech infrastructure
needed** — inject on the spot, genes merge, pack destroyed. That makes field-harvested
genepacks a self-contained treasure. The front half (extraction FROM the organism) must
be ours; the consumables mod supplies the proven XML patterns to carry it:

1. `CompProperties_Milkable` on a creature yielding an item (SlimeGel model) — periodic
   genepack "secretion" from a tended superorganism node. Vanilla comp, zero C#.
   ⚠️ Milkable yields ONE fixed thingDef; random-gene genepacks need C# or a hatcher relay.
2. `butcherProducts` (SlimeGlob ×60) — kill a node, harvest a genepack clutch. Zero C#.
3. `CompProperties_Hatcher` + `CompProperties_TemperatureRuinable` (CatalystSerum model) —
   extracted "gene buds" that must be kept warm/alive or they spoil: the **live-only,
   dies-outside-the-reactor** feel, vanilla comps only.

## What to steal

**For the Superorganism sheet (AB_GelatinousSuperorganism):**
- `CMSlime` as the node template: milkable + egg-layer + butcherProducts on one predator
  body (healthScale 10, needsRest false) — reskin to gel-mass, yield genepacks/gel.
- CatalystSerum's hatcher+temperature-ruinable combo for extracted material that dies off-reactor.
- Genepacks Injection closes the loop: extracted packs are immediately-injectable prizes,
  and its endogene setting can make reactor genes "true" inheritance rather than xeno overlay.
- MutagenSlurry's `SlurryHigh` (debuff phase rolling 19 random hediffGivers) as the
  "raw contact with the reactor" hazard event.

**For The Rot's items:**
- `IgniFurnace`/`IgniWarm` hediffs = the grown-heater effect in hediff form (no gene exists;
  author `RUT_` gene or hediff modeled on these numbers).
- HearthBrew (ComfyTempMin −6/−8 drink) + AmbrosiaTea's 4-day rotDestroys = template for
  live teas; add a freeze/refrigeration-kill comp if "dies if refrigerated" must be literal.
- Oracalium = luciferium-style bargain done cheap (accumulating long-term hediff + decay +
  withdrawal); Ichorio's 4-class stacking hediff = biosculpter-cycle-in-a-cup.
- Ursa/Sil/Midia pills as "archive of a war's genetic material" loot — descriptions already
  read as banned military/glitterworld mutagen programs.

Not verified: DLL internals (coma, prisoner-administer flow — About text only); whether an
Ichorio recipe exists anywhere (none in XML); vanilla-gene heat emitter absence (UNMEASURED).
