# BRIDGE_PAWN_THOUGHTS_CARAVAN_GAP_1 — `jawa/pawn_thoughts` cannot read a caravan pawn

Surfaced 2026-09-02 trying to live-verify `TravelCompanions` (a
`Thought_Situational` from Caravan Adventures that only evaluates while a
pawn is actually IN a caravan) for `PAWN_FLAVOR_SILENT_NONAPPLY_1`. Formed
a real caravan via `jawa/caravan_create` with 3 quicktest colonists, then
called `jawa/pawn_thoughts` on one of them by both bare id and name —
both refused: `"No spawned pawn matching '<x>'. N pawns are spawned."`
Caravan members are world pawns (de-spawned from the map, tracked via
`WorldObject_Caravan`), and `jawa/pawn_thoughts`'s pawn lookup only
searches spawned map `Thing`s (`FindPawn`, same helper `jawa/list_pawns`
etc. use) — it never checks `Find.WorldPawns` or a caravan's own pawn
list.

## spec

Any `jawa/pawn_*` tool that resolves a pawn by id/name should also try
`Find.WorldPawns.AllPawnsAlive` (or the specific caravan's
`PawnsListForReading`) when the map lookup misses, so a pawn currently in
a caravan (or otherwise off-map: a prisoner in transit, a wounded pawn on
another map, etc.) is reachable the same way. This is squarely
`rimbridge-companion` territory (`JawaBench.BridgeTools`), not a
`rimbridge`-skill driving question.

## verify

- `jawa/pawn_thoughts` (or a shared `FindPawn` helper used by several
  tools — check for one before touching each call site individually)
  finds a caravan-member pawn by id and by name.
- Re-run the actual motivating case: form a caravan of colonists who don't
  know each other well, read `TravelCompanions`'s live stage/text off one
  of them, confirm it reads the Phase-2-approved prose rather than
  vanilla ("Third wheel" etc.) — this is the live proof
  `PAWN_FLAVOR_SILENT_NONAPPLY_1`/`PAWN_FLAVOR_PHASE2_APPLY_1` are still
  owed for their DLC/workshop-mod-owned rows.

## criteria

A caravan pawn's thoughts are readable via the bridge without dissolving
the caravan first, and the `TravelCompanions` live text check above
passes or fails on real evidence (not blocked on tooling).

## 2026-09-02 (FOUNDRY) — fix written and compiled, NOT deployed, not live-verified

Confirmed the hypothesis exactly: `JawaBenchPawnTools.cs`'s `FindPawn` (shared by
~20 tools including `jawa/pawn_thoughts`) builds its whole search list from
`foreach (var m in maps) all.AddRange(m.mapPawns.AllPawnsSpawned)` — `Find.Maps`
only, nothing else. `Find.WorldPawns.AllPawnsAlive` (confirmed real via RimSage,
`RimWorld/Planet/WorldPawns.cs`) is the population that actually holds caravan
members (`PassToWorld()` puts every caravan pawn there) and other off-map pawns.

**Fix**: added a fallback block to `FindPawn` — when the existing map-pawn pass
(id / `Thing_`-prefixed id / exact ThingID / name, unchanged, same order) finds
nothing, it now tries the identical match sequence against
`Find.WorldPawns.AllPawnsAlive` before giving up. A pawn matched on the map pass
still returns from that pass exactly as before — no behavior change for any
currently-working caller. A pawn matched on neither list gets an updated (but
still clearly a "not found") error string naming both pool sizes searched.

**Compiled, not deployed**: `python.exe build.py --gm` — Build succeeded, 0
Warning(s), 0 Error(s), bundle ships only `JawaBench.BridgeTools.dll`. Deploy
plan shows the expected commit-mismatch (game copy predates this change) — did
NOT run `--apply`: the game is up and another FOUNDRY fork holds the bridge for
an unrelated restart, and deploying a companion DLL needs the game DOWN (the OS
holds the file open) plus a subsequent restart for RimBridgeServer to
re-register the tool set.

**Owed to the next game-down window + restart** (exact steps, per the
`rimbridge-companion` skill's cycle):
1. Kill RimWorld, `python.exe build.py --gm --apply`, relaunch via Steam.
2. Form a caravan (`jawa/caravan_create`), confirm a member pawn now resolves
   by id AND by name via `jawa/pawn_thoughts` (or any `jawa/pawn_*` tool) —
   read back the actual pawn snapshot, not just absence-of-error.
3. Re-run the motivating case: read `TravelCompanions`'s live stage/text on a
   caravan member with low relationship — confirm it shows the Phase-2-approved
   prose, not vanilla ("Third wheel" etc.). This is also
   `PAWN_FLAVOR_SILENT_NONAPPLY_1`/`PAWN_FLAVOR_PHASE2_APPLY_1`'s own still-owed
   live proof for their DLC/workshop-mod-owned rows — close those alongside this
   one if it passes.
4. Also spot-check that a genuinely nonexistent pawn id still returns the same
   "not found" refusal shape (no regression in the negative case).

Item stays `doing` — no live proof yet.

## 2026-09-02 — deployed at the game-DOWN window (FOUNDRY)

`python.exe build.py --gm --apply` run the moment the owner said the game
was down (BENCH was concurrently driving its own reboot for other mods on
the same signal — this is a different target file,
`BridgeTools/JawaBench/JawaBench.BridgeTools.dll`, no collision). Build
succeeded 0/0, deployed clean. Commit-mismatch resolved
(`acec5065627f` -> `aa9ab7fa3053`). Still owed once the game is back up:
steps 2-4 from the note above (form a caravan, confirm pawn-by-id/name
resolution, the `TravelCompanions` live-text check, the negative-case spot
check).

## 2026-09-03 (FOUNDRY) — live-verified, core fix proven; TravelCompanions text check still blocked on tooling

On a trimmed quicktest list (Core/Harmony/Biotech/Droidworks/IonWeapons/Bridge —
no Caravan Adventures), formed a caravan of 2 colonists via `jawa/caravan_create`
(`Thing_Human283`, `Thing_Human289`). `jawa/pawn_thoughts` on the now off-map
caravan member:

- By id (`Thing_Human283`): succeeds, reads real thoughts (`NewColonyOptimism`,
  `Expectations`) — this exact call refused before the fix.
- By name (`Blas`): succeeds identically.
- Negative case (`NoSuchPawnXYZ123`): still refuses cleanly, and the refusal
  message now correctly names BOTH pools searched ("15 pawns are spawned, 20
  are world pawns") — no regression in the not-found shape.

**Core criterion met**: a caravan pawn's thoughts are readable via the bridge
without dissolving the caravan first.

**Still genuinely blocked, not done here**: the `TravelCompanions`-specific
live-text check needs Caravan Adventures active, which this trimmed list
doesn't carry — that's the DLC/workshop-mod-owned row this item said to close
"alongside this one if it passes," and it's a different, still-open check
(`PAWN_FLAVOR_SILENT_NONAPPLY_1`/`PAWN_FLAVOR_PHASE2_APPLY_1`), not this
item's own scope. Not closing those.

Cleaned up: killed the test process, restored `ModsConfig.xml` (589 mods,
confirmed on disk after exit), released the bridge.
