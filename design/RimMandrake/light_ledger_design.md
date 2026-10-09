# Light ledger — one radius per light, composed from every effect

Items: `LIGHT_LEDGER_ONE_1` (X-3 / TB-5 in `gpt_reviews/DESIGN_PASS_2026-10-08.md`) and the four
card rulings on `DEEPFIRE_WORLD_LIGHT_1` (X-9). Root-causes `SUN_SPHERE_GRAZE_PERSIST_1` and the
composition/save half of `TWILIGHT_WELL_LIGHT_STATE_1`.

## The defect class

`CompGlower.GlowRadius` is one field (`glowRadiusOverride ?? Props.glowRadius`, decompiled 1.6) and
**vanilla never saves it** — only `glowOn` and `glowColorOverride` are Scribed. Ten files in five
mods wrote it directly, each assuming it was the only writer:

| mod | writer | what it did to the field |
|---|---|---|
| TerminalBiomes | `RM_Building_SunSphere.RecomputeVisual` | culture radius, every 60 ticks — erased graze |
| TerminalBiomes | `RM_JobDriver_FeedOnGlow` (suulk graze) | `GlowRadius - loss` — erased by the above, lost on load |
| TerminalBiomes | `RM_MapComponent_WellLedger` (×2) | waning radius; lid-dark 0.1 overwritten by the next waning step, unsaved |
| EnvironmentalHazards | `RM_Comp_WarblingGlow` | `Props.glowRadius × wave` — erased any dimming on its lamp |
| LanternDeeps | `RM_AuroraCollapse.Apply` | `Props.glowRadius × mult` / back to `Props` — erased sippers, Dark |
| LanternDeeps | `RM_MapComponent_Sippers` (`SipperLedger`) | tolerance-guessing "did anyone write since me" |
| Abyss | `RM_MapComponent_Dark.LampPass` | `Props × factor`, skips krizzak lamps "so as not to fight" |
| Abyss | `RM_MapComponent_KrizzakDimming` (×2) | feed / recover from a remembered original |
| LuminousPigment | `MapComponent_DeepfireLights` (+ `.Worn`) | sole owner of its proxies' radius |

`RM_AbyssLight`'s `overlightRadius = 0` is a startup DEF edit, not a runtime write — out of scope.

## The helper

Two source files under `src/RimMandrake/_Shared/LightLedger/`, compiled INTO each consuming
assembly by `<Compile Include="..\..\_Shared\LightLedger\*.cs" Link=…>` (winbuild stages any
`..` Compile path; the `.srchash` covers linked files, so editing the shared file makes every
consumer's DLL stale until rebuilt — the push guard catches that).

- `LightLedgerKernel.cs` — no Verse type. `Compute(baseRadius, modifiers)`:
  `r = base × Π mul − Σ sub`, then `min(r, every cap)`, then `max(r, 0)`. Offline selftest compiles it.
- `LightLedger.cs` — `internal static class RimMandrake.Shared.LightLedger` (internal, so the
  copies in TerminalBiomes and EnvironmentalHazards, which TB references, never collide).

**Why no shared assembly:** the five writer mods share no common dependency (Abyss depends on
neither FlowWorks nor CreatureBehaviors), and adding one to every mod is a load-order change for a
200-line helper. **Shared state is vanilla-typed** — `Dictionary<CompGlower, Dictionary<string,float>>`
plus `Dictionary<CompGlower, Thing>` — parked in one `AppDomain` data slot
(`RimMandrake.LightLedger/1`), so every assembly's copy reads and writes the SAME ledger without a
type reference. Changing the stored shape means bumping the slot suffix and rebuilding every
consumer, together.

API (each owner names its modifier `"<mod>.<effect>"`):

```
SetBase(g, owner, radius)        the light's own radius (default Props.glowRadius); last writer wins
SetMul(g, key, factor)           1 clears it
SetSub(g, key, cells)            0 clears it
SetCap(g, key, maxRadius)        negative clears it
Clear(g, key) / Effective(g) / Describe(g)
Tag(g, "deepfire") / HasTag(g, tag)
SetCarrier(g, thing) / CarriesLitLight(thing)
```

Every Set recomputes once and writes `GlowRadius` only on a real change (≥0.01), and re-registers
with the glow grid **only while the lamp is lit** (`ForceRegister` on an unlit lamp re-lights an
unpowered one — the bug `RM_Comp_WarblingGlow` already found once). Destroyed lights are pruned lazily.

## Save-compat

The ledger is **not saved**, deliberately: vanilla does not save the radius either, and each effect
already owns (or now gets) its own Scribed input. On load every owner re-asserts its modifier from
its own state — `SpawnSetup` / `FinalizeInit` / its next pass. New Scribed fields:
`RM_MapComponent_GlowGraze.graze` (TerminalBiomes, by reference) and `WellLedger.lidDark`. No save
key is renamed or removed; an old save simply loads with no graze and wells not lid-dark.

## Migration (one commit each)

1. Helper + kernel selftest + **SunSphere/graze** (base = culture radius, `tb.graze` sub, Scribed).
2. **Wells** — base = waning radius; lid-dark = `tb.liddark` cap 0.1, Scribed flag, re-applied on load and to new wells.
3. **WarblingGlow** — `eh.warble` mul around the ledger's base.
4. **LanternDeeps** — `ld.aurora` mul; sippers `ld.sipper` mul (floor 0.25); `SipperLedger` deleted.
5. **Abyss** — `abyss.dark` mul, `abyss.krizzak` mul; the two now compose instead of stepping aside.
6. **LuminousPigment** — `SetBase` on proxies; proxies and the glow tank tagged `deepfire`; worn/hediff proxies carry their pawn.
7. A static selftest refuses any `GlowRadius =` write outside `_Shared/LightLedger/`.

## DEEPFIRE_WORLD_LIGHT_1 (card 2026-10-08)

| ruling | change | toggle (default) |
|---|---|---|
| creatures drawn to deepfire | `RM_JobGiver_SeekGlow` also considers `deepfire`-tagged lights of any faction; it always BASKS at them, never grazes (a proxy fed out would just respawn) | TB `seekGlowDrawnToDeepfire` (on) |
| deepfire-lit colony more visible at night | LP map pass: at night on a player home map, `GameComponent_ColonyVisibility.Adjust(+n × perLight)` via soft type lookup (Visibility optional) | LP `deepfireNightVisibility` (on), `deepfireVisibilityPerLight` 0.05/2500 ticks **PROVISIONAL** |
| glowing pawn gets no lacquer cloak | `CompLacquerCloak` treats `LightLedger.CarriesLitLight(wearer)` as seen | Scarlands `lacquerCloakDeniedWhileGlowing` (on) |
| Abyss Dark cannot swallow deepfire | `LampPass` skips `deepfire`-tagged lights explicitly (today it was true only because proxies are Ethereal; the glow tank WAS dimmed) | Abyss `darkSparesDeepfire` (on) |

The ledger itself has no toggle: it is plumbing, and each effect keeps its own.
