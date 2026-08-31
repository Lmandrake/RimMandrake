<!-- status: draft — BENCH concept for owner ruling, 2026-08-31. Tier: RimMandrake core (underwater framework) + RimStarWars sea-beast layer + RimUtinni Ash'karr seas. Working names: RimMandrake Depths / The Drowned Dark -->
# The Depths — underwater as space, dark for a whole new reason

_Owner's seed, verbatim anchor: "a mod that goes underwater using vacsuits
just like space does only for water. Dark and foggy for a whole new reason.
Alien plants and animals. Makes attack from above very real and constant like
drop pod raids." Answers EMPTY_SEAS_FAUNA_1 — the three seas hold nothing
alive today (MEASURED), and this is what they were waiting for._

_Owner's second seed, 2026-08-31, verbatim anchor: "New resources, the concept
of being immersed in a massive conductive fluid (electrical area attacks are
very powerful), most weapons malfunctioning, new weapons that work, slow
movement similar to vacuum dynamics, the need for oxygen, and some races being
totally adapted and comfortable (NOT Jawa). Ultimately it would be excellent if
we could have the Deepwater faction have settlements beneath the waves even.
And a great place to hide from the Empire." And on the donor mods (GravTide,
Electrofishing, Gerrymon's Nautian Style): "they tend to be too cartoonish. I
would like to take the underwater biome much more seriously than this." —
inspiration and parts sources, never the register. §9 carries the survey._

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

The honest unknown — how much of the vacuum layer is patchable versus
hardcoded — now has an **existence proof**: GravTide (§10) ships today doing
exactly this reuse, via `<inVacuum>true</inVacuum>` on a biome plus Harmony
patches on `VacuumComponent.ExchangeRoomVacuum`, `Pawn.HarmedByVacuum` and
kin. The bet is won in principle; the Odyssey source-read gate (§11) remains,
but it now has a map — GravTide's patch-target list IS the verify list, and
the read decides how much needs a companion DLL of our own, not whether the
approach works.

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
  pit-cover inverted — §9) becomes the sandbag of the deep.
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

## 5. The medium is the mechanic — immersion in a conductive fluid

The deep is not a dark room you walk through; it is a substance you are
suspended in, and every system below follows from that. (Owner's second seed —
all four are ruled IN.)

- **Oxygen is the clock.** The dive suit's air supply is the primary resource
  of every expedition — the vacuum layer's exposure timer made front-and-center
  rather than incidental. Every plan below the surface is shaped by the swim
  back. Adapted races (§7) are exempt, and that exemption is their whole
  economic and military identity.
- **Movement is slow, vacuum-style.** The same drag dynamics Odyssey applies
  in vacuum, reused with the sign flipped: unadapted pawns move through water
  like divers, not runners. Slowness is what makes the lamp radius, the
  descent shadow and the swim-back clock bite. Adapted races swim at full
  speed — in their country, *you* are the lumbering one.
- **Water is a massive conductive fluid, and electricity knows it.**
  Electrical AREA attacks are very powerful underwater — the owner's ruling,
  and the deep's signature combat physics, cutting both ways:
  - *Yours:* discharge weapons and tesla-mine emplacements that stun or kill
    everything in the water body around the point of discharge — the answer to
    a scavenger swarm or a shoal-borne ambush, and far stronger than any
    surface equivalent.
  - *Theirs, and the environment's:* a breached conduit electrifies the
    flooded room; a discharge is indiscriminate — your divers in the field
    are in the field. And a discharge is the loudest thing you can do:
    a massive spike of lure pressure (§3). The dinner bell, electrified.
- **Most weapons malfunction; the deep has its own armory.** Blasters and
  slugthrowers misfire, short, or do nothing underwater — carrying a surface
  loadout below is a mistake the game teaches once. What works, by design:
  - **Harpoon weapons** — the deep's ranged standard: slow, silent,
    armor-piercing, retrievable.
  - **Discharge/ion weapons** — the area nuke above, with its lure cost.
  - **Sonic/pressure weapons** — concussive bursts the medium carries better
    than air ever did; the mid-tier between harpoon and discharge.
  - **Melee, always** — spears and blades care nothing for wet; the silt
    ambusher fight is a knife fight whether you planned one or not.
  The verify target: how vanilla/Odyssey gates weapon function per
  environment, if at all — this may be the first genuinely new C# surface
  (a `weaponsUnderwater` verb gate) rather than a reskin.

## 6. The alien bestiary and flora — the art the owner already said yes to

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

## 7. The Deepwater faction — the people the water already belongs to

The owner's ruling: some races are **totally adapted and comfortable** down
there — and the Jawa are explicitly not among them. The deep is a foreign
country with its own citizens, and that asymmetry is the design.

- **Adapted races** (RimStarWars tier — aquatic species belong to every SW
  scenario): water-breathing, full move speed in water, dark-adapted senses,
  pressure-immune body. In gene terms, each adaptation is one lever of the
  drowning/pressure/drag stack in §5 turned off — which is why the stack
  must be stats and hediffs, not hardcode: a gene that zeroes a stat is free.
  The SW register offers Mon Calamari, Quarren, Nautolan and Gungan shapes to
  draw from; which species ship is an art-and-canon pass of its own.
- **The Jawa get nothing.** No dive gene, no comfort, no exception. Every
  Jawa below the surface is a guest inside a machine with a countdown — the
  clan's relationship to the deep stays technological (suits, hulls, hired
  guides), never biological. That keeps §1's dread honest for the player
  forever.
- **Settlements beneath the waves.** The Deepwater faction holds world-map
  settlements on sea tiles — lit towns in the trench dark, reachable only by
  diving, trading in what the surface cannot make (§8). They are the deep's
  proof of concept: civilization IS possible down here, just not yours yet.
- **The place the Empire cannot see.** The Empire's writ ends at the surface
  the way Sh'kaar's does — orbital scan, TIE patrol and garrison doctrine all
  stop at the waterline. The deep is where you go to disappear: fugitives,
  contraband, a clan that has made itself too interesting. A Deepwater
  settlement that will hide you is the campaign's ultimate bolt-hole — for a
  price, and the price is denominated in favors to people who never needed
  the Empire's permission to exist. (Genre precedent everywhere: the deep
  city is where you hide from the surface power. It plays.)

## 8. Why go — the reasons the sea tilemap earns its place

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
6. **Because the Empire cannot follow.** §7's bolt-hole: the deep is the
   one refuge orbital power cannot audit, and a campaign that picks a fight
   with the Empire needs exactly one of those.

## 9. Coupling notes

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

## 10. Donor-mod survey — measured 2026-08-31, owner-commissioned

All three named mods are subscribed on this machine and were read on disk
(workshop ids attached). Verdicts against the owner's lens — parts and
inspiration, never the register:

| Mod (workshop id) | What it IS | Verdict |
|---|---|---|
| **GravTide** (3779600989) | ~250 C# files, ~130 defs. Odyssey vacuum reused as water pressure — depth-rated suits (20/300/1000 m), hypoxia + HPNS hediffs, drowning formula `(1−GearSeal−BodySeal)×(1−WaterBreathing)`, `StatPart_WaterDrag` on MoveSpeed, `UnderwaterWeaponExtension` crippling unfit weapons, no-fire-underwater, flooding that shorts powered gear, depth-banded seafloor mapgen (vents, oil seeps, plasteel nodules), and a ship/platform/submarine layer | **The architecture textbook.** Not cartoonish — art is vanilla-consistent and its real-world vent/kelp ecology is exactly the seriousness the owner wants. Steal the *shape*: stat/hediff/extension architecture, patch-target list, depth-band mapgen. Its content register (industrial sub-nautical) is not ours — SW trench gothic is |
| **Electrofishing** (3542849317) | One building + one C# comp: water-body-gated AoE shock (Burn + chance-Stun to every pawn standing in water within radius), power-gated, and agitation can trigger a raid *from* the water | **One good pattern.** The water-body-scoped AoE is §5's discharge weapon in miniature, and shock-noise-summons-the-deep is our lure doctrine arriving armed. A weekend's C#, ours to rewrite |
| **Gerrymon's Nautian Style** (3147664706) | Pure StyleCategoryDef/ThingStyleDef/terrain reskin — an "Ocean" aesthetic for vanilla buildings and floors. **No race, no genes, no faction, no C#, no creature art at all** | **Least relevant.** Useful only as precedent that a style category can carry the Deepwater faction's visual identity via ATH Stylable Framework. The fish-people race the name implies does not exist in this mod or its family (8 siblings checked, all unrelated) |

**License reality:** none of the three grants reuse — no LICENSE file, no
permission clause anywhere. So nothing is copied: GravTide is a *map* of what
works (its patch targets, its stat shapes, its formula), and everything we
ship is written fresh under our own namespaces. If verbatim asset reuse ever
looks worthwhile, the route is asking the author (GravTide's About.xml links a
Discord), not lifting.

**What the survey changes upstream:** §2's bet is proven (GravTide exists);
§5's drowning/pressure/drag stack should be built as stats + DefModExtensions
*because* that is what lets §7's genes switch it off per-race; and the
"weapons malfunction" mechanic has a working precedent (verb/projectile
Harmony patches reading a per-weapon extension) rather than being novel risk.

## 11. Scope honesty — the v1 slice vs the dream

**v1 — "Dive expeditions" (a caravan-scale slice, no underwater colony):**
sea tiles become visitable sites with dive gear required; the oxygen clock
and vacuum-style water drag (§5); weapons gated per-environment, with the
harpoon standard and one discharge weapon shipping alongside; permanent-dark
short-sight rules; the light-lure clock; descent arrivals; one wreck-field
site type; one leviathan; the silt ambusher and harpooner; the Deepwater
faction present on the world map — settlements on sea tiles, visitable and
trading (§7), adapted-race genes on its pawns; Oomo's shore rite. No
base-building below, no moon pools, no flooding sim, no refuge storyline
yet. This ships on the Odyssey-analog bet at its cheapest and proves the
fantasy.

**v2 — "The Drowned Colony":** anchored platforms, sealed habitats, moon
pools, flood-on-breach (with §5's electrified-room consequence), farming
vents, the full bestiary, sound-lure, leviathan weather, and the Empire
bolt-hole arc — hiding the clan in a Deepwater settlement as playable
refuge, not just lore. The full "space but wet" dream — priced only after
the v1 source-read tells us how much of Odyssey's layer we can actually
wear.

**Gate before ANY build spec:** the Odyssey source-read (§2's VERIFY
column), now read side-by-side with GravTide's patch-target list (§10) as
the map of what is known to work. One session, game-down, rimsage only. It
decides patch-mod vs companion-DLL and therefore everything about cost.
