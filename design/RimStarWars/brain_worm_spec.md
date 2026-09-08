# Geonosian brain worms — research + def plan (design spec)

_`GEONOSIAN_BRAINWORM_MORPH_1`. RSW tier. Status: DESIGN — def plan awaits the
owner's review (the item's verify line). Donor never activated; nothing built._

## Research half 1 — the donor (examined 2026-09-08, plan-read only)

**Space Worms (Continued)** (workshop 2105322804, `Mlie` continuation;
subscribed, inactive). Ships: `Scuttlebug` race (+`FaceTeeth`), TWO infection
hediffs (`ScuttlebugInfection` "Parasitic Infection", `ScuttlebugQueenInfection`
"Blistered skin") with a custom C# `Scuttlebugs.ScuttlebugsHediff` class and a
`HediffCompProperties_Discoverable` gate, a `ScuttlebugPodCrash` arrival
incident, worm buildings/items, a tier-4 research line. **What it proves**: the
parasite-as-hediff shape with staged severity and a discoverable latency works
in vanilla mechanics plus one small DLL; the pod-crash vector is a clean
arrival. **What it does NOT have**: host-puppeting — scuttlebugs infect and
damage, they never take control. The puppeting half is ours to build.

## Research half 2 — the canon

Brain worms (Geonosis; *The Clone Wars* S2 "Brain Invaders" arc): parasites
commanded by Queen Karina the Great's hive; eggs enter the host through the
nose/mouth; they puppet LIVING hosts (infected clone troopers) and animate DEAD
Geonosians; and they **react badly to cold** — Ahsoka Tano stopped a shipboard
infestation by rupturing the coolant system and freezing the cargo hold.
Sources: [Wookieepedia — Brain worm](https://starwars.fandom.com/wiki/Brain_worm/Legends),
[Wookieepedia — Brain Invaders](https://starwars.fandom.com/wiki/Brain_Invaders),
[StarWars.com databank](https://www.starwars.com/databank/brain-worm).
🔑 The cold weakness is the gift: **on a tidally-locked world the cure is a
PLACE.** Carrying an infected friend into the night is a journey, not a recipe.

## Our def plan (never the donor's defs)

- **`RSW_BrainWorm`** (ThingDef+PawnKindDef): tiny (bodySize ~0.1), slow, near
  harmless in the open — the worm is only dangerous as a payload. Dies outright
  below ~0 °C ambient (comp check, no C# needed for the death half).
- **`RSW_BrainWormInfection`** (HediffDef, custom class): staged — latent
  (discoverable, days) → influenced (social/work debuffs, whispering) →
  **puppeted**: the host changes to a hostile hive "faction lens" via a forced
  mental state + custom ThinkTree node (our C#; the one genuinely new piece).
  Cure: host's ambient temperature below the threshold for N hours → worm
  ejects and dies (severity collapses). Surgery remains as the risky fast path.
- **Dead-host puppeting** — the arc's signature, and the expensive half.
  Two build options for the owner to pick at review:
  (a) v1: living hosts only (cheap, all mechanics above);
  (b) the Geonosian-corpse shambler, our own C# corpse-walker (NO Anomaly
  dependency unless `ANOMALY_EXCEPTION_ACCESS_1` is ruled open for it — per the
  item, not assumed).
- **Vector**: not weather. Candidates for the owner: Geonosian ruin dungeons
  (eggs in the dark), salvaged cargo, a quest. Placement is his ruling later.
- **Tie-ins honored**: `RSW_RimMandrakeGeonosianVariants` xenotype already
  exists (the hive has a face); the icon carve-out protects brain worms as an
  in-universe reference; the war-legacy split does NOT claim them — Geonosian
  biology, never Assailant arsenal.

## verify state
Donor examined without activation ✅; canon cited ✅; def plan NOT yet reviewed
with the owner — the item stays open on his review.
