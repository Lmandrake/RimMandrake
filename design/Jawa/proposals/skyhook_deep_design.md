<!-- status: REDESIGNED per the owner's 2026-09-02 sheet ruling (SKYHOOK_BESPIN_REDESIGN_1). The original space-elevator premise is dead; this file now describes repulsorlift high-altitude stations. Filename kept for link stability; the in-fiction rename below awaits the owner's word. -->
# Repulsor spires — high-altitude stations on a world where nothing hangs in the sky

✅ **"Repulsor Spires" RULED as the name** (owner, 2026-09-02, question card).

**The ruling that remade this doc (owner, 2026-09-02, verbatim):** *"Skyhooks
in this context can no longer be traditional space elevator type geostationary
objects due to the tidally locked nature. So instead these are going to have
to be very high altitude stations with a tapering tower beneath them, Bespin
style technology using repulsorlifts. This one should likely actually be over
the Rust Cathedral, an old research station turned into a cargo redistribution
center. High above the scorching temperature, the rare gases emitted from the
planet are being harvested industrially. But the stations automated
manufacturing has been taken over by the Empire. Each one has a ship handed
upon it with weapons capable of shooting anyone leaving the planet or
approaching. They cannot go into the atmosphere either, hence why the Utinni
remains outside their attack range."*

## 🔴 RULED — owner sitting, saved 2026-09-02 (review sheet, 9 rows, 6 cut)

Verdicts and the owner's notes, verbatim (frozen source: `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`; untouched rows keep their prefill — cut is the only destructive verdict):

| row | ruling | owner's note (verbatim) |
|---|---|---|
| shadow-line | v1→**v2** | (the redesign ruling quoted in full above) |
| ~~cargo-climbers~~ | ⛔ **CUT** (was v1) | makes no sense |
| ~~tether-static~~ | ⛔ **CUT** (was v2) | — |
| ~~pod-interception~~ | ⛔ **CUT** (was v1) | — |
| customs-heist | v2 | — |
| ~~vertical-society~~ | ⛔ **CUT** (was v2) | — |
| ~~the-cut~~ | ⛔ **CUT** (was v2) | — |
| ~~debris-corridor~~ → crash-salvage | dream→**v2** | Rather than a cut, this would be sabotaging the repulsorlift system, causing it to crash terribly and create this super rich treasure salvage area. |
| ~~cult-prophecy~~ | ⛔ **CUT** (was dream) | — |

Everything here is **v2** — no spire content ships in v1.

## 1. What a spire is

A very-high-altitude station held up by repulsorlifts, Bespin-style, with a
**tapering tower beneath it** reaching down toward the surface — not a cable
to orbit, not geostationary, nothing hanging from the sky. It sits high above
the scorching surface temperature, where the planet's rare emitted gases are
harvested industrially. Physics stays honest: on a tidally-locked world there
is no useful geostationary point, so the Empire (and whoever built these
before them) holds altitude the Star Wars way — powered lift, forever, at
industrial cost. That cost is the design's engine: a spire is valuable
exactly because keeping it up is expensive, and killable exactly because its
lift can fail (§4).

On a sun-fixed world a spire still casts **one eternal shadow band** on the
surface below — the old doc's best image survives the redesign: a fixed strip
of shade and cooled ground under each station, inhabited by whoever profits
from shade that didn't cost a mountain.

## 2. The first spire — over the Rust Cathedral

An old research station turned **cargo redistribution center**. Its automated
manufacturing has been **taken over by the Empire**. Docked upon it sits a
ship whose weapons can hit anything **leaving the planet or approaching it**
— but the ship cannot enter the atmosphere, which is why the Utinni survives
by staying low: the campaign's standing in-fiction answer for why the player
flies a gravship around a planet the Empire nominally blockades. The gas
harvest and the seized manufacturing give it an economy worth robbing; the
Rust Cathedral below gives it a ground anchor already authored on the map.

Register guard: the blockade ship is scenery-with-teeth, not a countdown — it
explains the campaign's shape (you fly LOW) rather than adding a clock.

## 3. The customs heist (v2)

The one interaction row that survived unchanged: cargo redistributed through
the spire sits in a customs yard under real Imperial security, so lifting it
is a proper heist against the ownership fabric — witnesses, propagation,
faction-record consequence (`ownership_settlement_spec.md` per-faction
security profiles; Empire reads "high"). Claims ride the goods: bulk
requisition steel decays to "just steel" in days, a numbered Imperial part
never fully decays and travels hot. How the clan gets UP there is part of the
heist design and is deliberately unresolved in this pass (the tower, a cargo
lifter, an invitation, a lie).

## 4. The crash — sabotage the lift, then mine the grave (v2)

The owner's redesign of the old debris-corridor row: **sabotaging the
repulsorlift system crashes the spire terribly**, and the wreck becomes a
**super-rich treasure salvage area**. Same authored-world discipline as every
other one-way door on Ash'karr: the crash field is a pre-authored alternate
state (tiles reserved beside the Rust Cathedral, inert until the arc fires),
revealed by a scripted world-state flip — never generated. Seized Imperial
manufacturing, gas-harvest plant, the docked ship's carcass: the richest
salvage site on the planet, earned by destroying the thing that made it, and
a permanent scar every player who takes this path shares, because the world
is frozen and this is authored.

## ⛔ Cut, and staying visible so nobody rebuilds them from the evidence

| dead row | what it was | why it cannot return |
|---|---|---|
| cargo-climbers | scheduled pods riding a cable, arrival-thunder events | "makes no sense" — there is no cable |
| tether-static | lightning weather geofenced to a cable | no cable |
| pod-interception | shooting down descending pods for scattered cargo | no pods on a line |
| vertical-society | the rigger caste, tension shrines, climber yards | the station is automated + Imperial; the working-caste premise died with the cable |
| the-cut | severing the tether as a campaign set-piece | replaced by §4's repulsorlift sabotage — the crash IS the set-piece now |
| cult-prophecy | riggers reading the cable's hum as divination | no cable, no hum, no riggers |

The old `HaiLuan.SpaceTower` reskin idea rode the v1 slice and dies with it —
nothing spire-shaped ships in v1.

## Build ladder — all v2

1. The spire as authored world presence: visible over the Rust Cathedral,
   the eternal shadow band beneath, the low-flight blockade fiction stated
   in-game (a letter or codex entry, not a mechanic).
2. The customs heist riding the ownership fabric.
3. The sabotage arc and the pre-authored crash-salvage field.

Supersedes: this doc's own prior text (git holds it); check
`design/Jawa/worldbuilding/orbital_towers_and_the_sky_ladder.md` for
space-elevator language before building — it predates this ruling.
