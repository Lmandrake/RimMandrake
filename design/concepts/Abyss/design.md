# The Abyss: the design, seen from the ship

**Status:** the one design document for the Abyss biome (`RM_Abyss`, source `src/RimMandrake/Abyss/`), rewritten
2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the older
definition sheet, cast bible, review and cleanse proposal as the place to read; what happened to every idea in them
is in `design/concepts/Abyss/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and
it launches nothing.

**A correction to this pass's own brief.** The brief called the Abyss "a sea biome: the ship is the only way down
and back". It is not. Every source describes a dark highland: *"obsidian teeth in a fog that light cannot cross"*.
The seabed rulings do not apply here. (The Abyss does have a fishery, by the owner's mark of 2026-11-17; it is in
mineral pools on land.)

**What the owner had already approved.** On 2026-11-17 he walked the cleanse proposal for the Abyss and approved its
scope with four marks (`cleanse/owner_marks.md`): *"I saw how much you put into 0.2.0 Impressive, and the right
call. It's still a daunting mod even with that you chose to keep in 0.1.0. I approve."* This design keeps that
scope and his four marks, and makes **one** move against it, which is the first thing under `NEEDS HIM`: the hidden
ship comes forward into 0.1.0.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Abyss/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A country of obsidian-black stone twisted into shapes no wind carved, drowned in a darkness that behaves like a
> substance: it fills the air, it pools, it parts without warning into pockets of impossibly clear air, and it
> closes again. Light does not fail here for lack of a sun — light is eaten in transit."* (`abyss.md` §1)

The owner's own line for the experience, typed 2026-10-20:

> *"The dark is a palpable tide that protects you yet conceals terrors close by. Wonders emerge just as often for
> moments of transcendent beauty, only to twist into nightmares just as swiftly. You fear staying here too long will
> find the source of the nightmares themselves."*

**Seen from the ship, the Abyss is the one biome that was about the ship from the start.** His concept of
2026-08-13: *"'Hiding' your gravship from pursuit is a big deal in this campaign."* The sheet's ruling: *"this is
one of the few biomes that measurably slows Imperial pursuit... no orbital eyes, no long lances; pursuit drops to
walking pace and short knives."* And its star: *"The sensor shadow — the place to run to when the Empire is close.
Refuge priced in darkness, breakage and cold."*

So the Abyss turns the other biomes inside out. Everywhere else the question is what a crew can see in a week
before the Empire arrives. Here the crew came *because* the Empire is close, the Empire is slow to come, and the
question is how long they dare stay. The design note that first worked his hiding idea out set the two rules this
document keeps: *"The hiding place must be poor"*, and *"it must not be permanent."*

And it gives the place its central bargain, which is already built: **light keeps the things in the Dark off you,
and light is what gives the ship away.**

The crew are small, hooded, weak in a brawl and evolved for the dune sea. This is the cold side of the world. The
Jawa see well in ordinary darkness. This is not ordinary darkness: it is in the air, and the sheet's ban is flat,
*"no clean sensing"*. (`UNMEASURED`: whether the built sight penalty already ignores the xenotype's dark vision.
The intent is that it gives them no pass.)

## The clock here is different

The Empire's search restarts at every landing: a probe droid five to eight days after landing, then scouts, a
strike, a cordon, a breach, a bombardment (`src/RimUtinni/EmpirePursuit/`; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers provisional). The Abyss is on the
pursuit's built list of poorly surveyed biomes, which multiplies every wait by four; the note of his 2026-08-28 ruling
(`design/Jawa/mods/ruthless_faction_pursuit.md`) records his figure for such refuges as 20 to 30 days. The ladder's own arithmetic: *"A Hidden clan on an Abyss tile
therefore gets roughly 40–64 days between rungs."*

**UNSETTLED: how long a stay lasts.** Assumed here: three weeks to two months before the first Imperial contact,
depending on how quiet the crew keeps. A season is fifteen days, so **the Abyss is the one stop where seasons pass
and slow things can be seen**: a crop under a lamp tree, stone wearing away, a crew getting used to the dark.

---

## The first minutes

The ship comes down past the terminator into air that eats its running lights. Every lamp aboard reaches a
fraction of what it reached an hour ago. Sound is muffled. There is no wind at all.

What the player sees is dim country with its outlines kept: black etched rock, dark sand, and the land's own
lamps, *"lit like a harbor at night"*: blue glow against yellow, a carpet of glowing grass.

Then the first gust arrives *"like an impact"*, and every gharrek on the map opens at once: flat, plate-shelled
crawlers that were invisible on the obsidian lift their shells and show *"a map-wide carpet of fluttering
gill-fans"* with a faint chemical glow, feed on the stirred air, and shut. Then stillness again.

The crew's first decision is in front of them before the ramp is down: how many lights to leave on.

## The first days

- **Warmth clears the air.** A heated room is clear inside while the Dark stands at its open door. The ship's warm
  rooms are islands. Cold rooms fill.
- **Lamps shrink; living light does not.** Artificial light reaches less the thicker the Dark. The glow plants
  resist it. A lamp tree (wickwood) can be dug up and replanted beside the ship; glowberries, once picked, are a
  light a crew member carries.
- **The moths come to the light.** Krizzaks are soft dark moth-things *"with a mouth like a lamp-glass"*. They eat
  light. They settle on lamps and glow plants and the lit radius shrinks: *"a perimeter going dark one lamp at a
  time is the warning."* They scatter from heat. They really fly.
- **Something waits for the lamp to fail.** The ishvarith, one of the Abyss's family of pitch-black, yellow-eyed
  things, will not cross firelight or a heated space. Light is a wall against it until the moths eat the wall.
- **The rattle.** The ombrathia hunts by the tremor of movement; its quills pick it up, and it *"raises them in a
  clattering hackle"* before it lunges. The rattle is the warning and it comes before the attack, not after.
- **The grip.** The saevitha has no mouth. It kills by holding on and draining warmth.
- **The grain.** The Dark, where it dies, falls as fine corrosive grain. It wears unroofed stone and steel, and it
  leaves a rust-brown oily dust, tholin, that sweeps up and refines to fuel. *"Roof everything"*, and feed the
  heaters with what fell on the roof.
- **The poor larder.** Berries, a slow black-and-violet fungus that grows only where grain has eaten the rock,
  milk and meat from the herds, and what can be fished from the mineral pools: black ribbon swimmers with pale
  hinged jaws, and things that ripple along the bottom. Each catch is also alive in the pool, moving.

## The first weeks

- **The hidden ship.** While the ship sits with its engine cold and few lamps lit, cover builds: the search loses
  it. Starting the engine tears the cover away. Every lamp lit for the farm, the perimeter or the workshop is
  weighed against it. (Built as `RM_MapComponentShipCover`; in the campaign layer, by his card of 2026-10-01 that
  the free tier gets no ship touch.)
- **Probes still come.** His words, typed 2026-09-30: *"Yes but probe droids will still come that must be
  avoided."* A probe drifts in under the Dark looking for movement and light. The crew beats it by being still,
  dark and cold, or by destroying it before it reports. A probe that reports collapses the cover, and the search
  resumes at its ordinary pace: the Abyss becomes a five-to-eight-day stop like any other.
- **Farming by lamp.** Crops grow under a lamp tree if they are also kept warm. Food is the reason to light up,
  and lighting up is the cost. This is the hide's real ration.
- **The lane.** Ordinary research at the bench teaches heat-folding, and the fold lamp: a fuelled heater-lamp with
  a throat that holds a lane of clear air open, stopped by walls and fading with distance. The review's phrase for it: *"explicitly a heater
  that clears air, not a magical sensor."* It is the only clean line of sight on the map, and the crew chooses where
  it points.
- **The Unveiling.** Rarely the Dark folds away wholesale and *"the actual map shows itself, naked and lit — then
  it simply folds back. The one moment you see what country you have been living in."* When it closes, the lamps
  shrink again, the moths return, and whatever was waiting is nearer than it was.
- **The wear.** Weeks of grain on anything left unroofed. The hide is paid for in roofing, fuel, cold and the
  things the crew is not salvaging while it sits here.

## "OMG did you see that?"

Each can happen inside a stay. Each says what is on screen.

1. **The ground opens its gills.** *On screen:* dead-still black rock, a gust, and the whole map flutters and
   glows for a few seconds. *Why it lands:* nobody knew anything was there.
2. **The lamps go out one at a time.** *On screen:* moths settling on the perimeter lights, each circle of light
   drawing in; a hooded figure with a torch chasing them off one lamp while the next dims. *Why it is alarming:*
   yellow eyes at the edge of the last circle.
3. **The rattle.** *On screen:* a crown of banded quills rising out of the dark with a clatter, a beat, and the
   lunge. *Why it works:* the player had the beat.
4. **Fishing.** *On screen:* a Jawa hauls a black ribbon with pale hinged jaws out of a mineral pool, and the pool
   is visibly full of more of them. His mark: *"YES TO FISH (WEIRD CREATURES)!"*
5. **The vine turns.** *On screen:* the paddle vines along the hull slowly face the one lamp left on.
6. **The helper.** *On screen:* a tamed sorter, stoop-backed, long-fingered, carrying one small item to the
   stockpile *"at a crawl"*, with great seriousness. A scavenger crew has found the only creature on the planet
   that likes tidying.
7. **The Unveiling.** *On screen:* the Dark lifts and the country stands lit, etched and enormous, for a few
   hours. *Why it is beautiful, and why it twists:* it closes.
8. **The probe.** *On screen:* a probe droid drifting between the crags, the ship dark, every crew member
   standing still. *Why it is funny:* someone left a lamp on in the galley.

## When the Empire arrives

It arrives late, and it arrives into the same Dark.

- **Nobody shoots far.** The Dark cuts sight and aim for everyone on foot, and intervening Dark spoils a shot even
  from clear air. The owner's phrase: *"walking pace and short knives."* For a crew that is *"weak in melee"* this
  cuts both ways, and the design keeps that.
- **The Empire's lights are eaten too.** A lit camp draws the moths; a camp going dark draws what waits for lamps
  to fail. A siege that has to sit in place for two days sits in the Abyss for two days.
- **The crew owns the only clear lane.** A fold lamp pointed down the approach is a firing lane the strike team
  does not have.
- **The grain falls on their steel as well.**
- **The Unveiling is nobody's friend.** For a few hours everyone can see everyone.
- **Launching ends the hide.** The engine tears the cover away. Leaving is the loud option, and it is always open.

## Who else attacks; who hates the Empire

- **What lives in the Dark,** impartially: the light-eaters, the thing that fears light, the quill-hunter, the
  warmth-drainer, and herd animals that turn on whoever hurts them.
- **People who hate the Empire have been here before.** The sheet lists *"fugitive holds — smuggler caches and
  bolt-holes of everyone the Empire ever chased into the sensor shadow; some still occupied, some now just supplies
  in the dark."* Nothing builds them yet. They are the natural answer to "who here might fight the Empire" and they
  are in "later", campaign layer.
- **The Nhaleth never appear.** The visitors who come for the Dark are a rumour: *"sworn to by nobody credible,
  believed by everybody a little."* No faction, no pawn, no certain structure, in any version.
- *0.2.0:* in a Witchfire storm, a summ may come down and cross the map. *"A storm does not bring the summ; the
  summ brings the storm."*

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The hide is poor. Food, fuel and warmth run down, and nothing here is the salvage the campaign is about.
- The grain eats what is left outside.
- A lit farm and a hidden ship cannot both be had in full.
- A probe that got its report out.
- *0.2.0:* the dread. *"You fear staying here too long will find the source of the nightmares themselves."* The
  free tier's whisper about the Nhaleth is that they *"are not visitors at all. They are whoever stays"*, and its
  sign after a long stay is a dream: *"Dreamt I didn't need the light."* For a crew in hiding, the rumour is about
  them.

**Stay, longer than anywhere else:**
- The pursuit's fourfold delay, and the cover on top of it.
- Warm rooms, living lamps, roofed work, fuel swept off the ground.
- Stillness when a probe is on the map.

## What the crew takes away

- **Time.** The weeks the Empire spent not finding them. It is the real product of the stop.
- **Fuel.** Tholin swept up and refined (built: it becomes chemfuel).
- **The fold lamp,** as knowledge: *"useful as a cold-night lamp anywhere."*
- **A lamp tree** dug up and carried; **glowberries**, a light in the hand.
- **Etchcap,** a delicacy and a trade good, slow and scarce.
- **Animals:** a pack beast, a milker, a sorter that tidies.
- *0.2.0, from Lightfall only:* parts cut from the rescue ship in the chasm wall to restore the crew's own (his
  words: *"You can't have two ships but you can cannibalize that one to improve yours. A rich haul. But only then do
  they discover that their ship only wants certain parts. It likes what it is and doesn't want deep redesign. Just
  repair."*); an egg; and a great bone to stand on the deck so the egg will bond.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The Dark dims the country and wild creatures but keeps their outlines; the crew stays fully drawn. | A predator, a rock face and a crew member at the same distance, in thick Dark and in a warm room. | A predator hidden entirely fails. A sky tint with nothing else dimmed fails. |
| Sight and aim suffer in the Dark, and a shot through intervening Dark suffers even from clear air. | A shooter in a warm clear room firing out through the Dark at a marked target; then the same shot down a fold-lamp lane. | The same room and target with the Dark switched off. |
| Warm rooms are clear; cold rooms are not. | Two rooms, one heated; open the heated one to the cold. | Temperature is the only thing changed. |
| Lamps reach less in the Dark; living lamps hold. | An electric lamp and a lamp tree side by side, in thin and thick Dark. | |
| Krizzaks shrink a light they settle on, and it recovers when they are driven off; they do not feed through a wall. | A lit lamp with a moth swarm and one behind a sealed wall. | Heat near the lamp: they leave. |
| The ishvarith breaks for darkness when lit and comes closer as the light fails. | The same animal approaching a lit edge, then the lamp dimmed by moths. | A trapped one may still attack: it is deterrence, not a wall. |
| The quill rattle comes before the close attack. | A crew member approached by an ombrathia. | A rattle spent on a distant hunt and silent at the lunge fails. |
| Grain wears unroofed stone and steel, spares what is roofed, and leaves dust that becomes fuel. | Matched pieces roofed and unroofed through an etchfall; sweep and refine. | Dry weather: no wear. |
| An Unveiling clears the Dark everywhere for a while and the Dark returns. | A full Unveiling with lamps, moths and a predator in place before, during and after. | It reveals nothing through unexplored fog. |
| Gusts are real and intermittent; gharrek open on each one. | A day of natural wind with gharrek on the map. | Steady wind with a gust sound over it fails. |
| The fold lamp holds a lane of clear air that walls stop. | A lamp pointed down an open approach and at a wall. | Unfuelled: the lane closes. |
| Vines turn to the strongest light; a picked glowberry lights its carrier. | Move the only lamp; hand a berry to a crew member in the Dark. | |
| The pools hold living swimmers and the line brings up the same creatures. | Watch a pool; fish it. | A catch with nothing living in the pool fails (standing ruling). |
| A quiet, dark ship gains cover; lamps slow it; the engine ends it. | A landed ship run dark, run lit, then started. | With the feature switched off none of the three changes anything. |
| A probe can be beaten by stillness and darkness or by killing it, and its report ends the cover and brings the search back to ordinary pace. | Three probes: avoided, destroyed, and allowed to report. Read the pursuit's next timer after each. | A probe that reports changes the timer; the other two do not. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary dark highland
(standing rule, every mod).

## Shared machinery

**Featured here** (the Abyss is where each is vital and should be proven):
- **The pursuit's survey shadow and the ship's cover** (`surveyShadowBiomes` in `EmpirePursuit`; the visibility
  dial). Every biome sits somewhere on the Empire's clock; this is the one whose identity is that clock.
- **The light ledger:** one shared account of who is dimming which light, so the Dark and the moths never fight over
  a lamp's radius. Any biome with light-eaters or darkness wants it.
- **The gust signal** (`RM_GustController`): one reading of real wind excursions that the gharrek, the sound and
  anything later all obey.
- **Exposure that wears things** (the etchfall sampler, on the shared hazards machinery).
- **Sound dimmed by a medium** (the muffling hook).

**Merely active here:** real flight (the moths); wreck salvage (storm-torn turbine housings and vanes); bone from
butchery; the ship's acoustic sounder; shared creature behaviours (tidying, light aversion's plumbing). The one sun
from geometry applies and has nothing to do: this is past the terminator, and an Unveiling's brightness is not
sunlight.

## Scope

"Built" is the 2026-11-17 census, not a pass. Items marked **(his mark)** were moved into 0.1.0 by the owner on
2026-11-17.

**0.1.0, the hide**
- The land: black etched highland and dark sand; stillness broken by gusts; etchfall; the rare Unveiling; the
  biome's dark swirling face on the world map. (built)
- The Dark: dimming with outlines kept (unbuilt presentation), the sight and aim penalty (built), intervening Dark
  spoiling shots (unbuilt), lamps shrinking (built), rooms cleared by warmth (built), muffled sound and the gust
  soundscape (built).
- Living light: the lamp tree and crops under it, glow globes, glowing grass (built); vines that turn to light and
  a picked berry that lights its carrier **(his mark; unbuilt)**.
- The fold lamp, reached by ordinary research **(his mark; built)**.
- The moths that eat light; the ishvarith; the saevitha; the ombrathia; the gharrek; the tameable sorter that
  tidies; the herds, pack animals and milkers; the summ as an ordinary great beast. (built)
- Etchfall, tholin and its fuel; etchcap in its hollows. (built)
- The fishery of creepy dark pool creatures, living in the pools **(his mark; unbuilt)**.
- The ordinary wreck field. (built)
- **The hidden ship:** cover that builds on a quiet, dark, landed ship and breaks on engine start; probes that
  still come; the report that ends the cover and restores the ordinary search. (cover and probes built; the
  pursuit's response to a broken cover is unverified) **Moved in by this rewrite.**

**0.2.0, Lightfall and the long stay** (as he approved on 2026-11-17, except the line above)
- The brood at the bottom of Lightfall: the landscape-sized sleeping mother, the clutch, the bone field, one wake
  meter fed by greed, the egg, the storms that follow a stolen egg home, the summing that *"never stops growing"*.
- The Ship in the Wall and the fittings it yields; the great bone aboard.
- The cryptid: rings, stocked dens and caches the sorter may or may not have made; the unwatched exchange; a clear
  pocket around nothing; whispers, tales and the long-stay dream.
- Drifting clear pockets outdoors; the nevarithia's worn knot of Dark and its release at death.
- A summ answering a Witchfire storm; summ regeneration and its hurt in daylight.
- Trade ships unable to find a covered ship.
- Learning heat-folding by watching warm air, with its letter (he left this open: *"We'll make that determination
  later."*).
- The roster's bespoke behaviours not yet built (corpse-stripping, spine spray, hungry digging, and the like);
  glow-globe poison; fungus spores.
- The four darkness rites (campaign).

**Later**
- Fugitive holds, seep-works and their explosions, the wind-farm ruins as inhabited sites: campaign layer.
- Lightfall as a landmark on the world: authored at the one painting pass.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Gust turbines and gust power (cut by card, 2026-10-01).
- A ship touch in the free tier (declined by card, 2026-10-01).
- Any on-screen Nhaleth; the name "Forsakens" for them (his words, 2026-10-01).
- Anything that reads as a fantasy dragon: no fire breath, no hoard, never the word (his words, 2026-10-01).
- Geothermal anything; steady wind; water rain; permanent clear weather; clean sensing; sun-fed residents (the
  sheet's bans, all kept).
- The four Lightfall options he did not pick (the Sink, the Lowered, the Mercy Engine, the Lantern Tide).
- **Recommended for dropping, not yet his:** gill-ash as a second fuel line; the unused donor weather copies; the
  natural-placement worker and its rarity slider.

## NEEDS HIM

1. **The hidden ship in 0.1.0.** On 2026-11-17 he approved it in 0.2.0. On 2026-11-18 he asked that the ship lens
   be the overriding priority for 0.1.0 and that the buckets stay *"a LITTLE open"*. *In 0.1.0* (this document's
   default): the Abyss's first version is the hide, which is what the biome is for; it adds two promises and one
   unverified link to an already *"daunting"* version. *Back to 0.2.0:* 0.1.0 is then a dark place to survive with
   only the passive fourfold delay, and the ship is scenery for one more version. *In 0.1.0, and move lamp-crop
   farming out to make room:* the hide gets poorer, which the hiding rule likes, and the cover-against-farm bargain
   loses its farm.
2. **Sharp-edged clear pockets outdoors.** The frozen sheet says *"clear pockets are real, sharp-edged, and
   unexplained to everyone in-world."* The built engine ties outdoor Dark to one shared outdoor temperature, so
   0.1.0 has none outdoors. The cleanse asked this on 2026-11-17 and it is unanswered. *Off until 0.2.0* (default).
   *On in 0.1.0:* the drifting-pocket code exists and needs a lore-compatible reason and its own scene.
3. **Does the grain eat the ship?** The hiding rule says something must erode while the crew is down here.
   `UNMEASURED` whether the hull counts as exposed steel to the built sampler. *The hull is exempt* (default; only
   what the crew builds outside wears). *The hull wears slowly:* the hide has a clock of its own, and the Abyss
   forces the crew out before the Empire does. *The hull wears only while the engine is cold:* the cover itself is
   what costs.
4. **Does an Unveiling expose the ship?** New in this rewrite, not in any source. *No* (default; nothing built
   changes). *Yes, while it lasts:* the most beautiful hours in the biome are the hours the Empire can see, which is
   his own line, *"only to twist into nightmares just as swiftly"*, made literal.
