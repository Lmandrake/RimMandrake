# SW-MODERN: FFG / Saga Edition / Imperial Assault adventure corpus

Scope: every Star Wars tabletop RPG line EXCEPT West End Games D6 (sibling agent's
domain). FFG Edge of the Empire / Age of Rebellion / Force and Destiny, WotC d20/Saga
Edition, Imperial Assault, and anything else adventure-shaped in this space.

## Retrieval situation — read this before trusting anything below

- **WebSearch is refused outright** for this model group (400: "tool type
  'web_search_20250305' is not supported") — confirmed by direct test this session.
- **Fetcher was filed with ~20 SEARCH/FETCH directives** across 5 request files
  (`2026-09-11_sw_modern_batch1..5` in `~/dev/Fetcher/Requests/`) covering every
  named lead plus Imperial Assault, Dawn of Defiance, Genesys. **None completed in
  this session.** Fetcher's process stayed alive and actively connected
  (confirmed via `lsof` — a live HTTPS connection to a CloudFront endpoint) but its
  single shared queue had 35-40 pending request files from concurrent sibling
  research agents and made zero visible progress across ~20 minutes of polling.
  This is a congestion problem, not a Fetcher malfunction — **the queued
  directives may still land after this session ends; re-poll
  `~/dev/Fetcher/Complete/` for files matching `sw_modern_batch*` before
  re-running this research.**
- **WebFetch worked for Wikipedia and archive.org's search API**, but returned
  402/403 for every Fandom (starwars.fandom.com, swrpg.fandom.com), DriveThruRPG,
  RPGGeek, and BoardGameGeek URL tried — consistent bot-protection blocks, not
  transient. DuckDuckGo HTML search hit a CAPTCHA; Bing HTML search returned
  generic dictionary/unrelated results (the query terms were apparently not
  reaching Bing's actual index through the fetch path used).
- **No adventure's actual room-by-room text was reached this session.** Every
  finding below is either (a) confirmed-real product metadata from Wikipedia, a
  tertiary source, or (b) explicitly marked UNREACHED. **Nothing below is a
  reconstructed room list — where I could not reach the text, I say so.**

## CONFIRMED real titles (Wikipedia, cross-referenced across two articles) — UNCERTAIN detail tier (wiki summary, NOT the adventure text)

Source for all of this section: `en.wikipedia.org/wiki/Star_Wars:_Edge_of_the_Empire`
and `en.wikipedia.org/wiki/Star_Wars:_Age_of_Rebellion`, fetched directly this
session. These are plot-hook-level summaries only — no area lists, no NPC
stats, no puzzle text.

**Edge of the Empire:**
- *Escape from Mos Shuuta* (Dec 17, 2012) — 32-page adventure bundled in the
  Beginner Game box; pre-generated characters + maps included in the box.
- *The Long Arm of the Hutt* (Dec 14, 2012) — sequel to Escape from Mos Shuuta,
  free PDF.
- *Under a Black Sun* (Jun 15, 2013) — Free RPG Day giveaway, Corellia, Black
  Sun pirate syndicate; later re-released digitally as *Shadows of a Black Sun*.
- *Beyond the Rim* (Sep 6, 2013) — REAL. Crews race to find the lost
  Separatist treasure ship *Sa Nalaor*.
- *The Jewel of Yavin* (Mar 31, 2014) — REAL. Heist adventure, target is a
  corusca gem.
- *Mask of the Pirate Queen* (Nov 19, 2015) — REAL. Bounty hunt targeting the
  Pirate Queen of Saleucami.

**Age of Rebellion:**
- *Takeover at Whisper Base* (Apr 25, 2014) — 32-page Beginner Game adventure.
- *Onslaught at Arda I* (Aug 14, 2014) — REAL. Secret Rebel base, includes mass
  combat rules and new vehicle stats. (Separately corroborated: 8 distinct
  actual-play podcast episodes on archive.org covering "Episode 1" through
  "Episode 3," suggesting the published adventure runs long enough to fill
  multiple real-play sessions — itself a pacing data point, though the episode
  count reflects a specific group's pace, not an official session estimate.)
- *Friends Like These* (Dec 8, 2016) — REAL. Defense of planet Xorrrn and
  Rebel shipyards; adds Mandalorian character-creation rules.

**Force and Destiny:**
- *Mountaintop Rescue* (Jun 18, 2015) — 32-page Beginner Game adventure.
- *Chronicles of the Gatekeeper* (Nov 5, 2015) — REAL. A Jedi holocron draws
  Force-sensitives into a knowledge-vs-corruption quest.
- *Ghosts of Dathomir* (Oct 19, 2017) — REAL. Outer Rim journey, Force visions,
  buried galactic secrets.

**Metric worth keeping:** all three beginner-box one-shots are stated at 32
pages — a concrete page-count anchor for "how long is a single-session FFG
adventure," useful for our duration/tedium metrics even without the text.

## Leads NOT found in the confirmed official adventure catalog

*Lure of the Lost, Debts to Pay, Operation: Shadowpoint, Perlemian Haul, Hidden
Depths, Dead in the Water* — none of these appear in either Wikipedia article's
adventure list for Edge of the Empire / Age of Rebellion / Force and Destiny.
This does not prove they're fictitious — several FFG sourcebooks (*Suns of
Fortune*, *No Disintegrations*, *Fly Casual*, *Special Modifications*, etc.)
embed shorter adventure seeds inside splatbooks rather than shipping as
standalone PDFs, and some of these names read like they could be sourcebook
chapter titles or fan/actual-play episode titles rather than standalone
products. **Status: UNCERTAIN — unresolved, not refuted.** Needs the Fetcher
backlog to clear, or a direct DriveThruRPG/RPGGeek catalog browse once those
domains stop 402/403-ing WebFetch.

## Confirmed real but content UNREACHED

- **Imperial Assault** (board game, FFG) — confirmed real via Wikipedia and
  BoardGameGeek listing, but its campaign-guide mission structure, tile system
  rules, and any named campaign missions were **UNREACHED** this session
  (fantasyflightgames.com 403s WebFetch directly; BoardGameGeek and
  Wayback Machine snapshots are also blocked from this tool). This is the
  single highest-value unexplored target named in the brief — an actual
  grid-based dungeon corpus closest to RimWorld's tile grid — and deserves a
  dedicated follow-up once Fetcher clears.
- **Dawn of Defiance** (WotC Saga Edition campaign) — Wikipedia has no
  dedicated article; a general Star Wars RPG lines article confirms WotC's
  "Star Wars Roleplaying Game (2000–2010)" line existed but gives zero
  adventure-level detail. **UNREACHED.**
- **Genesys** (FFG's spun-off narrative-dice system, mechanically identical to
  EotE/AoR/F&D) — no Wikipedia article found under either title tried;
  UNREACHED as a way to document the advantage/threat/triumph/despair trigger
  mechanics without needing the Star Wars-branded books themselves.

## What this means for the design questions in the brief

The narrative-dice trigger-logic question ("is it unusually rich, does it
transfer?") and every map/puzzle/loot-table ask **could not be answered this
session** — no adventure's actual text was reached. The one structural fact
that did surface (32-page one-shots as the FFG "unit" for a single beginner
adventure) is real but thin. Recommend a follow-up pass once
`~/dev/Fetcher`'s queue has drained, filed again against the same targets in
`2026-09-11_sw_modern_batch1..5.txt`.

## Sources saved

None — no full text or images were successfully acquired this session (every
attempt either 402/403'd or the designated search fallback did not return
before this session's time budget closed). No files were written under
`research/game_design/sources/sw_modern/` because nothing was actually reachable
to save; that directory was created but is empty. Re-run once Fetcher's queue
clears — the filed requests may still be resolving.
