# NONSW_XENOTYPES_SCOPE_1 — cut every remaining non-Star-Wars xenotype

## ruling
Owner, question card 2026-10-09 (BENCH note): cut all ~32 remaining non-Star-Wars xenotypes, same rule as the
twelve; repoint raider xenotype sets.

## done (FOUNDRY, 2026-10-18)
The dump (2026-10-16 capture, 115 XenotypeDefs) holds **31**, not 32: Alpha Genes 15 (`AG_*` + `VRE_Ocularkin`),
Phytokin 3, det.* 6, `BX_Beliar`, `HBX_Highborn`, `KAR_Orc`, `VRE_Archon`, `VRE_Fungoid`, `XylTitan`,
`BS_FrostJotunInBlue`.
1. **Spawn sets** (`src/RimUtinni/UtinniPatches/Patches/XenotypeCut_NonSW_SpawnSets.xml`): all 31 removed from
   every xenotypeSet (94 dump references, all top-level); the chance falls to Baseliner, as for the twelve.
2. **Cherry Picker SHIP** (`infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`, +184 typed keys, all
   validated by `cherrypick_build.check`): `XenotypeDef/<X>` for 26; for all 31 the Outland ascension gene,
   implanter ability+gene and the Alpha Genes meta/retromorphosis genes; scenarios `AG_ForsakenCrashlanded`,
   `AG_WretchScenario`, `BX_BeliarStart`. Typed only (`AG_Helixien` is also a HediffDef).
3. **Five defs kept, unreachable**: `VRE_Archon`, `VRE_Fungoid`, `VRE_Gauranlenkin`, `VRE_Animakin`,
   `VRE_Poluxkin` are named inside their own mod's assembly (DefOf or literal), the Sanguophage shape. Their
   real cut is retiring those three mods (filed as `VRE_XENO_MODS_RETIRE_DEFOF_HOLDOUTS`).
4. `KAR_Orc`'s "clan Gamorrean" relabel deleted from `OrcClan_GamorreanRename.xml` (faction rename kept).
5. **Canonical save** (`CANONICAL_ASHKARR_START_2026-09-12.rws`, iterparse): 2 carriers, neither on a map —
   `DV_Bogleg` Human62203 "Erika" (TradersGuild_Magister, world pawn alive), `BS_FrostJotunInBlue` Human469907
   "Gerd" (dead). None of the six cut-identity factions is on the world. Each carrier falls back with one Scribe
   "Could not load reference" on load.
Check: `src/RimUtinni/UtinniPatches/selftest_xenotype_cut_nonsw.py`.

## owed live
- L1 (next full-list load, SHIP applied): `cherrypicker.py --is-cut XenotypeDef/KAR_Orc --source live` true; no
  xenotypeSet in a fresh dump names any of the 31 (the selftest turns this into a live-leak check); Player.log has
  no new red beyond the two save carriers' Scribe lines and the Outland shared-list cross-reference noise.
- `validate_patch --defs` ran against the 15-mod tier list active now: disk matches UNMEASURED for the full list.
