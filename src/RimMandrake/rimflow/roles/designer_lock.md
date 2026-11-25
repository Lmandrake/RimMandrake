# Designer packet: Stage 5, Lock

The launcher injects this packet with `designer.md` at stage 5. Follow one versioned order, with no avoidable rework:

1. **The root is already his.** Stage 1 recorded his approval of the exact root text and its OWNER event. If the walk's
   root is not yet VALIDATED, the validation is his word or the Conductor window's act (owner 2026-11-19, --per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM --why on validate):
   `python3 src/RimMandrake/Utils/modcheck/cli.py validate <mod> --owner-said "<his words>"`.
   Suppose that the root was not validated before stage 3 wrote the tree. Then the `write` that stamps `root_hash` changes
   the tree, and the launcher reopens stage 3 and 4. So `return` to stage 2 with the decision "root validation". Do not
   rewrite here.
2. **The artifacts are frozen.** The tree, sheet, scenes and floor are those that stage 3 wrote and stage 4 examined.
   If any of them changed since, the launcher refuses a done result here.
3. **The coverage judge has signed, or said why not.** You never sign. Before this run started, the launcher ran
   `coverage_judge.py run <dir>` (role_launch `coverage_pre`). The judge is a fresh Opus run that did not make the tree.
   The judge read `designer_scene_contract.md`, this packet and the frozen artifacts, and judged coverage. The verdict is
   in `<dir>/coverage_verdict.json`.
   - On `covered`, the program signed (`concept_tree.py sign <dir> --by CoverageJudge`). The program writes a
     `rimflow note` on the concept's item that names the tree and sheet hashes. Then the program writes the stamp in tree.json.
   - Signed: commit tree.json and your seat's ledger shard. The gate wants both. The signature does not change the tree
     hash that the launcher tracks.
   - `not_covered`: each gap names `return_to` 3 (yours to fix) or 2 (needs his answer). `return` to that stage with the
     gaps as the decision. One pass lists all the gaps: its `checklist` has a row per inventory capability and leaf. Also
     put each `unchecked` id that the pass could not reach in your return. Then stage 3 fixes the whole list in one run.
   - No verdict (an error in the file): `blocked` on the error text.

   **When the judge stops.** The judge stops at the second `not_covered`, at a fourth judge run, or at judge spend past 4x
   its p90. Then the concept is blocked on `REFUSAL_NOTHING_COULD_EVER_PASS`, the Conductor is told, and this run never
   starts. Only `coverage_judge.py release <dir> --why ...` grants one more look.
   The second look only checks the repairs, gap by gap: `repairs` holds one answer per `gid`
   (design/specs/2026-11-17-judge-flaws-not-polish/7_same_problem_rule.md). A gap that the second look calls still open
   blocks as it was first written. A signature that the retired Arbiter already recorded still counts.

   **A re-judge sees only what you claim and what changed** (RIMMANDRAKE_REJUDGE_ONLY_CHANGED_GAPS). Every gap has a
   `gid` (`g1`...). The stage-3 run that reworks the gaps writes `<dir>/coverage_fixes.json`:
   `{"against": "<the verdict's judge>", "claims": [{"gap": "g3", "evidence": "<file and place that fixes it>"}]}`.
   - The next judge is shown three things: those claims, the entries that changed since the verdict (by hash), and the
     open gaps carried on file. The judge redoes only the checklist rows that these touch, and keeps the rest.
   - A gap you do not claim stays open unless the judge's own rows on all its ids read ok; then it is closed and listed
     as answered. When the judge answers `repairs`, that gap closes only when its slot (the judge's answer to that `gid` in `repairs`) also says repaired. A claimed gap
     closes the same way, never by the claim.
   - A new gap blocks only when it quotes a passage that a repair changed and a second reader confirms it a serious
     Problem. Any other new gap is advisory, on the owner's short list, and blocks nothing. The program puts that gap in
     `advisory_gaps` of `<dir>/coverage_verdict.json`.
   - No claim and no change: no judge runs.
   - A `coverage_fixes.json` against another judge is ignored. So the next round needs a new one.
   - A gap with `judge_fixed` was fixed by the judge itself, in `scenes.json`. Do not redo that fix and do not claim it:
     the next judge, a fresh one, checks it as a repair. If that judge fixes again, judging stops for the Conductor.

   **The owner may pass coverage on his own word**, past a `not_covered` verdict. That stamp is
   `concept_tree.py certify <dir> --owner-event OWNER:<tsn>` (`signed_by: owner`). The stamp is his, or the Conductor
   window's act under RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS (owner 2026-11-19; recorded
   `certified_by: conductor`, never as his words). The gate takes the stamp only on an OWNER.jsonl event, when all of
   these conditions hold:
   - the event holds his `ownerSaid` or `byCard`, or is that Conductor act;
   - the event is on this concept's item, on an item that a refusal record of this concept names, or on an item caused by
     one of these, directly or through a chain (`concept_tree.owner_event_problem`);
   - the event is newer than the verdict on file;
   - the stamp matches that verdict and the current `coverage_fixes.json`.

   Any other agent's `--why` or `--per-ruling` event certifies nothing. Lint and the other gate checks still run. Status
   and the lock page read "passed on the owner's word" beside the judge's verdict, never as a judge pass. You never
   certify.
4. **The gate**: `concept_tree.py gate <dir>` passes, and `designer_stage.py showcases <dir>` accepts the showcase
   set. The lock is refused while any record.json inventory capability has no showcase and no scene that exercises it. The program
   rechecks the scenes that the set names against the scene contract. A scene added since stage 3 is not trusted by its id.
5. **File the mod item**, `--kind mod`. Its `## verify` cites `design/concepts/<Mod>/tree.json` and the accepted tree
   hash. (A new mod under another kind escapes the gate.) The Maturation Pipeline builds the item from the locked bars
   (`design/specs/2026-11-13-maturation-pipeline.md`). FlowWorks and GSS (Gimme Some Slack) go the same way, as helpers
   that the Conductor launches. Before you file this item, every scene's missing entry point or control must be a filed
   build item. (The reset of a scene is harness housekeeping, never a mod item: owner 2026-11-17.)
6. Write `result.json` `done`. The launcher then marks the concept `locked`.

An edit, removal or waiver in a locked tree needs a `locked_change` decision. That decision is his word, or the Conductor
window's act (owner 2026-11-19: speaker conductor, delegated "conductor-act", source CONDUCTOR:<tsn>; a waiver names lost: and undo:).
A new concept comes back through the Designer as an amendment. Either gives a new hash and a new signature. A wrap-up that
matters is a scripted step or a check, never an instruction (owner, 2026-11-03, `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED`).

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.

## Known holes in the concept_tree gate

`concept_tree.py gate` has these limits. Read the tree yourself.

- A new mod filed under another kind with no citation escapes.
- A mod item may cite another mod's passing tree.
- `askcheck` catches a repeated waiver, not a rewording.
- The pruning check proves that a citation exists, not that the citation is good. That check wants an answer to "would you
  reject the mod on this alone?" for each leaf except an instrument leaf, in the `## pruning` section of the sheet.
