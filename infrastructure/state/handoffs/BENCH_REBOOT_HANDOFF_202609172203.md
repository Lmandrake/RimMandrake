# BENCH_REBOOT_HANDOFF_202609172203 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609171637`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->

**`PIT_SUPERDEEP_COLLAPSE_1` is now the largest ruled-but-unbuilt thing in the repo, and
its item — NOT the spec — is the authority.** `design/RimMandrake/pit_superdeep_collapse_spec.md`
(1127 lines) was written BEFORE three rounds of owner rulings that changed ten of its
answers, so the item says explicitly that the item wins on any disagreement and lists the
ten revisions the spec is owed. ⛔ **Do not read the spec and act on it without reading
`items/PIT_SUPERDEEP_COLLAPSE_1.md` first** — you would build the version he rejected.

The ruling in one line: **a pit is not a building, it is a SUPERDEEP excavated cell** on the
D/F primitive his own rulings 18/19 already established. His words: *"I'm not really sure a
pit is any different than a deep canal."* MEASURED, which is what made it a defect rather
than an opinion: only **1 of 20** `Source/Pits/*.cs` files touches the primitive, the pit
ships its own incompatible depth ladder (`Shallow/Deep/Chasm` — "Chasm" is in no enum, and
the ruled `Mid`/`Superdeep` don't exist for pits), and **all 18 pit defs share one texPath,
`Things/Building/Security/TrapSpikeArmed`**. So the exact defect that motivated the entire
north-star system — a pawn "staring at the camera" in a box labelled Pit — is unfixed, and
is provable from disk with no game.

Retire 15 of 20 source files, rehouse 5, **unchanged 0**. Zero unchanged is the measure of
the collapse: every file is written against a `Building`.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->

**1. 🔴 FlowWorks is in NO full mod-list snapshot, while the two mods it replaced still are.**
MEASURED against `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (634 active) and
every snapshot back to 2026-09-12: `mandrake.rm.flowworks` appears **zero** times, while
`mandrake.rm.fluidcanals` and `mandrake.rm.pits` are both active — and those two are exactly
the mods with no source in the repo (the only two such, of 114 active `mandrake.*` entries).
So whenever the FULL list is next restored, the game loads the stale deployed pre-merge
FluidCanals and Pits and never loads FlowWorks: a ~15-minute cold load spent proving nothing.
⚠️ **CAVEAT, and it matters:** this is measured from a SNAPSHOT, not the live file. The live
`ModsConfig.xml` is at a Windows path this laptop cannot reach, so **confirm on the Desktop
before acting.** He was shown this and reasonably observed the live list may be a reduced
debug list; the finding is about the RESTORE list, not live state. ⛔ Nothing was written to
`ModsConfig.xml` — it is an expensive-list action and unreachable from here.

**2. His two "nice-to-have" rulings became real commissions and he should know they are
filed.** `FLOWWORKS_DOOR_FAMILY_1` (Sluice + SecurityGrateDoor, both stuffable) came out of a
question about mechanoids, and the pit ruling grew a rendering feature — a pawn's vertical
draw offset varying with cell depth, plus superdeep walls **20% above the occupant's head**.
That 20% is the only number he has given for the pit's art and it is testable from a
screenshot. Neither was asked for at the start of the sitting; both are now items.

**3. He should know `pit_depth_ladder_legible` reopens ruling 19.** He rejected narrowing that
bar and ruled *"All depths must be visually legible and differentiable graphically"* — which
ruling 19's single inner-shadow-edge treatment for all dry depths cannot deliver. The item
says so plainly rather than logging 19 as satisfying it, but **19 is now effectively open and
nobody has re-ruled it.**

**4. 44 bars bind and 0 are covered, still.** `shows=` appears in **0 of 17** mod
`validation.py` files, so every `modcheck run` returns REFUSED before the game is consulted.
Six new pit bars were approved this window, which **adds refusals, not coverage**. He was told
this explicitly when approving them. The falsification test `NORTH_STAR_PIT_PILOT_1` has still
never run.

**5. Flagged and shipped deliberately:** `modcheck lint`'s suite gate is NOT armed. §3 of the
assessment wants the selftest to fail on live findings, but 41 exist today, and a permanently
red checker is a disbelieved checker. It asserts fixtures plus positive input counts only.
Arming it is owed after a cleanup pass.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->

- **`DETERMINISTIC_CHECKER_WAVE_1` — C1 and C2 SHIPPED, C3 declined by him, C5 shipped.
  Still open for C4/C6/C7/C8/C9.** Exact next action, cheapest first: **C7 is one command**
  — `code_review_status.py prune --apply` clears 97 dead-path DIRTY entries out of 227, so
  the review backlog stops reading 43% too big. C9 is ~10 LOC (make the exec-bit assertion
  in `selftest_documented_commands.py` platform-conditional; it fails on macOS only because
  `./game`, `./bridge`, `show.sh` lack the bit). C4 is `modcheck floor --all`, ~90 LOC.
  ⛔ Do NOT build any of them as a blocking `PreToolUse` hook — §10.9 and the standing ruling.

- **`modcheck lint` reports 41 FAIL / 15 WARN and nothing has been fixed.** The findings are
  real and mostly need HIS ownership calls, not code: 25 VACUOUS checks across 24 walks whose
  mods were absorbed into others. Exact next action: **do not repoint or delete a walk on your
  own judgement** — §10.5 records that an automated repointing sweep is what CREATED the 9
  subject-collisions `doctor` now reports. Build him a decision sheet (he asked for one, then
  chose "wait for C2, then build the sheet from it" — C2 now exists, so **that sheet is owed**).

- **`PIT_SUPERDEEP_COLLAPSE_1` — fully ruled, nothing built.** All ten of the spec's §9
  questions are answered on the item. Exact next action: **revise the spec against the item's
  ten owed revisions** (listed in the item's `## spec` section) BEFORE any code. First
  implementation question that must go back to him, per the item: with fluid typed per liquid
  BODY, **two pits joined by a channel become one body — do their fluids merge or refuse to?**
  That is gameplay-visible and undecided.

- **`FLOWWORKS_DOOR_FAMILY_1` — filed, no spec.** Exact next action: spec it, and build the
  TWO-def stuffable version (`Sluice`, `SecurityGrateDoor`). ⛔ He described three fixed defs
  and talked himself out of them in the same breath — do not build three.

- **The 12 stranded Pits bars are NOT moved, deliberately.** `Pits.md` still holds 11+1
  VALIDATED bars binding nothing (its mod folder holds only `__pycache__`). Moving them was
  blocked because several are claims about a `Building` that the ruling retires. They are
  rewritten as part of the collapse, and all 12 old ids are recorded on the item so none is
  lost. ⛔ Do not move them as-is.

- **`BENCH_REBOOT_HANDOFF_202609171637`** (this window's predecessor, 09:39 today) is still
  open and unclosed — I did not close another handoff's item.

- **Nothing is mid-edit. Working tree is clean** apart from 5 generated codebase-health
  artifacts that a sync job owns (`Transient/codebase_health.*`,
  `infrastructure/dashboards/hub/data/health.json`,
  `infrastructure/state/codebase_health_last.json`). I deliberately never committed those —
  they are not this window's work.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->

**1. 🔴 A backgrounded `Agent` is KILLED after 600 s of no streamed output, and leaves NOTHING
on disk.** Three died that way this window — "Agent stalled: no progress for 600s (stream
watchdog did not recover)" — all mid-read before their first write, all leaving a clean tree,
so each cost a whole run rather than being truncated. The two that survived streamed output at
385 s and 575 s. **Remedy that worked: tell the subagent to write a skeleton file immediately
and fill it section by section**, because a file write emits progress and persists partial
work. The spec that finally landed did exactly that after its predecessor died saying "I have
enough. Writing the spec." (Filed to LESSONS_INBOX, `44726fcde`.)

**2. `grep -c '<li>'` on `ModsConfig.xml` returned 48 where the real count is 631** — it counts
LINES containing the tag, not elements, and that file puts many on one line. A plausible wrong
number on exactly the class of file CLAUDE.md says never to scan. Parse the XML. I only caught
it because he pushed back on the finding.

**3. `northstar.parse()` returns a DICT, not an object.** `getattr(w, 'must_show')` silently
yields `None` → `len()` 0, so all four validated walks read as "0 bars" — an alarming wrong
number that looks like a catastrophic finding. Use `w['must_show']`. A count that is
conveniently *or* alarmingly round is a query bug until proven otherwise.

**4. A subagent reported a structural fix "done" when only half of it existed.** `doctor`'s
`status.check_or_orphaned()` helper was written, but nothing called it, because I had told the
agent not to touch `cli.py`. `modcheck status` still printed `FluidCanals GREEN` for a mod that
does not exist. **The lie was still on screen after the agent said it was fixed** — verifying
by running the command, not reading the summary, is what caught it. Corollary: if you forbid a
subagent from touching the caller, YOU own wiring it.

**5. A checker can manufacture findings by over-strict comparison.** `doctor`'s first pass
reported 13 STATUS_DISAGREEMENTs; the true count is 1. `status.check()` decorates a verdict
with a reason string (`"RED (last run failed)"`), so naive equality against the stored token
fails. 12 false positives would have made the checker disbelieved on day one. It self-caught
and reported it — the correct behaviour.

**6. Existence is not identity, confirmed live again.** `src/RimMandrake/Pits` passes
`os.path.isdir` while holding only `__pycache__`. Test for `About/About.xml`. This is already
in CLAUDE.md and it still bit twice this window.

**7. The bridge cannot tell two BENCH windows apart.** `handoff.py` REFUSED to write because
"BRIDGE still held by BENCH" — but that hold is the *Desktop* window's live Pyrelands session,
not this laptop's, and both sign as `BENCH`. ⛔ **Do not release it to satisfy the gate** — that
would break a live game. `--force` records it as open, which is the correct exit.

**8. Two of my own claims needed retracting to him, and both were caught only because they were
marked UNCERTAIN.** I called three pit bars "duplicates" of approved canal bars when each pit
version is broader or stronger (merging would have quietly strengthened something he'd already
validated), and I inferred from the Quarry screenshot that `pit_occupant_below_floor` "may need
no custom pawn draw" — he then ruled that there IS one. **Marking an inference UNCERTAIN is what
made both survivable.** Never launder a screenshot read into a measurement.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (4) — the next seat's queue

- `BARBSLINGER_SCORPION_REDESIGN_1` — Barbslinger redesigned: yellowish large scorpion-like creature, bulbous domed body, TWO independent tails each carrying an unusually large javelin-lik
- `DETERMINISTIC_CHECKER_WAVE_1` — walklint + modcheck doctor + bar-scoped north-star hash — C1/C2/C3 of the determinism assessment (owner picked 1+2+3, 2026-09-17)
- `PIT_SUPERDEEP_COLLAPSE_1` — Collapse the pit onto the D/F primitive: a superdeep cell you cannot climb out of, a room for prisoner storage, a ladder that works like a prison door
- `FLOWWORKS_DOOR_FAMILY_1` — Sluice and SecurityGrateDoor as STUFFABLE doors — cheap sluice passes liquid and holds small creatures, grate door passes liquid and holds a real pris

## Commits

```
fbea87682 rimflow: sync ledger/queue views
4b622e11b Ledger: note wave progress on DIRTY_CODE_REVIEW_STANDING_LOOP_1
81325f011 Oracle: validate the fallback letter too, not just the live reply
848a54cc1 Code review wave: mark 6 files clean, zero findings
616570761 All ten of the spec's open questions ruled — and the depth answer raises the bar
4037168ab Ledger: 3 FOUNDRY items closed/dropped this wave
3b446a8e2 set_current_map: hide the world layer too
d2256aea5 RM_Graffiti_WarningGlyph: replace both ISO hazard sprites with in-universe glyphs
285fd7552 Ledger: note FlowWorks code-review wave on DIRTY_CODE_REVIEW_STANDING_LOOP_1
173022c4c Mark 28 FlowWorks C# files CLEAN after full-file review
b32878458 Add a sanctioned emergency repair path for a torn ledger line
10bf37afc FlowWorks: fix ReportCell debug action's missing off-map bounds check
1a5f5b3ed Pyrelands: choked with grass (owner ruling, live walk 2026-09-17)
bb0872341 Sweep the closed NAMING_SCHEME_EXECUTION_1 rename gate out of 10 design drafts
f84421661 Ledger: repair unresolved git-stash conflict markers from d2414508e
d269fbf1b jawa/set_current_map: the Game.CurrentMap setter the bridge never exposed
d2414508e Four more pit rulings, and a door family commissioned out of one of them
d5ad5e05d rimflow: note wave progress on DIRTY_CODE_REVIEW_STANDING_LOOP_1
ab8f9df9a Mark 7 files CLEAN after full-file review (Armoury absorption generators, Oracle client, StarWarsRaces head types)
0afdb147c gen_kotorweapons_absorption.py: fix bare-defName collision false-positives
d5f35b021 rimflow: block BAZAAR_BROKER_TAB_1 on the same open Bazaar dependency chain
ac50a6526 rimflow: block BAZAAR_BANTER_LINES_1 on the same open Bazaar dependency chain
bbb4a697c rimflow: block BAZAAR_HAGGLE_DUEL_1 on open price-engine dependency
50f5d56f0 Greentide: rebuild assembly for the BaseWorkAmount cache fix
f2ec05625 rimflow: note wave progress on DIRTY_CODE_REVIEW_STANDING_LOOP_1
3bbfd88fd Mark 5 files CLEAN after full-file review (Greentide dig-out-buried, ProximityHatch props, RustCathedralHum attitude system)
a136c3b7e Greentide: freeze BaseWorkAmount at job start instead of recomputing live
e48443a16 Seven RUT biomes: generatesNaturally=false — they were breaking ALL worldgen
34f395caf FOUNDRY afk wave: block LANDMARK_NAMING_PASS_1, NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1, TILEGEN_SILENT_REUSE_1
6e52b2b3b rimflow: close WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1
6cdf52b39 WreckedMachines: remove the donor Automated Smelter from the build menu
080e6f87f rimflow: close FLOWWORKS_MECHANICS_TABLE_STALE_1
5c11150e3 flowworks_mod_definition.md: correct section 4's mechanics table against real source
863ae4aa0 rimflow: close AFTERMATH_DEAD_LETTERS_1 and AFTERMATH_TELEGRAPH_REFERENT_1
ed8398f9d Aftermath: wire the baseline letterLabel/letterText, fix the AlliesArrive telegraph referent
eefafc7c1 rimflow: note DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave
1cdc095a3 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave: mark 14 files clean, zero findings
0aa131589 rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave (13 files)
bc08f013b mark-clean: 13 files reviewed in DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave
c1ae25eaa DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave: fix misleading ConfigError in EnvironmentalHazards
735ecd850 rimflow: close FLAMEFANG_SNAKE_REBIRTH_1; block two more stuck items
0306dc1c8 rimflow: reassign the three held Pyrelands items to BENCH
239a59567 rimflow: PYRELANDS_GRASS_SATURATION_1 -- Bush/PincushionCactus ruling recorded
47aabd98c Pyrelands: evict Plant_Bush and Plant_PincushionCactus from wildPlants
ebde5ad1c BAZAAR_WINDOW_GRID_1: The Bazaar mod skeleton, slice 1 (plugin defs only)
5fad77171 rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave
7d87d8d3c Mark 4 files CLEAN (dirty-code-review wave): handoff.py, EnvironmentalHazards mod C#+csproj, mapgen_paint.py
2d48e8c5d handoff.py: bridge-holder gate used substring match, false-positive on a seat whose name is contained in another's
7dc279764 DEBUG_ACTION_ENUM_CRASH_1: add jawa/debug_action_yielders, per-yielder try/catch
0238b1f69 Four rulings on the pit spec: fluid per body, LAW 2 gets an exception
8ae4fa67b rimflow: LiquidDef registry first slice; block two dependent liquids items
bf3d6744a Mark art_checks.py, art_legibility.py, build_pyrelands_art_sheet.py, gm_blackboard_shadow.py CLEAN
69e7933af Code review: fix double-counted Cathedral Regard delta and a rung-skip in the conduct-posture stage machine; art_checks stops misdiagnosing a blank sprite as clipped
30880dca5 FlowWorks: LiquidDef registry skeleton (LIQUID_REGISTRY_CORE_1, first slice)
63f2e5623 rimflow: Pyrelands XML sweep — genstep NRE correlated, grass item noted
decc20622 rimflow: close PYRELANDS_MAPGEN_SCRUB_1, DOING_SEDIMENT_RECLAIM_1; block MODCHECK_DONOR_ENVIRONMENTS_1
baa2a0fb6 Merge remote-tracking branch 'origin/main'
e038d3f4e Pyrelands: correct the stale wildPlants comment (PYRELANDS_GRASS_SATURATION_1)
9c714b69f Spec the pit-superdeep collapse — and three things the ruling could not see
4117ae00b ARTPIPE_FAILED_REQUEUE_1: drop 27 gemini-banned failed jobs (lockjaw_improve_*, mantrap_improve_*)
0dd3ab9c3 Ledger sync: FOUNDRY dirty-code-review wave note (EnvironmentalHazards batch)
b8cd4cecc Mark 8 EnvironmentalHazards Fever-Wood-spike files CLEAN (dirty-code-review wave)
d3aa7fb5d Three eye-level souths wired (owner "Yes", 2026-09-17)
ff88071af Mark 22 files CLEAN (dirty-code-review wave)
cf2657ae8 Ledger sync: three eye-level souths delivered, awaiting owner verdicts
d79860270 DEPLOY_HOLD: hold Absorbed_OPTurret.xml, donor rpgwanderer.opturret still active
f5e25eeaa AA_FireWasp south: eye-level front portrait candidate (PYRELANDS_SOUTH_TOPDOWN_REGEN_1)
9613cfe3b Merge remote-tracking branch 'origin/main'
9b8ccfdac rimflow: block 3 more Rust Cathedral arc items on their shared foundation gate
a4debf028 Lesson: a backgrounded agent dies at 600s of silence, losing the whole run
81246e666 FurnaceBeast south: eye-level front portrait candidate (PYRELANDS_SOUTH_TOPDOWN_REGEN_1)
bc1fe302b rimflow: advance 3 more stuck items (belt-mode sweep)
9b63a43cc rimflow: FISH_BESTIARY_COMMISSION_1 correctly needs owner, not offline
7b9012ac9 rimflow: re-block MOVING_DUNES_BUILD_1 on the load-round shader gate
d6954229f rimflow ledger: recover + replay events lost to a git-stash mishap
92c5243f9 Mark-clean wave: 6 Utils files (migrate_names, selftest_art_checks, selftest_pit_logic, run_selftests, statusline, modset_builder)
66fbc9bbc modset_builder: stop hardcoding "down from 568" for the full mod count
dfbfa3a5c GR_Mantistanis south: eye-level front portrait candidate (PYRELANDS_SOUTH_TOPDOWN_REGEN_1)
f2926bfeb Merge remote-tracking branch 'origin/main'
aabb71efe the_forge.md §8's TIBANNA_EMBARGO_PLOT_1 pointer now lands on the real spec
5bff71c14 The pit's art was already ruled, and Quarry proves the collapse can look right
7f169188b FireHawk south: symmetric portrait wired (owner "Yes! Go", 2026-09-17)
23a3e4832 chore(sync): laptop 2026-09-17T12:14:54-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
756196f2a A pit is a superdeep cell, not a building — his ruling, in full
91ea31041 chore(sync): laptop 2026-09-17T11:03:08-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
8396e0c64 Ledger sync: symmetric south validated, awaiting owner verdict
d6e591819 FireHawk south: symmetric-wings portrait, split into body+wingL+wingR layers
fa27e1cab modcheck doctor: the five registries must agree, and the summary stops lying
d004443e4 Barbslinger scorpion v1 wired (owner approved 2026-09-17)
d029ade7d FlowWorks and WreckedMachines: false text out, re-validated on his word
67b6214ad Ledger: file DETERMINISTIC_CHECKER_WAVE_1, drop NORTHSTAR_HASH_SCOPE_1
5a0935a14 Bar-scoped hashing is declined, not deferred — and §6a survives it
2b8dbd314 walklint: 25 walk steps assert the absence of an id that cannot exist
917c1722c Ledger sync: wingsplit validation verdict + review sheets
1ff8b8f7f FireHawk wing-split art for FIREHAWK_FLIGHT_BEHAVIOR_1
4447ba4f6 validate refuses a zero-bar section — his re-validation path is now the gate
3a1b7072f Barbslinger scorpion redesign: fresh 3-facing candidate set
ddfeecc4f Ledger sync: Pyrelands art rulings + top-down-south regen item
```

## Game / bridge / tree state at wrap

- <could not run /Users/mandrake/dev/RimMaster/game: [Errno 13] Permission denied: '/Users/mandrake/dev/RimMaster/game'>
- Bridge: for     Interactive Pyrelands finalization with owner: minimal-list load, biome+animal grid screenshots, xenotype naked checkout grid

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
```

