# Hiding the gravship — the third verb

_VISION, 2026-08-13. **Owner's concept**, recorded and developed the hour it was
raised:_

> *"'Hiding' your gravship from pursuit is a big deal in this campaign, and
> allowing them to under the (admittedly very small) bodies of water or into the
> permanently dark terrain is pretty cool! In fact, maybe we should combine both
> of those concepts…"*

**Mod under evaluation: GravTide** — subscribed, evaluation running. Everything
below is design and does not depend on which mod supplies the mechanism.

---

## Why this is the strongest idea on the register

**The pursuit is the campaign's spine, and the player currently has exactly two
verbs against it: RUN or FIGHT.** Two verbs is a thin spine, and neither is a
Jawa verb. Jawas are not fast and they are not strong. **They are small and
overlooked, and being overlooked is the thing they are actually good at.**

⭐ **Hide is the third verb, and it is the one the fiction has been asking for
since the beginning.** A clan that survives by not being worth finding is the
whole characterisation, and nothing mechanical has ever expressed it.

## The two media, and why combining them is right

| | **under water** | **permanent dark** |
|---|---|---|
| conceals from | anything looking down | anything looking with eyes |
| where it exists | the handful of polar seas, marshes and lakes | caverns, deep canyons, polar night |
| who owns it | 🔴 **the Aquifer League holds every natural water tile** | nobody — it is worthless ground |
| what it costs you | **a diplomatic price**, every time | **isolation** |

⭐ **The combined version is the good one: a drowned cavern under polar night.**
Dark and submerged at once, and — because of the geography already specified in
`faction_world_spec.md` §4 — **that is the furthest possible place from
everything the clan needs.** No salvage. No sun. No trade. Cold enough to hurt a
species evolved for the dune sea.

## 🔴 The design rule that makes it a decision instead of a button

> **Hiding must cost the thing the campaign is about — salvage and progress —
> not hit points.**

A hiding place that is also a good base is not a decision, it is a strategy you
adopt once and never revisit. **The hiding place must be poor.** The player
should sit there watching the heat bleed off and feel the weeks they are not
earning.

⛔ **And it must not be permanent.** If you can hide forever the pursuit stops
mattering and the spine is gone. Something has to erode while you are down there
— stores, mood, the water itself, or the Empire narrowing its search.

## The rhythm this creates, which is the real prize

**Raid → get hot → go dark and cold → wait it out → come back up.**

RimWorld campaigns badly want a rhythm and this one has never had one. It also
gives the map a *purpose beyond resources*: the polar dark stops being empty
terrain and becomes **the place you run to**, which is exactly the "interesting
tiles cluster in intriguing patterns" the owner asked for — some clusters are
rich, and one kind is *safe and poor*.

## How it meshes with what is already decided

- **The Aquifer League becomes load-bearing.** They hold the water; hiding under
  it either costs goodwill or is stolen. **This turns the League from a trade
  partner into a gatekeeper**, which is a much better use of a faction that
  cannot raid you.
- **It pairs with the sky ladder** (`orbital_towers_and_the_sky_ladder.md`). Cut
  the Empire's towers and their reach shortens — so **the two anti-pursuit
  strategies are opposites**: hide and stay poor, or go up and hurt them and
  become hotter still. **A player choosing between those is a campaign.**
- **It gives Imperial Heat somewhere to go.** The gauge is unbuilt (M4) and had
  no decay mechanism specified. **Hiding is the decay mechanism.**
- **Water doctrine gets a second use.** Water was scarcity and economy; now it is
  also cover.

## What is v1, v2, and what is not ours

- **v1: nothing.** No part of this ships in the alpha.
- **v2: the whole loop**, and it wants the Heat gauge to exist first.
- ⚠️ **The mechanism is a mod question, not a design question.** Whether GravTide
  supplies submersion, whether anything in the stack supplies permanently dark
  terrain, and whether either can suppress a pursuit are being measured. **If the
  mods do not support it, this concept is still sound and simply waits** — do not
  bend the design to fit a mod that turns out not to do this.

## The one thing to check before building it

**Can the pursuit actually be suppressed?** The pursuit is a scenario part with
hardcoded behaviour; *Ruthless Faction Pursuit* redirects **who** pursues, which
is not the same as pausing **whether**. **If nothing can pause it, hiding has to
be expressed some other way** — fewer raid triggers, a longer timer, a Heat gauge
that only decays out of sight. That is a real fork and it is the first thing to
answer.

---

# ⭐ The deep — underwater as a hostile environment

_Owner, 2026-08-13, extending the concept:_

> *"I kinda love that we might be able to go down into the VERY SCARY Star Wars
> underwater environment. A whole new class of problematic monsters… and it
> should have the same issues as vacuum for breathing."*

## The single best thing about this idea

⭐ **Breathing-as-vacuum means we get the environment for free, because the ship
already has to be airtight for space.** Odyssey's vacuum rules — sealed rooms,
breaches, suits, pawns who die in the open — are already in the stack and already
apply to a gravship. **Point them at water and the same hull discipline serves
two environments.**

**And it makes the ship's condition matter.** Right now a hull breach is a
cosmetic problem on the ground. Under water it is the problem. The deck plan
stops being decoration and becomes the thing keeping everyone alive.

## The geometry that makes small water interesting

The owner called the planet's water *"admittedly very small"*. **That is only true
across the surface.** The fix is one line of setting physics:

> **The water bodies are narrow and DEEP. A small surface, a long way down.**

A lake you can walk around in an hour and cannot see the bottom of is far more
frightening than an ocean, and it costs nothing to specify. **The map does not
need to be wide to be deep.**

## What lives down there

**Star Wars has better underwater monsters than almost any setting**, and this
world's aquatic species are already in the roster — the Aquifer League is Selkath,
Mon Calamari, Quarren and Gungan. **The natives already exist; only the fauna is
missing.** Canon register to draw from: firaxa-class sharks under the Selkath
seas, and the Naboo lineage of things that eat each other in sequence.

**Design discipline: few, large and named.** Underwater is not a place for a
bestiary — it is a place for **two or three things nobody wants to meet**, each
one an event. `Alien_Bestiary.md` is the home for them when they are specified.

## ⭐ How this closes the hiding loop properly

The hiding rule above said *hiding must cost progress, not hit points*. **The deep
improves on that: it costs progress AND it is dangerous.**

- **It explains why the Empire does not simply follow you down.** The best kind
  of safety is somewhere the enemy could reach and chooses not to.
- **It gives the Aquifer League its real power.** They do not merely own the
  water — **they own the one place the rest of the galaxy cannot follow them.**
  Every other faction's leverage stops at the shoreline.
- **It makes hiding a gamble rather than a wait.** You are not safe down there.
  You are *unfound*, which is different, and something enormous is aware of you.

## Scope discipline — this is the part that could eat the project

⛔ **Not v1. Not early v2. And ONE place, not a new global layer.**

A whole environment class with its own physics, fauna, gear and failure modes is
exactly the kind of thing that sounds cheap because the pieces exist. **The
disciplined version is a single authored deep site** — one drowned cavern, one
descent, two monsters — proving the loop. If it lands, it grows.

**Feasibility, in order:** (1) can vacuum rules be applied to a water map at all,
(2) does anything in the stack render or generate an underwater map, (3) can the
pursuit be suppressed while submerged. **Question 1 is the one that decides
whether this is cheap or enormous**, and it is under investigation.

---

# 🔴 THE CHEAP ROUTE — owner, 2026-08-13, and it changes the whole proposition

> *"There's a pitch black Alpha Biomes biome already that is very alien and
> strange and almost perfect to pretend is at the bottom of the ocean, making
> this mod just inspirational to allow us to 'go to that biome' when we try to
> land on water instead."*

⭐ **This is the version to build.** Everything above described an environment we
would have to construct. This describes a **redirect**:

> **Landing on a water tile takes you to the dark biome.**

**We do not build the ocean floor. We arrive at one that already exists.**

## What that buys, itemised

| we thought we needed | what we actually need |
|---|---|
| an underwater map type | **none** — an existing biome generates it |
| underwater rendering | **none** |
| a new fauna set — "problematic monsters" | ⭐ **the biome ships its own**, and Alpha's creatures read as genuinely *not from here*, which is exactly right for the abyss |
| flora, terrain, weather, temperature | **all included** |
| vacuum/breathing plumbing | ⚠️ **now OPTIONAL** — a layer we may add for tension, not a prerequisite |

**GravTide drops from dependency to inspiration.** Whatever it does, the concept
no longer waits on it. **Evaluate it on its own merits, not as a blocker.**

## The one thing we do have to build

**The redirect itself: water tile + land → that biome's map.** That is the whole
mechanism, and it is the only feasibility question left that matters.
Under investigation: whether anything in the stack already lets a water tile
generate a playable map, and whether a biome can be forced for a given landing.

## The fiction, which now writes itself

**You do not fly to the dark place. You go down into it.** The descent is the
transition, and the strangeness on arrival is the point: **the clan expected mud
and found something alien and lit by nothing.** Nobody down there is Star Wars,
which is precisely why it is frightening — every other threat on this planet has
a name and a faction and a price.

⚠️ **One coherence cost, accepted with eyes open.** Alpha Biomes' dark biome was
authored for its own setting, so some of its flora and creatures will not read as
oceanic. **Do not repaint the biome** — that is the expensive path we just
escaped. **Cast it instead**: the clan calls it the deep, and what the clan calls
things is what the campaign calls them.

## Where this now sits

- **Feasibility is a single question**, not a research programme.
- **Cost has collapsed** from "a new environment class" to "a landing redirect".
- **Still v2** — but it moved from *aspirational* to *plausible* in one sentence,
  which is the best kind of design note to receive.
