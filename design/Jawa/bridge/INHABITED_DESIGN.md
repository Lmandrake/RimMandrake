# `Inhabited` — somebody lives here

_An independent RimWorld mod. Designed 2026-08-19 by DECIDE with the owner, in Q/A._

> **Owner's scope ruling: v1 for the DESIGN, v2 for the code.** The templates, casts and
> characters are authored NOW, so the hand-built world is built *as though the people will
> arrive*. The code that animates them is v2. ⛔ Do not file BUILD items for the code.

**The problem it solves.** RimWorld's world map is a set of props. A settlement is a name
and a loot table; a visitor is a timer with a psylink. Nothing on the planet is anybody's
home. `Inhabited` makes places have people, gives those people lives and names, and lets
the world remember what you did to them.

⭐ **The one-line test for every decision in here:** *would a player say "wasn't that guy
working a refinery a while ago?"* If a choice makes that sentence more likely, take it.

---

# 1. The model — four nouns

| noun | what it is |
|---|---|
| **PLACE** | a structure on a tile. Comes from the tile-mutator / landmark layer |
| **CAST** | the people who belong to it. A **persistent roster of real pawns**, never a spawn list |
| **ROUTE** | what the cast does across a day — barracks, worksite, patrol, home |
| **FATE** | what, if anything, could end them. ⭐ **Default: nothing. They live here.** |

The owner's worked example: a **refinery PLACE**, a **crew CAST** of foreman, guards, a
trader and drudges, a **ROUTE** of barracks → refinery → barracks, and a **FATE** of *flee
if threatened, and never come back*.

⭐ **Trade is a ROLE, not a template.** The oil sellers are a refinery cast that contains
someone who deals. This single reframe collapses a whole class of near-duplicate templates.

## 1.1 This supersedes the 36-template catalogue

`LIVING_NPC_TEMPLATES.md` lists 36 templates. Under this model most are not templates —
"Peasant Hearth", "Farmstead" and "Waystation Fort" are one PLACE+CAST+ROUTE+FATE machine
with different parameters. ⇒ **Expect ~6–8 real archetypes plus a parameter table.** A
smaller thing to build and a larger thing to vary. The 36 remain valid as a *content
list* — they are the places we want — but not as a class list.

## 1.2 FATE — flight is caused, never scheduled

⛔ **The `LordJob_TradeWithColony` visitor arc is NOT the template.** It is one FATE among
several, and the rarest. Residents are the rule.

| FATE | cause |
|---|---|
| ⭐ **Resident** | nothing ends them. **The default and the great majority** |
| **Flee — threatened** | the player menaced them. 🔴 **Goodwill drops with it** |
| **Flee — arrival** | ⭐ a gravship coming out of the sky is enough. Hostile casts may break on sight. *The ship is a presence in the world, not transport* |
| **Flee — starved out** | the larder empties, they raid the player's stores, **then** they go |
| **Transient** | a genuine caravan passing through. The rare case |

🔴 **Flight costs goodwill and there is no cheap apology.** Read off the assembly
2026-08-19: `FactionRelation.cs:28` hostile at `goodwill <= -75`; `:33` ally at `>= 75`;
`:38` **hostility ENDS only at 0**, so a faction driven hostile must be gifted back 75
points. Frightening a crew off their own refinery is not something a present fixes.

---

# 2. PLACE — and why this is the same system as tile mutators

The owner asked for *"a way to assign intelligent pawns to animate and embody the tile
augmenting buildings and structures we add."* That is not a new mechanism. **It is the
mutator layer plus a cast**, and every link is shipped:

```
TileMutatorDef.extraGenSteps  ->  our GenStep  ->  LordMaker.MakeNewLord(faction, job, map, pawns)
       (the PLACE)                 (the bridge)              (the CAST)
```

Verified 2026-08-19: `extraGenSteps` invokes arbitrary `GenStepDef`s, and seven shipped
GenSteps already call `MakeNewLord` in exactly this shape — `GenStep_SitePawns`,
`GenStep_WorkSitePawns`, `GenStep_SettlementPawnsLoot`, `GenStep_OrbitalMechhive`,
`GenStep_GravshipWreckage`, `GenStep_SleepingMechanoids`, `GenStep_InsectLairCave`.

⇒ **The mutator places the set; `Inhabited` places the company.** The two things the owner
asked for are two halves of one system.

## 2.1 A place must be able to feed its cast

🔴 **NPCs cannot farm. Three independent shipped walls**, none of them worth fighting:
1. `JobGiver_Work.PawnCanUseWorkGiver` requires `nonColonistsCanDo`; exactly **7**
   WorkGiverDefs carry it and **all seven are construction or repair**.
2. `WorkGiver_GrowerHarvest.ShouldSkip` opens `if (pawn.GetLord() != null) return true;` —
   **any lorded pawn skips harvest, even a colonist.**
3. `WorkGiver_Grower` sources cells from player-only zone data.

⇒ **Sustenance is PRESENT, not produced** — and the owner ruled it must be **visible,
stealable and destroyable**: *"I like that their food stocks are exposed. Very realistic."*
A refinery has a mess and a paste vat, a farmstead a granary, a Tusken camp a herd.

⭐ **This converts the limitation into content.** Burn the granary and the cast does not
starve to death in front of the player — **they leave**. That is FATE:flee firing for a
cause the player created, with no new code.

⚠️ **The forbid-flag hole is not a bug to fix — it is the warning shot.** `Thing.IsForbidden`
returns false for any non-player faction, so a hungry cast **will** raid the colony's
stockpile. Under this design that is the audible click before they go.

---

# 3. Persistence — the roster is real people, held in the world

**`WorldObject_Inhabited`, modelled on `Caravan`.** Not a novel class: `Caravan` is
`WorldObject, IThingHolder, IIncidentTarget, ILoadReferenceable, ITrader` carrying a real
`ThingOwner<Pawn> pawns`, with `CaravanEnterMapUtility` / `CaravanExitMapUtility` as the
bridge between people-held-in-the-world and people-standing-on-a-map. We are copying a
settled pattern, not inventing a persistence layer.

| the object holds | why |
|---|---|
| `ThingOwner<Pawn> roster` | ⭐ **actual `Pawn` objects.** Names, skills, relationships, scars, memories — all survive with no serialisation of ours |
| `placeDef` + `castDef` | archetype and parameters |
| `state` | inhabited · abandoned · looted · squatted |
| `stock` | trade goods **and the larder** |
| faction | inherited from `WorldObject` |

```
player arrives  ->  map generates   ->  GenStep pulls the roster out, spawns it into the Lord
player leaves   ->  map destroyed   ->  SURVIVORS return to the roster
                                        the dead do not
```

⇒ 🔑 **The world remembers by construction, not by bookkeeping.** Nobody writes "12 souls,
3 dead" anywhere. The roster simply *is* the survivors.

## 3.1 The dead are forgotten

Owner: *"those who die when you aren't watching are simply... forgotten. Lost. Very Star
Wars actually. They are 'eaten and forgotten.'"*
⛔ **No death record, no memorial, no ledger, no counter.** The absence is the memory.

## 3.2 Selling a pawn — and they stay

Owner: *"if you sell them your pawn, your pawn stays there."*
The pawn transfers into that `WorldObject`'s roster. The map is destroyed; they persist as
a real pawn in the world. Return in a year and **they spawn with the cast, wearing what
they wore, remembering that you sold them.** RimWorld's relationship and memory systems do
all of it; we moved one pawn between two owners.
⇒ This is the strongest single thing in the design, and it falls out of choosing the right
container. A record-based roster could not do it at all.

## 3.3 The world map becomes a census

Because it is a `WorldObject` it draws on the planet:

```
tile 8811   [gear] Kessek Refinery     Hutt Cartel
                   12 souls . oil . will trade
   ...you raid it...
tile 8811   [skull] Kessek Refinery    abandoned
                   9 souls fled . stock spoiling
```

The player can see where people are before landing, and see the hole they left.

## 3.4 Time — frozen until visited

A roster changes **only through the player's actions**. No background ageing, no drift, no
offscreen deaths to a dice roll. Every change in the world is legibly the player's doing,
which is what a hand-made frozen planet should feel like.

⚠️ **The assumption to prove early:** `Caravan` is designed to be transient and we are using
its shape for something permanent. Pawns held in a `ThingOwner` off-map are not ticked —
exactly what "frozen" wants — but vanilla never stress-tests it across years. **Hold a pawn
in a world object through a save/load and 100+ in-game days and confirm they return
intact.** Cheap test; everything rests on it.

---

# 4. The displaced pool — how people come back

People who lose their place are **not destroyed**. They enter a per-faction pool of the
placeless. **Any cast being instantiated draws from that pool BEFORE generating anyone new.**

```
you raid Kessek Refinery
   -> 9 flee   -> Hutt displaced pool
   -> 3 die    -> gone. eaten and forgotten.

two months later, you land at Vurr Station
   -> cast needs 11
   -> 6 drawn from the pool   <- the refinery survivors
   -> 5 generated fresh
   one of them remembers you. RimWorld already knows what you did to him.
```

🔑 **This does not violate "frozen until visited."** Redistribution happens at cast
**instantiation** — when a map generates — never on a background tick.

## 4.1 Three consumers, not one

1. **New casts** — the recurring-character effect above.
2. ⭐ **Beggars and refugees at the player's own colony.** `GiveQuest_Beggars` ("beggars
   arrive") ships in this build. Draw its pawns from the pool and **the beggars at your gate
   are the people whose livelihood you burned down last month.**
3. **Recruitment** — the player may hire from the same pool. *"I burned down his refinery
   and now he works for me."*

🔴 **THE DESIGN HAS NO MORALITY SYSTEM AND MUST NEVER GROW ONE.** No karma, no reputation
number, no "the world disapproves" popup. The consequence is delivered entirely by
RimWorld's existing name, backstory and memory systems, plus the player's own recognition.
**The moment this acquires a guilt statistic it becomes a mechanic instead of a memory.**

## 4.2 Drift between factions is rare and must carry a reason

Owner: *"Drift between factions should be possible but rare and have a story... a reason.
Enslavement. Escape from their old owner. A lost battle."*

| reason | may change faction? |
|---|---|
| **Enslaved** | ✅ to the new owner. Ties to `Slavery_Acceptable` and the Jawa-trader / Hutt-keeper split |
| **Escaped an owner** | ✅ to factionless, or whoever shelters them |
| **Lost a battle** | ✅ absorbed by the victor |
| **Sold by the player** | ✅ to the buyer's cast |
| **Fled a threat** | ⛔ stays in faction; resurfaces at another of its sites |
| **Starved out** | ⛔ same |

The reason is carried on the pool entry and is readable. Drift is never random.

---

# 5. The people

## 5.1 Nobody is flat, and the reason is the campaign's own

Owner: *"I want ALL of the people documented deeply... it matters."* And, decisively:
*"But are there really little people in the world? Remember we're playing Jawa..."*

⇒ **A Jawa clan is exactly who every other faction calls an extra.** A system that renders
other people's crowds as anonymous spawns asserts the hierarchy this campaign exists to
look at from below. **No anonymous pawns anywhere in the system.** It also pays off
mechanically: buying or selling a person is a decision only if that person is someone.

## 5.2 The tonal brief — the cantina principle

Owner, verbatim, and this governs every line written:
> *"There should be heartbreaking cases, hilarious examples, bizarre characters, utterly
> boring dweebs... they should not just be 'real people' with complexity, but
> **theatrically interesting**. One or two of them should be REALLY strange and
> interesting, while the rest are just the bizarre background that Star Wars usually has.
> We're recreating the **traditional Star Wars movie feel**, not the dark gritty Andor-type
> stuff. This isn't a WW2 recreation, it's a living breathing impossibly sci-fi world with
> **contradictory ethics living side by side in a way that seems utterly ridiculous and yet
> entrancing**."*

⇒ **Not comedy versus gravity. All registers at once, none of them ironic.** ⛔ Not Andor:
no grit-as-seriousness. The world is impossible and cheerful about it.

## 5.3 The register palette — 14 registers in 6 families

The first four were the owner's examples, not the set. **More registers is also the
principal defence against homogenisation**, which is the real risk in a large authored cast.

| family | registers | what it is for |
|---|---|---|
| **Suffering** | **heartbreaking** · **doomed** · **thwarted** | someone in the wrong life · visibly will not survive · the best person in the room, in the worst job |
| **Comic** | **hilarious** · **oblivious** · **grand** | the sucky job played straight · cheerfully wrong about their own situation · absurd self-importance for their station |
| **Strange** | **bizarre** · **transcendent** · **feral** | unexplained and unbothered · has genuinely seen something and cannot say what · barely socialised, wrong for company |
| **Flat** | **utterly boring** · **dutiful** | ⭐ deliberately unremarkable and *specific about it* · takes a pointless job seriously |
| **Dangerous** | **menacing** · **corrupt** | you would not want to be alone with them · small-scale grift, skimming, a fiddled ledger |
| **Warm** | **tender** · **devoted** | unexpectedly kind in a brutal place · loves something disproportionately — a machine, a beast, a dead person |

**Distribution rules, and they are what keep a cast from becoming a parade:**
- ⭐ **One or two REALLY strange standouts per cast; the rest is background texture.** A cast
  where everyone is remarkable has nobody remarkable in it.
- **No cast may draw more than two from the same FAMILY.** This is what stops a refinery
  becoming all-Suffering or all-Comic.
- **Every batch of 25 authored characters must contain its share of Flat.** Dull people are
  the hardest to write and the first thing that quietly disappears.

## 5.4 The roster is hand-authored — several hundred

⛔ **The earlier proposal of 20–30 hand-authored standouts plus a generated pool is
OVERTURNED by the owner:** *"we should have a pool of several hundred hand-authored
standouts. Why not? It's easy to do at design time. And given we know our racial factions
very well, we can do a tremendous job."*

**Sized against the world:** 72 settlements plus ~16 named gazetteer places is ~90 sites; at
1–2 standouts each that wants 90–180 placed, and several hundred gives depth, spares, and a
stocked displaced pool for the beggars.

⭐ **The matrix is already built: 70 xenotypes × 11 factions × 14 registers × the role
table.** Every cell has a reason to be specific — an Ugnaught sump-clearer for the Hutts
writes differently from a Geonosian one, and this project knows both.

A generated fragment pool remains, demoted to **filler for the genuinely incidental**.

## 5.5 🔴 The real risk is homogenisation, not effort

The characteristic failure of a large authored cast is that by number 200 they all have the
same shape — a wry observation, an ironic detail, a sad little ending. Three guards, built
into the format rather than trusted to care:

1. **Register and family quotas per batch**, enforced, including Flat.
2. **No shared SHAPE.** Two characters may share a trait but never a structure. A grief, a
   joke and a bewilderment are different shapes, not different topics.
3. **A sameness pass** across the whole set, read by someone who did not write them.

## 5.6 🔑 THE CRAFT RULES — what actually makes a background character land

_From a research pass on Star Wars production design and background writing, 2026-08-19.
⚠️ **Attribution honesty:** these citations reached DECIDE through a research summary; the
quotes are specific and plausible but DECIDE has not read the primary sources. Treat the
RULES as sound and the QUOTES as reported._

**1. The range is held by the CROWD, not by any single character.**
The Dickens comic-ironic model: mostly banality, spiked with the grotesque-comic, **one
unremarked tragic figure per crowd**. ⭐ This is a sharper statement of §5.3's distribution
rule and it supersedes the loose version — no individual carries the tonal range; the cast
does. A character trying to be interesting on their own is the failure mode.

**2. "Unremarked" is the whole trick.** The tragic figure in a crowd is not pointed at.
Nobody in the scene comments on him. ⛔ Never write a character who is *presented* as sad,
strange or funny — write one who simply is, while everyone around them gets on with it.

**3. Do not explain. Withholding IS the characterisation.**
Boba Fett: four lines, 6m32s of screen time, and *"most of what we think we know is
assumption."* The counter-example is midi-chlorians, which turned the Force into *"a
numbers game."* ⇒ **A background character gets ONE unexplained fact.** Do not resolve it.
Tolkien's Letter 247 is the same principle — *"towers of a distant city gleaming in a
sunset mist"* — and Grybauskas's gloss on it, *"checking the pen"*, is exactly what
over-explaining does.

**4. One line of friction can encode an entire social order.**
Wuher's *"We don't serve their kind here."* ⇒ Where a character has a line, prefer a line
that implies a society over one that describes a self. **This is the single highest-value
instruction in the list for our purposes**, because our characters exist to make a planet
feel inhabited, not to have arcs.

**5. The used universe.** ⚠️ **ATTRIBUTION CORRECTED 2026-08-19.** An earlier draft of this
rule credited Mollo with *"he didn't want anyone to notice the costumes."* **That phrasing
has no locatable primary source and must not be attributed to him.** The sourced equivalent
is **Lucas's** brief, as reported: *"I don't want the audience to notice any of the
costumes. I just want to see light versus dark."* Likewise ⛔ **do not attribute "used
universe" to Gary Kurtz** — no direct quote is locatable; the doctrine traces to Lucas and
to Roger Christian, who dressed the sets from airfield scrap that *"cost nothing"*.
⇒ The rule itself stands and is well evidenced: **every possession a character has was
owned by someone else first, and shows it.** Nothing is new, nothing is bespoke, nothing is
clean.
🔑 **Christian's qualifier is the part that matters and the part usually missed:** *"You
can't just stick pieces randomly, it has to be done with an aesthetic of what looks real
and works mechanically."* ⇒ **Random damage means nothing. Every flaw must imply someone's
decision to patch it** — not *"his hand is scarred"* but *"he still works the same bench
that took the hand."*

**6. Flat characters are a legitimate craft object, not a shortfall.** Forster's defence of
the flat character stands behind the **Flat family** in §5.3. A character who is exactly one
thing, sharply, is doing real work in a crowd. ⇒ Keep the Flat quota; do not let the
authoring drift it upward into "interesting".

**7. Interrupt the ordinary rather than announce the exotic.** The cantina was staged *"not
to explain who they were, but to interrupt the ordinary."* ⇒ The strange character works
because the boring ones are there first. **Write the dull half of a cast BEFORE the
standouts**, or the standouts have nothing to stand against.

**8. Structure a character as name → archetype → want → social weakness.**
The tabletop NPC method (Sly Flourish). Terse, generative, and it forces a *want*, which is
what makes a background character playable rather than decorative.

**9. Occupational interdependence makes a society legible.** Koster's *"weak-tie
interdependence"* from Star Wars Galaxies — the one Star Wars product that had to invent
hundreds of ordinary jobs and make them feel like a society. ⇒ **Characters should need
each other's jobs.** The sump-clearer's work is why the refiner's work is possible.

**10. ⛔ The Andor line, and why we do NOT take it.** Andor's labour economics are excellent
(*"cheaper than droids and easier to replace"*; Gilroy: *"a billion beings… they don't all
have to do with lightsabers"*) — but the owner ruled explicitly **against** that register:
*"not the dark gritty Andor-type stuff."* ⇒ Take the *observation* that ordinary work exists
and is exploited; leave the *tone* of grim seriousness. Our world is impossible and cheerful
about it.

**11. Names accrete mythology.** Kenner and Topps invented nicknames for unnamed background
figures and fans built mythologies on them. ⇒ **A good name plus a job is often enough**;
the player will do the rest. This is the argument for naming everyone even when the entry is
short.


**12. The memorable detail should be WORTHLESS.** Christian bought the airfield scrap that
became the Star Wars aesthetic because *"no one wanted this scrap... it was cheap as
chips"*, coming in $100,000 under budget. ⇒ The one detail that makes a background
character land should be something nobody would pay for — a rent arrangement, a smell, a
debt of forty credits, a nickname born of a misheard word. **Treasure and titles are the
enemy of texture.**

**13. Break symmetry across the WHOLE roster.** Lucas: *"I was working very hard to keep
everything nonsymmetrical. Nothing looks like it belongs with anything else... It's a very
common thing in science fiction to see a set that has one influence."* ⇒ Across 300
characters, **no two neighbours may share a naming convention, an origin logic or a design
influence.** A settlement where everyone's name rhymes is a set with one influence.

**14. Build tics from physical DISCOMFORT, not from personality.** The performers in the
Saurin masks discovered on set that you could breathe better by putting a hand inside the
mask's mouth to ventilate it — producing a "characteristic gesture" for entirely
non-characterful reasons. ⇒ A Chagrian files his horns, a Selkath's armour hisses mist, an
Ortolan flinches at the compressor. **The body first; the personality is what the body made
of them.**

**15. Write what they do when something terrible happens three metres away.** From the
cantina: the aliens stop, look at the severed arm, and go back to their business *as if
nothing had happened*. ⇒ ⭐ **The two men playfighting over lunch on the far side of the
rancor door tell you more about that palace than the rancor does.** For every character,
know their reaction to horror at close range. It is usually the most characterising line
they have.

**16. The name comes FROM the trade or the tic, never before it.** The historical mechanism:
the toy line named the cantina extras — "Walrus Man", "Hammerhead" — *before* any fiction
did, and fans built mythologies on those names. ⇒ Design the silhouette and the job, then
name. One physical or verbal tic per character, **unrepeated across the whole roster**.

## 5.8 🔑 THE ATTACHMENT FORMAT — measured against players, not assumed

_Evidence: ~70 first-person "favourite pawn" accounts from r/RimWorld recovered via
PullPush, a Ludeon forum topic via Wayback, title-frequency over **15,115** archived
r/RimWorld slugs, plus a disk measurement of vanilla backstory prose. 2026-08-19._

### 🔴 The finding that sets our format

**Authored text IS credited by players — in exactly one place: the unique/backer pawns.**
Players hunt them by name across runs — *"Very memorable pawn, awesome backstory."* And the
tell they use to spot one is explicit:

> *"A dead giveaway that a backstory belongs to a unique pawn is that it has **2 paragraphs
> instead of one**."*

Confirmed on disk: **34% of vanilla descriptions carry a `\n\n` break**, and the
backer-authored set averages **38.4 words against 31.9** for Ludeon's shuffled generic set.

⇒ ⭐ **THE RULE SPLITS.**
- **Generic filler** — ~50 words, 2–3 sentences, one paragraph.
- **Every one of our authored characters — TWO PARAGRAPHS, and conspicuously specific.**
  Two paragraphs is not padding; **it is the signal of authorship that players actively look
  for and credit.** This is measured evidence for the owner's instinct that everyone should
  be documented deeply.

### The recipe, corrected against the evidence

**One strong skill · one trait that visibly causes trouble · at least one RELATIONSHIP · a
survivable injury · a name worth saying.**

| element | verdict |
|---|---|
| ⭐ **relationship** | **the single most load-bearing element, above everything else.** Most long player stories are really about a pair or a family. Every character needs at least one tie |
| **a trouble-trait** | one of the two strongest drivers, and usually *the stated reason*: *"a legendary plasteel sword, 20 melee. **But she is alcoholic.** A literal warmachine running on booze."* Also abrasive, volatile, nudist |
| ⛔ **pyromaniac specifically** | **DO NOT USE as the trouble-trait.** It appears in disaster anecdotes and **never** in affection ones |
| **a name worth saying** | stronger than expected. Players *rename*: *"I immediately named her Curly because of her hair. **I don't remember her original name.**"* · *"Tater the Raider"* · *"Thor 'The Swede' Gunderson… I've had a Thor in every run for years"* |
| **injury** | ⚠️ **skews to UPGRADE, not scar.** Bionics and archotech parts are named far more than peg legs. The highest-scoring post found: *"Tiberius, and his bonded tiger Augusta, who both lost their left eye at around the same time"* |
| ⛔ ~~bad at the thing they were hired for~~ | **weak — largely DECIDE's invention.** Real but incidental. Cut it |
| ⛔ ~~rivalry~~ | **absent: 2 hits in 15,000 titles. Cut it.** Kinship and partnership carry; enmity does not |

### The limit of all this, stated honestly

In ~70 favourite-pawn accounts there were **zero quotations of generated backstory prose**,
and one flat disavowal — *"I can't remember his traits or backstory"* — from a man describing
his favourite pawn. **Attachment grammar is event history**: what he survived, who she
married, who died.

⇒ ⚠️ **We cannot write attachment. We can only invite it.** The authored text's job is to
seed the contradiction the player will later narrate in their own words — which is why the
trouble-trait and the relationship matter more than any sentence we write.
*(That seeding claim is the researching agent's inference, marked UNCERTAIN — absence of
quotation is not proof of non-reading.)*

⭐ **And this is why `Inhabited` puts its weight on the ROSTER surviving rather than on the
prose.** A character the player meets twice, in two places, with a memory in between, will
beat any paragraph we could write about them.

## 5.7 Sources of texture

- **Star Wars canon — for texture.** Mine the **background, not the notables**: a moisture
  farmer, a docking-bay clerk, a spice-dock tallyman. Canon background characters accreted
  from dozens of authors and are weirder than anything invented cold. ⚠️ **Change names and
  details.** The moment a name is recognisable it becomes a guest appearance, which is the
  failure the owner named.
- **RimWorld community favourites — for STRUCTURE, not content.** What players love is
  emergent, not authored, so those stories cannot transplant. What they teach is which
  combinations invite attachment — that feeds the FORMAT, and therefore all 300.

---

# 6. The build — what is shipped and what is ours

| piece | verdict |
|---|---|
| Named, detailed, persistent pawns | ✅ shipped |
| Confined to a home area · eats · sleeps · wanders · repairs | ✅ shipped |
| Roster held off-map through map destruction | ✅ shipped — the `Caravan`/`ThingOwner<Pawn>` pattern |
| Place visible on the world map | ✅ shipped — it is a `WorldObject` |
| Defend when harmed, flee when broken | ✅ shipped — the trader-caravan graph, re-pointed |
| Beggar quest drawing from our pool | ✅ shipped — `GiveQuest_Beggars` |
| **Day/night ROUTE** | 🔵 small custom — one `LordToil` tick |
| **Sleeps at night specifically** | 🔵 small custom — one JobGiver (~30 lines) |
| `WorldObject_Inhabited` + the displaced pool | 🔵 the real new code, and it is modest |
| **Farming** | 🔴 blocked three ways. **Not attempted** — see §2.1 |

🔴 **DO NOT build a StateGraph with transitions for anything we will re-tune.**
`Lord.ExposeData_StateGraph` serialises toils by **positional index** and re-runs
`CreateGraph()` on load, so changing toil ORDER silently corrupts existing saves. ⇒ **one
toil that reassigns duty on a tick**; the schedule becomes ordinary C#. Vanilla's own graphs
are safe only because they never change.

---

# 7. Open questions

- **Cast size distribution** — how many people is a refinery? A farmstead? Not yet set.
- **How the player initiates trade** with a cast that is not a settlement.
- **Whether a place can be re-occupied** by a *different* faction after abandonment
  (`state: squatted` is reserved for it, unspecified).
- **What the gravship's arrival actually triggers** — which casts break on sight, and on
  what test.
- ⚠️ **The `Caravan`-pattern longevity test** (§3.4) is the one that could invalidate the
  architecture. Do it first.

---

# 8. Provenance

Designed in Q/A with the owner on 2026-08-19; every ruling is recorded verbatim in
`infrastructure/state/queue/DECIDE.md`, item `living-npc-templates-a-mod-concept-7b2e4d`.
Engine facts read from the 1.6 decompile and RimSage the same day, not inferred.
Supersedes the class-list reading of `LIVING_NPC_TEMPLATES.md`; that file remains valid as
a content list of places we want.
