# 07 — rimflow, RimPulse, review sheets, modcheck, queue state (2026-10-11)

## 1. Queue health

All numbers MEASURED 2026-10-11 ~08:50 PDT by a python replay of the bench clone's ledger
(`rimflow.model.read()` + `model.replay()`; script in this window's scratchpad, 43 s per replay).
⚠️ The bench clone may be behind origin (lesson `infrastructure/state/lessons/20261011T052223Z-FOUNDRY-reconcile-sweep-use-fresh-clone.md`);
the decay list below must be re-checked in a fresh origin clone before anyone acts on it.

**Ledger:** 18,573 events in 3 shards (`infrastructure/state/ledger/events/{BENCH,FOUNDRY,OWNER}.jsonl`); 2,933 items ever.

| state | items |
|---|---|
| done | 2,063 |
| dropped | 111 |
| superseded | 76 |
| **open: proposed** | 196 |
| **open: ready** | 13 |
| **open: doing** | 101 |
| **open: built** (implemented, owes live levels) | 235 |
| **open: validated** | 138 |
| **open total** | **683** (93 of them blocked) |

- Open by owner: FOUNDRY 591, BENCH 86, OWNER 6. Open by `needs`: bridge 420, offline 173, owner 63, deploy 15, game-up 12.
- 🔴 **The queue is an acceptance backlog, not a work backlog.** 373 of 683 open items are `built`/`validated` and only owe
  live levels: next owed level L2 238, L1 54, GREEN-MIN 54, L3 10, L4 12, GREEN-FULL 5. 420 open items need the bridge.
  Throughput is bridge-bound (same conclusion as `FOUNDRY_REBOOT_HANDOFF_202610040745.md`: "required checks proven = 28 of 1690").
- **Inflow beats outflow ~2:1.** Last 14 days: 1,155 `file` vs 527 `close` + 24 `drop` + 13 `supersede` events.
- **Age** (days since the item's last ledger event): 601 open items < 7 d, 43 at 1-2 weeks, 21 at 2-3, 14 at 3-4, 4 at 4+.
  **39 open items have had no event in 14+ days; 82 in 7+.** All 235 built and 138 validated items are < 7 d (they are new since the
  2026-10-07 redesign). 55 proposed items are 7+ d old, 17 are 14+.
- **`doing` with no live lease: 89 of 101** (`lease_status` None; 9 released, 3 lapsed). 25 of them have been silent 7+ days — legacy
  `start` (no lease) left these looking in flight forever. `rimflow reclaim` exists but only for your own items.
- **Blocked forever-ish:** 93 blocked; 61 have no `blocked_on` (only a prose reason, so nothing can auto-unblock them); 20 have been
  blocked 14+ days.
- 🔴 **Blocked on a gate that has already closed — 6 items** (`blocked_on` points at a terminal item):
  `ASSIGNMENT_SHEETS_VERDICT_SITTING_1`→`BIOME_KITS_PUSH_TO_TEST_1` (done, 21.8 d), `DESIGN_MATERIALS_REVIEW_1`→`BAROQUE_BEDAZZLE_PROGRAM_1` (done, 11.6 d),
  `SALVATION_RITES_UNIFICATION_1`→`BIOME_MOD_UNIFICATION_1` (done), `BIOME_DEFNAME_MIGRATION_WAVE_1`→`LANTERNDEEPS_TIER_COLLISION_1` (done),
  `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1`→`FALL_LINE_ARRIVAL_MECHANISM_1` (done), `HOSTILE_MOBILE_PLANTS_1`→`REACTION_MECHANISM_GENERALISE_1` (done).
  A further 13 blocked items name a closed item in their block REASON text (e.g. `HORRORS_RAIDING_FACTION_1` holds on `HORRORWASTES_BIOME_DISSOLVE_1`,
  done, 28.6 d; `FLOOD_WITNESS_EVENT_1` cites `FLOOD_CANYON_BIOME_1`, done; `MOD_VALIDATION_RETROFIT_1` cites `MOD_VALIDATION_PIT_PILOT_1`, done).
  The tool does not auto-unblock when `blocked_on` closes — this is the CLAUDE.md "a gate cited by NAME outlives the item it names" trap, mechanised.
- **Prose citing closed items as gates:** 66 open items (86 lines) have a gate-ish line (gate/blocked/after/until/depends/before…) naming a
  done/dropped/superseded item. Heuristic, needs a human read per line; list in scratch `gatecites.json` (regenerable by the census script).
- **Prose coverage:** 468 live `items/*.md` files vs 683 open items → **216 open items have no prose file** (e.g. `ANT_HIVE_REAL_GEOMETRY_1`,
  `ART_SUBJECT_RESOLVER_1`, `BRIDGE_STALL_DIAGNOSTIC_1`). One orphan file: `infrastructure/state/items/LANDMARK_NAMING_PASS_1.names` (not .md; DELETE or move into the item's .md).
  0 closed-folder files whose item is still open.
- **Duplicates:** title similarity > 0.8 finds 246 pairs, but almost all are deliberate template families (`*_FIRST_SCRIPT_1` ×~25,
  `{GREYSEA,TWILIGHTSEA,PROPANELAKE}_FLOOR_PASS_1`). One id-stem family: `DEEPS_FAUNA_MECHANICS_1` / `_2`. **No real duplicate found by title;
  UNMEASURED by meaning.**
- **Ledger integrity:** replay errors already in the file: 7 (double drop/close/supersede, one double `file` of `FLOWWORKS_BUILD_PROGRAM_1`,
  one cross-seat `start` refused). 19 contested claims (two windows claiming one item; `COLD_LOAD_RUN_SHEET_4` ×3, `COMMISSION_LEDGER_CLEANUP_1` ×3).
  Harmless (first record wins) but they are noise in every replay.
- `ownerSaid` events: 1,459 — the owner-quote provenance is heavily used.

### Proposed decay sweep (NOT executed — re-check each in a fresh origin clone first)

| # | item(s) | proposed action | why | risk if wrong |
|---|---|---|---|---|
| D1 | the 6 `blocked_on`-closed items above | `rimflow unblock` (or re-block on the real successor) | gate already closed | item starts before a real prerequisite; low, the reason text is kept |
| D2 | `HORRORS_RAIDING_FACTION_1`, `FLOOD_WITNESS_EVENT_1`, `MOD_VALIDATION_RETROFIT_1`, `FAUNA_LORE_DIVERSIFICATION_1`, `MACRO_GENERATOR_V0_1`, `BAZAAR_BROKER_TAB_1` | re-read the block reason; unblock or re-point | reason names a closed gate | same as D1 |
| D3 | 25 `doing` items silent 7+ d with no lease (`ASSAILANT_DUNGEON_BUILD_1`, `CATHEDRAL_*` ×3, `BAZAAR_HAGGLE_DUEL_1`/`BANTER_LINES_1`/`BROKER_TAB_1`, `COLD_LOAD_RUN_SHEET_4`, `DESERT_WRAPS_ART_COMMISSION_1`, `BIOME_ENRICHMENT_DESERT_WASTELAND_1`, `EXPLOSIVE_PLANT_GROWTH_1`, `TWILIGHT_BOTTOM_CAST_1`, `DUNGEON_SETPIECE_TEXT_1`, `JOSSUR_FLIGHT_FRAMES_1`, `SUBSTRUCTURE_PROPS_LAYER_OOB_1`, `GELATINOUSSLIME_KIT_ART_1`, `MIASMA_WARDEN_MOTHER_ART_1`, …) | `reclaim` to ready (owning seat) | they read as in flight, so `next` never offers them | an agent really is mid-work: none has a lease, so none is provably alive |
| D4 | proposed 14+ d design-parking items: `NORTH_STAR_ATMOSPHERIC_TBD_1`, `WORLD_REMAKE_FINAL_STEP_1`, `ECOSYSTEM_PYRAMID_LAW_1`, `BIOME_SPECIFIC_FAUNA_LAW_1`, `BAZAAR_STOLEN_GOODS_PROPERTY_1`, `INDIGENOUS_TECH_REVISIT_1`, `BIOME_NUISANCE_NORMALIZATION_1`, `WEBWORK_TERRAIN_WEATHER_PASS_1`, `SCALD_*` ×2, `SUMP_INHABITED_NOTES_1`, `WEBWORK_EGG_WEAPON_VERSION_1` | KEEP but set `needs owner` + one-line card text, or drop | parked design; `BIOME_SPECIFIC_FAUNA_LAW_1` is per CLAUDE.md "input to per-biome sittings, not a work queue" → **drop/supersede** | dropping a parked design the owner still wants; keep `WORLD_REMAKE_FINAL_STEP_1` (owner ruling: world remake is the last step) |
| D5 | `REBOOT_BREAKGLASS_VERIFY_1` | KEEP, `needs owner` | genuinely his reboot + phone | none |
| D6 | 216 open items without prose | no action en masse; `rimflow lint` should list them | the `claim` path refuses missing prose, so they silently never get offered | — |
| D7 | `LANDMARK_NAMING_PASS_1.names` | MOVE into the item .md or `design/` | the `items/*.md` glob is "the live set"; a stray suffix is noise | the names list is input to a tool — check importers first |
| D8 | 6 OWNER-owned open items | card them in one batch | owner items never move without him | — |
## 2. Friction log (process tooling)

Source: newest 60 files in `infrastructure/state/handoffs/` (by mtime) + all 299 `infrastructure/state/lessons/*`. A python pass
pulled every line naming a tool AND a friction word (refus/trap/stale/silently/by hand/…): 163 distinct lines, read by hand.
"Files" = distinct handoff/lesson files reporting it. Ranked by recurrence × cost.

| rank | friction | files | evidence (examples) | what agents do by hand | fix class |
|---|---|---|---|---|---|
| 1 | **`--owner-said` forged-quote guard refuses genuine owner words** — mid-turn messages, card free-text, session-opening message under the /clear caveat, quotes with apostrophes/ellipses/curly quotes, subagent sessions; and its regex fires on the flag's spelling inside unrelated prose, killing the whole compound command | **11** | lessons `20260924T182022Z-BENCH-…block-forged`, `20260924T204345Z-…`, `20260926T041457Z-…ship-only-dive`, `20260928T154936Z-…forged-quote-guard`, `20260929T062905Z-…`, `20261004T205753Z-…`, `20261010T104517Z-…rimflow-owner-quote-fl`; handoffs `BENCH_HANDOFF_202610101044.md`, `BENCH_REBOOT_HANDOFF_202610042057.md`, `FOUNDRY_REBOOT_HANDOFF_202610030327.md`, `BENCH_HANDOFF_202610071515.md` | drop the flag, record under own seat, paste quote into note text; ask him to re-type one sentence | tooling: let the guard read the CURRENT turn + queued mid-turn messages (the transcript jsonl has them), normalise quotes/whitespace, match only the flag token in argv, not prose. **Same 7 lessons say the same thing — MERGE into one lesson** |
| 2 | **Compound-command refusals by PreToolUse/pre-push ledger hooks** (judges HEAD before the command runs; ledger path after an `rm` path; registry filename in prose) | **8** | lessons `20261011T125553Z-FOUNDRY-pre-push-pretooluse-ledger-hook-judges.md`, `20261010T004445Z-BENCH-shared-bench-clone-pul…`, `20261010T205804Z-BENCH-pre-push-ledger-lint-h…`; handoffs `FOUNDRY_HANDOFF_202610111255.md`, `FOUNDRY_REBOOT_HANDOFF_202610040745.md`, `FOUNDRY_REBOOT_HANDOFF_202610012215.md`, `BENCH_REBOOT_HANDOFF_202610081345.md` | split into 3 separate Bash calls | already a CLAUDE.md Git rule; PROMOTE one canonical line into `using-rimflow` + GIT_WORKFLOW, DELETE the duplicate lessons |
| 3 | **Stale seat clone → stale rimflow view / unpushable ledger events** (queue renders from behind-origin ledger; `NOT_APPEND`; `handoff.py --wake` reads stale checkout; served sheets keep the clone dirty) | **7** | lessons `20261011T052223Z-FOUNDRY-reconcile-sweep-use-fresh-clone.md`, `…-stale-clone-ledger-e…`, `20261010T235838Z-BENCH-landing-commits-throug…`, `20261002T055400Z-BENCH-handoff-py-wake-run-st…`; handoff `FOUNDRY_HANDOFF_202610111255.md` (foundry clone 244 commits behind, replaced) | fresh scratch clones, `ledger_sync.py`, stash/pop recipes | tooling: `rimflow next/queue/show` should print "ledger N commits behind origin" (a `git rev-list --count HEAD..origin/main` after a cheap fetch) and refuse sweeps when behind |
| 4 | **`close --sha` / `implemented` sha traps** — silent HEAD fallback after a failed commit; rebase leaves dead sha; `implemented` refused unless on origin/main; helper reports "moved to closed/" wrong; `rimflow file` prints a refusal-looking tail on success | **6** | handoffs `FOUNDRY_REBOOT_HANDOFF_202610011154.md`, `FOUNDRY_HANDOFF_202610091641.md`, `FOUNDRY_REBOOT_HANDOFF_202610110224.md`; lessons `20261001T115528Z-FOUNDRY-rimflow-close-sha-si…`, `20260924T182022Z-BENCH-…git-commit` (closed/ prose never committed) | `rimflow show` after every verb; correct by `note` | tooling: `close` must refuse with no explicit `--sha` and verify `merge-base --is-ancestor`; `file` output fix; `close` should `git add` the moved prose |
| 5 | **Bridge lock** — 45-min staleness kills a helper's long live session; cross-clone race (both seats held it 10:47/10:48Z); lock names a live PID whose game is gone; `./game` state stale | **6** | `FOUNDRY_REBOOT_HANDOFF_202610071234.md` (`BRIDGE_LOCK_CROSS_CLONE_RACE_1`), `FOUNDRY_HANDOFF_202610080208.md`, `FOUNDRY_REBOOT_HANDOFF_202610110224.md` (`BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID`: "model.bridge_gate does not check the new lock yet"), lesson `20261007T220228Z-FOUNDRY-bridge-hold-stale-45…` | keep-alive events; measure bare `./game` | in flight (`BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID` built, not wired) — finish wiring `bridge_gate` |
| 6 | **Sheet lifecycle silent failures** — rebuilt sheet re-letters columns → 28 spurious rejected events (no retract verb); legacy pre-snapshot decisions refused by enact (229 rows stranded); followed notes re-filed; `serve_gated.py` refuses non-biome sheets; enact refuses conflict sheets ("snapshot missing"); 5 silent enact failure classes; selftest_enact wrote into the real repo | **6** | lessons `20261009T130028Z-BENCH-sheet-rebuilt-after-ow…`, `20261010T004445Z-BENCH-legacy-pre-2026-10-04-…`, `20261009T054044Z-BENCH-followed-sheet-notes-m…`, `20261010T104515Z-BENCH-enact-redo-job…`; handoffs `FOUNDRY_HANDOFF_202610091006.md`, `BENCH_REBOOT_HANDOFF_202610100440.md`, `BENCH_REBOOT_HANDOFF_202610102057.md`, `BENCH_REBOOT_HANDOFF_202610090437.md` | independent post-enact audits; hand-run `legacy_redo_triage.py`; fold `.map.json` back | mostly fixed (ab6bed31a, selftest_enact_ws.py); gap = **no single lifecycle doc** (§3) and no `retract` verb |
| 7 | **Seat/identity mismatches** — `--seat MACBENCH` refused; python.exe has no seat env without `RIMFLOW_SEAT`; `handoff.py` can't tell two BENCH windows apart; `live_session.py` refuses unless FOUNDRY holds the bridge | **5** | `MACBENCH_REBOOT_HANDOFF_202609240027.md`, lesson `20261007T220228Z-FOUNDRY-python-exe-needs-rim…`, `20261002T230900Z-BENCH-northstar-driver-live-…`, CLAUDE.md handoff.py bullet | reassign to FOUNDRY; sign as BENCH and name self in text | tooling: python.exe wrapper exports `RIMFLOW_SEAT` |
| 8 | **Cross-seat / OWNER-owned item refusals** — `unblock`, `claim`, `reassign` refuse other seats' or OWNER items; 5 FOUNDRY items carried a stale owner block BENCH could not lift; "13 items said blocked on owner after he had already ruled" | **4** | `BENCH_REBOOT_HANDOFF_202610100440.md`, `BENCH_REBOOT_HANDOFF_202610030757.md`, `FOUNDRY_REBOOT_HANDOFF_202610030327.md` | leave notes for the other seat | policy conflict: CLAUDE.md "Correctness outranks seat ownership" says fix on sight; the CLI refuses `unblock` cross-seat. Let `unblock` be cross-seat with `--reason` (as `close` already is) |
| 9 | **modcheck instrument truthfulness** — zero-bar walks exit 0; `cannot show` polarity; mod_hash covered non-shipping files → STALE; Windows python could not lock status file → runs silently never recorded; `selftest_watch.py` dirtied tracked fixtures | **5** | lessons `20260917T051009Z-…north-star-walk-who`, `20260916T114419Z-…modcheck-checklist`, `20261011T052223Z-FOUNDRY-selftest-watch-dirti…`; handoffs `FOUNDRY_HANDOFF_202610061232.md`, `FOUNDRY_HANDOFF_202610061623.md` | — | all fixed; KEEP lessons as history only if a skill cites them, else DELETE (git is provenance) |
| 10 | **Health publisher re-dirties tracked artifacts on every rimflow call** (blocks `pull --rebase`); post-commit hook fires per replayed commit mid-rebase | 2 | `MACBENCH_REBOOT_HANDOFF_202609240027.md`, lesson `20260924T040800Z-FOUNDRY-codebase-health-publ…` | commit them first | re-check: if still true, move those artifacts out of git (like queue views were, 2026-10-02) |
| 11 | `--to` / `reassign` counts as a claim / `retarget` quirks | 4 | `BENCH_REBOOT_HANDOFF_202610022308.md`, `FOUNDRY_REBOOT_HANDOFF_202610030327.md`, memory `rimflow-cli-quirks.md` | — | low; document in skill |
| 12 | Name grammar refusals (`SUBJECT_INTENT_TWIST`, length cap) | 2 | `FOUNDRY_HANDOFF_202610040201.md`, lesson `20261004T064814Z-…` | `rimflow namecheck` first | low recurrence since `namecheck` exists — KEEP |

**Not a complaint but a cost:** a full ledger replay takes ~43 s CPU in python (measured, this audit). Every `rimflow` verb that
replays pays it unless cached; 2 handoffs mention rimflow slowness. UNMEASURED whether the CLI caches the replay.
## 3. Docs and skills

| system | doc(s) today | skill(s) today | verdict |
|---|---|---|---|
| **rimflow** | `design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md`, `design/RimMandrake/rimflow_validation_levels_addendum_2026-10-07.md`, `design/RimMandrake/rimflow_gpt_review_2026-10-07.md`, `infrastructure/agents/CHARTER.md` (implemented/lease/reconcile mentions), `rimflow --help` | `skills/using-rimflow/SKILL.md` (261 lines) | **skill is behind the 2026-10-07 redesign**: 0 mentions of `renew`, `built`, `land.sh`, `publish`; 1 of `implemented`, `validated`, `reconcile` is absent (measured by grep -c on the 261-line file). The redesign lives only in two dated design docs. |
| **RimPulse** | only the module docstring in `src/RimMandrake/Utils/pulse/pulse.py` (lines 1-27) | none (1 passing mention in `using-rimflow` line 244) | **no doc, no skill.** Agents learn `pulse.py hand` from handoffs. Not mentioned in CHARTER/BENCH/FOUNDRY.md (0 hits). |
| **review-sheet lifecycle** (build → serve_gated → owner clicks → refresh/remap → enact → audit → clear notes) | `design/RimMandrake/art_ledger_design_2026-10-04.md` (only doc naming `serve_gated`/`art.py enact`), `art_review_facts_spec.md` | `~/.claude/skills/review-sheets` (474 lines, generic, cross-project, 0 mentions of serve_gated/enact/remap), `skills/scaled-game-image-review` (130 lines; names serve_gated 1×, refresh_sheets 3×, scaled_review_gate 3×; 0× `art.py enact`, `remap_decisions`, `nonart_sheet`) | **split across 3 places, and the most failure-prone step (enact + post-enact audit + note clearing + stale-letter guard) is in none of the skills.** Art review is PAUSED (owner 2026-10-10), so this is a cheap moment to consolidate. |
| **modcheck** | `design/RimMandrake/debug_process.md`, many northstar docs, `modcheck --help` | none dedicated (`rimworld-debug-testing` touches it) | adequate via debug_process.md; candidate for a `modcheck` section in `rimworld-debug-testing` rather than a new skill |

**Proposals**

| target | action | why | risk |
|---|---|---|---|
| `skills/using-rimflow/SKILL.md` | **REWRITE (curation pass)** around the 2026-10-07 states: proposed→ready→doing(lease, renew 10 min, lapses 45)→`implemented --sha` (on origin/main)→built→validated→done; `reconcile`, `reclaim`, `why`; landing via `./publish`/`land.sh`; friction ranks 1-4, 7, 8, 11 above as a "refusals and their exits" table | the skill teaches a pre-lease model | low; content exists in the two 10-07 design docs |
| `design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md` + `…validation_levels_addendum…` | MERGE into one undated `design/RimMandrake/rimflow.md` (spec), skill points to it | dated filenames read as history; agents can't tell which is current | low |
| new `skills/review-sheets-rimmandrake/` (or fold into `scaled-game-image-review`) | **CREATE** the project lifecycle: build (`art_sheet.py`/`nonart_sheet.py`) → `scaled_review_gate.py` → `serve_gated.py` → owner → `refresh_sheets.py`/`remap_decisions.py` (when columns re-letter) → `art.py enact` preview/`--apply` → fresh-agent audit → followed-notes cleared; the 6 sheet lessons become its traps section | 6 recurring failures, no single doc | medium: must not duplicate the global `review-sheets` (generic HTML/UX) — layer on top and link |
| `skills/scaled-game-image-review` | MERGE into the above if the new skill is made (its 130 lines are the art-specific half) | one skill per lifecycle | low |
| RimPulse | **CREATE** `src/RimMandrake/Utils/pulse/README.md` (CLI, state dir `~/.local/state/rm-dashboard/`, HTTP API `/api/now` `/api/stream` `/api/thumb` `/api/ack` `/api/seen` `/api/probe` `/api/metric`, systemd units, `hand` contract) + one line in CHARTER: "hand the owner anything to look at with `pulse.py hand`" | only a docstring today | none |
| `~/.claude/skills/review-sheets` | KEEP global; add one pointer line to the project skill | generic and cross-project already | none |
## 4. Code health

Sizes MEASURED by a python line count over `*.py` (excluding `__pycache__`):

| tool | .py files | selftests | LOC total | selftest LOC | largest |
|---|---|---|---|---|---|
| rimflow `src/RimMandrake/rimflow/` | 30 | 17 | 14,580 | 5,886 | `cli.py` 3,156 · `model.py` 2,391 · `render.py` 860 |
| RimPulse `src/RimMandrake/Utils/pulse/` | 4 (+ `widget/lantern.pyw` 526, `widget/index.html` 330) | 1 | 1,746 | 319 | `pulse_core.py` 822 · `pulse.py` 573 |
| sheets/art `src/RimMandrake/Utils/art/` | 63 | 25 | 18,636 | 3,807 | `art_sheet.py` 2,904 · `enact.py` 1,762 · `artledger.py` 995 |
| modcheck `src/RimMandrake/Utils/modcheck/` | 76 | 28 | 19,762 | 6,949 | `detectors.py` 1,053 · `runner.py` 765 · `suite.py` 730 |

**Selftests — RUN this audit:** `run_selftests.py --timings --only <the 71 selftests in these four dirs>` →
**PASS 71/71, FAIL 0, UNMEASURED 0, CRASH 0, SKIPPED 0, GREEN**, wall 181.8 s (6 workers).

- ⚠️ `src/RimMandrake/Utils/modcheck/selftest_deployed_floor.py` alone took **181.7 s** — the whole wall time — and ran in the
  default tier. Its name says "deployed"; if it reads the deployed Steam Mods tree it should carry `# selftest-tier: deployed`
  (run_selftests.py's own rule) so the default unit suite drops from ~3 min to ~1 min. Next slowest: `art/selftest_texture_gap_lint.py`
  57 s, `art/selftest_art.py` 32.5 s, `rimflow/selftest_lease.py` 20.8 s.
- Coverage gaps by eye: RimPulse has 1 selftest for 1,395 non-test LOC (covers `pulse_core` classifiers; the HTTP handler and
  `Collector` are untested). rimflow is well covered (selftest LOC = 40% of total).
- `cli.py` at 3,156 lines and `art_sheet.py` at 2,904 are the split candidates; not urgent while selftests are green.
- Ledger replay costs ~43 s CPU for 18,573 events (measured: census script `model.read()`+`replay()`). Growth is ~1,100 events/day
  (14-day verb counts sum to ~6,100 → ~430/day; UNMEASURED precisely). A replay cache keyed on shard byte-lengths would make every
  read verb O(new events). Check whether `cli.py` already caches before filing.

**Dead-file candidates** — a single-pass regex of every non-selftest module name in these four dirs over 6,819 tracked
text files (Transient excluded) + `~/.local/bin` + user systemd units; sanity probe: `model` 689 referencing files, `enact` 40.
No rimflow, pulse or modcheck module is unreferenced. Seven art modules have no referrer outside selftests:

| path | lines | last commit | verdict |
|---|---|---|---|
| `src/RimMandrake/Utils/art/migration_proof.py` | 173 | 2026-10-10 | one-shot proof of the schema-2 migration — DELETE after confirming the migration closed (git is provenance) |
| `src/RimMandrake/Utils/art/placeholder_jobs.py` | 166 | 2026-10-05 | one-shot Grey Sea placeholder job builder; superseded by `art.py enact` — DELETE candidate |
| `src/RimMandrake/Utils/art/sheet_own_renders.py` | 139 | 2026-10-09 | one-shot "keep own render?" sheet; hard-codes a dated output — DELETE once that sheet is enacted |
| `src/RimMandrake/Utils/art/tint_candidates.py` | 91 | 2026-10-05 | one-shot tint variants for 3 creatures — DELETE candidate |
| `src/RimMandrake/Utils/art/remap_decisions.py` | 96 | 2026-10-06 | **KEEP** — reusable, named in the brief as sheet machinery; it just has no doc. Fold into the sheet-lifecycle skill |
| `src/RimMandrake/Utils/art/move_mod_textures.py` | 67 | 2026-10-05 | **KEEP** — the only safe way to rename a mod's Textures through the art ledger; document it in `rimworld-deploy` or the sheet skill |
| `src/RimMandrake/Utils/art/sheet_js_harness.py` | — | — | KEEP — test helper imported by 3 selftests |

Per CLAUDE.md "Don't delete on a grep alone — verify, then file it": the 4 DELETE candidates should be filed as one item, not deleted here.
## 5. RimPulse as the telemetry front-end (interfaces only; telemetry design belongs to another auditor)

**What RimPulse is today (measured):** `rm-pulse.service` active (systemd --user), collector every 5 s, HTTP/SSE on
`127.0.0.1:8765`, state in `~/.local/state/rm-dashboard/`. Live `/api/now` answered during this audit.

| interface | shape | telemetry use |
|---|---|---|
| **Sources** (`Collector`, `pulse.py` ~l.140-170) | `sessions`, `subagents`, `kernel` (OOM), `memwatch` (`~/.local/state/rm-memwatch/events.jsonl`), `ledger` (both clones), `artpipe`, `hands`, `sheets`, `bridge`, `probe`; each reports `{ok, at, ms}` in `pulse_now.json["sources"]` | a telemetry source = one more `src(name, fn)` entry. Pattern already handles failure per source |
| **Event log** `pulse.jsonl` | 2,112 rows, one schema `{key, kind, ts, was}` — state transitions of widget rows (done 830, run 349, look 270, idle 223, review 201, amber 134, red 14…) | already a transition time-series; not a metrics series (no numeric value field) |
| **Metric log** `metrics.jsonl` | 527 rows, `m` ∈ alarm_open/alarm_close (with `age_s`), toast, digest, session_ended_clean | the seed of SLO metrics (time-to-notice); `pulse.py metrics` summarises |
| **Ingest endpoints** | `POST /api/metric {m,…}`, `POST /api/probe {rimworld_running}` (Windows widget posts it) | the natural write path for game/bridge/disk telemetry from python.exe or the game side — no new server needed |
| **Read endpoints** | `GET /api/now` (snapshot), `GET /api/stream` (SSE), `GET /api/thumb` | a chart pane in the widget can subscribe to SSE |
| **Ledger read** | `pulse_core.read_ledger(CLONES)` reads both seat clones | ⚠️ inherits friction #3: a stale seat clone shows a stale queue. Should read origin (or the D:\ mirror) |
| **Sheets read** | `SHEETS_DIRS = <clone>/Transient/biome_ffar` only | lesson `20261011T060426Z-BENCH-rimpulse-lists-review-sheets-only-from.md` — non-biome sheets are invisible |

**Recommended contract for the telemetry designer (proposal, not design):**
1. Telemetry writers append numeric samples to their OWN jsonl (`{ts, metric, value, unit, tags}`) — game TPS (`BRIDGE_TPS_REGULAR_REPORT_1` already
   records it), disk free per mount, WSL memory, ledger replay ms, selftest wall, artpipe queue depth. RimPulse reads them as one more
   source and computes red/amber thresholds; it never becomes the store of record (its state dir is per-machine, unversioned).
2. Thresholds map onto RimPulse's existing kinds (`red`/`amber`/`warn`) so alarms reuse `ack`, `alarm_open/close` time-to-notice and the
   phone hook (`PHONE_PUSH_ENABLED=False`, owner has not ruled — see Questions).
3. Add a `/api/series?metric=&since=` read so the widget (or a published page) can draw sparklines; keep the collector cadence at 5 s
   and let writers choose their own sample rate.
4. Give pulse its own selftest for the HTTP handler before adding endpoints (today: 0 tests on `make_handler`).
## Top 10 actions, ranked by value

| # | target path | action | why (one line) | risk if wrong |
|---|---|---|---|---|
| 1 | `.claude/hooks/block_forged_owner_said.py` (+ rimflow `--owner-said`) | tooling fix (file an item): read current-turn + mid-turn messages, normalise quotes/whitespace, match the flag only in argv | #1 friction, 11 files, every owner ruling captured mid-turn loses its provenance flag | guard weakens → forged quotes; keep refusal on any non-owner text |
| 2 | `skills/using-rimflow/SKILL.md` | REWRITE in a curation pass for the 2026-10-07 lease/built/validated model + a "refusals and their exits" table (friction 1-4, 7, 8, 11) | skill teaches the pre-lease model (0 × renew/built) | low |
| 3 | 6 blocked items whose `blocked_on` is closed + 13 whose reason cites a closed gate (§1 D1/D2) | `rimflow unblock` after a fresh-clone re-check; file a tooling item: `close` of X prints/auto-flags items blocked_on X | items frozen on gates that already lifted, up to 28.6 days | unblocking before a real successor gate |
| 4 | 25 lease-less `doing` items silent 7+ d (§1 D3) | `reclaim` by owning seat | invisible to `rimflow next`; inflate WIP | none provably alive |
| 5 | rimflow `next`/`queue`/`show` + `pulse_core.read_ledger` | print "ledger N commits behind origin" and refuse sweeps when behind | friction #3 (7 files) incl. RimPulse's own ledger read | an extra fetch per call; cache 60 s |
| 6 | new project sheet-lifecycle skill (merge `skills/scaled-game-image-review`) + document `remap_decisions.py`, `move_mod_textures.py` | CREATE / MERGE | 6 recurring sheet failures, no single doc; art is paused so it is cheap now | duplicating the global `review-sheets` skill — layer, don't copy |
| 7 | `src/RimMandrake/Utils/pulse/README.md` + one CHARTER line on `pulse.py hand` | CREATE | RimPulse has no doc and is about to become the telemetry front-end | none |
| 8 | `rimflow close` / `implemented` | refuse without explicit `--sha`, verify `merge-base --is-ancestor`, stage the moved `items/closed/` prose; fix `file`'s refusal-looking tail | friction #4 (6 files) | stricter close refuses a legit offline close — allow `--reason` |
| 9 | `src/RimMandrake/Utils/modcheck/selftest_deployed_floor.py` | tag `# selftest-tier: deployed` if it reads the deployed tree | 181.7 s of a 181.8 s run | a real unit check moves out of the default sweep |
| 10 | 7 duplicate owner-said lessons + 4 compound-hook lessons in `infrastructure/state/lessons/` | MERGE into one lesson each (keep the newest, delete the rest) | same trap recorded 11 times; lessons are read on demand, duplicates cost reads | losing a variant (e.g. card free-text vs mid-turn) — merge the variants into the one file |

Also (lower): `rimflow unblock` cross-seat with `--reason` (friction #8, conflicts with CLAUDE.md "Correctness outranks seat ownership");
file the 4 one-shot art scripts as a dead-file item; merge the two 2026-10-07 rimflow design docs into one undated spec; replay cache.

## Questions only the owner can answer

1. **The forged-quote guard refuses your genuine mid-turn and card free-text words (11 recorded times).** Which do you want?
   (a) widen it to read the current turn and mid-turn messages, still exact-match; (b) keep it strict and accept that those rulings
   are recorded as "in chat" without the flag; (c) drop the guard for rimflow notes and keep it only for art-ledger displacement.
2. **373 open items only owe a live check (L1/L2/GREEN).** Should agents (a) keep proving them one by one as bridge time allows,
   (b) batch-close items whose L0 passed and whose mod later went GREEN as a whole, or (c) drop the L2 requirement for content-only items?
3. **Lease-less `doing` items 7+ days old (25).** (a) reclaim them all to ready automatically after 7 days with no event, (b) list them
   for the owning seat each week, or (c) leave them.
4. **Phone push from RimPulse** (hook exists, off, "not decided by the owner yet" 2026-10-08): (a) reds only, (b) reds + questions waiting on you,
   (c) keep it off.
5. **Parked design items 14+ days old** (`ECOSYSTEM_PYRAMID_LAW_1`, `INDIGENOUS_TECH_REVISIT_1`, `BIOME_NUISANCE_NORMALIZATION_1`, …):
   (a) move them to a "someday" target (v2) so the v1 queue shows only live work, (b) drop them, or (c) keep them in v1.
