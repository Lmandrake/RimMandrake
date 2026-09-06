# Visual portfolio — creature DISTRIBUTION analysis (economy · lethality · biome law · dominance · husbandry)

**Built 2026-09-05** by `design/Jawa/worldbuilding/review/gen_creature_distribution_portfolio.py`
(MandrakeVisuals stack: visual-intent → visual-portfolio → visual-encoding /
visual-composition / scientific-visualization → visual-critic / visual-render-qa).
Companion to `PORTFOLIO_creature_size_mismatch.md` (figs 1–3, the drawSize-vs-bodySize
question — NOT redone here; its corrected live-only worklist stands). This portfolio
owns **figs 4–8** and the interactive explorer.

Data: `creature_register_rows.json`, 1,165 rows, 595-mod dump captured 2026-09-05.
**Live** everywhere below = not Cherry-Picker cut, not commonality-zeroed, not
modDropped: **895 of 1,165 rows (MEASURED)**. Cut 270, zeroed 6 (all 6 also cut).
Kinds (live): animal 583 · insectoid 184 · mechanoid 64 · vehicle 35 · entity 14 ·
dryad 13 · leviathan 2. `statsResolved` false on 2 (RUT_LongHunger, SandWorm_Thing) —
those rows are UNMEASURED for every stat axis and drop out of the figures.

---

## decision_frame

**The decision:** the renormalization pass (doctrine: literal 1:1 sizes, mass-scaled
health/damage, explicit yields) is about to move `bodySize` on hundreds of creatures.
**What must be renormalized deliberately, what is already law-governed, and which
population does each biome actually need once the sheets' laws bind?**

Decision-relevant questions, written before selection:
1. Is the YIELD economy law-governed today, and who escapes? (bodySize renorm moves
   meat quadratically — every escape must be known before the pass)
2. How much of the CASUAL-LETHALITY law (Law 3, K=12–15) is already deployed, and
   where is the second manifest wave? (validation of beastnorm + its worklist)
3. How far is the current fauna assignment from the biome sheets' hard bans? (the
   curation workload the sheets created)
4. Which creatures will dominate every biome regardless of curation? (ubiquity)
5. What does the husbandry parameter space look like? (wildness × trainability)

Q1–Q3 are the scored portfolio (distinct question ids); Q4–Q5 ship as labeled
supplementary exploration figures — honesty over quota, and they feed the explorer.

## question_slate

| id | member | supportable? |
|---|---|---|
| **RELATIONSHIP** (yield vs size, two reference laws) | fig4 | ✅ measured stat + measured laws (MegafaunaYield.xml read directly) |
| **COMPARISON_ACROSS_GROUPS** (K coefficient by mod) | fig5 | ✅ same derived measure, common denominator (÷bodySize), per-mod strips |
| **DEVIATION** (fauna vs sheet law, per biome) | fig6 | ✅ sheet bans are written checkable; thresholds stated where the sheet gives prose |
| MAGNITUDE/ubiquity (spread × commonality) | fig7 (supplementary) | ✅ but off the renorm decision — curation aid |
| DISTRIBUTION (husbandry cross-tab) | fig8 (supplementary) | ✅ but descriptive, no current decision hangs on it |
| CHANGE_OVER_TIME / FLOW / SPATIAL | — | ❌ no time field, no edges, set-membership not geography |

Measure-comparability: fig4 classifies by PROVENANCE (`meatStatBase` None = engine
default = conforms by construction), not by naive tolerance — a first draft that
tolerance-tested everything misclassified the sub-kink small creatures and was
repaired. fig5's K = bestHit ÷ bodySize shares one denominator across all mods;
mods with n<8 are pooled and labeled. fig6 weights markers by spawn commonality
(area ∝ √commonality, disclosed) so a comm-0.8 violator outshouts a comm-0.001 one.

---

## The findings (all MEASURED, live population)

### F1 — Two meat-yield laws coexist, and our own biggest animals are on the wrong side (fig4)
- Above bodySize 1.0, **400 creatures** carry an authored base equal to the doctrine
  law (140·bs → resolved 140·bs², the megafauna economy) — MegafaunaYield.xml landed.
- **14 big creatures are still on the engine's linear default** because the patch
  generator never included their mods: **all 12 `RimMandrake - SW Sea Beasts`**
  (RSW_Lanternwhale bs 40 → 5,600 meat where the law says 224,000; RSW_Starmaw 36;
  RSW_Reefback 32; RSW_ElderSando 20; RSW_SandoAquaMonster 14; RSW_StormSando 12; +6
  smaller) plus **ThrumbaToad** (GRiNDTerra, bs 3) and **DA_Taraal** (Dark Ages, bs 2.5).
  A bs-40 whale yielding less than a conforming bs-16 land beast (GR_Paraceramuffalo,
  35,840) is either the sanest yield cap on the planet or an omission — **owner call
  needed**: if the linear whales are intended, record them as the stated cap the
  doctrine already demands; if not, add the mod to `gen_megafauna_yield.py`.
- **16 authored escapes match neither law.** All explainable but two:
  Anomaly's 5 entities at exactly HALF yield (intentional horror-economy),
  6 small-critter downtunes (Little Critters ×3, GR_Manbear/Manalope, AA_PebbleMit,
  BMT_PustuleHornet, JRWProtovermes, AM_UnshackledDryad ~flat) — and the two worth a
  look: **Zakkeg** (bs 8.2, authored 700 base → 5,740; neither law) and
  **AA_Behemoth** (bs 32, 32,000 meat ≈ the game's second-largest yield, q=0.22 of law).
- **57 flesh creatures are authored unbutcherable** (explicit MeatAmount 0): AA 21,
  VGE 18, Outer Rim Droid Depot 8 (animal-classed droids — correctly meatless), plus
  goo/energy exotics. Mostly intentional; worth one owner skim since renorm sets
  yields explicitly anyway.
- Dryads: 13 live, meat ≈ 3.7 flat (wooden — conforms to concept, not to the curve).
- Small side is healthy: engine-default median q = 1.000 for 0.286 ≤ bs ≤ 1;
  vanilla's postProcessCurve inflates below the 0.286 kink (measured q 1.11 @ bs
  0.18, 1.48 @ bs 0.1) — renorm must not "fix" that inflation, it is the engine's own.
- 🔴 **Renorm sensitivity:** with yields quadratic in bs, a ×2 size correction is a
  ×4 meat correction. The doctrine's rule (explicit per-creature yields with a stated
  cap) is not optional bookkeeping — fig4 is the before-photo to re-shoot after the pass.

### F2 — The K=15 lethality pass landed exactly where it was aimed, and nowhere else (fig5)
Live flesh with bodySize ≥ 1 and melee tools: **n=496**. In the Law-3 band (12–15.5):
**141**. Below: **337**. Above: 18.
- **SW Animal Collection 104/105 in band (99%), RSW Sea Beasts 12/12 (100%)** — the
  `mandrake.rsw.beastnorm` K=15 signature, verified in data (KraytDragon teeth 180 =
  15×12, GreaterKrayt 225 = 15×15).
- Everyone else still hits vanilla-soft: Alpha Animals median K 8.0 (17% in band,
  n=89), VGE 6.7 (n=71), Biomes! Caverns 5.5 (n=48), Jurassic 4.7 (n=27, 0%),
  Core 6.5, VFE-Insectoids 6.7, Dark Ages 7.9, Megafauna 5.2, Mythic Ages 7.0.
- **The second-wave worklist, by size of the offender:** AA_Behemoth (bs 32, best hit
  72 → K 2.3), GR_ArchotechCentipede (bs 20, hit 200), **GR_Paraceramuffalo (bs 16,
  best hit 17, K≈1.1 — the game's biggest meat yield defended like a housecat: the
  meat-piñata problem in one row)**, AA_SummitCrab (15/40), GR_Mechamuffalo (13/6!),
  GR_Mechathrumbo (10/30), GR_Thrumffalo (8.4/29), BMT_Thrumbungus (8.2/28).
- Above-band outliers to sanity-check when their mods are normalized: JOE_Nautilant
  K=102 (bs 8.2, hit 833 — Cephaloids boss), JOE_Cephalope K=53, RG_Rimclaw K=32.
- ⚠️ Caveat: K uses max single tool power; DPS/cooldown shape (Law 3's sublinear
  half) is not tested here — a quicktest instrument, not this register, owns that.

### F3 — The biome sheets' bans vs the actual fauna: the curation gap is the majority of each roster (fig6)
The sheets are the TARGET (authored 2026-09-05); the mod-assigned fauna predates
them. These are workloads, not bugs:
- **Desert** (`Desert`, law: no pursuit predators): 172 live residents, **110
  predators (64%), 52 pursuit-capable** (predator special + moveSpeed ≥ 4.5 — stated
  proxy). Top by spawn weight: Wraid (comm 0.8, spd 5), Scurrier (0.8), Gutkurr
  (0.8), Meganeura (0.7, spd 8!), then GR_Manwolf, JOE_Cephalope (spd 8.8), Nexu,
  AA_SandLion. The desert as assigned is a chase arena.
- **Arid shrubland** (`AridShrubland`, law: small·medium·VOID·huge): 222 residents,
  **95 in the banned large band (43%)** [bands stated: 1.5 ≤ bs ≤ 3.5]. Top by
  weight: Jamel (0.8), Dactillion (0.8), IridonianReek (0.8), Uvak (0.8), Zeer (0.8),
  Gutkurr (0.8) — the SW collection parks its whole midrange here (59 of the 95 are
  SW). Huge-young exemption UNMEASURED (no life-stage data in the register).
- **Dune sea** (`ExtremeDesert`, law: giant or grain-scale only): 116 residents,
  **88 medium (76%)** [banned band stated: 0.3–3.0]. Top: Shyrack (0.8), LavaFlea
  (0.8), Sketto (0.7), StoneCrab (0.7), BMT_Glowtail (0.7).
- Other sheet biomes (poison forest, nightside, terminator, wreck fields, fall line,
  deep desert): **UNMEASURED here** — no confirmed BiomeDef binding in the register
  (fall line is injected onto existing defs by design; the rest need a def mapping
  before their fauna bans can be linted).
- ⭐ Also measured while resolving residency: the register's biome table is still
  the mods' own default worldview — temperate forest is the most-populated biome
  (282 live residents) on a planet that has none. **Biome-side curation is the
  bigger half of the fauna work, and none of it has landed yet.**

### F4 — Ubiquity, not any single bad def, is what kills biome identity (fig7, supplementary)
**25 live creatures are both widespread (≥20 spawn biomes) and common (top ≥ 0.3)**
— 11 of them Alpha Animals (AA_PebbleMit in **45** of 52 BiomeDefs, FissionMouse/
Swarmling 40, Aerofleet 35, CrystalMit 33), plus vanilla's Rat (comm 3.0, 23
biomes), Hare, WildBoar, Boomalope, Muffalo, and SW's GraniteSlug/Mynock/Neebray/
Scavrat. Whatever the per-biome curation does, these will be the connective tissue
of every map unless their per-biome records are cut deliberately. (Spread counts all
52 registered BiomeDefs — an upper bound on campaign ubiquity, disclosed on-figure.)

### F5 — Husbandry space: taming difficulty, not trainability, is the gate (fig8, supplementary)
Live animals+insectoids with wildness: 752. The single biggest cell is
**wild(≥0.75) × Advanced-trainable: 161 creatures** — the exotic-war-beast corner
(WarWyrm, EnergySpider, VFEI2_Queen, AA_Dunealisk…). The classic farm block
(tame × None: 65 — Goat, Duck, Donkey, Gorg, Bantha-kin) is smaller than the exotic
corner. Renorm consequence: the haul-training gate (bodySize 0.40) and taming-food
scaling will move through this table when sizes go literal; re-cut fig8 after.

---

## member_case_files (condensed; one inspect-and-repair round each, verdicts on the final render)

### fig4_yield_law — RELATIONSHIP — **SHIP**
Log-log scatter (both axes accuracy-critical → position; log disclosed), the two
measured laws drawn as reference lines (never fitted), classes by provenance with
marker+hue redundancy, zero rail disclosed ("log axis cannot show zero"), every
named outlier labeled with a leader line. Repairs: tolerance→provenance
classification (the honesty fix), overlapping rail labels separated, footer wrap.
Read-back matches the intended takeaway (two laws; biggest animals on the linear one).

### fig5_lethality_by_mod — COMPARISON_ACROSS_GROUPS — **SHIP**
Per-mod jittered strips on one shared K axis (ENC-05), every creature drawn
(SCI-01), medians as ticks, Law-3 band shaded + labeled, in-band share as
zero-anchored bars in a right gutter, K>30 clipped with the clipped creatures named
on-figure. Repairs: band label moved out of title collision, gutter labels moved
inside bars, clipped-note relocated. Grayscale-safe (marker shape ▼/●/▲ carries
band position redundantly with hue).

### fig6_biome_law_gap — DEVIATION — **SHIP**
Three small multiples, each on its law's natural axis (speed for the pursuit ban,
log bodySize for the two size bans), ban regions shaded, violators = red triangles,
marker area ∝ √commonality (disclosed), stated analytic thresholds printed on-panel,
top violators labeled with commonality. The TARGET-vs-predates-it caveat and the
UNMEASURED huge-young exemption are on the figure. Repairs: annotations pinned
inside axes (ylim fixed), footer/xlabel separation, right-edge clipping.
Note: panels deliberately do NOT share an x quantity (different laws) — each panel
is self-labeled, per the render-QA small-multiples exception.

### fig7_dominance / fig8_husbandry — supplementary, not scored
Both pass the hard gates (sources, units, log disclosure, colorbar on fig8,
counts printed in cells, grayscale-monotonic map); they are exploration aids for
Q4/Q5 and the explorer covers their axes interactively.

## portfolio_score (4-axis, scored members only)

| axis | weight | score | reasoning |
|---|---|---|---|
| 1 Validity floor | pass/fail | **PASS** | all three carry SHIP after one repair round; provenance-classification fix removed the one honesty defect found |
| 2 Diversity | 40 | **36** | RELATIONSHIP / COMPARISON_ACROSS_GROUPS / DEVIATION, and unlike the size portfolio the three ride three DIFFERENT measures (meat, K, ban-membership). −4: figs 4 and 5 both condition on bodySize |
| 3 Coverage | 30 | **27** | Q1–Q3 each own a member; Q4/Q5 covered by labeled supplementaries. −3: fig6 covers only 3 of 9 sheet biomes (the rest UNMEASURED — no def binding) |
| 4 Contribution | 30 | **28** | each member's unique reveal is material (F1's unpatched-mod hole, F2's exact pass footprint, F3's per-biome workload); −2: fig6's thresholds are stated choices, not sheet numbers |
| **total** | 100 | **91** | |

---

## The interactive explorer (deliverable 3)

`design/Jawa/worldbuilding/review/viz/creature_explorer.html`
(`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\viz\creature_explorer.html`)
— generated by `gen_creature_explorer.py`, self-contained (475 KB, all 1,165 rows
embedded), offline, opens straight from disk.

- **Any-axis scatter**: 15 axes (bodySize, drawSize, healthScale, moveSpeed,
  wildness, meat, leather, armorSharp, bestHit, K=bestHit/bs, health/bs, meat/bs,
  topCommonality, biome spread, art px/cell), log toggles per axis.
- **Reference laws draw themselves** when the axis pair has one (meat: both yield
  laws; bestHit: the 12–15 band; drawSize: vanilla's 1.9·√bs).
- Color by kind / top-12 mods / cut status; filter live-only, by biome residency,
  kind, mod, text search; hover shows the creature's **actual sprite**
  (relative into `../creature_art/`) plus its stats.
- **Click collects creatures into a basket** (persisted in localStorage; "copy
  defNames JSON" button) — the deck lesson applied: the artifact the owner
  manipulates is the extraction path, so an outlier safari ends as a pasteable
  defName list for a queue item, not a memory.
- Calls made: NOT published as a claude.ai Artifact — the sprite hovers require the
  local `creature_art/` files (2,328 PNGs; embedding would blow the 16 MB artifact
  cap), and the page is a workbench next to its data, like the register sheet. Not
  a review-sheets decisions artifact either: it captures no keep/cut decisions —
  the basket is a collection aid; anything kept must be copied out (stated on-page).
- QA: JS syntax node-checked; canvas logic reviewed; not browser-rendered in this
  session (no headless browser on this box) — first-open defects, if any, are one
  generator edit away.

## Renormalization guidance (the actionable summary)

1. **Before the size pass**, rule on the 14 linear-yield big creatures (RSW Sea
   Beasts + ThrumbaToad + DA_Taraal): intended cap → record it; omission → extend
   `src/RimUtinni/Doctrine/Source/gen_megafauna_yield.py`'s mod list. Either way
   fig4 stops showing an unexplained second branch.
2. **Yields are quadratic in bs above 1.0** — any bodySize edit ≥ a few percent
   materially moves meat. The doctrine's explicit-yield manifest must be cut from
   the POST-renorm sizes, and fig4 re-rendered as the validation photo.
3. **Second beastnorm wave, ranked worklist = fig5's below-band strips**: Alpha
   Animals (89 flesh bs≥1, median K 8) and VGE (71, K 6.7) are the two biggest
   blocks; the 8 named giants (F2) are the marquee inversions; decide whether
   Core's own animals (24, K 6.5) are in scope or vanilla-sacred.
4. **Biome fauna curation is unstarted** (F3): the sheets need BiomeDef bindings
   for the remaining 6 sheet-biomes before their bans can be linted, and the three
   bindable ones each need half their roster moved or cut. The fig6 violator lists
   (top-commonality first) are the cut order.
5. **The 25 homogenizers (F4)** should be ruled on once, globally (per-biome
   commonality cuts), not rediscovered per biome.

## Lessons already filed to LESSONS_INBOX
- Provenance beats tolerance when classifying against a law (the meatStatBase-None
  population conforms by construction; tolerance-testing it manufactured 43 fake escapes).
- A doctrine patch generated per-mod (FindMod blocks) silently skips mods added
  later — our own RSW Sea Beasts never got the megafauna economy.
