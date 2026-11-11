# Reefback nursery combat

2026-11-11 — `RIMMANDRAKE_RECONCILE_HUGETHINGS_REEFBACK_NURSERY_COMBAT`, A1L0/A2L0 only. Delegated design, not owner approval. Fresh tools-disabled Opus selected KEEP for a local young-only profile after receiving exact source and a hunting model fixed before tuning. Brief, unedited result and process receipt: `whittle/ht-reefback-combat/evidence/design_prompt.txt`, `design_raw.json`, `design_call.json` (rc0). Final independent Codex judgment: `whittle/ht-reefback-combat/JUDGE.md`.

The young reefback is thin-crusted nursery prey relative to its open-sea adult, whose nominal tail sweep is catastrophic at contact. The warden mother remains a dangerous resident guard with her existing water and anchor constraints. “Cheap to hunt” describes the relative ranged damage budget below; contact can still injure or kill, and multiple young can retaliate. There is no new mother response to killing a calf outside her existing target rules. Size16 exceeds the mother's8; size and damage are different quantities. No resident is removed to resolve that tension.

Only `RM_ReefbackJuv` changes in `TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml`: tools replace the inherited list with powers16/10, cooldowns3/2.5 seconds, original linked groups and bulk chanceFactor0.3; baseHealthScale8; armor blunt/sharp/heat0.25/0.30/0.30; kind combatPower150; description explains the thin crust. The adult retains powers480/120, cooldowns8.5/6, health20, armor0.60/0.70/0.75 and kind power2000. Mother retains powers22/18, cooldowns2/2.6, health7, armor blunt/sharp0.55/0.65 and kind power1400. Her elder factors default to1. combatPower is a generation-cost profile (`PawnGenOption.Cost`), not a damage multiplier.

| Race/stage | Size | HealthScale (decimal) | Nominal tool damage | Body / brain / heart max health |
|---|---:|---:|---:|---:|
| Young baby | 6.4 | 2 | 8 / 5 | 80 / 20 / 30 |
| Young juvenile, final | 16 | 4.8 | 12 / 7.5 | 192 / 48 / 72 |
| Adult race baby, control | 6.4 | 5 | 240 / 60 | 200 / 50 / 75 |
| Adult race juvenile, control | 16 | 12 | 360 / 90 | 480 / 120 / 180 |
| Adult race adult | 32 | 20 | 480 / 120 | 800 / 200 / 300 |
| Mother baby, control | 1.6 | 1.75 | 11 / 9 | 70 / 18 / 27 |
| Mother juvenile, control | 4 | 4.2 | 16.5 / 13.5 | 169 / 43 / 64 |
| Mother adult / elder | 8 | 7 | 22 / 18 | 280 / 70 / 105 |

Installed Core factors for baby/juvenile are body0.2/0.5, health0.25/0.6 and melee0.5/0.75. Installed engine IL independently establishes `HealthScale = stage.healthScaleFactor * race.baseHealthScale`, and part health `CeilToInt(part.hitPoints * HealthScale)`. Pinniped's core part is Body, base40; Brain10 and Heart15 are additional controls. Float32 arithmetic matters: young juvenile HealthScale is4.800000190734863 (Body192), mother juvenile4.200000286102295 (Body169, rather than decimal168). Damage is nominal, assuming healthy linked natural parts and pawn MeleeDamageFactor1, before target armor and other modifiers. The engine also consumes part efficiency and the pawn damage stat; the model does not suppress them in play.

Two hypothetical modest ranged hunters each fire damage12, sharp penetration0.15, once per3 seconds at hit probability0.60. These are illustrative inputs, not a named weapon or measured pawn. Naked-target residual armor `r=max(sharpArmor−0.15,0)` lies in[0,1]. Engine natural armor deflects with probability r/2, halves with probability r/2, and otherwise passes full damage. Expected landed damage is `12*(1−0.75*r)`; team DPS is `4.8*(1−0.75*r)`. The half branch changes damage type to blunt. The common Body-part budget is not whole-pawn HP.

| Target | Expected landed damage | Team DPS | Expected damage in30s | Body budget / DPS (s) |
|---|---:|---:|---:|---:|
| Young baby | 10.65 | 4.26 | 127.8 | 18.7793 |
| Young final juvenile | 10.65 | 4.26 | 127.8 | 45.0704 |
| Before-fix final juvenile | 7.05 | 2.82 | 84.6 | 170.2128 |
| Mother adult/elder | 7.50 | 3.00 | 90 | 93.3333 |
| Adult reefback | 7.05 | 2.82 | 84.6 | 283.6879 |

Thus the juvenile's normalized budget is about48% of the mother's and16% of the adult's; the30s volley consumes66.56%,32.14% and10.58% of their respective Body budgets. These are damage-budget comparisons, never downing/kill-time predictions. Firing assumes uninterrupted access: no contact time, chase, water movement, fleeing, cover, pain, random hit locations, bleed-out, herd revenge or hunter survival is simulated. Inherited manhunter-on-damage0.2 remains a source parameter; no per-hit independent probability or live turn rate is claimed. A 12-damage tail can accumulate serious wounds; “wounds rather than kills” is not a guarantee. No actual hits, population, deployment, flight, art or L4-feel acceptance follows.

The two-stage young race remains permanently young: baby minAge0 and final juvenile0.1, no automatic conversion into the adult species. Miasma0.15, Grey Sea adult0.005, mother source/comps, young sizes6.4/16, art/draw sizes, group2–3 and ecosystem weight4 are preserved. Density6.5 is a different field and supplies no population comparison. The lifecycle is retained as established design/wiring, without claiming transport or realized population outcomes. `the_grey_sea.md` is absent; the actual roster and `the_grey_deep.md` supply the current Grey Sea context. The frozen Miasma sheet and owner answers remain unchanged.

Reproduce with `python3 src/RimMandrake/HugeThings/northstar/measure_reefback_combat.py --game-dir <installed-game-root> --engine-il <fresh-selected-IL> --baseline-root <pre-edit-source-tree> --out <output-directory>`. Windows PowerShell on PATH supplies offline .NET XPath evaluation; no game assembly is executed. Final inputs, hashes, raw/resolved XML, before comparison, mutant fixtures, patch audit and actual process receipts are under `whittle/ht-reefback-combat/evidence/raw/`. The audit selects repository patches against raw and resolved source, outside excluded lanes; it does not simulate load order or external mod patches/settings. Relevant hits add products, temperature or acoustic payload, not these combat/stage values. Focused controls reject appended tools/stages, lost inherited stats, missing health/armor/profile overrides and broken parents; they retain adult/mother and linked-body controls. No other repository reefback descendants or young description translations were found in the bounded audit.
