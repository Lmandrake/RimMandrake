# WRECKAGE_VERMIN_SPAWN_1 — vermin spawn from the wreckage itself

Owner, 2026-09-12 (verbatim on the filing event): "Yes vermin should be able
to spawn from wreckage." Confirms the frozen fall_line.md design line ("Ship
vermin nests under the larger hulls, living on what falls") as a build
requirement, not just flavor.

## What already exists (checked 2026-09-12, BENCH)
- Biome-level wandering: the ship-vermin band (Scavrat, WompRat, Mynock,
  VFEI2_Fuelmite; vanilla Rat is biome-native) is in `wildAnimals` of the five
  biomes the Fall Line crosses via `BiomeCast_Ashkarr.xml`, deployed
  byte-identical (Mynock weights 0.3/0.3/0.3/0.2/0.5).
- ShipVermin mod (`src/RimMandrake/ShipVermin`, SHIP_VERMIN_MOD_1 closed
  2026-09-11): About + `RSW_Mynock_ShipVermin.xml` comp patch + alert DLL. No
  wreck-anchored spawner exists anywhere.

## spec
- A spawn mechanism anchored to wreckage things/structures (Fall Line hulks,
  wreck salvage sites, grounded ruins): nests under/inside the wrecks emit
  vermin over time — a comp on wreck defs or a MapComponent keyed to wreck
  presence, whichever survives contact with how the hulks are actually built
  (verify the wreck defs' identity first; do not guess defNames).
- Species drawn from the ship-vermin band; respect the ruled pressure curve
  ("Nuisance unless there are many").
- Mod Settings per MOD_OPTIONS_RETROFIT_1: wreck-spawning on/off, rate, which
  species.
- Home: the ShipVermin mod (RimMandrake tier — mechanism is generic
  "vermin from wrecks"; any campaign-specific wreck-def wiring goes in the
  Utinni layer).

## verify
On a quicktest map with a wreck structure placed: vermin appear attributable
to the wreck (not biome wander) at the configured rate; toggling the setting
off stops it; no spawns on wreckless maps from this mechanism.

## built 2026-09-12, FOUNDRY — offline complete, live verify OWED

Mechanism: `RM_CompProperties_VerminNest` / `RM_CompVerminNest`
(`src/RimMandrake/ShipVermin/Source/`) — a generic ThingComp, attached via a
comps-list patch to any wreckage ThingDef, that periodically spawns one wild
pawn of a settings-enabled species nearby. Reuses
`RM_MapComponent_VerminPopulation`'s existing group-tag pressure pool
(default tag `ShipVermin`, hard cap 12 — the SAME pool RSW_Mynock's breeder
already presses against), so a nest and a breeding population share one
ceiling. Home is the ShipVermin mod per the spec; the mechanism decides
nothing about which ThingDef is "wreckage".

Wiring (campaign-specific, RimUtinni layer):
`src/RimUtinni/UtinniPatches/Patches/WreckVerminNest_ShipChunk.xml` attaches
the comp to `ShipChunk_Mech` (Odyssey's "mechanoid ship chunk" — the exact
prop scattered six-per-hulk in `RUT_Jawa_GroundHulk`, and the only real
Thing the ground-hulk PrefabDef actually places that is debris rather than
a generic Ancient-Danger casket). Verified via `validate_patch.py --live
--defs` (592-mod live load set): 0 errors, ShipChunk_Mech resolves, the
outer conditional matches.

Mod Settings added to ShipVermin's own `ShipVerminSettings`
(`RM_ShipVerminMod.cs`): wreck-spawning on/off, a 0.25x-3x rate multiplier,
and a per-species checkbox roster (Mynock, Scavrat, Womp rat, VFEI2_Fuelmite
gated by GetNamedSilentFail, Rat).

Both `RM_CreatureBehaviors.csproj` and `RM_ShipVermin.csproj` build clean
(0 warnings, 0 errors) via the Windows-native dotnet toolchain.

## live verify attempted 2026-09-12, FOUNDRY — two real bugs found and fixed, RE-BLOCKING

Built a lightweight custom quicktest mod list (minimal 25-mod base +
`mandrake.rm.shipvermin` + `mandrake.rm.creaturebehaviors` + a session-only
scratch mod carrying a byte-identical copy of `WreckVerminNest_ShipChunk.xml`,
never committed) to avoid the full 597-mod campaign list — a
`start_debug_game_ready` on the full list crashed the game outright
mid-worldgen, matching the already-filed `NINEFOLD_DEBUG_GAME_READY_CRASH_1`
signature.

**Bug 1 — the wiring patch never actually attached the comp, on ANY mod
list, ever.** `jawa/get_defs` on `ShipChunk_Mech` showed only
`CompProperties_InspectString` — `RM_CompProperties_VerminNest` was absent.
`Player.log`: `Patch operation Verse.PatchOperationConditional(...) failed`.
Root cause: `ShipChunk_Mech`'s own raw XML (confirmed by reading
`Defs/Odyssey/ThingDefs_Buildings/Buildings_Gravship.xml` directly) has NO
literal `<comps>` element — `CompProperties_InspectString` is INHERITED from
`ShipChunkBase`, and `PatchOperationAdd` targets the raw per-def XML tree,
not the resolved/inherited one. The original patch comment's claim that
"ShipChunk_Mech already ships its own `<comps>`" was wrong. **Fixed**: added
the same check-or-create `<comps/>` dance `RSW_Mynock_ShipVermin.xml` already
uses. Confirmed live after the fix: `get_defs` now shows
`RM_CompProperties_VerminNest` attached.

**Bug 2 — even attached, the comp could never tick.** `ShipChunk_Mech`
inherits `tickerType` from `ShipChunkBase` -> `BuildingBase`
(`Defs/Core/ThingDefs_Buildings/Buildings_Exotic.xml` /
`Buildings_Base.xml`), and NEITHER declares one, so it resolves to the C#
default `TickerType.Never` (confirmed via `Verse.TickerType`/`ThingDef.cs` —
plain field, enum value 0). `ThingWithComps.Tick()` — and therefore every
comp's `CompTick()`, including `RM_CompVerminNest`'s — is only invoked while
the parent is on a tick list, which `Never` guarantees it never is. Proven
live: with Bug 1 alone fixed but `tickerType` still `Never`, 0 spawns after
270,190 ticks (already past the full 2-4 day / 240,000-tick worst case).
**Fixed**: patch now also sets `tickerType` to `Normal` on `ShipChunk_Mech`
specifically. Confirmed live: `get_defs` now shows `tickerType: Normal`.

**Both fixes committed** to `src/RimUtinni/UtinniPatches/Patches/
WreckVerminNest_ShipChunk.xml`, offline-validated (`validate_patch.py`, 0
errors).

**Still unresolved — RE-BLOCKING, not closing.** With BOTH fixes live (comp
attached AND ticking confirmed), spawned a fresh `ShipChunk_Mech`, ran the
population/species/reachability preconditions by code inspection (all
clear: no `RM_VerminPressureExtension`-carrying pawn exists in this mod set
so the population pool reads 0 of 12; `Rat` PawnKindDef exists and is
settings-enabled; open desert terrain around the spawn point), then advanced
the game (`rimworld/step_game_ticks` + `jawa/set_game_speed`) past 263,701
ticks — comfortably past the documented 240,000-tick worst case — with
`jawa/list_pawns` showing **zero** Rat (or any ship-vermin-band) pawn within
the nest's own radius (6-cell check around the wreck) the entire time,
while the wreck itself remained spawned and undamaged throughout. Two
ambient wild Rats did spawn elsewhere on the map (biome wander, far from the
wreck) — correctly NOT counted as nest output.

⇒ **A third defect remains in `RM_CompVerminNest.TrySpawn()` or its
`CellFinder.TryFindRandomCellNear` call**, not yet isolated (`TrySpawn`
fails silently on every branch — no log line distinguishes population-cap /
no-species / no-reachable-cell). Suspect candidates for the next pass: the
2×2 footprint's exact anchor cell vs. `parent.Position` used as the
reachability origin, or a live inspection of `nextSpawnTick`'s actual value
(no debug-report hook exists for this comp the way `RM_FloodedCanyonDebugActions`
has one — add one before the next attempt so the failing branch can be read
directly instead of inferred from silence).

Re-blocking rather than closing: the wiring is now measurably closer to
correct (two real, previously-unknown, 100%-blocking defects fixed) but the
item's own `## verify` — an actual observed spawn — is still not met.
