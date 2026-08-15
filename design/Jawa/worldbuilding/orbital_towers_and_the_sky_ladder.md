# Orbital towers and the sky ladder — the Empire's way down

_VISION, 2026-08-13. **Owner's design, recorded the moment it was made**, because
it closes a hole I had left open and had ruled `[v2]`-blocked an hour earlier._

> *"The space towers were owned by the Galactic Empire — how they land and access
> the surface — so they get VERY angry about it. And that's the whole point the
> Hutts were after."*

---

## What this fixes, stated first

**Space Tower's kill condition (b) was "it must cost Imperial Heat", and Imperial
Heat does not exist** — it is a blackboard variable at M4, not a mechanic
(`build_plan.md:180`). CREATE offered an Empire-goodwill patch as a proxy and I
ruled it **invisible**: a −15 against a faction the design wants permanently
hostile is bookkeeping the player never feels.

**The owner's answer does not need the gauge at all.** The cost is not a number.
**The cost is that you just broke the Empire's elevator, and the Empire noticed.**

## The three facts, and everything follows from them

1. **The towers are Imperial infrastructure.** They are how the Galactic Empire
   gets down to the surface and back — a fleet in orbit is not an occupation
   until it can *land*. The towers are the ladder.
2. **The Hutts sell you the map.** Not from generosity. **The Cartel wants the
   Empire's surface access shortened**, and a Jawa clan is a deniable instrument
   that already owns a ship and a reputation for taking things apart.
3. **The Empire retaliates.** Not with a goodwill tick — with weight, aimed at
   you, because you are the one who was seen leaving.

## Why this is worth building — the player-facing answer

**It turns loot into a campaign.** A tower you rob for a gold chest is an errand.
A tower you rob *because someone paid you to cut the Empire's ladder* is a move
in a war, and the retaliation is the confirmation that it worked.

⭐ **And it gives the Jawas the role the fiction always claimed and never
mechanised: the small party everyone uses.** The Hutts are not your ally; they
are your client. You are being *spent*. The player should be able to feel that
and take the job anyway, because the pay is real and the alternative is being
poor — which is the most Jawa sentence in this document.

⭐ **It also finally makes the sky-ceiling two-directional.** `desert_world_design.md:651`
established that going up gets you noticed. Until now that was pure cost. **Now
going up is also how you hurt them**, and the player has a reason to accept the
risk instead of merely avoiding it.

## The strategic layer — one line, and it is the whole v2 pillar

> **Every tower you take down shortens the Empire's reach in that region.**

Fewer towers → less Imperial pressure locally. **The player can, with enough
nerve and enough Hutt money, buy themselves quiet by making the sky expensive.**
That is a strategy the campaign does not currently have, and it uses only things
that already exist: a site, a quest, a raid weight.

⚠️ **Not v1, and not to be started as v1.** `V1_SCOPE.md` ships one quest. This
is a **v2 storyline pillar** and is written down so it is not re-derived.

## Variants the owner asked to keep on the register

**"Real orbital elevator / skyhook experiences, or just go with the towers."**
Both fit the same fiction; they differ in what the player does:

| | what it is | the player's verb | cost to build |
|---|---|---|---|
| **Tower** ⭐ | the mod's own multi-level dungeon, orbital | **strip and leave** | ships today |
| **Skyhook** | a tether the Empire lowers to a fixed surface site — the *ground* end is the target | **cut it, and watch the sky end fall** | new authoring; the falling half is the memorable part |
| **Elevator** | a permanent Imperial ground installation that the towers serve | **besiege or infiltrate** | closest to vanilla site content; cheapest of the two new ones |

**Recommendation: take the towers now, and hold the skyhook as the one set-piece.**
A tether whose orbital end comes down when the ground end is cut is a thing the
player will describe to someone else, and **one of those is worth more than three
more dungeons.** Volume is not the goal here (see
`tile_augmentation_catalogue.md` §7.4: author few pools, deep).

## Two things this changes for whoever builds it

- ⚠️ **The mod's hostiles are `AncientsHostile`, not Imperial.** As shipped, the
  tower reads as a derelict, not as a garrison. **v1/v2 thin version: leave it** —
  a *disused* Imperial tower the Empire still counts as theirs is perfectly
  coherent, and it explains why a clan can get in at all. **When the pillar is
  built, re-cast the garrison to the Galactic Empire's pawn groups**, which is
  the same `pawnGroupMakers` work the Sith/stormtrooper roster already needs.
- **The Hutt commission is the natural home for the `salvage rumour` item**
  (`v1_quest_the_claim.md`). Same object, bigger job: the rumour you buy from the
  Cartel is sometimes a wreck on the sand, and sometimes a ladder.

## Where the pieces already are

| piece | state |
|---|---|
| the tower dungeon | **installed, one ModsConfig line** — `HaiLuan.SpaceTower`, dependency already active at load 108 |
| a readable quest-giving item | **BUILD is building it** (`ST_TowerMap` pattern: `CompProperties_Usable` + `UseEffectGiveQuest`, all Core classes) |
| the Hutt Cartel | faction 1 in the roster, `[v2]` for authoring |
| the Galactic Empire | owner's ruling 2026-08-13 — the ship's pursuer, `pawnGroupMakers` unbuilt |
| Imperial Heat gauge | **M4, not built — and this pillar no longer waits on it** |

---

## ⭐ SHAPE RULED — owner, 2026-08-13: finite backbone, repeatable sides

**A small number of AUTHORED towers that form an arc with a real ending, plus
randomly-offered ones for loot.**

**Why this shape and not the other two:**

- **A purely finite arc** has the most weight and then stops. When the last tower
  falls the best content in the campaign is over, and what remains is farming.
- **A purely repeatable job** never means anything. If the sky always refills,
  cutting it is a chore with a payout, and the player learns their actions do not
  land.
- **Both together is the only version where the story has a shape AND the player
  still has something to do afterwards.**

### How to keep them distinct, because this is where it goes wrong

| | backbone towers | side towers |
|---|---|---|
| **count** | **few. Three to five.** Authored, hand-placed, named | as many as the storyteller offers |
| **who offers it** | the **Hutt Cartel**, as a commission with a stated goal | ordinary rumour purchase / random offer |
| **what falls** | **Imperial reach in that region, permanently** | loot |
| **can it be repeated** | **no** | yes |
| **the player should feel** | *I am winning a war* | *I am making rent* |

⛔ **The failure mode to avoid: making the side towers feel like the backbone.**
If a random tower also shortens Imperial reach, the arc stops mattering. **Only
backbone towers move the world state.** Side towers pay in salvage and nothing
else — and that is not a lesser reward, it is the campaign's normal income.

⭐ **The ending must be real.** When the backbone is cut, the Empire's local
surface access is broken and the player should be *told* — a letter, a visible
change in raid pressure, the Hutts paying out and going quiet. **A finite arc
that ends without ceremony reads as content running out rather than a victory.**
