<!-- status: spec — SARLACC_SPEC_SESSION_1, BENCH 2026-08-31, green-lit by the owner with scope
     widened verbatim: "Also include deep sarlacc dungeon experience with wildly animated sarlacc
     emergence and attack tentacles." Supersedes nothing: V2_DREAMS' sarlacc entry stays as register
     history; research/Jawa/rimworld_sarlacc_encounter_current_design.md is this spec's surface-
     encounter foundation and remains its vision doc. All engine claims below are MEASURED
     (rimsage source reads 2026-08-31, recorded here and in the V2_DREAMS entry). -->
# The Sarlacc — unified spec: the event above, the dungeon below

**The defining realization stands (vision doc): the sarlacc did not arrive on
the map — the colony was built over it.** This spec joins that surface
encounter with the owner's deep-dungeon ask into one build, on geography that
already exists.

## 1. The geography is already authored — five sites on Ash'karr

| landmark | tiles | role in this spec |
|---|---|---|
| `sw_DeadSarlacc` ×4 | Glare · Dry Marches · Kiln · Pale Flats | **husk delves** — the dungeon without the monster: dried gullet levels, salvage, bones of the digested, no surface event |
| `sw_Sarlacc` ×1 | Dew Belt (tile 2920) | **THE sarlacc** — ancient tier, the full surface event and the living dungeon |

The dead-vs-live split gives the campaign a difficulty ladder for free and
makes the live one legendary by contrast. ⚠️ All five landmarks currently
render magenta — the donor mod declares the LandmarkDefs and ships no world
art (`ASHKARR_WORLD_DEFINITION.md`, magenta-tiles finding). World-art for both
landmark defs rides this build's art pass regardless of everything else.

**v1 is unchanged:** the standing §13 ruling ("v1 takes the mod's landmark")
holds — v1 ships the geography and the reputation. Everything below is the v2
build this spec makes executable.

## 2. Layer 1 — the surface event ("wildly animated emergence and attack tentacles")

Staged escalation per the vision doc (agitated animals → tremors → subsidence
→ pit opens → tentacles → structural feeding). Engine mapping, measured:

- **Emergence is nearly free.** The `GroundSpawner`/`BuildingGroundSpawner`
  family (PitBurrow and FleshmassHeart both use it) carries delay, dust,
  sustainer sound and completion effecter ALL IN XML; only the `Spawn()`
  override is a thin C# subclass. The pit-opening spectacle — sand collapse,
  debris, the maw revealed — is this family plus our effecters/motes.
- **There is NO non-pawn animator in the engine.** `AnimationDef` is
  hard-wired to `PawnRenderTree`; buildings cannot play one. Therefore:
  **tentacles are PAWNS** — a `RSW_SarlaccTentacle` creature, spawned by the
  maw, anchored by a lord duty (the `DefendFleshmassHeart` shape), rendered
  through PawnRenderTree so keyframe `AnimationDef`s (strike, coil, slam,
  submerge) work in XML. This satisfies "wildly animated" with shipped
  machinery; the vision doc's spline renderer stays a stretch goal, not the
  base plan.
- **The strike loop** for the maw itself: the `CompFleshmassSpitter` pattern
  (IAttackTargetSearcher + native verb, periodic search-and-cast from a fixed
  point) with the ranged verb swapped for short-range tentacle verbs. The swap
  is unprecedented in vanilla but small; the search-and-cast loop is proven.
- **Grab-and-drag**: `CompDevourer`'s despawn + `IThingHolder` container is
  the shipped hold pattern — a grabbed pawn lives inside the tentacle/maw,
  struggles (job-driven timer), and is rescued by killing the holder. Same-map
  only in vanilla; the swallow-transition is §3.
- **Subterranean tendrils** (ancient tier): a racing ground-disturbance
  effecter chain ending in a `GroundSpawner` tentacle eruption at the target —
  all three pieces exist; the chain is ours.

## 3. Layer 2 — the dungeon below ("deep sarlacc dungeon experience")

- **The portal:** `PitGate : MapPortal` is fully self-contained (own lifecycle,
  no GameComponent) and siteable with one `GenSpawn.Spawn` call; its def
  already wires `pocketMapGenerator`/`exitDef`. We author `RSW_SarlaccMaw`
  (PitGate-derived def) at the landmark site — a *place*, never a random
  event.
- **The gullet maps:** an Undercave-derived `MapGeneratorDef` family (100×100
  default pocket size), our gensteps swapping cave dressing for digestive
  theming. The Anomaly fleshmass genstep toolbox is PERMITTED here by canon
  (`anomaly_content`: "the sarlacc's design may draw on it too").
- **DEPTH IS LEGAL:** pocket-map nesting is UNENFORCED by the engine —
  `MapPortal.GeneratePocketMapInt` never checks `base.Map.IsPocketMap`. The
  "deep" experience is literal: **stacked gullet levels** (throat → crop →
  the pearl chamber), each a portal down inside the previous. ⚠️ Known soft
  risk, carried: transport/quest helpers resolve "the real map" only one
  level up (`ShipJob_Arrive`, `QuestGen_TransportShip`) — no shuttle/quest
  logic may target a nested level, and the build tests save/load across two
  levels before committing to three.
- **Being swallowed is a route in:** Devourer hold + portal spawn composed —
  a surface grab can end with the pawn deposited on level 1 instead of
  dropped. No shipped code merges the two systems; the merge is ~20 lines and
  it is the single best moment the design owns.
- **The bottom:** vanilla never puts `FleshmassHeart` in the Undercave
  (measured: surface-only incident) — so the thing at the bottom is OURS:
  `RSW_SarlaccHeart`, the digestive core, guarded by tentacle pawns. Killing
  it (or stealing the pearl) triggers the collapse escape.
- **The collapse is the exit bell:** vanilla's shape is exactly right —
  `BeginCollapsing()` arms a ~25000-tick timer, staged rumble/roof-drops, then
  the map dies killing everyone left. Repointed: our trigger is the heart's
  death/the pearl's theft, and every level collapses upward in sequence. The
  escape climb IS the third act.

## 4. The pearls — ruled register made mechanical

Register canon: sited, earned by risk, top of the reward table, **never
farmable**. Mechanically: `RUT_SarlaccPearl` — a unique item in the live
sarlacc's deepest chamber, ONE ever (the world holds one live sarlacc); husk
delves hold lesser "dead pearls" (high-value trade goods, finite, placed at
authoring time, never regenerated). The pearl is the campaign's proof-of-deed
object; what it unlocks (quest chain, relic status, Mob'Unloo's price) is an
owner ruling at the art/lore sitting, not this spec's call.

## 5. Layer 3 — the ancient intelligence (couples to LLM_INGAME_WIRING_1)

The vision doc's digested-memories personality is an encounter-personality
layer: fragmentary voices, recognition, adaptive targeting. This is the
natural first consumer of `LLM_INGAME_WIRING_1`'s event-triggered small calls
— a voice assembled from what the sarlacc has eaten is exactly "more than
prescribed dialog" on an infrequent cadence. Base build ships prescribed
fragments; the LLM hook upgrades them when that item lands. No dependency
either way.

## 6. Prerequisites and deadlines

1. 🔴 **World-creation deadline:** the frozen save must be created with
   playstyle **`AmbientHorror` + Custom difficulty** (V2_DREAMS measurement:
   keeps Anomaly content alive, skips the monolith gate, keeps the threat dial
   at 0 and adjustable; locked at creation, unpatchable after). This line goes
   to `SCENARIO_SETTINGS_SPEC` / the scenario item before ANY frozen save is
   authored. Our scenario must not set `standardAnomalyPlaystyleOnly`.
2. Landmark world art for `sw_Sarlacc`/`sw_DeadSarlacc` (the magenta fix) —
   art pass, independent, can ship in v1.
3. Naming: `mandrake.rsw.sarlacc` (SW legendary megafauna tier), `RSW_`
   prefixes; the pearl and Ash'karr site identities `RUT_`.

## 7. Build phases, each with its own gate

1. **Husk delve** (no monster): maw def + one gullet generator + loot pass —
   proves portal, generator, collapse, save/load at depth 1. Quicktestable.
2. **Depth** — level 2 + nesting save/load proof. Gate: a two-level descent
   survives save/reload with pawns on both levels.
3. **Tentacle pawn** — render tree, AnimationDefs, lord anchor, strike verbs.
   Gate: a tentacle strikes, coils and submerges on a quicktest map, judged at
   display size.
4. **The surface event** — GroundSpawner emergence chain + escalation stages +
   grab. Gate: the staged awakening reads as the vision doc's sequence.
5. **The swallow route + the heart + the pearl + collapse escape** — the full
   live-sarlacc loop.
6. **Personality fragments** (+ LLM hook when available).

Each phase lands with a PROVE/EXPECT/LIES plan per the sprite/build doctrine;
nothing rides a cold load that a quicktest can prove.

## 8. Open for the owner (not blocking phases 1–2)

- Pearl consequence: quest chain vs relic vs trade apex.
- Tentacle art direction: how far past "RimWorld creature" toward horror.
- Whether husk delves ship in v1.5 (they need no Anomaly playstyle if built
  on our own portal def — worth checking; if true, only the LIVE sarlacc
  waits on the AmbientHorror save).
