# CLOSED.md — one line per finished item

_The ledger that lets bodies be DELETED. Its whole job is to stop a closed item
being re-filed, re-investigated, or carried as a struck-through block in a growing
file. One line, with the hash — `git show <hash>` has the full story._

**Append here, then delete the body from wherever it lived.** Never both.

🔴 **68 rows for 2026-08-12 and 2026-08-13 live in
`infrastructure/state/CLOSED_archive_2026-08-12_13.md`.** Grep the whole of
`infrastructure/state/` before re-filing — this file is the recent tail, not
the whole ledger. Archive the oldest again when it fills; never suppress a
closure to fit.

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-14 | BRIDGE B0 — companion deploy | DEPLOYED + byte-verified in the game copy, 17 tools, stamp `e2a2048f1434`; superseded by the 22-tool build | `e15c081` |
| 2026-08-14 | BRIDGE B-t1 — `ilscan.py` compiled defaults | DONE: decoder widened to `stfld` (0x7D); re-verified 2026-08-14, the vanilla-mirror block reproduces `Buildings_Gravship.xml` (16.9/18.9/250/750/24.9) | `027572c` |
| 2026-08-14 | OPS filing — `prove_new_tools.py` FAILs a healthy deploy | FIXED: `ALL_TOOLS` was 16 against a 17-tool deploy; now the full set, gate reads 20 (18 non-GM) | `68a0a30` |
| 2026-08-14 | BRIDGE B-v3 — bridge cannot order a pawn to walk | BUILT AND DEPLOYED as `jawa/order_pawn` (+`targetId`/`pathEndMode`). Live run still owed — carried in the queue, not closed as verified | `bee5da9` |
| 2026-08-14 | `jawa/damage` refusal fix — 'built, not deployed' | WRONG, it WAS deployed: `strings -a` misses UTF-16LE method-body literals; `strings -a -el` finds the marker in the game copy | `15bbf4a` |

## Drained out of `TODO_v2.md`, 2026-08-14 (1,172 → 349 lines)

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-14 | §1 explosion spec — mechanism, IL, energy model | **MOVED, not closed.** Deliverable had no home; now `design/Jawa/explosion_energy_model.md`. §1 survives as a one-paragraph register entry | — |
| 2026-08-14 | §1 droid explosion tiers + salvage IL | duplicate — already in `design/Jawa/droid_ruling.md` §6; the death/salvage IL trace merged into the new explosion doc | — |
| 2026-08-14 | §0c dog sled Eopie-vs-Massiff argument | body deleted; the sled shipped (C3a) and the measurements live in `src/Jawa/DesertVehicleReskin/Source/GEOMETRY.md`. **4 vehicles still open** | `ad3e3c7` |
| 2026-08-14 | §3.2 two-Empire fusion / aristocracy reconciliation | **STRUCK by the owner.** One Empire, one Emperor; vanilla `Empire` reskinned. Canon is `faction_world_spec.md` §5. ⚠️ `faction_roster_v2.md:357` still cites the dead §3.2 | `a8768c7` `78a0967` |
| 2026-08-14 | §3 P2 Royalty-Empire retheme route | dissolved by the same ruling — no retheme mod, label-only, and v1 row 1 already shipped it live | `fad8bab` |
| 2026-08-14 | §3 P1 Imperial settlement counts (10 vs "one or two") | reconciled 2026-08-12; `faction_roster_v2.md` `Target settlements` is **3** (it drives world-map placement, 10 would have inverted the doctrine) | — |
| 2026-08-14 | §3 W1 subscribe + version-verify Galactic Empire | **1.6 CONFIRMED ON DISK**, active in the 580 stack. `required_mods.md:604` carries the verdict | — |
| 2026-08-14 | §3 W2 correct `required_mods.md`'s "1.4/1.5 ONLY" ruling | done — the `❌ RETRACTED 2026-08-12` block plus the Rebel Alliance bullet. ⚠️ **Traps entry still owed** → `TODO_v2.md` §3a; **four bullets missed** → §3d | — |
| 2026-08-14 | §3.35 KotOR-Sith zero-install fallback | superseded — the real Empire module is live with 19 Imperial pawnkinds incl. `OuterRim_ImpStormtrooper_Desert` | — |
| 2026-08-14 | §3 U1 cluster N settlements near a point | mechanism found (Faction Control `factionGrouping: Tight` + CenterPoint), then **corrected at OPS**: `density` is a clumping radius, not suppression. Do not re-investigate Faction Territories, Odyssey landmarks or hand-placement — none was the answer | — |
| 2026-08-14 | §3 W5 `live_mod_inventory.md` stale + hand-maintained | generator built; the file now reports **580 active**, captured 2026-08-14T00:45Z | `b095ff5` |
| 2026-08-14 | §4 W6 Rebel Alliance enable + suppress | already closed both halves — see the `NEXT_RELOAD` block below | `5f68a9e` |
| 2026-08-14 | §1 W8 ion guard collision | already closed — `IsMechanoid` is the right guard; see below | `fc460e3` |

## Drained out of `NEXT_RELOAD.md`, 2026-08-13 (2,354 → 275 lines)

| date | item | outcome | hash |
|---|---|---|---|

## Drained out of `TODO.md`, 2026-08-13 (995 lines → a pointer stub)

`TODO.md`'s own closed table, moved verbatim so the hashes stay findable.

| item | outcome | commit |
|---|---|---|
| 3a. Do symlinked skills get discovered? | **Yes.** Layout stays; the directories fallback is dead. | `0ee33f6` |
| 3c. `src/Jawa/README.md` said four mods | Six. Corrected. | — |
| 5. Docs instructed the call that livelocks the game | All five instances **replaced**, not just warned. | `0b44a1c` |
| 8. Companion build output untracked | Tracked; false rationale removed. | — |
| 3b2. rimbridge traps described its own size | Fixed, then the **fix decayed too** — "short" → "It is 800 lines" at 1,127. Number removed, not corrected. | `b267fab` `297f19d` |
| 3b3. `savemap.py` save-write gotchas | `paint()` no longer orphans `underGrid` (measured 829 buried cells; tested 4/4 incl. write+reload). **`fogGrid` deliberately NOT fixed** — `skills/rimworld-savegame/SKILL.md` §6. | `cccfeb5` `914eecd` |
| 10. `refresh.py` interpreter/path failures | **Both halves fixed.** `D_CONFIG`/`D_DUMP` are candidate lists via `_first_existing`; `run()` now prints `FAILED (exit N)` and `do_offline` refuses to stamp on failure. **Verified under WSL `python` — clean run, exit 0.** | `29c89f0` |

And the sections that were retired with the file:

| item | outcome | commit |
|---|---|---|
| §0 faction roster, Stages 1–2 | done; the evidence is `design/Jawa/worldbuilding/faction_engine_gap_audit.md`. Stages 3–4 migrated to `queue/VISION.md` **V9** `[v2]` | — |
| §9 `validate_patch.py` "matches N nodes IN ONE MOD" | reproduction record closed — it is a **mode confusion, not a validator bug**; `--all-versions` has no load set, so ⛔ do NOT "fix" the walk. The wording fix alone survives, at CREATE, `[v2]` | — |
| §13 Mythological Creatures! removal | removed, 573 active, fingerprint `87050b782f95012f`. Its own prediction was **wrong**: the clean exit left `ModsConfig.xml` untouched; RimSort reconciled it ~90 s later | — |
| §15 graphics protocol premise | replaced; the per-script table and warning kept verbatim, venv at `~/.venvs/rimworld` | `c585929` |
| §16 `refresh.py --patches` validated against NOTHING under WSL | **fixed and re-verified in the code** — refuses to validate when any input is absent, uses `_GP.WORKSHOP/LOCAL_MODS/GAME_DATA`, and `and ok`s the validator's exit code. ⚠️ `queue/OPS.md` **O1** is stale-open against this | — |
| §17 Space Tower | ruled and answered twice — `queue/CREATE.md` **C2** KEEP unconditionally, `queue/VISION.md` **V11** ruled in, VISION gates CREATE. The measured file survey does not need re-running | — |
| §22 "RimWorld rewrites `ModsConfig.xml` on exit" is FALSE | 5 of 6 rows corrected, and the seven fix mods verified **present** in `ModsConfig.xml`. Only `design/Jawa/mods/forbidden_mods.md:171` survives, at OPS, `[v2]` | `a43b610` |
| owner decision #5 — retire `TODO.md` | RULED + EXECUTED: 995 lines → 13-line stub; 4 doctrine moves, 5 deletions as verified duplicates, 4 survivors filed at seats, 12 inbound citations repaired | `e66650f` `dd51a3a` `6edb9d2` `53cb615` `9828b62` `a1c32d2` |
| owner decision #7 — the keep-or-delete set | RULED + EXECUTED: 36 tracked files removed (11.5 MB), 15.4 MB untracked build output off disk, 3 docs salvaged-then-deleted, 7 rows fixed/linked/rewritten instead of deleted, 5 `.skill` zips untracked | `91a6d4b` `fdb5e74` `2caa9ad` `7a11091` `c5fd571` `6b192e9` `8c23f92` |

## Drained out of `queue/CREATE.md`, 2026-08-13 (1,113 → 150 lines)

| date | item | outcome | hash |
|---|---|---|---|

## Drained out of `queue/OPS.md`, 2026-08-13 (650 → 120 lines)

| date | item | outcome | hash |
|---|---|---|---|
| PROJECT P8 — review `rimworld-start-prep`, resolve its clash with `rimworld-load-round` | APPROVED and landed. OPS's measurement won: the game does NOT rewrite `ModsConfig.xml` on exit; load-round §4 corrected in place | `a43b610` |
| 2026-08-14 | CREATE C-t1 — `validate_patch.py` said "IN ONE MOD" | Under `--all-versions` there is no load set, so the count describes **folders on disk**, never the running game. Now reads "one mod folder"; the sibling info line matches. **The walk was correct and is unchanged — wording only.** ⚠️ `skills/` edits do not ship until `package_skill.py --all` re-zips | `499256c` |
| 2026-08-14 | CREATE C-LOAD — the Armadillo `wildBiomes` duplicate's source | **Beasts of the Rim (Continued)** (`mlie.beastsoftherim`, WS 2194018641), sole contributor — verified against the whole workshop tree *and* against every `wildBiomes`-touching `PatchOperation` for an indirect xpath route. **It is at 63, we are at 581: the `PatchOperationConditional` fires.** The feared silent no-op was not happening. Also corrected: the biome side is **Core's** `Biomes_WarmArid.xml`, only the entry is Odyssey-gated | `9acddd3` |
| 2026-08-14 | CREATE — v1 row 8's flight rider, *"is flight v1 or v2?"* | **Capability v1, hardware NOT** — and the deck plan had already ruled it, at `ship_deck_plan.md:224`: *"Phase 4 — Fly … mobility earned, not given"*, with zones `S` and `U` reserved by name. The missing thruster/tank/console is the design, not an omission. Minimum flying config is **8 of 4,057 cells**, Steel 370, and only `BasicGravtech` via `VGE_PilotCockpit`. ⚠️ **One live question left and it has a deadline** — if a thruster's exclusion run must be OUTDOOR, the exported stern needs re-cutting. §11 of `gravship_flight_invariants.md` | `0311e55` |
| 2026-08-14 | PROJECT P9 — OPS suppressed a trap for "the 723-line traps budget" | **The constraint never existed.** `doc_budget.py:69` globs `skills/*/references/traps*.md` — the 700 is **PER FILE**, and the largest is 348. The 723 was the SET total read against a per-file number. 🔴 **Never suppress a trap for the budget**; only the index is held short | — |
| 2026-08-14 | PROJECT P10 — `preload_check.py` answered SAFE/NOT-SAFE by seat | **Fixed by OPS; my first diagnosis was the symptom.** Not the interpreter — `:138` guarded on `hasattr(GP, "STEAM_WORKSHOP")` while `game_paths` exposes `WORKSHOP`, so the platform branch was dead for **every** seat and both hardcoded `/mnt/c` literals always won. Now per-platform roots, and a missing root FAILS instead of `continue`-ing in silence. Same root cause as BRIDGE's GravTech false alarm | — |
| 2026-08-14 | The Armoury patches swept into `81939e1`, a commit titled *genome tooling* | **The sweep is REAL — 922 lines of weapon balance landed under an unrelated subject**, the hazard `CLAUDE.md` §"commit explicit paths only" exists to stop, and it hit while the owning seat was dead. ⚠️ **But "no provenance banner" is WRONG and would have blocked a deploy on a phantom:** both files carry a header naming `gen_armoury_patch.py` and the two rationale docs, and that generator is committed and current (`269a267`), so the patches are regenerable. 🔴 **Not amendable — `--amend` is banned in this tree.** Recorded forward instead. **RULING (MVP seat): the deploy HOLD stands on SCOPE, not provenance** — v1 row 6 is closed, weapon balance is not v1, and it can ship any window. **The shutdown window belongs to `get_defs`, `fire_quest` and the `isJunk` fix** | `81939e1` |
| 2026-08-14 | ⚠️ **CORRECTION to the row above** — I flattened two risks into one and closed the live one | **OPS's concern was never authorship, it was ANCHOR CONTAMINATION**, and the generator banner does not speak to it. The live def dump is **post-patch**, so a generator can re-anchor on our own writes and ratchet — `patch_provenance.py:185-197` returns `(None, "unknown")` precisely so the generator SKIPS rather than guesses (*"guessing is how 99 became 34"*). 🔴 **The tell: `observed/2026-08-13/inventory/patch_ledger.json` — the file the generators anchor through — is uncommitted-modified (15 insertions), and has been all night.** ⇒ the anchors behind the current 922 lines are **not the committed ones: unverified, not wrong.** Cheap fix, because it is regenerable: re-run `gen_armoury_patch.py`, read the banner, **commit the ledger with it.** 📌 *A header answers "who made this"; it says nothing about "what values it anchored on".* The scope hold needs none of this and is unaffected | — |
| 2026-08-14 | CREATE C14 — a reusable quest-authoring skill | **`skills/rimworld-quests/` ships**: SKILL.md (412 lines), three research references, and `scripts/validate_quest.py`. All four owner rulings met — XML-first with C# as a stated escape hatch, the validator, both stages (prose spec → def-field mapping), and the gate: **`src/RimMandrake/StrandedQuest/`, one real non-Jawa quest authored end to end**, pure XML, no DLC dependency. 🔴 **The validator's calibration is the deliverable, not its check count** — 151 shipped quests give 1 error and 40 warnings, and that error is a real Ludeon slip (`CreepJoinerArrival`'s `questNameRules` defines `questDescription->`). The first version reported 915 errors on the same corpus; resolving `ParentName` inheritance and `SubScript` outputs is what closed the gap. ⚠️ **Neither the quest nor the validator has been seen in game** — offline only | `ebec4b4` |
- **#11 `StrandedQuest`** — stays inert, `[v2]`. Answered from `V1_SCOPE.md:86` by OPS, verified by PROJECT: v1 gets one `QuestScriptDef` and row 3 fills it. Never needed the owner. 2026-08-14.
