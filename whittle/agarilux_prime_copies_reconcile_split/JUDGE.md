# JUDGE: AGARILUX_PRIME_COPIES_RECONCILE_SPLIT

Judge: CLAUDE_ARCHMAGI_OFFLINE2 judge seat, 2026-11-11, blind (read STATEMENT.md, NOTES.md and evidence/ only, plus
my own checks against the repo and the live def dump; did not read DONE.md, BROADEN.md or the earlier JUDGE.md).

What I checked myself, beyond reading the evidence:
- Re-ran `resolve_agarilux_prime.py` and `search_losing_path.py` into /tmp: output identical to
  `resolved_texpath_after.txt` and `search_after.txt` (apart from the timestamp line).
- Queried the live def dump (`defs.sqlite`, captured 2026-11-02T17:59:18Z) myself: RM_AgariluxPrime is a ThingDef from
  mandrake.rm.biomes with texPath `RotSpecies/AgariluxPrime`; AB_AgariluxPrime has no row; 0 dumped defs name
  `Things/Plants/AB_AgariluxPrime`.
- `git ls-files src | grep -i agarilux`: the only AgariluxPrime PNG left is `src/RimMandrake/TheRot/Textures/RotSpecies/AgariluxPrime.png`.
- Ran a wider git grep for `AB_AgariluxPrime` (bare name, all of the repo except whittle/) than the builder's search. The
  extra hits are comments naming the donor def (RM_RotSporeKit_GuardianGroves.xml, RM_TheRot_DonorPorts.xml),
  `AB_AgariluxPrime_Mutator` (a different def), and three Transient/ files (one-time human-read sheets). None of them reads the deleted texture.
- Survivor blob: `9d83052dca` ('Land the 4 v3 regens', 2026-09-20) blob 28b1e08b... equals HEAD's TheRot blob; the deployed
  copy's sha256 is 85779af9..., which matches the art ledger.
- The gptredo_03 decisions.jsonl rows: TheRot ACCEPT judged sha b0a767dc..., UtinniPatches REGEN judged sha c93606ba...;
  neither is the survivor's 85779af9....
- Read the item file's Decision section (the statement requires it to be there) and the landing diff 45408f140e.

## Statement lines

1. **One owner is decided and recorded: TRUE.** The item file has a "Decision, 2026-11-11" section naming TheRot
   (mandrake.rm.biomes) as owner. The reason given is what the game loads: the only definer is TheRot, and the final texPath is
   `RotSpecies/AgariluxPrime` after the TheRot repoint, which the 2026-11-02 full-list dump confirms. `resolved_texpath_before.txt` reads the base def
   and the repoint from git at the parent commit, and `resolved_texpath_after.txt` section 2 lists every patch op on the def (19 ops, 0 on texPath).
   broaden_checks B evaluated 69,195 xpaths across the 316-mod load set and found none reaching graphicData/texPath.
   I checked the dump myself and it agrees.

2. **Exactly one copy of the texture ships: TRUE.** Both donor-slot PNGs are gone from src (landing diff: 124588 B and
   253476 B deleted), and the only AgariluxPrime PNG left in src is the survivor. `search_after.txt` reports 0
   live-reader hits. Each OTHER-DEF hit is labelled with the donor def AB_AgariluxPrime it serves, or as a docstring
   example. The art ledger has retire events for both copies (`art/events/CLAUDE_ARCHMAGI_OFFLINE2.jsonl`, sha null, prev =
   the two judged shas). The art-eval hits are append-only run records (gptredo_03). I checked that the unfiled UtinniPatches row in
   `gptredo_03/regen_jobs.json` has no `regen_filing.json`, so `auto_judge.unfiled_rows` will not pick it up.

3. **Every inbound reference is fixed: TRUE.** The same commit changed the base def's texPath, deleted the repoint
   patch, and wrote the art-ledger retire rows. Both deploy plans show the deployed copies as
   `- ... deleted in repo -- --apply prunes it`. validate_patch.py is OK on the three touched patch files and the def file (0 errors; the 396 warnings
   are add-if-missing conditional shapes in PlantTolerances_Ashkarr.xml for every plant, so they were there before this change). The 3 selftests are GREEN. The
   unproven_adjudicate --check and the art_sheet resolution check agree with the change.

4. **The surviving copy's judgement stands: TRUE.** The evidence shows the statement's premise was wrong: there were three
   copies, and the survivor (the drawn `RotSpecies/AgariluxPrime` v3) is neither gptredo_03 subject. Both gptredo_03 rows
   are quoted (ACCEPT b0a767dc on the 256 px TheRot donor-slot file, REGEN c93606ba on the UtinniPatches file), and both of
   those files were retired. The survivor's standing judgement is the owner's 2026-09-20 approval ("The rot art is approved."). It
   came after the v3 landing commit and covers byte-identical content (I confirmed the blob). The item's rule says to re-judge
   only if the REGEN copy survives, and it did not, so no re-judge is owed. The root cause (art_sheet's slot scan ignores
   patches, so gptredo judged pictures the game never drew) and 11 sibling Rot ports with the same split are filed as items
   (ledger lines 10-11).

## Where the evidence is weak, staged or flattering
- The survivor's only judgement is a blanket owner sentence that ratified an agent prefill row. `judgement_record.txt`
  says so plainly, and no row-level owner look or art-eval pass has ever judged the drawn picture. That is enough under
  the item's rule, but it is the thinnest point.
- In `resolved_before.sh`, the closing "resolution BEFORE", "live game agreed" and "owner" lines are hardcoded echo
  text written to look like output. Its claim "UtinniPatches is not in the active mod list" is at best imprecise:
  mandrake.rut.patches is active in `ModsConfig.FULL.LATEST.xml`, and the 2026-11-02 dump loaded it at order 296. The deploy
  plan's "not enabled" refers to the game's current ModsConfig. This does not change the outcome, because nothing drew
  that slot either way.
- broaden_checks A puts src first, so for UtinniPatches it reads the post-change repo, and for biomes it reads the stale
  deployed copy. That makes it a mixed before/after view, not a clean census.
- In `bulk_accept_plan_agarilux.txt`, the artpipe done/ scan is filename-only because a full-content grep timed out. The job
  `dregen_RM_AgariluxPrime_ABAgariluxPrime_v1` still has `install_to` set to the retired path. The current plan does not see it,
  but the evidence never says why.
- `three_copies_before.png` is a flat side-by-side still, which is all this item needs. It is not an in-game look.
- Observation for the parent to file (I was told to write only this file): the survivor is a 4096x4096, 27 MB PNG for
  one plant. That is outside this item's scope, but it may be a texture-memory or load-time cost.
- The deployed game still holds both retired copies until the next biomes/UtinniPatches deploy. That is expected for an
  offline item.

would show: yes
