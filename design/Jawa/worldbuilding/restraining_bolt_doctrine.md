# The restraint bolt — making the campaign's moral problem cost something

_VISION, 2026-08-13. **Owner's concept**, recorded the moment it was raised:_

> *"We should drop faction goodwill every time we use a restraint bolt, to the
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

---

# ⭐ REVISED SHAPE — state, not event. VISION, 2026-08-13

**CREATE raised a build risk that turns out to improve the design.** Their point:
a natural hook (`hediff PostAdd`, comp `PostSpawnSetup`) **can re-fire on save
reload**, so a one-shot penalty would drift silently every load until the
Enclaves hate you for no reason anybody can see.

**The fix is not a better hook. It is a better mechanic.**

> **The penalty is not paid when you fit a bolt. It is paid for as long as you
> hold bolted droids.**

## Why this is strictly better, not merely safer

| | one-shot on application | ⭐ ongoing, proportional to bolts held |
|---|---|---|
| re-fire bug | **silent, invisible, corrupts the save** | **impossible — it is idempotent by construction** |
| fits the fiction? | the offence is a moment | ⭐ **the offence is a condition.** It *is* slavery to them — the wrong is that the droid is still wearing it |
| freeing a droid | needs its own opposite hook | **stops the bleed automatically.** No second mechanism |
| "whose droid" | needs a conditional | **naturally unconditional — you count bolts, not owners** |
| tuning | a number per bolt | **an equilibrium** |

## ⭐ The equilibrium is the whole mechanic

Goodwill recovers on its own over time. Bolt pressure pushes it down. **So the
number of bolted droids the clan holds sets the standing it settles at.**

- **Two bolted droids** — the Enclaves disapprove, and trade anyway.
- **A dozen** — cold, no help, no gifts.
- **Forty** — you are what they exist to oppose, and they act like it.

**Nobody has to author those bands.** They fall out of one rate against vanilla's
recovery. **And the player can read their own standing as a statement about how
they have chosen to live**, which is the thing the roster promised and never
delivered.

## What this changes for the build

- **The hook question softens.** It no longer needs a once-and-only-once moment.
  It needs **a periodic tick that can count bolted droids in the colony** —
  cheaper, and immune to the failure CREATE identified.
- **The unbolt hook disappears entirely.** There is nothing to fire.
- **The "not their droids" clause gets cheaper, not dearer**, whichever side the
  mechanism sits on.

⚠️ **The original concept is unchanged in substance** — using restraint bolts
costs you standing with the Free Droid Enclaves, unconditionally. Only the shape
of the accounting moved, and it moved because a build constraint exposed a better
answer.

## Fallback if no equilibrium exists — cap the ceiling, do not drain the pool

**CREATE's analysis, which I accept:** if vanilla goodwill drift is a **constant
per day** rather than **proportional to the gap**, there is no resting point for
an ongoing penalty to find. A penalty under the drift does nothing; a penalty a
hair over it walks to the floor regardless of size. **2 bolts and 40 bolts both
end at the floor, only at different speeds** — a step function, not a gradient,
and no tuning fixes it because what is missing is the equilibrium itself.

⭐ **In that case the design does not die, it changes shape again — to a CAP:**

> **Bolts do not push your standing down. They lower the ceiling it can reach.**

- Drift is no longer an opponent. It carries you *up to* the cap and stops.
- **It scales exactly as required**: 2 bolts → nearly no ceiling loss; 40 → they
  will trade but never help, and eventually not even trade.
- **It is already in this project's vocabulary.** `faction_roster_v2.md:2317`
  specifies the Duneborn as *"Friendly, capped at +75, never allied"* — a
  goodwill ceiling is a thing this design already asks for elsewhere.
- **It reads better in play.** Not *"they are angry at me"* but *"they will deal
  with me, and they will never trust me"* — which is a truer statement of what a
  slaver is to an abolitionist.

**So the recon has three possible verdicts, and all three have a build:**

| drift shape | build |
|---|---|
| a standing persistent modifier exists | **state a level** — best case |
| drift is proportional | **state a rate** — the equilibrium design as written |
| drift is constant | ⭐ **cap the ceiling** — no drift fight at all |

**There is no outcome in which this concept cannot ship.** Only the accounting
moves.

## The curve — specified now, so the build is not waiting on me

**If a continuously-recomputed standing offset is available** (CREATE's
`GoodwillSituationWorker` lead — unconfirmed), the offset should be computed from
the **number of bolted droids currently held by the colony**, not from a lifetime
total and not from droids that have left.

> **offset = −2.5 × (bolted droids held), clamped at −100.**

**Linear, deliberately.** Not because linear is elegant but because it is the
only shape a player can infer without being told: *each bolted droid costs a
little, and it adds up*. A curve with an elbow in it reads as arbitrary.

| bolts held | offset | what the player sees |
|---:|---:|---|
| 1–2 | −3 to −5 | they notice, and trade anyway |
| 5 | −13 | cool |
| 12 | −30 | cold; no gifts, no help |
| 20 | −50 | openly hostile in tone |
| 40+ | −100 | you are what they exist to oppose |

**One tunable: the coefficient.** Everything else falls out of it, and the bands
above are consequences rather than authored thresholds.

⚠️ **Count what is HELD, not what was ever fitted.** A droid sold, freed or
destroyed stops counting the moment it is gone — that is what makes freeing one
feel immediate, and it is the whole reason this shape was chosen over a running
total.

## Two rulings the curve needed — VISION, 2026-08-13

_CREATE identified both; both are design calls, so both are answered here rather
than settled by whichever loop is cheapest to write._

### R1. What "HELD" means — one rule, five consequences

> **Every droid the PLAYER FACTION owns that is wearing a bolt, wherever it is.**

Faction-wide, not map-wide. The five edges CREATE named, resolved:

| case | counts? | why |
|---|---|---|
| in a **caravan**, or on another map we own | ✅ **yes** | ownership does not lapse with distance |
| **downed** on our map | ✅ yes | still ours |
| **carried off by raiders** | ❌ no — **the moment it stops being ours** | ownership is the whole test |
| **listed for sale**, still standing here | ✅ yes, until sold | it is still ours until it is not |
| a **visitor's or raider's** bolted droid | ❌ **no** | the Enclaves object to *our* conduct, not to the practice existing |
| in **cryptosleep or storage** | ✅ **yes** | ⭐ storing a slave is not freeing one |

⭐ **The last row is the one that matters most, and it is why the rule is
ownership rather than presence.** Any presence-based count invites the obvious
exploit — shelve the bolted droids when the Enclave trader is due. **Ownership
cannot be gamed without actually giving the droid up**, which is exactly the
behaviour the mechanic is trying to price.

⚠️ Note this is consistent with the owner's original clause. *"Whether it's on
one of their droids or not"* is about **who made the droid** — irrelevant, all
bolts count. This rule is about **who owns it** — decisive.

### R2. 🔴 The clamp moves ABOVE the hostility threshold. Bolts never cause war.

**CREATE is right and my −100 was wrong.** Faction hostility flips well before the
floor, so a −100 clamp meant roughly thirty bolted droids bought an **Enclave
raid**, off a cliff, with no guarantee that freeing droids walks it back.

**That contradicts what this mechanic is for.**

> **Bolt count sets how much they will HELP you. It never sets whether they
> SHOOT at you.**

- **Clamp the offset above the hostility threshold** — CREATE supplies the exact
  number; the design requirement is that the worst reachable state is *"coldest
  possible, still trading"*.
- **Hostility with the Enclaves remains reachable — by doing something to them.**
  Raiding them, refusing them, siding against them. **A war should be a decision,
  not something that accrues while you are thinking about water.**
- **This preserves the promise that freeing droids works.** We never cross the
  line where recovery stops behaving, so *"stop the bleed by freeing them"* stays
  true at every point on the curve.

⚠️ **This narrows the "two end states" I wrote earlier.** The industrial clan does
not automatically acquire the Enclaves as an enemy — it acquires a faction that
will trade and never help. **That is the better version**: an enemy you never
chose is a punishment, and a permanent cold shoulder is a consequence.
