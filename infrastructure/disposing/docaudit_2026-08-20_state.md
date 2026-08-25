# Doc audit — the `infrastructure/state/` run-sheet cluster, 2026-08-20

**Question asked (owner):** *"I mostly wanted an audit over all these .md files we keep
updating. They're expensive to keep in that way. I wonder if some of them are redundant
and could be collapsed."*

**Metric used:** maintenance cost — how many documents must a seat open and edit to
record ONE fact, and how many say the same thing in parallel.

**ANALYSIS ONLY.** Nothing in `infrastructure/state/` was changed. This file is the
only write.

⛔ Out of scope by instruction: `infrastructure/state/queue/*` (append-only work logs;
high churn is inherent and correct there).

---

## 0. The corpus, measured

| file | lines | commits | created | last touched |
|---|---:|---:|---|---|
| `EXPECTED_FAILURES_next_load.md` | 939 | 21 | 2026-08-13 `79d422d` | 2026-08-20 |
| `WORLDGEN_FACTION_CHECKLIST.md` | 486 | 17 | 2026-08-13 `551aebf` | 2026-08-20 |
| `NEXT_RELOAD.md` | 433 | 55 | 2026-08-13 `7e98004` | 2026-08-20 |
| `observed/LIVE.md` | 406 | 14 | 2026-08-15 `e0997c0` | 2026-08-20 |
| `V1_CHAIN.md` | 390 | 19 | 2026-08-14 `e440a40` | 2026-08-20 |
| `TEST_PLAN.md` | 351 | 13 | 2026-08-13 `0a7850d` | 2026-08-19 |
| `WORLDGEN_RUN.md` | 224 | 13 | 2026-08-14 `76b264e` | 2026-08-19 |
| `OWNER_DECISIONS.md` | 146 | 19 | 2026-08-13 `7e98004` | 2026-08-20 |
| `V1.md` | 98 | 14 | 2026-08-14 `7c74cd7` | 2026-08-19 |
| `BUILDABLE.md` | 92 | 3 | 2026-08-15 `3c0b05e` | 2026-08-15 |
| `observed/SESSION_2026-08-19_BRIDGE_EXPANSION.md` | 56 | — | 2026-08-19 | 2026-08-19 |
| `modlists/README.md` | 53 | 2 | 2026-08-19 `8502ae5` | 2026-08-20 |
| `infrastructure/STRUCTURE.md` | 280 | 9 | 2026-08-13 `7e98004` | 2026-08-19 |
| `infrastructure/DOC_BUDGET.md` | 199 | 15 | 2026-08-13 `7e98004` | 2026-08-19 |

Also present and unlisted anywhere: `MODE` (one word, `interactive`, 1 commit, untouched
since 2026-08-14), `closed_ledger.json`, `status_matrix.json`, `status/*.json`.

**The whole cluster is seven days old.** Every file here was created 2026-08-13 → 08-19.
The cost the owner is feeling is not accumulated history; it is that a week produced
fourteen parallel documents for one project.

---

## 1. The three pre-load gates: **one job in the middle, split in two — with a third
file that gates an event nobody is scheduled to run**

The honest answer is not "one job" and not "three jobs". It is **1.5 jobs across three
files.**

| file | the event it gates | is that event booked? |
|---|---|---|
| `NEXT_RELOAD.md` | the next cold load — deploy window, then the in-game batches | yes, continuously; 55 commits, the highest churn in the cluster |
| `EXPECTED_FAILURES_next_load.md` §3 | **the same load**, from the log side | yes — same event |
| `EXPECTED_FAILURES_next_load.md` §2 | the irreversible new-world generation | **no.** The file itself says so |
| `WORLDGEN_FACTION_CHECKLIST.md` | the Configure Factions page of that same worldgen run | **no** — same unbooked event |
| `WORLDGEN_RUN.md` | everything around that page in that same run | **no** — same unbooked event |

🔑 **The split that is real:** *worldgen* (one irreversible owner-driven event, not
scheduled) versus *the next quicktest load* (recurring, cheap, happens constantly).
`EXPECTED_FAILURES_next_load.md:42-46` states this itself and warns against confusing
the two.

🔑 **The split that is NOT real, and is where the cost is:** `NEXT_RELOAD.md` and
`EXPECTED_FAILURES §3` are **the same job, cut down the middle by phase** — one holds
"what to do", the other holds "what the log should say when you do it". A seat cannot
execute either without the other. They cross-reference each other explicitly:
`EXPECTED_FAILURES:609` → "the event is `NEXT_RELOAD.md` §1.0"; `EXPECTED_FAILURES:788`
→ "Then `NEXT_RELOAD.md` §5 in its own order"; `NEXT_RELOAD:69` → "write the three
signatures into `EXPECTED_FAILURES`". **Every load therefore edits both files, and the
same check is written twice.**

Evidence that the two-file split is already leaking (each item appears in both):

| check | `NEXT_RELOAD.md` | `EXPECTED_FAILURES_next_load.md` |
|---|---|---|
| `--gm` strips `jawa/fire_incident` + `jawa/send_letter`, count −2 | `:65`, `:142`, `:206` | `:617`, `:639` |
| derived `jawa/*` tool count; `--include='*.cs'` is load-bearing | `:196-201` | `:630-633`, `:276` |
| "Gates compare measurements to measurements, never to prose" *(verbatim)* | `:210` | `:292` |
| `[JawaPlantGrowth] scaling <N> plant defs` is the only positive evidence | `:178-180`, `:289` | `:662`, `:665` |
| C36 — `BTD_*` / `guy762_` / `OuterRim_` crossrefs must be 0 | `:170-176` | `:537`, `:693`, `:602`, `:813` |
| B62 unbuilt ⇒ only `eopie sled` passes | `:67`, `:282` | `:681-683` |
| `Failed to find any textures at` fires only when every direction is missing | `:365` | `:676` |
| `knownExpansions` overcounts a `<li>` count | `:421` | `:876-879` |

And `EXPECTED_FAILURES` duplicates itself internally, because each per-load block
restates the previous block's checks rather than referencing them:

- `PatchOperationRemove failed` on `requiredMemes`/`classicIdeo` is harmless — `:536`
  (S8) **and** `:691` (T4), near-verbatim, grep repeated at `:547` and `:702`, results
  rows at `:601` and `:812`. §3's T4 **reverses** §2's S8 on the `BTD_*` row.
- `No Verse.PawnKindDef named JDSCIS_*` harmless — `:538` **and** `:692`.
- Crossref naming `Jawa_Tribal_Scavenger` / `Jawa_Colonist` is the one worth stopping
  for, citing `c06e89e` — `:541-544` **and** `:695-699`.
- "An unrun check is not a pass" *(verbatim)* — `:572` **and** `:792`.
- The `[RimBridge]` failure grep, identical regex — `:81`, `:300`, `:645`.
- "only `Jawa_IndigenousTribes` carries `requiredCountAtGameStart`" — `:513-515` **and**
  `:761-763`, citing the same queue id `seven-factions-have-no-required-count-9c4e17`
  twice, and **contradicted** by `WORLDGEN_FACTION_CHECKLIST:452` ("All seven authored
  defs carry `requiredCountAtGameStart 1`").

**Verdict.** Three files, two jobs, and one of those two jobs is not booked. The load
job (`NEXT_RELOAD` + `EXPECTED_FAILURES §3`) is **one job split by phase and should be
one file**. The worldgen job (`EXPECTED_FAILURES §2` + `WORLDGEN_FACTION_CHECKLIST` +
`WORLDGEN_RUN`) is **one job split across three files for an event with no date**.

---

## 2. Lifecycle — per-event files whose event has passed

**Standing (correctly permanent):** `V1.md`, `V1_CHAIN.md`, `OWNER_DECISIONS.md`,
`observed/LIVE.md`, `STRUCTURE.md`, `DOC_BUDGET.md`, `modlists/README.md` (procedure
half), `TEST_PLAN.md`.

**Per-event, and the event has passed:**

| file / block | its event | status now |
|---|---|---|
| `EXPECTED_FAILURES_next_load.md` **§3** | "the **2026-08-15 deploy-window load**", signatures written 2026-08-15 ~15:50 | 🔴 **Results table still blank** (`:797-821`, 16 rows). Loads have run since — `LIVE.md` records live-bridge harvests dated 2026-08-19 and 2026-08-20 with commit hashes (`669be9e`, `a5b0f2d`), and `modlists/` holds PRESWAP captures stamped `20260819` and `20260820`. **Five days and multiple loads have passed against an unfilled block** — the exact failure the file's own header (`:11-18`) and `:799-801` say to declare out loud. Nobody has. |
| `EXPECTED_FAILURES_next_load.md` **§2** | the new world generation | ⬜ Blank since 2026-08-13. The event is **not scheduled and not schedulable by a seat** — it is the owner's one hand-made world. This is not a stale block; it is a block whose event may never be booked, sitting in a file that seats open every load. |
| `EXPECTED_FAILURES_next_load.md` **second "§7"** (`:825-926`) | "BUILD's items, 2026-08-20" | 🔴 **A fourth load's content appended without a §4 block, reusing the section number `S7` already used at `:493`.** The per-load block discipline the file's own rule 2 mandates has broken down inside the file. |
| `NEXT_RELOAD.md` **§1.0**, "the deploy manifest, in order. **Opened 2026-08-15**" | that deploy window | 4 of 6 steps still unticked, five days on, while the file's other sections have been rewritten 55 times. |
| `WORLDGEN_RUN.md` | "the one-shot run that closes v1 rows 2 and 7" | Event never booked. `WORLDGEN_FACTION_CHECKLIST:32` and `WORLDGEN_RUN:181` both carry the ratified "21 untick / 6 keep" tally; ~39 `☐` boxes remain unticked. |
| `BUILDABLE.md` | none stated | 3 commits, untouched since **2026-08-15**. 92 lines of which **25 are the banner** (§3). Not referenced from `STRUCTURE.md`. |
| `MODE` | — | 1 commit, 2026-08-14, one word. Referenced nowhere in `STRUCTURE.md`. |
| `observed/SESSION_2026-08-19_BRIDGE_EXPANSION.md` | one session | Its content is already restated in `LIVE.md`; see §3 item 3. |

⚠️ **The most expensive lifecycle defect is not a stale file — it is a blank results
table that nobody is required to notice.** `EXPECTED_FAILURES` gates on a human
remembering to fill a table, in a file whose length (939 lines) guarantees the table is
not on screen when the load ends.

---

## 3. Fact duplication — the same assertion in two or more files

Ordered by cost. 🔴 = the two statements **disagree**, which is worse than duplication.

### 3.1 🔴 The active mod count — the most repeated and most contradicted fact in the repo

**Measured now, from the file the docs point at**
(`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`, parsed):
**`activeMods` = 577, `knownExpansions` = 5.** md5 `5cb6857188b284243c1c628f17cd0120`.

| what a doc says | where |
|---|---|
| "the owner's real **583**-mod list. **Restore it before he plays**" | `modlists/README.md:6` |
| "Captured 2026-08-19 20:15, **583** active, md5 `5a9a4d3a958ad96dad442bedfc926f5c`" | `modlists/README.md:9` |
| "CURRENT MOD SET — **576** active … `FULL.LATEST.xml` holds it and is byte-for-byte identical to live" | `modlists/README.md:24-30` |
| "**578** → **576**. Any doc still saying 578 is stale" | `modlists/README.md:38` |
| "`ModsConfig.xml` is **578** active mods, NOT 583" | `observed/LIVE.md:175` |
| dump holds **576**, `ModsConfig` holds **575** | `observed/LIVE.md:15`, `:72` |
| "**576** mods, 529 files under `defs/`" | `observed/LIVE.md:10` |
| "Claimed 583 active mods. It is **578**" | `observed/SESSION_2026-08-19…:52`, `:21`, `:28` |
| "`<activeMods>` **575**, down from 576"; "573/**578**"; "576/**577**" | `EXPECTED_FAILURES:620`, `:881`, `:910` |
| "Live reads **578** today against the **575** freeze copy" | `V1_CHAIN.md:80`, `:120` |
| "the live **573**-mod def set" / "the **573**-mod dump" | `WORLDGEN_FACTION_CHECKLIST:169`, `:412` |
| "`ModsConfig.xml` (**584 → 583**)" — a third lineage for the same removal | `WORLDGEN_RUN.md:57` |
| "the **578**-mod game" | `OWNER_DECISIONS.md:131` |
| "~**561** active mods" cited as an example of a stale snapshot | `DOC_BUDGET.md:185` |

**Nine distinct numbers across eight files.** `modlists/README.md` **contradicts itself
inside 53 lines** (583 at `:6`, 576 at `:24`) — and it is the file a seat opens before
restoring the owner's real list. Its stated md5 `5a9a4d3a…` **no longer matches the file
it names**, and even its newer figure (576) is off by one against the measured 577.

✅ The correct rule is already written, once, in the right voice, in the wrong file:
`TEST_PLAN.md:64` — *"Read `ModsConfig.xml` for the active list; never a count written
in a doc."* Same rule in `CLAUDE.md`. **Every one of the fourteen numbers above exists
in violation of a rule the repo already has.**

### 3.2 🔴 `Player.log` rotation — two seats state the opposite behaviour

- `EXPECTED_FAILURES:26` — *"`Player.log` is **rotated by the launcher, not appended**."*
- `observed/LIVE.md:309` — *"🔴 `Player.log` **PERSISTS between runs**."*
- `observed/SESSION_2026-08-19…:41` — persists, *"so grepping … matched the PREVIOUS
  session"* — i.e. the failure mode was actually hit.

This is not cosmetic. `EXPECTED_FAILURES:827` prescribes grepping the log at the main
menu. **If LIVE.md is right, that procedure returns last session's evidence**, and every
signature collected that way is unsound.

### 3.3 🔴 The 25-line owner worldgen ruling — byte-identical in seven state files

`md5(lines 3–27)` = `7dd856d0a39dfbf9dbed5eb96b0b9093` in **all** of:
`NEXT_RELOAD.md` · `V1.md` · `V1_CHAIN.md` · `WORLDGEN_RUN.md` · `BUILDABLE.md` ·
`WORLDGEN_FACTION_CHECKLIST.md` · `OWNER_DECISIONS.md`.
Plus longer variants in `design/V2_DREAMS.md` (32 blockquote lines) and
`WORLDGEN_FACTION_CHECKLIST.md` (118 blockquote lines total), and a condensed copy in
`CLAUDE.md` and `queue/CHECK.md`.

**Cost: 175 identical lines inside `infrastructure/state/` alone, and a seven-file edit
if the owner ever refines the ruling.** Drift has already started — the lines
immediately after the shared block diverge between `V1.md` and `WORLDGEN_RUN.md`.

⚠️ The ruling itself is owner content and must never be lost. But **it is already
canonical in `CLAUDE.md`**, which is auto-loaded into every session of every seat. The
seven copies are not the record; they are seven mirrors of a record that is guaranteed
already in context.

### 3.4 🔴 Faction / xenotype expectations — four incompatible rosters

| claim | where |
|---|---|
| "21 untick / 6 keep, ratified"; "All **27** factions … NOT FOUND count: 0" | `WORLDGEN_FACTION_CHECKLIST:32`, `:109`, `:168`; echoed `WORLDGEN_RUN:181` |
| step 9 Factions "specced — **7** new, 6 patches, 1 fix" | `V1.md:49` |
| "all **8** Jawa faction defNames"; "the **15** `Jawa_*` faction counts" | `EXPECTED_FAILURES:818`, `:748`, `:931` |
| "apply to **8** factions, not 12" | `V1_CHAIN.md:333` |
| "the eleven new factions exist and are settable" | `EXPECTED_FAILURES:493` (S7) |
| a quicktest shows all **54** factions vs "**24 of the 48** factions" | `WORLDGEN_RUN:214`, `EXPECTED_FAILURES:367` vs `EXPECTED_FAILURES:907` |

7 / 8 / 11 / 15 authored factions; 27 / 48 / 54 on the page. **No two of the five
worldgen-facing documents agree on how many factions exist**, and the checklist is the
document the owner will read at the irreversible screen.

### 3.5 The `OuterRim_GalacticEmpire` ruling — propagated to three files, incompletely

`NEXT_RELOAD:306`, `:311` · `EXPECTED_FAILURES:144-148`, `:399`, `:471`, `:594` ·
`WORLDGEN_FACTION_CHECKLIST:278`, `:294-318`, `:417-419`.
🔴 `EXPECTED_FAILURES:399` marks the row **DEAD 2026-08-20**, while `NEXT_RELOAD:280`
still books an L3 Empire-raid screenshot and `V1.md:75` keeps row 1 REOPENED. **One
ruling, nine sites, three files, and the propagation is not complete.** The related
vanilla-`Empire` label/`fixedName`/`leaderTitle` fact is stated in both
`WORLDGEN_FACTION_CHECKLIST:66,78,104,281` and `EXPECTED_FAILURES:398,595`.

### 3.6 🔴 Bridge companion DLL identity — self-contradicting inside one file

`EXPECTED_FAILURES:64` says 154,112 B, md5 `b9aef17f…`; `:227` says 227,840 B; `:617`
gives md5 `f0d4e6e7…`. Port 5174 and the `BridgeTools\` sibling-of-`Mods\` location are
stated in both `observed/LIVE.md:170-172` and `EXPECTED_FAILURES:64,169,227,617`.
🔴 `jawa/*` tool count likewise disagrees: 106 (`SESSION_…:6`), "25 new" / "22 more"
(`LIVE.md:194`, `:257`), "21 tools, was 17" (`EXPECTED_FAILURES:227`).
The one reliable route — count `jawa/*` from `rimbridge/list_tools` — is written twice
(`NEXT_RELOAD:186`, `EXPECTED_FAILURES:634`).

### 3.7 Facts that duplicate but agree (cheap to lose, still a multi-file edit)

| fact | locations |
|---|---|
| cold load ~23–30 / ~25–30 / ~25 min | `NEXT_RELOAD:30`, `:70` · `WORLDGEN_FACTION_CHECKLIST:485-486` · `WORLDGEN_RUN:37`, `:178` · `LIVE.md:237` · `SESSION_…:21` · `DOC_BUDGET:176` |
| 13-mod minimal list = 22 s cold load, ~1 min cycle | `LIVE.md:237` · `SESSION_…:21` |
| `modlist_swap.py --status / --minimal / --restore` | `modlists/README.md:13-15` · `LIVE.md:241` · `SESSION_…:33` |
| live `ModsConfig.xml` path | `modlists/README.md:4` · `BUILDABLE.md:80` · (`CLAUDE.md`) |
| `FULL.LATEST.xml` is the restore target | `LIVE.md:179` · `EXPECTED_FAILURES:857` |
| `Player.log` path | `EXPECTED_FAILURES:23`, `:832` |
| deploy = plan first, then `--apply --mod <Name>`; no `--plan` flag | `STRUCTURE.md:243-248` · `NEXT_RELOAD:66-67`, `:141` · `BUILDABLE.md:81` |
| Steam `Mods\<ModName>` path | `STRUCTURE.md:245` · `NEXT_RELOAD:67` · `EXPECTED_FAILURES:739` · `WORLDGEN_FACTION_CHECKLIST:305`, `:327` |
| `build.py --apply` without `--gm` drops two tools | `LIVE.md:245-246` · `WORLDGEN_RUN:172` · `EXPECTED_FAILURES:617`, `:639` (🔴 LIVE says the tool *refuses and names them*; the other three call it silent) |
| load order: `mandrake.jawaplantgrowth` after `brrainz.harmony` | `NEXT_RELOAD:66` (as an instruction) · `EXPECTED_FAILURES:618` (as already satisfied) |
| a quicktest never visits Configure Factions (trap `2d1685e`) | `WORLDGEN_RUN:214` · `EXPECTED_FAILURES:171`, `:367-369` |
| the three xenotype donors are OFF | `NEXT_RELOAD:171-172` · `EXPECTED_FAILURES:620`, `:693` · `V1_CHAIN.md` donor table |
| 21,872 tiles | `WORLDGEN_RUN:115` · `V1.md:50` · `V1_CHAIN:90` · `SESSION_…:27` · `LIVE.md:203`, `:243` |
| worldgen is manual, one-shot, nothing regenerates | `V1.md:3-27,83-94` · `V1_CHAIN:90` · `WORLDGEN_FACTION_CHECKLIST:124` · `WORLDGEN_RUN:57` · `STRUCTURE:109` · `OWNER_DECISIONS:57` |
| 🔴 `refresh.py` needs Windows `python.exe`, while its sibling `modlist_swap.py` is invoked with WSL `python3` — both touch the same `ModsConfig.xml` | `NEXT_RELOAD:134` vs `modlists/README.md:13`, `LIVE.md:241` |

---

## 4. `doc_budget.py` — what it measures, and why the answer is not useful

### What it reports today

```
8 file(s) over budget.
repo total: 472 markdown files, 98,385 lines (~1082k tokens if read whole)
```

| file | lines | budget | over | class |
|---|---:|---:|---:|---|
| `queue/CHECK.md` | 1781 | 150 | +1631 | ⛔ protected (queue) |
| `queue/DECIDE_ARCHIVE.md` | 1456 | 150 | +1306 | ⛔ protected (queue) |
| `queue/CHECK_CLOSED.md` | 1029 | 150 | +879 | ⛔ protected (queue) |
| `queue/DECIDE.md` | 757 | 150 | +607 | ⛔ protected (queue) |
| `queue/HUMAN.md` | 465 | 150 | +315 | ⛔ protected (queue) |
| `agents/POLICY.md` | 281 | 150 | +131 | identity |
| `NEXT_RELOAD.md` | 433 | 400 | **+33** | run sheet |
| `OWNER_DECISIONS.md` | 146 | 120 | **+26** | ⛔ do-not-touch content |

### The defect, stated plainly

🔴 **Five of the eight overruns are queues — the one class the owner has explicitly
excluded from collapse. A sixth is `OWNER_DECISIONS.md`, the class that must never be
cut. So six of eight flags are unactionable, and the tool is in practice measuring
queue-draining hygiene rather than documentation bloat.**

🔴 **And the two largest, fastest-churning run sheets in the repo are not measured at
all.** `BUDGETS` in `src/RimMandrake/Utils/doc_budget.py:73-98` is a hand-maintained
allowlist. `infrastructure/state/*.md` has no class glob — only two per-file entries
(`NEXT_RELOAD.md`, `V1_CHAIN.md`) and `OWNER_DECISIONS.md`. Consequently these are
**invisible to the budget**:

| unbudgeted | lines |
|---|---:|
| `EXPECTED_FAILURES_next_load.md` | **939** |
| `WORLDGEN_FACTION_CHECKLIST.md` | **486** |
| `observed/LIVE.md` | 406 |
| `TEST_PLAN.md` | 351 |
| `WORLDGEN_RUN.md` | 224 |
| `V1.md` | 98 |
| `BUILDABLE.md` | 92 |
| **total unmeasured** | **2,596** |

The single largest file in the run-sheet cluster is 2.3× the budget of the largest file
the tool *does* watch, and it has never appeared in a report. A budget with an
allowlist rewards not being added to the allowlist.

⚠️ Two further weaknesses:

- **The `prov/100` column is computed but never gated.** `queue/HUMAN.md` at 9.7
  provenance lines per 100 and `V1_CHAIN.md` at 8.2 are the highest-provenance files in
  the repo; nothing acts on that. The tool's own docstring says provenance "is the thing
  that accumulates" — then does not budget it.
- **The `PROVENANCE` regex matches `2026-\d\d-\d\d`**, so every dated *measurement* —
  the thing the repo most wants to keep — scores as provenance to be deleted. The metric
  points the wrong way for `observed/LIVE.md`, whose entire value is dated measured
  facts with commit hashes.

**Is it useful?** As written, marginally: it produces one true actionable signal
(`NEXT_RELOAD.md` +33) out of eight. **The fix is small and worth doing:** add
`("infrastructure/state/*.md", 250)` as a class glob **below** the per-file entries, and
exclude the queue globs from the exit-1 count (report them separately as "drain me"),
so the tool stops conflating two different problems. That single change surfaces
`EXPECTED_FAILURES_next_load.md` at +689 and `WORLDGEN_FACTION_CHECKLIST.md` at +236 —
which is the bloat the owner is actually asking about.

Note also that `STRUCTURE.md`'s live-state table (`:195-205`) lists **nine** entries and
omits `WORLDGEN_RUN.md`, `V1.md`, `BUILDABLE.md`, `observed/`, `modlists/`, `MODE`,
`closed_ledger.json` and `status_matrix.json` — despite `STRUCTURE.md:276-278` requiring
that "a new `infrastructure/state/` entry belongs here in the same commit". The manifest
is 8 entries short of the directory.

---

## 5. Proposed target shape

Constraints honoured: `OWNER_DECISIONS.md` untouched; the `V1.md` / `V1_CHAIN.md` scope
tables untouched; **no measured evidence carrying a commit hash is deleted — it is
moved into `observed/LIVE.md`, which already exists for exactly that.**

### Target: 14 files → 8

| # | target file | absorbs | what it costs | what it saves |
|---|---|---|---|---|
| **1** | `infrastructure/state/LOAD.md` *(new; supersedes `NEXT_RELOAD.md`)* | `NEXT_RELOAD.md` + `EXPECTED_FAILURES §3` and the appended 2026-08-20 block | one careful merge, ~2 h. §3's signature/result pairs move next to the step that produces them. Risk: the "signatures written BEFORE the log exists" discipline must survive — keep it as a rule at the top and a `written:` / `filled:` stamp per row | **the single biggest saving.** One file per load instead of two, both currently edited on every load (55 + 21 = 76 commits). Kills the 8 cross-file duplications in §1 and the "which file do I open first" cross-reference loop |
| **2** | `infrastructure/state/WORLDGEN.md` *(new)* | `WORLDGEN_RUN.md` + `WORLDGEN_FACTION_CHECKLIST.md` + `EXPECTED_FAILURES §2` | ~2 h, and the faction tally must be reconciled first (§3.4) — that reconciliation is required work regardless | One document for one irreversible unbooked event, instead of three that each restate the roster differently. The owner reads ONE thing at the Configure Factions screen |
| **3** | `infrastructure/state/EXPECTED_FAILURES_next_load.md` | — | **retired.** §1 (closed, filled) moves to `observed/LIVE.md` as a dated harvest; §2 → target 2; §3 + the 08-20 block → target 1 | 939 lines, the largest and most self-duplicating file in the cluster, ceases to exist. Its 6 internal self-duplications go with it |
| **4** | `observed/LIVE.md` | + `observed/SESSION_2026-08-19_BRIDGE_EXPANSION.md`, + `EXPECTED_FAILURES §1` | 30 min. Session file's content is already largely restated here | One home for measured facts. Removes the 583-vs-578 restatement at `SESSION_…:52` |
| **5** | `infrastructure/state/V1.md` + `V1_CHAIN.md` | unchanged, **but** — 🔴 keep both or merge is a **DECIDE call, not this audit's**. `V1.md` is 98 lines of which 25 are the banner; net content is ~73 lines and is a summary of `V1_CHAIN.md`'s tables | if merged: 1 h | ⛔ Scope tables are protected. Flagged, not proposed |
| **6** | `infrastructure/state/TEST_PLAN.md` | unchanged | — | Standing procedure, owned by CHECK, correctly separate from any one event |
| **7** | `infrastructure/state/OWNER_DECISIONS.md` | unchanged | — | ⛔ Protected |
| **8** | `infrastructure/state/modlists/README.md` | unchanged, **but fix §3.1 first** | 10 min | Deleting the stale `583` / md5 lines at `:6`, `:9` removes a self-contradiction from the file a seat reads before restoring the owner's real list |
| — | `infrastructure/state/BUILDABLE.md` | **retire** — 3 commits, untouched since 08-15, absent from `STRUCTURE.md`, 27% banner | 5 min: confirm nothing cites it, then `git rm` | 92 lines, one fewer file to keep the banner in sync across |
| — | `infrastructure/state/MODE` | **retire or document** | 5 min | One word, one commit, unreferenced in the manifest |

### Three changes worth more than any merge

1. 🔴 **Delete the 25-line banner from all seven state files and cite `CLAUDE.md`
   instead.** The ruling is auto-loaded into every session already. **Saves 175 lines and
   turns a seven-file edit into a one-file edit** the next time the owner refines it.
   One line replaces it: *"Worldgen ruling: `CLAUDE.md` § *There is no worldgen feature*."*
   ⚠️ Do the `CLAUDE.md` copy first and verify it is complete; the ruling is owner
   content and must not thin in transit.
2. 🔴 **Delete every mod count from every document.** `TEST_PLAN.md:64` and `CLAUDE.md`
   already forbid them; nine numbers exist across eight files in violation. Replace each
   with the command that reads it. Two commits on 2026-08-20 (`ab40d81`, `ea55a01`)
   already started this — finish it.
3. 🔴 **Settle `Player.log`: rotated or persistent (§3.2).** One grep of the live file
   settles it. Until then every log-derived signature in the cluster is unsound, and no
   amount of merging fixes that.

### Net

| | before | after |
|---|---:|---:|
| files in the cluster | 14 | 8 |
| lines in `infrastructure/state/*.md` | ~2,660 | ~2,050 est. |
| files edited to record one load's result | **2** | **1** |
| files edited to change the owner's worldgen ruling | **7** (+`CLAUDE.md`, +`V2_DREAMS.md`) | **1** |
| files stating the active mod count | **8** | **0** |

---

*Audit performed 2026-08-20 against `main` at `669be9e`. Read-only; no file under
`infrastructure/state/` was modified.*
