# SIX_FACTIONS_NEVER_RAID_1 — only the Hutt Cartel has ever been seen to raid

Measured live 2026-08-27, 582 mods, paused scratch map.
Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

Each authored faction made the **sole** hostile faction in turn — every other returned to
Neutral first — then `jawa/fire_raid` at 3000 points, up to 3 firings, reading the spawned
pawns' own faction rather than the echoed one.

    Jawa_HuttCartel            ✅ 27 pawns, own faction, own kinds
    Jawa_FreeDroidEnclaves     ⛔ nothing in 3 firings
    Jawa_WildsteamClan         ⛔ nothing in 3 firings
    Jawa_DeepwaterCompact      ⛔ 3 Thrumbo, faction None — wildlife, not a raid
    Jawa_GeonosianFoundryHive  ⛔ nothing in 3 firings
    Jawa_AscendantHelix        ⛔ nothing in 3 firings
    Jawa_Junkers               ⛔ nothing in 3 firings

**18 firings, zero arrivals**, against the Hutt raiding five times across the session
(16 · 55 · 40 · 21 · 27 pawns).

## Why this is not just the known intermittency
`AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1` establishes that `fire_raid` sometimes delivers
nothing — the Hutt itself needed retries. So 3 firings is a weak negative for any ONE faction.
🔑 **But 18 consecutive firings across six factions is not weak**, and the Hutt succeeded on the
first firing twice in the same session. The asymmetry is the finding.

## ⛔ The obvious lead is already REFUTED — do not spend a session on it
"The Hutt has the most settlements" does not survive its own data: **`Jawa_Junkers` also has 4
settlements and raided nothing.** Settlement count is:

    Hutt 4 · Junkers 4 · FreeDroid 2 · Deepwater 2 · Helix 2 · Wildsteam 1 · Geonosian 1

⇒ 4 settlements is neither sufficient (Junkers) nor is 1–2 obviously disqualifying. Look
elsewhere.

## What has already been ruled out for these factions
- ⛔ not hostility — each was verified `hostile: true` and present in `raid_preview`'s
  `hostileFactions` before firing
- ⛔ not the pawn kinds — every kind spawns fine via `jawa/spawn_pawn`, armed and clothed
- ⛔ not the group makers — every `Combat` maker resolves and fields only our own kinds
- ⛔ not the tick budget — every successful raid this session landed its first pawn by ~300
  ticks, and these were watched to 1200

## Watch out
🔴 **`Player.log` is dead as an error channel in this process** — it hit
`Reached max messages limit` and `jawa/drain_log` returns 0 lines. Whatever these firings logged
is lost. **A fresh load is needed to see their errors**, and that alone may answer it.
⚠️ Read the spawned pawns' faction. `resolved.faction` echoes the request
(`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`) and a raid requested from `Jawa_FreeDroidEnclaves`
arrived as 22 `Jawa_Hutt_*` pawns when more than one faction was hostile.

## criteria
- [ ] Each of the six either raids as itself, or the reason it cannot is named from the engine.

## 2026-08-30 (FOUNDRY) — the engine gate read, one of the seven answered, one lead killed

### The gate, named: `PawnGroupMakerUtility.UsableFactions`
`Source/RimWorld/PawnGroupMakerUtility.cs:355` is the only place the engine decides which
factions may source a combat group. A faction must satisfy **all** of:

    !Hidden · !temporary · !defeated · def.humanlikeFaction · HostileTo(player)
    def.pawnGroupMakers != null
    def.pawnGroupMakers.Any(x => x.kindDef == PawnGroupKindDefOf.Combat)
    !def.raidsForbidden
    points >= def.MinPointsToGeneratePawnGroup(Combat)

`TryGetRandomFactionForCombatPawnGroup` (line 360) is its only caller of consequence.

### ✅ `Jawa_DeepwaterCompact` is ANSWERED — `raidsForbidden = true`
Read live off the def, 585-mod set: Deepwater is the **only** one of the seven with
`raidsForbidden: true`. `UsableFactions` filters on `!def.raidsForbidden`, so the
storyteller can never select it, and `TimedDetectionRaids` skips it too
(`Planet/TimedDetectionRaids.cs:51`). ⇒ **Deepwater will never raid in play, by design of
its own def.** Whether that is what the owner wants is a separate question and belongs to
whoever owns the faction spec; mechanically it is not a bug and needs no further probing.

### ⛔ The points gate is REFUTED as an explanation — do not re-test it
`MinPointsToGeneratePawnGroup(Combat)` resolves to the cheapest `isFighter` option's
`combatPower` (`PawnGenOption.Cost => kind.combatPower`). Computed for all five remaining
factions off their own rosters:

    Jawa_GeonosianFoundryHive   Jawa_Geonosian_Grunt      56
    Jawa_Junkers                Jawa_Junkers_Grunt        56
    Jawa_WildsteamClan          Jawa_Wildsteam_Specialist 82
    Jawa_FreeDroidEnclaves      Jawa_Droid_Grunt          90
    Jawa_AscendantHelix         Jawa_Helix_Grunt         130

Every one clears the 3000 points the firings used by **more than twentyfold**. Also
checked and clean: all five set `humanlikeFaction` true, and the two factions with only
**2** `pawnGroupMakers` (Geonosian, Junkers) are missing the **Trader** maker, not the
Combat one — both carry an intact 4-option Combat maker.

### 🔴 The correction that matters: none of the above can explain the 18 firings
`IncidentWorker_RaidEnemy.TryResolveRaidFaction` (lines 58-73) returns **true immediately**
when `parms.faction` is already set and hostile:

    if (parms.faction != null && parms.faction.HostileTo(Faction.OfPlayer)
        && (!parms.faction.deactivated || parms.forced))
        return true;

`fire_raid` names the faction, so `UsableFactions` is never reached — `raidsForbidden`,
`MinPointsToGeneratePawnGroup` and the whole line-355 filter are **bypassed** on the exact
path the 18 firings took. ⇒ The empty firings are **downstream of faction resolution**, in
pawn-group generation, the raid strategy, or the arrival mode. Every FactionDef-field
hypothesis is now exhausted; the def is not where the answer is.

⭐ Consequence for whoever picks this up: the two findings above are about **play**
(the storyteller's own selection), not about `fire_raid`. Deepwater is answered for play
and still unexplained for `fire_raid`, like the other five.

### Live re-test NOT done this session — and why, so nobody repeats the attempt blind
The 585-mod game was up and the bridge free, but the item needs a MAP and the campaign save
`WORLDMAP_V1_original` has none (`currentMapId: null` — it is a world-only save).
`rimworld/start_debug_game_ready` was called and had not produced a map after **10 minutes**
on the full mod list; the driving script was killed, and the game fell back to `Entry`.
⇒ Budget a quicktest map on the FULL list at ≥10 min, or do this item on the minimal list
instead (`rimworld-debug-testing`), where a quicktest world is ~5 s.

## criteria
- [x] `Jawa_DeepwaterCompact` — reason named from the engine: `raidsForbidden = true`
      excludes it from `PawnGroupMakerUtility.UsableFactions`, so the storyteller can never
      pick it. Not a bug; a property of its own def.
- [ ] The other five — still open, but the search space is now much smaller. Every
      `FactionDef` field the engine consults is verified clean, and `TryResolveRaidFaction`
      short-circuits before any of them on an explicit `parms.faction`. ⇒ **Next step is
      NOT another def read.** Fire one raid for a non-Hutt faction on a map and read
      `effects.logs` on the `fire_raid` response itself — that is per-call log capture and
      it survives the `Reached max messages limit` that killed `drain_log` last time.
