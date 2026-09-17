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

**Ruling, owner 2026-09-16 — the axis is not only appearance.** A `must read`
axis is added for mods whose experience is TEXT, chosen over three alternatives
(visual lines only for Oracle; accepting its written dismissal; exempting text
mods to a separate gate), with the cost accepted: a spec change, a judge that can
assess prose, and the system's scope widening past appearance. §10 is the design.
It qualifies the judging ruling above — a model does **not** judge on every run
for one class of read line, and §10.4 says which and why.

## 1. The north star section

Added to each mod's existing `design/validation_walks/<tier>/<Mod>.md`. Three
parts below, plus a fourth for mods whose experience is TEXT rather than
appearance — the `must read` axis of §10, added on the owner's ruling of
2026-09-16. A mod may carry either axis or both; the format, the ids and the
prose discipline are identical, and only the evidence and the judge differ.

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

One new optional parameter on `component()`. (`reads=`, its text sibling for the
`must read` axis, is §10.5 — same shape, different evidence.)

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

The floor is per AXIS: §10.5 adds `uncovered_reads()`, the same shape again over
`must read` ids. A mod with both axes must clear both.

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

🔴 **Everything in this section is about SCREENSHOTS and does not carry to text.**
The text judge of §10.4 has strictly narrower powers — it may fail a read line
and, on model-generated prose, it may never pass one. Do not reason from this
section to that one; a sprite is a fixed object between runs and generated prose
is not, and that difference is the whole reason the powers differ.

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
2. every validated must-show line is claimed by at least one component (§3),
   and every validated must-read line likewise (§10.5);
3. every claimed line is judged YES on its evidence (§4) — except that an
   **open-generator read line is never judged YES by a model at all** and needs
   the owner's own recorded verdict every time it binds (§10.4);
4. the mod's checklist is VALIDATED, not DRAFT — per axis: a mod with a
   VALIDATED `must show` and a DRAFT `must read` is bound by the first and not
   the second (§10.1);
5. the owner has personally reviewed the sheet at least once — recorded, and
   required only for the mod's **first** GREEN.

A DRAFT checklist cannot green a mod. That is the gate he identified as missing,
and it belongs in a hook rather than in this paragraph.

⚠️ Consequence of 3 that should be stated rather than discovered: **a mod whose
validated checklist carries an open-generator read line cannot go GREEN
unattended.** That is deliberate — it is a mod whose experience is prose a model
writes fresh each run, and there is no artifact for a regression guard to guard.
If that cost is unacceptable for some mod, the fix is to phrase its lines against
the generator's FIXED parts (§10.2), not to let a model pass them.

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

### 6a. The hash is scoped per AXIS — required BEFORE any read line is written

The property above is the design's best one and it has a defect of scale, filed
as `NORTHSTAR_HASH_SCOPE_1`: the hash covers the whole section including its
explanatory prose, so a well-meant typo fix destroys a validation silently. That
item stands on its own. The `must read` axis makes a NARROWER cut of it
mandatory, because without it the axis cannot be added to any already-validated
mod at all.

**MEASURED 2026-09-16** (laptop, offline, against `northstar.py` as it stands and
the two live validated walks):

| | Pits | Graffiti |
|---|---|---|
| recorded hash matches disk today | ✅ | ✅ |
| appending a `### must read` block under the CURRENT whole-section rule | 🔴 **hash breaks — reverts to DRAFT** | 🔴 **hash breaks — reverts to DRAFT** |
| show-axis hash, with read-axis lines excluded, equals the recorded hash | ✅ | ✅ |
| …and survives an appended read block | ✅ | ✅ |

So the rule is:

- 🔑 **The show-axis hash covers the section MINUS every line from a
  `### must read` / `### cannot read` heading to the next `### ` heading; the
  read-axis hash covers only those lines.** The two axes cannot invalidate each
  other.
- The read axis carries its **own** header fields inside its first block,
  `read-state:` and `read-validated-hash:`, excluded from both canonical forms
  exactly as `state:`/`validated-hash:` already are. A mod may therefore be
  VALIDATED on one axis and DRAFT on the other, which is the normal case: he
  will rule on appearance and on prose in different sittings.
- ✅ **This migration costs no re-validation.** Excluding a block that does not
  exist changes nothing, so Pits and Graffiti keep the hashes they already
  carry — measured above, not assumed. That is the only reason this cut is worth
  making separately from `NORTHSTAR_HASH_SCOPE_1`, whose broader fix (hash the
  bars, not the commentary) *will* change both recorded hashes and does need him
  to re-validate or the CLI to re-record on his word.
- ⛔ **Do not write a read line into a walk that already has a VALIDATED
  `## must show` until this is built.** MEASURED 2026-09-16: today's
  `_checklists()` returns None polarity for a `must read` / `cannot read`
  heading, so read ids are silently *dropped* and cannot contaminate the visual
  floor — a DRAFT read block is safe to author. What is NOT safe is the hash: it
  is the whole-section bytes today, and the table above is what happens.

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
| 8 | axis-scoped hashing (§6a) — blocks writing a read line into any validated walk | none |
| 9 | the `must read` machinery of §10: `reads=`, `capture_text`, `uncovered_reads`, the text judge's narrowed powers | none |

**6 is the only bottleneck in the system** and the strategy for it is §8. Nothing
in 1–5 blocks it any more. 8 and 9 are the read axis and block only read lines;
nothing about the visual floor waits on them.

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
- **Order by PLAYER-FACING surface area, appearance or prose.** Mods whose
  experience *is* appearance first (pits, graffiti, inhabited, wrecked machines,
  antiquities); mods whose experience is prose get read lines instead (Oracle,
  Aftermath, AftermathRites, PawnFlavor, JawaVoice — §10.6). A mod that is pure
  arithmetic goes last and may honestly need neither — Visibility's walk says so
  correctly, and that is a legitimate answer.
- 🔴 **Re-examine the 7 walks that dismissed the visual pass before trusting
  any of them.** Each is a written claim that nothing visual matters, and the
  pit proves how wrong such a claim can be while sounding reasonable. ⚠️ Three of
  the seven are dismissals of the wrong axis rather than false ones: they say
  "no art" and are right, then conclude "nothing to check" and are wrong,
  because the mod speaks to the player in prose. Give those a read pass, not a
  visual one — Oracle, `Aftermath.md` and `AftermathRites.md` are all this shape.
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

## 10. The `must read` axis — when the experience is TEXT

Owner ruling, 2026-09-16: **add a `must read` axis.** Chosen over three
alternatives (give Oracle visual lines only; accept its dismissal; exempt text
mods to a separate gate), with the cost stated and accepted — a spec change, a
judge that can assess prose, and a widening of the system past appearance.

### 10.0 Why the visual floor is the wrong instrument here

`validation_walks/RimMandrake/Oracle.md` dismissed the visual pass with: *"the
letter TEXT's tone/register is exactly what the selftest lint already checks
mechanically; nothing here needs a human eyeball this pass."* That is §Why's
sentence with the nouns swapped, and it fails for one specific reason:

🔴 **Oracle's letters are written by a model at runtime, so they cannot be fully
linted even in principle.** MEASURED 2026-09-16 from the source: the lint is
`OracleValidator.TryValidateOhm` — a 600-character cap, five substring tells
(`i am the cradle-mind`, `i am the cradle`, `part of me`, `my other selves`,
`we are one`) and one taboo (`zizzik`). It validates the HARNESS. Nothing in it
can answer whether a letter reads as a god speaking rather than as a helpful
assistant, and no amount of tuning it can, because the string it must judge does
not exist until the call returns.

🔑 **The generalisation:** the visual floor asks *is the thing on screen the
thing he wanted*. For a text mod the artifact is not a picture and the question is
not appearance, but it is the same question, and a lint stands in the same
relation to it that `facing_symmetry` stands to a sprite (§4a) — a real check
that is not the check.

And the axis has work waiting beyond Oracle before it is even built:
`Transient/north_star_batch1_traces_DRAFT_2026-09-16.md` records that Aftermath
and AftermathRites have letters as their ONLY player-facing output, and that
Aftermath's eight authored payload letters never reach the screen at all
(`AFTERMATH_DEAD_LETTERS_1`) — authored experience, present in data, absent from
the game, which is this document's founding defect class in prose.

### 10.1 Section format

`### must read` and `### cannot read` are siblings of `### must show` and
`### cannot show`, inside the same `## north star` section. No new artifact class,
per the location ruling of 2026-09-15.

```markdown
### must read
read-state: DRAFT                 # DRAFT | VALIDATED — owner's word only
read-validated-hash:              # set by the CLI; never by hand

- [ ] `ohm_fallback_is_in_register` (fixed) — the prescribed fallback text
      itself reads as Ohm speaking, not as an error message

### cannot read  (optional)
- [ ] `never_reads_as_an_assistant` (absolute) — the helpful-assistant register
```

- **A mod may carry both axes, and most text mods should.** They are not
  alternatives: they answer different questions about the same experience. Oracle
  has a real visual surface — which letter card a god's words arrive on — and it
  is drafted in §10.7's example alongside its read lines.
- **One id namespace across both axes, and an id belongs to exactly one.** A
  `reads=` claim naming a show id, or a `shows=` claim naming a read id, is a
  lint error of the same class as an orphan (§2) — it is a component offering the
  wrong kind of evidence, and a screenshot of a letter card is not evidence about
  what the letter says.
- **Each line carries its evidence class in parentheses** after the id —
  `(fixed)`, `(enumerated)`, `(open)` for `must read`, and `(absolute)` for every
  `cannot read`. The class is not decoration: §10.4 keys the judge's powers off
  it, so the runner has to be able to read it.
- Ids are stable and never reused; grouping by mechanic is required exactly as in
  §1; an agent distils the lines from `### the experience` and adds no new claims.
- Hashing is per axis and is a hard prerequisite — **§6a, read it before writing
  a read line into any walk.**

### 10.2 What a read line may assert — and the distribution problem

This is the hard part of the design, so it is stated as a rule with its reasoning
attached rather than as a convention.

⛔ **A read line about a generator is not a claim about one output.**
"Reads as a god, not a chatbot" is a claim about a *distribution*. One captured
letter cannot settle it, in either direction: a good sample does not make the
generator good, and a bad sample proves only that the generator can produce a bad
one — which, for an unbounded generator, was never in doubt. A design that judges
generated prose from one sample and records a verdict is manufacturing a number,
and it is the same move as reading a screenshot of the one pit that happened to
look right.

🔑 **The resolution is to classify by what produces the text, because three of the
four classes are not distributions at all.** Every read line declares its class,
and the class fixes its evidence, its bar and who may pass it.

| class | what produces the text | evidence | bar | who may pass it |
|---|---|---|---|---|
| **fixed** | one authored string in a def or in source | that string, captured from the player-facing channel | the string satisfies the line | the judge may pass it (§10.4) |
| **enumerated** | a finite authored set drawn from at runtime | **every member of the set**, listed | all members satisfy the line | the judge may pass it |
| **open** | a model, at runtime, unbounded | a batch of N samples captured in ONE run before anyone looks | k of N, both numbers the owner's | 🔴 **only the owner** |
| **absolute** (`cannot read` only) | any of the above | the same artifact as the axis it guards | **zero occurrences.** One counterexample fails the mod | the judge may FAIL it; a clean batch is not a pass, it is the absence of a failure |

Consequences worth stating outright, because each one removes work:

- 🔑 **Bind the generator's fixed parts, not only its outputs.** Oracle's persona
  and law blocks are `const string`s (`OracleRegisterBlocks.Law`, `.Ohm`,
  MEASURED 2026-09-16) and its fallback text is a fixed string. Those ARE the
  generator's specification and its floor, they are stable artifacts, and a read
  line about them is class `fixed`. This is the honest answer to "one sample is
  not evidence about a generator": stop sampling the generator and bind what
  determines it. MEASURED: there is no temperature, seed or sampling flag in the
  invocation at all (`OracleClient.cs` — `claude -p --output-format text
  --system-prompt <register> --disallowed-tools …`, context on stdin), so the
  persona block, the lint and the fallback are the *only* levers that exist.
- 🔑 **The fallback is the floor, and the floor is fixed.** Law #2 of
  `llm_ingame_wiring_spec.md` — the game is whole with the LLM absent — means the
  prescribed fallback ships on every failure, timeout, kill-switch flip and lint
  rejection. It is therefore the text most players will actually read, and it is
  one string. Bind it first.
- 🔑 **Never sample an enumerable set — enumerate it.** A `RulePackDef`,
  `rulesStrings`, a backstory pool, AftermathRites' 16 authored messages: the
  distribution *is* the set, so a run that draws three of sixteen and passes has
  learned nothing about the other thirteen. This is the read-axis form of the trap
  that got Graffiti's drafted `mark_variants_do_not_repeat` line cut by ruling —
  a bar a run passes or fails by `Graphic_Random`'s luck is not a bar. Enumerated
  evidence comes from the def, not from play, and needs no game running.
- 🔑 **Push everything you can into `cannot read`.** An absolute line needs no N,
  no k and no statistics: a taboo violated once is violated. §1 already observed
  that what he would reject carries more information than what he wants, and on
  the read axis that is not a stylistic preference — it is the difference between
  a decidable bar and an undecidable one.
- ⛔ **An open-class line's N and k are the owner's numbers, stated in the line.**
  An agent may propose them and must mark the proposal as a proposal. A line with
  no N is unfalsifiable prose and is rejected by review.
- 🔴 **The batch is captured in one pass, before anyone reads it, and the whole
  batch is the record.** Re-rolling a consumer until k/N clears is optimizing the
  measure, and a rising pass rate over re-rolls with the persona block unchanged
  is the signature of it (global rule: a rising score with flat mechanical
  findings is not progress). A failed open line's remedies are the persona block,
  the lint and the fallback — never another roll.
- ⚠️ **No defensible N was derived in authoring this, and none is asserted here.**
  UNMEASURED: what N makes a k/N verdict on register mean anything. What is
  measured is that Oracle's budget default is 3 calls per in-game day
  (`OracleSettings.godsBudgetPerDay = 3`), so a batch of 20 is not something a
  normal session produces — an open-class batch is a deliberate harness run, not
  an observation of play.

### 10.3 The evidence artifact — captured from the player's channel, never the def

A read line's evidence is **text, not a screenshot.** That is not a workaround; it
is what makes the axis worth having, because §1's *"answerable yes/no by LOOKING
at one screenshot"* genuinely cannot reach a letter body — the body needs a click,
which the batch-1 draft flagged as an open question and which this axis answers.

- **The capture is a bridge read of the player-facing channel.** MEASURED
  2026-09-16 from `Transient/bench_tools_dump.json`: `rimworld/list_letters`
  ("List current letter-stack entries with native letter ids, semantic letter
  content, and structured look-target metadata") and `rimworld/open_letter` exist,
  and `ORACLE_EXPERIMENT_SPIKE_1`'s own close records reading the delivered
  letter's raw `text` field back through it and matching a marker string
  byte-for-byte. `jawa/letter_list` returns label/defName/arrivalTick only — no
  body — so it is not an evidence source for a read line.
- 🔴 **Text captured from a def proves the words EXIST; only text captured from
  the channel proves they ARRIVED.** This is not a technicality: it is
  `AFTERMATH_DEAD_LETTERS_1` exactly — eight letters authored in defs, read by
  nothing, on screen never. A read line whose evidence came from the def is
  therefore admissible for `enumerated` register questions ("do these sixteen
  authored messages all read in-world") and **inadmissible** for any question
  about what the player experiences. A walk needs both: a state assertion that
  the string reached the stack, and a read verdict on the string that did.
- **`(enumerated)` lines are the exception that needs no game.** Their evidence is
  the authored set, so they can be judged from disk — which is what makes the
  read axis authorable and largely *runnable* on this laptop, unlike the visual
  floor.

### 10.4 Who judges — a model MAY pass a read line (owner ruling, 2026-09-16)

The visual judge of §4 is reused for its transport and its narrow-question
discipline.

🔴 **OWNER RULING, 2026-09-16, verbatim: "Let a model YES green a line."** This
**replaces** the asymmetry originally specified here, under which a model's `YES` on
an `open` line was recorded `NEEDS-OWNER` and could green nothing. He was shown that
cost and the objection — that the same kind of thing which wrote the prose would be
certifying it, and that `Agent_Policy.md`'s forbidden-place #4 covers text he reads as
a conclusion — and ruled against it anyway. **His reasoning is sound and worth stating,
because the two failure modes are not the same size.** The asymmetry's cost was
*unbounded and unrecoverable*: any mod with an open read line could never go GREEN
unattended, ever — a permanent tax on the one resource this entire system exists to
conserve. The cost he accepted instead is *bounded and recoverable*: a tonally-flat
letter slips through, he meets it in play, and re-opens the line. An off-register
letter is nowhere near the severity of a pawn standing upright in a 64px trap icon,
which is what the visual axis exists for.

So, as of this ruling:

- **A model judge may return a passing verdict on any read line, `open` ones
  included, and that pass greens the line.** There is no `NEEDS-OWNER` gate.
- ⚠️ **Residual risk, stated rather than argued:** on `open` lines the grader and the
  generator may be the same model (the UNMEASURED note below), so a pass there is the
  weakest verdict this system produces. Weight it accordingly — when a letter reads
  wrong in play, suspect the line before suspecting the letter.
- 🔴 **`cannot read` lines are untouched and remain absolute.** They find violations
  rather than granting passes: zero occurrences, one counterexample settles it
  (§10.2). A model reporting a violation with a quoted span is checkable in seconds,
  which is the cheap direction the ruling never contested.
- **On `fixed`, `enumerated` and `absolute` lines the judge may pass, exactly as
  on the visual axis.** The object is stable and pinned by a hash, so a judged
  verdict is a real regression guard on a real artifact. The distinction is the
  artifact's stability, not taste: a sprite does not change between runs and
  neither does a `const string`; an open generator's output is a new object every
  time, so there is nothing for a regression guard to guard.
- 🔴 **Model tier is opus.** `Agent_Policy.md`'s catcher table, row 4 — *"Only the
  owner's eye — art, the world, prose he reads → opus"*. The tier requirement stands
  untouched by the 2026-09-16 ruling: he lifted the *authority* limit, not the *tier*
  floor, so a read verdict is never delegated to a cheaper model. That policy's
  forbidden-place #4 (*"Text the owner reads as a conclusion"*) now carries an
  explicit carve-out for north-star read verdicts, recorded there in the same change
  as this one.
- ⛔ **No fan-out, no voting, no second opinion.** One judge, one owner. Several
  reviewers agreeing on a contested register question is evidence of a shared
  blind spot, not of quality — and register is the contested case by definition,
  since the uncontested part is a substring check and belongs in the lint (§10.6).
- ⚠️ **UNMEASURED, and it matters: whether the judge and the generator are the
  same model.** Both go through `claude -p`; nothing in either path pins a model
  version, and the game machine's CLI and this checkout's differ by version
  already (2.1.228 vs 2.1.266, recorded in `OracleClient.cs`). The mitigation is
  NOT "use a different model", which cannot be guaranteed — it is the rule above,
  that the model cannot grant a pass on the one class where the overlap would
  matter.

### 10.5 The join: `reads=`, and the read floor

The mirror of §2 and §3, unchanged in shape, so that nothing new has to be
learned:

```python
with t.component("ohm_letter", toggle="enabled",
                 reads=["ohm_fallback_is_in_register",
                        "never_engineering_marker_in_player_text"]):
    t.bridge_call("jawa/oracle_test_ohm_letter")
    t.wait_ticks(60)
    t.capture_text("rimworld/list_letters")     # PROPOSED — see below
```

- `reads=` names which must-read/cannot-read ids **this component's captured text
  is evidence for**. Optional, defaulting to `None`, so all 18 existing scripts
  keep running unchanged.
- `t.capture_text(...)` is the text sibling of `t.screenshot()`: it appends to a
  `component.texts` list the way screenshots append to `component.screenshots`,
  and the judge is given the artifact plus the line's own prose plus, for an open
  line, its declared N.
- `floor.uncovered_reads(must_read_ids, components)` — a validated must-read line
  no component claims makes the mod REFUSE, identically to §3.
  `floor.orphan_reads` is the reverse lint.
- **An `open` line's claimant must produce the whole batch in one component run.**
  A component that captured 4 of a declared 20 has not produced the evidence and
  the line is UNJUDGEABLE, never a partial pass — the same rule as a component
  that claims a visual line and captured no screenshot.
- ⚠️ All four names in this subsection are **PROPOSED by this spec and not built**
  (owed item 9, §7). `component()`'s real signature today is
  `component(self, name, toggle=None, beyond_toggle=False, shows=None)`;
  `suite.py` has `screenshot()` and `checkpoint()` and no text capture.

### 10.6 What a read line may NOT be

The reciprocal of §10.0, and the thing that keeps this axis from becoming a way
to spend the owner's attention on regex work.

⛔ **A read line must be a question a string check cannot answer.** If a line is
fully expressible as a substring, a length, a regex or a def read-back, it is not
a read line — it is a lint rule, and writing it here instead is the same defect as
the pit's dismissal, mirrored: claiming a human judgement for a question a machine
settles, rather than the reverse.

- Oracle's *"never says 'I am the Cradle-Mind'"* and *"never names Zizzik"* are
  already `OracleValidator` tells and stay there. Its 600-character cap is a
  number and stays there.
- 🔑 **But a `cannot read` line over lint-covered ground still earns its place**,
  and this is the one case where duplication is correct: the lint stops the string
  at runtime, and the validated line stops the LINT from being quietly weakened.
  R-W6's laws are the owner's ruling; a later agent trimming a tell out of
  `SelfUnificationTells` to make a test pass is exactly the failure a validated
  statement of intent exists to catch. Write the line, and say in it that the lint
  is its enforcement.
- ⛔ **The lint is never cited as evidence for a read line.** It is the thing
  under test, not the test. Oracle's walk citing its own lint as the reason no
  human eye was needed is the sentence this axis exists to delete.

### 10.7 Scope — which other walks need this axis

MEASURED 2026-09-16 across `src/` (grep for the player-facing text calls, mods
only, bridge tooling and `Utils/` excluded):

| | count |
|---|---|
| shipped mod folders calling `ReceiveLetter` / `LetterStack` | **15** |
| shipped mod folders calling `Messages.Message` | 15 |
| union — mod folders that speak to the player in prose from C# | **25** |
| walk files in total (unchanged) | 77 |

⚠️ That is a count of mod FOLDERS carrying the call, not of walks that need read
lines — the judgement is per mod and is the owner's. Folder-to-walk mapping was
done by name only and is a lower bound. And it counts C# only: prose shipped
purely in XML (labels, descriptions, backstories, `rulesStrings`) is not in it.

The named text surfaces, strongest case first:

- **Oracle** (`open`) — the trigger case. The only open-generator consumer that
  exists today; the raid-redesigner of `PLOT_MECHANISM_MODS_WAVE_1` Part 1 becomes
  the second, riding whatever `OracleClient` becomes.
- **Aftermath** and **AftermathRites** (`enumerated`/`fixed`) — letters as their
  ONLY player-facing output, 16 authored messages of which 5 are reachable, and 8
  payload letters read by nothing. Immediate work, and it needs no game: the set
  is on disk.
- **PawnFlavor** (`enumerated`) — 50 BackstoryDefs across ten factions, 13
  TraitDefs, and three `PatchOperationFindMod` blocks that relabel other mods'
  `ThoughtDef`/`XenotypeDef`/`MentalBreakDef` flavour text *to Jawa voice*. Pure
  prose, no visual surface at all, and the largest enumerable set in the repo.
- **JawaVoice** (`enumerated`) — SpeakUp `rulesStrings` for Jawa speech. Drawn
  from at random in play and therefore never to be sampled; the authored set is
  the distribution.
- **Doctrine / Rites / FactionSlate** (`enumerated`) — ideoligion, precept and
  faction prose. UNMEASURED which of the three actually ships player-read strings
  of its own versus patching others'.
- **StrandedQuest** (`fixed`) — one quest's offer and outcome text.
- **Antiquities** (`fixed`) — its drafted `catalogued_state_visible` line is
  proved via `jawa/inspect_string`, i.e. text, which the batch-1 draft flagged as
  "exactly the kind of proof the north star exists to distrust". It is a read
  line, not a show line, and moving it is the correct fix.
- **SalvageClaim / Property** (`fixed`) — its walk's *"no visual lines"*
  conclusion is the one genuine one in batch 1, and it has exactly one text line:
  the float-menu string. The read axis gives that mod the coverage the visual
  floor honestly could not.

## 11. The read axis's falsification test

This axis fails if it does not turn Oracle red, and fails differently if it turns
into owner-attention spent on lint work.

```
PROVE   Oracle moves from unvalidated to REFUSED-or-RED once its read
        checklist is VALIDATED and §10's machinery is in place
EXPECT  REFUSED on the read floor first (validated read lines with no
        component claiming them), then RED on
        `never_engineering_marker_in_player_text` — MEASURED offline
        2026-09-16: the only fallback string in the mod is
        "[FALLBACK] My spine settles where you touched it. Good work,
        small hands." and the only letter label is "Ohm speaks (Oracle
        spike)". A bracketed engineering marker and a project codename,
        both in text the player reads
LIES    a model returning YES on an `open` line and that YES being allowed
        to green the mod; any run in which the same `claude -p` both wrote
        the letters and passed them; an `open` line recorded as passing
        against one captured letter; a `must read` line a regex settles
```

⚠️ Two first-run signatures to distrust, both stronger here than on the visual
axis. A batch that clears an open line on its first outing is the most likely sign
the line was written to be passed — and unlike a screenshot, nobody can re-check
it later, because the letters are gone. A pass rate that rises across re-rolls
with the persona block, the lint and the fallback all unchanged is not the mod
improving; it is the sample being chosen.
