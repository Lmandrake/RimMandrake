# CREEP_WEB_HARVEST_LIVE_1 — live-check the creep-web colonist harvest

Parent: `SHOKKWEAVE_SOLE_SOURCE_1` (route 4, ruled BUILD with a live check by question card 2026-10-09). Built at
`6c1f40e9d` in mandrake.rm.webwork (folded into mandrake.rm.biomes at runtime). Not run then: the game was RUNNING and
a new DLL cannot deploy under a running game.

## spec
1. Game DOWN. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Webwork` (plan; however the biomes fold is
   deployed today), read the plan, `--apply`. Confirm the deployed `RimMandrake.Webwork.dll` hash equals the repo's
   `.srchash`-stamped DLL.
2. Launch, take the bridge, start a throwaway quicktest map (rimworld-debug-testing; NEVER the canonical save).
3. `jawa/static_call type=RimMandrake.Webwork.RM_WebworkProof`:
   - `ProofHarvest "true|RM_Webwork_Anchor|34"` → must read
     `HARVEST designatable True | workgiver True | yield 3 | weaveNear 0->3 | spawned 1`
   - `ProofHarvest "true|RM_Webwork_Web|0"` → `yield 2`, `weaveNear 0->2`, `spawned 0`
   - `ProofHarvest "false|RM_Webwork_Anchor|0"` → `designatable False`, `yield 0`
4. The real colonist walk: `ProofHarvestDesignate "RM_Webwork_Anchor"` → `DESIGNATED x,z | designatable True`;
   step ~2000 ticks (colonist with Construction enabled, undrafted); `ProofHarvestRead "x,z"` →
   `READ nodePresent False | weaveNear 3 | lastYield 3`.
5. Or run the suite: Webwork `validation.py` chain `map_mechanics`, component `creep_web_harvest`.
6. Player.log must NOT contain `RM_CompProperties_HarvestYield has no yield`, `Could not find type named
   RimMandrake.Webwork.RM_CompProperties_HarvestYield`, or `alwaysDeconstructible=true but deconstructible=false`
   for any `RM_Webwork_` def.

## verify
Steps 3 and 4 read exactly as above on a quicktest map; step 6 clean. Then note the result on
`SHOKKWEAVE_SOLE_SOURCE_1` (its verify line "border-map creep-web cut yields Shokkweave and can spawn the emergent
Shokk") and close this.
