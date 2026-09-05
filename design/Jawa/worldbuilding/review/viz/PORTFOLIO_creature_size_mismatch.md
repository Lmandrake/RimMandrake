# Visual portfolio — creature size mismatch (bodySize vs drawSize)

**Built 2026-09-05** by `design/Jawa/worldbuilding/review/gen_creature_size_portfolio.py`
(MandrakeVisualize stack: `visual-portfolio` → `visual-critic` → `visual-intent` /
`visual-encoding` / `visual-composition` / `visual-render-qa` / `scientific-visualization`).
Data: `creature_register_rows.json`, 1,165 rows, 595-mod def dump captured 2026-09-05.

> ⚠️ The skill's registry files (`principles/analytical_questions.yaml`,
> `evaluation/PORTFOLIO_RUBRIC.md`) are **not present on disk** — only each skill's
> `SKILL.md`. Question ids below are the FT-Visual-Vocabulary spine ids named in
> `visual-intent`'s intent→family table and in `visual-portfolio`'s procedure text.
> Registry-integrity could not be machine-checked.

---

## decision_frame

**The decision (set by the parent, used verbatim as the Coverage anchor):**
> Which creatures need intervention, and is the defect **systematic by provenance**
> (a mod ships a whole block wrong) or **scattered per-creature**? It decides the fix
> strategy: block-level edits (cheap) vs creature-by-creature (expensive).

Decision-relevant questions, written down **before** selection:
1. Does the population obey the engine's own size law at all, and how big is the defect? *(validity of the whole measure + scale of the problem)*
2. Is the deviation concentrated in particular source mods? *(the decision itself — most decision-relevant)*
3. Would a single block-level multiplier actually fix a mod's creatures, or only shift them? *(the cost half of the decision)*
4. Which specific creatures need work, with the numbers to act on? *(the deliverable)*
5. How much of the apparent problem is already cut and therefore not work at all?

Q3 and Q5 are folded into members 2 and 3 as encoded layers rather than given slots
of their own — they are qualifiers on Q2/Q4, not separate analytical questions.

---

## question_slate (supportable questions, after the measure-comparability check)

| id | supportable? | why |
|---|---|---|
| **RELATIONSHIP** (correlation) | ✅ | two quantitative fields, n=892 live; the reference law is measured, not fitted to these points |
| **COMPARISON_ACROSS_GROUPS** (distribution by category) | ✅ | 52 source mods, 26 with n≥6 live; measure is a normalized ratio |
| **DEVIATION / RANKING** | ✅ | signed departure from a meaningful reference (1.0×), orderable |
| DISTRIBUTION (pooled histogram of ratio) | ⚠️ dropped | dominated — member 2 shows the same distribution *disaggregated by mod*, which is strictly more informative and is required anyway by SCI-07 |
| MAGNITUDE / PART_TO_WHOLE | ⚠️ dropped | "167 of 892 out of band" is one number; it is a caption, not a figure |
| CHANGE_OVER_TIME | ❌ | no time field |
| SPATIAL | ❌ | biome membership is categorical set-membership, not geography |
| FLOW | ❌ | no edges |
| UNCERTAINTY | — | cross-cutting overlay (the vanilla band is drawn on every member), never a standalone slot |

### Measure-comparability record (MUST, extends SCI-06)

- **Measure:** `mismatch = max(drawSize) / (1.995 × bodySize^0.375)`.
- **Common support:** the denominator is **RimWorld's own fitted law** (n=66 vanilla
  animals + mechanoids, R²=0.71, from `creature_size_model.md` §2), so vanilla's
  deliberate small-animal inflation (~6× at bodySize 0.2, converging to ~1× above 2.5)
  is *divided out* — a raw `drawSize/bodySize` would not have been comparable across
  the mass range, and was rejected.
- **Residual drift verified, not assumed:** median ratio across bodySize octiles is
  1.15 → 0.98 → 0.98 → 1.00 → 1.08 → 1.07 → 1.09 → 1.21. All inside the vanilla band,
  so ratios ARE comparable across the mass range. Stated on every figure.
- **Simpson's-paradox / aggregation check (SCI-07, gate G13):** a mod's median could be
  an artefact of which mass range that mod populates. Checked by splitting each mod at
  its own median mass: Vanilla Vehicles Expanded 1.72× / 1.59×, Biomes! Caverns
  0.85× / 0.94×, Alpha Animals 1.36× / 1.08×, Core 1.05× / 1.01×. Offsets survive the
  split → they are authoring choices, not composition artefacts. Member 2 additionally
  plots **every creature as a point**, so no pooled summary stands alone.
- **Exclusions, disclosed on every figure, never silent:**
  - 2 creatures have no `bodySize` and therefore **no ratio at all** — `RUT_LongHunger`,
    `SandWorm_Thing` (C#-driven specials).
  - `VGE_Astronaut` — humanlike-proportioned mech, the known false positive of the
    animal law; excluded from the live pool and named on the figures.
  - No `Humanlike`-intelligence rows exist in this register, so the humanlike exclusion
    is otherwise vacuous here.
  - **Vehicles (35)** are `ToolUser` and were **not** in vanilla's fitted population.
    They are *shown with a distinct open-square marker and disclosed*, not dropped —
    dropping them would have hidden the single worst offender (Balloon, 4.11×).
  - **CUT creatures (270)** are excluded from the block statistics and the worklist —
    a creature Cherry Picker already removes needs no intervention — but are drawn as
    a faint ghost layer in member 1 so the reader sees what was dropped.

---

## candidate_views → member_case_files

### Member 1 — `fig1_size_law_scatter.png` / `.svg`
- **question id:** RELATIONSHIP
- **intent record:** takeaway "81% of live modded creatures obey the engine's own size
  law; the defect is a minority and it runs in both directions" · audience: owner,
  domain-expert, high numeracy · medium: technical_report · reader task: correlate ·
  candidate families: scatter (log-log) vs binned-residual plot → scatter wins, it keeps
  every creature visible and shows the *absolute* cell sizes the ratio throws away.
- **encoding table:** bodySize → x position (log) · drawSize → y position (log)
  *(both accuracy-critical → position, ENC-01)* · in-band/oversize/undersize → hue **and
  marker shape** ●/▲/▼ (ACCESS-01: never colour alone) · vehicle → open square outline
  (redundant with hue) · cut → low-contrast open ring (context layer, HIER-04) ·
  vanilla law → black reference line, vanilla scatter band → light fill.
  No bars → ENC-02 n/a; log axes disclosed in-figure (UNC-01 surfaced, not silent).
- **fidelity record:** provenance = measured (def dump) · transform = log-log, disclosed ·
  the drawn line is vanilla's **measured** law, NOT a fit to these points — this is the
  SCI-07 discipline: no pooled fit over the modded population is drawn or implied.
- **qa_report:** hard gates pass. Two repair rounds: annotation overprints (locusts/small
  butterflies, catalope/catchicken, bloodrop larvae/moss grub) merged into single labels
  with leader lines and white haloes; log minor-tick labels suppressed; footer clipping
  fixed by enlarging the canvas. Read-back matches the intent takeaway.
- **verdict: SHIP**

### Member 2 — `fig2_mismatch_by_mod.png` / `.svg`
- **question id:** COMPARISON_ACROSS_GROUPS
- **intent record:** takeaway "provenance explains most of it: whole mods sit off-centre,
  and for six of them one block edit clears most of the damage — but not for all" ·
  reader task: compare distributions across groups + rank · medium: technical_report.
- **encoding table:** mismatch ratio → x position (log, common axis for all mods,
  ENC-05) · mod → y category, **sorted by median** · every creature → a jittered point
  (SCI-01: raw distribution shown, not just a summary) · IQR → a line, median → a tick ·
  right panel: block-fix efficacy → bar length **anchored at zero** (ENC-02) · block vs
  scattered → hue **plus** the legend's own wording and the count column (ACCESS-01).
- **fidelity record:** the right-panel efficacy is a *counterfactual computed from the
  data* — "how many of this mod's out-of-band creatures return to band if the whole mod
  is multiplied by 1/median" — labelled as such. Efficacy is suppressed and replaced by
  "too few out of band to characterise" where n_out < 3 (a percentage on a denominator of
  1–2 is noise), and by "a block edit would make it worse" where it is negative. This
  replaced the first draft, which printed −67% / −100% on denominators of 3 and 1.
- **qa_report:** hard gates pass. Repairs: clipped y-label (Jurassic) fixed; the legend
  was sitting on top of the Biotech bar → moved above the panel; count labels were
  painted inside variable-coloured bars → moved to a dedicated gutter; log minor-tick
  labels collided with the major ones → suppressed; footer wrapped, no longer clipped.
  **Title claim-frame check (SCI-06/G12):** the first draft's title asserted "The defect
  IS systematic by provenance" — the figure shows it is systematic for *some* mods and
  scattered for others. Retitled to the frame the marks actually encode.
- **verdict: SHIP**

### Member 3 — `fig3_worklist.png` / `.svg`
- **question id:** DEVIATION (ranking of signed departure)
- **intent record:** takeaway "here are the 32 live creatures furthest off the law, with
  the numbers, tagged by which fix is cheaper" · reader task: rank + act · medium:
  technical_report / worklist.
- **encoding table:** mismatch ratio → x position (log) with stems from **1.0×**, the
  meaningful reference for a ratio · creature → y category, sorted by ratio · direction →
  hue + stem side · fix strategy → marker ring hue **plus an explicit `[BLOCK FIX]` /
  `[hand fix]` text tag on every row** (ACCESS-01, and it survives grayscale) ·
  bodySize and drawSize printed verbatim in each row label (ANNO-05: the acting number is
  on the figure, not in a lookup).
- **fidelity record:** ranked by |log ratio| so a 0.44× undersize and a 2.3× oversize rank
  on the same footing — a raw-difference ranking would have buried every undersize case.
  The figure states it diagnoses and does not prescribe: which field to edit (`bodySize`
  = mass/yield/haul/shootability, or `drawSize` = the sprite only) is a per-creature
  design call, per `creature_size_model.md` §3.
- **qa_report:** hard gates pass. Repairs: log minor-tick label collisions suppressed;
  right-edge clipping of the axis label and footer fixed; colour-only fix-strategy coding
  replaced by the text tags above.
- **verdict: SHIP**

---

## valid_pool
All three candidates carry a `visual-critic` SHIP verdict. No candidate was dropped for
invalidity; two candidate *questions* (DISTRIBUTION, MAGNITUDE) were dropped for
domination and for being a caption rather than a figure.

## selection
Greedy, coverage-first (MMR-style), against the five decision-relevant questions:
1. **Member 2** first — it answers the stated decision directly (Q2 + Q3). Highest coverage.
2. **Member 3** next — adds Q4 (the actionable list) and Q5 (what is already cut), which
   member 2 cannot carry at creature granularity.
3. **Member 1** last — adds Q1: it is the only member that establishes the *measure itself*
   is sound (the population really does track the law, so the ratio is meaningful) and the
   only one showing absolute cell sizes.

Pairwise-distinct primary question ids: RELATIONSHIP / COMPARISON_ACROSS_GROUPS / DEVIATION. ✅
No fourth member: the remaining supportable questions are dominated. Three is the set the
decision needs, not a quota.

---

## tradeoff_cards

### Card 1 — the law scatter
- **Question answered:** RELATIONSHIP.
- **Encoding & why:** log-log scatter; both fields are accuracy-critical, so both go on
  position, the highest-precision channel. Log-log turns the power law into a straight
  reference line a reader can eyeball residuals against.
- **Reveals that the others don't:** that the ratio measure is *legitimate at all* — 81%
  of live creatures fall inside vanilla's own scatter band, so the register is not
  globally broken and the mismatch flag is picking out real outliers rather than an
  artefact of the law. It is also the only view showing absolute size (a 15-cell Balloon
  next to a 0.8-cell grub) and the only one showing the 270 already-cut creatures.
- **Hides / can mislead:** provenance is invisible — every point looks independent, so a
  reader would conclude "scattered" from this figure alone, which is exactly wrong. Dense
  overplotting in the 1–4 cell region hides how many creatures sit there.
- **Best audience / medium:** analyst, on a page or screen. Too dense for a projected slide.
- **Gates cleared / stressed:** ENC-01, ACCESS-01/05, SCI-01, SCI-03, UNC-03, ANNO-03/05/06.
  *Stressed:* PERC-02 — marks touch in the dense core; mitigated with alpha and a ghost
  layer, but individual mid-population creatures are not separable.

### Card 2 — mismatch by source mod
- **Question answered:** COMPARISON_ACROSS_GROUPS.
- **Encoding & why:** one shared log axis so mods are directly comparable (ENC-05); every
  creature drawn as a point, because a median alone would have been exactly the pooled
  summary SCI-07 forbids; a zero-anchored bar panel for the block-fix counterfactual.
- **Reveals that the others don't:** **the answer to the decision.** Whole mods sit off
  centre, and the second panel separates the two cases the owner is choosing between —
  a mod whose creatures are uniformly shifted (one edit) from a mod whose creatures are
  individually wrong (per-creature work). Nothing else in the set can distinguish those.
- **Hides / can mislead:** it is a *live-only, n≥6* view — 26 mods of 52; small mods are
  absent. It also cannot tell you which creature is which, and the counterfactual assumes
  a mod-wide multiplier is even an acceptable edit (it changes mass, yield and haul if
  applied to `bodySize`).
- **Best audience / medium:** the decision-maker. This is the one figure to read if only
  one is read.
- **Gates cleared / stressed:** ENC-02 (bars at zero), ENC-05, SCI-01, **SCI-07** (raw
  points + confound split disclosed), **SCI-06** (title reframed to match the marks),
  ACCESS-01, ANNO-04/05/06/07. *Stressed:* HIER-01 — two panels compete slightly; the
  left panel is given 2.5× the width to keep primacy.

### Card 3 — the worklist
- **Question answered:** DEVIATION / RANKING.
- **Encoding & why:** diverging lollipop from 1.0× on a log axis, so equal stem lengths are
  equal ratios in both directions; the acting numbers are printed on each row.
- **Reveals that the others don't:** the per-creature numbers to actually edit —
  `bodySize` and `drawSize` verbatim, ranked so undersize and oversize compete fairly —
  and, per row, which of the two fix strategies applies. It is the only member that is a
  work order rather than an analysis.
- **Hides / can mislead:** it is a **top-32 crop of 167** live out-of-band creatures, so it
  understates the volume of work; and ranking by |log ratio| deliberately elevates
  small-mass creatures whose absolute pixel error is tiny (the 0.50× pupae are 1 cell
  drawn where 2 were implied — visually minor, mechanically odd).
- **Best audience / medium:** whoever executes the fix. Prints well; readable as a table.
- **Gates cleared / stressed:** ENC-01, ACCESS-01 (text tags, not colour alone), SCI-02,
  ANNO-02/03/05/06/07, UNC-03. *Stressed:* ANNO-01 — 32 direct labels is at the density
  limit for a single-axis figure.

---

## portfolio_score (4-axis, per `visual-portfolio` §7)

| axis | weight | score | reasoning |
|---|---|---|---|
| **1 — Validity floor** | pass/fail | **PASS** | all three carry a `visual-critic` SHIP verdict; every hard gate passes after two repair rounds; the comparability basis, every exclusion, and the aggregation confound are disclosed on each figure |
| **2 — Diversity** | 40 | **35** | three pairwise-distinct question ids spanning relationship / group-comparison / deviation. Deducted 5: all three ride the *same derived measure*, so they are diverse in question but not in variable. |
| **3 — Coverage** | 30 | **28** | the most decision-relevant question owns the strongest member, and the cost half (block-fix efficacy) and the already-cut qualifier are both encoded. Deducted 2: mods with n<6 are uncharacterised, so provenance coverage is 26 of 52 mods (though 96% of live creatures). |
| **4 — Contribution** | 30 | **27** | every card's "reveals" is non-empty and materially unique; each names a real cost. Deducted 3: member 1's contribution is partly *methodological* (it validates the measure) rather than decision-changing on its own. |
| **total** | 100 | **90** | |

## verdict

**SHIP — 3 members.** No graceful degradation needed; the third member earns its slot on
Q1 (measure validity + absolute scale) rather than padding.

---

## The answer to the decision

**Both — and the split is now measurable.** Of the 892 live (uncut) creatures, **167 are
out of vanilla's band**; within the 26 characterisable mod blocks, 160 are out of band and
**a single per-mod multiplier would return 67 of them (42%), leaving 93 that need
individual edits.**

Systematic blocks (block edit is the cheap right answer):

| mod | n live | median | out of band | one block edit fixes |
|---|---|---|---|---|
| Vanilla Vehicles Expanded | 23 | **1.71×** | 17 | **88%** |
| Alpha Animals | 135 | 1.16× | 25 | **68%** |
| Biotech | 18 | **0.75×** | 6 | **100%** |
| Caravan Adventures | 6 | **2.10×** | 5 | 80% |
| Horrors (Continued) | 6 | 1.27× | 3 | 67% |
| Biomes! Polluted Lands | 37 | 0.94× | 5 | 60% |

Scattered (per-creature work, a block edit barely helps):

| mod | n live | median | out of band | one block edit fixes |
|---|---|---|---|---|
| **Biomes! Caverns** | 89 | 0.87× | **27** | **7%** |
| Vanilla Genetics Expanded | 93 | 1.16× | 16 | 38% |
| Star Wars Animal Collection | 160 | 1.05× | 14 | 14% |
| Jurassic Rimworld (Continued) | 28 | 1.29× | 11 | 27% |
| Alpha Mechs | 27 | 1.04× | 9 | 22% |
| Alpha Vehicles - Neolithic | 12 | **1.80×** | 9 | 44% |

**Two findings that change the plan:**

1. **The prior evidence was measured on a population that is mostly already cut.** The
   Jurassic dinosaur block was cited at 2.5–2.9× too big — but only **28 of its 131**
   creatures are live; Cherry Picker already removes the rest. Of the 232 out-of-band
   creatures in the register, **65 are already cut**. Ranking mods on the full register
   (Jurassic median 1.37×, n=131) is a materially different — and wrong — worklist from
   ranking them on what the game actually loads.
2. **The heaviest single target is a mod nobody flagged: Biomes! Caverns.** 27 live
   out-of-band creatures, more than any other mod, and it is the one block a cheap fix
   will *not* touch (7%). Its defect is bimodal, not a shift: 7 pupae all sit at exactly
   `bodySize 1.0 → drawSize 1.0` (0.50×) while `chem snail` is 2.83× the other way. The
   pupae are a *sub-block* — one shared life-stage `drawSize` — so they are cheap to fix
   as a group even though the mod as a whole is not.
