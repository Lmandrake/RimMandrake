# EMPIRE_PURSUIT_SCENPART_INSTALL_1 — put endless Empire pursuit into the live campaign, with the owner

Owner, 2026-08-28: "please add a Bench item to work with the player to add it to our
game... however that will happen."

## spec
Install `ScenPart_RuthlessPursuingMechanoids` targeting **`Empire`** (the reskinned
vanilla faction — owner: "Our Star Wars empire IS the re-skinned Empire") into the
campaign, per the recipe in `design/Jawa/mods/ruthless_faction_pursuit.md`.

**"However that will happen" is the open question.** Candidate routes, in order of
likely cleanliness — a BENCH session with the owner picks one:
1. **Runtime insert via bridge/C#**: `Find.Scenario.parts` is runtime state; a small
   companion tool (or C# eval) constructs the part with the chosen values and appends
   it, then a save proves it scribed. Cleanest for an already-running campaign.
2. **Savegame edit**: write the `<li Class=...>` block (in the design note, scribed
   names verified) into the save's `scenario` → `parts` — game down, backup first,
   rimworld-savegame skill rules apply.
3. **Scenario editor at the final world-freeze**: if the shipped save is ever
   re-rolled from a scenario, the part simply belongs in that scenario.

## The three knobs the owner sets when we do it (from the design note)
- when pursuit begins (`firstRaidDelayHours` — game start vs "after the schism")
- pressure curve (`raidDelayHours` 636±204 vanilla vs tighter)
- `canDoNormalRaid` (pursuit-only vs also normal raids)

## verify
Grep the next save for `ScenPart_RuthlessPursuingMechanoids` with
`pursuitFactionDef` = `Empire` and the chosen values; then a scratch-game live check
with a tiny `firstRaidDelayHours` proves waves actually fire.

## criteria
- [ ] The part exists in the campaign save with the owner's chosen values.
- [ ] Pursuit faction is `Empire` (the reskinned vanilla def), not OuterRim_GalacticEmpire.
- [ ] A raid wave proven to fire on a scratch game before the campaign relies on it.
