# ARMOURY_MW2_CUT_1 — cut ModularWeapons2 out of the KotOR Armoury entirely

Owner ruling 2026-09-13 (verbatim): *"remove those two gadgets, cut the mod
thoroughly, and restore Show Me Your Hands."* HIGH PRIORITY — a shipped
complexity reduction + it kills the SMYH×MW2 pawn-gen crash at its real root.

Supersedes the gate-only framing of `ARMOURY_MW2_DEP_UNGATED_1` (owner chose
cut over gate). Full evidence: `Transient/mw2_disentanglement_review_2026-09-13.md`.

## Why this is safe (verified, not assumed)
MW2 modularity on our KotOR content is UNREACHABLE and INVISIBLE in play:
- **0 `GunsmithPresetDef`s** exist for any KotOR weapon anywhere on disk →
  MW2's `RandomizePartsForPawn` early-returns → no NPC/trader/spawn ever
  carries a part. Only hand-attachment at the bench, which the owner ruled out
  (2026-08-03, `required_mods.md:723`).
- **All 207 parts inherit `NullTex`** (`ModularPartsMountsBase.xml:201`) →
  `Graphic_UniqueByComp` renders pixel-identical to a plain sprite → zero
  visual loss.
- Canonical start (`CANONICAL_ASHKARR_START_2026-09-12.rws`) serializes
  `<attachedParts />` empty on all 9 MW2-comp things.
- 0/181 comp-bearing defs have a stat/verb/tool that lives ONLY in a part —
  every weapon/armour degrades to a fully-functional plain item.

## Execution — ORDER MATTERS (strip defs BEFORE removing MW2 from ModsConfig)

1. **Strip the field-level MW2 usage** across Armoury's ~44 weapon/apparel/
   gadget files: remove the `ModularWeapons2.CompProperties_ModularWeapon`
   comp blocks (~181) and swap `graphicClass=ModularWeapons2.Graphic_UniqueByComp`
   → the plain vanilla graphicClass the def would otherwise use (Graphic_Single
   for most; verify per def). Prefer a generator/scripted pass over hand-edits;
   diff to a temp path and verify no other field is touched.
2. **Delete the 21 root-tag MW2 def files** (`<ModularWeapons2.ModularPartsDef>`
   / `ModularPartsMountDef`) under
   `src/RimStarWars/Armoury/Defs/Absorbed_AdditionalMods/kotorcore/ModularWeapons2/`,
   the 3 UpgradeItem defs, and the `guy762_KotORWorkbench`
   (thingClass=`ModularWeapons2.Building_GunsmithStation`) building.
3. **Delete the two gadgets that ARE their parts** (owner ruled remove):
   `guy762_wristlauncher` (whole function is MW2 slots) and the jetpack MISSILE
   attachment (the jump/jetpack apparel itself survives — remove only the
   missile part/verb that depends on MW2).
4. **Research cleanup**: drop the 3 now-orphaned research rows
   `guy762_ResearchKotOR_workbench/advupgrade/exupgrade` (defined in the still-
   active kotorcore donor — Cherry Pick or retag-drop; they'd otherwise sit
   researchable with nothing to build).
5. **Remove MW2 from ModsConfig** (`kaitorisenkou.modularweapons2`) — LAST of
   the def work, so nothing references a now-absent assembly on the next load.
   Cutting MW2 also silences kotorcore's own gated MW2 folder cleanly via its
   `IfModActive`.
6. **Invert `validation.py`'s min16 note** in Armoury if it asserts MW2 presence.
7. **Restore Show Me Your Hands** (`<li>mlie.showmeyourhands</li>`) to ModsConfig
   — SAFE now that MW2 is gone (no transpiler). Backup before/after.
   Current interim state: SMYH is DISABLED (BENCH removed it 2026-09-13,
   `Transient/ModsConfig.backup.20260913_183819.xml`) to hold the crash off
   until this cut lands; this step puts it back.
8. **Cold load + verify** (full list, or min+KotOR): 0 `TypeInitializationException`
   for ModularWeapons2, 0 red errors for `guy762_*` weapons; positive sighting —
   spawn a pawn holding `guy762_brifle`/`guy762_vblade`, confirm it renders and
   fires. Then **resave the canonical start** (back up Saves first, stat after).

## verify
MW2 absent from ModsConfig; Armoury loads with 0 MW2-related config errors;
KotOR weapons/armour spawn, render, and fight as plain items; wrist launcher +
jetpack missile gone with no dangling refs; SMYH active and drawing hands with
no pawn-gen crash; canonical start resaved and confirmed (new file, no silent
current-slot overwrite).

## Watch out
- Strip defs BEFORE pulling MW2 from ModsConfig or the root-tag defs error.
- `validate_patch.py` with BOTH --live and --defs after the strip.
- The deployed Armoury (2026-09-05) and the active kotorcore donor both define
  the same parts; last-loaded wins and the current log shows no dup lines —
  but re-check after the cut that nothing re-introduces them.

## Step 8 verify — done 2026-09-14

Prior session's steps 1-7 had committed the content strip but never DEPLOYED
it — the restart it triggered booted against a stale `Mods/Armoury` still
holding all 25 pruned files, so its own "0 TypeInitializationException"
reading was against the wrong tree. Re-verified properly this session:

1. `deploy_custom_mods.py --mod Armoury --apply --prune` synced the repo
   deletions to the live Mods folder (66 files deployed, 25 orphaned MW2
   files pruned) — confirmed via a `no_game` bridge check first, then a
   fresh Steam relaunch on the full 594-mod list.
2. Cold load: 0 `TypeInitializationException`, 0 `modularweapons2` hits.
3. Quicktest map, spawned pawns, equipped `guy762_brifle` and
   `guy762_vblade` — both resolve correctly (`jawa/pawn_get` confirms the
   equipped defNames), zero new log errors. Positive sighting: drafted the
   rifle-holder, ordered `AttackStatic` against an adjacent hostile — it
   fired and downed the target (`[Ninefold] ... downed in battle: Kit`),
   confirming render+fire, not just equip.
4. **A second, unfiled class of defect found while chasing "no lingering
   issues"**: 86 dangling `<li>guy762_KotORWorkbench</li>` (recipeUsers) /
   `<ThingDef>guy762_KotORWorkbench</ThingDef>` (descriptionHyperlinks)
   references across 18 Armoury def files — step 2 deleted the workbench
   ThingDef but never swept the ~90 items whose recipeUsers/hyperlinks
   pointed at it, which is what the boot log's 24 "Could not resolve
   cross-reference ... wanter=recipeUsers" lines and 1
   `DefHyperlink` line were. Removed all of them (verified every candidate
   defName absent from the whole repo first). Of the 18 files, only 6 are
   actually deployed (`Absorbed_KotorWeapons/*`) — the other 12 live under
   `Absorbed_KotorCore/`, held/undeployed while the kotorcore donor mod
   stays subscribed, so those fixes have no live effect today but stop the
   bug from resurfacing if that donor is ever retired. Also removed 50
   dead `<li>` loot-table entries in `Absorbed_KotorCore_KotORResource_
   JunkPile.xml` (`<mineableThing>` pointing at deleted MW2 part defs,
   e.g. `guy762_scopeitem_accuracy`) — same held/undeployed caveat.
   **Not re-verified against a second cold boot** (defs only parse at
   startup, and a third ~20min restart wasn't spent proving a log line
   silences) — logically sound (every removed defName confirmed absent
   repo-wide, XML re-validated well-formed, `validate_patch.py` shows 0 new
   errors) but worth a glance at the next natural boot's log.
5. The 3 `guy762_ResearchKotOR_workbench/advupgrade/exupgrade` research
   projects and `guy762_armband_wristgun` "Could not load reference to"
   lines during save-load were investigated and are SAVE-side residue only
   (the research projects are confirmed already absent from the live
   DefDatabase via an earlier unrelated research-tree ruling, not this
   item; the wristgun/blueprint refs are dead Scribe references with no
   live-def counterpart) — exactly what step 8's resave exists to clear,
   not a defs-side bug.
6. Backed up `CANONICAL_ASHKARR_START_2026-09-12.rws` (md5
   `ff87730ff0ca1304b8a8aa0e5befb380`, 16000222 bytes) to
   `Transient/saves_backup_2026-09-14_mw2cut/`, loaded it with
   `ignoreModCompatibility` (594 recorded mods vs 589 active — MW2 is 1 of
   5 expected-missing, the other 4 are pre-existing unrelated gaps outside
   this item's scope), resaved to the SAME name. New file: 16372486 bytes,
   md5 `c7595e68e272b9e70c16bd09394585d9` — genuinely rewritten, same
   single slot (no stray file created). Confirmed 0 mentions of
   `modularweapons2`/`guy762_KotORWorkbench`/`guy762_armband_wristgun` in
   the resaved file (down from 14 in the backup); the `Techprint_guy762_
   ResearchKotOR_*` hits that remain are a different, still-valid ThingDef
   family (techprint items), not the cut research projects.
7. `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1`'s own verify criteria (map+pawn
   gen with 0 `InvalidProgramException`, a pawn spawns holding a weapon)
   are satisfied by steps 2-3 above — closing it alongside this item.
