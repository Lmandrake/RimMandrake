# RimWorld Hand-Crafted Map Atlas
## Publicly discoverable custom terrain, scenic starts, authored levels, and reusable map sources

**Research date:** 2026-08-07  
**Target game:** RimWorld, with special attention to the current 1.6 / Odyssey ecosystem  
**Scope:** local RimWorld map tiles that were deliberately *authored*—terrain sculpted, rivers/coasts/mountains repainted, landmarks/ruins/dangers deliberately placed, or an entire playable level composed—rather than simply a beautiful colony built on an ordinary random seed.

> **Completeness warning.** “All known” cannot literally mean every private Discord upload, deleted Reddit post, unpublished commission, or unindexed save file. This document is a best-effort census of the **publicly discoverable/indexable handcrafted-map scene** I could verify across Reddit, GitHub, Steam Workshop/Discussions, Ludeon forums, YouTube, Patreon, and surviving map-sharing tools. I deliberately exclude ordinary colony screenshots, lucky seeds, and purely procedural Geological Landforms rolls unless the creator explicitly says the map was further designed or edited.

---

# 1. Executive findings

1. **u/UnknwnBuilds is the dominant identifiable public RimWorld map-maker.** Their GitHub profile explicitly describes their work as world design/map making and, as of this research date, exposes **37 public RimWorld map repositories**. Those repositories are an unbroken numbered run from **World 25 through World 61**. Their Reddit history proves the numbering began earlier: a January 2023 post calls four maps “#11 to #14,” and their Discord post says downloads and commissioned/requested worlds were collected in `#World_Downloads`. Therefore **at least 61 numbered worlds have existed**, but Worlds 1–24 are not all recoverable from the open-web archive.
2. The linked Reddit creator’s method is not just “generate until pretty.” The repeated pipeline is: **Map Preview / Map Designer for a blockout → Developer Mode for hand placement/painting → landmarks/ruins/dangers/vegetation → distribute as `.rws` and/or Save Maps blueprints**.
3. There is a genuine, if small, **independent map-making scene**: Grapesforlifes, SuperTaster3, VenomSnake1974, and others have published hand-edited maps or downloadable examples independent of UnknwnBuilds.
4. A second tradition is **authored adventure/challenge maps** rather than scenic blank starts: custom Black Hawk Down/medieval scenarios, a World of Warcraft Wailing Caverns recreation, Dungeon Core’s authored dungeon-map framework, and Adam Vs Everything’s RimWorld Community Challenge saves.
5. This practice predates the recent “Designer Map” flair. Direct terrain editing is documented in community discussions by 2019–2020; a 2020 utility could extract maps from saves into reusable map-generator blueprints; Map Designer released in 2020 and became the standard procedural blockout tool.

---

# 2. Inclusion criteria and confidence grades

| Grade | Meaning | Included here? |
|---|---|---|
| **A — verified hand-authored** | Creator explicitly describes Dev Mode / terrain painting / manual sculpting, and/or provides a timelapse/download | **Yes, core catalogue** |
| **B — verified custom-designed** | Creator explicitly says Map Designer/Map Reroll/custom tools were used; amount of tile-by-tile hand work is uncertain | **Yes, marked hybrid** |
| **C — authored scenario/level** | Map is deliberately composed for a scenario, dungeon, challenge, or recreation; beauty may not be the sole goal | **Yes, separate section** |
| **D — procedural only** | Geological Landforms, Map Designer preset, or a lucky seed with no demonstrated manual editing | Usually **excluded**, except a few historically useful examples |
| **Not a map example** | Attractive player base built on ordinary/random terrain | **Excluded** |

### Search method

The sweep used several overlapping routes so one index would not dominate the result:

- Followed the user-supplied UnknwnBuilds Reddit post into the creator’s profile, Discord announcement, newer Reddit releases, GitHub profile, and numbered repositories.
- Searched and paged through Reddit’s **Designer Map**-tagged ecosystem and keyword variants such as `custom map`, `Map Designer`, `dev mode`, `Terrain Set`, and `hand painted`.
- Searched independent creators named in comments and derivative-map posts.
- Searched Steam Workshop for the tools used to create/export maps and Steam Discussions for pre-flair authoring practices.
- Searched Ludeon forums for old map editors/exporters and pre-Workshop map-authoring utilities.
- Searched YouTube/Patreon for timelapses and distributed challenge saves.
- Rejected false positives aggressively: normal bases, merely interesting seeds, and non-RimWorld “custom map” results are not catalogued.

---

# 3. The main corpus — UnknwnBuilds / RimWorld Map Makers

## 3.1 Creator and community provenance

- **GitHub profile:** https://github.com/UnknwnBuilds?tab=repositories  
  Current profile description: world design and map making; files are mainly RimWorld map files. The profile showed **37 public repositories** on 2026-08-07.
- **Reddit profile:** https://www.reddit.com/user/UnknwnBuilds/
- **RimWorld Map Makers Discord announcement:** https://www.reddit.com/user/UnknwnBuilds/comments/zlvbex/rimworld_map_makers_custom_rimworld_map_discord/  
  The creator says the community is centered on custom RimWorld maps, offers downloads to everyone, and that most early maps were requests with downloads in `#World_Downloads`.
- **Current Discord link shown on GitHub:** https://discord.gg/zk2Kv3GkYz  
  The older Reddit announcement itself carries a separately updated invite; Discord invite URLs can expire/change, so the GitHub profile is the safer current pointer.
- **User-supplied early showcase:** https://www.reddit.com/r/RimWorld/comments/zda2hp/some_more_custom_maps_i_made_for_rrimworld_users/
- **January 2023 set, explicitly “#11 to #14”:** https://www.reddit.com/r/RimWorld/comments/1088yn0/ive_created_a_few_more_custom_maps_all_available/

### Their documented workflow

In the January 2023 post, UnknwnBuilds says they use **Map Designer + Map Preview to obtain a base-map idea, then edit the tile more deeply with Dev Tools**. In later posts the same pattern recurs: rough procedural generation first, then manual terrain/rock/object placement. This is the clearest public example of RimWorld being used almost like a 2D level editor.

---

## 3.2 Complete currently public GitHub catalogue — Worlds 25–61

The table below is the **complete public repository run visible on the creator’s GitHub on 2026-08-07**. Titles/sizes/biomes are taken from the repository summaries. The repository numbering is part of the creator’s own naming scheme.

| # | Map | Size | Biome / stone summary | Direct download / repository |
|---:|---|---:|---|---|
| 61 | **Dragons Fall** | 400×400 | Temperate Forest; all stones | https://github.com/UnknwnBuilds/World_61 |
| 60 | **Satsuki** | 250×250 | Boreal Forest & Glacial Plain; Limestone/Marble/Slate; Odyssey | https://github.com/UnknwnBuilds/World_60 |
| 59 | **Secluded Cove** | 400×400 | Temperate Forest; Marble & Slate | https://github.com/UnknwnBuilds/World_59 |
| 58 | **the Dead City** | 500×500 | Temperate Forest, partial Tropical Rainforest; all stones | https://github.com/UnknwnBuilds/World_58 |
| 57 | **Ides Veil** | 250×250 | Temperate Forest; Sandstone & Slate | https://github.com/UnknwnBuilds/World_57 |
| 56 | **Kains Swamp** | 250×250 | Tropical Swamp; Granite & Slate | https://github.com/UnknwnBuilds/World_56 |
| 55 | **Lighthouse Blues** | 200×200 | Temperate Forest; Granite & Sandstone | https://github.com/UnknwnBuilds/World_55 |
| 54 | **Charlottes RimWorld** | 275×275 | Feralisk Infested Jungle (Alpha Biomes); Slate/Granite/Limestone | https://github.com/UnknwnBuilds/World_54 |
| 53 | **The Tar Pits** | 275×275 | Tar Pits (Alpha Biomes); Slate/Marble/Limestone | https://github.com/UnknwnBuilds/World_53 |
| 52 | **Island Inferno** | 300×300 | Biomes! Islands — Jungle Island; Slate & Sandstone | https://github.com/UnknwnBuilds/World_52 |
| 51 | **Darkrest** | 275×275 | Forsaken Crags; Cragstone | https://github.com/UnknwnBuilds/World_51 |
| 50 | **Lush River** | 250×250 | Arid Shrubland; Granite & Marble | https://github.com/UnknwnBuilds/World_50 |
| 49 | **The Estuary** | 350×350 | Temperate Forest; Granite/Limestone/Marble | https://github.com/UnknwnBuilds/World_49 |
| 48 | **Jungle Wound** | 250×250 | Tropical Rainforest; Limestone & Granite | https://github.com/UnknwnBuilds/World_48 |
| 47 | **Mals Hollow** | 250×250 | Tundra; Limestone & Sandstone | https://github.com/UnknwnBuilds/World_47 |
| 46 | **Cervantes Cliffs** | 300×300 | Temperate + Boreal Forest; Slate & Marble | https://github.com/UnknwnBuilds/World_46 |
| 45 | **In Memory of Rain** | 325×325 | Desert; Slate & Marble | https://github.com/UnknwnBuilds/World_45 |
| 44 | **Cathedral** | 275×275 | Temperate Forest; Granite/Sandstone/Marble | https://github.com/UnknwnBuilds/World_44 |
| 43 | **Sacraficial Altar** *(creator spelling)* | 275×275 | Cold Bog; Slate & Granite | https://github.com/UnknwnBuilds/World_43----SacraficialAltar |
| 42 | **Lake Lands** | 300×300 | Temperate Forest; Limestone & Sandstone | https://github.com/UnknwnBuilds/World_42---Lake-Lands |
| 41 | **A Giant's Rest** | 250×250 | Temperate Forest; Slate & Sandstone | https://github.com/UnknwnBuilds/World_41 |
| 40 | **A Riverious Tale** | 250×250 | Temperate Forest; Marble & Slate | https://github.com/UnknwnBuilds/World_40 |
| 39 | **Winterly Mistakes** | 250×250* | Ice Sheet; Marble/Granite/Slate | https://github.com/UnknwnBuilds/World_39 |
| 38 | **Point Sea** | 275×275 | Arid Shrubland; Sandstone & Slate | https://github.com/UnknwnBuilds/World_38 |
| 37 | **Leviathans Rest** | 500×500 | ReGrowth: Temperate Forest; Granite/Slate/Marble | https://github.com/UnknwnBuilds/World_37 |
| 36 | **River Rest** | 250×250 | Tropical Jungle; Sandstone & Slate | https://github.com/UnknwnBuilds/World_36 |
| 35 | **Cythlios ReMemory** | 275×275 | Tundra; Marble & Slate | https://github.com/UnknwnBuilds/World_35 |
| 34 | **Elizes Depression** | 250×250 | Temperate Forest; Marble & Sandstone | https://github.com/UnknwnBuilds/World_34 |
| 33 | **Decayed Mines** | 275×275 | Boreal Forest; Marble | https://github.com/UnknwnBuilds/World_33 |
| 32 | **Ruined Dam** | 300×300 | Temperate Forest; Granite/Sandstone/Marble | https://github.com/UnknwnBuilds/World_32 |
| 31 | **Deserted Trader** | 275×275 | Desert; Marble/Granite/Sandstone | https://github.com/UnknwnBuilds/World_31 |
| 30 | **Feylas Cirque** | 350×350 | Boreal Forest; Marble/Granite/Slate | https://github.com/UnknwnBuilds/World_30 |
| 29 | **Blood Gulch** | 250×250 | Arid Shrubland; Granite & Sandstone | https://github.com/UnknwnBuilds/World_29 |
| 28 | **Flows End** | 300×300 | Temperate Forest; Marble & Slate | https://github.com/UnknwnBuilds/World-28 |
| 27 | **Azurian Meadows** | 300×300 | Temperate + Boreal Forest; Granite & Marble | https://github.com/UnknwnBuilds/World_27 |
| 26 | **The Temple** | 250×250 | Tropical Jungle; Limestone/Sandstone/Granite | https://github.com/UnknwnBuilds/World_26 |
| 25 | **Lumi's Pass** | 250×250 | Temperate Forest; Limestone & Granite | https://github.com/UnknwnBuilds/World_25 |

\*The World 39 GitHub summary contains the obvious typo `250 x 25 0`; the catalogue normalizes this to 250×250 rather than treating it as a novel map dimension.

---

## 3.3 Strong UnknwnBuilds study pieces with process/showcase sources

These are not the only worlds worth opening; they are the best-documented examples where the public source tells us *what was intentionally designed*.

### World 61 — Dragons Fall — landmark as the entire geography

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1s046zo/dragons_fall_a_400_x_400_custom_map_you_have_the/
- Download: https://github.com/UnknwnBuilds/World_61
- Timelapse: https://www.youtube.com/watch?v=Fnq86gnpFJY
- **Why study it:** a giant dead dragon is not decoration placed *on* the map; its corpse is the map’s main landform. The river passes through the mouth, an anima tree occupies the heart, and the creator says the commission specifically requested a dragon + river design. This is the strongest example of **terrain as narrative landmark**.

### World 58 — the Dead City — scenic map becomes an authored ruin level

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1pmpj3p/
- Download: https://github.com/UnknwnBuilds/World_58
- **Why study it:** 500×500 ruined city, constrained coastal access, and multiple custom ancient dangers. This is much closer to a hand-authored expedition destination than to “pretty starting terrain.”

### World 57 — Ides Veil — authored ancient danger

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1p50ez0/
- Download: https://github.com/UnknwnBuilds/World_57
- Timelapse: https://youtu.be/X4IYS3f8JZU
- **Why study it:** explicitly combines terrain design with a custom mechanoid-inhabited ancient danger. Useful example of authored threat placement rather than pure aesthetics.

### World 55 — Lighthouse Blues — landscape, ruin dressing, agricultural traces

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1l05j3r/
- Download: https://github.com/UnknwnBuilds/World_55
- Timelapse: https://youtu.be/J8Xgii3AVu0
- **Why study it:** creator describes beginning from an ordinary beach/flat-mountain base and manually placing stonework, editing beaches, and adding ruins/farms. Good demonstration of **small-scale environmental storytelling**.

### World 51 — Darkrest — Alpha Biomes + manual sculpting

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1j7bytr/
- Download: https://github.com/UnknwnBuilds/World_51
- **Why study it:** begins from Map Designer, then uses Dev Mode operations such as rock/terrain/object placement. Shows that alien biome content can be used as a palette rather than accepting its default generation.

### World 49 — The Estuary — strongest “watch the transformation” example

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1ilq74t/
- Download: https://github.com/UnknwnBuilds/World_49
- Timelapse: https://youtu.be/WP0dSsrVTYw
- Independent smaller adaptation: https://www.reddit.com/r/RimWorld/comments/1io9isn/
- **Why study it:** the creator explicitly encourages comparison between the original Map Designer generation and the hand-authored result. It is a clean demonstration of **procedural blockout vs. artistic finishing**.

### World 46 — Cervantes Cliffs — deliberately authored biome transition

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1esw15l/
- Download: https://github.com/UnknwnBuilds/World_46
- Timelapse: https://youtu.be/c8aOV64wi1A
- **Why study it:** deliberately creates the impression of ecological processes—biome transition, drying river, beaver-dam/sedimentation ideas—using Biome Transitions/Geological Landforms as raw material. Particularly relevant if a map should read as a *place with geological history*.

### World 45 — In Memory of Rain — large-scale desert geomorphology

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1ejwc3l/
- Download: https://github.com/UnknwnBuilds/World_45
- Timelapse: https://youtu.be/NnDEcHzQ-8U
- **Why study it:** intentionally shaped desert dunes, watercourses/deltas, traces of old civilizations and ancient dangers. One of the most relevant studies for arid-world authoring.

### World 44 — Cathedral — ruin as focal architecture

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/1dvziek/
- Download: https://github.com/UnknwnBuilds/World_44
- **Why study it:** ruined cathedral + catacomb + mountain composition. Creator describes rough generation with Map Designer followed by hand work with development tools. Good model for a **single monumental POI** controlling the composition.

### World 32 — Ruined Dam — functional ruin / infrastructural archaeology

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/15cstlq/
- Download: https://github.com/UnknwnBuilds/World_32
- **Why study it:** a ruined dam, former lake, and ancient-complex relationship make the map tell a story of previous infrastructure. This is exactly the “abandoned industrial site” design language useful for explorable world destinations.

### 500×500 Kingdom / isthmus concept-art map

- Reddit showcase: https://www.reddit.com/r/RimWorld/comments/11oxmo8/
- **Why study it:** creator describes using Map Designer + Map Preview for the rough shape and then hand-designing toward concept art, with Geological Landforms’ isthmus form helping the macro-composition. It is a particularly explicit example of **reference-image-to-RimWorld translation**.

---

## 3.4 The pre-GitHub era — Worlds 1–24 and the open-web gap

This is where an “all known” claim needs discipline.

### What is verifiable

- **5 Dec 2022:** the user-supplied post shows multiple requested custom maps by UnknwnBuilds:  
  https://www.reddit.com/r/RimWorld/comments/zda2hp/some_more_custom_maps_i_made_for_rrimworld_users/
- **14 Dec 2022:** the creator announces **Rimworld Map Makers**, says most maps so far were requests, and says all available downloads were collected in Discord’s `#World_Downloads`:  
  https://www.reddit.com/user/UnknwnBuilds/comments/zlvbex/rimworld_map_makers_custom_rimworld_map_discord/
- **10 Jan 2023:** a four-map showcase is explicitly described by the creator as “only #11 to #14”:  
  https://www.reddit.com/r/RimWorld/comments/1088yn0/ive_created_a_few_more_custom_maps_all_available/
- **28 May 2023:** GitHub World 25 appears, after which the currently public GitHub numbering is continuous through World 61.

### What cannot be honestly reconstructed from indexing alone

I did **not** find a complete public title/metadata index for Worlds 1–24. Some were downloadable in Discord and some were shown in Reddit posts, but open-web search does not expose the entire old Discord `#World_Downloads` history. The safest conclusion is:

> **At least 61 numbered UnknwnBuilds worlds have existed. Worlds 25–61 are completely enumerable from current public GitHub; Worlds 1–24 are a partially visible Discord/Reddit-era archive and should not be silently invented.**

For archival work, the **RimWorld Map Makers Discord** is therefore the next place to inspect manually.

---

# 4. Independent scenic / handcrafted map-makers

## 4.1 Grapesforlifes — downloadable custom-landform experiments

**GitHub:** https://github.com/Grapesforlifes  
The account currently exposes two public RimWorld map repositories:

- **Lone Mountain Bay** — https://github.com/Grapesforlifes/Lone_Mountain_Bay_RW
- **Yirah Valley** — https://github.com/Grapesforlifes/Yirah_Valley_RW

### Malta study / precursor work

- Reddit: https://www.reddit.com/r/RimWorld/comments/14jgc0k/
- **Grade A/B.** A 200×350 map loosely based on part of Malta. The creator describes using **Map Preview + Map Designer for general shape, then Dev Tools for terrain and mountains**, and explicitly credits UnknwnBuilds as an influence. This is independent evidence that the same craft pipeline was spreading beyond one creator.

### Lone Mountain Bay

- Reddit: https://www.reddit.com/r/RimWorld/comments/14n4vbl/lone_mountain_bay_225x325/
- GitHub: https://github.com/Grapesforlifes/Lone_Mountain_Bay_RW
- **Grade A.** 225×325. A lone mountain/ridge above a river inlet, with an abandoned sanguophage castle and servants’ quarters. The creator says it took roughly an hour and was partly a proof of concept for simulating elevation in RimWorld’s 2D presentation.

### Yirah Valley

- GitHub: https://github.com/Grapesforlifes/Yirah_Valley_RW
- **Grade A/B.** A second downloadable authored-map repository. Even where the Reddit showcase is less easily indexed, the public repository establishes that it was distributed as a reusable RimWorld map.

---

## 4.2 SuperTaster3 — Mousecliff

- Reddit: https://www.reddit.com/r/RimWorld/comments/1dkv93o/mousecliff_map_design/
- **Grade A — exceptionally well documented process.**
- The creator begins from a Geological Landforms shape (TROMOLO), uses **Map Designer + Map Reroll**, then manually paints the result in Developer Mode. They specifically name `Place Rock` and `Terrain Set`, painting shallow ocean, sand, soil, fertile soil and rough slate, then repeatedly revising edges to make islands/coasts look natural.
- **Why this source matters:** it is one of the best written mini-tutorials on the *craft* of making a handmade RimWorld landscape rather than merely configuring a generator.

---

## 4.3 VenomSnake1974 — first fully landscaped map

- Reddit: https://www.reddit.com/r/RimWorld/comments/1mtwq5y/
- **Grade A.** 300×300. The creator says they began on a grassland map and used Dev Tools for **all the landscaping**, placing bushes/rocks/etc. manually.
- **Why include it:** confirms that a creator can skip the “designer” layer entirely and treat Dev Mode as the map editor.

---

## 4.4 Glittering_West_8092 — ring fortress / straight river map (2026)

- Reddit: https://www.reddit.com/r/RimWorld/comments/1vcpee8/is_this_a_decent_starting_map/
- **Grade B.** The creator explicitly says it is **not a random seed** and was built with “a mod like Map Designer.” The unusually straight river and ring-like mountain fortress are deliberate.
- **Why include it:** a very recent example showing that the “Designer Map” idiom remains active in 1.6-era RimWorld.

---

## 4.5 2021 “Town by the river” — Map Designer-built colony terrain

- Reddit: https://www.reddit.com/r/RimWorld/comments/n1up12/
- **Grade B.** Creator says the map was made with Map Designer, so there is no normal seed to share, and recommends combining Map Designer with Map Reroll.
- **Why include it:** one of the early high-visibility examples of a colony whose attractiveness comes from deliberately configured local geography.

---

## 4.6 2021 infestation colony — Fertile Valley authored start

- Reddit: https://www.reddit.com/r/RimWorld/comments/rk3zdi/
- **Grade D/B hybrid.** The creator used Map Designer and the Fertile Valley preset, then Map Reroll. There is less evidence of manual tile painting than in the core corpus.
- **Why keep it:** useful evidence of the transition from “seed hunting” to “author the desired starting geography.”

---

## 4.7 2023 mountain-city terrain — Map Designer + TerraForm

- Reddit: https://www.reddit.com/r/RimWorld/comments/1191me1/
- **Grade A/B.** The map was generated from Map Designer and then manually modified with **TerraForm**; the creator says an additional crater/mountain layer was added manually.
- **Why include it:** a strong example of using a modded generated macro-shape as a starting canvas and then editing the geometry directly.

---

## 4.8 Estuary derivative — community remixing of a handcrafted map

- Reddit: https://www.reddit.com/r/RimWorld/comments/1io9isn/
- Parent inspiration: https://www.reddit.com/r/RimWorld/comments/1ilq74t/
- **Grade A derivative.** Another player created a smaller 275×275 adaptation of UnknwnBuilds’ Estuary concept and discussed using Save Maps.
- **Why include it:** evidence that handcrafted maps are not only consumed; they can become **design motifs copied/remixed by other players**.

---

# 5. Authored adventure maps, challenge maps, and level recreations

These are not always “blank beautiful colony maps,” but they are highly relevant because they show RimWorld terrain being treated as an authored **level** rather than a procedural backdrop.

## 5.1 Black Hawk Down village + medieval castle scenario (2020)

- Reddit: https://www.reddit.com/r/RimWorld/comments/htm6fn/
- **Grade C.** Creator describes a custom Black Hawk Down story with a desert village and custom villains, plus a medieval scenario with a castle.
- **Importance:** evidence of direct adventure-map/scenario authoring before the modern Designer Map community consolidated.

## 5.2 Wailing Caverns recreation (World of Warcraft) — WIP

- Reddit: https://www.reddit.com/r/RimWorld/comments/1buznzu/
- **Grade C/A.** Creator is recreating WoW’s **Wailing Caverns** inside RimWorld; the cave shape was completed and flooring/terrain were manually edited, with plans for mountain roofing.
- **Importance:** demonstrates literal **level translation** from another game, not just landscape beautification.

## 5.3 Dungeon Core — reusable custom dungeon-map framework

- RimWorld Base summary: https://rimworldbase.com/dungeon-core-mod/
- Steam Workshop search entry should be checked against the current installed 1.6 version before adoption.
- **Grade C.** Public descriptions identify **five dungeon maps plus one randomized dungeon map** and explicitly allow additional custom maps tagged for the Dungeon system. Named custom-map contributors in public descriptions include HaiLuan, Ancot, KT411 and aaaa椿.
- **Importance:** this is the most direct bridge from handcrafted local maps to **repeatable expedition destinations**.

## 5.4 Adam Vs Everything — RimWorld Community Challenge (RWCC)

### RWCC overview / restart (2024)
- https://www.patreon.com/posts/rwcc-returns-105402513

### June 2024 challenge
- https://www.patreon.com/posts/rwcc-june-2024-105403109

### July 2024 — verified custom lakeside map
- Patreon: https://www.patreon.com/posts/rwcc-july-2024-107847162
- YouTube: https://www.youtube.com/results?search_query=Adam+Vs+Everything+RimWorld+Community+Challenge+July+2024+Lakeside+Custom+Map
- **Grade C/A.** July’s published challenge specifically uses a **unique custom map** and downloadable `.rws` variants; the accompanying video describes it as a lakeside custom map.
- **Wider-series caveat:** community recollections describe RWCC as using custom maps month after month, but I only treat July 2024 as primary-source-confirmed here rather than assuming every challenge had a bespoke terrain.

---

# 6. Tool lineage — how this scene became possible

## 6.1 Developer Mode — the original hand editor

### 2020 Steam discussion: built-in terrain editing
- https://steamcommunity.com/app/294100/discussions/0/2992043384045658790/
- A community answer points out that RimWorld itself already provides a crude editor: enable **Dev Mode**, use **God Mode** for instant structures, and use the dev tools’ **place terrain** command. This is the fundamental authoring mechanism behind many later maps.

### 2019-era discussion of terrain editing
- https://www.reddit.com/r/RimWorld/comments/bvan10/
- Community discussion already points players toward dev-mode terrain placement / Terraform-style mods when they want deliberately constructed water/terrain features.

---

## 6.2 Map Designer — procedural blockout, not the final brush

- Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2111424996
- Workshop ID: **2111424996**
- First posted: **2020-05-28**
- Current Workshop page tags it for **1.6**.
- It can manipulate mountain position/shape, terrain fertility/water, stones, object densities, rivers and map features, and can start from presets or from scratch.

### Important RimWorld 1.6 limitation as of this research

The current Workshop description explicitly says the following controls are **temporarily disabled in 1.6**:

- Map Features
- River Banks
- River Style
- Beach Terrain

That means older timelapses can show Map Designer abilities that are presently degraded. For 1.6 handcrafted work, **Dev Mode / Map Edit Tools becomes more important**, especially for precise hydrology and shorelines.

---

## 6.3 Map Preview — see the blockout before committing

- Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2800857642
- Workshop ID: **2800857642**
- Current page supports **1.3–1.6**.
- It displays the map that would generate for a selected world tile, can reroll tile seeds, and is designed to work with Geological Landforms and other map-generation mods.

---

## 6.4 Map Reroll — historical companion to Map Designer

- Ludeon forum thread: https://ludeon.com/forums/index.php?topic=18073.0
- Older creators frequently pair it with Map Designer: establish the desired statistical/shape constraints, reroll until the macro-composition is promising, then hand-edit.
- On modern 1.6, Map Preview’s seed-reroll functionality is often a more current route, but historical posts use Map Reroll constantly.

---

## 6.5 Map Edit Tools — direct current 1.6 editing UI

- Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3229348657
- GitHub: https://github.com/dougbenham/Rimworld-MapEditTools
- Workshop ID: **3229348657**
- Current page tags **1.0–1.6**.
- Provides Architect → MapTools actions including **add/remove roofs, change terrain to any type, and instantly smooth floors/walls**.
- **Importance:** in 1.6 this is a useful complement to the partially-disabled Map Designer controls and vanilla Dev Mode.

---

## 6.6 Save Maps (Continued) — turns a handcrafted tile into a reusable artifact

- Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2916523481
- Workshop ID: **2916523481**
- Current page tags **1.2–1.6**, updated in 2026.
- Can save a complete map as a **blueprint**, with or without items/colonists, then load it elsewhere. It can also save only player-built structures and can override the target map.
- Saved presets live under RimWorld’s config directory (`SavedMapPresets`).
- **Importance:** `.rws` saves are not the only distribution model anymore; Save Maps is the clearest mechanism for building a library of reusable handcrafted terrain blueprints.

---

## 6.7 Better Map Sizes — canvas sizing

- Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2099101052
- Workshop ID: **2099101052**
- Current page tags **1.1–1.6** and permits arbitrary custom map sizes.
- **Caution for 1.6:** recent comments report failures/defaulting to 250×250 for some setups; users point to a separate **Better Map Sizes Fix** or manual mod-setting entry. Treat current compatibility as something to test, not assume.

---

## 6.8 RimWorld Custom Maps utility / MapGeneratorBlueprints (2020)

- Ludeon forum: https://ludeon.com/forums/index.php?topic=50269.0
- GitHub: https://github.com/SickBoyWi/RimWorldMaps
- **Historical importance:** reads a RimWorld save and emits XML usable as `MapGeneratorBlueprints`, aimed at custom home/quest maps. This is an early predecessor to the modern “author a map once, inject/reuse it elsewhere” workflow.

---

## 6.9 RimEdit — very early web-map-editor lineage

- Ludeon forum: https://ludeon.com/forums/index.php?topic=1560.0
- **Historical importance:** an early JavaScript/web editor centered on terrain, roofs, rock and fog. It demonstrates that players were trying to turn RimWorld maps into authorable level data almost from the beginning of the game’s modding history.

---

## 6.10 Tutorial / demonstration source

- **Ic0n Gaming — Map Designer / Map Reroll tutorial:** https://www.youtube.com/watch?v=DTydAEaiCWQ
- Useful as a period demonstration of the 2020-era Map Designer workflow. Current 1.6 controls differ, so use it for concepts rather than exact UI correspondence.

---

# 7. The recurring handcrafted-map workflow — synthesis from the sources

This section is **analysis**, not a claim that every creator follows identical steps.

### Stage 1 — choose a macro-landform

Use a world tile / Geological Landforms / Map Designer to get the coarse geometry: coast, valley, crater, ridge, isthmus, river, cirque, island, mountain mass.

### Stage 2 — reroll for a promising canvas

Do not paint 90,000 cells from nothing if generation can cheaply provide 70% of the structure. Map Preview/Map Reroll lets the author iterate until the large shapes are close.

### Stage 3 — manually sculpt the silhouette

Developer Mode and/or Map Edit Tools does the artistic work:

- paint terrain bands;
- move/create shallow and deep water;
- carve coastlines and islands;
- place rock masses and cliff lines;
- create believable passes, ravines and shelves;
- smooth or deliberately break procedural symmetry.

SuperTaster3’s Mousecliff description is especially useful: the author repeatedly paints and repaints island edges until the boundary reads as natural rather than as a brush stroke.

### Stage 4 — texture the geology/ecology

Add soil transitions, sand/gravel, fertility pockets, stone variation, vegetation clusters, dry channels, marsh, scree and other small-scale signals. This is what separates “edited geometry” from a map that looks plausibly generated by nature.

### Stage 5 — add one or more authored focal landmarks

The strongest maps almost always have a **readable noun**:

- dead dragon;
- ruined dam;
- cathedral/catacomb;
- dead city;
- lighthouse;
- abandoned castle;
- cliff shelf;
- giant’s resting place;
- sacrificial altar.

This is more powerful than mere irregularity because the player can remember and talk about the map as a *place*.

### Stage 6 — seed environmental history

Ruins, abandoned farms, old road alignments, former lakebeds, broken infrastructure, ancient dangers and ecological boundaries imply that something happened before the colonists arrived.

### Stage 7 — package the map

The established routes are:

1. distribute a ready-to-load **`.rws` save**;
2. distribute a **Save Maps blueprint**;
3. in older/custom systems, turn the authored map into a generator blueprint/quest-map asset.

---

# 8. Visual/design patterns worth stealing

Again, these are synthesis from the catalogue rather than quotations from creators.

## 8.1 Make hydrology tell a story

The memorable maps treat water as a physical process: estuaries, deltas, former reservoirs, drying rivers, river mouths, coastline inlets. A river should look like it has a reason to be where it is, not merely a blue stripe across noise.

**Best studies:** The Estuary, Cervantes Cliffs, Ruined Dam, In Memory of Rain, Dragons Fall.

## 8.2 Use topography to define rooms without walls

Cliffs, ridges, islands, necks and passes create natural “rooms” for future gameplay. This gives beauty and tactical identity simultaneously.

**Best studies:** Mousecliff, Lone Mountain Bay, Feylas Cirque, Lumi’s Pass, Secluded Cove.

## 8.3 Put authored content at compositional anchors

A ruin is more convincing when it occupies the place the landscape naturally points toward: at the end of a valley, inside a ring, on an island, against a cliff, below a dam.

**Best studies:** Cathedral, Ruined Dam, the Dead City, Lighthouse Blues.

## 8.4 Design ecotones, not hard biome rectangles

Cervantes Cliffs and multi-biome work show the value of gradual transitions. Where possible, use terrain/plant/soil bands to make one ecological regime bleed into another.

## 8.5 Give the player tempting “wrong” spaces

The strongest authored maps often contain an obviously beautiful/defensible location that is not automatically the optimal one—an island without resources, a safe crater with valuable exterior geothermal/farmland, a ruin that is also dangerous. Handcrafting is wasted if it only produces a free super-base.

## 8.6 Preserve negative space

Procedural RimWorld often fills every region with equivalent noise. Human-authored maps can deliberately leave large calm spaces so a dramatic cliff, city ruin, dragon skeleton, river bend, or mountain face actually reads at map scale.

## 8.7 Treat ancient dangers as rooms in a level

Ides Veil and the Dead City suggest a direction beyond pretty terrain: custom ancient dangers can become **encounter nodes** placed with intent. That is especially powerful for exploration campaigns where arrival should trigger curiosity rather than immediate base-building.

---

# 9. Study-first shortlist — the highest-value references

If there is only time to inspect a dozen examples, these are the ones I would open first:

| Map / source | Why it is unusually instructive |
|---|---|
| **Dragons Fall** | Landmark literally becomes geography; strongest “map tells a story at a glance” example |
| **The Estuary** | Explicit procedural-before / hand-authored-after workflow + timelapse |
| **In Memory of Rain** | Desert geomorphology, deltas, old civilizations—excellent arid-world reference |
| **Cervantes Cliffs** | Designed ecological transition and apparent geological/hydrological history |
| **Ruined Dam** | Infrastructure-as-archaeology; useful model for abandoned industrial destinations |
| **Cathedral** | Monumental ruin + catacomb positioned as map focal point |
| **the Dead City** | Full authored ruined-city destination with custom danger nodes |
| **Ides Veil** | Hand-designed terrain plus bespoke hostile ancient danger |
| **Darkrest** | Shows how alien-biome content can be treated as an editable palette |
| **Mousecliff** | Best written explanation of manual coastline/island painting technique |
| **Lone Mountain Bay** | Independent downloadable proof of concept for “elevation” and abandoned-site storytelling |
| **Wailing Caverns recreation** | Demonstrates literal authored-level translation, useful beyond colony-start aesthetics |
| **RWCC July 2024** | Demonstrates custom terrain packaged as a repeatable story/challenge save |

---

# 10. What this suggests for a handcrafted RimWorld world

The public examples establish three increasingly powerful tiers of authored local-map content:

### Tier A — beautiful starting tile

Hand-sculpt the physical canvas but leave gameplay otherwise vanilla. This is what many Designer Map posts do.

### Tier B — environmental-story map

Terrain + landmark + ruins + resource placement + traces of previous inhabitants. UnknwnBuilds’ best maps live here.

### Tier C — authored expedition level

Terrain + story landmark + deliberately placed threats/ancient dangers + loot/reward logic + possibly scripted/incidental content. Dungeon maps and challenge saves point in this direction.

For a world where many destination tiles should feel unique, **Tier C is the important leap**: the landscape is not just scenic; it becomes a location with an encounter grammar.

---

# 11. Current 1.6 authoring stack — practical reference

| Role | Tool | 1.6 status visible in current source | Source |
|---|---|---|---|
| Procedural blockout | **Map Designer** | Tagged 1.6, but Map Features/River Banks/River Style/Beach Terrain temporarily disabled | https://steamcommunity.com/sharedfiles/filedetails/?id=2111424996 |
| Preview / seed iteration | **Map Preview** | Tagged 1.6; actively updated | https://steamcommunity.com/sharedfiles/filedetails/?id=2800857642 |
| Direct hand editing | **Vanilla Dev Mode** | Built into game; longstanding terrain/object tools | https://steamcommunity.com/app/294100/discussions/0/2992043384045658790/ |
| Direct editing UI | **Map Edit Tools** | Tagged 1.6 | https://steamcommunity.com/sharedfiles/filedetails/?id=3229348657 |
| Reusable map blueprints | **Save Maps (Continued)** | Tagged 1.6; updated 2026 | https://steamcommunity.com/sharedfiles/filedetails/?id=2916523481 |
| Custom canvas dimensions | **Better Map Sizes** | Tagged 1.6, but current user reports show setup/compat issues | https://steamcommunity.com/sharedfiles/filedetails/?id=2099101052 |
| Macro landforms | **Geological Landforms** | Commonly paired with Map Preview/Designer; verify current installed version | https://steamcommunity.com/sharedfiles/filedetails/?id=2773943594 |
| Historical reroll workflow | **Map Reroll** | Older lineage; not the first choice for a fresh 1.6 workflow | https://ludeon.com/forums/index.php?topic=18073.0 |

---

# 12. Important exclusions / false positives

To keep this useful, I intentionally did **not** count the following as handcrafted maps merely because they are visually striking:

- colonies whose buildings are exquisitely designed but terrain is a normal seed;
- Geological Landforms screenshots where the landform was generated and not manually altered;
- “best seed” posts;
- world-map/planet editors unless they also provide a local authored tile;
- generated dungeons with no authored template evidence;
- image posts where the author never says the terrain was custom;
- unrelated games returned by generic “custom map” web searches.

This is why the catalogue is smaller than a search for “beautiful RimWorld map,” but much more relevant to **actual map authoring**.

---

# 13. Source index / bibliography

## UnknwnBuilds / RimWorld Map Makers

- GitHub profile/repositories — https://github.com/UnknwnBuilds?tab=repositories
- GitHub repositories page 2 — https://github.com/UnknwnBuilds?page=2&tab=repositories
- Reddit profile — https://www.reddit.com/user/UnknwnBuilds/
- RimWorld Map Makers Discord announcement — https://www.reddit.com/user/UnknwnBuilds/comments/zlvbex/rimworld_map_makers_custom_rimworld_map_discord/
- User-supplied “Some more custom maps…” — https://www.reddit.com/r/RimWorld/comments/zda2hp/some_more_custom_maps_i_made_for_rrimworld_users/
- “few more custom maps” / #11–#14 — https://www.reddit.com/r/RimWorld/comments/1088yn0/ive_created_a_few_more_custom_maps_all_available/
- 500×500 Kingdom map — https://www.reddit.com/r/RimWorld/comments/11oxmo8/
- Ruined Dam — https://www.reddit.com/r/RimWorld/comments/15cstlq/
- Cathedral — https://www.reddit.com/r/RimWorld/comments/1dvziek/
- In Memory of Rain — https://www.reddit.com/r/RimWorld/comments/1ejwc3l/
- Cervantes Cliffs — https://www.reddit.com/r/RimWorld/comments/1esw15l/
- The Estuary — https://www.reddit.com/r/RimWorld/comments/1ilq74t/
- Darkrest — https://www.reddit.com/r/RimWorld/comments/1j7bytr/
- Lighthouse Blues — https://www.reddit.com/r/RimWorld/comments/1l05j3r/
- Ides Veil — https://www.reddit.com/r/RimWorld/comments/1p50ez0/
- the Dead City — https://www.reddit.com/r/RimWorld/comments/1pmpj3p/
- Dragons Fall — https://www.reddit.com/r/RimWorld/comments/1s046zo/

## Independent creators / examples

- Grapesforlifes GitHub — https://github.com/Grapesforlifes
- Malta study — https://www.reddit.com/r/RimWorld/comments/14jgc0k/
- Lone Mountain Bay — https://www.reddit.com/r/RimWorld/comments/14n4vbl/
- Lone Mountain Bay GitHub — https://github.com/Grapesforlifes/Lone_Mountain_Bay_RW
- Yirah Valley GitHub — https://github.com/Grapesforlifes/Yirah_Valley_RW
- Mousecliff — https://www.reddit.com/r/RimWorld/comments/1dkv93o/
- First Dev-Tool landscaped map (VenomSnake1974) — https://www.reddit.com/r/RimWorld/comments/1mtwq5y/
- 2026 custom ring/river map — https://www.reddit.com/r/RimWorld/comments/1vcpee8/
- Town by the River — https://www.reddit.com/r/RimWorld/comments/n1up12/
- Infestation / Fertile Valley map — https://www.reddit.com/r/RimWorld/comments/rk3zdi/
- 24-year mountain city / manually TerraForm-ed terrain — https://www.reddit.com/r/RimWorld/comments/1191me1/
- Estuary derivative — https://www.reddit.com/r/RimWorld/comments/1io9isn/

## Authored levels / challenge maps

- 2020 custom/adventure maps discussion — https://www.reddit.com/r/RimWorld/comments/htm6fn/
- Wailing Caverns recreation — https://www.reddit.com/r/RimWorld/comments/1buznzu/
- Dungeon Core overview — https://rimworldbase.com/dungeon-core-mod/
- RWCC return/overview — https://www.patreon.com/posts/rwcc-returns-105402513
- RWCC June 2024 — https://www.patreon.com/posts/rwcc-june-2024-105403109
- RWCC July 2024 custom map — https://www.patreon.com/posts/rwcc-july-2024-107847162

## Tools / historical lineage

- Map Designer — https://steamcommunity.com/sharedfiles/filedetails/?id=2111424996
- Map Preview — https://steamcommunity.com/sharedfiles/filedetails/?id=2800857642
- Map Edit Tools — https://steamcommunity.com/sharedfiles/filedetails/?id=3229348657
- Map Edit Tools GitHub — https://github.com/dougbenham/Rimworld-MapEditTools
- Save Maps (Continued) — https://steamcommunity.com/sharedfiles/filedetails/?id=2916523481
- Better Map Sizes — https://steamcommunity.com/sharedfiles/filedetails/?id=2099101052
- Geological Landforms — https://steamcommunity.com/sharedfiles/filedetails/?id=2773943594
- Steam 2020 map-editor discussion — https://steamcommunity.com/app/294100/discussions/0/2992043384045658790/
- Ludeon Map Reroll thread — https://ludeon.com/forums/index.php?topic=18073.0
- RimWorld Custom Maps utility — https://ludeon.com/forums/index.php?topic=50269.0
- RimWorldMaps GitHub — https://github.com/SickBoyWi/RimWorldMaps
- RimEdit historical thread — https://ludeon.com/forums/index.php?topic=1560.0
- Map Designer / Map Reroll tutorial — https://www.youtube.com/watch?v=DTydAEaiCWQ

---

# 14. Open archival leads — where more maps probably exist

These are **not claimed as additional verified map titles**; they are places where the remaining public-history gap is most likely to be closed.

1. **RimWorld Map Makers Discord `#World_Downloads`** — best lead for UnknwnBuilds Worlds 1–24 and commissions/request variants that never received GitHub repositories.
2. **Old Reddit posts deleted or poorly indexed by search engines** — especially late 2022 through May 2023, before World 25 began the current GitHub run.
3. **Save Maps blueprint sharing threads/Discords** — maps may circulate as files without ever receiving a Reddit showcase.
4. **Dungeon Core community maps** — the framework explicitly supports authored map additions, and current Workshop/local files may expose more template names than web summaries do.
5. **Streamer challenge-save communities** — scenario saves often contain hand-authored maps but are advertised by challenge premise rather than by the phrase “custom map,” making them difficult to discover via generic web search.

---

# 15. Bottom line

There is enough precedent to say confidently that **hand-authoring RimWorld maps is an established craft practice**, not an eccentric one-off. The best public corpus is UnknwnBuilds’ World series, but the most important idea is broader: creators are already treating RimWorld’s procedural terrain as a **blockout**, then using Dev Mode and editing/export tools to turn it into deliberately composed landscapes and levels.

For future reference, the most reusable conceptual formula from the sources is:

> **Generate the geology you do not care to paint → hand-sculpt the silhouette and hydrology → place one memorable landmark → add evidence of history → add an encounter or danger with positional intent → package the result as a save/blueprint.**

That is the point at which a RimWorld tile stops being “a good seed” and becomes a **designed place**.
