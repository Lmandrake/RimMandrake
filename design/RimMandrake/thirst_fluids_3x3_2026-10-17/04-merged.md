# Thirst and fluids: merged 3x3 result (2026-10-17)

Item `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT`. Inputs, all in this folder or beside it:
pass 1 `design/RimMandrake/thirst_fluids_design_2026-10-17.md` · pass 2 blind `02a-blind-solutions.md` · pass 2
critique `02-review.md` · GPT blind `03a-gpt-blind.md` · GPT critique `03-gpt.md`. Provenance tags: **P1**, **P2b**
(pass 2 blind), **P2c** (pass 2 critique), **Gb** (GPT blind), **Gc** (GPT critique), **M** (this merge).
Offline design only; nothing built or run live.

## 1. What every pass agreed (the shared core)

All four independent samples reached the same core: a per-liquid **use class**, separate from hazard data
(P1 `drinkClass`, P2b same, Gb "classify by permitted use"):

| class | rows | drunk | auto-gathered |
|---|---|---|---|
| Potable | fresh, icy, the five coloured waters, distilled/stilled water items | normally | yes |
| LastResort | the four slimes (+ the Gelatinous biome's own slime if Q5 says so) | only when no potable water is available | never |
| BreakOnly | salt water, brine (Q8) | only inside the salt-water mental break | never |
| Never | acid, toxic (Q8), propane, chemfuel, tar, lava, reaction liquor, astrofuel, blood | never | never; moved only by an order |

Further agreed points:
- one **source adapter** covers registry rows, terrain-only liquids (`RM_Slime_Liquid`, `AB_LiquidSlime`) and loose
  water items (`RM_DistilledWater`, `RM_StilledWater`) — P2c found these outside the system; Gc generalised it.
- the slime last resort **rechecks potable availability right before swallowing**, and a brief reservation of the
  only bottle does not unlock slime (Gb, Gc).
- the salt break must not re-enter while salt poisoning is active (P2c), and should need "no potable reachable" (P2c).
- a **drinking reserve** on every liquid network: sprinklers and machines stop above it, drinkers do not (P2b, P2c, Gc).
- a still's or machine's **bill counts as the order** for its non-potable input (P2c, Gb "explicitly authorised
  repeating bill"); without it a salt-coast colony's stills never get brine.
- partial draws from buckets/barrels need a saved litres state on the container (P2c; Gc "partial-container
  conservation").

## 2. Live ruling violations in BUILT code (confirmed, fix first)

1. **Auto-fill gathers any liquid.** `WorkGiver_FillBottle` → `RM_LiquidBottleUtility.TryFindFillCell` passes
   `requireFreshWaterOnly: false`; nearest liquid to the pawn wins, salt or acid alike (P1 read the giver; P2c read
   the callee chain, `RM_LiquidBottleUtility.cs:110-117, 255-314`). Confirmed by two reads.
2. **Thirsty pawns drink salt water routinely.** Fouled is ranked by quality then distance, not gated
   (`RM_ThirstMath.Acceptable` line 136 gates only Toxic) (P2c). Single read; strong, file:line cited.

## 3. The options after review

| option | strongest form | from |
|---|---|---|
| **A — bottles, batched and capped** | drink bottles; fill **and** wash in batches of ~10; colony stock target counts inventories; route-cost source choice; refill hysteresis | P1, batching P2c, route/hysteresis Gc |
| **B — drinking stations** | a tank tap on the net with drinking vessels at it; one job per drink | P1, Gb "fixed utilities" |
| **C — network-first vessel roles** | bottle = mouths, bucket = small top-ups/gardens, barrel = bulk transport, hose = temporary runs, pipe = permanent supply; machines take from a port first, then a bucket/barrel refuel job, never bottles; vessel roles are defaults with emergency exceptions | P1, exceptions Gc |
| **D — the bottler** | a net-fed machine that fills and washes bottles to a stock target; pawns drink real bottles (ruling met literally); empty supply, washing water, power, output cap, and counted against the reserve | P2c, constraints Gc |

Ideas no option took up, worth keeping: a pawn-owned reusable bottle refilled and drunk in one job (Gc); crate
exchange depots for real batch returns (Gc); scheduled barrel delivery to outposts (Gb "scheduled service", Gc).

**How they compose.** A is the base (it fixes §2). D replaces A's fill/wash jobs where a net exists. C's machine
ports and reserve are orthogonal and come when the first fluid-burning machine needs one. B and D are alternatives
for the same slot: B if the owner says vessels at a station count as bottles, D if he means real bottles.

## 4. Claims after review

| claim | P1 | after review | trust |
|---|---|---|---|
| auto-fill takes any liquid | measured, giver only | confirmed via callee chain (P2c) | high |
| no slime containers | measured, defName grep | confirmed by extension census (P2c) | high |
| 3 jobs per bottle drink | estimated | confirmed from drivers, `count = 1` (P2c) | high |
| water jobs/day, 10 pawns | 180 (A) / 60-70 (B) | **depends on the scenario, not an error**: 180 at 3 L/day and the 3x cap (Gc reproduced it); 75-90 at the **built** 2.4 L/day and ~1.9x heat (P2c). A batched fill+wash: 72 at the cap (Gc) | both right for their inputs; the budget question stands |
| green slime row = Gelatinous body | unmeasured | **separate defs** (P2c); whether they *should* be one stays the owner's (Gc) | measured |
| sprinkler uses as much as 8-14 colonists | — | **refuted** (Gc): 350 L/day ÷ 2.5-4.5 L/pawn = **78-140 colonists** per head. The reserve need is *stronger* | arithmetic, checked here |
| only Cannibal nullifies raw-food mood | measured, XML | true in XML, but Ascetic skips taste thoughts in C# (`FoodUtility`, Gc) — an XML census is not a behaviour audit | medium |
| no vanilla need-driven mental break | assumed | narrowed (Gc): withdrawal hediff stages carry mental-state givers — a precedent for a **hediff-stage trigger** for the salt break | medium |
| genes `StrongStomach`/`RobustDigestion` mean "hardy" | P1 proposed exempt | Gc: they mean food poisoning / raw food, **not** indifference to taps | judgment → Q3 |

## 5. Where the passes disagreed (left as disagreements)

- **Do cups at a station count as "bottles"?** P1 proposed yes (B); P2c says it rewrites the ruling and drops B for
  D; Gc says it plausibly matches the intent but extends the wording, and calls predicting refusal unsupported. → Q1.
- **Should a debuff-free pond beat a nearer tap?** P2c says the tier order was inverted; Gc says that is a
  preference, not a textual correction. → Q2.
- **Slime per-kind effects.** P1: red stomach burn, white +food, yellow extra disgust and food poisoning. Gb/Gc:
  white gives a flammable residue (more fire damage), not nutrition; yellow gives nausea, not infection; green's
  organ rot needs owner approval. → Q6.
- **Mood numbers.** P1 slime −20 ×2 stack, tap −3 for 0.5 day; Gb slime −25 for a day, tap −3 for 6 h, no stack. Close
  enough; tuning lives in settings.

## 6. Recommendation (M)

1. **Now:** the use-class field and source adapter; fix both §2 violations; batched fill and wash with a counted
   stock target (A). This is small and every pass agreed.
2. **With it:** the salt break (thirst-driven through a hediff stage, needs no potable reachable, no re-entry while
   poisoned), slime last resort with recheck, purge hediff, per-kind effects as row data.
3. **Before sprinklers ship:** the per-net drinking reserve.
4. **First logistics building:** D (the bottler), or B if Q1 says station vessels count.
5. **When a liquid-burning machine needs it:** C's ports and bucket/barrel refuel jobs; bills as orders.

What would change it: Q1 = "station vessels count" swaps D for B (B needs no item-output path). A measured live
job count far below the estimates would let A stand alone longer.

## 7. Questions for the owner (card-ready, plain language)

**Q1. What counts as "drinking from a bottle" (no mood penalty)?**
- (a) Only real bottles. Taps, buckets and barrels always give the small penalty. *Most literal; to keep pawn chores
  down we build a bottling machine that fills and washes bottles off the pipes.* **← recommended:** keeps your words
  exactly and the machine makes it cheap.
- (b) A drinking station with cups or bottles beside the tap also counts. *Fewest chores and no extra machine, but
  stretches "bottles" to mean "a proper cup".*
- (c) Any piped tap counts; only drinking straight from a tank or barrel is penalised. *Rewards plumbing, but most
  built colonies would never see the penalty.*

**Q2. Is drinking from a pond or river penalty-free?**
- (a) Yes, free, like today; a pawn picks the nearer of a pond or a bottle. **← recommended:** matches the earlier
  ruling that pawns drink from rivers.
- (b) It counts as a "tap": small penalty unless hardy. *Makes bottles matter more on wet maps.*

**Q3. Who is hardy enough to skip the tap penalty?**
- (a) Ascetic only. *Narrow and obvious.*
- (b) Ascetic, Tough, Undergrounder. **← recommended:** "hardy" people, still a short list.
- (c) Also the strong-stomach and robust-digestion genes. *Easy for gene-builders, but those genes are about food
  poisoning and raw food, not about drinking from a barrel.*

**Q4. Who is "wild and uncivilized"?**
- (a) Wild people and animals only. *Simplest.*
- (b) Also tribal-faction pawns. **← recommended:** matches what RimWorld means by uncivilized.
- (c) Also our Jawas. *Flavourful, but Jawas are traders with machines, not a tribe.*

**Q5. When is there "no drinkable water", so slime is allowed?**
- (a) Nothing the pawn can reach right now (prison walls, forbidden stock and danger count against it); rechecked
  before each swallow. **← recommended:** a locked-up or stranded pawn can still be desperate.
- (b) None anywhere on the map. *Slime almost never happens in a colony; a prisoner with only slime just dehydrates.*
- Sub-question: should the Slime biome's own living slime also be drinkable this way (with its poison-cure and
  slow-conversion effects)? Yes / No.

**Q6. What does each slime do when drunk (on top of the big mood hit and a day of laxative)?**
- (a) Red burns the stomach (pain); green upsets the gut; white leaves a flammable coating (fire hurts more); yellow
  brings nausea. **← recommended:** follows each slime's existing description without inventing disease.
- (b) As (a), but green also rots something inside — *harsher, matches "nothing comes out the way it went in".*
- (c) Write-in your own per-kind effects.

**Q7. Can slime ever be bottled?**
- (a) No — drunk only from pools and tanks. **← recommended:** keeps it a desperate act, no slime stockpiles.
- (b) Yes, by order only. *Lets an expedition carry an emergency supply.*

**Q8. Salt water and its cousins.**
- Salt-water break: (a) extreme thirst alone can cause it, but only with no fresh water in reach, and not again while
  still salt-sick **← recommended** · (b) it also needs low mood, like other breaks *(rarer; a happy parched pawn
  never cracks).*
- Is brine the same as salt water (break only)? Yes / No (never drunk at all).
- Toxic water: (a) never drunk **← recommended** · (b) a last resort like slime.

**Q9. May pawns fetch non-drinkable liquid on their own for a machine that uses it (a still eating brine, a
generator eating chemfuel)?**
- (a) Yes, a bill on that machine counts as your order. **← recommended:** otherwise a salt-coast camp's stills sit
  empty.
- (b) No, every fetch needs a direct order. *Literal, but heavy micromanagement.*

**Q10. Does drinking water come first on a shared pipe network?**
- (a) Yes: sprinklers and machines stop when the tank drops to a reserve. **← recommended:** one sprinkler uses the
  daily water of roughly 80-140 colonists.
- (b) No, first come first served. *Simpler; crops can drink a colony dry.*

**Q11. With Dubs Bad Hygiene's thirst running, should the salt-water break and slime rules still apply?**
- (a) Yes, read Dubs' thirst bar for the break. *Same story in both modes; some code against Dubs.*
- (b) No, Dubs' thirst rules alone. **← recommended:** one boolean, nothing to break when Dubs updates.

**Q12. Smaller defaults — approve as a set or pick out any to change:** boiling water drinkable once cooled; no
eating ice or snow; sanguophages do not drink stored blood; animals drink only fresh pond/river water and never
slime or salt; brine kills a watered crop; buckets can fight fires.

## 8. Rulings (owner, 2026-10-17, by card; write-ins verbatim in quotes)

| Q | ruling | whose option |
|---|---|---|
| Q1 bottle | write-in: *"cups, piped taps, any civilized access. Only where it's awkward and difficult is penalized, like on travel or out in the field"* | owner's own; closest to (b)+(c) widened |
| Q2 ponds/rivers | (a) yes, free | M's rec |
| Q3 hardy | (b) Ascetic, Tough, Undergrounder | M's rec |
| Q4 uncivilized | (b) wild people, animals, tribals | M's rec |
| Q5 slime-when | write-in: *"It should follow the same rules for when people eat rotten food that makes them sick, whatever that is."* Sub: the Slime biome's living slime is drinkable by the same rules as other slime | owner's own |
| Q6 slime effects | write-in: *"Much worse. Red is Contagion: full mutation exposure right away. Green is full exposure to the absorption rules from that biome. White infects you with the Rot spores. Yellow is just nausea and vomiting."* | owner's own |
| Q7 slime bottling | (b) yes, by order only | against M's rec |
| Q8 salt | break needs thirst **plus** low mood, like other breaks (b); brine = salt, break only; toxic water = a last resort like slime, with toxic buildup | (b) against M's rec; toxic against M's rec |
| Q9 machine bill = order | (a) yes | M's rec |
| Q10 drinking reserve | (a) yes | M's rec |
| Q11 Dubs | **yes**: read Dubs' thirst; the salt break and slime rules still apply under Dubs | against M's rec |
| Q12 smaller defaults | **HOLD** — *"I'll go through them"* at a later sitting; the six stay open | — |

### 8.1 What the rulings change

**Q1 kills the "bottles first" premise.** The penalty is about **awkward access**, not about vessels. Civilized
access — a bottle, a cup, a piped tap, a tank or barrel tap at home — is free. The small penalty (`RM_Thought_
DrankRough`, −3, PROPOSED) fires only when drinking is awkward: on a caravan or travelling, out in the field away
from any civilized access (drinking from a carried bucket or barrel, scooping from a tank with no tap). Ponds and
rivers are free (Q2). Exempt: Ascetic, Tough, Undergrounder; wild people, animals, tribal-faction pawns (Q3, Q4).
Consequences: the bottler machine (option D) is **no longer needed for the penalty**; drinking stations (option B)
become the natural home drinking mode with no reinterpretation; bottles return to their travel/field job. The
job-count problem shrinks to the network: tap drinks are 1 job.

**Q5 mirrors vanilla's rotten-food rule** (MEASURED in decompiled `RimWorld/FoodUtility.cs:385-421` and
`JobGiver_GetFood.cs:74`, `CompRottable.cs:155`): non-fresh food is skipped unless the pawn is **desperate**, which
vanilla defines as hunger category `Starving` (need at 0); a desperate pawn still ranks better food first; wild men
and animals (`NonHumanlikeOrWildMan`) skip the restriction; eating it adds `AteRottenFood` and food poisoning
(cause `Rotten`). Mirror: slime and toxic water are eligible only when thirst is at its bottom category (need 0,
`Dehydrated`), always ranked below any potable source the normal search finds; the massive mood thought and the
purge hediff stand in for `AteRottenFood` and food poisoning. Whether wild people/animals also skip the restriction
for slime is one of Q12's held defaults ("animals never drink slime"), so it stays open. This **replaces** P1's
"no potable available" definition (§3.3 of the design) and drops the recheck machinery to vanilla's.

**Q6 ties slime to the three biome systems** (each effect reuses what that biome mod already has — search before
building): red → Contagion mod's mutation exposure at full; green → the Gelatinous Slime absorption
(`RM_Slimification` and the slime dose, `src/RimMandrake/GelatinousSlime`) at full; white → The Rot's spore
infection (`src/RimMandrake/TheRot`); yellow → nausea and vomiting only (vanilla `Vomit` job). On top: the massive
mood hit and the day-long laxative (ruled earlier). The design's mild per-kind table (§6 of the design) is void.

**Q7** adds slime bottles/buckets/barrels to the generator, filled **only by order** (the use class already blocks
auto-gather). **Q8** makes `RM_Break_DrinkBrine` an ordinary mood-pool mental break, eligible only when also
parched; brine and salt water both `BreakOnly`; toxic water moves to `LastResort` with `ToxicBuildup` as its effect.
**Q9** a bill on a still or machine authorises fetching its non-potable input. **Q10** per-net drinking reserve.
**Q11 reverses the recommendation**: under Dubs our code reads `DBHThirst`'s level for the break and the last-resort
gate, and our slime/salt/toxic consequences apply; Dubs' own drinking AI still chooses among potable drinks, and our
non-potable bottles keep `SeekForThirst false` so Dubs never picks them on its own.

### 8.2 The plan after the rulings (supersedes §6)

1. **Fix the two rule breaks in built code first:** auto-fill gathers any liquid (`WorkGiver_FillBottle` /
   `RM_LiquidBottleUtility.TryFindFillCell`, `requireFreshWaterOnly: false`); thirsty pawns drink salt water
   routinely (`RM_ThirstMath.Acceptable`/`Better`).
2. Use-class field on rows **and** terrain-only liquids/water items (source adapter); salt+brine BreakOnly, slimes and
   toxic LastResort, rest Never.
3. Awkward-access penalty with the Q3/Q4 exemptions; buckets, barrels and tank taps drinkable.
4. Last-resort gate mirroring vanilla's desperate rotten-food rule; mood + purge; per-kind effects wired to
   Contagion, Gelatinous Slime, The Rot; yellow nausea/vomiting; toxic → ToxicBuildup.
5. Salt break in the mood pool, gated on parched; relief then `RM_SaltPoisoning`; no re-entry while poisoned.
6. Slime containers, order-only. Bills as orders for machine inputs. Per-net drinking reserve.
7. Dubs mode: read `DBHThirst` for steps 4-5.
8. Batched fill/wash and a stock target remain (bottles still serve travel); drinking stations as the home mode;
   C's machine ports when a liquid-burning machine needs one. The bottler is dropped.
9. Q12's six defaults are **not built** until he rules them.
