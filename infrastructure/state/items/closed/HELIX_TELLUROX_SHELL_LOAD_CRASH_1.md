# HELIX_TELLUROX_SHELL_LOAD_CRASH_1

HelixTellurox crashes mod load to Core-only: a def parse error
(MissingMethodException: default ctor for System.String) breaks RSW_TelluroxShell,
whose null butcherProducts ref NREs corpse-gen.

## spec

Determine whether `mandrake.rsw.helixtellurox` genuinely crashes a load to
Core-only, and if so, what actually triggers it — the mod was disabled in the
live ModsConfig and a full source-verified field/type audit of
`Races_Tellurox.xml` found no defect on its own.

## Live test (2026-09-04, FOUNDRY, isolated minimal-list restart)

Took the working 21-mod MINIMAL list (already confirmed clean this session —
two prior launches loaded fine, bridge up, real quicktest colonies playable)
and added exactly one mod: `mandrake.rsw.helixtellurox`. Relaunched via Steam.

**Result: the game DID fall back to Core-only (6 mods)** — `ModsConfig.xml` was
rewritten by the engine itself to just Core+expansions, matching this item's own
description exactly. `harvest_log.py --stale-ok` confirmed the fallback
(`ModsConfig 6 active mods`) and the VERY FIRST exception in the fresh
`Player.log`, before any per-mod banner prints, is:

```
Exception loading from System.Xml.XmlElement: System.MissingMethodException:
Default constructor not found for type System.String
  at Verse.DirectXmlToObject.ObjectFromXml[T] (...)
```

**The exact signature this item names.** This is a genuine live reproduction, not
a theoretical concern — the crash-to-Core-only symptom is real and happens on the
very next launch after enabling this one mod.

## ⚠️ NOT a clean isolation — read before acting on it

HelixTellurox ships **no C# assembly and no .cs file at all** (pure XML content,
confirmed: `find src/RimStarWars/HelixTellurox -iname "*.dll" -o -iname "*.cs"`
returns nothing) — a `MissingMethodException`/`TypeLoadException` class of crash is
normally an assembly-loading problem, which makes HelixTellurox a structurally
unlikely direct cause on its own, consistent with this item's own prior audit
finding no defect in `Races_Tellurox.xml`.

The same crashed log also contains **several unrelated, pre-existing errors** that
were latent in the MINIMAL list *before* HelixTellurox was ever added —
`mandrake.rsw.droidworks` and `Neronix17.OuterRim.Core` were already active in
MINIMAL in the two earlier clean launches this session:
- `Error while instantiating a mod of type OuterRimCore.OuterRimCoreMod:
  ... NullReferenceException`
- Four `RecipeDefs_Droidworks.xml` / `Items_Droidworks.xml`:
  `ArgumentNullException: Value cannot be null. Parameter name: s` (a
  `Verse.ParseHelper.ParseIntPermissive` float-parse failure)
- Multiple `XML error: <everVisible>... doesn't correspond to any field in type
  HediffDef` for `RSW_DW_PoweredDown`/`RSW_DW_RestrainingBolt` (Droidworks)

None of these name HelixTellurox or Tellurox. **So this run proves "the crash-to-
Core-only symptom reproduces when this mod is added" but does NOT by itself prove
HelixTellurox's own content is the trigger** — it could be an interaction (this
mod tips something else in the list over an edge) rather than a defect in
HelixTellurox itself.

## criteria

Not yet met. To close this cleanly, isolate further: relaunch plain MINIMAL alone
again (rule out simple flakiness — it loaded clean twice already this session, so
this is a low-probability check but a cheap one), then add HelixTellurox to a
MUCH smaller list (bridge tier + whatever it actually needs, without
droidworks/OuterRim.Core in the mix) to see if the crash still reproduces without
those two confounds present.

## verify

`harvest_log.py --stale-ok` after the isolated relaunch; the decisive read is
whether `ModsConfig.xml`'s active-mod count matches what was launched with (no
fallback) and whether the exact `MissingMethodException` signature above appears
or not.
