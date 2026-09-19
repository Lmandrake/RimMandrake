# DROID_DISTRESS_CALL_REPOINT_1

## Spec
Ruling 13 (`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0): "Distress
Call quest: re-point to DW kinds - it becomes the wild/crashed-droid rescue."
§5 row C7: patch `btd.gbp.shippack.kotor.vge`'s 5 (see Correction below)
`KotORDroidColonist_*` refs to Droidworks kinds; reframe as the crashed/wild-
droid rescue. Verify: "quest offers and completes with DW pawns." Narrowed by
the filing brief to a kind-repoint + text pass on the EXISTING quest content -
explicitly not `DROIDWORKS_WILD_DROIDS_1`'s (E4) new incident mechanic.

## Open question answered: yes, LoadFolders-gated
`DROID_PROGRAM_STATE_2026-09-06.md` asked whether the quest sub-mod is
`LoadFolders`-gated on `guy762.KotORDroids`. Confirmed by reading both mods'
own `LoadFolders.xml` on disk:

- `btd.gbp.shippack.kotor.vge` (workshop 3614012898):
  `<li IfModActive="guy762.KotORDroids">1.6/Mods/BTD_KotOR_Droids/</li>`
- its dependency `btd.remix.gravshipblueprints` (workshop 3575162262) ships a
  **byte-identical duplicate** of the same folder, gated:
  `<li IfModActiveAll="guy762.KotORDroids,btd.gbp.shippack.kotor.vge">1.6/Mods/BTD_KotOR_Droids</li>`
  (and a second line for the non-VGE shippack variant).

So the `IncidentDef`/`QuestScriptDef`/`SitePartDef` for `BTD_DroidDistressCall`
do not exist at all unless `guy762.KotORDroids` is active - **both copies load
simultaneously** when the full mod list is active (confirmed below), which is
why the patch's guard is `PatchOperationConditional` on the target node, not
`MayRequire`/`FindMod` on a mod name (rimworld-modding's own doctrine: those
check the mod, Conditional checks the def, and the def's existence here is a
`LoadFolders` fact, not just an installed-mod fact). Once `guy762.KotORDroids`
retires (D2), this folder stops loading in both copies and the patch becomes a
harmless no-op forever - the donor-independent successor is `DROIDWORKS_WILD_DROIDS_1`
(E4), out of scope here.

## Correction: 19 kinds, not 5
The design doc's "MEASURED" note names 5 sample defNames
(`{T3UD,SentWD,R8009UD,MPDMkI,KX12UPD}`). Read live off both the workshop disk
copy (`BTD_IncidentDef_DroidDistressCall.xml`'s `rewardDroidKindDefs` list) and
the current live def dump's pre-patch `BTD_DroidDistressCall` `IncidentDef`
(capture `2026-09-08T21-25-01Z`, 600 mods including `guy762.KotORDroids` and
both BTD ship-pack mods): the list actually names **19** `KotORDroidColonist_*`
kinds. All 19 confirmed as real `guy762.KotORDroids` `PawnKindDef`s (their own
`PawnKinds_PlayerDroids.xml`) and all 19 have a pre-existing 1:1 Droidworks
absorption in `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`
(`RSW_DW_KotORDroidColonist_<same suffix>`) - the 5-name sample was simply an
incomplete transcription; the real number and the full list are recorded here
so nobody re-derives it wrong a second time.

## Built
`src/RimStarWars/Droidworks/Patches/BTD_DistressCall_Repoint.xml` - one
`PatchOperationConditional` (guard: the target node exists) wrapping a
`PatchOperationReplace` that swaps the whole `<rewardDroidKindDefs>` list for
the 19 `RSW_DW_KotORDroidColonist_*` equivalents, 1:1 by suffix:

| donor (guy762.KotORDroids) | Droidworks |
|---|---|
| `KotORDroidColonist_T3UD` | `RSW_DW_KotORDroidColonist_T3UD` |
| `KotORDroidColonist_3CUD` | `RSW_DW_KotORDroidColonist_3CUD` |
| `KotORDroidColonist_ITUD` | `RSW_DW_KotORDroidColonist_ITUD` |
| `KotORDroidColonist_R8009UD` | `RSW_DW_KotORDroidColonist_R8009UD` |
| `KotORDroidColonist_GE3LD` | `RSW_DW_KotORDroidColonist_GE3LD` |
| `KotORDroidColonist_GE3PD` | `RSW_DW_KotORDroidColonist_GE3PD` |
| `KotORDroidColonist_KX12UPD` | `RSW_DW_KotORDroidColonist_KX12UPD` |
| `KotORDroidColonist_KX12APD` | `RSW_DW_KotORDroidColonist_KX12APD` |
| `KotORDroidColonist_MPDMkI` | `RSW_DW_KotORDroidColonist_MPDMkI` |
| `KotORDroidColonist_KM1MD` | `RSW_DW_KotORDroidColonist_KM1MD` |
| `KotORDroidColonist_KM1HMD` | `RSW_DW_KotORDroidColonist_KM1HMD` |
| `KotORDroidColonist_SentWD` | `RSW_DW_KotORDroidColonist_SentWD` |
| `KotORDroidColonist_DevWD` | `RSW_DW_KotORDroidColonist_DevWD` |
| `KotORDroidColonist_DevAD` | `RSW_DW_KotORDroidColonist_DevAD` |
| `KotORDroidColonist_ADMkI` | `RSW_DW_KotORDroidColonist_ADMkI` |
| `KotORDroidColonist_ADMkI_sf` | `RSW_DW_KotORDroidColonist_ADMkI_sf` |
| `KotORDroidColonist_ADMkIV` | `RSW_DW_KotORDroidColonist_ADMkIV` |
| `KotORDroidColonist_ADMkIV_sith` | `RSW_DW_KotORDroidColonist_ADMkIV_sith` |
| `KotORDroidColonist_GOTO` | `RSW_DW_KotORDroidColonist_GOTO` |

Read `rimworld-quests` skill in full before touching anything (task
requirement). Consequence for scope: the `QuestScriptDef` node tree itself
names **no** kind defName anywhere - kind selection is entirely inside the
`IncidentDef`'s `modExtension`, consumed by the (compiled, unmodified)
`RWM_BTD_Remix_GravshipBlueprints.BTD_IncidentWorker_DroidDistressCall`
workerClass. So no `QuestScriptDef` patch was needed or written.

## Reframe text - none needed
Checked every player-facing string (`questNameRules`, `questDescriptionRules`,
`letterLabel`, `letterText`) for KotOR-specific language. None exists: the
quest already reads as a generic "distress call from a crashed freighter" /
"the other droids being transported as cargo have gone haywire and become
hostile" rescue, and every reward `PawnKindDef`'s own `label` is already
generic ("war droid", "protocol droid", "specialist droid" - never "KotOR"
anything). The kind repoint alone completes ruling 13's reframe; no text patch
was written.

## Explicitly out of scope, left untouched
- `hostileFactionDef guy762_KotORFaction_RogueDroids` (label "rogue droid
  collective", hidden `FactionDef`) - the site's hostile spawn faction. Ruling
  2 bans a rogue-droid faction going forward, and §7 item 1 of the design doc
  already retires this concept alongside `guy762.KotORDroids` itself (D2/E4).
  Repointing which faction fields the site's hostiles is a mechanism change,
  not a kind-repoint-and-reframe; left for whoever executes D2 or E4.
- `eligibleShipLabels`, the `SitePartDef`, the `QuestScriptDef` node tree -
  none names a KotOR-specific kind or donor string.
- `DROIDWORKS_WILD_DROIDS_1` (E4)'s own mechanic (factionless spawning,
  capture-to-Wild-spike, reprogram-as-recruit) - a separate unbuilt item, not
  built here per the filing brief.

## Verify
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/RimStarWars/Droidworks/Patches/BTD_DistressCall_Repoint.xml')"` - well-formed.
- `validate_patch.py` against `--mods-config infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
  (600 mods, the full campaign list that actually includes both BTD ship-pack
  mods and `guy762.KotORDroids`) + `--defs` pointing at the RimWorld `Mods`
  folder, the full Steam Workshop content root, and `deployed/`: **`OK - 0
  errors, 0 warning(s)`**. The operation correctly hits **both** duplicate
  copies of the target def (`[BTD] Gravship Blueprints` and `[BTD] Ship Pack:
  KotOR Ships VGE`, 1 match each) - expected, not a bug (validator's own note:
  "do NOT add a positional predicate to 'fix' it").
- Re-ran with `--live` against the `2026-09-08T21-25-01Z` capture (600 mods,
  same full list, `mandrake.rsw.droidworks` + `guy762.KotORDroids` + both BTD
  mods all active in that capture): same `OK - 0 errors, 0 warning(s)`, and
  directly confirmed in the dump's own JSON: the pre-patch `BTD_DroidDistressCall`
  `IncidentDef` names exactly the 19 donor kinds listed above, and all 19
  `RSW_DW_KotORDroidColonist_*` replacement kinds exist as real live
  `PawnKindDef`s in the same capture.
- **Live/bridge quest-offer or -completion test: NOT attempted.** `rimflow
  bridge who` showed it held by another FOUNDRY window (C4, idle 5 min - not
  stale) at the time this item was built; per the filing brief's own
  instruction ("if held, don't wait, stop at offline validation") this closes
  on offline validation alone. The current live `ModsConfig.xml` is also a
  minimal ~30-mod list with neither BTD mod nor `guy762.KotORDroids` active
  (confirmed by direct read), so a live test right now would additionally
  require restoring the full list first - a second reason not to chase it in
  this pass.

## Assumptions recorded
- The 19-kind, 1:1-suffix mapping is taken as correct because both the donor
  and the Droidworks absorption were read live off disk/dump, not assumed from
  the design doc's stale 5-name sample.
- `PatchOperationConditional` (not `MayRequire`) is the deliberate guard choice
  per `skills/rimworld-modding/references/patch-operations.md`'s own guidance
  quoted above - not an oversight relative to the `IonBuildup_PowersDownDroid.xml`
  precedent (which uses `PatchOperationFindMod`, a weaker guard, for a
  different situation: a def that exists unconditionally once its owning mod
  is active).
- `hostileFactionDef` was deliberately left alone; see "out of scope" above.
