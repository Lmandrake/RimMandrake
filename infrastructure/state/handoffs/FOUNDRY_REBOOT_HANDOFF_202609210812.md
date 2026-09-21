# FOUNDRY_REBOOT_HANDOFF_202609210812 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609202354`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**"Builds clean, validates, selftests pass" is not "done" for anything the running game touches — of the 26 items closed this wave, at least four major defects were completely invisible to every offline check and surfaced only because an agent insisted on a live load before closing:** the biome-flora generator silently overwriting six hand-authored plants' wildPlants entries with stale donor names (`BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`); a stale compiled `CreatureBehaviors.dll` missing three types that killed `RSW_ShadeWhale` and the staggerseed's whole corpse-dispersal hediff outright (`SHADEWHALE_EXTENSIONS_UNBUILT_1`); `mandrake.rut.ashkarrflora` simply absent from the owner's stored FULL mod list, so two correctly-built plants had never once been able to spawn in the actual campaign (`ASHKARRFLORA_NOT_IN_MODLIST_1`); and the same missing-suffix bug in the Armoury's texture-absorption generator silently dropping worn graphics for **123 apparel defs (1,560 PNGs)**, not just the one founder robe that first surfaced it (`FOUNDER_ROBE_MAGENTA_1`). Every one of these shipped a prior FOUNDRY pass believing it was finished. The discipline that caught all four: never close a build item on "compiles + validates" alone when the criteria say "live" — take the bridge, load it, and look.

## What the owner should see

- **A mod that never made it into his list is fixed: `mandrake.rut.ashkarrflora` is now in the stored FULL list** (`ASHKARRFLORA_NOT_IN_MODLIST_1`, live-verified). Its two plants (staggerseed, fuzz) can spawn in his actual campaign for the first time.
- **123 apparel defs across the whole Armoury mod were rendering with no worn graphics at all** (KotOR undersuits, jackets, tunics, armour — 1,560 missing PNGs), found while chasing one magenta founder robe. Fixed and live-verified on a real full cold load, zero magenta pixels. He never asked for this fix and never knew the scope; worth a look at the founders and a few Armoury pieces next time he plays.
- **A novel engine technique went live in his mod list**: the arid_shrubland venomvine's body-size passability barrier is the first thing this codebase has ever built against RimWorld 1.6's pathfinder (`PathRequest.IPathGridCustomizer`), and it uses that interface in a way vanilla itself never does (a persistent, shared, async-mutated array). It passed 9 of 10 live verification steps with real controls — genuinely well-tested — but it is new engine territory with no precedent to fall back on if something surfaces later that these tests didn't catch.
- **Five owner name-cards are waiting**, all filed this wave, none urgent: `STAGGERSEED_SHIPPING_NAME_1` (the cycle plant), `ARIDSHRUBLAND_SHIPPING_NAMES_1` (fuzz/giant/tunnel-snake/venomvine/Stall-Gale), `SHRUBLAND_TREE_GUARDIAN_1` (a unique, not yet ruled on at all), `SCRAPNEST_BIRD_BASE_THEFT_1` (should the scrap-nest birds raid his base — currently built so they cannot), and `DESERT_GLITTER_BIRDS_COMMENSALS_1` waits on a separate design item, not him.
- **A security/provenance gap in this session's own tooling was found and closed**: `./game --said` (and `apply_blanket_ruling.py --said`) completely bypassed the hook that stops an agent from fabricating a quote and stamping it as his own authorization on the ledger — caught live when a FOUNDRY subagent's own words landed on the ledger as `"seat":"OWNER"`. Fixed same-session (`OWNER_SAID_FLAG_BYPASS_1`).
- BENCH was independently active this wave too (biome-split naming rulings, Pyrelands/Scarlands renames) — see BENCH's own handoff for that thread, not duplicated here.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `COMMISSION_LEDGER_CLEANUP_1` — 10 of 85 slugs worked in two partial passes (desert sheet's 4, arid_shrubland's 6), each resolved to built/queued/re-filed/dropped and recorded in the item's own dated sections; 75 slugs across ~22 remaining sheet groups untouched. NEXT: pick the next sheet group (e.g. `weeping_stones`, 8 slugs, or `dune_sea + deep_desert`, 8 slugs) and repeat the same pattern — re-verify currency against `infrastructure/artpipe/{done,pending}` first, since the daemon ships continuously and slugs go stale in hours.
- `DESERT_STAGGERSEED_BUILD_1` — both C# mechanisms (corpse-dispersal shade-seeking, euphoric prepared dish) are built, validated, and selftested clean under the internal working name `RUT_Staggerseed`; deliberately left open per its own criteria because it ships under an owner-given name, not the working one. NEXT: once `STAGGERSEED_SHIPPING_NAME_1` gets an owner ruling, rename `RUT_Staggerseed` throughout (defs, C# class name is generic and does not need touching) and close.

## Traps learned

- `./game --said`/`apply_blanket_ruling.py --said` bypassed the owner-quote provenance hook entirely (different flag spelling than `--owner-said`, which the hook only matched literally) — fixed, both flags now covered (filed: LESSONS_INBOX, see: `OWNER_SAID_FLAG_BYPASS_1`).
- A same-mod generator (`biome_flora.py`) held a `PatchOperationReplace` on 13 biomes' `wildPlants` that silently outranked the hand-authored def every load — fixed by giving authored biomes ownership of their own field and having the generator refuse to touch them (see: `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`).
- `jawa/list_pawns` nests health at `row["health"]["hediffs"]`, not the flat `row["hediffs"]` a naive read expects — a wrong key silently reads as "0 hediffs everywhere," including on a mechanism that was working the whole time (filed: LESSONS_INBOX).
- `modset_builder.py --apply` crashed on `cp1252` printing an emoji in a tier's `why` text *before* writing `ModsConfig.xml`, so a tier swap silently did not happen and the next launch ran the stale list — fixed, stdout/stderr now forced to utf-8 (filed: LESSONS_INBOX).
- A crash log's own embedded mod-count line is the only trustworthy evidence of which list produced it — a preserved log's file mtime and even the live `ModsConfig.xml`'s own mtime can both mislead, since a metadata-preserving tier-restore copy shares the pre-swap timestamp (see: `MAPGEN_NRE_FULL_LIST_20260920_1`, closed as not-a-defect).
- RimWorld 1.6's pathfinder has no native per-body-size passability and no 4th-`PathGridDef` extension point (the pathfinder was rewritten onto Unity's job system) — the only real hook is `PathRequest.IPathGridCustomizer`, and vanilla only ever uses it synchronously with a fresh temp array (see: `VENOMVINE_FORTRESS_PASSABILITY_1`).

## Closed since the last handoff (26)

- `CREATURE_REGISTER_GEN_CORPSE_MISMATCH_1` — de4992cc78914d88487889c33f9c76a03dfc82bf
- `DESERT_SHADE_PLANTS_DESIGN_1` — 417c7f516bd57b177d2d64f4a319bfb9aea68ea0
- `PORTED_BEAST_MECHANICS_REBUILD_1` — ed0ec38fc35b3849c6b6d423683ec3eaafa79096
- `DESERT_LEACHMOSS_BUILD_1` — 39a7132b128e9eb7a39e82d48c0aeda9cb0044ee
- `OWNER_SAID_FLAG_BYPASS_1` — 03a73e17df8897e2da5ba0ee84fca3b237bdec02
- `VENOMVINE_CONTACT_VENOM_BUILD_1` — 10033074a
- `DESERT_SHADE_WHALE_FILTERFEED_1` — 0b4dbe404
- `SWBESTIARY_BODYPART_LIVE_VERIFY_1` — 9c2c5fe2221c39e8a58399e3a357cd626e7c2eed
- `SWBESTIARY_MISSING_BODYPART_DEFS_1` — 9c2c5fe2221c39e8a58399e3a357cd626e7c2eed
- `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` — 03d963de20b87d088b95eaeba301c0dd34e78576
- `SHADEWHALE_EXTENSIONS_UNBUILT_1` — 37fefdc0ee34e0e7164fa4be509920614a8b2294
- `DESERT_LEACHMOSS_LIVE_VERIFY_1` — d07d993f6fa5b7a977fbf2518e77997e256a695b
- `VENOMVINE_LIVE_VERIFY_1` — d07d993f6fa5b7a977fbf2518e77997e256a695b
- `SHADE_WHALE_ECOLOGY_LIVEPROOF_1` — d07d993f6fa5b7a977fbf2518e77997e256a695b
- `SHRUBLAND_SCRAPNEST_BIRDS_1` — accf4da6852368ee1fad39c5495ea87003223d5c
- `MAPGEN_NRE_FULL_LIST_20260920_1` — fa21d88857acdeade4f2d9cea34ae0322070e50e
- `FOUNDER_ROBE_MAGENTA_1` — 435086e29810c269e3695ecc20db1f602ab2174a
- `ASHKARRFLORA_NOT_IN_MODLIST_1` — ad6d1fd579897b577c25030b3b3ef05ee3acfe2e
- `SHRUBLAND_GIANT_ENRAGE_1` — 37b8105facfe953d5cd5e2f83d16c7f8b828149d
- `SCRAPNEST_BIRD_LIVE_VERIFY_1` — 37b8105facfe953d5cd5e2f83d16c7f8b828149d
- `FILTH_ON_NATURAL_TERRAIN_NOOP_1` — 37b8105facfe953d5cd5e2f83d16c7f8b828149d
- `VENOMVINE_FORTRESS_LIVE_VERIFY_1` — 6f43699c0ccf2e8a2db90552f2748ff52661cc2f
- `VENOMVINE_FORTRESS_PASSABILITY_1` — 6f43699c0ccf2e8a2db90552f2748ff52661cc2f
- `BRIDGE_MAP_DROP_SERIALIZATION_LOOP_1` — 2a4442d9d9f6769330c73620207d8fd57de32370
- `BRIDGE_SELECT_NONCOLONIST_PAWN_1` — 2a4442d9d9f6769330c73620207d8fd57de32370
- `VENOMVINE_PATHCOST_AND_FLYER_1` — f707e69f1792c609ca9de301a1e4d571bc007d5e

## Filed and still open (9) — the next seat's queue

- `STAGGERSEED_SHIPPING_NAME_1` — owner card: the cycle plant's shipping name (working: staggerseed)
- `DESERT_GLITTER_BIRDS_COMMENSALS_1` — desert megafauna's glitter-bird shadow commensals
- `SHRUBLAND_TREE_GUARDIAN_1` — Tree-guardian uniques: owner card (candidate, not yet ruled)
- `ARIDSHRUBLAND_SHIPPING_NAMES_1` — Owner card: arid_shrubland working names (fuzz, giant, tunnel-snake, venomvine, Stall/Gale)
- `SCRAPNEST_BIRD_BASE_THEFT_1` — owner card: should scrap-nest birds steal from player bases?
- `PYRELANDS_DEFNAME_RENAME_1` — RM_FE_Pyrelands -> RM_Pyrelands: owner ruled rename now, before the biome split
- `SCARLANDS_RENAME_OURS_1` — RUT_Scarlands collides with vanilla Odyssey Scarlands - owner ruled rename OURS
- `UMBRA_IS_A_REGION_NOT_A_BIOME_1` — RUT_Umbra is a REGION, not a biome - owner ruled it out of the biome list
- `BARREN_REGIONS_NAME_NOTHING_1` — 10 of 22 BARREN_REGIONS entries name regions that do not exist - the keep-empty test fails open

## Commits

```
9e901ca6b Handoff housekeeping: commit artpipe daemon backlog and tier-swap snapshots
98747ea6a Two false facts about the live mod list, one of them mine from an hour ago
e15771bf7 list_pawns: name the nested-health trap in the tool's own description
e0a0612ad rimflow sync: venomvine flyer item closed, prose out of the live glob
f707e69f1 jawa/pawn_flight, and the venomvine flyer exemption MEASURED
72b5dec81 Painter region names now match the planet, read off the save not guessed
84d42c63b Rename defName RM_FE_Pyrelands -> RM_Pyrelands (owner ruling 2026-09-21)
91630bd1e The mapgen crash was never on the full mod list, and the handoff said it was
f9748478c Biome split: seven of ten owner questions ruled, and §2 corrected to match
9a75129d6 Recover uncommitted output: arid_shrubland naming review sheet
d9e6314df Owner rulings 2026-09-21: eight decisions recorded on their items
b497260c6 Two lessons: PlanetTile in a bridge reply, and an unfalsifiable cast-timing bar
b54e34b13 rimflow sync: both bridge-tool items closed, prose out of the live glob, bridge released
2a4442d9d Prove the non-colonist ability tools live; grant_ability now creates the tracker
3dce2729f map_drop: stop handing the serializer a live PlanetTile
5f492651d rimflow sync: both venomvine fortress items closed, map_drop defect filed
6f43699c0 Venomvine fortress: live-verify the body-size path barrier, 9 of 10 steps
897344579 rimflow sync: bridge released by FOUNDRY
288faa64a rimflow sync: three live-verified items closed, prose out of the live glob
37b8105fa Live-verify four shrubland/desert mechanics; venomvine flyer step still unmeasurable
... 114 more: git log --oneline deaed4580..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-21T08:07:36Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
 M Transient/codebase_health.html   automated health publisher (rimflow-triggered regen) -- not this session
 M Transient/codebase_health.json   automated health publisher (rimflow-triggered regen) -- not this session
 M Transient/codebase_health_artifact.html   automated health publisher (rimflow-triggered regen) -- not this session
 M design/Jawa/fauna/cast_assignment.csv   FOUNDRY (commission-ledger species-donor claims: TunnelSnake/Klorslug, ShrublandGiant/Fambaa, ScrapNestBird/Whisperbird) -- may also carry BENCH's concurrent desert-family work, diff before committing
 M infrastructure/dashboards/hub/data/health.json   automated health publisher -- not this session
 M infrastructure/state/codebase_health_last.json   automated health publisher -- not this session
?? Transient/desert_family_rulings_2026-09-21.md   BENCH, live in-progress (concurrent this wave) -- not mine to commit
?? Transient/world_label_hierarchy_2026-09-21.md   BENCH, live in-progress (concurrent this wave) -- not mine to commit
?? Transient/triposr_prototype/{TripoSR,torchmcubes}/   pre-existing nested git repos (own .git dirs); flagged un-committable by this wave's artpipe hygiene pass -- leave alone
?? "\\wsl.localhost\Ubuntu\tmp\..." (x2)   bogus escaped-Windows-path artifacts, not real repo content -- not ours to interpret
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow's own concurrency-lock scratch dir, self-cleaning -- not a real edit
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing untracked backup from 2026-09-11 -- not this session
?? infrastructure/state/handoffs/FOUNDRY_REBOOT_HANDOFF_202609210812.md   this handoff itself -- committed in the same act as this line
```

