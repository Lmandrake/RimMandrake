# Holder–pipeline fusion: the pipeline as a long-term holder's checklist

Item: `RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF` · design helper, Sun 2026-11-15
~9:20 PM PST (measured, GPT blind + critique, starred claims re-measured, merged). He chose by card the same evening (below);
the build is `RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE`, its plan `design/plans/2026-11-15-holder-pipeline-fusion-build.md`.
Run files (measurement, outside sources, GPT's blind answer and critique, status): `design/specs/2026-11-15-holder-pipeline-fusion/`.
GPT's critique, verbatim: `design/specs/2026-11-15-holder-pipeline-fusion.gpt.md`.

Tags: `[measured]` (how is said) · `[guess ~N%]` · `[HIS]` his words · `[PROPOSAL]` ours.

## Decisions (owner, 2026-11-15)

By question card, ~9:45 PM PST (the whole card is stamped on `RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF`). `[HIS]`

1. Which do we build? → **"Resumed session per mod (Recommended)"**: "Why: keeps context as the mod progresses, unattended, which is what you asked for. The dispatcher resumes one long session per mod at every stage; built as the packet version first, falls back to it. Cost: a warm session can cling to a refuted theory; may cost more per stage; resume is untested in our detached launcher."
2. Who fixes what a blind judge finds? → **"Anyone finding anything documents precisely how they would fix it but it goes back to the holder fully informed."** (This replaces his 11-13 rule, under which the blind judge fixed what it found on the spot.)
3. Which mod is the pilot? → **"Do all three side by side as a deeper test. When one reveals a needed fix to the system all three benefit."** (Gimme Some Slack, FlowWorks, Explosive Knockback.)
4. Context ceiling? → **"Try 400k first."**

His additions the same evening (~9:40 PM PST): "I think the key to closing many tickets for the same mod might be keeping that context and working them all together. I think a mod holder should be handing off to its next version with context of what has happened before. Even into judging phases. I think this might be very important. Almost like a conductor custom following along. I think we're on to something."

What they change below: Option B, built as A first; three pilot mods side by side; a holder ceiling of 400k (one setting, `holder_context_ceiling_tokens` in `src/RimMandrake/rimflow/modledger.json`); every `finding.open` carries the finder's precise proposed fix and the holder applies it; the holder works all its mod's open tickets together; the holder carries across Design Versions with its context (§3.4 Lifetime); the holder stays alive and following through the judging phases while the judges stay blind.

## Five-line summary

1. He is right about the store problem `[measured]`: one mod (Gimme Some Slack) has its state in about 17 stores, its current stage copied in 3 places (and a second file using the same key for a different numbering), 413 ledger items and 126 agent runs touching it; a fresh agent cannot read all of it (≈297k tokens, more than a window).
2. He is also right that the pipeline turned ownership into handoffs; Anthropic's own published guidance names exactly our shape (separate planning, build and review agents) as the one that "lost context at each handoff".
3. "Foundry/Bench proved more live work" cannot be settled `[measured]`: the ledger's live-verified items fell from 15.2 to 3.7 a day, but the pipeline now writes its live results into the mod folders instead (four in-game visits in three days, 34–47 passing rows each). Live evidence moving to another store is the same sprawl. What clearly rose is churn: 161 items filed a day.
4. The design: one append-only **mod ledger** per mod (one shard per writer, so a holder cannot edit a judge's findings or his words), every other per-mod file becomes a generated view, and a named **holder** that every stage run *is*, starting from a bounded packet the ledger prints. Anyone who finds something (a blind judge, a checker, the steward) writes the finding with the precise fix they would make; it goes back to the holder, who applies it or disputes it, and only a judge can turn one green. The dispatcher alone grants the holder's lease and accepts stage moves.
5. The three options differ in what carries the context between stages: the record alone (A), a resumed per-mod session (B), or a long-lived seat window (C). His pick: **B, built as A first, piloted on three mods side by side.** All three need the ledger; B keeps warm context without needing a window kept open, our dispatcher already resumes sessions, and the evidence from Relentless says long sessions do much of their landing late (84% of the landings in sessions that passed 200k came after 200k), so a holder is let grow to 400k (his "Try 400k first.") before it rotates.

## The three options (read this section alone)

All three share the same core, which is his two fixed points made concrete:

- **One mod ledger per mod, append-only, stored nowhere else.** Everything a run learns about the mod (stage moves, bars, tests run, findings, causes tried and refuted, questions and his answers, decisions, spend) is one event in it. `stage.json`, `journal.md`, `log.md`, the status page row and the mod's handoff text stop being written by hand and are printed from the ledger.
- **Blind judges stay.** A judge sees the candidate (a commit), the locked bars and the test entry point, never the holder's story. Each finding goes into the ledger with the precise fix the judge would make, and back to the holder fully informed; the holder applies it (or disputes it); a new blind judge looks again. Only a judge event turns a finding green.
- **Questions to him are ledger events** with an asked / answered / superseded state, checked against his past answers before anyone asks.
- **Three pilot mods advance side by side** (Gimme Some Slack, FlowWorks, Explosive Knockback); a fix to the system found on one lands for all three. Other pipeline-machinery work is capped (it was close to half the runs tonight).

### Option A — "The record is the holder"

**What it is.** Keep today's fresh, capped stage runs launched by the dispatcher, but every run on a mod is that mod's holder by name and lease, starts from a packet the ledger prints (≈10–20k tokens: where it stands, open findings, causes already refuted, his answers, next action), and must write what it learned back as events before it may end. No session is kept warm.

- **Pros.** Smallest change to what runs today; survives every restart by design; cheapest per run; the dispatcher, caps and timers stay. Restarting is a non-event.
- **Cons.** Every run is still a new mind: what the packet leaves out is lost (Cognition: "Actions carry implicit decisions"); this is the shape that already loses context, made better rather than removed. Does not give him "context is kept as it progresses", and it cuts every holder at each stage, where the Relentless transcripts say long sessions did most of their landing late (§1.4).
- **Build effort.** About 3–4 helper runs (ledger writer and lint, views for one mod, packet, dispatcher reads packet) `[guess ~60%]`. **Test effort:** offline selftests plus a pilot of about a week.
- **Risk.** Medium-low. The ledger becomes one more store if any writer keeps its old file; the fix is that at cutover the old files are archived read-only and their writers redirected, all at once.
- **Retired.** Hand-written `journal.md`, `stage.json` as a source, the steward's journal lines, per-mod handoff prose, per-mod rimflow items (findings become ledger events).

### Option B — "The holder is a resumed session" (his pick)

**What it is.** Option A's ledger, plus: each advancing mod has one holder session that the dispatcher *resumes* (`claude -p --resume <session>`) for every stage it does itself, instead of starting a stranger. It is allowed to build context well past today's 200k window backstop (his correction, 2026-11-15 ~9:08 PM, via the Conductor: "You're going to have to let them build up more context... Significant numbers of fixes happened after around 250k context."): it runs to **400k** (his "Try 400k first."), then at its next natural boundary writes a checkpoint and a new session of the same holder starts from the packet, before the 1M window's auto-compaction (~750k) can cut it. Rehydrating from the ledger is the fallback after a forced restart, not the normal mode (§1.4). The holder does preflight, build, applying the fixes the judges' findings propose, and the in-game acceptance, working all of its mod's open tickets together in one context; it carries into the mod's next Design Version and follows the judging phases; blind judges and the pre-human check stay independent.

- **Pros.** Keeps context as the mod progresses, unattended (C keeps it too, but only while a window is up); one mind reads every blind finding about its own code; the ledger makes rotation safe, so a lost session costs one packet, not the mod; matches Anthropic's guidance that "an agent handling a feature should also handle its tests"; the resume path already exists in our dispatcher (`dispatcher.py` resumes seat windows with `claude_bounded.sh --bg --resume`) `[measured: grep]`.
- **Cons.** Resuming gives back the conversation, not certainty: a warm session anchors on its own beliefs and can carry a refuted cause, so the packet is re-read at every resume and the ledger wins any disagreement; B may cost more than A per stage `[guess ~50%]`; a resume that fails after the session had already edited code or driven the bridge must first reconcile (unpublished commits, the clone, the bridge) before anything restarts, or it repeats the damage; a long context degrades ("context rot", cited in `design/RimMandrake/perpetual_orchestrator_context_2026-10-26.md`), so the blind judges and the packet re-read matter more the longer it runs; a resume after the one-hour prompt cache has expired re-writes and pays for the whole context (about $3 at the 400k ceiling, scaled from that doc's rates `[guess ~55%]`), so the dispatcher resumes a holder promptly when a judge's findings land.
- **Build effort.** Option A plus a session-id event, the resume launch, the reconcile step, the rotation rule, and a spend cap per mod and stage in place of today's USD 15 per run (a holder running to 400k will pass a per-run cap; the per-stage ceiling he set, USD 100, stays) `[guess ~55%]`. **Test effort:** A's tests plus a kill-and-resume test: kill a holder mid-stage; the next one must reconcile, avoid a refuted cause and respect an answered question.
- **Risk.** Medium. Mitigated because A is built first and B falls back to A (after the reconcile) when a resume fails.
- **Retired.** Everything A retires, plus "new stage, new builder" launches for the holder's own stages.

### Option C — "The holder is a seat" (Foundry/Bench back, with the pipeline as its checklist)

**What it is.** One or two long-lived holder seats (windows like Foundry and Bench were), each holding exactly one mod at a time from preflight to his live walk, doing its own live tests on the bridge. The pipeline's stages become the checklist in the mod ledger that the seat ticks; the dispatcher no longer builds or fixes, it only launches the blind judges and the pre-human check when the seat asks, and wakes the seat when a finding lands. Machinery work stops unless it blocks the held mod.

- **Pros.** What he remembers working; the fewest moving parts; one owner he can talk to about the mod; WIP is limited by construction (seats = mods in flight).
- **Cons.** A seat is an interactive window: it restarts at its context limit through the handoff ritual, and we measured that Conductor-window restarts lose about 12% of what the dying window owed (`design/specs/2026-11-15-conductor-restart-loses-nothing.md`); the ledger is what saves C, as it saves A and B. A seat can be woken by a timer, but every wake lands in a window someone must keep alive and healthy; the seat's own warm context goes stale between sittings just as B's does; work a seat does outside the dispatcher is invisible to it; and it undoes part of his 11-13 design (Dispatch "opportunistically allowing them access").
- **Build effort.** Lowest code (ledger plus a role file) `[guess ~70%]`, highest attention cost: seats need watching, waking and handing off.
- **Risk.** Medium: flow depends on windows staying up; correctness depends on the seat writing the ledger as faithfully as A's runs must.
- **Retired.** The dispatcher's builder, fixer and steward launches; the steward role at stage changes (the seat is the steward of its mod).

### How each honours his two fixed points

| | Blind judges stay | One monotonic per-mod source of truth |
|---|---|---|
| A | sealed judge findings in their own shard, routed to the holder | the mod ledger; all else views |
| B | same as A | same as A |
| C | dispatcher still launches them, seat cannot reach their brief | same ledger; the seat writes it like any holder |

**A fourth idea, from the GPT review, folded in rather than offered.** GPT's own pick was "D": one transactional coordinator (a database with a state machine) instead of git-sharded files. It is a choice about *storage*, not about what the holder is, so it is not a fourth holder option. We take its main benefit, one authority for leases and stage moves, by making the dispatcher (already the single launcher) the only writer of those events and the only judge of whether a move is valid. We do not take the database: ledger writers run on two machines today (`CLAUDE_STEVEDESKTOP_*` shards beside Archmagi's) and publish through git, which the rimflow shards already handle. If the pilot shows conflicting transitions, D is the fallback.

**Combinations.** A is the first step of B (B = A + resume). C can run *on top of* A or B for the one mod he is sitting with (a window resumes the holder session instead of a timer), so "B now, C-style sitting when he is there" composes cleanly.

**His pick: B, built as A first.** Build the ledger and packet (A) for the three pilot mods side by side (Explosive Knockback, the smallest, backfilled first; then Gimme Some Slack and FlowWorks), run their views beside the old files for a few days, cut over (old files archived read-only, their writers redirected), then switch each mod's holder stages to resume one session. A fix to the system that one pilot needs lands for all three. What would change this: if the pilot shows resumed sessions repeating refuted causes or costing more than about 1.5× an A run per stage, stay at A; if he would rather sit with one mod than have it run overnight, take C on top.

His answers to the three decisions this section asked are at the top (Decisions, owner, 2026-11-15).

---

## 1. What we measured

Full tables: `design/specs/2026-11-15-holder-pipeline-fusion/00-measure.md` (read-only census, Sonnet helper, 2026-11-15).

### 1.1 Where Gimme Some Slack's state lives today `[measured: find, du, grep over src/ for writers]`

- **About 17 stores** (39 if each kind of file in the concept folder is counted): the concept folder (169 files, 1.79 MB, 114 commits), ledger events in 6 shards (1,166 events naming the mod), 98 open item files (28 naming it strictly), 121 closed ones, 17 handoffs (438 KB), 139 Conductor log lines, the dispatcher's `state.json`, `ticks.jsonl` and 5 briefs, the status page, the mod's source folder (`CHANGELOG.md`, `KNOWN_LIMITS.md`).
- **The same fact in several places:** the current stage in 3 agreeing copies plus ledger notes (`version/stage_record.json`, the journal's "stands" top, `MATURATION_NOW.md`; re-measured down from 6), and a homonym: `stage.json` also has a `stage` key, value 5, which is the Designer's inner step, not pipeline stage 5, a trap for any cold reader; the bar count (48) in 4; his words in 3; Designer results twice (30 result files and 34 KB inside `stage.json`).
- **Writers:** `stage.json` alone is written by `designer_stage.py`, `coverage_judge.py`, the `maturation*.py` modules and `maturation_now.py`; the journal by steward agents by hand and by `maturation.py`/`maturation_autonomy.py`. No store has one writer.
- **A view that has gone stale:** the journal's "Waiting on" line read "not yet written for this stage" at measurement.
- **Two stores that disagree on one number:** open items are 888 by the items folder and 2,992 by filed-minus-closed in the ledger; the Conductor's evening note said 2,195. `[measured]` The items folder is the one to trust; the gap is filed-then-dropped ids `[guess ~60%]`.

### 1.2 How many minds held this mod `[measured: id regex over ledger text; upper bound]`

About **126 distinct runs** appear in its ledger events (27 Designer runs, 3 exam runs, 11 stage-spend rows, 48 detached runs in the Conductor log), across 9 seats. Each started cold. The blind judge's brief we could find is 15.6 KB and points at about 91 KB of files (~23k tokens) before any code; two of three sampled briefs are not kept on disk at all, so what a run started from is often unknowable after it ends.

### 1.3 The "Foundry/Bench was better" claim `[measured: ledger, all 19 shards]`

Rule: an item closed in the window that also carries a passing `verify` at L1 or above (every level above L0 needs the bridge or him, `model.py` `LEVEL_NEEDS`). The close event's `live` field is not game proof (it holds timer readings).

| window | closes/day | live-proven/day | items filed/day | distinct bridge takes/day |
|---|---|---|---|---|
| Oct 1 – Nov 1 (Foundry + Bench) | 59.0 | 1.7 | 128.8 | 12.2 |
| Nov 2 – Nov 12 (Relentless) | 108.8 | 2.9 | 100.9 | 34.9 |
| Nov 13 – Nov 15 (pipeline, 3 days, noisy) | 79.0 | 4.0 | 161.0 | 12.0 |

**Re-measured by a second rule, and the answer moved** (`02m-remeasure.md`). Counting every item with a passing L1+ `verify` in the window, closed or not: **15.2 → 13.4 → 3.7 a day**, a four-fold fall. But the pipeline no longer writes its live results as ledger `verify` events; it writes them into the mod folders: four in-game visit records in the three pipeline days (Explosive Knockback twice, 47 of 56 and 47 of 53 rows passing; FlowWorks; Pyrelands, 34 of 39) and 17 in-game stage runs in the spend files `[measured]`. So the eras cannot be compared with one instrument. What can be said: live work did not stop in the pipeline days (the evening of 11-15 was a quiet one, not the era); live evidence moved out of the ledger into a second store, which is the sprawl again; and filing rose to 161 items a day. This is consistent with his reading that live access was not the missing piece, but it does not prove it.

### 1.4 What a holder can actually carry `[measured: wc -c, tokens ≈ bytes/4]`

| what a fresh agent reads | tokens |
|---|---|
| the journal's "stands" top alone | ~1.8k |
| minimum pickup today (journal, stage record, bars) | ~10k |
| all mod files except the big test table | ~68k |
| + the 28 open items | ~110k |
| + the test table | ~187k |
| + the 17 handoffs | ~297k (more than one window) |

**How long can a holder run?** The ~200k restart is **our** setting, not the model's: the window backstop in `src/RimMandrake/rimflow/dispatcher_schedule.json` (110k soft, 200k hard, his card of 2026-11-01, "Same limits as Foundry") `[measured]`. Relentless sessions ran on `claude-opus-5-5` with peaks up to 750k, and BENCH's own sessions peaked at a median of 347k on the 1M window (`design/RimMandrake/perpetual_orchestrator_context_2026-10-26.md`). His correction tonight (via the Conductor, 2026-11-15 ~9:08 PM PST): *"You're going to have to let them build up more context. Recall the lesson from the last pipeline. Significant numbers of fixes happened after around 250k context."* He placed it (2026-11-15 ~9:30 PM PST): *"It was during the design of artisan. We found they had that dependency on context window size."* The Artisan loop's ceilings record it: soft 250k, firm 350k (`~/.claude/skills/artisan/SKILL.md` "Context ceiling"; `src/RimMandrake/Utils/artisan_now.py` `SOFT_CONTEXT, FIRM_CONTEXT`) `[measured: grep]`; the written reasoning behind those numbers was not found. It was also measured from 3,260 Relentless transcripts (`design/specs/2026-11-15-holder-pipeline-fusion/02c-context-evidence.md`) `[measured]`:

- across all sessions, only 3.9% of landings came after 250k, because most helpers were short (session peak median 83k);
- but in the **74 sessions that grew past 200k and landed anything, 208 of their 249 landings (84%) came after 200k, and 111 (45%) after 250k; 51 of the 74 landed nothing before 200k.**

So he is right for the case that matters: a session that is allowed to run long does most of its landing late, and our 200k cap would have ended most of those before their first landing. (Limits: a landing is any publish, not a verified fix; hard problems make long sessions, so this shows late work happens, not that a packet restart would have failed.)

**What follows for the holder.** It is allowed to grow to 400k (his pick, "Try 400k first."; one setting, `holder_context_ceiling_tokens` in `src/RimMandrake/rimflow/modledger.json`), then rotates at its next natural boundary, before the 1M window's auto-compaction (~750k by the 10-26 simulation). Warm turns are cheap while the one-hour cache holds (that doc: 150k cached ≈ $0.03 a turn); the expensive moment is a resume after the cache has gone cold, so the dispatcher resumes a holder promptly. **Rehydration from the ledger is the fallback after a forced restart, not the normal mode.** The record still has to be complete, because the mod's history (~297k) is already more than any one rotation will see, and because a forced restart can come at any time.

## 2. Outside practice, and where we violate it

Sources read on the page, quotes verbatim (fetched 2026-11-15):

| practice | source | what it says | where we break it |
|---|---|---|---|
| **One agent keeps a feature and its tests; handoffs lose context** | Anthropic, "Building multi-agent systems: when and how to use them", Jan 2026, https://claude.com/resources/articles/building-multi-agent-systems-when-and-how-to-use-them | "Each handoff loses context." · teams with separate planning, execution and review agents "lost context at each handoff and spent more tokens coordinating than executing." · "an agent handling a feature should also handle its tests, because it already possesses the necessary context." | Our stages are exactly planning (Designer), execution (builder) and review (judge) agents, each a stranger; ~126 runs on one mod (§1.2). |
| **Verification by a fresh agent works** | same article; Cognition, "Multi-Agents: What's Actually Working", Apr 2026, https://cognition.com/blog/multi-agents-working | "Verification subagents succeed because they sidestep the telephone game problem." · review works "best when the coding and review agents do not share any context beforehand." | We keep this, rightly: it is his fixed point. |
| **Writes stay single-threaded; others contribute intelligence** | Cognition, same 2026 piece; and "Don't Build Multi-Agents", Jun 2025, https://cognition.com/blog/dont-build-multi-agents | "multi-agent systems work best today when writes stay single-threaded and the additional agents contribute intelligence rather than actions." · "Actions carry implicit decisions, and conflicting decisions carry bad results" | Until his 2026-11-15 answer, his 11-13 rule had a blind judge fix what it found on the spot, so the mod's code had several writers in turn (now replaced: the finder writes the fix, the holder applies it); `stage.json` has at least four writer modules (§1.1). |
| **Progress file + git + feature list; each new session rehydrates from them** | Anthropic, "Effective harnesses for long-running agents", Nov 2025, https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | "each new session begins with no memory of what came before." · "Read the git logs and progress files to get up to speed on what was recently worked on." · agents were "asked to work on only one feature at a time." · warns of "Claude's tendency to mark a feature as complete without proper testing." | We have a journal meant for this, but it is one of ~17 stores, partly hand-written and stale (§1.1), and runs start from ticket prose and a brief, not from one progress record. |
| **Structured notes outside the window** | Anthropic, "Effective context engineering for AI agents", Sep 2025, https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | "the agent regularly writes notes persisted to memory outside of the context window." · "overly aggressive compaction can result in the loss of subtle but critical context" | Notes exist but are scattered; the cause-already-refuted that sent a helper out twice was in a note no brief carried. |
| **Event sourcing: the log is the truth, everything else is a projection** | Martin Fowler, "Event Sourcing", https://martinfowler.com/eaaDev/EventSourcing.html (page not re-read in this run; the pattern is standard) | state is rebuilt from the stored sequence of events; views are disposable | Our per-mod state files are edited in place; the ledger exists but mod state is not derived from it. |
| **Single writer** | Martin Thompson, "Single Writer Principle", Mechanical Sympathy blog, 2011 (cited via a QCon talk; URL not fetched: unknown) | one writer per piece of data | No mod store has one writer. |
| **One accountable owner (DRI / single-threaded owner)** | GitLab handbook, https://handbook.gitlab.com/handbook/people-group/directly-responsible-individuals/ (search result; not fetched) | one named person accountable end to end | Accountability for a mod belongs to the Conductor as steward "always" (his card 11-13), who holds every mod and none closely. |
| **Limit work in progress; stop starting, start finishing** | Kanban practice (search results; no primary source fetched) | cap items in flight | Four to five mods advance at once plus ~half the runs on machinery; 161 items filed a day. |
| **Andon: stop and fix the line, don't route around** | Toyota UK, https://mag.toyota.co.uk/andon-toyota-production-system/ (search snippet) | anyone may stop the line for quality; the leader fixes within takt | Our "pipeline fixes its own defects" ruling is andon-like, but every fix files 1–3 new tickets, so the cord pulls more work in instead of stopping. |

**Where we violate it, in one line each:** many writers per fact (single writer); state edited in place (event sourcing); strangers at each stage (one owner per feature and its tests); the steward owns all mods (DRI); no WIP cap on machinery (Kanban); a self-fix that spawns tickets (andon). **Where we already follow it:** blind verification with no shared context, and append-only sharded ledger code (`rimflow`'s shards and `ledger_lint` `NOT_APPEND`), which the design reuses.

## 3. The design (common to all three options)

### 3.1 The mod ledger

**Where.** `design/concepts/<Mod>/ledger/<WRITER>.jsonl`, one file per writer, in git like the rimflow shards and for the same reason: many clones publish, and one file per writer cannot conflict at merge. The mod's state is the merge-ordered read of all its shards. It reuses rimflow's model and lint code `[PROPOSAL]`; it is not the global ledger.

**Writers (one shard per producer, never per role).** `HOLDER.<lease>` (each holder lease gets its own shard, so a stale holder and its successor never share a file), `JUDGE.<run>` (one per blind run, sealed when the run ends: the dispatcher records the shard's hash in its own shard, so a later edit is detectable), `OWNER` (his words, cards and answers, written by the card capture and `--owner-said` paths), `DISPATCH` (launches, leases, stage acceptances, stops, spend; written only by the one dispatcher tick), `STEWARD` (the Conductor's decisions), `BACKFILL` (the one-time import from today's stores; every one of its events cites the old file it came from). Every event has a unique id and an idempotency key, so a re-published or duplicated append is harmless. A writer can only append to its own shard: the holder cannot edit or drop a judge's finding or his answer. This is GPT's point that the holder owns the mod but not the evidence.

**Monotonic** means history only grows. A conclusion can be overturned (a refuted cause, a pass invalidated by a new commit), by a later event that names the one it supersedes; nothing is ever edited or deleted. Publish refuses a shard that is not a strict extension of its last published form (the existing `NOT_APPEND` check). A refuted cause carries what it was refuted *on* (the commit and the files it depends on) and reopens by itself when those change, so history does not preserve a stale verdict forever.

**Who decides what is true now.** Ordering across shards is not authority. The dispatcher alone grants holder leases (with a number that only grows, a fencing token) and accepts stage moves: a holder writes `stage.exit_claimed` naming the evidence; the dispatcher's tick checks the preconditions (the judge's or checker's confirmation, no open finding, the expected current stage) and writes `stage.accepted` or `stage.rejected` with the reason. A `HOLDER` event carrying an old fencing token is ignored by the reducer, and on takeover the dispatcher stops the old run's unit before launching the new one.

**Event shape.**

```
{id, key, ts, tsn, mod, version, writer, run, kind, subject, supersedes?, code_sha?, token?, body, evidence: [path or sha], authority?}
```

`seq` is the event's line number in its shard, assigned on read (a shard only grows, so it never moves), not stored. `id` is derived from the writer and the idempotency `key`; `token` is the holder's fencing token, required on every `HOLDER` event.

Kinds: `lease.grant` (DISPATCH; the fencing token), `lease.renew|release` (HOLDER), `judge.sealed` (DISPATCH; the judge shard's hash), `run.start|end` (DISPATCH), `version.open` (the mod's Design Version moves on; the holder carries over), `session.id` (B: the holder's resumable session and its context size), `session.checkpoint` (B), `stage.enter`, `stage.exit_claimed` (holder), `stage.exit_confirmed` (judge or steward), `bar.locked|added|eased|deferred` (OWNER or STEWARD with his authority), `test.run` (result, sha), `live.run`, `finding.open` (any finder: JUDGE, STEWARD, OWNER; its body must carry `proposed_fix`, the precise fix the finder would make, or the append and the lint refuse it), `finding.claimed_fixed` (HOLDER, having applied the proposed fix or a better one it names, with a test), `finding.verified|reopened` (a later JUDGE), `finding.disputed` (HOLDER, goes to the neutral fixer per the refusal ruling), `cause.tried|refuted`, `question.ask`, `question.answer` (OWNER), `question.withdrawn`, `decision` (with `--owner-said`/`--by-card`/`--per-ruling`/`--why` provenance as today), `spend`, `note`.

**The single-writer rule, enforced.** One command appends (`modledger append`), checks the writer against the shard and, for `HOLDER`, the live lease token. Views carry the offset of every shard they were built from and the reducer's version, and publish refuses a hand-edited or stale view. The launcher records each run's start, end, commits and test commands as events itself, so a run that dies still leaves its trace; a run that ends without a `session.checkpoint` of the fixed shape (what was done, with evidence; what is next; what was ruled out) is a flagged run. This is tamper-evidence and discipline, not prevention: an agent with a shell can still write a file by hand, and the lint is what catches it. (GPT objection 10, accepted as a limit.)

### 3.2 What "stored nowhere else" deletes or turns into views

| today | becomes |
|---|---|
| `stage.json`, `version/stage_record.json` | generated views (kept as files only while code still reads them) |
| `journal.md` "stands" top and history; steward's `CONDUCTOR INTERVENED` lines | generated `state.md` (the packet) and `history.md`; interventions are `decision` events |
| `log.md`, `park_summary.md`, `result.*.json` copies in `stage.json` | deleted after backfill; results are events |
| per-mod rimflow items and notes (413 ids for this mod) | `finding`/`cause`/`question` events; rimflow keeps one item per mod version plus cross-mod and tooling work |
| per-mod handoff prose | a handoff points at a ledger seq; it says nothing about the mod the ledger does not |
| the mod's rows on `MATURATION_NOW.md` and in the dispatcher's `state.json` | generated from the ledger |
| incident plans about the mod | `finding` events; no prose copy |
| `exam.json`, `coverage_verdict.json`, `test_table.json`, `tree.json`, `bars.md` | stay as the *artifacts* (evidence files the events cite); `bars.md` and the counts become views |

### 3.3 The packet (rehydration)

Printed from the ledger on demand, bounded (target ≤ 15k tokens; today's minimum pickup is ~10k, §1.4): version and stage; the bars with their latest verdict; open findings with their judge's text; **causes refuted** (so nobody chases them again); his answers that bear on open work; the open questions; the holder's last checkpoint ("what I was doing, what I'd do next"); spend. Everything else is one `modledger show <subject>` away. The full history is never read whole. The packet ends with what it left out (subjects and counts), and when it would pass its budget it drops the oldest closed material first, never an open finding, a refuted cause or an answer. Every time a run misses something that was in the ledger, that miss becomes a packet regression test.

### 3.4 The holder

- **Identity:** `HOLDER/<Mod>`, one per mod, carried across its Design Versions; each lease names the version it works on. It is a role with a lease, not a process.
- **Lease:** granted by the dispatcher at launch with a fencing token, renewed while running, lapses after 45 minutes idle (borrowed from the bridge rule; a starting number). A run without the current lease cannot append to a `HOLDER` shard that counts. A stuck holder's lease lapses and the next launch takes over from the packet: one stuck run never sticks the mod.
- **Lifetime (his addition, 2026-11-15: "a mod holder should be handing off to its next version with context of what has happened before. Even into judging phases."):** from the first version's preflight onward, across versions. When the mod's Design Version moves on (`version.open`), the same holder carries on: its session (B) or, after a rotation, its successor started from the packet, which lists what the earlier versions decided, refuted and were told. It stays alive and following through the judging phases, like a per-mod Conductor: it reads each sealed finding as it lands and applies the fix, while the judges stay blind (they never read a `HOLDER` shard).
- **All its tickets together:** the holder works every open finding, question and ticket of its mod in one context (his: "the key to closing many tickets for the same mod might be keeping that context and working them all together"), not one fresh run per ticket.
- **Context ceiling:** 400k tokens (his "Try 400k first."), then a checkpoint and rotation at the next natural boundary. One setting, `holder_context_ceiling_tokens` in `src/RimMandrake/rimflow/modledger.json`; nothing else names the number.
- **Rehydration:** A, every run from the packet; B, resume the last session while under the rotation threshold, otherwise the packet; C, the seat's window, with the packet after each handoff.

### 3.5 The pipeline as the holder's checklist

| stage | who | why |
|---|---|---|
| 1 Designer | the Designer with him; the coverage judge stays blind | design is argued with him; on a mod's first version the holder starts at lock and reads the design history; on a later version the holder carried from the previous one follows the Designer stage |
| 2 Preflight | holder | its own plan, its own context |
| 3 Offline build | holder | |
| 4/5 Blind challenge | **blind judge finds and writes the precise fix it would make; the holder, following along, applies it; a new blind judge re-judges** | judge stays blind; one writer of code |
| 6 In-game acceptance | holder drives the scripted live checks | it owns its tests, as Foundry did |
| 7 Pre-human check | independent fresh agent; the holder follows and applies what it finds | a holder must not certify its own evidence |
| 8 His walk | him; the holder prepares the sitting and takes his findings | |

The stage exits are checklist items in the ledger. The holder can only *claim* an exit; a judge, the pre-human checker or the steward confirms the evidence, and the dispatcher accepts the move. The dispatcher's question per mod becomes "what is the next unchecked item, and is the holder already on it?".

### 3.6 Blind feedback reaches the holder, the judge stays blind

A judge run has two phases. **Discovery, blind:** its brief is the candidate commit, the locked bars and the test entry point only: no `HOLDER` shard, no history, no earlier verdicts. It writes its findings to its sealed `JUDGE` shard. **Then verification, targeted:** only after discovery is sealed, it is given the earlier judges' open findings that the holder claims fixed (the finding text and its reproduction, never the holder's story) and rules on each. Every finding carries the finder's precise proposed fix, so it reaches the holder fully informed. The holder must answer every finding (`claimed_fixed` with a test, having applied that fix or a better one it names, or `disputed`, which goes to the neutral fixer under the refusal ruling); it cannot mark one verified. Cycles are counted from the shards. The exit is today's: every bar's test run green on the candidate commit, and no finding open; we drop the "two passing judges in a row" idea (GPT objection 14: two judges share models and bars, so the second adds cost more than certainty).

### 3.7 Questions to him: one register

Every question is a `question.ask` event with the exact question, the mod, what it blocks, the obvious answer (Evidence-for-Ask) and the evidence against it. Before asking, the asker checks one generated **answer index** (every `question.answer` across all mod ledgers plus his rulings, `owner_rulings.py`); an answered question is reopened only with a named new fact. Questions and rulings that span mods stay in rimflow, the global ledger, which the index reads too; so do the bridge, tooling and cross-mod work. The Conductor's daily list is a generated view: open questions, oldest first. This replaces stale files answering for him (the Pyrelands giant question).

### 3.8 Migration, smallest first step

1. Build `modledger` (append, lint, show, packet, views) on rimflow's shard code, with its offline selftest (watch it refuse a hand-edited view, a non-append shard and a stale fencing token).
2. Backfill the three pilot mods, Explosive Knockback first (the smallest), then Gimme Some Slack and FlowWorks: one baseline event set per mod from today's stores (stage, bars, open findings, his answers, refuted causes, open questions), each event citing the old file it came from.
3. **Shadow first:** for a few days each mod's views are generated beside the old files and compared every tick; a judge that did not write the backfill reads the packet against the old files. Cut over only when they agree.
4. Cut over: the old files are archived read-only with their provenance (not deleted), and every writer to them is redirected or refused, on the same day.
5. The next stage run starts from the packet (A). Then (B) the holder session is resumed.
6. The three pilots advance side by side throughout (his "Do all three side by side as a deeper test. When one reveals a needed fix to the system all three benefit."); a fix to the system found on one lands for all three.

The build estimates in the options are for one mod; redirecting every legacy writer across all mods is the larger, unestimated part (GPT objection 17, accepted).

**Cap while piloting:** the three pilot mods advancing, and machinery work only where it blocks one of them (his "pipeline fixes its own defects" still holds for a blocking defect).

## 4. Critique

**Where the idea is right.**
- The store sprawl is real and measured (§1.1), and outside practice is unanimous that one record, one writer and one owner per feature beat handoffs (§2).
- His instinct about the live game is consistent with the evidence, though not proven by it: live work kept happening in the pipeline days (§1.3), and the evening's failures were memory failures (a stale answer, a refuted cause relaunched) and churn, not a missing bridge.
- "The pipeline is a checklist, not a handoff" fixes the specific defect that the stage boundary is where context dies.

**Where it fails, or needs a guard.**
1. **A holder marks its own homework.** Guard: a holder can claim, never confirm; only a judge, the pre-human checker or the steward confirms (§3.5–3.6). Anthropic's harness post names the exact risk ("mark a feature as complete without proper testing").
2. **Context limits.** No holder holds the whole mod (its history is already ~297k tokens and growing), but a holder can hold far more than our 200k backstop allows: the window is 1M, and long Relentless sessions landed 84% of their work after 200k (§1.4). So the ceiling is set from that evidence and his pick (400k, rotate at a boundary before auto-compaction), and the ledger stays the truth: warm context is how the holder works, never what it cites.
3. **Anchoring.** A long-lived holder keeps its first theory. Blind judges are the counterweight; a holder whose finding count does not fall for two cycles is rotated (a fresh holder from the packet).
4. **One holder stuck, one mod stuck.** The lease lapses; a takeover costs one packet. With three mods in flight, one stuck mod costs a third of the throughput; that is the price of WIP limits and it is worth it if finishing rises.
5. **Concurrency on a monotonic log.** One shard per writer and a lease on `HOLDER` remove write races; merge order across shards is the existing rimflow problem, already solved there.
6. **The ledger outgrows a holder.** It will (Gimme Some Slack's history is already past one window). The packet is the bounded read; full history is searched, never read.
7. **Cost.** Resumed sessions re-read a large context every turn; cheaper per step than a stranger reading 23–52k tokens of briefs and files and re-deriving, or not `[guess ~50%]`. The pilot measures it.
8. **It does not fix churn by itself.** Close to half the evening's runs were the pipeline fixing itself, each filing more tickets. Perfect memory does not stop that; the WIP and machinery caps do. This is the part of the Conductor's earlier "total fix" that the fusion still needs.
9. **It changes one of his own rules, and he changed it.** His 11-13 rule had the blind judge fix on the spot; his 2026-11-15 answer replaces it: "Anyone finding anything documents precisely how they would fix it but it goes back to the holder fully informed." The finder's work is the precise fix written down; the holder is the one writer of code.
10. **Migration is the dangerous part.** A ledger plus old files still written is store number 18. The old files must become views on the pilot mod the same day, or the pilot proves nothing.

**What would falsify it** (on each pilot mod, against its own last week; the pilots run together, so they cannot separate the ledger's effect from the WIP cap's, so only the first two lines are clean tests of the ledger, and A versus B is read stage by stage, not as a controlled trial):
- a refuted cause chased again, or an answered question asked again (target 0; either one falsifies the "single source" claim);
- the mod's stage readable from more than one hand-written place (target 1);
- blind finding to holder fix, median time (should fall);
- dollars per bar that reaches in-game pass (should not rise more than ~1.5×; B is dropped to A if it does);
- relays to him about the mod (should fall).

## 5. GPT skeptical review, answered

GPT (model `gpt-6.1-sol` via Codex) reviewed the design blind of authorship; its full reply is `design/specs/2026-11-15-holder-pipeline-fusion.gpt.md`, its earlier blind answer `design/specs/2026-11-15-holder-pipeline-fusion/02a-gpt-blind.md`. Its blind answer reached the same two shapes as A and B on its own and picked B ("a resident builder"); its critique picked a fourth, D.

| # | objection (short) | answer |
|---|---|---|
| 1 | A's "cheapest per run" ignores rediscovery and retries | **Accepted.** Cost is now read to an accepted stage, retries and judges included (§4 falsifiers). |
| 2 | A moves the memory problem into the packet | **Accepted.** The packet lists what it left out, has an overflow rule, and every miss becomes a packet regression test (§3.3). |
| 3 | B oversells "one mind"; 120k unproven | **Accepted.** B's wording changed; the packet is re-read at each resume. The 120k number is gone: on his correction and his pick the ceiling is 400k, set from the Relentless landing measure (§1.4), with a rotation before auto-compaction. |
| 4 | B's fallback can repeat damage | **Accepted.** A reconcile step (clone, unpublished commits, bridge) runs before any retry. |
| 5 | C's disadvantages partly invented | **Accepted.** C's cons rewritten: timers can wake a seat; the real cost is a window kept healthy and restarts through handoffs. |
| 6 | the options mix independent decisions; C also keeps warm context | **Partly accepted.** The options now differ on one axis only (what carries context between stages); storage is shared core. Rejected that "sequential judge edits are single-threaded writes, so fine": they are, but they split *ownership* of the code, which is his point. |
| 7 | shards fix file contention, not state conflicts | **Accepted.** The dispatcher alone grants leases and accepts stage moves after checking preconditions (§3.1). |
| 8 | a role shard still has many writers | **Accepted.** One shard per producer (per lease, per judge run), event ids, idempotency keys. |
| 9 | an expired lease leaves the old process alive | **Accepted.** Fencing tokens; the dispatcher stops the old unit before takeover. The 45 minutes stays a starting number. |
| 10 | authority is declarative | **Accepted as a limit.** It is tamper-evidence (sealed shard hashes, lint), not prevention; said so in §3.1. OS-level separation is not proposed: every agent here runs as one user. |
| 11 | append-only can keep nonsense forever | **Accepted.** Refuted causes carry their conditions and reopen when the code they depend on changes. |
| 12 | views need reducer versions; "seq N" undefined across shards | **Accepted.** Views carry every shard's offset and the reducer version. |
| 13 | a judge denied earlier findings cannot verify their fixes | **Accepted.** Two-phase judge: blind discovery sealed first, then targeted verification of claimed fixes (§3.6). |
| 14 | two passing judges is uncalibrated | **Accepted.** Dropped; the exit stays every bar's test green on the candidate commit, no finding open. |
| 15 | the ledger cannot capture "everything learned"; one trivial event passes the check | **Accepted.** The launcher writes run start, end, commits and tests itself; the end check needs a checkpoint of a fixed shape. A run that writes confident fiction is still possible; blind judges are the check on it. |
| 16 | cross-mod coordination unresolved | **Accepted.** One generated answer index; cross-mod rulings, the bridge and tooling stay in rimflow (§3.7). |
| 17 | migration estimate is fantasy | **Accepted.** Shadow mode before cutover; legacy files archived with provenance, not deleted; the estimate now covers one mod only and says the rest is unestimated. |
| 18, 25 | consider D: one transactional coordinator | **Partly accepted.** Its main benefit (one authority for transitions) is taken by the dispatcher; the database is not, because ledger writers run on two machines through git today (`02m-remeasure.md`). D is the named fallback if the pilot shows conflicting transitions. |
| 19 | the pilot confounds everything; "items filed per day" improves by renaming | **Accepted.** That falsifier is removed; the falsifiers now say which are clean tests of the ledger and that A versus B is read stage by stage, not as a trial. We cannot run a controlled experiment with three pilot mods advancing together; said plainly. |
| 20–22 | star claims: 17 stores not reproducible; ★4 over-read; ★6 conditional | **Accepted.** ★4 re-measured and withdrawn (§1.3); ★2 re-measured down to 3 copies plus a homonym; ★1 kept with its census as sole source. |
| 23 | `--resume` documented for headless use | **Accepted;** and our dispatcher already uses it for windows (`dispatcher.py`). Detached systemd use is still untested. |
| 24 | resumed-session cost depends on cache hits | **Accepted.** Stages hours apart mean cache misses; B's cost is the pilot's to measure. |

**The two strongest objections**, in our reading: **7–9** (who decides which state transition is valid, and what stops a stale holder), which changed the core (the dispatcher as sole authority, fencing tokens); and **13** (a blind judge cannot check fixes to findings it was not shown), which changed the judge into two phases.

**Where the passes still disagree.** GPT would build the coordinator database first (D); this design keeps git-sharded files with the dispatcher as the authority. Both agree: stabilise durable state before testing resume. GPT also advised piloting one mod; he chose three side by side.


## Claims table

| # | claim | value | status | ★ |
|---|---|---|---|---|
| 1 | stores holding Gimme Some Slack's state | ~17 (39 by file kind) | measured (census, `00-measure.md`) | ★ |
| 2 | places holding its current stage | 3 copies + ledger notes, and one homonym key (re-measured from 6) | measured twice | ★ |
| 3 | distinct runs touching it | ~126, upper bound | measured (id regex) | |
| 4 | live-proven work per day, Foundry/Bench vs now | not comparable: ledger verify items 15.2 → 13.4 → 3.7/day, but pipeline live results moved to mod folders (4 in-game visits in 3 days) | measured by two rules; first reading ("rose") withdrawn | ★ |
| 5 | items filed/day A→C | 128.8 → 161.0 | measured | |
| 6 | full rehydration exceeds one window | ~297k tokens | measured (bytes/4) | ★ |
| 7 | minimum pickup today | ~10k tokens | measured | |
| 8 | `--resume` in our code | unused in the pipeline launch path; already used by `dispatcher.py` to resume windows | measured (grep, widened at re-measure) | ★ |
| 9 | `claude -p --resume` works in a detached systemd run | documented for headless use (per GPT, Anthropic headless docs); our systemd use untested | guess ~80% | ★ |
| 10 | resumed session cheaper or equal per stage vs packet run | ? | guess ~50% | ★ |
| 11 | build effort A 3–4 runs, B +2, C least code | | guess ~55–70% | |
| 12 | restarts lose ~12% of owed things | 9 of 76 | measured in `2026-11-15-conductor-restart-loses-nothing.md` | |
| 13 | about half of the evening's runs were self-repair | ~half | Conductor's estimate, not measured here | |
| 14 | in Relentless sessions that passed 200k, landings after 200k / after 250k | 208 / 111 of 249 (84% / 45%); 51 of 74 sessions landed nothing before 200k | measured (3,260 transcripts, `02c-context-evidence.md`; a landing is any publish) | ★ |
| 15 | the 200k restart is our setting | `dispatcher_schedule.json` backstop 110k soft / 200k hard, his card 2026-11-01 | measured (read) | ★ |
