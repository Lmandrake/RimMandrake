# RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN

## spec
The fourth clause of the pre-judgement certificate, `red_seen`, of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 4). After
RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN.
Protects against: a deciding test that cannot fail. Evidence: the Knockback cycle-3 judge filed
RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN (a gate whose OR passed green) and
RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST; ten of the Gimme Some Slack cycle-2 judge's planted faults were
weakenings of test files that nothing caught. That it would have caught the first is a guess (~60%): one probable
incident, so no backfill is ordered.

Build in `judge_certificate.py`: `red_seen(root, mod, test_id, patch=...)` (apply the patch, run the test, want a
non-zero exit, reverse the patch, prove the files byte-identical; a test that stays green is NOT recorded),
`grandfather(root, mod)` (written once), the verbs `maturation.py red-seen <Mod> <TEST> --patch FILE` and
`certificate <Mod> --grandfather`, and the clause: PASS on a recorded red for the test file as it is now, WARN
"grandfathered" for a test unchanged since the list was written, REFUSED for a new or edited deciding test with no
proof. Run `--grandfather` once for each advancing mod in the same change and commit the lists, so nothing that exists
today is refused. Tell the builders: the Stage 3 builder brief (`maturation.brief_text`) gains one line naming the verb.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
item: RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py --red-seen

## criteria
- A1: the acceptance test with `--red-seen` prints `PASS 28/28` and exits 0 (it reruns the first ticket's clauses).
- A2: the grandfather lists are committed for every advancing mod and `certificate` still certifies whatever it certified before this change.
- A3: one real test of one mod is proven with a real planted fault through the verb; the record is committed and named in the close note.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py --red-seen` exits 0 with `PASS 28/28`.
Watched failing at ed7e3b5389: `FAIL 2/28`, exit 1 (no module; the two that pass are the "source is restored" clauses, true
when nothing ran, which a correct build must keep). Not yet run against any implementation.
