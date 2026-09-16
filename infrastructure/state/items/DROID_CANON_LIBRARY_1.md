# DROID_CANON_LIBRARY_1

Broad canon index of Star Wars droids, deliberately wider than the game's current content
because the owner intends to add droids from it. Owner's ask, verbatim: *"do the same thing
for every droid type on the web we can find. We may very well add more droids to the game, so
make this search more broad and comprehensive. Include manufacturing company, typical racial
ownership, time period, etc."*

## What exists

`design/RimStarWars/canon_references/DROIDS_INDEX.md` — **1,757 droids**, eight columns, every
row carrying a source URL. QA'd once: junk rows, duplicates and malformed rows removed, and
two invented-looking fields blanked.

Measured coverage (derived by counting the table's own rows, not a naive scan):

| column | filled | |
|---|---|---|
| name | 1757 | 100% |
| continuity | 1757 | 100% |
| source URL | 1757 | 100% |
| class / role | 1577 | 89.8% |
| typical owners | 890 | 50.7% |
| manufacturer | 693 | 39.4% |
| **era** | **48** | **2.7%** |
| already in repo | 54 | 3.1% |

## 🔴 RULED — era stops at 2.7% (owner, 2026-09-15)

**Era cannot be filled from canon, and the owner accepted that rather than deriving it.**

A script fetched all 1,757 articles: 48 carry a usable era, **1,709 are confirmed blank** — no
`firstmade`, `retired`, `birth` or `death` field exists on the article — and zero errored. The
gap is in Wookieepedia, not in our extraction.

He was offered a derived-era column built from each droid's first appearance, which would have
given near-complete coverage, and **chose to stop at 2.7% instead.** So:

- ⛔ **Do not "finish" the era column.** It is not unfinished; it is complete and the field is
  genuinely absent. A future pass that fills it by inference is reversing a ruling.
- Era is honest where present and blank where canon is silent. Filtering the index by period is
  therefore not possible, and that cost was accepted knowingly.

Two traps caught during that run, worth keeping: treating the Legends continuity flag as an era
marker would have mislabelled roughly half the index, and one live wiki page really does carry
`retired=Galactic Republic` — a faction, not a date, the same defect our own earlier QA had
already fixed once.

## Chassis entries — ruled and underway

**Owner ruled 2026-09-15: entries for the 54 droids already in the repo**, not the whole index
and not a wait-for-candidates. Those 54 canon rows collapse to **25 distinct chassis** — 11
droideka variants share one sprite set, 11 B1 variants share another — so an entry covers a
**chassis** and lists the canon variants it stands for. Slugs are `droid_*`.

Two index-row pairs turned out to be **one chassis each, merged on evidence**: FX-7 with
FX-series, and MSE with MSE-6. Exactly one texture set exists in `src/` for each, and canon
treats them as line-to-member rather than rival models — the MSE *series* article's own infobox
image is a photograph of an MSE-6. The index rows were correctly left unmerged, since they
differ on owners, continuity and cost.

## Droid findings so far

Same shape as the species sweep: the defs and sprites disagree with canon.

- 🔴 **Body sizes are badly off.** DSD1 `baseBodySize` 0.7 against a canon 1.98 m tall by
  **3.05 m wide** — and its sprite's legs are far too short, so the "wide spider" read is lost
  entirely. FX-7 is 0.75 against 1.7 m. *(Body size is functional, not cosmetic, so it is
  inside the owner's clearance.)*
- **Colour is wrong and nothing can correct it.** FX-7's sprite is neutral charcoal where canon
  is steel **blue**-grey, carrying an identity white tint so no tint fixes it. MSE tints
  `RGBA(110,110,110)` mid-grey against canon **black**. ⛔ Both are cosmetic — gated.
- **Folded forms do not exist as content.** DUM pit droids have their arms truncated to stubs
  and no folded form; the droideka has no rolled-up ball. These are content gaps, not bugs.
- **MSE's top-down roof is blank**, though canon puts the order tray, sensor combs and red
  lightbar there — the only surface actually visible from above in play.

⚠️ **`Races_Primitive.xml` reuses the MSE texture, so editing that texture changes two races.**
Anyone fixing MSE art must check this first.

## 🔴 Errors in OUR index, found by writing the entries

These are defects in `DROIDS_INDEX.md` itself, not in the repo's defs — so they are ours to
fix, and they are neither cosmetic nor def changes.

1. **`:1650` maps the wrong canon droid to a repo sprite.** The row names the **T1-series
   utility droid** — 0.96 m, Duwani, a KotOR II *maintenance* droid, Legends, no faction, no
   weapons. The repo sprite is unmistakably the **T-series tactical droid**: 1.93 m, Baktoid,
   CIS, donor mod `JDS_Separatists`, matching TA-175 exactly, and whose sourced alternate name
   **is "the T-1"**. The repo label is correct; our mapping is wrong. Rows **1647/1648**, the
   correct ones, are unmapped.
2. **`:1650` is marked `canon` on an article carrying the Legends flag.** Continuity is wrong.
3. **`:1603` (ST-series, canon, Baktoid) is unmapped**, while only its Legends twin at `:1627`
   — which has a blank manufacturer — carries the chassis. Backwards.
4. **Two repo donors are absent from the index entirely:**
   `RSW_DW_Race_OuterRim_SuperTacticalDroid` and `RSW_DW_Race_OuterRim_TacticalDroid`.
5. **The continuity column is wrong on at least four rows.** B1-A, K-X12 and R-8009 are all
   marked `canon` while their articles carry the Legends flag, joining `:1650`. Of the rows
   checked closely, only AQ was graded correctly — so continuity should be treated as
   unreliable across the whole index until re-derived, not just on these four.

**GNK's two rows are correct as they stand.** Canon treats GNK power droid and GNK-series power
droid as **one droid across a continuity fork** — each article names the other in its `{{Top}}`
template, which is Wookieepedia's convention for exactly this. Both rows stay; both map to one
repo chassis.

## More droid findings

- **Scale is inconsistent rather than merely wrong**: KX is 2.16 m at `baseBodySize` 1, while
  the buzz droid is 0.25 m at 0.7. There is no shared scale rule.
- **`MoveSpeed` 2.0 is shared by the T-1 and the ST-series**, which erases canon's distinction
  that one has "more fluid motion programming".
- **"Pistoeka Sotage Droid"** — "Sabotage" is misspelled in the defName, the label *and* the
  texture filenames. ⚠️ Upstream JDS content in a generated file, so not ours to fix casually,
  and a defName change carries save risk.
- The buzz droid sits under `DW_Family_Labour` despite being a saboteur.
- **Folded forms are absent everywhere**: the Pistoeka sprite shows only the deployed form and
  the folded sphere exists nowhere on disk, matching the droideka's missing ball and DUM's
  truncated arms.

- **Colour channels wasted or misused.** GNK sets both colour channels to the same value, so
  its two-tone mask does nothing, and its indicator panel is masked black and never lights,
  though canon lights it amber, green or red. B1A is tinted pale blue-grey where all canon art
  is tan with rust-orange — and the plain B1 **in the same file** already carries the correct
  tan. The K-X12 assassin variant's photoreceptors are **magenta**, where canon is red and the
  utility variant is correctly red.
- **AQ's sprite is dark charcoal against a canon pale grey-white with teal accents**, and it has
  no mask or colour channels at all — so that one is a repaint, not a def edit.
- 🔑 **A canon trap worth knowing:** GNK's `sensor = Purple` is **conditional on Scourge
  infection.** A naive read of the infobox gives every gonk droid purple eyes.
- **Orphan art found:** `Textures/KotOR/Droid/gonk/` is referenced by no def anywhere in the
  repo — and it is **the better of the two gonk assets.** Worth wiring up rather than
  regenerating.
- **AQ carries `CompDroidDetonation` with `energyDensity 0`**, which contradicts the rule stated
  in its own rollout comment.

✅ **Genuine matches worth protecting from a future "fix":** KX's `RGBA(20,20,20)` tint;
LR-57's `MoveSpeed` 1.7 against canon "sluggish"; three photoreceptors on both super-tactical
donors; and the OuterRim super tactical droid's **three-option random palette**, which
mechanically reproduces canon's per-unit colour schemes. That last one is a genuinely good
piece of design already in the repo.

## Still open

- **Do individual droids get `description.md` entries** the way the 69 species did, and if so
  which? 1,757 is infeasible; the 54 already in the repo plus named candidates is not.
- Manufacturer at 39% and owners at 51% could both be raised from article prose rather than
  infoboxes, if either is worth the runs.
