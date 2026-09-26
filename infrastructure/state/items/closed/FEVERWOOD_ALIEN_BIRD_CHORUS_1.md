# FEVERWOOD_ALIEN_BIRD_CHORUS_1 — the cacophony, and the one thing that stops it

## spec

Authority: `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md`
§4, §6c.

**Owner's brief:** *"Perhaps dramatic beautiful birds that swoop, shrill, and warble to
create the typical 'swamp cacaphony' that replaces the eerie silence the webwork squares
already specialize in?"*

⇒ **The crown is the LOUDEST place on the planet, deliberately** — because the Webwork next
door owns silence (`the_webwork.md` §9: *"the quietest green place on the planet"*). The two
wetlands are a matched pair of opposite sound registers.

## 🔴 The chorus is an instrument, and it falls for ONE thing

Decision taken by question card: **the crown goes quiet ONLY for the water.** Silence means
the thing below stirred — **not** raids, **not** predators, **not** a pawn in the mud. The
rarest signal is the loudest, and it welds the birds to the biome's one rule.

✅ **This closes a gap already recorded.** `RM_MapComponent_SilenceCue` exists in
`src/RimMandrake/CreatureBehaviors/`, and `FEVER_WOOD_MECHANICS_1`'s F2 pass recorded its
one defect: **no public "hush now" entry point an unrelated event can call** — its only
trigger is a carrying pawn's `PredatorHunt` job near a colonist. This item's chorus is the
consumer that justifies building that entry point.
⚠️ F2 also flagged the **assembly split**: `EnvironmentalHazards` cannot currently reference
`CreatureBehaviors`. Resolve that or give the cue its own entry point.

✅ The frozen sheet wrote the payoff before any of this existed — §9:
*"crown-life constant and easy; ground-level none — then a ripple, and everything above goes
silent to watch."*

## what the birds are to the player — all four

Decisions taken by question card (**tameable**, **plumage**, **nests** — all three), plus
the owner's typed addition.

| role | note |
|---|---|
| **tameable** | a private chorus cultivated near the base |
| **plumage worth money** | 🔑 the temptation sits directly against the alarm — selling feathers means shooting your own early-warning system |
| **nests worth raiding** | eggs / nest material in the crown, guarded by adults — a reason to climb |
| ⭐ **thieves** | *"Some birds here steal items if you have Property mod"* (owner) |

✅ **"Property mod" is OURS — verified on disk 2026-09-23:** packageId
`mandrake.rm.property`, at `src/RimMandrake/RimProperty/` with its own `Assemblies/`. So
the stealing behaviour is a clean `MayRequire="mandrake.rm.property"` on content we
control — **not** a third-party dependency. ⛔ Do not record it as one.

## 🔴 Art brief — a hard requirement, not flavour

**Owner, verbatim:** *"And these should be alien birds, not just parrots. Very strange.
Membranous, hairy, or weirdly shaped feathers."*

⛔ A brightly-coloured Earth-parrot silhouette **fails this brief** even with an exotic
palette.

## injection candidates — check each against the brief

Already built and homeless, all fliers: `RSW_CanCell`, `RSW_Neebray`, `RSW_Porg`,
`RSW_Sacapillar`, `RSW_Mynock`. ⚠️ **`RSW_Porg` is canonically bird-cute and probably fails
the membranous/hairy/strange brief** — check before using. These ride the campaign patch
layer; the `RM_` tier needs its own invented birds so the free mod is rich alone.

## flight is not optional here

🔑 Standing rule (owner, 2026-09-19): *if it flies in the fiction, it flies in the game.*
1.6 flight is **Core**, and the switch is a **stat**, not a bool —
`Pawn_FlightTracker.CanEverFly` returns `GetStatValue(MaxFlightTime) > 0f`. There is no
`canFly` field.
⛔ **Do not build a Spastic wing-layer render tree** — that approach was tried on
`FIREHAWK_FLIGHT_BEHAVIOR_1` and the owner's own live test found it broken. The correct
mechanism is the whole-body directional flip-book
(`flyingAnimationFramePathPrefix` + frame count, north/east/south, west mirrors east).
✅ Never block flight waiting on frames — with none, the creature simply flies without a
wing-beat.

## open

How the call registers divide (swoop / shrill / warble) and how many birds there are. §6c
settles what they are *to the player*, not how the chorus is voiced.
