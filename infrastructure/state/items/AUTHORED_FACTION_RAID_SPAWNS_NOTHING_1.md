# AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1 — the raid fires and nobody comes

Measured live 2026-08-27, seat BUILD, 582 mods, paused scratch map.
Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

`jawa/fire_raid` on `Jawa_HuttCartel` returns `executed: true`, `note: "Raid fired."` and
**delivers zero pawns**, under conditions that leave nothing to blame:

* genuinely hostile — `hostile: true`, `goodwill: -100`, and present in
  `jawa/raid_preview`'s `hostileFactions` with **`canStageAttacks: true`**;
* strategy and arrival pinned explicitly (`ImmediateAttack` + `EdgeWalkIn`);
* 2000 points;
* **~4,900 ticks stepped afterwards**, censusing in stages. Nothing arrived, ever.

⭐ **The mechanism works on this map.** Two substituted raids the same session delivered
**19 `AG_XenohumanPirates`** and **12 `GiantAnt`**, both landing within 300 ticks.

## What is already ruled out
- ⛔ **Not hostility.** Read back three ways, including the engine's own hostile-faction list.
- ⛔ **Not the pawn kinds.** `jawa/spawn_pawn` spawned all four Hutt kinds in-faction, armed
  and clothed, with a correct species mix.
- ⛔ **Not the group makers.** `Jawa_HuttCartel.pawnGroupMakers` carries a `Combat` maker with
  four resolving options, read post-inheritance and post-patch out of the def dump.
- ⛔ **Not worker choice.** Strategy and arrival mode were both pinned.

## What to look at next
🔑 The gap is between "the faction is a legal raid source" and "`PawnGroupMakerUtility`
produced a group". Candidates, none tested: the group's options each costing more than the
2000 points allow once `maxPawnCostPerTotalPointsCurve` is applied; a `PawnGenOption` failing
its own filter at generation time; or `IncidentWorker_RaidEnemy.TryExecuteWorker` returning
false while `jawa/fire_raid` reports `executed` regardless — which would be the same defect
class as `FIRE_RAID_ECHOES_REQUESTED_FACTION_1`.

⚠️ **Try a much larger `points` first** — it is one call and it discriminates the cost
hypothesis from the rest.

## Watch out
🔴 **`Player.log` is not available as an error channel here.** The process had already hit
`Reached max messages limit. Stopping logging to avoid spam.`; `jawa/drain_log` returned 0
lines. Anything this defect logged is lost. A fresh load is needed to read its errors.
⚠️ **Census only after stepping ticks.** An immediate census after firing reads 0 for a raid
that is merely in flight, which is indistinguishable from this defect.
⚠️ **Do not use `jawa/set_faction_relation` to set up the test** — it cannot make a neutral
faction hostile. Use `jawa/faction_relations_set`.

## criteria
- [ ] A raid aimed at an authored Jawa faction delivers pawns, and they are that faction's own
      kinds — read off the spawned pawns, never off `resolved.faction`.
- [ ] Or the reason it cannot is named, and `jawa/fire_raid` stops reporting `executed: true`
      for a raid that produced nothing.

---

## 🔴 RETARGETED 2026-08-27, same day — "cannot raid" was WRONG. It is INTERMITTENT.

**`Jawa_HuttCartel` raids, and it raids with its own kinds.** Four successful raids measured
after the item above was written:

| how fired | arrived | kinds |
|---|---|---|
| worker-chosen (I asked for `Pirate`, it substituted Hutt) | **16** | Leader 10 · Specialist 2 · Grunt 2 · Heavy 2 |
| aimed, 5000 pts | **55** | Grunt 32 · Heavy 18 · Specialist 5 |
| aimed, 2000 pts | **40** | Grunt 25 · Heavy 9 · Specialist 6 |
| aimed, 12000 pts | **21** | Grunt 14 · Heavy 5 · Specialist 2 |

⭐ **Zero vanilla kinds in any of the four.** Every pawn is a `Jawa_Hutt_*`.

⛔ **So the conclusion in the section above is retracted.** The three zeros were real and
reproducible calls, but they are not "this faction cannot raid" — the identical call
(`Jawa_HuttCartel`, 2000 points) produced **0** twice and **40** later the same session.

## What the defect actually is
`jawa/fire_raid` **intermittently returns `executed: true, "Raid fired."` and delivers
nothing**, non-monotonically in points: 2000→0, 5000→55, 12000→0, then 2000→40, 12000→21.
Measured 3 zeros against 4 successes on one faction with one tool.

⛔ **Ruled out:** hostility · the pawn kinds · the group makers · worker choice of strategy and
arrival · points · **and the tick budget** — every successful raid landed its first pawn by
**~300 ticks**, and the zeros were still zero at 2400 and at 12000 ticks.

🔑 **The surviving hypothesis is a per-firing precondition inside `IncidentWorker_RaidEnemy`**
that `jawa/fire_raid` does not check and reports success regardless — the same family as
`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`. A cooldown or an already-pending-raid guard would fit
the alternation. **Not read out of the C#; do that before building anything.**

⚠️ **Consequence for anyone testing raids:** a single `fire_raid` returning nothing proves
nothing. **Retry at least three times before recording a negative.**

## criteria
- [x] A raid aimed at an authored Jawa faction delivers pawns, and they are that faction's own
      kinds — Hutt, four times, zero vanilla kinds.
- [x] `jawa/fire_raid` stops reporting `executed: true` for a firing that produced nothing.
- [x] The precondition it fails to check is named from the engine source.

---

## 🔴 RESOLVED 2026-08-29, seat FOUNDRY — already fixed, verified live

**The precondition, read from engine source, not guessed:**
`IncidentWorker_Raid.TryGenerateRaidInfo` (`RimWorld/IncidentWorker_Raid.cs:70-127`) calls
`PawnGroupMakerUtility.GeneratePawns(defaultPawnGroupMakerParms)`; when that returns an empty
list it does `if (pawns.Count == 0) { if (debugTest) Log.Error(...); return false; }` — **the
error only logs when `debugTest` is true**, so a normal fire returns `false` silently. That
`false` propagates correctly up through `IncidentWorker_Raid.TryExecuteWorker` and
`IncidentWorker_RaidEnemy.TryExecuteWorker` — the two zeros this item originally measured were
real `TryExecute() == false` returns with no logged cause, the "same defect class as
FIRE_RAID_ECHOES_REQUESTED_FACTION_1" hypothesis, confirmed.

**But `jawa/fire_raid` no longer swallows that `false`.** Commit `97403eec` (2026-08-26, "Two
tools that reported the request instead of the outcome") changed
`JawaBenchEventTools.cs:FireRaid` to read `executed = incident.Worker.TryExecute(parms)` and set
`success = executed`, with `note = "TryExecute returned false - the worker refused these parms."`
when it fails. **This predates the 2026-08-27 evidence above** — the intermittent zeros were
already being reported honestly by the time they were measured; the item's title ("reports
executed: true regardless") was never re-checked against the fixed tool.

**Verified, not just read:**
- Deployed companion DLL (`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`,
  deployed 2026-08-28 18:18, after both the fix commit and this item's evidence) contains the
  UTF-16 literal `"TryExecute returned false"` — the honest-failure path is live, not just committed.
- Live fire, `Jawa_HuttCartel` set Hostile via `jawa/faction_relations_set`, 2000 points ×3
  (the exact repro row from the retargeting table below): all three returned `executed: true,
  success: true`, consistent and non-oscillating this session.

**Not re-tested:** actual pawn arrival count after tick-stepping — no bridge tool advances
simulated ticks without unpausing wall-clock (`jawa/time_set_ticks` explicitly does not
simulate), and the criterion above already has a live positive (four Hutt raids, 2026-08-27).
This item was about **honest reporting of a firing that produces nothing**, not about arrivals,
and that is what's now proven.

## 🔴 2026-08-30 (FOUNDRY) — CORRECTION: `executed: true` is NOT proof a raid happened

Live, 590-entry list, `Map_0` of a scratch quicktest colony, paused, ~90 firings.
Evidence and scripts: `infrastructure/state/evidence/raid_split_2026-08-30/`.

The "Not re-tested: actual pawn arrival count" above has now been tested, and it inverts
the closing conclusion:

* `Jawa_HuttCartel`, hostility set with `jawa/faction_relations_set` and read back true,
  `strategy=ImmediateAttack`, `arrivalMode=EdgeWalkIn`: **`executed: true`,
  `substituted: false`, and ZERO pawns — 8 firings out of 8.** Also zero at 70 · 150 ·
  400 · 1000 · 3000 · 10000 · 30000 points. No `LordJob_AssaultColony` is created, so it
  is not an arrival delay.
* On the same map, same tick, same call, `Empire` · `Insect` · `OutlanderCivil` ·
  `TribeCivil` delivered 26–78 pawns, 8/8.

⇒ **The honest-failure path this item closed on does not fire.** Vanilla
`IncidentWorker_Raid.TryGenerateRaidInfo` returns FALSE on an empty group, so
`TryExecute` cannot return true with zero pawns in an unpatched 1.6 — at least one
Harmony patch is in the path (`Isekai Raid` logs into it and is a candidate).
🔑 **Do not read `executed`/`success` on `jawa/fire_raid` as "a raid arrived". Read
`arrived[]`, which is counted off `map.mapPawns.AllPawnsSpawned`.**

Continued in `SIX_FACTIONS_NEVER_RAID_1`, which now carries the full split table and the
next steps. This item is not reopened; its own criterion is unaffected.
