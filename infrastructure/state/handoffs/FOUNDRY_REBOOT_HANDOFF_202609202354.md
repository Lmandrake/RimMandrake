# FOUNDRY_REBOOT_HANDOFF_202609202354 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609202127`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A CLOSED ledger item's own `## verify` criteria can be silently unmet.
`BMT_FLORA_ABSORPTION_1` closed itself as done, but all 14 dead `BMT_` plant
cross-refs were still sitting live and mostly UNGUARDED in 8 biomes' hand-authored
`Defs/BiomeDefs/RUT_*.xml` `<wildPlants>` tables — the generator
(`biome_flora.py --write` → `Patches/BiomeFlora_Ashkarr.xml`) only ever
OVERWRITES that content at load, it never edits the base file, so `--check`
(roster vs. `FAMILIES`, never vs. the base XML) could not see the base file was
stale. This pattern recurred FOUR separate times this session across different
agents (flora repoint, flora move/purge, the fauna-cut channel) — a
roster/generator-layer fix that never reached the load-bearing hand-authored
layer. **Before trusting any closed item's "zero X remain" claim, grep the
actual deployed/hand-authored XML directly, not just the design-layer source.**

## What the owner should see

- **`TITANOSLIME_SLIME_BIOME_1`'s design assumes `mandrake.rm.gelatinousslime`
  and TitanicCreatures are real, loaded mods — this is UNMEASURED against the
  actual 618-mod campaign list.** The design session only saw a 15-mod test
  tier. Confirm before a build pass starts, or the whole spec needs revisiting
  against whatever's actually available.
- **`PORTED_BEAST_MECHANICS_REBUILD_1` stays open on a real gap, not FOUNDRY
  caution**: Voltmaw/Cindermite's remaining criteria (ability gizmo + AI use,
  cone/no-fire behavior, settings persistence) could not be forced through the
  bridge — `select_pawn`/`ToolMapForPawns` refuse non-colonist pawns, and the
  hostile AI never proactively engaged an isolated colonist over 1260 ticks.
  This may need either a longer live observation window or your own manual
  play to actually confirm, not another bridge attempt.
- **`COMMISSION_LEDGER_CLEANUP_1`** (85 genuinely-owed new-art/def
  commissions, re-derived from the 118-row ledger with the other 33 found
  already-built/superseded/queued) is real, unstarted, unreviewed work — worth
  a look before a build pass just starts generating against it blind.
- You already ruled on: the 12 sizeBin corrections (applied), the dusk-rat art
  conflict (art-register approval stands), and the Titanoslime ask itself —
  all landed this session, nothing further needed from you on those three.

## What is half-done, and where it stops

- `CREATURE_REGISTER_GEN_CORPSE_MISMATCH_1` — filed, not investigated;
  NEXT: read `gen_creature_register.py`'s corpse cross-check to find what the
  two numbers (1242 vs 1265) actually count and why they diverge, before
  trusting a regenerated creature register again.
- `FALL_LINE_ARRIVAL_MECHANISM_1` — design filed (BENCH, this session's
  concurrent activity) with the full 15-species list preserved; NEXT: pick up
  as a FOUNDRY build once the design side is confirmed settled.
- `COMMISSION_LEDGER_CLEANUP_1` — filed, not started; NEXT: read it, re-verify
  currency (it's already hours old), then work it as ordinary build/art-queue
  filing per its own list.
- `TITANOSLIME_SLIME_BIOME_1` — design DONE (`design/RimMandrake/RM_titanoslime_spec.md`),
  item left in `doing` for a FOUNDRY build pass; NEXT: confirm the
  GelatinousSlime/TitanicCreatures mod-dependency question above with the
  owner first, then build per the spec's own sized build list (§8).
- `PORTED_BEAST_MECHANICS_REBUILD_1` — re-blocked after partial live
  verification (Ferroclaw's steel-eating confirmed, Voltmaw/Cindermite's
  criteria not forceable via bridge this pass); NEXT: either a longer
  unattended observation window on a live map, or ask the owner to manually
  trigger/observe the ability gizmo and cone-fire behavior himself.
- `SWBESTIARY_UNPREFIXED_DONOR_DEFS_1` — proposed, not started, correctly
  skipped this session; NEXT: do not start until the 94 desert-port art jobs
  still in `infrastructure/artpipe/pending/` finish landing (the item's own
  warning: renaming defNames while their art is in flight risks a texPath
  mismatch) — check `infrastructure/artpipe/pending/` count before picking
  this up.

## Traps learned

- A ledger item's `## verify` criteria being "met" at close time does not mean
  it stays met — the generator-vs-hand-authored-XML two-layer gap above hit
  four times this session (filed: LESSONS_INBOX).
- A subagent that backgrounds a shell command (e.g. `run_selftests.py &`) and
  then waits for a notification will deadlock — nothing wakes it. One agent
  this session did exactly that and had to be nudged via `SendMessage` to
  poll/check in the foreground instead (see:
  `subagent-background-wait-deadlock-brief-line` memory).
- A hand-rolled regex sweep for dangling `PawnKindDef.race` cross-refs across
  `src/**/*.xml` produced 133 hits, almost entirely false positives (verified
  one was flatly wrong — the def existed, the regex mis-paired `<ThingDef>`/
  `<defName>` blocks). The correct instrument was a real XML parse with
  inheritance resolution against the EXACT crashed mod list, which a
  follow-up agent used successfully (see:
  `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`, root-cause section).
- The live game can crash to full process death (confirmed via `tasklist`,
  not just a bridge error) from dev mode's auto-open Spawn-Pawn palette
  hitting a `PawnKindDef` with an unresolvable `<race>` — root cause was a
  soft `loadAfter` where a hard `modDependencies` was needed, so the def got
  silently dropped whole on a narrower mod tier (see:
  `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`).

## Closed since the last handoff (6)

- `ROSTER_VALIDATOR_STALE_REFS_1` — ac8b64d1c49494275554ac3164c7a277c51614cf
- `EXTREME_DESERT_UNRULED_VERMIN_1` — 66649b5a0
- `FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1` — 66649b5a0
- `SHEET_ORPHAN_CONSUMPTION_1` — 3c57dff4ac1bd898d6cee6b4b90ac293c8b900d9
- `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` — eaf288a211baf46c081e4eea68f6881613f4482d
- `DRUM_LURE_PREDATOR_BUILD_1` — eaf288a211baf46c081e4eea68f6881613f4482d

## Filed and still open (4) — the next seat's queue

- `CREATURE_REGISTER_GEN_CORPSE_MISMATCH_1` — gen_creature_register.py refuses: CORPSE CROSS-CHECK FAILED 1242 vs 1265
- `FALL_LINE_ARRIVAL_MECHANISM_1` — Build the Fall Line arrival mechanism for the 15 species pulled from ambient wildAnimals
- `COMMISSION_LEDGER_CLEANUP_1` — 85 genuinely-owed new-art/def commissions from the 118-row ledger
- `TITANOSLIME_SLIME_BIOME_1` — Owner ask: a Titanoslime for RUT_Slime, devour-whole + grows-as-it-eats

## Commits

```
dd11b99f8 rimflow sync: bridge release after live verification session
9f153e8fd rimflow sync: close BRIDGE_PAWN_SPAWN_CRASHES_VEF_1 + DRUM_LURE_PREDATOR_BUILD_1, re-block PORTED_BEAST_MECHANICS_REBUILD_1
eaf288a21 Live bridge re-verify: VEF crash fix holds, drum-lure mechanics confirmed, ferroclaw eating confirmed
0298fddbd Biome work triage: what is workable with no game and no bridge
f738b745a ledger: TITANOSLIME_SLIME_BIOME_1 claimed and started (BENCH, design pass)
dd1adf4f6 TITANOSLIME_SLIME_BIOME_1: design spec for the Titanoslime (RM_GelatinousSlime apex)
78b63a979 DONOR_DEFS_PORT_TO_OURS_1: census the 66 live donor/port label twins
556403f99 READ_LINE_REGISTRY_SHARED_1: shared read-line ids get a registry and a lint
f53094e0b rimflow: close SHEET_ORPHAN_CONSUMPTION_1 at 3c57dff4a
04a0b78c9 FALL_LINE_MAJOR_REGION_LABEL_1: why no Ash'karr label reads as major, and the fix
3c57dff4a SHEET_ORPHAN_CONSUMPTION_1: apply the 12 sizeBin grading corrections, resolve the dusk-rat register conflict, freeze both decisions files
9ee72eb02 STALE_VIVIFIED_WORLDMAP_CITED_1: file the stale-worldmap citation defect
4f8f16a2e FALL_LINE_ARRIVAL_MECHANISM_1: the arrival spec, with the region name corrected
a356ca4ef PYRELANDS_SOUTH_TOPDOWN_REGEN_1: the work was already done; nothing regenerated
e75b542eb File TITANOSLIME_SLIME_BIOME_1: owner's Titanoslime ask, with engine research done
7a4ea578c EXPLOSIVE_PLANT_GROWTH_1: per-plant roster, replacing the per-biome framing
943f4b37d BRIDGE_PAWN_SPAWN_CRASHES_VEF_1: root-cause the null-race PawnKindDef crash
ee8b70911 FOUNDERS_EXPORT_TO_REPO_1: the founders now have a repo copy
22abdbd8d DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1: deploy the 14 biome tables, item is done
daf29f0d9 SHEET_ORPHAN_CONSUMPTION_1: record the flora move/purge channel's close-out, summarize state
... 28 more: git log --oneline a9542bf8a..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-20T23:52:32Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   automated health publisher (rimflow-triggered regen) -- not this session
MM Transient/codebase_health.json   automated health publisher (rimflow-triggered regen) -- not this session
 M Transient/codebase_health_artifact.html   automated health publisher (rimflow-triggered regen) -- not this session
 M deployed/config/ModsConfig.before-tier-pits.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
 M design/Jawa/fauna/cast_assignment.csv   concurrent BENCH session, mid-edit as of this handoff -- do not touch, do not stash
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_a_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_b_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_a_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_b_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_dewback_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_grmolebear_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_kreetle_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_megatardi_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_orray_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_rutcathedralroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_rutscarroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_wyyyschokk_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_scratches_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_scratches_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_scratches_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_tally_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_tally_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_tally_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_0.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_4.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_5.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_warn_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_warn_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/rslpn_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/rswollim_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/rswollimwood_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_lasat_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_lasat_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_lasat_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_mimbanese_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_mimbanese_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_mimbanese_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_nelvaanian_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_nelvaanian_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_nelvaanian_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_ortolan_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_ortolan_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/pending/xeno_head_ortolan_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/registry.jsonl   artpipe daemon (autonomous, continuous output) -- not this session
MM infrastructure/artpipe/throughput.jsonl   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/dashboards/hub/data/health.json   automated health publisher (rimflow-triggered regen) -- not this session
 M infrastructure/state/ledger/events.jsonl   rimflow ledger, auto-regenerated by every claim/close this session and concurrent BENCH activity -- shared, not a single seat's edit
 M infrastructure/state/queue/BENCH.md   auto-regenerated by rimflow render on any write -- not specifically this session
 M infrastructure/state/queue/FOUNDRY.md   auto-regenerated by rimflow render on any write -- reflects this session's claims/closes
 M src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs   concurrent BENCH session (water/FlowWorks work) -- not this session
 M src/RimMandrake/Pyrelands/validation.py   concurrent BENCH session -- not this session
 M src/RimUtinni/UtinniPatches/Patches/AshStorms_Pyrelands.xml   concurrent BENCH session -- not this session
 M src/RimUtinni/UtinniPatches/Patches/BiomeDescriptions_Ashkarr.xml   concurrent BENCH session -- not this session
 M src/RimUtinni/UtinniPatches/Patches/ManyWaters_RiverSteam_Ashkarr.xml   concurrent BENCH session -- not this session
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   scratch/tmp path outside the repo tree -- not a real tracked file
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   scratch/tmp path outside the repo tree -- not a real tracked file
?? deployed/config/ModsConfig.before-tier-beastmechanics.xml   this session -- backup made before the live BRIDGE_PAWN_SPAWN_CRASHES_VEF_1/DRUM_LURE/PORTED_BEAST verification pass swapped to the extended beastmechanics tier
?? deployed/config/ModsConfig.before-tier-bridge.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-diving.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-fish.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-oracle.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-visibility.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-warlab.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-xenotypes.xml   concurrent BENCH session (XENOTYPE_CANON_CORRECTION_1) -- not this session
?? design/RimMandrake/biome_mod_architecture.md   concurrent BENCH session -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_igitz_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_igitz_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_igitz_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_igitz_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_igitz_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_igitz_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iriaz_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iriaz_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iriaz_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iriaz_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iriaz_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iriaz_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jamel_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jamel_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jamel_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jamel_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jamel_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jamel_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jimvu_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jimvu_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jimvu_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jimvu_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jimvu_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_jimvu_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kreetle_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kreetle_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kreetle_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kreetle_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kreetle_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kreetle_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kwi_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kwi_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kwi_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kwi_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kwi_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kwi_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kybuck_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kybuck_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kybuck_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_kybuck_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_lothcat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_lothcat_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_lothcat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_lothcat_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_lothcat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_lothcat_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_massiff_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_massiff_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_massiff_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_massiff_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_massiff_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_massiff_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mudhorn_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mudhorn_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mudhorn_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mudhorn_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mudhorn_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mudhorn_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mynock_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mynock_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mynock_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mynock_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mynock_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_mynock_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_nuna_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_nuna_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_nuna_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_nuna_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_nuna_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_nuna_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_pufferpig_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_pufferpig_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_pufferpig_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_pufferpig_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_pufferpig_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_pufferpig_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agarilux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arpeau_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_brightbell_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bryolux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowstool_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nuitae_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_palemoss_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_sagecrust_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_sagecrust_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_shinecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_shinecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_skulltop_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_skulltop_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_slimypholiota_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_slimypholiota_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_violetwimple_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_violetwimple_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_witchesoyster_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_witchesoyster_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wrinklecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wrinklecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rslpn_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rslpn_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollim_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollim_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollimwood_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollimwood_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_agelesscap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_agelesscap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_falsefruit_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_falsefruit_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_grownfurnace_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_grownfurnace_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_palemoss_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_palemoss_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_paletree_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_paletree_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_regenerantveil_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_regenerantveil_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/failed/desert_swaca_kybuck_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/failed/desert_swaca_kybuck_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ashworm_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ashworm_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ashworm_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Barbthorn_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Barbthorn_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Barbthorn_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Cindermite_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Cindermite_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Cindermite_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunegrass.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunestalker_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunestalker_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunestalker_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_EmberCarpet.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandhorn_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandhorn_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandhorn_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandmaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandmaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandmaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandstrider_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandstrider_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandstrider_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Scrubgrass.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spinerat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spinerat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spinerat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spineroller_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spineroller_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spineroller_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporemass_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporemass_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporemass_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporepaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporepaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporepaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stareling_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stareling_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stareling_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Starvine.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stoneback_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stoneback_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stoneback_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_SweetbarkTree.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_VellaraBloom.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Voltmaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Voltmaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Voltmaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Whirlbloom.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_ronto_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_ronto_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_ronto_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scavrat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scavrat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scavrat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scurrier_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scurrier_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scurrier_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_shyrack_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_shyrack_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_shyrack_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_skalder_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_skalder_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_skalder_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_sketto_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_sketto_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_sketto_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_urusai_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_urusai_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_urusai_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_womprat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_womprat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_womprat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_worrt_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_worrt_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_worrt_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_wraid_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_wraid_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_wraid_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_bolotaur_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_bolotaur_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_bolotaur_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_cannok_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_cannok_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_cannok_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_clodhopper_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_clodhopper_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_clodhopper_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_convor_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_convor_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_convor_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_falumpaset_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_falumpaset_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_falumpaset_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralgrazer_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralgrazer_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralgrazer_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralnerf_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralnerf_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralnerf_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_graniteslug_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_graniteslug_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_graniteslug_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_grank_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_grank_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_grank_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_horax_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_horax_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_horax_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_jakobeast_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_jakobeast_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_jakobeast_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_krykna_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_krykna_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_krykna_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_nerf_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_nerf_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_nerf_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_pikobis_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_pikobis_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_pikobis_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_bloddle.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_porg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_porg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_porg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_qormot_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_qormot_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_qormot_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_runyip_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_runyip_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_runyip_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_shaak_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_shaak_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_shaak_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_strill_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_strill_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_strill_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_teemuss_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_teemuss_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_teemuss_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_uvak_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_uvak_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_uvak_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_varactyl_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_varactyl_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_varactyl_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_voorpak_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_voorpak_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_voorpak_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_vulptex_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_vulptex_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_vulptex_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_warwyrm_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_warwyrm_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_warwyrm_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_whisperbird_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_whisperbird_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_whisperbird_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_zeer_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_zeer_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_zeer_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow's own concurrency-lock scratch dir -- not a real edit
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing untracked backup from 2026-09-11 -- not this session
```

