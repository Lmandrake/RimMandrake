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

The sheet already says what a shadow here *is*: a staging post, a commons stratified
centre-to-rim, a trap, a midden, a dew ring. "All the animals" is the commons half. The other
half, which the sheet names and nobody built, is that **a shadow is the only place anything
on this ground can be kept** — so it is where everything that was ever lost, hidden, planted
or abandoned has ended up, and where anything that wants to be *found* waits. Every idea
below comes from that.

Format per idea: **pitch** · *what the player sees* · why only here · size · reuses · tier.
Sizes: XML · small C# (<150 lines) · big C#. Echo checks against the other ten bedazzle docs
are called out where they bite.

### 2A. Things to DISCOVER

**D1. The gap graves — salvage that lies in the sun.** *"Dying in the open is the only
privacy on this planet"* (§4) means nobody ever retrieves anything from a gap. So the open
between patches is strewn with the mummified, unlooted dead — pack animals still loaded,
travellers with their kit. *Seen:* a glint on the pavement 30 cells out, between two patches.
Getting it is a **colonist dash**: out, grab, back, before `RM_SunLoad` downs them — and the
farther graves are only reachable in a smoke-haze window or in the gloomcast's shadow.
*Only here:* the loot is guarded by geometry, not by a monster; the same strict-dash law that
governs the animals governs your salvager. **The player learns the sprint economy with their
own pawns' bodies.** Size: small (a GenStep scattering `Corpse`+gear on low-shade cells;
the rest is §1). Reuses: §1 sun-load, vanilla corpse/gear gen. Tier: RM (label "sun-dried
remains"). Distinct from the Stillsand's *buried* record — these lie on top, in the light.

**D2. The still gnomons — treasure at the tip of a shadow that never moves.** Somebody, long
ago, understood that the sun here never moves. They raised single standing stones where
nothing else stood, and buried something **exactly where the shadow ends** — because that
spot will be the same in a thousand years. *Seen:* a lone dressed monolith with a carved
line on the ground-face, and a long rendered shadow (§1.3) whose tip lands on a patch of
subtly wrong sand. Dig the tip: a cache. *Only here:* **the only biome on the planet where a
shadow is a coordinate.** The directional grid (§1.3) makes this readable on screen, and the
same fact explains why the builders came here. Some gnomons point at nothing any more —
someone got there first — and one chain points *to the next gnomon*. Size: small (a
`Building` monolith with `staticSunShadowHeight`, a GenStep burying a cache at
`pos + shadowVector × height`). Reuses: §1.3's pinned vector, vanilla `Mineable`/stash
content. Tier: RM (anonymous builders); Utinni can name them later.

**D3. Route cairns — the herders' patch-chain maps.** §7 "known viable routes… worth
mapping". Herder camps leave cairns in patches whose stones are stacked to point along a
viable chain. *Seen:* a small cairn at a patch rim. Study it (one colonist, an hour) and the
map overlays **the chain it marks, with the dash distance of each gap for a human** — which
patches your colonists can actually cross between. *Only here:* the discovery is a route
through light, not a place. Size: small C# (an overlay drawn from §1.2's patch graph, a
`CompUsable` to reveal it). Reuses: patch graph. Tier: RM.

**D4. The shade-cool cellars — someone dug down under a patch.** The coolest ground in the
biome is *under* the deep centre of an old patch. Abandoned root cellars and cisterns open
off the lee of big rocks: hatch → a pocket map one room deep holding stores that kept
(nothing rots in this heat either). *Only here:* the reason to dig is the shade above.
Size: medium (Odyssey pocket-map portal; the Twilight's skylight and the sarlacc throat use
portals too — this is a *cellar*, human-made and small, not a dungeon). Reuses:
`MapPortal` pattern already used by `RM_SeaDiveHatch`. Tier: RM. ⚠️ Echo risk with Stillsand
buried record — kept apart by being **built** rooms under shade, never sand-buried loot.

**D5. The dew wells that remember — dew-line condensers left running.** Ancient condenser
fins set along a patch's dew line, still beading water into stone basins. Drink here and the
basin is a real, small, renewable water source in a rainless biome. *Only here:* water that
exists only because the shadow's edge is cold. Size: XML + small (a building that yields
water only if its cells are rim cells — the dewfringe gate's boundary test). Reuses:
`RM_Patch_DewfringeWildSpawnGate` boundary test, FlowWorks. Tier: RM. Distinct from the
Leaning Scrub's buildable vaporator economy (slate #4 there): these are **relics on the
rim**, not an industry.

### 2B. Things to FEAR

**F1. The mirrak — the shadow that is an animal.** *(new, RM, mirrak)* A flat, broad,
dark-backed ambusher that lies on open pavement and **presents as a shade patch**. An
overheated animal (or colonist) dashing for the nearest shadow reaches it — and it closes.
*Seen:* a dark oblong on the pavement that the grid does not score as shade (and the route
cairns never mark). Tell: no dew halo, no tenants, and the shadow points the *wrong way* —
once §1.3 pins the sun, every real shadow is parallel, and a mirrak's is not. *Only here:*
it preys on the dash itself; it is only possible where every creature's life depends on
reaching shade fast. Ban 3 safe — it never moves to hunt. Size: small C# (an ambush comp —
`RM_CompAquaticAmbusher` is the shipped shape — plus a "counts as shade to the dash job
giver, not to the grid" flag). Reuses: ambusher comp, §1 dash job. **The strongest single
creature idea in this doc**, because it only works if the dash is strict.

**F2. The tollok — the rent of resting.** *(new, RM, tollok)* Tick-like shade-dwellers
clustered in the deep centres of old wild patches; anything that rests there long picks up a
bleeding, itching infestation. *Seen:* animals leaving the best centre early, shaking.
*Only here:* rest is mandatory (§1) so rest has a price; and it is the reason the player's
**own, built** shade is worth more than a natural patch — yours is clean. Size: XML
(hediff + a HediffGiver keyed to resting in wild shade ≥ N hours; small C# for the "wild vs
built" test — roofed cells are built). Reuses: shade grid, vanilla hediff machinery. Tier: RM.

**F3. The overfull patch — the stampede for your roof.** §4's "worst moment available":
a herd arrives overheated at a patch already full, can't wait, and **bolts for the nearest
bigger shade — your base.** Not manhunter: panicked and sun-loaded, they go through
fences and into barns and they will not leave until they have cooled. *Only here:* an
incident whose cause is geometry and heat; it lands **on your doorstep because your roof is
the biggest patch**. Size: small (incident worker; the herd simply runs §1's "exposed, no
reachable patch" branch toward the player's roofed area). Reuses: §1 dash branch, the ruled
harbour ladder (marquee #1) — this is its violent rung. Tier: RM.

**F4. Sunstruck bodies in the rim.** Animals that arrive too late lie downed at the rims,
still alive, still dangerous if you approach (a downed predator bites). Scavengers work only
the patch edge (§4 "Scavengers here specialise exclusively in kills at a patch edge").
*Seen:* a rim littered with the half-dead — free meat, if you go get it past what is eating
it. Size: XML (falls out of §1's sunstruck stage). Reuses: §1. Tier: RM. Enrichment, not a
standalone.

**F5. The heat-shimmer false horizon.** In the open, a colonist with high `RM_SunLoad`
misreads distance: their destination drifts, their dash overshoots the patch. A mental
state, not a map effect. Size: small (a stage on the sun-load hediff that forces a random
offset on the next Goto). Tier: RM. Low priority.

### 2C. Shade that ISN'T natural — hidden, lying, planted

**N1. The empty patch.** 🔑 *(the owner's "maybe some of those shady spots aren't so natural
after all")* Every patch here is crowded — the commons law. So **a perfect, deep, dew-ringed
shadow with nothing in it** is the loudest warning on the map. What is under it is the
sarlacc (§2D S2), the mirrak (F1), a tollok nest, a minefield, or a buried vehicle. The
animals know; the player learns to watch the animals. Size: zero on its own — it is an
emergent read once §1 makes patches reliably full. Stated here because it should be
**designed for**: every "unnatural shade" idea below must empty its patch of wildlife
(`RM_JobGiver_Dash` treats a flagged patch as occupied-by-predator).

**N2. The wreck road — a patch-chain someone built out of dead vehicles.** A clan, long ago,
stripped and dragged wrecked landspeeders, skiffs, cart chassis and a crawler tread section
into a line across a wide gap, each one a shade-caster exactly one human dash from the next.
*Seen:* a dotted line of rusting hulks across the open, every one with animals in its lee.
*The choice:* it is **the richest salvage on the map and it is the only road across the
gap.** Every wreck you strip breaks a link — for the caravans, the herds, and your own
colonists. The Jawa instinct versus the route. *Only here:* salvage whose value is its
shadow. Size: small (GenStep placing wreck buildings with `staticSunShadowHeight` along a
line, chained by patch-graph distance; deconstruct yields). Reuses: `RSW_DeadCaravan` /
`RSW_PodracerWreck` wreck art, Alpha Vehicles-Neolithic carts (`DesertVehicleReskin`),
§1.2 patch graph. Tier: RM for the mechanic (generic "wreck"), RSW for canon hulls.

**N3. The crawler shade — a dead sandcrawler is the biggest harbour for miles.** The
`RSW_DeadCrawler` mutator (shipped, already whitelisted to `Desert`) drops a half-buried
three-deck hull with "sleeping hands" inside. In the Long Shade it is read differently: the
hull throws the **largest shadow on the map** — so its lee is a full stratified commons
(gloomcast in the centre, herds, a dakkra at the rim), and to reach the hatch you walk
through the whole hierarchy. *Only here:* the dungeon's outer defence is an ecosystem using
it as shade. Size: XML (give the hull a big `staticSunShadowHeight`; let §1 do the rest).
Reuses: `RSW_DeadCrawler`, `RSW_GenStep_DeadCrawler`. Tier: RSW (canon sandcrawler).

**N4. The lure awning — shade as bait.** Hunters' craft: a cheap stretched-hide awning on
poles that casts a patch where there was none, placed one dash from a herd's route. Game
comes to it. *Player-buildable* (after studying a herder's blind, D3-style): place it, and
the next dashing herd stages under your hunters' guns. *Only here:* the one biome where
**you can bait with geometry.** Cost: a dakkra may take tenancy first. Size: XML (a
building that casts shade and is not roofed — or is roofed; the grid counts either).
Reuses: shade grid. Tier: RM.

**N5. The dry vaporator stands — shade the farmers left behind.** The moisture farmers'
tall vaporators are the only man-made verticals out here, and each throws a long thin
shadow with its own dew line. Abandoned ones stand in lines across old fields — **a manmade
patch-chain nobody meant to build**, now colonised. Repair one and it works again (and the
wildlife in its lee is now your problem). Size: XML (reuse the KotOR vaporator art —
`Absorbed_KotorCore_Building_MoistureVaporators.xml`, ⚠️ that file is flagged
"do not deploy until it retires" — confirm the absorption state first). Tier: RSW (canon
vaporator). ⚠️ Echo: Leaning Scrub slate #4 owns *buildable moisture farming*; this is kept
distinct as **ruins that happen to be shade**, and its gameplay is the patch, not the water.

**N6. The mirror field.** *(bold)* An old array of sun-tracking mirrors that no longer
track — frozen, like the sun, at the angle they last held. They **throw light into shadows**:
certain patches are *unshaded* by a beam from half a map away. Turn a mirror (a repair job)
and a patch opens up, or another one dies. The only object on the planet that **edits the
shade map**. Size: big-ish (grid needs a "lit by mirror" subtraction; the mirror is a
rotatable building; ~150 lines). Tier: RM. See §4 W3.

### 2D. The SARLACC young — one at a time

What exists (MEASURED, `src/RimStarWars/Sarlacc/`): `RSW_SarlaccSwimmer` — Stage I, a mobile
sub-sand predator with a **fixed water reserve spent on every strike and metre**, that
"does not chase" and "does not strike anything that carries no water — droids pass over it
unnoticed"; `CompSarlaccSwimmer` roots it into `RSW_SarlaccAnchored` (Stage II, a pit that
strikes only at what stands beside its mouth) on a `RSW_DeepDesertSeep` or when it runs dry;
Stage III the cistern; the "changed return" hediffs for the swallowed. Home: the **deep
desert** (`sarlacc_native_habitat_draft.md`, ACCEPTED 2026-09-12). Owner, 2026-09-02:
*"there are smaller, more mobile ones."*

🔑 **Why a swimmer belongs here without breaking one-home:** the owner's own carve-out is
*"young versions that grow in [one place] then migrate"*. A swimmer is exactly a life stage
that moves — born at a deep-desert cistern, it swims **outward, toward water**, and the
nearest water in its world is the Long Shade's dew lines. So the Long Shade is where the
sarlacc's young **go to root**. That is one creature, one home, one migration.

**S1. The swimmer's crossing — one juvenile at a time.** *(the owner's "young sarlacc raids,
one at a time")* A single swimmer arrives at the soft-sand edge of the map, low on water. It
does not hunt the colony; it goes for **water** — anything wet that stands on soft sand near
a dew line. *Seen:* a sand-wake that moves patch to patch like everything else here (it
dashes too — it spends water per metre), a pause at each rim, then a strike at whatever is
standing on the rim. *The choice:* hunt it (hard — it is under sand, and only on
**hardpan** can it never reach you; ban 6's bargain gets its apex — ⚠️ no owned hardpan
terrain exists yet, review slate #6 `RM_Hardpan`), or **let it root.**
*Only here:* one monster, trackable, whose goal is not you but a place — and the player can
see where it is going. Size: small (IncidentDef + worker that spawns one swimmer at the map
edge; the swimmer's own comp does the rest). Reuses: `RSW_SarlaccSwimmer`,
`CompSarlaccSwimmer` in full. Tier: RSW (canon).
⚠️ Echo check vs the Stillsand's sand busters: the busters are an **infestation you
trigger**, many, erupting. S1 is **one named individual on a journey** — kept apart, and
must stay that way (never a swarm, never erupting from under your base).

**S2. The rooting — a juvenile emergence into a permanent mouth.** *(the owner's "juvenile
sarlacc emergences")* If S1's swimmer reaches a dew ring with enough water it roots: the
patch's tenants flee all at once, the dew line darkens wet, and the mouth opens in the
centre of the shade. **Your map now has an anchored sarlacc — forever**, a well with a
mouth, the deep centre of the best patch on the map owned by something that takes a tithe.
That is N1's empty patch, explained. *Keep or kill:* a rooted sarlacc is water (the anchored
stage "is filling"), pearls (ruled, "sarlacc pearls"), a disposal pit for the Rite of
Offering (ruled v1, *"a rite of offering and forgetting"*) — and a death at the rim now and
then. Size: small (one hook: dew-ring rim cells count as a seep for `CompSarlaccSwimmer`'s
root test). Reuses: `RSW_SarlaccAnchored`, `CompSarlaccAnchoredMouth`. Tier: RSW.

**S3. The droid runner.** The swimmer ignores droids. So in sarlacc country a clan's
droids are the only safe salvagers of a sarlacc-held patch — send a droid to strip the wreck
in the lee of the mouth. The Jawa fantasy, with the sarlacc's own shipped rule doing the
work. Size: zero (already true of the shipped comp). Tier: RSW. Worth stating to the player
in the swimmer's description — it already is.

**S4. The old rooting.** Map-gen variant: some Long Shade maps start with an anchored
sarlacc that rooted decades ago under the deepest patch — its apron of pressed residue ringing
the shade. Size: XML (GenStep placing `RSW_SarlaccAnchored` under the largest patch). Tier:
RSW. ⚠️ Keep rare; the cisterns are the deep desert's.

⛔ **Cut:** a sarlacc *egg clutch* in the middens — it echoes the Stillsand's eggs-as-water
and the deep desert's birth-trap eggs, and the swimmer's birth belongs to the cistern.

### 2E. INHABITED — broken crawlers, stranded people, desperate farmers

**I1. The desperate moisture farm — a homestead the ecosystem is besieging.** The ruled
harbour ladder (marquee #1) happening to **somebody else**. A moisture-farmer family's
roofed homestead is the biggest shade for a day's walk, so everything alive has moved into
their yard: a dakkra holds the barn shadow, a herd is packed against the south wall, the
vaporators are down because nobody can reach them alive. *Seen:* an Inhabited place with
the family indoors, rationing, and the whole biome's hierarchy standing outside. *Player:*
clear the yard (and get paid in water and a vaporator), trade them passage, or wait for them
to give up and inherit the stand. Size: small–medium (an `RM_InhabitedPlace` variant +
seeding the yard with §1 residents). Reuses: `Inhabited` (HOMESTEAD cast roster, 10 named
characters), `RSW_GenStep_MoistureFarm` template, the harbour ladder's incident rungs.
Tier: RM mechanic, RSW dressing (moisture farm is canon). **Distinct from Leaning Scrub**:
no farming economy — the farm is a siege.

**I2. The waiting camp — stranded at the last patch before the gap.** §8: "the last patch
before a wide gap is the most contested real estate in the biome". Travellers whose beast
died, who cannot cross: a camp of a dozen people sharing one shadow with the wildlife,
rationing. They pay for **shade on the move** — escort them across (your colonists carrying
a portable awning, W1, or walking in the gloomcast's shadow). *Only here:* a rescue whose
obstacle is 40 cells of sunlight. Size: small–medium (quest; `RM_Stranded` in
`StrandedQuest` is the in-house quest shape — a survivor who must be sheltered until
collected). Tier: RM.

**I3. The shade-rent men.** A Junkers-style crew has claimed a dead crawler's (N3) lee and
charges rent for shade — caravans pay in water to rest. Deal with them, displace them, or
become them. Size: XML-first (an Inhabited place on `RSW_DeadCrawler` with JUNKERS cast;
`CastRoster_JUNKERS.xml` exists). Tier: RSW/Utinni.

**I4. The broken caravan in the gap.** A caravan whose draught animals collapsed
mid-crossing (`DesertVehicleReskin`'s carts, `RM_DraughtFuelExtension` — carts that run on
animals): the carts are shade now, the crew is sheltering under them, and they have one
day's water. Rescue in the sun (D1's dash, with lives), or salvage later. Size: small (event
spawning the shipped `RSW_DeadCaravan` layout live, with living crew). Reuses:
`RSW_DeadCaravan`, `DesertVehicleReskin`. Tier: RSW.

**I5. The Jawa crawler that comes back.** The crawler in N3 was somebody's. Once a map's
dead crawler has been looted, a Jawa clan may arrive to reclaim it — trade, dispute, or a
salvage-rights fight, and on good terms they will **tow it**, and the map's biggest shadow
leaves with them (every tenant of the lee stampedes for the next — F3). Size: medium
(incident + a tow visual that despawns the hull). Tier: Utinni (Jawa clans). The most
Jawa idea here.

## 3. Golden hour

pending

## 4. Wild cards

pending

## 5. Recommended shortlist

pending
