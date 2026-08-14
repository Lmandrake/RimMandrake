# TODO_RETIREMENT_PLAN.md — the mechanical plan for retiring `infrastructure/state/TODO.md`

> # ✅ EXECUTED 2026-08-13. `TODO.md` is a 13-line pointer stub.
>
> **This is a record, not a plan.** All five steps ran; the four LIVE items are
> filed at their seats, the doctrine moved or was deleted as duplicate, and 12
> inbound citations were repaired. Commits in `CLOSED.md` under owner decision #5.
> Everything below describes the tree as it was BEFORE the retirement.

_Written 2026-08-13. **This is a STAGING document. Nothing has been moved, and no
queue file, `TODO.md`, `CLOSED.md` or doctrine file has been edited.** Seats are
writing to their queues right now; executing against a live queue is the collision
this plan exists to avoid._

Source read end to end: `D:\Luke\dev\Rimworld\infrastructure\state\TODO.md`, 968
lines, 17 sections.

---

## 🔴 THE HEADLINE NUMBERS

| | |
|---|---|
| **True LIVE count** | **4** — not ~14 |
| Lines in sections with **zero** live content | **801 of 968** (83%) |
| Lines that are not live, counting the closed record inside the four live sections | **~875 of 968** (90%) |
| Sections that are wholly CLOSED, DEAD or DOCTRINE | **13 of 17** |

**Why the ~14 estimate was high, and it is not an estimating error.** Ten of the
items counted as live have since been migrated into per-seat queues or fixed in
code, and `TODO.md` was never updated to say so. This plan re-verified every one
against the source file or the running repo rather than against the item's own
prose.

### The four LIVE items, in full

| # | item | seat | v1/v2 | why it is homeless |
|---|---|---|---|---|
| L1 | §9 — `validate_patch.py:1363` warns *"xpath matches N nodes IN ONE MOD"*, which reads as a scoping claim; in `--all-versions` there is no load set, so "one mod" describes a folder, not the game | **CREATE** | **v2** | Owner ruled `validate_patch.py` is CREATE's (`CLOSED.md`). Verified absent from all five queues; only the *Patches-vs-Defs* question migrated (`C-v2`), not the wording |
| L2 | §20 — `src/RimMandrake/Utils/ilscan.py:152` decodes only `ldc.r4` (`op == 0x22`), so compiled defaults cannot be attributed to a field name | **`[?]` → recommend BRIDGE** | **v2** | Verified still true in the file today. `queue/CREATE.md:255` **cites** §20 but does not restate it — retiring `TODO.md` deletes the finding outright |
| L3 | §21 — two Doors Expanded SW mask files carry an underscore RimWorld never looks for (`SWDoorBlastBDoor_Frame_east_m.png`, `SWDoorBlastDDoor_Frame_east_m.png`) | **CREATE** | **v2** | Verified on disk: both wrong names are still there next to the correctly-spelled `SWDoorBlastDoor_Frame_eastm.png`. Absent from every queue; `C5` is adjacent but covers a different slot |
| L4 | §22 residual — `design\Jawa\mods\forbidden_mods.md:171` still asserts RimWorld rewrites `ModsConfig.xml` on exit | **OPS** | **v2** | The three skills files were corrected (`P8`, `a43b610`); this one was not. `forbidden_mods.md` is a mod-set document, and the mod list is OPS's exclusively |

⚠️ **L2 is the only one whose ownership I could not settle from
`infrastructure/agents/*.md`.** `ilscan.py` reads IL out of a compiled assembly —
BRIDGE's stated expertise — but it lives in `src/RimMandrake/Utils/` and is not in
BRIDGE's owned list, and the seat that hit the defect was CREATE, reading mod
settings defaults. **Recommend BRIDGE on expertise; the owner or PROJECT should
confirm rather than let it sit `[?]`.**

---

## 🔴 EXECUTION BLOCKER — 11 inbound references point INTO this file

**Retiring `TODO.md` breaks live cross-references in nine other documents.** Five
of them already dangle today. This must be repaired in the same commit series or
the retirement trades one stale file for nine broken pointers.

| citing file:line | cites | status today |
|---|---|---|
| `design\Jawa\droid_ruling.md:4`, `:433` | `TODO.md` §1 | ❌ **already dangling** — §1 does not exist here; the body is `infrastructure\state\TODO_v2.md:210` |
| `src\RimMandrake\WreckedMachines\V2.md:119` | `TODO.md` §1 | ❌ **already dangling** — same |
| `infrastructure\state\V1_SCOPE.md:504` | `TODO.md` §1 | ❌ **already dangling** — same |
| `design\Jawa\mods\required_mods.md:593`, `:603` | `TODO.md` §4, §3 | ❌ **already dangling** — neither section exists |
| `design\Jawa\worldbuilding\faction_roster_v2.md:357` | `TODO.md` §3.2 | ❌ **already dangling** |
| `design\Jawa\art\graphics_overhaul_protocol.md:240` | `TODO.md` §10 | ❌ **already dangling** — §10 survives only as a row in the closed table |
| `design\Jawa\worldbuilding\faction_engine_gap_audit.md:3`, `:159`, `:181` | §0 Stage 2, §0, §12 | ✅ resolves — **breaks on retirement** |
| `design\Jawa\worldbuilding\faction_stage2_gap_audit.md:3`, `:69` | §0 Stage 2, §0 | ✅ resolves — **breaks on retirement** |
| `design\Jawa\worldbuilding\faction_stage3_buildable_spec.md:3`, `:462` | §0 Stage 3, §3d | ✅ resolves — **breaks on retirement** |
| `design\Jawa\mods\cherry_picker_killlist.md:58` | §0 Stage 1 | ✅ resolves — **breaks on retirement** |
| `infrastructure\state\EXPECTED_FAILURES_next_load.md:8` | §7 | ✅ resolves — **breaks on retirement**, and this is a live pre-load file |
| `infrastructure\state\V1_SCOPE.md:524` | §12 | ✅ resolves — **breaks on retirement** |
| `infrastructure\state\queue\CREATE.md:255` | §20 | ✅ resolves — **breaks on retirement, and takes L2 with it** |
| `infrastructure\disposing\STALE_FILE_AUDIT.md:82` | `TODO.md:39`, `TODO.md:124` | ⚠️ **cited by LINE NUMBER** — breaks the moment any line above 124 moves |

**Mechanical fix, one commit:** repoint §0/§3d/§12/§20 citations at their queue
successors (`V9`, `O4`, `traps-tooling.md`, and L2's new home), repoint every §1
citation at `TODO_v2.md` §1, and replace the two line-number citations in
`STALE_FILE_AUDIT.md` with the successor ids.

---

## The classification table

Every section, in file order. Line spans are inclusive.

| § | lines | first line of the section | class | destination | note |
|---|---|---|---|---|---|
| — | 1–24 | `# TODO.md — the authoring backlog` | **DEAD** | pointer stub | The three-file distinction table (`TODO.md` / `parked_mod_concepts.md` / `NEXT_RELOAD.md`) is now wrong: the queue role moved to `queue/<SEAT>.md`. Replace the whole file with a ~10-line stub pointing at the five queues + `CLOSED.md` |
| 0 | 25–52 | `## 0. [v1] ⭐ THE FACTIONS — one reskin ships; the roster is v2` | **CLOSED** + **DEAD** | `CLOSED.md` (already has the row) | `CLOSED.md:12` already carries *"v1 row 1 — Empire reskin \| SEEN LIVE \| `fad8bab`"*. Stages 1 and 2 are done and their evidence lives in `faction_engine_gap_audit.md`. **Stages 3–4 already migrated → `queue/VISION.md` V9, open, `[v2]`.** Nothing here is homeless |
| 2 | 53–70 | `## 2. [PROJECT] ⚠️ PARTLY OPEN — `agents_def.md` contradicts itself` | **DEAD** | — | Triple-recorded: `CLOSED.md:15` closes it (`468ecb3`) **and** `queue/PROJECT.md` P1 carries the live remainder (full rewrite for the five-seat structure). TODO's copy is the third. Delete |
| 3d | 71–132 | `## 3d. [WORLD] `faction_roster_v2.md:42` claims `FactionDef` expresses "goodwill"` | **DEAD** | — | Split and fully migrated. The line **is fixed** — verified: `faction_roster_v2.md` now reads *"`FactionDef` does NOT express goodwill"* (`queue/VISION.md` V10, closed). The open half — does Faction Customizer persist across worlds — is `queue/OPS.md` **O4, open** |
| 7 | 133–279 | `## 7. ⏳ Items that belong in `NEXT_RELOAD.md` but could not be filed there` | **CLOSED** + **DOCTRINE** | `CLOSED.md` (row exists) + D7 below | `CLOSED.md:13` already closes it. All four items migrated (`8a6659e`); the `[BRIDGE]` gap closed; the three-assembly waiver was re-put and **stands**. Live remainder is `queue/OPS.md` **O5** (write the three expected-failure signatures), which the owner ruled still standing. One real doctrine line survives → D7 |
| 9 | 280–341 | `## 9. ⚠️ [PROJECT] CORRECTED — this is a mode confusion, not a validator bug` | 🟢 **LIVE (L1)** | `queue/CREATE.md` | Only lines ~323–332 are live: reword the `IN ONE MOD` warning. **Verified still present at `skills\rimworld-modding\scripts\validate_patch.py:1363`.** The other ~52 lines are the reproduction record → `CLOSED.md` one-liner. ⛔ Carry the *"do not fix the walk"* prohibition into the queue entry or the next reader breaks `--all-versions` |
| 11 | 342–426 | `## 11. [ANY] The git hook guards `add`, not `commit`` | **DEAD** | — | **The defect is fixed.** Verified in `.claude\hooks\block_blanket_git_stage.py`: it blocks `git commit` **without a pathspec** and documents the index race by name. `queue/PROJECT.md` **P2** already holds the residual (*confirm and close loudly*). The protective doctrine is already in `CLAUDE.md`. Delete |
| 15 | 427–440 | `## 15. ✅ DONE [CREATE] `graphics_overhaul_protocol.md:217` — premise now false` | **CLOSED** | `CLOSED.md` | Fixed `c585929`; verified in `design\Jawa\art\graphics_overhaul_protocol.md` — the premise is replaced, the per-script table and warning kept. One line: *"§15 graphics protocol premise — replaced, table kept verbatim, venv at `~/.venvs/rimworld` — `c585929`"* |
| 16 | 441–498 | `## 16. [WORLD] `refresh.py --patches` validates against NOTHING under WSL` | **CLOSED** | `CLOSED.md` | ⭐ **Fixed and re-verified in the code today.** `src\RimMandrake\Utils\refresh.py:405-435` now refuses to validate when any input is absent, uses `_GP.WORKSHOP/LOCAL_MODS/GAME_DATA`, and `and ok`s the validator's exit code. ⚠️ **`queue/OPS.md` O1 still carries this as OPEN — it is stale-open and should be closed, not migrated** |
| 16b | 499–518 | `**The line:** *"A bare `python` is not on PATH in WSL at all…"*` | **DEAD** | — | 🔴 **ORPHANED BODY.** These 20 lines are §15's *original* body, stranded under §16's heading when §16 was appended between §15's closure and its text. They read as open work; §15 above them says DONE and the fix is in the file. This is the exact failure the closed table at 842–853 describes. Delete with §15 |
| 12 | 519–602 | `## 12. [v2] Tools that compare a proxy and fail toward success` | **DOCTRINE** + **DEAD** | ⚠️ **blocked on `OWNER_DECISIONS.md` #5** — see recommendations below | Doctrine → D1, D2. All four open bullets are gone or migrated: deploy hold list **closed** (`C1`, `e15c081`); artefact-existence **fixed** (verified: `refresh.py` `_has_files` with the exact doctrine in its docstring) though `O2` still reads open; `loadset_fingerprint` **fixed** (verified: it now returns `missing` and a `modCount` of mods *present on disk*) though `O3` still reads open; Patches-vs-Defs **fixed** (`validate_patch.py` docstring line 4 says it does both) though `C-v2` still reads open |
| 13 | 603–637 | `## 13. [WORLD] ✅ CLOSED 2026-08-13 01:05 — removed, 573, new fingerprint` | **CLOSED** + **DOCTRINE** | `CLOSED.md` + D8 | Verified closed. Doctrine → D8 (and D8 is **already** in `traps-mods-and-managers.md`, so it is a delete, not a move) |
| 13 *(again)* | 638–689 | `## 13. [WORLD] ⏳ Mythological Creatures! unsubscribed — verify after a CLEAN EXIT` | **DEAD** | — | 🔴 **This is the duplicate section number**: two `## 13` headings, 35 lines apart, the second inside a `<details>` block. Superseded by the first, which records that its central prediction was **wrong**. Delete |
| 14 | 690–742 | `## 14. [BRIDGE] The visual-audit queue is not runnable` | **DEAD** | — | Fully migrated. `jawa/list_factions` **closed** (`CLOSED.md:11`, `7bd8b60`, 34 factions live); rotation → `queue/BRIDGE.md` **B1**; style → **B2**; xenotype → **B3**, all open and built. Nothing homeless |
| 17 | 743–809 | `## 17. [PROJECT] [v2] Evaluate **Space Tower**` | **DEAD** | — | Answered twice and ruled. `queue/CREATE.md` **C2** = *KEEP, unconditionally*; `queue/VISION.md` **V11** = *ruled in*; owner ruled the dependency direction (`CLOSED.md:52`). The measured file survey is worth one `CLOSED.md` line, no more |
| — | 810–863 | `## ✅ Closed — one line each, so nobody re-files them` | **CLOSED** + **DOCTRINE** | `CLOSED.md` (7 rows) + D4, D5, D6 | Move the seven table rows verbatim into `CLOSED.md`. The prose below it is doctrine → D4 (a fix may be a prohibition), D5 (a sweep launders stale items — **already** in `DOC_BUDGET.md`), D6 (`foundationGrid` uniformity — **nowhere else**, do not lose it) |
| 20 | 864–897 | `## 20. [?] `src/RimMandrake/Utils/ilscan.py` reads only `ldc.r4`` | 🟢 **LIVE (L2)** | **`[?]` → recommend `queue/BRIDGE.md`** | `[v2]` — verified: `ilscan.py:152` is still `if op == 0x22:` alone. The section carries a **verified fix and its validation** (widening to `0x7D` reproduces `Buildings_Gravship.xml` exactly), so migrate the body, not a summary. **Ownership ambiguity is real — see the note above L1** |
| 21 | 898–935 | `## 21. [?] Two donor mask filenames carry an underscore RimWorld will never look for` | 🟢 **LIVE (L3)** | **`queue/CREATE.md`** | `[v2]` — verified on disk 2026-08-13: both `_east_m.png` files still present, alongside the correctly-spelled `..._eastm.png` that proves the convention. `[?]` resolves to CREATE: the fix is authoring a new override mod, which is CREATE's by `infrastructure\agents\CREATE.md` ("ORIGINATING… any future not-yet-live mod") and by the one-donor-one-fix-mod ruling |
| 22 | 936–968 | `## 22. [?] "RimWorld rewrites `ModsConfig.xml` on exit" is FALSE` | 🟢 **LIVE (L4)**, mostly **CLOSED** | `queue/OPS.md` for the one live row | 5 of 6 rows are done — verified: `rimworld-load-round\SKILL.md:50`, `traps-mods-and-managers.md:69` and `rimworld-modding\SKILL.md:326` all now carry the correction (`P8`, `a43b610`); the `NEXT_RELOAD.md:18-35` row is **dead** (those lines are now the worldgen anchor); the `TODO.md:644` row dies with the file. **Only `forbidden_mods.md:171` survives = L4.** The section's *second* claim — seven fix mods absent from `ModsConfig.xml` — is **also closed**: verified all seven are present today (`C3a`) |

---

## DOCTRINE — recommendations for `OWNER_DECISIONS.md` #5

🔴 **I have not decided this and have moved nothing.** Owner decision #5 asks
where `TODO.md` §12's doctrine and §7's closed record should go. Below is one
recommendation and one line of case per item, so it can be answered once.

**My overall recommendation in one sentence:** *doctrine goes to the traps file
for the domain it is about, never to `agents_def.md`* — `agents_def.md` is read
once at session start and describes **who does what**, while these are all
**how to avoid a specific failure**, which is what an indexed traps file is for
and what agents actually grep.

| id | doctrine | recommended destination | the one-line case |
|---|---|---|---|
| **D1** | §12 — *"An artifact that records an OUTCOME cannot answer a question about a CAPABILITY"*, plus the two-question procedure (*what artifact does this compare? what can that comparison NOT distinguish?*) | `skills\rimworld-modding\references\traps-tooling.md`, title added to the `traps.md` index in the same commit | The five confirmed instances are **already** logged in that file (`f8eea20`, `cfaaf0d`); the generalisation belongs with its own evidence, and it is invoked while reading a mod's files, which is exactly when that file is open |
| **D2** | §12's counterpart — *"take the RULE from a precedent, not the NUMBER"* (the 64%-hidden-conduit refusal) | same file, adjacent entry to D1 | It is the mirror image of D1 — *right field, wrong instance* versus *wrong field* — and separating them loses the pairing that makes either memorable |
| **D3** | §11 — the ordered *"what actually protects you"* list, headed by `git commit <paths> -F -` | **NOWHERE — delete** | Already stated in `CLAUDE.md` §"Commit explicit paths only" **and** enforced by `.claude\hooks\block_blanket_git_stage.py`, whose own header documents the index race; a third copy is precisely the drift this project keeps paying for |
| **D4** | 822–840 — *"sometimes the correct output is a DO-NOT-DO-THIS, and the prohibition must say why or the next person will helpfully undo it"* | `skills\rimworld-savegame\SKILL.md` (the `fogGrid` instance is savegame-specific), with the one-sentence generalisation in `infrastructure\DOC_BUDGET.md` | Both worked instances are concrete savegame hazards; the *general* clause is a documentation rule and `DOC_BUDGET.md` already owns "a written instruction rots" |
| **D5** | 842–860 — *"check the target exists before you collapse"* and *"a sweep that reformats without re-checking launders stale items into fresh-looking ones"* | **NOWHERE — delete** | Verified already present as `infrastructure\DOC_BUDGET.md` §"Before you collapse, summarise or defer anything: check the target exists" (line 94) |
| **D6** | 838–840 — `foundationGrid` is **uniform across all 62,500 cells**; a rule inferred from a uniform sample is how a wrong rule gets baked in | `skills\rimworld-savegame\SKILL.md`, beside the existing `foundationGridDeflate` material | 🔴 **This exists nowhere else** — grepped `skills\`; the only other hit is a rimbridge note about the *terrain layer*, not the uniformity warning. Deleting `TODO.md` without moving this loses it |
| **D7** | §7 — *"write the three expected-failure signatures BEFORE launching; a signature invented after reading the log is not evidence, it is a story that fits"* | `skills\rimworld-load-round\SKILL.md` | Verified **not** in that skill today (`grep signature` → nothing), and it is the condition on which the owner's batching waiver rests — the file read before every load is the only place it can do its job |
| **D8** | §13 — *"a clean exit makes `ModsConfig` authoritative about what the game LOADED, never about what is on disk NOW"*; check the entry **and** the folder, read the mtime as the tell | **NOWHERE — delete** | Verified already present at `skills\rimworld-modding\references\traps-mods-and-managers.md:69-74`, in corrected form, with the Steam half preserved |
| **D9** | §0 — *"`125 distinct fields` is the SCHEMA, not a checklist"*; 24 fields never vary, the real surface is `pawnGroupMakers` | **NOWHERE — delete** | Verified already recorded at `design\Jawa\worldbuilding\faction_engine_gap_audit.md:159`, which is the audit that produced it and the file VISION reads |

**Net if the owner takes these:** 4 doctrine moves (D1, D2, D4+D6, D7), 5 deletions
verified as already-recorded elsewhere. `agents_def.md` gains **nothing**, which is
the recommendation.

---

## Mechanical execution order

Do not start until `OWNER_DECISIONS.md` #5 is answered — steps 3 and 4 depend on
it. Steps 1, 2 and 6 do not, and can go first.

1. **Repair the inbound references** (the blocker table above), including the two
   line-number citations in `STALE_FILE_AUDIT.md`. One commit, no deletions yet.
2. **Append the CLOSED rows.** 7 rows from the existing closed table verbatim, plus
   one new line each for §0, §7 (row exists), §9's reproduction, §13, §15, §16,
   §17, §22. **Do not re-add rows `CLOSED.md` already holds for §2, §7 and §14.**
3. **Move the doctrine** per the owner's answer to #5 — D1, D2, D4, D6, D7 as ruled;
   D3, D5, D8, D9 deleted as verified duplicates.
4. **File the four LIVE items** — L1 → `queue/CREATE.md`, L2 → wherever the `[?]`
   is ruled, L3 → `queue/CREATE.md`, L4 → `queue/OPS.md`. Each carries its
   verification evidence, not a summary; L1 must carry its *do not fix the walk*
   prohibition.
5. **Reduce `TODO.md` to a pointer stub** — five queues, `CLOSED.md`,
   `OWNER_DECISIONS.md`, `TODO_v2.md`. ~10 lines, well under its 400-line budget.
6. **Separately, tell the owning seats their queues are stale-open** — `O1`, `O2`,
   `O3` and `C-v2` are all recorded open while the code is verifiably fixed. That
   is four items on other seats' boards, so it is a filing, not an edit.

---

## What surprised me, in order

1. **`TODO.md` is 90% dead weight, not 60%.** The ~14 estimate counted items the
   queues had already absorbed. The real figure is **4**.
2. **Nine other files cite `TODO.md` by section number, and five of those citations
   already dangle.** Retiring the file without repairing them makes a documentation
   problem worse, not better — and one citation (`queue/CREATE.md:255` → §20) is
   what keeps L2 alive at all.
3. **Four queue items are recorded OPEN against code that is verifiably fixed**
   (`O1`, `O2`, `O3`, `C-v2`). `refresh.py` even carries the doctrine from its own
   TODO entry in a docstring — the fix landed and nothing wrote back to the queue.
4. **Lines 499–518 are an orphaned §15 body sitting under §16's heading**, reading
   as open work, ~60 lines below its own closure — the exact failure mode this
   file's own closed table warns about at line 842.
5. **The duplicate `## 13` is benign** — the second is the original, deliberately
   kept inside a `<details>` block — but the file records that its own central
   prediction was **wrong**, which is the most useful thing in it.
