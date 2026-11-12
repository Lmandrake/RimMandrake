# JUDGE: HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT

Judged 2026-11-11, around 22:25 PST, at HEAD a85f6f86fc, by a blind judge in the CLAUDE_ARCHMAGI_OFFLINE3 judge window. This replaces the earlier JUDGE.md in this folder.
I read STATEMENT.md, NOTES.md, the item file and every file in evidence/. I did not read DONE.md, BROADEN.md or PROMPT.md.
I ran the work myself. My outputs are in /tmp/judge_hs2/: wake.txt, selftest.txt, run_selftests.txt, queue.txt, owner.txt and show_sea.txt.
Nothing under src/ is modified against HEAD, so the code I ran is the committed code.

## Statement line

> Wake prints only next actions, open items and the last reply; then a one-screen state file generated from the
> ledger is done as `infrastructure/state/items/HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT.md` says, shown by fresh evidence.

**true.** Here is each clause of the item's spec, verify and criteria sections:

- **Half 1: the wake prints only the last reply, the carry-forward, owner-should-see, half-done, pointers with live state, game/bridge and the full path.** True.
  - My own `RIMFLOW_SEAT=BENCH handoff.py --wake` exited 0 and printed 71 lines (7242 bytes).
  - It printed the LAST REPLY between `<<<` and `>>>`, then the four `##` sections in this order: carry-forward, owner-should-see, half-done, game/bridge.
  - After them came the full-path line, then POINTER STATUS. That shows live ledger state for each pointer: CLOSED pointers are shouted, and each open pointer gets the newest note written since the handoff.
  - Last came the LEDGER STATE NOW line.
  - The only other text is the handoff's title and the two-line preamble under it.
- **Commits, closed/filed lists and the uncommitted list are dropped, and the file stays whole.** True.
  - Those sections, Traps included, are missing from my wake output.
  - The full file still has them. `BENCH_REBOOT_HANDOFF_202611111355.md` is 8531 bytes, and its game/tree section still holds the 23-line uncommitted block.
  - git shows no edit to that file since its handoff commit 2c55c24396.
- **The item's own byte measurement (14141 before, 9217 after, on `BENCH_REBOOT_HANDOFF_202611071817.md`).** I cannot reproduce the "before" figure, and nothing hangs on it.
  - That file is 12351 bytes and has not changed since 0bcd731141. So 14141 must have measured the old wake output, not the file.
  - The evidence re-measures the file at 12351 bytes against a 6694-byte view, which is smaller than the 9217 the item recorded.
  - Half 1 was already marked DONE in the spec. This is an old number, not a claim of this round.
- **Half 2: a generator writes a one-screen file with open items, owner-pending, live helpers and NEXT lines.** True.
  - `src/RimMandrake/Utils/ledger_state.py` writes `infrastructure/state/derived/state_now/BENCH_STATE_NOW.md`, and my wake regenerated it (mtime 22:23:59).
  - The file has 47 lines, at most 120 columns wide, with the four sections in order.
  - The code caps each section at 7 rows (NEXT at 6 two-line rows), so the file cannot pass 48 lines. It also has a hard cut at 50.
  - I checked the contents against the ledger independently:
    - **Open items:** "this seat's 1817". `rimflow queue BENCH` has exactly 1817 unique item headings, and the per-state tally adds up to 1817.
    - **Owner-pending:** "17 items … (10 more answered by him)". `owner_queue.py` says "17 truly his" and "10 answered".
    - **Live helpers:** 7 unexpired leases are listed, all 7 of them. My own lease is among them, which fits.
    - **NEXT:** I spot-checked the `SEA_FLOOR_AND_CATCH_PASS_1` row with `rimflow show`. Its newest NEXT is the 06:13:31Z note by CLAUDE_STEVEDESKTOP_OFFLINE4, which is 22:13 PST. Two events follow it (a release note and an OWNER reassign), matching "⚠ 2 later events".
- **Verify: a selftest builds a test ledger with `RIMFLOW_LEDGER`, checks each of the four sections and the one-screen limit, and the wake pointer names the file.** True.
  - I ran `selftest_ledger_state.py`: exit 0, 33 ok rows, 0 failures.
  - It covers each section, the ≤50-line and ≤120-column limits, a 400-item stress ledger (42 lines), the file landing under the test root rather than the real repo, and the wake regenerating the file and naming it.
  - `run_selftests.py --only selftest_handoff selftest_ledger_state` is GREEN, 2 of 2.
  - mutations.txt shows the selftest catching 15 deliberate breaks of the code. I did not re-run those mutations. I did read `ledger_state.py` in full, and the properties they target are visible in the code.
- **Criteria: under 50 lines on the live ledger, regenerates without a human, `--wake` points at it.** True.
  - The live file is 47 lines.
  - Every wake rewrites the file, and its header line carries "ledger as of" and "generated" times. regeneration.txt shows two wakes with a real ledger note between them: the NEXT row went from "third fresh reader" to "blind judge".
  - The seat with no handoff (CLAUDE_ARCHMAGI_OFFLINE3) is still pointed at its file.

## Where the evidence is flattering or thin

- **Regeneration happens on a wake (or a hand run), not on a timer.** A window that reads the file long after a wake reads stale state. The "generated" time on the header line is the only guard. The criteria ask for nothing more.
- **Live BENCH is at 47 of 50 lines,** close to the limit. The safety is the fixed caps, not luck. The NEXT section shows 6 of 183 items and defers the rest to `rimflow show`. The design accepts that.
- **The regeneration demo is self-made.** The ledger write between the two wakes is the builder's own note, 7 seconds apart. My own wake, run a minute later on the live ledger, regenerated the file too, so the claim stands.
- **The BENCH handoff the wake reads is 16.5 hours old.** That is real ordinary use, not a staged handoff.
- **The OFFLINE3 seat case is the idle path:** no handoff and 1 open item.
- **The overtaken-NEXT case is staged on a synthetic ledger** (staged_overtaken_next_STATE_NOW.md). The live file has real ⚠ rows too, and I checked one of them.

## Owed, outside this item's criteria (it does not falsify the line)

- **All three files are DIRTY under `code_review_status.py check`:**
  - `src/RimMandrake/Utils/ledger_state.py` and `src/RimMandrake/Utils/selftest_ledger_state.py` have never been marked clean.
  - `src/RimMandrake/Utils/handoff.py` has changed since its 2026-10-28 clean mark at 498429b05a.
  - The project rule says code is not clean until a full-file review says so. My read of ledger_state.py found no significant defect, but that read is not a mark-clean review.
- **The evidence/ files, DONE.md and PROMPT.md are modified but not committed at HEAD.** Commit them with the close.

would show: yes
