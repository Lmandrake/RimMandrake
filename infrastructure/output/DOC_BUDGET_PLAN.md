# DOC_BUDGET_PLAN.md — how each over-budget document gets back under

_A plan, not an edit. Nothing in this report was changed; four seats are writing
these files live and `queue/CREATE.md` and `queue/PROJECT.md` were dirty in
`git status` while it was written._

**Baseline: `ad8455b`, 2026-08-14 02:13 UTC.** Line numbers below are from that
tree and **will drift** — re-check with `grep -n` before cutting, never trust a
number here as a target.

**Measurement:** `python3 src/RimMandrake/Utils/doc_budget.py` →
**12 files over budget, 1,922 excess lines.**

**This report is not authoritative** (`infrastructure/output/README.md`): no seat
may cite it as a rule. It is a worksheet. When a cut lands, the finding lands in
`CLOSED.md` or a trap file and this document becomes spent.

---

## The scoreboard

| file | lines | budget | over | dominant cause |
|---|---|---|---|---|
| `infrastructure/state/queue/CREATE.md` | 588 | 150 | **+438** | closed bodies + 3 `<details>` archives of superseded text |
| `infrastructure/state/queue/OPS.md` | 556 | 150 | **+406** | one finished investigation never collapsed to its conclusion |
| `infrastructure/state/queue/VISION.md` | 404 | 150 | **+254** | 10 decided items still under a heading that says `## Open` |
| `infrastructure/state/NEXT_RELOAD.md` | 642 | 400 | **+242** | organised by seat, not by phase; closed bodies retained |
| `infrastructure/state/V1_SCOPE.md` | 539 | 300 | **+239** | successive corrections appended instead of replacing |
| `infrastructure/state/queue/BRIDGE.md` | 350 | 150 | **+200** | two items each filed twice by two routes, never reconciled |
| `infrastructure/agents_def.md` | 237 | 200 | **+37** | one-day regrowth of the live-bridge cluster (rules 1a/1b/1c) |
| `infrastructure/state/queue/PROJECT.md` | 186 | 150 | **+36** | one inbox item restates the skill it points at |
| `CLAUDE.md` | 328 | 300 | **+28** | restates `skills/agent-messaging/SKILL.md`, which it already cites |
| `infrastructure/agents/OPS.md` | 147 | 120 | **+27** | two seat-specific sections duplicating `agents_def.md` rule 7 |
| `infrastructure/agents/PROJECT.md` | 130 | 120 | **+10** | `## The MVP seat` restates `agents_def.md` |
| `infrastructure/agents/BRIDGE.md` | 125 | 120 | **+5** | one section duplicated by the block 8 lines below it |

**The single biggest win: `queue/CREATE.md`, −274 lines**, and 119 of those are
three `<details><summary>original entry</summary>` blocks the file itself labels
superseded. That is one delete, no judgement, no rehoming.

---

## 🔴 Read this before cutting anything

**1. Verify the destination exists first** (`DOC_BUDGET.md`, "Before you collapse,
summarise or defer anything"). Two claimed destinations were checked during this
audit and came back **different**:

| claim | reality |
|---|---|
| the `BTD_Jawa` dedupe lesson is "filed as a trap" | ❌ **no such entry exists.** `grep -rn 'BTD\|Xenotype Remix\|dedupe' skills/rimworld-modding/references/` returns only Wookiee and Hutt entries. **Write the trap before deleting `queue/OPS.md` L389–494.** |
| "a def dump is DISK, not RUNTIME" needs a new home | ✅ already fully homed at `skills/rimworld-debug-testing/SKILL.md:186`, §5, with its own worked measurement. Do not write a second copy — `DOC_BUDGET.md`'s anti-rule says one durable home, never both. |

**2. Only two sinks have headroom.** `CLOSED.md` 53/150 and
`skills/rimbridge/references/traps.md` 283/700. **Do not move bulk into another
queue file — all five are over their own budget.** Moving 40 lines from
`NEXT_RELOAD.md` into `queue/OPS.md` is not a cut.

**3. Cite headings, not line numbers.** Every cut here breaks inbound citations,
and the repo already carries stale ones: `infrastructure/state/TODO.md:163` cites
`NEXT_RELOAD.md:784` in a **642-line** file; `queue/OPS.md:311` cites
`agents_def.md:605` in a **237-line** file. Six docs cite `V1_SCOPE.md` by line
(`design/Jawa/worldbuilding/row8_build_order.md` four times). **Repoint to
headings in the same commit as the cut**, or the cut manufactures more rot.

**4. One pass per file, then commit and push** (`agents_def.md` rule 6a). A held
file instructs peers not to write.

---

# The per-file plan

## 1. `infrastructure/state/queue/CREATE.md` — 588 → ~314 (−274)

**Why it is over:** closure was recorded by *prepending a ✅*, not by deleting.
~341 of 588 lines sit under a heading that already carries a ✅ and a hash, and
the file archives its own git history inline.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | three `<details><summary>original entry</summary>` blocks | 181–226, 267–316, 339–361 | 119 | **delete** — parents are `✅ CLOSED 61fe954 / 48e5e16 / cb95f60`; git holds them. C5's own closer says *"The brief's transform was WRONG… Read the commit before trusting the numbers below."* | **119** |
| B | `### 🔴 C3a. ART REVIEWED BY THE OWNER, 2026-08-13 — three fixes owed` | 57–145 | 89 | one `CLOSED.md` row (`7e3018e`). Generalisation already at `skills/rimworld-modding/references/traps-art.md:75`. **Keep L137–138** (the unruled head shapes) and **L140–144** (the Pillow interpreter path → better in `infrastructure/agents/CREATE.md`) | **~82** |
| C | `## Closed` section — C1, C2, C9 | 407–455 | 49 | three `CLOSED.md` rows. **C1 is already `CLOSED.md:16`** — pure duplicate today | **~45** |
| D | `### C4. ✅ Gravship comp radii — CLOSED offline` | 228–257 | 30 | one `CLOSED.md` row; its three findings were already filed out to `queue/BRIDGE.md` B3, `queue/VISION.md` V13, `TODO.md` §20 (it says so at L251–256) | **~28** |

**Earns its length — do not cut:**
- `## C-LOAD` (520–588, 69) — fully open, and the **only** record that
  `mandrake.jawa.armoury` names two packageIds that do not exist. Cutting it
  re-costs a full audit of a 580-mod list.
- `### C12` (383–400) — a live hazard: two textures shipped by both
  `Jawa_Patches` and C6's fix mods, resolved by load order.
- `#### 🔴 RETIRING mandrake.missingartfixes` (163–180) — ordered procedure;
  step 1 must precede the folder delete or the blast-door brief dies with it.
- The rows 3/4 map-gen trap (482–488) — prevents a guaranteed false negative
  inside a ~25-minute load.

---

## 2. `infrastructure/state/queue/OPS.md` — 556 → ~306 (−250)

**Why it is over:** a completed investigation was never collapsed to its
conclusion. L12–233 (222 lines, 40% of the file) is the Faction Control dig; its
entire actionable output is two sentences at L198–200. The rest is method, plus a
measurement the heading itself calls *"(historical — the world it describes is
being discarded)"*.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | `### The proposed exclusion list` + `### Measured evidence (historical…)` | 70–126, 127–177 | 108 | two-line pointer to `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`, which supersedes it section-for-section. ⚠️ **Carry two things across first:** L163–166 (`V1_SCOPE.md:233` says 32 factions, it is **41**) → `queue/PROJECT.md`; L109–112 (BRIDGE still calls Rebel Alliance a fiction problem) → `queue/BRIDGE.md` | **~104** |
| B | `## From BRIDGE — three identical "Jawa" rows` + its retraction blockquote | 389–430, 469–494 | 68 | one `CLOSED.md` row. 🔴 **Blocked: write the trap entry first — it does not exist** (see §3 of the pre-flight). ⚠️ The retraction sits **80 lines below** what it retracts, with two live owner asks wedged between; a reader acts on 42 lines of withdrawn analysis before reaching it | **~66** |
| C | `### 🔴 5b. ANSWERED — and there is NO suppression field` | 178–233 | 56 | **keep L188–200** (the `FactionDensity` fields and `__result = dist < fd.Density;` — row 2 is open and this is the load-bearing negative). Cut the IL-vs-GitLab method, the 1.6 deltas, the ilprobe note (→ `src/RimMandrake/Utils/ilprobe/`), the parse traps (→ traps) | **~42** |
| D | savegame block item 5 | 42–68 | 27 | ruling already `CLOSED.md:19`; Steam Cloud lesson already `traps-mods-and-managers.md:116`. **Keep L60–63** — an open owner question (the delete-all-savegames order is not in effect on disk) | **~24** |
| E | `### O6. ✅ DONE` (306–314) and the duplicate O5 (293–301 vs 363–367) | — | 23 | `CLOSED.md`; keep the ruling copy of O5, delete the "possibly moot" framing | **~14** |

**Earns its length — do not cut:**
- `## Open` (236–291) — eight genuinely open items at 4–11 lines each with
  evidence intact. **This is what the whole file should look like.**
- O-v2 / O-v3 (431–468) — owner's asks, each with a do-not-break constraint.
- `### O-v.` (371–386) — costs a startup complaint on a ~25-min load, and
  carries the owner's veto *"Ask me before deleting it."*
- The `Jawa_Patches` def-resolution list (500–505) — gate evidence for CREATE's
  v1 rows 3/4. If it moves, it moves to `NEXT_RELOAD.md`, **not** `CLOSED.md`.

---

## 3. `infrastructure/state/queue/VISION.md` — 404 → ~154 (−250)

**Why it is over:** ~215 of the 254 excess is closed bodies never deleted. Ten
items are decided and **eight still sit under a heading that says `## Open`.**
The authority is `infrastructure/state/AGENT_VISION_state.md` §3.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | `### V11. Space Tower — ✅ RULED IN, conditionally` | 108–194 | 87 | one `CLOSED.md` row. Design at `design/Jawa/worldbuilding/orbital_towers_and_the_sky_ladder.md`; verdict already duplicated at `queue/CREATE.md:425`. Move only L183–189 (no licence file; `rootSelectionWeight` declared twice) | **~85** |
| B | `## Open — the roster's verified defects` (V1–V6) | 35–79 | 45 | six `CLOSED.md` one-liners. All six closed per state file §3; V6 also `CLOSED.md:49`. Citations already in `design/Jawa/worldbuilding/faction_stage2_gap_audit.md` — **verify that file's contents before deleting** | **~44** |
| C | `## ✅ V-x. CLOSED CHECKED-AND-FINE` | 376–404 | 29 | one `CLOSED.md` row. Self-confessed: *"Body kept below only so the reasoning is legible"* + a `<details>` wrapper round the wrong filing. That is provenance in the doc, verbatim | **29** |
| D | `## Filed by CREATE` / `### V13. ship_designs.md … stale` | 248–271 | 24 | one `CLOSED.md` row — the fix is already in the file | **24** |
| E | `## ⭐ V-new` items 1–3 (275–286) · `### V12` (238–246) · `### V10 ✅ CLOSED` (101–106) | — | 27 | V-new 1–3 are verbatim duplicates of `CLOSED.md` rows 49/52/53; V12's state file now exists (90 lines). Keep the Sith joint-build paragraph 288–292 | **~25** |

Optional: `## Filed by OPS — PLAYER-ZERO PROPOSITION` (332–374, 43) is **open** but
restates `WORLDGEN_FACTION_CHECKLIST.md:160–178` — compress to ~8 (the ask, the
pointer, the O10 blade caveat), **−35**. Rule, do not close: it is VISION's call.

⚠️ **One contradiction to resolve, not to act on blindly:** the queue marks V10
`✅ CLOSED`, the state file lists V10 as still open. The queue's claim is stronger
(dated check, quoted line) — confirm before deleting.

**Earns its length — do not cut:**
- `## ⭐ V-crit. The faction exclusion list — and OUR factions come FIRST`
  (295–330) — owner's sequencing rule verbatim, on the critical path for a
  **one-shot** worldgen screen, with a three-point definition of done.
- V7 (82–87) — four measured live values. Evidence, not provenance.
- V14 RimTunes (206–231) — two unanswered questions gating downstream tagging,
  with defNames and counts.

---

## 4. `infrastructure/state/NEXT_RELOAD.md` — 642 → ~230 + a new 45-line doc

**Why it is over:** it is organised **by seat** (`BRIDGE'S OWN ROWS`, `CREATE'S
ROWS`) but read **in one linear pass by whoever is driving the load**. The real
boundary is *when*, and it is scrambled: the deploy that gates two ⭐ v1 rows sits
at line 565 of 642, and the pre-launch mod-list work is split 350 lines apart.

**Closure notation is inconsistent — five different forms**, none of them the
`CLOSED.md` one-line form rule 3 mandates. ~28 items: 3 closed, 3 partly, 22 open.

### 4a. Cuts — 161 lines

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| C1 | `## ✅ v1 ROW 2 — Faction Control's settings panel — **DONE, DO NOT SPEND A LOAD ON IT**` | 354–410 | 57 | one `CLOSED.md` row; derivation lives verified at `queue/OPS.md:178`. Keep L406–408 (the ⚡ `rimworld/update_mod_settings` test — still open) | **54** |
| C2 | shutdown-window MOOT notice + ❌ correction + mtime table | 90–128 | 39 | `CLOSED.md` + one trap. Keep the 2-line mtime rule. **Retitle the section** — "BEFORE THE GAME GOES DOWN" is itself the falsified claim | **37** |
| C3 | `### 🔻 (a) FOR OPS — seven fix mods … load NOTHING` | 467–502 | 36 | **move to the new §0 PRE-LAUNCH.** Drop the per-mod `loadAfter` column (superseded 4 lines later by "one slot clears all seven") and L498–502 (duplicates L636–638) | **18** |
| C4 | `### 🔴 #1 in full — the droid ruling's load-bearing family` | 423–458 | 36 | keep the 3-call block, the PASS/FAIL table, the two ⚠️ reads. Delete the W8 history — already `CLOSED.md:37` (`fc460e3`) | **14** |
| C5 | `### ⚠️ The design is settings-dependent, with 0.28 of a cell of margin` | 318–332 | 15 | closed at `CLOSED.md:47`. → `skills/rimbridge/references/traps.md` (283/700, has room). Keep 2 lines pointing at FIRST CALL 1 | **13** |
| C6 | `**2 — RETIRING mandrake.missingartfixes HAS AN ORDER…**` | 583–592 | 10 | pointer only — target verified at `queue/CREATE.md:163`. It already says *"Do not re-derive the sequence"* | **9** |
| C7 | `### The owner's rule, which outranks the list` + R1/R2 | 77–85, 59–66 | 17 | `CLOSED.md`; both R1/R2 say "changes nothing this run". Operational content survives at L41–44 | **16** |

### 4b. The audience split — a **phase** split, not a seat split

161 lines of cuts still leaves 481, 81 over. **The split is required, not optional.**

**Doc 1 — `NEXT_RELOAD.md`, the RUN SHEET (~230 lines), ordered by phase:**
§0 PRE-LAUNCH game DOWN (the six-file deploy, mod-list rows, the seven fix mods,
the `ModsConfig` mtime rule, `refresh.py`) · §1 the worldgen screen · §2 FIRST
CALLS 1–3 · §3 BRIDGE's batch · §4 gravship build sequence · §5 the quest script ·
§6 fresh map for row 4 · §7 ion vs droid · §8 AFTER: carry-ins and the harvest.

**Doc 2 — `infrastructure/state/LOAD_OBSERVE.md` (~45 lines).** A different reader
in a different posture: the owner watching a screen while BRIDGE fires calls. One
line each, no order, no procedure — the 6-row check table, row 4's visual
signature, the "which Jawa" trap, the seven mods that can never produce a log
line, and the thesis at L631–638.

**No third document.** The reference material already has homes:
`skills/rimbridge/references/traps.md`, `CLOSED.md`, `queue/OPS.md` §5b.

**Earns its length — do not cut:**
- **L53–57, the R4 conditional** — a decision that *cannot* be precomputed, on a
  screen that cannot be revisited, whose failure costs another ~25-minute
  session. Highest value-per-line in the repo.
- §3 FIRST CALLS (157–185) — *"A ship built on the wrong answer does not lift and
  **nothing logs why**."*
- §5c `### 🔴 The build sequence is FIVE steps, not the JSON's three` (277–303) —
  25/25 vs **0/25** measured, 103 → 0 refused cells, and a one-way door.
- L512–519, the `Jawa_ClaimRumour` script — eight lines, zero prose, executable.
  **This is the form the whole file should be in.**
- L631–638 — *"Exit 0 means the LOG is clean. It does not mean the load passed."*
- **Every measured number**, wherever it sits. Cut the story, keep the citation.

🔧 **Free fix while in there:** five `file:///` URLs violate the current path rule
at L249, 316, 323, 419, 426 — L323 carries `%20` twice.

---

## 5. `infrastructure/state/V1_SCOPE.md` — 539 → ~274 (−265)

**Why it is over: successive corrections were appended as new headings instead of
replacing the text they corrected.** The gravship floor question is stated **five
times in five states**, and they now contradict each other in-file: L180–184 says
*"The floor contradiction is CLOSED and the README was wrong"*; L227–231 then
instructs the reader to *"Verify the export re-imports with its floors before
calling the row done."* **A reader arriving at L227 re-runs a test closed at L180.**

### 🔴 Live defect — the burn-down disagrees with itself, 70 lines apart

The table at L296–305 reads row 3 🟩 **BUILT**, deployed and row 8 🟩 **BUILT +
EXPORTED**. The prose at L376–381 reads *"Row 3 — not started"*, *"Row 8 — not
started"*, *"Net: v1 build is still 0"*. **This is PROJECT's accountable
deliverable contradicting itself.** Fix it in the same pass, whatever else happens.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | `### ⚠️ CORRECTION — "offline design loop" was MY overstatement` | 120–165 | 46 | **delete** — already present at `queue/BRIDGE.md` §B-new/§B-v2 and `skills/gravship-layout/SKILL.md:180–215`. Lesson L162–164 → `traps-tooling.md` | **~44** |
| B | `### ⚠️ Row 5's gate was wrong` + `### ⚖️ Row 5 RULED — it closes on BTD_Jawa` | 386–397, 398–452 | 67 | keep ~6 lines (the ruling + the reversal fact). `queue/VISION.md:376–404` already did this collapse properly, with the wrong filing in `<details>`. **The L419–423 trap is already homed** at `skills/rimworld-debug-testing/SKILL.md:186` — do not write a second copy. ⚠️ L425–452 is **corrupt**: L431's "SUPERSEDED" ruling states the *same* conclusion as the ruling that superseded it, so the record no longer shows what changed | **~61** |
| C | the four gravship row-8 sections | 93–119, 166–185, 208–236, 251–265 | 91 | `design/Jawa/worldbuilding/row8_build_order.md` + `skills/gravship-layout/SKILL.md`. **Keep the gate blockquote L220–222 and the 4-criterion table L173–178** — that is the burn-down for row 8. Delete the redundant floor restatements | **~75** |
| D | `### 🔴 THE HEADLINE: the campaign world has still not been generated` | 307–385 | 79 | keep ~10 lines (quicktest-only, the score, "rows 2 and 7 are one event"). Mechanism narration already at `queue/OPS.md:22–235` + `CLOSED.md:19`; Bantha amendment already `TODO_v2.md` §0c | **~60** |
| E | `### Faction Control is live but has NO SUPPRESSION FIELD` | 479–494 | 16 | collapse to one clause in the row-2 table cell. `queue/OPS.md:178–235` holds it at **higher** fidelity — IL disassembly *and* published source | **~15** |
| F | row 1 closed body (blockquote in the burn-down) | 281–291 | 11 | already `CLOSED.md:12` (`fad8bab`) | **~10** |

⚠️ **`### 1. jawa/list_factions needs a SHUTDOWN window` (239–250) is now WRONG** —
it presents the tool as pending and shutdown-gated; BRIDGE built it and
`CLOSED.md:11` records it live with 34 factions (`7bd8b60`). Stale instruction
still steering a reader; delete on sight.

**Earns its length — do not cut:**
- **L28, the owner's ruling verbatim:** *"Everything ships THIN, except the
  gravship, which ships DEEP."* Including the emphasis.
- **`### The gate` (37–52)**, especially *"seen working in-game once. Not 'the log
  is clean' — seen"*, and the ruling that verification rides the bridge not the
  reload. Cited from four design docs.
- **The v1/v2 table (53–67)** — this *is* the scope line, already at target
  density.
- **The burn-down table (296–305)** — PROJECT's accountable deliverable, named in
  the budget tool's own charter. **Fix it against L376–381; never trim it.**
- **`## What v1 explicitly does NOT contain` (495–511)** — its job is to stop
  re-proposals, and it **points** rather than restating. Model section for the
  rest of the file.
- **`### ⭐ THE SEQUENCING CONSEQUENCE` (453–478)** — trim prose to ~15, but keep
  "THE ANCHOR MOVED" and the ordered next-session plan; four seats act on it.

---

## 6. `infrastructure/state/queue/BRIDGE.md` — 350 → ~190 (−160)

**Why it is over — a different cause from the others: the same item filed twice by
two routes and never reconciled.** `B-v1` appears at 220–252 *and* 255–276 (same
ruling, same `Jawa_SaltCrust` defName, same warning, same deliverables). The
mid-game import appears at 278–297 *and* 299–326.

**Two numbering schemes also collide:** `B1/B2/B3` at 28–62 mean the pawn tools;
`B2` at 113 and `B3` at 122 mean unrelated things. This has **already produced a
wrong cross-reference** — L142 says "B1's ranking should drop" but means the B0
block. **Renumber during the cut, while the bodies are being touched anyway.**

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | duplicate `### B-v1. Dry-lake footprint → Jawa_SaltCrust` | 255–276 | 22 | delete; fold its one unique sentence (*repaint must be bounded by BOTH a rect and a source-terrain match*) into the surviving copy and trim that to ~14 | **~40** |
| B | `## ✅ B0. DEPLOYED 2026-08-13 10:05 — byte-verified` | 75–110 | 36 | one `CLOSED.md` row. Self-confessed at L83: *"**Nothing below is outstanding.** Kept as the record of what changed and why."* The 7-row commit table is provenance by definition. Keep the `🔴 STILL OWED` call as 2 lines folded into B3 | **~32** |
| C | `## Filed by OPS — prove_new_tools.py FAILs on a healthy deploy` | 184–216 | 33 | one `CLOSED.md` row (`68a0a30`). ⚠️ **Keep L209–215 — a separate, still-open finding**: deployed DLL mtime 10:05 vs `Player.log` 10:04 ⇒ the 17-tool build has never been loaded. Relocate into the `🟡 B1,B2,B3` block | **~25** |
| D | duplicate mid-game-import blocks | 278–297, 299–326 | 48 | merge to one ~14-line `B-v2` | **~34** |
| E | `## Closed on migration` | 66–72 | 7 | delete — already `CLOSED.md:11` (`7bd8b60`) | **7** |

**Earns its length — do not cut:**
- **`### 🟡 B1, B2, B3 — BUILT AND UNVERIFIED` (28–62)** — the most valuable block
  in the file: three tools that compile but have never run, the exact closing
  command, the census gate value **20**, and the 🔴 `--gm` trap where a wrong
  deploy *silently* strips `jawa/fire_incident` and `jawa/send_letter`.
- **`### B-v3. jawa/order_pawn` (328–350)** — a measured negative with tick counts
  (4520 → 4820 → 5120) proving it is not a paused-game artifact.
- **The ⛔ block at 154–158** — the save is deleted (`acc3261`), so those numbers
  are the only surviving record.

---

## 7. `infrastructure/agents_def.md` — 237 → ~198 (−39)

**Why it is over: a one-day regrowth of a single topic cluster, and it is content
this file's own charter excludes.** The last five commits to the file are *all* the
live-bridge cluster (`a07a711`, `3f8d05e`, `d12b94b`, `aa968e0`, `c70aeb9`). Rules
1a+1b+1c are **64 lines, 27% of the file**, and none existed at the dissolution
(`infrastructure/archive/OLD_HISTORY.md:58` — *"564 lines → 158, nothing lost"*).

The charter at L3–4 is the failing test: *"what is left is only what sits between
seats and lives nowhere else."* Most of 1b/1c is **bridge operating knowledge**,
and it demonstrably lives elsewhere.

⚠️ **Rule numbers 1a/1b/1c must survive as labels** — all five identity files cite
"rule 1a" by name. Compress the bodies, keep the numbers.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | rule **1c** in full | 106–131 | 26 | the ⚠️ timeout trap is **already stored twice** — `skills/rimbridge/references/traps.md:218–223` and `capability-matrix.md:70–74`; delete. Issuance rationale → commit `d12b94b`. Owner quote → commit `c70aeb9`. **Retain ~5 lines** of the between-seats fact | **~21** |
| B | rule **1b** narration + closing recap | 87–91, 99–104 | 11 | narration → commit `3f8d05e` **but keep the two measured strings** `status: no_game` and `"No current map."`. The ⚠️ paragraph is already `traps.md:274`. **Keep the four-row state table 94–98** | **~10** |
| C | ⛔ addressability paragraph | 45–53 | 9 | `skills/agent-messaging/SKILL.md` §3 (85–97) already owns it; L52–53 duplicates SKILL.md:86. **Keep ~4 lines** — the one fact the skill lacks: only `--name`/`/rename` write the addressable field, so the fallback script cannot rescue a running session | **~5** |
| D | rule 1a's "Why it is written down" | 81–83 | 3 | commit `a07a711`. The rule already works in all five identity files without it | **3** |

**Earns its length — do not cut:**
- **The five-seats table (18–24) + the MVP clause (29–32)** — the authority
  boundary between seats. This is the file's core purpose.
- **Rule 6a (147–152)** — *"Your `M` is everyone else's locked door… holding a file
  for hours **actively instructs peers not to write**."* Plus the measured cost
  (a doc held 14:28→18:01 blocked the load queue). Load-bearing rationale.
- **`## Handoffs` (184–207)**, especially *"validate against the NEWEST backup,
  never a pinned one"* with the literal `ls -t … | head -1`.
- **The BRIDGE/OPS verification-vs-validation split (205–207).**
- **Rule 9 (170–179)** — owner-ratified, unique; the `runtime/` example is what
  makes "who owns this directory?" recognisable as a malformed question.
- **Rule 1's two verbs (65–66)** — *"Asking **authorises**; announcing
  **informs**."* Nine words that both `CLAUDE.md` and the messaging skill defer to.

---

## 8. `infrastructure/state/queue/PROJECT.md` — 186 → ~140 (−46)

**Why it is over:** one inbox item is 26% of the file and **restates the doc it
points at** (rule 4). Otherwise this file is genuinely mostly open, well-compressed
work — the cheapest of the five queues to fix.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| A | `### Two things in it that came from the owner this session` (inside P8) | 171–183 | 13 | **delete** — verified already in the target: `skills/rimworld-start-prep/SKILL.md:111` and §117–139 (`loadBottom` vs `loadAfter`), and §144–146 + :296 (RimSort's "all clear"). Both also in the skill's frontmatter | **13** |
| B | P8 preamble | 140–150 | 11 | L140–143 is provenance (*"Sent as a file, not a message, because no PROJECT seat was reachable"*) → commit. L145–150 restates the skill's model → replace with the path | **~9** |
| C | `## Needs the owner` items 1, 2, 4 | 71–76, 80–81 | ~11 | **delete, no new rows needed** — all three are already answered in `CLOSED.md` rows 50, 51, 52. Only item 3 (77–79) is still unanswered | **~11** |
| D | `## Standing duties` bullet 1 + the stale trailer at 185–186 | — | ~6 | bullet 1 restates the file's own preamble (L3–4); the trailer calls `WORLDGEN_FACTION_CHECKLIST.md` uncommitted — it exists, 22,755 B | **~6** |

**Earns its length — do not cut:**
- **`### 🔴 It contradicts a shipped skill, and the shipped one is wrong`
  (152–163)** — a live doc defect with exact citations:
  `skills/rimworld-load-round/SKILL.md:46–47` claims the game rewrites
  `ModsConfig.xml` on exit, **measured FALSE**, with timestamps, plus the note
  that line 53 half-corrects line 47 so the file disagrees with itself.
- **`## P4. Two git traps` (99–118)** — drafted destination text waiting on a
  lock, not narration. It shrinks when it lands in `CLAUDE.md`, not before.
- **`### P6` (51–61)** — the ⚠️ correction that all five `Jawa*` mods are active at
  `ModsConfig.xml` lines 560–571 of 575, so the rename is a load-order edit and
  **not** a `sed`. Measured, and it changes the cost estimate.

---

## 9. The three identity files — `agents/OPS.md`, `agents/PROJECT.md`, `agents/BRIDGE.md`

**The diff *is* the answer.** All five identity files share an identical nine-section
skeleton. Only **four** sections exist outside it — and all four are in the three
over-budget files. **Every overrun is fully explained by them; the shared skeleton
is not the problem in any of the three.**

| file | extra section | lines | n | verdict | saves |
|---|---|---|---|---|---|
| `agents/OPS.md` (+27) | `### ⭐ You are PLAYER ZERO — comment on anything, decide nothing` | 66–77 | 12 | **delete** — already stated four times in-file (L6, L21, L93, L109). Fold the one unique clause (*play evidence in, decisions out*) into `## Reviewing others` | **11** |
| | `## 🔴 The mod list is YOURS, exclusively` | 37–55 | 19 | compress to 5. **Keep L50–54 only** — RimSort writes `ModsConfig.xml` too, read its mtime first; and a mod-list change lands only on restart. Neither is in `agents_def.md` rule 7, which owns the rest | **14** |
| `agents/PROJECT.md` (+10) | `## The MVP seat` | 50–57 | 8 | **delete** — `agents_def.md:29–32` owns it near-verbatim, and `agents/PROJECT.md:23` already carries the pointer. **Stated three times** | **8** |
| | `**Queue coordination is yours.**` | 29–31 | 3 | delete — `agents_def.md:225–231`; L24 already states the assembly duty | **3** |
| `agents/BRIDGE.md` (+5) | `## Game state — you observe, PROJECT declares` | 81–88 | 8 | **delete**; move its one unique clause (*you are the only seat that can see whether the game is up*) into the rule-1a block **8 lines below**, which already states the rest. Lands BRIDGE at 117 | **8** |

### 🔴 The structural fix — one change, all five files, −105 lines

Two blocks are **byte-identical across all five seats** (verified by `md5sum`):

| block | locations | n each | total |
|---|---|---|---|
| `## Communication` boilerplate | OPS 124–141 · PROJECT 109–126 · BRIDGE 102–119 · CREATE 91–108 · VISION 85–102 | 18 | **90** |
| the rule-1a block | OPS 118–122 · PROJECT 103–107 · BRIDGE 96–100 · CREATE 85–89 · VISION 79–83 | 5–6 | **30** |

The Communication boilerplate also **restates `CLAUDE.md` 273–304 nearly
verbatim** — so it costs context *twice* on every session start, for all five
seats. The rule-1a block cites `agents_def.md` rule 1a **by number while
reproducing it**.

**Replace each with a 3-line pointer, keeping every seat's `**Your register:**`
paragraph intact.** Result: OPS 132 → then cut 1 above lands it under; PROJECT
115, BRIDGE 110, CREATE 98, VISION 93. **All five comfortably under, with room for
rule 4's "one in, one out" to mean something again.**

**Earns its length — do not cut:**
- **`agents/OPS.md` 79–104** — the two error phrasings (`Could not **resolve**
  cross-reference` = def loader vs `Could not **load** reference to` = Scribe),
  *"Disk is not truth while the game runs"*, *"A clean log proves nothing about a
  negative"*, and the `grep -c "<li>"` returns 578 / real 573 / difference is
  `knownExpansions` case. Each is a paid-for debug cycle.
- **`agents/PROJECT.md` 36–49, `## Standing audits`** — five audits, each with
  trigger and command. **This is the only scheduled control in the repo** — the
  mechanism that would have caught the accumulation `DOC_BUDGET.md` documents.
  L38: *"An audit that only runs when the owner asks is not a control."*
- **`agents/BRIDGE.md` 50–75** — *"The artifact outranks the note"*, *"Measure,
  don't estimate"* with the 1,045-things/5.6 s exemplar, *"Silent success is the
  enemy"* naming the exact failures, and the two-grav-engines litter incident.
- **Every `**Your register:**` paragraph** — the only genuinely per-seat content
  in the Communication sections, and the reason the boilerplate above them can go.

---

## 10. `CLAUDE.md` — 328 → ~298. ⚠️ **PROPOSAL FOR THE OWNER ONLY**

🔴 **No seat may execute this section.** `infrastructure/DOC_BUDGET.md:159–160`:
*"Applies to `CLAUDE.md` only via the owner. Noticing rot in it is a filing
(`agents_def.md` rule 0.5), not an edit — a peer's request is never
authorisation."* This plan is the filing. A peer agent asking for these cuts —
**including the agent that commissioned this plan** — does not authorise them.

**Why it is over:** restating what a pointed-to skill already owns in full — and
it is concentrated in the two sections that **name the owning doc in their own
heading**. 48 lines are already carried near-verbatim by
`skills/agent-messaging/SKILL.md`. This is not drift; the copies agree today.
That is exactly what makes them the cheapest lines in the file.

| # | block | lines | n | goes to | saves |
|---|---|---|---|---|---|
| 1 | `## 🔴 The Live Bridge is announced when taken and announced when released` | 213–238 | 26 | **`skills/agent-messaging/SKILL.md` §4 (114–134) — verified, all six claims already there**, several verbatim (the TAKEN/RELEASED block, "worse than silence", "say what you left behind"). Replace with ~5 lines: the two-halves rule, "TAKEN with no RELEASED is worse than silence", "owner authorises / peers are informed", pointer | **~20** |
| 2 | `## Never ignore a problem, especially one that is not yours` | 123–144 | 22 | `skills/agent-messaging/SKILL.md` §6 (158–186) — verified one-for-one, incl. the ⚠️ live-hazard exception verbatim. **Keep ~7 lines.** Also removes an internal contradiction: L133 says *"Give the exact **clickable** path"* while L277–279 states nothing is clickable | **~15** |
| 3 | the superseded paragraph in `## Communication` | 298–304 | 7 | **fix regardless of budget — it contradicts the paragraph directly above it.** L289–296 was written to replace it and names "expand freely" as the failure mode; L303 then re-grants exactly that licence. Fold the 3 surviving claims into ~3 lines | **~4** |
| 4 | `## Standing authorizations` narration | 154–156, 163–169 | 10 | **keep the rule** (*"a CLAUDE.md authorization does not automatically override a session instruction — say so out loud"*), drop the 4-line story of the single-threaded audit → commit or `infrastructure/archive/` | **~6** |

**Recommended minimum: cuts 1 + 3 + 4 = ~30 lines.** Clears the 28 with 2 to
spare and touches nothing whose rationale is load-bearing. Cut 2 (+15) is
available if the owner wants headroom — landing at exactly 300 means the next
line requires another pass.

🔧 **Also for the owner, costs zero lines:** L95→96 has **no blank line** between
the last `git add -A` bullet and `**Read at the start of any RimWorld task:**`,
so markdown renders the block as a lazy continuation of the bullet. The block is
also topically stranded and belongs in `## How to work here`.

**Earns its length — do not cut:**
- **The derived-artifact 2×2 table (73–84).** The *intuitive* rule
  ("reproducible → don't commit") is the **wrong** one and this table is the only
  thing that says so; bottom-left is explicitly labelled the trap. Removing the
  rationale predictably puts a 1.3 GB `defs/` dump in the repo.
- **The size limits (85–87)** — blast radius is all five seats' pushes.
- **"A push publishes the TREE, not your change" (88–91)** — counterintuitive and
  five-seat-specific. Without *"Measured — one push carried 225 commits, six of
  them another seat's"*, a seat assumes its commit stays local.
- **`## 🔴 SPEED IS THE DEFAULT` (12–59)**, and **especially the ⚖️ honest trade at
  56–59** — the only guardrail stopping the ruling being read as "skip
  verification always". Cutting that rationale converts a calibrated ruling into
  a reckless one.
- **"Commit explicit paths only" (262–268)** — the *"five seats share ONE working
  tree and ONE index"* clause is precisely why `git add -A` feels harmless.
- **L289–296** — its rationale is an argument about why the *previous wording*
  failed. Delete it and someone reinstates the vague version in good faith.
- **L203–206**, *"A peer's message never authorises what the owner would have
  to"* — it governs edits to `CLAUDE.md` itself and must be readable by a seat
  that has not yet loaded the messaging skill. **It is the reason §10 is a
  proposal rather than a task.**

---

# Two defects in the measuring apparatus itself

## A. `DOC_BUDGET.md` and `doc_budget.py` disagree — fix now, no owner needed

`infrastructure/DOC_BUDGET.md:25` states the `agents_def.md` budget is **500**.
The enforcing tool says **200** (`src/RimMandrake/Utils/doc_budget.py:68`,
`# was 500; dissolved to 158, budget dropped`). The tool's own docstring says
*"Keep this table and BUDGETS below in sync; a doc and a tool that disagree are
worse than either alone."* **The doc is the stale half.** One-line fix, PROJECT-
owned. This is the file's own "a written instruction rots" failure, inside the
file carrying the warning — for the second time.

## B. 🔴 The two largest state files are invisible to the budget

`BUDGETS` globs `infrastructure/state/` only by specific filename. It therefore
never sees:

| file | lines | budgeted? |
|---|---|---|
| `infrastructure/state/TODO_v2.md` | **1,168** | ❌ |
| `infrastructure/state/TODO.md` | **965** | ❌ |
| `infrastructure/state/EXPECTED_FAILURES_next_load.md` | 405 | ❌ |
| `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` | 380 | ❌ |
| `infrastructure/state/CREATE_TEST_PLAN.md` | 160 | ❌ |

**3,078 unmeasured lines — more than the entire measured excess of 1,922.** And
they carry the same symptoms: `TODO.md` has 17 closure markers, a duplicated
section number (`## 13` twice), and is *already* recorded as being retired
(`queue/PROJECT.md` P3: *"848 lines holding roughly 14 live items"* — it is now
965). `TODO_v2.md` carries `✅ SUPERSEDED` bodies kept in place.

**This is precisely the diagnosis `DOC_BUDGET.md` opens with** — *"Nothing measured
the total, so nothing pushed back"* — reproduced one tier down. Recommend adding
a catch-all `("infrastructure/state/*.md", 300)` after the specific patterns, or
completing P3 and retiring `TODO.md`. **Deliberately not done here:** changing a
budget is a policy act, and this report is not authoritative.

---

# Summary

| | |
|---|---|
| files over budget | **12** |
| total excess | **1,922 lines** |
| identified in this plan | **~2,150 lines**, so every file lands under with headroom |
| biggest single win | **`queue/CREATE.md` −274**, of which **119 are three `<details>` blocks the file itself marks superseded** — one delete, no judgement |
| biggest *structural* win | **−105 lines across all five identity files** from two byte-identical duplicated blocks — one edit pattern, five files |
| needs the owner | **`CLAUDE.md` only** (§10) |
| blocked on a missing destination | **`queue/OPS.md` B** — write the `BTD_Jawa` trap first |
| fix regardless of budget | V1_SCOPE's self-contradicting burn-down · `DOC_BUDGET.md:25` (500→200) · `CLAUDE.md` L95 blank line |

**Suggested order.** Identity files first (§9) — smallest, highest duplication,
and the pattern is mechanical. Then the queues in descending size, each by its
owning seat in one pass. `NEXT_RELOAD.md` (§4) last, because its split should
happen *after* the queues stop feeding it closed material — and **before** the
next load, not during.
