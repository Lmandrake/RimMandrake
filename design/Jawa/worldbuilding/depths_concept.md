<!-- status: draft — BENCH concept for owner ruling, 2026-08-31. Tier: RimMandrake core (underwater framework) + RimStarWars sea-beast layer + RimUtinni Ash'karr seas. Working names: RimMandrake Depths / The Drowned Dark -->
# The Depths — underwater as space, dark for a whole new reason

_Owner's seed, verbatim anchor: "a mod that goes underwater using vacsuits
just like space does only for water. Dark and foggy for a whole new reason.
Alien plants and animals. Makes attack from above very real and constant like
drop pod raids." Answers EMPTY_SEAS_FAUNA_1 — the three seas hold nothing
alive today (MEASURED), and this is what they were waiting for._

## 1. The fantasy

The surface of Ash'karr belongs to the sun that never sets. The deep does
not. Fifty meters down there is no day, no horizon, no Searer — only a green
darkness that ends three body-lengths from your faceplate, the tick of your
own regulator, and the slow rain of the galaxy's garbage settling into the
silt. Every wreck that ever fell into these seas is still down here. So is
everything that learned, over ten thousand years, to eat around them.

**This is the one country Sh'kaar cannot enter.** The sun's writ ends at
depth — the deep is Ishko's second kingdom, darkness so total it does not
need walls. And the first time a diver switches on a lamp down there, the
whole theology snaps into mechanics: light is work-speed, light is sight,
and light is a dinner bell. The lure-layer doctrine the Jawa use on raiders
is inverted onto the player. Down here, *you* are the baited beacon.

## 2. The analog — Odyssey's vacuum, reframed (the engineering bet)

The core bet of this mod: **RimWorld 1.6 already ships an environment-suit
survival layer** — vacuum, vacsuits, sealed rooms, hostile-exterior maps.
Water is vacuum with the sign flipped: pressure instead of nothing, drowning
instead of decompression. We reskin and patch the machinery rather than
reinvent it. Mechanism families to reuse, **every one VERIFY-against-source
before the build spec freezes** (names below are candidates from play
knowledge, not verified symbols):

| Space (Odyssey) | Depths | VERIFY target |
|---|---|---|
| Vacuum room-state + exposure hediff | **Pressure/water state** + drowning-pressure hediff | the vacuum severity pipeline: is it a room stat, a hediff giver, or both; is the damage type patchable |
| Vacsuit apparel requirement | **Dive suit** (vacsuit-analog stats: pressure rating, air supply) | which apparel stat gates vacuum immunity; can a parallel stat ride the same checks |
| Hull integrity / sealed rooms | **Hull vs water**: a breach FLOODS (severity spreads room-by-room) | how vacuum "leaks" propagate; reuse for flood-fill |
| Airlocks | **Moon pools** — the open hole in the floor that pressure keeps dry | airlock door family; whether a floor-portal variant is C#-cheap |
| Space map generation (asteroid/orbital sites) | **Seafloor map generation** (silt plains, reef walls, wreck fields, trench edges) | the orbital MapParent/site generator family; how much is def-driven |
| Substructure (gravship floor) | **Anchored platform** — the buildable seabed footing | substructure terrain affordance; reusable as-is? |
| Drop-pod arrival workers | **Descent arrivals** (§4) | PawnsArrivalModeWorker family — can arrivals animate downward with a warning shadow |

The honest unknown: how much of the vacuum layer is data (patchable) versus
hardcoded to the literal word "vacuum" in C#. That single source-read decides
whether v1 is a patch mod or needs a companion DLL, and it should happen
before anything else is specced further.

## 3. Darkness and fog — the defining sensory rule

- **Permanent dark.** No day/night cycle below; ambient light is zero
  everywhere, forever. The deep is not "night outdoors" — it is a place
  where light exists only if you brought it.
- **Short sight.** Line-of-sight capped hard (a fog-of-war radius of a few
  cells beyond your lamp). The map is discovered lamp-cone by lamp-cone, and
  what you mapped an hour ago is dark again behind you. Dread by geometry.
- **The light economy — the mod's central dilemma.** Powered lamps give full
  work speed and sight and *accumulate lure pressure* (a rising attraction
  clock read by §4's spawner — light literally calls the leviathan).
  **Bioluminescent flora gives dim, safe light** — harvestable, plantable,
  weak. The player constantly chooses between working fast under bright
  lights with a rising dinner-bell meter, or living slow and blue-green and
  unseen. This is Ishko vs Sh'kaar restated in lumens, one country down.
- **Sound as the second leak** (v2 candidate): drills, turrets and engines
  add lure pressure even unlit. The quiet colony is the theology again.

## 4. Attack from above — the water column is the sky

The owner's drop-pod instinct, made native:

- **Everything arrives by DESCENT.** Predator raids do not path in from a
  map edge — they come down out of the column. The warning is a **shadow**:
  a darker darkness sliding across the silt, two beats before impact (the
  F9 signature grammar applies — every descent is signed by its shape).
  Attack from above is "very real and constant" exactly as drop raids are:
  you harden the roofless dimension, not the walls. Overhead netting (the
  pit-cover inverted — §7) becomes the sandbag of the deep.
- **The rain of salvage.** The same column delivers the economy: wrecks,
  cargo pallets, dead machines and drowned ships **sink in** over time —
  scatter events seeded by the surface world's battles and by history. The
  sea is the galaxy's largest scrap-heap and it is still being fed. Rekko's
  country as much as Ishko's: the deep is where everything discarded
  eventually comes home, and the Keepers of the Second Hand were always,
  theologically, going to end up down here.
- **Leviathan weather.** The apex creatures are not raids but *weather* — a
  leviathan passing overhead is an eclipse with intent: lights off, work
  stops, everyone holds still on the silt until the shadow slides on. (It
  reads your lure pressure. Usually it keeps going.)

## 5. The alien bestiary and flora — the art the owner already said yes to

Creature slots by role, sized under **beast-normalization Law 3** (best-hit
≈ 12–15 × bodySize — at sea scales this is the whole point):

| Role | Body size | The idea |
|---|---|---|
| **Shoal grazers** | 0.1–0.5 | ambient life in hundreds; part scenery, part food, part alarm system (a shoal scattering is your only warning some nights) |
| **Silt ambushers** | 1–2 | the pit trap grown fins: buried flatforms that ARE the seabed until stepped on — trap-sense reads them, nothing else does |
| **Harpooners** | 2–4 | mid-size pack hunters that strike from outside your lamp radius and retreat; the bull-class — one hit downs a diver, Law 3 honest |
| **The leviathan class** | 12–20 | under Law 3 a bs-15 sea monster hits for ~200: not an encounter, an EVENT. One per sea, named, known, mapped around. Star Wars is legendary for huge beasts; here is where ours live |
| **Scavenger swarms** | 0.2, in numbers | arrive at blood and noise; the corpse-cleanup that makes every fight's aftermath its own countdown |
| **The colossal neutral** | 30+ | a filter-feeder so large it reads as terrain; graze-anchored, harmless, awe — the deep's thrumbo, and the proof the deep is a place, not a dungeon |

**Flora as systems, not set dressing:** lightkelp forests (the safe-light
crop and the sight-line breaker both); tangle beds (natural entanglement —
the snare register underwater); pressure-fruit (the unique food that
justifies farming down here at all); vent gardens (heat + light + danger in
one tile — the deep's oasis, and its most contested real estate).

## 6. Why go — the reasons the sea tilemap earns its place

1. **Salvage no one else can reach** — the sunken colonization-age fleet.
   The terraformer that made these seas drowned its own support ships in
   them; the wreck-vaults hold pre-fall technology (Rekko's "the whole Jawa
   future may already be aboard" extends: some of it is *below*).
2. **Unique materials**: leviathan hide/bone (the armor tier the surface
   cannot craft), pressure-formed minerals, vent chemistry, lightkelp
   pharmaceuticals — each a trade line Mob'Unloo prices gladly.
3. **Quest vaults**: sea-floor dungeon sites, the drowned counterpart of the
   Forsaken vaults arc.
4. **The theology demands it — Oomo's pilgrimage.** His Body-vision is a
   water-bearing sanctuary "filling its chambers with eggs to re-seed the
   world." The sea is his cathedral: a rite AT the water (the clan at the
   shore, the eggs blessed in the shallows) is the pilgrimage his worship
   has been missing, and the first reason a pious clan ever looks at the
   coast tiles. The deep is the one place his waters and Ishko's dark agree.
5. **Because the map already paid for it.** Three seas were hand-authored
   into a fixed world and currently hold nothing. This mod is the reason
   they exist.

## 7. Coupling notes

- **Beast normalization**: sea creatures are born under Law 3 — no retrofit.
- **Pits come along**: the trap doctrine translates — weighted drift-nets
  (the cover, floating), anchored snare-lines in the column (the tripwire,
  vertical), and the moon-pool cage (the pit cell, flooded — the deep's
  prisoner hold). Overhead netting is the pit cover pointed up.
- **Naming**: `mandrake.rm.depths` (framework) · sea-beast content
  `mandrake.rsw.*` (SW's legendary megafauna belong to every SW scenario) ·
  Ash'karr's three named seas, their leviathans and Oomo's rite
  `mandrake.rut.*`.
- **Trap-sense, Visibility, the Ninefold**: lure pressure is Visibility's
  sibling dial — same shape, wetter; consider one shared C# core.

## 8. Scope honesty — the v1 slice vs the dream

**v1 — "Dive expeditions" (a caravan-scale slice, no underwater colony):**
sea tiles become visitable sites with dive gear required; permanent-dark
short-sight rules; the light-lure clock; descent arrivals; one wreck-field
site type; one leviathan; the silt ambusher and harpooner; Oomo's shore
rite. No base-building below, no moon pools, no flooding sim. This ships on
the Odyssey-analog bet at its cheapest and proves the fantasy.

**v2 — "The Drowned Colony":** anchored platforms, sealed habitats, moon
pools, flood-on-breach, farming vents, the full bestiary, sound-lure,
leviathan weather. The full "space but wet" dream — priced only after the
v1 source-read tells us how much of Odyssey's layer we can actually wear.

**Gate before ANY build spec:** the Odyssey source-read (§2's VERIFY
column). One session, game-down, rimsage only. It decides patch-mod vs
companion-DLL and therefore everything about cost.
