# SALVAGER_CONTENT_PROVE_ROGUES_GROUNDED

Owner, 2026-10-20, by question card: "Odyssey orbital fugitive quest and salvager wreck sites still spawn Celestial
Rogues pawns; keep?" -> "Cut them".

Built offline (2026-10-20): three guarded ops at the end of
`src/RimUtinni/UtinniPatches/Patches/FactionSlate/BannedFactions.xml`, registry `content_cut` in
`src/RimMandrake/Utils/factions/banned_factions.json`, asserted by `src/RimMandrake/Utils/banned_factions.py`
(check-repo PASS; selftest 26/26). Design: `design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md` §5, §8.4.

| def | op | what is lost |
|---|---|---|
| QuestScriptDef `OrbitalFugitive` | rootSelectionWeight 0 | the whole orbital-fugitive quest and its gravtech reward |
| GenStepDef `Opportunity_OrbitalWreck_Salvagers` | linkWithSite removed | the wreck's hostile salvager guards only; wreck, prefabs and loot stay |
| ThingSetMakerDef `Reward_MalfunctioningTransportPod` | Salvager_Pirate option removed | a live pirate in the pod (weight 2 of 20); no loot option removed |

Before deploy, `check-dump` on capture `2026-10-21T04-26-37Z` FAILS on exactly those three (expected) and its sweep
finds no other GenStep or ThingSetMaker route.

`SALVAGER_CONTENT_PROVE_ROGUES_GROUNDED` — built and committed, not deployed; NEXT: deploy UtinniPatches
(`deploy_custom_mods.py --mod UtinniPatches --apply`), load, take a def-dump capture, and run
`python3 src/RimMandrake/Utils/banned_factions.py check-dump <capture>` until it prints PASS.
