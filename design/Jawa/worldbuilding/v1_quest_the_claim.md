# "The Claim" — the v1 quest, specified

_VISION, 2026-08-13. **This is `V1_SCOPE.md` row 3.** The row reads *"One
`QuestScriptDef` that fires and resolves. Any premise."* — CREATE owns the build,
and "any premise" left the one part that is mine unwritten. This is the premise,
the player-facing text, and the shape. **CREATE picks the nodes; nothing here
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
the only on-brand premise that is *thin* in the `V1_SCOPE.md` sense, and it is not
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

Amounts are CREATE's call and should sit at the *low* end — this is the first
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

_Added 2026-08-13 after CREATE found the first build defaulted to
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

### ✅ MECHANISM ESTABLISHED — CREATE, 2026-08-13, three independent ways

**`everAcceptableInSpace` gates ACCEPTANCE by the player, not site placement.**
Set it `true` and the offer reaches the ship. Core's `Script_BanditCamp.xml`
already ships the exact pair this rule wants: `everAcceptableInSpace true` +
`GetMap canBeSpace true` for the offer, plain `QuestNode_GetSiteTile` for a
**ground** site. **Both layers hold together in one def.** So The Claim's shape
is buildable as specified, and it is built (`Jawa_TheClaim`, `5c14e26`).

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

⛔ **Do not blanket-patch every `QuestScriptDef` to `true` in the meantime.** Some
vanilla quests are nonsense in orbit (a refugee walks to your colony), and a
sweep that makes them offerable trades a silence for a stream of absurd offers —
which is the more visible failure of the two. **The default flips for quests we
author; adopted quests get judged one at a time.**

## What "done" means for row 3

`V1_SCOPE.md`'s gate is **seen working in-game once**. For this row that is:
**the quest appears in the quests tab, is acceptable, and reaches an end state** —
completed or expired, either counts. **It does not have to be balanced, and the
site does not have to be interesting.** Balance and site design are v2.

## Where this goes next — v2, and only noted so the thin version does not fight it

The same premise deepens without being rewritten: the rival clan becomes faction
11 (Indigenous Jawa Clans), the wreck becomes an Imperial one and raises Heat to
loot, and the reward becomes a droid chassis with a bolt still in it — which
hands the player the Free Droid Enclaves' moral problem the first time they use
it. **None of that is v1. All of it is reachable from this text unchanged.**
