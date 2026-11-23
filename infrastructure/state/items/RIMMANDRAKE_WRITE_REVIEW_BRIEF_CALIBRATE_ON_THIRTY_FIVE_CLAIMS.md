## spec
Filed 2026-11-18 about midnight PST by the detached run on `RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT`, as step 4 of that item: owed by the owner's
card of 2026-11-18 (`standing_rulings.md` §A boundary page before pipeline code). Not from a review finding.

Write the code-review brief for pipeline machinery (design `design/specs/2026-11-18-review-growth-cycle/01-design.md` section 5.3) as
`src/RimMandrake/rimflow/roles/code_review.md`: two looks per page version (one full inspection, one recheck of the
repairs), against the boundary page only; a finding is a Problem for one of three reasons, with the page quoted;
everything else is one line on `polish.md` or `next_version.md` beside the page. Add a `code_review` family to the
refusal contract (`refusal_contract.py`, `infrastructure/state/judge_calibration.json`) and calibrate it on the 35
claims of review rounds two to four with the analyst's labels, 4 problems and 31 polish [labels ~70%]:
`D:\ClaudeWork\rimmandrake\conductor\control_review_rounds_real_or_treadmill_20261118.md`.

Codex and GPT reviews of pipeline code run (owner, card 2026-11-23; `standing_rulings.md` §A boundary page before
pipeline code). They do not wait for this item. Running the calibration is a call to a review model: it needs the
Conductor's word first.

## refs
file: src/RimMandrake/rimflow/refusal_contract.py
file: design/RimMandrake/standing_rulings.md

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/code_review_brief_accept.py` exits 0 (4 checks).
- The Conductor has the calibration's result.

## verify
python3 src/RimMandrake/rimflow/acceptance/code_review_brief_accept.py   # exit 0
Acceptance test: watched failing on a6aac8a6fc7c: 4 of 4 fail. Expected: 4 pass.

## What the card said

<!-- answered 2026-11-19T08:39:22Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** The new review rule needs written instructions for the reviewer. We test the instructions before use: the reviewer sorts 35 old complaints, and we count how many it sorts correctly. Codex does the reviews, so the test calls Codex. Your stop says no Codex reviews of pipeline code. Do we run this test?
**Picked:** Run the Codex test once (Recommended)
**Its description:** Codex sorts the 35 old complaints one time. It reviews no new code and no ticket comes from it. I recommend it because reviews cannot restart without tested instructions. Cost: Codex tokens for one read of 35 complaints, amount unknown. Reviews stay stopped until you say start.
**Other options:** Test with Claude Opus, not Codex · Do not write instructions now
