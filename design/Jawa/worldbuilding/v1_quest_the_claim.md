# "The Claim" — the v1 quest, specified

_A retired seat, 2026-08-13. **This is row 3.** The row reads *"One
`QuestScriptDef` that fires and resolves. Any premise."* — BUILD owns the build,
and "any premise" left the one part that is mine unwritten. This is the premise,
the player-facing text, and the shape. **BUILD picks the nodes; nothing here
names an XML field it has not been told to treat as unverified.**_

---

## Why this premise and not a better one

**Every richer idea I had depends on a system v1 does not have.** Written down so
nobody re-proposes them and so the choice does not look timid:

| rejected premise | what it needs | status |
|---|---|---|
| A Homestead well fails; sell them water | water and thirst doctrine | **v2, zero implementation** |
| Free a bolted droid for the Enclaves | Free Droid Enclaves faction | **v2, unbuilt** |
| The Directorate demands tribute | a hostile Directorate | **the antagonist does not exist yet** (V6/V7) |
| Rival clan bounty | faction relations matrix | **v2** |

**"The Claim" needs a world tile, a stash, a timer, and text.** That is all. It is
the only on-brand premise that is *thin* in the v1 sense, and it is not
a placeholder — it is the campaign's thesis compressed into one quest.

## The premise

> **Something fell. Jawa law says it belongs to whoever plants a claim-marker on
> it first. Someone else is already walking.**

The player is offered a wreck on a nearby tile. They travel, they take what is in
it, they come home. If they are slow, another clan gets there first and the offer
closes — **nothing is lost but the opportunity**, which is the correct stake for
the first authored quest in the game.

**What it teaches, and this is the whole reason it is worth authoring:** in this
campaign you do not get rich by producing. You get rich by *arriving first at
something broken*. A player who runs this once has learned the loop.

## The shape

| beat | fiction layer | engine layer |
|---|---|---|
| **Offer** | A trader, a passing caravan, or nothing at all — rumour is enough | quest fires on the ordinary opportunity cadence; no faction required |
| **Site** | The wreck, on a tile within easy caravan range | a site with a stash; **ground layer, not orbit** |
| **Opposition** | Scavengers already picking it over — *not* a faction we have designed | thin. Whatever the engine gives cheapest. **This is not the fight the campaign is about** |
| **Reward** | Salvage: metal, components, and **one thing that reads as progress** | see the reward rule below |
| **Expiry** | A rival clan plants their marker | quest expires; no penalty, no goodwill loss |

⚠️ **Two layers, said explicitly because conflating them costs real work:** "a
rival clan" is a *story fact* and must have **no `FactionDef` behind it** in v1.
It is a line of text explaining why the timer exists. Do not author a faction to
justify a countdown.

### The reward rule — one line, and it matters more than the amounts

**The haul must contain exactly one item the player cannot yet make.** Not a
better version of something they have — a *category* they have not opened.
Components, an advanced component, a mech corpse, a droid chassis if one is
buildable by then. **Bulk steel is the texture; the one item is the memory.** A
quest whose entire reward is 400 steel is a resource trickle, and the player will
not remember running it.

Amounts are BUILD's call and should sit at the *low* end — this is the first
quest, not a windfall, and v1 has no economy tuning behind it.

## The text the player reads

**Write these as given.** The strings are the only part of a thin quest the
player actually experiences, so they are the part that decides whether v1 reads as
*our* campaign or as vanilla with a reskin.

**Name:** `The Claim`

**Offer:**

> Something came down past the ridge two nights ago — big enough to see, far
> enough that nobody has walked out to it yet.
>
> Nobody who will admit to it.
>
> Clan law is old and short: the wreck belongs to whoever plants a marker on it.
> Not to whoever saw it, and not to whoever needs it. **Whoever gets there.**

**Accepted:**

> The marker is cut and stowed. Now it is a walking problem.

**Expired:**

> Someone else's marker is standing in it. By the time your people crest the
> ridge there is nothing left worth the walk back — stripped to the frame, and
> the frame is spoken for.
>
> They were closer. That is the whole of it.

**Completed:**

> The marker stands. What was in the hull is on the sled and moving.

⚠️ **Register note for whoever edits these:** Jawa voice here is *flat, short,
and unsentimental about property*. No exclamation, no adventure-speak, no
"brave colonists". The clan is not excited; the clan is on time.

## 🔴 Standing design rule for EVERY quest we author — not just this one

_Added 2026-08-13 after a retired seat found the first build defaulted to
`everAcceptableInSpace` unset, i.e. **not offerable while the colony is aboard the
ship**._

> **A quest that cannot be offered while the clan is aboard the gravship is
> broken for this campaign, whatever else it does.**

The premise is *a clan that lives on a ship*. If our quests go quiet the moment
the player boards, then the ship — the thing the whole campaign is built around —
becomes the place where the game stops talking to you. **That is the single worst
thing an authored quest can do here**, and it would be invisible in testing
because a ground colony sees the quest fire perfectly.

**So: our quests must reach the player wherever the ship is.** The two layers,
kept apart on purpose:

- **The OFFER must reach a colony in space or aboard the ship.** Always. No
  exceptions in this campaign.
- **The SITE may be pinned to the ground layer** — that is a separate field and a
  separate decision, and for "The Claim" the site *is* ground. A wreck on a tile
  you walk to is the point.

### ✅ MECHANISM ESTABLISHED — a retired seat, 2026-08-13, three independent ways

**`everAcceptableInSpace` gates ACCEPTANCE by the player, not site placement.**
Set it `true` and the offer reaches the ship. Core's `Script_BanditCamp.xml`
already ships the exact pair this rule wants: `everAcceptableInSpace true` +
`GetMap canBeSpace true` for the offer, plain `QuestNode_GetSiteTile` for a
**ground** site. **Both layers hold together in one def.** So The Claim's shape
is buildable as specified, and it is built (`Jawa_TheClaim`, `47733f8` — the original
hash 5c14e26 is unresolvable: it was written between the history bundle being cut and the
2026-08-13 re-init, so it survives in neither, and `47733f8` re-lands the same def).

### ✅ REFINED 2026-08-13 — read at IL level, and the severity drops

**The quest is still OFFERED in space. What is blocked is the Accept button.**
Measured from `Assembly-CSharp.dll` metadata: `QuestGen.Generate` attaches
`AcceptanceRequirementNotSpace` when `everAcceptableInSpace` is false, and its
string is Core's `QuestNotSpace` — *"cannot accept in space"*. The player sees
the quest and cannot take it.

**And the ordinary storyteller path never reaches the offering filter at all.**
`GiveQuest_Random` is tagged `targetTags World`, and `World.Tile` is literally
`PlanetTile::Invalid`, so both `CanQuestOccurOnTile` overloads return true on
their first branch. **The layer checks are dead code on that path.**

**`autoAccept` suppresses the whole thing** — a quest that auto-accepts skips
both the filter and the accept requirement.

⇒ **This is friction in orbit, not silence, and it is legible to the player.**
It is also defensible fiction — *you come down to take work* — which is why the
ruling below is "leave vanilla alone", not "patch 200 defs".

### 🔴 The campaign-wide half — and the one number nobody has

**Core's own `OpportunitySite_ItemStash` omits the field, and so do most vanilla
quests.** This was never a mod problem: **vanilla's quest offering goes quiet
while the colony is on a space map**, and no quest we adopt is safe by default.

⚠️ **Before anyone sweeps 200 vanilla quest defs, settle the impact — nobody has
measured it.** The field only bites while the colony's map *is a space map*. A
gravship landed on a surface tile is an ordinary map and quests flow normally.
So the real question is:

> **How much of this campaign is actually spent on the Orbit layer?**

- If the answer is *"transit and orbital sites only"* — the defect is an
  annoyance, and fixing **our authored quests** is the whole fix.
- If the answer is *"the clan lives in orbit for stretches"* — it is a campaign
  stopper and needs a blanket patch.

**Nobody owns that question. It is a play-pattern question, so it is mine**, and
it is not answerable offline — it needs the gravship in the air.

⛔ **RULED: leave vanilla alone. Do not sweep.** Three reasons, now that the
mechanism is measured rather than guessed:

1. **It is legible, not silent.** The player reads *"cannot accept in space"* on
   the button. Nothing disappears; nothing is mysterious.
2. **It is good fiction as-is.** A clan in orbit cannot take a job on the
   ground. *Come down to do business* is a rule the setting would have invented.
3. **A blanket `true` costs more than it buys** — a refugee walking to your
   colony in orbit is a more visible failure than a greyed-out button.

**The default flips only for quests WE author, and only where being takeable
from orbit is the point.** Adopted quests are judged one at a time.

## What "done" means for row 3

The gate is **seen working in-game once**. For this row that is:
**the quest appears in the quests tab, is acceptable, and reaches an end state** —
completed or expired, either counts. **It does not have to be balanced, and the
site does not have to be interesting.** Balance and site design are v2.

## Where this goes next — v2, and only noted so the thin version does not fight it

The same premise deepens without being rewritten: the rival clan becomes faction
11 (Jawa Trade Moot), the wreck becomes an Imperial one and raises Heat to
loot, and the reward becomes a droid chassis with a bolt still in it — which
hands the player the Free Droid Enclaves' moral problem the first time they use
it. **None of that is v1. All of it is reachable from this text unchanged.**

---

# The rumour item — ruled 2026-08-13, a retired seat

_A retired seat found the pattern in Space Tower's `ST_TowerMap`: a **tradeable item that
hands you the quest when you read it** — `CompProperties_Usable` +
`UseEffectDestroySelf` + `UseEffectGiveQuest`, all Core classes. They asked
whether it stays a bare test object or becomes fiction. **It becomes fiction**,
and here is the whole of it._

## Why it is worth being real

**It converts "wait for the storyteller" into "the clan buys its own next job."**
That is a *decision the player makes*, and decisions are the thing this campaign
is thinnest on. A quest that arrives is content; a quest you paid for is a
choice, and the player remembers the second one.

**And it is Jawa to the bone.** The clan does not only trade in salvage — it
trades in *knowing where the salvage is*. Information is merchandise here. That
is a characterisation we have written down and never once made mechanical.

## The item

**Label: `salvage rumour`.** Physically a scrap — nav data on a plate offcut,
coordinates scratched by someone who did not live to use them. Not a map, not a
datapad. **Cheap-looking, and worth more than it looks**, which is the clan's
entire self-image.

**Reading it consumes it and offers the quest.** One rumour, one job.

### Where it comes from — two lanes, and both must exist

| lane | source | what it costs | what it teaches |
|---|---|---|---|
| **Bought** ⭐ | **The Hutt Cartel**, primarily | silver, at a price that stings early | the fast lane: you can *buy* your next opportunity |
| **Found** | wreck loot, raider inventories, ancient sites | nothing but the risk you already took | a poor clan is never locked out |

⛔ **Do not make it purchase-only.** A clan that cannot afford rumours would
simply stop receiving content, and the failure would look like the game being
empty rather than the player being broke. **Buying is the fast lane, not the
only lane.**

**Why the Hutts and nobody else.** They are the faction that knows where
everything fell and will sell you anything including your own location — the
roster already says the best market is the one that might betray you, and it has
never been mechanical. **This makes it mechanical for the price of one trader
stock entry.** The Homestead are farmers and do not know; the Empire would not
tell you; the Deepwater Compact deals in water, not coordinates.

## v1 vs v2, stated so nobody over-builds

- **v1 — build the bare object.** It exists, it is spawnable, reading it fires
  The Claim. **That is the whole v1 requirement**, and its real job is that the
  gate ("seen working in-game once") stops depending on waiting for the
  storyteller cadence.
- **v2 — put it in Hutt trader stock and in wreck loot.** One line each. The
  fiction above is already written so that step is a stock entry, not a redesign.
