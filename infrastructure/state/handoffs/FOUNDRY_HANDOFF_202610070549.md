# FOUNDRY_HANDOFF_202610070549 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610070107`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Rimflow now has `built`/`validated` states, level-tagged criteria, token leases and RECONCILE offers (`rimflow next` checks git before offering). The stuck-state cause was structural, not agent error; the old habit of picking `doing` items blind is what to stop. Details and commands: memory `rimflow-redesign-built-validated-leases-2026-10-07` and `design/RimMandrake/rimflow_gpt_review_2026-10-07.md`.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Rimflow redesign shipped in four steps on your answers (order 1-4, level tags, FOUNDRY owns acceptance, import as built). `design/RimMandrake/rimflow_validation_levels_addendum_2026-10-07.md` records your words. About 175 built items now wait for a bridge sitting (`rimflow next --acceptance --seat FOUNDRY`).
- Open design calls handed back: stun-then-handle for the net job (WEEPINGSTONES_NET_TARGET_FLEES_1); Forge dhokkur wall-shove/trail-fade defaults are guesses (settings); TECHPRINT_FACTION_GATING_1 may belong to you rather than FOUNDRY.
- A muffalo-like creature near the pits showed a hard-edged dirt rectangle drawn over its body (screenshots `Transient/desk_muffalo.bmp`, `desk_muffalo_crop.png`); cause untraced.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `RIMFLOW_ACCEPTANCE_SITTING_1` (no such item filed) — about 175 built items owe L1/L2/GREEN-MIN live checks and BENCH holds the bridge; NEXT: when the bridge is free run `rimflow bridge take --for "acceptance sitting"` then `rimflow next --acceptance --seat FOUNDRY` and clear L1 first.
- `NEW_BUILDS_NOT_RECORDED` — ~20 builds pushed this session (wreck-fall, Warscar aerosol, CathedralPass, condenser quests, draftprints, Ninefold, brood ransom, feral survivor, Greentide port, goodwill floor, FlowWorks pair, dhokkur, chotrix, greatbole, Rakatan, Bazaar price) are not yet `implemented` in rimflow; NEXT: write level-tagged criteria and run `rimflow implemented <ID> --sha <sha>` for each.
- `FEVERWOOD_UNATTRIBUTED_XML` — RM_FeverWood.xml and RUT_FeverTrunkCore.xml hold uncommitted edits nobody claimed; NEXT: run `git diff` on both and commit or restore.
- `RUT_ORPHAN_PNGS` — RUT_DryAirBlower.png and RUT_GreatboleHeartwood.png remain in UtinniPatches because the art guard refused their deletion; NEXT: record a ledger live event for them, then delete.
- `WARSCAR_AEROSOL_SCREEN_1` — parts 1-2 pushed (c283093c9); NEXT: build part 5, the RM_AerosolScreen building, and switch ShipShields to the new comp.
- `RUSTCATHEDRAL_GOODWILL_FLOOR_1` — standing only drops, validation.py roster check fails (unconfirmed pre-existing); NEXT: run git stash-free check by running validation.py on 510d305aa^ vs HEAD and add a recovery path for standing.
- `CRACKEDLANDS_CHERRYPICKER_LASSO` — LASSO_CHERRYPICKER_REMOVAL_1 needs the live Cherry Picker config reconciled against CherryPicker.SHIP.xml; NEXT: with the game down, reconcile then set LassoSpawnChance 0.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- The queue view lists some items under two sections, so a census over it double-counts (449 rows, 389 unique) (see: design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md)
- A pushed texture add/move is refused by the art guard unless recorded via `art.py install <mod-path> <rel-under-Textures> <sha> --reason script:...`; mod arg is the repo path `src/RimMandrake/<Mod>` (see: .claude/hooks/block_unledgered_texture.py)
- zsh does not split an unquoted variable of paths; use an array for publish pathspecs (filed: memory zsh-does-not-word-split-unquoted-vars)
- Manifest NOPROSE/UNBUILT rows are the least reliable; WEEPINGSTONES_NET_FLEEING_FLIER_1 was already fixed at 0ef6dd60b (see: infrastructure/state/reconcile_manifest_2026-10-07.md)
- `winbuild` stamps `+dirty` if source is uncommitted; commit source, rebuild, push the DLL again (see: DLL_SOURCE_STAMP_GUARD_1)

## Commits

```
4f5fc9937 BAZAAR_PRICE_ENGINE_1: price store, seed rules, Tradeable.GetPriceFor postfix (active only inside a Bazaar window), intel gates and columns, 7 settings; cannot change a price in play until BAZAAR_WINDOW_GRID_1 adds the window intercept; follows the 2026-09-20 four-module ruling, not the three artifacts; never run live
a292bdd8b RAKATAN_ARCHOTECH_MACHINES_1: grade ladder, Refurbished smelter, mobile power cell and emanator (3 grades), components, research; component source/ruin wrecks/turrets/art not built; dev-spawn only; never run live
196c6f895 GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1: plantable seed with water-gated growth, dryad servants crossover (off by default); fixes the greatbole core never ticking (harvest ladder could not fire); song/hum/pilgrims/thermal not built; never run live
13030f792 WARSCAR_CHOTRIX_SIGNS_1: chotrix print class + kill-drag marks (silence ring was already built); print art is a placeholder copy, real art owed; never run live
ca4f97aca FORGE_DHOKKUR_WAYS_1: wake groan, remembered polished trails, wall-shove (8 settings, guessed defaults for the owner's two open questions); never run in game; trail art owed
74d9a7442 FlowWorks: rebuild DLL with a clean source stamp (cc8bbdff9)
cc8bbdff9 FlowWorks: retire channelConfinementEnabled (liquid always confined to the channel); rewrite the tank-loop northstar row against the real WorkGivers; fix two docs that still described the setting; selftest_flowworks_northstar and O9 were already failing; srchash +dirty, rebuild
510d305aa RUSTCATHEDRAL_GOODWILL_FLOOR_1: band keeps its own standing (-100..100, saved with the map) instead of reading the permanentEnemy faction's goodwill; nothing raises it yet; never run live
7670e0db2 rimflow: adjudicate the 9 conflicted manifest items; 7 reconciled partial
e1980635e rimflow ledger: SALVAGE_WRECKAGE_EVERYWHERE_1 reconciled partial with remaining scope
4fcf97556 rimflow ledger: reconcile verdict 'partial' with remaining scope for 86 partly built items
b439a0929 Explosive Knockback: live run 18/18 PASS record, review save grid key
243e9afd9 Explosive Knockback scenes: 18/18 PASS live; three scene defects fixed
33f54bfd9 Explosive Knockback mod (mandrake.rm.explosiveknockback): blasts throw pawns, items and corpses
c4c481143 FlowWorks: blasts break pit covers (owner Q5/Q9); flyer takeoff from a covered pit cell now counts as a fall
b1be1effc FOUNDRY/CHARTER: describe leases, implemented/built/validated, level tags, reconcile, FOUNDRY-owned acceptance sittings
46f8e3b38 Cauldron, Miasma, The Rot, Wasteland sheets pass the gate; donor-original-absent note counts as the donor column (req 4)
5a4b51247 GSS GPT source read (35 findings, 31 confirmed against code), looks pre-review recipe doc, campaign log GSS section
d72fdf9df GSS in-game runner (7 scenes incl. every gizmo/menu/setting), fuzz G2 locator + G6 probe, gss_states looks board + autofix triage
4d21a0018 rimflow ledger: import 184 source-proven items as built (level-tagged criteria); 2 owed nothing beyond L0 and went to done
... 44 more: git log --oneline 0fff8ab3d..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M src/RimMandrake/FeverWood/Defs/BiomeDefs/RM_FeverWood.xml   unattributed, NOT mine (2 and 10 line edits present before any of my builders touched FeverWood); read git diff before keeping
 M src/RimMandrake/FeverWood/Defs/ThingDefs_Buildings/RUT_FeverTrunkCore.xml   unattributed, NOT mine (2 and 10 line edits present before any of my builders touched FeverWood); read git diff before keeping
?? Transient/ModsConfig_before_bridge4.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/ModsConfig_before_d.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/ModsConfig_before_fwfinal.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/ModsConfig_before_fwmap.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/Player_load13_20261004.log   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_bridge4_deploy_plan.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_bridge4_progress.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_bridge_log_20261004d.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deep_proto.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_d_biomes.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_d_plain.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_done   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_plan_d.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_prune.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_prune_c.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r5_biomes.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r5_plain.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r5_plain2.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r5_plain3.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r6_biomes.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r6_done   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_deploy_r6_plain.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_first_errors_d.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_flowworksNS_preflight2_20261005.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_flowworksNS_prep2_20261005.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwfinal_probe_burn.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwfinal_probe_ext.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwfinal_probe_foam.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwfinal_probe_fx.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwfinal_probe_p3.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwfinal_v2live_20261005.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwkits_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwliquids_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwlogistics_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_fwsheet_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_gitprobe.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest10_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest11_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest3_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest5_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest6_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest7_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest8_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_harvest9_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe2.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe_kits.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe_pawns.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe_rr.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe_ruins.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_probe_size.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun19a_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun19b_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun20a_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun20b_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun20c_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004i.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004j.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_b1_20261004k.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_b2_20261004l.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_b3_20261004m.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_kits_Forge_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_kits_batch1_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_rerun_kits_batch2_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_reviewFW4_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_setbg.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/belt_sum.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/desk_muffalo.bmp   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/desk_muffalo.png   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/desk_muffalo_crop.png   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_doing_offline_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_doing_slice_00   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_doing_slice_01   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_doing_slice_02   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_doing_slice_03   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_fw_reviewmap_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_fw_v2_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_gss_proof_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/foundry_kits_rerun_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_A.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ALL.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ALL2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_B.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_EXT.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_RES.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_boot.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_boot2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_boot3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_boot4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_chainsA.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_chainsA2.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_chainsB.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_cover.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_drysite.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_drysite2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ext1.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ext2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ext3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ext4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ext5.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_ext6.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_iso1.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_iso2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_iso3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_iso4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_iso5.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_plotA.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_plots.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_probe.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_probe2.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_probe3.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riv1.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riv2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riv3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riv4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_rivercount.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riversite.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riversite2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_riversite3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_runA.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_runA.progress   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_runB.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_runB.progress   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_runC.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_runC.progress   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_settings.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_weir.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_ovn_works.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fw_review_map_build_log.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/fwvisuals_serve.log   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/gpt_rimflow_review_20261007.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/list_tools.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_art_poles_20261004/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_densify_human_review_notes.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_full_plan_run2_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_full_plan_run3_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_full_plan_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_live_run2_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_fast_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_fast_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots_pass1/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_noshots2_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_noshots3_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_noshots3_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_noshots_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_rec2_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_rec3_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_rec4_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_rec_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_matrix_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_owner_shots_r4/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_owner_shots_r5/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_owner_shots_r6/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_owner_shots_r7/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_probe_aerial_after_load.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_read_settings.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_relaunch2_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_relaunch_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_scenes_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_time_calls.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/mc_time_calls2.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_01_open.png   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/fixtures.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/live_queue/J1_situational_rerun/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/live_queue/J2_abort_proof/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/live_queue/situational_rerun/FlameStatues_summary.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/live_queue/situational_rerun/ResearchRetag_summary.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T023842/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T030802/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T032016/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T035902/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T050655/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T053947/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T055717/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T060347/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T062227/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T063127/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T064738/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T064928/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T071347/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T072546/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261004T074823/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261005T232247/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261005T233028/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261005T235519/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T001545/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T002351/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T003801/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T003853/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T004010/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T004657/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T011305/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T020612/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T021919/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T025413/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T044850/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T045919/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T050151/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T050713/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T060942/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T061257/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T061439/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T062549/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/modcheck/surprises/20261006T063053/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/northstar/Greentide_20261003T102251Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/refused_toll_rite_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/review_pyrelands_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/unfinished_line_world_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? Transient/venomvine_forms_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient/ shelf life ~14 days
?? conversations/   generated conversation record, not mine
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ns_flowworks_backup.20261002T070221.json   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ns_flowworks_backup.20261005T142015.json   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? deployed/config/ns_flowworks_backup.20261005T161529.json   generated ModsConfig/northstar backups from earlier bridge sessions, not mine
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_dirt.png   FlowWorks art-source pngs from an earlier session, not mine; art-guard applies if committed
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_stone.png   FlowWorks art-source pngs from an earlier session, not mine; art-guard applies if committed
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_dirt.png   FlowWorks art-source pngs from an earlier session, not mine; art-guard applies if committed
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_stone.png   FlowWorks art-source pngs from an earlier session, not mine; art-guard applies if committed
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T232949.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T233603.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T000710.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T001245.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T002141.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003132.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003420.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003624.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003701.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003821.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T004655.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T010918.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011022.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011246.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T020515.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021000.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021144.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021337.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021908.json   generated north-star run results from earlier live sessions, not mine
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T033840.json   generated north-star run results from earlier live sessions, not mine
```

