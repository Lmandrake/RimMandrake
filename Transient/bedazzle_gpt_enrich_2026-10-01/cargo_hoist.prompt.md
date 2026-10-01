You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants a UNIVERSAL VERTICAL CARGO DEVICE — "the ship's hoist" — to become a signature mechanic of the campaign, reused all over the place. Your job: tell us how to NEST this device into the campaign (where it lives, how the player meets it, how it grows), and list EVERY useful plot moment it could serve.

# The owner's words (verbatim, typos kept)

"Your idea for the hoist should be repurposed. Inhabited locations ijnhutt territories that are slave pits. You can sell any slave to the pit and the characters walk them over and lower them down the pit. Also has slaves already down there in an oubliette that cannot get out. Will also pay for unconscious beasts even if not tamed. Slave put fodder for the arenas. Could also have dungeon entrances that support this joist up and down. Now I'm wondering if we can have a universal cool new mechanic be the ships's houst. A cargo device that is universal for vertical cargo movement. Could be a unique gravship component in this campaign. Reuse it all over the place. ... get gpt commentary on how to next it and all the differentnusefulnplot moments it might help in. I named two here. Could we even incorporate a lottery in the hutt trading areas like that cool old catapult idea from the ancients rimworld expansion mod in their vault? Replaced what you sent with items of similar value. Lots of possibilities here. Just have to be careful we don't get caught in endless animation development."

# The device as designed so far (build on this; do not redesign the core)

- THE KEEL HOIST: a winch, cable and cradle. One C# comp everywhere. It moves things VERTICALLY between two places walking does not connect.
- Two forms: (1) SHIP FORM, a fitting inside the Odyssey gravship (only buildable where a grav engine is), which flies with the ship and drops its cable onto any cave mouth / shaft / hatch / pit the ship parks over; (2) PLACED FORM, a fixed head-frame over one mouth, owned by NPC sites (Hutt pits, old vaults, mines) and possibly buildable by the player.
- Two target kinds: MAP-TO-MAP (paired with an existing RimWorld MapPortal: a cave mouth into an underground pocket map, a dungeon entrance, the ship's sea-dive hatch; cargo lands beside the exit below, and a "cradle" cell below sends things up) and WITHIN-MAP (onto a cell nobody can walk to: the floor of a pit room, a cliff shelf).
- It moves items, colonists, slaves, prisoners, downed pawns, and (new) downed WILD animals and downed strangers, who arrive captured.
- Engine route: subclass of MapPortal reusing vanilla's load dialog and haul jobs; transit is a hidden timer, not an animation. TETHER LOCK: the gravship cannot launch while a cable is down (Harmony postfix on the engine's launch check). That is its main cost: your ship is pinned while the cable is deployed.
- Visual budget is a HARD rule: a drawn line for the cable and two static sprites (cradle empty/loaded). No animation is required for anything. Any idea that needs frame animation, rigging or a cinematic is disqualified unless it degrades to "fade, then it is there".
- Hutt slave pit: the pit buys slaves and unconscious beasts (tame or not); your own pawns walk them over and lower them; slaves already trapped in an oubliette below; the oubliette feeds the Hutt arenas.
- Hutt lottery ("chance chute"): you load cargo and pay a stake; it goes down; hours later a crate comes up with items of similar total market value (rolled: mostly 0.7-1.1x, rare 3x jackpot, rare 0.3x dud; the house keeps a cut). Inspired by Vanilla Quests Expanded - Ancients' pneumatic tube launch port (send cargo from a vault, "you may receive some goods from another vault in return").

# Binding project rules (violating one disqualifies the idea)

- RimWorld 1.6, ALL five DLCs present (Royalty, Ideology, Biotech, Anomaly, Odyssey); depend on them freely.
- One fixed, hand-made, tidally locked desert planet (dayside, terminator, nightside). NO worldgen features, no procedural planets. Content lives on maps, sites, incidents, pawns, buildings, quests.
- The player is a Jawa scavenger clan (Star Wars flavour). Their sandcrawler and their identity are salvage, trade, droids.
- THE SHIP IS THE ONLY WAY DOWN TO AND BACK FROM THE SEA FLOOR. Owner: "You can't 'dive' as an individual pawn nor return as one. It's ship or nothing." The hoist is part of the ship, so it may serve the seas, but no idea may let an individual pawn reach the sea floor by itself.
- Powerful tech is GOOD. Balance it by cost or gating, never by narrowing what it can do.
- Every mod ships real Mod Settings.
- Free tier (RM_) uses only INVENTED names and must stand alone; genuine Star Wars IP (Hutts, Rancors, Sarlacc, canon species) lives only in the campaign layer (RUT_). Say which tier each idea belongs to.
- No animal or pawn ever vanishes without a readable sign (a letter, a mark, a trail).
- Own superdeep pits already exist as a design: a pit is terrain, an enclosed pit area is a room, prisoners are captured "from the lip" without anyone entering. An earlier "oubliette" pit FITTING was cut by the owner; do not re-pitch a trap-fitting.

# Existing campaign hooks you may nest into (all real)

- Lantern Deeps: an underground pocket map of living crystal reached through a cave mouth/old mineshaft on the coldest surface maps; superbly equipped dead miners; dead droids worn by immobile crystal minds.
- Four terminal seas with sea-floor pocket maps reached through a hatch built inside the gravship.
- Dungeons: Foundry towers (one deep floor each), six breached Ancient vaults (one holds frozen Rakata), the Assailant's frozen first-impact site whose thaw needs an "old power core" delivered to a hidden socket, Fever Wood ant hives (reactive procedural dungeons), a Sarlacc pit planned as stacked pocket maps.
- Hutt Cartel faction: Gorga the Immense's Palace with planned districts (palace hall, holding pens, cistern court, spicehouse); a captive-droid trade (droids in Hutt torture chambers, buy or rescue); an arena-beast trade (Rancor "under the trapdoor", Acklay, Reek, Nexu); a pitched casino; a slave pen "the player cannot unsee; a liberation choice with a price".
- Fall-zone wreckage whose manifests can point at lost cargo.
- The Jawa religion "the Salvation": nine small jealous gods (Ohm the living machine, Zizzik malfunction, Mob'Unloo ledger and exchange, Ozzik who always seeks to enslave and always fails, Oomo, Rekko, Sh'kaar, and others); rites can be taught by places.
- The Galactic Empire pursues; selling certain goods raises Imperial heat and Hutt interest.

# What we want back

1. NESTING (about 400 words): where the device first appears, how the player first meets it (found, bought, salvaged, taught?), how it grows (upgrades, research rows, a placed form), which faction "owns" its culture, and the single best ORDER to introduce its uses so it feels like one campaign spine rather than a feature list. Include one paragraph on how it should feel to the player.
2. PLOT MOMENTS: AT LEAST 20, numbered, each 2-4 sentences: the situation, what the hoist does in it, the decision it creates, and tier (RM_ or RUT_). Cover at least: the Hutt slave pit (selling, the oubliette, buying someone back up, arena fodder), the lottery, dungeon entrances, Lantern Deeps, the seas (within the ship-only rule), rescue, theft/raid while tethered, the Empire, the Jawa gods, the sandcrawler, and at least four you think of that we did not. Mark your THREE BEST with a star and say why in one line each.
3. RESEARCH: for at least eight of the moments, cite what it draws from (game + feature, or mod + feature: e.g. Oxygen Not Included rocket cargo, Dwarf Fortress minecarts/pits, Frostpunk, Kenshi slavers, Subnautica, Factorio, Barotrauma, Sunless Sea, Darkest Dungeon, FTL, Vanilla Expanded mods, SOS2, Anomaly's pit gate) and what ours does that the source does not.
4. SCOPE TRAPS: the five places this design is most likely to sink into "endless animation development" or endless engineering, and the cheapest acceptable stand-in for each.
5. Your honest critique: one paragraph on what is weakest about the device or the lottery as designed, and one change you would make.

Keep the whole answer under 3,500 words. Plain prose and numbered lists; no tables wider than four columns.
