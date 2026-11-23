# Result: `RIMMANDRAKE_REWRITE_DELEGATION_DEBUG_DOCS_SECTION_NUMBERS_STAY`

Part of batch 7 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_BIOME_DELEGATION_DEBUG_DOCS_CODE_CITES_THEM`). Files:
`design/RimMandrake/delegation_policy.md` and `design/RimMandrake/debug_process.md`. Run 2026-11-23, one detached
helper run.

Base: 9308e4fc6018d8256ca99df8918d763311d4c119

Special rule of the batch: code cites both files by section. Each heading stays word for word. Each section number and
each list number stays (`delegation_policy.md` §1 to §6, §2.1 to §2.5, §4.1 to §4.7; `debug_process.md` §0 to §8, §6a,
§6b, §6c, and the numbered items of §0 and §2).

## Scores

| measure | `delegation_policy.md` before | after | `debug_process.md` before | after |
|---|---|---|---|---|
| bytes | 16,053 | 18,746 | 28,611 | 30423 |
| words in linted prose | 2,307 | 2,766 | 4,043 | 4,335 |
| STE violations per 100 words | 5.03 | 2.06 | 4.70 | 2.49 |
| sentences over 20 words | 47 | 16 | 71 | 29 |
| flagged lines (mechanical) | 4 | 3 | 7 | 1 |
| lines that a cold reader cannot act on (hand count, by the writer) | 12 | 0 that this run could resolve; 4 listed under "Could not determine" | 17 | 0 that this run could resolve; 4 listed under "Could not determine" |

The files grew by 17% and 6%.

### The long sentences that stay

`delegation_policy.md` (16):

| line | kind |
|---|---|
| 16, 67, 67, 72, 76, 123, 136 (second), 192 | an owner quote, or a sentence around one |
| 79, 85 | a sentence that holds a command (`art.py install --by-card "…"` with the card text) |
| 136 (first) | a sentence that holds a command (the `lost:` and `undo:` code spans) |
| 55, 55, 60, 105, 197 | a bold lead that stays word for word, joined by the lint with the next sentence |

`debug_process.md` (29):

| line | kind |
|---|---|
| 195, 275, 358, 370, 370, 370, 376, 398, 398, 398, 415 | an owner quote |
| 11, 40, 59, 82, 100, 139, 175, 179, 231, 245, 290, 336, 372, 374, 380, 409 | a bold lead that stays word for word, joined by the lint with the next sentence |
| 64 | the old wording, restored after the meaning read (the "When … show (a) and (b)" trigger) |
| 306 | none of the three kinds: a plain sentence just over 20 words ("An item reaches a Test Pilot in two cases: …") |

The flags that stay: two `shout` flags in `delegation_policy.md` (the slogan "What it does NOT change" and the ⛔ marks),
one `bare-id` flag on `D4(a)`, which now has its gloss on the next line. One `shout` flag in `debug_process.md` (the 🔑
mark, kept).

## Code and tests that read the files

- `src/RimMandrake/rimflow/selftest_conductor_authority.py` needs `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` in
  `delegation_policy.md`. The line "design/RimMandrake/delegation_policy.md names the ruling" reads `ok`. The test as a
  whole reads 102 ok and 6 FAIL. None of the 6 is in these two files: `roles/list_shape.md`, `maturation.py`,
  `bridgetools/build.py` and `rimflow/wake_words.py`, each changed on 2026-11-23 by other runs. This run filed them as
  `RIMMANDRAKE_REPAIR_CONDUCTOR_AUTHORITY_SELFTEST_SIX_RED_SINCE_TODAY`, with the selftest as its acceptance test.
- The other five tests that `git grep -l` finds (`selftest_extensions.py`, `selftest_governor.py`,
  `selftest_salvage_lift_policy.py`, `selftest_telemetry.py`, `selftest_bacta_mock.py`) cite the files only in comments
  or in a string about another file. None of them reads the text.
- `selftest_retired_era_gone.py` and `selftest_skills_by_work.py`: PASS on the new files.
- Code cites `delegation_policy.md` §1, §2, §2.1, §2.2, §2.3, §2.5, §3, §4, §4.3, §4.5, §5, and `debug_process.md`
  §2, §2.4, §6a, §6b and "section 3". Every one of these sections and list items still exists at the same number.

## The hand count

`delegation_policy.md`:

| old line | what a cold reader lacks | state after |
|---|---|---|
| "only for NONE/PLACEHOLDER/DONOR destinations" | what the three states are | gloss from `src/RimMandrake/Utils/art/regen_eligibility.py` |
| "applying a ruling to its twins (a case the ruling does not name)" | the term in a parenthesis inside a long sentence | "A twin is a case that the ruling does not name." |
| "Check: `CARDS_ENFORCE_DELEGATED_CLASSES_STOP`." | what "Check:" points at | names the item and the hook `.claude/hooks/block_delegated_cards.py` |
| "the refusal is self-declared" | what the gate can see | "The gate knows only what the seat declares." |
| "the next shadow sheet" | what a shadow sheet is | gloss from `src/RimMandrake/Utils/art_eval/shadow.py` |
| "a player-truth check" | what a player-truth is | gloss from `design/RimMandrake/player_truth_testing_pilot_2026-10-26.md` (repaired after the meaning read) |
| "token-blind by allow-list" | what token-blind means here | gloss from the `delegated_digest.py` docstring |
| "at its cut" | what the cut is | "The cut is the moment of the page's snapshot." |
| "D4(a)" | a bare id | gloss from `design/RimMandrake/dispatcher_risk_response_2026-10-29.md` §7 (repaired after the meaning read) |
| "adds the reason to the brief (§4.6)" | a wrong pointer (see "Fixed on sight") | §4.7 |
| "That covers, among the rest: …" (one sentence of about 90 words) | twelve acts in one sentence | a list |
| "Four of those … Cutting …; changing …; deleting …; and loosening …" | four acts in one sentence | a list |

`debug_process.md`:

| old line | what a cold reader lacks | state after |
|---|---|---|
| "**Source first, still.**" | what to do | "Read the source before you go live." |
| "membership in a family script" | what a family script is | gloss: one script that covers a group of related mods |
| "plus a walk whose `## must be true` …" (§1) | what a walk is | names the walk file and §2.1 |
| "the Charter's expensive list" | where the list is | `infrastructure/agents/CHARTER.md` §The expensive list |
| "**Runnable with no LLM (Lightspeed).**" | what Lightspeed is | gloss from `lightspeed-authoring.md`: the testq lane that runs a proof with no model |
| "in a `live-proof` line" | what a live-proof line is | a line of `infrastructure/state/live_proofs/<ID>.txt` |
| "Declare the smallest tier." | which tier | the smallest mod-list tier that holds the mod |
| "at a path of the owner mod's own" | "owner mod" reads as the owner's mod | "a path inside the mod that owns the creature" |
| "the door … keeps the outcomes apart" | which outcomes | gloss from `gpt_door.py`: one named verdict per consult, and no answer is never a success |
| Rung 0: five classes in one paragraph | five instructions in one block | a list |
| Rung 2: four outcomes joined by "·" | four instructions in one line | a list |
| "**Ablation is later and explicit.**" | what ablation is | "Ablation is the removal of tests." |
| "The pause is bounded by live-run throughput, not authoring." and the long authors sentence | three instructions in one sentence | a list |
| "Basis: pass 7 (pass 7, 2026-10-13: …)" | which pass 7 | "Pyrelands live pass 7" (BENCH ledger, bridge event "pyrelands pass 7", 2026-10-13) |
| "is adopted where it set: …" | seven points in one sentence | a list |
| "a list with neither is not written" | who refuses | "A door does not write a list that has neither: the guard refuses that list." (repaired after the meaning read) |
| the zoom-mod paragraph (one sentence of about 90 words) | six facts in one sentence | a list |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`), `delegation_policy.md` | a copy with `CARDS_ENFORCE_DELEGATED_CLASSES_STOP` removed and "inside 45 minutes" changed to "inside some minutes" | 1 lost (the id), exit 1. Check 1 did not see the lost 45. |
| check 2 (`rule_doc_lint.py keep`), `delegation_policy.md` | the same copy | 3 lost (the code span, one copy of 45, the id), exit 1 |
| check 1, `debug_process.md` | a copy with `NORTHSTAR_BRIDGE_UTILIZATION_1` removed and "a 2-cell margin" changed to "a small margin" | 1 lost (the id), exit 1. Check 1 did not see the lost 2. |
| check 2, `debug_process.md` | the same copy | 3 lost (the code span, one copy of 2, the id), exit 1 |
| check 1 | the final `delegation_policy.md` | 53 items, 0 lost, exit 0 |
| check 2 | the final `delegation_policy.md` | 137 spans, 0 lost, exit 0 |
| check 1 | the final `debug_process.md` | 61 items, 0 lost, exit 0 |
| check 2 | the final `debug_process.md` | 196 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | 18 PASS 0 FAIL; 19 of 19; GREEN 12 planted cases |
| `selftest_block_forged_validation.py` | after the hook fix below | 29/29 passed |

Two keep artifacts on the first draft, both in `delegation_policy.md`: (1) check 2 read the text between two italic
quotes ("; he explicitly extended it to art. This replaces the 2026-09-15 rule") as one quote. The rewrite keeps that
text word for word. (2) check 2 read the corrected `§4.7` as a lost `4.6`. A one-line move pointer below the §4 list
keeps `§4.6` (see "Fixed on sight").

Names of people: this run read the diff for names. The Conductor, the owner, GPT, Steam, the Designer, Graffiti,
Pyrelands, FlowWorks, MessyConduit, `RUT_Barbslinger`, Camera+, BENCH, OWNER, Utinni, Test Pilot and Dispatch each stay
at the same count or more.

## What the meaning read found

Two fresh Opus readers (agent type rm-judge, model opus), one for each file, one after the other. Each reader got the
old and the new text and no reasoning from the writer. The writer fixed every finding. No reader read the repairs.

`delegation_policy.md` (7 items: 4 meaning changes, 3 confirmations):

| first draft | why it was wrong | repair |
|---|---|---|
| "D4(a), the option that he chose on card D4" | D4 is decision D4 of `dispatcher_risk_response_2026-10-29.md`. The Conductor ruled option (a) on 2026-11-01 under his "Do items 1,2,3 owner items now." He did not choose it on a card. | the gloss names the file and the Conductor's ruling |
| "A player-truth is a plain sentence about the game that a person agrees with at once." | The pilot file defines a coded check swept over the whole input space offline. The draft let a sentence pass as a measurement. | the definition from `player_truth_testing_pilot_2026-10-26.md` |
| "The table shows the classes. The examples are not a complete list." | The old "That includes, and is not limited to" left the classes open too. The digest uses more classes (`art marks`, `bridge idle`, `leftovers`, `conductor act`, `ceiling release`). | "The table is not a complete list: other calls and other classes are also the agents' to decide." |
| "`refusal_contract.py submit` checks the record before it sends anything back." | The tool became the actor, and the judge lost its duty to run the check. | "The judge checks the record with `refusal_contract.py submit` before the judge sends anything back." |
| "cut his OWNER bridge hold inside 45 minutes" | The reader accepted it: the verb matches the four-acts paragraph. | none |
| "(§4.7)" and the move pointer | The reader confirmed: commit `ad403fd090` (2026-11-12) inserted item 6. | none |
| the other glosses (NONE/PLACEHOLDER/DONOR, shadow sheet, cut, token-blind, the hook path) | The reader confirmed each against its source. | none |

The reader's polish line: "A judge takes each taste call first" read as if the judge takes the call. The writer took it:
"Each taste call … goes through a judge first (§4)."

`debug_process.md` (6 meaning changes, all fixed):

| first draft | why it was wrong | repair |
|---|---|---|
| "Use no `$`-built commands. Use no game-mutating calls in a `live-proof` line" | The split made the `$` ban apply everywhere. `lightspeed-authoring.md` limits it to proof lines. | "In a `live-proof` line, use no `$`-built commands and no game-mutating calls." |
| "The owner superseded three points of the review:" | The old text does not say whose points they were. "The pilot" was hardly a GPT point. | the old "Superseded by the owner:" |
| "A seat can see (a) and (b) in …. That seat tells the owner" | The trigger "when they show" became a note on where to look. | the old "When … show (a) and (b), the seat that saw it tells the owner" |
| "record it, and carry on. Stop only if …" | The old text did not order a STOP. The new "Stop" read like the prior-pass-now-fail STOP. | "record it, and carry on, unless the red invalidates the reproduction or threatens state." |
| "The instruments are a script check, source, the log, and a mod-set bisection." | The list became a closed set. | the old "…that fits: a script check, source, the log, or a mod-set bisection." |
| "The guard does not write a list that has neither." | The doors write the list. The guard makes them refuse. | "A door does not write a list that has neither: the guard refuses that list." |

The reader confirmed each gloss (family script, walk, Lightspeed, live-proof line, smallest tier, owner mod, composed
mod, ablation, the GPT door) and the added cross-references. The writer also took one polish point ("So water, plants
and clutter cannot decide the result").

## Fixed on sight

1. **`delegation_policy.md` §5 pointed at the wrong judge-protocol item.** It said "adds the reason to the brief
   (§4.6)". Commit `ad403fd090` (2026-11-12) inserted the refusal-record item as item 6. So the brief-line rule is item
   7. The pointer now reads §4.7. A one-line move pointer under the §4 list says that a citation of §4.6 from before
   2026-11-12 means item 7. `design/RimMandrake/automated_art_evaluation_design_2026-10-23.md:398` is one such
   citation.
2. **The refusal message of `.claude/hooks/block_forged_validation.py` cited `delegation_policy.md` §2.1 for new
   north-star bars.** Since 2026-11-19 (commit `222065499a`), §2.1 is the live flight test of a flyer. The rule that
   agents may add new north-star bars is now under §1 (root `CLAUDE.md`: "Agents may add regression checks and new
   north-star bars (`design/RimMandrake/delegation_policy.md` §1)"). The hook now cites §1. The hook's selftest passes
   29/29.

## Conflicts (listed, not decided)

1. **Who binds a north-star line.** `debug_process.md` §6: "An agent may still draft north-star lines (DRAFT). Only his
   `modcheck validate --owner-said` binds them." Root `CLAUDE.md` lets agents add new north-star bars
   (`delegation_policy.md` §1), and `delegation_policy.md` §2 lets the Conductor add a locked bar. The hook
   `block_forged_validation.py` offers `validate --delegated --judge-verdict` for new bars and `--per-ruling` for the
   Conductor. The §6 line can be older than those routes. The Conductor decides.
2. **Long runs of game time.** `debug_process.md` §Test disturbances (owner, 2026-10-13): *"long runs are possible but
   risky … Avoid them when possible unless it's a clear win …"*. §Long-duration properties (owner, 2026-10-13): *"No
   more long runs, ok?"*. Both are his words on the same date. The file keeps both.
3. **The end of a live debug session versus the holding store.** Root `CLAUDE.md` §How we debug and
   `debug_process.md` §0.4: each live debug session ends with a check in the script. The last section of
   `debug_process.md` (owner, 2026-11-12): a defect that he reports in a look goes to
   `design/RimMandrake/validation_holding/`, and nothing from there is wired into a ladder stage, gate, nightly list or
   close check. The two can cover one defect. This run did not determine which rule wins for a defect that he reports
   in a look and that a session then debugs.
4. **Old section numbers in records.** Before 2026-11-19, `delegation_policy.md` §2 was "the short list" (2.1 was
   north-star bars). Some records still cite that numbering: `design/concepts/Contagion/` (`log.md`, `record.json`,
   `stage.json`, a result file: §2.1 for new bars), and the closed item `CARDS_ENFORCE_DELEGATED_CLASSES_STOP` (§2.4
   for twins). These are records of their date. This run did not edit them.

## Could not determine

| file | line | question | who would know |
|---|---|---|---|
| `delegation_policy.md` | "raise a cap, N or a stage ceiling" | what N is here (the slot count per seat of `slot_allocator.py` is likely, not confirmed) | the Conductor |
| `delegation_policy.md` | "the owner-only kinds of the Designer: a root, an exam waiver, a floor disable, a locked-tree change, a waiver" | the meaning of each kind | the author of `src/RimMandrake/rimflow/roles/designer.md` |
| `delegation_policy.md` | "inside the weekly partition that he set (card 2026-10-25)" | what the weekly partition divides | the Conductor; the `rimflow-operations` skill |
| `delegation_policy.md` | "lifting a coverage park" | what a coverage park is | the authors of `maturation.py` |
| `debug_process.md` | "(the driver does not record into `modcheck_status.json` today)" | whether "today" (2026-10-01) is still true | the authors of `northstar_driver` |
| `debug_process.md` | "one expectations_l2 batch" | what the batch does, in one plain sentence | `skills/live-debugging-proof-harness/references/traps.md` |
| `debug_process.md` | "the pilot (now a full stop and a new way of working)" | what the pilot of the GPT draft was; the prompt and answer in `Transient/debug_process_gpt/` are gone | the Conductor; git history of that Transient folder |
| `debug_process.md` | "the `code_review_status.py` discipline" | kept without a gloss; the sentence before it says what it means (any edit makes the record STALE) | none needed |

## What this run did not test

- No agent read the new files in a real run. No measurement shows that an agent acts better on the new text.
- No reader read the repairs after the two meaning reads.
- The last four sentence splits (the player-truth definition, the `art marks` bullet, the D4(a) gloss, and the Test
  Pilot cases) came after the meaning reads. The checks and the lint ran again after them.
- `selftest_conductor_authority.py` ran only on the new text. Its 6 failures name other files.
