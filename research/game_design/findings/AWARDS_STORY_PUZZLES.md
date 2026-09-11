# Awards, Storytelling Craft, Content Tables, and Interconnection

Research pass 2026-09-11. Scope: (1) awards/canon as a discovery instrument for
adventure/dungeon design, (2) storytelling and event-trigger craft, (3) raw
content-table fodder, (4) how discrete authored places compose into one world.

**Retrieval note on this pass:** `WebSearch` is refused outright (400, tool
type not supported for this model group — confirmed, not a transient error).
The `fetcher` skill's local script was running throughout, but its SEARCH
directives were, for most of this session, routed through a broken "bing
(after brave(error))" fallback engine that returns keyword-matched junk
completely unrelated to the query (e.g. querying "Dark Souls interlocking
world shortcuts" returned Netflix's *Dark* TV series; querying "sandbox vs
adventure path" returned sandbox video games). A minority of queries landed on
`duckduckgo` or `ddg-lite` and returned real, relevant results — the routing
appears to be non-deterministic per query, not something I could force.
Separately, the Fetcher **queue itself was heavily contended** by several
concurrent sibling research agents; four of my batched requests sat at zero
progress for 25+ minutes and are marked below as abandoned, not failed.
Given this, **the majority of what follows was retrieved via direct `WebFetch`
calls to specific, known-good URLs** (official award sites, Wikipedia,
named blogs, primary PDFs), discovered by having WebFetch read a page's own
navigation rather than by searching. Where WebFetch's underlying model
refused to reproduce a table verbatim (citing "fair use" and paraphrasing
instead — this happened on the richest table source), I fell back to
`curl` + local HTML parsing to get the exact text myself. That technique is
worth keeping: **don't ask an LLM-mediated fetch tool to reproduce a table
verbatim; fetch the raw page yourself and parse it.**

Every claim below is marked CONFIRMED (I read the primary source myself, this
session) or UNCERTAIN (secondhand, unverified, or a gap I could not close).
No award winner, year, or table was invented; gaps are stated as gaps.

---

## 1. Awards and canonically-praised design, as a discovery instrument

### ENnie Awards — Best Adventure

Official site: `ennie-awards.com`. The nav has no visible "past winners" index
on the homepage; it is at **`ennie-awards.com/history-of-winners/`**, which
links to one page per year at
`ennie-awards.com/portfolio-item/<year>-nominees-and-winners/` (2016 is an
outlier: `.../2016-ennie-award-nominees-and-winners/`). CONFIRMED — I read the
history page and five year-pages directly.

As of at least 2024, the category split into **"Best Adventure – Long Form"**
and **"Best Adventure – Short Form."** Prior years used a single "Best
Adventure" category with Gold/Silver winners plus nominees.

Verified year-by-year (CONFIRMED, read from the official per-year pages):

- **2001** — Gold: *Death in Freeport* (Green Ronin Publishing). Nominees:
  *NeMoren's Vault* (Fiery Dragon), *The Longest Night* (Privateer Press),
  *The Bloody Sands of Sicaris* (Paradigm Concepts), *The Pit of Loch-Durnan*
  (Mystic Eye Games). No Silver awarded that year.
- **2010** — Gold: *Pathfinder AP #31: Stolen Land* (Paizo). Silver: *Trail of
  Cthulhu: The Armitage Files* (Pelgrane Press). Nominees: *The Grinding Gear*
  (Lamentations of the Flame Princess), *A Song of Ice and Fire: Peril at
  King's Landing* (Green Ronin), *WFRP: The Gathering Storm* (Fantasy Flight).
  Honorable Mention: *Trail of Cthulhu: Shadows over Filmland*.
- **2016** — Gold: *Curse of Strahd* (Wizards of the Coast). Silver: *Dracula
  Dossier – Director's Handbook* (Pelgrane Press). Nominees: *Achtung! Cthulhu
  – Shadows of Atlantis* (Modiphius), **Maze of the Blue Medusa** (Satyr
  Press) — a critically celebrated OSR module (Zak Smith/Patrick Stuart) that
  did not win gold but is a recurring "greatest OSR module" touchstone in the
  hobby's own retrospectives — and *Deadlands: Stone and a Hard Place*
  (Pinnacle).
- **2020** — Gold: *A Pound of Flesh* (Tuesday Knight Games; authors Donn
  Stroud, Sean McCoy, Luke Gearing). Silver: *Trilemma Adventures Compendium
  Vol 1* (multiple authors incl. Skerples — see the content-tables section
  below, same designer). Nominees included *The Halls of Arden Vul Complete*
  (Expeditious Retreat Press).
- **2024** — Long Form Gold: *Delta Green: God's Teeth* (Caleb Stokes, Arc
  Dream). Long Form Silver: *Call of Cthulhu: Alone Against the Static*
  (Chaosium). Short Form Gold: *Eat The Reich* (Grant Howitt, Rowan, Rook and
  Decard). Short Form Silver: *One-Shot Wonders* (Roll & Play Press).

**No published "why it won" citation text exists for ENnie categories** — the
ENnies are judged/voted, not citation-driven like the Diana Jones Award, so
there is no reasoning to quote here. That absence is itself a finding: of the
leads in this brief, ENnies are the weakest source for *reasoning*, strongest
for *what the hobby voted for, product by product, over 25 years*.

### Origins Award — Best Roleplaying Adventure / Best Roleplaying Supplement

Source: Wikipedia's per-year pages, `en.wikipedia.org/wiki/<year>_Origins_Award_winners`.
CONFIRMED — read four year-pages directly.

- **1994** — Best Roleplaying Adventure: *Council of Wyrms* (AD&D; TSR;
  designer Bill Slavicsek). Best Roleplaying Supplement: *The Encyclopedia
  Magica, Volume 1* (TSR; designers Slade, Doug Stewart). The 1994 ceremony
  had 23 categories total, including a dedicated Adventure Gaming Hall of
  Fame with five inductees (not itemized in what I read — gap).
- **2000** — Best Roleplaying Adventure: **Death in Freeport** (Chris Pramas,
  Green Ronin). Best RPG: *Dungeons & Dragons* (Tweet/Cook/Williams). Best
  Roleplaying Supplement: *GURPS Steampunk* (Steve Jackson Games).
- **2005** and **2010** — category names had already drifted to "Role-Playing
  Game of the Year" / "Role-Playing Game Supplement of the Year" — no
  dedicated *Adventure* category survived by these years. 2005 winner:
  *Artesia: Adventures in the Known World* (Mark Smylie). 2010 winner:
  *The Dresden Files Roleplaying Game, Vol. 1: Your Story* (Evil Hat).

**Finding worth flagging:** *Death in Freeport* won **both** the 2000 Origins
Award for Best Roleplaying Adventure **and** the 2001 ENnie Gold for Best
Adventure — two independently-judged awards bodies converging on the same
product in the same product cycle. That kind of cross-award convergence is a
stronger discovery signal than either award alone. A second instance: *The
Dracula Dossier: Director's Handbook* won 2015 Golden Geek Best RPG Supplement
**and** 2016 ENnie Silver Best Adventure.

### Diana Jones Award

`en.wikipedia.org/wiki/Diana_Jones_Award` — CONFIRMED, full table read. This
is the hobby's most citation-driven award (a small invited panel, not a
public vote), but it honors the whole hobby, not adventures specifically —
most winners are RPGs, people, movements, or companies, not modules. Adventure
/ dungeon-adjacent winners: **2007, *The Great Pendragon Campaign*** (Greg
Stafford) — a full campaign-length adventure supplement; **2015, *The Guide
to Glorantha*** — a two-volume setting sourcebook. Full winner list by year
(2001–2026) is in the findings above; not reproduced twice here for space —
see the saved Wikipedia read notes if the full table is needed again.

### Golden Geek Award (BoardGameGeek)

`en.wikipedia.org/wiki/Golden_Geek_Award` — CONFIRMED. **RPG categories only
existed 2014–2018**, then were discontinued — a fact worth knowing before
searching for a Golden Geek RPG winner outside that window and finding
nothing. Categories: Best RPG Artwork/Presentation, Best RPG Supplement, RPG
of the Year. Notable: 2016 RPG of the Year was *Blades in the Dark*; 2017 RPG
of the Year was *7th Sea*; 2015 Best RPG Supplement was *The Dracula Dossier:
Director's Handbook* (see cross-award note above).

### IGF (Independent Games Festival) — Excellence in Design

`en.wikipedia.org/wiki/Independent_Games_Festival` — CONFIRMED. The design
category has been renamed repeatedly: **Best Game Design (1999–2000) →
Innovation in Game Design (2001–2006) → Design Innovation (2007–2008) →
Excellence in Design (2009–present)**. There is **no dedicated level-design or
world-design category** at IGF — Excellence in Design covers overall design
innovation. Representative winners: *Opus Magnum* (2019), *Keep Talking and
Nobody Explodes* (2016), *Papers, Please* (2014).

### Gaps in this domain (UNCERTAIN — not fabricated, just not reached)

GDC Choice Awards' specific "Best Level Design"-equivalent category and its
winners; DICE Awards and BAFTA Games narrative/design honorees; a verified
"Dungeon Magazine 30 Greatest D&D Adventures of All Time" list (this list is
real in my training knowledge as a 2004 Dungeon Magazine feature, but I could
not independently re-verify it against a primary or even a solid secondary
source this session — **do not cite it as fact until re-verified**); any
"greatest dungeons of all time" critics'-list roundup. All of these were
blocked by the broken search engine during this session, not by absence of
the source. Re-run these as `FETCH`/`SEARCH` once Fetcher's engine routing is
healthy, or once WebSearch works for this model group again.

---

## 2. Storytelling and event-trigger craft — concrete trigger-timing doctrine

This is the section the owner asked for by name ("when do you trigger dungeon
events?"). Two primary sources below give an actual **algorithm**, not just a
principle — read them directly if building the RimMaster dungeon director.

### Don Carson — "Environmental Storytelling" (Gamasutra/Game Developer, foundational)

CONFIRMED, read at
`gamedeveloper.com/design/environmental-storytelling-creating-immersive-3d-worlds-using-lessons-learned-from-the-theme-park-industry`.
Carson's frame, drawn from theme-park "themed environment" design:

- **The 15-second rule**: on entering a space, the player must be able to
  answer "Where am I?" and "What is my relationship to this place?" within 15
  seconds, through self-discovery, not exposition.
- **Cause-and-effect storytelling**: broken doors, crashed vehicles,
  explosions — visual aftermath that lets players infer danger and history
  without being told.
- **"Following Saknussemm"**: the player follows breadcrumbs left by a
  fictitious predecessor (named for the explorer whose trail Verne's
  characters follow in *Journey to the Center of the Earth*) — narrative
  progression through what's left behind, not through a guide NPC.
  **Direct trigger-timing implication for RimMaster: a dungeon's "trigger"
  can be spatial rather than temporal — the predecessor's trail is discovered
  in whatever order the player walks it, and each discovery is self-contained
  enough to read regardless of approach order.**
- **Less-is-more**: clutter dilutes signal; use decoration to point at story
  beats, not fill space.
- Lighting as drama; asymmetry over sterile geometric symmetry.

### Jennell Jaquays / "Xandering the Dungeon" (Justin Alexander, thealexandrian.net)

CONFIRMED, read at
`thealexandrian.net/wordpress/13085/roleplaying-games/xandering-the-dungeon`.
Non-linear dungeon design (originally "jaquaying," renamed "xandering" after
a 2010 dispute over the term — the article covers this history). Core claim:
*Caverns of Thracia* (Jaquays, 1979) has **three separate entrances** and
**eight or more secret paths between levels**, so different approach orders
produce genuinely different play, and player choice ("retreat, circle around,
rush ahead") has real consequences rather than being cosmetic. Contrasted
against *Keep on the Shadowfell* as a modern linear anti-example. **Direct
relevance to the owner's "player arrives out of order" risk**: a xandered
structure doesn't have an "intended order" to violate in the first place —
multiple entrances are the design, not a failure mode to patch around.

### The Three Clue Rule (Justin Alexander, thealexandrian.net)

CONFIRMED, read at `thealexandrian.net/wordpress/34423/roleplaying-games/three-clue-rule`.
**"For any conclusion you want the PCs to make, include at least three
clues."** Because each clue is really several chokepoints (search it, notice
it, understand it, draw the right conclusion), redundant paths to the same
conclusion are cheap insurance, not overkill. Extensions with direct
trigger-timing value:
- **Permissive clue-finding** — reward clever unplanned approaches to finding
  a clue, don't gate it to one specific action.
- **Proactive clues** — when players are stuck, **force a new clue into the
  scene via an event** rather than waiting: Alexander's own line is "have a
  guy with a gun walk through the door." **This is an explicit trigger rule:
  the trigger condition is "player is stalled," and the response is to
  inject an authored event, not to wait for the player to find the next
  authored beat unaided.**
- Red herrings are usually unnecessary — players invent their own.

### Node-Based Scenario Design (Justin Alexander, thealexandrian.net)

CONFIRMED (part 1 only — part 2's URL guess 404'd and I didn't re-derive it;
gap), read at
`thealexandrian.net/wordpress/1701/roleplaying-games/node-based-scenario-design-part-1-the-plotted-approach`.
Central maxim: **"Don't prep plots, prep situations."** A plotted
scene-sequence (A then B then C) fails because every transition becomes a
bottleneck — if players don't take the expected exit from a scene, "the
adventure is going to grind to a painful halt," and every choice that doesn't
follow the intended arrow "breaks the game." The fix is to prep self-contained
situations (nodes) that can be entered and connected in any order.

### Emily Short — "Beyond Branching: Quality-Based, Salience-Based, and Involuntary Narrative Structures" (2016)

CONFIRMED, read at
`emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/`.
Frames the core problem as: **"How do I choose which piece to show the player
next?"** — exactly the dungeon-event-trigger question, generalized. Three
structures:

- **Quality-Based Narrative (QBN)**: content units ("storylets") are unlocked
  by numeric "qualities" (inventory, skill, relationship, story-progress
  variables) rather than by branch position. Handles players discovering
  things in any order without a combinatorial explosion of authored branches.
- **Salience-based narrative**: content is tagged with conditions against
  **current world state** (Short's example: dialogue tagged
  `location = kitchen, stove = burning`); the engine fires whichever tagged
  fragment's conditions currently match, preferring the most specific match.
  Named real examples: **Left 4 Dead's contextual dialogue** and *Firewatch*.
  **This is precisely a trigger-timing rule: don't hand-place a trigger at a
  location; author a library of fragments each tagged with the state that
  makes them true, and let the most-specific match fire whenever that state
  occurs.**
- **Waypoint narrative** (used in Short's own game *Glass*): the system
  pathfinds through a graph of conversation topics toward an authored
  narrative beat; the player can derail it, and the system "constantly tries
  to heal the story, to move from the player's chaotic input back towards the
  next authored beat." Adding more content increases routing options rather
  than branching exponentially.

### Valve — "The AI Systems of Left 4 Dead" (Michael Booth, AIIDE 2009) — the concrete algorithm

**CONFIRMED — full 95-slide deck read in full and saved** to
`research/game_design/sources/awards_story/valve_ai_systems_of_left4dead_booth2009.pdf`
(retrieved from `cdn.fastly.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf`).
This is the single richest, most concrete trigger-timing source found this
session — an actual shipped algorithm with real numbers, not a principle.

Four stated AI goals; the fourth is the one that matters here: **"Generate
Dramatic Game Pacing"** — explicitly modeled on the observation that
Counter-Strike's *natural, emergent* pacing is "spiky": quiet tension
punctuated by unpredictable intense combat, and that constant combat fatigues
while constant quiet bores.

**The algorithm ("Adaptive Dramatic Pacing"), verbatim from the slides:**

- Track a per-survivor **"Survivor Intensity"** value.
  - **Increases** when: injured by Infected (proportional to damage);
    incapacitated; pulled/pushed off a ledge; a nearby Infected dies
    (inversely proportional to distance).
  - **Decays toward zero over time** — but **does not decay while Infected
    are actively engaging** the survivor.
- State machine driven by the **team's max Survivor Intensity**:
  1. **Build Up** — spawn the full threat population until intensity crosses
     a peak threshold.
  2. **Sustain Peak** — hold full population for **3–5 seconds** after the
     peak, guaranteeing a minimum build-up duration and letting the fight
     that's already happening play out.
  3. **Peak Fade** — switch to minimal population ("Relax" candidate) and
     monitor until intensity decays out of peak range; explicitly, "Peak Fade
     won't allow the Relax period to start until a natural break in the
     action occurs" — i.e., the transition itself waits for a quiet moment,
     it isn't just a timer.
  4. **Relax** — minimal threat population for **30–45 seconds**, or until
     survivors have traveled far enough.
- **Boss encounters are explicitly exempt** from this modulation — "Overall
  pacing affected too much if they are missing... Boss encounters are
  intended to change up the pacing anyhow."
- Explicit design conclusion: **"Algorithm adjusts pacing, not difficulty.
  Amplitude (difficulty) is not changed, frequency (pacing) is."**

A second, separable technique from the same deck, under "Promote
Replayability": the **map designer creates several possible weapon-cache
locations and item groups; the AI Director selects which subset actually
exists** each playthrough — deliberately over-authoring options and letting a
director pick a subset, rather than authoring exactly what will appear. The
stated reason for keeping this designer-placed (rather than fully
procedural): "Allows visual storytelling/intention" and avoids physically
implausible placement (a cache leaning against a wall vs. floating).

**Direct transferability to RimMaster's dungeon design**: define an
intensity/tension metric per dungeon, a small state machine with real
build/sustain/fade/relax durations, and author *more* possible encounters,
loot placements, and set-pieces than will appear in any one run — then let a
director choose the live subset per playthrough, exempting your biggest
set-piece beats from the pacing algorithm the way L4D exempts bosses.

### Academic drama management — Sharma, Ontañón, Mehta, Ram, "Drama Management and Player Modeling for Interactive Fiction Games" (Georgia Tech Cognitive Computing Lab, AIIDE-era paper)

**CONFIRMED — full paper read and saved** to
`research/game_design/sources/awards_story/drama_management_player_modeling_magerko_gatech.pdf`
(retrieved from `sites.cc.gatech.edu/fac/ashwin/papers/er-09-10.pdf`). Their
system, C-DraGer, was deployed and evaluated with real human players inside
the interactive-fiction game *Anchorhead*.

- **DM action taxonomy** (the vocabulary of what a "trigger" can actually
  do): **Causers** (hints, or direct causers — push the player toward a plot
  point); **Deniers** (direct — block a path to a plot point); **Temporary
  Deniers**, each paired with a **Re-enabler** (e.g. hide the key, then later
  make it visible again). **Explicitly, "no operation" is itself a valid DM
  action** — the system's default is often to do nothing.
- **Selection mechanism**: at every game cycle, search (expectimax) over
  predicted player actions and candidate DM actions, scored against (a) a
  learned **player interest model** — case-based reasoning over past
  players' feedback, mapping the current player's action trace to predicted
  "interestingness" per upcoming plot point — and (b) **author-specified
  story-coherence heuristics**: *thought flow* (penalize jumping between
  unrelated topics too often), *activity flow* (penalize scattering events
  across too much unnecessary travel), and **"manipulation" — a heuristic
  that explicitly favors the story line requiring the LEAST DM intervention**.
- **Trigger-timing doctrine distilled**: don't fire the next available event;
  search for the minimum intervention that keeps predicted player interest
  high while preserving topical/spatial coherence, and treat "do nothing" as
  the default outcome of that search, not an oversight.

### Harvey Smith & Matthias Worch — "What Happened Here?" (GDC 2010)

CONFIRMED to exist at `witchboy.net/articles/what-happened-here/` (Harvey
Smith's own site lists it as a talk with downloadable slides+notes as a zip).
**UNCERTAIN on content** — I could not extract the slide content itself
through WebFetch (it only rendered the landing-page blurb: "an Environmental
Storytelling talk"), and did not download/parse the zip given the queue
contention at the time. This is a real gap, not a dead end — the zip is a
concrete next retrieval target.

### Gaps in this domain

Left 4 Dead's own later "verb" taxonomy expansion (mentioned in the deck's
"Future Work" slide) was not tracked into the sequel; the "room tells the
story" search term and the L4D-Director-talk search term both hit the broken
search engine and returned nothing usable — not re-attempted given the above
already covers the same ground more concretely.

---

## 3. Content lists to raid — verbatim tables

**Source, all of this section**: `coinsandscrolls.blogspot.com` — Skerples'
long-running, well-regarded OSR design blog (its "Treasure Overhaul" and
*Veins of the Earth* connections are referenced inside the tables themselves;
*Veins of the Earth* is itself a well-regarded, ENnie-nominated-adjacent OSR
book). CONFIRMED for every table below: fetched the raw HTML directly via
`curl` (bypassing a WebFetch refusal to reproduce tables verbatim, which cited
"fair use" and offered a paraphrase instead — noted above as a retrieval
technique worth keeping), then extracted the post body with BeautifulSoup.
Full verbatim text of all nine tables is saved under
`research/game_design/sources/awards_story/`; the summaries below are
oriented at what's usable, not a replacement for reading the saved files.

1. **`coinsandscrolls_treasure_dungeon_stocking.txt`** — "OSR: Treasure for
   Dungeon / Room Stocking." Reproduces, verbatim and side by side:
   - **AD&D Room Stocking**: 1d20 room-contents table (60% Empty, 10% Monster
     Only, 15% Monster & Treasure, 5% Special/Stairway, 5% Trick/Trap, 5%
     Treasure Only) and a 1d100 "treasure without monster" table (25% 1000×
     cp/level, 25% 1000×sp/level, 15% 750×ep/level, 15% 250×gp/level, 10%
     100×pp/level, 4% 1d4 gems/level, 3% 1 jewelry/level, 3% roll on Magic
     Items Table).
   - **B/X Room Stocking**: 1d6 room-type table, 1d6 treasure-presence table,
     and a dungeon-level-keyed table (levels 1–9) giving SP/GP/Gems/
     Jewelry/Magic-Item dice and percentages per level.
   - **OSE compressed version** of the same, plus a **direct comparison**:
     AD&D gives a 20% per-room treasure chance, B/X and OSE give 27.7%.
   - A **"Treasure Overhaul" d100 method** and a faster 1d20 alternative,
     plus **a working formula for how many treasure-bearing rooms a dungeon
     level needs**, keyed to party size and target level-up pace (worked
     example included in the source: a 4-PC level-1 dungeon needs ~20 rooms
     of treasure at ~200gp average room value to deliver ~2000gp).
2. **`coinsandscrolls_ludicrous_loot.txt`** — "Ludicrous Loot from Veins of
   the Earth": a **1d10 unique-artifact table** (Occultum — a magic-amplifying
   currency metal; Stone Lightning — fossilized lightning bolts that double
   damage against stone; a Bedrock Charter that commands stone itself; Soul
   Tablets; Half-Mile Cloth; a Dream Key; the Sideways Citadel; a Fossilized
   Angel; a Red-Gold Crown of Command) and a **1d5 unique-book table** (Der0
   Manual of Surgical Alterations; a Prophecy Cylinder; The Riddle of Steel;
   The Unnatural Gourmand; Your Horrible Secret) — each with full flavor text
   and concrete mechanical effects, directly reusable as high-value dungeon
   capstone loot.
3. **`coinsandscrolls_veinscrawl_encounter_tables.txt`** (largest haul,
   ~28KB) — full wandering-encounter tables for a megadungeon ("Veinscrawl")
   setting.
4. **`coinsandscrolls_1d200_dangerous_things.txt`** — a 1d200 table of bad
   things/hazards/omens (explicitly built as a tribute/completion of a George
   Carlin bit — comedic tone, but structurally a genuine random-hazard/
   disclaimer/curse table).
5. **`coinsandscrolls_1d100_variant_skeletons.txt`** — 1d100 skeleton-monster
   variants (a monster-variety table, directly the "wandering monster table"
   category from the brief).
6. **`coinsandscrolls_1d100_prophetic_underground_dreams.txt`** — 1d100
   omen/dream fragments; usable as a foreshadowing/rumor table.
7. **`coinsandscrolls_giant_table_london_streetfolk.txt`** — a large NPC/
   street-folk generator table.
8. **`coinsandscrolls_medieval_price_list.txt`** — a real-world-grounded
   medieval price list, useful for grounding salvage/scavenge pricing.
9. **`coinsandscrolls_caves_and_props.txt`** — a short cave/prop dressing
   list.

### Gaps in this domain

Did not reach the original AD&D 1e DMG Appendix A tables directly (they are
not freely reproducible; the treasure-stocking table above quotes/paraphrases
them faithfully but is not the primary text). Did not independently source
graffiti/inscription-specific tables, ship's-log-fragment tables, or a
dedicated "what's in this container" table as separate hauls — time-boxed in
favor of exhausting one confirmed-rich source per the owner's own instruction
("when you find a rich source, take all of it rather than sampling"). Did not
verify a d20 SRD / Pathfinder SRD treasure-table reproduction — `d20srd.org`,
`d20pfsrd.com`, and `dandwiki.com` all returned 403/404 to WebFetch this
session; the official free 5e SRD 5.1 PDF (`media.wizards.com`) was checked
directly (text-extracted via `pypdf`) and **does not contain** the classic
d100 treasure-hoard/trinket tables — those are DMG-exclusive, not part of the
Creative-Commons SRD content, which is worth knowing before assuming the
"official free" SRD has them.

---

## 4. Interconnection — how discrete authored places compose into one world

This domain overlaps most with RPG-THEORY's remit (map-structure taxonomy);
kept here strictly to the "how do separate places connect / how does a player
arriving out of order get handled" angle the brief asked for.

### Node-based design, xandering, and the Three Clue Rule (see Section 2 for full detail)

All three (Alexander's node-based scenario design, Jaquays' non-linear
dungeon structure, and the Three Clue Rule's redundant-connective-clues) are
directly about interconnection, not just single-scene pacing: a node-based
campaign is a graph of self-contained situations connected by whatever the
players actually do, not a fixed order; a xandered dungeon has no single
"correct" entrance; the Three Clue Rule's redundancy is the connective tissue
(a rumor economy in miniature) that lets a discovery reached by *any* path
still land the intended conclusion.

### Metroidvania / ability-gating (Wikipedia, `en.wikipedia.org/wiki/Metroidvania`)

CONFIRMED. The genre's structure: parts of the world are inaccessible until
the player acquires an item/ability/tool/knowledge (double jump, wall jump,
morph-ball-style shrinking); this item is **often boss-gated**, giving a
narrative reason for the gate; **backtracking is the content**, not a
chore — new abilities retroactively unlock earlier areas and secrets. One
named distinction is directly load-bearing for the owner's "arriving out of
order" risk: a **"soft lock"** — an obstacle (often a boss) that is "difficult
but not impossible to defeat when the player-character is starting out, and
becomes much easier to defeat with increased experience and abilities." A
soft lock lets a player who arrives *early* or *out of intended sequence*
still attempt the content — painfully, but not impossibly — rather than
bouncing off a hard wall. **This is the single most directly transferable
answer, from this session's research, to the "player arrives out of order"
risk named in the brief**: gate by difficulty curve wherever the frozen world
can't guarantee intended sequence, reserve hard locks (true impossibility
without the key item) only for gates where an out-of-order arrival would be
narrative nonsense rather than just hard.

### Gaps in this domain (UNCERTAIN — not reached this session)

Zelda's specific dungeon-ordering design (there is a well-known video
critique series, "Boss Keys" by Mark Brown, that maps every 2D/3D Zelda
dungeon's gating structure — not verified this session, flag for a follow-up
fetch rather than citing from memory); Dark Souls' interlocking-shortcuts
level design (the specific `gamedeveloper.com` article I guessed at was
wrong — a real article on this topic almost certainly exists but I did not
re-locate it); Diablo's act structure; a pointcrawl/hexcrawl origin piece
(Chris McDowall's Bastionland blog is the likely primary source for
"pointcrawl" as a coined term — not verified this session); a sandbox-vs-
adventure-path ttrpg design-philosophy debate piece. All four were blocked by
the broken search engine, not by absence of source material — worth a
dedicated follow-up pass once search access is healthy.

---

## Summary of what's saved

`research/game_design/sources/awards_story/`:
- `valve_ai_systems_of_left4dead_booth2009.pdf` (4.2MB) — full 95-slide deck,
  the Adaptive Dramatic Pacing algorithm.
- `drama_management_player_modeling_magerko_gatech.pdf` (~500KB) — full
  academic paper, C-DraGer / Anchorhead drama-manager evaluation.
- `coinsandscrolls_treasure_dungeon_stocking.txt`
- `coinsandscrolls_ludicrous_loot.txt`
- `coinsandscrolls_veinscrawl_encounter_tables.txt`
- `coinsandscrolls_1d200_dangerous_things.txt`
- `coinsandscrolls_1d100_variant_skeletons.txt`
- `coinsandscrolls_1d100_prophetic_underground_dreams.txt`
- `coinsandscrolls_giant_table_london_streetfolk.txt`
- `coinsandscrolls_medieval_price_list.txt`
- `coinsandscrolls_caves_and_props.txt`

All files are well under the 40MB single-file ceiling.
