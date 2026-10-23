# Art-eval pilot — SCORE (GPT vs Opus 5.5 vs the owner)

Scored 2026-10-23 by a BENCH helper (Opus 5.5) against `answer_key.json` (owner's 2026-10-10 sitting on
`weepingstones_sheet_2026-10-05`). Inputs: `runs/gpt/verdicts.json` (gpt-6.1-sol high, one call per subject),
`runs/opus/verdicts.json` (Opus 5.5, one agent, all 47). Verdict tables are computed by script; the
reason-match table (§2) is a manual semantic read by one scorer — treat it as one rater's judgement, not a
measurement. **N is small: 47 subjects, 18 owner REDOs. Bootstrap 95 % intervals on accuracy are ~±0.13 wide.**

**Flagged rows (8)** = every row with a caveat in the key: Boma, Dactillion, Fanback, Ollopom, Dewshrooms,
MurrinCatch (letters reconstructed; Boma/Dactillion/Fanback/Ollopom partly thumbnail-only), Tirbak (pick A has no
picture), Mirrik (CUT for a roster reason, not art). **Clean = the other 39.**

---

## 1. Verdict agreement with the owner

Baseline to beat: **always KEEP** = 28/47 (0.596) all, 22/39 (0.564) clean.

### Confusion matrices (rows = owner, columns = reviewer KEEP / REDO / CUT)

| | GPT all 47 | Opus all 47 | GPT clean 39 | Opus clean 39 |
|---|---|---|---|---|
| owner KEEP | 22 / 6 / 0 | 26 / 2 / 0 | 18 / 4 / 0 | 20 / 2 / 0 |
| owner REDO | 7 / 11 / 0 | 9 / 9 / 0 | 6 / 11 / 0 | 9 / 8 / 0 |
| owner CUT | 0 / 1 / 0 | 1 / 0 / 0 | — | — |

Neither reviewer ever said CUT (the prompts offer no CUT for art; Mirrik's CUT is a roster call).

### Headline

| measure | GPT all | Opus all | GPT clean | Opus clean |
|---|---|---|---|---|
| accuracy | 33/47 = 0.70 | 35/47 = 0.74 | 29/39 = 0.74 | 28/39 = 0.72 |
| bootstrap 95 % (all 47) | 0.57–0.83 | 0.62–0.87 | | |
| Cohen's κ | 0.39 (95 %: 0.12–0.63) | 0.44 (0.19–0.68) | 0.47 | 0.40 |
| REDO recall (his REDOs caught) | 11/18 | 9/18 | 11/17 | 8/17 |
| REDO precision (its REDOs he also REDO'd) | 11/18 | 9/11 | 11/15 | 8/10 |
| false REDOs (he kept) | 6 | 2 | 4 | 2 |

**GPT vs Opus are statistically indistinguishable on accuracy**: 6 rows only GPT got right, 8 only Opus
(McNemar exact p ≈ 0.8). They differ in *shape*: GPT is the stricter rule-applier (more REDOs, more recall,
more false alarms); Opus is lenient (high precision, half the recall).

### Letter agreement

| | GPT | Opus |
|---|---|---|
| rows both owner and reviewer KEEP (Tirbak excluded) | 22 | 25 |
| reviewer pick == his pick (strict) | 16/22 | 17/25 |
| reviewer pick ∈ his kept set (pick / variant / other slot) | 21/22 | 24/25 |
| REDO∩REDO rows: `redo_base` is a picture he retained as the base | 11/11 | 7/9 |
| GPT and Opus picked the same letter (both KEEP) | 25/25 | |

Strict misses are mostly *variant vs pick* swaps (Fanback C/B, Steamfrond B/A, Weepmat B/A — his variant
chosen as pick), one real disagreement (Dripfringe: both picked A, he picked B), and a key artefact: on the 4
catch KEEPs (Ikkal, Tarrik, Ullo, Vobbal) his "pick" is A, a Tang's **donor meat retexture**, with the catch
picture C as `keep_other_slot`. Both reviewers kept C and deleted A per the "donor is never a final keep" law.
The card does not say these rows hold two slots (meat icon + catch); that is a bundle defect, not a reviewer miss.

### Deletes (safety)

| | GPT | Opus |
|---|---|---|
| deletes on pictures he purged/rejected (recall of his 25) | 25/25 | 24/25 |
| deletes on pictures he never ruled (`not_chosen`) | 44 | 44 |
| deletes on pictures he KEPT or retained as a base | **22** | **17** |
| … of which catch-row structure (meat slot A, living reference D/C) | 11 | 13 |
| … of which flagged reconstructed rows (Boma, Dactillion, Fanback, Ollopom) | 5 | 4 |
| … of which clean flora — including 2 of his picks (Steamfrond A, Weepmat A) | **6** | **0** |

GPT deletes every non-pick by default; on flora that destroyed 4 variants he kept and 2 of his picks.
Opus put passing non-picks in `keep_also` instead.

---

## 2. Reason quality — did the reviewer find what he found? (manual, one rater)

HIT = names the same defect as his note. PARTIAL = names it but rates it minor / keeps anyway, or names half
of it. MISS = does not name it. RECONCEPT = his note replaces the brief (the art matches the def text he had
at the time); no reviewer can be expected to find it, so it is outside the denominator.

| subject | his note (defect part) | GPT says | | Opus says | |
|---|---|---|---|---|---|
| Huldu | "make more alien: an alien otter-equivalent" | "cute, recognizably Earthly otter" | HIT | "a recognisable, cute Earth otter ('must read as ALIEN')" | HIT |
| Kirruk | "Total regen… alien comb-flier, slotted trailing teeth-like combs… Quasi-avian" | "reads as an Earth raptor… redo as alien soarer with comb-slotted wings" | HIT | "plainly terran hawk… comb-tooth slotted trailing edge is only an ordinary feather fringe" | HIT |
| Loomu | "Image is too cute, make it more realistic looking and wet" | "glossy round eyes and a smiling face violate 'not cute/cartoon'" | HIT | "the south face is slightly cute; tidy… in a variant" (KEEP) | PARTIAL |
| Murrin | "Redo completely. A fast alien fish… Colorful and odd." | overhead north, baked water rings | MISS (verdict right) | "reads close to an Earth perch/sunfish — a more alien variant would suit" (KEEP) | PARTIAL |
| Ssurr | "crest-fan isn't rotating with the creature properly" | "fan spans across its body in south/north but becomes a lengthwise dorsal sail in east" | HIT | "crest-fan does not turn with the body… full wheel on south AND north and… full side-on sail on east" | HIT |
| Vellak | "Make more alien… less recognizably camel… furred snake for a neck/head" | coherent facings, KEEP | MISS | "head, neck and legs are a plain Earth camel with a sail glued on… make head, neck and gait alien (less recognisably camel)" | HIT |
| Vizhik | "Close… generate highly realistic images… Drop all this art." | overhead south/north | MISS (verdict right) | "alien and painterly" (KEEP) | MISS |
| Ambrosia | "make the art very special. Softly glowing golden fruit…" | "lily-like flowers without visible ambrosia fruit… baked rock base" | HIT | "Neither shows the ambrosia FRUIT" (KEEP, needs_human) | PARTIAL |
| HulduCatch | "Make it look like a dead one of these" | "alert, propped-up posture misses 'lying on the ground'" | HIT | "C does not match the current living Huldu art — the living art should be redone to agree with C" (KEEP) | PARTIAL |
| IvvolCatch | same | "regenerate from D [living] as a compact body lying inert with its eye-ridge closed" | HIT | "does not match the living Ivvol… redo… as the D body lying flat with the eye-ridge shut" | HIT |
| KarrekCatch | same | "compact, painterly pile" (KEEP) | MISS | "greener than the bronze living swarm; warming its palette toward D" (KEEP) | PARTIAL |
| LoomuCatch | same | "regenerate from D as a… catch lying on its side with collapsed appendages" | HIT | "the D body slumped boneless on the ground as an item" | HIT |
| MurrinCatch ⚑ | same | "realistic deep-bodied fish" (KEEP) | MISS | "neither shows the deep keel and single tall dorsal comb-fin of the living Murrin" | HIT |
| Ozhu | same | "curled as a landed catch" (KEEP) | MISS | "posed mid-swim; a… coiled-on-the-ground version would sit better" (KEEP) | PARTIAL |
| SkarrinCatch | same | "whole, curved silver catch" (KEEP) | MISS | "drift[s] from the stocky toothy living Skarrin… reads mid-leap rather than lying landed" (KEEP) | PARTIAL |
| VizhikCatch | same | "the card supplies no confirmed living-species reference" (KEEP) | MISS | "a different animal… not the wrist-thin blue eel… in the living art" | HIT |
| Skarrin | re-brief: "slender knife-like silver eel-thing with a cruel suction-like mouth" (def text says "pool fish") | silver toothy fish, KEEP | RECONCEPT | "close to an Earth predatory fish… nice-to-have" | RECONCEPT |
| Vhakk | "Drop all of this art, it's all bad… flounder × badger, eyes on stalks" (new brief) | REDO: overhead north | RECONCEPT | REDO: palette disagrees across facings | RECONCEPT |

**Tally on the 16 judgeable REDO notes:**

| | HIT | PARTIAL | MISS |
|---|---|---|---|
| GPT | 8 | 0 | 8 |
| Opus | 8 | 7 | 1 |
| either reviewer HIT | 11 | +4 PARTIAL-only | 1 (Vizhik) |

**Headline: Opus names his defect on 15 of 16 (8 fully, 7 seen but under-weighted); GPT names it on 8 of 16 and is
blind to the other 8.** Opus's errors are *severity*, GPT's are *perception*. All 7 Opus PARTIALs are KEEP
verdicts whose own note contains the defect he redid it for. The HIT/PARTIAL quotes are specific
(they name the body part or facing), not generic.

KEEP rows with an art note he still kept (not scored as errors): ColossusToad "Redo more alien… based on the
current (b) but extended" (both KEEP, neither flagged alienness — Opus argued a frog body is correct), Rockfinger
"Make this 50 % larger" (neither flagged size), and 8 flora rows "Two more variants, more realistic" (both kept the
same picture; neither asked for more variants).

---

## 3. GPT ↔ Opus and the ensemble rule

| | all 47 | clean 39 |
|---|---|---|
| GPT–Opus verdict agreement | 32/47 (κ 0.27) | 28/39 (κ 0.36) |
| **agree → auto** | 32 auto, **27 correct (0.84)** | 28 auto, 23 correct (0.82) |
| **disagree → human** | **15/47 (32 %)** | 11/39 (28 %) |
| his REDOs: auto-REDO / sent to human / silently auto-KEPT | 6 / 8 / **4** | 6 / 7 / 4 |
| + also route Opus `needs_human` | 19 to human, 28 auto, 25 correct (0.89) | 15 human, 21/24 correct |
| OR rule (either says REDO → REDO) | 22 REDO flags, 14 his REDOs (recall 14/18, precision 14/22) | 18 flags, 13 his |

The 5 auto-decided errors: **Sillik** (both REDO an owner KEEP for overhead south/north on a wall-clinger — the
prompt's no-overhead rule is stricter than he is), **Skarrin** (reconcept), and three catches both kept —
**KarrekCatch, Ozhu, SkarrinCatch**. The silent auto-KEEPs are the dangerous class: 4 of his 18 REDOs never
reach him under the agree→auto rule. Every one of the 4 is a swimmer or a catch.

---

## 4. Cost and latency

| | GPT | Opus |
|---|---|---|
| model | gpt-6.1-sol, effort high, via `gpt_consult.py` | Claude Opus 5.5, one foreground agent, no subagents |
| time | 1131 s summed over 47 calls (mean 24.1 s, median 22.7 s, max 47.6 s Sillik); 0 failures, 0 parse failures | 629 s wall for all 47 (05:23:43–05:34:12; ~13.4 s/subject) |
| parallelism | per-call; would run N-wide | sequential in one context |
| tokens | **UNMEASURED** — not recorded in `meta.json` | **UNMEASURED** — not recorded in `meta.json` |
| extra outputs | `image_seen` line per call | `seen`, `confidence`, `needs_human` per subject |

Opus confidence is weakly informative: mean 0.65 on correct rows (35) vs 0.57 on wrong (12); 6 of the 13 rows
below 0.6 are wrong. `needs_human` (8 rows) caught 4 wrong verdicts and 4 right ones.

---

## 5. Failure patterns by class

| class | n | his REDOs | GPT right | Opus right | pattern |
|---|---|---|---|---|---|
| flora/ground_cover | 3 | 0 | 3 | 3 | both fine on verdict; GPT deletes his kept variants (Verdimoss B) and his pick (Weepmat A) |
| flora/bush | 8 | 1 | 7 | 7 | GPT false REDO on Bladderquill (height vs "knee-high"); Opus keeps Ambrosia though it says "no fruit"; GPT deletes his pick Steamfrond A |
| flora/tree, special | 2 | 0 | 2 | 2 | neither picks up his "50 % larger" on Rockfinger; both pick A on Dripfringe (he picked B) |
| fauna/walker | 7 | 2 | 6 | 5 | both REDO Sillik (overhead wall-clinger he accepted); Opus false REDO on Burrak ("recognisable grizzly"); both catch Ssurr's fan |
| fauna/walker_pack | 2 | 1 | 0 | 2 | GPT misses "too camel" on Vellak and REDOs Tirbak for an east-only harness he tolerated |
| fauna/flyer | 3 | 1 (+1 CUT) | 1 | 2 | both catch Kirruk "Earth raptor"; GPT REDOs Dactillion for raised grounded wings (he kept) |
| fauna/swimmer | 7 | 5 | 6 | 3 | **Opus's worst class**: sees "Earth fish / slightly cute" and keeps (Loomu, Murrin, Vizhik); GPT gets verdicts right but on facing/overhead grounds, not his "more alien / realistic" |
| fauna/amphibious | 2 | 0 | 2 | 2 | fine (thumbnail rows) |
| item/catch | 13 | 8 | 6 | 9 | **both models' worst class**. GPT does not use the living facing set as the reference ("no confirmed living-species reference was supplied" — it was, as D); Opus compares to the living art but rates mismatch / living pose as minor. Neither knew that a catch whose living species is itself being redone must be REDO |

Two structural findings behind the catch class:
- **His 8 catch REDOs are exactly the 7 `…Catch` rows that carry a living-reference candidate, plus Ozhu**; 5 of
  those 7 living species (Huldu, Loomu, Murrin, Skarrin, Vizhik) were REDO'd in the same sitting. His note —
  "generate AFTER the source is settled" — makes the catch a *dependent* verdict: if the living row is REDO, the
  catch is REDO regardless of its picture. Counterfactual with that one rule (using the reviewer's OWN fauna
  verdicts): GPT catch recall 3/8 → 5/8; Opus 4/8 → 5/8, no new false REDOs (no KEEP catch has a REDO'd
  living row). Using his fauna verdicts it would be 6/8 for both (KarrekCatch and Ozhu still missed).
- **Opus's PARTIALs are a severity-calibration problem, not perception.** Flipping its 7 PARTIAL rows to REDO
  would give recall 16/18 — but a blunt "any criticism → REDO" rule would also flip at least Ikkal, Ullo, Tarrik,
  Duul, Dactillion and Tirbak (owner KEEPs with Opus follow-up notes). The flip has to be defect-specific.

---

## 6. Prompt improvements (for the skill)

1. **Catches are dependent verdicts.** Review living fauna first; pass each catch row its living row's verdict.
   Rule: *living row REDO → catch REDO (blocked on source)*. Mark the living-reference candidate explicitly on
   the card ("D = LIVING REFERENCE, not a candidate; never delete it"), and require the catch to read as a
   **dead** specimen of THAT body — lying, limp, eyes shut — with "mid-swim / mid-leap / propped up / hanging in
   water" as a blocking `CATCH_POSE` reason code, and "differs from the living art" as blocking `CATCH_WRONG`.
2. **Make "reads as Earth X" blocking for invented creatures, with a test.** Both his top note families are
   "more alien / less recognisably <Earth animal>" and "too cute". Add: *"Name the Earth animal it most resembles.
   If a stranger would name it in one word (otter, camel, hawk, perch, octopus), verdict REDO with
   STYLE_EARTHLY — not a variant note."* Targets Opus's Loomu/Murrin PARTIALs and GPT's Vellak miss. Cost, from
   these outputs: it would also flip owner KEEPs Burrak ("grizzly") and Vobbal ("Earth octopus") — exempt
   subjects whose def text names the Earth body (octopus-like, frog). Same treatment for `STYLE_CARTOON` "cute" on a face.
3. **Severity ladder: a named defect on the subject's defining feature is never a "follow-up".** Require each
   reason to be tagged `blocking` or `polish`, with blocking = identity (species, alienness, the def's
   signature feature missing — e.g. Ambrosia's fruit) and polish = scale tweaks, a stray harness, palette warmth.
   Verdict is REDO iff any blocking reason. This targets Opus's 7 PARTIALs without flipping its polish notes.
4. **Relax the facing laws to his observed tolerance.** He kept Sillik (overhead wall-clinger), Dactillion
   (grounded wings raised), Tirbak (east-only harness). Make F_TOPDOWN on wall-clingers / serpentine bodies,
   FLYER_WINGS_GROUNDED and east-only gear `polish`, not `blocking`. This removes 3 of GPT's 6 false REDOs and
   both models' Sillik error. (Keep F_INCONSISTENT blocking when a *structure* fails to rotate — Ssurr.)
5. **Delete only what is broken.** "Delete = DONOR, PLACEHOLDER, or a blocking defect. A non-pick that passes
   goes in `keep_also`." GPT's default delete-all-others destroyed 2 of his picks and 4 kept variants on flora.
6. **Ask for variants on KEEPs.** 8 flora KEEPs carry "Two more variants, more realistic"; add a `wants_variants`
   field and the rule "a single own-art picture for ground cover or bush → request ≥2 variants".
7. **Scale check against the def's words.** Neither saw Rockfinger "50 % larger"; GPT's Bladderquill and Ikkal
   scale REDOs were false alarms. Have code, not the model, compute drawn height vs the description's size word
   and hand the model the number; the model then only judges whether it *reads* wrong.
8. **Card fixes found while scoring:** state when a row holds two slots (meat icon + catch item) so a kept meat
   retexture is not scored as a pick; record which pictures are thumbnails; carry the living row's verdict onto
   catch cards.

Caveats on all of the above: one biome, one sitting, one scorer for §2, 18 REDOs. The counterfactuals in §5
are re-scorings of existing outputs, not re-runs; a changed prompt must be re-raced (on a different biome, to
avoid tuning to this key) before any number here is quoted as the new rate.
