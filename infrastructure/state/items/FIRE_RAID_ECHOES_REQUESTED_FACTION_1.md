# FIRE_RAID_ECHOES_REQUESTED_FACTION_1 — it reports what you asked for, not what raided

Measured live 2026-08-26, seat CHECK, full 582-mod list, game paused.

```
jawa/fire_raid {faction: "Jawa_FreeDroidEnclaves", points: 400, spawnCenter: "5,5", dryRun: false}
  -> success true, resolved.faction "Jawa_FreeDroidEnclaves"
  -> what arrived: 5 x Jawa_Blackstar_Grunt, faction "Blackstar Company"   (Pirate)

jawa/fire_raid {faction: "Mechanoid", ...}
  -> resolved.faction "Mechanoid"
  -> what arrived: Totharth Mechhive                                        (matches)
```

## Cause, read not guessed

`Jawa_FreeDroidEnclaves` is **Neutral** to the player on this world — `jawa/faction_relations_get`
reports 10 hostile / 14 neutral / 0 ally over 25 factions, and the Enclaves are in the neutral
column. `IncidentWorker_RaidEnemy` will not raid with a non-hostile faction, so it chose its own.
**That substitution is correct engine behaviour.** The defect is that the tool never says it
happened.

## Why it matters

🔴 A raid test that names a faction and then reads `resolved` has verified **nothing** about which
faction raided. This is the project's standard silent-success shape in a new place: the echo is the
request, not the outcome.

## What to change

After the incident fires, read `IncidentParms.faction` **back** (or diff the arrivals) and report
`requestedFaction` alongside `actualFaction`, with an explicit warning line when they differ. A
`dryRun` should also refuse — or at minimum flag — a faction that is not hostile to the player,
since that is knowable before firing.

## Until then

**Census the ARRIVALS, never the reply.** `jawa/list_pawns` before and after, diff the ids, group by
`factionName`. That is what caught this.

Evidence: `infrastructure/state/evidence/live_half_of_load_2026-08-26_CHECK.md` (run 2)

---

## Already fixed in source

`jawa/fire_raid` in `JawaBenchEventTools.cs` warns BEFORE firing when `requestedFaction` is not
hostile to the player, and the result carries `requested`/`actual`/`substituted` so a caller diffing
the reply — not just the arrivals — now sees the substitution.

Undeployed, which is why the live measurement still showed the defect. Needs a game-down window to
deploy and re-run the two calls above to prove `substituted: true` on the Enclaves case.
