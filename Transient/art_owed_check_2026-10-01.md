# Art owed check, 2026-10-01

Items: `FORGE_MISSING_ART_1`, `WARCASKET_CASK_ART_1` (both BLOCKED in FOUNDRY queue; neither has an `items/<ID>.md` prose file, subjects taken from the queue titles). Read-only check, nothing queued or edited.

Method: python walk of `infrastructure/artpipe/{done,pending,active,failed,_artsrc,_withdrawn}`, plus `registry.jsonl`, `art_status.json`, `Transient/*.decisions.json` (16 files). Sanity probe: `Brindeth` found in done (2), _artsrc (2), registry (7), art_status (2). `pending/` exists and holds 0 jobs (probe 0, as expected: the daemon has drained it); `active/` holds 0.

| subject | exists? | path | ruled? | what remains owed |
|---|---|---|---|---|
| RUT_TibannaGas | YES, generated, validated pass | `D:\Luke\dev\RimMandrake\infrastructure\artpipe\_artsrc\RUT_TibannaGas\RUT_TibannaGas.png`; done job `...\artpipe\done\RUT_TibannaGas.json`; wired copy `D:\Luke\dev\RimMandrake\src\RimUtinni\UtinniPatches\Textures\Things\Item\Resource\RUT_TibannaGas\RUT_TibannaGas_a.png` | no decision in any `.decisions.json` | nothing to generate; owner look at the render only if wanted. Item blocked-line is stale for this subject |
| RUT_FoundryTowerEntrance | YES, generated, validated pass | `...\artpipe\_artsrc\RUT_FoundryTowerEntrance\RUT_FoundryTowerEntrance.png`; wired copy `D:\Luke\dev\RimMandrake\src\RimUtinni\UtinniPatches\Textures\Things\Building\Production\RUT_FoundryTowerEntrance.png` | no | nothing to generate |
| RUT_FoundrySalvageCache | YES, generated, validated pass | `...\artpipe\_artsrc\RUT_FoundrySalvageCache\RUT_FoundrySalvageCache.png`; wired copy `D:\Luke\dev\RimMandrake\src\RimUtinni\UtinniPatches\Textures\Things\Building\Production\RUT_FoundrySalvageCache.png` | no | nothing to generate |
| RM_CinderCrust | NO (no file in done, _artsrc, failed, registry, art_status, decisions, or any src Textures) | def `D:\Luke\dev\RimMandrake\src\RimMandrake\TheForge\Defs\ThingDefs_Plants\RM_TheForge_Flora.xml` (texPath `Things/Plant/RM_CinderCrust`, no PNG behind it) | no; identity unruled (`design\Jawa\worldbuilding\biomes\forge_bedazzle_cast_2026-09-29.md` row says identity regen owed) | OWED, and correctly gated: the plant's identity line must be written before any art is queued (queue `blocked:` line) |
| RM_CaskBay | YES, generated (256x256, validator skipped: no reference) | `...\artpipe\_artsrc\RM_CaskBay\RM_CaskBay.png`; done job `...\artpipe\done\RM_CaskBay.json` (rimflow_item_id WARCASKET_CASK_ART_1) | no | NOT WIRED: no PNG under `D:\Luke\dev\RimMandrake\src\RimMandrake\Warcasket\Textures\Things\Building\RM_CaskBay\`; copy render to the def texPath `Things/Building/RM_CaskBay/RM_CaskBay` (also remove the "ART: none generated" comment). Owner has not looked. Do not confuse with `RM_WasteCaskBay` (Wasteland mod; 3 facings sit in `failed/`) |
| RM_HalfExtractedCore | YES, generated (256x256, validator skipped) | `...\artpipe\_artsrc\RM_HalfExtractedCore\RM_HalfExtractedCore.png`; done job `...\artpipe\done\RM_HalfExtractedCore.json` | no | NOT WIRED: copy to `Warcasket\Textures\Things\Item\Resource\RM_HalfExtractedCore\RM_HalfExtractedCore.png` and drop the BLOCKED comment in the def |

## Counts
Exists 5 of 6 (3 already wired, 2 rendered but unwired). Owed 1 (RM_CinderCrust, gated on a design identity line). Wiring owed 2.

Caveats: `registry.jsonl` has no queued/generated events for RM_CaskBay or RM_HalfExtractedCore under those exact target names (only the done job files prove them); `RM_WasteCaskBay` is a different subject. The FORGE queue line "No render anywhere" is stale for three of its four subjects.
