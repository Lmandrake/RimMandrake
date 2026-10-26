# Cards for your next session (drafted 2026-10-26 for 2026-10-27)

## Summary (10 lines)
1. Twelve cards: five answer your questions of 2026-10-26 (Q1-Q5); seven are the one-primary cards D1-D7 as changed by the GPT review.
2. Q1 BENCH's memory: BENCH cannot restart itself; automatic compaction is its restart, and an existing hook repairs a missed handoff after it. Recommended: keep BENCH thin and make that repair trustworthy (its counter reads 100% MISSING today, a fault).
3. Q2 Seeing what is running: the queue lists 123 items as "being worked", and none of them has a live claim. Recommended: one "now" record built from running workers, not from the queue.
4. Q3 Focus: our numbers do NOT clearly show that focus closed more mods, because nothing records "this mod is finished". Recommended: a FOCUS lane for 1-2 named mods, each with a written finish list.
5. Q4 Blocked-by: the queue can say "this waits on that", but only one link per item, and only after something has gone wrong. Recommended: a planned "after" link set when work is filed.
6. Q5 This week's plan: since 10-19, 799 of 823 closed items carry no check level at all. Recommended: a tick counts only when a check at the level the plan asked for has passed.
7. D1-D7: same shape as before. Changes: D2 becomes "pilot only", D3 now has conditions, D6 lets running workers finish their item, and D7 gets a longer drill and stricter rules for retiring the old window.
8. One clash to settle: "one worker per mod" (D1) and focus (Q3) pull against each other. Q3's recommendation narrows the rule to one worker per C# project, and D1 and D3 are written with that narrower rule.
9. No screens are proposed. Each card names only the data and the rule that would produce the answer.
10. Not measured: whether focus really closes mods faster;  whether "dependencies" would be kept true.

Words used throughout:
- **Item**: one piece of work in the queue.
- **Ledger**: the append-only log every agent writes. Each item's state comes from it.
- **Close**: an agent marks an item finished against a commit.
- **Check level L0-L4**: how strongly a piece of work was checked.
  - L0: offline tests.
  - L1-L2: in the running game.
  - L3: a second AI judges the result.
  - L4: you look at it.
- **Engine**: the planned no-AI timer that starts one-item AI workers. It is not built.
- **Tokens**: the unit AI use is metered and paid in; a weekly allowance caps them.
- **Hook**: a small script Claude Code runs automatically at set moments (for example before every turn).
- **C# project**: the one build file that compiles a mod's code into its DLL. Two workers editing it at once is what collided on 09-26.
- **GSS**: the FlowWorks pipe-network work stream (BENCH's lane since 10-23).
- **Bridge**: the link that lets an agent drive the running game; a "bridge hold" says who is driving it.

---

## Q1. How does BENCH look after its own memory, so you don't have to?

**Your words (2026-10-26):** "how does Bench self-manage its context so I don't have to?"

**Facts:**
- BENCH is one long conversation. Every turn re-sends all of it. When it gets full (the "context"), Claude Code shrinks it to a summary ("compaction"), and details are lost.
- Three guards exist today:
  1. **A compaction checklist** (`CLAUDE.md` § Compact Instructions). It tells the summary to keep seven things word for word: open next steps, your rulings, bridge holds, running helpers, uncommitted files, unfiled lessons, and a "HANDOFF OWED" flag if no handoff was written.
  2. **The handoff ritual.** Before it ends, a session writes a file under `infrastructure/state/handoffs/` (191 files so far). The next session reads it on waking. Handoff commits ran at 1-9 a day from 10-19 to 10-26.
  3. **A warning on the status line**, at 60% full ("hand off soon") and 85% ("HAND OFF NOW") (`~/.claude/statusline.sh` lines 226-236).
- **The gap:** the status line is drawn on your screen, not put into BENCH's conversation. As far as we know, BENCH never sees its own warning; we have not proven this with a test. On the phone you may not see it either. If that holds, today the warning only works if a human notices it.
- **Measured on 09-17** (`infrastructure/agents/BENCH.md` line 61): 60% of the next steps written in handoffs died unread. The wake step that now prints each open step was added because of that.
- **The one-primary design (D1) shrinks the problem.** BENCH would keep only your conversation and the live game work you do together; queue work goes to one-item workers that start fresh. BENCH still fills, but far more slowly than today.
- **BENCH cannot restart itself.** It cannot type `/clear` into its own window, and a restarted process would lose Remote Control (only a human can turn that back on). Your correction, 2026-10-26: *"Bench can't handoff and restart bench, can it?"* So a fill warning delivered to BENCH buys only one thing: writing the handoff a little before automatic compaction instead of repairing it after.
- **The repair-after already exists.** `~/dev/Lodestar/bin/hooks/compaction_watch.py` (owner, 2026-10-22) runs on every compaction: before it, it logs whether a handoff was written; after it, it tells the resumed BENCH to push you a notice and, if no handoff was written, rebuild one from the transcript on disk. Compaction is, in effect, BENCH's restart.
- **Its counter is not trustworthy yet:** `D:\ClaudeWork\logs\compactions.jsonl` lists 435 compactions under the BENCH clone, 203 of them today, and every one says handoff MISSING. A 100% reading is an instrument fault until proven otherwise; helpers working in the same folder are probably logged as BENCH (filed: `COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT`).

**Options:**
1. **Compaction is the restart; make it lossless (recommended).**
   - How: keep automatic compaction; keep BENCH thin (chatty work in helpers, so it fills slowly); fix the compaction counter so it counts only the seat and judges the handoff correctly; put "compactions without a handoff" in the digest.
   - Trade: no new hook, nothing for you to watch. Some nuance from the hurried summary is still lost, recovered from the transcript on disk.
2. **Also feed BENCH its fill level** (the earlier recommendation, withdrawn).
   - Trade: lets BENCH write the handoff before compaction rather than after. Small gain, a per-turn hook, and it cannot restart anything.
3. **You restart BENCH on a timetable** (for example each morning: `/clear`, then "wake").
   - Trade: a clean start for about 47,546 tokens (two probes, 10-26), but it needs your hand at the window, which is exactly what you asked not to do.

---

## Q2. How can you see what is being worked on, without logging in?

**Your words:** "How can I track work being done so I'm aware?"

**Facts:**
- **What exists:**
  - **RimPulse**, the dashboard. A collector reads the ledger every 5 seconds. Its pages are `/brief` (status), `/streams` (flow numbers, refreshed every 15 min), and a "to look at" list of things handed to you.
  - **Two digests a day**, built at 05:45/06:00 and 17:15/17:30. A second reader checks every line against the ledger.
- **Two problems:**
  - **Reach.** RimPulse pages are reachable only from the home network (Tailscale), and your phone is not on it. Nothing is pushed to you.
  - **"Being worked" is not true.** Measured just now (21:52 UTC): 123 items are marked "doing". 0 of them hold a live claim (a claim lasts 45 min and is renewed while someone works). 49 have lapsed claims and 74 never took one. So the queue cannot tell you what is actually running.
- **Data that would answer "what is happening now":**
  1. Running workers, read from the engine's own process list and claim renewals, never from the "doing" label.
  2. What changed in the last 12 h: built, checked, failed, blocked.
  3. What needs you, and how long it has waited.

  All three come from the ledger plus the engine's journal. None needs a new screen.

**Options:**
1. **One "now" record, built from running workers, delivered by the digest and up to 3 pushes a day (recommended).**
   - Why: it fixes the false "doing" count at the source, and it reaches you without a log-in.
   - How: the collector writes the record every 15 min. The twice-daily digest is published where your phone can open it (a claude.ai page), and pushes follow D4/D5.
   - Trade: you see real activity, with reasons. But it needs the engine (or claim renewals by BENCH's helpers) to be truthful, and a phone route (D4).
2. **Fix only the "doing" label.**
   - Why: the smallest change. Anything without a live claim is shown as "not being worked" (its state is untouched).
   - Trade: an honest "being worked" count at once. But BENCH's own helpers often take no claim, so their real work would show as idle until they do. But you still have to open RimPulse from home to see it.
3. **Push every change as it happens.**
   - Why: nothing is ever missed.
   - Trade: complete. But it would be dozens of messages a day (513 closes today alone), which is the noise D5 caps at 3.

---

## Q3. FOCUS: grinding 1-2 mods to finished

**Your words:** "if there's only one agent per mod, that implies we will always be working on many mods again. We only started making real progress closing mods when we focused hard on 1-2 at a time. ... what we will have in place to bring back that intense focus".

**Facts:**
- **There is no "mod finished" record.** Items carry no mod field (we matched mod names inside item names to count). The automated mod check ("modcheck GREEN") is the nearest thing we have, and it is not your acceptance.
- **Measured, by week:**
  - "focused commits" are commits that touch 1-3 mods.
  - "top-2 share" is the share of those commits that went to the two busiest mods.
  - "first GREEN" is the first time a mod's automated check passed.

| week starting | mods touched | top-2 share | top 2 | first GREEN | L3/L4 passes |
|---|---|---|---|---|---|
| Sep 7 | 55 | 38% | UtinniPatches, Droidworks | 2 | 0 |
| Sep 14 | 55 | 47% | UtinniPatches, SWBestiary | 1 | 0 |
| Sep 21 | 61 | 38% | UtinniPatches, TerminalBiomes | 0 | 0 |
| Sep 28 | 93 | 15% | UtinniPatches, Stillsand | 5 | 0 |
| Oct 5 | 107 | 27% | FlowWorks, GimmeSomeSlack | 6 | 3 |
| Oct 12 | 44 | 54% | FlowWorks, Pyrelands | 0 | 2 |
| Oct 19 | 64 | 61% | FlowWorks, UtinniPatches | 0 | 6 |

- **What the table says:**
  - 11 of the 14 mods that ever passed the automated check first passed in the two weeks of Sep 28 - Oct 11. Those were the MOST spread-out weeks.
  - In the two FlowWorks focus weeks (Oct 12-25), the top two mods took 54-61% of focused commits, with FlowWorks first both weeks. FlowWorks alone took 56-63% of the closes that name a mod. Those weeks show 0 first passes, but 8 higher-level passes (L3/L4).
- **So our data neither confirms nor refutes your memory.** The reason is the missing "finished" record: we cannot count mod closures, only stand-ins for them.
- **What is not measured:** whether a focused mod finished faster than it would have otherwise. FlowWorks is not recorded as finished.
- **The clash:** the GPT review's rule, "one worker per mod at a time", exists because workers editing the same C# project file collided when merging (09-26). With only 1-2 focus mods, that rule caps focus at 1-2 workers.
- **What exists:** CRUNCH ("crunch on X by Friday": every slot on one path) is written in the operating-modes design. No code for it exists.

**Options:**
1. **A FOCUS lane: you name 1-2 mods, each with a written finish list (recommended).**
   - Why: it gives "finished" a definition we can count, and it puts the work where you said progress came from.
   - What a finish list is: each line is a check at a stated level, for example "L2: pump fills tank in game" or "L4: you walk the biome".
   - How:
     - The engine gives focus-mod items first pick of every free slot.
     - Inside a focus mod, workers split by kind of work: art, XML, checks and the game run in parallel, and only C# is limited to one worker per project. This narrows D1's rule to the thing that actually collided.
     - Other mods get leftover slots, verify work only.
     - The digest reports "list lines passed / total" each day.
   - Trade: you get focus you can measure, and a real "mod finished" date. But you must write or approve each finish list (about 5 min a mod), and other mods stall while it runs.
2. **Focus by order only, keeping strict one worker per mod.**
   - Why: it is the safest for merges.
   - Trade: fewest merge collisions (it prevents the 09-26 kind; edits to files shared across mods can still collide). But at most 2 workers ever touch your focus mods, so "intense" focus becomes slow focus.
3. **CRUNCH as designed: a goal and a date, every slot on that one path.**
   - Why: it is already designed, and good before a deadline.
   - Trade: as strong as focus gets. But it needs a date, it sends every other stream to 0, and it has no finish list, so "done" is still whatever agents close.
4. **No focus mechanism; the allocator spreads work as now.**
   - Why: the most throughput on paper.
   - Trade: nothing to build. But it is the many-mods mode you asked us to leave.

---

## Q4. "Blocked by" links, so the plan can be computed

**Your words:** "it seems potentially valuable to use 'blocked by' when we plan out tickets so that there's some shadow of the plan that can be computed and tracked."

**Facts:**
- **The queue already has a "waits on" link**: `block --on <other item> --until built|validated|done`. It has three limits:
  - one link per item;
  - it marks something as WRONG right now ("blocked"), not as planned order;
  - it never lifts itself: an agent must unblock by hand.
- **Measured:**
  - 387 block events since 08-21, of which 99 named the item they waited on.
  - Right now: 114 items are blocked, and 48 of them name a blocker.
  - A replay on 10-25 found 21 of 73 named blocks outliving their blocker, six of them by 7-21 days.
- **What a plan needs:**
  - several "after" links per item, set when the work is filed;
  - "ready" worked out from those links;
  - from the links, three answers: the longest chain of links to each goal, what is ready now, and what is waiting on what.

**Options:**
1. **A planned "after" link, separate from "blocked" (recommended).**
   - Why: it lets the plan's shape be computed, and it keeps "wrong" and "not yet" apart.
   - How: when an item is filed, it can name one or more items it comes after (`file --after X --after Y`). The queue offers it only once they reach the stated level. A check flags links to dropped items, loops, and items that have waited longer than a week on one link.
   - Trade: you get the dependency chains toward each goal, a ready list and a waiting list (a true critical path in time would also need size estimates per item, which `--kind`/size labels could supply later). But it is a medium build in the queue's core, with tests. And a wrong link to a live item ("after X" when X was not really needed) holds work back; no check can catch that, only the weekly-wait flag hints at it.
2. **Reuse "blocked" for planning, allowing several blockers.**
   - Why: there is no new idea to learn.
   - Trade: a smaller build. But "blocked" keeps meaning both "broken" and "later", and unblocking stays manual, which is the 21-of-73 problem above.
3. **Keep the plan's links in a separate weekly plan file, not in the queue.**
   - Why: quickest. One file per week.
   - Trade: about an hour to start. But two sources of truth drift apart; the GitHub ticket mirror (Q5) was such a second copy, though its retirement note records no reason.

---

## Q5. "This week's plan", ticked off only when REALLY done

**Your words:** "I really need some kind of 'this week's plan' shown graphically and parts being ticked off as we go... REALLY ticked off, not just 'text generated towards code' as it is today. ... We have UtinniControl room and a bunch of other past attempts at this same need. DON'T build any UI right now."

**Facts: why the past attempts fell short.**

| attempt | when | what it showed | why it fell short |
|---|---|---|---|
| Goal sheet (`infrastructure/state/GOAL_SHEET.md`) | 08-21, last edited 09-10 | everything that must be true before play | ticked by hand in prose, with no evidence link, and stale for 46 days |
| Ticket board + GitHub Project mirror | 08-29 to 09-11 | kanban and a link graph over GitHub issues copied from the queue | a second copy of the queue; retired by your ruling on 09-11 (the retirement note gives no reason) |
| Utinni Control Room hub (`infrastructure/dashboards/hub/`) | built 09-11, data last rebuilt 10-02 | tabs for code health, maturity, world map and art | every publish needed an AI session, so it went 24 days stale; it had no plan or week view |
| Project maturity dashboard | 09-08 to 10-22 | each feature's level, from planned to played | levels set by agents with a command (`rimflow capability set`), not by passing checks; its last data (09-26) said 0 of 58 features "played" |
| RimPulse (live since 10-08) | now | incidents, things to look at, flow numbers | it measures flow, not a plan; home network only |
| "By your return" plan in RimPulse | built today, 10-26, never used for real | a short plan with on track / behind | a tick is "the queue says done", the same problem |

- **The common thread:** where these showed progress at all, it was someone writing "done" or setting a level, never a check passing.
- **Measured:**
  - Since 10-19, 823 items were closed. 799 of them carry no check level at all.
  - Ever, only 13 items have a passing L3 (second AI) or L4 (your eyes) check.
  - Today 391 of 513 closes were never started (bulk or paperwork closes; orchestration review §(b)).
- **Data that gives a REAL tick:**
  1. The week's plan is a list of items (or Q3 finish-list lines), each with the check level it owes.
  2. A line is ticked only by a passing check event at the level the line owes (L0-L4), with an evidence path, recorded by someone other than the worker who built it.
  3. Each day records three counts: planned, built (the item reached the queue's "built" state, which needs a published commit; a bare close does not count), and verified. That gives the picture: one bar each.

**Options:**
1. **Ticks come only from passing checks at the owed level (recommended).**
   - Why: it is exactly "REALLY ticked off". A close with no check shows as "closed, not checked", never as a tick.
   - How:
     - On Monday, one card sets the week: at most 10 items, or 1-2 finish lists.
     - The digest reports "verified X of Y" twice a day.
     - Later this extends the "by your return" plan to a week; the data is already in the ledger.
   - Trade: honest progress, and the gap between built and verified becomes visible. But early weeks will likely look slow: 343 items are built and unchecked right now, a backlog checks must work through.
2. **Ticks from closes, as the existing "by your return" plan does.**
   - Why: it works today.
   - Trade: no build. But it is the "text generated towards code" you rejected.
3. **Only your own look ticks a line (L4 for everything).**
   - Why: it is the most trustworthy.
   - Trade: as real as it gets. But it costs your time on every line; only 7 L4 checks have ever been recorded.

---

## D1. The shape: who does what

**Facts:**
- Today there are two AI windows: **BENCH** (talks with you) and **FOUNDRY** (works the queue). FOUNDRY sits idle until someone wakes it: its longest ledger silence since 10-22 was 23.2 h.
- **The proposal:**
  - BENCH stays your one window.
  - A no-AI timer (the engine) starts one-item AI workers every 2 minutes, within the allowed count N.
  - Each worker does one item and exits.
- **Two additions from the review:**
  - **An attempt number on each try**, so a late, stale worker cannot close or publish. 19 contested claims are on record.
  - **One worker per mod.** Q3 recommends narrowing this to one worker per C# project; if you take that, D1 and D3 mean the narrower rule.
- Retiring FOUNDRY for good becomes a separate card, asked after the pilot.

**Options:**
1. **BENCH for you plus the engine for the queue, with attempt numbers and the collision rule (one per mod, or one per C# project per Q3) (recommended).**
   - Why: no long-lived queue window to stall, and BENCH's memory is spent only on you.
   - Trade: nobody needs to wake anything. But it is a new script and worker brief to build, and each worker pays a small start-up cost.
2. **A master orchestrator window that only runs helpers, kept alive by `/loop`.**
   - Why: it keeps your talk apart from the queue.
   - (`/loop` is a Claude Code command that re-runs a prompt on a timer inside one window.)
   - Trade: little to build. But it is still a long-lived window: it fills up, and when it hangs nobody is told (FOUNDRY's failure).
3. **Keep the two windows.**
   - Trade: nothing to build. But the idle gaps and the logging in to check stay.

## D2. May a program start AI sessions on its own?

**Facts:**
- Today, waking an AI session is your act. Your one exception is the SteveDesktop watcher, which may start one capped session after 30 min with no answer.
- The engine would start sessions all day, within N, with a stop file that halts it within 2 min.
- The review changed our recommendation from "yes" to "pilot only".

**Options:**
1. **Yes, for the pilot only; after it, one short card shows you the measures and asks for the standing yes (recommended).**
   - Pass measures (single_primary_design §6): worker failures under 15%; engine idle with work ready under 10 min a day; cost per accepted item at most 1.25x FOUNDRY's last 7 days; rework no higher than baseline; no two workers on one item; nothing done on the expensive list.
   - Why: it earns trust with numbers before it becomes permanent.
   - Trade: lower risk. But it means one more card after the pilot.
2. **A standing yes now.**
   - Trade: no second card. But it trusts an engine that has never run.
3. **No.**
   - Trade: no new risk. But FOUNDRY stays a window you must wake.

## D3. FlowWorks and the GSS work: may the engine build them?

**Facts:**
- Your 10-23 ruling gave all FlowWorks and GSS work to BENCH "to prevent mutual waiting" between two windows. That ruling stands until you change it.
- The review attaches conditions to any move.

**Options:**
1. **Only after the close gate (a worker may only mark work built; closing needs proof of the owed check) and the collision rule have run clean for 48 h, and only offline items; BENCH keeps the live game work and your looks (recommended).**
   - Why: the engine earns the lane in steps.
   - Trade: more hands on your main mod later. But it waits on two builds.
2. **It stays BENCH's lane.**
   - Trade: no risk to the mod you care most about. But BENCH's slots are its only hands.
3. **The engine builds it now, like anything else.**
   - Trade: fastest. But it is untested on your most complex mod.

## D4. How a phone notification reaches you

**Facts:**
- Your phone is not on the home network, so nothing reaches it today.
- A push service such as ntfy would send counts and a link, never item text or paths, for example "5 cards ready, about 3 min". The topic name works like a password, so anyone who learns it could read the counts. Sending it is an outward act, so it is your call.
- A push does not stop us re-asking you things. That needs "decision receipts": each card gets an id, and each answer a recorded receipt that it was carried out, so a decided question cannot be asked again (`OWNER_CARDS_HARDEN_DECISION_RECEIPTS`).

**Options:**
1. **ntfy, counts and a link only (recommended).**
   - Why: it is instant and carries only counts.
   - Trade: you are told within minutes. But it is a new outside service.
2. **Email to you.**
   - Trade: uses something you already have. But it is slower and mixes with your mail.
3. **No push; the digest page only.**
   - Trade: nothing new. But you still go and look.

## D5. Notification budget

**Facts:**
- What would earn a notification:
  - emergencies: the engine stopped for 30 min, a machine unreachable, or the tokens running out within 6 h;
  - one card holding 5 or more items for 2 h;
  - a batch of 5 cards ready.

**Options:**
1. **At most 3 a day, and quiet 00:30-06:30 except emergencies (recommended).**
   - Why: few enough that each one matters.
   - Trade: calm. But a non-urgent item may wait for the digest.
2. **Up to 6 a day, no quiet hours.**
   - Why: you hear about every blocking card the same day.
   - Trade: faster answers. But more interruptions, including at night.
3. **Emergencies only; everything else waits for the digest.**
   - Why: the fewest interruptions.
   - Trade: calm. But a card holding 5+ items can wait up to 12 h.

## D6. More helpers while you are at BENCH

**Facts:**
- Your words: "You may exceed current limit of subagents for interactive work with me."
- The change from the review: when you come back, running engine workers finish their item rather than being killed, and any allowance above the total expires on its own.

**Options:**
1. **While you are present, BENCH may use the whole total; the engine starts no new workers and lets running ones finish, so for up to one item's length (45 min at most) the total is briefly exceeded; more if you say so, expiring by itself (recommended).**
   - Why: you come first, and no half-done work is thrown away.
   - Trade: fast answers for you. But the queue slows while you are here.
2. **A fixed number for BENCH.**
   - Trade: predictable. But it is wrong both on busy days and on quiet ones.
3. **No cap while you are present.**
   - Trade: the most speed. But spend can run away.

## D7. The trial run

**Facts:**
- The plan, in order:
  1. A 24 h "shadow" day: the engine only writes down what it would do, and costs nothing.
  2. A one-hour fault drill.
  3. A 48 h pilot: offline items only, at most 2 workers, at least 15 items.
  4. A 7-day watch for rework.
- **The review adds:**
  - two drill cases: a stale attempt (a late worker must be refused), and a budget reservation (each worker books its token budget when it starts, so running work counts against the daily ceiling);
  - a baseline that leaves out bulk closes and never-started closes;
  - for retiring FOUNDRY: answering a card from the phone must work end to end, and the 7-day rework watch must be clean.

**Options:**
1. **That plan, with the review's additions (recommended).**
   - Why: every step can be halted by stopping one timer (work already committed stays and is reverted by hand if needed).
   - Trade: safe. But about 10 days pass before a full rollout.
2. **Go straight to the pilot.**
   - Trade: saves a day. But it skips the zero-cost rehearsal.
3. **A longer shadow.**
   - Trade: more days of "what it would have picked". But the drill tests failures and the shadow only tests choices; a longer shadow adds little once a day's choices look right.

---

## Evidence and what is UNMEASURED

**Where the numbers come from:**
- **Ledger counts:** `model.replay(model.read())` over 28,607 events (08-21 to 10-26), run at 21:52 UTC on 10-26.
- **Block field:** `src/RimMandrake/rimflow/cli.py` `block --on/--until`; `model.py` fields `blocked_on` and `blocked_until`.
- **Check levels:** `model.py` lines 225-234.
- **Mods touched per week:**
  - command: `git log --since=2026-08-01 --name-only` over `src/*/<mod>/`, for the 130 folders that have `About/About.xml`;
  - "focused" means 1-3 mods per commit;
  - the week of Oct 26 is partial (one day).
- **First GREEN:** the git history of `infrastructure/state/modcheck_status.json` (64 versions). 7 mods are GREEN now; 14 have ever been.
- **Mod-named closes:** a mod name found inside the item's id or title. This is a stand-in, not a field.
- **Status-line warning:** `~/.claude/statusline.sh` lines 226-236.
- **Hub staleness:** git log of `infrastructure/dashboards/hub/data`.
- **Retired board:** the ledger note on `QUEUE_GITHUB_MIRROR_1` (2026-09-11).

**UNMEASURED:**
- Mod closures, because no "finished" record exists. The "focus works" claim is not shown either way.
- Compactions with no handoff.
- Whether BENCH ever sees its status line. Believed not; not proven by a test.
- Whether planned links would be kept true.
- Why you retired the ticket mirror; no reason was recorded.
