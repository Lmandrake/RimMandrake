# MachineLooks: kept and candidate art (inventory at intake, 2026-11-23)

Measured from `design/specs/2026-11-20-vanilla-electrical-art-home/art/put_record.json` (the 26 art-store puts of
2026-11-20), the judge verdicts in `infrastructure/state/delegated/2026-11-20/{Battery,VEA_Icons}.json` (judge GPT via
`gpt_consult.py`, brief `design/RimMandrake/art_judge_brief.md`), the art store
`D:\ClaudeWork\rimmandrake\artstore\<sha[:2]>\<sha>.png` (each path below checked present on 2026-11-23), and for the
fridge the artpipe registry and the art ledger `infrastructure/state/art/events/BENCH.jsonl`. Nothing here is installed
in any mod. "Planned texture" is the put record's path, relative to the future mod's `Textures/RimMandrake/`.

## Battery (vanilla `Battery`, drawSize 2x3; 128 px per cell: north/south 256x384, east 384x256)

South reuses the north picture; west mirrors east. Judge: every row below KEEP.

| look | facing | size | art-store sha | planned texture | verdict |
|---|---|---|---|---|---|
| Scrapper | east | 384x256 | 5e83d9d23b7f30feeaa99bc60a86358e5af45752694f647ffe5babb97cb6f408 | MachineLooks/Scrapper/Battery_east.png | KEEP, round 1 |
| Scrapper | north (+south) | 256x384 | 99f88c5a7bc5542469c4359c38474bb083a47358b0ecb3e60191fb366cae3312 | MachineLooks/Scrapper/Battery_{north,south}.png | KEEP, round 1 |
| Industrial | east | 384x256 | 4c2fdad52e7a39690e66c454d90a5b5f1a92627ee938be3756d63a9002a50fa9 | MachineLooks/Industrial/Battery_east.png | KEEP, round 1 |
| Industrial | north (+south) | 256x384 | 293eeb6a8df1294e43b5c0bb68d1ea56107c10f50d98d2b44216d12f7117a18a | MachineLooks/Industrial/Battery_{north,south}.png | KEEP, round 1 |
| Modern | east | 384x256 | 27fc4e01430e976ae8a8227268664825643fa0cbb9df574d87eb1c1db6d2f5dc | MachineLooks/Modern/Battery_east.png | KEEP |
| Modern | north (+south) | - | none (not put) | MachineLooks/Modern/Battery_{north,south}.png | **REDO three times, OWED**: C2, the north facing is not the same size as the east (too small, then front face too tall, then too shallow). Item RIMMANDRAKE_REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE. Raw renders: `D:\ClaudeWork\rimmandrake\scratch\vea_20261120\raw` |
| Futuristic | east | 384x256 | 23eb88a4aba903936c59f8248c20c79af257c2b3d126627b095dff7c44eb6da1 | MachineLooks/Futuristic/Battery_east.png | KEEP, round 1 |
| Futuristic | north (+south) | 256x384 | 700ef80546e91ba4708334c0f2326fea084dd006dc07db92e0d28294539a5738 | MachineLooks/Futuristic/Battery_{north,south}.png | KEEP, round 1 |

Battery charge bar over each look's gauge window, per facing: UNMEASURED (`commissions.md` §"The battery's charge
bar"; check at the first live look).

## Look icons (one per look, shared by every mod with the looks; 256x256)

Judge: 4 of 4 KEEP (`VEA_Icons.json`). Their put record plans copies only for Gimme Some Slack and FlowWorks; Machine
Looks would ship its own copy at `RimMandrake/MachineLooks/UI/Looks/<Look>.png` (`design/NAMING_SCHEME_PLAN.md`: each
mod ships its own copy at its own texPath root). That third copy is not yet in the put record.

| look | art-store sha | verdict |
|---|---|---|
| Scrapper | 5a1ea13a670ce18ba93f17583ae89ffa7d87390cc0fa6f6c7900fe936908a007 | KEEP |
| Industrial | 89aa6a69326b45c504ef3a0e8a5d20879f9b3df893fd2734da7f1f05c120da02 | KEEP |
| Modern | 42fd8952fe2955b06fabd9866f43246e24f74f9cc5ce4cc941642f59f6bd163d | KEEP |
| Futuristic | 9b6e9ea89bf6b0663cc9f210958188508eb05f65b428fb8e65d42f8fd0182537 | KEEP |

## Fridge (cold-storage) pictures: CANDIDATES, never judged

13 artpipe renders of 2026-10-26 (list `infrastructure/artpipe/art_lists/coldstorage_ladder_2026-10-26.csv`, item
COLD_STORAGE_COOLERS_BUILD_RSW_LADDER). Registry events: queued, generated, validated (pass) only; no judge verdict
anywhere; imported to the art store 2026-11-04 (art ledger, kind artpipe). The artpipe `_artsrc` copies are pruned. The
judging is item COLD_STORAGE_LADDER_ART_JUDGE_SHEET (proposed). None of them is in one of the four looks: each is one
picture per facing, look UNMEASURED. They were drawn for the defs below, which today borrow a vanilla texture.

| def (mod) | facing | size | art-store sha | borrows today | verdict |
|---|---|---|---|---|---|
| RM_EvaporativeCrock (ColdStorage, RM) | single | 512x512 | df418b34029fa83a19c034b0d4e66812ecdfbc655a7ab19e868423db1ab62076 | PlantPot | not judged |
| RSW_CoolingChamber (Cuisine, RSW) | east | 1024x1024 | 873f938ec28ccf8ba7c4f6f1f31b8c36e4c40c447a14fcea84e85588d4581804 | ShelfSmall | not judged |
| RSW_CoolingChamber | north | 1024x1024 | ab65c42c7c717ea6c83adffb609576618bdfd2904e347e6abdf680da3e49ac50 | ShelfSmall | not judged |
| RSW_CoolingChamber | south | 1024x1024 | 37903105cd038059bc42c09f6375b4f084bcaa0c3094b30d5bed4e2e73533fdb | ShelfSmall | not judged |
| RSW_CoolingSupplyUnit (Cuisine, RSW) | east | 512x512 | c4fa4e72ac60f91d04a67c36673a1a893bcbb1d7efc10eefa3c7f0699b3d754e | ShelfSmall | not judged |
| RSW_CoolingSupplyUnit | north | 512x512 | a43a740b7e01417e94d9b0700cb9e603a1692e48006fffbeca5a2bc0452f13d5 | ShelfSmall | not judged |
| RSW_CoolingSupplyUnit | south | 512x512 | 100915e25cb31bda297e5afa8a9280c5ad1e1bc7db54f6cb3326225ffa964b34 | ShelfSmall | not judged |
| RSW_CoolingUnit_Wall (Cuisine, RSW) | east | 512x512 | 0339ace43579ce3511a638278970acfcc5cb003e2a23dc6d382f0d7f8159fcc4 | TempControl/Cooler | not judged |
| RSW_CoolingUnit_Wall | north | 512x512 | 2bddebca978e4f8be61cd8b344b6bf69f3d540bd9e4ff46a8f4d097056e31ad1 | TempControl/Cooler | not judged |
| RSW_CoolingUnit_Wall | south | 512x512 | b68da10c7e746edb9691308f76b070e9c0dbb8ef6d7951e25ea6f02d653848ad | TempControl/Cooler | not judged |
| RSW_CryoUnit (Cuisine, RSW) | east | 512x1024 | 117344db03c18ac05b240df63346aebe2fcdae738bf13d99887f8f8eed1429d9 | ShipCryptosleepCasket | not judged |
| RSW_CryoUnit | north | 512x1024 | 0b733ce41a4bd3793b5725fa0487c2b94ca1cac9d59d686456ac77ea148f63e4 | ShipCryptosleepCasket | not judged |
| RSW_CryoUnit | south | 512x1024 | 9fc77b721e9715b73db6d334082e7d7790d2d21a7c0069c1b3a15c244fce4655 | ShipCryptosleepCasket | not judged |

Their resolution against the 128 px per cell rule: UNMEASURED (each def's drawSize not read for this inventory).

## Not Machine Looks

The 12 wall-lamp pictures and the 3 power-pole buttons of 2026-11-20 (all KEEP) belong to Gimme Some Slack
(`design.md`: GSS keeps the installation). The wrong sheet `Transient/biome_ffar/vanilla_electrical_looks_sheet_2026-11-20.html`
(a suit charger in the battery rows) must not be served.
