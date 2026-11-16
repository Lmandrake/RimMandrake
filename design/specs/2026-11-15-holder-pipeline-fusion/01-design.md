# Holder–pipeline fusion: the pipeline as a long-term holder's checklist

Item: `RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF` · DRAFT for Mandrake, design helper, Sun 2026-11-15
~9:10 PM PST. Design only: nothing here is built, and nothing is built until he picks.
Run files (measurement, outside sources, GPT's blind answer and critique, status): `design/specs/2026-11-15-holder-pipeline-fusion/`.
GPT's critique, verbatim: `design/specs/2026-11-15-holder-pipeline-fusion.gpt.md`.

Tags: `[measured]` (how is said) · `[guess ~N%]` · `[HIS]` his words · `[PROPOSAL]` ours.

## Five-line summary

1. He is right about the store problem `[measured]`: one mod (Gimme Some Slack) has its state in about 17 stores, its current stage written in 6 places, 413 ledger items and 126 agent runs touching it; a fresh agent cannot read all of it (≈297k tokens, more than a window).
2. He is also right that the pipeline turned ownership into handoffs; Anthropic's own published guidance names exactly our shape (separate planning, build and review agents) as the one that "lost context at each handoff".
3. One part of the evening's story is false `[measured]`: live-proven closes per day did not fall since Foundry/Bench (1.7 → 2.9 → 4.0); what rose is churn: items filed per day (129 → 161) and relays to him.
4. The design: one append-only **mod ledger** per mod (sharded by writer so a holder cannot edit a judge's or his words), every other per-mod file becomes a generated view, and a named **holder** that every stage run *is*, starting from a bounded packet the ledger generates; blind judges write sealed findings the holder must answer, and only a judge can turn a finding green.
5. The three options differ in what the holder *is*: the record (A), a resumed session (B), or a long-lived seat (C). Recommendation: **B, built on A's ledger, piloted on one mod with a two-mod WIP limit**, because the ledger is needed by all three and B is the only one that keeps the warm context he asked for without betting on a window staying alive.

## The three options (read this section alone)

All three share the same core, which is his two fixed points made concrete:

- **One mod ledger per mod, append-only, stored nowhere else.** Everything a run learns about the mod (stage moves, bars, tests run, findings, causes tried and refuted, questions and his answers, decisions, spend) is one event in it. `stage.json`, `journal.md`, `log.md`, the status page row and the mod's handoff text stop being written by hand and are printed from the ledger.
- **Blind judges stay.** A judge sees the candidate (a commit), the locked bars and the test entry point, never the holder's story. Its findings go into the ledger and to the holder; the holder fixes; a new blind judge looks again. Only a judge event turns a finding green.
- **Questions to him are ledger events** with an asked / answered / superseded state, checked against his past answers before anyone asks.
- **Two mods advance at a time**, and pipeline-machinery work is capped (it was close to half the runs tonight).

### Option A — "The record is the holder"

**What it is.** Keep today's fresh, capped stage runs launched by the dispatcher, but every run on a mod is that mod's holder by name and lease, starts from a packet the ledger prints (≈10–20k tokens: where it stands, open findings, causes already refuted, his answers, next action), and must write what it learned back as events before it may end. No session is kept warm.

- **Pros.** Smallest change to what runs today; survives every restart by design; cheapest per run; the dispatcher, caps and timers stay. Restarting is a non-event.
- **Cons.** Every run is still a new mind: what the packet leaves out is lost (Cognition: "Actions carry implicit decisions"); this is the shape that already loses context, made better rather than removed. Does not give him "context is kept as it progresses".
- **Build effort.** About 3–4 helper runs (ledger writer and lint, views for one mod, packet, dispatcher reads packet) `[guess ~60%]`. **Test effort:** offline selftests plus a one-mod pilot of about a week.
- **Risk.** Medium-low. The ledger becomes one more store if any writer keeps its old file; the fix is that old files become read-only views the same day.
- **Retired.** Hand-written `journal.md`, `stage.json` as a source, the steward's journal lines, per-mod handoff prose, per-mod rimflow items (findings become ledger events).

### Option B — "The holder is a resumed session" (recommended)

**What it is.** Option A's ledger, plus: each advancing mod has one holder session that the dispatcher *resumes* (`claude -p --resume <session>`) for every stage it does itself, instead of starting a stranger. When the session nears ~120k tokens it writes a checkpoint event and a new session of the same holder starts from the packet. The holder does preflight, build, fixing the judges' findings, and the in-game acceptance; blind judges and the pre-human check stay independent.

- **Pros.** The only option that literally keeps context as the mod progresses, which is his idea; one mind reads every blind finding about its own code; the ledger makes the rotation safe, so a lost session costs one packet, not the mod; matches Anthropic's guidance that "an agent handling a feature should also handle its tests".
- **Cons.** A warm session anchors on its own beliefs (a refuted cause can survive in it; the ledger must win over memory); resumed long sessions cost more per turn than a 15k packet `[guess ~70%]`; `--resume` is unused in our code today `[measured: grep]`, so its behaviour in detached systemd runs is unproven here.
- **Build effort.** Option A plus about 2 runs (session id kept as a ledger event, resume path in the launcher, rotation rule) `[guess ~55%]`. **Test effort:** A's tests plus a resume test (kill a holder mid-stage, check the next one avoids a refuted cause and respects an answered question).
- **Risk.** Medium. Mitigated because A is built first and B falls back to A by itself when a resume fails.
- **Retired.** Everything A retires, plus "new stage, new builder" launches for the holder's own stages.

### Option C — "The holder is a seat" (Foundry/Bench back, with the pipeline as its checklist)

**What it is.** One or two long-lived holder seats (windows like Foundry and Bench were), each holding exactly one mod at a time from preflight to his live walk, doing its own live tests on the bridge. The pipeline's stages become the checklist in the mod ledger that the seat ticks; the dispatcher no longer builds or fixes, it only launches the blind judges and the pre-human check when the seat asks, and wakes the seat when a finding lands. Machinery work stops unless it blocks the held mod.

- **Pros.** What he remembers working; the fewest moving parts; one owner he can talk to about the mod; WIP is limited by construction (seats = mods in flight).
- **Cons.** Throughput is capped at one or two mods; a seat window still restarts at its context limit, and we measured that restarts lose about 12% of what a dying Conductor window owed (`design/specs/2026-11-15-conductor-restart-loses-nothing.md`): the ledger is what saves C, exactly as it saves A and B; the unattended overnight progress the dispatcher gives today stops unless a seat is kept alive; it also undoes part of what he asked for on 11-13 (Dispatch "opportunistically allowing them access").
- **Build effort.** Lowest code (ledger plus a role file) `[guess ~70%]`, highest human-attention cost: seats need waking and handing off.
- **Risk.** Medium-high for flow (idle when no window is up), low for correctness.
- **Retired.** The dispatcher's builder, fixer and steward launches; the steward role at stage changes (the seat is the steward of its mod).

### How each honours his two fixed points

| | Blind judges stay | One monotonic per-mod source of truth |
|---|---|---|
| A | sealed judge findings in their own shard, routed to the holder | the mod ledger; all else views |
| B | same as A | same as A |
| C | dispatcher still launches them, seat cannot reach their brief | same ledger; the seat writes it like any holder |

**Combinations.** A is the first step of B (B = A + resume). C can run *on top of* A or B for the one mod he is sitting with (a window resumes the holder session instead of a timer), so "B now, C-style sitting when he is there" composes cleanly.

**Recommendation: B, built as A first.** Build the ledger and packet (A) for one mod, Gimme Some Slack, turn its old files into views the same day, then switch that mod's holder stages to resume one session. Keep two mods advancing at once. What would change this: if the one-mod pilot shows resumed sessions repeating refuted causes or costing more than about 1.5× an A run per stage, stay at A; if he would rather sit with one mod than have it run overnight, take C on top.

**Decisions for him.**
1. Which option (A, B, C, or B-with-C-sittings).
2. His 11-13 rule says a blind judge "should FIX THEM RIGHT THERE". Tonight's says their feedback "should come to that same builder". The design follows tonight's (judges find, the holder fixes, a new judge re-judges). Confirm that tonight's words replace the 11-13 rule.
3. Pilot mod: Gimme Some Slack (most stores, most history) or FlowWorks.

---

## 1. What we measured

Full tables: `design/specs/2026-11-15-holder-pipeline-fusion/00-measure.md` (read-only census, Sonnet helper, 2026-11-15).

### 1.1 Where Gimme Some Slack's state lives today `[measured: find, du, grep over src/ for writers]`

- **About 17 stores** (39 if each kind of file in the concept folder is counted): the concept folder (169 files, 1.79 MB, 114 commits), ledger events in 6 shards (1,166 events naming the mod), 98 open item files (28 naming it strictly), 121 closed ones, 17 handoffs (438 KB), 139 Conductor log lines, the dispatcher's `state.json`, `ticks.jsonl` and 5 briefs, the status page, the mod's source folder (`CHANGELOG.md`, `KNOWN_LIMITS.md`).
- **The same fact in several places:** the current stage in 6 (`stage.json`, `version/stage_record.json`, the journal's "stands" top, `MATURATION_NOW.md`, the dispatcher's `state.json`, ledger notes); the bar count (48) in 4; his words in 3; Designer results twice (30 result files and 34 KB inside `stage.json`).
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

So live-proven work per day **did not fall**; the evening's sense that "nothing gets proven" is true of that evening, not of the era. What did rise is filing (161 a day now) and the noise reaching him. This supports his own reading that live access was not the missing piece, and points the fix at churn and memory, not at throughput.

### 1.4 What a holder can actually carry `[measured: wc -c, tokens ≈ bytes/4]`

| what a fresh agent reads | tokens |
|---|---|
| the journal's "stands" top alone | ~1.8k |
| minimum pickup today (journal, stage record, bars) | ~10k |
| all mod files except the big test table | ~68k |
| + the 28 open items | ~110k |
| + the test table | ~187k |
| + the 17 handoffs | ~297k (more than one window) |

**What persists is the record, not the context.** A window restarts near 200k; no agent will ever hold this mod's whole history. So "a long-term holder" can only mean one of three things, which are the three options: a **record** a fresh agent rehydrates from (A), a **session** that is resumed while it fits and rotated from the record when it does not (B), or a **seat** whose window is kept up and handed off (C). In all three, the record is what makes it long-term; the difference is how much warm context rides on top.

## 2. Outside practice, and where we violate it

Sources read on the page, quotes verbatim (fetched 2026-11-15):

| practice | source | what it says | where we break it |
|---|---|---|---|
| **One agent keeps a feature and its tests; handoffs lose context** | Anthropic, "Building multi-agent systems: when and how to use them", Jan 2026, https://claude.com/resources/articles/building-multi-agent-systems-when-and-how-to-use-them | "Each handoff loses context." · teams with separate planning, execution and review agents "lost context at each handoff and spent more tokens coordinating than executing." · "an agent handling a feature should also handle its tests, because it already possesses the necessary context." | Our stages are exactly planning (Designer), execution (builder) and review (judge) agents, each a stranger; ~126 runs on one mod (§1.2). |
| **Verification by a fresh agent works** | same article; Cognition, "Multi-Agents: What's Actually Working", Apr 2026, https://cognition.com/blog/multi-agents-working | "Verification subagents succeed because they sidestep the telephone game problem." · review works "best when the coding and review agents do not share any context beforehand." | We keep this, rightly: it is his fixed point. |
| **Writes stay single-threaded; others contribute intelligence** | Cognition, same 2026 piece; and "Don't Build Multi-Agents", Jun 2025, https://cognition.com/blog/dont-build-multi-agents | "multi-agent systems work best today when writes stay single-threaded and the additional agents contribute intelligence rather than actions." · "Actions carry implicit decisions, and conflicting decisions carry bad results" | Today a blind judge "fixes it right there" (his 11-13 rule), so the mod's code has several writers in turn; `stage.json` has at least four writer modules (§1.1). |
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

**Writers (one shard each).** `HOLDER` (the mod's holder, whichever run is it), `JUDGE` (one shard per blind run, sealed when the run ends), `OWNER` (his words, cards and answers, written by the card capture and `--owner-said` paths), `DISPATCH` (launches, leases, stops, spend), `STEWARD` (the Conductor's decisions). A writer can only append to its own shard: the holder cannot edit or drop a judge's finding or his answer. This is GPT's point that the holder owns the mod but not the evidence.

**Monotonic** means history only grows. A conclusion can be overturned (a refuted cause, a pass invalidated by a new commit), by a later event that names the one it supersedes; nothing is ever edited or deleted. Publish refuses a shard that is not a strict extension of its last published form (the existing `NOT_APPEND` check).

**Event shape.**

```
{seq, ts, mod, version, writer, run, kind, subject, supersedes?, code_sha?, body, evidence: [path or sha], authority?}
```

Kinds: `lease.take|renew|release`, `session.checkpoint` (B), `stage.enter`, `stage.exit_claimed` (holder), `stage.exit_confirmed` (judge or steward), `bar.locked|added|eased|deferred` (OWNER or STEWARD with his authority), `test.run` (result, sha), `live.run`, `finding.open` (JUDGE), `finding.claimed_fixed` (HOLDER), `finding.verified|reopened` (a later JUDGE), `finding.disputed` (HOLDER, goes to the neutral fixer per the refusal ruling), `cause.tried|refuted`, `question.ask`, `question.answer` (OWNER), `question.withdrawn`, `decision` (with `--owner-said`/`--by-card`/`--per-ruling`/`--why` provenance as today), `spend`, `note`.

**The single-writer rule, enforced.** One command appends (`modledger append`), checks the writer against the shard and, for `HOLDER`, the live lease token. Views carry "generated from ledger seq N, hash H" and publish refuses a hand-edited view (hash mismatch). A run that ends without having written any event since its start is a flagged run, the same way an item left open is flagged today.

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

Printed from the ledger on demand, bounded (target ≤ 15k tokens; today's minimum pickup is ~10k, §1.4): version and stage; the bars with their latest verdict; open findings with their judge's text; **causes refuted** (so nobody chases them again); his answers that bear on open work; the open questions; the holder's last checkpoint ("what I was doing, what I'd do next"); spend. Everything else is one `modledger show <subject>` away. The full history is never read whole.

### 3.4 The holder

- **Identity:** `HOLDER/<Mod>/<version>`, one per advancing mod version. It is a role with a lease, not a process.
- **Lease:** taken at launch, renewed while running, lapses after 45 minutes idle (the bridge rule's number). A run without the lease cannot append to `HOLDER`. A stuck holder's lease lapses and the next launch takes over from the packet: one stuck run never sticks the mod.
- **Lifetime:** from preflight to his live walk of that version; a new version gets a new holder that starts from the old one's ledger.
- **Rehydration:** A, every run from the packet; B, resume the last session while under the rotation threshold, otherwise the packet; C, the seat's window, with the packet after each handoff.

### 3.5 The pipeline as the holder's checklist

| stage | who | why |
|---|---|---|
| 1 Designer | the Designer with him; the coverage judge stays blind | design is argued with him; the holder does not exist until the version locks (the holder may be started at lock and read the design history) |
| 2 Preflight | holder | its own plan, its own context |
| 3 Offline build | holder | |
| 4/5 Blind challenge | **blind judge finds; holder fixes; a new blind judge re-judges** | judge stays blind; one writer of code |
| 6 In-game acceptance | holder drives the scripted live checks | it owns its tests, as Foundry did |
| 7 Pre-human check | independent fresh agent | a holder must not certify its own evidence |
| 8 His walk | him; the holder prepares the sitting and takes his findings | |

The stage exits are checklist items in the ledger. The holder can only *claim* an exit; a judge, the pre-human checker or the steward confirms it. The dispatcher's question per mod becomes "what is the next unchecked item, and is the holder already on it?".

### 3.6 Blind feedback reaches the holder, the judge stays blind

The judge's brief is built from the candidate commit, the locked bars and the test entry point only: no `HOLDER` shard, no history, no earlier verdicts. Its findings land in its sealed `JUDGE` shard; the holder's packet shows them as open. The holder must answer each one (`claimed_fixed` with a test, or `disputed`); it cannot mark one verified. The next blind judge sees the new candidate and the bars, and its own run decides. Cycles are counted from the shards. Two judge runs in a row passing the same candidate is the exit `[PROPOSAL, from GPT's blind answer]`.

### 3.7 Questions to him: one register

Every question is a `question.ask` event with the exact question, the mod, what it blocks, the obvious answer (Evidence-for-Ask) and the evidence against it. Before asking, the asker searches `question.answer` events across all mod ledgers and his rulings; an answered question is reopened only with a named new fact. The Conductor's daily list is a generated view: open questions, oldest first. This replaces stale files answering for him (the Pyrelands giant question).

### 3.8 Migration, smallest first step

1. Build `modledger` (append, lint, show, packet, views) on rimflow's shard code, with its offline selftest (watch it refuse a hand-edited view and a non-append shard).
2. Backfill Gimme Some Slack: one baseline event set from today's stores (stage, bars, open findings, his answers, refuted causes, open questions). A judge that did not write the backfill compares the packet with the old files.
3. The same day, its old files become generated views; writers to them are redirected or refused.
4. Its next stage run starts from the packet (A). Then (B) resume the holder session.
5. A second mod only after a week, judged by the falsifiers below.

**Cap while piloting:** two mods advancing, and machinery work only where it blocks one of them (his "pipeline fixes its own defects" still holds for a blocking defect).

## 4. Critique

**Where the idea is right.**
- The store sprawl is real and measured (§1.1), and outside practice is unanimous that one record, one writer and one owner per feature beat handoffs (§2).
- His instinct about the live game holds up: live-proven work per day rose, it did not fall (§1.3). The evening's failures were memory failures (a stale answer, a refuted cause relaunched) and churn, not a missing bridge.
- "The pipeline is a checklist, not a handoff" fixes the specific defect that the stage boundary is where context dies.

**Where it fails, or needs a guard.**
1. **A holder marks its own homework.** Guard: a holder can claim, never confirm; only a judge, the pre-human checker or the steward confirms (§3.5–3.6). Anthropic's harness post names the exact risk ("mark a feature as complete without proper testing").
2. **Context limits.** No holder holds the mod; at best it holds the last ~120k tokens of it. The design is honest about this only if the record is complete. B's warm context is a bonus, never the truth: the ledger wins any disagreement with memory.
3. **Anchoring.** A long-lived holder keeps its first theory. Blind judges are the counterweight; a holder whose finding count does not fall for two cycles is rotated (a fresh holder from the packet).
4. **One holder stuck, one mod stuck.** The lease lapses; a takeover costs one packet. With two mods in flight, one stuck mod halves throughput; that is the price of WIP limits and it is worth it if finishing rises.
5. **Concurrency on a monotonic log.** One shard per writer and a lease on `HOLDER` remove write races; merge order across shards is the existing rimflow problem, already solved there.
6. **The ledger outgrows a holder.** It will (Gimme Some Slack's history is already past one window). The packet is the bounded read; full history is searched, never read.
7. **Cost.** Resumed sessions re-read a large context every turn; cheaper per step than a stranger reading 23–52k tokens of briefs and files and re-deriving, or not `[guess ~50%]`. The pilot measures it.
8. **It does not fix churn by itself.** Close to half the evening's runs were the pipeline fixing itself, each filing more tickets. Perfect memory does not stop that; the WIP and machinery caps do. This is the part of the Conductor's earlier "total fix" that the fusion still needs.
9. **It changes one of his own rules.** On 11-13 he said a judge "should FIX THEM RIGHT THERE"; the single-writer rule moves fixing to the holder. His tonight's words point that way, but it is his to confirm (decision 2).
10. **Migration is the dangerous part.** A ledger plus old files still written is store number 18. The old files must become views on the pilot mod the same day, or the pilot proves nothing.

**What would falsify it (measured on the pilot mod over about a week, against the same mod's last week):**
- a refuted cause chased again, or an answered question asked again (target 0; either one falsifies the "single source" claim);
- the mod's stage readable from more than one hand-written place (target 1);
- blind finding to holder fix, median time (should fall);
- dollars per bar that reaches in-game pass (should not rise more than ~1.5×; B is dropped to A if it does);
- items filed per day about the mod (should fall sharply, since findings stop being tickets);
- relays to him about the mod (should fall).

## 5. GPT skeptical review, answered

(pending: critique consult)

## Claims table

| # | claim | value | status | ★ |
|---|---|---|---|---|
| 1 | stores holding Gimme Some Slack's state | ~17 (39 by file kind) | measured (census, `00-measure.md`) | ★ |
| 2 | places holding its current stage | 6 | measured | ★ |
| 3 | distinct runs touching it | ~126, upper bound | measured (id regex) | |
| 4 | live-proven closes/day A→B→C | 1.7 → 2.9 → 4.0 | measured (verify L1+ rule) | ★ |
| 5 | items filed/day A→C | 128.8 → 161.0 | measured | |
| 6 | full rehydration exceeds one window | ~297k tokens | measured (bytes/4) | ★ |
| 7 | minimum pickup today | ~10k tokens | measured | |
| 8 | `--resume` unused in our launch code | 0 hits | measured (grep of `detached_helper.py`, `maturation*.py`) | ★ |
| 9 | `claude -p --resume` works in a detached systemd run | yes | guess ~80% | ★ |
| 10 | resumed session cheaper or equal per stage vs packet run | ? | guess ~50% | ★ |
| 11 | build effort A 3–4 runs, B +2, C least code | | guess ~55–70% | |
| 12 | restarts lose ~12% of owed things | 9 of 76 | measured in `2026-11-15-conductor-restart-loses-nothing.md` | |
| 13 | about half of the evening's runs were self-repair | ~half | Conductor's estimate, not measured here | |
