# Gizka — the ship-pest event (design spec)

_`GIZKA_TRIBBLE_ADAPTATION_1`. RSW tier — any Star Wars scenario, nothing
campaign-specific. Status: DESIGN, awaiting the owner's review (the item's own
verify line). Nothing here is built._

## What the Tribble module taught (examined 2026-09-08, never activated)

`zylle.TribbleTrouble` (workshop 2400590961, subscribed/inactive): one
ThingDef+PawnKindDef pair, breeding via a custom `CompProperties_TribbleSpawner`
(C#, `ZTribble.dll`), ONE arrival incident (`IncidentWorker_Tribbles`), sounds,
tales, a think tree. **The shape to borrow**: pest-as-comp on an ordinary animal
plus a themed arrival — small, self-contained, no Harmony surgery.
**The shape to reject**: arrival as a random weather-tier incident. Ours is an
EVENT WITH A STORY — it rides things the player did.

## Donor state — MEASURED 2026-09-08

- Creature def: **none** anywhere in stack or src (dump + live Mods + workshop
  swept). Only four SoundDefs exist — `RSW_Pawn_Gizka_{Angry,Call,Death,Wounded}`
  in SWBestiary: the audio was prepped, the animal never landed.
- Art: **absent** — no gizka texture in `src/`, the deployed Mods folder, or any
  workshop folder. Art must be generated (sprite pipeline, later; the local
  imagegen track is parked — this spec does not commission art).

## The design

### 1. Arrival — always a consequence, never weather

One gizka, found where the player was just acting: a purchased cargo lot
("something moved in crate three"), wreck salvage, a docked/landed gravship hold,
a trade caravan's "free gift". One animal. Small (bodySize ~0.2), bright,
bouncy, hungry. Colonists can name it; it follows people; **+3 cuteness mood**
to anyone who interacts. The letter is warm, not warning.

### 2. The turn — fed and warm, it breeds

`RSW_CompGizkaBreeder` (our generalized spawner): breeding rate scales with
ambient temperature and food access — a colony that stores food behind doors at
16 °C is EXACTLY a gizka incubator. Curve (fair, visible, slow to start):
1 → 2 in ~6 days of comfort, then each adult doubles on the same clock while
comfort holds. Cold, hunger, or population pressure stall it (see §5).

### 3. Escalation stages — each with a warning the player can read

| stage | pop | what happens | the warning sign |
|---|---|---|---|
| Cute | 1–3 | mood bonus, tales, nothing else | colonists visit it |
| Underfoot | 4–8 | minor filth, food nibbling begins | "gizka got into the rice" letter |
| Infestation | 9–20 | raids food stores in earnest; **chews wiring**: powered buildings gain breakdown MTB penalty while gizka share the room | sparking-conduit motes, a named breakdown cause ("gizka-chewed") |
| Plague | 21+ | rooms crowd, beauty/space debuffs, breeding accelerates no further (cap §5) | the colony can hear them (ambient soundscape swells) |

### 4. The exits — each priced, all real

- **Cull** — fast, certain; −mood per kill scaled by cuteness interactions
  banked (the pet you named costs more than the swarm you didn't).
- **Sell them onward** — the KotOR scam, the Jawa answer: traders BUY gizka
  (small silver each, never scaling — see §5); a caravan can haul a crate off.
- **Poison bait** — kibble + go-juice mash: quiet, no mood hit for the crafter,
  small hit for animal-lovers; leaves corpses to haul.
- **Vent the cold** — open the hold/room to the night: comfort collapses,
  breeding stops, population halves over days; free but slow, and the survivors
  remember the warm kitchen.
- **Lean in** — gizka ranching: meat and sale stock. Deliberately mediocre
  (§5) — a funny bad idea that WORKS, just never better than muffalo.

### 5. The anti-exponential law (hard)

The exponential belongs to the PEST, never the player: sale price is flat and
low, never demand-scaled; meat yield is small; the breeder comp hard-caps map
population (~24) and slows near the cap, so neither the infestation nor the
ranch ever compounds. A gizka economy stays a joke that pays pocket change.

### 6. Build shape (later item, not this one)

`RimStarWars.Gizka` namespace (nested grammar), mod folder candidate
`src/RimStarWars/Livestock` (join the existing animal mod, not a new folder —
one comp, one incident, one pawnkind + the four existing SoundDefs wired in).
DefNames: `RSW_Gizka` (ThingDef/PawnKindDef), `RSW_GizkaArrival`
(IncidentDef), `RSW_CompGizkaBreeder`. Art: 3-facing sprite set via the
sprite pipeline once unparked, validated against SWBestiary's canvas/scale.
