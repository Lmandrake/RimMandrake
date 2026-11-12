# JUDGE: AGARILUX_PRIME_COPIES_RECONCILE_SPLIT

Judge: CLAUDE_ARCHMAGI_OFFLINE2 judge helper, 2026-11-11. Blind to DONE.md and BROADEN.md. I read STATEMENT.md, NOTES.md,
every file in evidence/, the item file (where line 1 says the decision must be recorded), the commit 45408f140e diff, and
the image three_copies_before.png. I re-ran both scripts against the current tree (/tmp/judge_resolve.txt,
/tmp/judge_search.txt). Both match the committed evidence. I also ran my own checks, listed below.

## Line by line

1. **One owner is decided and recorded: TRUE.**
   - The item file has a dated "Decision, 2026-11-11" section: TheRot (mandrake.rm.biomes) owns the def and the texture. It
     gives the reason from what the game loads.
   - resolved_texpath_before.txt reads the def chain from git at the parent commit. The base texPath was
     `Things/Plants/AB_AgariluxPrime`, and the TheRot Conditional/Replace changed it to `RotSpecies/AgariluxPrime`.
   - resolved_texpath_after.txt section 4: the live def dump (2026-11-02, 317 mods, fingerprint 228dc89a) reads texPath
     `RotSpecies/AgariluxPrime` from mandrake.rm.biomes. AB_AgariluxPrime has no row, and a sanity probe shows the
     instrument can see.
   - broaden_checks.txt covers load order: 3137 patch files and 69195 xpaths across the 316-mod load set. None of them
     reach graphicData/texPath.

2. **Exactly one copy of the texture ships: TRUE (in src/, which is how the line defines it).**
   - `git ls-files` lists one AgariluxPrime PNG under src: `TheRot/Textures/RotSpecies/AgariluxPrime.png` (sha 85779af9).
   - I searched the whole repo for the stem `AB_AgariluxPrime` myself (125 files). Every hit in src/ is a donor defName in
     a comment, the retire script, or the new def comment. Nothing reads the deleted path.
   - `art.py status Things/Plants/AB_AgariluxPrime` shows no LIVE row and "slots: (none in our defs)".
   - Not yet done: the copies already deployed in Steam Mods (RimMandrake.Biomes/.../Things/Plants/AB_AgariluxPrime.png and
     UtinniPatches/...) stay on disk until the next deploy. The deploy plans in evidence/ show `-` prune lines for both.
     Neither file is drawn, so the game looks the same with or without them. A deploy is owed, not a fix.

3. **Every inbound reference is fixed: TRUE.**
   - Commit 45408f140e moves `RotSpecies/AgariluxPrime` into the base def and deletes the repoint, so src readers and the
     game now agree. It also deletes both PNGs and writes two art-ledger retire events (prev shas b0a767dc and c93606ba).
   - My search found no deploy manifest, def, patch or art-eval brief still naming the deleted path.
   - One artpipe job still names the retired install_to: `dregen_RM_AgariluxPrime_ABAgariluxPrime_v1` in
     D:\ClaudeWork artpipe done/. I checked bulk_accept_renders.load_jobs. It skips any job whose `_artsrc/<id>/<id>.png`
     is missing, and that directory does not exist, so the hourly installer cannot put the file back. That matches
     bulk_accept_plan_agarilux.txt.
   - The remaining hits are dated sheet snapshots and append-only event logs.
   - Checks: validate_patch.txt passes 3 patch files with 0 errors (396 advisory nomatch warnings, none on texPath).
     validate_def.txt shows 0 errors on the def file. selftests.txt is GREEN 3/3: alpha_plants_renders, hugethings_lint and
     hugethings_footprint. The footprint test covers the `<texture>AgariluxPrime</texture>` variant key, which belongs to
     the survivor's stem.

4. **The surviving copy's judgement stands: TRUE.**
   - The statement assumed the survivor would be one of the two gptredo_03 copies. It is neither, and the evidence says so
     plainly. judgement_record.txt lists both gptredo_03 rows: the TheRot ACCEPT row judged the 256 px
     Things/Plants/AB_ copy (sha b0a767dc), and the UtinniPatches REGEN row judged sha c93606ba. Both are retired.
   - The survivor is the 4096 px v3 (sha 85779af9). Its git blob is identical to the one in the 2026-09-20 v3 landing
     commit. The owner approved it in the 2026-09-20 Rot landing ("The rot art is approved."), after that commit. The
     evidence notes that this was a blanket ratification of prefill rows, not a row-by-row look.
   - The item's rule is to re-judge only if the REGEN copy survives. It did not, so no re-judge is owed.
   - I checked the four later sheets that showed RM_AgariluxPrime (gptredo_03 shadow, gpt_review_therot 10-24,
     therot 11-03, flora_legibility 11-05). All are reviewStatus "prefill" with no human pick, so deleting the 256 px
     ACCEPT copy goes against no owner ruling.
   - The image shows three different designs. The survivor is the purple, spreading spore-cap with hyphae roots, which
     matches the art-eval brief's departures (pale, a spore pall, a root mat). The deleted ACCEPT copy is a
     different-looking bulb-tree.

## Where the evidence is thin or flattering

- All live-game evidence comes from a 2026-11-02 dump taken before this change. The after state is shown only offline.
  The risk is low, because the base def now holds exactly what the patch used to produce. This is an offline seat.
- resolved_texpath_before.txt says both donor-slot copies "shipped and loaded". UtinniPatches is not enabled in
  ModsConfig (deploy_plan_UtinniPatches.txt), and broaden_checks A finds no UtinniPatches copy in the active load set.
  The item's own premise, "one shadows the other at load", was also wrong. These are small factual slips that do not
  change the result.
- art_ledger_status_after.txt prints the RotSpecies/AgariluxPrime block twice. This is cosmetic.
- The survivor is a 4096x4096 PNG of 27 MB. That is out of scope here, but it is very large for one plant texture.
- The root cause (artledger.scan_def_slots ignores texPath patches, which mislabelled the IN GAME column) is filed as
  RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES. Other v3 repoints in RotSpecies_NamesAndSizes.xml (for example
  RM_RecurvedStropharia) may be mislabelled the same way until that item is fixed.

## Owed after this item (not blocking)
- Deploy mandrake.rm.biomes (and UtinniPatches if it is ever enabled) with --apply so the stale undrawn copies are pruned.

would show: yes
