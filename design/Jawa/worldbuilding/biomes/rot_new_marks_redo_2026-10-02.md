# The Rot: the three open marks, pitched again (2026-10-02)

_BENCH design pass, second try. The owner turned down all three earlier ideas with *"none of these hit
the mark"*: the sheened hull, the ground's heartbeat, and Unseaming. This pass pitches six new ideas, two
each for **ship touch** (MISS), **sound** (PARTIAL) and **technology** (PARTIAL). They build on what he
chose this sitting: the giant is **the gut that walks** (a huge, slow maggot covered in small wriggling
tentacles and eye spots, with *"the old ship that's pinging from within begging the players to figure out
how to kill it"*), and the rite is **the Unjoining** (Ta'Baa: a colonist who let the jungle into their
body is purged until the symbiont dies, just before the clan leaves). He likes ideas that are bold,
specific and full of story, and that tie the biome to the ship, the gods and the clan's trade. He turns
down ideas that are sentimental or abstract._

Sources: `rot_bedazzle_review_2026-10-02.md` §0–§6; GPT's five ideas and the other-biome avoid list in
`Transient/bedazzle_gpt_enrich_2026-10-02/rot_gpt.md` and `rot_gpt.prompt.md`. Every hook marked
UNMEASURED has to be resolved in RimSage before anything is built. The bans still apply to every row: no
teas or symbionts that leave the Rot (4), and no active bioweapon (7).

## Ship touch (mark 6)

### S1. The Swallowed Navigator: the ping is talking to *your* ship

- **In play:** The old ship pinging inside the gut is not just noise. It is a navigation core, and the
  first time your gravship lands in the Rot, your pilot console answers it. As long as the gut is alive,
  every ping the console catches writes another line of a dead ship's flight log into yours. The ship's
  Narrator reads each line out as a letter, and each finished stretch of the log marks a **salvage site
  somewhere on the planet**: a piece of the old ship's scattered cargo, a wreck it left behind, a cache
  its crew buried. This is the clan's trade as a giant-sized dilemma. Kill the gut and you cut out the
  core (an installable ship part, which needs the giant's hook to decide what it does), but the log stops
  where it stopped. Keep it alive and you keep getting coordinates, while a thing that eats whatever lies
  down roams the map your wounded lie on.
- **Why a Rot player cares:** the giant he chose stops being only a boss. It is a treasure map that is
  still writing itself, and how long you can stand living with it is a scavenger's greed against the
  colony's safety. It also explains the ping: the old ship wants to be found.
- **Mechanism:** a `ThingComp` on the giant (new C#) emits a ping on a timer. A `MapComponent` (new C#)
  checks for an Odyssey pilot console on the map (the console's class is UNMEASURED) and adds log progress
  with each ping. When progress reaches a threshold, it places a `WorldObject` site from a `SitePartDef`
  holding salvage, through a quest the way vanilla's "item stash" quests do (`QuestScriptDef`, site
  parts). The log is a fixed, hand-written list of entries (the world is fixed, so the sites are authored
  tiles and never generated). On the giant's death, a butcher product or corpse drop gives the core as a
  `ThingDef`. Mod Settings: on/off, pings per log entry, number of entries.
- **Not a neighbour's:** the Lantern Deeps' Orun-Ghal is a dead suit you study. The Rust Cathedral's
  bolts spy *on* the ship. Here a living giant feeds the ship knowledge, and killing it ends the feed.
- **Cost:** M (the site list and the letters are the work; the comps are small).

### S2. The Rot Will Not Let Them Go: a launch siege for the joined

- **In play:** A colonist carrying a Rot symbiont has, in the sheet's words, joined the biome. When you
  start the launch countdown with a joined colonist aboard, the jungle tries to keep them. The warm mat
  grows up over the landing struts and holds the ship down for a few hours. Every hybrid on the map that
  shares wounds turns toward the hull. The joined colonist feels the pull and may walk off the ship
  toward the nearest guardian grove (a mental break with a target). You have three ways out. Hold the
  Unjoining first and leave clean. Fight off the network while the crew cuts the struts free. Or leave
  the joined colonist behind. Ta'Baa's rite and the ship's departure become the same story: the
  Unjoining is what makes leaving the Rot easy.
- **Why a Rot player cares:** the symbiont was the best thing the Rot gave you (Sheen immunity, fast
  healing, no sleep), and here is the price, paid at the moment you are most exposed. It turns the rite
  he chose into a plan you make before you leave.
- **Mechanism:** a Harmony prefix on Odyssey's launch-start path (exact method UNMEASURED) checks the
  crew for any Rot symbiont hediff. If one is aboard, it fires a `GameCondition` (new C#) that blocks
  launch for N hours, spawns the strut-grasp as a `ThingDef` building on the engine cells that has to be
  cut down (a vanilla deconstruct or attack target), sends the map's wound-link creatures to the ship
  with a `LordJob` (vanilla assault-to-point), and rolls a `MentalStateDef` ("the pull", wander to a
  grove; new C# worker). Mod Settings: on/off, hold length, break chance.
- **Not a neighbour's:** the Stillsand dunes bury the ship, the Webwork's roots fill its doorframes, and
  the Abyss hides it. This is the only one where the biome holds the ship back **because of who is
  aboard**.
- **Cost:** M.

## Sound (mark 7)

### O1. Something Is Still Alive In There

- **In play:** The gut eats whatever lies down, and that includes a downed colonist, a caravan animal or
  a wounded raider. You hear what it swallowed: a muffled knocking and a voice through the hide that
  grows fainter as digestion goes on. The knocking is a clock and a name. Select the gut and its
  inspector says who is inside and how long they have; the sound tells you before you look. Cut the
  belly open in time and they come out alive, Sheen-soaked and half digested. Wait too long and they come
  out as a corpse. Sometimes the knocking is a stranger: a trader's pack animal, still carrying its packs.
- **Why a Rot player cares:** this sound is the reason you fight the giant *now* and not later, and it
  gives the ping-in-the-gut a terrible neighbour. It is also how the gut becomes a threat to your people
  without ever hunting: it simply clears up after a fight.
- **Mechanism:** reuse Anomaly's devourer, which swallows a pawn, digests it over time and gives it back
  when it takes damage (its comp and hediff names are UNMEASURED; read them in RimSage). The gut's
  `ThingComp` (new C# only if the devourer's comp cannot be attached as it is) chooses as targets only
  pawns that are already downed. A sustained `SoundDef` (knocking, then a muffled voice) is pitched to
  the time left, and an inspect string names who is inside. Mod Settings: on/off, digestion time,
  loudness.
- **Not a neighbour's:** the Nightside Ice and Stillsand rumbles warn you of a predator coming. This
  sound tells you who has already been taken and how long you have to get them back.
- **Cost:** S to M (mostly reuse).

### O2. The Joined Ear: hearing the Rot through a colonist who joined it

- **In play:** When you select a colonist carrying a Rot symbiont, the soundscape changes to what they
  hear: the network from the inside. That is the slow pull of the mat, the hum of every grove, and a
  sharp wrong note wherever something is hiding. The wrong note marks a **skerrith** standing still as a
  cap, a guardian grove about to vent, or a digestion site under the mat. Each one also gets a small
  marker while the joined colonist is near. The joined colonist is your best scout in the Rot. The
  Unjoining takes that ear away for good, and that is the rite's real cost.
- **Why a Rot player cares:** the skerrith (a person-sized mantis that passes as a cap) is otherwise
  invisible until it strikes, and the groves give little warning. The ear is a real advantage, and it
  makes the symbiont choice and the Unjoining choice weigh something.
- **Mechanism:** a `MapComponent` (new C#) watches `Find.Selector`. While a symbiont host is selected it
  plays a looping `SoundDef` and, for hidden threats within N cells, plays a positional "wrong note"
  `SoundDef` and draws a `Mote` or overlay on them. The skerrith needs a hidden or disguised state to
  read, through its comp or its stand-still job (UNMEASURED). The grove side reads the existing guardian
  defence comp. Mod Settings: on/off, range, loudness.
- **Not a neighbour's:** the Stillsand geophone is a device you plant, and the Greentide's cue is a
  silence. Here the listener is a body that has joined the biome, and you lose it by choice.
- **Cost:** M.

## Technology (mark 2)

### T1. The Gut-Mother: getting implants back from the dead

- **In play:** The gut digests everything except metal, and the clan learns to keep a piece of that
  digestion alive. From the dead giant you cut a **gut-mother**, a living digestive sac. Studying it
  unlocks a vat you grow anywhere from that sac: feed it a corpse and in a day it gives back everything
  in the body that was not flesh. That means bionic arms, a power claw, a buried slug, a raider's
  smuggled gem, all clean. As far as we know, RimWorld has no way to recover an implant from a corpse
  (believed, UNMEASURED; check before building). Vats can be split like a starter culture, so the clan
  can **sell gut-mother starters** across the planet: a Jawa trade good no one else has.
- **Why a Rot player cares:** this is the payoff for killing the giant (beside S1's reason to keep it
  alive), and it is the most Jawa idea of the lot. Scavengers who recover machines from the dead, and the
  more raiders who come to you, the richer you get.
- **Mechanism:** the giant's butcher product is a `ThingDef` (the sac). A `ResearchProjectDef` needs the
  sac to be studied (vanilla studiable or analysis comp). The vat is a grown `Building` like the existing
  grown furnace, with a `CompRefuelable` that takes corpses and a new C# `ThingComp` that, after a timer,
  reads the corpse's `health.hediffSet` for `Hediff_AddedPart` / implant hediffs with a `spawnThingOnRemoved`
  and spawns those things plus any inventory and equipment. Splitting is a vanilla `RecipeDef` that makes
  a new sac. Ban 4 check: the sac is neither a tea nor a symbiont, and it does not travel as a stockpiled
  dose but as a building culture. Flagged for his ruling all the same. Mod Settings: on/off, digestion
  time, chance an implant is recovered.
- **Not a neighbour's:** Unseaming (turned down) took apart gear you owned. This recovers what is inside
  the dead. The Greentide lace stops bleeding, and Pyrelands breakers are grid gear.
- **Cost:** M.

### T2. The Unjoining Draught: a purge that drives out anything living in a body

- **In play:** The first time the clan holds the Unjoining, the clan's doctor watches a symbiont die
  inside a colonist and learns how it was done. That unlocks a vile draught that works anywhere. It
  drives out **whatever has taken root in a body**: muscle parasites, gut worms and, above all, Anomaly's
  hidden horrors (a metalhorror nested inside a colonist is forced out early, where you can see it and
  fight it, instead of bursting out at the worst moment). It is brutal. The drinker spends a day sick and
  in pain, takes organ damage, and loses any symbiont or beneficial implant that grew in. Powerful, and
  paid for in suffering.
- **Why a Rot player cares:** the rite he chose becomes a lesson the clan carries off the continent,
  which is how a Ta'Baa act (refusing to root) turns into a tool. Late in a campaign with Anomaly
  running, this answers a fear that nothing else answers.
- **Mechanism:** a `ResearchProjectDef` unlocked from the rite's outcome worker (the existing
  `RUT_ResearchMod_GrantRite` pattern, run in reverse: a rite that grants research; new C#, small). The
  draught is an ingestible `ThingDef` with an `IngestionOutcomeDoer` (new C#) that removes the hediffs on
  a defined list (muscle parasites, gut worms, every Rot symbiont) and adds a purge sickness. For the
  metalhorror it calls Anomaly's own emergence path (implant hediff and emerge method UNMEASURED in
  RimSage) instead of quietly deleting it. Free tier for the draught; the trigger from the rite lives in
  the campaign, and the free tier also gets a research route to it (dissecting a dead symbiont husk) so
  it stands alone. Mod Settings: on/off, organ damage, sickness length.
- **Not a neighbour's:** the Greentide lace closes wounds. This empties the body of guests. It is the
  only tech on the planet that comes out of a rite.
- **Cost:** M.

## Names

The new invented names are all English compounds: gut-mother, joined ear, Unjoining draught. A Python
sweep over `src/` and `design/` (`.xml/.md/.cs/.txt/.json/.py`, case-folded) found zero files for
`gutmother`, `gut-mother`, `joined ear`, `purge draught`, `gut vat` and `pingback`. The sanity probe
`korrum` found 52 files. One working title was dropped because it collided: *"Running Dark"* (hiding the
ship by cutting power) is the Abyss's idea in `blackcrags_bedazzle_review_2026-09-30.md`. That is why S1
became a log the ship receives and not a stealth game.

## Recommended picks

- **Ship touch: S1, the Swallowed Navigator.** It builds directly on the line he loved (the old ship
  pinging inside the gut), it turns the giant into a treasure map, and it leaves him a real choice between
  keeping the giant alive and killing it.
- **Sound: O1, Something Is Still Alive In There.** Cheap because it reuses Anomaly's devourer, it reads
  instantly, and it gives a reason to fight the gut now.
- **Technology: T1, the Gut-Mother.** The most scavenger-trader idea of the six, a new trade good, and the
  reward for killing the giant that balances S1's reason to keep it alive.
- The other three (S2, O2, T2) all hang off the Unjoining. If he wants the rite to carry more of the
  biome, **S2** is the strongest single companion to it.
