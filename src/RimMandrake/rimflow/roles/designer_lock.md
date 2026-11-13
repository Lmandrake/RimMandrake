# Designer packet: Stage 5, Lock

Injected with `designer.md` at stage 5. One versioned order, no avoidable rework:

1. **The root is already his.** Stage 1 recorded his approval of the exact root text and its OWNER event. If the walk's
   root is not yet VALIDATED, that is his word only:
   `python3 src/RimMandrake/Utils/modcheck/cli.py validate <mod> --owner-said "<his words>"`. If it was not validated
   before stage 3 wrote the tree, the `write` that stamps `root_hash` changes the tree, and the launcher reopens stage 3
   and 4: `return` to stage 2 with the decision "root validation" rather than rewriting here.
2. **The artifacts are frozen.** The tree, sheet, scenes and floor are those stage 3 wrote and stage 4 examined; the
   launcher refuses a done result here if any of them changed since.
3. **The coverage judge has signed, or said why not.** You never sign. Before this run started, the launcher ran
   `coverage_judge.py run <dir>` (role_launch `coverage_pre`): a fresh Opus run that did not make the tree read
   `designer_scene_contract.md`, this packet and the frozen artifacts and judged coverage; on `covered` the program
   signed (`concept_tree.py sign <dir> --by CoverageJudge`: a `rimflow note` on the concept's item naming the tree and
   sheet hashes, then the stamp in tree.json). Its verdict is in `<dir>/coverage_verdict.json`. Signed: commit tree.json
   and your seat's ledger shard (the gate wants both; the signature does not change the tree hash the launcher tracks).
   `not_covered`: each gap names `return_to` 3 (yours to fix) or 2 (needs his answer); `return` there with the gaps as
   the decision. One pass lists them all: its `checklist` has a row per inventory capability and leaf, and any `unchecked`
   ids it could not reach go in your return too, so stage 3 fixes the whole list in one run. No verdict (an error in the file): `blocked` on the error text.
   The judge stops at the third `not_covered` (or a fourth judge run, or judge spend past 4x its p90): the concept is
   blocked on `REFUSAL_NOTHING_COULD_EVER_PASS`, the Conductor is told, and this run never starts; only
   `coverage_judge.py release <dir> --why ...` grants one more look. So the first `not_covered` is the list to fix whole:
   each gap carries `new_since` (`unfixed`, `changed`, `regression`, `late`), and a `late` gap is the earlier judge's miss. A signature the retired Arbiter already
   recorded still counts.
   **A re-judge sees only what you claim and what changed** (RIMMANDRAKE_REJUDGE_ONLY_CHANGED_GAPS). Every gap has a
   `gid` (`g1`...). The stage-3 run that reworks them writes `<dir>/coverage_fixes.json`:
   `{"against": "<the verdict's judge>", "claims": [{"gap": "g3", "evidence": "<file and place that fixes it>"}]}`. The
   next judge is shown those claims, the entries changed since the verdict (by hash) and the open gaps carried on file;
   it redoes only the checklist rows they touch and keeps the rest. A gap you do not claim stays open; a new gap on
   anything it was not shown counts only tagged `late` with a reason. No claim and no change: no judge runs. A file
   against another judge is ignored, so the next round needs a new one.
   **The owner may pass coverage on his own word**, past a `not_covered` verdict. He did so first on ExplosiveKnockback on 2026-11-13
   (OWNER:1794608649743135329: "Yes, fix it like that, and then please record this as an actual Pass."). That stamp is
   `concept_tree.py certify <dir> --owner-event OWNER:<tsn>` (`signed_by: owner`), and it is his alone. The gate takes it only on an
   OWNER.jsonl event that holds his `ownerSaid` or `byCard`, names this concept's item, and is newer than the verdict on file. It must
   also match that verdict and the current `coverage_fixes.json`. An agent's `--why` or `--per-ruling` event certifies nothing, and
   lint and the other gate checks still run. Status and the lock page read "passed on the owner's word" beside the judge's
   verdict, never as a judge pass. You never certify.
4. **The gate**: `concept_tree.py gate <dir>` passes, and `designer_stage.py showcases <dir>` accepts the showcase set:
   the lock is refused while a record.json inventory capability is exercised by no showcase and no scene, and the
   scenes the set names are rechecked against the scene contract (a scene added since stage 3 is not trusted by id).
5. **File the mod item**, `--kind mod`, with `## verify` citing `design/concepts/<Mod>/tree.json` and the accepted tree
   hash. A new mod under another kind escapes the gate. The Producer admits it. Relentless runs `gate` at the pool, at the
   lease, and at `enrol`. FlowWorks and GSS go to Relentless like every other mod. Every scene's missing entry point,
   control or restoration step is a filed build item before this one.
6. Write `result.json` `done`. The launcher then marks the concept `locked`.

Changing a locked tree: his word only, for an edit, removal or waiver (a `locked_change` decision with his OWNER event); a
new concept comes back through the Designer as an amendment. Either gives a new hash and a new signature. A wrap-up that
matters is a scripted step or a check, never an instruction (owner, 2026-11-03, `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED`).

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.

## Known holes in the concept_tree gate
- `concept_tree.py gate` limits: a new mod filed under another kind with no citation escapes until `RA_S05_INTAKE_ENFORCE_TREE_FIRST`; a mod item may cite another mod's passing tree; `askcheck` catches a repeated waiver, not a rewording; the pruning check proves a citation exists, not that it is good. Read the tree yourself.
