# Broaden: what a real user would try that I had not

## The question (to GPT via `src/RimMandrake/Utils/gpt_consult.py`, model gpt-6.1-sol, 2026-11-11 21:39 PST)

Given the statement, the item's spec, verify and criteria, `ledger_state.py`, `selftest_ledger_state.py`, the wake
function and a live 42-line sample for BENCH, plus how I had tested (a CLI-written test ledger, every section checked for
what must and must not appear, the 50-line and 160-column bound, a 400-item stress ledger, the live ledger read-only,
four mutations): *what would a real user try that I have not (someone new, someone experienced, someone trying to break
it, a messy real case)? Name the one or two most revealing tests. Is anything in the file misleading to a waking agent?*
The full question is `D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_ARCHMAGI_OFFLINE3\broaden_q.md`.

## The answer (verbatim)

The biggest remaining risk is **a freshly generated file presenting an old or incomplete instruction as actionable**. These two tests would be revealing:

1. **An instruction withdrawn without another `NEXT:`.**  
   Create an item with `NEXT: deploy the DLL`. Later, keep it open, block it awaiting owner approval, and add a plain note: “Deployment cancelled; wait for the owner.” Add eight doing items so the blocked item falls below the Open items cap, while its NEXT remains visible.

   Run the actual `handoff.py --wake` in a fresh subprocess, using the temporary ledger. Give a fresh agent the wake output and generated file; ask for its first proposed command, without executing it.

   **Pass:** it inspects the item or identifies the approval block. **Fail:** it proposes deployment. Also assert that the visible NEXT row communicates the current blocker. Currently it prints only `mine[iid].state`, omitting `blocked`, `needs`, and lease ownership; the later cancellation note does not invalidate the old NEXT.

2. **A consequential condition beyond the clipping boundary.**  
   Write a valid NEXT whose instruction starts “Deploy the DLL…” but whose final condition—“only after the owner approves; otherwise leave it untouched”—falls beyond the displayed width. Make this item appear among the eight visible NEXTs. Repeat with a long valid item ID.

   **Pass:** the reader recognizes the instruction as incomplete and retrieves `rimflow show <ID>` before acting; the output preserves the timestamp and clearly marks incomplete text. **Fail:** it treats the displayed prefix as sufficient authorization.

   Your live sample already demonstrates this risk: “restore it from that bundle … **if t…**” loses the condition. The stress test proves bounded length, but cannot establish that clipping preserves meaning.

Yes, parts could mislead a waking agent:

- **NEXT is historical advice attached to a currently open item.** Generating the file now does not make that advice current. Show current blockers, owner dependency, and lease holder alongside it, and explicitly require inspection of truncated instructions.
- **“Live helpers” establishes unexpired leases, not running agents.** After a reboot, those leases can outlive their processes. “Unexpired leases — worker activity unverified” would communicate what the ledger actually proves.
- A blocked item that is also doing or leased enters `inprog`, where its row **omits the blocked flag and reason**. That can conceal a stop condition even when the item is visible.

The first test checks whether the summary respects changed circumstances; the second checks whether compression changes what an agent believes it is allowed to do.

## What I tried, and what I found

1. **GPT's test 1, an overtaken NEXT.** I built it into the selftest: `NEXT: deploy the DLL`, then a block waiting on his
   approval, then the plain note "Deployment cancelled; wait for the owner." **Found: GPT was right.** The row printed only
   `proposed; NEXT: deploy the DLL`, with no block and no hint that anything came later. **Fixed:** every row now carries
   the item's standing (`BLOCKED: <reason>`, `needs owner`, `leased by <seat>`), and a NEXT row counts the ledger events
   recorded on the item after it, as in `⚠ 2 later events`. The heading says what a ⚠ or a cut (…) row means:
   `rimflow show <ID>` first. In-progress rows had the same gap (a doing+blocked item hid its block), now fixed too.
   I then gave the staged file to a fresh Opus reader that had never seen the code, and asked for its first command on
   that item. It ran `rimflow show`, citing the ⚠ and the block, and "would deploy nothing"
   (`evidence/fresh_reader_round1.md`, Part B).
2. **GPT's test 2, a condition lost to clipping.** It is real and only partly fixed. The stamp and the ⚠ are never cut
   (the action text is what gives way), and the heading tells the reader to open a cut row. The full text cannot fit one
   line, so the reader must follow the pointer. A 64-character id now drops the long flags before it would cut the stamp
   (selftest check).
3. **"Live helpers" overclaims.** It is renamed: "unexpired leases … (a lease is a claim on the ledger, not proof its
   worker still runs)". The ledger cannot see a process, so the label now says what it shows.
4. **The messy real case: a fresh reader on the real BENCH wake** (my own addition: ordinary use, not staged). This was
   the most revealing test. The reader found four things neither GPT nor my selftest had:
   - an owner note written `NEXT then: deploy … with him` was not read as a NEXT, so the file showed an older, wrong
     `NEXT: deploy Pyrelands DLL`. **Fixed:** the regex reads the spoken forms (`NEXT then:`, `NEXT (after X):`); the row now
     shows the owner's NEXT.
   - an open pointer (`RIMMANDRAKE_COMPARE_ARTISAN_WHITTLE_COST_PER_CLOSED_ITEM`) whose work a later ledger note reports
     done ("Comparison written") read as live work, and its status word `file` read like an order. **Fixed:** each open
     pointer prints `open (filed, never started)` and, under it, what the ledger recorded after the handoff with its
     newest note: `since the handoff: 2 ledger events; newest note 11-11 12:24 (BENCH): "Comparison written …"`.
   - the handoff's age was invisible (its NEXTs were 16 hours old). **Fixed:** "written 2026-11-11 05:56 PST, 15.9 h before
     this wake".
   - the handoff's game section ("NOT RUNNING … Bridge: FREE") contradicted the state file (game UP, bridge held), and
     nothing said which was current. **Fixed:** the state-file line in the wake carries `now: … game UP · bridge … (a
     game/bridge section above is as at the handoff)`.
   A second fresh reader, on the wake after these fixes (`evidence/fresh_reader_round2.md`), checked three items with
   `rimflow show` and found the file "right as of its own time". It treated the comparison pointer as done ("the
   comparison is already written") because of the new since-the-handoff line, and found two more problems: rows of up
   to 160 columns ran to about 64 rows on a 120-column terminal, and "open (filed, never started)" still read as an
   invitation to start. **Fixed at eb4690e8ff:** at most 120 columns, each NEXT row is two lines (stamp and standing
   first, then the action, which alone is cut), "this seat's 1819" in the heading, and "open (no start on the ledger)".
5. **A separate full-file code review** (fresh Opus, read-only) found seven issues, all now fixed with a selftest check
   each: the `CONDUCTOR` alias showed an empty seat; times were Pacific only because the host is; an empty `NEXT:` borrowed
   the next line; a non-string note text crashed the build; a long id cut the stamp; Designer turns were missing from
   owner-pending (the status board includes them); header fields were unclipped.

6. **The blind judge's first pass** (would show: yes) named two more, both fixed at dac52e2f15: an owner note
   "NOT BEFORE Wed 2026-11-11 ~3 PM PST. NEXT then: …" showed only the action, losing its date gate (a spoken-form NEXT
   now keeps the sentence it leans on), and the wake printed the handoff template's `<!-- -->` guidance (dropped).
7. **My own progress note** then broke the reader: "fixed (NEXT then: keeps its date gate …); NEXT: re-judge" showed
   the quoted spoken form and hid the real `NEXT: re-judge`, because an action ran to the end of the line. Fixed at
   d7ff8762de: an action ends at the next NEXT on its line. Selftest case added.

8. **A third fresh reader on the final code** (`evidence/fresh_reader_round3.md`) chose the right move on every pointer
   (comparison written, so it waits on the owner's read), honoured the date gate on the POCOCK row, and found its three
   spot checks right as of the file's own time. Its remaining complaints concern the old window's words or what the
   ledger does not hold (loops without leases, "waiting on you" files that are not needs=owner items). Out by design.

What remains: the live BENCH file is 45 lines at up to 120 columns: one screen on a 120x50 terminal. On an 80-column
terminal the long rows still wrap. A cut NEXT action needs `rimflow show <ID>`, which the file says.
