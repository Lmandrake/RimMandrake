# RimPulse — intention, success criteria, architecture and honest state (2026-10-22)

Written by a FOUNDRY helper, 2026-10-22 ~21:45 PDT, at the owner's request. Every claim cites a file,
commit, item or a measurement taken while writing; **UNMEASURED** marks what was not measured. Repo files are
given at the read-only mirror `D:\Luke\dev\RimMandrake\...`; runtime state lives in WSL at
`\\wsl.localhost\Ubuntu\home\mandrake\.local\state\rm-dashboard\` (the code calls it `STATE_DIR`).

GPT's review of this document: `D:\Luke\dev\RimMandrake\design\RimMandrake\rimpulse_gpt_review_2026-10-22.md`.

## (a) Purpose — the returning owner

### The scenario, in his words

> *"my need to come back to two busy agents (like right now) and roughly know what is waiting for me to look
> at, what needs ruling, and any issues that happened while I was away."* — owner, 2026-10-22

RimMandrake runs two Claude windows, usually at once: **BENCH** (works with him) and **FOUNDRY** (an autonomous
queue), each with its own subagents, plus an art daemon (artpipe), a live RimWorld game and a telemetry stack.
He leaves, for minutes or hours. When he returns, both agents are still busy, and he has to know where things
stand **without interrupting either of them and without reading transcripts.** RimPulse exists to answer three
questions at a glance:

1. **What is waiting for me to LOOK AT?** Things an agent made *for his eyes*: review sheets, contact sheets,
   keeper saves, pictures.
2. **What NEEDS RULING from me?** Open decisions only he can make. Since 2026-10-22 that is a short list:
   `D:\Luke\dev\RimMandrake\design\RimMandrake\delegation_policy.md` §2 (north-star bars; irreversible acts on
   others' work; replacing art he kept; changing his rulings; outward or paid acts; presence-bound acts such as
   flyer live tests). Everything else agents decide (CLAUDE.md, "Agents decide nearly everything", 2026-10-22).
3. **What ISSUES happened while I was away?** Things that broke: a window killed by the kernel's
   out-of-memory killer, a window that died, a daemon that crashed, a game that died. Each must come with its
   **cause**, not only its name.

Running-work presence ("BENCH working, 3 agents") is context for those three questions, not a fourth goal.

### Where it came from

- Design pass 2026-10-08, `Transient/away_dashboard_design_2026-10-08.md` (seat-clone only, untracked):
  measured that every earlier dashboard here (FleetView, `board.py` toasts, the GitHub mirror, the Hub,
  the maturity dashboard, `board_live.py`) **died because he had to go and open it or an agent had to
  remember to refresh it**; only pushed or timer-driven things survived (memwatch toasts, the status line,
  Lodestar `BOARD.md`). That pass recommended alarms plus a digest first and a statusline strip as the
  surface; he chose otherwise (section e).
- Built as `AWAY_DASHBOARD_BUILD_1` (BENCH), first commit `593156f3a`, 2026-10-08; closed done 2026-10-21
  ("RimPulse in daily use since").
- Failure that prompted this document, 2026-10-22 evening: the collapsed widget showed two red pills,
  `✖ BENCH 19:40` and `✖ RIMPULSE 19:11`, naming a seat and a time but no cause. He said *"Do you still
  remember the reason for RimPulse at all?"* and *"I'm having to deduce that RimPulse appears nearly
  broken..."*. The causes (kernel OOM kills of the BENCH tool cgroup at its 6 GB cap, ×5 today; of
  `rm-pulse.service` at its 256 MB cap, ×6 today, systemd restart counter 10) were only in the expanded rows.
  Filed `RIMPULSE_RED_PILLS_FIX_NAME_THE_CAUSE`.

## (b) Success criteria — what a glance must do, and must never do

### In about 10 seconds, from the collapsed strip or the expanded widget, he must know

| # | He must be able to say | Without |
|---|---|---|
| G1 | "N things are waiting for me to look at; the newest is X" | opening anything |
| G2 | "N decisions need me; the oldest/most blocking is X, and an agent is **blocked right now** on Y" | reading item files |
| G3 | "While I was away: these things broke, **because** ...; this one is still broken / this one recovered" | expanding rows, reading logs, deducing |
| G4 | "BENCH and FOUNDRY are both alive and working (or: one is idle waiting for me)" | switching windows |
| G5 | "I can trust this view: it is fresh and every source is reporting" | guessing |

### It must never

- **N1 — make him deduce.** Every alarm states what happened, to what, and why, in its own text (pill or row).
  A seat name and a time is not an alarm text.
- **N2 — show an unexplained red.** Red means "something broke that matters to you", with its cause and its
  current state (still broken / recovered / fixed by commit X).
- **N3 — cry wolf.** An alarm he cannot act on, or that is already resolved, trains him to ignore red.
  (2026-10-08 design, adopted from GPT: alert precision ≥90% or the alert type is cut.)
- **N4 — hide a real problem** behind a fold, a count, a stale snapshot, or a collector that silently stopped.
- **N5 — look healthy while stale** (freshness is shown separately; 2026-10-08 design §5).
- **N6 — need upkeep from him or an agent** to stay current (the measured cause of death of every earlier
  dashboard; kill criterion: >15 min/week upkeep).
- **N7 — steal focus** (owner complaint 2026-10-08; `lantern.pyw` docstring).
- **N8 — put unread material in front of him** (CLAUDE.md "Nothing reaches the owner unread", 2026-10-22):
  what it lists to look at should already have passed an agent's own look.

## (c) Current architecture

All code in `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pulse\` (19 commits, `593156f3a` .. `d320538a7`).
🔴 The systemd units run the code in the **BENCH clone** (`/home/mandrake/rm/bench/src/...`, see
`systemd\rm-pulse.service` `ExecStart`), so a FOUNDRY commit reaches the daemon only after BENCH pulls.

### Spine: `pulse.py daemon` (`rm-pulse.service`)

- systemd user service, `Restart=always`, `Nice=10`, `MemoryMax=768M` (was 256M until `d320538a7`,
  2026-10-22). A 5 s collector loop plus an HTTP/SSE server on `127.0.0.1:8765` (`/api/now`, `/api/stream`,
  `/api/ack`, `/api/seen`, `/api/probe`, `/api/thumb`, `/api/metric`, `/api/series`).
- `rm-pulse-health.timer` every 2 min runs `pulse.py health --restart`: restarts the service if `/api/now`
  is older than 60 s.
- `rm-pulse-digest.timer` at 06:00 and 17:30 runs `pulse.py since --scheduled`.
- Each tick (`Collector.gather` → `pulse_core.collect_snapshot`, a pure function) writes
  `pulse_now.json` (snapshot), `state.json` (acks, seen windows, seen looks, last digest), appends kind
  transitions to `pulse.jsonl` and metric events to `metrics.jsonl`. Every source is wrapped: a failing
  source is reported in `sources` (ok/at/error), never guessed.

### Collectors (`pulse_core.py`)

| Source | Reader | Feeds |
|---|---|---|
| Claude Code session files `~/.claude/sessions/<pid>.json` (status busy/idle/waiting, `waitingFor`); liveness = `/proc/<pid>/stat` start time matches `procStart` | `read_sessions` | window rows, amber, lost-window red |
| Transcripts + `subagents/agent-*.jsonl` (running = moved in 15 min and last record is not `end_turn`); pending `AskUserQuestion` text | `session_extras` | subagent counts, the question text |
| Kernel log `journalctl -k` (`oom-kill:` lines with memcg and cap) every 20 s | `read_kernel_oom`, `kill_class` | OOM reds; planted 128 MiB pen test → calm line; harness test kill → warn |
| memwatch `~/.local/state/rm-memwatch/events.jsonl` | `classify_oom` | fallback only when the kernel log is unreadable |
| rimflow ledger, both clones, folded through `rimflow.model.replay` (re-read when any shard changes) | `read_ledger`, `owner_rulings`, `current_items` | "to rule" (open items with `needs == owner`, 14-day window), done rows, the item each seat is on |
| `hands.jsonl` written by `pulse.py hand <path>` | `read_hands` | "to look at" (deliberate hand-offs) |
| Review-sheet servers: `Transient/biome_ffar/*.serve.log` in both clones, last URL whose `/status` answers 200 (every 45 s) | `read_sheets` | "to look at" (live sheets, grouped "Biome sheets") |
| artpipe state dirs (pending/active/done/failed counts) | `read_artpipe` | artpipe chip |
| `infrastructure/state/BRIDGE` + a RimWorld process probe posted by the widget | `read_bridge`, `classify_game` | rimworld chip |
| Telemetry verdicts `/mnt/e/telemetry/state/alerts.json` (Windows telemetryd) | `read_telemetry` | telemetry red/warn rows, four sparklines |

### Classification (`pulse_core.py`)

- **red** — kernel OOM kill of a seat window/tool cgroup or of a systemd service (`classify_kernel_oom`,
  grouped per seat/service, "today" = since local midnight but at least 6 h); a window whose process died
  while its session file stayed (`classify_sessions`, 24 h window; deaths before the current boot fold into one
  "WSL restarted" warn line); telemetry red alerts.
- **amber** (explicit) — a seat window with `status == waiting` (a question card or permission prompt).
  **amber_soft** — a seat idle ≥60 s after acting, with **no running subagents**, fading after 2 h (owner
  ruling 2026-10-08, section e).
- **warn** — contained harness test kills, WSL restart, telemetry warnings and "telemetry blind".
- **stuck** — busy with no transcript growth for 20 min (dim, never flashes).
- **review** ("to rule"), **look** ("to look at"), **run**, **idle**, **done**.
- Acks: `ack` covers occurrences up to the ack time; a later occurrence re-raises. Ack ≠ resolve. Unacked reds
  stay on screen until their window expires (OOM: the "today" window; lost window: 24 h).

### Surfaces

- **Widget** — `widget\lantern.pyw` (Windows pythonw + pywebview/WebView2; frameless, always on top, never
  takes focus; autostart task `RimFlow Pulse` at logon and every 10 min; self-watchdog) loads
  `widget\index.html` from the daemon. Layout D (owner card 2026-10-10): title bar with one freshness light
  per collector and a `live Ns`/`stale`/`monitor down` stamp; body = unacked red rows, then **"to rule"**
  (seat asks pinned on top, then rulings; 5 shown, `+ N more`, `older (N)` fold after 3 days), then
  **"to look at"** (4 shown; sheets folded into one group; opening dims, never removes — owner 2026-10-10),
  then warn rows, then an "acknowledged (N)" fold; **bottom strip** = alarm pills (red / amber / warn
  only), presence chips (bench, foundry, rimworld, artpipe, mem, other windows dim), and `✓ N` done tally
  (click opens the last digest). Collapsed, only the strip shows. Toasts for new red and seat-amber are raised
  by the widget (memwatch toasts seat OOMs itself, so those are skipped).
- **Digest** — `pulse.py since` writes a dated Markdown file under
  `D:\ClaudeWork\rimmandrake\dashboard\digests\` with ✖ red, ◐ waiting, ◇ to rule, ✓ done (with links),
  ▶ running. Triggers: the 06:00 / 17:30 timer; `./pulse back`; and the `UserPromptSubmit` hook
  `hooks\im_back_hook.py` (installed in `.claude\settings.json`) that prepends it when he types "I'm back"
  (optionally "I'm back 3h" / "since 5pm").
- **Hand-off verb** — `pulse.py hand <path-or-url> --title ... --seat ...` is how an agent puts something in
  "to look at".
- **Metrics** — `pulse.py metrics`: red time-to-notice (first owner prompt in any window after a red opened),
  question age (amber open→close), alert precision (acks labelled actionable vs noise).
- **Phone** — a hook point only (`PHONE_PUSH_ENABLED = False`, `pulse.py`): not ruled (section e).
- **Self-test** — `selftest_pulse.py` (fixture-driven over the pure core): **OK, 0 failing** (run 2026-10-22
  ~21:50).

## (d) Honest current-state assessment (measured 2026-10-22, 21:45–21:55 PDT)

Snapshot at 21:45: `pulse_now.json` 2 s old, every source `ok` — the spine itself is alive and fresh.
Tally: **2 red, 0 amber, 0 amber_soft, 0 warn, 3 run, 43 done, 59 to rule, 25 to look at.**
Strip: `✖ BENCH 19:40 · ✖ RIMPULSE 19:11 · ✓ 43`.

### What works

- **Freshness and coverage (G5).** One light per collector, `live Ns`, `monitor down` pill when the stream
  stops, a health timer that restarts a hung daemon (one `spine_restart` in the metrics log ever).
- **Presence (G4).** Chips correctly showed `foundry run`, `bench run` (with subagent counts in the row text:
  "BENCH working · ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING · 3 agents").
- **OOM attribution in the row text.** The expanded rows do name cause and cap: "OOM kill · BENCH tool cgroup
  at 6.0 GB cap · ×5 today"; "OOM kill · RimPulse daemon (rm-pulse.service) at 256 MB cap · ×6 today · see
  journalctl --user -u rm-pulse.service". The kernel log confirms the counts: 6 kills in
  `app.slice/rm-pulse.service`, 5 in `claude-seat-BENCH-951.scope/claude-code-bash`, 1 planted harness kill
  today (`journalctl -k`, grouped by `oom_memcg`).
- **"To rule" is honest to rimflow.** It folds through rimflow's own replay (lesson
  `infrastructure/state/lessons/20261011T063941Z-BENCH-reader-that-re-derives-rimflow-item.md`, commit
  `9b45858b1`), so it lists exactly the open items with `needs == owner`.
- **Planted test kills are not alarms** (`kill_class`, commit `69c85b19f`); WSL restarts fold into one line
  (commit `8f6167818`).

### What is broken or misleading

1. **Pills do not name the cause (violates N1, N2).** `build_strip` emits `✖ <who> <HH:MM>` for every red; the
   collapsed strip — the form he actually glances at — cannot say what happened. Filed:
   `RIMPULSE_RED_PILLS_FIX_NAME_THE_CAUSE`.
2. **A red stays red after the cause is fixed (violates N2/N3).** The RIMPULSE red at 19:11 still shows at
   21:45 although the daemon has run cleanly since 19:11:48 (`systemctl --user show`: `NRestarts=10`,
   `MemoryCurrent` 215 MB, `MemoryMax` 805306368 = 768M, in effect) and its cap was raised in `d320538a7`.
   An OOM red clears only when acked or when the "today" window rolls (`classify_kernel_oom`). There is no
   "recovered" state: the row cannot tell a still-broken thing from one that broke once and recovered.
3. **The daemon itself was OOM-killed 6 times today at 256 MB** (kernel log; `NRestarts=10` since boot). Cause per
   commit `8f6167818`: reading whole `serve.log` files (17–27 MB) every 45 s; fixed by streaming, and the cap
   raised. Sub-cause, still live (item 6): its own probes grow those logs.
4. **`metrics.jsonl` is 253 MB, 1,828,885 lines, 99.7 % junk.** 1,824,178 lines are `red_noticed` for only
   **25 distinct incidents** (one incident re-noticed 107,304 times): the 5 s tick re-noticed every red still
   on screen (fix in `pulse.py _notice_metrics`, comment "MEASURED 2026-10-22"). **Measured: zero
   `red_noticed` lines in the last hour**, so the fix is live; the file was never rotated or cleaned.
5. **`pulse.py metrics` lies (instrument trap).** It reads only the last 8 MB of the file. It reports "red
   time-to-notice n=60246" (the true count of distinct incidents is 25) and **"alert precision: no acks yet"**
   while the full file holds 17 `alarm_ack` events. All 17 are labelled `noise`, all on "window lost" reds,
   all written within about one second on 2026-10-11 (`state.json` ack times) — a **bulk ack by an agent, not
   his judgement**. So: alert precision is UNMEASURED (no owner-labelled acks exist), and every red type that
   was ever labelled was labelled noise.
6. **Review sheets can never stay "opened", and always look brand new.** Pulse's own `/status` probe (every 45
   s) is logged by each sheet server into its `serve.log` (measured: the log tail is nothing but
   `GET /status?t=...` lines; `all_bridge_art_sheet_2026-10-21.serve.log` is 2.56 MB). `classify_looks` uses
   the log's mtime as the sheet's time and resets `opened` whenever mtime > the seen time — so all 12 live
   sheets showed `since` = 21:44 (now), and an opened sheet reads unopened again within 45 s. This silently
   breaks "opening dims, never removes" (owner 2026-10-10) and makes sheet ages meaningless.
7. **"To rule" is too long to be glanced (G2).** 59 open owner items, oldest 2026-10-09; 20 of them are one
   family (`*_TITAN_POPULATE_*`, filed 10-21 14:43–14:44). The widget shows 5. Whether each still truly needs
   *him* under the 2026-10-22 delegation policy §2 has not been re-triaged (UNMEASURED how many would survive;
   the last bulk triage was BENCH 2026-10-12, ledger `needs` events "keeps RimPulse 'to rule' to real
   questions").
8. **"To look at" is stale and not reviewed-first (G1, N8).** 25 rows: 12 live sheet servers plus 13 hand-offs,
   **the newest hand-off from 2026-10-15** (`hands.jsonl` last written Oct 15). Agents have not used
   `pulse.py hand` for a week; nothing checks that a listed thing passed the "Nothing reaches the owner
   unread" gate (`prereview.json`).
9. **There is no "issues while you were away" list (G3).** Issues are only the red/warn rows currently on
   screen. Not collected at all: failed builds, failed selftests (the nightly sweep log), artpipe failures
   (the chip says "1018 failed" as a plain idle chip), stopped items, hook refusals, a seat that went idle for
   hours, digest timer failures. Resolved issues vanish when acked or expired, so "what happened" decays into
   "what is still red".
10. **Telemetry warnings flap.** Over 14 days: `tel:vitals:hostiles` opened 475 times, `tel:vitals:modal_stuck`
    344, `tel:blind:tps` 123; warn alarms close at a median age of **21 s**. Each re-open gets a new incident id
    (`@since`), so an ack never sticks. Red telemetry: `tel:mem_low` 47 opens, `tel:vitals:colony_dead` 36.
    577 toasts recorded in total (UNMEASURED: how many he saw or found useful).
11. **"Window lost" reds were the worst offender.** 21 such reds opened; the only labelled ones were all
    "noise"; red closes have p90 age ≈ 985,000 s (11 days) — reds lingering until expiry. Commit `8f6167818`
    added the 24 h expiry and the WSL-restart fold.
12. **The "I'm back" path is unused.** Of 42 digests on disk, 9 are `back`, **the last on 2026-10-16**; the
    rest are scheduled. The 17:30 digest today was 73 lines, 56 of them "to rule" rows — a digest dominated by
    the backlog, not by what changed.
13. **Amber worked as designed when it fired** (476 explicit asks, median open 227 s, p90 1,818 s; 181 soft,
    median 595 s) — but whether he noticed them from the widget or from the window itself is UNMEASURED.
14. **Deploy skew.** Units run the BENCH clone's code; FOUNDRY fixes wait for a BENCH pull (`ExecStart`).
15. **Ack is hover-only** (`.ack{opacity:0}` until row hover, `index.html`); there is no ack from the strip.

### Does it answer the three questions today?

| Question | Verdict | Why |
|---|---|---|
| What is waiting for me to LOOK AT? | **Partly** | lists live sheets and old hand-offs; sheets never stay opened (6); hand-offs stopped a week ago (8) |
| What NEEDS RULING? | **Partly** | correct but 59 long (7); seat questions pinned on top work |
| What ISSUES happened while I was away? | **No, not as a list** | only current red/warn rows; pills lack the cause (1); resolved reds linger (2); most failure kinds are not collected (9) |
| (Are both agents alive and busy?) | **Yes** | chips and run rows |
| (Can I trust the view?) | **Yes for freshness; no for metrics** | lights work; `metrics` misreports (5) |

## (e) Decisions already made, and open questions

### Decided by him

| Date | Ruling | Source |
|---|---|---|
| 2026-10-08 20:01, by card | Build the **full beautiful dashboard now**; surface = **floating widget**; amber = explicit requests + finished-and-idle, typed: *"(2) but not if there are subagents or background agents still working"*; digest typed: *"When I say I'm back, and 6am, and 5:30pm"* | ledger note on `AWAY_DASHBOARD_BUILD_1`, 2026-10-09T03:38:47Z |
| 2026-10-08 20:39 | Typed *"I like concept C by the way."*, then by card: **one floating widget in concept C's style (no terminal strip)** | ledger note, 2026-10-09T03:39:48Z |
| 2026-10-08, by card | Install the "I'm back" digest hook | `hooks\im_back_hook.py` docstring; commit `9b17744c3` |
| 2026-10-10, by card | Layout D: two short lists, one chip strip, authors by colour (BENCH green, FOUNDRY orange, ArtPipe purple, emergency red) | `widget\index.html` header comment; commit `f494bdae8` |
| 2026-10-10 | Clicking a look item opens and dims it; **nothing ever drops off when clicked** | `classify_looks` docstring; commit `7f58887b7` |
| 2026-10-22 | Nothing reaches him unread; agents decide nearly everything (§2 short list) | CLAUDE.md; `standing_rulings.md`; `delegation_policy.md` |

Not decided: **phone push** (`PHONE_PUSH_ENABLED = False`, "NOT decided by the owner yet (2026-10-08)");
whether to measure first (2026-10-08 Q6). The 2026-10-08 kill criterion (stop expanding if time-to-notice and
question age do not improve 30 %, precision <90 %, or upkeep >15 min/week) was adopted in the design but has
never been evaluated — and its two inputs are currently unmeasurable (items 4–5).

### Open questions

1. Should a red **auto-clear to a "recovered" line** when its subject is healthy again (daemon running N
   minutes since the kill; window replaced), instead of waiting for ack or midnight?
2. Should "issues while you were away" be a **separate list that persists after recovery** (a log of
   incidents in the away window), distinct from "currently broken"?
3. Should "to rule" show only **§2-reserved** decisions, with everything else re-triaged to agents? Should
   item families (20 TITAN items) fold into one line?
4. Should "to look at" admit only things that passed the prereview gate, and **auto-expire** hand-offs?
5. Is a floating widget the right primary surface, given that the 2026-10-08 measurement said only
   push/timer surfaces survive and the "I'm back" digest has gone unused for 6 days?
6. Phone push: still unruled.
7. Which failure sources are worth adding (selftest nightly, builds, artpipe failures, stopped items), and
   which should never be red?
