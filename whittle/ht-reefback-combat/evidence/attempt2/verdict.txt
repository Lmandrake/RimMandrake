# Independent Codex judgment — reefback nursery combat

Judged 2026-11-11 in `/home/mandrake/rm/codex-ht` by a fresh Codex reader that did not make the work. **KEEP the implemented stat/profile remedy and the bounded current nursery wording. All three frozen bullets and both L0 criteria are true within their stated offline scope.** This does not endorse every incidental assertion in the delegated design response; two errors are explicitly rejected below.

## Reading and execution boundary

I read the allowed statement, notes, item-before, independent design prompt/response, neutral raw evidence, relevant source, installed Core/five-DLC definitions and offline managed metadata, and permitted rules/specifications. I did not read builder conclusions, reconciliation documents, previous judgments, handoffs or parent summaries, or discover Whittle files outside `evidence/raw/`. No contamination was encountered. References below to files named inside allowed documents are not claims that I opened those files.

Every shell exported the three required seats as `CODEX_STEVEDESKTOP_HUGETHINGS`, sourced the required testcentre environment, and carried all three through `WSLENV`. I made no game, bridge, build, deployment, network, ledger or git mutation and accessed no other clone. This judgment is my only file write. I did not run the general validator: its entry point reads configuration and records evidence (`skills/rimworld-modding/scripts/validate_patch.py`, `_evidence_start`, `_record_evidence`, `main`). I inspected the exact XML and ran separate in-memory checks instead. An initial optional `lxml` import was unavailable; the completed checks used standard-library XML and .NET XPath.

## Exact frozen bullets

1. **TRUE** — “Reconcile the young reefback, adult reefback and warden mother's combat roles with the established Miasma nursery lifecycle through independent delegated design judgment, preserving existing residents and measured young body sizes.”

   The independently delegated remedy in [design_raw.json](evidence/design_raw.json), `result` §§1–3, is implemented in the young ThingDef and PawnKindDef. The explicit, pre-tuning hunting assumptions are in [design_prompt.txt](evidence/design_prompt.txt), opening paragraphs. The current nursery specification, [miasma_fauna_roster_2026-09-23.md](../../design/Jawa/worldbuilding/biomes/miasma_fauna_roster_2026-09-23.md), §4, paragraph “Reefback combat detail”, agrees with the resolved nominal stats and uses a relative ranged damage budget. Its narrower wording avoids unsupported safety promises. The young remains size 6.4/16; neither an eviction nor maturation into the adult was introduced. Raw comparisons and stage checks below substantiate preservation independently of the design verdict.

2. **TRUE** — “Apply warranted local stat/profile or specification corrections and demonstrate exact effective stage damage and health, with a worked modest hunting comparison against the adult and meaningful focused XML/inheritance positive and negative controls.”

   The warranted corrections are local tools, armor, health, kind combatPower and the thin-crust description. The old calf inherited juvenile damage 360/90 and HealthScale12, above the resident adult/elder mother's 22/18 and HealthScale7. This is a demonstrated source/specification tension, not an observed gameplay failure. The stage table, damage consumer, before/after comparison, replacement/merge fixtures, parent failure, and adult/mother controls below substantiate this bullet. Primary artifacts: [current sea-beast XML](../../src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml), [raw before XML](evidence/raw/before/src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml), [controls](evidence/raw/final/controls.json), and [engine IL](evidence/raw/engine-final.stdout.txt).

3. **TRUE** — “Retain reproducible offline source evidence and a fresh independent Codex judgment for the complete decision; distinguish the source model from actual hits, population outcomes and live balance, and make no deployment, flight, art or L4 acceptance claim.”

   The raw folder retains source snapshots, input hashes, engine-reader and XPath scripts, fixtures, arithmetic, process arguments, return codes and streams. I independently reproduced the selected arithmetic and controls and reproduced the installed reflection-only IL byte-for-byte. This file supplies the fresh judgment. No actual hit, downing, kill time, population result, live balance, deployment, flight, render/art or L4 acceptance is established. These are explicit L0 criteria; live hits are not an additional gate.

## Inheritance, changes and consumers

The complete selected ThingDef chains are `BasePawn → AnimalThingBase → RM_Reefback → RM_ReefbackJuv` and `BasePawn → AnimalThingBase → RM_WardenMother`. The kind chains are `AnimalKindBase → RM_Reefback_Kind → RM_ReefbackJuv` and `AnimalKindBase → RM_WardenMother`. Installed Core `Defs/ThingDefs_Races/Races_Animal_Base.xml` supplies all three base nodes. The adult source is sea-beast XML lines 1314–1430; the young is lines 1840–1918; [mother XML](../../src/RimMandrake/Miasma/Defs/ThingDefs_Races/RM_WardenMother.xml) supplies the mother and elder stage. The same inputs are retained under [raw/final/inputs](evidence/raw/final/inputs.json).

Direct comparison of the before/current sea files found **34 top-level definitions in each, with exactly two changed nodes**, the young ThingDef and kind. Within those nodes the changes are exactly: expanded thin-crust description; added sharp/blunt/heat armor 0.30/0.25/0.30; replacement tools 16/10 with cooldowns 3/2.5 and bulk chanceFactor0.3; baseHealthScale8; combatPower150. Tools use `Inherit="False"`; statBases merge. Adult tools480/120, health20, size32, armor0.70/0.60/0.75 and kindPower2000 remain. The mother's file and both biome files are byte-identical to their raw before snapshots. The young's age table, graphic stages and group2~3 also compare unchanged.

Inherited source values retained by the calf include MoveSpeed2, MarketValue8000, comfy temperatures−30/50, Wildness1, Pinniped body, sealskin leather, waterSeeker, waterCellCost1, foodTypeNone, disableMating, canBePredatorPreyfalse, manhunterOnDamageChance0.2, lifeExpectancy500, ecosystemWeight4 and kind water-speed factor2. The current Miasma row is0.15; Grey Sea adult row0.005. Neither density6.5 nor ecosystemWeight4 nor group2~3 is a population count. Parent and child graphic stages are separate from combat stage factors.

Installed Core `Defs/Misc/LifeStageDefs/LifeStages.xml` lines176–222 gives baby body/health/melee factors **0.2/0.25/0.5**, juvenile **0.5/0.6/0.75**, and adult constructor defaults1. The elder specifies body factor1 and inherits health/melee constructor defaults1. These defaults are verified in `RimWorld.LifeStageDef::.ctor` in the retained IL, not guessed from missing XML.

The production consumer chain is `Tool.AdjustedBaseMeleeDamageAmount → VerbProperties.AdjustedMeleeDamageAmount → GetDamageFactorFor → Verb_MeleeAttackDamage.DamageInfosToApply` (including its iterator `MoveNext`). For healthy natural linked parts with no equipment/hediff/gene modifiers it uses tool power × linked-part efficiency1 × stage melee factor × `MeleeDamageFactor`1. Installed Core `Defs/Stats/Stats_Pawns_Combat.xml` lines20–34 gives that stat's default1 and an Anomaly shambler-crawling modifier, excluded by the healthy/unmodified premise. The actual damage iterator subsequently applies a **0.8–1.2 random multiplier**, followed by damage/armor processing. Therefore the table reports nominal adjusted damage, not exact realized hits. Damage-derived armor penetration, damaged linked parts, tool selection, misses and downstream injury mechanics also matter. See [engine-final.stdout.txt](evidence/raw/engine-final.stdout.txt), methods beginning at lines91,912,1012,1109,1209.

`Pawn.BodySize` is baseBodySize × stage bodySizeFactor; `Pawn.HealthScale` instead uses baseHealthScale × healthScaleFactor. `BodyPartDef.GetMaxHealth` multiplies the part's base hitPoints by HealthScale and takes `CeilToInt`. Installed Odyssey `Defs/Bodies/Bodies_Animal_Pinniped.xml` has corePart Body and both linked groups, HeadAttackTool and FrontLeftPaw. Installed Core body parts supply Body40, Brain10 and Heart15. Body is one part, not the pawn's total health pool. See retained IL lines719–727,892–911 and the installed snapshots in `raw/final/inputs/installed/Data/`.

I also checked a real override omitted by the instrument's narrow health-getter search: [RM_ForgeDhoggurSwell.cs](../../src/RimMandrake/TheForge/Source/RM_ForgeDhoggurSwell.cs), lines243–315, patches `Pawn.HealthScale` and `BodySize`. It multiplies only pawns in the swell registry; registration is through the swell comp. None of these selected resolved races has that comp or the swell hediff. It does not alter the healthy selected model. The named Pyrelands health rewrite applies to FurnaceBeast, and Greentide combatPower writes apply to its ant kinds. This is an explicit dismissal after reading their guards, not a claim that runtime patches cannot exist.

`combatPower` does not multiply attack damage or health. The installed `PawnGenOption.get_Cost` reads it for generation cost (IL lines72–76). Local [RM_PitBuyer.cs](../../src/RimMandrake/KeelHoist/Source/RM_PitBuyer.cs), lines46–52, reads it for beast fighter classification; its kernel threshold is100, so both150 and2000 qualify. Pyrelands arrival selection filters canArriveManhunter, which the calf still inherits asfalse. Thus150 is profile/cost metadata, not evidence for lower hits or a demonstrated population effect.

## Independently rederived effective stages

Nominal powers below assume the healthy, unmodified natural-melee case above. HP triples are **Body / Brain / Heart**, calculated with float32 multiplication before ceiling.

| Race/stage, minimum age | BodySize (decimal) | HealthScale (decimal) | Nominal tool damage | Part max HP |
|---|---:|---:|---:|---:|
| Young baby,0 | 6.4 | 2 | 8 / 5 | 80 / 20 / 30 |
| Young juvenile,0.1 onward | 16 | 4.8 | 12 / 7.5 | 192 / 48 / 72 |
| Adult-race baby,0 | 6.4 | 5 | 240 / 60 | 200 / 50 / 75 |
| Adult-race juvenile,0.2 | 16 | 12 | 360 / 90 | 480 / 120 / 180 |
| Adult-race adult,0.6 | 32 | 20 | 480 / 120 | 800 / 200 / 300 |
| Mother baby,0 | 1.6 | 1.75 | 11 / 9 | 70 / 18 / 27 |
| Mother juvenile,0.15 | 4 | 4.2 | 16.5 / 13.5 | 169 / 43 / 64 |
| Mother adult,0.4 | 8 | 7 | 22 / 18 | 280 / 70 / 105 |
| Mother elder,38 | 8 | 7 | 22 / 18 | 280 / 70 / 105 |

Float32 young juvenile HealthScale is4.800000190734863; multiplying by40 rounds to192 before ceiling. Mother juvenile HealthScale is4.200000286102295; its Body product exceeds168 and ceilings to169. These independently recomputed values agree with [measurement.json](evidence/raw/final/measurement.json), `species/*/stages`, and the exact single-precision process in [check_float.ps1](evidence/raw/check_float.ps1)/[float-final.stdout.txt](evidence/raw/float-final.stdout.txt). The delegated response's192-or193 caveat is resolved here as192 for the checked path.

The calf has only baby0 and juvenile0.1; the latter remains the last stage at0.6,25,50,499 and500. Its race never switches to RM_Reefback. The mother keeps size8 at adult/elder and lifeExpectancy45; this work does not prove the fiction's literal centuries or a biological conversion between mother and reefback. No rendering was measured.

## Frozen modest hunting case

Two hypothetical ranged hunters each fire damage12, sharp AP0.15, every3 seconds, hit probability0.60, at a healthy naked target. These are illustrative inputs fixed in `design_prompt.txt` before the remedy, not a named weapon or measured pawn. For residual armor `r=max(armor−0.15,0)` in[0,1], the installed natural-armor branches give deflection probabilityr/2, half-damage probabilityr/2 and full-damage probability1−r. Hence expected remaining fraction is`1−0.75r`. Half of12 is exactly6, so the armor half-damage rounding adds no expected-value error here. Team DPS is`4.8 × fraction`.

| Target | Sharp armor | Fraction | Expected damage per landed hit | Team expected DPS | Body-part budget | Budget / DPS seconds | Expected damage in30s |
|---|---:|---:|---:|---:|---:|---:|---:|
| Young baby | .30 | .8875 | 10.65 | 4.26 | 80 | 18.78 | 127.8 |
| Young juvenile | .30 | .8875 | 10.65 | 4.26 | 192 | 45.07 | 127.8 |
| Pre-fix young juvenile | .70 | .5875 | 7.05 | 2.82 | 480 | 170.21 | 84.6 |
| Mother adult/elder | .65 | .625 | 7.50 | 3.00 | 280 | 93.33 | 90.0 |
| Open-sea adult | .70 | .5875 | 7.05 | 2.82 | 800 | 283.69 | 84.6 |

This independently reproduces [measurement.json](evidence/raw/final/measurement.json), `species/*/hunting`, and [baseline.json](evidence/raw/final/baseline.json), `RM_ReefbackJuv/hunting`, from XML and `ArmorUtility.ApplyArmor` (retained IL lines626–718). The30-second volley covers66.6% of the new juvenile Body budget, versus17.6% before,32.1% for the mother and10.6% for the adult. The juvenile budget/DPS ratio is about48.3% of the mother's and15.9% of the adult's. That supports the current **relative ranged-budget** meaning of cheap.

Contact remains dangerous. The juvenile nominal tail12/cooldown3 is much lighter than mother22/2 or adult480/8.5, but those quotients are not simulated exchanges or hard30-second upper bounds. Random melee variation alone can put a juvenile tail at14.4 before later processing. Repeated hits, vulnerable parts, armor, pursuit and retaliation defeat a guarantee of merely wounding. BodySize16 also has consequences outside the health budget, including bleeding. No pain, bleed-out, herd response, fleeing, water path, survival or realized30-second hunt was simulated.

## Controls, patch audit and preservation

I reran in-memory parent resolution and mutation cases from the actual source, rather than accepting retained pass labels. Their outputs match the raw XML fixtures in [controls.json](evidence/raw/final/controls.json):

| Control | Independently obtained result |
|---|---|
| Final young tools and graphics | Two tools16/10, two race stages and two kind graphic stages |
| Remove tools replacement flag | Four tools, including inherited480/120; unacceptable |
| Remove race-stage replacement flag | Five entries, including the parent's adult stage; unacceptable |
| Remove kind-stage replacement flag | Five graphic entries; unacceptable |
| Remove young tools entirely | Adult480/120 return, yielding240/60 and360/90 |
| Remove local health override | Base20, stage HealthScales5/12 |
| Remove local sharp override | Sharp0.70 returns |
| Replace statBases instead of merging | Inherited MoveSpeed disappears |
| Remove kind combatPower override | 2000 returns |
| Break parent name | Resolution rejects the missing parent |
| Omit health stage/race factors | Wrong Body values320 or10/24, versus80/192 |
| Substitute body size for HealthScale | Wrong6.4/16, versus2/4.8 |
| Omit melee stage factor | Wrong16/10, versus8/5 and12/7.5 |
| XML named child fields in changed defs | No duplicate named sibling fields |
| Adult and mother controls | Stage values in the table retained; mother and biome before/current bytes equal |

The synthetic translation and extra-child fixtures in `controls.json/audit_positive_fixtures` select `RM_ReefbackJuv.description` and `ControlChild` respectively. The real source scan finds no masking translation and no other RM_Reefback/RM_Reefback_Kind child. Armor boundary fixtures0,.15,1.15 correspond to remaining fractions1,1,.25; they check the formula's declared domain, not a general armor simulator.

I independently scanned **4,565 XML files** across `src/` and the installed Core, Royalty, Ideology, Biotech, Anomaly and Odyssey `Defs/` trees, with zero parse errors. Selected definitions and parent names occur only at the sources named above. Using the retained selected raw/resolved documents and .NET `XmlDocument.SelectNodes`, I evaluated **22,695 distinct XPath expressions from52,876 authored patch-operation nodes**, including source lanes excluded by the retained instrument; there were zero XPath errors. Applicable non-root hits concern recipes, FaunaNorm comfort temperature and meat products. No hit changes the selected tools, health, armor, body size, stage factors or combatPower. Root additions were inspected for the selected identities; none introduces a competing selected definition. This is an offline selected-document audit, not execution of the full active mod list.

[patch-audit.json](evidence/raw/final/patch-audit.json) independently retains473 patch-file fingerprints and raw/resolved selector results. All473 files still match their recorded hashes. In particular the calf really **is** targeted by `FaunaNorm_Law5_Tolerance.xml` and `FaunaNorm_Law6_Products.xml`; saying no patch targets it would be false. Their comfort-temperature/product edits do not invalidate these combat calculations. The inherited source comfy maximum50 can become73.3 under the applicable tolerance patch; it is not asserted to be the loaded value.

The source XML, installed body/stage inputs, assembly and selected C# snapshot fingerprints also match [inputs.json](evidence/raw/final/inputs.json). I reran [read_engine.ps1](evidence/raw/read_engine.ps1) via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <that raw script> -GameDir D:\SteamLibrary\steamapps\common\RimWorld` using reflection-only loading. Return code0, empty stderr, stdout SHA256`a7e67d0423ef5c2e91fc887ec3004af846970ae7972271d04901c97b020aec7b`, exactly equal to `engine-final.stdout.txt`. The producer's retained command in [measure-final.receipt.json](evidence/raw/measure-final.receipt.json) names the instrument, installed game, retained engine IL, before snapshots and output directory; its implementation is [measure_reefback_combat.py](../../src/RimMandrake/HugeThings/northstar/measure_reefback_combat.py). I inspected it and recomputed its arithmetic separately without executing its file-writing main. The independent computations explicitly rounded each float multiplication to float32 before ceiling.

## Design reconciliation and limits

The governing [the_miasma.md](../../design/Jawa/worldbuilding/biomes/the_miasma.md), lines97–127, promises cheap young, catastrophic parents and a dangerous water-bound resident guard. [the_grey_deep.md](../../design/Jawa/worldbuilding/biomes/the_grey_deep.md), lines101–107, locates the adult's heavy crust in its centuries at sea. The independent remedy's thin-crusted nursery prey, catastrophic adult and intermediate adult/elder mother health profile fit those constraints without shrinking the calf or replacing residents. The current fauna specification§4 correctly keeps size and health separate and narrows cheap to the explicit model. The owner’s no-growth-campaign wording in that specification's successor section remains compatible with a permanently juvenile calf. Old JSON roster notes about mother placement,50% hurt revenge and historical names are not measurements of the current XML.

I **reject** two incidental claims in `design_raw.json/result`§§1,4–5: “wounds rather than kills” is not guaranteed, and its5.6/4.4 damaging-hit counts in30 seconds count one hunter. With20 total shots the stipulated unretaliated model gives11.1/8.7 expected damaging hits. Those counts still cannot establish production manhunter probabilities. Its71%/62% figures are not accepted as either correct team-model calculations or observations. The current nursery combat paragraph makes neither claim, so these errors do not require a different stat remedy or fail the frozen L0 work. Likewise its contact totals are illustrative nominal quotients, not hard bounds. This judgment accepts the narrowed specification explicitly, not the raw response wholesale.

Mother radius16 is a configured anchor-duty radius, not a measured attack radius or global calf-death trigger. [RM_CompTerritorialAnchor.cs](../../src/RimMandrake/EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs), lines265–340, uses existing defense/tolerance and water-or-adjacent-water target rules. [RM_CompWaterLocked.cs](../../src/RimMandrake/EnvironmentalHazards/Source/RM_CompWaterLocked.cs) has a periodic recovery/backstop, not a proof that no path ever crosses land. Existing stranded-young calls can issue a mother Goto (`Miasma/Source/RM_MapComponent_YoungCall.cs`); I therefore do not infer an absolute radius16 movement cage. Existing young damage breaks its crèche record (`RM_WardenMotherSuccession.cs:163–177`), while mother death despoils her marker (`EnvironmentalHazards/Source/RM_CompCrecheMarker.cs:60–88`). None of this newly implements remote revenge for killing an ordinary calf.

**Mechanism/defect disposition:** the checked remedy adds no gameplay mechanism. It uses ordinary inherited animal melee, health, natural armor and kind metadata. The old combat/spec inversion is proven in source and corrected locally; it was never proven an actual hunting failure. The discovered swell override is inapplicable under the checked premise. Existing mother land-crossing limitations and fiction/size/age tensions remain limitations, not newly repaired or newly accepted functionality. No new retaliation, water-pathing or maturation mechanism is being accepted without proof. No new live gate is warranted by these two explicit L0 criteria.

## Frozen item criteria

- **A1 L0 — TRUE:** “Independently judged young/adult/mother combat roles, specifications and effective stage stats agree; focused XML/inheritance controls pass and roster residents remain.” Supported by the bounded specification reconciliation, complete stage table, rederived controls and before/current source comparisons above.
- **A2 L0 — TRUE:** “Exact changed XML, effective stage damage/health and the worked hunting comparison pass focused offline validation with adult controls; no actual hit, population or L4-feel acceptance is inferred from the source model.” Supported by the exact two-node change audit, production IL, float32 HP calculation, frozen-model arithmetic and adult/mother controls above. Arbitrary external mods, the active loaded game and ordinary owner-play balance remain outside this judgment.

would show: yes
