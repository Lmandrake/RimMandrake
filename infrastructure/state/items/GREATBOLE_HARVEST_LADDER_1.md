# GREATBOLE_HARVEST_LADDER_1 — the greatbole harvest

**Spec: `design/Jawa/worldbuilding/biomes/kits/greatbole_harvest_spec.md`** — read it first; this item
is the ledger entry, not the design.

Ruled by the owner across four card rounds, 2026-09-23. ⛔ Nothing built.

## the shape in one table

| removed | event | tree afterwards |
|---|---|---|
| **40%** | The Great Shaking — fruit + grubs fall; interior damaged, pawns staggered | alive |
| **60%** | The violent healing — seals chambers, crushes what stays, **continues to 100%** | alive, fully restored |
| **70%** | The catastrophe — 50-cell crush radius, map permanently altered, huge yield, Wildsteam sacrilege | **dead, forever** |

🔑 **The organising rule both numbers fall out of:** below the line you mine faster than it heals;
above it, it heals faster than you mine.

🔴 **And the emergent consequence — do not codify it as a rule.** Past 60% a pick cannot keep up, so
**only explosives can reach 70%.** The mechanic makes the method compulsory without any rule saying so,
which is exactly how the owner described reaching it. ⛔ Adding a restriction that says "explosives
only" would replace an emergent truth with an arbitrary one.

## 🔑 Why this is far cheaper than it looks — MEASURED 2026-09-23

**Four of the six mechanisms it needs are already shipped**, and one of them answers a thing the owner
proposed as new:

- **`RM_ToxinSealant` (item + terrain) already gives permanent habitation**, and
  `RM_MapComponent_LivingRegrowth` already gates regrowth on the sealant terrain. His "special oil to
  seal a portion so it will not grow back" **exists and is wired.** Its description even already reads
  *"The living wood beneath cannot push through it, or close the cut you made."*
- **`BoleRecord.footprint` + `timers`** make "how much has been removed" computable today.
- **The creak-then-crush path** is the Shaking and the 60% event's engine, already shipped.
- **`RM_EatCleanableExtension`** already makes a *wild* race forage named items and consume them.
- ⚠️ **`RM_ParentalEnrageExtension`** guards *young*; the grub needs it widened to guard an **item**.
- ⚠️ **`RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` + its alert** already give interval
  breeding, soft/hard caps, an aggression curve that ramps between them, and a player-facing warning —
  its own framing is *"nuisance unless there are many."* ⛔ It does **not** gate on food; that is the gap.

⇒ The genuinely new work is the threshold ladder, two widened extensions, the fruit and its three
products, Royal Rind's protections, the seed's water rule, and the Wildsteam hooks. The spec's §9 lists
it.

## 🔴 Where the balance actually lives, because it is not where it usually is

**Nothing limits yield.** The fruit pays food, gear and the planet's best luxury material; the grubs pay
edible bugflesh *and* spines worth trading. The owner chose that knowingly — *"those grubs are NASTY to
deal with."*

⇒ **Difficulty is the entire bound**, and the dilemma is the brake: **take the fruit and you starve the
grubs into a manhunter swarm; leave it and you breed them into an army.** Both are bad, the player
chooses every harvest, and neither is a punishment for playing wrong.

⛔ **Therefore the grub fight may not be easy, and the population curve must be legible.** A brake
nobody can see is not a brake. ⚠️ If the fight is ever easy this becomes the most profitable loop in the
game.

## ✅ The Wildsteam angle needed no new fiction

MEASURED from their own live cast doc: the Wildsteam Clan's faith is the Green Oath — `NaturePrimacy`,
**`TreeConnection`**, `AnimalPersonhood` — and its **taboo is verbatim "cutting a living tree."** They
are the only faction that plants.

⇒ The catastrophe is a **sacrilege**, not a penalty. And the owner ruled the **seed is the atonement**:
planting a greatbole is their own sacrament performed by an outsider, and it is a real diplomatic route.
🔑 One fruit holds both the atrocity and the apology.

⚠️ Accepted cost: goodwill is farmable if seeds are plentiful. ⇒ Cap it, or tie it to the planted tree
**surviving** — which usefully makes a plant-then-fell player look exactly as cynical as they are.

## ✅ A third card round, 2026-09-23 — six additions, and two of them changed the design's shape

1. 🔑 **Fruitfall** — a random event dropping one or two fruits and a few grubs. **This is the piece that
   completes the economy:** without it the only route to fruit is wounding the tree, so any player who
   wanted Royal Rind had to commit sacrilege. Now the fruit has two routes with opposite costs —
   **patience or sacrilege.** ⛔ Neither may be strictly better.
2. 🔑 **Pilgrims come for the SONG.** *"They go from one to another to learn the wisdom each teaches in
   its song."* ⇒ The hum stops being a warning system and becomes the thing another faction crosses a
   planet to hear. **And their reaction is read off the tree's body, not off a counter:** sap-sealed rooms
   don't count against the player, open regrowing cuts are **wounds** (furious, or enraged), and
   **witnessing a Great Shaking makes them attack outright.** ⇒ Sealing is morally as well as practically
   correct, a fully regrown cut is genuine atonement, and the worst thing a player can do is be *seen*
   mid-harvest. 🔴 Generic pilgrims without the Utinni scenario, so `RM_` tier with a campaign skin.
3. **The song, specified**: ultra-deep bass that slowly drifts, **pitch rises with every cut** (physically
   right — a hollower body rings higher), two disharmonious sounds overlapping near a threshold, the
   harmonious blend returning only as the tree heals, and a genuinely unpleasant **beat frequency** near
   breaking. ⇒ This gives the invisible 40% threshold the perceptible warning the owner had accepted doing
   without. ⚠️ The beat specifically may not be achievable from two live sustainers (phase randomisation);
   fallback is baking it into one authored file.
4. **Thermal sanctuary**: chambers hold **deep-ground temperature**, because *"all the water coursing
   through the tree's flesh upwards"* is a permanent thermal blanket. 🔑 Same fact explains why a **seed
   needs adjacent water** — both ends of the species' life run on one sap column.
5. **The fruit is hauled one at a time**, and **purple grubs read like purple fruit**. Taken together
   deliberately: a slow hauler approaching a pile that might not be only fruit *is* the ambush.
6. ⛔ **Fire cannot excavate it** — the heartwood is too dense to burn out. A cheap slow burn route would
   have deleted the explosives-only consequence, which is the best emergent detail in the design.
7. **The root causeways survive the tree** — dead roots are still roads. Zero work, and the catastrophe's
   permanent alteration stays the crater, the fallen trunk field and the standing husk.

## ✅ Two OPT-IN crossovers, ruled 2026-09-23 — anima focus and arboreal servants

**Yes to either, or even both — as Mod Settings toggles, DEFAULT OFF.** Utinni ships with both off, so
⛔ **no campaign mechanic, quest or balance assumption may depend on either.** Spec §8b.

- **Anima:** the greatbole grows the grass and is a meditation focus. 🔑 It marries the song and the moral
  ledger — grass only on uncut ground, and (if achievable) **focus quality tracking the tree's harmony**,
  so the dissonance a player hears at a threshold is the dissonance that ruins their psycasting.
  ⚠️ **Ship the fixed-strength focus first**; runtime-variable strength is unmeasured, and being
  default-off means the simple version blocks nothing.
- **Servants:** arboreal helpers a connected colonist directs. ⚠️ I objected that they compete with the
  hostile grubs, which are this feature's only balance brake — the objection holds when the *design*
  chooses and dissolves when the *player* does.
- **Both on:** no mechanical conflict. 🔑 Servants and grubs **will fight**, and that is expected
  behaviour to document rather than suppress. ⛔ The grubs stay hostile in every configuration; they
  belong to the fruit, not the tree.

🔴 **A process note worth keeping, because it recurred twice in one session.** He asked *"could we wire it
as an anima tree… or alternatively the servants?"* and I built a four-way pick-one card. He had meant
**both, as options**. Same shape as the tier question earlier the same night: a request framed loosely got
adjudicated into a decision that did not need making. ⇒ **When he asks "could we also do X or Y", check
whether he means "as options" before designing a choice between them.**

## ✅ Desktop answer to spec §10 question 1 — MEASURED from the decompiled engine (RimSage), 2026-09-23

**Q: can a plant's growth rate read adjacent terrain? YES, with a `Plant` subclass — not from XML alone.**

- `Plant.GrowthRate` is **`public virtual float GrowthRate`** (RimWorld/Plant.cs:289-303). Vanilla returns
  `GrowthRateFactor_Fertility * _Temperature * _Light * _NoxiousHaze * _Drought`, and `GrowthRateFactor_Fertility`
  reads **only the plant's own cell**: `PlantUtility.GrowthRateFactorFor_Fertility(def, base.Map.fertilityGrid.FertilityAt(base.Position))` (:350).
- `GrowthPerTick` (:334-347) multiplies by `GrowthRate` — the virtual — so an override is honoured by the growth tick
  (`growthInt += GrowthPerTick * 2000f`, :822) and by the "time to grow" readout (:421-426).
- ⇒ A `thingClass` deriving from `Plant` that overrides `GrowthRate` and multiplies in a factor read from
  `GenAdj.CellsAdjacent8Way(this)` → `Map.terrainGrid.TerrainAt(c)` (or `fertilityGrid.FertilityAt(c)`) expresses §3c's
  "seed needs water beside it" exactly. Also override `GrowthRateCalcDesc` (virtual, :305) so the inspect string shows the
  water factor, or the player sees a slow plant with no explanation.
- Cost: one C# class in the biome mod (Greentide kit assembly), no Harmony. Nothing in the engine forbids it.

`needs` moves from `game-up` to `offline`: this was the one question that could have come back "not expressible", and it
did not. The remaining 13 engine questions in §10 are the same shape (read the code, not the game) and are Desktop-RimSage
work, not game-up work.

## spec

Follow the spec document. Order, because it front-loads what can fail:

1. **Answer the spec's §7 unmeasured questions on the Desktop.** ⛔ Nothing authored first. The largest
   is whether a plant's growth rate can read adjacent terrain — §3c's whole appeal rests on it. ✅ **ANSWERED 2026-09-23: YES, via a `Plant` subclass overriding the virtual `GrowthRate` — see the Desktop answer section.**
2. **The threshold ladder and the three events**, on the existing footprint/timer data.
3. **Widen the two generic extensions** (guard-a-thing; breed-while-fed + manhunter-on-famine) in
   `mandrake.rm.creaturebehaviors`. ⛔ Content stays in a content mod — that assembly ships none.
4. **The fruit, the butcher recipes, the three products.**
5. **Royal Rind's protections**, ours first, the expansion-gated vacuum variant second.
6. **The seed**, its water requirement, and the Wildsteam hooks both directions.
7. **Gorbeleth toxin as the sealant's reagent** — cheap, and it makes an already-written line true.
8. Mod Settings per the standing rule: all three thresholds, plus toggles for the catastrophe and the
   breeding.

## verify

The three thresholds fire at 40/60/70 and each reads as the tree answering more loudly. A sealed chamber
still survives a living tree; a dead husk never fruits again. Grubs contest the fruit, breed while fed,
and turn manhunter when starved. Planting moves Wildsteam one way and the catastrophe moves it the
other. ⛔ No live-proven claim from the Mac, and ⚠️ the grub difficulty is judged by playing.

## criteria

You stand at the edge of a hole you made in a living thing and decide whether to take one more chamber.

## Watch out

- 🔴 **The 50-cell blast radius is bigger than most players' whole base**, so a colony near a greatbole
  is inside it. That is the intent — but the 70% threshold must be **unreachable by accident**. The
  explosives-only consequence already helps; do not weaken it.
- 🔴 **Regrowth state is Scribed, and this is live shipped content.** Changing the footprint, radius or
  def names risks existing saves. ⛔ Not a draft.
- ⚠️ **`FEVER_WOOD_MECHANICS_1` is blocked on `RM_MapComponent_LivingRegrowth`** (F7, bore-caves /
  Greatbole reuse) and `RUT_FeverTrunkCore` is a sibling on the same machinery. ⛔ Everything added must
  stay content-blind; that component names no bole, no biome and no Greentide today.
- ⚠️ **The 60% event can kill a colonist who was merely standing somewhere.** Per-cell creaks already
  exist, but the whole-bole event needs one unmissable signal — a player not watching that chamber must
  still be told.
- 🔑 **Say which greatbole def you mean, every time.** The species is three things — `RM_Greatbole` the
  mature fellable tree, `RUT_GreatboleHeartwood` the mineable blob, `RUT_GreatboleCore` the 1×1
  bookkeeping marker. Confusing them has already misled two design passes in one session
  (`GREATBOLE_BARK_EDGE_ART_1`).
