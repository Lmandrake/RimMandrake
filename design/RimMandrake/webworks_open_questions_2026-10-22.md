# The Webwork: open questions for the owner (2026-10-22)

Written by FOUNDRY, offline, while the owner slept. Each question is a card: pick a number, or
write in something else. Every card names what the evidence says, where it says it, and one
recommendation with one line of why.

Thu Oct 22, 12:07 AM PDT

**What the Webwork is, in one paragraph (so the cards read cold).** The Webwork is our jungle biome,
mod `mandrake.rm.webwork` (`src/RimMandrake/Webwork/`). It is owned by the **ollathrix**: a giant
web-spinning predator that dies in open sun ("sun-scald") and so lives under the canopy. The biome
ships 6 animals (the ollathrix plus 5 invented residents), 17 plants, a guaranteed ollathrix **nest**
on every Webwork map (it lays inert, sellable eggs), a web network laid across the map (cables you
climb slowly, sticky local webs, silk carpet near spider sites), a **webfall** weather, the
**urraveth remains** (a dead giant the spiders ate, read bone by bone), and the **traction lance** (a
crewed emplacement that reels a pawn in on a fabric tether). Its silk is **thrixweave**: vanilla
hyperweave renamed, sold by no trader. Your north star for it (2026-10-20): *"So quiet that you know
you're in terrible danger. It makes treasure, it eats all, and it's coming for you."*

**Terms used below.** *BiomeDef*: the game's definition of a biome (its animals, plants, weather).
*Mod Settings*: the options screen every mod ships. *RM_ / RUT_*: our free tier (no Star Wars) and
our campaign tier (Star Wars). *Frozen twin*: `RUT_Webwork`, the older copy of this biome that sits
on today's frozen world; `RM_Webwork` is the new one. *End paint*: the one-time repaint of the
planet once every biome is built (your ruling: a biome on zero tiles until then is expected).

---

## Q1. Should the Webwork be able to appear on a newly generated world at all?

**What was found.** The Webwork carries a *biome worker* (`RM_BiomeWorker_Webwork`): code the game
calls during world generation to score each tile and decide where a biome goes. It is switched by a
Mod Setting, "Let the Webwork generate on new worlds", **on by default**. The code comment
justifies it: *"this mod ships for everyone else's generated planets ... CLAUDE.md 'no worldgen
feature' is about that world specifically."* Your rulings say otherwise: worldgen as a
player-facing capability is **out, permanently**, and *"Players never generate anything. They
receive a savegame holding the fixed world."* On our frozen world this code does nothing at all
(the script records it as inert). Other biome mods (the Greentide, the Pyrelands) copy the same
pattern, so the answer probably applies to all of them.

1. **Delete the biome worker and the setting, in every biome mod.** Buys: the code obeys the ruling
   with no reading between the lines; one less setting that does nothing in our game. Costs: a
   player who installs the free-tier mod alone into an ordinary game gets a biome that never
   appears anywhere; the mod is useful only inside our savegame.
2. **Keep it, default OFF, labelled "unsupported: for worlds you generate yourself".** Buys: the
   free mods still work for someone who generates their own planet, at no promise from us; matches
   how you treated cross-biome switches on 2026-10-15 (exist, off, labelled). Costs: we keep
   shipping worldgen code we have promised never to test; the comment's wrong reading of the
   ruling must still be corrected.
3. **Keep it as it is (on by default).** Buys: nothing to change; free-tier players get the biome
   on their own planets. Costs: it contradicts the ruling as written, and a player sees a
   worldgen-affecting option we never validate.
4. **Keep the code, remove the setting, worker always on.** Buys: no confusing option. Costs: the
   worst of both: the worldgen behaviour stays and nobody can turn it off.

**Recommended: 2.** It is the shape you already ruled for cross-biome switches, and it keeps the
free mods usable outside our save without promising anything.

---

## Q2. May the web creep out of the Webwork onto the maps next to it?

**What was found.** The *front creep* (`RM_MapComponent_FrontCreep`, Mod Setting "The web creeps
out over the border", **on by default** in both the Webwork's and Creature Behaviours' settings)
advances Webwork structures (anchors, webs, gutters) onto **any map whose tile borders a Webwork
tile**, about one band a day, up to 10 cells deep. That map may be another biome entirely. On
2026-10-15 you ruled: *"We can't guarantee they will work in other biomes beyond our framework"*:
build no new cross-biome switch; existing ones stay, **off**, labelled unsupported. The front creep
predates that ruling, so today it is an existing cross-biome mechanic that is still on. Its numbers
are also unruled (`advanceIntervalTicks`, `maxBandDepth`, `spawnDensity` are marked invented).

1. **Turn it off by default and label it unsupported**, per the 2026-10-15 ruling. Buys:
   consistent with the ruling; no Webwork content shows up on, say, a Stillsand map we never
   tested. Costs: loses the strongest in-game form of *"it's coming for you"*: the jungle visibly
   advancing on your neighbours.
2. **Keep it on, but only onto maps of OUR biomes** (the creep checks the neighbour is one of our
   BiomeDefs). Buys: keeps the menace; stays inside the framework we validate. Costs: new code and
   one more check to prove; a border with a vanilla biome simply never creeps, which may read as
   arbitrary.
3. **Keep it on everywhere (an exception to the 2026-10-15 ruling).** Buys: the fullest version
   of the fiction. Costs: we ship a cross-biome effect we promised not to guarantee; any bug lands
   on maps that are not ours.
4. **Delete it.** Buys: least code, no exception. Costs: the mechanic is built and wired; its
   menace has no replacement.

**Recommended: 2.** It keeps the north star's "it's coming for you" while staying inside the
biomes we test.

---

## Q3. The "titan passage" wants a living giant in the Webwork; the Webwork sitting banned one

**What was found.** Two of your rulings pull opposite ways. On 2026-10-02, by question card, you
chose **the dead giant the spiders ate** (the urraveth remains) and the item says *"Not the living
morravell: it was not chosen and is not to be built. No living giant."* On 2026-10-21 the *titan
passage* (a mechanic where a huge creature walks through a map, drawn from the biome's own animals
or a "passers" list of visiting giants) found no giant to draw in the Webwork, and you said:
*"Every biome should have something like this."* The ollathrix is ruled one race, one kind, so it
cannot simply be made bigger.

1. **The Webwork is the one biome with no titan passage; its giant is the dead one.** Buys: honours
   the Webwork sitting exactly; the urraveth already says "the spiders eat giants here". Costs:
   breaks "every biome should have something like this".
2. **A passers list: a giant from a neighbouring biome sometimes wanders in** (it stays homed in
   its own biome, so the one-biome rule holds). Buys: a titan passage with no new creature and no
   living Webwork giant; a passing giant that the web may catch is the urraveth's story happening
   live. Costs: a giant not built for jungle; it must not die so fast it reads as a bug.
3. **Build a new living Webwork giant after all** (the morravell, or another). Buys: the biome gets
   its own titan, like the others. Costs: reverses the 2026-10-02 ruling; new creature, new art.
4. **A titan passage where the giant is already wrapped:** a web-carried carcass dragged across
   the map by the ollathrix. Buys: keeps "no living giant" and gives the biome a passage of its
   own. Costs: a new mechanic, not a reuse of the titan passage; more design.

**Recommended: 2.** It satisfies both rulings at once with content that already exists.

---

## Q4. The Felled Noon rite needs dangerous sun, but the Webwork may get no sun at all

**What was found.** *The Felled Noon* is a ruled rite for Sh'kaar, the hungry sun (campaign tier,
not built): participants fell the tallest tree and stand bare-headed in the sunlit hole it leaves,
while the ollathrix pace the shade line around them. Its risk is **Direct Sun**, your
2026-10-19 model: sun heat is a function of geometry only, the same on every map. That model is
**not built yet**, and you also said it runs on tree-heavy maps only if the tree shade model is
excellent: *"Without one, it is turned off on tree-heavy maps"*. The Webwork is one of five
tree-heavy day-side biomes. Separately, the shade grid the ollathrix's sun-scald reads today came
from the per-biome heat work that Direct Sun undoes. So the rite's danger, and the
ollathrix's fear of sun, both hang on the tree shade model.

1. **Hold the rite until the tree shade model ships, then build it as ruled.** Buys: one honest
   version, no rework. Costs: the rite waits on a large, unscheduled build.
2. **Build the rite now with sun-scald (the ollathrix) as the only danger, and add Direct Sun
   when it exists.** Buys: playable soon; the ring of predators at the shade line is the drama
   anyway. Costs: the participants' own risk is missing at first; "the hungry sun" rite without a
   hungry sun.
3. **Move the rite's danger off the sun entirely** (the felling wakes the web; the danger is the
   gathering). Buys: no dependency on any sun model. Costs: changes the rite's meaning; Sh'kaar's
   rite no longer involves exposure.
4. **Make the Webwork the first map the tree shade model must handle** (it becomes the test case).
   Buys: the rite and the scald drive the shade work directly. Costs: commits the shade model's
   first sitting to the Webwork before other biomes.

**Recommended: 2.** The ollathrix at the shade line is the rite's spectacle, and it already works
from the shade grid; the participants' sun risk can arrive later without a rebuild.

---

## Q5. At the end paint, which Webwork gets painted: the new one or the frozen twin?

**What was found.** Two Webwork biome definitions exist. `RM_Webwork` (new) has 6 animals, all
invented and all ours. `RUT_Webwork` (the frozen twin on today's world, never edited) still has
the older cast: the ollathrix plus three Star Wars donor animals (the jewel beetle, the kreetle, the
shyrack) that the 2026-09-24 sitting **cut** from the Webwork. The jewel beetle also lives in the
Fever Wood (an animal in two biomes). Your shade-model table even shows the two twins with
different canopies (0.35 against 0.64 tree cover). Nothing written says which one the end paint
lays down.

1. **Paint `RM_Webwork`; retire `RUT_Webwork` at the paint.** Buys: the ruled roster is the one
   players meet; the cut animals finally leave; the one-biome rule holds. Costs: campaign players
   lose the three Star Wars animals here unless a later patch adds canon ones back.
2. **Paint `RUT_Webwork`, but update it to match `RM_Webwork` first.** Buys: keeps the campaign
   biome's name and identity. Costs: two definitions to keep in step forever; editing a frozen def.
3. **Paint `RM_Webwork`, and let the campaign layer add canon animals through a patch** (the way
   the tooke-trap plant is added today). Buys: one biome, free tier whole, Star Wars on top. Costs:
   needs a new roster decision for which canon animals, if any, belong; the sitting cut all three.

**Recommended: 1.** It is what the sitting ruled, and option 3 stays open later without blocking it.

---

## Q6. The egg black market's selling channel has waited four weeks on a trade window that does not exist

**What was found.** Ollathrix eggs are inert contraband: you can only sell them. The ruled design
(2026-09-24) sells them two ways: a Hutt Cartel caravan (**built**), and a **broker tab** in the
Bazaar trade window that pays a jackpot without waiting for a caravan. The Bazaar's tabs have never
been built (its window is not even wired to open), so the broker channel has been blocked since
2026-09-26. Engine fact: the game's normal pricing never pays a premium when the player sells, so
any jackpot needs its own price code wherever it lives.

1. **Keep waiting for the Bazaar's tabs.** Buys: the design as ruled. Costs: no date; the jackpot
   stays missing.
2. **Build the broker as a comms-console contact instead** (call a broker, sell eggs at a premium,
   a shuttle collects them). Buys: ships now on vanilla parts. Costs: a second selling surface the
   Bazaar would later duplicate.
3. **Make it a quest: a broker asks for N eggs by a deadline, for a large payout.** Buys: uses the
   quest system, which exists; gives the jackpot a story. Costs: you cannot sell whenever you
   want; a quest is a different feeling from a market.
4. **Drop the broker; the caravan is the market.** Buys: nothing more to build. Costs: the "cash
   out without waiting" fantasy is gone.

**Recommended: 3.** It delivers the jackpot now with machinery that exists and suits contraband,
and the Bazaar tab can still come later.

---

## Q7. How should "so quiet you know you're in terrible danger" be judged?

**What was found.** You wrote the experience line on 2026-10-20; no north-star bars (your own
pass/fail lines, which only you validate) exist yet. The build mostly fits *quiet*: the Webwork's
animal density is **1.0** against vanilla rainforest's **5.4**, and its ambient sound is a near
silence bed. But it also has six species, a guaranteed nest on every map, ollathrix that can burst
out when you destroy web-harvest things, and a creeping web, so "quiet" and "it's coming for you"
compete. Which of these does the bar measure?

1. **Quiet means few animals seen**: a bar on how many living animals are visible on arrival
   (low), with the ollathrix unseen until something wakes them. Buys: easy to measure and to
   tune. Costs: it measures emptiness, not dread.
2. **Quiet means quiet until you act**: bars that pass when nothing attacks in the first days
   unless the colony cuts web, mines the nest or enters canopy, and then something always comes.
   Buys: the danger is a reaction to the player, which is what "you know you're in danger" means.
   Costs: harder to test (needs a short scripted sequence per trigger).
3. **Quiet means sound**: a bar on the soundscape (the hush plays; the web-thrum plays when the web
   is touched). Buys: cheapest; matches the line literally. Costs: says nothing about play.
4. **No bars; you judge it by playing it.** Buys: the feeling is yours to judge. Costs: nothing
   protects it from a later change that makes the jungle noisy.

**Recommended: 2.** It turns your sentence into cause and effect, which is what a bar can protect.

---

## Q8. Should one biome be the game's only source of hyperweave?

**What was found.** The Webwork renames vanilla **hyperweave** to *thrixweave* in every game that
loads it, and (Mod Setting on by default) strips it from every trader and quest reward, so the
only way to get it is to cut it in the Webwork. It is also the strongest tether for the traction
lance. Until the end paint the Webwork is on zero tiles, and after it the Webwork may be one
region far from the player. So the law forecloses hyperweave for any colony that never reaches the
Webwork: hyperweave clothing and armour, and the best tether, become Webwork-only.

1. **Keep the sole-source law as built.** Buys: the Webwork "makes treasure", exactly your line;
   a reason to go there. Costs: a whole vanilla material tier disappears for colonies that never
   go; nobody may ever trade for it.
2. **Sole source for buying, but rare traders resell it at a steep price.** Buys: still treasure,
   still the Webwork's, but not a hard lock. Costs: weakens the reason to go; one more number.
3. **Keep vanilla hyperweave; make thrixweave a new, separate, better fabric.** Buys: vanilla
   balance untouched; the Webwork adds rather than removes. Costs: a new material with its own
   art and stats; every recipe would need to choose; the rename and strip are undone.

**Recommended: 1.** It is your north star's "it makes treasure" made literal, and the Mod Setting
already lets a player turn the strip off.
