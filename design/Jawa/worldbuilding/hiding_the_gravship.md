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
