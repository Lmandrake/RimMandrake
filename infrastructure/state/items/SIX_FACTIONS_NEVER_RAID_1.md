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
