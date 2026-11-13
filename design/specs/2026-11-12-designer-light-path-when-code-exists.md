# The Designer's light path when code exists (spec, nothing built)

Date 2026-11-12. Item `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS`. Authority: owner card
OWNER.jsonl:1794527885746395760 ("Designer path" -> "Light path when code exists"), owner note
OWNER.jsonl:1794527688430451936 (fix E: "If we can insert an owner quick-look to settle a difficult or several questions
swiftly, offer that loudly."), Conductor brief 2026-11-12 (`CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`): write the spec,
do not build it. Nothing here is built.

Every number is tagged `[measured]` (read on 2026-11-12 from `design/concepts/ExplosiveKnockback/stage.json`,
`record.json`, or `D:\ClaudeWork\rimmandrake\designer_fixes_BCDE\measure_delta.json`) or `[estimate]`.

## 0. The short answer

When most of a mod is already built, the Designer stops writing a design for a builder and starts writing a check of
what exists. Stage 0 still reads everything. Stages 1 and 2 become one sitting with him, held over a first-look save
that a fresh judge looks at first. Stage 3 writes the tree from the inventory. Stage 4, the exam, is dropped. Stage 5
keeps the gate and one coverage judgement, followed by delta rounds. Expected cost is about 2M tokens a mod
`[estimate, range 1.5-2.5M]`, against about 3M today for a mod that walks cleanly. ExplosiveKnockback, which did not
walk cleanly, spent 90.0M `[measured]`.

## 1. Where the tokens went on ExplosiveKnockback

| stage | charges | tokens |
|---|---|---|
| 0-2 Read, argue | 3 runs | 0.55M `[measured]` |
| 3 Write | 14 runs | 49.9M `[measured]` (3.6M a run) |
| 4 Exam | 9 runs + 43 helpers | 31.9M + 1.64M `[measured]` |
| 5 Lock | 8 judges + 4 helpers + 2 runs | 5.71M + 0.16M + 0.2M `[measured]` |

The mod's cap was 4M. Of its 28 inventory capabilities, 20 have `impl: present` and 7 are `absent` `[measured]`. Of the
25 in scope, 17 are present, and only 1 has current proof (12 stale, 12 missing) `[measured]`. That is the case the
light path is for: the question is "does what exists do what he wants", and the walk spent itself asking "could a worker
misread this design".

B, C and D, landed today, cut the loop. B parks the walk when he is away (e3c6fa76427b). C sets a ceiling at twice the
cap (e3c6fa76427b). D makes each re-judge look only at what changed, 714k -> ~175k tokens a rerun `[estimate from
measured material x0.24]` (7a7f9bbc5dcb). The light path cuts the work the loop was repeating.

## 2. The rule that picks the path

At the end of stage 0 the launcher (`designer_stage.py`) computes `path` and records it in `stage.json`, next to the
inputs it used:

- **light** when both of these hold:
  1. `built_evidence(repo, mod)` finds the mod's `src/` tree, and that tree holds an `About/About.xml` plus at least one
     `Defs/**/*.xml` or `Source/**/*.cs`. In other words, there is a mod to load.
  2. At least one `record.json` inventory entry in scope (`scope` approved or opened_by_owner) has `impl: present`.
     There is no share-built threshold (owner, 2026-11-12: *"If any part of the mod is built, suggest a live walk of
     what already exists today before additional design is added." ... "No 2/3 needed."*). The path opens by proposing
     that walk, so nothing is asked of him that a look at the running mod would measure.
- **full** otherwise: the six stages as today.

The path changes only on his word on the item (`rimflow note --owner-said`), or when a stage-0 rerun recomputes it. The
packet states the path and the counts behind it.

E's rule is different and weaker: it owes a quick-look offer once any capability has `impl: present`. One built thing is
enough to look at. Building the design around what exists needs most of the mod.

## 3. The six stages on the light path

| stage | full path | light path |
|---|---|---|
| 0 Read | inventory, built evidence, three failure modes | **unchanged**; it also files the first-look save item (section 4) |
| 1 Argue the idea | root approved by him | **merged with 2**: the root is drafted from About.xml and the inventory, and approved in the same sitting |
| 2 Argue the edge | asks until none is sent | **one sitting over the first-look save**: every ask is a quick look (E) at a station or grid cell, and a capability he waves through is `approved` from his words |
| 3 Write | tree, sheet, plan, scenes, floor | **shrinks**: one leaf per in-scope capability, taken from the inventory; scenes only for a capability whose proof is not current and that no station shows; each absent capability becomes a filed build item and is not designed further; `plan.md` drops. One run, plus one rework at most |
| 4 Exam | exam.json passes, with helpers | **dropped**: the pre-looked first-look save and his sitting replace it, because there is no build left to misread |
| 5 Lock | gate, coverage judge, showcases | **kept, lighter**: gate, one full coverage judgement, then D's delta rounds; the showcase set is the save's station list |

Every gate that stays is unchanged. Budget, recovery and refusal never waive one, as today.

## 4. The first-look save and the pre-look judge

The standard is `RIMMANDRAKE_PREPARE_FIRST_LOOK_MATRIX_SAVEGAME`, which rewrites `design/RimMandrake/northstar_human_review.md`
into one doc. A save has numbered, labelled stations, one per capability. Where a variable matters, the save holds a
matrix grid: one cell with every fitting and facing, repeated over the variables, with a key sheet that names every
station and cell.

On the light path:

1. Stage 0 files `<MOD>_STAGE_FIRST_LOOK_SAVE` (`--needs bridge`), listing the in-scope present capabilities and the
   variables the inventory names. The Designer makes no code and stages nothing. A bridge seat builds the save, and the
   Designer waits on that item (`blocked`, `on`).
2. A fresh judge pre-looks the save (`design/RimMandrake/scene_look_judge_brief.md`): first "does anything look odd",
   then each station against what it claims. Nothing reaches him unread. A station that fails pre-look is fixed or
   marked on the key sheet before he sees it.
3. His stage 1-2 sitting happens in that save. The packet puts **QUICK LOOK OFFERED** first (E, already built). Each ask
   names the station or cell that settles it.
4. The keeper save is filed in the mod's `review/` folder. Stage 5's coverage judge reads its key sheet as the scene
   list.

The save costs bridge time outside the Designer's budget, roughly 1-2M tokens of a bridge seat `[estimate]`. It is the
first-look save the mod is owed anyway once the system calls the mod ready, so building it earlier moves that cost
forward rather than adding to it.

## 5. What the coverage judge still does

- It judges once at lock, in full: one checklist row per in-scope capability, each row naming the station, cell, scene
  or current proof that covers it. Gaps get gids.
- Later rounds are D's delta (`coverage_fixes.json` claims plus changed entries). With no claim and no change, no judge
  runs.
- C's ceiling (twice the cap) and B's away-park apply unchanged. The third refusal still stops the walk.
- What it no longer does: judge a scene written for a capability that a pre-looked station already shows. The key sheet
  row and the pre-look verdict are the evidence it checks.

## 6. Expected tokens per mod

| step | light path | basis |
|---|---|---|
| 0 Read | 0.3M | EK stage 0 `[measured]` |
| 1+2 one sitting | 0.4M | EK stages 1-2 were 0.25M `[measured]`; plus drafting the root `[estimate]` |
| 3 Write, one run + one rework | 0.8M + 0.3M | a tree copied from the inventory, with few scenes, against EK's 3.6M a run `[estimate]` |
| 4 Exam | 0 | dropped |
| 5 Lock: one full judge + one delta + the lock run | 0.35M + 0.15M + 0.1M | EK judges ran 0.63-0.79M on 41-56-row checklists `[measured]`; this checklist is about half that `[estimate]`; delta from D `[estimate]` |
| **total** | **about 2.4M at most; about 2M typical** | `[estimate]`, plus 1-2M of bridge time for the save (section 4) |

The saving over today's ~3M is moderate on a mod that walks cleanly. The large saving comes from removing the stage 3/4
rework loop, the 83M of EK's 90M `[measured]`, which the light path cannot enter. Stage 4 does not exist on it, and stage 3 is one
run plus one rework.

## 7. Open questions (each with a recommendation)

1. **The threshold for "code exists": settled by the owner, 2026-11-12.** Any built part is enough, and the first act
   is to suggest a live walk of what exists before design is added. No share-built threshold.
2. **Does the exam drop entirely?**
   - (a) Drop it. The pre-looked save and his sitting replace it.
   - (b) Keep one unhelped exam run, capped at 0.5M.
   - (c) Keep it as today.
   - **Recommend (a).** The exam asks whether a builder could misread the design, and on a built mod there is no builder
     left to misread it. EK's exam cost 33.6M `[measured]`.
3. **When the first-look save is built.**
   - (a) Before the stage 1-2 sitting, so he argues while looking. The cost is a bridge build before the design is
     settled.
   - (b) After lock only, as today's first look.
   - (c) A rough station save before the sitting, and the full matrix after lock.
   - **Recommend (a).** It is the only option that lets a look settle his questions, which is what E asks for, and the
     save is owed in any case.

## 8. What building it would touch (proposed, not filed)

- `designer_stage.py`: `path` at stage-0 done; the manifest picks packets per path; stage 4 skipped on light; stages 1-2
  merged; the filed save item and the `blocked` wait.
- `roles/designer_manifest.json`: light-path packets. `roles/designer_write.md`: the inventory-to-leaves rule.
  `roles/designer.md`: the protocol table gains the light column.
- `coverage_judge.py`: rows citing a station key. D already covers re-judging.
- Tests: the path rule on EK's record (light) and on a no-code concept (full); stage 4 skipped; the save item filed
  exactly once; the real alarm and told files untouched.
