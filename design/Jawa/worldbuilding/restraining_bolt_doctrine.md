# The restraining bolt — making the campaign's moral problem cost something

_VISION, 2026-08-13. **Owner's concept**, recorded the moment it was raised:_

> *"We should drop faction goodwill every time we use a restraining bolt, to the
> independent droid faction, whether it's on one of their droids or not. It's
> slavery to them."*

---

## Why this is the right mechanic

**The roster has claimed this for months and never made it true.**
`faction_roster_v2.md:2345` reads: *"Jawas acquire droids using restraining
bolts, which the Free Droid Enclaves define as slavery. The player's core
progression loop is the Enclave's central atrocity. This is deliberate and left
unresolved."*

**It was unresolved because nothing implemented it.** A moral problem the player
never pays for is set dressing. This makes it a price.

⭐ **And the detail that makes it work is "whether it's on one of their droids or
not."** That is not a theft penalty — it is a **principle**. The Enclaves are not
protecting property, they are objecting to an act. **That single clause
characterises the faction better than any amount of prose has managed**, and it
is the reason the mechanic reads as conscience rather than bookkeeping.

## ⭐ The structural prize: a snowball brake that comes from fiction

**Droid labour is the player's economic engine and their water answer** — droids
do not drink, which is the whole Jawa advantage (`water_doctrine.md`). So the
more the clan wins, the more bolts it fits, and **the penalty scales itself.**

**This is an anti-exponential brake that nobody had to design as a nerf.** It
costs no balance tuning, it cannot be gamed, and it arises entirely from who
these people are. That is the best kind of mechanic this project can get.

## The four decisions it needs

### 1. Small per bolt, unbounded in aggregate

**A single bolt should barely register. Forty should make you their enemy.**
Volume does the work, so the player who dabbles is fine and the player who builds
an industry has made a choice. **Do not add a floor** — becoming the Enclaves'
enemy must be genuinely reachable, or the mechanic is theatre.

⛔ **Do not make it punishing enough to discourage droids.** Droid labour is the
campaign's engine; a penalty that stops the player using it breaks the premise
instead of complicating it.

### 2. They always know

**No detection mechanic. No line of sight. Droids talk to droids.**

It is simpler, it is cheaper, and **it is much more unsettling** — the player
learns that somewhere a network is counting. Any "were you seen?" system would
turn a moral cost into a stealth minigame, which is the wrong genre.

### 3. Removing a bolt pays it back

**Bolt = minus. Unbolt = plus.** That is the entire moral system in two numbers,
and it is what keeps the Enclaves **negotiable**, which pillar 5 requires — only
the Empire is permanently un-negotiable.

**The player should be able to buy their way back by freeing droids**, and it
should be expensive, because it costs them the labour they fitted the bolt for in
the first place. **A redemption you can afford easily is not one.**

### 4. It is a branch, not a fail state

Two coherent end states, and **both must be playable**:

- **The industrial clan.** Bolts everywhere, water security absolute, and the
  Enclaves are an enemy who raid you with things you cannot easily kill.
- **The clan that stopped.** Fewer droids, more thirst, more dependence on
  trade — and an ally nobody else on the planet has.

⭐ **The second path must be genuinely viable or the choice is fake.** That means
water has to be solvable without droids, which puts a real requirement on the
purification and trade routes in `water_doctrine.md`.

## What this does NOT do

- ⛔ **It does not make bolts illegal or blocked.** No prohibition, no warning
  dialog. The player is allowed to do it and simply has to live in a world where
  someone objects.
- ⛔ **It does not affect any other faction.** The Hutts do not care. The Empire
  does not care. **Only the Enclaves**, and their isolation on this point is
  characterisation.

## Feasibility — the one build question

**Something has to fire when a bolt is applied.** That is a hook, and it is
almost certainly C#: a Harmony patch on whatever applies the bolt, calling a
goodwill change against the Enclave faction.

**Before anyone estimates this, establish which mod actually supplies restraining
bolts in our stack, and whether the application is a recipe, a comp, an ability
or an apparel item.** The shape of that answer decides whether this is twenty
lines or a project. **Unverified today** — and it is the only thing standing
between this concept and a build spec.

`[v2]`. The Enclaves are unbuilt (`V1_SCOPE.md` names them explicitly as
deferred), so this lands with them.
