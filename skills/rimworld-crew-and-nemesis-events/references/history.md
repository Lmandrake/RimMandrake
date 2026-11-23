# History: corrected lines and their evidence

The active files hold the lessons. This file holds the old lines that were wrong, and what showed it (2026-11-23).

- **Card C07.** `SKILL.md` said that "whether anyone may join the crew at all is an open owner question". The owner answered
  the card on 2026-10-10: `design/RimMandrake/mod_audit/OWNER_RULINGS.md`, row C07. That row also says that our own
  `mandrake.rm.strandedquest` is read as not retired, owner to confirm. No confirmation was found in the ledger.
- **Retired mods.** `SKILL.md` said that all its source mods retire. `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
  (315 mods) holds Tribute Demand, RM_Stranded and Space Worms. That list does not hold Rimesis, We Are United or More
  Slaves. His rulings are rows C07 (We Are United, More Slaves) and C09 (Rimesis) of `OWNER_RULINGS.md`.
- **The person demand of Tribute Demand.** `SKILL.md` and the study said 15% of rolls. The code is
  `roll = Rand.Value * DemandWeight` with `DemandWeight` 1.8, and the person branch is `roll < 0.15`
  (`IncidentWorker_Extortion.cs`, `GenerateDemands`). So the chance is 0.15 / 1.8, about 8%. If that branch finds no
  candidate, the roll falls through to animals. `SKILL.md`, `references/crew_mechanisms.md` and the study also said that the
  whole branch needs two free colonists. Only a colonist needs that; `PrisonersOfColony` are always candidates.
- **OldFriends and kidnaps.** `SKILL.md`, `references/crew_mechanisms.md` and the study said that OldFriends already records
  a demanded colonist. `Patch_ColonistKidnapped` returns when `kidnapper?.Faction` is null, and it records the kidnapper.
  Tribute Demand calls `faction.kidnapped.Kidnap(pawn, null)`. In vanilla, `KidnappedPawnsTracker.Kidnap` sends its letter
  only when the kidnapper is not null (RimSage).
- **Resurrection.** `SKILL.md` told the reader to use `ResurrectionUtility` "on a pawn you kept alive".
  `ResurrectionUtility.TryResurrect` logs an error and returns false for a pawn that is not dead (RimSage).
- **Rimesis points.** `SKILL.md` said that the point factors of Rimesis stay near 1.0 to avoid stat inflation. The ordinary
  factor is 1.0, but an armed retaliation raid is 1.5, an elite group is 0.7 to 0.82 and a horde is 1.15 to 1.3 (study §2.7). The study also lists +0.1 per extra returner and a karma
  multiplier.
