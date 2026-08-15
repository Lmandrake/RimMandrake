# V1_CHECKLIST.md — every remaining step to v1, in order

_Assembled by PROJECT, 2026-08-14, from a full audit of `V1_SCOPE.md`, all five
seat queues, `NEXT_RELOAD.md`, `WORLDGEN_RUN.md`, `WORLDGEN_FACTION_CHECKLIST.md`,
`OWNER_DECISIONS.md` and `EXPECTED_FAILURES_next_load.md`._

> **`V1_SCOPE.md` says WHAT v1 is and WHY. This file says WHAT IS LEFT and IN WHAT
> ORDER.** They are different documents on purpose. **Where they disagree about
> state, this file is newer — but `V1_SCOPE.md` still wins on the v1/v2 LINE.**

**Nothing here is a v1 decision.** Every scope call is already the owner's or
already recorded; this file only sequences them.

---

## SCORE: **5 of 8 rows closed** — 1, 4, 5, 6, 8. **Open: 2, 3, 7.**

**The single scarce thing is ONE shutdown window followed by ONE cold load.** That
sequence closes rows 2 and 7, W1, W3 and W4, and puts row 3 in reach in the same
session. Everything in Phase 0 exists to make that sequence not need repeating.

| phase | needs | closes |
|---|---|---|
| **0 — now** | nothing. Offline, game may be up | prepares everything |
| **1 — shutdown window** | game **DOWN** | nothing directly; **unblocks all of it** |
| **2 — cold load + worldgen** | ~25–30 min, **irreversible** | **2, 7**, W1, W3, W4 |
| **3 — on-map verification** | the map from phase 2 | **3**, row 4's hulk rider |
| **4 — the playable session** | phase 3 green | **v1 itself** |

---

## PHASE 0 — do now, offline. No game required.

| # | step | owner | gate / evidence | state |
|---|---|---|---|---|
| 0.1 | Finish `jawa/fire_quest` and `jawa/get_defs` in the companion | BRIDGE | builds; tool names present via `strings -a -el` | 🔄 in progress |
| 0.2 | Sea step: arc-distance predicate + elongation assertion | CREATE | ✅ `c3ee8e7`, DLL rebuilt `ba85ee1` | ✅ **done, repo only** |
| 0.3 | `isJunk` removed from both scatter defs | CREATE | ✅ `de1018b` | ✅ **done, repo only** |
| 0.4 | 🔴 **Release the stale hold** at `AGENT_CREATE_state.md:40` — it still reads *"placement code HELD for VISION's settled spec"* and the spec settled 01:30, the code landed 02:39 | CREATE | the line no longer says HELD | ⬜ **open** |
| 0.5 | 🔴 **Fix `EXPECTED_FAILURES_next_load.md`'s census gate.** It requires the count to read **21** and makes ≠ 21 a **FAIL that gates rows 2 and 7**. The artifact defines **24** | OPS | gate derives the count, does not name it | ⬜ **open — would fail the correct deploy** |
| 0.6 | 🔴 **`worldgen_sea_spec.md` still says *"Latitude IS the axis"* (`:150`) and *"this file wins"* (`:170`)** — both wrong, and unedited on disk. Anyone building from the spec alone still gets the wrong axis | VISION (down) | the spec states arc distance from the subsolar point | ⬜ **open** |
| 0.7 | Fix the `[?]` routing instruction at `CREATE_TEST_PLAN.md:268` — it routes findings to `TODO.md`, which was retired. Anything filed during the run lands in a stub nobody reads | CREATE | it names a live destination | ⬜ **open** |
| 0.8 | Settle O12 — the 9 `GeneratePawnRelations` NREs. OPS's own note: *"Settle it BEFORE the worldgen session; relation generation runs for faction leaders and a failure there is silent"* | OPS | attributed or cleared | ⬜ **open** |
| 0.9 | Fix O14 — `preload_check.py`, the last gate run before a 25–30 min load, answers differently per seat | OPS files · CREATE owns the file | both interpreters agree, and a missing root FAILS rather than passing | ⬜ **open** |

---

## PHASE 1 — the shutdown window. **The game must be DOWN.**

🔴 **`--apply` overwrites the game copy with whatever is in the repo at that
moment, including a peer's half-finished work. Scope it with `--mod`; never bare.**

| # | deploy | why it cannot wait |
|---|---|---|
| 1.1 | companion DLL — `jawa/get_defs` + `jawa/fire_quest` | ⚠️ **must pass `--gm`** or it strips `fire_incident` and `send_letter` |
| 1.2 | `JawaScrapfields.xml` (`de1018b`) | repo-only; game copy still has `isJunk` |
| 1.3 | `JawaGroundHulk.xml` (`de1018b`) | same |
| 1.4 | ⏳ **`BuzzerApostrophe_Fix.xml`** (`3822ef9`) | 🔴 **THE ONLY ITEM WITH A DEADLINE.** Names bake into the save as strings — worthless the moment the world is made |
| 1.5 | `AnimalBiomeDuplicates_Fix.xml` (`9acddd3`) | ⬇️ **drop this one first if the window is tight.** Already deployed since 08-10 with zero live errors; the drift is a refinement |
| 1.6 | **`JawaSeaShaper.dll` — SOLO, not in the batch** | a new assembly poisons attribution for everything beside it. ⚠️ The write **fails `OSError 22` while the game runs** — loaded and locked |
| — | Armoury × 2 | ⛔ **HELD on scope.** Row 6 is closed; weapon balance is not v1 |

📐 **If the window is tight, rank by what the window does to VALUE, not by
severity** — see `NEXT_RELOAD.md` §1d. The nastiest bug on this list is the one to
drop, because its fix is already live.

---

## PHASE 2 — the cold load and the worldgen run. **IRREVERSIBLE.**

**Full runbook: `infrastructure/state/WORLDGEN_RUN.md`. This is the index.**

| # | step | owner | gate / call |
|---|---|---|---|
| 2.1 | Announce `LIVE BRIDGE TAKEN`; the **owner** authorises connecting | whoever drives | announcing informs, it does not permit |
| 2.2 | Cold load (~25–30 min) | — | — |
| 2.3 | **Harvest the startup log before any mutating call** | OPS | `harvest_log.py`. ⚠️ The moment anyone spawns a pawn, O12 becomes unattributable |
| 2.4 | **Tool-surface census** | BRIDGE | `rimbridge/list_tools`. 🔴 **Derive the expected count from the artifact — do not compare against a number in a doc.** Three files carried three different numbers |
| 2.5 | 🔴 **OWNER DECIDES AT THE SCREEN: planet type, coverage, seed** | **owner** | ⛔ Nobody pre-ratifies these |
| 2.6 | **Configure Factions** — 21 untick / 6 keep, box by box | OPS at the screen | `WORLDGEN_FACTION_CHECKLIST.md`. **Screenshot before leaving — it is the only record** |
| 2.7 | Anomaly settings: playstyle `Disabled`, **DLC stays enabled**, cherry-picks stand | whoever drives | already ruled; do not re-open at the screen |
| 2.8 | **Generate** | — | — |
| 2.9 | 🔴 **Read the sea step's `Report()` out of the log BEFORE choosing a tile** | CREATE/OPS | ⚠️ **A missing `Report()` means registration failed and the step never ran** — silently. It self-tests coverage, body count, compactness and aspect |
| 2.10 | 🔴 **OWNER PICKS THE LANDING TILE** | **owner** | mutators shown alongside |
| 2.11 | Land | — | — |
| 2.12 | `jawa/list_factions` — the excluded factions are absent | BRIDGE | ✅ **closes ROW 2** |
| 2.13 | `jawa/world_stats` — the world exists on the intended planet type | BRIDGE | ✅ **closes ROW 7** |

---

## PHASE 3 — on-map verification

⚠️ **3.1 and 3.2 do NOT need the campaign world.** They work on any fresh map. If
phase 2 slips again, run them anyway rather than letting them wait.

| # | step | owner | gate / call |
|---|---|---|---|
| 3.1 | Fire *The Claim* and follow it to an end state | BRIDGE | `jawa/fire_quest questDef=Jawa_TheClaim`, then a **state read at T+n**. 🔴 `success` must mean *found in `QuestManager`*, never *the method returned*. ✅ **closes ROW 3** |
| 3.2 | The ground hulk places, and is ship-shaped | CREATE/BRIDGE | **count the prefab pieces and their bounding box.** ⛔ **Not "reads as a downed ship"** — no call can collect that. Row 4's rider |
| 3.3 | Row 5's optional sighting — a naturally-spawned campaign Jawa | BRIDGE | free while the map is up; **row 5 is already closed and this does not reopen it** |
| 3.4 | Confirm the exported layout is **flight-CAPABLE** (owner's ruling: capability v1, hardware v2) | CREATE | zones `S` and `U` reserved per the deck plan. ⚠️ **If a thruster's exclusion run must be OUTDOOR, the stern needs re-cutting — and that reopens row 8.** Test it here, cheaply, not later |

---

## PHASE 4 — the playable session. **The owner's gate, 2026-08-14.**

> **v1 is not "the world was made". It is the 8 rows, plus the campaign surviving
> one real play session.**

**This phase had never been scoped. It needs a definition before it can be run** —
proposed below, for the owner to accept or cut.

| # | proposed gate | why |
|---|---|---|
| 4.1 | The colony survives **one in-game day** with no red errors in the log | the cheapest objective pass/fail |
| 4.2 | Pawns eat, sleep, haul and work — no stuck jobs, no pathing deadlock | "playable" means the loop turns |
| 4.3 | The clan reads as Jawas on a desert world — xenotype, gear, terrain, the ship | ⚠️ **taste, not a call. The owner's eyes are the instrument.** Do not fake a gate for it |
| 4.4 | One save / reload round trip without loss | the campaign must persist to be a campaign |

⛔ **Anything found in phase 4 that is not one of 4.1–4.4 is v2**, per the standing
rule that v1 closes when the gate passes.

---

## 🔴 BLOCKING THE OWNER — nothing moves past phase 2 without these

1. **Release the worldgen hold.** Its stated cause was the sea (~49% ocean against
   a 25% design). **The engineering half is now done in the repo** — it needs
   deploying, not building.
2. **Planet type, coverage, seed** (step 2.5).
3. **The landing tile** (step 2.10).

⚠️ **None of these three are in `OWNER_DECISIONS.md`, whose own rule is that every
owner question lives there and nowhere else.** That is a process defect and it is
PROJECT's.

---

## ⚠️ OPEN CONTRADICTIONS — a closed row may not deliver what v1 needs

| # | contradiction | who resolves |
|---|---|---|
| C1 | 🔴 **ROW 1 IS CLOSED AGAINST A DEMOTED VESSEL.** `V1_SCOPE.md` defines v1's one authored faction as the Imperial Desert Directorate on `OuterRim_GalacticEmpire`. `WORLDGEN_FACTION_CHECKLIST.md:41-48` — **ratified** — makes vanilla `Empire` the Galactic Empire under Palpatine, **strikes** the two-Empire split, and calls the Directorate *"superseded scaffolding"*. **The checkbox is green; the antagonist it was for does not exist** | **VISION** |
| C2 | The `fixedName` patch on vanilla `Empire` is unbuilt and in no seat's queue. Without it the world will not say "Galactic Empire". ⚠️ Its stated dependency is *"needs the generated name first"* — so it is **post-worldgen** and cannot ride the one-shot | CREATE builds · VISION rules |
| C3 | `V1_SCOPE.md` §"Sequencing" says do not verify rows one at a time and hold rows 3 and 4 for the campaign session. `WORLDGEN_RUN.md` says the opposite and is later. **This file follows the later one** — see phase 3's note | PROJECT — **resolved here** |
| C4 | Where the missing scrapfield chunks went is still unexplained. **Owner ruled it ships anyway; row 4 is closed and the density is `[v2]`** | ✅ **ruled — do not re-open** |

---

## ✅ CHECKED AND FINE — recorded so nobody re-finds them

- **Four commit hashes that `git` cannot resolve** — `b2a0a36`, `b7e49db`,
  `7bd8b60`, `fc460e3` — are **not fabricated**. History was re-initialised
  2026-08-13 to shed a 278 MB `.git`; all four are recorded in
  `infrastructure/archive/OLD_HISTORY.md`, which is the ledger `check_refs.py`
  falls back to. **A pre-2026-08-13 hash that resolves nowhere is expected.**
- **Row 4's `isJunk`/`Dunes` campaign risk is retired by design**, not deferred —
  with `isJunk` gone the factor is 1 on every tile. No test needs scheduling.
- **`jawa/list_factions` is already built, deployed and run live** (34 factions).
  `V1_SCOPE.md` still describes it as owed at a shutdown window; it is not.
