# RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD

## spec
In-game (Stage 6), pre-human (Stage 7) and his-walk (Stage 8) evidence is not bound to one build: mod_sha is recorded
but never compared; no deployed hash, mod list or game build is recorded; Stage 7 has no brief, launcher or reader;
there is no pass record. Source: skeptical review 2026-11-15
(`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\claims_checked.md` A12;
`design/RimMandrake/maturation_pipeline.md` §9 "Designed but not built" and item 7). Partial already landed in
a3b3dead86b8: read_ingame_exit refuses a visit whose rows name more than one build.

## decision: what Stage 7 must show (2026-11-15, Evidence-for-Ask, delegated)
Taken under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME (no evidence against the obvious answer; it is
his own Stage 7 purpose plus the CARRIED outputs, made concrete).

Stage 7 shows, and its reader requires:
1. A fresh-reader consistency verdict over all the evidence, per his Stage 7 purpose: "Examine all the evidence as not
   merely sufficient but consistent and not containing obvious anomalies beyond the stated goals that would waste a
   human's review time."
2. A "known, not fixed" list (CARRIED).
3. A ranked walk brief: what to open, what to look at, and what changed since his last look (his card 2026-11-12).
4. The build identity, four parts, read on Archmagi when the walk savegame is made: mod source sha, deployed folder
   hash, the parsed ModsConfig activeMods list in order, and the game build. Every Stage 6 verdict is compared against
   it; any mismatch means a re-run, not a pass (his 18a: a verdict counts only on the version and list he walks).
   A minimal-list test counts when its list matches the modset_builder tier list from the same commit.
5. The pass record: date, git commit, bars, evidence, cost, cycles (Design Versions draft §3.7), plus that build
   identity.

Evidence against: none found; nothing of his asks Stage 7 to show less or other, and every part above is already in
his words or the CARRIED list. This unblocks the rest of this item (it already needs offline).

Builder also owes: update `design/RimMandrake/maturation_pipeline.md` §9 item 7 and the spec's Stage 7 marks in the same
commit.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_maturation.py`, new cases:
in-game rows on a mod_sha other than the stage's build refuse; a build identity with a different activeMods list
refuses; the Stage 7 reader refuses a missing part (verdict, known-not-fixed list, walk brief, build identity); the
pass record carries all fields.
