# Star Wars video games — authored dungeon-like levels and their layouts

Scope: SW-VIDEOGAMES lane of the dungeon-design research fan-out for RimMaster's
Jawa scavenger campaign. Companion/sibling lanes (do not duplicate): SW-D6,
SW-MODERN, SCIFI-DERELICT, RPG-THEORY, METRICS, AWARDS-PUZZLES, plus three agents
reading local RimWorld disk state.

**Status of this pass:** built from direct `WebFetch` retrieval (Wikipedia primarily
— accessible; Fandom/wiki.gg/StrategyWiki/IGN/Polygon all returned 401/402/403 or an
explicit block from this environment's fetch path) plus two Fetcher `SEARCH` batches
that were filed but **not yet delivered** at write time — the local Fetcher instance
was serving a shared queue of ~30+ requests from sibling research agents and had not
reached mine. Their eventual output lands at
`~/.cache/Fetcher/Delivery/2026-09-11_sw_dungeons_batch1/` and `...batch2/` (7-day
cache) and should be pulled into this file on a follow-up pass — see the exact
directive list in `sources/sw_videogames/2026-09-11_webfetch_transcripts.md`.

**Important limitation, stated per the no-fabrication rule:** no source found this
pass gives a room-by-room walkthrough map for Star Forge, the Korriban tombs, Manaan,
Peragus, or Trayus Academy. Everything below about those places is at the level Wikipedia
game-articles operate at (named areas, order of visitation, a few named beats, critic
commentary) — real, sourced, and useful, but NOT the connection-graph-level detail the
task ultimately wants. Getting that requires either the pending Fetcher searches for
walkthrough/fan-map sites, or a licensed strategy guide. Flagged UNCERTAIN below wherever
this bites.

Legend: **CONFIRMED** = stated in a source I read, URL given. **UNCERTAIN** = inference,
recollection, or a lead not yet run down — says what's missing. **DOES-NOT-TRANSFER** =
depends on avatar/3D camera/jump/real-time reflex; RimWorld has none of these.

---

## 1. KOTOR is the right place to dig hardest, and here's why concretely

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars:_Knights_of_the_Old_Republic,
https://en.wikipedia.org/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_%E2%80%93_The_Sith_Lords)
— KOTOR 1 and 2 are party-based with pausable, largely turn-resolved combat (d20-derived),
not twitch/reflex-based. That control scheme — order a party, watch resolution, no jump
button, no first-person aim — is the same category as RimWorld's indirect pawn control.
This is the single most transferable game in the whole SW video-game catalog for THIS
campaign's control scheme.

**Locations confirmed to exist and their narrative role** (both articles above):
KOTOR 1 — Taris (opening, crash-landing), Dantooine (Jedi academy hub), Korriban (Sith
academy), Star Forge (final area). KOTOR 2 — Peragus Mining Facility (opening,
protagonist wakes with amnesia), Telos IV (hub, Atris), Nar Shaddaa (incl. a yacht
level), Dxun/Onderon (paired locations, Onderon is a devastated revisit of a
KOTOR-1-adjacent world), Dantooine and Korriban again but **ruined** versions of their
KOTOR-1 selves (a direct "same place, changed by time/war" reuse worth stealing for a
frozen-world campaign that can't add new maps later), Malachor V culminating in the
**Trayus Academy**.

**UNCERTAIN / gap:** the actual room graphs (how many rooms, branch points, backtrack
points) for any of these are not sourced yet. Needs: a walkthrough site (GameFAQs,
StrategyWiki via a route that isn't 403'd) or the pending Fetcher batch.

## 2. KOTOR II's production history is itself a transferable lesson about scope

**CONFIRMED** (KOTOR II Wikipedia article) — Obsidian built the game in 14-16 months
starting with 7 people, growing to ~30; lead writer/designer Chris Avellone attributed
the game's unfinished feel directly to that schedule. The **droid planet M4-78** was
cut wholesale after E3 2004 once the team recognized the timeline couldn't support it,
and its assets were folded into the smaller Nar Shaddaa yacht level rather than wasted.
This is a real, documented case of "cut a whole authored place and salvage its pieces
into a place you're keeping" — directly relevant to a frozen, never-expanding world
where a cut dungeon can't be patched back in later; better to fold its best rooms into
one that ships. The **fan-restoration (TSLRCM)** case is a second lesson: even 20 years
later, restoring cut official content required corralling 22 individual mod contributors
for legal clearance and Disney's naming preferences killed a planned official Switch
re-release of the restoration — evidence that "we'll add it back later" for a shipped,
frozen artifact is a much bigger ask than it looks.

## 3. Fallen Order / Survivor: the puzzle grammar transfers even though the traversal cannot

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars_Jedi:_Fallen_Order,
https://en.wikipedia.org/wiki/Star_Wars_Jedi:_Survivor) — both games are explicit
Metroidvania structures: "new areas are accessed as Cal unlocks skills and abilities,"
and Force powers are described in-source as "lock-and-key mechanisms for puzzle-solving."
Survivor adds named optional puzzle rooms: **seven "Meditation Chambers"** on the hub
planet Koboh, explicitly modeled on Breath of the Wild shrines, each a self-contained
puzzle+reward unit; and **"Force Tears,"** smaller optional challenge rooms with a
skill-point payoff.

- 🔑 **DOES-NOT-TRANSFER:** wall-run, double-jump, force-push/pull-as-traversal, and any
  puzzle whose solve is "jump/climb/dash through this in real time." All of this
  requires an avatar with a controllable jump arc and a chase camera. RimWorld pawns
  don't jump and aren't directly steered.
- **Indirect-control analogue that DOES exist:** the underlying pattern — "ability X,
  once acquired, removes a specific named obstacle, which was visible-but-blocked all
  along" — is exactly the gating grammar of a RimWorld quest reward, research project,
  or an item a pawn must be carrying/wearing. The self-contained optional puzzle-room
  unit (a "Meditation Chamber" — walk in, solve one discrete mechanism, walk out with a
  reward, unrelated to the main path) maps cleanly onto a sealed sub-structure that a
  squad enters, solves via object manipulation (levers, power routing, a terminal), and
  exits — no traversal-skill content required for the RimWorld version at all.
- **Reception, worth weighing as a caution:** Koboh (Survivor's open hub) was described
  by critic Morgan Park as "a collection of linear levels connected to a central area
  like spokes on a wheel," and Ali Jones criticized that the game "failed to populate
  these vast spaces beyond throwing challenges" constantly despite the area dwarfing all
  of Fallen Order combined. **Lesson: bigger authored space with the same puzzle density
  reads as emptier, not richer — density must scale with size, not just item count.**

## 4. Dark Forces / Jedi Knight era: the maze criticism is real and specific

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars_Jedi_Knight:_Dark_Forces_II,
https://en.wikipedia.org/wiki/Star_Wars:_Dark_Forces) — IGN's Tom Chick on Jedi Knight
(Dark Forces II): "The levels can be awfully linear, throwing you up against some
frustrating brick walls where you don't know where to go or what you're supposed to do
next." The SAME reviewer/outlet praised the game's "dizzying sense of scale." So the
period's signature failure mode is confirmed as: **scale without legibility** — big,
freely-navigable 3D space with no readable next-step signal, producing "where do I go"
frustration rather than satisfying exploration. Dark Forces (1) is confirmed to use
"multi-step puzzles such as mazes controlled by switches," and GameSpot's period review
called the puzzling "more mentally challenging than your average key hunt" while still
"occasionally frustrating."

- 🔑 **DOES-NOT-TRANSFER:** the maze-as-3D-navigation-challenge itself (relies on a
  first-person camera and manual wayfinding). **What DOES transfer:** the failure mode
  is a legibility lesson, not a geometry lesson — a RimWorld dungeon (sealed
  sub-structure, travel site) can still fail the same way if it hides its next-step
  signal, even though the player never "gets lost in 3D space" the way an FPS player
  does. The switch-gates-a-door pattern itself is control-scheme-agnostic and transfers
  directly (a pawn flips a switch/pulls a lever/interacts with a console; no reflex
  needed).

## 5. Jedi Outcast / Jedi Academy: two opposed structural experiments, both with documented reception

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars_Jedi_Knight_II:_Jedi_Outcast,
https://en.wikipedia.org/wiki/Star_Wars_Jedi_Knight:_Jedi_Academy) — Outcast is
strictly linear; multiple outlets (Eurogamer, X-Play) said its level design "succumbs to
the Dark Side" via "illogical and frustrating situations," while IGN called the SAME
game's level design "intelligent" — a genuine critical split on the identical content,
worth citing as evidence that "good level design" verdicts are not uniform even among
professional critics. Academy instead used a **mission-select structure**: complete only
80% of available missions in any order to advance — Game Over Online said this
"weakens the plotline" via "disjointedness," while GameSpot/IGN defended it for
"balance and accessibility." Academy's designer Justin Negrete called **Hoth**
specifically "one of the most challenging areas to design," built from direct Empire
Strikes Back reference material.

- **Transfers directly, no camera dependency:** the choice between a strictly ordered
  chain of dungeons vs. a partial-completion-required set the player can tackle in any
  order is a pure structural/pacing decision, identical in kind whether the "player" is
  a first-person avatar or a colony issuing caravan orders. The 80%-not-100% threshold
  is a specific, citable number worth reusing as a METRICS input for "how much of a
  hub's optional content must be gated vs. optional."

## 6. Republic Commando: the closest thing in the whole catalog to RimWorld's actual control input

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars:_Republic_Commando) — the whole
game is built around **giving contextual orders to AI squadmates** rather than directly
controlling them: sealed doors surface a "breach-and-clear" order, terrain surfaces a
sniper-position order, squadmates default into explosives/hacking/sniper roles, and
downed troopers are revived by squadmates (total wipe is the only real fail state). The
climactic Kashyyyk level requires **splitting the squad** to man four separate
anti-aircraft turrets simultaneously.

- 🔑 **This is a DOES-TRANSFER, not a caveat** — it is literally the same input
  paradigm as ordering RimWorld colonists (assign a role/task, let the AI execute,
  intervene contextually), just applied to combat instead of colony work. The
  "split the squad across N stations that must all hold at once" beat from Kashyyyk is
  directly portable as a multi-objective dungeon climax requiring a colony to split its
  strike team across simultaneous console/turret/valve stations.

## 7. Star Wars Galaxies: the one confirmed precedent for "small sealed dungeon carved out of an open map"

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars_Galaxies) — Kashyyyk in SWG "is
divided into a small central area with several instanced 'dungeon' areas," explicitly
contrasted against other planets' fully open 16 km² of navigable terrain. This is the
one piece of hard evidence in this pass of a Star Wars game explicitly building
small sealed instanced pockets inside an otherwise-open persistent world — structurally
identical to this campaign's "sealed sub-structure in a colony map" brief. Level-90 group
"Heroic" instances were confirmed named: Tusken Invasion, IG-88, Axkva Min, Imperial
Star Destroyer, Exar Kun; a Battle-of-Echo-Base instance was added for Hoth in Nov 2008.

- **UNCERTAIN:** a "Death Star instance" was in this task's lead list but this source
  does NOT confirm it — the five named Heroics above are what's confirmed, no Death Star
  among them. Do not carry the Death-Star-instance claim forward as fact; it needs its
  own source or should be dropped.
- No control-scheme conflict here: SWG heroics are MMO group content, same
  DOES-NOT-TRANSFER caveat as SWTOR below for any real-time dodge/positioning mechanic,
  but the container concept (small instanced pocket cut from a big open map) transfers
  with zero modification.

## 8. LEGO Star Wars: the single cleanest confirmed case of ability-gated (not reflex-gated) content

**CONFIRMED** (https://en.wikipedia.org/wiki/Lego_Star_Wars:_The_Video_Game) — Free Play
mode explicitly reopens a completed level with a different unlocked character, and that
character's specific powers (Force abilities, special jump types, etc.) open areas the
original story-mode roster could not reach. Studs (currency) and 10 hidden minikits per
level are collected through exploration/destruction and gate cosmetic/vehicle unlocks,
not the main path.

- 🔑 **DOES-NOT-TRANSFER:** the traversal half (a "special jump" is still a jump).
- **DOES transfer, and cleanly:** the GATING LOGIC — "this specific unit-type, and only
  this one, can open this specific path" — is precisely a RimWorld-native pattern
  already: a colonist with a required skill, an EMP-capable pawn, a xenotype with a
  specific gene, or a specific held item, gates a specific route. LEGO Star Wars is
  useful less as a level-design reference and more as clean, citable confirmation that
  "swap which unit is doing the exploring to reach previously-blocked content" is an
  established, well-received (Metacritic 76-79, praised for accessibility) design
  pattern independent of whether that unit's superpower is a jump.

## 9. SWTOR flashpoints: named as dungeons, but this pass found almost no design detail

**CONFIRMED, thin** (https://en.wikipedia.org/wiki/Star_Wars:_The_Old_Republic) — the
article states flatly that SWTOR "features dungeons and raids in the form of Flashpoints
and Operations respectively," and confirms that Knights of the Fallen Empire added a
**solo mode for story-critical flashpoints** — an explicit, dated design decision to make
instanced dungeon content completable without a group. That solo-mode pivot is itself a
useful data point: even a game built around group content ended up shipping a way to
solo its dungeons.

- **UNCERTAIN / real gap:** no specific flashpoint's layout, boss sequence, or puzzle
  design surfaced from this source. This is exactly the kind of detail the still-pending
  Fetcher batch was searching for; needs a follow-up pull.
- DOES-NOT-TRANSFER for anything that is a real-time boss mechanic (telegraphed AoE
  dodges, interrupt timers) — those need reflexes RimWorld pawns don't have and a player
  camera RimWorld doesn't have. The STRUCTURE (linear approach, trash encounters,
  named boss, mechanic-gated final room) is control-scheme-agnostic and transfers as a
  pacing template regardless.

## 10. Battlefront (2004) and Empire at War: confirmed as NOT dungeon content — useful negative results

**CONFIRMED** (https://en.wikipedia.org/wiki/Star_Wars:_Battlefront_(2004_video_game),
https://en.wikipedia.org/wiki/Star_Wars:_Empire_at_War) — Battlefront's maps are
capture-and-hold conquest battlegrounds (command posts, up to 25+ vehicles), not
authored gated spaces; its single-player criticism was about narrative
faction-switching, not level layout. Empire at War's "sites" are a 3D strategic galaxy
map plus generic space/ground RTS battle maps (e.g., controlling Kuat cuts Imperial
Star Destroyer cost 25%) with no dungeon-like authored content surfaced in the article.

- **Verdict for this research line: both are confirmed OUT of scope for dungeon-map
  templates.** Recorded here specifically so a later pass doesn't re-spend a Fetcher
  search rediscovering the same negative result.

## 11. Metroidvania genre definition (not SW-specific, but load-bearing)

**CONFIRMED** (https://en.wikipedia.org/wiki/Metroidvania) — the genre's core gating
text: "Not all areas of this map are available at the start, often requiring the player
to obtain an item... or a new character ability to remove some obstacle blocking the
path forward," and ability unlocks "open up shortcuts that reduce travel time." This is
the formal statement of the exact pattern both Fallen Order and Survivor use (see §3) —
cited separately here because this general-genre article does not itself name either
Star Wars game (checked explicitly; the SW-specific application is sourced to their own
articles).

---

## Retrieval notes for whoever continues this

- `WebFetch` worked reliably on `en.wikipedia.org` (200, real content each time) and
  failed on every non-Wikipedia domain tried: `starwars.fandom.com` (402),
  `starwars.wiki.gg` (401), `strategywiki.org` (403), `www.ign.com` and
  `www.polygon.com` (explicit "Claude Code is unable to fetch from" block),
  `www.giantbomb.com` (403 on a guessed URL — also a rule violation, don't repeat: never
  guess an article URL).
- `WebSearch` is refused outright for this model group (confirmed again this session,
  matches the brief's warning).
- The **Fetcher** local script was running and reachable, but its request queue was
  shared with ~8 sibling research agents filing in parallel; my two batches
  (`sw_dungeons_batch1`, `sw_dungeons_batch2`, 12 SEARCH directives each) were still
  unprocessed after roughly 10 minutes of polling. They are NOT lost — Fetcher retries
  automatically and nothing needs refiling — but this file's KOTOR/Manaan/Trayus/Zeffo
  room-level gaps specifically need those results pulled once
  `~/.cache/Fetcher/Delivery/2026-09-11_sw_dungeons_batch1/` (and `batch2`) populate.
