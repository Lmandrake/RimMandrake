# BENCH_REBOOT_HANDOFF_202609202255 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609202015`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward


🔴 **Four separate claims that BLOCKED work turned out to be false, and every one had
already cost somebody a run.** This session's whole shape is: read the item, reproduce
the claim, *then* act.

- `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` said bridge pawn spawns NPE **"universally"** and
  that it kills the debug-testing workflow. **`jawa/spawn_pawn` works fine** — measured
  same map, same session, same defName, and 65 pawns had already gone through it that
  hour. Only the `GenSpawn`-on-a-`ThingMaker`-Thing routes fail
  (`rimworld/spawn_thing`, `jawa/spawn_batch`). `PORTED_BEAST_MECHANICS_REBUILD_1` sat
  **BLOCKED** on that false claim with its DLL built and live since 10:29.
- `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` said **"SWBestiary is not deployed"**. It
  was. 15 of its 18 dangling refs already resolved.
- `canon_references/chagrian` said the canon infobox is **"blue only"**. It carries blue
  AND orange — and that false line had already caused **two canon-sourced genes to be
  deleted** three days earlier.
- `canon_references/ugnaught`'s `## ruling` section said *"(empty — owner has not
  reviewed this race yet)"* while his ruling was three days old.

🔑 **And the instruments lied the same way.** A subagent claimed it had "verified the
missing packageIds are absent from the Workshop cache" — one `grep` found them
immediately in a root holding **1271 folders**. A census of 17 Ithorians returned
**17/17 on one gene**, which was the query reading the xenotype's whole gene list, not
each pawn's. ⇒ **A round, uniform, or conveniently alarming number is a query bug until
you check one case by hand.**

## What the owner should see


- ⏸️ **The metal-eater is UNTESTED, not failed.** `PORTED_BEAST_MECHANICS_REBUILD_1`
  criterion 1 **PASSES** live — all five comp classes resolved and khorrak
  (`RSW_Ferroclaw`), `RSW_Voltmaw` and zhakka (`RSW_Cindermite`) all spawn. Criterion 2
  was attempted twice and **both runs were invalid**: first the animal was 73% fed, then
  `jawa/pawn_need` silently read instead of writing. Don't read those as a failure.
- 🔴 **The skin-colour pass may be less visible than it looks.** MEASURED: every pawn of
  a species carries **all** its skin genes (17/17 Ithorians held the same six); which
  override actually RENDERS is **not established**, and Bith pawns with byte-identical
  gene sets came out orange, green and pink. Nobody should promise that editing these
  lists changes what he sees until that is measured against a decompiler.
- ⚠️ **He ruled the DIRECTION on Zygerrian, not which two genes survive** — BENCH chose
  the pair that read "Light". Recorded as BENCH's choice, not his word.
- ⚠️ **The founders still exist only inside `CANONICAL_ASHKARR_START_2026-09-12.rws`.**
  Untouched this session. `FOUNDERS_EXPORT_TO_REPO_1`.

## What is half-done, and where it stops


- `PORTED_BEAST_MECHANICS_REBUILD_1` — criterion 1 PASSES; 2–6 unverified.
  NEXT: resolve `jawa/pawn_need`'s parameter shape from the tool schema (it returned
  `action:"list"` and set nothing), make a ferroclaw genuinely hungry, then re-test.
  ⛔ Do not re-file criterion 2 as failing — it was never exercised.
- `XENOTYPE_CANON_CORRECTION_1` — steps 1–4 done (dossier, verification, skin, grid).
  NEXT: head shapes. 12 artpipe jobs are queued for the four borrowed heads
  (Lasat←Cathar, Nelvaanian←Bothan, Ortolan←Kubaz, Mimbanese←Tusken); when frames land,
  re-run `stage_xenotype_grid.py` for the second grid.
- `EXPLOSIVE_PLANT_GROWTH_1` — three variants ruled; the model was reframed.
  NEXT: re-cut the roster **per-plant, not per-biome** — he ruled the behaviour rides
  plant genetics/identity, and "plants that are contaminated" is his worked example.
  ⛔ Do not author a per-biome variant table.
- `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` — selftest landed and green; SWBestiary
  turned out already deployed and the 5-file gap is now closed too.
  NEXT: lift the two biome-table holds in `src/DEPLOY_HOLD.txt` in one sitting, then
  the item closes.
- `SHEET_ORPHAN_CONSUMPTION_1` (FOUNDRY's) — unblocked by his ruling.
  NEXT: FOUNDRY files the 17 non-BMT flora art jobs and holds the 20 `BMT_Plant_*`.
- `FOUNDERS_EXPORT_TO_REPO_1` — untouched. NEXT: extract the founders from the canonical
  save into the repo; they have no repo copy at all.

## Traps learned


- **`jawa/spawn_pawn` is the ONLY working bridge pawn spawn.** `rimworld/spawn_thing`
  and `jawa/spawn_batch` both NPE on any pawn and both work fine on non-pawns.
  (filed: LESSONS_INBOX; item: `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`)
- **`<loadAfter>` is invisible to dependency closure.** A mod supplying comp classes or
  textures must be in `<modDependencies>`, or a reduced tier drops it and **a missing
  comp type discards the whole def with no error naming it**.
  (filed: LESSONS_INBOX; fixed in `SWBestiary/About/About.xml`, `3bb3e6966`)
- **`modset_builder --restore` restores the previous TIER once tiers are chained**, not
  the owner's list — it would have handed back a 16-mod list reporting success.
  (filed: LESSONS_INBOX)
- **Four bridge tools name the same argument differently** — `set_pawn_rotation` takes
  `pawnId` while `pawn_gear` beside it takes `pawn`; `take_screenshot` takes `fileName`;
  `set_fog` takes `action`+`rect`. `rimbridge_client`'s unknown-param guard caught all
  four; the bridge would have discarded them and returned success.
  (see: `.claude/skills/rimworld-live-review/SKILL.md` §8a)
- **`jawa/sky_glow_set` does not survive to the shutter** — identical mean brightness
  with and without it. Get light from `jawa/time_set_ticks`, and never post-brighten a
  colour review. (see: same skill, §8b)
- **`pkill -f` matches this window's own shell and kills it** (exit 144). Kill by PID.
  (see: `pkill-f-matches-my-own-shell` memory)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `FALL_LINE_ARRIVAL_MECHANISM_1` — Build the Fall Line arrival mechanism for the 15 species pulled from ambient wildAnimals

## Commits

```
d9fa7dac0 Two lessons from the beastmechanics verification
3bb3e6966 SWBestiary: two hard dependencies were invisible to dependency closure
22994f753 PORTED_BEAST_MECHANICS_REBUILD_1: criterion 1 PASSES live; two undeclared deps found
90e203d46 SHEET_ORPHAN_CONSUMPTION_1: apply the last 3 of 15 flora moves, sync the generator
68639d928 SHEET_ORPHAN_CONSUMPTION_1: flora art:improve channel closed at zero owed
736efec90 EXPLOSIVE_PLANT_GROWTH_1: four owner rulings, and one that changes the model
1543b12ec SHEET_ORPHAN_CONSUMPTION_1: the 2026-09-10 fauna cut never reached the live game
0d6405f66 CUT_FALLOUT_GENERATED_DATA_1: record subtask (b) as fully DONE
c83be065e LESSONS_INBOX: the pawn-spawn lesson said the wrong thing, and it idled a seat
b43a3abbd PORTED_BEAST_MECHANICS_REBUILD_1: its blocker is false, live verification can proceed
61c6a9233 Sync last 3 stale BMT_ names in biome base XML: TwistingThorngrass/TwistingThornweed/TreeMartyr
108e10ade BRIDGE_PAWN_SPAWN_CRASHES_VEF_1: "universally" was false - jawa/spawn_pawn works
8725fb338 Base BiomeDef source still carried 5 dead BMT_ cross-refs already fixed by a live patch
fe98d2ed9 CUT_FALLOUT_GENERATED_DATA_1: clean dead BMT_ cross-refs out of the hand-authored biome base files
185518a53 Three off-canon colours trimmed on his ruling; the gene-list-is-not-a-pool finding
40249a986 SHEET_ORPHAN_CONSUMPTION_1: owner unblocked the flora channel
4de14e825 rimflow: close EXTREME_DESERT_UNRULED_VERMIN_1 and FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1 at 66649b5a0
66649b5a0 EXTREME_DESERT_UNRULED_VERMIN_1: pull all 15 Fall-Line rows out of ambient wildAnimals
2479ce1db Correct a false caption on the xenotype sheet
90b8c46eb XENOTYPE_CANON_CORRECTION_1: steps 3 and 4 done, three rulings recorded
... 14 more: git log --oneline b29056d11..HEAD
```

## Game / bridge / tree state at wrap

- **game: DOWN.** BENCH closed it after the beastmechanics verification.
- **bridge: FREE.** Released by BENCH. ⚠️ The ledger recorded it as held by FOUNDRY at
  release time — that is the `handoff.py` two-window ambiguity, not a stolen lock.
- 🔴 **`ModsConfig.xml` is the REAL 618 list again — restored by hand, not by
  `--restore`.** Tiers were chained this session (xenotypes 16 → beastmechanics 14), so
  `modset_builder --restore` would have handed back a **16-mod** list while reporting
  success. The 618 list was copied from
  `deployed/config/ModsConfig.before-tier-xenotypes.xml` and verified at 618 active.
  ⛔ Do not run `--restore` to "fix" it.
- **Two new tiers exist and are worth reusing:** `xenotypes` (16 mods, bridge up in
  **45 s**) and `beastmechanics` (14 mods, same). Against ~15 minutes on the full list.
- **Keeper save:** `XENOTYPE_SKIN_REVIEW_2026-09-20.rws` (10.7 MB, verified on disk,
  nothing existing overwritten). Stays until he says delete.
- **artpipe daemon is LIVE** (pid 605) with 12 xenotype head jobs queued; its ~799
  uncommitted files under `infrastructure/artpipe/` are its own churn.
- BENCH holds nothing mid-edit. All five subagents reported.

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-20T22:55:05Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   — code_review_status.py's health publisher — regenerated by any prune/list, not a seat's
MM Transient/codebase_health.json   — code_review_status.py's health publisher — regenerated by any prune/list, not a seat's
 M Transient/codebase_health_artifact.html   — code_review_status.py's health publisher — regenerated by any prune/list, not a seat's
 M deployed/config/ModsConfig.before-tier-pits.xml   — pre-existing tier backup, not this session's
 M design/Jawa/fauna/cast_assignment.csv   — another window (fauna pass) — not BENCH's, left alone
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_a_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_b_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_a_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_b_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_dewback_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_grmolebear_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_kreetle_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_megatardi_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_orray_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_rutcathedralroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_rutscarroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_wyyyschokk_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_scratches_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_scratches_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_scratches_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_tally_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_tally_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_tally_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_0.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_4.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_5.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_warn_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_warn_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/rslpn_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/rswollim_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/rswollimwood_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/registry.jsonl   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
MM infrastructure/artpipe/throughput.jsonl   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/dashboards/hub/data/health.json   — code_review_status.py's health publisher — regenerated by any prune/list, not a seat's
 M infrastructure/state/codebase_health_last.json   — code_review_status.py's health publisher — regenerated by any prune/list, not a seat's
 M infrastructure/state/ledger/events.jsonl   — another window — left untouched deliberately
 M infrastructure/state/queue/BENCH.md   — another window — left untouched deliberately
 M infrastructure/state/queue/FOUNDRY.md   — another window — left untouched deliberately
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   — another window — not BENCH's, left untouched
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   — another window — not BENCH's, left untouched
?? deployed/config/ModsConfig.before-tier-beastmechanics.xml   — BENCH — tier backup written by modset_builder this session; the xenotypes one holds the real 618 list
?? deployed/config/ModsConfig.before-tier-bridge.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-diving.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-fish.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-oracle.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-visibility.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-warlab.xml   — pre-existing tier backup, not this session's
?? deployed/config/ModsConfig.before-tier-xenotypes.xml   — BENCH — tier backup written by modset_builder this session; the xenotypes one holds the real 618 list
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agarilux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arpeau_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_brightbell_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bryolux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowstool_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nuitae_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_palemoss_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_sagecrust_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_sagecrust_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_shinecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_shinecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_skulltop_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_skulltop_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_slimypholiota_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_slimypholiota_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_violetwimple_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_violetwimple_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_witchesoyster_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_witchesoyster_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wrinklecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wrinklecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rslpn_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rslpn_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollim_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollim_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollimwood_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollimwood_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_agelesscap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_agelesscap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_falsefruit_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_falsefruit_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_grownfurnace_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_grownfurnace_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_palemoss_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_palemoss_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_paletree_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_paletree_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_regenerantveil_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_regenerantveil_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/desert_swaca_kybuck_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/desert_swaca_kybuck_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ashworm_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ashworm_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ashworm_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Barbthorn_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Barbthorn_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Barbthorn_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Cindermite_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Cindermite_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Cindermite_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunegrass.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunestalker_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunestalker_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunestalker_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_EmberCarpet.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandhorn_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandhorn_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandhorn_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandmaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandmaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandmaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandstrider_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandstrider_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandstrider_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Scrubgrass.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spinerat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spinerat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spinerat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spineroller_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spineroller_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spineroller_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporemass_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporemass_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporemass_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporepaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporepaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporepaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stareling_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stareling_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stareling_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Starvine.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stoneback_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stoneback_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stoneback_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_SweetbarkTree.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_VellaraBloom.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Voltmaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Voltmaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Voltmaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Whirlbloom.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_ronto_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_ronto_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_ronto_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scavrat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scavrat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scavrat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scurrier_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scurrier_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scurrier_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_shyrack_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_shyrack_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_shyrack_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_skalder_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_skalder_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_skalder_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_sketto_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_sketto_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_sketto_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_urusai_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_urusai_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_urusai_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_womprat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_womprat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_womprat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_worrt_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_worrt_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_worrt_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_wraid_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_wraid_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_wraid_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_bolotaur_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_bolotaur_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_bolotaur_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_cannok_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_cannok_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_cannok_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_clodhopper_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_clodhopper_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_clodhopper_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_convor_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_convor_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_convor_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_falumpaset_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_falumpaset_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_falumpaset_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralgrazer_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralgrazer_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralgrazer_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralnerf_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralnerf_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralnerf_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_graniteslug_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_graniteslug_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_graniteslug_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_grank_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_grank_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_grank_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_horax_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_horax_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_horax_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_jakobeast_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_jakobeast_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_jakobeast_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_krykna_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_krykna_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_krykna_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_nerf_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_nerf_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_nerf_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_pikobis_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_pikobis_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_pikobis_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_bloddle.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_porg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_porg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_porg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_qormot_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_qormot_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_qormot_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_runyip_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_runyip_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_runyip_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_shaak_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_shaak_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_shaak_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_strill_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_strill_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_strill_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_teemuss_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_teemuss_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_teemuss_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_uvak_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_uvak_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_uvak_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_varactyl_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_varactyl_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_varactyl_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_voorpak_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_voorpak_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_voorpak_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_vulptex_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_vulptex_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_vulptex_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_warwyrm_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_warwyrm_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_warwyrm_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_whisperbird_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_whisperbird_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_whisperbird_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_zeer_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_zeer_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_zeer_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/state/.rimflow_conc_97j8px_9/   — another window — left untouched deliberately
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   — another window — left untouched deliberately
```

