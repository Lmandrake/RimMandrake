# GALACTIC_EMPIRE_NAME_COLLIDES_1 — two factions, one name, and a player sees both

Measured 2026-08-27, capture `2026-08-26T14-20-04Z` plus live `jawa/list_factions`.
Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

    fixedName "Galactic Empire" -> 2 FactionDefs:  Empire · OuterRim_GalacticEmpire

Both are in the live world and both read **Galactic Empire** to the player. This is the exact
condition `BLACKSTAR_NAME_MUST_NOT_LEAK_1`'s criterion forbids — *"a generated world in which
`Blackstar Company` and `Galactic Empire` each name exactly one faction"* — and it is the
half of that criterion which FAILS.

⭐ **It is not our leak.** `Empire` is vanilla Royalty's faction; `OuterRim_GalacticEmpire` is
the Star Wars one. Neither name came from the Blackstar reskin, and the Blackstar half is
clean: **zero** FactionDefs now carry `fixedName: "Blackstar Company"` (it became namer-based
at `5d1c1908`), and live it names exactly one faction on a world carrying **four**
`PirateBandBase` factions.

## Why this is DECIDE's and not BUILD's
The mechanism is one `PatchOperationReplace` on a `fixedName` and BUILD can write it in a
minute. **Which faction loses the name is a lore call**, and it changes what a player reads
over a faction for the whole campaign.

🔑 **Recommendation, not a ruling:** rename **vanilla `Empire`**. This is a Star Wars campaign;
`OuterRim_GalacticEmpire` is the Galactic Empire the fiction means, it fields our authored
Empire kinds, and Royalty's empire is the interloper here. ⚠️ But Royalty's `Empire` carries
the whole permit/title/tribute system, so it is a faction the player deals with by name, and
renaming it touches quest and letter text nobody has surveyed.

⚠️ **`Ancients` collides too** — `Ancients` and `AncientsHostile` share `fixedName: "Ancients"`.
That one is vanilla-on-vanilla and almost certainly intended (one faction, two hostility
states). Named here only so the next reader does not re-derive it as a third defect.

## criteria
- [ ] Exactly one faction in a generated world reads `Galactic Empire`.
- [ ] The faction that keeps the name is the one the campaign's fiction means, recorded with
      the reason.
