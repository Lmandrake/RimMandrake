# JUDGE — AGARILUX_PRIME_COPIES_RECONCILE_SPLIT

Judged 2026-11-11 by a blind judge seat (CLAUDE_ARCHMAGI_OFFLINE2 judge pass). I read STATEMENT.md, NOTES.md, every file in
`evidence/`, the item file, commit 45408f140e (def, patch, retire script, art events) and the gptredo_03 decision rows.
I did not read DONE.md or BROADEN.md. What I ran myself against the current tree:
- `evidence/resolve_agarilux_prime.py`: same output as `resolved_texpath_after.txt` apart from the capture line.
- `evidence/search_losing_path.py`: same output as `search_after.txt`.
- My own `git grep AB_AgariluxPrime` over the whole repo (225 hits): every hit in `src/` names the donor defName or
  `AB_AgariluxPrime_Mutator` (comments, worldmap_prefill), not the texture. Outside `src/` the hits are dated sheets, rulings,
  census or Transient records, or `flora_scale_panels.json` (a different file, `plant_art/AB_AgariluxPrime.anchor.png`).
- `art.py status Things/Plants/AB_AgariluxPrime`: no LIVE row, "slots: (none in our defs)".
- `validate_patch.py` on the touched patch and def, against the full 316-mod list (install + workshop roots): OK, 0 errors.
  Without `--defs`, the def file reports 3 errors on other defs (RM_Bryolux, RM_Glowstool, RM_GlowingAgarilux) whose textures
  another mod supplies. Those errors do not touch this item.
- artpipe `pending/` and `active/`: no *agarilux* job. The sanity probe works: `_requeued_manifests` shows GiantAgarilux jobs, a separate def.

## Lines

1. **One owner is decided and recorded.** TRUE. The item file has a "Decision, 2026-11-11" section: TheRot
   (`mandrake.rm.biomes`) owns the def and texture. Its reason comes from what the game loads. The base def plus TheRot's
   PatchOperationReplace resolved to `RotSpecies/AgariluxPrime` (`resolved_texpath_before.txt`), and the full-list live def
   dump of 2026-11-02 reads that texPath from `mandrake.rm.biomes`. That dump has no `AB_AgariluxPrime` row and no def
   naming the old slot, and a probe confirms the dump does contain the RotSpecies path. The item also corrects its own premise.
   There were three copies, not two, and neither copy judged in gptredo_03 was the one the game drew.

2. **Exactly one copy of the texture ships.** TRUE, measured as the line defines it (`src/`). Both donor-slot PNGs were
   removed in 45408f140e through `artledger.retire`, and the art events record both retires. The only `*AgariluxPrime*.png`
   under `src/*/*/Textures` is `TheRot/Textures/RotSpecies/AgariluxPrime.png`. No live reader in `src/`, the art ledger or
   art-eval state names a retired copy. The remaining hits serve the donor def, are dated or append-only records, or are
   this change's own comment and script.

3. **Every inbound reference is fixed.** TRUE. The base def's texPath now names `RotSpecies/AgariluxPrime`, and the repoint
   patch is deleted. No patch xpath in the load set reaches its graphicData/texPath (broaden_checks B). In the art ledger the
   old slot has no live entry. The donor-render installer's plan (`bulk_accept_plan_agarilux.txt`) has 0 rows for the old
   artpipe job and a working sanity probe (104 dregen jobs seen). Both deploy plans list the retired PNG as "deleted in repo
   -- --apply prunes it". My rerun of validate_patch passes, and the selftests passed (selftests.txt, 3/3 GREEN).

4. **The surviving copy's judgement stands, or it is re-judged.** TRUE. The survivor is neither gptredo_03 subject; the
   statement's two branches assumed it would be one of them. `judgement_record.txt` quotes both gptredo_03 rows with their
   judged file paths and shas: ACCEPT on b0a767dc… (the TheRot donor slot) and REGEN on c93606ba… (UtinniPatches). Neither
   sha is the survivor's (85779af9…). I checked the survivor's standing in the owner's rulings myself:
   - 2026-09-18: the owner gave the old picture a row "regen", with the note "20 wide, rename".
   - 2026-09-20: v3 landed, at git blob 28b1e08b…, the same as today.
   - That morning: "The rot art is approved." (approvedBy owner) keeps the row, whose thumb is `rot_agariluxprime_v3`.
   So the judgement that stands is the owner's own, and the copy he asked to have regenerated is not the survivor.
   No re-judge is owed under the item's rule.

## Where the evidence is weak or flattering

- `three_copies_before.png` composites all three pictures on flat green at about 480 px each. It shows which picture is
  which. It does not show how any of them looks in game.
- No game load has run since the change. The post-change texPath comes from `src/` plus a pre-change dump (2026-11-02).
  The risk is low: the def now names the path directly and no patch touches it. A future dump should still read
  `RotSpecies/AgariluxPrime`.
- `broaden_checks.txt` section A says it covers "the located load set", but its packageId map takes `src/` first.
  UtinniPatches is therefore read from `src/` (after the deletion), and Biomes from the stale deployed folder. It mixes
  views and is not a picture of the game before the change.
- The game's Mods folder still holds both retired PNGs, in `RimMandrake.Biomes/.../Things/Plants` and `UtinniPatches/...`,
  until the next deploy of those two mods prunes them. No def draws them, so nothing changes in game. This is a deploy
  still owed, not a defect on any line.
- The survivor is 4096x4096 (27 MB). It is the owner-approved bytes and outside this item's scope. I note its size only.

would show: yes
