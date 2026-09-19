# DUMP_DRAWSIZE_CAPTURE_1 — RimDefDump was skipping every Unity value struct, not just GraphicData

Filed by a concurrent BENCH session claiming the def dump had no `drawSize` field
anywhere. Re-confirmed independently before touching anything.

## Where the gap actually lives

Not `measure/dumpdb.py` (the item's title, and its own filename hint). That script
stores each def's JSON verbatim in `defs.json` with no field-level filtering — it
is not where anything gets dropped. The capture-side tool is
`src/RimMandrake/RimDefDump/Source/DefReflector.cs`, a reflection walker that
serializes the LIVE post-inheritance def graph. Its `IsSkippedType()` blanket-skips
anything in the `UnityEngine` namespace, written to keep heavy asset objects
(Texture2D, Material, Mesh, ...) out of the dump. `Vector2` — what `drawSize` is
typed as — lives in that same namespace, so it, and every other lightweight Unity
struct (`Color`, `Color32`, `Quaternion`, `Rect`, `Bounds`) on every def in the
population, was silently discarded at the field-selection step. Whole-population
gap, confirmed — matches the "no statBases on any ThingDef, no colour on any
ColorDef" precedent this project already had.

## Confirmation (against the live capture, before fixing)

`GravEngine` and `GravshipShieldGenerator` both set
`<graphicData><drawSize>(3,3)</drawSize></graphicData>` in raw XML (checked via
RimSage `get_def_details`, raw inheritance). Queried `defs.sqlite` via
`measure.dumpdb.DumpDB` (not grep/strings — instrument, not scan) for both
defNames' `graphicData` JSON block: present, but its keys were
`$type, addTopAltitudeBias, allowAtlasing, allowFlip, cachedGraphic, drawRotated,
flipExtraRotation, graphicClass, ignoreThingDrawColor, linkFlags, linkType,
onGroundRandomRotateAngle, overlayOpacity, renderInstanced, renderQueue,
shaderType, texPath` — no `drawSize`, no `color`, no `colorTwo`. Gap confirmed for
real, not just trusted from the filing.

## Fix

`DefReflector.cs` `IsSkippedType()`: added a narrow `SafeUnityValueTypeNames`
allowlist (`Vector2`, `Vector3`, `Vector4`, `Color`, `Color32`, `Quaternion`,
`Rect`, `Bounds`) checked before the blanket UnityEngine-namespace skip. Everything
else in `UnityEngine` (Texture, Material, Mesh, GameObject, Component, ...) is
still skipped exactly as before — this is an allowlist carve-out, not a reopened
namespace. Applies to both `FieldsOf()` (field-selection) and `WriteValue()`
(value-write), since both call the same `IsSkippedType()`. Class-level doc comment
updated to match.

Built clean: `"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build
src/RimMandrake/RimDefDump/Source/RimDefDump.csproj -c Release` — 0 warnings, 0
errors, `RimDefDump.dll` rebuilt in `src/RimMandrake/RimDefDump/1.6/Assemblies/`
(committed alongside the source, per this repo's existing convention for this
mod). Not deployed to the game copy — that happens in the next down window, per
`rimworld-deploy`.

## What still needs a live dump

The fix is capture-side C#; it cannot be proven against real output until the
companion runs inside a game load and writes a fresh `DefDump/`. **Next natural
game-up window**: re-capture, then re-check `GravEngine`/`GravshipShieldGenerator`
in the new `defs.sqlite` — `graphicData.drawSize` should appear as
`{"$type":"Vector2","x":3.0,"y":3.0}` (and `color`/`colorTwo` similarly on
GraphicData/ColorDef). If it does, this item is fully proven and the
bodySize-visual normalization work (Law 1) can read `drawSize` from the dump.
No further code change expected to be needed at that point.
