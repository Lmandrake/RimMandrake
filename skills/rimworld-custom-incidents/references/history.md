# History: corrected lines and their evidence

The active files hold the lessons. This file holds the old lines that were wrong, and what showed it (2026-11-23). Each
engine fact was read in the decompiled 1.6 source through RimSage.

- **Retired mods.** `SKILL.md` said that all eight source mods retire. `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
  (2026-11-20) holds Tribute Demand and Space Worms. That list does not hold the other six. Row C09 (event layers over
  Randy) of `design/RimMandrake/mod_audit/OWNER_RULINGS.md` drops Storyteller Enhanced and cuts Large Faction Bases and the
  events of Better Infestations. C09 does not name Tribute Demand or Space Worms; study §2.12 calls Tribute Demand a KEEP.
- **Success with no pawns.** Raid Protection Fee showed the defect in our 2026-10-10 live pass: the incident returned
  true and nothing arrived.
- **`forced` stamps.** `SKILL.md` said that a forced fire "stamps nothing". `StoryState.Notify_IncidentFired` returns at
  once for a forced fire, so there is no cooldown and no ThreatBig clock. But `Storyteller.TryFire` still sets
  `lastIncidentTick`; only `StorytellerComp_RandomMain` reads it, for targets in space.
- **`bypassStorytellerSettings`.** `SKILL.md` said that this needs no C#. The flag is a field of `IncidentParms`, so the code
  that makes the parms sets it. `CanFireNow` also skips `earliestDay` for it.
- **Which options remove a letter.** `SKILL.md` said that only vanilla `Option_Close` calls `RemoveLetter`.
  `ChoiceLetter.cs` also calls it in `Option_Reject`, `Option_JumpToLocation` and `Option_ViewInQuestsTab`.
- **A removed letter can be opened again.** `Letter.OpenArchived` calls `OpenLetter`, which rebuilds `Choices`. Nine
  vanilla choice letters test `ArchivedOnly`. Our letter in `RM_WalkingCondenser.cs` (the 1500 silver letter) did not on
  2026-11-23.
- **A removed demand is an escaped demand.** `Letter.CanDismissWithRightClick` is true by default. A right-click removes the
  letter before the timeout, so a default branch in `Removed()` under `TimeoutPassed` does not run. `LetterStack.RemoveLetter` calls `Removed()`
  for a letter that is no longer on the stack too, so `TimeoutPassed` alone runs the default branch again after a payment.
- **`terrainAffordanceNeeded`.** `SKILL.md` said that it is null for items. Stuff items set it (`Items_Resource_Stuff.xml`,
  and the stone blocks). `CellFinderLoose.TryFindSkyfallerCell` tests `GetAffordances(map).Contains(terrainAffordance)`.
- **The refused demand.** `references/recipes.md` §2 allowed a direct worker call with `bypassStorytellerSettings` for the
  raid. `IncidentWorker.CanFireNow` reads that flag, and a direct call to `TryExecute` skips `CanFireNow`. Also, `SKILL.md` §2 forbids the direct call.
