# The Long Shade — what's in the shade (volley turn 3 ideation, 2026-09-29)

Item: `LONGSHADE_BEDAZZLE_SITTING_1`, volley turn 3. Status: ideation for the owner; nothing
here is ruled.

Builds on: `desert.md` (frozen sheet — §1, §4 "the sprint economy", "the shelter is the trap",
"the patch is a commons", §8 "middens / dew line / wide gaps", §9 "permanent golden hour",
§10 engine facts), `long_shade_bedazzle_2026-09-27.md` (thesis + Rulings Q1–Q12),
`longshade_bedazzle_review_2026-09-29.md` (census, scorecard, slate). Nothing below reopens a
ruling. Invented names follow the ruled Desert register (doubled consonant, 5–7 letters,
-a/-ik/-ok); descriptive English for flora.

## 0. The owner's words this turn

Verbatim, typed (2026-09-29):

> *"It's ok… but a tad boring unless we get really strict about the dashing animal behavior.
> If we can do that it's quite interesting. But the shade should be more interesting. That's
> where everything's hanging out. Read the original sheet again about those shaded regions
> and let's do some ideation around them what's in there to discover or fear other than "all
> the animals?" Might this tie into young sarlacc raids? (One at a time) or juvenile sarlacc
> emergences? Maybe some of those shady spots aren't so natural after all? Inhabited
> definitely could have some great material here. Broken down sand crawlers and other
> vehicles. Desperate moisture farmers. I like the golden hour concept. A perpetual beautiful
> sunset. … Now generate many more possible ideas that are very different than our other
> biomes. Let's spice this baby up!"*

Standing from turn 2: Sh'kaar ideoligion **PARKED** (not developed here) · the dung plant is
**maidenbloom** · golden hour is **IN** · the artist-inspiration mod is
`ARTIST_BIOME_INSPIRATION_MOD_1` (one hook line in §3, nothing more).

**Name-sweep record (this pass).** New invented names used below — `mirrak`, `tollok`,
`harrok`, `skellok` — are **0 files** under `src/ design/ infrastructure/ skills/` and 0 lines
in `infrastructure/artpipe/registry.jsonl` (probe `korrum`: 37 files — the instrument sees).
Rejected as taken: *vellok* (20 files), *kessik* (46). ⚠️ The Wookieepedia search probe failed
for the control (`bantha`) too, so **canon-collision is UNMEASURED** for these four — re-sweep
before any def.

## 1. Strict dashing — can we enforce rest-dash-rest?

**Verdict: yes, and most of it is already on the bench.** Strict dashing is not one mechanic;
it is four, and three of them are extensions of shipped code. The owner's condition — *"really
strict about the dashing animal behavior"* — is met when (a) the open ground *costs*
something a creature can measure, (b) the cost is bounded by body size, (c) creatures plan
routes shade-to-shade instead of straight lines, and (d) resting is what the shade is for.
Build all four and "nothing pursues" stops being a ban we police and becomes physics the
animals obey.

### 1.1 What already ships (MEASURED from `src/RimMandrake/CreatureBehaviors/Source/`)

| piece | what it does today | what strict dashing needs from it |
|---|---|---|
| `RM_MapComponent_ShadeGrid` (151 lines) | `ShadeAt(cell)` 0..1; roofed = 1; else falloff from any building with fillPercent ≥ 0.8 or plant with visualSize ≥ 1.5 within **radius 2, isotropic**; full recompute every 2000 ticks | 🔴 **isotropic** — a ring round every caster, not a shadow. The sheet says *"a shadow four times its own height"* thrown one way forever. See 1.3 — this is the single most important upgrade in this document |
| `RM_HediffComp_ShadeDrivenSeverity` | severity/day lerped between `severityPerDayInSun` and `severityPerDayInShade` by `ShadeAt` | **is already the heat-load engine** — set sun rate positive, shade rate negative and it accumulates in the open and bleeds off in shade. XML only, except: it is gated on the `heatDrivenBurstEnabled` setting (needs its own toggle) and it has no body-size term (1.2) |
| `RM_CompHeatBurstPredator` + `RM_HeatDrivenBurst` | burst → decay → forced Goto to shade when fatigued; polling comp, no Harmony | the predator half of strict dashing is **done** (bearer: `RSW_WraidAlpha`; dakkra def owed) |
| `RM_JobGiver_WanderInShadeGrid` / `RM_ShadeSeekingWanderExtension` | wander prefers shaded cells | becomes the *rest* job (stay put, idle in shade) |
| `RM_JobGiver_SeekShade` / `RM_SeekShadeExtension` | Greentide kit: go under a **roof** past a temperature threshold | reads `roofGrid`, not the grid, and temperature is map-wide (§10) — **superseded for this biome** by 1.2's heat-load trigger |
| `RM_HediffComp_ShadeStagger` | vorrel victim staggers toward shade | the "collapse" end state already has a walker |
| `RM_Comp_ShadowCaster` + follower | gloomcast's shadow carries pirrik | the gloomcast is already a *moving* shade cell the grid must count |

### 1.2 What new work it takes

1. **Heat load — `RM_SunLoad` hediff (XML on the shipped comp + ~20 lines).** Stages:
   *warm* → *heat-laden* (MoveSpeed ×0.8) → *overheating* (Consciousness −, pain) →
   *sunstruck* (downed; lethal if it stays in sun). Positive in sun, negative in shade, so
   **rest time is set by distance run** — the sheet's "rest is thermal accounting" verbatim.
   Add one prop to `RM_HediffCompProperties_ShadeDrivenSeverity`: `bodySizeExponent`, rate
   in sun divided by `bodySize^k`. That single term **is** "dash range is a function of size":
   a bs-0.3 tebbra has seconds, a bs-16 gloomcast has a day. Applies to **colonists too** —
   the player dashes under the same law (the most important consequence; see §2 D1, §4 W1).
2. **The patch graph — `RM_MapComponent_ShadePatches` (~150 lines, medium).** On each grid
   recompute: flood-fill cells with `ShadeAt ≥ 0.6` into patches, record each patch's
   centre, rim cells and area, and link two patches when their nearest-edge gap is ≤ the
   longest dash any resident can make. Per body-size band, a patch's **reachable set** is
   precomputed. This is also what the harbour scorer (ruled marquee #1) and the named gaps
   (Q12) want — build it once.
3. **Sun-cost pathing — one Harmony postfix (~60 lines, small; the LongShade mod already
   carries Harmony for the dewfringe gate).** 🔑 MEASURED via RimSage (decompiled 1.6):
   `PathRequest` has a public `IPathGridCustomizer customizer` whose `GetOffsetGrid()` returns
   a `NativeArray<ushort>` of per-cell cost offsets — vanilla uses it for
   `UsedRectPathGridCustomizer` (roads avoid structures) and `BreachingGrid`. Normal pawn
   movement (`Pawn_PathFollower.GenerateNewPathRequest`) passes **none**. A postfix there
   attaches one shared per-map "sun cost" grid (cost ∝ 1 − ShadeAt, rebuilt with the grid)
   for any pawn whose race carries `RM_DashExtension`. Result: **every vanilla job** — eat,
   flee, hunt, herd-follow, go-to-mate — routes shade-to-shade automatically, with no job
   giver rewritten. This is what makes "strict" cover behaviour we did not write.
4. **The dash itself — `RM_JobGiver_Dash` + `RM_JobGiver_Rest` (~120 lines, small–medium),
   inserted at `Animal_PreMain`.** Rest: in shade with sun-load > 0 → idle/lie down in the
   deepest cell the hierarchy allows (strongest takes the centre — `bodySize` + predator
   flag rank; the weak take the rim). Dash: sun-load 0 and a need elsewhere → Goto the next
   patch on the graph with `LocomotionUrgency.Sprint`. Exposed with no reachable patch in
   range → **sprint to nearest shade regardless of who is in it** ("arriving overheated at a
   shelter already full" — the sheet's worst moment, now emergent). A pre-dash pause
   (60–180 ticks at the rim, facing the target) gives the §9 signature image: *an animal at
   the edge of a shadow, deciding.*
5. **Signalling before the run (optional, small).** A dashing animal checks the target
   patch's occupants first; a predator present there → pick another or wait. §4 "nobody
   commits without asking". A mote/call gives the player the read.

### 1.3 The directional grid — make the mechanical shade the rendered shade

🔑 **The engine CAN render a fixed, long shadow — MEASURED via RimSage.** `SkyManager` sets
the sun-shadow vector every tick from `GenCelestial.GetLightSourceInfo(…Shadow)`, **unless**
`GetOverridenShadowVector()` finds an override — which it takes from any live
`WeatherEvent.OverrideShadowVector` **or any thing carrying a `CompAffectsSky` whose
`OverrideShadowVector` is non-null**. Buildings, rocks and trees already print sun shadows
scaled by `ThingDef.staticSunShadowHeight`. So: one invisible map-anchored thing with a
`CompAffectsSky` subclass pins the shadow vector to a long low-sun angle, permanently — and
`RM_MapComponent_ShadeGrid` casts its mechanical shade **along the same vector**, length =
`staticSunShadowHeight × k` per caster. Rendered shadow and mechanical shade agree by
construction, which is exactly the §10 ⚠️ the sheet said was "cheap to decide now, expensive
to retrofit". (Needs one check: `Graphic_Shadow` skips roofed cells and
`Biome.disableShadows` must stay false.) ~80 lines on the grid + ~40 for the comp.

Consequence for play: patches become **long lee strips on one side of every caster** —
geometry the player can read off the screen and a wall they build throws a shadow they can
predict. That is the biome.

### 1.4 Honest size

| part | size | risk |
|---|---|---|
| `RM_SunLoad` + body-size term | XML + ~20 lines | low |
| directional grid + sky-pinning comp | ~120 lines | medium — must be tested for perf (full-map recompute already every 2000 ticks) |
| patch graph | ~150 lines | medium |
| sun-cost path customizer (Harmony) | ~60 lines | medium — NativeArray lifetime; the one Harmony patch |
| rest/dash job givers + hierarchy | ~120 lines | medium — tuning, not code |
| **total** | **~470 lines C#, one FOUNDRY item, 2–3 build sessions** | Tuning is the real cost: dash budgets per size band need a quicktest with a herd, a predator and a colonist, watched **by the owner** for "does this read as strict". |

Everything reads one grid, so a mod option turning the grid off degrades every animal to
vanilla, as the grid's own contract already promises.

## 2. What's in the shade

pending

## 3. Golden hour

pending

## 4. Wild cards

pending

## 5. Recommended shortlist

pending
