# GREENTIDE_TERROR_REPLACEMENT_1: the Vurrak, design (BENCH, 2026-10-02)

Status: DRAFT, design only, for the owner to rule on. No defs, code, items or ledger verbs.

## 0. Read this first: the brief and the owner's ruling disagree

This pass was briefed as "design ONE new lunger at commonality 0.15". The item already holds an
owner ruling that changes that (card, 2026-09-23, typed in the notes box):

> *"I select Vurrak and Illisk... Illisk should be a shoal of toothy fish (pirahnna essentially)
> that are crazy fast and nearly unkillable except with explosives."*

So the dianoga's slot is filled by **two** chosen creatures, not one still to be invented. Designing
a fresh creature would overwrite his pick. The bedazzle review (`greentide_bedazzle_review_2026-10-02.md`)
also proposes a third water predator, the **dhollock** (deep-water lunger, built comp).

What is actually missing is the **Vurrak**: he selected it ("a silted ambusher that is
indistinguishable from bank until weight lands on it") but gave no body, size or mechanism. The
Illisk is fully specified by him. ⇒ This doc designs **the Vurrak**: five candidate bodies for it,
one recommended. That is one lunger-band creature at about 0.15, which is what the brief asked for,
inside his ruling rather than over it.

## 1. The gap (measured)

Parsed as XML elements, 2026-10-02, BENCH clone:

| roster | rows | weight sum | dianoga | lungers present |
|---|---|---|---|---|
| `RUT_Greentide` (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml`) | 26 | 9.168 | absent | Dragonsnake, Hssiss, RSW_Worrt (water-margin) |
| `RM_Greentide` (`src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml`) | 7 | 3.05 | absent | none (vanilla Warg, Muffalo, Elephant, Cobra, Megaspider, Rat, Hare) |

`WildAnimals_Greentide.xml` keeps one mention of the dianoga, a removal comment at line 195.

- The de-wire is done. The free roster has **no lunger at all**. The campaign roster's lungers are
  canon or neighbours' (Hssiss is the Sump's junior lunger), and **nobody owns the bank.**
- Sheet ban 6, "no safe standing water", is carried today only by canon animals in the campaign
  tier. The free tier does not carry it at all.
- Water niches once the ruled and proposed creatures land: deep water = dhollock (proposed);
  open reach = Illisk (ruled); **the bank edge = Vurrak (ruled, no design)**.

Constraints on the Vurrak: invented name, `RM_` tier, cast inline in `RM_Greentide` (Q11a and
`GREENTIDE_FREE_ROSTER_OWNED_1`); one home; not fire-themed (§4b); not Earth-nameable (ban 2: the
shape may echo Earth, the name may not); not tentacled (that is the Fever Wood's look); reads as a
**creature, not a trap** (the risk he accepted on the card).

Where it must differ from neighbours:
- **Mirrak** (Longshade, built `RM_CompFalseShadeAmbusher`): a visible oddity, a shadow lying where
  there should be none, in desert light. It seizes whatever comes next to it.
- **Dhollock**: invisible while in deep water, then lunges.
- **Worrt and shiro** (already Greentide): wait at the water's edge or on the floor.
- Desert jellypot, the cracked lands' gornt: sit and wait.
- Dune burrowers: strike from under the sand.

The Vurrak's trick is different from all of these. **The ground itself stands up**, and only when
something walks onto it.

## 2. Five candidates

Source: GPT consult, `gpt-6.1-sol`, effort high, 2026-10-02. It was given a "Greentide only"
subject guard, and the answer opened with the required line, so it is **on topic**. The answer is
saved verbatim beside this doc: `greentide_terror_replacement_gpt_consult_2026-10-02.md`. Names
were checked for collisions by BENCH: zero hits in `src/`, `design/` and `infrastructure/`, and zero
Wookieepedia search results for vurrak, rellock, sammeth and emmock (sanity probe: `wyyyschokk`
returns 4+).
⚠️ Two names have problems. **Urrel** is close to the existing `Murrelith`/`Trurrel`, so it would
need a new name if picked. **Sammeth** is one letter off the bedazzle review's `yammeth`.

**Rules shared by all five** (from the consult; BENCH agrees):
- The disguise is perfect while the creature rests.
- The fair warning starts the moment weight lands, about 90 ticks before the strike.
- The lunge hits the cell it marked during the warning. A pawn that steps clear makes it miss.
- After the reveal it is an ordinary visible animal: it bleeds, it can be shot, and it leaves a corpse.
- Anything can set it off: colonists, raiders, visitors, other animals. No truce (ban 1).

| # | name | body (size) | how it hides and what sets it off | the warning you get | how you beat it | risk |
|---|---|---|---|---|---|---|
| 1 | **Vurrak**, the buckling bank-wedge | lopsided wedge with a high rear keel, three unequal buttress legs, a biting cleft under one shoulder; petrol-violet hide, turquoise cartilage, chalk-pink teeth (1.35) | flattens into a bank shelf; one pawn entering its cell is enough | the "bank" rises under the pawn: three joints unfold and the mouth shows | draft and step inland at once; shoot it during the lunge or the stagger after | a flat open/shut graphic could read as a pressure plate |
| 2 | **Rellock**, the walking terrace | four stacked body tiers around an offset head, on two broad pedestal feet (1.65) | lies as two silt steps; the first step arms it, crossing onto the second fires it | the first step sinks and the second rises | back off the first step instead of crossing | the most trap-like of the five (a collapsing stair) and the costliest to animate |
| 3 | **Urrel**, the rolling bank-knot | two rigid, unequal hoops locked around a bite block; no limbs (1.2) | a round hummock; fires only when approached from the water side | a pale crescent of its inside rolls into view | sidestep the marked line; shoot it while it rights itself | could read as a wheel or a coiled snake; name collides |
| 4 | **Sammeth**, the load-drinking saddle | a hollow arch on two stout legs, jaw hanging underneath (1.5) | a cushion-shelf; fires after 120 ticks of standing on it | the arch lifts and the mouth shows | keep moving; never stop to shoot while standing on it | overlaps with the shiro's sit-and-wait; name collides |
| 5 | **Emmock**, the weighted silt crown | three rigid lobes around a mouth set in its side (1.85) | a silt fan; any contact makes it flex, but only a body of 0.6 or more fires it | a loud joint crack and the whole body shows | let small wildlife reveal where they are; punish its slow recovery | a hidden size rule feels arbitrary; lobes drift toward slime or tentacle |

The consult's ranking (1 = best): **Vurrak** is 1st for fairness and build cost and 2nd for terror.
**Rellock** is 1st for terror and 4th for cost. **Emmock** comes last everywhere.

Research the consult gave as fear references only (no anatomy is borrowed): the Mime (Alpha
Animals), and the Sightstealer, Revenant, Devourer and Metalhorror (Anomaly). The Subnautica sand
shark: a small fin over ordinary-looking sand. The Don't Starve depths worm: a harvestable lure. The
Rain World white lizard: camouflage given away by eyes and saliva. The common lesson is that
**terror comes from not being able to trust ordinary scenery, and fairness comes from a tell
between the trigger and the bite.**

## 3. BENCH recommendation

**Build candidate 1, the Vurrak (buckling bank-wedge), at commonality 0.15 in `RM_Greentide`'s
`<wildAnimals>`, band `lunger`.** Reasons:

- **It is literally what he picked.** One footstep and the bank stands up. Nothing needs adding to
  his sentence.
- **It is cheapest.** The only new piece is a bank-contact trigger on top of the lunge and
  visibility handling that `RM_CompAquaticAmbusher` already has (one new comp or one new mode; see
  the C# note below). It needs one cell, no multi-cell footprint, and no terrain edits.
- **It reads as an animal.** Within the warning it shows legs, a mouth and a lopsided gait, then it
  chases and feeds like any predator. That answers the card's "creature, not a trap" risk.
- **It is distinct from the mirrak.** The mirrak is a visible oddity in open light that seizes
  whatever comes next to it. The Vurrak cannot be seen until it is stepped on, then commits to one
  marked cell, so stepping clear makes it miss. Different trigger, different counter.
- It completes the water triad: dhollock in deep water, Illisk in the open reach, Vurrak on the bank.
  No river crossing in the Greentide is free (ban 6, extended to the shore).

**Runner-up: the Rellock**, if he wants maximum terror over cost and is happy to own the
"stairs collapsing" risk.

Notes for whoever builds it later (FOUNDRY; not filed here):
- Body size 1.35 is a starting point. Its prey ceiling should exceed the mirrak's 1.2, so that a
  colonist is a target.
- A RimWorld pawn does not block movement, so "a pawn steps into its cell" can be detected
  directly, without registering pressure cells.
- `RM_CreatureBehaviors.csproj` lists every `.cs` file explicitly, so a new comp is a two-file change.
- A hidden pawn must also be hidden from the selector and from tooltips, or the disguise leaks.

## 4. Art brief: the Vurrak

- **Subject:** `RM_Vurrak`. An invented bank ambusher from the Greentide river delta. Not Star Wars
  canon and not an Earth animal. Never describe it as a crocodile, turtle, frog, crab or any other
  Earth animal in prompts, labels or descriptions.
- **Silhouette:** an asymmetric solid wedge, low at the front and rising to a high rear keel like an
  overturned hull. Three **unequal** buttress legs: two on one side, one thick one on the other. The
  gait is visibly lopsided. A wide biting cleft opens under one shoulder (the left on the east
  view), with chalk-pink peg teeth. Small, deep-set eyes on the keel's flank. No tail, no tentacles,
  no shell seam running all the way round. It must not read as a clam or a box.
- **Palette:** petrol-violet hide with an oily green-blue sheen. Turquoise cartilage shows at the
  joints and inside the cleft. Its back is caked in grey-ochre river silt that cracks off along
  the joints. The alien colours are the point; avoid muddy brown on the creature itself, which
  belongs to the silt only.
- **Facings:** north, east and south, standard RimWorld animal facings; west mirrors east. Normal
  pawn canvas, drawSize about 1.6-1.8 (it reads big for its 1.35 body).
- **Second state (only if the disguise is rendered as an overlay):** the resting "bank shelf" pose.
  A flat silt slab, the keel pressed flush, the legs folded under, matching wet Greentide bank
  terrain. It must be convincing at game zoom. Build cost: one extra texture set.
- **Before generating:** check artpipe for existing renders first
  (`artpipe_state.py find vurrak bank ambusher`). The bedazzle review's art commission (row 6)
  already lists the Vurrak.

## 5. Questions for the owner

**Q1. Which body do you want for the Vurrak?**
- **A. The buckling bank-wedge (recommended).** A lopsided three-legged wedge. Step on it and the
  bank rises and bites. *Cheapest and fairest; a bit less shocking than B.*
- **B. The walking terrace.** Two silt steps: the first one arms it, crossing to the second fires
  it. *Scariest moment of the five; looks most like a trap and costs the most to animate.*
- **C. The weighted crown.** Only something your size or bigger sets it off; small animals just
  reveal it. *Clever and readable once learned; the size rule feels arbitrary at first.*

**Q2. How much warning between the step and the bite?**
- **A. About 1.5 seconds (90 ticks), and the game pauses the first time one is ever revealed.**
  *Fair to learn; a drafted pawn can usually step clear.*
- **B. About 1.5 seconds, no pause.** *Tenser; an undrafted hauler will usually get bitten.*
- **C. Almost none: it bites the moment weight lands.** *Pure terror, but it plays like a hidden
  trap, which is the risk you accepted on the card.*

**Q3. How common?**
- **A. 0.15, the dianoga's old weight.** *A few per map; every bank is a gamble.*
- **B. 0.08.** *A rare legend; most crossings are fine, and that is what makes it bite.*
- **C. 0.25.** *Banks are routinely deadly and players will start building causeways early.
  Stacked with the Illisk and the dhollock, this may make the river feel unwinnable.*

**Q4. Does it bite other animals too, or only people?**
- **A. Anything that steps on it (recommended).** *Fits "no truce". Players can watch wildlife set
  them off and learn where they lie.*
- **B. Only colonists, visitors and raiders.** *Every bite is a story about your people, but it
  needs a special exception, which goes against the free-for-all.*

## Sources

- `infrastructure/state/items/GREENTIDE_TERROR_REPLACEMENT_1.md` (owner ruling 2026-09-23; open questions)
- `design/Jawa/worldbuilding/biomes/the_greentide.md` §4 and §6 (Lungers; hard bans 1-6)
- `design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` (dhollock; water triad; art row 6)
- `design/Jawa/worldbuilding/biomes/rosters/*.json` (cross-biome predator census, live rows only)
- `src/RimMandrake/CreatureBehaviors/Source/RM_CompAquaticAmbusher.cs`, `RM_CompFalseShadeAmbusher.cs`
- GPT consult, saved: `design/Jawa/worldbuilding/biomes/greentide_terror_replacement_gpt_consult_2026-10-02.md`
