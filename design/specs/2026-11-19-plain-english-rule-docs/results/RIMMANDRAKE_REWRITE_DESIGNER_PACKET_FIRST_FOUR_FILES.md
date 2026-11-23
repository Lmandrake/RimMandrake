# Result: `RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FIRST_FOUR_FILES`

Part 1 of batch 11 (`RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FILES_HASH_IN_STAGE_RECORD`) of `batch_plan.md`. Files:
`src/RimMandrake/rimflow/roles/designer.md`, `designer_grounding.md`, `designer_dialogue.md`, `designer_write.md`.
Run 2026-11-23. No `rm-role-designer*` unit was active at the start (the item's launch check).

Base: `d41afe8aee428811fbee2eaa7d27e1e9bb2d2ec5`

## What a changed packet hash does to an open concept (the batch's special rule)

Answer from `src/RimMandrake/rimflow/designer_stage.py` at the base commit: **nothing**. A changed hash is recorded, and
no code compares it.

- `open_run` (line 2084) computes `manifest_hashes(stage)` and stores them in `stage.json` as `running.manifest`. The
  packet text is built at the same moment, from the files as they are then (`packet()`, line 3397).
- `close_run` copies `running.manifest` into the accepted result entry as `manifest` (line 2696).
- No other line in `designer_stage.py` reads `manifest` from `stage.json`. No other `.py` file reads it
  (`git grep` for `["manifest"]` and `get("manifest")` over `src/`). The stale-input logic (`stale_stage`,
  `input_hash`, `INPUT_FILES`) reads only the concept's own files (`record.json`, `sheet.md`, `tree.json`,
  `scenes.json`, `floor.json`, `exam.json`), never a packet file.
- So an edited packet file does not reopen a stage, reject a result or void a run. A run that is open during the edit
  keeps the text that it got at open. The next run gets the new text and records the new hash.
- The hash is a record of which packet text each run read. Nothing more.

## Scores

| file | measure | before | after |
|---|---|---|---|
| `designer.md` | bytes | 23,703 | 25,024 |
| | words in linted prose | 3,273 | 3,456 |
| | STE violations per 100 words | 2.96 | 2.78 |
| | sentences over 20 words | 30 | 29 |
| | flagged lines | 3 | 2 |
| | the same file without the verbatim block (below): STE / long | 2.29 / 16 | 2.10 / 15 |
| `designer_grounding.md` | bytes | 5,878 | 6,259 |
| | words / STE / long / flagged | 870 / 2.41 / 1 / 1 | 930 / 2.15 / 1 / 1 |
| `designer_dialogue.md` | bytes | 8,815 | 9,415 |
| | words / STE / long / flagged | 1,341 / 3.21 / 6 / 0 | 1,432 / 2.79 / 3 / 0 |
| `designer_write.md` | bytes | 7,950 | 8,526 |
| | words / STE / long / flagged | 1,072 / 1.96 / 1 / 2 | 1,160 / 1.64 / 1 / 2 |
| all four | lines that a cold reader cannot act on (hand count, by the writer) | 24 | 0 that this run could resolve; 4 listed under "Could not determine" |

Two files miss the 2.5 target:

- `designer.md` (2.78). Lines from "## What a first version may contain" to the end of "## The fate of an extra" are a
  word-for-word copy of `roles/designer_cleanse.md`. `selftest_designer_first_version_rules.py` keeps the two copies
  equal. This part did not edit that block. The block alone scores 5.49, with 14 long sentences. Without the block the
  file scores 2.10. The block can change only together with `designer_cleanse.md`, in the part of this batch that owns
  `designer_cleanse.md`.
- `designer_dialogue.md` (2.79). 16 of its 40 violations are "would", "could" or "should" in tests that the rule needs
  ("would he reject the mod?", "could expose a different failure") and in his quotes. 11 are -ing forms, many in names
  ("Drawing requirements", "pruning question"). This run kept those words.

### The long sentences that stay

| file, line | kind |
|---|---|
| `designer.md` 3, 304 | a sentence that holds a command |
| `designer.md` 37, 39, 41, 43 | a sentence that holds a command (a "read first" pointer) |
| `designer.md` 92, 102, 107, 121, 140 | two short sentences that the lint joined at a bold lead |
| `designer.md` 133 | a sentence that holds a command |
| `designer.md` 199, 255, 292 | an owner quote (his card text; his 2026-11-15 words; his 2026-11-02 words) |
| `designer.md` the 14 in the verbatim block | not edited: a test binds the block to `designer_cleanse.md` |
| `designer_grounding.md` 24 | a sentence that holds a command (step 5) |
| `designer_dialogue.md` 28 | an owner quote, joined at a bold lead |
| `designer_dialogue.md` 72 | two short sentences that the lint joined at a bold lead |
| `designer_dialogue.md` 123 | a sentence that holds a command (the pruning question, a slogan kept word for word) |
| `designer_write.md` 44 | a sentence that holds a command |

The flags that stay: the 🔑 and 🔴 marks and **QUICK LOOK OFFERED** (the text that the launcher prints), and one
`pronoun` flag inside the verbatim block.

## Code that reads the files, and what the rewrite kept for it

- `selftest_designer_first_version_rules.py`: the verbatim block (unchanged, byte for byte); "One whole-mod check
  instead" and `2026-11-17T06:24:09Z`; "stage 4", "stage 5" and "still" near the third answer; "locked before" and
  "next version" before the block.
- `selftest_touching_code_cost_rule.py`: "§Touching code has a cost; if you see it, do it. File a repair ticket only when
  it passes test 1" and "Only `his_words` is his alone" stay.
- `selftest_rule_homes_in_briefs.py`: both home paths and the six section names stay.
- `selftest_self_fix_rule.py`: "The pipeline fixes its own defects" stays.
- `selftest_restart_now.py`: `designer.md` names `--now` exactly once.
- `selftest_conversion_owed.py`: `designer_write.md` does not say "biomes in scope only".
- `selftest_designer_stage.py`, `selftest_flagship_contract.py`, `selftest_designer_park.py`: packet assembly and the
  scene contract; unchanged behaviour.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| `designer.md` | "On demand." | a fragment with no subject | "The Designer runs on demand." |
| `designer.md` | "waits for a new press" | what a press is | the `run-now` command is named as the press |
| `designer.md` | "the stage's packet (`roles/designer_manifest.json`, hashed into `stage.json`)" | what a packet is | gloss from `packet()` in `designer_stage.py` |
| `designer.md` | "Floor:" | what the floor is | gloss from `designer_write.md`: the bar that every mod inherits |
| `designer.md` | "a worker and a Marker" | what a Marker is | gloss from `concept_agent_design_2026-11-01.md` |
| `designer.md` | "Gate A lint" | what Gate A is | gloss from `concept_tree.py`: the door lint, `concept_tree.py lint` |
| `designer.md` | "his queue line and his park page" | what the park page is | names `park_summary.md` |
| `designer.md` | "there is no share-built threshold" | a coined term | "no threshold for the share of the mod that is built" |
| `designer.md` | "Away, you park." (one 120-word paragraph) | what to park means; six rules in one paragraph | a definition, then one bullet per rule |
| `designer.md` | "at twice the item's cap" | which cap | gloss from `loop_ceiling` in `designer_stage.py`: the concept's budget cap |
| `designer.md` | "When only the reserve is left" | what the reserve is | gloss from `DEFAULT_RESERVE` in `designer_stage.py` |
| `designer.md` | "an OWNER-shard event" | what the shard is | names OWNER.jsonl |
| `designer.md` | "`his_words` (`## his words`)" | where the section is | names `sheet.md` |
| `designer.md` | "write hold-outs, or bind an oracle" | what a hold-out is; who binds | gloss from the design of record; "the Setter binds oracles" |
| `designer.md` | "It is recorded as above." | which record above | names the Conductor-act route (`concept_tree.py` help text) |
| `designer.md` | "Something you learn that no skill holds: …" (under "You must not") | the line read as a ban | moved out of the list as its own instruction |
| `designer_grounding.md` | "this project keeps having already built it" | the subject of "it" | "the thing is often already built" |
| `designer_grounding.md` | "GSS sitting 1" | what GSS is | "GSS (GimmeSomeSlack)", from `LEXICON.md` and the concept's `aliases` |
| `designer_grounding.md` | "an ask whose wording offers … is refused when … and refused outright when …" | two refusal cases in one sentence | two bullets |
| `designer_dialogue.md` | "the five moves, cheapest wrong version first" | where the five moves are | names §A turn with him |
| `designer_dialogue.md` | "as a Claim" | what a Claim is | "part 1 of a turn" |
| `designer_dialogue.md` | "Send none without one" | none of what, without what | "Send no ask without an `evidence_against`" |
| `designer_dialogue.md` | "apply the world's-logic test" | what the test is | gloss from `designer_examples.md` |
| `designer_write.md` | "Orthogonality chooses showcases" | a coined term | "the rule of very different functionality" |

Glosses added on the way, not counted above: the Setter's fields (`designer_write.md`, from `concept_tree.py`), which
tiers need `tier_reason` (`concept_tree.py lint`), and when `establishes` is needed (`designer_stage.py`).

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of new `designer.md` with the stand-alone code span `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` replaced and "45+ min" changed to "a long time" | 0 lost, exit 0. The id still stands inside a longer code span, so check 1 does not see the loss. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 1 lost (the 45), exit 1. Check 2 did not see the lost code span either, for the same reason. |
| check 1 | a copy with `RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED` replaced and "45+ min" changed | 2 lost (the path and the id), exit 1 |
| check 2 | the same copy | 3 lost (the code span, the id, the 45), exit 1 |
| check 1, each of the 4 files | the final rewrite | 52, 11, 11 and 11 items, 0 lost, exit 0 |
| check 2, each of the 4 files | the final rewrite | 200, 68, 47 and 86 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | — | PASS; 19 of 19 |
| the 9 rimflow tests named above, `selftest_skills_by_work.py`, `selftest_retired_era_gone.py` | the final files | PASS |

The blind area found by the first planted copy: when a code span is lost but its text stays inside a longer span, both
checks pass. The meaning read guards that case.

Names of people: this run read the diff for names. No person's name is in the four files. Conductor goes from 9 to 10
in `designer.md`, Marker from 2 to 3, Setter from 0 to 1; Setter goes from 2 to 3 in `designer_write.md`. Each increase is
a gloss. No name was lost.

### A test fixed on the way

`selftest_conversion_owed.py` failed on the base commit: "standing_rulings: his 2026-10-15 words stay". The test looked
for "we're not going to validate\nthat at this time" with a fixed line break. The rewrite of `standing_rulings.md`
(`d11bfc6623`) kept his words but wrapped the line at another place. This run changed the test to compare with
whitespace flattened. The test then passed. A copy of `standing_rulings.md` with his words changed still reads red.

## What the meaning read found

Four fresh Opus readers (rm-judge, model opus), one for each file, one at a time. Each reader got the old and the new
text and not the writer's reasoning. The readers found 10 lines. The writer repaired all 10. No reader read the repairs.

| file | first draft | why it was wrong | repair |
|---|---|---|---|
| `designer.md` | "The packet is the list of files for the stage in `designer_manifest.json`." | Too narrow. `packet()` also builds a header, a view of `record.json`, **What is already built** and other sections, and the file relies on them. | "The packet is the text that the launcher builds for the stage" with its parts listed. |
| `designer.md` | "Record that act in the same way as the delegated call." | Chose the evidence-for-ask route. `concept_tree.py` records a certification as a Conductor act under `RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`, `certified_by conductor`. | names that route |
| `designer.md` | "Define everything. Define only the core concepts …" | Under "You must not", the new order read as a ban on itself. | the second sentence goes in parentheses |
| `designer_grounding.md` | "Put each ruling that you use into `record.json`" | Narrowed "each one" (all his words: ledger events, north star, rulings) to rulings. | "each of his statements or rulings" |
| `designer_grounding.md` | "the bounded questions (the named uncertainties)" | Unsupported gloss. It could let a run skip the starting reads and steps 1-6. | gloss removed |
| `designer_dialogue.md` | "When the intent is genuinely unresolved, ask him …. Otherwise, do not ask." | Turned a limit into a duty; an exploratory question can settle the intent. | old sentence restored |
| `designer_dialogue.md` | "A fresh reviewer reads each ask" (turn part 5) | Narrowed the review of the whole turn to the asks. | sentence removed |
| `designer_write.md` | "The Setter is the agent that binds those fields; you only propose them." | The launcher owns `budget`; the Designer proposes only the oracle and the tier. | "The Setter binds `oracle`, `tier` and `guard`; the launcher owns `budget`. You propose only the oracle and the tier." |
| `designer_write.md` | "When a line sets `evidence_mode`, `establishes` names …" | `designer_stage.py` asks for `establishes` only in `compressed`, `decomposed` or `inferred` mode. | names the three modes |
| `designer_write.md` | "A live tier needs `tier_reason`." | `concept_tree.py lint` asks for `tier_reason` on every tier except `offline`, `quicktest` included. | "Live needs `tier_reason`" stays, and the lint's rule follows it |

After the repairs, this run split two more long sentences (the packet gloss in `designer.md`, the `establishes`
sentence in `designer_write.md`). The checks and tests ran again after that edit. No reader read those two edits.

## Conflicts (listed, not decided)

1. **Who certifies a first-touch pass.** `designer_grounding.md` §The first time an item names a mod: "Certify with him
   and clear up confusion." `designer.md` §Authority and provenance: since 2026-11-19 the Lock stage's first-touch
   certification is also the Conductor window's act. The grounding line can be older than the 2026-11-19 ruling. The
   Conductor decides.
2. **`tier_reason`.** The old line said "Live needs `tier_reason`". `concept_tree.py lint` asks for it on every tier
   except `offline`, so a `quicktest` leaf also needs it. The new text states both. If "live" in the old line was meant
   to cover `quicktest`, the two agree.

## Could not determine

| file | line | question | who would know |
|---|---|---|---|
| `designer.md` | "a worker and a Marker" | The Marker comes from the design of record (a retired-era "Relentless Setter and Marker"). Does a Marker still exist in the Maturation Pipeline, or is the word now the Pipeline's judge? | the Conductor; the author of `maturation.py` |
| `designer.md` | "The judge still stops at its second refusal, on one alarm." | what "on one alarm" means for the Designer | the author of `coverage_judge.py` |
| `designer_dialogue.md` | "Keep reviewed asks ready, taste first" | whether "taste first" means asks on taste come first in the order | the Conductor |
| `designer_dialogue.md` | "Ask the form per surface; never infer it." | what a "surface" is here (a screen, a sheet section, a scene) | the author of the 2026-11-02 dialogue rules (`designer_examples.md`) |

## What this run did not test

- No Designer run read the new files. `selftest_designer_stage.py` builds packets from them; no live stage ran.
- No measurement shows that a Designer run acts better on the new text.
- The repairs of the meaning-read findings and the last two sentence splits had no second meaning read.
