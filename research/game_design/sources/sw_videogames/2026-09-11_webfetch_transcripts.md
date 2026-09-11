# WebFetch source transcripts — SW video game dungeon research

Retrieved 2026-09-11. Each block is the AI-summarized extraction WebFetch returned
for the given URL (WebFetch converts HTML to markdown then a small model answers
the prompt — this is NOT the raw article text, it is a filtered summary of it).
Treat as CONFIRMED for the specific quoted phrases (which are verbatim from the
source) and the facts attributed to named critics; treat any unquoted paraphrase
as CONFIRMED-paraphrase, still traceable to the URL.

Two Fetcher SEARCH batches were also filed the same day and were still queued
behind ~30 sibling-agent requests at write time (shared local Fetcher instance,
one directive processed at a time). Not yet delivered:
- `/Users/mandrake/dev/Fetcher/Requests/2026-09-11_sw_dungeons_batch1.txt` (12 SEARCH directives:
  Star Forge, Korriban, Taris Undercity, Manaan, Trayus Academy, Peragus, Zeffo tombs GDC,
  Bogano vault, Survivor chambers, Dark Forces maze retrospective, Jedi Knight analysis,
  Jedi Outcast/Academy retrospective)
- `/Users/mandrake/dev/Fetcher/Requests/2026-09-11_sw_dungeons_batch2.txt` (12 SEARCH directives:
  SWTOR flashpoints, SWG dungeons, Republic Commando, Battlefront maps, LEGO SW gating,
  scavenging/junk-world games, Fallen Order metroidvania map analysis, Nar Shaddaa,
  Dantooine ruins, KOTOR2 Nar Shaddaa Vogga worm, Dark Forces/Jedi Knight postmortem,
  Dathomir witch fortress puzzle)

When Fetcher drains this queue, results land at
`~/.cache/Fetcher/Delivery/2026-09-11_sw_dungeons_batch1/` and `...batch2/` (7-day local
cache — copy anything needed into this sources folder). This file should be revisited
and merged with those results, especially for room-by-room walkthrough detail on
Star Forge, Korriban tombs, Manaan, and Trayus Academy, which no source below actually
gives at that granularity.

---

## https://en.wikipedia.org/wiki/Star_Wars:_Knights_of_the_Old_Republic

Locations: Dantooine and Korriban as Jedi/Sith academies; opens on Taris after a
crash-landing; Star Forge space station as final battleground. Ebon Hawk is "a
playable location, though no combat takes place on board" in the original games.
KOTOR won GOTY from IGN, GameSpot, Computer Gaming World, PC Gamer, etc.; its story
twist ranked #2 in Game Informer's top ten video game twists (2007).

## https://en.wikipedia.org/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_%E2%80%93_The_Sith_Lords

Eight primary playable environments: Peragus Mining Facility (opening, protagonist
regains consciousness), Telos IV (hub world, Atris), Nar Shaddaa (incl. Goto's yacht),
Dxun + Onderon (paired, Onderon a devastated revisit from game 1), Dantooine and
Korriban (ruined versions of game-1 locations), Malachor V (Trayus Academy, climax).
Ebon Hawk, Harbinger (hijacked Republic cruiser), Ravager (Sith cruiser) as additional
explorable spaces.

Development: started Oct 2003 with 7 Obsidian staff, grew to ~30; Chris Avellone
called the compressed 14-16 month timeline the cause of an "unfinished" state; COO
Chris Parker called the schedule "extremely aggressive." Biggest cut: the droid planet
M4-78, dropped after E3 2004; its assets were repurposed into the Nar Shaddaa yacht
level (per designer Kevin Saunders). TSLRCM (fan restoration mod) fixed ~500 bugs and
restored content; a planned official Switch DLC release of it was cancelled in June
2023, and Aspyr later said (revealed Dec 2025) this was due to being unable to secure
permission from all 22 original mod contributors plus a Disney preference for legal-name
over username crediting.

Reception: Metacritic 85 (PC) / 86 (Xbox). GameSpy named Kreia best character of 2005.
Criticism: identical graphics to game 1, technical issues incl. pathfinding bugs
("warp and skip around the map"); GameSpy acknowledged the rushed, incomplete ship.
~1.5M copies sold by early 2006 (1.275M NA by 2008).

## https://en.wikipedia.org/wiki/Star_Wars_Jedi:_Fallen_Order

Metroidvania structure: "new areas are accessed as Cal unlocks skills and abilities."
Five planets: Bogano, Zeffo, Kashyyyk, Dathomir, Ilum — each revisited multiple times.
"Force powers function as lock-and-key mechanisms for puzzle-solving and secret
discovery," with wall-run, double-jump, force-push, force-pull gating new areas.
Reception: exploration widely praised — "beautifully realized," "always well-rewarded
for exploring off the beaten path," comparisons to Tomb Raider puzzles; some critics
felt certain areas were too "gamey," compromising immersion. No fast travel, by design,
to encourage exploration.

## https://en.wikipedia.org/wiki/Star_Wars_Jedi:_Survivor

Metroidvania framework continues; unlockable shortcuts speed repeat visits. Koboh
(main hub planet): lead designer Martin Badowsky — "a dense central area with more
open outskirts areas as players explore outwards," landing pads placed centrally.
Jedha designed to feel "ancient"/"mythical" (Mediterranean/Egyptian refs); Tanalorr
"heaven-like, otherworldly" (blue/purple palette).

Puzzles: seven High Republic-era "Meditation Chambers" scattered on Koboh, explicitly
inspired by "the shrines found in The Legend of Zelda: Breath of the Wild" — reward
perks/skill points. "Force Tears" are optional challenge rooms with a skill-point
reward.

Reception on space design: Morgan Park — Koboh is "a collection of linear levels
connected to a central area like spokes on a wheel." Ali Jones — Respawn "failed to
populate these vast spaces beyond throwing challenges" constantly, despite Koboh
"dwarfing all of Jedi: Fallen Order combined." Dan Stapleton praised density/craft;
Alessandro Fillari found climbable surfaces hard to identify; Alice Bell said
traversal options "may become overwhelming."

## https://en.wikipedia.org/wiki/Star_Wars_Jedi_Knight:_Dark_Forces_II

21 levels with objectives. IGN's Tom Chick: "The levels can be awfully linear,
throwing you up against some frustrating brick walls where you don't know where to
go or what you're supposed to do next." IGN also: "No other first person shooter has
come close to Jedi Knight's dizzying sense of scale and its vast levels." Next
Generation praised "the wide-open nature of the levels but their high level of
functionality and organic feel." Puzzles require either Force power use or finding
a specific object. No individual level names surfaced in this article (checked
explicitly — only story locations Nar Shaddaa and Sulon/Barons Hed appear, not level
titles).

## https://en.wikipedia.org/wiki/Star_Wars:_Dark_Forces

Jedi engine allowed multi-floor level architecture — unusual for a 1995 FPS. "Ships
come and go at the flight decks, rivers sweep along, platforms and conveyor belts
move." GameSpot: levels are "diverse and ingenious, with plenty of creative obstacles,"
recreate the Star Wars aesthetic, and are "more mentally challenging than your average
key hunt," while "occasionally frustrating." Mentions "multi-step puzzles such as
mazes controlled by switches." Lead developer Daron Stinnett aimed for an "active
environment."

## https://en.wikipedia.org/wiki/Star_Wars_Jedi_Knight_II:_Jedi_Outcast

Built with GtkRadiant (per designer Chris Foster); small team, many roles overlapped.
Linear level progression with "a variety of puzzles." Programmer Mike Gummelt: head-sever
was disabled by management request; lightsaber timing drew on "Bushido Blade."
Reception split: IGN called level design "intelligent" but said the game "starts too
slowly" (GameSpot agreed); Eurogamer and X-Play both said level design "succumbs to the
Dark Side," calling out "illogical and frustrating situations." Net read: stronger
mid/late game, weak over-puzzle-heavy opening.

## https://en.wikipedia.org/wiki/Star_Wars_Jedi_Knight:_Jedi_Academy

Mission-based, deliberately non-linear: players choose mission order, need only 80%
completion to advance the plot. Design process: paper-plan levels first for size/flow,
then apply Quake III engine detail (lighting), polish gameplay last. Level designer
Justin Negrete: Hoth was "one of the most challenging areas to design," built from
extensive Empire Strikes Back reference. Reception split: GameZone liked the pacing
variety ("fast blast... beat in ten or so minutes" vs. hour-long missions, "very
refreshing"); Game Over Online said the free-order mission structure "only serves to
weaken the plotline" / creates "disjointedness," while GameSpot and IGN defended it for
balance and accessibility.

## https://en.wikipedia.org/wiki/Star_Wars:_Republic_Commando

Core mechanic: squad leadership over 3 AI squadmates via a contextual "squadmate order
system" — sealed doors trigger breach-and-clear prompts, terrain offers sniper-position
orders; squadmates default to explosives/hacking/sniper roles; downed troopers can be
revived, permadeath only if the whole squad drops at once. Notable levels: Geonosis
(opening — assassinate Sun Fac, sabotage droid factory + AA bunker) and Kashyyyk
(climax — squad splits to man four AA turrets against advanced droids, ends with Sev
separated and a forced evac). Reception: praised for story/characters/combat, criticized
for a short campaign and average multiplayer; Metacritic 78; called "one of the best
Star Wars video games ever made."

## https://en.wikipedia.org/wiki/Star_Wars:_The_Old_Republic

Confirms "the game features dungeons and raids in the form of Flashpoints and
Operations respectively," but the article gives almost no per-instance design detail —
just patch-note mentions of new Flashpoints/Operations being added, and that
Knights of the Fallen Empire introduced a solo mode for story-critical flashpoints
(an explicit accessibility-driven design shift toward single-player-viable instanced
content, relevant to a game with no forced grouping).

## https://en.wikipedia.org/wiki/Star_Wars_Galaxies

Kashyyyk "is divided into a small central area with several instanced 'dungeon' areas,"
contrasted with other planets' "16 square kilometers of openly navigable area" — i.e.
SWG explicitly used small instanced pockets ("dungeons") carved out of an open world,
architecturally close to this campaign's "sealed sub-structure in a colony map" idea.
Level-90 "Heroic" group missions: Tusken Invasion, IG-88, Axkva Min, Imperial Star
Destroyer, Exar Kun (five named heroic instances — NOT a "Death Star" instance per this
source; that lead is UNCONFIRMED here). Hoth added Nov 2008 as an instance depicting the
Battle of Echo Base. Reception: praised for sandbox scale, criticized for complexity and
thin quest content; later updates (notably the NGE) drew heavy backlash (not detailed
in this article).

## https://en.wikipedia.org/wiki/Lego_Star_Wars:_The_Video_Game

Story mode is chapter-linear; once a chapter's levels are cleared they're freely
replayable in Free Play with any unlocked character. Studs (currency) fuel unlocks;
each level hides 10 minikit canisters that assemble into vehicles in a hub "Parking
Lot." Free Play access is explicitly character-ability-gated: replaying with a
different unlocked character (Force powers, special jumps, etc.) opens areas the
original story-mode character roster couldn't reach. Reception: "puzzles and battles
are undemanding but fun" (NYT); Edge on session length, "rarely goes beyond 20 minutes
at a time." Metacritic 76-79 — "generally favorable," praised mainly for accessibility,
not challenge.

## https://en.wikipedia.org/wiki/Star_Wars:_Battlefront_(2004_video_game)

Two era campaigns (Clone Wars, Galactic Civil War), each switching the player's faction
mid-campaign; Clone Wars campaign ends at Kashyyyk (pre-Episode III release). Notable
maps: Kashyyyk, Geonosis, Endor, Hoth, Kamino; Jabba's Palace added as a bonus map in the
2024 Classic Collection remaster. Core loop: capture/hold command posts, up to 25+
vehicles, some maps include neutral/hostile indigenous forces. Reception: visuals
praised ("Never before have the Star Wars battles been so well recreated and detailed");
single-player criticized for confusing, disjointed faction switches.

## https://en.wikipedia.org/wiki/Star_Wars:_Empire_at_War

RTS: space battles (starfighter squadrons + capital ships, upgradeable space stations)
and ground battles (infantry + vehicles, capturable Reinforcement Points), tied together
by a 3D galactic strategic map (e.g. controlling Kuat cuts ISD price 25%). No dungeon-like
authored site content surfaced in this article — this is a confirming negative: EaW's
"sites" are generic capturable planets/battle maps, not authored puzzle/gated spaces.
Metacritic 79; GameSpot positive, IGN noted repetitive battles; 6.7M copies sold by 2017;
AIAS Strategy Game of the Year nominee.

## https://en.wikipedia.org/wiki/Metroidvania

Genre-defining gating mechanic, not Star-Wars-specific but load-bearing for how Fallen
Order/Survivor gate progress: "Not all areas of this map are available at the start,
often requiring the player to obtain an item (such as a weapon or key) or a new
character ability to remove some obstacle blocking the path forward." Ability unlocks
also "open up shortcuts that reduce travel time" — the backtrack-with-new-tool loop.
Neither Fallen Order nor Survivor is actually named in this particular article (checked
explicitly) — the genre-mechanics description is sourced here, the game-specific
application is sourced from the Fallen Order/Survivor articles above.
