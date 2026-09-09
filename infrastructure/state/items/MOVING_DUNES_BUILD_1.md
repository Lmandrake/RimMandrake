# MOVING_DUNES_BUILD_1 — build the dunes engine

Spec: `design/MOVING_DUNES_DESIGN.md` (v2). Mod:
`src/RimMandrake/MovingDunes/`, packageId `mandrake.rm.movingdunes`,
assembly `RimMandrakeMovingDunes`, namespace `RimMandrake.MovingDunes`.

## spec

Werner slab transport on Odyssey's `Map.sandGrid`, source/sink map edges,
`RM_DuneMaterialDef` skins, burial caches with a `BuryThingsAt` API, plant
choke, and a per-map tinted sand layer. Everything a designer might retune is
data (RULED). The design's §5 "Out, explicitly" list is honoured: no
multi-material-per-map, no own grid, no snow drifting, no sand as a haulable
item, no burying pawns or turrets, no worldgen, no non-Odyssey fallback.

## verify

- `dotnet build …\RimMandrake_MovingDunes.csproj -c Release` → **0 warnings,
  0 errors** (run 2026-09-09).
- `python3 src/RimMandrake/MovingDunes/Source/selftest_moving_dunes_constants.py`
  → **13/13**. This is the design §6.3 guard: it fails when a vanilla constant
  the Harmony patches recognise BY VALUE stops appearing in the decompiled
  source, which is a silent failure play can never surface.
- `validate_patch.py Patches/BiomeBindings.xml --defs <Data> <workshop> <Mods>`
  → 0 errors; both xpaths hit (Core `Biomes_WarmArid.xml`, plus GRiNDTerra's
  redefinition of the same defs).
- `deploy_custom_mods.py --mod MovingDunes` → clean plan, 6 files, packageId
  unique across tiers.

## criteria

1. A dune-field map's sand persists (ambient decay suppressed) and MOVES
   downwind; drifts bank behind walls and refill dug pits. — **built, not yet
   observed live.**
2. Loose wild items under deep drift become caches and come back out when the
   wind turns. — **built, not yet observed live.**
3. A map's material def, not code, carries every tuning number. — **done.**
4. The tint route is decided by the design's shader gate. — **OWED, see below.**

## what is done

| file | what it is |
|---|---|
| `Source/RM_DuneMaterialDef.cs` | the whole knob panel + `RM_DuneGlobalsDef`, with ConfigErrors |
| `Source/DuneFieldExtension.cs` | biome opt-in + per-weather storm override |
| `Source/DuneFieldRegistry.cs` | Map→field lookup the hot-path prefixes use |
| `Source/MovingDunesMod.cs` | Harmony bootstrap (loud-failure per rule) + hide-depth pass + DefOf |
| `Source/Patch_SandGrid.cs` | `CanHaveSand` (sand holds on sand) + `AddDepth` (decay suppression) |
| `Source/SectionLayer_DuneSand.cs` | the skinned layer + vanilla-layer suppression prefix |
| `Source/MapComponent_DuneField.cs` | wind state, transport batches, source/sink influx, mass cap, burial trigger, plant choke |
| `Source/Thing_BuriedCache.cs` | the container + the erosion reveal |
| `Source/DuneBurialUtility.cs` | `BuryThingsAt` public API + the wild/unclaimed rule |
| `Source/MovingDunesDebugActions.cs` | dev handles (report / shift wind / run 100 batches / seed drift / bury here) |
| `Source/selftest_moving_dunes_constants.py` | the §6.3 constants guard, 13 checks |
| `Defs/`, `Patches/`, `Languages/`, `About/` | generic sand material, globals, cache ThingDef, Desert + ExtremeDesert bindings |

~1,900 lines C# + XML (the design estimated 1,100–1,400 C#; the overage is
almost entirely the ConfigErrors and the citation comments, not extra mechanism).

## OWED — the shader-tint gate (design §2 "Rendering", §7.1)

**Not run. This item stays open until it is.**

The one honest unknown: does the vanilla sand shader (`MatBases.Sand`, loaded
from `Materials/Misc/Sand`) respect material `color`? It cannot be answered
from source — the material asset lives in the game's packed resources, and no
bridge tool reads a live `Material`'s shader.

It is NOT a cheap quicktest as the design assumed: the mod is not in
`ModsConfig.xml`, so the gate needs a deploy + a mod-list write + a restart.
It was deliberately NOT run tonight against the owner's live 599-mod session
for a one-field decision. It should ride the next load round, not burn a slot.

**Run sheet — do this on any load that has MovingDunes active:**

1. Land on a Desert or ExtremeDesert map (`RM_Dunes_Sand` binds both).
2. Confirm arming: dev action *Moving Dunes → Dune field: report*. Expect
   `canHaveSand=True decaySuppression=True vanillaLayerSuppression=True`.
3. Edit `Defs/DuneMaterialDefs/Materials.xml`: set `<tint>(0.35,0.55,1.0)</tint>`
   (a blue no desert could be mistaken for) with `tintMode` **MaterialColor**.
   Deploy, load, seed drift (dev tool *seed drift at cell*), LOOK.
4. Blue sand ⇒ `MaterialColor` is correct; ship it, revert the tint to
   `(1,1,1)`, done.
5. Still sand-coloured ⇒ set `tintMode` to **VertexColor** and repeat step 3.
   That path is already implemented (it surrenders the pollution mask, which
   §2 explicitly permits on skinned maps) and needs no new code.
6. Neither works ⇒ the shader ignores both channels. Fall back to a tinted
   TEXTURE: recolour `Misc/Sand`'s main texture per material and set it on the
   per-map instance. That is new code and a new item, not a rider on this one.

Note the design's own crest-shading is deliberately routed through ALPHA in
both modes, so relief reads correctly whichever way the gate falls. Only the
COLOUR depends on it.

## other owed / recorded decisions

- **Cache art.** The design says "low-bump graphic". `RM_Dunes_BuriedCache`
  ships `drawerType None` instead: a texPath that does not resolve renders
  nothing and reports nothing, and inventing one would be exactly the silent
  failure this mod's discipline is against. The def already carries
  `hideAtSnowOrSandDepth 0.30`, so a sprite drops in later with no other
  change. One PNG, whenever art time exists.
- **Hide-depths are a startup C# pass, not an XML patch** (design §2 says
  patch). An xpath cannot see `category` on most item defs — they inherit it
  from an abstract parent and PatchOperations run before inheritance resolves.
  The pass reads post-inheritance truth, touches only defs still carrying
  vanilla's 99999 default, and logs its own count (and errors on a measured
  zero).
- **Supply is a RATIO plus a base, not a bare `influxPerDay`.** The design's
  §2 supply semantics are "influx ≪ / ≈ / > loss". `influxLossRatio` says that
  literally and self-tunes; `influxPerDay` is the "per-biome base" the design
  also names and doubles as the cold start (a map holding no sand loses none,
  so it could otherwise never be given any).
- **Mass cap is binding.** Design §7.3 (may a material legitimately bury a map
  permanently?) is owner-level and UNRULED; the design's own stated default
  until then is cap-binding, and that is what ships.
- **Cache cap is refuse-new, not oldest-merge.** At `maxCachesPerMap` no new
  cache CELL is opened; existing caches still merge, so an advancing front
  keeps working. Oldest-merge is more machinery than the save-bloat risk earns.
- **`SandGrid.DepthGrid_Unsafe` is internal** — a modded layer cannot read the
  NativeArray the vanilla one does. `GetDepth` is used instead (one bounds
  check per read, only on section regen).
- **Not deployed.** `deploy_custom_mods.py --apply` not run and `ModsConfig.xml`
  not touched: both are expensive-list acts and neither is useful before the
  gate above rides a load round.
