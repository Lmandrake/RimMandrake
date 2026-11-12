# NOTES (picked 2026-11-11 by CLAUDE_ARCHMAGI_OFFLINE2)

- Runs so far: 0. Mode whittle. Item filed 2026-10-24 by FOUNDRY during GPTREDO_JUDGE_UNJUDGED_ROWS; owner BENCH since
  the FOUNDRY retirement.
- Copies: `src/RimMandrake/TheRot/Textures/RotSpecies/AgariluxPrime.png` (md5 b7ce28d8…) and
  `src/RimUtinni/UtinniPatches/Textures/Things/Plants/AB_AgariluxPrime.png` (md5 09cc4868…). Different files.
- Def: `src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml:542` declares RM_AgariluxPrime with base
  texPath `Things/Plants/AB_AgariluxPrime` (the donor Alpha Biomes path, also the UtinniPatches file's path).
  `src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml:369-374` repoints it to `RotSpecies/AgariluxPrime`
  (v3 regen landing, 2026-09-20). So in game the TheRot copy is probably the one drawn: verify, don't assume.
- Open question for the build: does the UtinniPatches `AB_AgariluxPrime.png` also serve the donor def
  `AB_AgariluxPrime` (Alpha Biomes texture override)? If Alpha Biomes is retired/inactive, it serves nothing. Check
  Alpha Biomes status (both mod roots, active and inactive) before deleting. Also check `RotGiants_HugeFootprint.xml`
  `<texture>AgariluxPrime</texture>` and the UtinniPatches `AB_GiantAgarilux` / `Plant/Agarilux` neighbours (out of
  scope unless they are the same split).
- Art-eval evidence: `infrastructure/state/art_eval/runs/gptredo_03/decisions.jsonl` (subjects
  `RM_AgariluxPrime__TheRot`, `RM_AgariluxPrime__UtinniPatches`); images `D:\ClaudeWork\rimmandrake\art_eval\gptredo\`.
- Classification: no past failures (no runs). Offline only; nothing needs the game.
