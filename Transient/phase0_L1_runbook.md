# Phase 0 L1: the donor-off live round (runbook)

Spec: `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §0.5.4 (L1) and §0.5.5 item 5. Item: `DONOR_OFF_LOAD_PROVE_AFTER_BENCH`.
Driver: `src/RimMandrake/Utils/modcheck/l1_donor_off_round.py`. Tier: `donor_off_phase0` in `modset_builder.py`.
The tier has no `mlie.starwarsanimalcollection`, no `sarg.alphaanimals` and no `daria40k.alphaanimalspatchoutposts`. `forbid`
refuses the tier if a dependency drags any of them back in. It loads all five DLC. **Alpha Biomes stays in**, because the composed
`mandrake.rm.biomes` hard-depends on it. Retiring it is the owner's O1 card.

**Who:** FOUNDRY (or whichever seat holds the bridge). **Owner present:** only for the FLIGHT rows. Every other row runs unattended.
**Duration (INFERRED):** about 2 h. That is 30 min of deploy, swap and launch, 60 to 75 min of rows, then teardown, and +10 min for flight if he is there.

## 0. Blockers measured 2026-10-15 (offline)
`derive` gave 211 species, 3 plants, 17 biomes, 23 flyers and 3 unresolved names. The unresolved ones are RSW_Aiwha (removed), RSW_Mynock
(declined) and RM_Skorra (cut by the owner, `ed98c4985`).
- **O01 FAIL:** the *deployed* `SWBestiary\About\About.xml` still hard-depends on `sarg.alphaanimals`. The src dropped that dependency at `447cae1f2`.
  The fix is to deploy SWBestiary. But `15414fe38` says **do not deploy SWBestiary until the Sarlacc art lands**: 3 textures
  (`RSW_DeadSarlaccHusk`, `RSW_SarlaccPit`, `RSW_SarlacciSpore`). Those 3 and the P1 plants
  (`RSW_Plant_HydenockTree_Wild`, `..._JoganTree_Wild`, `..._TookeTrap_Wild`, `RSW_RawJoganFruit`) have no PNG yet.
- **O03 FAIL:** subjects whose texPath has no PNG in src. They will read as texture misses in L03/L04. Re-run `derive` and see O03 for the current list.
  It moves as the P4/P5 art installs.
- No fixed save yet. `SAVE_LOAD` reads the name from `Transient/phase0_p6_save_census.md` (`*_donorfree.rws`), or you pass `--save`.

## 1. Before taking the bridge (WSL, game may be up)
```
cd /home/mandrake/rm/foundry && git pull --ff-only
python3 src/RimMandrake/Utils/modcheck/l1_donor_off_round.py derive --out /mnt/d/Luke/dev/_rmscratch/l1_manifest.json
python3 src/RimMandrake/Utils/modset_builder.py --tier donor_off_phase0          # plan only: must NOT say REFUSING
python3 src/RimMandrake/Utils/donor_pack_port.py check                            # 0 donor-only refs / donor-served tex (Biotech Acid is known)
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SWBestiary              # dry runs; read every - line
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Shokk
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches
python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes              # Contagion, Slime, Forge, Miasma ... ports
```
Go only when `derive` exits 0 (O01 and O04 PASS) and the dry runs touch nothing another seat owns.

## 2. Take the bridge, game down, deploy, swap, launch
```
rimflow bridge take --for "Phase 0 L1 donor-off round"
./game --why "Phase 0 L1 donor-off round: deploy + tier swap" going-down      # then close RimWorld
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SWBestiary --apply      # repeat for Shokk, UtinniPatches, --compose biomes
python3 src/RimMandrake/bridgetools/build.py --gm --apply                         # only if preflight L05 says companion mismatch
python3 src/RimMandrake/Utils/preflight_bridge.py --tier quicktest --modset donor_off_phase0
python3 src/RimMandrake/Utils/modset_builder.py --tier donor_off_phase0 --apply   # backs up ModsConfig (md5) first
python3 src/RimMandrake/bridgetools/launch_ready.py                               # READY on a current-process receipt
python3 src/RimMandrake/Utils/preflight_bridge.py --live --modset donor_off_phase0  # L01-L07; L05 = companion build
python.exe src/RimMandrake/Utils/rimbridge_client.py --timeout 300 --call rimworld/start_debug_game_ready --yes-i-know-this-is-live
```
The quicktest call outlives the client timeout and succeeds anyway. **Do not re-issue it.** Poll `jawa/list_pawns` until a map answers.

## 3. Run the rows (python.exe, repo root, one window)
```
python.exe src/RimMandrake/Utils/modcheck/l1_donor_off_round.py run --manifest "D:\Luke\dev\_rmscratch\l1_manifest.json" --phase pre,log,spawn,plants,burst,oomb,haze,portal,mapgen | tr -d '\r'
```
- **Flight, owner present only.** This is a state read via `jawa/pawn_flight action=report`. It is never visual and never a take-off:
  `... run --manifest ... --phase flight --owner-present "<his exact words>"`. Without him the 23 FLIGHT rows stay UNMEASURED/OWNER.
- **Save, last.** Loading the save ends the quicktest map: `... run --manifest ... --phase save [--save <name>]`.
  On a 25-mod tier the save's other mods are missing. Only reference errors that name a donor def, or its RSW_ rename, are graded.
  If a mod-mismatch dialog blocks the load, the row reads UNMEASURED; read `rimworld/get_ui_state`.
- A partial run (`--phase` not `all`) writes `mode: "partial"`. Each run writes `Transient/phase0_L1_result_<stamp>.json`.

## 4. Teardown
```
python3 src/RimMandrake/Utils/modset_builder.py --restore          # md5-verified back to the pre-swap copy
rimflow bridge release
./game --why "Phase 0 L1 done, owner list restored" down
```

## 5. Reading the result
PASS means the game was asked, answered, and met the bar. FAIL means it answered and missed. UNMEASURED means it could not be asked, and that is
**not green**. Classify each non-PASS row as MOD, SITE or HARNESS before filing anything (`live-debugging-proof-harness`).
`tapLost > 0` voids every log-based verdict. A row that ran after a colony death or a menu drop is not counted.

| §0.5.5 item 5 clause | rows |
|---|---|
| 0 exceptions in the donor-off Player.log | `L01_FIRST_EXCEPTION` (first line named) |
| 0 cross-reference misses on RM_/RSW_/RUT_ | `L02_XREF_OURS` |
| 0 texture misses on RM_/RSW_/RUT_ | `L04_TEX_OURS` (`L03_TEX_PORTED` is the subset on ported subjects) |
| every ported species spawns | `SPAWN_<kind>` x211, `PLANT_<def>` x3 |
| every donor-row biome generates a map with animals or plants | `MAPGEN_<biome>` x17, `ROSTER_<biome>` (rows still donor-guarded drop: listed, expected) |
| flight state reads true for every flyer | `FLIGHT_<kind>` x23 (owner present) |
| (L1 extras from §0.5.4) the fixed save loads | `SAVE_LOAD` (gate item 4 itself is the offline save grep, P6) |
| (mechanisms this round also proves) | `BURST_*` x5 (Bloody Mess killed vs gestation, bulloo, blistered bulloo, scorchpod), `OOMB_GROWTH`, `OOMB_SPLIT`, `HAZE_ZHOOL`, `PORTAL_ENTER`/`PORTAL_EXIT` |

Record a green round with `rimflow verify DONOR_OFF_LOAD_PROVE_AFTER_BENCH --result pass --config donor_off_phase0 --level L1 --evidence Transient/phase0_L1_result_<stamp>.json`. P7 then removes the donors from the full list.
