# Pulse redesign proposal — 2026-10-10

## 1. Diagnosis (why "13h HESTIA EMERGENCY bench-61" appears)

All paths under `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pulse\` (mirror of the bench clone).

**What emits them.** `pulse_core.py:271-273` (`classify_sessions`): any live interactive Claude
window whose session file says `status == "idle"`, has no running subagent, and has been idle
≥ `IDLE_AMBER_SECS` (60 s, `pulse_core.py:47`) becomes an `amber_soft` row reading
"<name> finished — idle, waiting for you". There is **no upper age bound and no project filter**:
`read_sessions` (`pulse_core.py:66-79`) takes every `kind=="interactive"` file in
`~/.claude/sessions/`, whatever repo it is in. `KIND_ORDER` (`pulse_core.py:527`) ranks
`amber_soft` at 2, above `run` (4) and `review` (5), so they sort to the top; `build_strip`
(`pulse_core.py:550-551`) then also makes each one a bordered amber pill in the bottom strip.

**What the three windows actually are** (measured 07:07 from `~/.claude/sessions/*.json` + `/proc`):

| row | pid | cwd | what it is |
|---|---|---|---|
| HESTIA | 167554 | `D:\Luke\dev\Hestia` | another project's window, opened at the 17:50 relaunch and **never used** — `statusUpdatedAt` = its start time |
| EMERGENCY | 167625 | `D:\Luke\dev` | the spare emergency window, same: idle since launch |
| bench-61 | 168170 | `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench` | **not a seat.** A child spawned by the phone's `claude remote-control --name Server` tile (pid 167508): `entrypoint: "sdk-cli"`, `nameSource: "derived"` (cwd basename `bench` + an id fragment). Idle since spawn. |

So "Bench vs bench-61": `seat_name()` (`pulse_core.py:202-204`) strips `AGENT ` from the
user-set name "AGENT BENCH" → `BENCH`; the RC child has no user name, so Claude Code derived
`bench-61` from its cwd. Two rows, one seat. (If two real BENCH windows are open they also
both print as `BENCH` — the row key is the session id, the label is not.)

**Why stale = "emergency-looking".** Nothing is classed red; the word EMERGENCY is just a window
name. But the amber rule was written for "a seat finished its turn and is waiting for my next
message", and a never-touched window satisfies it forever: 13 h idle is treated exactly like
61 s idle. The fix the data implies:
1. Only RimMandrake seat windows (`nameSource=="user"` and name starts `AGENT `, or cwd in the seat
   clones) can raise amber; RC children (`entrypoint=="sdk-cli"`) and other projects' windows
   are presence chips only.
2. "Finished, waiting for you" requires the window to have *done something* since launch
   (`statusUpdatedAt - startedAt > a few s`) and decays to a plain stale chip after N hours (e.g. 2 h).
3. Status chips move to the bottom strip; amber is reserved for a real `status=="waiting"`
   (a pending question card).

**Two further defects seen on the way:**
- `order_rows` (`pulse_core.py:536`) sorts `review` rows **oldest first** (ascending `since`), and the
  widget shows only 3 (`widget/index.html:187`). So the visible three are 13 d, 11 d and 9 d old,
  while today's `ART_TEXTURE_GAPS_FOLLOWUP_1` (20 min old, a real art pick) is hidden under "+5 more".
- `needs --to OWNER` ledger events carry **no `evidence` field** (all 22 measured: keys are
  `event,id,reason,seat,to,ts,tsn`), so a ruling row cannot link to the sheet/PNG it is about.


## 2. Current UI

`D:\Luke\dev\RimMandrake\Transient\pulse_redesign_2026-10-10\current.png` — the live widget (580×400,
its real `lantern.pyw` size) rendered from the daemon's `/api/now` snapshot at 07:07 (saved beside it
as `snapshot_live.json`; `current_static.html` is the same page with that snapshot inlined).

Of ~19 visible lines: 3 are the false "waiting for you" rows, 5 are the "now" presence block,
1 is the clock — **9 of 19 lines (47 %) are "who's awake"**, plus 3 duplicate pills in the strip.
Rulings get 3 lines + "+5 more", and those 3 are the *oldest* (13 d / 11 d / 9 d). Artifacts to
look at get **zero lines**: pulse has no artifact source at all.


## 3. Data sources for the two main panels

Measured 2026-10-10 07:10. "Exists" = already read by `pulse_core.py`.

| feed | source | exists? | notes |
|---|---|---|---|
| **Rulings** | ledger `needs --to OWNER` not yet closed (`classify_ledger`, `pulse_core.py:475-495`) | yes | 8 open ≤ 14 d. Seat is on the event, so author colour is free. **No `evidence` field** → cannot link to what to look at. Sort must flip to newest first. |
| **Rulings: live questions** | session `status=="waiting"` + the pending `AskUserQuestion` text (`session_extras`, `pulse_core.py:110-135`) | yes | Should head the ruling list (it is the only truly blocking thing). |
| **Artifacts: live review sheets** | `Transient\biome_ffar\*.serve.log` — line 1 path, line 3 "N rows · N decided · reviewed / NEVER reviewed", line 4 URL; liveness = TCP connect to that port | **no — add** | 27 sheet servers, all 27 LIVE (python socket check; note `/dev/tcp` silently reads all 27 as dead under zsh). 10 of 27 say NEVER reviewed. ⚠ `SHEETS_INDEX_2026-10-05.md` lists **stale ports** — read the serve.logs, never the index. |
| **Artifacts: files** | `Transient\` html/png/rws newer than N h, in both clones | **no — add, but not alone** | 555 files changed in 24 h (377 bench, 178 foundry): mostly progress logs, `img/` crops and rebuilt sheets. Raw mtime is not "for you to look at". Also: git syncs Transient, so the clone a file sits in does **not** say who made it (`codebase_health.html` is in both), and commits carry no seat. |
| **Artifacts: explicit hand-off** | *new* ledger event, e.g. `rimflow present <path\|url> [--item ID] "one line"` → `{event:"present", seat, evidence, title}`; cleared by `rimflow seen` or the widget's "done" | **no — add** | The only feed that answers "what am I supposed to look at" without guessing, and the seat (= colour) comes free. `needs --to OWNER --evidence <path>` gives rulings the same link. |
| **Keeper saves** | new `.rws` in the Saves folder + its grid-key item file | no | His rule: options he judges in-world ship as saves. Could ride `present` (`evidence` = save path). |
| **Presence chips** | sessions, subagents, game probe/BRIDGE, artpipe, kernel OOM | yes | Become the bottom strip; filter to seat windows; RC children + other projects as dim chips. |


## 4. Options

All three share one shell, built straight from his brief:
- **No clock.** The title bar carries `pulse`, then **one live light per collector**
  (sessions · ledger · sheets · game · art · kernel · mem — green fresh, mustard stale, red down) and the
  "live 3s" light he liked. These are the "lot more of those".
- **One bottom strip** replaces the "now" block, the three false amber rows and the old pills: small chips
  sorted most-recently-active left → stale right (`rimworld · bench ×1 · foundry ×3 · artpipe · mem — ○ hestia · emerg · phone 13h · ✓14`).
  Idle-for-hours windows collapse into one dim hollow-dot chip at the far right; the RC child is
  labelled `phone`, not `bench-61`. Seat chips carry the author colour.
- **Author by colour only**: BENCH = teal `#5fb3ad`, FOUNDRY = mauve `#c38bb5`, anything else = sand.
  Amber/red stay reserved for alarms, so colour never means two things.
- Fed with the real 07:07 data (`mock_data.js`): the 8 open owner-rulings, and 8 artifacts from the
  census (27 live biome-sheet servers rolled into one entry, `codebase_health.html`, five contact PNGs,
  the Messy Conduit live-shot folder). Mocks are static HTML; PNGs are 580×400 @2x, the widget's real size.

### A — Inbox (one list, newest first)
`D:\Luke\dev\RimMandrake\Transient\pulse_redesign_2026-10-10\proposal_A.png`
Rulings and artifacts merged into one queue sorted by age; a 3 px author bar + a kind glyph
(◇ ruling, ▣ image, ▤ page, ☰ sheets, ▦ folder); rulings in cream, artifacts in sand, > 3 days dimmed;
11 rows + "+N older". **Best for:** "what is new since I last looked". **Costs:** rulings and
look-at items compete for the same rows, so an old blocking ruling sinks under fresh PNGs; no thumbnails.
Smallest code change (one list renderer).

### B — Shelf (rulings list + thumbnail shelf)
`D:\Luke\dev\RimMandrake\Transient\pulse_redesign_2026-10-10\proposal_B.png`
Top: "to rule" — 4 newest rulings + "+4 older · oldest 13d". Bottom: "to look at" — a 4×2 shelf of
thumbnails with an author-coloured top edge, caption and age; sheets/pages get a typed placeholder
("27 live · 10 unseen"). **Best for:** art-heavy days — he can recognise a contact sheet without
reading. **Costs:** only 8 artifacts fit; thumbnails need the daemon to serve resized images
(`/api/thumb?path=`); dark images (the plants check) read as blank tiles.

### C — Next up (hero card + queue)
`D:\Luke\dev\RimMandrake\Transient\pulse_redesign_2026-10-10\proposal_C.png`
The single freshest ruling becomes a hero card **paired with the thing to look at to answer it**
(thumbnail, the question, `open picks ↗`, full native path); below, the rest — rulings first,
then artifacts, each with a ↗ when it has something to open. **Best for:** "what do I do right now".
**Costs:** depends on the new `needs --evidence` field (today no needs event carries one — the pairing
and the hero's question line in the mock are hand-filled from the item's reason text); one hero
means the second-most-urgent thing is a plain row.


## 5. GPT review

`codex.exe exec -m gpt-6.1-sol`, reasoning effort high, with `current.png` + A/B/C PNGs attached as images
(`gpt_consult.py` inlines text only, so codex was called directly with `-i`). Full answer:
`D:\Luke\dev\RimMandrake\Transient\pulse_redesign_2026-10-10\gpt_review.md`.

**Ranking: B > A > C, and a hybrid beats all three.**
- **A:** mixing rulings and artifacts makes him classify every row; newest-first buries unanswered
  decisions under fresh output; a topic name ("art texture gaps followup") is not the request.
  Best at dense, predictable scanning.
- **B:** clearest split of his two jobs (decide / inspect) — best fit to the brief — but the
  thumbnails (~130×50 px) are recognition cues, not usable previews; captions truncate exactly where
  batch/version live; the fixed split does not scale past 8 artifacts / 4 rulings.
- **C:** pairing a decision with its evidence is the strongest *idea*, but "freshest" is no reason
  for a hero; the hero eats a quarter of the body; the path clips; dimming old rulings treats age
  as unimportance.
- **Hybrid:** B's two labelled sections + A's compact rows + C's evidence links; each ruling shows a
  plain-language request and an "open evidence" action; ≥ 3 rows per non-empty section, either may
  borrow the other's unused space; "view all N"; no automatic hero. Attaching an artifact to a ruling
  should make one linked item, not two obligations.
- **Shell:** seven green lamps can read as "all healthy" — distinguish stale/error by shape, not colour
  alone; collapse stale sessions into one chip; teal vs mauve are distinguishable, but dimmed variants
  lose contrast on brown — keep request text bright regardless of age.

**What I changed in response** — built `proposal_D` (the hybrid), un-dimmed old rulings (age turns
rust instead), made stale lights a hollow ring and down lights a rust diamond (shape, not just colour).
**Where I did not follow it:** GPT suggests a compact BENCH/FOUNDRY key; the owner said names are
"too expensive", and the bench/foundry chips in the bottom strip already carry the two colours, so the
strip *is* the key. GPT also suggests moving the per-collector lights into a health panel; the owner
asked for "a lot more of those", so they stay visible.

`D:\Luke\dev\RimMandrake\Transient\pulse_redesign_2026-10-10\proposal_D.png`


## 6. Recommendation

**Build D** (two labelled lists, compact rows, evidence links, shared shell). It keeps B's
decide/inspect split that GPT and the brief both favour, scales like A, and carries C's best idea
without the hero. Thumbnails shrink to 26×18 recognition chips on artifact rows only.

Backend changes D needs, in order (each independently useful, none built — PROPOSE ONLY):
1. `classify_sessions`: amber only for seat windows that actually did something since launch; never for
   `entrypoint=="sdk-cli"` (RC children) or other projects; decay to a stale chip after ~2 h. Rename the RC
   child chip `phone`. (Fixes the three false rows today.)
2. `order_rows`: rulings newest-first (today the 3 visible are the 3 oldest).
3. New collector `read_sheet_servers()`: `Transient\biome_ffar\*.serve.log` + TCP check → one "N sheets
   live · M unseen" row. Never read `SHEETS_INDEX_*.md` (its ports are stale).
4. `rimflow needs --evidence <path|url>` and a new `rimflow present <path|url> [--item ID] "line"` ledger
   event (seat = colour, free); pulse lists open presents until seen/closed.
5. Daemon `/api/thumb?path=` (Pillow, cached) for the 26×18 chips; strip + lights in the widget.


## 7. Decisions for the owner (question cards)

1. **Layout** — Which layout should Pulse become?
   - D: two lists — rulings on top, things to look at below, one line each with a tiny preview (recommended)
   - A: one combined list, newest first
   - B: rulings list on top, picture tiles below
   - C: one big "do this next" card, then the rest
2. **Look-at feed** — What should count as "something for you to look at"?
   - Only what an agent explicitly hands you (they mark it when they make it) (recommended)
   - That, plus every review sheet that is currently being served
   - Anything new in the Transient folder (about 550 files a day — very noisy)
3. **Old asks** — What happens to a ruling nobody has answered for a week or more?
   - Stays in the list until resolved, age shown in rust (recommended)
   - Moves into a collapsed "older" group at the bottom
   - Drops off after 14 days, as today
4. **Gone when** — When should a "look at" item leave the list?
   - When you click "seen" on it (recommended)
   - As soon as you open it from the widget
   - Only when the agent closes the related item

