# BENCH_REBOOT_HANDOFF_202609210158 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609210000`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward


🔴 **Three of this session's wrong answers came from instruments that returned a
confident number, not from missing information.** Every one looked like a clean result:

- a `RSW_<donorName>` prefix test reported **105 species to author**, then 11, when the
  truth was **2** — because a port RENAMES the def, so a prefix can never find it;
- a `measure sql` query with the wrong column name (`defName` instead of `def_name`)
  returned an error LINE, and the script grepping for rows reported **0 of 109**;
- `ET.iterparse` with `el.clear()` on every element returned **71 features with all-None
  names**, which reads exactly like "the save holds no data".

🔑 **The general form: a count that is conveniently round, or alarmingly clean, is a query
bug until proven otherwise** — and the alarming direction is the one you will believe
without checking. Every one of these was caught by asking "could this number be the
instrument rather than the world?" and re-measuring a different way.


## What the owner should see


🔴 **`Transient/WHAT_NEEDS_THE_OWNER_2026-09-21.md`** is the ranked list — six decisions,
each with everything downstream already built. Sent to him. The two that matter most:

- **Two of his own rulings disagree about `RSW_MossBeetle`** — ruled CUT 2026-09-19, swept
  back in by the blanket desert "replace" ruling of 2026-09-20. One word settles it.
- **16 drafted creature names are shipping unreacted-to**
  (`Transient/drafted_creature_names_2026-09-21.md`). `NONCANON_BEAST_RENAME_1`'s design is
  "agent drafts, owner reacts" — a name nobody strikes becomes the real name by default.
  🔑 There are TWO layers and he may want to rule separately: the defName is English
  (`RSW_Stoneback`), the label a player reads is pseudo-SW (**bokka**).

⏸️ **The Fall Line is DONE and waiting only on his eye.** `maxDrawSizeInTiles` 10 → 26
(effective 15 → 42), verified by parsing the `.rws`, saved as
`ASHKARR_FALLLINE_LABEL26_2026-09-21`, canonical save byte-unchanged. Picture:
`D:\Luke\dev\Rimworld\Transient\fall_line\alt420.png`.
🔑 The wider finding is his call and is NOT that item: **all 71 world features sat at the
size curve's floor**, so the planet had no visual hierarchy at all. 70 still do.

🔴 **`OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1`** — `AshkarrFlora` and `GelatinousSlime` are
built AND deployed AND absent from `ModsConfig`. `RUT_Fuzz`, the **heaviest** row in the
AridShrubland table at 0.9, therefore never spawns. Third instance of this failure mode.
A mod-list change is his call, so nothing was edited.


## What is half-done, and where it stops


- `FALL_LINE_MAJOR_REGION_LABEL_1` — APPLIED, SAVED and photographed; `needs: owner`.
  NEXT: show him `D:\Luke\dev\Rimworld\Transient\fall_line\alt420.png` and close on his
  word. ⚠️ Nothing is owed technically — it is open only because he has not looked yet.
- `FOUNDERS_IMPORTER_OWED_1` — importer BUILT, selftest 28/28, runner 68/69; the live-test
  save `FOUNDER_IMPORTER_LIVETEST_2026-09-21.rws` is built and verified offline (all 6
  `Wimp` sourceGenes above the allocated base). NEXT: **load it and check all 6 founders
  carry `Wimp`** — one load, and it closes. Not done because the other window held the
  bridge.
- `BRIDGE_SELECT_NONCOLONIST_PAWN_1` — DLL deployed, all three tools confirmed in the LIVE
  tool list. NEXT: prove "does not refuse on faction" on the beastmechanics tier (~90 s
  quicktest, no cold load needed). That also closes `PORTED_BEAST_MECHANICS_REBUILD_1` 4–6.
- `TITANOSLIME_SLIME_BIOME_1` — built, compiles, deployed, 0 validation errors. NEXT:
  activate `mandrake.rm.gelatinousslime` and run the spec's seven §8 gates. Art owed;
  it renders magenta until then, which is the missing-texture colour, not a defect.
- `DESERT_FAMILY_PORT_EXECUTION_1` — defs 96 of 109 DONE. NEXT: the owner's 12 answers,
  then review the 25-row art sheet `Transient/desert_art_verdict_2026-09-20.html`, then
  step 4 (biome-table rewire). ⛔ Do NOT queue art — the daemon is mid-run on this item.
- `ROT_ROSTER_DEAD_DONOR_NAMES_1` — assessed. NEXT: it is a **WIRING** job, not a porting
  one — 51% of the roster is species we already own and never wired. Only `MA_Sporemole`
  is a real port-or-drop call.
- `BIOME_MOD_SPLIT_EXECUTION_1` — still blocked, but on **8** questions not 10; Q5 and Q6b
  were settled by fact. NEXT: put Q2/Q3/Q5 to him; nothing starts until they land.
- `ASHKARR_PAINTER_NAMES_DIVERGED_1` — filed, untouched.
  NEXT: ask him one question — do region names carry a leading "The "? (Live says no for
  all 10; the painter says yes for all 10.) Then make the literals and the planet agree.
  ⛔ Do NOT run `ashkarr_paint.py` or `ashkarr_settle.py` before that: re-running would
  rename 7 live regions and resurrect `The South Crags` over the `Sootreach` he ruled.


## Traps learned


- 🔴 **A `RSW_<donorName>` prefix test cannot find a ported species** — the port renames it.
  The mapping is in `<!-- X -> RSW_Y -->` comments under `SWBestiary/Defs/DesertPort/`. (filed: LESSONS_INBOX.md 2026-09-21)
- 🔴 **`measure sql`'s columns are `def_name`/`def_type`.** A wrong name returns an error
  line, so a row-grep reports a confident **0**. Check the query errored. (filed: LESSONS_INBOX.md 2026-09-21)
- 🔴 **`ET.iterparse` + `el.clear()` on every element** destroys a node's children before
  its own `end` fires. Clear only what you just read. (filed: LESSONS_INBOX.md 2026-09-21)
- 🔴 **Gene `loadID`s are save-local like `Faction_N`.** Splicing a pawn elsewhere makes its
  gene refs resolve SUCCESSFULLY into the destination's own genes, silently dropping any
  trait with a `<sourceGene>`. A collision does not error — it resolves to the wrong object. (filed: LESSONS_INBOX.md 2026-09-21; see: `infrastructure/state/items/FOUNDERS_IMPORTER_OWED_1.md`)
- 🔴 **The artpipe daemon may already be running your wave.** Grep `registry.jsonl` for
  `source: "<ITEM_ID>"` before filing jobs — 77 of 81 "owed" renders were already in flight. (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ **Animal art hangs off `PawnKindDef.lifeStages`, not the `ThingDef`.** (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ **`rimflow needs <ID> <val>` needs `--to`**, and zsh does not word-split unquoted
  variables — `R="python3 x.py"; $R close` fails with the whole string as the filename. (see: `~/.claude` memory zsh-does-not-word-split-unquoted-vars)
- ⚠️ `launch_and_wait.sh` exits **0** on TIMEOUT after 280 s; a full-list cold load took
  **21 minutes**. Its exit code is not the signal — grep the log for the bridge line. (filed: LESSONS_INBOX.md 2026-09-21)
- ⚠️ A subagent told to avoid backgrounding still backgrounded a slow selftest and stalled;
  brief them to run a NARROWER command instead, not to wait. (see: `~/.claude` memory subagent-background-wait-deadlock-brief-line)


## Closed since the last handoff (8)

- `ENVHAZARDS_NEVER_ACTIVATED_1` — 9bf9ccf4e
- `PYRELANDS_DENSITY_TRIPLE_1` — 1d55fa45d
- `READ_LINE_REGISTRY_SHARED_1` — 556403f99
- `FOUNDERS_EXPORT_TO_REPO_1` — d9232c36e
- `STALE_VIVIFIED_WORLDMAP_CITED_1` — 6cb085e3f
- `STALE_V24_NAMES_IN_FROZEN_SHEETS_1` — c279720b5
- `DEAD_BIOME_DEFS_IN_PROSE_1` — 5e3940963
- `BIOME_ROSTER_DEAD_SPECIES_REFS_1` — cbd2deb85

## Filed and still open (7) — the next seat's queue

- `ASHKARR_PAINTER_NAMES_DIVERGED_1` — ashkarr_paint.py would rename 7 live regions and resurrect an overruled name: all 10 of its region literals carry a 'The ' the planet does not, and on
- `FOUNDERS_IMPORTER_OWED_1` — The founders round trip needs a committed importer, not prose: a gene loadID collision silently drops the Wimp trait from 5 of 6 founders with nothing
- `FOUNDER_ROBE_MAGENTA_1` — The founders' robe layer renders as flat magenta in the CANONICAL world - magenta is RimWorld's failed-texture colour; check guy762_Robes_jawa
- `SHRUBLAND_TREE_GUARDIAN_1` — Tree-guardian uniques: owner card (candidate, not yet ruled)
- `ARIDSHRUBLAND_SHIPPING_NAMES_1` — Owner card: arid_shrubland working names (fuzz, giant, tunnel-snake, venomvine, Stall/Gale)
- `OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` — Two of our own mods are built and deployed but absent from ModsConfig, so their content is inert - including RUT_Fuzz, the heaviest row in the AridShr
- `FORGE_ROSTER_UNRECONCILED_BMT_1` — RUT_TheForge's roster JSON carries 27 unreconciled BMT_ names with zero live wiring - the same gap the Rot has, and the largest of four

## Commits

```
457983a72 LESSONS_INBOX: eight from the BENCH AFK wave
645aa8ddb ledger sync: BIOME_ROSTER_DEAD_SPECIES_REFS_1 closed, 0 of 23 still dead
22f62aaa9 Two items from the roster assessment: inert mods, and the Forge's 27 dead names
cd40e8007 ledger sync: DEAD_BIOME_DEFS_IN_PROSE_1 closed
cbd2deb85 Assessment: dead roster refs across BIOME_ROSTER_DEAD_SPECIES_REFS_1 and ROT_ROSTER_DEAD_DONOR_NAMES_1
7c0b36989 SARLACC_HABITAT_BUILD_1: a tiles-CSV reading is not a live measurement
07747fe1a LESSONS_INBOX: four traps from the desert-plants live-verify round
5e72dc140 ledger sync: both SWBestiary body-part items closed, biome-flora defect filed
5e3940963 DEAD_BIOME_DEFS_IN_PROSE_1: Weeping Stones donor name corrected to RUT_WeepingStones
9c2c5fe22 Live-verify batch: body-part repoint PASSES; desert wildPlants are silently wiped
7fb18ee8a DEAD_BIOME_DEFS_IN_PROSE_1: flag two more prose facts riding on dissolved/contested biome defs
90e535981 GRASSLANDS_TILES_CSV_STALE_1 dropped: it is the fourth rediscovery of a ruled non-defect
c58a876b9 ledger sync: BENCH session close-out
656237e68 FOUNDERS_IMPORTER_OWED_1: live-test artifact built and verified offline
f6c7d4a65 Founders importer: the Wimp regression is now a selftest, not a caveat
59c0613d9 Founders importer: allocate ids above the destination's issued ranges
f81ac2b63 COMMISSION_LEDGER_CLEANUP_1: arid_shrubland sheet's 6 slugs resolved
6a222e517 Triage: point item 3 at the built drafted-names batch
9ee222a79 Drafted creature names: the batch NONCANON_BEAST_RENAME_1 owes the owner
d3335a2fc ledger sync: close the two stale-name items, link the Blue Desert red exit to its own item
... 40 more: git log --oneline b0c2af4cc..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-21T01:53:11Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   the health publisher — auto-regenerated; `code_review_status.py`'s `_trigger_health_rebuild` re-dirties these on every prune/list. NOT a seat's
 M Transient/codebase_health.json   the health publisher — auto-regenerated, not a seat's
 M Transient/codebase_health_artifact.html   the health publisher — auto-regenerated, not a seat's
 M deployed/config/ModsConfig.before-tier-pits.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
 M design/Jawa/fauna/cast_assignment.csv   FOUNDRY — already modified before this window woke; left untouched
 M infrastructure/dashboards/hub/data/health.json   the health publisher — auto-regenerated, not a seat's
 M infrastructure/state/codebase_health_last.json   the health publisher — auto-regenerated, not a seat's
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   another window's scratchpad path leaked into the repo root (session 84f9b274, not this one) — left untouched
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   another window's scratchpad path leaked into the repo root (session 84f9b274, not this one) — left untouched
?? deployed/config/ModsConfig.before-tier-beastmechanics.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-bridge.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-diving.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-fish.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-oracle.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-visibility.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-warlab.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? deployed/config/ModsConfig.before-tier-xenotypes.xml   FOUNDRY — `modset_builder.py` mod-list tier backups from its live-verify batches; left untouched
?? infrastructure/state/.rimflow_conc_97j8px_9/   another window's rimflow concurrency lock — left untouched deliberately
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   another window — left untouched deliberately
```

