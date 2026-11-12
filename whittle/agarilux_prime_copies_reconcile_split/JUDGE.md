# JUDGE — AGARILUX_PRIME_COPIES_RECONCILE_SPLIT (fresh judge, CLAUDE_ARCHMAGI_OFFLINE2 seat, 2026-11-11)

Read: STATEMENT.md, NOTES.md, every file in evidence/ (the image opened), the item file, commit 45408f140e's diff of
the def and patch, the art-ledger retire events, the 2026-09-20 owner-approval decisions file. Not read: DONE.md, BROADEN.md.
Re-ran: `resolve_agarilux_prime.py` and `search_losing_path.py` against the current tree; both outputs are identical to
`resolved_texpath_after.txt` and `search_after.txt` once timestamps are stripped. Re-ran selftests
`selftest_alpha_plants_renders.py` and `selftest_hugethings_lint.py`: PASS 2/2. Could not re-run `validate_patch.py --live`
(the offline-lane gate refuses it), so for that one I rely on the builder's `validate_def.txt` / `validate_patch.txt` (0 errors).

## Line 1: One owner is decided and recorded. TRUE
The item file now has a "Decision, 2026-11-11" section: TheRot (mandrake.rm.biomes) owns the def and the texture. The reason
comes from what the game loads. RM_AgariluxPrime is defined only in TheRot. Before the change its base texPath
`Things/Plants/AB_AgariluxPrime` was repointed by the RotSpecies_NamesAndSizes.xml Conditional/Replace to
`RotSpecies/AgariluxPrime` (`resolved_texpath_before.txt`, read from git). The 2026-11-02 full 317-mod def dump reads
RM_AgariluxPrime texPath = RotSpecies/AgariluxPrime from mandrake.rm.biomes, AB_AgariluxPrime has no row, and 0 dumped defs
name the old slot. A sanity probe confirms the dump can see the new path (`resolved_texpath_after.txt` section 4). After the
change the base def names RotSpecies/AgariluxPrime directly, and 0 of 69,187 xpaths across the 316-mod load set reach its
graphicData/texPath (`broaden_checks.txt` B). The decision also corrects the item text: there were three copies, and
neither gptredo_03 copy was ever drawn. That correction holds up: `three_copies_before.png` shows three distinct
pictures, and `deploy_plan_UtinniPatches.txt` shows UtinniPatches is not even enabled in ModsConfig.

## Line 2: Exactly one copy of the texture ships. TRUE (as the line defines it: src/)
Both donor-slot PNGs (TheRot 124,588 B and UtinniPatches 253,476 B) are gone from src. They were retired through the art
ledger (`art/events/CLAUDE_ARCHMAGI_OFFLINE2.jsonl`: two `live` events with sha null and prev = the two gptredo-judged
shas). The only `*AgariluxPrime*` PNG under src/*/*/Textures is `TheRot/Textures/RotSpecies/AgariluxPrime.png`. The
repo-wide search finds 0 live-reader hits. The remaining hits fall into four groups: this change's own comments, other-def
rows (donor AB_AgariluxPrime design data, a derived snapshot whose --check passes, a docstring), dated sheet/ruling
snapshots, and append-only ledgers. Each group is labelled. `art_ledger_status_after.txt`: the old slot has no def slot;
RotSpecies/AgariluxPrime is LIVE at 85779af91a06.
Note, not a caveat on the line: the deployed Steam copies of both retired PNGs still exist until the next deploy. Both
deploy plans list them as `-` prunes. They are not drawn by anything, and the offline lane may not deploy.

## Line 3: Every inbound reference is fixed. TRUE
The def and patch were updated in one commit (45408f140e): the base texPath was repointed and the now-redundant repoint
operation was removed, with a pointer comment left in its place. Art ledger: retire events recorded. Art-eval and
sheet tooling: `sheet_resolution_after.txt` shows art_sheet's src reader now resolves RotSpecies/AgariluxPrime, and
def_by_tex for the old slot is none. That fixes the misattribution that put the 256 px copy on the sheets as "IN GAME".
Artpipe: the one done job with install_to at the retired path (`dregen_RM_AgariluxPrime_ABAgariluxPrime_v1`) does not
appear in the hourly installer's plan. That job is a dated record, and the planner's sanity probe sees 104 dregen jobs.
Deploy manifests: both plans prune the old files. Validators: validate_patch 0 errors on the def and patch files;
selftests GREEN (I re-ran 2 of the 3).

## Line 4: The surviving copy's judgement stands, or it is re-judged. TRUE
`judgement_record.txt` quotes both gptredo_03 rows: the TheRot donor-slot copy (sha b0a767dc…) was ACCEPT, and the
UtinniPatches copy (sha c93606ba…) was REGEN. Both are retired. The survivor is neither of them. It is the v3 render the
owner approved on 2026-09-20 ("The rot art is approved.", approvedBy owner, row AB_AgariluxPrime keep). The git blob is
identical to the 'Land the 4 v3 regens' commit 9d83052dca, which I checked contains RotSpecies/AgariluxPrime.png, and the
approval is stamped after that landing. The survivor is not the REGEN copy, so the item's rule owes no re-judge.
The evidence is candid that this approval was a blanket verbal approval of a prefilled sheet rather than a judgement of
this row on its own. That is still the owner's judgement of these exact bytes, and it outranks a gptredo agent verdict.

## Staging / flattery check
- Nothing flattering found. The re-runnable scripts reproduce exactly against HEAD. The search lists every hit class,
  including the uncomfortable ones (append-only and dated records), and has a sanity probe.
- `three_copies_before.png` is a fair side-by-side rendered from git at the parent commit, at equal size on a neutral
  ground. It is a still, but nothing here needs motion.
- The live-game claim rests on a dump from 2026-11-02, before the change. The post-change claim is a src/patch xpath read,
  not a load. That fits an offline item and is stated openly.
- Out-of-scope observation: the survivor is a 4096 px, 27 MB PNG for one plant, which is heavy. Not this item's question.

would show: yes
