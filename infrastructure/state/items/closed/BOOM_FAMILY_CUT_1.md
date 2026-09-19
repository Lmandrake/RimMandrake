## spec
Owner, verbatim (2026-09-10): "the explosive Boom creatures should just be
cut independent of that sheet (they're ridiculous)." Cut the 15-creature
boom family: CherryPicker cuts with `cut(deftype,name)`, prove by
live-config readback; remove from biome-cast wildAnimals patches; rebuild
the tag->surviving-item index after (content-moderation trap); check
nothing else spawns/references them (traders, quests, chemfuel economy -
Boomalope milk).

## the 15, verified against real files (not guessed)
None of the 12 `GR_`-prefixed defNames resolved in the offline def dump
(stale for these mods) or the live bridge's bare-name lookup, so each was
read off the donor mod's own shipped XML on disk before touching anything:
`Boomalope`, `Boomrat` (Core), `VFEI2_Boomtick` (VFE Insectoids 2),
`GR_Bearalope`, `GR_Boomabear`, `GR_Boomalisk` (an Alpha-Animals-compat
submodule file, not the main hybrids file), `GR_Boombeetle`, `GR_Boomcat`,
`GR_Boomffalo`, `GR_Boomsnake`, `GR_Boomsquirrel`, `GR_Chickenlope`,
`GR_Manalope`, `GR_ParagonBoomalope`, `GR_Squirralope` (all Vanilla
Genetics Expanded). Independently corroborated: `design/Jawa/worldbuilding/
review/round2/build_review_deck.py` already carries an identical
`CUT_BOOM` set of exactly these 15 names.

## done
- **CherryPicker cut, proven live**: added all 15 to
  `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` (the
  ratified anchor — required; `cherrypick_build.py` refuses to write a cut
  that isn't ratified, by design, "changing what is cut is the owner's
  decision" — the owner's own words above ARE that ratification) and to
  `observed/inventory/decisions_animals.json` for provenance.
  `cherrypick_build.py --write` → 1963 keys written; none of the 15
  appeared in its "444 do not resolve" warning list (all real).
  `cherrypicker.py --source live --is-cut` verified CUT for all 15 against
  the freshly-written live settings file. Takes effect on the next load
  (Cherry Picker reads settings at def-load time) — not restarted this
  session.
- **wildAnimals biome-cast patches removed** (two live copies existed —
  `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` and an
  actively-maintained design-stage mirror at
  `design/Jawa/fauna/BiomeCast_Ashkarr.xml`, both fixed): `Boomalope`/
  `Boomrat` from Pyrelands.xml's Core roster, `Boomalope` from
  `ZBiome_Grasslands` (a whole-`wildAnimals`-replace Operation that existed
  ONLY to inject it — removed entirely rather than left replacing with an
  empty list), `VFEI2_Boomtick` from `RUT_Scarlands.xml` and from
  `Scarlands`' `BiomeCast_Ashkarr.xml` Operation (also removed entirely).
  No replacement creature substituted anywhere — that would be new design,
  not this cut.
- **Stat patches removed, surgically** (not by re-running the generators —
  see the trap below): 9 `ComfyTemperatureMin/Max` `Operation` blocks for
  the `GR_*` creatures in `AnimalTolerances_Ashkarr.xml`; 20
  `MeatAmount`/`BoneAmount` `<li>` blocks + 3 `milkAmount`/`woolAmount`
  blocks (`Boomalope`, `GR_Boomffalo`) in `MegafaunaYield.xml`. Diffs: 367
  and 255 lines, all deletions, nothing added — confirmed surgical.
- **`useMeatFrom` collateral fix**: `RSW_Absorbed_Protovermes.xml` had
  `<useMeatFrom>Boomrat</useMeatFrom>` — a LIVE field reference that would
  have failed to resolve once Boomrat is cut. Repointed to `Megaspider`,
  matching the pattern its own sibling files (`RSW_Absorbed_Baseopsis`,
  `_Holcorobeus`, `_Termitotron`) already used. The other 4
  `RSW_Absorbed_*` files mention Boomrat only in a historical comment, not
  a live field — left alone.
- **Vault dungeon guardian fixed at the generator source, not the generated
  XML**: `RUT_Symbol_Boomsnake` (`pawnKindDef GR_Boomsnake`) was placed once
  in Type-2's garrison ring by `gen_vault_layouts.py`. Removed the symbol's
  `PAWN_SYMBOLS` registration and its slot in `garrison_symbols` (6→5,
  cycling the remaining symbols rather than substituting a new creature),
  then re-ran the generator — `StructureLayoutDefs_Vaults.xml` and
  `SymbolDefs_Vaults.xml` regenerated clean, Boomsnake gone from both.
- **`cast_assignment.csv` (the design-stage roster source)**: removed the
  `Scarlands`/`VFEI2_Boomtick` and `ZBiome_Grasslands`/`Boomalope` rows —
  the only two of the 15 that appear there at all (the code comment in
  `gen_vault_layouts.py` claiming Boomsnake is "HorrorWastes-native
  (cast_assignment.csv)" does not check out; no such row exists).
- `validate_patch.py`, 0 errors, on every touched patch/def file.

## 🔴 trap hit and recovered from: regenerating from a curated CSV can
   silently re-allocate way more than the cut

`animal_tolerances.py --write` was tried first (the "proper" way, per its
own file header). It wrote to a DEAD path
(`src/Jawa/Jawa_Patches/Patches/...`, parked since the 2026-09-04
`JAWA_PATCHES_SPLIT_1` split and never updated) — fixed that stale hardcode
to the real live path (`src/RimUtinni/UtinniPatches/Patches/...`), a real,
separate, small bug this cut happened to trip over. Re-ran correctly — and
the output differed from the live file by **13,424 deletions against 1,704
insertions**, wildly more than 9 creatures' worth. **Reverted immediately**
(`git checkout --`) rather than trusting an in-place overwrite, per
`patch-a-curated-artifact-never-reallocate` — the live dump has drifted far
more than just this cut since the file was last generated, and a full
regen would have silently changed hundreds of other animals' tolerances in
the same commit as a 15-name cut. Removed the 9 boom blocks by hand
instead. `gen_megafauna_yield.py --write` was refused outright by its own
`LOADAFTER CHECK` guard (a real, separate, pre-existing gap: `gravtide.mod`
missing from `About.xml`'s `loadAfter` — fixed, small and clearly correct
per the tool's own instructions) — then tested with `--out <tmp>` before
touching the live file, found the same shape of unrelated drift (a
newly-unblocked GravTide yield group, several already-renamed/retired
`OuterRim_*` droid entries dropping out), and again removed the 9 boom
creatures' 23 blocks by hand rather than accepting the full regen. Both
generators' underlying gaps are now fixed for whoever next has reason to
run them for real — that regen is not this item's to do.

## NOT done / explicitly out of scope
- The `weaponTags → surviving-item` index (skills/rimworld-content-
  moderation) is a **weapon/apparel** mechanism (a pawn kind disarmed when
  every weapon carrying its required tag is cut) — it does not apply to a
  wild-animal cut; checked and confirmed not applicable rather than run
  the wrong instrument.
- `design/Jawa/worldbuilding/biomes/rosters/*.json` (7+ files) carry
  extensive curation-sheet PROSE treating Boomalope as a deliberate
  "in-joke KEEP" (owner card 2026-09-09) — directly superseded by today's
  ruling, but rewriting a whole design-review corpus's reasoning text is
  its own substantial task, owned by the design/worldbuilding side, not a
  tail end of this build item. Left as historical record; flagging for
  whoever next touches those rosters.
- `RSW_PROTOVERMES_TEXPATH_MISSING_1` filed separately: `validate_patch.py`
  surfaced a pre-existing, unrelated pink-placeholder texPath defect in
  the same file this item touched for `useMeatFrom` — confirmed via `git
  diff` that this item's edit never came near the broken `texPath` line.

## verify
`cherrypicker.py --source live --is-cut ThingDef/<name>` → CUT, all 15
(done, this session). `validate_patch.py` on every touched file → 0 errors
(done). A player-visible check (no Boomalope-family creature spawns, no
Boomalope milk/meat in storage filters, the vault's flesh-weapon-loose
garrison still generates with 5 guardians) is owed on the next real load —
not chased this session, per the same "hold on a restart while the owner is
mid-session" reasoning as `RUT_SCAVENGEREVENTS_BUILD_1`.
