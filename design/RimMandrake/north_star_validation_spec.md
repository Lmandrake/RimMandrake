# North stars — binding a mod's intended EXPERIENCE to its validation run

Owner-designed sitting 2026-09-15 (BENCH). Extends
`mod_validation_runner_spec.md` (the modcheck rulings of 2026-09-12); it does not
replace it. Everything in that spec still stands — this adds the half it was
missing.

## Why this exists

The owner, on seeing the pit mod do exactly what its spec asked and nothing more:

> *"I was somewhat shocked and appalled when I saw the Pit mod doing precisely
> what we asked it to do: and only that. A simple little trap that just Snares a
> pawn to stand there staring at the camera, stuck in a trap with "Pit" written
> on it. Not at all "falling in a pit" but I understand what happened."*

**The pit mod was recorded GREEN when he said this.** Four findings, all measured
2026-09-15, explain how:

1. **`component()` has no visual expectation.** Its signature is
   `component(self, name, toggle=None, beyond_toggle=False)`
   (`modcheck/suite.py:118`). A component can capture a screenshot; it cannot
   state what the screenshot must show.
2. **The judge does not exist.** `mod_validation_runner_spec.md` §2 rules that
   "one model pass at the end judges outcomes against each component's stated
   expectation." Nothing in `modcheck/` implements it — zero references to a
   judge or an LLM pass anywhere in the package.
3. **So a verdict is purely the state assertions.** `runner.py:205` computes
   `all_green` from component verdicts alone. No code path reads a screenshot.
   The 2026-09-12 ruling that "neither alone passes a component" is written down
   and not enforced: screenshots are captured and never looked at.
4. **The pit's own walk dismissed the visual pass in writing** —
   `validation_walks/RimMandrake/Pits.md`: *"No [S] line: the mass-trigger and
   escape mechanics are the whole point and are fully script-checkable; nothing
   here is visual-only."*

And the mechanism is worse than a missing check. The pit's script asserts
`t.expect_pawn_despawned(walker)` — and that assertion is **true**. The pawn
really does leave the map as a thing. But `Building_OpenPit` draws its first
occupant through `IThingHolderWithDrawnPawn` (`Building_OpenPit.cs:29-35`), over
a graphic that is still vanilla's 64×64 `TrapSpikeArmed` icon
(`Pit_OpenPits.xml:32-35`, flagged a placeholder in its own header). So the state
is correct and the screen is wrong **at the same time**, and every mechanical
assertion passes while the player watches someone stand in a box labelled Pit.

🔑 **The lesson generalises past art.** A validation suite that can only assert
state will certify any mod whose state is right and whose experience is absent.
That is the class of defect this document exists to make impossible to pass.

## The scale of the gap (MEASURED 2026-09-15)

| | count |
|---|---|
| validation walk files | 77 (27 RimMandrake / 23 RimStarWars / 27 RimUtinni) |
| mods with a `validation.py` | 18 |
| mods recorded in `modcheck_status.json` | 14 — 12 RED, 2 GREEN |
| human-visual `[S]` steps across all 77 walks | 75 (~1 per mod) |
| walks explicitly dismissing the visual pass | 7 |

The two GREEN entries are FluidCanals and Pits. The Pits GREEN came from
`MODCHECK_RUNNER_SWAP_LIVE_PROOF_1` on config `min+Pits` — a run proving the
*runner* worked, never a judgement of the pit.

## Rulings (owner, 2026-09-15)

Answered by card, this date. These four shape everything below.

- **Unit: one whole mod.** One north star per shipped mod, matching the roster
  the walks and status registry already use — not per mechanic, not per test
  scenario. *(He chose this over a finer unit with its cost stated: a per-mod
  checklist can sprawl or go vague. The mitigation is structural, not
  discretionary — see §1's grouping rule.)*
- **Location: inside the existing walk file.** No new artifact class. The 77
  walks already carry code-anchored assertions and already reserve an `[S]`
  human-visual slot.
- **Enforcement: per mod, as he validates each.** The visual floor binds only
  where he has validated that mod's checklist. Every other mod behaves exactly
  as it does today. This makes the whole change additive — no existing script
  breaks.
- **Judging: a model on every run, his own eyes once before a mod's first
  GREEN.** Mirrors the code-review rule already in force: the first pass is
  whole-file and human, later passes are incremental.

- **Authorship** (his words, this date): *"I write vision, agent writes
  checklist, I validate checklist before it's fully filed. That's the part
  that's missing: the last one."*

## 1. The north star section

Added to each mod's existing `design/validation_walks/<tier>/<Mod>.md`. Three
parts:

```markdown
## north star
state: DRAFT                      # DRAFT | VALIDATED — owner's word only
validated-hash:                   # set by the CLI when he validates; never by hand

### the experience  (OWNER'S WORDS)
Free prose. What this mod should feel like when it is working. His voice,
not summarised, not tidied. This is the only part an agent never writes.

### must show
Grouped by the mechanic each line belongs to. Every line has a stable id and is
answerable yes/no by LOOKING at one screenshot.

- [ ] `pit_reads_as_hole` — a sprung pit reads as a dark hole at play zoom with
      its label hidden, not as an icon on the floor
- [ ] `pit_occupant_below_floor` — a captured pawn is not drawn standing at
      floor level
- [ ] `pit_occupied_distinguishable` — occupied and empty sprung pits are
      distinguishable at a glance, without a tooltip
- [ ] `pit_covered_invisible` — a covered pit is invisible at play zoom
- [ ] `pit_covered_seam_at_max_zoom` — and shows a seam at maximum zoom

### cannot show  (optional)
What he would reject. Often sharper than what he wants — the pit's rejection
("not at all falling in a pit") carried more information than any description of
success did.

- [ ] never reads as a vanilla spike trap
```

**Grouping is the guard against the per-mod unit going vague.** The file is
per-mod; every *line* names one mechanic and binds to specific components. A pit
mod's section carries separate groups for the trap, the prisoner cells and the
dig sites. A line that could apply to the whole mod is too vague to be a
must-show and is rejected by review, not by a tool.

**Ids are stable and never reused.** A component references a line by id; renaming
an id orphans a claim, which the floor check reports.

**An agent distils `must show` from `the experience` and adds no new claims** —
the same discipline `canon_references/AGENT_BRIEF.md` imposes on its own
checklists, and for the same reason.

## 2. The join: `shows=`

One new optional parameter on `component()`:

```python
with t.component("falls_in", toggle="trapTriggerEnabled",
                 shows=["pit_reads_as_hole", "pit_occupant_below_floor"]):
    t.walk_over(walker, pits)
    t.wait_ticks(600)
    t.expect_pawn_despawned(walker)
    t.screenshot()
```

- `shows=` names which must-show ids **this component's screenshots are evidence
  for**. It is the only wiring between intent and test.
- Optional and defaulting to `None`, so all 18 existing scripts keep running
  unchanged. That is what makes the per-mod rollout possible.
- An id in `shows=` that no validated checklist defines is a **lint error**, not
  a silent pass. Claiming to show something nobody asked for is the same defect
  class as a patch that matches nothing.

## 3. The visual floor

`floor.py` today answers one question: which Mod Settings toggles have no
covering component. It gains a second, identical in shape:

```
uncovered_shows(must_show_ids, components) -> sorted ids with zero claiming component
```

- **A validated must-show line with no component claiming it makes the mod
  REFUSE**, exactly as an uncovered toggle does. Uncovered *experience* becomes
  as fatal as uncovered *settings*.
- Only validated checklists are consulted. A DRAFT section contributes nothing
  to the floor — it cannot fail a mod, and it cannot green one either.

## 4. The judge

New module, `modcheck/judge.py`. Runs once at the end of a run, per the
2026-09-12 ruling that the LLM never drives.

- **Input per screenshot**: the image, the component's name, and the *specific
  must-show lines it claims*. Never a bare "does this look right" — that
  question is unanswerable and its answer is worthless.
- **Output per claimed line**: `YES` / `NO` / `UNJUDGEABLE`, with one sentence of
  why. `UNJUDGEABLE` is a real verdict for a screenshot that cannot settle the
  line (wrong zoom, occluded subject) and never collapses to a pass.
- **A `cannot show` line is judged with the opposite polarity**: it states a
  defect, so `NO` clears it and `YES` fails the mod. The judge is asked the same
  narrow factual question either way — is this statement true of this image —
  and the polarity is applied by the runner, never by telling the model which
  answer is wanted. (Built 2026-09-16. The first implementation collected every
  checkbox id in the section into one list, which put the pit's own rejection
  line into the visual FLOOR and would have demanded a component prove the
  defect was on screen.)
- **Transport is `claude -p`**, a subprocess, not an HTTP endpoint — the standing
  ruling of 2026-09-05 for every LLM consumer in this repo. No API key, no base
  URL.
- **The judge is never the only reader.** A mod's first GREEN requires the
  owner's own eyes on the sheet (§5). The judge catches regressions afterward on
  a bar it did not set.

⚠️ **The judge grades work its own kind produced.** That is the exact
self-grading trap the global rules name, and it is the reason the checklist must
carry his validation before it can bind. A model judging a screenshot against an
agent-written bar would be two agents agreeing, which is not evidence.

### 4a. The judge earns its place — MEASURED 2026-09-15

Tested end-to-end against a real shipped asset, with independent ground truth
established first.

- **Subject**: `src/RimStarWars/GizkaArtOverride/Textures/swanimals/Gizka/Gizka_north.png`
  — a north facing, 256×256.
- **Numeric ground truth**: mirror-symmetry of the visible silhouette about its
  own vertical axis = **0.845**. A north facing is a front/rear view and should
  be near-symmetric, so 0.845 **passes** the 0.80 floor that
  `art_checks.facing_symmetry` uses.
- **The judge's verdict**: `NO` — *"drawn as a full side profile facing right — a
  single eye visible, body elongated left-to-right, and no symmetry about a
  vertical axis — despite being the `_north` (rear-view) texture."* Elapsed 17.8 s.
- **Adjudicated by looking**: the judge is correct. The sprite is unambiguously a
  side profile of a lizard facing right, with one eye.

🔑 **So the numeric gate passes an asset the eye rejects, and the judge caught
it.** This is not a tuning problem — `facing_symmetry`'s own docstring concedes
it "CANNOT catch a face in the north," because a frontal face is symmetric too.
A blobby side profile scores as symmetric by accident. No threshold fixes that.

Two consequences beyond this spec:

- The defect found is exactly the one `ARTPIPE_FACING_COHERENCE_1` describes
  ("facing sets are three independent side-profiles; north shows a face"), now
  confirmed on a live shipped sprite rather than inferred.
- Any future claim that a geometric check makes visual judgement unnecessary
  should be tested against this case first. It is the counterexample.

## 5. What GREEN means, restated

A mod is GREEN only when all of:

1. every component's state assertions pass (unchanged from 2026-09-12);
2. every validated must-show line is claimed by at least one component (§3);
3. every claimed line is judged YES on its evidence (§4);
4. the mod's checklist is VALIDATED, not DRAFT;
5. the owner has personally reviewed the sheet at least once — recorded, and
   required only for the mod's **first** GREEN.

A DRAFT checklist cannot green a mod. That is the gate he identified as missing,
and it belongs in a hook rather than in this paragraph.

## 6. Validation state and staleness

Extends `modcheck_status.json`, which already follows the CODE_REVIEW_STATUS
pattern (per-mod hash, never hand-edited).

- `modcheck validate <mod>` records the content hash of the north star section
  and sets `state: VALIDATED`. Owner-authorised only.
- **Any edit to the section reverts it to DRAFT automatically**, by hash
  mismatch. His validation cannot be silently rewritten by a later agent — the
  single most important property of this design.
- The existing `minor` declaration mechanism is unchanged and does not extend to
  checklists: there is no "minor" edit to a validated statement of intent.

## 7. What is built, what is owed

**Built** (verified 2026-09-15): `modcheck/` runner, suite, floor, status,
report, cli, selftest; 18 `validation.py`; `modcheck_status.json`; 77 walk files
with code-anchored `## must be true`.

**Built 2026-09-16** (`NORTH_STAR_RUNNER_WIRING_1`), 66 offline checks in
`modcheck/selftest_northstar.py`, none of which shells out:

| # | item | where |
|---|---|---|
| 1 | `shows=` on `component()`; orphan-id lint | `suite.py`, `floor.orphan_shows` |
| 2 | `uncovered_shows()` and the pre-run refusal | `floor.py`, `runner.visual_floor`/`refusal` |
| 3 | `judge.py` + both halves required for green | `runner.apply_judgement` |
| 4 | DRAFT/VALIDATED hash state; `modcheck validate` | `northstar.py`, `cli.py` |
| 5 | the GREEN definition of §5 | `status.verdict_for`, `.claude/hooks/block_forged_validation.py` |

**Owed:**

| # | item | owner time |
|---|---|---|
| 6 | north star sections in 77 walks | **his vision + validation** |
| 7 | `validation.py` for the 59 mods that have a walk and no script | none |

**6 is the only bottleneck in the system** and the strategy for it is §8. Nothing
in 1–5 blocks it any more.

Two things 1–5 deliberately do NOT do, so nobody reads more into them:

- **The toggle floor is still not wired into a run.** `floor.uncovered()` is
  called only from `selftest.py`, exactly as before. The visual floor was wired
  because it binds nothing until he validates a mod; wiring the toggle floor
  would refuse mods today, against §MOD_OPTIONS_RETROFIT_1's own known gap.
- **No mod's behaviour changed.** Every one of the 18 scripts has no `shows=`
  and no walk has a VALIDATED checklist, so every run still resolves exactly as
  it did. MEASURED 2026-09-16, the two recorded GREENs: **FluidCanals still
  records GREEN** (its walk has no `## north star` section at all), and **Pits
  records `DRAFT-CHECKLIST`** — its checklist exists and is not his yet. So the
  pit stops being green the moment it is next run, before he validates anything,
  which is the first half of §9's falsification test arriving early.

## 8. Getting 77 of them written

The constraint is his attention, not agent throughput. Everything below exists
to spend less of it.

- **He never writes from a blank page.** An agent drafts candidate must-show
  lines from what already exists — the walk's `## must be true`, the mod's
  About.xml and Mod Settings toggles, its actual sprites — and he accepts, edits
  or rejects them. He reacts rather than composes, and reaction is where he is
  demonstrably sharpest: he identified the pit defect in one glance.
- **His recorded words are already a source.** The pit's checklist was drafted
  without him present, from verbatim quotes already in
  `PIT_TRAP_VISUAL_REDESIGN_1`. Any mod he has ever ruled on has vision prose
  sitting in the ledger or an item file.
- **Batch by visual family, never alphabetically.** One sitting covers mods
  sharing a visual language (hazards; creatures; structures), so a judgement
  about one carries to the next.
- **Order by visual surface area.** Mods whose experience *is* appearance first
  (pits, graffiti, aftermath, inhabited, wrecked machines, antiquities). A mod
  that is pure arithmetic goes last and may honestly need no visual lines —
  Visibility's walk says so correctly, and that is a legitimate answer.
- 🔴 **Re-examine the 7 walks that dismissed the visual pass before trusting
  any of them.** Each is a written claim that nothing visual matters, and the
  pit proves how wrong such a claim can be while sounding reasonable.
- **The 59 missing scripts do not wait on him.** They can be written with state
  assertions today and gain `shows=` when their mod's checklist is validated,
  because enforcement is per-mod. Streams 6 and 7 run in parallel; only 1–5
  block.

## 9. The falsification test

This design fails if it does not turn the pit red.

```
PROVE   Pits moves from GREEN to REFUSED-or-RED once its checklist is
        VALIDATED and the machinery of §§2-5 is in place
EXPECT  REFUSED on the visual floor (validated lines with no component
        claiming them), then RED on the judge once components claim them
LIES    a green Pits after validation; a judge returning YES on
        `pit_occupant_below_floor` against the current 64px trap icon with a
        pawn drawn standing on it
```

⚠️ A run where the judge passes everything on its first outing is not success —
it is the most likely sign the bar was written to be passed. Check the pit
first, because the answer there is already known.
