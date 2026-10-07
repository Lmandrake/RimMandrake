# TWILIGHT_ART_REUSE_ELSEWHERE_1 — Twilight Sea sheet art he asked to reuse in other biomes

Source: Twilight Sea sheet close 2026-10-07 (`Transient/biome_ffar/twilightsea_sheet_2026-10-05.decisions.json`).
Each picture is held in the art store by sha (none purged). The Twilight Sea side of every row is done; what is
owed is new content in ANOTHER biome, so it waits for that biome's own sitting.

1. **Scaa Lumsigh — a new Greentide river fishable from the current faa art.** His note on `RSW_Faa`: "Follow canon closely. However, existing fish images can be remade into a new fish: Scaa Lumsigh for fishing in the Greentide rivers. Move this image to that fishing source, then regen Faa scalefish according to canon"
   Art (SWBestiary faa, column A): east `2aa6758ed0bfc966810ab56b9a3503324e6d1960c89712c3ce1a8b21a1e727c4`, north `16bf54ac8baa12239db06f4d50d1df80c471a8e8cd8d4771dc0473ea399bb7f5`, south `f4d721d5a0ab356c6eba8cd8c85d6cf8ad8a2c11107ade307aa371caae791beb`, west `7e140da59624b22295e72cb36da42c47e27d936e7146803b05eac8a5c22850de`. The faa itself is regenerating to canon (artpipe `twilightsea_faa_canon_redo_v1`); install the old bytes at a new Scaa Lumsigh texPath BEFORE the faa redo overwrites the live file.
2. **A new Greentide river fishable from the current mee art (unnamed).** His note on `RSW_Mee`: "Again, move this fish art to the Greentide rivers as fishable, and redo this according to Canon carefully. "
   Art (column A): east `18e7e0a381173360f4536cb3b14e0bb98c2b1536fd8f92667887bfd77827fa44`, north `82aff98e9423139c9cc104f44882e3cf813fd8f90a5b04a53fdb549196b488ee`, south `b0e8510ca41fc131890dad2893eae68556781c78fe5236a4423f9da61ad864a7`, west `cea8f41561c5f80390860ce42a68d7e628ab81f95b4da4d498a248303775b3c3`. Same ordering trap as 1 (`twilightsea_mee_canon_redo_v1`).
3. **Old niim art for fishing elsewhere.** His note on `RM_Niim`: "Old art (a) can be kept for fishing elsewhere, but (B) belongs here now." Art (column A, niim v1): east `2351a5717e70a581925b919fde57afd893d01c5cbade28c7ed305a2eb26c4707`, north `7c1410aff2c9e08b89e8b6389588a857255f98aad18a05c9f9200c19fc6a5f03`, south `d555b7b36f515c1a566845e13b7733abde40d12d96b0aa16cb8a5c26adc203c2`. Where is not named — ask at the next sea/river sitting.
4. **A new Sump plant from the noothelm B render, with Star Wars cuisine implications.** His note on `RM_NoothelmPlant`: "Needs to look like seaweed growing a single golden bulb. But keep art (b) for a new plant in the Sump. It's pretty. Make something new with Star Wars cuisine implications."
   Art (column B): south `610a8fe01edf8271e908c597e3da8b2c762c800f9aa9742d40483a3cd6ba8aaf`. The noothelm itself is regenerating as seaweed with a golden bulb (`twilightsea_noothelm_redo_v1`).

NEXT: at the Greentide sitting, author items 1-2 (ThingDef FishBase + Greentide river fishTypes row + `art install` of the shas above); at the Sump sitting, item 4; ask him where item 3 goes.
