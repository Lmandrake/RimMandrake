# SALVAGE_WRECKAGE_EVERYWHERE_1 — wave 2 (FOUNDRY helper, offline)

## 1. Art install (wreck_* renders)
DONE 9c63abbb5: 41 renders installed via `artpipe_state.py collect` (art ledger, reason artpipe-collect);
24 children got texPath + measured shadow (Scald ratio 0.70/0.63 x mean alpha bbox). 10 worker_error
flakes requeued (failed/ -> pending/). Still placeholder: RM_ContagionWreckFragment,
RM_FeverWoodWreckCarapace, RM_StillsandWreckTread. validation.py now checks texPath PNGs + shadow.

## 2. Smaller offline pieces
- Forge cache loot: DONE 938558741 (Carapace child, RUT_WreckWeathering_ForgeWarm + RUT_SalvageLoot_Foundry;
  still DEPLOY_HOLD with the F4 tower chain, whose 'no art yet' reason was false)
- Wasteland sarcophagus + radiation hazard: DONE 2d8bcc7c9 (RM_WastelandWarcasketSarcophagus,
  Carapace+1=Sealed; Irradiated doses ToxicBuildup 0.12 x (1-ToxicResistance); Wreck hazards setting)
- Grey Sea / Blue Desert mineable jackets: DONE 2d8bcc7c9 (ring of RM_BrineJacket / RM_BlueIceMineable
  laid by the wreck field; Grey shard extra table RM_SalvageLoot_GreyShards)
- Long Shade crawler road wreck list: DONE 0b118fbb5 (RM_WreckList_CrawlerRoad; RSW skiff/tread are list rows)

## 3. Step 9 offline half (RSW/RUT layers, Fall Line register)
DONE 938558741: RSW_FreshTIEPanelWreck, RSW_FreshLandspeederWreck; droid parts on all four rare tables;
RUT_FallLineWreck{Hull,Carapace}, RUT_WreckWeathering_FallLine, RUT_SalvageLoot_Imperial, RUT_WreckList_FallLine,
RUT_FallLineWreckFall (baseChance 0). 12 art jobs queued aebff1aac.

## L0 proof
Wreckage + LongShade validation.py STATIC PASS (new checks red-tested); validate_patch OK on every
changed file; run_selftests 212/214 (known env: tool_metadata, utinnipatches_dump).

## Remainder
See item prose `infrastructure/state/items/SALVAGE_WRECKAGE_EVERYWHERE_1.md` Open; ledger note 1b1712789.
