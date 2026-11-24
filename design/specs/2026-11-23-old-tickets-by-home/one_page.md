# The old tickets by home (2026-11-23, 9:45 PM PST)

All counts are measured from the ledger. The kept list is on the ledger. Print it with
`python3 src/RimMandrake/rimflow/list_home.py counts` (or `list`, `list --home mod:FlowWorks`, `no-home`).

**The set.** 1,105 open tickets that were filed before Shape went live (2026-11-23, 6:00 AM PST). 923 of them are what is
left of the 936 (13 closed since). The other 182 were outside the 936 because they wait on something. They are just as
old, so they got homes too.

| kind of home | tickets | homes | looks current | looks overtaken | cannot tell |
|---|---|---|---|---|---|
| mods and biomes | 617 | 101 | 463 | 46 | 108 |
| pipeline repair | 294 | 18 | 126 | 12 | 156 |
| game needs above one mod | 171 | 25 | 138 | 5 | 28 |
| machines and accounts | 21 | 3 | 10 | 0 | 11 |
| could not place | 2 | - | 1 | 0 | 1 |
| **all** | **1,105** | | **738** | **63** | **304** |

72 younger tickets have no home yet. The list names them. A new ticket shows there until someone gives it a home.

- **Mods, largest:** FlowWorks 65, SWBestiary 26, TheRot 23, Rites 22, TerminalBiomes 22, Scarlands (the Warscar) 20,
  LongShade 17, DivingInteraction 16, Minerals 16, CreatureBehaviors 14, EnvironmentalHazards 14, StarWarsRaces 13. The
  other 89 homes hold 1 to 12 each. Four of the 101 have no folder of that name: TheScald, TheChill, Umbra, ArtistMuse.
- **Game needs:** art and canon 31, world map and its painting 23, flight 14, mods to remove or replace 13, seas 12,
  Direct Sun 11, load errors 8, the ship 8, campaign events 7, biome casts 6, map generation 6, Mod Settings 5, dungeons and
  wreckage 5, canonical saves 4, audio 3, naming 3, and 9 homes with 1 or 2.
- **Pipeline repair:** Operations 52, test lane 50, bridge 43, rule documents 30, Conductor tools 24, Maturation Pipeline
  21, art pipeline 20, judges 10, helpers 8, owner review 8, Designer 6, Dispatcher 6, ledger 4, and 5 homes with 1 to 3.
- **Machines:** SteveDesktop 12, accounts 5, Archmagi 4.
- **Largest groups of one mod or need:** facing redraws 13, found rites 12, the mineral registry 12, the Cathedral
  concealment arc 9, Sleeping Ice new life 9, the Grey and Twilight Seas 9, flyer flip-books 9.
- **The same kind of ticket in many mods:** old Designer first passes 39, first scripts 37, the GPT review of 2026-10-08
  37, live checks of old builds 24, red validation rows 20, "no giant for the titan passage" 15.
- **Looks overtaken, 63:** 41 write build items for the retired Relentless Pipeline (39 are the Designer first passes), 4
  name a deleted `RUT_` twin biome, 3 repaint the world early, and 15 others. Each one names what overtook it.
- **Could not place, 2:** `RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL` (it says that its home mod is
  undecided) and `UTILITY_CREATURES_DESIGN_DIG_THIS_PIT_BOY` (an idea for a mod with no name).

## Your worry: tickets out of line with modern needs

I found no ticket that builds worldgen, a path without a DLC or a per-biome heat exception (a word search of the whole
prose, plus the reading). The risk that I found is smaller: tickets for retired machinery and deleted biomes (the 63), and
tickets that recheck an old build or cite an old measurement (most of the 304 "cannot tell").

## Mods and biomes: they wait with their mod

No mod ticket goes to Shape. When a mod advances, its Designer run reads `python3 src/RimMandrake/rimflow/list_home.py
list --home mod:<Mod>`. It drops the overtaken tickets with the reason that the list names. It takes the others as input to
the version that it designs. Nothing more is built for this now, so for now the Conductor puts that command in the press.

## Pipeline repair: what grouped runs need

One ticket at a time: 294 runs for pipeline repair (the sort's count of about 800 was for all old tickets). Grouped: **39
runs for 254 tickets**. The other 40 tickets need no new run:

- 21 are standing alarm tickets and 2 are standing host items. Their own watch works them.
- 12 are the plain-English rewrite, which has its own chain of runs.
- 3 old Designer passes and 2 clone-pool tickets look overtaken. The Conductor reads them and drops them.

| part | groups, one run each (tickets) |
|---|---|
| Operations | scratch and disk (9), telemetry (7), alarm faults (6), sense-phase overruns (5), phone alerts and start package (4) |
| test lane | red selftests and nightly (11), bridge-conditions migration (11), proof honesty (10), testq faults (9), testq tick and cache (4), scene tools (3) |
| bridge | game-health record (16), client and companion safety (10), companion tools (9), bridge conditions (8) |
| rule documents | inventory and canon corrections (8), retired words and seats (6), skills and reviews (4) |
| Conductor tools | seat restart (12), pointers, studies and spend (12) |
| Maturation Pipeline | walks, looks and pages (8), tick, ceilings and records (7), tickets and principles (6) |
| art pipeline | art evaluation (8), install and ledger (7), tool faults (5) |
| judges | briefs and calibration (5), code reading (5) |
| owner review | choices and messages (4), look and card tools (4) |
| one group each | Dispatcher (6), helper launch (6), ledger (4), Designer stage (3), def tools (3), deploy and lists (3), List Pipeline (3), publish and git (2), hooks (1) |

A run first drops what fails the worth-the-touch test, then fixes the rest. Whether a group of 12 to 16 fits in one run is
a guess (~60%); if not, add 4 runs.

## How far to trust this

One agent placed each ticket. A program put the old Designer passes, the first scripts, the harness-repair tickets and the
titan-passage tickets by rule, 95 in all, and the agent saw each of those titles too. For each ticket the agent read the
title and the start of the prose, not the whole of a long prose. No fix was tried, and nothing was closed. A random check
of 60 tickets found each home fitting its title. The same agent made that check. A wrong home is corrected with one
`rimflow home` command.
