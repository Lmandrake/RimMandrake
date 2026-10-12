# STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY (HARNESS tool gap, JawaBench companion)

`pyre_furnacebeast_warmth` is UNMEASURED by construction: the bar is a felt-temperature offset,
`RimMandrake.Pyrelands.FurnaceWarmthField.OffsetFor(Pawn)` (public static, CompFurnaceWarmthAura.cs), which also feeds the
`Thing.AmbientTemperature` postfix. `jawa/static_call` coerces int/float/bool/string/IntVec3/Map/Def only
(JawaBenchCompanionProbeTools.cs), so no tool can hand it a Pawn.

Spec (companion DLL unit, not built here): in `jawa/static_call`'s argument coercion add
`else if (typeof(Thing).IsAssignableFrom(pt))` -> resolve the arg as a ThingID (`Human123`) or thingIDNumber on the current
map (then every map), refuse with the candidates when not found or when the found thing is not assignable to `pt`.
Also useful: `jawa/pawn_ambient` reading `pawn.AmbientTemperature` vs `pawn.Position.GetTemperature(map)` (the difference
is every AmbientTemperature postfix, ours included).

Then validation.furnace_warmth reads OffsetFor(colonist) beside the penned beast and again 10+ cells away: > 0 beside,
0 away, is the state half of the bar.
