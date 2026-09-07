# The Scarlands — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over two rounds and ratified
("Ok! Let's write it up! Nice work."). Defines `Scarlands` — 🔑 **vanilla Odyssey,
not a mod** (verified in the source index: `Defs/Odyssey/BiomeDefs/Scarlands.xml`,
with first-party ruins layouts, crater gen-steps, junk prefabs and gravcore site
hooks — the one donor that can never be retired out from under us). **The name is
kept: THE SCARLANDS** (owner's ruling). Thematic handle: **the last stand** — and
its image: **a battlefield where the whole story is still legible in the ground,
except who the enemy was.**_

🔴 **THE LORE IS PARTITIONED.** This sheet contains campaign truths the players
must DISCOVER (owner's ruling). §P is everything a player-facing text may say;
§GM is the truth ladder with its reveal gates. **Nothing from §GM appears in any
def description, biome text, or first-tier lore doc** — written as a hard ban in
§6 so no roster or flavor pass can leak it.

## 0. The measurements everything rests on

MEASURED 2026-09-06 off the live `world/ASHKARR_WORLDMAP_tiles.csv`: **90 tiles,
all in the Scorch** — the deep dayside (lat −12..+21, lon −10..+22), pressed
against the substellar neighborhood. Sun median **+72°**; temp median 59.4 °C
(57.6..66.0); rain **zero everywhere**; broken hill country (36 large-hill, 11
mountainous of 90); elevation to 620 m. ⚠️ Three river tiles at arc ~18 where
nothing should flow — flag for the freeze review. Neighbors are the whole story:
the **Rust Cathedral** (`AB_MechanoidIntrusion`, permanently at war) one region
over, its 305-tile pollution halo — the planet's largest connected poison block —
spilling into the Scorch; the **AncientLaunchSite** (tile 4000, in the Scorch)
where the dead-straight **Ashfall Road** begins; eight of twelve Free Droid
enclave seats next door in the Cathedral's holy poison.

Donor inventory (Odyssey): **kept nearly whole** — the AncientRuins_Scarlands
layouts, craters (L/M/S), junk clusters and prefabs, hermetic crates and ancient
pod contents, `AncientMegastructure` floor terrain below fertility 0.7, all-toxic
water variants, fish population zero, `wildAnimalScariaChance 0.5` (reflavored,
§GM), ToxRain and Gray Pall weathers, the settle-warning. **Stripped** —
SnowGentle/SnowHard (snow at 60 °C is a donor absurdity). **Evicted** — the
vanilla-Earth zoo and vanilla wildPlants (all-alien rule; the flora here is §4's
crusts, not grass).

## 1. What it is

The wound that never closed. Crater fields and slag hills on shattered
megastructure floors; bunkers, embankments, ruined turret rings and burnt shield
emplacements that all tell the same story, still perfectly legible after all this
time — a defense, layered and desperate, facing outward. Destroyed war machinery;
crashed ships of fabulous technology plundered to skeletons generations ago.
Whatever great city the ancients had here, there is very little left of it:
occasional ruins underground, skeletal building husks in a few places, little
else. The ground is poisoned in a way that does not fade and never will, the
wildlife is mad, machines defend the place for reasons they do not give — and it
is, by every Jawa's flat testimony, **cursed**.

## 2. Planetary position

Deep dayside (arc 11–22, sun ~+72°) × **the war anomaly**: this ground's identity
owes nothing to climate and everything to a single day at the end of an ancient
war. The energy regime just keeps the corpse hot.

## 3. Driving forces

**The weapons are still running.** Three engines, none of them alive:

- **Chemistry just short of life** — intentionally noxious compounds that
  self-replenish through self-replicating reactions. They do not decay away; they
  *maintain themselves*. This is why the land will never be fertile again.
  **Never.**
- **Million-year nuclear decay chains** — heat and radiation on a timescale that
  makes the ruin permanent geology.
- **The madness in the blood** — scaria, endemic at 50% in the wildlife (§GM owns
  its authorship; §P knows only that the animals here go mad).

The only surface water in the deep dayside rises here, and it kills you: the
ancients' buried plumbing and coolant galleries still leak upward into poisoned
ponds — and into the **rainbow pools** (§8).

## 4. What life remains

No soil, no sun-and-leaf economy — everything alive here eats what the war left.
The sorts (actual assignment rides the full plant-and-animal pass):

- **The Glowers** — black-hued mosses and lichens along the ground, **eating the
  radiation itself** (Earth's radiotrophic molds prove the trick): glassy dark
  varnish painting crater bowls and hotspots, thickening for centuries. The only
  flora. Harvestable as radiogenic fuel and pigment — with everything that
  implies.
- **The plated grazers** — rhino-armored browsers of crust and wreck-lichen,
  their plate so thick **they care little about weapons or much of anything...
  until the madness inevitably comes** (owner). The biome's scaria host: an
  animal built beyond fear, guaranteed to lose its mind — the worst possible
  combination, and the answer to "what's out here to GO scaria."
- ⭐ **The mynock** — the wiring-eater, and it is CANON AND LIVE: *The Empire
  Strikes Back*'s cable-chewing ship parasite, already in the mod set (Star Wars
  Animal Collection) and currently cast to three nightside biomes, one of them
  dissolved — **proposed true home: here**, grazing the dead war machines.
  Oddly cute — *to the Jawa*. 🔴 **The ship infestation** (owner): if the
  gravship comes to the Scarlands, mynocks get aboard — reproducing strangely
  fast, consuming conduit, flooring and lighting until hunted out of the hull.
  The biome follows you home (`SCARLANDS_MECHANICS_1`).
- **The Mortuary Guild** — slow, patient carrion-specialists, the only things
  that can digest the preserved dead of a graveyard that won't properly rot.
  Uncannily calm where everything else is mad; the one safe animal here, and the
  most disturbing.
- **The weapon-descendants** — feral living munitions breeding true since the
  last day, still executing fragments of a dead war's doctrine. (Their §GM
  meaning stays out of every def text.)

## 5. Always true

- The defense is legible: every ruin faces outward, layered toward the same
  approaches — the last stand is still visible in the ground itself.
- There is no evidence anywhere of what they were fighting.
- The land can never be made fertile; the toxicity replenishes itself.
- The wildlife carries the madness; the plated grazers always succumb in the end.
- The Forgotten Sentinels defend, never raid, never pursue past their lines, and
  never explain.
- Every ancient danger here has already been opened and destroyed.
- Salvagers return changed — sick in body, marked in mind. The Jawa call the
  place cursed and keep coming anyway.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No §GM truth in player-facing text** — no def description, settle
   warning, biome text, item flavor, or first-tier lore doc names the Rakata,
   the Assailants, the Cathedral's nature, scaria's authorship, or the pilgrims'
   why. The reveal gates (§GM) are the only doors.
2. 🔴 **No fertile ground** — no soil terrain, no farmable cell, no def whose
   story is growth; fertility here is a lie by definition.
3. 🔴 **No green** — the flora palette is black, glass, and rust; a green plant
   def resident here violates the sheet.
4. 🔴 **No intact treasure in the open** — surface wrecks are always stripped;
   value is sealed (hermetic, buried, or powered-down) or it is absent.
5. 🔴 **No snow weathers** (donor strip); ToxRain and Gray Pall stay.
6. 🔴 **No Sentinel aggression beyond their lines** — a Sentinel raid def or
   pursuit story violates the ruling; they defend only.
7. 🔴 **No vanilla-Earth fauna or flora** (standard eviction).

## §P — what the players are told

The biome description and all first-tier lore say only this register:

> A nuclear wasteland of inexplicable, self-renewing toxicity, strewn with the
> unmistakable works of a colossal ancient defense — bunkers, embankments,
> shield emplacements aimed outward, ruined turrets by the hundred — all telling
> the same story, with no trace of the enemy it was built against. **"The Jawa
> do not know who they were fighting, but they were keeping them away from the
> Rust Cathedral — that much is clear."** The ground is actively defended to
> this day by the Forgotten Sentinels, for reasons known only to them. They
> aren't talking. Runaway droids flee here to die. The animals are mad. The
> pools are beautiful and lethal. The place is cursed — *"though how glorious it
> would be to be able to... somehow."*

## §GM — the truth ladder (reveal-gated; never in first-tier text)

1. **The last stand**: this was the final defense of the great machine that is
   now the Rust Cathedral — it used every weapon it had (nuclear, toxic, its own
   biological variants) against the Assailants in one last great defense, and
   failed. The Assailants started on the far side of the world (the Impact Site
   canon, `the_propane_lakes.md`) and worked their way here. This was the grand
   plan, the place that couldn't fall. It fell. *Gate: earned lore via the
   neutral droids / the Cathedral.*
2. **The Sentinels**: the survivors — units in the wrong place at the wrong time
   to help, the only ones left. They guard their builders' graves and their
   god's deathbed. *Gate: as above; "Forgotten Sentinels" is the player-facing
   name throughout.*
3. **The Cathedral**: the enormous machine was on the verge of becoming an
   Archotech Mind — **forever incomplete** next door, oozing poisons and
   depressed nuclear sighs onto the land of its once-proud builders. *Gate:
   talking to the Rust Cathedral itself.*
4. **The Rakata**: this is the Pyrrhic LOSS of the final Rakatan stand
   (`ANCIENTS_AS_RAKATA_SPEC.md`); **scaria is their invention** — a madness
   weapon meant to turn the Assailants on each other. It didn't. It just hurt
   the ecosystem, to this day. *Gate: late; via the educated factions or the
   bastion record.*
5. **The pilgrims**: thawed Ancients walk here when they leave their vaults,
   only to discover there is no reason to remain alive anymore. *"This is where
   our grandparents fell."* Many of the dead droids, too, committed suicide on
   arrival — the lowest of the world, seeking freedom in the midst of death,
   losing hope at the sight of it. *Gate: found piecemeal at the pilgrim ends.*

## 7. Uniquely available

- **The sealed salvage** — the richest old-tech trove on the planet: hermetic
  crates, ancient pods, intact sublevels under the husks (donor gen-steps,
  first-party). The open wrecks teach the rule: everything obvious is long
  plundered; the prizes are sealed.
- ⭐ **Reclaimable droids** — among the dead of the hospice, **some entirely
  intact and just powered down**: walk in, carry one out, wake it. And a
  spare-parts trove in the darker sense. The tragedy is the economy.
- **Reagents from the rainbow pools** — self-replenishing chemistry no lab can
  make, harvested at the biome's full price.
- **Glower fuel** — radiogenic harvest from the black crusts.
- **The old tongue** — Rakatan script on every surface, long forgotten and
  unspoken, readable only by the very educated: **the Ascendant Helix and the
  Deepwater Compact** can translate (their scholars' monopoly, and a reveal-gate
  key).
- **Mynock pets** — oddly cute, catastrophically hungry; the Jawa keep trying.

## 7b. The curse, as mechanics

Three currencies price every salvage run: **toxic buildup** (the body), the
**Scarlands mark** (the mind — a lingering scar of mood and nightmare that
persists after leaving and never fully fades), and **scaria exposure** (you and
your animals). Plus the fourth the owner added: **the infestation** — mynocks in
the hull, breeding, eating conduit. You can salvage here. You'll return...
changed. That is the Jawa testimony, and the mechanics make it true.

## 8. Inhabited objects — all injected, all telling the one story

- ⭐ **The shield projectors** — old emplacements aimed to keep something OUT:
  dead projector rings facing the approaches, the plan's bones. Some hum yet.
- **The Last Line** — bunkers, embankments, turret rings, crater strings walking
  in from the far-side direction: the battle archaeologically legible; a player
  who maps the craters is reading the last day. At its heart, **the bastion that
  couldn't fall** — the deepest dungeon, holding the ladder's final record.
- **Sentinel ground** — patrol lines, repair alcoves, grave-wards; defense
  only, forever.
- **Ancient dangers, plentiful — and ALL already opened and destroyed**
  (owner): sprung mech clusters, cracked-open threat vaults, spent horrors.
  The message is deliberate: *this is what all that was for.*
- **The droid hospice** — rings of powered-down chassis facing the Cathedral;
  fresh arrivals still trickling in; many self-ended on arrival; a few intact
  and reclaimable; rumors that some survive beyond yet (the hidden enclave is a
  quest, never a map marker).
- **The pilgrim ends** — terminal camps along the Ashfall Road; each one found
  is a rung of §GM's ladder, in the Ancients' own words.
- **The stripped fleet** — skeletal crashed ships, gutted generations ago.
- ⭐ **The rainbow pools** — bright chemistry and minerals, attractive and
  pretty and *horrible*: hot from their own reactions, utterly deadly. **"The
  color isn't life, it's reaction and acid."** (owner, verbatim — the biome's
  palette thesis.)

## 9. Artistic theme

**"A battlefield still explaining itself, in a land the color of reaction."**

- **Light:** merciless white glare at +72° over black varnish and rust; heat
  shimmer as the standing air; Gray Pall and ToxRain as the only weather moods.
- **Palette:** crater-black glower crusts, rust and bone of the works, slag
  grey — and the rainbow pools as the only saturation on the map: acid greens,
  copper blues, sulfur yellows, all lying about what they are.
- **Silhouette language:** outward-facing geometry — emplacement rings, turret
  stubs, embankment lines; skeletal husks; the Sentinels' patient patrol.
- **Motion:** shimmer, a mynock flock off a wreck, a plated grazer's slow walk —
  then scaria's sudden sprint.
- **Sound:** wind on metal, Geiger-tick ambience, the pools' faint boil; the
  Sentinels make no sound the player's pawns can hear.

---

## Owed

- `SCARLANDS_MECHANICS_1` — the C# kit: the mynock ship-infestation system
  (boarding, breeding, conduit/flooring/lighting consumption, hunt-out), the
  Scarlands mark hediff, scaria-onset behavior for the plated grazers,
  Sentinel defend-only AI bounds, pre-sprung danger dressing.
- `STAGED_LORE_DESCRIPTIONS_1` — the owner's wish, filed: can the scenario
  change its own terrain/biome descriptions as lore is revealed, stage by stage?
  ("Wouldn't that be amazing.") Engine feasibility first; the §P/§GM ladder is
  the content it would drive.
- `ANCIENT_RUINS_MOD_AUDIT_1` — the mall-maps mod audit (filed this sitting);
  its generation tech, if worth learning, feeds this biome's injected sites.
- **Roster** — rides the full assignment pass: the sorts of §4, the mynock
  re-cast (its three current homes include the dissolved HorrorWastes), donor
  density corrections.
- **Reconciliations at the canon sitting** (`CANON_LORE_PROPAGATION_1`,
  Wednesday): one line each into `what_the_machines_are.md` and the Propane
  Lakes' terramanufacture history tying the god-machine program to the Rust
  Cathedral AI (forever incomplete); `ANCIENTS_AS_RAKATA_SPEC.md` gains the
  last-stand paragraph; `the_forgotten_war.md` reconciled or superseded.
- **The three river tiles** at arc ~18 — freeze-review flag (nothing should
  flow here).
- **Def-label check** — "scarlands" label stands (name kept by ruling); no
  rename needed at the freeze review, only the donor strip patch.
