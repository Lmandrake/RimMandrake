# Dead and redundant mod-list entries, 2026-10-16

Owner: "Remove all dead entries." / "yes, remove redundant mods." Instrument: About.xml packageId of every folder in both mod roots
(Steam Mods, 1379 folders, 1378 with a packageId, 1378 unique, no duplicates; workshop root included), case-insensitive; probe found
brrainz.harmony and mandrake.rm.biomes; Ludeon.RimWorld* excluded as core/DLC. Run on the live list, the found-live backup and FULL.LATEST (all 551 entries).

| packageId | kind | why |
|---|---|---|
| vlvop.tormentmaster.expansion | DEAD | not installed in either root; nothing of ours depends on it (only records/ideo savefiles mention it) |
| mandrake.rm.explosivegrowth | DEAD + REDUNDANT | no standalone folder; folded into mandrake.rm.biomes (Biomes/_Kits/ExplosiveGrowth deployed) |
| mandrake.rut.plantgrowth | REDUNDANT | listed in Biomes.compose.json `absorbed`; its roster and RUT_BloomBurst now in UtinniPatches (deployed); loading both multiplies growth x16 |

No duplicate packageIds in activeMods. Removed from: live ModsConfig.xml, infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml;
551 -> 548, knownExpansions and version unchanged. Backups: deployed/config/ModsConfig.pre-dead-removal-20261016.xml (live before),
deployed/config/ModsConfig.full-post-dead-removal-20261016.xml (new dated copy; the found-live file is untouched).
Left alone: historical snapshots, ideology saves (.xtp/.rid), restructured_model_v4.json (research data), the deployed Mods/PlantGrowth folder
(src/RimUtinni/PlantGrowth still exists, so deploy --prune does not treat it as removable).
