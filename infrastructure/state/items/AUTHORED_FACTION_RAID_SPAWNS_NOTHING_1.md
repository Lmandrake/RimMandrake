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
- [ ] `jawa/fire_raid` stops reporting `executed: true` for a firing that produced nothing.
- [ ] The precondition it fails to check is named from the engine source.
