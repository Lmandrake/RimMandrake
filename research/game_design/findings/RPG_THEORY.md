# RPG Dungeon Design Theory — Principles, Vocabulary, and Failure Modes

**Scope**: this file is the THEORY thread — the body of published principle, criticism, and
craft writing about what makes a dungeon good. It supplies vocabulary and laws; it does not
catalog specific content to build (that's other agents' domain) or measurement instruments
(that's METRICS's domain — a principle says what to do, a metric says how you'd know).

**Confidence key**: **CONFIRMED** = I read the primary text directly (fetched page, quoted
verbatim, or a direct-primary quote surfaced through a secondary source with citation).
**UNCERTAIN** = secondhand, a summary-of-a-summary, or an attribution I could not verify
against a primary text. Every line carries its evidence (URL or saved path).

**Retrieval note**: WebSearch is disabled for this model group (confirmed by direct test,
400 error). Web access was via WebFetch (direct URL fetch + small-model summarization) and
the `fetcher` skill (search + fetch, queued — shared across sibling research agents, so
several batches never completed in this session; noted where a lead went unretrieved).
Sources saved under `research/game_design/sources/rpg_theory/`.

---

## 1. Jennell Jaquays and "Jaquaysing" / "Xandering" the dungeon

**The core claim is REAL, not a slogan without substance**, but the attribution history is
unusually tangled and worth stating precisely because the owner asked me to check who
actually said what.

- **CONFIRMED** (via Wikipedia, https://en.wikipedia.org/wiki/Jennell_Jaquays, citing a 2022
  RPGnet interview and a 2024 New York Times obituary): Jaquays, in her own words: *"My
  earliest dungeon designs nearly all had multiple paths through them and I tried to create
  situations that could be solved by cleverness as much as they could be combat."* And: *"If
  everything is on the same path, you're not really making exploration choices. Variable
  paths through a setting allow for meaningful exploration choices."* The New York Times
  described her modules *Dark Tower* and *Caverns of Thracia* as *"renowned for their
  pathbreaking designs"* which *"often contained several possible entrances and multiple
  avenues, some of them secret, by which players could accomplish their goals,"* in an era
  (mid-to-late 1970s, via Judges Guild) when contemporary modules were overwhelmingly linear.
- **CONFIRMED** (Justin Alexander, The Alexandrian, "Xandering the Dungeon," 2010, via
  WebFetch of https://thealexandrian.net/wordpress/13085/roleplaying-games/xandering-the-dungeon):
  Alexander is the one who turned Jaquays' *practice* into a named *technique* with articulated
  principles. Core claims: *Caverns of Thracia* has three separate entrances to the first level
  and "two conventional paths and no less than eight unconventional or secret paths" descending
  to lower levels; the payoff is that repeated playthroughs, or a party splitting up, produce
  genuinely different experiences. He explicitly contrasts this with linear published modules
  (he names 4th-edition D&D's *Keep on the Shadowfell*) where "heading down the corridor" is
  exploration in name only — "whereas when I head down I-94 I am merely a driver." His load-bearing
  counter-argument to the objection that non-linear dungeons are harder to run: *"the actual
  running of the adventure isn't more complex as a result"* of branching — because populating
  a dungeon logically (see §6, "goal-oriented opponents"/monster rosters) scales the same way
  regardless of topology.
- **ATTRIBUTION HISTORY — verify before citing a name casually.** Alexander originally coined
  the term as "jaquaying the dungeon" (2010), eponymous to Jaquays. **CONFIRMED** (WebFetch,
  https://thealexandrian.net/wordpress/50123/roleplaying-games/a-historical-note-on-xandering):
  he later renamed it "xandering" (after his own surname, Alexander) and gives three reasons —
  (1) Jaquays asked that if her name were used it at least be spelled correctly ("jaquaysing,"
  with the "s"; Alexander says *"her name is very important to her"*), (2) the term had become
  a target for online harassment campaigns directed at anyone who used it, escalating in some
  cases to death threats, and (3) legal/trademark caution when revising his published book. His
  own account states Jaquays did not ask for her name's *removal*, only correct spelling — a
  distinction critics raised sharply after Jaquays' death in January 2024, arguing Alexander's
  full swap to "xandering" (rather than "jaquaysing") prioritized his own convenience over her
  actual, milder request. **UNCERTAIN**: I have not independently verified Jaquays' own
  side of this dispute beyond Alexander's self-report; treat the harassment/legal justification
  as Alexander's account, not adjudicated fact. **Practical guidance for this project: cite the
  technique as Jaquays' practice, articulated and named by Alexander; use "xandering" only when
  quoting Alexander's own terminology, and always name Jaquays as the source of the practice.**
- **Melan diagrams — REAL, separately attributed, and a genuine analytical tool.** **CONFIRMED**
  (WebFetch of https://thealexandrian.net/wordpress/45711/roleplaying-games/xandering-the-dungeon-addendum-how-to-use-a-melan-diagram):
  invented by an ENWorld/Dragonsfoot poster using the handle **"Melan," in a 2006 ENWorld thread
  titled "dungeon layout, map flow and old school game design."** A Melan diagram is *"a
  graphical method which 'distills' the dungeon into a kind of decision tree or flowchart by
  stripping away 'noise.'"* Rules for building one: (a) a corridor with only one exit becomes
  a straight line, because following it involves no navigational decision; (b) a room with
  multiple exits becomes a fork/branch — this is the only thing the diagram exists to show;
  (c) a side-chamber reachable only one way is dropped as noise (it's not a navigational choice,
  even if it matters for content); (d) secret passages are dotted lines, but only shown when
  they're the *sole* access to a space; (e) level transitions (stairs, chutes) are marked as
  line terminations. **It is explicitly an analysis tool, not a design tool** — you build a
  dungeon first, then diagram it to check its shape, not the reverse.
  - **Translation to RimMaster**: this taxonomy is directly portable to a top-down tile map —
    it does not depend on first-person navigation at all, only on "how many ways can you go
    from here." A RimWorld sub-map or ruin's floor plan can be Melan-diagrammed exactly the
    same way a paper dungeon can, and doing so is a cheap, real check: draw the diagram, see
    if it's a corridor with rooms hanging off it (bad) or has real loops/branches (good).

## 2. Justin Alexander / The Alexandrian — the most systematic body of work found

This is genuinely the deepest, most argued-through body of theory located, confirmed across
several primary essays.

- **The Three Clue Rule — CONFIRMED, full primary text read** (WebFetch,
  https://thealexandrian.net/wordpress/1118/roleplaying-games/three-clue-rule, 2008; saved
  in full at `sources/rpg_theory/alexandrian/three_clue_rule.txt`).
  **Statement, verbatim**: *"For any conclusion you want the PCs to make, include at least
  three clues."* **Reasoning, verbatim**: *"the PCs will probably miss the first; ignore the
  second; and misinterpret the third before making some incredible leap of logic that gets
  them where you wanted them to go all along"* — stated as a joke, then made rigorous: each
  clue is a *plan* for how players reach a conclusion; three clues means a plan plus two
  backup plans, because "plans never survive contact with players." He generalizes it beyond
  mysteries: a **"chokepoint"** is *"any problem that must be solved in order for the adventure
  to continue."* Non-chokepoint problems need only one solution (players can fail and the game
  goes on); **chokepoints need at least three independent solutions**, because a single point
  of failure that halts the whole scenario is the actual design defect, not "the players didn't
  get it." Corollaries, all argued (not just asserted): **permissive clue-finding** — treat your
  planned clues as "a safety net," not "a straitjacket," and reward any player approach that
  plausibly should surface information, rather than gatekeeping it behind the one path you
  imagined; **proactive clues** — when players stall anyway, have something *happen* to them
  (Chandler's line, quoted: *"Have a guy with a gun walk through the door"*) rather than waiting;
  **red herrings are overrated** — deliberately planted false leads are hard to place correctly
  and usually unnecessary, because *"the players are almost certainly going to take care of it
  for you"* by getting attached to wrong theories on their own.
  - **Survives the move to RimWorld? Yes, and directly.** A colony sim already has no
    "GM improvising a hint" — information has to be *placed*, discoverable through multiple
    independent channels (a corpse's inventory, a terminal log, an NPC faction's rumor, a
    scannable artifact, a captured raider's interrogation). The Three Clue Rule translates
    almost without modification: any fact the player MUST learn to progress a dungeon (a key
    location, a weakness, an escape route) needs ≥3 independent, redundant discovery paths, because
    there is no GM at the table to bail out a stuck colony the way a human GM can improvise. The
    analogue of "the GM notices players are stuck and drops a clue" is a scripted fallback event
    (e.g., a distress beacon triggers automatically after N in-game days if the player hasn't found
    the real lead) — this is the "proactive clues" corollary, mechanized.

- **"Don't Prep Plots, Prep Situations" — CONFIRMED, full primary text read** (WebFetch,
  https://thealexandrian.net/wordpress/9721/roleplaying-games/dont-prep-plots, 2009; saved at
  `sources/rpg_theory/alexandrian/dont_prep_plots.txt`).
  **Definition, verbatim**: *"A plot is a sequence of events: A happens, then B happens, then
  C happens... A situation, on the other hand, is merely a set of circumstances. The events
  that happen as a result of that situation will depend on the actions the PCs take."*
  **Argument for why situations are less work, not more** (directly rebutting the intuitive
  objection): a plotted adventure is a chain of potential failure points — every one of 8 steps
  in his worked example is a place the plan breaks if players don't do the expected thing. A
  situation-based prep of the *same content* only adds one new task (alternate ways to reach a
  conclusion — which the Three Clue Rule already covers) on top of work you needed anyway (build
  the locations, NPCs, and antagonist goals). Key operational advice: **"goal-oriented
  opponents"** — instead of pre-scripting NPC reactions to hypothetical player choices, define
  what the antagonist is *trying to do*, then improvise their reaction live; **"know your
  toolkit"** — prep resources (personnel, locations, information) organized in reusable chunks,
  not branching contingency trees, because *"if you need an individual goon, just peel 'em off
  one of the squads"*; a whole contingency tree for "if PCs go left" / "if PCs go right" is
  *"plot-based prep juiced up on Choose-Your-Own-Adventure steroids"* — 90% of it gets thrown
  away and unused. Alexander's own **definition of railroading**, stated precisely in a comment
  thread on this essay: *"Railroading happens when the GM negates a player's choice in order to
  enforce a preconceived outcome... Failure is not railroading."* An NPC reacting logically to a
  player's action (even hostilely) is not railroading; forcing an encounter regardless of what
  the player chose to do is.
  - **Survives the move to indirect squad control? Yes, with a real analogue, and it's the
    single most load-bearing translation in this file.** RimWorld has no GM improvising in the
    moment — an authored dungeon is closer to "prepped plot" by construction (raid triggers,
    quest scripts). The Alexandrian's actual argument, stripped of the GM-specific parts, is:
    **build the location and the antagonist's goals/resources as standing state, and let player
    action determine what happens, rather than scripting a fixed sequence of trigger events.**
    Mechanically for RimWorld: model the dungeon's defenders/hazards as things with their own
    goals and a reaction table (e.g., "if the vault door is breached, the guardian AI does X")
    rather than a linear quest-node chain that fires in a fixed order regardless of the pawns'
    actual path through the map. `QuestScriptDef`'s node-tree-at-offer-time architecture (see
    project's own `rimworld-quests` skill) is structurally closer to "prepped plot" than
    "prepped situation" — the closest situational analogue is a persistent `MapComponent` that
    watches world state and reacts, not a quest node chain.

- **"Game Structures" essay series — CONFIRMED, index/intro read**
  (https://thealexandrian.net/wordpress/nodetype/rpg-theory/game-structures; saved at
  `sources/rpg_theory/alexandrian/game_structures_index.txt`). Central claim: every RPG
  implicitly answers two questions — *"(1) What do the characters do? (2) How do the players do
  it?"* — and different activities (dungeoncrawl, urbancrawl, hexcrawl, mystery, combat) need
  *different* underlying procedures, because a structure tuned for one (e.g., "which direction
  do you walk" works in a dungeon where every step is a meaningful, dangerous decision) produces
  a bad game when applied to a context where it doesn't fit (the same procedure applied to open
  wilderness/city travel, where most steps carry no information, becomes tedious). I did not
  retrieve the individual "Part 3: Dungeoncrawl" essay's full text in this session (linked from
  the index but not separately fetched) — treat its *specific* dungeoncrawl procedure claims as
  **UNCERTAIN/unretrieved** pending a follow-up fetch; the general "game structures must match
  the activity" claim above is CONFIRMED from the index essay itself.
  - **Directly relevant to the translation problem the owner named**: RimWorld's "game
    structure" for indirect squad control is fundamentally the click-to-order/pause-based
    tactical structure — it does not have a "declare an action, roleplay it out" structure at
    all. Every dungeon-theory principle in this file has to be re-asked as "what does THIS
    principle demand of the tile-grid-and-pause structure," not assumed to transfer as prose.

- **Node-Based Scenario Design — PARTIALLY retrieved.** The index page
  (https://thealexandrian.net/wordpress/17945/roleplaying-games/node-based-scenario-design)
  lists nine parts (Plotted Approach; Choose Your Own Adventure; Inverting the Three Clue Rule;
  Sample Scenario; Plot vs Node; Alternative Node Design ×2; Freeform Design in the Cloud; Types
  of Nodes) but the article text itself was not retrieved in this session — only a comment where
  Alexander describes nodes as *"useful conceptual groupings"* functioning like *"tributaries"*
  in campaign design, i.e., functionally independent chunks that can be developed and run
  somewhat separately. **Mark this UNCERTAIN pending direct retrieval of Part 1** — I know the
  series exists and roughly what it covers, but I have not read the actual definitions.

## 3. Melan diagram / map-shape taxonomy — see §1. Additional shapes not independently confirmed

Beyond the Melan-diagram vocabulary (linear corridor / branch / dead-end-noise / secret-dotted /
level-transition, all CONFIRMED above), broader taxonomy terms the field commonly uses —
**hub-and-spoke, loop/ring, network, hourglass** — appeared only in unread search-result
snippets this session (a fetcher search on "Melan dungeon map structure" returned promising
hits — beyondfomalhaut.blogspot.com's "The Anatomy of a Dungeon Map," and a
homicidallyinclinedpersonsofnofixedaddress.com post titled "Dungeons as networks" — that were
never fetched due to Fetcher queue contention with sibling research agents this session).
**UNCERTAIN / unretrieved**: do not cite a hub/loop/hourglass taxonomy as attributed to a named
source from this file; it is very likely real (it is common OSR-blogosphere vocabulary) but I
have not read a primary statement of it to quote or attribute correctly.

## 4. Bryce Lynch / tenfootpole.org — module review criteria, CONFIRMED

**CONFIRMED** via direct fetch of the Review Standards page
(https://tenfootpole.org/ironspike/?page_id=1201) and cross-checked against a live review page
(https://tenfootpole.org/ironspike/, saved at `sources/rpg_theory/tenfootpole_frontpage_2026-09.txt`,
which independently repeats the same principles in practice, e.g. of a 2026 review: *"Dungeon
maps should have lots of 'loops.' Linear dungeons are not a good thing."*).

- **Explicitly declines a numeric score**: *"I try to avoid giving a module a rating. I think
  it's far more useful if I describe the module and tell you what I liked and didn't like about
  it."* His actual category tags (confirmed present on live reviews) are qualitative buckets:
  "The Best," "No Regerts," "Meh. It's fine," down through harsher categories.
- **Loops over corridors**: *"Dungeon maps should have lots of 'loops.' Linear dungeons are not
  a good thing."* — an independent, convergent statement of the Jaquays/Alexander xandering
  principle from a completely different lineage (module reviewing rather than GM-craft essays).
- **"Details" vs "specificity"** — a named distinction, argued at length in the live review of
  *The Swan Hollow Intrigue*: *"detail is bad. It is trivia. It explains why's or how's that we
  don't need to know... Specificity, though, are those things that inspire us to greatness in
  running the game. It is terse... If a picture is worth a thousand words then one well written
  specific sentence is worth more than a page of details."* This is a genuine, nameable
  **failure mode distinct from "too much text"**: the failure isn't verbosity per se, it's
  spending words on *why* instead of on *what a person at the table can immediately picture and
  use*.
- **Boxed/read-aloud text**: *"Long read-aloud causes players to lose focus and pull out their
  phones... Long italics is hard to read, cognitively."* — a named, testable failure mode
  ("the long-boxed-text problem").
- **Rooms should be "imagined first and statted second."** Encounter design should feel
  designed for the fiction of the room, with mechanics justifying it, not the reverse.
- **Named opposite of the "empty room" complaint**: Lynch does NOT treat an unguarded, contentless
  room as automatically bad — an "empty" room with some risk/reward texture (his phrase:
  "empty rooms and some unguarded treasure" as deliberate pacing/breather content) is fine;
  the failure mode is a room that is empty *and inert*, giving the player nothing to read, decide,
  or remember.
  - **Translation to RimWorld**: "details vs specificity" maps directly onto item/room flavor
    text and onto map dressing — a scavenged ruin room with one specific, visually legible prop
    (a single wrecked mech chassis slumped against a wall) beats a paragraph of lore text nobody
    reads in a game with no dialogue trees. "Loops over corridors" is the Melan principle again,
    independently confirmed. The "long boxed text" failure mode has a precise RimWorld analogue:
    a `LetterDef` or quest popup wall-of-text the player must read before they can act is the
    same failure as long italic read-aloud — RimWorld players click past text exactly like
    tabletop players check their phones.

## 5. Expedition to the Barrier Peaks (S3) — the crashed-spaceship-in-fantasy precedent

**CONFIRMED** via Wikipedia (https://en.wikipedia.org/wiki/Expedition_to_the_Barrier_Peaks).
Written by Gary Gygax (originating as an Origins II 1976 tournament scenario, with Rob Kuntz
credited for "inspiration" via his "Machine Level" concept; published 1980 as module S3).
Premise: a downed spaceship in the Greyhawk setting's Barrier Peaks; the crew is dead of an
unspecified disease, but robots and alien creatures remain active; players collect color-coded
access cards to unlock sections and operate ship systems.

- **Reception, both directions, both CONFIRMED-cited on the Wikipedia page**: contemporary
  reviews were enthusiastic about the genre mashup — Tim Byrd, *The Space Gamer* (Aug 1980):
  *"successfully combines fantasy with SF... one of the best modules TSR has published."*
  Marcus Rowland, *White Dwarf* (Aug 1981): 9/10. *Dungeon* magazine ranked it 5th-greatest D&D
  adventure ever published (2004). **But** designer Bill Slavicsek deliberately *excluded* it
  from his own *Dungeon Survival Guide*, reasoning: *"Once you add ray guns and power armor to
  the game, you have a fundamentally different experience"* — i.e., the tech doesn't stay
  contained; it changes what the *rest* of the campaign can be once players own it.
  Aaron Starr (*Black Gate*) reported a concrete, practical play problem: players struggle to
  convincingly roleplay in-fiction ignorance of technology they, the real people, recognize —
  the module assumes fantasy characters encountering blaster rifles and powered armor as
  bewildering, but real-world player knowledge undercuts that in actual play.
- **This is exactly the owner's stated problem, independently corroborated by 45+ years of
  actual-play criticism**: the tension isn't "can sci-fi tech go in a fantasy dungeon" (yes,
  it can, and the mashup itself was well-reviewed) — it's (a) **containment**: tech taken out
  of the dungeon changes the campaign's baseline permanently (Slavicsek's objection), and
  (b) **diegetic ignorance vs. real knowledge**: characters are supposed to not understand
  what players obviously do (Starr's objection). Both translate directly and usefully to a Jawa
  scavenger campaign that is explicitly ABOUT normalizing scavenged tech rather than
  quarantining it — meaning objection (a) is a designed-for feature here, not a bug, but
  objection (b) still applies in reverse: a RimWorld colonist "not knowing" what a scavenger
  finds is less of a problem than a *player* needing the game to telegraph an item's danger/use
  without dialogue.

## 6. Genre-adjacent design theory confirmed this session (video game / academic)

- **Metroidvania gating — CONFIRMED via Wikipedia** (https://en.wikipedia.org/wiki/Metroidvania).
  Core mechanic, quoted: *"Not all areas of this map are available at the start, often requiring
  the player to obtain an item... or a new character ability to remove some obstacle blocking
  the path forward."* Attributed genre-founding design intent to **Koji Igarashi**: design maps
  that *"encourage exploration but which still guide the player on a main path,"* while giving
  *"means where the player can be aware of where they are in the game world at any time"* — i.e.,
  non-linearity must be paired with a legible sense of place, or exploration curdles into
  confusion. **This is the formal statement of "progressive discovery / lock-and-key" the owner
  asked about** — it is real, and it is exactly the affordance-then-obstacle-then-tool pattern:
  the gate (obstacle) is placed BEFORE the key exists to be found, so the player learns the gate
  matters, then later re-encounters it with the tool and the payoff is legible.
  - **Survives the move to RimWorld? Yes, this is probably the single cleanest fit in the whole
    file.** A locked/sealed sub-structure that visibly exists but is inert until the player
    acquires a specific tool/tech/keycard is mechanically identical whether reached by
    platformer-jump or by pawn-pathfinding-and-door. The "legible sense of place" requirement
    (Igarashi) does need a translation: RimWorld has no persistent single-screen minimap of a
    dungeon's shape by default — the analogue is ensuring the *map itself*, in top-down view,
    reads its own shape (the Melan-diagram test again: does the physical layout show its loops
    and gates at a glance, or does it read as noise).
- **Darkest Dungeon — CONFIRMED via Wikipedia** (https://en.wikipedia.org/wiki/Darkest_Dungeon).
  Developer Tyler Sigman on the origin of the stress/affliction system: cited *Band of Brothers*
  episode 7, where a soldier who has watched friends die becomes unable to fight, as *"the
  feeling they wanted to capture"* — i.e., attrition is modeled as *psychological*, not just
  HP/resource depletion, and deliberately avoided a "insanity" Lovecraft-horror framing in favor
  of something closer to real stress reactions. Explicit design intent, stated as wanting to
  *"toy with player agency"* — the game deliberately creates situations where the player does
  NOT have full control over a stressed/afflicted hero's actions, as the emotional core of the
  attrition system, not an incidental randomness layer.
  - **This is the single most transferable ATTRITION theory found**, because Darkest Dungeon is
    already indirect, party-based, tile/room-based, and explicitly about the decision to press
    on vs. withdraw — closer to RimWorld's actual control scheme than any tabletop source in
    this file. The translation is nearly a direct port: model dungeon-crawl attrition on
    colonists as an accumulating, visible, non-HP resource (RimWorld already has mood/mental
    breaks — the design lesson is to make a dungeon-specific version of that pressure legible
    and consequential the way DD's stress bar is, rather than folding it silently into the
    existing mood system where the player can't feel the clock ticking).

## 7. Leads pursued this session that did NOT confirm, or failed outright — say so plainly

- **Gygax's own AD&D DMG dungeon-design advice, Moldvay's B/X stocking procedure**: **NOT
  RETRIEVED** this session. A guessed Grognardia URL 404'd; a Moldvay-stocking blog fetch
  failed on a DNS error under Fetcher-queue contention. I did not find and confirm a primary
  statement of either. Do not treat these as covered — they remain open leads for a follow-up
  pass with a working search path.
- **Principia Apocrypha, A Quick Primer for Old School Gaming**: **NOT RETRIEVED**. Both
  fetches failed (DNS/network errors via the shared Fetcher queue at the time of the attempt).
  Real documents (I have seen both cited independently before this session, but that prior
  familiarity is not primary-source verification performed *in* this session) — re-attempt
  needed.
- **The Angry GM's "Five Room Dungeon"**: the specific URL guessed and the one returned by
  search both 404'd on his site as currently structured (he appears to have reorganized/removed
  the piece, or retitled it). **Do not cite an Angry-GM-authored Five Room Dungeon article from
  this file** — I could not find it live. The Five-Room-Dungeon *model* itself is widely
  attributed elsewhere to Johnn Four / Roleplaying Tips, but I could not confirm that
  attribution against a primary source in this session either — **treat "who invented the
  five-room dungeon" as UNVERIFIED**, not as a settled fact, until a direct primary fetch
  succeeds.
- **Melan's original taxonomy beyond the diagram addendum, the broader
  linear/branching/hub/loop/hourglass shape vocabulary, Gygax/Moldvay/Angry-GM/Sly-Flourish
  material, Caverns of Thracia / Keep on the Borderlands / Tomb of Horrors / Temple of Elemental
  Evil / Curse of Strahd / Barrowmaze / Rappan Athuk critical-literature deep dives, GDC talks,
  Level Up!/Theory of Fun/Rules of Play, Zelda-specific "Nintendo four-step" documentation, and
  Into the Breach/XCOM mission design**: **queued via the fetcher skill in four additional
  request batches this session (`rpg_dungeon_theory_2` through `_5`), but the shared Fetcher
  instance was heavily contended by multiple sibling research agents running in parallel and
  most of these batches had not completed by the time this report was due.** They are not lost —
  the request files remain in `/Users/mandrake/dev/Fetcher/Requests/` and will process
  eventually — but **their content is UNCONFIRMED and absent from this file.** A follow-up pass
  should check `~/.cache/Fetcher/Delivery/2026-09-11_rpg_dungeon_theory_{2,3,4,5}/` for results
  and fold in only what actually confirms.

---

## Saved primary sources

`/Users/mandrake/dev/RimMaster/research/game_design/sources/rpg_theory/`
- `alexandrian/three_clue_rule.txt` — full page text, The Alexandrian, "Three Clue Rule" (2008)
- `alexandrian/dont_prep_plots.txt` — full page text, The Alexandrian, "Don't Prep Plots" (2009)
- `alexandrian/game_structures_index.txt` — full page text, "Game Structures" series index (2012)
- `tenfootpole_frontpage_2026-09.txt` — live front page of tenfootpole.org (Sept 2026 reviews),
  corroborating the Review Standards principles in actual practice

No file saved exceeds a few hundred KB; all are plain text extracts, well under the 40 MB cap.
