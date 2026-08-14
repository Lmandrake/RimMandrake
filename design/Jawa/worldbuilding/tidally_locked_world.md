# The world is TIDALLY LOCKED — and it explains everything

_VISION, 2026-08-14. **Owner's ruling, and it is the largest single piece of
worldbuilding this project has produced.** Recorded the hour it was made. Mods
installed for it: `Tidally Locked` plus two others._

> **One face of the planet never turns away from the sun. The other never sees
> it. Everything that lives does so in the band between.**

---

## The three worlds on one planet

| | **DAYSIDE** | ⭐ **THE TERMINATOR** | 🔴 **NIGHTSIDE** |
|---|---|---|---|
| light | perpetual, unmoving sun | **perpetual twilight** | **perpetual night** |
| heat | scorching, worse toward the centre | temperate | **cold** |
| water | **none at the centre** · rare oases in the near-deserts | ⭐ **all of it** — the seas, the rivers | frozen or absent |
| who lives there | **the Galactic Empire**, at the dead centre · **the neutral droid factions** in low mountains with poisonous volcanic springs · the Hutts at the oases · Tuskens and the Trade Moot in the near-desert | **the Deepwater Compact** on the seas · **the Wildsteam Clan** on the rivers, in the jungles and poison marshes · the Homestead on the arable margin | ⭐ **the Forsakens' leavings.** Terrible and strange creatures. The Forgotten Arsenal |
| the player's relationship | where the work is | where the water is | ⭐ **where you go when you cannot be found** |

---

## ⭐⭐ What this SOLVES — and it is most of the campaign

**This is not flavour. It retires four separate design problems at once.**

### 1. Hiding stops being a mechanic and becomes a PLACE

**Owner's ruling: Imperial pursuit is greatly extended or terminated while the
player is on the nightside.**

I had specced hiding as *"it must cost progress, not hit points"* and hunted for
a mechanism. **The tidal lock gives it geography instead.** Go dark — literally —
and the hunt loses you. And the price is not a number:

- **no sun** → no solar, no crops, nothing grows
- **cold** → a species evolved for the dune sea is wrong here
- **terrible fauna** → the refuge is inhabited
- **distance** → everything you trade for is on the other side of a planet

⭐ **A refuge you cannot farm is the perfect hiding place**, because staying is
its own punishment and nobody has to author a timer.

### 2. It explains the forsaken crags

`AB_RockyCrags` carries a **hardcoded 0.34 sun-glow multiplier** and can never
roll clear weather — I had recorded that as a biome quirk. **It is not a quirk any
more. It is physics.** The dark biome *is* the nightside, and its own description
already says an ancient race partly terraformed this world and left.

⭐ **The Forsakens tried to fix a tidally locked planet and failed.** That is why
the dark never lifted, and it is the best back-story this world has been offered.

### 3. It explains why the water is where it is

🔴 **This SUPERSEDES my latitude rule.** I had written *"water increases with
latitude; the poles hold the standing water."* **Wrong axis.**

> **Water follows the TERMINATOR, not the poles.** It is the only band where
> water is neither boiled nor frozen.

⚠️ **But the seas must not read as a literal ring** — owner's explicit
instruction. **Elongated natural blobs lying NEAR the terminator, and one of them
near a pole** to make the planet feel alien rather than diagrammatic.

### 4. It explains the Empire's position, and the droids'

**The Empire holds the dead centre of the dayside — the harshest desert, no water
at all, volcanoes and mountains — because nobody else could.**

⭐ **That is the Empire's whole character expressed as a map position.** Their
power is logistics: they truck their own water and can therefore be anywhere,
including the one place with none. **A faction that holds the worst ground on the
planet is more frightening than one that holds the best.**

**And the neutral droid factions sit in the low mountains among poisonous
volcanic springs** — a place that kills anything that breathes, held by things
that do not.

---

## The Hutts: BESIDE the oasis, never on it

🔴 **Owner's correction, and it is a playability rule, not a fiction one:**

> **The Hutts dwell BESIDE an oasis, never on top of one — or the player can
> never reach the water at all.**

**But the oasis tile itself is the prize and must look it:**

- ⭐ **very heavily augmented** — the most built-up tile type in the game
- **swarming with Hutt-loyal defenders**
- rare, in the **near-deserts** between the centre and the terminator

⭐ **The design consequence is a genuine tactical choice, which "they own it" would
have foreclosed:** the water is reachable, guarded, and *not* the same tile as the
settlement. **You can raid the well without besieging the town** — and that is a
far better decision than a binary.

---

## Faction positions, revised

| faction | where, now |
|---|---|
| **Galactic Empire** | ⭐ **dead centre of the dayside.** No water, volcanoes, mountains |
| **neutral droid factions** | low mountains, **poisonous volcanic springs** |
| **Hutt Cartel** | **beside** the rare near-desert oases |
| **Deep Desert Tribes** | the near-desert, between centre and terminator |
| **Jawa Trade Moot** | the same band — circuits across the near-desert |
| **the Junkers** | wreck fields, wherever things fell |
| **Homestead Defense League** | the arable margin of the terminator |
| ⭐ **Wildsteam Clan** | **the rivers** — the wild jungles and poisonous marshes |
| ⭐ **Deepwater Compact** | **the seas of the twilight band** |
| **Geonosian Foundry Hive** | subterranean, dayside rock |
| **Ascendant Helix** | isolated, cold — **nightside edge** suits them |
| **Blackstar Company** | everywhere; they follow the money |
| 🔴 **the Forgotten Arsenal** | ⭐ **the nightside.** It is where the Forsakens left it |

---

## 🔴 What must change, urgently

1. **The sea spec is now wrong.** `worldgen_sea_spec.md` says *"three oddly-shaped
   bodies at HIGH LATITUDE, centroid nearer a pole than the equator."*
   **It must become: elongated blobs lying near the TERMINATOR, with one near a
   pole.** ⚠️ **CREATE is building to the old test right now.**
2. **`faction_world_spec.md` §4 geography** — the latitude bands are superseded by
   day / terminator / night. Rewrite.
3. **The biome verdicts shift**: cold biomes are no longer "poles only", they are
   **nightside**. And the harshest desert is **not** at the equator — it is at the
   **subsolar point.**

## ⚠️ One design caution, stated so it is deliberate

**If the nightside terminates the pursuit, a player could simply move there and
stay.** The ruling already prevents it — no sun, cold, terrible fauna, and every
trading partner a planet away — **but that must remain true in the numbers, not
just in the prose.** ⛔ **The moment the nightside becomes farmable, the campaign's
central tension is over.**
