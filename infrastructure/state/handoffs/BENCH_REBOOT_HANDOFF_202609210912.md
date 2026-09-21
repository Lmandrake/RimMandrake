# BENCH_REBOOT_HANDOFF_202609210912 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609210158`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔴 **Eleven owner rulings landed in one sitting, and the two most expensive mistakes of the
session were both in the QUESTIONS, not the answers.**

- Two desert questions were put to him as *"7 droid rows"* and *"5 vanilla rows"*. Both were
  already **0 and 3** — changed by same-day commits. His answers survived and nothing wrong
  was built, but he was asked to rule on work that no longer existed.
- The cold-load question was put to him as *"map generation is BROKEN on the full list"*. It
  was a **19-mod tier**, already diagnosed and closed by FOUNDRY hours earlier.

🔑 **Re-measure a count immediately before putting it in front of him, not when the item was
written.** This queue moves same-day, and an item's own prose is not a measurement.

## What the owner should see

**Five things are built and waiting only on his eye. Nothing else is blocked on him.**

| what | path |
|---|---|
| 4 biome names — the whole mod split waits on these | `D:\Luke\dev\Rimworld\Transient\biome_name_drafts_2026-09-21.md` |
| 6 shrubland names **+ the new tree guardian** | `D:\Luke\dev\Rimworld\Transient\shrubland_name_drafts_2026-09-21.md` |
| 16 drafted creature names — unreacted-to becomes real | `D:\Luke\dev\Rimworld\Transient\drafted_creature_names_2026-09-21.md` |
| the 71-label hierarchy he ruled — proposed vs current | `D:\Luke\dev\Rimworld\Transient\world_label_hierarchy\ashkarr_labels_PROPOSED.png` |
| 24 desert renders | `D:\Luke\dev\Rimworld\Transient\desert_art_verdict_2026-09-20.html` |

**Three one-word decisions, each blocking one item:**
- **`Rat`** — he ruled *"replace all 5"*, but `Rat` is wired nowhere, so re-adding one to
  replace it would contradict the Fall-Line arrivals ruling. `DESERT_FAMILY_PORT_EXECUTION_1`.
- **`MA_Sporemole`** — genuine port-or-drop; donor mod inactive, no port exists.
- **The label ceiling** — Deadstone lands at effective 104. A looking decision.

🔴 **He has NOT been told the mapgen premise dissolved.** He ruled *"fix mapgen first, then
one load"* believing the full list was broken. It never was. The load was run on the half of
his ruling that still stands — one batched load — and it passed; he should know the question
was wrong.

## What is half-done, and where it stops

- `WORLD_LABEL_SIZE_HIERARCHY_1` — offline pass DONE, preview rendered, **no save written**.
  NEXT: show him `ashkarr_labels_PROPOSED.png`; on his word, apply via the bridge to a NEW
  save slot. ⛔ Never the canonical save.
- `GELATINOUSSLIME_FIRST_LOAD_ERRORS_1` — 3 faults found by the first load with the mod
  active. NEXT: delete the two `wildGroupSize` lines inside `<race>`, then read the
  `RM_Titanoslime` ConfigError with `harvest_log.py --show configerror`.
- `PATCH_FILES_UNDER_DEFS_INERT_1` — 2 patch files under `Defs/`, 7 operations inert, one an
  owner ruling from 2026-09-16. NEXT: move both to `Patches/`, redeploy, and **prove the
  operations took** — a patch that matches nothing logs nothing.
- `TITANOSLIME_PERMANENT_GROWTH_LIVE_1` — built and deployed, unproven. NEXT: a scratch map,
  not the campaign; drive every shrink path and run the reversible-ON control.
- `WORLDVIEW_MISLABEL_FALLOUT_1` — renderer fixed, conclusions not. NEXT: list every
  label-bearing worldview artifact and classify each as unaffected or needing a re-check.
- `BARREN_REGIONS_NAME_NOTHING_1` — 10 of 22 entries name nothing. ⛔ `ashkarr_settle.py`
  must not run until fixed. NEXT: resolve each of the ten, then make the set REFUSE on a
  name that matches nothing.
- `UMBRA_IS_A_REGION_NOT_A_BIOME_1` — ruled, untouched. NEXT: decide what biome Umbra's tiles
  carry before retiring the BiomeDef.
- `BIOME_MOD_SPLIT_EXECUTION_1` — **unblocked**, all 10 questions ruled. NEXT: every row whose
  name is settled can start; Q2/Q5 rows wait on his pick.

## Traps learned

- 🔴 **A savegame's `tileFeature` grid stores the feature's uniqueID, not its list index.**
  `worldview.py` read it as an index and mislabelled every region on every Ash'karr render,
  with matching wrong tile counts. Fixed at `1a96f1e2a`. An id-vs-index confusion never
  errors — it just renames everything. (filed: LESSONS_INBOX.md 2026-09-21; item `WORLDVIEW_MISLABEL_FALLOUT_1`)
- 🔴 **Never type a `jawa/` leaf or a parameter name you have not just read.**
  `jawa/pawn_detail` does not exist and `jawa/pawn_traits` takes `pawn`, not `pawnId`. Each
  produced a confident **"0 of N carry Wimp"** — the alarming direction, which is the one you
  believe without checking. (filed: LESSONS_INBOX.md 2026-09-21)
- 🔴 **A patch file under `Defs/` is parsed as a Def and every operation is inert.** Scope it
  by `root.tag == "Patch"`; searching `Defs/` files that mention `PatchOperation` returns ~20
  and is WRONG — the real count is 2. (filed: LESSONS_INBOX.md 2026-09-21; item `PATCH_FILES_UNDER_DEFS_INERT_1`)
- 🔴 **`launch_and_wait.sh` printed `TIMEOUT after 273s` on a load that succeeded at 1005 s.**
  Its exit code is not the signal. Poll for the bridge line yourself. (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ **`grep -c` on a Player.log counts LINES.** One 30-line stack trace is not 30 errors. Use
  `measure count-errors`; the blind-scan hook refuses and names the instrument. (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ **The canonical save's `<features>` element is NESTED.** A non-greedy regex to the FIRST
  `</features>` yields an unparseable fragment. Take the last close tag. (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ **A creature's size field is `baseBodySize` inside `<race>`, not `<bodySize>`.** Grepping
  the wrong name returns nothing and reads as "no such field" — it briefly made a true
  finding look false. (filed: LESSONS_INBOX.md 2026-09-21; item `TUNNELSNAKE_VIOLATES_SIZE_LADDER_1`)
- ⚠️ **Before normalising names against "the planet", measure the planet.** 68 of 71 features
  carry no article but **three do**, and two painter divergences were a spelling and a plural,
  not articles. A blanket strip would have written three new wrong names. (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ **A roster JSON's `evictions[]` are already-dispositioned records.** Counting every
  `BMT_` string in `the_forge.json` produced "27 unreconciled names" and a filed item; the
  live count was zero. (filed: LESSONS_INBOX.md 2026-09-21)

## Closed since the last handoff (2)

- `FORGE_ROSTER_UNRECONCILED_BMT_1` — a1ad39b1d1c2fcd346ace3feb9132ff14bdded12
- `FOUNDERS_IMPORTER_OWED_1` — ea58abc1b880ee4d8006bca69c89a07092b02443

## Filed and still open (9) — the next seat's queue

- `BARREN_REGIONS_NAME_NOTHING_1` — 10 of 22 BARREN_REGIONS entries name regions that do not exist - the keep-empty test fails open
- `SHEET_REVIEWED_FLAG_UNIFORM_1` — No uniform way to tell an owner-ruled sheet from an agent prefill - six different keys across 13 sheets
- `WORLDVIEW_MISLABEL_FALLOUT_1` — worldview.py labelled the wrong regions on every render - re-check conclusions drawn by LOOKING
- `FEATURE_DRAWCENTER_UNVERIFIED_1` — Only 2 of 71 world features have a verified drawCenter, and growing labels make a wrong one worse
- `SWEETLINE_WOOL_HARVEST_1` — The giant-wool harvest the sweetline trees are built around does not exist as a def
- `TUNNELSNAKE_VIOLATES_SIZE_LADDER_1` — RSW_TunnelSnake ships at baseBodySize 2.0, inside the large band a ratified ruling declares empty
- `PATCH_FILES_UNDER_DEFS_INERT_1` — Two patch files sit under Defs/ so RimWorld parses them as Defs - 7 operations inert, including a 2026-09-16 owner ruling
- `GELATINOUSSLIME_FIRST_LOAD_ERRORS_1` — First load with GelatinousSlime active: wildGroupSize in the wrong element twice, plus an RM_Titanoslime def error
- `TITANOSLIME_PERMANENT_GROWTH_LIVE_1` — Prove Titanoslime growth is permanent in a running game - not testable from a load, needs a scratch map

## Commits

```
ce801a9b3 Founders importer PROVEN LIVE: 6 of 6 carry Wimp. Item closed.
ea58abc1b The batched cold load ran: Pyrelands rename PASSES live, two new defects found
35d6e2035 rimflow: close PYRELANDS_DEFNAME_RENAME_1 (verified, no code change owed)
bf43fce41 Decision strings for the batched cold load, written before launching
eb83c571c LESSONS_INBOX: three counting traps from the ruled-work round
61d8ebb3c Two of the desert counts put to the owner were already stale when I asked him
a1ad39b1d Roster reconciliation writeup: record final commit hash
6af64f818 Reconcile the Rot and the Forge rosters: wire 10+1 owned-but-unwired species, drop 3 dead rows
a0157f8b6 Fill in the commit hash in the desert-family-rulings progress note
de67541e0 DESERT_FAMILY_PORT_EXECUTION_1: three owner rulings 2026-09-21 (MossBeetle back, droids out, vanilla rows replaced)
0e31bfdea Shrubland name sheet: add the tree guardian so it is one sitting, not two
b7834d837 Two items the tree-guardian design turned up, one of them a ratified-ruling violation
e607b317e Sweetline guardian spec: generic warden species, scoped-rage territory (SHRUBLAND_TREE_GUARDIAN_1)
c4e471926 LESSONS_INBOX: the id-vs-index mislabel, and borrowing a formula without checking it
da0f5ae53 Two items from the label pass: mislabelled renders, and 69 unchecked label positions
1a96f1e2a Size the whole planet: label hierarchy for all 71 world features, offline
9a897d130 GelatinousSlime activated and four blocked deploys landed while the game was down
739c9d505 Run sheet: Titanoslime permanent growth is built, not owed
8b9483b2e Titanoslime: growth is now permanent, not reversible (owner ruling 2026-09-21)
440fb1292 LESSONS_INBOX: four traps from the wake-and-rule round
... 12 more: git log --oneline 91630bd1e..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-21T09:10:41Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   the health publisher — auto-regenerated by `code_review_status.py`'s `_trigger_health_rebuild` on every prune/list. NOT a seat's
 M Transient/codebase_health.json   the health publisher — auto-regenerated, not a seat's
 M Transient/codebase_health_artifact.html   the health publisher — auto-regenerated, not a seat's
 M design/Jawa/fauna/cast_assignment.csv   FOUNDRY — already modified before this window woke; left untouched
 M infrastructure/dashboards/hub/data/health.json   the health publisher — auto-regenerated, not a seat's
 M infrastructure/state/codebase_health_last.json   the health publisher — auto-regenerated, not a seat's
 M infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202609210158.md   MINE — added an explicit `NEXT: nothing` to the corrected mapgen entry so the gate stops reading a closed item as half-done work. Committed with this handoff
M  infrastructure/state/items/BARREN_REGIONS_NAME_NOTHING_1.md   🔴 THE OTHER WINDOW — FOUNDRY has already picked up the item I filed this session and is working it. STAGED, not mine. ⛔ Do not commit, revert or stash it
M  src/RimMandrake/Utils/ashkarr_settle.py   🔴 THE OTHER WINDOW — FOUNDRY, same barren-regions work. STAGED. ⛔ Leave it alone
A  src/RimMandrake/Utils/selftest_ashkarr_settle.py   🔴 THE OTHER WINDOW — FOUNDRY's new selftest for the barren-regions guard. STAGED and NEW. ⛔ Leave it alone
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   another window's scratchpad path leaked into the repo root (session 84f9b274, not this one) — left untouched
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   another window's scratchpad path leaked into the repo root (session 84f9b274, not this one) — left untouched
?? infrastructure/state/.rimflow_conc_97j8px_9/   another window's rimflow concurrency lock — left untouched deliberately
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   another window — left untouched deliberately
```

