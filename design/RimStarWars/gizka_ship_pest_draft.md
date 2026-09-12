# Gizka ship-pest — design draft (parts 3–6)

_`GIZKA_TRIBBLE_ADAPTATION_1`, parts 3–6. Status: DRAFT for the owner's review —
nothing here is built, no name is coined (every new identifier is a
`<RSW_...>` placeholder). Ground truth from the 2026-09-12 recon
(`Transient/GIZKA_TRIBBLE_RECON_2026-09-12.md`): the Tribble module's arrival
shape (random ThreatBig incident roll) is REJECTED; the gizka creature is
REUSED from the active Star Wars Animal Collection, not commissioned._

_The 2026-09-08 spec this replaces was deleted in this change (its "creature
and art absent" base was wrong — the creature ships in the active donor; git
holds the old text). Its arrival/exit/anti-exponential intent is carried
forward here._

## 0. The creature we reuse (all values MEASURED from the live donor def)

`Gizka` ThingDef/PawnKindDef/BodyDef in **Star Wars Animal Collection
(Continued)** (`Mlie.StarWarsAnimalCollection`, WS 3497316713, ACTIVE),
`1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`:

- bodySize 0.18, healthScale 0.4, hungerRate 0.35, MoveSpeed 3.0,
  Wildness 0.5, petness 0.15, nuzzleMtbHours 12, ComfyTemp 0–60 °C,
  lifeExpectancy 12, adult at 0.09 yr (~5.5 days), herdAnimal.
- **MarketValue 100**, tradeTags `StandardAnimal/AnimalCommon/AnimalFarm` —
  traders already buy and sell it. (This value is an anti-exponential
  problem — see §4 and the owner cards.)
- **`CompProperties_EggLayer` already on the def**: 1–2 eggs per lay,
  `eggLayIntervalDays 1`, fertilized + unfertilized egg defs shipped by the
  same mod. Vanilla fast breeding EXISTS on this creature out of the box —
  a hen-tier reproductive engine, needing only a mated pair.
- `foodType OmnivoreRoughAnimal, OvivoreAnimal, AnimalProduct` — it eats
  stored meals, eggs, milk: the "raids food stores" beat is already real
  vanilla behavior for a hungry roaming animal with this diet.
- Own name generators (colonists' named gizka read as Star Wars names),
  own `Pawn_Gizka_*` SoundDefs, art in the mod's AssetBundle
  (`swanimals/Gizka/Gizka`, `GizkaW` white-mask variant in 6 tint colors,
  `Gizka_Dessicated`).
- Already in our biome rosters (`RUT_AridShrubland.xml` patch, 0.4 weight;
  round2 fauna decisions all "keep").

**No new creature def is needed.** Places a new def IS genuinely needed are
flagged inline with ⚑ and collected in §7.

Parallel-content flag (not this item's fix): SWBestiary carries duplicate
`RSW_Pawn_Gizka_{Angry,Call,Death,Wounded}` SoundDefs
(`SoundDefs_SWBestiary.xml:2536-2626`) that predate the donor's activation;
the donor now ships its own `Pawn_Gizka_*` set and the ThingDef references
the donor's. The RSW_ set is currently unreferenced by any creature —
reconcile under this item's build or NAMING_SCHEME_EXECUTION_1, whichever
lands first.

UNKNOWN (owed before build, from the recon): whether the AssetBundle gizka
sprite renders live (quicktest). If it does not, that becomes an art task —
loose-PNG override per the loose-PNG-beats-bundle finding — not a new def.

## 1. Discovery — a found-aboard EVENT, never a raid roll

Owner's sentence, the design's spine: *"finding one of these in the ships
should be an event... cute at first but then becomes a real problem."*

**Rejected shape** (the Tribble module's): `IncidentCategoryDef ThreatBig`,
random storyteller roll, refire timer. Arrival with no story, indistinguishable
from weather. None of that is used — no IncidentDef in the threat categories
at all.

**Adopted shape: the gizka rides something the PLAYER did.** A single
`<RSW_GizkaStowawayManager>` (GameComponent or MapComponent — build's choice)
listens for a small set of player-action hooks and, gated by chance and
cooldown (Mod Settings, §5), spawns **one** gizka near the action with a
warm, non-warning letter:

| trigger | hook point (mechanism sketch) | flavor |
|---|---|---|
| Gravship lands / hold first walked | Odyssey gravship arrival event (exact hook to be verified against Odyssey source at build — SPECULATIVE until read) | "Something has been living in the hold." |
| Wreck / crashed-ship salvage | completion of deconstruct/claim on ship-chunk & wreck buildings | "It hopped out of the wreckage." |
| Purchased cargo delivered | trade completed with orbital/caravan trader above a goods threshold | "Crate three was not empty." |
| Quest flavor (optional, later) | a quest reward line item — gizka as the "free gift" nobody asked for | the classic scam, inbound |

- Exactly ONE animal per discovery. It spawns tame-or-near-tame (low
  Wildness handling roll — the creature's petness 0.15 and nuzzle behavior do
  the endearing work: nuzzles are the vanilla cuteness mood bonus, and
  colonists name it via the mod's own name generators).
- Letter is `PositiveEvent`-toned ⚑ (new LetterDef or reuse of a vanilla one
  — build decides; if new, `<RSW_LetterGizkaFound>`).
- Chance/cooldown numbers: NOT set here — Mod Settings sliders with defaults
  proposed on an owner card (§8). No invented number is a fact.
- The spawned gizka (and only event-lineage gizka) carries
  `<RSW_HediffShipboardFecundity>` ⚑ — see §2. Wild-biome gizka never get
  it, so the shrubland population stays ordinary fauna.

## 2. The turn — fed + warm → the problem

Comfort is the fuse. While a fecund gizka is **fed** (has had food recently /
food is reachable) and **warm** (ambient within its comfy band), the hediff's
breeder logic runs; cold, hunger, or the population cap stall it.

Mechanism: `<RSW_HediffShipboardFecundity>` ⚑ with a hediff comp shaped like
the Tribble's `CompProperties_TribbleSpawner` — **shape only** (a
self-replication comp with an interval knob, gated); the inactive mod's code
and numbers are never copied. Asexual spawning (one stowaway must be enough —
KotOR canon and the owner's premise), interval scaled by comfort, offspring
inherit the hediff. Why not ride the def's own EggLayer: (a) eggs need a
mated pair for fertile lay — one found animal would be inert; (b) the comp
must be **per-pawn** (event lineage only), and comps are per-def — a hediff
is the per-pawn carrier that leaves the wild population untouched.
The EggLayer stays as-is on the def: it is the donor's, it only matters if
the player deliberately breeds pairs (the "lean in" exit), and unfertilized
eggs are a small food trickle that makes ranching look tempting.

**Escalation stages — each with a fair warning BEFORE it hurts:**

| stage | shipboard pop (placeholder bands — owner card) | what happens | the warning the player can read |
|---|---|---|---|
| **Cute** | 1–2 | nuzzles, naming, tales; nothing else | the discovery letter itself said "they breed" in its flavor line |
| **Underfoot** | ~3–6 | filth, first food nibbling (vanilla diet doing its work) | letter: "gizka got into the food stores" the first time stored food is eaten |
| **Infestation** | ~7–15 | food-store raiding in earnest; **wiring/component chewing begins**: while a fecund gizka shares a room with powered buildings, those buildings take a breakdown-MTB penalty ⚑ (`<RSW_GizkaChewedBreakdown>` cause string; mechanism: a MapComponent applying the penalty, riding the vanilla breakdown system — no Harmony surgery expected, verify at build) | a letter at the stage boundary + sparking motes on affected conduits + breakdown letters that NAME the cause ("gizka-chewed"), never a silent stat |
| **Plague** | cap (~placeholder 20–25 — owner card) | crowding: beauty/space debuffs from bodies and filth; breeding STOPS at the cap (anti-exponential floor, §4) | the colony can hear them — ambient call-sound swell (donor's `Pawn_Gizka_Call`), and the stage letter says plainly: population has peaked, here are your options |

Stage letters are the contract: every stage boundary announces itself before
its cost lands. No stage skips; venting/culling back below a band steps the
stage back down.

## 3. The exits — each priced

All five are real choices; none is free; none compounds (§4).

| exit | how it rides existing systems | the price |
|---|---|---|
| **Cull** | draft-and-kill or slaughter designation — pure vanilla | mood: vanilla already charges for bonded/named animal deaths and witnessed slaughter; the ones colonists nuzzled and named cost the most. Fast, certain, sad. Optional ⚑ `<RSW_ThoughtGizkaCulled>` if vanilla thoughts prove too weak to feel — owner card. |
| **Sell onward** | vanilla trade — the def already has `AnimalFarm/AnimalCommon` tradeTags; the KotOR scam ("somebody always buys gizka") is the Jawa answer | slow (needs a trader/caravan), and pays pocket change **only if the sale price is flattened** — donor MarketValue 100 × a breeding swarm is a money printer. Requires a value patch ⚑ (our patch, our mod, not an edit to the donor) — number on an owner card. Mood-cheapest exit: sold is not slaughtered. |
| **Poison bait** | ⚑ new recipe + bait item (`<RSW_GizkaBait>`), consumed via the animal's own greedy diet | crafting cost + time; corpses to haul; small mood hit for animal-loving colonists (SPECULATIVE: vanilla may need a helper thought ⚑); quiet and hands-off otherwise |
| **Cold / vent the hold** | temperature is the fuse: drop the room below the breeding gate (the creature's ComfyTemperatureMin is 0 °C — the STALL threshold must sit above ambient cold snaps, tunable) and breeding stops; sustained cold attrits the swarm | free in silver, slow in days, costs the room (heaters off / doors open / hold vented); survivors are alive and still cute — this exit stalls, it does not solve |
| **Lean in — farm them** | vanilla animal husbandry: pen, feed, the def's own EggLayer with a mated pair, butcher for the donor's Saurian meat, sell stock | deliberately mediocre by §4: tiny meat yield (bodySize 0.18), flat low sale price, hungerRate 0.35 relative to yield, and the fecundity hediff never applies to deliberately-bred stock (only event lineage) — a funny bad idea that works, and never beats a muffalo |

## 4. The anti-exponential law (hard, per the item)

**The exponential belongs to the PEST, never the player.** The arithmetic
shape, qualitative:

- Pest side: population growth is geometric while comfort holds
  (each fecund gizka replicates on its interval) — that is what makes the
  problem a PROBLEM — but it is **clamped**: a hard map-population cap, and
  the interval stretches as the cap nears. Geometric onset, flat ceiling.
- Player side: every income line is **linear and flat**. Sale price per head
  is a flat small number, never demand- or population-scaled; meat per
  butcher is tiny and fixed; eggs are a trickle. Player revenue =
  (small constant) × (heads moved), and heads are capped. There is no term
  in the player's income that multiplies by population growth rate — so no
  ladder exists to climb: gizka farming's best case is "pocket change with
  extra steps," while ignoring the pest's own geometric phase costs food,
  components, and rooms. The joke stays a joke.
- Guard in mechanism: the fecundity hediff is the ONLY fast-breeding path
  and it never attaches to player-bred stock; the EggLayer pair-breeding
  path is vanilla-slow-ish and yields the mediocre farm above.

## 5. Mod options (MOD_OPTIONS_RETROFIT_1 doctrine — owner, 2026-09-12)

The mod ships a `Mod` subclass + `ModSettings` with a real
`DoSettingsWindowContents` UI (not a stub). Defaults = the shipped design;
all-off degrades gracefully (features gate at the comp/mapcomponent level —
no NREs, no orphaned defs; the creature itself belongs to the donor mod and
is untouched by any toggle). All settings are LIVE-behavior settings (no
worldgen interaction — nothing here touches the frozen map), and the UI
says so per the doctrine.

| setting | kind | gates |
|---|---|---|
| Gizka stowaway events | master on/off | the whole discovery manager; off = donor creature remains ordinary fauna, nothing else exists |
| Discovery frequency | slider | chance + cooldown on the trigger hooks |
| Breeding rate | slider (interval multiplier) | the fecundity hediff's replication interval |
| Escalation (chewing/breakdowns) | on/off | the Infestation-stage breakdown mechanic specifically — cute+breeding stays, sabotage stops |
| Population cap | slider | the hard clamp |
| Per-trigger toggles (gravship / salvage / cargo / quest) | checkboxes | each discovery hook individually |

## 6. Mechanism sketch — rides existing vs new

**Rides existing (no code, or config only):**
- Creature, art, sounds, name generators, egg items — donor mod, ACTIVE.
- Endearment: vanilla nuzzle (+mood), bonding, naming, tales.
- Food-store raiding: the def's own omnivore/ovivore/animal-product diet.
- Cull pricing: vanilla bonded/named-death and slaughter thoughts.
- Sell: vanilla trade via existing tradeTags.
- Cold exit: vanilla temperature + comfy band.
- Farm: vanilla husbandry + the def's EggLayer.
- Breakdowns: the vanilla breakdown system (we add a cause, not a system).

**New C# (all names are `<placeholders>`, RSW_ tier, coined by the build item
under the tier grammar — nothing coined here):**
1. `<RSW_GizkaStowawayManager>` — Game/MapComponent: trigger hooks, gate,
   one-animal spawn, letters. (The Tribble's `IncidentWorker` is the shape
   REJECTED; this replaces it.)
2. `<RSW_HediffShipboardFecundity>` + its hediff comp — per-pawn, inherited,
   comfort-gated asexual replication, capped. Shaped like
   `CompProperties_TribbleSpawner` (one interval knob, logic in C#) — shape
   referenced only; no code or numbers from the inactive mod.
3. `<RSW_GizkaChewedBreakdown>` mechanic — room-shared breakdown-MTB penalty
   + named breakdown cause. (Verify at build whether vanilla exposes enough
   without Harmony; SPECULATIVE that it does.)
4. Mod settings class per §5.

**⚑ New defs genuinely needed (small, all non-creature):**
- MarketValue-flattening patch on the donor `Gizka` ThingDef (our patch file).
- `<RSW_GizkaBait>` item + recipe (poison-bait exit).
- Stage/discovery LetterDefs (or vanilla reuse — build decides).
- Possible helper ThoughtDefs (cull, bait) ONLY if vanilla mood proves too
  weak in playtest — default is vanilla.
- NO IncidentDef, NO ThingDef/PawnKindDef/BodyDef for the creature, no art
  commission (bundle-render check owed first).

**Mod home**: an RSW_-tier mod folder (candidate: alongside SWBestiary in
`src/RimStarWars/` — name coined at build under NAMING_SCHEME_PLAN.md), with
`MayRequire`/loadAfter on `Mlie.StarWarsAnimalCollection`; if the donor is
absent the whole feature no-ops cleanly (the stowaway manager checks the def
exists).

## Owner cards — RULED, sitting 2026-09-12

- **Card 1 escalation: tunable, slow default.** Season-long slow burn ships
  as the default; every rate in Mod Settings (MOD_OPTIONS_RETROFIT_1).
- **Card 2 price: ~15 silver.** The donor's 100 is patched down; the scam
  stays funny, never income.
- **Card 3 cull guilt: IN.** Small "watched the gizka cull" mood penalty on
  top of vanilla — the humane exits stay competitive with the knife.
- **Card 4 launch scope: HOLD the whole feature for the gravship-hold
  discovery hook.** The flagship found-in-your-hold moment ships WITH the
  feature or the feature does not ship — confirming the engine hook is the
  gating spike.
- **Card 5 free-gift quest gag: IN v1** (owner, follow-up card 2026-09-12,
  reversing the deferred-by-default) — a gizka can arrive as a quest-reward
  "free gift"; one quest-system touch, ships with the feature when the
  hold-hook gate opens.
