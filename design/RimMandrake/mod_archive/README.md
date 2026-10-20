# ALL_ORIGINAL_MODS: every mod that was ever on the owner's list

Owner, 2026-10-20: *"KEEP A FILE WITH ALL THE ORIGINAL MODS STORED so we can go back and reconsider things as we progress forward."*

`ALL_ORIGINAL_MODS.tsv` has one row per packageId found in any list of 100+ mods in `infrastructure/state/modlists/`
(every `ModsConfig.FULL.*`, backups, the `ModsConfig_5xx` snapshots) or in any committed version of `ModsConfig.FULL.LATEST.xml`
since its first commit (2026-08-19, the 583-mod backup), plus every Wave removed list. `about/<packageId>.xml` is the mod's own
About.xml (small text only) wherever its folder still exists on this machine or in `src/`.

| column | meaning |
|---|---|
| name, name_source | from About.xml on disk (`About.xml (disk)` / `(src)`), else `mod_facts.jsonl`, else `UNKNOWN` (workshop folder long gone) |
| workshop_id, folder_name, author, supported_versions | from About.xml / mod_facts where known |
| lifecycle, lifecycle_date, ruling_doc | `ACTIVE-380`, `RETIRED-WAVE1` (in PRE_WAVE1 542, absent from WAVE1_498; includes donor-free removals made between), `RETIRED-WAVE2` (118), `RETIRED-EARLIER` (gone before PRE_WAVE1; see `last_seen_list`), `DROPPED-BY-KEEPCUT` (Wave 3, owner 2026-10-20), `RETIRED-WAVE3` (6), `RETIRED-WAVE4` (50, `design/RimMandrake/retirement_register_wave4_2026-10-20.md`) |
| current_profile | DEV/TEST/AUTHORING/SHIP/PAINT per the `RULED_2026-10-20` lists (SHIP/DEV/TEST/AUTHORING) and the WAVE2 PAINT list; `-` when retired |
| reason, reconsider_when | the removal reason from the wave file, or the 07 profile reason for active mods; `reconsider_when` only where `07_deeper_drops.md` gives an add-back column |
| first_seen_list, last_seen_list | first and last list (file name, or `LATEST@<sha> <date>`) containing it |

Tool: `python3 src/RimMandrake/Utils/mod_archive.py build | check | add <packageId> --lifecycle ... --date ... --doc ... --reason ...`.
`check` exits 1 if any id in any list or wave removed list lacks a row. After a future retirement: update the wave removed file,
then `add` (manual rows live in `overrides.tsv` and survive `build`) or just re-run `build`, then `check`, then commit the TSV and `about/`.
Not hooked into anything. `RETIRED-EARLIER` rows carry no per-mod reason (those removals predate the wave files; the reason lives in that period's ledger).
