# Curatable Sources of Generated RimWorld Map Images

**Scan date:** 2026-08-05  
**Purpose:** A working catalog of internet sources containing actual RimWorld map images—both developed player colonies and relatively untouched/generated map tiles—that can be explored and potentially collected later.

> **Terminology used here**
>
> - **Player base:** A played, built, or decorated colony map, ideally rendered as most or all of the tile.
> - **Raw tile:** An unbuilt or minimally altered generated map showing terrain, mountains, rivers, roads, coastlines, caves, landforms, ruins, or biome structure.
> - **Curatable:** The source has stable post pages, direct media links, useful metadata, feeds/APIs, pagination, or enough organization to support deliberate collection.
> - **Downloadable does not mean reusable:** Preserve attribution and check the license or obtain creator permission before republication, dataset release, model training, or commercial use.

---

## Best starting points

| Priority | Source | Best for | Corpus quality | Collection friendliness |
|---:|---|---|---|---|
| 1 | [RimWorld Gallery — m/RimWorldPorn](https://rimworld.gallery/m/RimWorldPorn) | Full-map player-base renders | Excellent | Excellent: stable pages, direct originals, pagination, RSS |
| 2 | [r/RimWorldSeeds](https://www.reddit.com/r/RimWorldSeeds/) | Raw tiles with seeds and coordinates | Excellent | Very good: Reddit JSON, flair/title metadata |
| 3 | [RimWorld Wiki screenshot categories](https://rimworldwiki.com/wiki/Category:Images_-_Screenshots) | Structured raw-map and terrain examples | Very good | Very good: file pages, original files, categories |
| 4 | [Geological Landforms workshop gallery](https://steamcommunity.com/sharedfiles/filedetails/?id=2773943594) | Diverse mod-generated raw landforms | Excellent but finite | Good: direct Steam CDN images |
| 5 | [Steam Community screenshots](https://steamcommunity.com/app/294100/screenshots/) | Huge mixed stream of bases and maps | High volume, low precision | Moderate: pagination and direct CDN assets |
| 6 | [Imgur RimWorld tag](https://imgur.com/t/rimworld/top/all) | Historical albums, full colonies, seed maps | Rich but noisy | Good with API credentials; moderate manually |
| 7 | [r/RimWorld Colony Showcase](https://www.reddit.com/r/RimWorld/search/?q=flair%3A%22Colony%20Showcase%22&restrict_sr=1&sort=top&t=all) | Broad player-base corpus | Very good | Very good via Reddit JSON, but images vary in quality |

---

# A. Full-map player bases and colony renders

## 1. RimWorld Gallery — `m/RimWorldPorn`

- **Main gallery:** <https://rimworld.gallery/m/RimWorldPorn>
- **Photos only:** <https://rimworld.gallery/m/RimWorldPorn/combined?type=photos>
- **Newest:** <https://rimworld.gallery/m/rimworldporn/default/newest?type=photos>
- **Top:** <https://rimworld.gallery/m/RimWorldPorn/combined/top>
- **RSS feed:** <https://rimworld.gallery/rss?content=threads&magazine=RimWorldPorn>
- **Pagination pattern:** append `&p=2`, `&p=3`, and so forth to a filtered page.

### Why it is unusually valuable

This is the strongest single source for **large, whole-map colony renders**. The community rules favor images that show the entire map or most surrounding terrain rather than cropped rooms. Many submissions were made with a full-map renderer and expose an original media asset rather than only a compressed preview.

### Example

- [Aethelgard — 56 colonists, 620 days, custom 300×300 map](https://rimworld.gallery/m/RimWorldPorn/t/14348/Aethelgard-56-colonists-620-days-10-years-custom-300x300-map)

On an item page, look for the image link or **Open original URL**. Direct media commonly uses a stable host such as `media.rimworld.gallery`.

### Collection strategy

1. Read the RSS feed for new item URLs.
2. Crawl numbered gallery pages for historical items.
3. Record the item page, creator, title, date, description, and direct original-media URL.
4. Detect federated reposts or crossposts before treating an image as unique.

### Caveats

- Approximately 245 threads were visible at scan time; this will change.
- Creator descriptions vary in detail.
- Public visibility does not establish a license for reuse.

**Ratings:** Bases ★★★★★ · Raw tiles ★★☆☆☆ · Metadata ★★★★☆ · Automation ★★★★★

---

## 2. r/RimWorld — `Colony Showcase` flair

- **Filtered search:** <https://www.reddit.com/r/RimWorld/search/?q=flair%3A%22Colony%20Showcase%22&restrict_sr=1&sort=top&t=all>
- **Subreddit:** <https://www.reddit.com/r/RimWorld/>
- **JSON form of a listing:** add `.json` to compatible Reddit listing/search URLs.

### What it contains

A very large and continuing supply of player colonies: screenshots, stitched maps, Progress Renderer output, themed bases, mountain complexes, ships, cities, challenge colonies, and mod-heavy settlements.

### Collection strategy

- Query the exact flair and collect post metadata through Reddit’s supported API or JSON listings.
- Preserve galleries as galleries; one post may contain multiple stages or detail images.
- Search titles and text for `full map`, `colony showcase`, `base`, `settlement`, `city`, `progress renderer`, `year`, and `day`.

### Caveats

- Reddit-hosted previews may be resized or recompressed.
- Many posts emphasize aesthetics rather than reproducibility.
- Some images are partial views, UI screenshots, or composites rather than clean maps.

**Ratings:** Bases ★★★★★ · Raw tiles ★★☆☆☆ · Metadata ★★★★☆ · Automation ★★★★☆

---

## 3. r/RimWorldPorn on Reddit

- **Subreddit:** <https://www.reddit.com/r/RimWorldPorn/>

This is now principally useful as a **discovery and redirect layer** for the higher-resolution RimWorld Gallery community. It can still contain historic posts and links, but the Mbin-based gallery above is the better primary corpus.

**Ratings:** Bases ★★★★☆ · Raw tiles ★☆☆☆☆ · Metadata ★★★☆☆ · Automation ★★★☆☆

---

## 4. Steam Community — RimWorld screenshots

- **All screenshots:** <https://steamcommunity.com/app/294100/screenshots/>
- **Trending this year:** <https://steamcommunity.com/app/294100/screenshots/?browsefilter=trendyear&p=1>
- **Trending three months:** <https://steamcommunity.com/app/294100/screenshots/?browsefilter=trendthreemonths&p=1>
- **Pagination:** increment `p=1`, `p=2`, etc.

### What it contains

A massive mixed stream with many colonies, map views, raw terrain, mod demonstrations, world maps, UI screenshots, memes, combat scenes, and close-ups.

### Why it remains useful

Each screenshot page normally exposes an image hosted on Steam’s image CDN, often under `images.steamusercontent.com`, plus author and caption information. It is a high-volume source even though precision is much lower than RimWorld Gallery.

### Search and filtering ideas

Search or manually scan for:

- `full map`
- `colony`
- `base`
- `settlement`
- `city`
- `mountain base`
- `seed`
- `map`
- `landform`

### Caveats

- Expect substantial manual filtering or image classification.
- Steam pages and CDN URL forms can change.
- Review Steam’s terms and rate limits before bulk acquisition.

**Ratings:** Bases ★★★★☆ · Raw tiles ★★★☆☆ · Metadata ★★★☆☆ · Automation ★★★☆☆

---

## 5. Steam discussion threads devoted to bases

- [SHOW ME YOUR BASES](https://steamcommunity.com/app/294100/discussions/0/569247980380507245/)
- [Post image of your current Base](https://steamcommunity.com/app/294100/discussions/0/1640927348811674338/)

These threads are useful **lead generators**. They point to Steam screenshots, Imgur albums, and sometimes outside hosts. They are less suitable as a canonical corpus because links may disappear and comment structure is inconsistent.

**Ratings:** Bases ★★★☆☆ · Raw tiles ★☆☆☆☆ · Metadata ★★☆☆☆ · Automation ★★☆☆☆

---

## 6. Imgur — RimWorld tag and historical albums

- **Top RimWorld posts:** <https://imgur.com/t/rimworld/top/all>
- **Chronological/tag activity:** <https://imgur.com/t/rimworld/time>
- **Gallery API documentation:** <https://apidocs.imgur.com/>
- **Tag gallery endpoint pattern:** `https://api.imgur.com/3/gallery/t/rimworld/{sort}/{window}/{page}`

### Why it matters

Imgur holds a large historical archive of colony albums, progression series, base-design collections, and map-seed screenshots, particularly from years when Reddit and forums routinely used Imgur as the image host.

### Strong example albums

#### Player bases

- [Sakura no Machi — Asian-inspired RimWorld base](https://imgur.com/gallery/sakura-no-machi-asian-inspired-rimworld-base-9PCcP)
- [RimWorld Colony of 11 Years](https://imgur.com/gallery/rimworld-colony-of-11-years-pEO98)
- [RimWorld base designs I made and liked](https://imgur.com/gallery/rimworld-base-designs-i-made-n-liked-KgJmCta)

#### Seeds and raw maps

- [RimWorld Seed](https://imgur.com/gallery/rimworld-seed-F2StogS)
- [A16 defendable temperate-forest seed](https://imgur.com/gallery/rimworld-seed-a16-defend-temperate-forest-perfect-seed-ZfLLx)
- [Alpha 17 desert/mountains/river/highway seed](https://imgur.com/gallery/rimworld-alpha-17-3-seed-desert-mountains-river-highway-2ysRv)
- [Mountain-base seed](https://imgur.com/gallery/rimworld-seed-mountain-base-voe5X)

### Collection strategy

- Manual: inspect albums and use original-image links where available.
- Programmatic: use the official Imgur API with a registered client ID and observe API limits and terms.
- Store album order and captions; they frequently contain crucial version, seed, or design context.

### Caveats

- The `rimworld` tag includes fan art, memes, screenshots, and unrelated material.
- Old seed posts may no longer reproduce on current RimWorld versions.
- Some posts have weak or missing authorship metadata after reposting.

**Ratings:** Bases ★★★★☆ · Raw tiles ★★★☆☆ · Metadata ★★★☆☆ · Automation ★★★★☆

---

## 7. Lemmy.World — `c/rimworld`

- **Community:** <https://lemmy.world/c/rimworld>
- **Likely API listing pattern:** `https://lemmy.world/api/v3/post/list?community_name=rimworld&sort=TopAll&limit=50&page=1`

The federated community contains colony screenshots, full-map images, modded bases, and occasional raw maps. It can provide direct-media URLs and structured post metadata.

### Caveats

- Verify the API endpoint before building a collector; it was not fully validated during this scan.
- Federation can create duplicate records across Lemmy and Mbin communities.
- Smaller corpus than Reddit or Steam.

**Ratings:** Bases ★★★☆☆ · Raw tiles ★★☆☆☆ · Metadata ★★★☆☆ · Automation ★★★☆☆

---

## 8. r/RimWorldConsole — `Colony Showcase`

- **Filtered search:** <https://www.reddit.com/r/RimWorldConsole/search/?q=flair%3A%22Colony%20Showcase%22&restrict_sr=1&sort=top&t=all>

A useful niche corpus of console-built colonies. Images are often ordinary screen captures rather than full-map renderer exports, but they broaden the visual distribution and avoid a PC-only bias.

**Ratings:** Bases ★★★☆☆ · Raw tiles ★☆☆☆☆ · Metadata ★★★☆☆ · Automation ★★★★☆

---

# B. Raw, original, or minimally built generated tiles

## 9. r/RimWorldSeeds

- **Subreddit:** <https://www.reddit.com/r/RimWorldSeeds/>
- **Top of all time:** <https://www.reddit.com/r/RimWorldSeeds/top/?t=all>
- **JSON listing:** <https://www.reddit.com/r/RimWorldSeeds/top.json?t=all&limit=100>
- **Pagination:** use the returned `after` value in the next request.

### Why it is the best raw-map source

Posts commonly include:

- an unbuilt full-map screenshot;
- the world seed;
- map coordinates;
- biome or terrain flair;
- map size;
- world coverage;
- DLC or mod notes;
- occasionally the game version.

This is the best existing internet corpus for pairing a **map image with partial reproducibility metadata**.

### Example recent-style post

- [“Odyssey god tile” — 300×300 crater lake](https://www.reddit.com/r/RimWorldSeeds/comments/1sh844y/found_the_odyssey_god_tile_a_300x300_crater_lake/)

### Collection strategy

1. Pull listing metadata through Reddit’s supported API or JSON endpoint.
2. Retain post flair as a probable biome label.
3. Parse seed, coordinates, map size, coverage, version, DLC, and mods from title/body/comments.
4. Keep an explicit `reproducibility_confidence` field rather than assuming every seed will regenerate exactly.

### Reproducibility warning

A seed image is not enough by itself. RimWorld map output can depend on:

- exact game version;
- capitalization and spacing of the seed;
- map size;
- world coverage;
- latitude/longitude or tile location;
- DLC enabled;
- terrain, biome, world-generation, and map-generation mods;
- mod versions and load order.

**Ratings:** Bases ★☆☆☆☆ · Raw tiles ★★★★★ · Metadata ★★★★☆ · Automation ★★★★★

---

## 10. RimWorld Wiki — screenshot and map-feature categories

- **Screenshot category:** <https://rimworldwiki.com/wiki/Category:Images_-_Screenshots>
- **Map Features subcategory:** <https://rimworldwiki.com/wiki/Category:Images_-_Map_Features>
- **Biomes overview:** <https://rimworldwiki.com/wiki/Biomes>

### What it contains

The screenshot category contained **856 files at scan time**, with category pagination. It includes many clean, high-resolution examples of map topology and biome/landform combinations. Examples visible in the index included filenames such as:

- `Basin in boreal forest.jpg` — 6400×6400
- `Cavern in desert.jpg` — 3200×3200
- `Chasm in desert.jpg` — 3200×3200
- `Coastal island in arid shrubland.jpg` — 3200×3200

### Why it is valuable

- Files have individual description pages.
- **Original file** links support clean downloads.
- Categories and filenames provide more structured labels than most social-media sources.
- The Map Features category can sharply reduce irrelevant UI and gameplay screenshots.

### Collection strategy

Use category pagination and record:

- file page URL;
- original media URL;
- filename/title;
- pixel dimensions;
- description;
- categories;
- uploader/date;
- license or copyright statement shown on the file page.

A standard MediaWiki API may offer cleaner enumeration, but verify the wiki’s current API configuration and usage policy before scripting.

### Caveats

Licensing is **per file**. Some images may be publisher-owned or used under wiki-specific terms rather than openly licensed for arbitrary redistribution.

**Ratings:** Bases ★★☆☆☆ · Raw tiles ★★★★★ · Metadata ★★★★★ · Automation ★★★★☆

---

## 11. Geological Landforms — Steam Workshop gallery

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2773943594>

The mod page states that it includes **43 landforms** and provides an example of each in its image gallery. This makes it one of the densest curated sources of visually distinct generated map tiles: canyons, islands, basins, cliffs, coasts, valleys, craters, and other topologies.

### Why it is especially useful

- Compact and deliberately curated.
- Most images are map-scale rather than room-scale screenshots.
- Direct Steam CDN image assets are exposed from the workshop gallery.
- Excellent for designing or classifying tile-specific gameplay opportunities.

### Caveats

These are **mod-generated landforms**, not a representative sample of vanilla RimWorld maps. Keep a `generation_family=Geological Landforms` label.

**Ratings:** Bases ★☆☆☆☆ · Raw tiles ★★★★★ · Metadata ★★★★☆ · Automation ★★★☆☆

---

## 12. Map Preview — Steam Workshop

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2800857642>

Map Preview shows the map that will be generated on a selected world tile before settlement. Its workshop gallery contains raw examples, but its larger value is that it creates a practical workflow for generating a new image collection from selected tiles.

### Dataset-building use

- Choose world tiles systematically.
- Capture previews before any colony is created.
- Pair screenshots with world seed, coordinates, biome, hilliness, roads, rivers, DLC, and mod configuration.
- Use repeated runs to measure generation variability.

**Ratings:** Existing corpus ★★☆☆☆ · New raw-map generation ★★★★★

---

## 13. Map Designer — Steam Workshop

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2111424996>

The gallery contains examples of generated maps and the settings used to shape them. It is valuable for **parameterized custom-map imagery**, especially when the intended dataset should include extreme or designed terrain rather than only natural vanilla generation.

### Caveat

Label these as designed/custom maps; they should not be mixed silently with untouched random tiles.

**Ratings:** Bases ★☆☆☆☆ · Raw/custom tiles ★★★★☆ · Metadata ★★★★☆ · Automation ★★☆☆☆

---

## 14. Configurable Maps (Continued) — Steam Workshop

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2889137767>

Another source of custom-generated map examples and configuration screenshots. Useful for expanding variation in mountain, water, fertility, ruin, geyser, and terrain distributions.

**Ratings:** Bases ★☆☆☆☆ · Raw/custom tiles ★★★★☆ · Metadata ★★★☆☆ · Automation ★★☆☆☆

---

## 15. Biome Transitions — Steam Workshop

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2814391846>

This mod’s workshop gallery is useful for maps containing blended or adjacent biome regions rather than one homogeneous biome. It is a high-value source when the curation goal includes ecological gradients or unusual terrain combinations.

**Ratings:** Bases ★☆☆☆☆ · Raw/modded tiles ★★★★☆ · Metadata ★★★☆☆ · Automation ★★☆☆☆

---

## 16. Biomes! Islands — Steam Workshop

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2038001322>

The workshop gallery contains many island-map examples, and the mod description identifies multiple island types. It is a useful historic source for coastal and isolated-map topology even if the mod version is now old or incompatible with current RimWorld.

### Caveat

Treat the images as an archive of mod-generated island maps, not as evidence that the maps reproduce in the current game.

**Ratings:** Bases ★☆☆☆☆ · Raw/modded tiles ★★★★☆ · Metadata ★★★☆☆ · Automation ★★☆☆☆

---

## 17. Alpha Biomes — Steam Workshop

- **Workshop page:** <https://steamcommunity.com/sharedfiles/filedetails/?id=1841354677>

A large gallery of highly distinctive modded-biome maps. The images are useful for visual diversity, biome classification, environmental storytelling, and ideas for tile-specific resources or hazards.

**Ratings:** Bases ★★☆☆☆ · Raw/modded tiles ★★★★☆ · Metadata ★★★☆☆ · Automation ★★☆☆☆

---

# C. Historic and manual-discovery sources

## 18. Ludeon Studios forums

- [Screenshot/history thread](https://ludeon.com/forums/index.php?topic=48520.0)
- [Succession-game story thread](https://ludeon.com/forums/index.php?topic=37108.0)

The official forums contain older colony screenshots, storytelling maps, development-era images, and succession-game archives. These can reveal historical UI and map-generation styles no longer common in current screenshots.

### Limitations

- External image-host links may be dead.
- Attachments and forum markup vary.
- Metadata is narrative rather than standardized.

**Ratings:** Historic value ★★★★☆ · Harvestability ★★☆☆☆

---

## 19. Official RimWorld screenshots and SteamDB mirror

- **Official Steam store:** <https://store.steampowered.com/app/294100/RimWorld/>
- **SteamDB screenshots page:** <https://steamdb.info/app/294100/screenshots/>

These are a small, curated set of publisher-selected images. They are useful as a **reference corpus** for canonical visual presentation, but not as a broad source of organically generated full maps.

**Ratings:** Representativeness ★★☆☆☆ · Metadata ★★★★☆ · Reuse restrictions likely strong

---

## 20. RimWorld Discord

- **Invite:** <https://discord.com/invite/rimworld>

The community includes channels where players share colonies and screenshots. It can be rich for manual discovery and contacting creators, but it is poor for automated curation:

- authentication required;
- message and attachment URLs may not be stable archival identifiers;
- Discord’s terms and community expectations matter;
- creators may not expect bulk collection.

Use this principally to **request submissions or permissions**, not as a scraping target.

**Ratings:** Discovery ★★★★☆ · Harvestability ★☆☆☆☆

---

# D. Tools for deliberately generating new map-image corpora

These are not primarily internet image archives. They are useful for producing a cleaner and better-documented corpus than social-media harvesting alone.

## 21. Progress Renderer

- **Current Steam fork:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2010777010>
- **Older/original workshop entry:** <https://steamcommunity.com/sharedfiles/filedetails/?id=1438693028>
- **GitHub source:** <https://github.com/JonathanTroyer/Progress-Renderer>

Generates large renders of the full map or a selected area, manually or on a schedule. It is the best route for asking players to contribute standardized full-colony images.

### Suggested contribution protocol

Request:

- one full-map render;
- one screenshot with UI/version/mod-list context;
- colony age and population;
- map size;
- seed and tile coordinates when available;
- DLC and mod-list export;
- explicit reuse license or permission statement.

---

## 22. SeedFinder

- **Steam Workshop:** <https://steamcommunity.com/sharedfiles/filedetails/?id=2839151249>
- **Reddit release/discussion:** <https://www.reddit.com/r/RimWorldSeeds/comments/w6a3ej>

SeedFinder can search generated worlds and write full-map screenshots whose filenames include seed and coordinates. This is particularly valuable for building a reproducible raw-map dataset rather than relying on incomplete human-entered metadata.

### Best use

Define a sampling plan across:

- biome;
- hilliness;
- coast/river/road combinations;
- temperature and rainfall;
- latitude bands;
- landform mods;
- map sizes;
- DLC/mod configurations.

---

## 23. RimworldRender

- **GitHub:** <https://github.com/Epicguru/RimworldRender>

A tool oriented toward rendering RimWorld progress or video sequences. It can help turn periodically captured maps into consistent timelapse frames and a colony-development dataset.

---

# E. Suggested acquisition and curation schema

A collector should keep the social post and the media asset as separate records. A minimal image record might look like this:

```yaml
record_id: stable-local-id
source_name: rimworld_gallery | reddit | steam | imgur | wiki | lemmy | contributed
source_page_url: https://...
media_url: https://...
retrieved_at: 2026-08-05T00:00:00Z
creator_display_name: null
creator_profile_url: null
post_title: null
post_date: null

image_kind: player_base | raw_tile | map_preview | world_map | progress_frame | mixed
built_state: raw | minimally_altered | developed | unknown
full_map: true | false | unknown
ui_visible: true | false | unknown
pixel_width: null
pixel_height: null
file_format: png | jpg | webp | unknown
file_size_bytes: null
sha256: null
perceptual_hash: null

rimworld_version: null
dlc: []
mods: []
mod_collection_url: null
seed: null
seed_case_preserved: true
world_coverage_percent: null
map_size: null
latitude: null
longitude: null
tile_id: null
biome: null
hilliness: null
landform: null
roads: []
rivers: []
coastal: null

colony_name: null
colony_age_days: null
colonist_count: null
storyteller: null
difficulty: null

license_text: null
permission_status: unknown | permitted | restricted | pending
attribution_text: null
notes: null
```

## Recommended controlled vocabulary for `image_kind`

- `player_base_full_map`
- `player_base_partial`
- `raw_tile_full_map`
- `raw_tile_partial`
- `map_preview`
- `seed_documentation`
- `mod_landform_example`
- `biome_example`
- `world_map`
- `progress_render_frame`
- `diagram_or_design` — usually exclude from an actual-map corpus
- `non_map_screenshot` — exclusion label

---

# F. Practical deduplication

Crossposting is common across Reddit, Imgur, Steam, Lemmy, Mbin, and Discord. Use multiple layers:

1. **Exact file hash** — catches byte-identical copies.
2. **Perceptual hash** — catches resized, recompressed, and lightly cropped copies.
3. **Aspect ratio and dimensions** — inexpensive prefilter.
4. **Canonical source URL matching** — captures crossposts that retain the original URL.
5. **Image embedding or feature similarity** — useful for crops, annotations, and UI overlays.
6. **Human review** — distinguish the same colony at different dates from true duplicates.

Keep related images as a **colony series** rather than discarding every near-duplicate. Progression is often the scientifically interesting dimension.

---

# G. Reproducibility tiers for raw tiles

| Tier | Required metadata | Interpretation |
|---|---|---|
| A | Version, exact seed, coverage, map size, exact coordinates/tile, DLC, full mod list and versions | Strong attempt at exact regeneration |
| B | Version, seed, map size, coordinates, DLC; mods partly known | Likely reproducible with investigation |
| C | Seed and approximate location/biome only | Visual reference, weak reproducibility |
| D | Image only | Appearance corpus only |

Do not describe a map as reproducible solely because a seed is present.

---

# H. Rights, attribution, and ethical collection

Before downloading at scale or redistributing anything:

- Read each platform’s terms, API rules, robots directives, and rate limits.
- Record creator identity and canonical post URL at acquisition time.
- Preserve all captions and license statements.
- Do not infer an open license from public access or a visible download control.
- Ask creators for permission when publishing a collection, training a model, or redistributing original-resolution images.
- Provide an opt-out and correction route in any public dataset.
- Avoid Discord bulk scraping; solicit voluntary submissions instead.
- Treat wiki files individually because licenses and ownership notices can differ.
- Consider storing only metadata, thumbnails, hashes, and source links until reuse permission is resolved.

---

# I. Weak or inefficient sources

These can occasionally surface useful images but should not anchor the collection.

| Source type | Problem |
|---|---|
| Generic Google/Bing image search | Duplicate-heavy, incomplete attribution, transient result URLs |
| Pinterest | Extensive reposting and attribution loss; originals often elsewhere |
| YouTube screenshots | Low map resolution, video copyright, weak seed/mod metadata |
| TikTok/short-form video | Poor archival stability and difficult original-frame extraction |
| Discord scraping | Authentication, unstable context, consent and platform-policy concerns |
| Random blogs | Small volume, external-host link rot, inconsistent metadata |
| AI-generated RimWorld-like art | Not an actual generated game map; exclude explicitly |

---

# J. Recommended first-pass collection plan

## Pass 1 — High precision

1. Harvest RimWorld Gallery metadata and original-media URLs.
2. Harvest `r/RimWorldSeeds` posts and extract reproducibility fields.
3. Enumerate RimWorld Wiki Map Features and selected screenshot files.
4. Capture workshop galleries for Geological Landforms and major biome/map-generation mods.

## Pass 2 — High recall

5. Collect r/RimWorld `Colony Showcase` posts.
6. Scan Steam Community screenshots with map-related keywords and image filtering.
7. Query the Imgur `rimworld` tag and retain albums with full maps or seeds.

## Pass 3 — Historic and contributed material

8. Resolve old Ludeon forum links and Imgur albums.
9. Invite creators to submit standardized Progress Renderer exports.
10. Use SeedFinder and Map Preview to fill biome/landform gaps systematically.

## Quality-control target

Maintain separate datasets or labels for:

- vanilla raw maps;
- DLC-dependent raw maps;
- mod-generated raw maps;
- developed player colonies;
- designed or manually configured maps;
- historical game versions.

Mixing these without labels would make the resulting corpus visually rich but analytically unreliable.

---

# K. Compact URL inventory

```text
https://rimworld.gallery/m/RimWorldPorn
https://rimworld.gallery/m/RimWorldPorn/combined?type=photos
https://rimworld.gallery/rss?content=threads&magazine=RimWorldPorn

https://www.reddit.com/r/RimWorldSeeds/
https://www.reddit.com/r/RimWorldSeeds/top/?t=all
https://www.reddit.com/r/RimWorldSeeds/top.json?t=all&limit=100
https://www.reddit.com/r/RimWorld/search/?q=flair%3A%22Colony%20Showcase%22&restrict_sr=1&sort=top&t=all
https://www.reddit.com/r/RimWorldPorn/
https://www.reddit.com/r/RimWorldConsole/search/?q=flair%3A%22Colony%20Showcase%22&restrict_sr=1&sort=top&t=all

https://steamcommunity.com/app/294100/screenshots/
https://steamcommunity.com/app/294100/screenshots/?browsefilter=trendyear&p=1
https://steamcommunity.com/sharedfiles/filedetails/?id=2773943594
https://steamcommunity.com/sharedfiles/filedetails/?id=2800857642
https://steamcommunity.com/sharedfiles/filedetails/?id=2111424996
https://steamcommunity.com/sharedfiles/filedetails/?id=2889137767
https://steamcommunity.com/sharedfiles/filedetails/?id=2814391846
https://steamcommunity.com/sharedfiles/filedetails/?id=2038001322
https://steamcommunity.com/sharedfiles/filedetails/?id=1841354677
https://steamcommunity.com/sharedfiles/filedetails/?id=2010777010
https://steamcommunity.com/sharedfiles/filedetails/?id=2839151249

https://imgur.com/t/rimworld/top/all
https://imgur.com/t/rimworld/time
https://apidocs.imgur.com/

https://rimworldwiki.com/wiki/Category:Images_-_Screenshots
https://rimworldwiki.com/wiki/Category:Images_-_Map_Features
https://rimworldwiki.com/wiki/Biomes

https://lemmy.world/c/rimworld
https://ludeon.com/forums/index.php?topic=48520.0
https://discord.com/invite/rimworld

https://github.com/JonathanTroyer/Progress-Renderer
https://github.com/Epicguru/RimworldRender
```
