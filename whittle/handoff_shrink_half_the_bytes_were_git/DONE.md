# Done claim

- true: Wake prints only next actions, open items and the last reply; then a one-screen state file generated from the ledger is done as `infrastructure/state/items/HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT.md` says, shown by fresh evidence. | evidence: `whittle/handoff_shrink_half_the_bytes_were_git/evidence/wake_BENCH_live.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/BENCH_STATE_NOW_live.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/wake_CLAUDE_ARCHMAGI_OFFLINE3_live.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/CLAUDE_ARCHMAGI_OFFLINE3_STATE_NOW_live.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/half1_bytes.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/regeneration.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/selftest_ledger_state.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/mutations.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/staged_overtaken_next_STATE_NOW.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/review_passes.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/code_review_status.txt`

All evidence was regenerated at e4da6e13f6 (the last code change is 7149527f48), at 23:58 PST on 2026-11-11.

## How each part of the item reads in the evidence

**Half 1** (`half1_bytes.txt`, and the top of `wake_BENCH_live.txt`):
- The wake view of the live BENCH handoff keeps the one thing to carry, what the owner should see, what is half-done, and game/bridge.
- It drops the traps, the closed and filed lists, the commits, the uncommitted list and the template's `<!-- -->` guidance.
- Its closing line names every heading it left out and gives the full path. The file itself stays whole.
- The item's own measuring file re-measures at 12351 bytes whole against 6785 bytes in the view.
- The last reply comes first.

**The pointer lines now carry the ledger's real state** (`model.replay`):
- A pointer to an item that is done, dropped or superseded is shouted CLOSED. A superseded one names the end of its successor chain and that item's state.
- An open pointer gets its state, BLOCKED if blocked, and its owner when that is another seat. Below it comes the newest note written since the handoff.
- Pointers are only the ids in what was printed.

**Half 2:**
- **Generator:** `src/RimMandrake/Utils/ledger_state.py` writes `<state>/derived/state_now/<SEAT>_STATE_NOW.md`, gitignored, beside the ledger in use.
- **The four sections,** shown in `BENCH_STATE_NOW_live.md`:
  - open items: this seat's, by state, each with its standing: BLOCKED with its reason, an owner `WAITS until`, needs, lease;
  - owner-pending: owner_queue's answer, across every seat;
  - live helpers: unexpired leases, across every seat;
  - NEXT lines: the newest `NEXT:` on each open item, with its writer, its Pacific time, and ⚠ if the ledger has moved since.
- **Selftest:** `selftest_ledger_state.txt` runs on a `RIMFLOW_LEDGER` test ledger written by the real CLI.
  - 46 checks, 0 failures; `run_selftests.py --only selftest_handoff selftest_ledger_state` GREEN.
  - It checks each section for what must and must not appear, and the bounds of ≤50 lines and ≤120 terminal columns.
  - It also checks the wake regenerating the file and naming it.
- **Mutations:** 31 deliberate breaks each turn a selftest red (`mutations.txt`): the 15 from earlier rounds and one per fix this round.

**Criteria:**
- **Under 50 lines on the live ledger:** BENCH, the busiest seat with 1824 open items, is 41 lines, and the caps bound any ledger at 48. A worker seat is 23.
- **Regenerates without a human:** every `handoff.py --wake` rewrites it. `regeneration.txt` shows two ordinary wakes around a real ledger note, and the second shows the new NEXT.
- **`--wake` points at it:** the `LEDGER STATE NOW …: <path>` line under the pointer block, with a `now:` line giving game and bridge as the ledger has them.

**This round: five reviews** by fresh Opus reviewers (`review_passes.md`). Three found real defects that ordinary use hits, and all are fixed:
- 132 open items were shown as "CLOSED -- do NOT act";
- the hidden filed list (another seat's items included) came out as "open pointers — pick each up";
- an owner wait never showed;
- `CONDUCTOR_HANDOFF_*` files and `RIMFLOW_SEAT=Conductor` were invisible to BENCH;
- heading variants and fenced `##` lines dropped text;
- a trailing empty NEXT discarded the real one;
- lease ends had no date;
- CJK text was clipped by characters, not columns;
- the selftest had a 1 December date bomb.

The fourth pass found nothing significant. The fifth, a full-file review of `handoff.py` and both selftests, found the same last-verb defect on the write side: the `--check` gate listed 63 done items of 146 as still doing. That is fixed too, the gate now lists 30 with none done, and the re-review is CLEAN. All four files read CLEAN under `code_review_status.py` (`code_review_status.txt`).

- `--check` and the write mode's still-doing gate and closed/filed lists read `model.replay` too.

## What I'm least sure about
- "One screen" assumes a 120x50 terminal. On 80 columns the long rows wrap.
- A NEXT is the action as its writer put it. ⚠ and … mark a moved or cut row, but nothing can tell whether the action still holds. The file says to run `rimflow show` first.
- "Live helpers" means unexpired leases. In tonight's live file it reads 0, because the lane loops are stopped (token alarm) and my own lease had lapsed. The selftest covers the non-empty case, but the live file does not show one right now.
- BENCH's open-items section shows 7 of 1824 rows, all in-progress work, so "next to offer" rows never fit on BENCH today. `rimflow next` and `rimflow queue` answer that, and the row says so.
- The write mode's "Closed since the last handoff" list has no cap (1394 rows for a window since 11-01). The wake hides that section, and this predates the item.

## What I did not test
- A wake on SteveDesktop or the Mac. The TZ case is in the selftest; the machines are not.
- The Windows Terminal profile's own wake prompt. I ran the same command on the same live ledger.
- A second, different-model broaden this round (GPT). The token alarm held it back, and the earlier GPT broaden stands.
