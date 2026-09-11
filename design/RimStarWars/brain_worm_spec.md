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
- **Dead-host puppeting — 🔴 RULED OUT PERMANENTLY** (owner, 2026-09-11,
  verbatim: *"Never corpse-walker. Too gross."*). Living hosts only, forever —
  not deferred to v2, dead. No Anomaly-exception question exists for this mod.
- **Vector — RULED** (owner, 2026-09-11), three build:
  1. **Geonosian ruin dungeons** — eggs in the dark, exploration hazard.
  2. **Salvaged cargo** — the Ahsoka route; the scavenger fantasy of dragging
     home something that hatches.
  3. **Weaponized eggs as war retribution** (owner, verbatim: *"As punishment
     if they go to war against the Jawa: bring a catapult and hurl eggs at
     their ship, then leave."*) — a player-side delivery of eggs against
     factions that war on the colony; delivery mechanism (catapult/launcher
     item vs caravan action) is the build's design question, the fantasy is
     fixed.
  A scripted quest vector was offered and NOT picked — build none.
- **Tie-ins honored**: `RSW_RimMandrakeGeonosianVariants` xenotype already
  exists (the hive has a face); the icon carve-out protects brain worms as an
  in-universe reference; the war-legacy split does NOT claim them — Geonosian
  biology, never Assailant arsenal.

## verify state
Donor examined without activation ✅; canon cited ✅; def plan REVIEWED with the
owner 2026-09-11 ✅ (puppeting scope + vectors ruled above). Build:
`BRAINWORM_MOD_BUILD_1` (FOUNDRY).
