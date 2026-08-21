<!-- status: live -->
# `Inhabited` — somebody lives here

_An independent RimWorld mod. Designed 2026-08-19 by DECIDE with the owner, in Q/A._

> 🔴 **REVERSED BY THE OWNER, 2026-08-20: the CODE IS v1 AND IS BEING BUILT NOW.**
> *"Please ship the Inhabited spec to BUILD for actual v1 construction, we have spare time
> tonight."* ⇒ The items are filed in `infrastructure/state/queue/BUILD.md` under the
> `INHABITED_*` names. **What this changes:** §6's "🔵 the real new code" is v1 work with a
> queue item behind it, and the §7 open questions are now blocking rather than academic —
> DECIDE owes the answers named there.
> **What it does NOT change:** the design in this file stands unaltered; the casts and
> characters are still authored as written; and 🔴 **§2.1 farming stays NOT ATTEMPTED** —
> it is blocked three ways in the shipped engine and being v1 does not unblock it.
>
> ~~**Owner's scope ruling: v1 for the DESIGN, v2 for the code.** The templates, casts and
> characters are authored NOW, so the hand-built world is built *as though the people will
> arrive*. The code that animates them is v2. ⛔ Do not file BUILD items for the code.~~
> ⛔ **DEAD — superseded 2026-08-20 by the ruling above.** Kept visible because the
> sentence "do not file BUILD items for the code" is exactly what a later reader would
> otherwise act on.

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

## 1.1a The parameter table — two entries ruled, and one parameter refused

§1.1 promises *"~6–8 real archetypes plus a parameter table"*. DECIDE, 2026-08-21, on the
three structural calls CHECK offered:

⭐ **`decay` — TAKEN. One float, 0–1, on the PLACE.** It is the highest-value single entry
in the table because it turns **every** archetype into its own ruined variant for nothing:
one number the GenStep reads to set building HP, missing walls, filth and whether the
larder still holds anything. ⇒ *the refinery* and *the refinery nobody has run in nine
years* are one archetype, not two.
⚠️ **`decay` is about the PLACE, never the cast.** A ruined place with a full cast is
squatters (§7.3); a whole place with no cast is abandoned. Do not let one number mean both.

⛔ **`hostility` — REFUSED, because it is not a parameter.** CHECK proposed
`hostility: conditional` (neutral until provoked) as the setting that makes a place read as
inhabited rather than placed. ✅ **The intent is right and it is already the only mode:**
`LordJob_DefendPoint` gives pawns that cannot turn hostile on their own, and §1.2 makes
Resident *"the default and the great majority"*. ⇒ **A place carries no hostility field.
The FACTION relation decides**, and §7.2 is where that is spelled out. A place that is
hostile on sight is a raid, and a raid is not an inhabited place.

⛔ **"Templates are containers, not leaves" — OVERTAKEN, not refused.** It was a good answer
to *"how do we organise 36 template classes"*, and §1.1 deleted that question. Six to eight
archetypes with a parameter table have no containment problem to solve.

---

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

> 🔴 **CORRECTED BY BUILD, 2026-08-20, off the 1.6 decompile: "pawns held in a `ThingOwner`
> off-map are not ticked" IS FALSE for a custom holder, and copying `Caravan` literally
> would have deleted every cast in the game.** `WorldObject.DoTick` walks its child holders
> and calls `ThingOwner.DoTick` on each, skipping only owners that are `is Map` or
> `is Caravan` — a hardcoded type test a mod cannot join. And `Caravan.pawns` is
> `LookMode.Reference`, which is safe only because caravan pawns live in `WorldPawns` and
> `WorldPawnGC.GetCriticalPawnReason` carries an explicit `p.IsCaravanMember()` test; a
> custom holder matches none of that method's tests, so the collector would take the roster
> between visits.
> ⇒ **The shipped code diverges deliberately in exactly two places** —
> `IThingHolderTickable` with `ShouldTickContents => false`, and `LookMode.Deep` with the
> roster kept OUT of `WorldPawns`. Both are commented at the divergence in
> `src/Jawa/Inhabited/Source/WorldObject_Inhabited.cs`.
> 🔑 **The soak in §7 still stands and is still the gate** — this fixes the two failures
> that were findable on disk; it does not prove the third one that is not.

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

⭐ **The matrix is already built: 71 xenotypes × 12 factions × 14 registers × the role
table.** ⚠️ **Name the denominator, always.** The 71 is *what we define under `src/`*; the
oft-quoted 70 is the BTD mod's roster, 42 is Outer Rim alone, 44 the art-audit subset,
79 the mechanically distinct species across all mods, and 139 the live xenotypes at 578
mods (2026-08-20). The 12 is *factions carrying dossiers* — the roster is **13**, and the
thirteenth, the Forgotten Arsenal, holds no settlement and has no cast. ~~11~~ was a count
of a dead world.

Every cell has a reason to be specific — an Ugnaught sump-clearer for the Hutts
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

## 5.7 ⭐ A NAMED CHARACTER KEEPS THEIR OWN RACE — ruled 2026-08-21

**The question:** 51 of the 269 carry a race their own faction cannot generate. When the
two disagree, which wins?

🔴 **The engine does not leave this open, so not deciding IS deciding.** Every `Jawa_*` pawn
kind carries `useFactionXenotypes: true`, and `PawnGenerator.cs`:

| | |
|---|---|
| `:1751` | at generation, draws the xenotype **from the faction's `xenotypeSet`** |
| `:518` | in validation, **rejects** any candidate whose xenotype is not in that set |

⇒ bind a named character to such a kind and their authored race is **discarded, or they
fail to generate**. Silently, both ways.

### ⇒ THE RULE

1. ✅ **The authored race wins. `CharacterApplier` forces the xenotype** (`request.ForcedXenotype`).
2. ⛔ **Named characters are not generated through a kind with `useFactionXenotypes: true`** —
   give `Inhabited` its own unconstrained kinds, or clear the flag on the ones it uses.
3. ⛔ **Do NOT widen a faction's `xenotypeSet` to make a named character fit.** That set is
   the owner's race/faction matrix and it governs the faction's **anonymous** pawns. Editing
   it to accommodate one person changes what a thousand others look like.
4. ✅ `useFactionXenotypes` keeps governing anonymous fill, unchanged.

🔑 **Why the individual wins, and it is the design's own answer.** §4.2 has named people
**drift between factions** — enslaved, escaped, absorbed after a lost battle, sold by the
player — and §4 redistributes them through the displaced pool. **A Muun in Imperial service
is the setting working.** A named character is a person, not a sample from a distribution.

### Two traps found while mapping all 269, both of which faked a missing def

- ⚠️ **The 2026-08-15 dump contains 251 XenotypeDefs and none of ours.** Read against it,
  every one of our races reports MISSING. **Use the 2026-08-21 578-mod capture** (139 rows).
- ⚠️ **`Klatooinian` is spelled `RimMandrakeKlatoonian` in the def** — one "o" adrift from
  the Star Wars spelling the prose uses. A prose→defName mapper that normalises spelling
  will silently drop him. **Yttakin is vanilla**, not one of ours, and a `RimMandrake`
  prefix breaks it the same way.

⇒ **253 of 269 map cleanly.** The remaining 9 are `CAST_NINE_SPECIES_MISSING_1`.

---

## 5.7a THE FOUR OPTIONAL FIELDS — and sparse is the specification

**Owner, 2026-08-21:** *"You don't have to spec out items weapons and armor for everyone,
nor all their skills. Just if they have an unusually high or low skill in something for
narrative reasons, or if they have a special weapon, armor, or unusual item."*

Four optional lines, written directly under `` `traits:` `` in the same backticked style:

```
**Shaa Nel** · Tusken · f · 30
`traits: ShootingAccuracy(CarefulShooter), Ascetic`
`weapon: OuterRim_CyclerRifle`
`skills: Shooting 18`
childhood: given a cycler at fifteen and told what it was for, which was not people.
```

| field | holds |
|---|---|
| `weapon:` | one ThingDef defName |
| `apparel:` | ThingDef defNames, comma separated |
| `item:` | a carried or installed ThingDef — bionics go here |
| `skills:` | `Skill N`, comma separated. 0–20; **8 is average, so only write outliers** |

🔑 **THE TEST, and it is what the pass is judged on: every field must trace to a specific
sentence of that character's own BLOCKQUOTE.** Not the `adult:` line, not the `childhood:`
line — the blockquote is the character. And it must agree in both directions: a person
written as a fighter gets the weapon *and* the skill to use it; a person with no such
sentence gets neither.

⛔ **SPARSE IS THE SPECIFICATION, NOT A SHORTCUT.** ⭐ Measured after the first full pass:
**123 of 294 characters carry anything at all — 18 weapons, 15 apparel, 27 items, 101 skill
lines.** 171 people carry nothing and that is correct output. Do not backfill to look
complete.

⭐ **A low number is as good as a high one, and often better.** `Medicine 5` on a nurse
every drone would rather have than the machine; `Shooting 0` on a man who spent twenty-nine
years carrying the boarding ramp; `Intellectual 0` on a hunter who cannot read and draws the
mark's face on his own forearm instead. Each of those does more than a 17 would.

⛔ **A weapon a sentence FORBIDS must not be written.** *"She will not be given a weapon,
because she goes hands and teeth immediately"* gets `Melee 14` and no `weapon:` line. Three
characters in the first pass were armed by an early draft against their own prose.

🔴 **Every defName must resolve in the def dump before it is written.** The first pass
proposed nine that did not exist — stilts, a spanner, a translator collar, a Whiphid cooling
shroud. Five were dropped and four had real substitutes found (`GS_Gaffi`,
`OuterRim_CyclerRifle`, `Apparel_Bandolier`, `DV_MeleeWeapon_SerratedScimitar`). **A dead
defName in a frozen world is a person holding nothing, and nothing logs.**

---

## 5.7b ⛔ FOUR TRAIT PAIRS THE ENGINE FORBIDS — check before you write a `traits:` line

**Added 2026-08-21, after 14 of the 269 shipped with an impossible pair.** These are not
style advice: `TraitDef.conflictingTraits` says the pawn cannot hold both.

| do not pair | with |
|---|---|
| `Kind` | `Abrasive` · `Psychopath` |
| `Ascetic` | `Jealous` · `Gourmand` · `Greedy` |
| `Brawler` | `ShootingAccuracy` *(either degree)* · `Wimp` |
| ⭐ `TooSmart` | `SlowLearner` |

⭐ **The `TooSmart` × `SlowLearner` row was missed on the first pass and caught by the
audit, on a character written the same day the rule was added.** That is the argument for
running the check rather than trusting the table: **derive the pairs from the shipped
`TraitDef`s' own `conflictingTraits` and intersect with the vocabulary the rosters actually
use.** Ten pairs matter today; a new mod can add more tomorrow.

🔴 **The two that actually caught us, and why.** They are not random slips — each is a real
character type that our house voice reaches for, and the engine models it as one trait, not
two:

- **`Ascetic` + `Jealous`** — four of the fourteen. Both read as *"wants nothing / resents
  what others have"*, so a writer reaches for the pair naturally. ⇒ **Decide which engine
  the person runs on.** Someone who takes the smallest ration in public is `Ascetic`;
  someone who cannot bear a rival holding what they hold is `Jealous`. Almost nobody is
  both, and the prose always says which.
- **`Kind` + `Abrasive` / `Kind` + `Psychopath`** — the *"decent but unbearable"* and the
  *"performs warmth without feeling it"* characters. ⇒ ⭐ **`Psychopath` plus prose about
  learned warmth is the stronger version anyway** — Prith Vane and Ren Ashek both work
  better that way, and one of them reads the right words off a card at the bedside.

⚠️ **RimWorld will not tell you.** `TraitSet.GainTrait` checks no conflicts and imposes no
trait cap, so an impossible pair loads with **zero errors** and generates a pawn silently.
`CharacterDef.ConfigErrors` now names the pair at load and `CharacterApplier` refuses the
second trait — so it is loud today, but only because we made it so.

✅ **The audit is one command** — build the conflict map out of the shipped `TraitDef`s and
scan every `traits:` line. It returned **269 scanned, 0 conflicts** on 2026-08-21.

---

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

## 5.9 🔴 CAST THE FAITH, NOT THE INDUSTRY — owner, 2026-08-20

*"Do consider the different faction personalities. Folks in the Hutt org should make sense
in a pretty terrible, cutthroat place. The moisture farmers are libertarian and generally
pretty decent. Things like that."*

⇒ **A cast is not "people who do this job". It is "the kind of person who survives HERE."**
The same role written for two factions must produce two different people: a Hutt tallyman
and a Homestead tallyman are not the same man in a different coat.

⭐ **AND THE ANSWER WAS ALREADY IN THE SPEC.** Every faction's ideoligion name in
`FACTION_SPEC.md` §"The 14 factions" — the heading is historical; **13** stand, the ~~14th~~
(the Unbound Hive) being struck through and cut — **is its moral climate in three words.** Nobody had
used them this way. Do.

| faction | its faith | the moral climate | what the cast must SHOW |
|---|---|---|---|
| **Hutt Cartel** | *the Reckoning of Debts* | 🔴 **cutthroat and transactional.** Everything is owed; forgiveness destroys value | who survives by being **useful**, and who survives by being **owned**. Nobody here is safe, and several are comfortable anyway |
| **Homestead Defense League** | *the Covenant of Free Wells* | ⭐ **libertarian and generally decent.** Owner's own words | neighbourly by practice not sentiment · suspicious of any authority · a code about water that they'd die on · and **decency that costs them something** |
| **Deep Desert Tribes** | *the Sun-Debt* | territorial; water is sacred and **moisture farming is sacrilege** | zealots who are not villains. They arrive fast, hit hard and are gone — write people for whom that is *righteous* |
| **Free Droid Enclaves** | *the Continuity Protocol* | self-owned, dignity-obsessed, religious about their own origin | machines who will not be property again, and what that does to how they speak to you |
| **Geonosian Foundry Hive** | *Meckgin* | duty and caste as cosmology; work unfinished is the beginning of the end of the world | people who cannot stop, and are **not unhappy about it** |
| **Wildsteam Clan** | *the Green Oath* | growers and river people on a dying world | the only faction that plants. Write the smugness that comes with it |
| **Deepwater Compact** | *the Balance* | the seas, measured and rationed | people for whom excess is the sin |
| **Ascendant Helix** | *the Ascendant Genome* | improvement as doctrine | `Transhumanist` and `BodyMastery` country. Also: who gets left behind by it |
| **Blackstar Company** | *the Contract* | predatory, but **contractual** — that is the whole joke | professionals. Paperwork before violence |
| **Jawa Trade Moot** | *The Salvation* — shared with the player | communal, clannish, sharp trade, ⭐ **thieving as a virtue** | our own people from outside. Kin, rivals and customers at once |
| **the Junkers** | ⭐ **`the Weight`** | ⚠️ **CORRECTED 2026-08-20.** This table first read *"no doctrine, only the ladder"* from `FACTION_SPEC.md:47` — that is the **characterisation**, not the name. The shipped def carries `<ideoName>the Weight</ideoName>` and a full description: *"We have no word for what we believe, because belief is not worn and everything real is worn. Weight is rank. What is bolted to you was cut off somebody slower… **Nothing is wasted in the warrens. Not the plate. Not the meat.**"* | 🔑 **Read the DEF, not the roster table.** Position is everything, weight IS rank, and the last line licenses far more than a ladder does |
| **Galactic Empire** | *The Rising Order* | hierarchy as virtue | the banality. Clerks, not villains |

🔑 **The test for any character:** *would this person be a different person in the faction
next door?* If the answer is no, the faith is not doing its work and the character is
generic.

⚠️ **This rule arrived after the first four fan-out casts were commissioned** (Free Droid
Enclaves, Jawa Trade Moot, Geonosian, Junkers). Their briefs carried faction *context* but
not this rule. **DECIDE applies it as a revision pass on return**, and every later
commission carries it from the start.

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

# 7. The five that were open — answered 2026-08-21

⭐ **Every answer below is built out of numbers RimWorld already computes.** Nothing here
adds a stat, a score or a tracker. That is not thrift, it is §4.1's rule: the moment this
design acquires its own number it becomes a mechanic instead of a memory.

| was open | answer |
|---|---|
| **Cast size distribution** | ✅ **RULED** and written into `INHABITED_GENSTEP_CAST_SPAWN_1` — hive foundry 14–22 · waystation 10–16 · refinery 8–14 · nomad camp 6–12 · trade moot 5–9 · homestead 4–7 · droid enclave 3–6 |
| **The four missing character fields** | ✅ **ANSWERED BY THE OWNER**, 2026-08-21, and narrower than the question: race on all 269, kit and skills **only where the prose earns them**. `CAST_RACE_AND_KIT_FIELDS_1` |
| **The twelfth faction has no cast** | ⏳ authoring debt, filed — `DEEPWATER_CAST_ROSTER_1`, ~25 people for the Deepwater Compact |
| **Trade · arrival · squatting** | ✅ **RULED BELOW** |
| ⚠️ **The `Caravan`-pattern longevity soak** (§3.4) | 🔴 **still the gate.** Two of its three failure modes were found on disk and fixed; the third needs the 100-day soak. Do it first |

## 7.1 Trade is a PERSON, not a place

⛔ **Do not give `WorldObject_Inhabited` a trade dialog.** You trade with the quartermaster,
not with the refinery — which is both the right fiction and the shipped mechanism.

**One cast member is the trader.** The route is `IncidentWorker_VisitorGroup.cs:96-97`,
copied exactly:

```csharp
TraderKindDef k = faction.def.visitorTraderKinds.RandomElementByWeight(t => t.CalculatedCommonality);
pawn.trader.traderKind = k;
```

⚠️ **`pawn.trader` only exists if the pawn's `PawnKindDef.trader` is true** —
`PawnComponentsUtility.cs:247` is where the tracker is created. So the designated cast
member needs a kind with `trader: true`, or the tracker must be added explicitly. **A pawn
without the tracker silently cannot be traded with and nothing logs.**

⇒ The player walks up and trades. `JobDriver_TradeWithPawn` is shipped, needs no UI, and
works on any pawn with a tracker.

🔑 **The consequences fall out for free, and they are the reason to do it this way:**
- **Kill the trader and the place stops trading** until the cast is re-instantiated. That
  is a real decision the player can make and understand.
- **The trader can flee** with the rest, into the displaced pool (§4), and turn up as
  someone else's quartermaster two months later.
- A cast with no eligible member simply does not trade. ⛔ **Do not fall back to
  generating one** — a place that has nothing to sell should say so by having nobody to
  sell it.

✅ **The world-map route is available if it is ever wanted:**
`CaravanVisitUtility.TradeCommand(caravan, faction, traderKind)` takes a faction and a
trader kind and is not settlement-specific. `[v2]` — the on-map route is the design.

## 7.2 What a gravship's arrival triggers — one ratio, three faction states

**The test is the cast's own combat strength against the arriving party's**, both summed
from `PawnKindDef.combatPower` — the same number RimWorld already uses to size every raid.

```
defenceRatio = Σ combatPower(cast) / Σ combatPower(landing party)
```

| the cast's faction | on arrival |
|---|---|
| **hostile** (`goodwill <= -75`) | ⛔ **never flees. It fights.** A gravship landing on an enemy site is an assault, and treating it as a scare would waste the best confrontation in the design |
| **neutral** | flees iff `defenceRatio < 0.5` — *outmatched, and they know it* |
| **ally** (`goodwill >= 75`) | never flees |

⭐ **`isFighter` is the second lever and it is already on every kind.** A cast that is
mostly `isFighter: false` — a homestead, a trade moot — will fail the ratio against almost
any landing party, which is exactly the *"break on sight"* the FATE table asks for. **The
civilians run because they are civilians, not because a flag says so.**

🔴 **AND THE GOODWILL COST IS GATED, deliberately.** §1.2 says flight costs goodwill and
that hostility only ends at 0, so a scared-off crew is expensive to repair. ⇒ **arrival-flight
costs goodwill ONLY if the player lands on the site's own tile.** Landing on an adjacent tile
and walking in costs nothing. Without that gate, crossing the planet would strip-mine the
player's relations with everyone he flew over, and he would have had no way to know.

## 7.3 Squatting — yes, but never by the people you drove out

A place whose cast leaves becomes `Abandoned`. It becomes `Squatted` under three conditions,
all of them already tracked:

1. **A different faction's displaced pool has enough members** for the place's cast size.
2. **That faction is hostile to the original owner.** Squatters are people who lost their
   own place, taking someone else's.
3. **Evaluated at cast instantiation only** — when the player next generates a map there.
   ⛔ Never on a tick. This is §3.4's rule and squatting does not get an exception.

🔴 **The original faction may NEVER re-occupy its own abandoned place.** If the Hutts you
drove out of Kessek Refinery could drift back into it, the raid would be erased, and §3.4
promises that *"every change in the world is legibly the player's doing."* A place the
player emptied stays empty until **somebody else** takes it — which is a consequence, not
an undo.

⇒ Squatters keep their own faction; the place's ownership changes with them. The reason is
carried on the pool entry exactly as §4.2 requires, and reads: *lost their own place.*

---

# 8. Provenance

Designed in Q/A with the owner on 2026-08-19; every ruling is recorded verbatim in
`infrastructure/state/queue/DECIDE.md`, item `living-npc-templates-a-mod-concept-7b2e4d`.
Engine facts read from the 1.6 decompile and RimSage the same day, not inferred.
Supersedes the class-list reading of `LIVING_NPC_TEMPLATES.md`; that file remains valid as
a content list of places we want.
