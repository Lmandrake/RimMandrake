# belt_merges_20261009m — Silooth override fold + MATERIAL_MERGES_CLEANUP_1

FOUNDRY offline builder, 2026-10-09. No bridge, no deploy.

## Task 1 — Silooth art override fold
- Silooth home = SWBestiary (Patches/Silooth/Silooth_Warbeast.xml). Art moved to SWBestiary/Textures/RimStarWars/SWBestiary/Silooth/;
  patch now redirects li[2]+li[3] bodyGraphicData texPath (the two stages the same-path override reached).
- src/RimStarWars/SiloothArtOverride deleted. No modlist/compose/loadAfter referenced it (git grep: only ledgers, art ledger, Transient).
- Item SILOOTH_ART_FOLD_1 filed; deploy note lives in its prose.

## Other ArtOverride mods (report only)
- 59 more standalone *ArtOverride mods: 28 under src/RimStarWars (donor mlie.starwarsanimalcollection, Lockjaw on sarg.alphaanimals),
  31 under src/RimUtinni (donors sarg.alphaanimals, alphamemes, mlie.horrors, VGeneticsE, vfe.insectoid2, BOTR).
  All texture-only same-path swaps (Grutt, Grithe carry 1 xml each). Same shape as Silooth -> fold candidates.
- MantistanisArtOverride and MycoidColossusArtOverride have NO About.xml (not deployable as mods at all).
- Existing item ART_OVERRIDE_FAMILY_SCRIPT_1 covers the family.

## Task 2 — MATERIAL_MERGES_CLEANUP_1
(pending)

## Deploy notes (next game-down, NOT applied)
- Silooth: deploy SWBestiary; delete C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SiloothArtOverride; drop its packageId from live ModsConfig if active.
