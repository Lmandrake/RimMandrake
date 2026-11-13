## spec
Owner fix D: after round one the coverage judge is given only the gaps the Designer claims fixed, the evidence for
each, and the material whose hash changed since the previous round. A new gap counts only if tagged late with why it
was not visible in round one. Measure tokens per rerun before/after on the saved EK rounds
(design/concepts/ExplosiveKnockback/).

Authority: owner ruling OWNER tsn=1794527688430451936 and card tsn=1794527885746395760 on RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS; Conductor brief 2026-11-12 (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Already landed before this: 5e1fb090e736 (third-refusal stop), 40fde3bc437f (refusal_contract.py). Context: EK overnight loop, design/concepts/ExplosiveKnockback/stage.json; spec design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md.

## Done when
Selftests: the rerun prompt carries only claims and changed material; unclaimed prior gaps carry forward unjudged;
no claims and nothing changed launches no judge; an untagged new gap on unchanged material is dropped and recorded.
A measured before/after packet size over the EK rounds is reported.

## Built (2026-11-12)
`coverage_judge.py`: every gap gets a `gid`, every verdict stores entry hashes (inventory, decisions, leaves, scenes,
showcases, rest rows, floor, sheet sections); `delta_plan`/`delta_prompt`/`delta_merge` run a round-2+ judge on
`coverage_fixes.json` claims plus changed entries; `plan()` skips when nothing is claimed and nothing changed. A legacy,
covered, errored or unchecked prior falls back to the full judge. Doc: `roles/designer_lock.md` item 3,
`roles/designer_write.md`. Test: `selftest_coverage_delta.py` (24 ok, 6 mutants caught); the three loop tests pin the
full path. Measured on the eight EK reruns (`D:\ClaudeWork\rimmandrake\designer_fixes_BCDE\measure_delta.json`,
script beside it; every prior gap claimed, so an upper bound): material handed to the judge 57.8k -> 13.9k tokens per
rerun (x0.24); scaling the measured billed 714k per rerun by that ratio estimates ~175k. An estimate: a judge may
still open files at a claim's evidence.
