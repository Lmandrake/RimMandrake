# World remake 11: the keep/cut ruling applied (2026-10-20)

FOUNDRY helper, offline. Source: `Transient/retirement_keepcut_sheet_2026-10-20.decisions.json` (70 rows: 59 cut, 8 keep, 3 blank).
Applied by `design/RimMandrake/world_remake_2026-10-19/keepcut_apply.py` to the WAVE2 profile lists; `FULL.LATEST` and the live
ModsConfig are untouched. Archive of every mod ever listed: `design/RimMandrake/mod_archive/ALL_ORIGINAL_MODS.tsv`.

| profile | WAVE2 | RULED_2026-10-20 | file (`infrastructure/state/modlists/`) |
|---|---:|---:|---|
| DEV | 118 | 117 | `ModsConfig.DEV.RULED_2026-10-20.xml` |
| TEST | 206 | 153 | `ModsConfig.TEST.RULED_2026-10-20.xml` |
| AUTHORING | 226 | 173 | `ModsConfig.AUTHORING.RULED_2026-10-20.xml` |
| SHIP | 330 | 326 | `ModsConfig.SHIP.RULED_2026-10-20.xml` |
| PAINT | 81 | 81 (unchanged) | `ModsConfig.PAINT.WAVE2_2026-10-19.xml` |

Rule applied: **cut** = leave DEV, TEST and AUTHORING, stay in SHIP; the 4 **DROPs** leave every profile.

## Wave 3 (outright drops, owner-confirmed by the cut)
`gravtide.mod` (GravTide), `deon.rimtek.core`, `deon.rimtek.digipal`, `deon.rimtek.docmate`. They were TEST/AUTHORING/SHIP only; now in no profile.
Lifecycle `DROPPED-BY-KEEPCUT` in the archive. Not yet removed from `FULL.LATEST` or the live ModsConfig (a deploy step).

## Cuts that were already in no profile (6, no list change)
`rm.wreckedmachines`, `rut.greentideraidant`, `rut.rustcathedralroaches`, `rut.shokkweaveeconomy` (ours, not in the 380) and
`zacharyfoster.mineralsframework` / `mineralssparkle` (already Wave 2 drops). Ruling recorded; nothing to move.

## Undecided (blank): left where they are
- `boots.sensiblefactions`: stays in AUTHORING only. Audit: droppable after the paint; timing is his call.
- `petetimessix.researchreinvented`: stays in DEV/TEST/AUTHORING/SHIP. Audit wants a DEV-to-TEST demotion; everything is tuned against its research UI.
- `vanillaexpanded.vfearchitect`: stays in TEST/AUTHORING/SHIP. Needs the research-retag reference guarded first.

## Closure checks
For each RULED profile, every retained mod's hard `dependencies` (About.xml via `mod_facts.jsonl`) that were in the WAVE2 profile are still present:
**0 violations, 0 cuts restored.** No retained mod hard-depends on a dropped or moved mod.
Flag for the owner: `oskarpotocki.vfe.tribals` is cut (leaves DEV/TEST/AUTHORING) but is in PAINT. PAINT was left unchanged because the sheet scopes cut to DEV/TEST;
say the word and it leaves PAINT too (PAINT then loses a mod that Tribals' dependants `vanillaexpanded.vfecore` and others only soft-reference).
Keeps (8) change nothing: `7f.alienworlds`, `7f.alienworlds.tidallylocked`, `oblitus.mylittleplanet` stay AUTHORING+PAINT; `biomesteam.coreframework`, `zylle.morevanillabiomes` stay DEV..PAINT until the repaint;
`broms.deeporbit` until fixtures retire; `zal.biomeskit` with Geysers; `vanillaexpanded.vfepropsanddecor` SHIP.

## Salvation ideology re-save caveat (from 09_second_look.md)
`src/Jawa/ideoligion/The Salvation.rid:404` and `MandrakeJawa.xtp` name all 50 MOVE candidates as the active-mod stamp the editor writes into an ideo file.
Moving them out of DEV/TEST/AUTHORING makes the ideo files load with a missing-mod notice (harmless); **re-save the ideo under the new profile** to refresh the stamp.
The 4 Wave 3 drops fall under the same caveat if the ideo stamps them.
