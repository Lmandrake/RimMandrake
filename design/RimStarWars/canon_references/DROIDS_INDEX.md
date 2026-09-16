<!-- QA
2026-09-15 QA pass (post-build watchdog kill). Rows before: 1766 (python/awk count of
table-shaped lines under the header separator). Rows after: 1757.
Removed/changed, by category:
  - Junk rows (category/disambig/file/template/redirect pages, individual characters
    mistaken for models): 0 found. Names and source URLs were already scoped to real
    droid-model articles; no non-droid pages detected.
  - Rows with no source URL: 0 found. Every row already carried a `[wiki](...)` link.
  - Invented-looking fields: 1 fixed. `Overseer droid (Death Star)`'s era field held
    "retired Galactic Republic" — a faction name, not a date, and a duplicate of the
    owners field next to it — blanked as unparseable/likely-mismapped rather than kept
    as a plausible-looking date. `DX-5 Incinerator Droid`'s class/role field carried
    leaked wikitext (`Battle droid\|degree=`) — stripped to `Battle droid`. No pattern
    of a manufacturer or era repeated across unrelated droids was found; manufacturer
    and era distributions look organically sourced (dominated by real canon droid
    manufacturers; era filled on only ~2% of rows, consistent with the file's own
    claim that Wookieepedia's droid infobox rarely carries a date).
  - Duplicates: 9 rows removed. All were the same droid under a case/hyphen spelling
    variant (e.g. "MSE series" vs "MSE-series", "Loader Droid" vs "Loader droid") where
    one row was a strict subset of the other's data (no conflicting named owner) — kept
    the better-sourced row each time. Left alone on purpose: near-identical names that
    disagreed on a *specific named owner* (e.g. the three "Hunter(-/ )killer droid"
    rows, "Turret droid" vs "Turret-droid", "Droid guard" vs "Guard droid") — these
    read as distinct real articles about different models sharing a generic name, not
    scrape duplicates, and merging them would have discarded real sourced facts on a
    guess. Also left alone: "ASP-19 Battle Droid" vs "ASP-19 battle droid/Legends" — an
    explicit canon/Legends continuity fork, not a spelling duplicate.
  - Table integrity: 1 broken row fixed (the DX-5 leaked-wikitext row above, which had
    10 pipes instead of 9). All 1757 rows now have exactly 9 pipes / 8 columns.
Worst systematic problem: none rising to "systematic" — the build was clean. The two
field-correctness fixes were isolated scrape/template artifacts, not a repeated pattern.
The dominant issue was spelling/case duplication from Wookieepedia's own inconsistent
page-title casing, not fabrication.
Coverage counts in the "Coverage" section below were recomputed from the table after
these fixes (python column-count over the corrected file), not carried over from the
pre-QA figures.
-->

# Star Wars droids — canon INDEX

_Breadth index of droid **types** (models, series, classes, lines) — not individual droids._
Built 2026-09-15 from the Wookieepedia MediaWiki API (`starwars.fandom.com/api.php`)
via Fetcher. Article HTML is Cloudflare-walled; the API is not.

## How to read this

- **Every row carries a source URL.** Nothing here is inferred from a search snippet.
- **Blank means unknown, never "none".** Fields come from the page's own
  `{{DroidSeries}}` infobox (`manufacturer`, `class`, `degree`, `firstmade`,
  `retired`, `affiliation`) or, where the infobox was not retrieved, from the
  page's own Wookieepedia categories (`Category:<X> products` → manufacturer,
  `Category:Droid models of the <Y>` → owners, `Category:<Z> droid models` → role).
  Nothing in this table was guessed.
- **`era` is the infobox `firstmade` / `retired` date, not a saga era.** 🔴 Measured:
  Wookieepedia's droid infobox has **no era field**, and modern articles carry **no
  era icons** — across 2,036 retrieved article wikitexts, 0 `{{Top}}` era parameters
  were found (only continuity/quality flags: `leg`, `ca`, `ga`, `fa`). So for most
  droids the honest era answer is blank, and the **`typical owners` column is the
  best available time-period proxy** (Trade Federation ⇒ fall of the Republic,
  Sith Empire ⇒ Old Republic, First Order ⇒ sequel era, and so on). Deriving an era
  from an affiliation is left to the reader on purpose — it is not written here as fact.
- **`continuity`** — `canon`, `canon (+Legends)`, or `Legends` (a Legends-only droid).
  Where a field was blank in canon and present in Legends it is marked `*(Legends)*`.
- **`in repo?`** names the chassis this repo already ships art for, from
  `src/RimStarWars/Droidworks/Textures/{JDS,KotOR,OuterRim}` and
  `design/Jawa/fauna/sprites/`. A named chassis means *that chassis* is present —
  not necessarily this exact variant.

## 🔴 Repo-versus-canon conflicts found

- **`design/Jawa/worldbuilding/droid_taxonomy.md` organises droids by SOURCE MOD**
  (KotOR rogue droids / JDS Separatists / Outer Rim Depot) — a mod-provenance
  taxonomy, not a canon one. Canon organises droids two ways at once: by
  **degree** (first through fifth) and by **function class** (astromech, protocol,
  battle, probe, labor…). Neither canon axis appears in the repo's taxonomy, and
  the repo's three families cut across both. The two are not interchangeable.
- **`design/Jawa/reconciled_lore/08_droids.md` counts "85 kinds" of droid** to be
  ported to Droidworks. This index enumerates over a thousand canon droid types,
  so the repo ships well under 10% of canon breadth — the gap is the opportunity
  the owner is asking about, not an error.
- **The repo's four-tier format model** (blank / mindless / programmable / sapient)
  and its **five states** are original design vocabulary. They are not Wookieepedia
  terms and no canon page in this index uses them. Canon's own vocabulary here is
  `degree` (class one … class five). Do not conflate the two.

## Coverage

- **1757 droid types** indexed (post-QA 2026-09-15; see `<!-- QA -->` note below).
- Most have their infobox parsed from retrieved wikitext; a small remainder are
  category-derived (name + URL + whatever the categories carry). The exact
  infobox-vs-category split from the original build is not recoverable from the
  table alone, so it is not restated here rather than guessed at.
- 54 rows match a chassis this repo already ships.
- 693 have a manufacturer; 890 have owners; 1577 have a class/role; 48 have a firstmade/retired date
  (era-fill pass, 2026-09-15 — see below).

### Era-fill pass, 2026-09-15

The owner asked for `era` explicitly, so it got a dedicated pass rather than a re-run of
the original build: a script re-fetched all 1757 pages' live wikitext from the same
MediaWiki API (`action=parse&prop=wikitext`), parsed the `{{DroidSeries}}` infobox's
`firstmade`/`retired` fields (falling back to `{{Droid}}`'s `birth`/`death` for the small
number of rows that are individual named droids, not series/models), and cross-checked
old-style `{{Top}}` era icons (found none — 0 hits across all 1757 pages, consistent with
the original build's measurement of 0 across 2,036 wikitexts). Result: **1710 of 1757
rows (97.3%) have no era in Wookieepedia's own infobox** — confirmed blank, not
unretrieved. Only 9 rows gained an era that the original build had missed; the other 39
already-filled rows were re-derived identically (0 conflicts against the prior build).
One row (`Overseer droid (Death Star)`) had a live `retired=[[Galactic Republic]]` value —
a faction name in a date field, on the wiki's own page, not a scrape error — rejected and
left blank rather than recorded as a plausible-looking but wrong date, per the same rule
that fixed this exact row in the 2026-09-15 QA pass above.

## Index

| name | class/role | manufacturer | era (firstmade/retired) | typical owners | continuity | in repo? | source URL |
|---|---|---|---|---|---|---|---|
| "Hatchling" maintenance droid | Maintenance droid | Roche Hive Mechanical Apparatus Design and Construction Activity for Those Who Need the Hive's Machines |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/%22Hatchling%22_maintenance_droid) |
| 0-LT utility droid | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/0-LT_utility_droid) |
| 1-1A medical droid | Medical droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/1-1A_medical_droid) |
| 11-17-series mining droid | Mining droid / Class five | Roche/Slayn & Korpil |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/11-17-series_mining_droid) |
| 11-3K viper probe droid | Probe droid | Arakyd Industries |  | Galactic Empire; Unbroken Clan; Scourge | canon |  | [wiki](https://starwars.fandom.com/wiki/11-3K_viper_probe_droid) |
| 11-4D's model | Class one Medical droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/11-4D%27s_model) |
| 11-88 factory droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/11-88_factory_droid) |
| 12-4C-41/b | Labor droid | SoroSuub Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/12-4C-41/b) |
| 1M-G Battle Droid | Battle |  |  | Ghost Squad | canon |  | [wiki](https://starwars.fandom.com/wiki/1M-G_Battle_Droid) |
| 2-0A medical droid | Medical droid / Class one droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2-0A_medical_droid) |
| 2-1 BXS combat-trauma surgical droid | Medical |  |  | Galactic Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/2-1_BXS_combat-trauma_surgical_droid) |
| 2-1B surgical droid | Medical droid / Class one droid | Industrial Automaton |  | Galactic Republic; Royal House of Naboo; Ajax Sigma's army; Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/2-1B_surgical_droid) |
| 2-1B technical droid | Technical droid | Geentech (development); Industrial Automaton (production) |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/2-1B_technical_droid) |
| 2-1C medical droid | Medical droid | Medtech Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/2-1C_medical_droid) |
| 2-ZH surgical droid | Medical droid / Class one droid | Industrial Automaton |  | Galactic Empire; Moruth Doole | canon |  | [wiki](https://starwars.fandom.com/wiki/2-ZH_surgical_droid) |
| 21D2-AN excavation droid | Excavation droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/21D2-AN_excavation_droid) |
| 250 Hover-Cam | Cam | Data-Link Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/250_Hover-Cam) |
| 2AS2 sound reproduction droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2AS2_sound_reproduction_droid) |
| 2BB | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2BB) |
| 2JTJ personal navigation droid | Service droid | Genetech Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2JTJ_personal_navigation_droid) |
| 2PO-series protocol droid | Protocol droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2PO-series_protocol_droid) |
| 2R-series medical droid | Medical droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2R-series_medical_droid) |
| 2V9 cargo lifter droid | Loader | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/2V9_cargo_lifter_droid) |
| 301-MAX Nightlight | Security droid | Kalibac Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/301-MAX_Nightlight) |
| 3C-series utility droid | Maintenance droid / Class 2 | Duwani Mechanical Products |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/3C-series_utility_droid) |
| 3D-4 administrative droid | Class three droid | Genetech Corporation | Prior to 26 ABY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/3D-4_administrative_droid) |
| 3D-4X administrative droid | Class three droid | Genetech Corporation | Prior to 22 BBY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/3D-4X_administrative_droid) |
| 3DO protocol/service droid | Protocol droid/Service droid | Duwani Mechanical Products |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/3DO_protocol/service_droid) |
| 3DVO cam droid | Class five droid | Loronar Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/3DVO_cam_droid) |
| 3PO-series protocol droid | Protocol droid / Class three | Cybot Galactica |  | Confederacy of Independent Systems (briefly, unwillingly); Royal House of Naboo; Galactic Republic; House of Organa | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/3PO-series_protocol_droid) |
| 3PX-series protocol droid | Protocol droid / Class three droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/3PX-series_protocol_droid) |
| 3Z3 medical droid | Medical droid / Class one droid | Industrial Automaton |  | Darth Krayt's Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/3Z3_medical_droid) |
| 434 unit | Kitchen droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/434_unit) |
| 434-FPC Personal Chef Droid | Class three droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/434-FPC_Personal_Chef_Droid) |
| 44-CRB crab droid |  |  |  | Pyke Syndicate | canon |  | [wiki](https://starwars.fandom.com/wiki/44-CRB_crab_droid) |
| 47-B-series droid | Repair droid | Loratus Manufacturing |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/47-B-series_droid) |
| 4C observation droid | Observation droid |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/4C_observation_droid) |
| 4XB Programmer Droid | Class two | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/4XB_Programmer_Droid) |
| 4XB programming droid | Programmer droid / Class 2 |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/4XB_programming_droid) |
| 5-BT Threat Analysis Droid | Security | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/5-BT_Threat_Analysis_Droid) |
| 5DS Ebranite Relations Droid | Protocol droid | Cybot Galactica |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/5DS_Ebranite_Relations_Droid) |
| 5M-Sec Droid | Security droid / Class three droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/5M-Sec_Droid) |
| 5YQ-series protocol droid | Protocol droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/5YQ-series_protocol_droid) |
| 79 Human-Cyborg Relations Droid | Protocol | Duorq |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/79_Human-Cyborg_Relations_Droid) |
| 850.AA Public Service Headquarters | Maintenance droid / Class five droid | Publictechnic |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/850.AA_Public_Service_Headquarters) |
| 8D smelter droid | Smelter droid / Class five droid | Roche Hive Mechanical Apparatus Design and Construction Activity for Those Who Need the Hive's Machines |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/8D_smelter_droid) |
| 8D-series smelter droid | Smelter droid | Roche Hive Mechanical Apparatus Design and Construction Activity for Those Who Need the Hive's Machines |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/8D-series_smelter_droid) |
| 9D9-s54 Dianoga spy droid | Spy droid | Imperial Department of Military Research |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/9D9-s54_Dianoga_spy_droid) |
| 9G Explorer Droid | Exploration | DeepSpace |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/9G_Explorer_Droid) |
| 9PO-series protocol droid | Protocol | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/9PO-series_protocol_droid) |
| A-1DA protocol droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/A-1DA_protocol_droid) |
| A-DSD advanced dwarf spider droid | Walker | Commerce Guild Manufacturers |  | Confederacy of Independent Systems; Commerce Guild | canon |  | [wiki](https://starwars.fandom.com/wiki/A-DSD_advanced_dwarf_spider_droid) |
| A-LT Utility Droid | Astromech droid |  |  | Crimson Dawn; Mercenaries (modified "Turret Slicer"); Galactic Empire (modified "Turret Slicer"); Alliance to Restore the Republi… | canon |  | [wiki](https://starwars.fandom.com/wiki/A-LT_Utility_Droid) |
| A-series assassin droid | Assassin/battle droid / Class four droid | Pollux Poi |  | Shell Hutts; Gree; Confederacy of Independent Systems; Nimbus commandos | canon |  | [wiki](https://starwars.fandom.com/wiki/A-series_assassin_droid) |
| A-type |  |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/A-type) |
| A1-R0 Weather Monitor Probe | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/A1-R0_Weather_Monitor_Probe) |
| A3 (droid model) |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/A3_%28droid_model%29) |
| A3L-N sentinel droid | Security droid |  |  | Crimson Dawn | canon |  | [wiki](https://starwars.fandom.com/wiki/A3L-N_sentinel_droid) |
| A4 laboratory assistant droid | Medical droid / Class one droid | MerenData |  | Confederacy of Independent Systems | Legends |  | [wiki](https://starwars.fandom.com/wiki/A4_laboratory_assistant_droid/Legends) |
| A5-series Assassin Droid | Assassin droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/A5-series_Assassin_Droid) |
| A7 Surveillance Drone | Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/A7_Surveillance_Drone) |
| A9G-series Data Storage Unit | Data storage unit / Class one droid | Industrial Automaton |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/A9G-series_Data_Storage_Unit) |
| AAD-4 assault droid | Assault droid / Class four droid | Arakyd Industries |  | Arakyd Industries | canon |  | [wiki](https://starwars.fandom.com/wiki/AAD-4_assault_droid) |
| AAT Driver Battle Droid | Battle droid / Fourth-degree droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/AAT_Driver_Battle_Droid) |
| AC series pilot droid | Pilot droid | Star Tours |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AC_series_pilot_droid) |
| AC1 surveillance droid | Security droid / Class five droid | Cybot Galactica |  | Galactic Empire; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/AC1_surveillance_droid) |
| AC1-series surveillance droid | Probe | Cybot Galactica |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/AC1-series_surveillance_droid) |
| ACC-7 assassin droid | Assassin droid / Class four droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ACC-7_assassin_droid) |
| Acrobat droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Acrobat_droid) |
| AD-4 Battledroid Centurion | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AD-4_Battledroid_Centurion) |
| AD-series weapons maintenance droid | Armorer droid / Class two droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/AD-series_weapons_maintenance_droid) |
| ADK-25-MED medical droid | Medical droid / Class one droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/ADK-25-MED_medical_droid) |
| Administrative droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Administrative_droid) |
| Adminmech droid | Class two |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Adminmech_droid) |
| Advertising droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Advertising_droid) |
| Aegis Mk IV | Battle droid / Class four droid | Holowan Laboratories |  | Holowan Laboratories | canon |  | [wiki](https://starwars.fandom.com/wiki/Aegis_Mk_IV) |
| Aegis-7 battle droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Aegis-7_battle_droid) |
| AG droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AG_droid) |
| Aggressor-series battle droid | Battle droid / Class four droid | Farrfin Droidworks |  | Darth Krayt's Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Aggressor-series_battle_droid) |
| Agonizer-6 nerve disruptor | Interrogation droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Agonizer-6_nerve_disruptor) |
| Agrirobot | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Agrirobot) |
| Agromech droid | Astromech |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Agromech_droid) |
| AL-5 Assault Droid | Battle droid |  |  | Order of Revan | canon |  | [wiki](https://starwars.fandom.com/wiki/AL-5_Assault_Droid) |
| Alien droid |  | Googly-eyed species |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Alien_droid) |
| All Terrain Patrol Droid | Droid walker |  |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/All_Terrain_Patrol_Droid) |
| All-Terrain Exploration Droid | Explorer droid / Class two droid | Cybot Galactica; Kuat Drive Yards |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/All-Terrain_Exploration_Droid) |
| AM-Mk II | Construction droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AM-Mk_II) |
| AMP Walker | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AMP_Walker) |
| Ampdroid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ampdroid) |
| Amplifier droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Amplifier_droid) |
| Analysis droid | Class one |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Analysis_droid) |
| Annihilator droid | Battle |  |  | Nawaam's army | canon |  | [wiki](https://starwars.fandom.com/wiki/Annihilator_droid) |
| ANT-621 droid | Construction droid | Industrial Automaton |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/ANT-621_droid) |
| Anti-Air Super Battle Droid | Battle droid / Class 4 |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Anti-Air_Super_Battle_Droid) |
| Anti-Intrusion droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Anti-Intrusion_droid) |
| AP-1-C attack droid | Battle droid / Class four droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/AP-1-C_attack_droid) |
| AP-2 attack droid | Battle droid / Class four droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/AP-2_attack_droid) |
| AP-3 attack droid | Battle droid / Class four droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/AP-3_attack_droid) |
| APA-5 droid | Labor droid |  |  | New Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/APA-5_droid) |
| APD-40 | Protocol droid / Class three droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/APD-40) |
| AQ-series battle droid | Battle droid; Droid tank | Haor Chall Engineering Corporation |  | Confederacy of Independent Systems | canon | AQ battle droid (JDS) | [wiki](https://starwars.fandom.com/wiki/AQ-series_battle_droid) |
| Aqua droid | Battle droid / Class four droid |  |  | Confederacy of Independent Systems | Legends |  | [wiki](https://starwars.fandom.com/wiki/Aqua_droid/Legends) |
| Aquatic battle droid | Battle droid |  |  | Jedi Order (secretly) | canon |  | [wiki](https://starwars.fandom.com/wiki/Aquatic_battle_droid) |
| AQX aquatic explorer droid | Exploration; Submersible |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AQX_aquatic_explorer_droid) |
| AR-2B Utility Droid | Class five droid | Karflo Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AR-2B_Utility_Droid) |
| AR-34 enforcer droid | Security droid / Class four droid | Hutt Cartel |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/AR-34_enforcer_droid) |
| Arachnodroid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Arachnodroid) |
| Arak-series probe droid | Probe droid / Class four droid |  |  | Galactic Empire; Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Arak-series_probe_droid) |
| Arakyd Probot Series | Probe | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Arakyd_Probot_Series) |
| Architect droid | Class three |  |  | Jedi Order; Galactic Republic; New Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Architect_droid) |
| Arena Droid | Class four; Training |  |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Arena_Droid) |
| Armor Droid | Battle droid |  |  | Ugnaughts | canon |  | [wiki](https://starwars.fandom.com/wiki/Armor_Droid) |
| Armorer droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Armorer_droid) |
| Aro-GX Security Droid | Security droid / Class four droid | Aro |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Aro-GX_Security_Droid) |
| Articulated holographic color separator | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Articulated_holographic_color_separator) |
| Artillery Droid AR-19 | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Artillery_Droid_AR-19) |
| AS-M12-series droid | Messenger droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/AS-M12-series_droid) |
| ASN courier droid | Courier droid / Class 3 |  |  | Zam Wesell; Galactic Empire; Crimson Dawn | canon |  | [wiki](https://starwars.fandom.com/wiki/ASN_courier_droid) |
| ASP-19 Battle Droid | Labor droid | Industrial Automaton |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/ASP-19_Battle_Droid) |
| ASP-19 battle droid | Training |  |  | Galactic Empire | Legends |  | [wiki](https://starwars.fandom.com/wiki/ASP-19_battle_droid/Legends) |
| ASP-19, Lightsaber Training Configuration, Mark IX | Training | Industrial Automaton |  | Order of the Sith Lords | canon |  | [wiki](https://starwars.fandom.com/wiki/ASP-19%2C_Lightsaber_Training_Configuration%2C_Mark_IX) |
| ASP-2 | Labor droid / Class 5 | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ASP-2) |
| ASP-38 Droid | Security |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ASP-38_Droid) |
| ASP-4 hunter droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ASP-4_hunter_droid) |
| ASP-6 Training Droid | Training |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ASP-6_Training_Droid) |
| ASP-7 labor droid | Labor droid / Class five droid | Industrial Automaton |  | Galactic Empire; Visler Korda's faction | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/ASP-7_labor_droid) |
| ASP-series labor droid | Labor droid / Class five droid | Industrial Automaton |  | Galactic Republic; Confederacy of Independent Systems; Galactic Empire; Second Revelation | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/ASP-series_labor_droid) |
| Assassin droid | Class four |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Assassin_droid) |
| Assassin probe | Assassin droid / Class four droid |  |  | Death Watch; Confederacy of Independent Systems | Legends |  | [wiki](https://starwars.fandom.com/wiki/Assassin_probe/Legends) |
| Assassination Unit Mark IV | Assassin droid | Czerka Corporation |  | Czerka Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Assassination_Unit_Mark_IV) |
| Assassination Unit Mark X | Assassin droid | Czerka Corporation |  | Czerka Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Assassination_Unit_Mark_X) |
| Assault battle droid | Battle droid / Class four droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems; Separatist holdouts; X1's faction | canon |  | [wiki](https://starwars.fandom.com/wiki/Assault_battle_droid) |
| Assault Unit AZ-B | Battle droid |  |  | Arlaia Zayzen | canon |  | [wiki](https://starwars.fandom.com/wiki/Assault_Unit_AZ-B) |
| Assembly Defender Droid AR-18 | Security droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Assembly_Defender_Droid_AR-18) |
| Assembly Droid FA-19 | Maintenance droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Assembly_Droid_FA-19) |
| Assembly Watcher WX | Security droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Assembly_Watcher_WX) |
| Astrobot |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Astrobot) |
| Astromech droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Astromech_droid) |
| Astronavigation droid | Class two | Golden Nyss Shipyards |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Astronavigation_droid) |
| Attack droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Attack_droid) |
| Attuma Duum's security droid | Security droid / Class four droid |  |  | Attuma Duum | canon |  | [wiki](https://starwars.fandom.com/wiki/Attuma_Duum%27s_security_droid) |
| Auto-chauffeur |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Auto-chauffeur) |
| Auto-fighter | Droid starfighter |  |  | Visler Korda's faction | canon |  | [wiki](https://starwars.fandom.com/wiki/Auto-fighter) |
| Automated fire extinguisher | Firefighter |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Automated_fire_extinguisher) |
| Automated repair droid | Maintenance droid | Loratus Manufacturing |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Automated_repair_droid) |
| Automated sentry gun | Sentry droid / Class four droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Automated_sentry_gun) |
| Automover | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Automover) |
| Autonomous Translator Module, Mark II | Linguistics droid; Protocol droid |  |  | Jabba's criminal empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Autonomous_Translator_Module%2C_Mark_II) |
| AVA-2 Prowler Droid | Battle droid |  |  | Galactic Republic; Balmorran resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/AVA-2_Prowler_Droid) |
| AZ-322 Peacemaker | Battle droid |  |  | House Organa | canon |  | [wiki](https://starwars.fandom.com/wiki/AZ-322_Peacemaker) |
| AZ-series battle droid | Battle droid / Class four droid | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/AZ-series_battle_droid) |
| AZ-series surgical assistant droid | Medical droid | Cybot Galactica |  | Kaminoan government; Galactic Republic; Galactic Empire; Clone Force 99 | canon |  | [wiki](https://starwars.fandom.com/wiki/AZ-series_surgical_assistant_droid) |
| B-1 series mercenary sentry droid | B1-series battle droid line; Sentry |  |  | Droid Gotra; The Twins | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B-1_series_mercenary_sentry_droid) |
| B-1 series protocol droid | Protocol droid |  |  |  | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B-1_series_protocol_droid) |
| B-2 series mercenary sentry droid | B-series battle; Sentry |  |  | Droid Gotra; The Twins | canon | B2 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B-2_series_mercenary_sentry_droid) |
| B-3Z technical droid | Technical droid / Class 2 |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/B-3Z_technical_droid) |
| B-NK Series Subversion Droid | Espionage droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/B-NK_Series_Subversion_Droid) |
| B-series battle droid | Battle |  |  | Trade Federation; Techno Union; Jedi Order (secretly); Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/B-series_battle_droid) |
| B-T3 Guard Droid | Battle |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/B-T3_Guard_Droid) |
| B1 Electrostaff droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Commerce Guild | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1_Electrostaff_droid) |
| B1 grapple droid | Battle droid / Fourth class droid | Baktoid Combat Automata *(Legends)* |  | Confederacy of Independent Systems | canon (+Legends) | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1_grapple_droid) |
| B1 melee battle droid | Battle droid / Fourth-degree droid | Bedlam Raiders |  | Bedlam Raiders | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1_melee_battle_droid) |
| B1 recon droid | Battle droid | Baktoid Combat Automata / Baktoid Armor Workshop |  | Confederacy of Independent Systems | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1_recon_droid) |
| B1 repeater blaster droid | Battle droid | Baktoid Combat Automata / Baktoid Armor Workshop |  | Confederacy of Independent Systems | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1_repeater_blaster_droid) |
| B1 supervisor droid | Battle droid; Supervisor droid / Third-classed; Fourth-classed |  | c. 32 BBY | Confederacy of Independent Systems | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1_supervisor_droid) |
| B1-A air battle droid | Battle droid |  |  | Confederacy of Independent Systems | canon | B1A (OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1-A_air_battle_droid) |
| B1-Bokujin | Battle |  |  | Yakuza | canon |  | [wiki](https://starwars.fandom.com/wiki/B1-Bokujin) |
| B1-SAL Probe Droid | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/B1-SAL_Probe_Droid) |
| B1-series battle droid | Battle droid / Fourth-degree droid | Techno Union; Geonosis Industries |  | Trade Federation; Techno Union; Jedi Order (captured); Confederacy of Independent Systems | canon (+Legends) | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1-series_battle_droid) |
| B1-series rocket battle droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Trade Federation | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1-series_rocket_battle_droid) |
| B1-series worker droid | Loader droid / Class five droid | AccuTronics |  | Galactic Empire; Radell Mining Corporation | canon | B1 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B1-series_worker_droid) |
| B1E unit | Medical droid / Class one droid |  |  | Corporate Sector Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/B1E_unit) |
| B2 buzzsaw droid | Battle droid / Class four droid |  |  | Confederacy of Independent Systems | canon | B2 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B2_buzzsaw_droid) |
| B2 chainsaw droid | Battle droid |  |  | Confederacy of Independent Systems | canon | B2 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B2_chainsaw_droid) |
| B2 grapple droid | Battle droid | Baktoid Combat Automata *(Legends)* |  | Confederacy of Independent Systems | canon (+Legends) | B2 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B2_grapple_droid) |
| B2 groundmech | Groundmech | Cybot Galactica |  | Andor family; Ferrix resistance movement | canon | B2 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B2_groundmech) |
| B2-AA air assault super battle droid | Battle droid / Class four droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/B2-AA_air_assault_super_battle_droid) |
| B2-ACM Trooper | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/B2-ACM_Trooper) |
| B2-HA super battle droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Bedlam Raiders | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/B2-HA_super_battle_droid) |
| B2-RP battle droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/B2-RP_battle_droid) |
| B2-series super battle droid | Battle droid / Class four droid | Baktoid Combat Automata |  | Techno Union; Trade Federation; Confederacy of Independent Systems; Separatist holdouts | canon (+Legends) | B2 (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/B2-series_super_battle_droid) |
| B2-X Computer Interface Unit | Computer interface unit | MerenData |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/B2-X_Computer_Interface_Unit) |
| B25-SAL Probe Droid | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/B25-SAL_Probe_Droid) |
| B3 battle droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/B3_battle_droid) |
| B3 ultra battle droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/B3_ultra_battle_droid) |
| B3-A ultra battle droid | Ultra battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/B3-A_ultra_battle_droid) |
| B3NK series | Pilot | Loronar Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/B3NK_series) |
| B4J4 security droid | Fourth-degree droid | Blujay |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/B4J4_security_droid) |
| B4Q |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/B4Q) |
| B8G labor droid | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/B8G_labor_droid) |
| BAF-1000 Assault Droid | Battle droid | Balmorran Arms |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-1000_Assault_Droid) |
| BAF-101 Scout Droid | Battle droid | Balmorran Arms |  | Galactic Republic; Balmorran resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-101_Scout_Droid) |
| BAF-1010 Artillery Droid | Battle droid | Balmorran Arms |  | Galactic Republic; Balmorran resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-1010_Artillery_Droid) |
| BAF-300 Heavy Battle Droid | Battle droid | Balmorran Arms |  | Galactic Republic; Balmorran resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-300_Heavy_Battle_Droid) |
| BAF-320 Repair Droid | Maintenance droid | Balmorran Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-320_Repair_Droid) |
| BAF-379 Industrial Droid | Industrial droid | Balmorran Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-379_Industrial_Droid) |
| BAF-600 Warfare Droid | Battle droid | Balmorran Arms |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-600_Warfare_Droid) |
| BAF-616 Construction Droid | Construction droid | Balmorran Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-616_Construction_Droid) |
| BAF-888 Defense Droid | Battle droid | Balmorran Arms |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-888_Defense_Droid) |
| BAF-999 Prototype Siege Droid | Battle droid | Balmorran Arms |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-999_Prototype_Siege_Droid) |
| BAF-X Series Invasion Droid | Battle droid | Balmorran Arms |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/BAF-X_Series_Invasion_Droid) |
| Baggage-robo | General labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Baggage-robo) |
| Baker droid | Cooking droid |  |  | Galactic Republic | Legends |  | [wiki](https://starwars.fandom.com/wiki/Baker_droid/Legends) |
| BAL-Core | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BAL-Core) |
| Bank guard droid | Security droid |  |  | Nico Deemis' syndicate | canon |  | [wiki](https://starwars.fandom.com/wiki/Bank_guard_droid) |
| Bartender droid | Bartender droid |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Bartender_droid) |
| Basilisk war droid | Battle; Droid walker | Basiliskans; Mandalorians *(Legends)* |  | Mandalorian Crusaders | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Basilisk_war_droid) |
| Battle droid | Class four *(Legends)* |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Battle_droid) |
| Battle droid (Graveyard) | Battle droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_droid_%28Graveyard%29) |
| Battle droid assassin | Battle droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems; Gizor Dellso's army; X1's faction | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_droid_assassin) |
| Battle Droid AX | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_Droid_AX) |
| Battle Droid BX | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_Droid_BX) |
| Battle Droid C-10 | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_Droid_C-10) |
| Battle Droid C-11 | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_Droid_C-11) |
| Battle Droid C-13 | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Battle_Droid_C-13) |
| BB-series astromech droid | Astromech droid / Class two droid | Industrial Automaton |  | New Republic; Resistance; First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/BB-series_astromech_droid) |
| BB9 | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BB9) |
| BCA-11/X lightsaber practice droid | Lightsaber practice droid | Baktoid Combat Automata |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/BCA-11/X_lightsaber_practice_droid) |
| BD explorer droid | Explorer droid | Behold-Urwar Droid Concepts |  | Jedi Order; Mantis crew; Shadow University | canon |  | [wiki](https://starwars.fandom.com/wiki/BD_explorer_droid) |
| BD10-series assay support droid | Class three | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BD10-series_assay_support_droid) |
| BDM spydroid | Surveillance droid |  |  | Star Tours | canon |  | [wiki](https://starwars.fandom.com/wiki/BDM_spydroid) |
| BDX droid | Explorer droid | Mubo (Refurbishment) |  | New Republic; Black Spire Outpost; Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/BDX_droid) |
| Bear droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Bear_droid) |
| Bell-bot | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Bell-bot) |
| Bender (droid) | Construction |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Bender_%28droid%29) |
| Berserker droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Berserker_droid) |
| BFL | General labor | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BFL) |
| BG-series droid | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BG-series_droid) |
| BG01-1 farming droid | Farming droid; Security droid |  |  | Habo village | canon |  | [wiki](https://starwars.fandom.com/wiki/BG01-1_farming_droid) |
| BigHaul Robo-Hauler | Droid vehicle; Loader | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BigHaul_Robo-Hauler) |
| BigScoop Robo-Harvester | Agricultural | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BigScoop_Robo-Harvester) |
| BII Butler Droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BII_Butler_Droid) |
| Binary droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Binary_droid) |
| Binary loadlifter | Loadlifter droid / Class five |  |  | Galactic Republic; Confederacy of Independent Systems; Morgan Elsbeth's forces; First Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Binary_loadlifter) |
| Binoc droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Binoc_droid) |
| Biodroid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Biodroid) |
| Biological science droid | Class one |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Biological_science_droid) |
| Bird Droid |  |  |  | Star Tours | canon |  | [wiki](https://starwars.fandom.com/wiki/Bird_Droid) |
| BK-series Administrative Protocol Droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BK-series_Administrative_Protocol_Droid) |
| BL-1T Riot Suppression Droid | Security droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BL-1T_Riot_Suppression_Droid) |
| BL-39 interrogator droid | Interrogation droid | Aratech Repulsor Company |  | Darth Krayt's Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/BL-39_interrogator_droid) |
| BL-series Battle Legionnaire | Battle droid / Class four droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Mandalorian Protectors | canon |  | [wiki](https://starwars.fandom.com/wiki/BL-series_Battle_Legionnaire) |
| BL0-series non-lethal combat droid | Combat droid | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BL0-series_non-lethal_combat_droid) |
| Black Sun gladiator droid | Gladiator | Black Sun | destroyed discontinued 3.5 ABY | Black Sun | canon |  | [wiki](https://starwars.fandom.com/wiki/Black_Sun_gladiator_droid) |
| Blaredroid | Nihil | Zeetar |  | Nihil | canon |  | [wiki](https://starwars.fandom.com/wiki/Blaredroid) |
| Blastromech droid | Security |  |  | Alliance to Restore the Republic; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Blastromech_droid) |
| Blayne's droid | Battle | Doctor Blayne |  | Doctor Blayne | canon |  | [wiki](https://starwars.fandom.com/wiki/Blayne%27s_droid) |
| BLX labor droid | Labor Droid / Class five droid | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BLX_labor_droid) |
| BM-B unit |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BM-B_unit) |
| BN-C46 Cargo Hold Droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BN-C46_Cargo_Hold_Droid) |
| BN-G1D Guild Bank Droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BN-G1D_Guild_Bank_Droid) |
| BN-L3G Legacy Cargo Hold Droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BN-L3G_Legacy_Cargo_Hold_Droid) |
| BN-T0 Utility Droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BN-T0_Utility_Droid) |
| BN-T1 Utility Droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BN-T1_Utility_Droid) |
| Boatman droid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Boatman_droid) |
| Bodyguard droid | Class four |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Bodyguard_droid) |
| Boku jinken droid | Battle |  |  | Yakuza | canon |  | [wiki](https://starwars.fandom.com/wiki/Boku_jinken_droid) |
| Bomb droid | Battle |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Bomb_droid) |
| Boss miner droid | Class five mining droid |  |  | Confederacy of Independent Systems; Nightsisters | canon |  | [wiki](https://starwars.fandom.com/wiki/Boss_miner_droid) |
| Botanical collection droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Botanical_collection_droid) |
| BR-series | Astromech droid |  |  | Zero Company | canon |  | [wiki](https://starwars.fandom.com/wiki/BR-series) |
| Brain walker |  |  |  | B'omarr Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Brain_walker) |
| Brochure droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Brochure_droid) |
| BRT supercomputer | Municipal Planning & Management | Aratech Repulsor Company | 200 BBY |  | Legends |  | [wiki](https://starwars.fandom.com/wiki/BRT_supercomputer/Legends) |
| BT-1 assassin droid | Assassin droid | Tarkin Initiative |  | Galactic Empire; Aphra's crew; Sith Order; Archaeologists | canon |  | [wiki](https://starwars.fandom.com/wiki/BT-1_assassin_droid) |
| BT-16 perimeter droid | Fourth degree | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/BT-16_perimeter_droid) |
| BT-series ordnance droid | Loader droid | Baktoid Fleet Ordnance |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BT-series_ordnance_droid) |
| BU-series bartender droid | Bartender | Industrial Automaton |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/BU-series_bartender_droid) |
| Bugnaught | Battle droid |  |  | The Cauldron | canon |  | [wiki](https://starwars.fandom.com/wiki/Bugnaught) |
| Builder Droid BD-17 | Labor droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Builder_Droid_BD-17) |
| Buoy droid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Buoy_droid) |
| Butler droid | Service |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Butler_droid) |
| Butterbug remote | Remote |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Butterbug_remote) |
| Buzz-droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Buzz-droid) |
| BX-23 Probe Droid | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BX-23_Probe_Droid) |
| BX-24 Probe Droid | Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BX-24_Probe_Droid) |
| BX-series droid commando | Battle droid / Fourth-degree droid | Baktoid Combat Automata; Confederacy of Independent Systems |  | Confederacy of Independent Systems; Hutt Clan; Cad Bane's group; Separatist holdouts | canon (+Legends) | BX commando (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/BX-series_droid_commando) |
| BXL-99 labor droid | Labor droid / Class five droid |  |  | Feral droids | canon |  | [wiki](https://starwars.fandom.com/wiki/BXL-99_labor_droid) |
| BY2B maintenance droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/BY2B_maintenance_droid) |
| C-1 protocol droid | Protocol droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C-1_protocol_droid) |
| C-10-L Rapid Response Droid | Rapid response droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/C-10-L_Rapid_Response_Droid) |
| C-14 |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/C-14) |
| C-8 saboteur droid | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/C-8_saboteur_droid) |
| C-9 protocol droid | Protocol droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C-9_protocol_droid) |
| C-B3 cortosis battle droid | Battle droid | Solha | By 19 BBY | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/C-B3_cortosis_battle_droid) |
| C-class VoxPop advocate droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C-class_VoxPop_advocate_droid) |
| C-series | Astromech droid | Industrial Automaton |  | Galactic Republic; Syndulla clan; Spectres; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/C-series) |
| C-series protocol droid | Protocol | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C-series_protocol_droid) |
| C-Viper series | Security | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C-Viper_series) |
| C0-RU Probe | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C0-RU_Probe) |
| C1-series astromech droid | Astromech droid / Class 2 | Industrial Automaton | retired Prior to or during 2 BBY | Galactic Republic; Alliance to Restore the Republic; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/C1-series_astromech_droid) |
| C2-N Dominator Droid | Battle droid |  | destroyed 3640 BBY, Corellia | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/C2-N_Dominator_Droid) |
| C2-R4 Multipurpose Unit |  | Squibs |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C2-R4_Multipurpose_Unit) |
| C3 |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C3) |
| C3-KR Probe Droid | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C3-KR_Probe_Droid) |
| C4LR litigation droid | Class three droid | Caldrahlsen Mechanicals |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/C4LR_litigation_droid) |
| C5D construction droid | Construction droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C5D_construction_droid) |
| C7-A7 Guard Droid | Security droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/C7-A7_Guard_Droid) |
| Cam droid | Class three; Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Cam_droid) |
| CAM-R0N Surveillance Probe | Surveillance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/CAM-R0N_Surveillance_Probe) |
| Camera Droid (Grand Arena) | Cam droid |  |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Camera_Droid_%28Grand_Arena%29) |
| Carbonite war droid | Battle droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Carbonite_war_droid) |
| Caretaker droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Caretaker_droid) |
| Caretaker droid (Iokath) |  | Unidentified Iokath species |  | Unidentified Iokath species; ARIES | canon |  | [wiki](https://starwars.fandom.com/wiki/Caretaker_droid_%28Iokath%29) |
| Caretaker Probe droid | Environmental droid |  |  | Jannimak | canon |  | [wiki](https://starwars.fandom.com/wiki/Caretaker_Probe_droid) |
| CB | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/CB) |
| CB-2B Maintenance Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/CB-2B_Maintenance_Droid) |
| CD-2 Harvester | Agrirobot | Corporate Sector Authority |  | Galactic Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/CD-2_Harvester) |
| Centaur Battle Droid | Battle droid | Baktoid Combat Automata |  | Baktoid Combat Automata | canon |  | [wiki](https://starwars.fandom.com/wiki/Centaur_Battle_Droid) |
| Ceremony, Gala, and Ritual droid | Protocol droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ceremony%2C_Gala%2C_and_Ritual_droid) |
| Cesta security droid | Security | Cestus Cybernetics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Cesta_security_droid) |
| CG guardian droid | Guardian droid |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/CG_guardian_droid) |
| Challat eater droid | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Challat_eater_droid) |
| Chameleon droid | Combat probe | Arakyd Industries; Techno Union *(Legends)* |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Chameleon_droid) |
| Chauffeur droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Chauffeur_droid) |
| Chiba DR-10 protocol droid | Class three droid | Chiba Corporation |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Chiba_DR-10_protocol_droid) |
| Chiewab Medical Droid | Medical droid / Class one droid | Chiewab Amalgamated Pharmaceuticals Company |  | Death Watch; Kaminoan cloners | canon |  | [wiki](https://starwars.fandom.com/wiki/Chiewab_Medical_Droid) |
| Chirq Council Mechanized Guardian | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Chirq_Council_Mechanized_Guardian) |
| Chroon-Tan B-Machine | Midwife droid / Class one |  |  | Kallidahin *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Chroon-Tan_B-Machine) |
| Church droid |  |  |  | Church of the Force; Temple of the Kyber | canon |  | [wiki](https://starwars.fandom.com/wiki/Church_droid) |
| CI-09 Peacekeeper | Battle |  |  | Dread Pirate Karvoy | canon |  | [wiki](https://starwars.fandom.com/wiki/CI-09_Peacekeeper) |
| City surveillance droid | Cam |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/City_surveillance_droid) |
| Class five droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Class_five_droid) |
| Class four droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Class_four_droid) |
| Class one droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Class_one_droid) |
| Class three droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Class_three_droid) |
| Class two droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Class_two_droid) |
| Class Two multi-phasic robot | Class two |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Class_Two_multi-phasic_robot) |
| Class-six protocol droid | Protocol droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Class-six_protocol_droid) |
| CLE-004 window cleaning droid | Class 5 | Publitechnic |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/CLE-004_window_cleaning_droid) |
| Cleaning droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Cleaning_droid) |
| CLL-series | Binary loadlifter | Cybot Galactica |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/CLL-series) |
| Cloud City security droid | Security droid |  |  | Cloud City | canon |  | [wiki](https://starwars.fandom.com/wiki/Cloud_City_security_droid) |
| CM3-series protocol droid | Protocol droid | Czerka Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/CM3-series_protocol_droid) |
| Cold assault battle droid | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Cold_assault_battle_droid) |
| Cold-weather Hailfire Droid | Droid tank |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Cold-weather_Hailfire_Droid) |
| Colicoid Infiltrator-series droid | Class four droid | Colicoid Creation Nest |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Colicoid_Infiltrator-series_droid) |
| Colossus droid | Security | ARIES |  | ARIES | canon |  | [wiki](https://starwars.fandom.com/wiki/Colossus_droid) |
| Combat analysis droid | Analysis droid | Czerka Corporation |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Combat_analysis_droid) |
| Combat-trainer | Training |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Combat-trainer) |
| Command Droid Mark V | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Command_Droid_Mark_V) |
| Command Droid Mark VII | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Command_Droid_Mark_VII) |
| Commando droid captain | Battle droid / Fourth-degree droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Commando_droid_captain) |
| Commando Droid Diplomat | Battle droid / Fourth-degree droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Commando_Droid_Diplomat) |
| Commando recon droid | Probe droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Commando_recon_droid) |
| Communications droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Communications_droid) |
| Confederate infantry prototype | Battle droid / Class four droid | Gizor Dellso | retired Sometime between 18 BBY and 12 BBY | Separatist holdouts | canon |  | [wiki](https://starwars.fandom.com/wiki/Confederate_infantry_prototype) |
| Construction droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Construction_droid) |
| Construction droid foreman | Construction |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Construction_droid_foreman) |
| Construction droid Mark II | Class five droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Construction_droid_Mark_II) |
| Control maintenance droid | Maintenance droid / Class two droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Control_maintenance_droid) |
| Controller droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Controller_droid) |
| COO-series cook droid | Kitchen droid / Class 3 | Industrial Automaton |  | Alliance to Restore the Republic; Scourge (As a vessel); Hutt Clan; Plazir-15 government | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/COO-series_cook_droid) |
| Cooking droid | Class three; Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Cooking_droid) |
| Corps Commander | Battle droid / Class four droid | Xim the Despot |  | Xim's empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Corps_Commander) |
| Cortosis sentry droid | Sentry droid |  |  | Empire of the Hand | canon |  | [wiki](https://starwars.fandom.com/wiki/Cortosis_sentry_droid) |
| Corvax Sentinel | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Corvax_Sentinel) |
| Courier droid | Messenger droid |  |  | Zam Wesell; Galactic Empire; Pyke Syndicate | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Courier_droid) |
| Crablike maintenance droid | Maintenance droid |  |  | Star of Empire; Systems Infiltration Manager | canon |  | [wiki](https://starwars.fandom.com/wiki/Crablike_maintenance_droid) |
| Crane droid | Industrial droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Crane_droid) |
| Crawl-carrier | Espionage droid | Confederacy of Independent Systems |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Crawl-carrier) |
| Crimson Condottiere | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Crimson_Condottiere) |
| Crisp-E-O donut droid | Cooking droid |  |  | Dexter Jettster | canon |  | [wiki](https://starwars.fandom.com/wiki/Crisp-E-O_donut_droid) |
| Crowd control droid | Security |  |  | Jinata Security | canon |  | [wiki](https://starwars.fandom.com/wiki/Crowd_control_droid) |
| Cryodroid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Cryodroid) |
| CT-4 series medical droid | Medical droid | Polis Massa Pria Assemblage |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/CT-4_series_medical_droid) |
| Culinary septoid droid | Cooking droid / Class 3 |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Culinary_septoid_droid) |
| Cultivator unit | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Cultivator_unit) |
| Customs droid | Service |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Customs_droid) |
| CWW8 Battle Droid | Battle droid | Neimoidian droid factory |  | Confederacy of Independent Systems; HK-47's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/CWW8_Battle_Droid) |
| CY-M Prototype | Battle |  |  | HK-47's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/CY-M_Prototype) |
| Cyclens | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Cyclens) |
| CZ-2X Infiltrator Droid | Battle droid | Czerka Arms |  | Czerka Arms | canon |  | [wiki](https://starwars.fandom.com/wiki/CZ-2X_Infiltrator_Droid) |
| CZ-4X Assault Droid | Battle droid | Czerka Arms |  | Czerka Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/CZ-4X_Assault_Droid) |
| CZ-series tutor droid | Educational |  | Many years before 19 BBY | Kyrell family; House of Organa; Disciples of the Whills | canon |  | [wiki](https://starwars.fandom.com/wiki/CZ-series_tutor_droid) |
| Czerka Mark 4 Droid | Battle droid | Czerka Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Czerka_Mark_4_Droid) |
| Czerka tripod battledroid | Battle droid | Czerka Corporation |  | Czerka Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Czerka_tripod_battledroid) |
| D-03 Repair Droid | Maintenance droid |  |  | Dread Host | canon |  | [wiki](https://starwars.fandom.com/wiki/D-03_Repair_Droid) |
| D-60 assault droid | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/D-60_assault_droid) |
| D-90 assault droid | B-series battle |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/D-90_assault_droid) |
| D-R0M Probe | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/D-R0M_Probe) |
| D-series protocol droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/D-series_protocol_droid) |
| D1-series aerial battle droid | Security droid | Techno Union | By 26 BBY | Techno Union; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/D1-series_aerial_battle_droid) |
| D99-X Maintenance Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/D99-X_Maintenance_Droid) |
| DA worker droid | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DA_worker_droid) |
| DA-series droid | Analysis |  |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/DA-series_droid) |
| Daa Corporation droid | Security droid |  |  | Daa Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Daa_Corporation_droid) |
| Dac pirate droid | Battle *(Legends)* |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Dac_pirate_droid) |
| Dark Trooper |  |  |  | Galactic Republic; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Dark_Trooper) |
| Darth Savik's remote droid | Battle droid | Darth Savik |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Darth_Savik%27s_remote_droid) |
| DBX |  | Delban Faxicorp |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DBX) |
| DC5-1 | Freight droid | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DC5-1) |
| DCM-8 Missile Platform Droid | Missile platform droid | Arakyd Patrol |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DCM-8_Missile_Platform_Droid) |
| DD-1 hover droid | Training droid | Industrial Automaton |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/DD-1_hover_droid) |
| DD-13 medical assistant droid | Medical droid | Ubrikkian Industries |  | Galactic Republic; Galactic Empire; Polis Massa Base | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/DD-13_medical_assistant_droid) |
| DD-19 "Overseer" labor pool droid | Supervisor droid / Class three droid | Ubrikkian Steamworks |  | Stark family; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/DD-19_%22Overseer%22_labor_pool_droid) |
| Dealer droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Dealer_droid) |
| Decimator 397 series assassin droid | Class four droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Decimator_397_series_assassin_droid) |
| Decon droid | Hazardous-service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Decon_droid) |
| Decon III | Decon droid | Industrial Automaton |  | Galactic Republic; Galactic Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Decon_III) |
| Defender 01-X | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Defender_01-X) |
| Defender 03-Z | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Defender_03-Z) |
| Defender Droid | Security; YVH-series battle | Tendrando Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Defender_Droid) |
| Delving droid | Mining droid |  |  | Blythe family | canon |  | [wiki](https://starwars.fandom.com/wiki/Delving_droid) |
| Demolisher weapons droid |  |  |  | Pirates of Tarnoonga | canon |  | [wiki](https://starwars.fandom.com/wiki/Demolisher_weapons_droid) |
| Demolition droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Demolition_droid) |
| Demolitionmech | Class two |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Demolitionmech) |
| Design droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Design_droid) |
| Detainment droid | Security |  |  | Galactic Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Detainment_droid) |
| Devastator war droid | Assassin droid | Ubrikkian Steamworks |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Devastator_war_droid) |
| DG-1B catering droid | Cooking droid / Class 3 | Industrial Automaton |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/DG-1B_catering_droid) |
| Diagnostics droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Diagnostics_droid) |
| Digger series sixwunthree | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Digger_series_sixwunthree) |
| Digit droid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Digit_droid) |
| Directional droid |  |  |  | Galactic Republic; Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Directional_droid) |
| Diver droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Diver_droid) |
| DK-27 Guardian Droid | Security droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DK-27_Guardian_Droid) |
| DL-series | Security droid / Class four droid | Veril Line Systems |  | Star Tours | canon |  | [wiki](https://starwars.fandom.com/wiki/DL-series) |
| DLC-13 Mining Droid | Mining droid |  |  | Klegger Corporation; Mensix Mining Company | canon |  | [wiki](https://starwars.fandom.com/wiki/DLC-13_Mining_Droid) |
| DLR series protocol droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DLR_series_protocol_droid) |
| DN-724 forensics droid | Analysis |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DN-724_forensics_droid) |
| Dogbot | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Dogbot) |
| Domodroid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Domodroid) |
| Doroido | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Doroido) |
| Doughnut dispenser droid | Cooking |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Doughnut_dispenser_droid) |
| DP-2 probe droid | Probe droid / Class two droid | Duwani Mechanical Products |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DP-2_probe_droid) |
| DP-6 Guard Droid | Security droid |  | destroyed 3640 BBY, Corellia | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DP-6_Guard_Droid) |
| Dragon-bird robot drone | Training |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Dragon-bird_robot_drone) |
| Dressing droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Dressing_droid) |
| DRFT-R | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DRFT-R) |
| Driller series Aynine | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Driller_series_Aynine) |
| Drilling droid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Drilling_droid) |
| Drink dispenser droid | Nurse droid; Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Drink_dispenser_droid) |
| DRK-1 Dark Eye probe droid | Probe droid; Spy droid; Camera droid |  |  | Sith; Confederacy of Independent Systems; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DRK-1_Dark_Eye_probe_droid) |
| Droid chef | Cooking droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_chef) |
| Droid cruiser | Battle droid / Class four droid |  |  | Fromm Gang | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_cruiser) |
| Droid guard | Security droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_guard) |
| Droid laser turret (Primacy) | Turret-droid |  |  | Bedlam Raiders | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_laser_turret_%28Primacy%29) |
| Droid laser turret (Saak'ak) | Turret-droid |  |  | Trade Federation | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Droid_laser_turret_%28Saak%27ak%29) |
| Droid lifeguard | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_lifeguard) |
| Droid marine | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Separatist holdouts | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_marine) |
| Droid racer | Droid starfighter |  |  | Team Vranki | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_racer) |
| Droid spy ball | Surveillance and listening |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Droid_spy_ball) |
| Droid starfighter | Battle; Droid vehicle |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Droid_starfighter) |
| Droid tank | Battle; Droid vehicle |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Droid_tank) |
| Droid tram |  |  |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_tram) |
| Droid worker | Battle droid / Class four | Karina | retired 0 ABY | Karina's empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Droid_worker) |
| Droideka | Battle droid | Colicoid Creation Nest |  | Xrexus Cartel; Trade Federation; Confederacy of Independent Systems; Separatist holdouts | canon (+Legends) | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Droideka) |
| Droideka Mark II | Battle droid / Class four droid | Phlac-Arphocc Automata Industries (designer); Zann Consortium Droid Works |  | Confederacy of Independent Systems; Separatist holdout; Zann Consortium | canon | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Droideka_Mark_II) |
| Droideka Oppressor | Battle droid |  |  | Alliance to Restore the Republic; Galactic Empire | canon | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Droideka_Oppressor) |
| Droideka Sentinel | Battle droid |  |  | Alliance to Restore the Republic; Galactic Empire | canon | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Droideka_Sentinel) |
| Droideka Sharpshooter | Battle droid | Colicoid Creation Nest |  | Trade Federation; Confederacy of Independent Systems | canon | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Droideka_Sharpshooter) |
| Drone |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Drone) |
| Dry Cleaner Droid | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Dry_Cleaner_Droid) |
| DSD1 dwarf spider droid | Battle droid | Baktoid Armor Workshop |  | Commerce Guild; Trade Federation; Confederacy of Independent Systems | canon (+Legends) | DSD1 dwarf spider (JDS) | [wiki](https://starwars.fandom.com/wiki/DSD1_dwarf_spider_droid) |
| DSK-1 "Deathstrike" seeker droid | Battle droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DSK-1_%22Deathstrike%22_seeker_droid) |
| DT-16 Destructor battle droid | 4th-degree Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DT-16_Destructor_battle_droid) |
| DT-17 | Attack droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DT-17) |
| DT-series sentry droid | Assassin droid; Sentry droid; Training droid | Baktoid Combat Automata | 19 BBY (white model); By 9 BBY (black model) | Ruling Council; Galactic Republic; Galactic Empire; Clone Force 99 (reprogrammed) | canon |  | [wiki](https://starwars.fandom.com/wiki/DT-series_sentry_droid) |
| DTS-series dismantler droid | Demolition droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DTS-series_dismantler_droid) |
| Duelist Elite | Training droid / Class four droid *(Legends)* | Trang Robotics *(Legends)* |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Duelist_Elite) |
| DUM-series pit droid | Repair droid / Class 5 | Serv-O-Droid, Inc. |  | Galactic Republic; Alliance to Restore the Republic; Scourge (As a vessel); The Colossus | canon (+Legends) | DUM pit droid (OuterRim) | [wiki](https://starwars.fandom.com/wiki/DUM-series_pit_droid) |
| DV4 maintenance droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/DV4_maintenance_droid) |
| Dwarf probe droid | Probe droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Dwarf_probe_droid) |
| DX-2 Dominator Droid | Battle droid |  | destroyed 3640 BBY, Corellia | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DX-2_Dominator_Droid) |
| DX-5 Incinerator Droid | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DX-5_Incinerator_Droid) |
| DX-6 Ravager | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DX-6_Ravager) |
| DZ-70 fugitive tracker droid | Combat probe | Arakyd Industries |  | Confederacy of Independent Systems; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/DZ-70_fugitive_tracker_droid) |
| E-3PO | 3PO-series protocol droid | Cybot Galactica |  | Galactic Empire; IG-88's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/E-3PO) |
| E-5 battle droid | Battle droid / Class four droid | Baktoid Combat Automata |  | Trade Federation; Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/E-5_battle_droid) |
| E-B load lifter | Loader |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/E-B_load_lifter) |
| E-series protocol droid | Protocol droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/E-series_protocol_droid) |
| E-XD-series infiltrator droid | Recon droid | Imperial Department of Military Research |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/E-XD-series_infiltrator_droid) |
| E2-I6 | Educational |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/E2-I6) |
| E3 Companion Droid | Class three | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/E3_Companion_Droid) |
| E4 baron droid | Battle droid | Baktoid Combat Automata |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/E4_baron_droid) |
| E522 assassin droid | Assassin droid | Baktoid Combat Automata (initially); Sienar Intelligence Systems |  | Confederacy of Independent Systems; Galactic Empire; Alliance to Restore the Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/E522_assassin_droid) |
| EB-89 Engine Maintenance Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/EB-89_Engine_Maintenance_Droid) |
| ED-V8-series envoy droid | Protocol droid | Rseikharhl Droid Group |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ED-V8-series_envoy_droid) |
| ED4 |  | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ED4) |
| EG labor droid | Labor droid / Class five droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/EG_labor_droid) |
| EG-5 Jedi Hunter droid | Battle droid |  | retired c. 21 BBY | InterGalactic Banking Clan; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/EG-5_Jedi_Hunter_droid) |
| EG-series power droid | Power droid | Veril Line Systems |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/EG-series_power_droid) |
| EI-9 network security droid | security droid / Class two droid | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/EI-9_network_security_droid) |
| Electric Caliph | Battle |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/Electric_Caliph) |
| Electrorefining droid | Mining droid / Fifth-degree droid |  |  | Techno Union | canon |  | [wiki](https://starwars.fandom.com/wiki/Electrorefining_droid) |
| Elevator droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Elevator_droid) |
| Eliminator 434-series assassin droid | Assassin droid / Class four droid | Unknown |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Eliminator_434-series_assassin_droid) |
| Elite Droid 04-A | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Elite_Droid_04-A) |
| EM-Two probe droid | Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/EM-Two_probe_droid) |
| Engine maintenance droid | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Engine_maintenance_droid) |
| Engineer battle droid | Battle droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems; Separatist holdouts; X1's faction | canon |  | [wiki](https://starwars.fandom.com/wiki/Engineer_battle_droid) |
| Engineering droid | Class two |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Engineering_droid) |
| Entertainment droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Entertainment_droid) |
| Environment droid Mark II | Mining droid |  |  | Peragus Mining Facility | canon |  | [wiki](https://starwars.fandom.com/wiki/Environment_droid_Mark_II) |
| Environmental droid | Class two |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Environmental_droid) |
| EOD-Mk IV explosives disposal remote | Remote | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/EOD-Mk_IV_explosives_disposal_remote) |
| EPHEMERIS |  | Eternal Empire |  | Eternal Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/EPHEMERIS) |
| ER-05 Maintenance Droid | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ER-05_Maintenance_Droid) |
| ER-1 probe droid | Probe droid | Graf Zapalo; A female droid designer; A male droid designer |  | Naboo | canon |  | [wiki](https://starwars.fandom.com/wiki/ER-1_probe_droid) |
| Eradicator-series battle droid | Battle droid / Class four droid | Colicoid |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Eradicator-series_battle_droid) |
| ERL-21 transcribot | Cam | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ERL-21_transcribot) |
| Espionage droid | Spy |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Espionage_droid) |
| EV-series |  | MerenData |  | Confederacy of Independent Systems; Galactic Empire; Alliance to Restore the Republic; Scourge (As a vessel) | canon |  | [wiki](https://starwars.fandom.com/wiki/EV-series) |
| EV-series medical droid | Medical droid | MerenData |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/EV-series_medical_droid) |
| EverAlert droid | Security | Justice Systems |  | Galactic Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/EverAlert_droid) |
| Evolution Droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Evolution_Droid) |
| EVS Construction Droid | Heavy industry; Automated factory | Veril Line Systems |  | Galactic Empire; Archa Sabis's droid army; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/EVS_Construction_Droid) |
| EW-39 War Droid | Battle droid |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/EW-39_War_Droid) |
| EX communication droid | Communications |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/EX_communication_droid) |
| EX-49 Mining Droid | Mining droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/EX-49_Mining_Droid) |
| Excavation droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Excavation_droid) |
| Executioner droid | Battle |  |  | Kenna | canon |  | [wiki](https://starwars.fandom.com/wiki/Executioner_droid) |
| ExOne series |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ExOne_series) |
| Explorer droid | Class two |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Explorer_droid) |
| Explorer Mk. V | Exploration | Smitroo Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Explorer_Mk._V) |
| Extermination droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Extermination_droid) |
| Eyeball Droid | Security droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Eyeball_Droid) |
| F series repair droid | Maintenance droid |  |  | Star Tours | canon |  | [wiki](https://starwars.fandom.com/wiki/F_series_repair_droid) |
| F1 exploration droid | Exploration droid / Class 5 | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/F1_exploration_droid) |
| F1-XD Autorepair Droid | Repair probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/F1-XD_Autorepair_Droid) |
| F2 Exploration Droid | Labor droid | Cybot Galactica |  | Various | canon |  | [wiki](https://starwars.fandom.com/wiki/F2_Exploration_Droid) |
| F4-RM Agriculture Droid | Agrirobot |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/F4-RM_Agriculture_Droid) |
| F7V Valet/Translator Droid | Service | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/F7V_Valet/Translator_Droid) |
| FA-4 pilot droid | Pilot droid / Class five | SoroSuub Corporation |  | Confederacy of Independent Systems; Galactic Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/FA-4_pilot_droid) |
| FA-5 valet droid | Pilot droid / Class three | SoroSuub Corporation |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/FA-5_valet_droid) |
| FA-series | Service droid | SoroSuub Corporation |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/FA-series) |
| Facilities Droid FA-18 | Maintenance droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Facilities_Droid_FA-18) |
| Factory droid | Labor droid / Class 5 |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Factory_droid) |
| Farmer droid | Labor droid | Industrial Automaton |  | A human tribe | canon |  | [wiki](https://starwars.fandom.com/wiki/Farmer_droid) |
| Fast-moving Probe Droid | Probe droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Fast-moving_Probe_Droid) |
| Fastbreeder | Labor droid; Combat droid | Self-replicating | Between 3658 BBY and 3643 BBY – retired 3643 BBY | Cinzia Xandret | canon |  | [wiki](https://starwars.fandom.com/wiki/Fastbreeder) |
| Fastlatch-class defense droid | Defense/security droid / Class four droid | Trade Federation |  | Pressure pirates; Clode Rhoden | canon |  | [wiki](https://starwars.fandom.com/wiki/Fastlatch-class_defense_droid) |
| FD-series extinguisher droid | Firefighter droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FD-series_extinguisher_droid) |
| FD3-MN fighting droid | Gladiator droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FD3-MN_fighting_droid) |
| FD4 fighting droid | Gladiator droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FD4_fighting_droid) |
| FDP-6000 Culinary Droid | Cooking droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FDP-6000_Culinary_Droid) |
| FEG-series pilot droid | Pilot droid / Class two droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FEG-series_pilot_droid) |
| Ferry droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ferry_droid) |
| Fertility droid | Medical |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Fertility_droid) |
| Fertilizer unit | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Fertilizer_unit) |
| Fiddler 10 | Maintenance droid |  |  | Fromm Gang | canon |  | [wiki](https://starwars.fandom.com/wiki/Fiddler_10) |
| Fighting droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Fighting_droid) |
| FIII Footman droid | 4th-degree security droid/servant droid | Tac-Spec Corporation |  | House Malreaux; House of Tund | canon |  | [wiki](https://starwars.fandom.com/wiki/FIII_Footman_droid) |
| Finance Retrieval and Net Investigations droid |  | Investa Arts |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Finance_Retrieval_and_Net_Investigations_droid) |
| Fire suppression droid Mark I | Firefighter |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Fire_suppression_droid_Mark_I) |
| Firefighter battle droid | Firefighter droid / Class three droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Firefighter_battle_droid) |
| Firefighter droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Firefighter_droid) |
| First Order probe droid | Probe droid / Class three droid |  |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/First_Order_probe_droid) |
| First Order sentry droid | Sentry droid; Security droid / Class Four | Rebaxan Columni |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/First_Order_sentry_droid) |
| FIV footman droid | Footman droid | Tac-Spec |  | House Kryze | canon |  | [wiki](https://starwars.fandom.com/wiki/FIV_footman_droid) |
| FL-1 Load Lifter Droid | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FL-1_Load_Lifter_Droid) |
| Flame battle droid | Battle droid | Trade Federation |  | Trade Federation; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Flame_battle_droid) |
| FLD scythe droid | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FLD_scythe_droid) |
| Flight droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Flight_droid) |
| Floating droid | Training |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Floating_droid) |
| Floating mine | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Floating_mine) |
| Flood droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Flood_droid) |
| Floor cleaner | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Floor_cleaner) |
| Floor-polish droid | Cleaning droid / Class five droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Floor-polish_droid) |
| FLR-series Logger Droid | Class 2 | Greel Wood Logging Corporation; Industrial Automaton |  | Greel Wood Logging Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/FLR-series_Logger_Droid) |
| FLTCH-series battle droid | Battle droid / Class four droid | Colicoid Creation Nest |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/FLTCH-series_battle_droid) |
| Fly eye | Surveillance droid | Loronar Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Fly_eye) |
| Flying attack droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Flying_attack_droid) |
| FO-4 warden droid | Warden droid | Ulban Arms |  | Corporate Sector Authority; Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/FO-4_warden_droid) |
| Foot droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Foot_droid) |
| Footman droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Footman_droid) |
| Foreign Intruder Defense Organism | Armor | New Republic Department of Research and Development |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Foreign_Intruder_Defense_Organism) |
| Forensics droid | Analysis |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Forensics_droid) |
| Fort IV | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Fort_IV) |
| Fort V | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Fort_V) |
| Freight droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Freight_droid) |
| FSD-6D flying surveillance droid | Surveillance droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/FSD-6D_flying_surveillance_droid) |
| Fuel droid | Class five droid |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Fuel_droid) |
| Fungus droid | Surveillance and listening |  |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Fungus_droid) |
| FUS-3 | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FUS-3) |
| FX-14 medical droid | Medical droid / Class one droid |  |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/FX-14_medical_droid) |
| FX-2 droid | Medical droid / Class one droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FX-2_droid) |
| FX-6 droid | Medical droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FX-6_droid) |
| FX-7 medical assistant droid | Medical droid / Class one droid | Medtech Industries |  | Galactic Republic; Alliance to Restore the Republic | canon | FX-7 (OuterRim) | [wiki](https://starwars.fandom.com/wiki/FX-7_medical_assistant_droid) |
| FX-8 |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/FX-8) |
| FX-series medical assistant droid | Medical droid | Medtech Industries |  | Galactic Empire; Alliance to Restore the Republic | canon (+Legends) | FX-series (OuterRim) | [wiki](https://starwars.fandom.com/wiki/FX-series_medical_assistant_droid) |
| G-100 remote banking droid | Mathematics | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G-100_remote_banking_droid) |
| G-12 service droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G-12_service_droid) |
| G-2RD series guard droid | Guard droid | Arakyd Industries | Before 0 BBY | Galactic Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/G-2RD_series_guard_droid) |
| G-40 | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G-40) |
| G0-ON Abductor | Battle droid |  |  | Nocturno | canon |  | [wiki](https://starwars.fandom.com/wiki/G0-ON_Abductor) |
| G0-ON Attacker | Battle droid |  |  | Nocturno | canon |  | [wiki](https://starwars.fandom.com/wiki/G0-ON_Attacker) |
| G0-T0 infrastructure planning system | Planning droid | Aratech Repulsor Company |  | Galactic Republic | canon | G0-T0 (KotOR) | [wiki](https://starwars.fandom.com/wiki/G0-T0_infrastructure_planning_system) |
| G1 series equipment operator droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G1_series_equipment_operator_droid) |
| G1T4-M1N1 | Astromech Droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G1T4-M1N1) |
| G2 repair droid | Maintenance droid | SoroSuub Corporation *(Legends)* | Between 19 BBY and 9 BBY – retired 12 ABY *(Legends)* | Resistance | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/G2_repair_droid) |
| G30-MN mining unit | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G30-MN_mining_unit) |
| G4 | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G4) |
| G4-B3 Heavy Fabricator | Labor droid |  | destroyed 3639 BBY, Nal Hutta | Karagga | canon |  | [wiki](https://starwars.fandom.com/wiki/G4-B3_Heavy_Fabricator) |
| G9 droid |  | Verpine |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/G9_droid) |
| GA Series Information Analysis Unit | Analysis | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GA_Series_Information_Analysis_Unit) |
| GA-97 (Czerka) |  |  |  | Czerka Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/GA-97_%28Czerka%29) |
| GA-series servant droid | Servant droid / Class three droid | Reiffworks Droid Restoration |  | Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/GA-series_servant_droid) |
| Gambling droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Gambling_droid) |
| Gand med droid | Medical droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Gand_med_droid) |
| Garbage droid | Cleaning droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Garbage_droid) |
| Gardener droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Gardener_droid) |
| GB-IB | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/GB-IB) |
| GB-III | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/GB-III) |
| GD16-series pilot droid | pilot droid / Class five droid | MerenData |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GD16-series_pilot_droid) |
| GE3-series protocol droid | Protocol droid | Czerka Corporation |  |  | canon | GE3 (KotOR) | [wiki](https://starwars.fandom.com/wiki/GE3-series_protocol_droid) |
| Gel-form droid | Training |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Gel-form_droid) |
| GEMINI | Sentient droids | Eternal Empire |  | Eternal Empire; Eternal Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/GEMINI) |
| GG-series hospitality droid | Protocol | Adascorp |  | Adascorp | canon |  | [wiki](https://starwars.fandom.com/wiki/GG-series_hospitality_droid) |
| GH Maintenance Droid | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GH_Maintenance_Droid) |
| GH-7 medical analysis unit | Class 1 Medical droid | Chiewab Amalgamated Pharmaceuticals Company |  | Confederacy of Independent Systems; Galactic Republic; Polis Massa | canon |  | [wiki](https://starwars.fandom.com/wiki/GH-7_medical_analysis_unit) |
| GH-7 series medical assistance droid | Medical droid | Chiewab Amalgamated Pharmaceuticals |  | Polis Massa Base | canon |  | [wiki](https://starwars.fandom.com/wiki/GH-7_series_medical_assistance_droid) |
| GH-8 medical droid | Medical droid |  |  | Vashka City Medcenter One | canon |  | [wiki](https://starwars.fandom.com/wiki/GH-8_medical_droid) |
| GHT-series Medevac unit | Class one droid | TelBrinTel Corporation |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/GHT-series_Medevac_unit) |
| Giant armadillo | Droid tank |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Giant_armadillo) |
| GK Oppressor | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GK_Oppressor) |
| GK-5 sentry droid | Sentry droid |  |  | HK-47 | canon |  | [wiki](https://starwars.fandom.com/wiki/GK-5_sentry_droid) |
| GK-600 guardian droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GK-600_guardian_droid) |
| Gladiator droid | Class four |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Gladiator_droid) |
| GLD-M General Labor Droid/Mining | Mining | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GLD-M_General_Labor_Droid/Mining) |
| GNK power droid | Power droid | Industrial Automaton |  | Galactic Republic | Legends | GNK gonk (KotOR + OuterRim) | [wiki](https://starwars.fandom.com/wiki/GNK_power_droid/Legends) |
| GNK-series power droid | Power droid / Class two | Industrial Automaton |  | Galactic Republic; Alliance to Restore the Republic; Scourge (As a vessel); New Republic | canon | GNK gonk (KotOR + OuterRim) | [wiki](https://starwars.fandom.com/wiki/GNK-series_power_droid) |
| Goliath Lifter | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Goliath_Lifter) |
| Gorax Hunt Droid |  |  |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Gorax_Hunt_Droid) |
| GP-2 medical droid | Medical droid |  |  | Galactic Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/GP-2_medical_droid) |
| Grapple droideka | Battle droid | Colicoids |  | Trade Federation | canon | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Grapple_droideka) |
| Grenade droid | Battle droid |  |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Grenade_droid) |
| Grenadier Droid | Battle |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Grenadier_Droid) |
| Grenadier Droid (Cloud City) | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Grenadier_Droid_%28Cloud_City%29) |
| Grievous Battle Droid | Battle droid | Baktoid Combat Automata |  | Baktoid Combat Automata | canon |  | [wiki](https://starwars.fandom.com/wiki/Grievous_Battle_Droid) |
| GT astromech droid | Class two droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/GT_astromech_droid) |
| GT-09 Mobile Repair Unit | Maintenance droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/GT-09_Mobile_Repair_Unit) |
| GT-13 Maintenance Response Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GT-13_Maintenance_Response_Droid) |
| GT-33 Repair Drone | Maintenance droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/GT-33_Repair_Drone) |
| GT-series construction droid | Construction droid / Class five droid | Veril Line Systems |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GT-series_construction_droid) |
| GTAW welding droid | Welding droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GTAW_welding_droid) |
| GU-series Guardian police droid | Class four | Cybot Galactica; SoroSuub Corporation | retired Post&ndash;Clone Wars | Galactic Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/GU-series_Guardian_police_droid) |
| Guard droid | Class four |  |  | Nihil | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Guard_droid) |
| Guardian (Tendrando Arms) | Battle | Tendrando Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Guardian_%28Tendrando_Arms%29) |
| Guardian Mark II Droid | Security droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Guardian_Mark_II_Droid) |
| Guardian NS-55 Enforcer Droid | Security droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Guardian_NS-55_Enforcer_Droid) |
| Gulper (droid) | Security |  |  | Great Heep | canon |  | [wiki](https://starwars.fandom.com/wiki/Gulper_%28droid%29) |
| GV/3-series guardian droid | Guardian droid / Fourth degree | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GV/3-series_guardian_droid) |
| GX1-series battle droid | Battle droid | Trang Robotics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/GX1-series_battle_droid) |
| GXR-7 command droid | Battle droid |  | destroyed 3643 BBY, the Brentaal Star | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/GXR-7_command_droid) |
| GXR-7 Sentinel | Battle droid / Class four droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/GXR-7_Sentinel) |
| GY-I information analysis droid | Information analysis droid / Class 1 | Cybot Galactica |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/GY-I_information_analysis_droid) |
| Gyrowheel 1.42.08-series recycling droid | Recycling droid | Veril Line Systems |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Gyrowheel_1.42.08-series_recycling_droid) |
| H-1ME battle mechanic droid | maintenance droid / Class two droid | Intertran Systems |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/H-1ME_battle_mechanic_droid) |
| H4-5D Heavy Labor Droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/H4-5D_Heavy_Labor_Droid) |
| Hand of doom | Battle droid |  |  | HK-47's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/Hand_of_doom) |
| Harvester (Confederacy of Independent Systems) | Droid walker / Class three droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Harvester_%28Confederacy_of_Independent_Systems%29) |
| Harvester droid | Agricultural |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Harvester_droid) |
| Haxion Brood Bounty Droid | Battle droid |  |  | Haxion Brood | canon |  | [wiki](https://starwars.fandom.com/wiki/Haxion_Brood_Bounty_Droid) |
| Hazmat droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hazmat_droid) |
| HD-234-C | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/HD-234-C) |
| HE-2 Arbiter Droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/HE-2_Arbiter_Droid) |
| Heavy Battle Droid | Battle droid |  |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Heavy_Battle_Droid) |
| Heavy Guardian | Espionage droid; Security droid |  |  | G0-T0 | canon |  | [wiki](https://starwars.fandom.com/wiki/Heavy_Guardian) |
| Heavy loader droid | Loader droid / Class five droid | JLD Mechanicals Consortium |  | Plazir-15 government; Resistance; Droid Depot | canon |  | [wiki](https://starwars.fandom.com/wiki/Heavy_loader_droid) |
| Heavy Tactical Fighting Unit | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Heavy_Tactical_Fighting_Unit) |
| Hermit crab droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hermit_crab_droid) |
| Hired gun droid | Enforcer droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hired_gun_droid) |
| HK Guardian Droid | Security |  |  |  | canon | HK-series (KotOR + OuterRim) | [wiki](https://starwars.fandom.com/wiki/HK_Guardian_Droid) |
| HK-130 | Sentry droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/HK-130) |
| HK-51 series assassin droid | Assassin droid / Class four droid | Czerka Corporation | 3668 BBY | Sith Empire; Galactic Republic; Eternal Alliance; GenoHaradan | canon |  | [wiki](https://starwars.fandom.com/wiki/HK-51_series_assassin_droid) |
| HK-77 assassin droid | assassin droid / Class four droid |  |  | Confederacy of Independent Systems; HK-47's Droid Army; Various third parties | canon |  | [wiki](https://starwars.fandom.com/wiki/HK-77_assassin_droid) |
| HK-87 assassin droid | Assassin droid | Czerka corporation |  | Galactic Empire; Imperial Remnant; Droid Gotra; The Twins | canon |  | [wiki](https://starwars.fandom.com/wiki/HK-87_assassin_droid) |
| HK-model gladiator droid | Assassin droid; Gladiator droid |  |  | Galactic Empire; Scourge (as a vessel); Imperial Remnant | canon |  | [wiki](https://starwars.fandom.com/wiki/HK-model_gladiator_droid) |
| HK-series assassin droid | Assassin; Protocol |  |  |  | canon | HK-series (KotOR + OuterRim) | [wiki](https://starwars.fandom.com/wiki/HK-series_assassin_droid) |
| HKB-3 hunter-killer droid | Battle droid / Class four droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/HKB-3_hunter-killer_droid) |
| HL-117 hover loader droid | Loader |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/HL-117_hover_loader_droid) |
| HL-444 hover loader | Labor droid / Class five droid | Arakyd Industries |  | Galactic Republic *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/HL-444_hover_loader) |
| HMOR homing droid | Homing droid / Class five droid | Imperial Department of Military Research |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/HMOR_homing_droid) |
| HN-TR Assassin/Combat Droid Prototype | Assassin droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/HN-TR_Assassin/Combat_Droid_Prototype) |
| Holgorian IM-220 | Maintenance droid |  |  | Je'daii Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Holgorian_IM-220) |
| Hollis-series steward droid | Service droid | Automata Galactica |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Hollis-series_steward_droid) |
| Holo-drone |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Holo-drone) |
| Holobug | Surveillance and listening |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Holobug) |
| Holocam E | Cam droid | Trang Robotics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Holocam_E) |
| Holodroid | Training *(Legends)* |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Holodroid) |
| Hologlide J57 cam droid | Cam | Industrial Automaton *(Legends)* |  | Podracing *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Hologlide_J57_cam_droid) |
| Homestead droid | Specialized labor |  |  | Saponza's Gang | canon |  | [wiki](https://starwars.fandom.com/wiki/Homestead_droid) |
| Homework Correction Droid | Educational |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Homework_Correction_Droid) |
| Homing droid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Homing_droid) |
| Horseshoe droid |  |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Horseshoe_droid) |
| Hospitality droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hospitality_droid) |
| Hoth sentry droid | Droid tank |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Hoth_sentry_droid) |
| Hound-W2 SPD | Security | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hound-W2_SPD) |
| House Paramexor Squire Armorer Droid | Armorer droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/House_Paramexor_Squire_Armorer_Droid) |
| Housekeeping droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Housekeeping_droid) |
| Hover cannon | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hover_cannon) |
| Hover Droid (large) | Class four droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hover_Droid_%28large%29) |
| Hover Droid (small) | Class four droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hover_Droid_%28small%29) |
| Hover guard | Sentry droid |  |  | Fromm Gang | canon |  | [wiki](https://starwars.fandom.com/wiki/Hover_guard) |
| HR-02 Omni Droid |  | Galactic Solutions Industries |  | Galactic Solutions Industries | canon |  | [wiki](https://starwars.fandom.com/wiki/HR-02_Omni_Droid) |
| HT drone | Training / Gladiatorial drone | Rodian D-Tec |  | Rodia; Bounty-hunting guilds; Planetary militias; Police academies | canon |  | [wiki](https://starwars.fandom.com/wiki/HT_drone) |
| Hubdroid | Security |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Hubdroid) |
| Human replica droid | Class four | LeisureMech Enterprises |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Human_replica_droid) |
| Human-droid relations specialist |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Human-droid_relations_specialist) |
| Hunter droid | Assassin droid |  |  | Galactic Empire; Sith | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter_droid) |
| Hunter droid/LEGO | Assassin |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter_droid/LEGO) |
| Hunter killer droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter_killer_droid) |
| Hunter-killer droid | Security droid |  |  | Ikkrukk's government | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter-killer_droid) |
| Hunter-Killer probot | Combat probe; Droid vehicle | Arakyd Industries |  | Galactic Empire; Dark Empire; New Republic (reprogrammed) | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter-Killer_probot) |
| Hunter-killer war droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter-killer_war_droid) |
| Hunter-Seeker droid | Droid starfighter | Colicoid Creation Nest |  | Trade Federation; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter-Seeker_droid) |
| Hunter/killer droid | Battle |  |  | Xucphra Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Hunter/killer_droid) |
| Hutt Guard Droid | Security droid |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/Hutt_Guard_Droid) |
| Hutt security droid | Security droid |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/Hutt_security_droid) |
| Hutt war droid | Battle |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/Hutt_war_droid) |
| HV-7 | Loader droid |  |  | Morgan Elsbeth's forces | canon |  | [wiki](https://starwars.fandom.com/wiki/HV-7) |
| HV-7 loading droid | Labor droid / Class 5 | Baktoid Industrial Systems |  | Mon Calamari Shipyards | canon |  | [wiki](https://starwars.fandom.com/wiki/HV-7_loading_droid) |
| HVAC droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/HVAC_droid) |
| HXZ-1 Immobilizer-series police droid | Fourth degree | Cybot Galactica |  | Police and civilian use | canon |  | [wiki](https://starwars.fandom.com/wiki/HXZ-1_Immobilizer-series_police_droid) |
| Hydroponics droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Hydroponics_droid) |
| I-10 Probe Droid | Battle droid |  |  | Rak'qua | canon |  | [wiki](https://starwars.fandom.com/wiki/I-10_Probe_Droid) |
| I-8 Black Widow | Security droid |  |  | Rak'qua | canon |  | [wiki](https://starwars.fandom.com/wiki/I-8_Black_Widow) |
| I-82 intel droid | Spy |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/I-82_intel_droid) |
| I-C2 Civil-Industrial Droid | Construction droid | Veril Line Systems *(Legends)* |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/I-C2_Civil-Industrial_Droid) |
| I-C4a combat construction droid | Construction droid | Veril Line Systems |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/I-C4a_combat_construction_droid) |
| I2-CG droid | Class two *(Legends)* |  |  | Galactic Empire *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/I2-CG_droid) |
| I2AM | Astromech | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/I2AM) |
| I2F series manufacturing droid | Industrial droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/I2F_series_manufacturing_droid) |
| I2F-5 | General labor |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/I2F-5) |
| I2F-73 | Loader |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/I2F-73) |
| IA-82 Artillery Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/IA-82_Artillery_Droid) |
| IC-360 camera droid | Cam droid |  |  | Star Tours | canon |  | [wiki](https://starwars.fandom.com/wiki/IC-360_camera_droid) |
| IC-M General Utility Droid | Cleaning droid | Cybot Galactica |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/IC-M_General_Utility_Droid) |
| ID-75 Heavy Assault Droid | Battle |  |  | Ayor-v9 | canon |  | [wiki](https://starwars.fandom.com/wiki/ID-75_Heavy_Assault_Droid) |
| ID-75 Heavy Construction Droid | Construction droid | Ayor-v9 |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ID-75_Heavy_Construction_Droid) |
| ID-75 Heavy Mining Droid | Mining droid | Ayor-v9 |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ID-75_Heavy_Mining_Droid) |
| ID10 seeker droid | Seeker |  |  | Galactic Empire; Alliance to Restore the Republic; New Republic; Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/ID10_seeker_droid) |
| ID9 seeker droid | Seeker / Class two droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ID9_seeker_droid) |
| IG drone | IG-series |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/IG_drone) |
| IG lancer droid | Battle droid | Phlut Design Systems |  | InterGalactic Banking Clan; Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IG_lancer_droid) |
| IG-1 | Assassin droid / Class 4 |  |  | Project Phlutdroid | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-1) |
| IG-100 MagnaGuard | Assassin droid; Battle droid; Bodyguard droid | Holowan Mechanicals |  | Confederacy of Independent Systems; Infinite Coil; Bedlam Raiders; Scourge (as a vessel) | canon (+Legends) | MagnaGuard (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/IG-100_MagnaGuard) |
| IG-106 assassin droid | Assassin droid | Holowan Mechanicals |  | Lok slicers | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-106_assassin_droid) |
| IG-110 lightsaber droid | Battle; IG-series | Holowan Mechanicals |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-110_lightsaber_droid) |
| IG-227 Hailfire-class droid tank | Droid tank | Haor Chall Engineering Corporation | By 33 BBY | InterGalactic Banking Clan; Confederacy of Independent Systems; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-227_Hailfire-class_droid_tank) |
| IG-86 sentinel droid | Assassin droid; Sentry droid | Holowan Mechanicals |  | InterGalactic Banking Clan; Hutt Clan; Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IG-86_sentinel_droid) |
| IG-88 assassin droid | Assassin droid; War droid | Holowan Laboratories *(Legends)* | Shortly after the Clone Wars | IG-88's Droid Army; Zann Consortium; House of Thul *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IG-88_assassin_droid) |
| IG-97 battle droid | Battle droid | Holowan Mechanicals |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-97_battle_droid) |
| IG-RM bodyguard and enforcer droid | Security droid; Assassin droid; Bodyguard droid / Class 4 | Holowan Laboratories |  | Broken Horn Syndicate; Galactic Empire; Mining Guild | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-RM_bodyguard_and_enforcer_droid) |
| IG-series | Assassin droid; Bodyguard droid / Fourth | Holowan Laboratories |  | Holowan Laboratories; InterGalactic Banking Clan; Confederacy of Independent Systems; Hutt Clans | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IG-series) |
| IG-series assassin droid | Assassin; IG-series |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/IG-series_assassin_droid) |
| Illumi-droid | Light |  |  | Confederacy of Independent Systems; Preigo's Traveling World of Wonder | canon |  | [wiki](https://starwars.fandom.com/wiki/Illumi-droid) |
| IM series | Security droid | Droid Security Systems |  | Spaceport THX1138 | canon |  | [wiki](https://starwars.fandom.com/wiki/IM_series) |
| IM-6 Battlefield Medical Droid | Medical droid / Class one droid | Cybot Galactica |  | Galactic Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IM-6_Battlefield_Medical_Droid) |
| IMG-099 Imperial Mark IV patrol droid | Sentry | Imperial Department of Military Research |  | Galactic Empire; Thrawn's forces | canon |  | [wiki](https://starwars.fandom.com/wiki/IMG-099_Imperial_Mark_IV_patrol_droid) |
| Imperial anti-security device | Combat probe |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_anti-security_device) |
| Imperial assassin droid | Assassin |  |  | Imperial Remnant | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_assassin_droid) |
| Imperial C-series war droid | War droid / Class four droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_C-series_war_droid) |
| Imperial construction droid | Construction droid |  |  | Galactic Empire; Scourge (As a vessel) | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_construction_droid) |
| Imperial Defense Droid | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_Defense_Droid) |
| Imperial espionage droid | Espionage droid | Cybot Galactica |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_espionage_droid) |
| Imperial loader droid | Labor droid |  |  | Galactic Empire; Imperial Remnant; Lumini Pirates | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_loader_droid) |
| Imperial Mark IV Sentinel Droid | Security droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_Mark_IV_Sentinel_Droid) |
| Imperial medical droid | Medical droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_medical_droid) |
| Imperial nanny droid | Medical droid; Nanny droid |  |  | Death Watch; Galactic Republic; Kaminoan government; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_nanny_droid) |
| Imperial Police Droid | Police droid |  |  | The Corner Shop; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_Police_Droid) |
| Imperial Ravager Droid | Droid walker |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_Ravager_Droid) |
| Imperial Reconnaissance Droid | Class four |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_Reconnaissance_Droid) |
| Imperial spider droid | Battle droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_spider_droid) |
| Imperial training droid | Training droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_training_droid) |
| Imperial warbot | Battle |  |  | Galactic Empire; Kligson's faction | canon |  | [wiki](https://starwars.fandom.com/wiki/Imperial_warbot) |
| IN-4 information droid | Information droid / Class one droid | Veril Line Systems |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/IN-4_information_droid) |
| Incinerator war droid | Battle droid | Galactic Empire |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Incinerator_war_droid) |
| Incubation droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Incubation_droid) |
| Indoctrination droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Indoctrination_droid) |
| Industrial droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Industrial_droid) |
| Industrial Site Guard Droid MC-1K | Security droid / Class four droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Industrial_Site_Guard_Droid_MC-1K) |
| Inert-screen load shifter | Loader |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Inert-screen_load_shifter) |
| Inferno firefighting robo | Firefighter droid | Corporate Sector Authority |  | Corporate Sector Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/Inferno_firefighting_robo) |
| Infiltrator demolition droid | Demolition droid | LIN Demolitionmech | 21 BBY | Confederacy of Independent Systems; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Infiltrator_demolition_droid) |
| Infiltrator probe droid | Probe droid | Arakyd Industries/Imperial technicians |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Infiltrator_probe_droid) |
| Information cataloging droid | Specialized labor | Kalibac Industries |  | Mid Rim Lending Network | canon |  | [wiki](https://starwars.fandom.com/wiki/Information_cataloging_droid) |
| Information retrieval droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Information_retrieval_droid) |
| Information-collating droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Information-collating_droid) |
| INS-444 | Maintenance droid / Class five | Publitechnic |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/INS-444) |
| INS-444 window installation droid | Window installation droid / Class five droid | Publictechnic |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/INS-444_window_installation_droid) |
| Internal systems probe droid | Probe droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Internal_systems_probe_droid) |
| Interrogation droid | Class four |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Interrogation_droid) |
| Intruder (assassin droid) | Assassin droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Intruder_%28assassin_droid%29) |
| Inventory droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Inventory_droid) |
| IR-15 Mobile Security Platform | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-15_Mobile_Security_Platform) |
| IR-18 Security Response Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-18_Security_Response_Droid) |
| IR-22 Security Response Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-22_Security_Response_Droid) |
| IR-3K Cloaked Guard Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-3K_Cloaked_Guard_Droid) |
| IR-45 Eradicator Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-45_Eradicator_Droid) |
| IR-52 Airborne Assault Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-52_Airborne_Assault_Droid) |
| IR-5B Stealth Security Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-5B_Stealth_Security_Droid) |
| IR-60 Aerial Commando Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-60_Aerial_Commando_Droid) |
| IR-68 Precision Combat Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-68_Precision_Combat_Droid) |
| IR-70 Tactical Marksman Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-70_Tactical_Marksman_Droid) |
| IR-82 Impulse Combat Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-82_Impulse_Combat_Droid) |
| IR-89 Armored Assault Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-89_Armored_Assault_Droid) |
| IR-8K Covert Assassin Droid | Assassin droid |  |  | The Shroud's syndicate | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-8K_Covert_Assassin_Droid) |
| IR-9X Replicator Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/IR-9X_Replicator_Droid) |
| Irrigation droid | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Irrigation_droid) |
| ISB-120 | Interrogation | MerenData |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ISB-120) |
| ISF-E4 Eliminator Droid | Battle |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ISF-E4_Eliminator_Droid) |
| Isotope-5 droid | Battle droid |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/Isotope-5_droid) |
| ISS-944 Power Droid | Combat-prepared power droid |  | destroyed 3643 BBY, Emperor's Glory | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ISS-944_Power_Droid) |
| IT-000 interrogator droid | Interrogation droid / Class 4 | First Order Department of Military Research |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-000_interrogator_droid) |
| IT-1 | Interrogation |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-1) |
| IT-3 Interrogator | Interrogation droid |  |  | Galactic Empire; Imperial Remnant | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-3_Interrogator) |
| IT-4 Warning Droid | Assassin droid |  |  | Rak'qua | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-4_Warning_Droid) |
| IT-O 26 Interrogation Droid | Interrogation |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-O_26_Interrogation_Droid) |
| IT-O interrogation droid | Interrogator droid | Imperial Department of Military Research |  | Galactic Empire; Ubrik Adelhard's Imperial remnant; New Republic; Imperial Remnant | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IT-O_interrogation_droid) |
| IT-S00.2 medical droid | Medical droid |  |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-S00.2_medical_droid) |
| IT-series |  | Uffel droid community |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-series) |
| IT-series interrogation droid | Interrogation |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-series_interrogation_droid) |
| IT-series utility droid | Maintenance droid | Duwani Mechanical Products |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/IT-series_utility_droid) |
| IW-37 pincer loader droid | Labor droid / Class 5 | Cybot Galactica |  | Galactic Republic; Morgan Elsbeth's forces | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/IW-37_pincer_loader_droid) |
| IX-6 heavy combat droid | Battle droid / Class four droid | Roche Hive Mechanical Apparatus Design and Construction Activity for Those Who Need the Hive's Machines |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/IX-6_heavy_combat_droid) |
| J-1 proton cannon | Droid artillery |  | c. 21 BBY | Techno Union; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/J-1_proton_cannon) |
| J4-SN Chef Droid | Cooking droid |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/J4-SN_Chef_Droid) |
| J4X droid | J4X droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/J4X_droid) |
| J8O soldier droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/J8O_soldier_droid) |
| J9 worker drone | Woker droid | Roche Hive Mechanical Apparatus Design and Construction Activity for Those Who Need the Hive's Machines |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/J9_worker_drone) |
| JC series pilot droid | Pilot | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JC_series_pilot_droid) |
| JD series |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JD_series) |
| Je'daii droid sentry | Sentry |  |  | Je'daii Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Je%27daii_droid_sentry) |
| Jedi assassin droid | Assassin droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Jedi_assassin_droid) |
| Jedi droid | Jedi droid |  |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Jedi_droid) |
| Jedi security droid | Security droid |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Jedi_security_droid) |
| Jedi training droid | Holodroid; Training | Upgrades and different models made by Kazdan Paratus *(Legends)* |  | Jedi Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Jedi_training_droid) |
| JJH2 model | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JJH2_model) |
| JK series droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JK_series_droid) |
| JK-13 security droid | Security droid | Cestus Cybernetics |  | Crime lords; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/JK-13_security_droid) |
| JL series droid | Security | Cestus Cybernetics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JL_series_droid) |
| JMM assassin droid | Assassin droid / Fourth-degree droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JMM_assassin_droid) |
| JN-66 analysis droid | Analysis droid / Class one | Cybot Galactica |  | Jedi Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/JN-66_analysis_droid) |
| JR series |  | Publictechnic |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JR_series) |
| JR-4 Recon Droid | Recon droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JR-4_Recon_Droid) |
| JR-8 series maintenance droid | Cleaning droid | Publictechnic |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JR-8_series_maintenance_droid) |
| JTR cleaning droid | Cleaning | SoroSuub Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JTR_cleaning_droid) |
| JU-9 Juggernaut War Droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JU-9_Juggernaut_War_Droid) |
| Juggernaut war droid | Battle droid | Duwani Mechanical Products | 4800 BBY – retired 4015 BBY | Galactic Republic; HK-01's droid army; Czerka Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Juggernaut_war_droid) |
| JV-Z1/D butler droid | Butler droid | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JV-Z1/D_butler_droid) |
| JV-Z1/S DataBank Droid | Class one |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/JV-Z1/S_DataBank_Droid) |
| K-1B | Medical |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/K-1B) |
| K-9 series hunting-and-tracking droid | Class four | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/K-9_series_hunting-and-tracking_droid) |
| K-series | Astromech |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/K-series) |
| K-series droid |  | J-6 | By 229 BBY | Aricho's resistance force | canon |  | [wiki](https://starwars.fandom.com/wiki/K-series_droid) |
| K-Series spaceport control droid | Spaceport control droid / Class three droid | Industrial Automaton |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/K-Series_spaceport_control_droid) |
| K-X12 probe droid | Probe | MerenData |  |  | canon | K-X12 probe (KotOR) | [wiki](https://starwars.fandom.com/wiki/K-X12_probe_droid) |
| K1-RF workbench droid | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/K1-RF_workbench_droid) |
| K3 security droid | Security droid | Rim Securities |  | Vanguard Axis | canon |  | [wiki](https://starwars.fandom.com/wiki/K3_security_droid) |
| K3-I Buzzer Droid | Battle droid |  |  | Rak'qua | canon |  | [wiki](https://starwars.fandom.com/wiki/K3-I_Buzzer_Droid) |
| K4 security droid | Security droid / Class four droid | Rim Securities |  | Private corporations; Local governments; Crime lords; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/K4_security_droid) |
| K5 Enforcer Droid | Security | Rim Securities |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/K5_Enforcer_Droid) |
| K7 "Black Dagger" Security Droid | Security droid | Rim Securities |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/K7_%22Black_Dagger%22_Security_Droid) |
| Kamino security droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Kamino_security_droid) |
| Kaminoan droid | Labor droid |  |  | Grand Army of the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Kaminoan_droid) |
| Kaminoan training droid | Training droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Kaminoan_training_droid) |
| Kaon Sentinel Mk. III | Class four droid |  |  | Kaon Security | canon |  | [wiki](https://starwars.fandom.com/wiki/Kaon_Sentinel_Mk._III) |
| Kesselian spice-mining droid | Mining droid / Class five droid |  |  | Spice Mines of Kessel | canon |  | [wiki](https://starwars.fandom.com/wiki/Kesselian_spice-mining_droid) |
| Khepi guardian droid | Sentry droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Khepi_guardian_droid) |
| Killdroid | Sentry droid |  |  | Nihil | canon |  | [wiki](https://starwars.fandom.com/wiki/Killdroid) |
| KL-2B Battle Droid | Battle droid / Class four droid |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/KL-2B_Battle_Droid) |
| KLR series combat droid | Combat droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/KLR_series_combat_droid) |
| KM1 mining droid | Mining droid / Class five droid | Duwani Mechanical Products |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/KM1_mining_droid) |
| Kol Huro combat droid | Combat Droid | Kol Huro system factories | 44 BBY | Mustag Olus | canon |  | [wiki](https://starwars.fandom.com/wiki/Kol_Huro_combat_droid) |
| KPR security droid | Security droid | Lerrimore Droids *(Legends)* |  | Lars family | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/KPR_security_droid) |
| Krath war droid | Battle droid / Class four droid | Cinnagar foundries *(Legends)* |  | Krath *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Krath_war_droid) |
| Krayn search droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Krayn_search_droid) |
| KT-series | Astromech droid / Class two droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/KT-series) |
| KT8 cooking unit | Cooking |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/KT8_cooking_unit) |
| KW traffic controller | Spaceport control droid / Class 3 | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/KW_traffic_controller) |
| KX-2 unit | Security droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/KX-2_unit) |
| KX-series security droid | Security droid / Fourth-degree droid | Arakyd Industries |  | Galactic Empire; Alliance to Restore the Republic (appropriated); Second Revelation; Droid uprising | canon | KX-series (OuterRim) | [wiki](https://starwars.fandom.com/wiki/KX-series_security_droid) |
| KXFO-series security droid | Security droid | Arakyd Industries |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/KXFO-series_security_droid) |
| Kyrotech Blademaster X-260 | Assassin | Kyrotech Corporate Combine |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Kyrotech_Blademaster_X-260) |
| L-1g general purpose droid | Service droid; Tactical droid; Worker droid / Class four droid |  |  | Alliance to Restore the Republic; Pyke Syndicate; Scourge (As a vessel); Scrapper Guild | canon |  | [wiki](https://starwars.fandom.com/wiki/L-1g_general_purpose_droid) |
| L2 Base Labor Droid |  | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/L2_Base_Labor_Droid) |
| L7 logician droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/L7_logician_droid) |
| L8O protocol droid | Protocol droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/L8O_protocol_droid) |
| Labor droid | Class five |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Labor_droid) |
| Land-clearing droid | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Land-clearing_droid) |
| Larceny droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Larceny_droid) |
| Laundry droid | Cleaning droid |  |  | First Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Laundry_droid) |
| LB-series bulk-loading droid | Bulk-loading droid | Kellenech Technologies |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LB-series_bulk-loading_droid) |
| LB-series courier droid | Courier droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LB-series_courier_droid) |
| LC "hunting droid" | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LC_%22hunting_droid%22) |
| LC-24 fire droid | Fire droid |  |  | Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/LC-24_fire_droid) |
| LC-92 antagonist | Security droid | Stonewall Labs |  | Stonewall Labs | canon |  | [wiki](https://starwars.fandom.com/wiki/LC-92_antagonist) |
| LE manifest droid | Manifest droid / Class three droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LE_manifest_droid) |
| LE-series droid | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LE-series_droid) |
| LE-series repair droid | Repair droid / Class two droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LE-series_repair_droid) |
| Legal-analyst droid | Analysis droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Legal-analyst_droid) |
| LEP servant droid | Service droid / Class three droid | Coachelle Automata |  | Galactic Republic; Confederacy of Independent Systems | Legends |  | [wiki](https://starwars.fandom.com/wiki/LEP_servant_droid/Legends) |
| LEP-series service droid | Service droid / Class three | Coachelle Automata |  | Confederacy of Independent Systems; Galactic Republic; Galactic Empire; Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/LEP-series_service_droid) |
| LGR series cooking droid | Cooking droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LGR_series_cooking_droid) |
| Librarian droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Librarian_droid) |
| Light droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Light_droid) |
| Line droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Line_droid) |
| Linguistics droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Linguistics_droid) |
| LM-432 crab droid | Droid tank / Fourth-degree droid | Techno Union |  | Techno Union; Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/LM-432_crab_droid) |
| Load-lifter (model) | Loader | Drendan |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Load-lifter_%28model%29) |
| Loader Droid | Loader droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Loader_Droid) |
| Loadlifter droid (model) | Labor droid / Class 5 |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Loadlifter_droid_%28model%29) |
| Logistics droid |  |  |  | Jedi Order; Chandrila Star Line; Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/Logistics_droid) |
| LOM-series protocol droid | Protocol droid / Class three | Industrial Automaton |  | Galactic Empire; Hutt Clan; Bounty Hunters' Guild; T'onga's crew | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/LOM-series_protocol_droid) |
| LON-29 battle droid commander | Battle droid / Class four droid | Balmorran Arms |  | Galactic Federation of Free Alliances; Darth Krayt's Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/LON-29_battle_droid_commander) |
| Longvision LV-38 spotter/probe droid | Probe droid | Loratus Manufacturing |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Longvision_LV-38_spotter/probe_droid) |
| Lothal astromech droid | Astromech droid | Lothal Logistics Limited |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Lothal_astromech_droid) |
| Lovolol cleaning droid | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Lovolol_cleaning_droid) |
| LOW-MO | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LOW-MO) |
| LR-57 combat droid | Battle droid; Sentinel droid | Retail Caucus |  | Retail Caucus; Confederacy of Independent Systems | Legends | LR-57 (JDS) | [wiki](https://starwars.fandom.com/wiki/LR-57_combat_droid/Legends) |
| LR-57 combat/retail droid | Battle droid | Retail Caucus |  | Retail Caucus; Confederacy of Independent Systems | canon | LR-57 (JDS) | [wiki](https://starwars.fandom.com/wiki/LR-57_combat/retail_droid) |
| LRD-series envoy droid | Protocol droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LRD-series_envoy_droid) |
| LSx-series slicer droid | Spy | Loronar Corporation |  | Galactic Empire; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/LSx-series_slicer_droid) |
| Lubrication droid | Industrial droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Lubrication_droid) |
| Lumber droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Lumber_droid) |
| LV3 |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/LV3) |
| LV8-series guard droid | Security droid / Class four droid | Baktoid Industrial Systems |  | Fel Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/LV8-series_guard_droid) |
| M-2 mining probe droid | Mining; Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/M-2_mining_probe_droid) |
| M-3PO military protocol droid | Military protocol droid / Class three | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/M-3PO_military_protocol_droid) |
| M2-AX Patrol Droid | Sentry |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/M2-AX_Patrol_Droid) |
| M3-M1 Medical Droid | Medical droid | Starfront Health Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/M3-M1_Medical_Droid) |
| M38-series explorer droid | Exploration droid / Class two droid | LesTech |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/M38-series_explorer_droid) |
| M4-3B Security Droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/M4-3B_Security_Droid) |
| M4-series Messenger Droid | Messenger droid | Cybot Galactica |  | Alliance to Restore the Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/M4-series_Messenger_Droid) |
| M4-T3 Astromech Droid | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/M4-T3_Astromech_Droid) |
| M4m | Courier and messenger | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/M4m) |
| MA-6 Frontline Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MA-6_Frontline_Droid) |
| MA-9 Frontline Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MA-9_Frontline_Droid) |
| MA-B0 cargo lifter droid | Loader |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MA-B0_cargo_lifter_droid) |
| Machinist Droid MC-12 | Labor droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Machinist_Droid_MC-12) |
| Magnobore |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Magnobore) |
| Maintenance droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Maintenance_droid) |
| Maintenance droid (Mos Eisley) | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Maintenance_droid_%28Mos_Eisley%29) |
| Maintenance Droid M2-T2 | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Maintenance_Droid_M2-T2) |
| Malagarr battle droid | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Malagarr_battle_droid) |
| Manifest droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Manifest_droid) |
| Manta droid subfighter | Droid vehicle; Submersible | Haor Chall Engineering |  | Trade Federation; Quarren Isolation League; Confederacy of Independent Systems; Great Houses of Serenno | canon |  | [wiki](https://starwars.fandom.com/wiki/Manta_droid_subfighter) |
| Manta droid submarine | Droid vehicle; Submersible | Haor Chall Engineering Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Manta_droid_submarine) |
| Mark I assault droid | Battle droid | Czerka Arms |  | Czerka Arms; Galactic Republic; Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_I_assault_droid) |
| Mark I training droid | Training droid |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_I_training_droid) |
| Mark II assault droid | Battle droid |  |  | Various | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_II_assault_droid) |
| Mark II assault droid (Cold War) | Training droid |  | By 3643 BBY | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_II_assault_droid_%28Cold_War%29) |
| Mark II reactor drone | Maintenance | Industrial Automaton |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Mark_II_reactor_drone) |
| Mark II War Droid | Battle |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_II_War_Droid) |
| Mark III Combat Droid | Battle droid |  |  | Specialists | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_III_Combat_Droid) |
| Mark III training droid | Training |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_III_training_droid) |
| Mark IV architect droid | Architect droid / Class 3 |  | By 25,020 BBY | Jedi Order; Galactic Republic; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_IV_architect_droid) |
| Mark IV assault droid | Battle droid | Czerka Arms |  | Czerka Arms; Galactic Republic; Sith Empire; Ahto City Civil Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_IV_assault_droid) |
| Mark IV Decimator Droid | Battle |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_IV_Decimator_Droid) |
| Mark IV Guardian Droid | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_IV_Guardian_Droid) |
| Mark IV sentry droid | Sentry droid / Class five droid | Imperial Department of Military Research |  | Galactic Empire | Legends |  | [wiki](https://starwars.fandom.com/wiki/Mark_IV_sentry_droid/Legends) |
| Mark IV training droid | Training |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_IV_training_droid) |
| Mark IX Executioner | Assassin droid | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_IX_Executioner) |
| Mark M Guard Droid | Battle droid |  |  | Specialists | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_M_Guard_Droid) |
| Mark One Pistoeka sabotage droid | Sabotage droid |  |  | Mitth'raw'nuruodo | canon | Pistoeka sabotage/buzz droid (JDS) | [wiki](https://starwars.fandom.com/wiki/Mark_One_Pistoeka_sabotage_droid) |
| Mark V Commando Droid | Battle droid |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_V_Commando_Droid) |
| Mark V Enforcer Droid | Battle droid |  |  | Specialists | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_V_Enforcer_Droid) |
| Mark V Temple Guardian Droid | Battle |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_V_Temple_Guardian_Droid) |
| Mark VII "Inquisitor" Series Seeker Droid | Seeker / Class four droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_VII_%22Inquisitor%22_Series_Seeker_Droid) |
| Mark VII gladiator droid | Gladiator droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_VII_gladiator_droid) |
| Mark VIII Enforcer Droid | Battle droid |  |  | Specialists | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_VIII_Enforcer_Droid) |
| Mark VIII Sentinel | Battle droid / Class four droid | Holowan Laboratories |  | Holowan Laboratories | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_VIII_Sentinel) |
| Mark X Executioner droid | Class four | Arakyd Industries *(Legends)* |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Mark_X_Executioner_droid) |
| Mark XI Executioner | Gladiator droid | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark_XI_Executioner) |
| Mark-37 combat droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark-37_combat_droid) |
| Mark-5 assault droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mark-5_assault_droid) |
| Marquee droid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Marquee_droid) |
| Massage droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Massage_droid) |
| Massdroid | Construction |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Massdroid) |
| Mataou Hutt security droid | Security droid |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/Mataou_Hutt_security_droid) |
| Mathematics droid | Class one |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mathematics_droid) |
| MCR-99 reconnaissance droid | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MCR-99_reconnaissance_droid) |
| MCR-X Stealth Recon Probe | Probe droid |  |  | The Shroud's syndicate | canon |  | [wiki](https://starwars.fandom.com/wiki/MCR-X_Stealth_Recon_Probe) |
| MD-0 medical droid | Class one | Industrial Automaton |  | Alliance to Restore the Republic; Galactic Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-0_medical_droid) |
| MD-1 medical droid | Class one | Industrial Automaton |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-1_medical_droid) |
| MD-15C medical droid | Medical droid / Class One |  |  | Resistance; First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-15C_medical_droid) |
| MD-2 medical droid | MD-series medical | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-2_medical_droid) |
| MD-3 medical droid | Class one droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-3_medical_droid) |
| MD-4 medical droid | Class one droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-4_medical_droid) |
| MD-6 medical droid | Medical droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-6_medical_droid) |
| MD-CH1 Droid | Exploration |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-CH1_Droid) |
| MD-S3 | Medical |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MD-S3) |
| MD-series medical droid | Medical droid | Industrial Automaton *(Legends)* |  | First Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/MD-series_medical_droid) |
| MdZ series droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MdZ_series_droid) |
| Mecha-Droid | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mecha-Droid) |
| Mechanized hold-tender | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mechanized_hold-tender) |
| Mechthorian | Security droid | Stonewall Labs |  | Stonewall Labs | canon |  | [wiki](https://starwars.fandom.com/wiki/Mechthorian) |
| MED-47 | Medical droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/MED-47) |
| Media droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Media_droid) |
| Mediator droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mediator_droid) |
| Medical droid | Class one |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Medical_droid) |
| Medical Droid (Sprocket) | Medical droid | Sprocket |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Medical_Droid_%28Sprocket%29) |
| Megadroid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Jabba's criminal empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Megadroid) |
| Memo droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Memo_droid) |
| Memorial droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Memorial_droid) |
| Memory droid | Data storage droid | SoroSuub Corporation |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Memory_droid) |
| Memory-wipe droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Memory-wipe_droid) |
| Mer-9 Protocol Droid | Espionage and infiltration | MerenData |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mer-9_Protocol_Droid) |
| Mercenary sentry droid | Sentry |  |  | Droid Gotra; The Twins | canon |  | [wiki](https://starwars.fandom.com/wiki/Mercenary_sentry_droid) |
| Metalwork droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Metalwork_droid) |
| Metropolis Razer | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Metropolis_Razer) |
| MEV-series medical evacuation droid | 1st-degree Medical droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MEV-series_medical_evacuation_droid) |
| MI-series security droid | Security droid / Class four droid | Holowan Mechanicals |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MI-series_security_droid) |
| Microdroid | Listening device *(Legends)* |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Microdroid) |
| Microdroid listener | Listening device |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Microdroid_listener) |
| MicroMed Droid | Medical |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MicroMed_Droid) |
| Midwife droid | Medical droid |  |  | Polis Massa Base | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Midwife_droid) |
| Military protocol droid | Battle; Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Military_protocol_droid) |
| MILL-247-EE industrial droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MILL-247-EE_industrial_droid) |
| Millicreep | Assassin droid |  |  | Umbaran militia; Confederacy of Independent Systems | Legends |  | [wiki](https://starwars.fandom.com/wiki/Millicreep/Legends) |
| Milvayne Authority drone |  |  |  | Milvayne Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/Milvayne_Authority_drone) |
| Mindscan droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mindscan_droid) |
| Mine-sniffer droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mine-sniffer_droid) |
| Miner droid (Christophsis) | Mining droid |  |  | Confederacy of Independent Systems; Nightsisters | canon |  | [wiki](https://starwars.fandom.com/wiki/Miner_droid_%28Christophsis%29) |
| Miner droid (Eos) | Miner droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Miner_droid_%28Eos%29) |
| Mini-droid |  | Mubo |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mini-droid) |
| Mini-Huvicko/Yuzabi Dowser binary hydromech droid | Hydromech droid | Huvicko/Yuzabi |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mini-Huvicko/Yuzabi_Dowser_binary_hydromech_droid) |
| Mini-Med | Medical | Medtech Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mini-Med) |
| Mining droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Mining_droid) |
| Mining droid Mark II | Mining droid / Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mining_droid_Mark_II) |
| Mining Droid MK3 | Mining droid |  |  | Klegger Corporation; Mensix Mining Company | canon |  | [wiki](https://starwars.fandom.com/wiki/Mining_Droid_MK3) |
| Mining droidnaught | Mining droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Mining_droidnaught) |
| Mining drone | Mining |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Mining_drone) |
| Mining survey droid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mining_survey_droid) |
| Miniprobe | Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Miniprobe) |
| Missile droid | Battle droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Missile_droid) |
| Misting fan | Fan droid | Resistance |  | Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/Misting_fan) |
| MixRMastR | Bartender droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MixRMastR) |
| MK 8001 Attendant Droid | Nanny droid / Class one droid | AccuTronics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK_8001_Attendant_Droid) |
| MK line droid | Protocol droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/MK_line_droid) |
| MK series | Battle droids; Protocol droids |  | c. 21 BBY | Joh's New and Used Droid Emporium | canon |  | [wiki](https://starwars.fandom.com/wiki/MK_series) |
| MK-1 Hazard Droid | Battle droid | Colicoids |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-1_Hazard_Droid) |
| MK-2 Hazard Droid | Battle droid | Colicoids |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-2_Hazard_Droid) |
| MK-3 Hazard Droid | Battle droid | Colicoids |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-3_Hazard_Droid) |
| MK-4 Hazard Droid | Battle droid | Colicoids |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-4_Hazard_Droid) |
| MK-series maintenance droid | maintenance droid / Class two droid | Kalibac Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-series_maintenance_droid) |
| MK-V Heavy Gunner Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-V_Heavy_Gunner_Droid) |
| MK-X Hazard Droid | Battle droid | Colicoids |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MK-X_Hazard_Droid) |
| MMR-9 | Class five | SoroSuub Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MMR-9) |
| MMV security droid | Security droid |  |  | Outer Rim Oreworks | canon |  | [wiki](https://starwars.fandom.com/wiki/MMV_security_droid) |
| MN-2E general maintenance droid | Maintenance droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MN-2E_general_maintenance_droid) |
| MO-Trak | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MO-Trak) |
| Mobile | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mobile) |
| Mobile hold-tender | Class five |  |  | Red Nebula exiles | canon |  | [wiki](https://starwars.fandom.com/wiki/Mobile_hold-tender) |
| Moderator droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Moderator_droid) |
| Monitor Droid TX | Probe droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Monitor_Droid_TX) |
| Mono-WLKR | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Mono-WLKR) |
| Monster droid | Customized multipurpose droid *(Legends)* | Jawas *(Legends)* |  | Galactic Republic; Galactic Empire; New Republic *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Monster_droid) |
| Montoro serving drone | Service |  |  | Mos Espa settlers | canon |  | [wiki](https://starwars.fandom.com/wiki/Montoro_serving_drone) |
| Moon moth espionage droid | Spycam | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Moon_moth_espionage_droid) |
| Mosquito droid | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Mosquito_droid) |
| MR-200 Series minesweeper droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/MR-200_Series_minesweeper_droid) |
| MR-9 housekeeping droid | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MR-9_housekeeping_droid) |
| MRD-39B assassin droid | Assassin droid | Corporate Sector Authority |  | Corporate Sector Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/MRD-39B_assassin_droid) |
| MRK-3 Assassin Prototype | Assassin droid | Chromium Kings |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MRK-3_Assassin_Prototype) |
| MSE series | Repair droid | Rebaxan Columni |  | Galactic Republic; Haddrex Gang; Confederacy of Independent Systems; Separatist holdouts | canon | MSE mouse (OuterRim) | [wiki](https://starwars.fandom.com/wiki/MSE_series) |
| MSE-6 series repair droid | Maintenance droid | Rebaxan Columni |  | Haddrex Gang; Galactic Republic; Confederacy of Independent Systems; Separatist holdouts | canon (+Legends) | MSE-6 mouse (OuterRim) | [wiki](https://starwars.fandom.com/wiki/MSE-6_series_repair_droid) |
| Multi-Environment Mining Droid MEMD-2 | 20,000 credits | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Multi-Environment_Mining_Droid_MEMD-2) |
| Municipal patrol droid Mark I | Sentry | Automata Galactica |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Municipal_patrol_droid_Mark_I) |
| Muscle droid | Security droid |  |  | Fromm Gang; The Great Heep | canon |  | [wiki](https://starwars.fandom.com/wiki/Muscle_droid) |
| Musician droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Musician_droid) |
| Mustafar Droid | Probe droid |  |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Mustafar_Droid) |
| Mustafar panning droid | Mining droid / Class five | Kalibac Industries/Techno Union |  | Techno Union; Tagge Company; Klegger Corporation; Mensix Mining Company | canon |  | [wiki](https://starwars.fandom.com/wiki/Mustafar_panning_droid) |
| MV-33 security droid | Security droid | Tagge Corporation |  | Tagge Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/MV-33_security_droid) |
| MX series droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/MX_series_droid) |
| MX-05 Constructor Droid | Construction droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/MX-05_Constructor_Droid) |
| Myrkr SS-23 | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Myrkr_SS-23) |
| N-101 Nemesis droid | Battle droid | Trang Robotics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/N-101_Nemesis_droid) |
| N2K-V5 Maintenance Droid | Maintenance |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/N2K-V5_Maintenance_Droid) |
| N4-10 Exterminator | Battle droid |  | destroyed 3642 BBY, Foundry | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/N4-10_Exterminator) |
| N5 sentry droid | Security droid; Sentry droid | SoroSuub Corporation |  | Second Revelation; New Republic; Droid Gotra; The Twins | canon |  | [wiki](https://starwars.fandom.com/wiki/N5_sentry_droid) |
| Nanny droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Nanny_droid) |
| Nano-droid | Class five |  |  | Galactic Republic *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Nano-droid) |
| Nav droid |  |  |  | Hutt Clan; Crimson Dawn | canon |  | [wiki](https://starwars.fandom.com/wiki/Nav_droid) |
| NAV-EX | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/NAV-EX) |
| Neimoidian battle droid | Battle |  |  | Trade Federation; Techno Union; Jedi Order (captured); Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Neimoidian_battle_droid) |
| Netdroid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Netdroid) |
| Nightsister service droid | Service |  |  | Nightsisters | canon |  | [wiki](https://starwars.fandom.com/wiki/Nightsister_service_droid) |
| NIL-8 Assassin Droid | Assassin |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/NIL-8_Assassin_Droid) |
| NL-6 courtesy droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/NL-6_courtesy_droid) |
| NM-K reconstitutor | Class five | Techno Union |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/NM-K_reconstitutor) |
| NON unit | Protocol droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/NON_unit) |
| Normtrooper | Battle |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Normtrooper) |
| NP-unit | Servo-droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/NP-unit) |
| NR knockoff | Repair droid / Class 5 | Tredwall | 2 BBY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/NR_knockoff) |
| NR-1100 slicer droid | 2nd-degree Slicer droid | New Republic Department of Research and Development |  | Alliance to Restore the Republic; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/NR-1100_slicer_droid) |
| NR-5 Series Repair Droid | Maintenance droid / Class five droid | Kalibac Industries | 2 BBY | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/NR-5_Series_Repair_Droid) |
| NR-S3 droid | Repair droid |  |  | Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/NR-S3_droid) |
| NS-36 Enforcer Droid | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/NS-36_Enforcer_Droid) |
| NS-7 Guardian Droid | Security droid |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/NS-7_Guardian_Droid) |
| O0-99 Imperial orbital load-lifter | Loader droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/O0-99_Imperial_orbital_load-lifter) |
| Observation droid | Cam |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Observation_droid) |
| Observation droid (Clone Wars) | Probe droid | Arakyd Industries |  | Galactic Republic; Pyke Syndicate; Zygerrian Slave Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Observation_droid_%28Clone_Wars%29) |
| Octoneedle | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Octoneedle) |
| Octuptarra combat tri-droid | Battle droid / Class four droid | Techno Union |  | Confederacy of Independent Systems; Techno Union | Legends |  | [wiki](https://starwars.fandom.com/wiki/Octuptarra_combat_tri-droid/Legends) |
| Octuptarra tri-droid | Battle droid walker / Class four droid | Techno Union |  | Techno Union; Confederacy of Independent Systems; Scourge (As a vessel) | canon |  | [wiki](https://starwars.fandom.com/wiki/Octuptarra_tri-droid) |
| OD-1M Assault Droid | Battle droid | Ayor-v9 |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OD-1M_Assault_Droid) |
| ODX-series protocol droid | Protocol droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ODX-series_protocol_droid) |
| OG-9 homing spider droid | Battle droid / Fourth-degree droid | Baktoid Armor Workshop |  | Commerce Guild; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/OG-9_homing_spider_droid) |
| OHK-99 | Battle droid | Grathan |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/OHK-99) |
| Okara Battle Droid Ax R2 | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Okara_Battle_Droid_Ax_R2) |
| Omniprobe | Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Omniprobe) |
| OOM command battle droid | Battle droid / Fourth-degree droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems; Separatist holdouts; Klik-Klak's droid army | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/OOM_command_battle_droid) |
| OOM pilot battle droid | Battle droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/OOM_pilot_battle_droid) |
| OOM-series battle droid | Battle droid / Class three droid | Baktoid Combat Automata / Baktoid Armor Workshop |  | Trade Federation; Confederacy of Independent Systems; Separatist holdouts; Klik-Klak's droid army | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/OOM-series_battle_droid) |
| OOM-series security droid | Battle droid / Fourth-degree droid | Baktoid Combat Automata |  | Trade Federation; Confederacy of Independent Systems; Ziro the Hutt's criminal organization | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/OOM-series_security_droid) |
| Operator droid |  |  |  | Nawaam's army | canon |  | [wiki](https://starwars.fandom.com/wiki/Operator_droid) |
| Opti-Pod | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Opti-Pod) |
| Opti-STRK | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Opti-STRK) |
| Opticron | Surveillance and listening |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Opticron) |
| OR-B5 Security Droid | Security |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/OR-B5_Security_Droid) |
| Oracle droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Oracle_droid) |
| Orb-Walker | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Orb-Walker) |
| Orbital sensor droid | Surveillance and listening |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Orbital_sensor_droid) |
| Orbot | Protocol droid / Class three droid | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Orbot) |
| Orbot Droid | Battle droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Orbot_Droid) |
| Orchestra droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Orchestra_droid) |
| Ore extraction droid | Mining droid / Fifth-degree droid |  |  | Techno Union | canon |  | [wiki](https://starwars.fandom.com/wiki/Ore_extraction_droid) |
| Ossus Stone Guardian | Security |  |  | Jedi Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Ossus_Stone_Guardian) |
| OT-09 Defender Droid | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-09_Defender_Droid) |
| OT-12 Battle Droid | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-12_Battle_Droid) |
| OT-12 Centurion Droid | Battle droid | Okara Droid Company |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-12_Centurion_Droid) |
| OT-12 Enforcer Droid | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-12_Enforcer_Droid) |
| OT-12 Hazmat Droid | Battle droid | Okara Droid Company |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-12_Hazmat_Droid) |
| OT-12 Pacification Droid | Battle droid | Okara Droid Company |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-12_Pacification_Droid) |
| OT-3 Industrial Repair Droid | Maintenance droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-3_Industrial_Repair_Droid) |
| OT-3 Relay Droid | Probe droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-3_Relay_Droid) |
| OT-5 Repair Droid | Maintenance droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-5_Repair_Droid) |
| OT-7 Assault Droid | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-7_Assault_Droid) |
| OT-7 Patrol Droid | Patrol droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-7_Patrol_Droid) |
| OT-9 Artillery Droid | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-9_Artillery_Droid) |
| OT-9 Sentinel Droid | Security droid | Okara Droid Company |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/OT-9_Sentinel_Droid) |
| Otoga line | Maintenance | Veril Line Systems |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Otoga_line) |
| Otoga-222 maintenance droid | Maintenance droid / Class five droid | Veril Line Systems *(Legends)* |  | Colossus | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Otoga-222_maintenance_droid) |
| Overseer droid (Death Star) | Supervisor droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Overseer_droid_%28Death_Star%29) |
| OX9 | Labor droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/OX9) |
| P-2B Assault Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/P-2B_Assault_Droid) |
| P-series droideka | Battle droid | Colicoid Creation Nest |  | Trade Federation; Confederacy of Independent Systems | canon (+Legends) | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/P-series_droideka) |
| P2 astromech unit | Astromech droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/P2_astromech_unit) |
| P2-series astromech droid | Astromech droid / Class two droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/P2-series_astromech_droid) |
| P2F hostile environment remote | Remote | Haor Chall Engineering Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/P2F_hostile_environment_remote) |
| P4T protocol droid | Protocol droid / Class 3 |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/P4T_protocol_droid) |
| Packager | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Packager) |
| PackTrack 41LT-R | Class five droid | LesTech |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/PackTrack_41LT-R) |
| Page droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Page_droid) |
| PanaRobo |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PanaRobo) |
| Paparazzi droid | Cam |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Paparazzi_droid) |
| Paramedic droid | Medical |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Paramedic_droid) |
| Parasite droid | Spy |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Parasite_droid) |
| Parole droid | Administrative droid |  |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Parole_droid) |
| Patch-in droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Patch-in_droid) |
| Patrol droid (First Order) | Patrol droid / Fourth-degree droid |  |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Patrol_droid_%28First_Order%29) |
| Patrol drone | Sentry |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Patrol_drone) |
| PD-series protocol droid | Protocol droid / Third degree | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PD-series_protocol_droid) |
| Personal assistant droid | Service |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Personal_assistant_droid) |
| Personal Droid | Service | LeisureMech Enterprises |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Personal_Droid) |
| Pest-control droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Pest-control_droid) |
| PG-5 gunnery droid | Gunnery droid / Class two droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/PG-5_gunnery_droid) |
| Phase X sovereign droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Phase_X_sovereign_droid) |
| Physical science droid | Class one |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Physical_science_droid) |
| PI-series medical assistant droid | Medical droid / Class one droid | Arakyd Industries |  | Darth Krayt's Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/PI-series_medical_assistant_droid) |
| Picodroid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Picodroid) |
| Pill droid | Rescue droid; Medical droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Pill_droid) |
| Pilot droid | Class two; Specialized labor |  |  | Trade Federation; Galactic Republic; Confederacy of Independent Systems; Garel Interstellar Excursions | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Pilot_droid) |
| PIP droid | Repair droid | Pui-ui Implement Products |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PIP_droid) |
| PIP/2 systems control droid | Class two | Genetech Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PIP/2_systems_control_droid) |
| Pirate droid | Security |  |  | Pirates of Tarnoonga | canon |  | [wiki](https://starwars.fandom.com/wiki/Pirate_droid) |
| Pistoeka sabotage droid | Sabotage droid | Colicoid Creation Nest |  | Confederacy of Independent Systems; Free Ryloth Movement; Mining Guild; Galactic Empire | canon (+Legends) | Pistoeka sabotage/buzz droid (JDS) | [wiki](https://starwars.fandom.com/wiki/Pistoeka_sabotage_droid) |
| Pitmaster droid |  |  |  | Ronto Roasters | canon |  | [wiki](https://starwars.fandom.com/wiki/Pitmaster_droid) |
| PJ unit | Loader |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PJ_unit) |
| PK-2M mining droid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PK-2M_mining_droid) |
| PK-series worker droid | Labor droid / Class five | Cybot Galactica |  | Trade Federation; Confederacy of Independent Systems; New Republic; Resistance | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/PK-series_worker_droid) |
| PK-Ultra worker droid | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PK-Ultra_worker_droid) |
| PKN-49 worker droid | Labor droid |  |  | Royal Naboo Security Forces | canon |  | [wiki](https://starwars.fandom.com/wiki/PKN-49_worker_droid) |
| Plasma battle droid | Battle droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Plasma_battle_droid) |
| Plasma probe | Class 5 probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Plasma_probe) |
| Plastoid infiltration droid | Battle | Cestus Cybernetics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Plastoid_infiltration_droid) |
| PLNK-series power droid | Power droid / Class two | Industrial Automaton |  | Galactic Republic; Alliance to Restore the Republic; Jabba's criminal empire | canon |  | [wiki](https://starwars.fandom.com/wiki/PLNK-series_power_droid) |
| PO5 entertainment unit | Entertainment droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/PO5_entertainment_unit) |
| Police droid | Security |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Police_droid) |
| Police probe | Cam droid; Probe droid; Police droid / Class four | Arakyd Industries |  | Coruscant Security Force | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Police_probe) |
| Porter droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Porter_droid) |
| Power droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Power_droid) |
| Prison Battle Droid | Battle droid |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Prison_Battle_Droid) |
| Probability droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Probability_droid) |
| Probe droid | Class two |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Probe_droid) |
| Probe Droid DX | Probe droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Probe_Droid_DX) |
| Probe killer | Assassin droid |  |  | Confederacy of Independent Systems; Death Watch | Legends |  | [wiki](https://starwars.fandom.com/wiki/Probe_killer/Legends) |
| Proctor droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Proctor_droid) |
| Programmer droid | Class two |  |  | Pyke Syndicate | canon |  | [wiki](https://starwars.fandom.com/wiki/Programmer_droid) |
| Projector droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Projector_droid) |
| Prospecting droid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Prospecting_droid) |
| Proto-Roller | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Proto-Roller) |
| Protocol Desk-Droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Protocol_Desk-Droid) |
| Protocol droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Protocol_droid) |
| Prototype battle droid | Battle droid | Galen and Curi |  | Radnor; Avon | canon |  | [wiki](https://starwars.fandom.com/wiki/Prototype_battle_droid) |
| Prowler (Imperial) | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Prowler_%28Imperial%29) |
| Prowler 1000 seeker droid | Probe droid / Fourth-degree droid | Arakyd Industries |  | Galactic Republic; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Prowler_1000_seeker_droid) |
| Public relations droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Public_relations_droid) |
| Purifier droid | Security | Unidentified Iokath species |  | Unidentified Iokath species; ARIES | canon |  | [wiki](https://starwars.fandom.com/wiki/Purifier_droid) |
| PX-74 Artillery Droid | Battle |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/PX-74_Artillery_Droid) |
| Pylon Guardian | Battle droid | Gray Secant |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Pylon_Guardian) |
| PZ protocol droid | Protocol droid / Class three | Serv-O-Droid, Inc. |  | Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/PZ_protocol_droid) |
| Q-4 Borer Droid | Mining | Quarren Industrial |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Q-4_Borer_Droid) |
| Q-series droideka | Battle droid | Colicoid Creation Nest |  | Confederacy of Independent Systems | canon (+Legends) | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Q-series_droideka) |
| Q7-series astromech droid | Astromech droid / Class two droid | Industrial Automaton; Kuat Systems Engineering *(Legends)* |  | Galactic Republic; Galactic Empire; Jinata Security | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Q7-series_astromech_droid) |
| Q9-series astromech droid | Astromech droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Q9-series_astromech_droid) |
| QB-35 |  | East Corner Heavy Industry |  | Land & Sky Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/QB-35) |
| QR-unit |  |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/QR-unit) |
| Quartermaster droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Quartermaster_droid) |
| QueTee model |  |  | Prior to 0 ABY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/QueTee_model) |
| Quingarus Systems cook-droid | Cooking |  |  | Quingarus Deluxe Droid Systems Factory | canon |  | [wiki](https://starwars.fandom.com/wiki/Quingarus_Systems_cook-droid) |
| R-1 recon droid | Probe droid | Arakyd Industries |  | Galactic Republic; Galactic Empire; Planetary garrisons; Independent operators | canon |  | [wiki](https://starwars.fandom.com/wiki/R-1_recon_droid) |
| R-10 household droid | Service | Lovolan |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/R-10_household_droid) |
| R-4 recon droid | Probe droid | Arakyd Industries |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/R-4_recon_droid) |
| R-8009 utility droid | Maintenance droid / Class 5 | Serv-O-Droid, Inc. |  |  | canon | R8-009 (KotOR) | [wiki](https://starwars.fandom.com/wiki/R-8009_utility_droid) |
| R-EAU Linemaster |  |  |  | Rocket-Jumper Elite Advance Unit | canon |  | [wiki](https://starwars.fandom.com/wiki/R-EAU_Linemaster) |
| R-series | Astromech | Industrial Automaton |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/R-series) |
| R-series guidance droid | Pilot |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/R-series_guidance_droid) |
| R0-M3 Droid | Battle |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/R0-M3_Droid) |
| R1 security droid | Security droid/Sentry droid | Industrial Automaton |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/R1_security_droid) |
| R1-M8 service droid | Service droid / Class three droid | A company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/R1-M8_service_droid) |
| R1-type shopkeeping drone | Shopkeeping drone | Industrial Automaton |  | Watto's junkshop | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/R1-type_shopkeeping_drone) |
| R2-series astromech droid | Astromech droid / Class two | Industrial Automaton | During or prior to 132 BBY | Royal House of Naboo; Galactic Republic; Jedi Order; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/R2-series_astromech_droid) |
| R2-Series5 astromech droid | Astromech droid |  |  | New Republic; Hapes Consortium | canon |  | [wiki](https://starwars.fandom.com/wiki/R2-Series5_astromech_droid) |
| R2z Starship Maintenance Droid | Maintenance | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/R2z_Starship_Maintenance_Droid) |
| R3-series astromech droid | Astromech droid / Class two | Industrial Automaton |  | Confederacy of Independent Systems; Galactic Republic (as a spy); Iron Squadron; Alliance to Restore the Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/R3-series_astromech_droid) |
| R37 Maintenance Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/R37_Maintenance_Droid) |
| R4 astromech droid | Astromech droid / Class two | Industrial Automaton |  | Galactic Republic; Jedi Order; Sith; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/R4_astromech_droid) |
| R4 courier droid | Astromech droid (repurposed); Courier Droid | Industrial Automaton |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/R4_courier_droid) |
| R4-P Astromech | Astromech droid / Class two droid | Industrial Automaton |  | Jedi Order; Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/R4-P_Astromech) |
| R4-P astromech droid | Astromech droid / Class two droid | Industrial Automaton; Kuat Systems Engineering (modification) |  | Jedi Order; Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/R4-P_astromech_droid) |
| R5-series astromech droid | Astromech droid / Class two droid | Industrial Automaton |  | Alliance to Restore the Republic; Galactic Empire; Galactic Republic; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/R5-series_astromech_droid) |
| R6 astromech droid | Astromech droid / Class two | Industrial Automaton |  | New Republic; Plazir-15 government; Resistance | canon |  | [wiki](https://starwars.fandom.com/wiki/R6_astromech_droid) |
| R6-series astromech droid | Astromech droid / Class two droid | Industrial Automaton |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/R6-series_astromech_droid) |
| R7-series astromech droid | Astromech droid / Class two droid | Industrial Automaton |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/R7-series_astromech_droid) |
| R8-series astromech droid | Astromech / Class two droid | Industrial Automaton |  | New Republic; Various | canon |  | [wiki](https://starwars.fandom.com/wiki/R8-series_astromech_droid) |
| R8-TT Service Droid | maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/R8-TT_Service_Droid) |
| R9-series astromech droid | Astromech droid | Industrial Automaton |  | Galactic Alliance; Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/R9-series_astromech_droid) |
| RA-7 protocol droid | Analysis droid; Inventory droid; Protocol droid; Spy droid / Class three droid | Arakyd Industries |  | Confederacy of Independent Systems; Ohnaka Gang; New Mandalorians; Galactic Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/RA-7_protocol_droid) |
| RA-9O protocol droid | Protocol droid | Arakyd Industries |  | Bounty Hunters' Guild; Ranzar Malk's crew | canon |  | [wiki](https://starwars.fandom.com/wiki/RA-9O_protocol_droid) |
| Race camera | Cam droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Race_camera) |
| Racing droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Racing_droid) |
| Rakatan droid | Medical droid |  |  | Infinite Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Rakatan_droid) |
| Rakatan guardian droid | Battle droid | Rakata |  | Rakata; Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Rakatan_guardian_droid) |
| Ramship | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ramship) |
| Ran-D housekeeper droid | Cleaning |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Ran-D_housekeeper_droid) |
| Ranger X-1 | Defense droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ranger_X-1) |
| Ratcatcher droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ratcatcher_droid) |
| Raxus Droid | Battle droid / Class 4 |  |  | Raxus guard | canon |  | [wiki](https://starwars.fandom.com/wiki/Raxus_Droid) |
| Razor droid | Security droid / Class three droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Razor_droid) |
| RB-1 maintenance droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RB-1_maintenance_droid) |
| RC-101 | Loader |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RC-101) |
| RC-AD Riot Control/Assault Droid | Security droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/RC-AD_Riot_Control/Assault_Droid) |
| RC-D03 Battle Droid | Battle droid / Class four droid |  |  | Galactic Republic; Rike's Raiders | canon |  | [wiki](https://starwars.fandom.com/wiki/RC-D03_Battle_Droid) |
| Reactor drone | Maintenance |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Reactor_drone) |
| Recon remote | Probe | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Recon_remote) |
| Recon-PK series droid | Surveillance droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Recon-PK_series_droid) |
| Reconnaissance droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Reconnaissance_droid) |
| Recording droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Recording_droid) |
| Recycling droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Recycling_droid) |
| Red worker droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Red_worker_droid) |
| Redkihl Rokk's spider droid | Battle droid / Class four droid |  |  | Redkihl Rokk's Pirates | canon |  | [wiki](https://starwars.fandom.com/wiki/Redkihl_Rokk%27s_spider_droid) |
| Refresh droid | Battle | Haor Chall Engineering |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Refresh_droid) |
| Refuse droid | Cleaning droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Refuse_droid) |
| Remote |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Remote) |
| Remote droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Remote_droid) |
| Repair drone | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Repair_drone) |
| Replica droid | Protocol |  | By 200 BBY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Replica_droid) |
| Republic shuttle probe droid | Probe droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Republic_shuttle_probe_droid) |
| Repulsor pilot droid | Pilot |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Repulsor_pilot_droid) |
| Repulsor-droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Repulsor-droid) |
| Requisition droid |  |  |  | Sarkin Enneb's criminal group | canon |  | [wiki](https://starwars.fandom.com/wiki/Requisition_droid) |
| Rescue droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Rescue_droid) |
| Research Battler | Battle droid | Gray Secant |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Research_Battler) |
| Research Combatant | Battle droid | Gray Secant |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Research_Combatant) |
| Research Probe | Probe droid | Gray Secant |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Research_Probe) |
| Resource probe droid | Probe | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Resource_probe_droid) |
| RH-series research droid | Science droid | Cybot Galactica |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/RH-series_research_droid) |
| RHTC-560 Hunter Trainer | Training / Gladiatorial droid | Rodian D-Tec |  | Rodia; Bounty-hunting guilds; Planetary militias; Police academies | canon |  | [wiki](https://starwars.fandom.com/wiki/RHTC-560_Hunter_Trainer) |
| RIC-920 rickshaw droid | Labor droid | Serv-O-Droid, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RIC-920_rickshaw_droid) |
| RIC-series general labor droid | Labor droid / Class five | Serv-O-Droid, Inc. |  | Plazir-15 government | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/RIC-series_general_labor_droid) |
| Ringneck recon droid | Probe droid | Arakyd Industries |  | Confederacy of Independent Systems; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Ringneck_recon_droid) |
| RIV-3T | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RIV-3T) |
| RJ unit |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RJ_unit) |
| RK-94 Protector Droid | Battle droid | Ayor-v9 |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RK-94_Protector_Droid) |
| RL droid | Pilot droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RL_droid) |
| RLG guardian droid system | Security | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RLG_guardian_droid_system) |
| RM-2020 espionage droid | Espionage droid / Class four droid | MerenData |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RM-2020_espionage_droid) |
| RM-series military intelligence droid | Military intelligence droid | MerenData |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RM-series_military_intelligence_droid) |
| RMD-20 "Eye in the Sky" Series Monitoring Droid | Cam | Kystallio Detection Plus |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RMD-20_%22Eye_in_the_Sky%22_Series_Monitoring_Droid) |
| RMS droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RMS_droid) |
| RO-D-series droid | Labor droid/Security droid / Class five droid | Balmorran Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RO-D-series_droid) |
| Robo-flagwaver | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Robo-flagwaver) |
| Robo-vassal |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Robo-vassal) |
| Rocket battle droid | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Commerce Guild | Legends |  | [wiki](https://starwars.fandom.com/wiki/Rocket_battle_droid/Legends) |
| ROLL-R | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ROLL-R) |
| Roller mine |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Roller_mine) |
| Rolo droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Rolo_droid) |
| Rover droid | Security droid |  |  | ComNet Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Rover_droid) |
| Roving Eye observation droid | Cam droid / Class two droid |  |  | Darth Krayt's Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Roving_Eye_observation_droid) |
| Royal Guard droid | Courier and messenger |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Royal_Guard_droid) |
| Royal med droid | Medical droid |  |  | Royal Naboo Security Forces | canon |  | [wiki](https://starwars.fandom.com/wiki/Royal_med_droid) |
| RQ protocol droid | Protocol droid / Class three | Lothal Logistics Limited |  | Galactic Empire; Lothal Port Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/RQ_protocol_droid) |
| RS-D04 Assault Droid | Battle droid / Class four droid |  |  | Galactic Republic; Rike's Raiders | canon |  | [wiki](https://starwars.fandom.com/wiki/RS-D04_Assault_Droid) |
| RT-11 Patrol Droid | Probe patrol droid | Kerkarr |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/RT-11_Patrol_Droid) |
| RT-D02 War Droid | Battle droid / Class four droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/RT-D02_War_Droid) |
| Rug-cleaning droid | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Rug-cleaning_droid) |
| RWW-series protocol droid | Protocol droid / Class three droid | Teagan Tech Consortium |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/RWW-series_protocol_droid) |
| RX-77 Defense Droid | Battle droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/RX-77_Defense_Droid) |
| RX-series pilot droid | Pilot droid; Astromech droid / Class Three | Industrial Automaton |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/RX-series_pilot_droid) |
| S-1 security droid | Security droid |  |  | Corellian Security Force | canon |  | [wiki](https://starwars.fandom.com/wiki/S-1_security_droid) |
| S-2 security droid | Security droid |  |  | Corellian Security Force | canon |  | [wiki](https://starwars.fandom.com/wiki/S-2_security_droid) |
| S-3P5 Labor Droid | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S-3P5_Labor_Droid) |
| S-43 enforcer droid | Battle droid; Enforcer droid / Class three droid |  |  | Hutt Clan | canon |  | [wiki](https://starwars.fandom.com/wiki/S-43_enforcer_droid) |
| S-EP1 security droid | Security droid | Ulban Arms |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/S-EP1_security_droid) |
| S-X VAC-u-Bot | Class five droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S-X_VAC-u-Bot) |
| S/D Decimator droid | Class 4 | Baktoid Innovations |  | Techno Union; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/S/D_Decimator_droid) |
| S12 droid |  | Industrial Automaton | By c. 2 BBY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S12_droid) |
| S19 astromech droid | astromech droid / Class two droid | LesTech |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S19_astromech_droid) |
| S2R(A) Science Droid | Class one | TelBrinTel Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S2R%28A%29_Science_Droid) |
| S3-D7 Combat Droid | Battle droid / Class four droid |  |  | Exchange | canon |  | [wiki](https://starwars.fandom.com/wiki/S3-D7_Combat_Droid) |
| S6-series security/maintenance droid | Maintenance droid; Security droid | MerenData |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S6-series_security/maintenance_droid) |
| S7-H7 Slicing Droid | Slicer droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/S7-H7_Slicing_Droid) |
| S9-series heavy power droid | Power droid / Class five droid | Veril Line Systems |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/S9-series_heavy_power_droid) |
| SA-27 Suppression Droid | Battle droid / Class four droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SA-27_Suppression_Droid) |
| SA-45 Technician Droid | Maintenance droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SA-45_Technician_Droid) |
| SA-5 protocol droid | Protocol droid / Class One |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SA-5_protocol_droid) |
| Sabotage droid | Spy |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Sabotage_droid) |
| Safari droid | Class one | Serv-O-Droid, Inc. |  | Galactic Society of Creature Enthusiasts | canon |  | [wiki](https://starwars.fandom.com/wiki/Safari_droid) |
| Safeguard Mk II | Battle droid / Class four droid | Holowan Laboratories |  | Holowan Laboratories | canon |  | [wiki](https://starwars.fandom.com/wiki/Safeguard_Mk_II) |
| Safety droid | Class 4 |  |  | At Attin's government | canon |  | [wiki](https://starwars.fandom.com/wiki/Safety_droid) |
| Sailing droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sailing_droid) |
| Salvage droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Salvage_droid) |
| Sanitation droid | Cleaning |  |  | HK-01's droid army | canon |  | [wiki](https://starwars.fandom.com/wiki/Sanitation_droid) |
| Sapper droid | Class four |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Sapper_droid) |
| Sartorifex Robo-Valet | Service | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sartorifex_Robo-Valet) |
| Satellite droid | Surveillance droid |  |  | Nawaam's army | canon |  | [wiki](https://starwars.fandom.com/wiki/Satellite_droid) |
| SB-20 Slicer Droid | Espionage/slicer droid | Illicit Electronics |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SB-20_Slicer_Droid) |
| SB-53 Incineration Droid | Battle droid / Class four droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SB-53_Incineration_Droid) |
| SBD series assistance and rescue droid |  | Karflo Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SBD_series_assistance_and_rescue_droid) |
| SC-68 Electrocution Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SC-68_Electrocution_Droid) |
| Scanning Patrol Detail series | Security droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scanning_Patrol_Detail_series) |
| Scapedroid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scapedroid) |
| Scar Removal Droid | Medical droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scar_Removal_Droid) |
| Scarab droid | Assassin | Sienar Intelligence Systems |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Scarab_droid) |
| Scarab Mark 3 Assassin Droid | Assassin droid | Sienar Intelligence Systems |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Scarab_Mark_3_Assassin_Droid) |
| Scarab Mark VI assassin droid | Assassin droid | Sienar Intelligence Systems |  | Galactic Empire; Dark Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Scarab_Mark_VI_assassin_droid) |
| Scarecrow droid | Farm droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scarecrow_droid) |
| Scav droid | Nihil | Zeetar |  | Nihil; Pan Eyta's crew | canon |  | [wiki](https://starwars.fandom.com/wiki/Scav_droid) |
| Scavenger droid (Koboh) |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scavenger_droid_%28Koboh%29) |
| Science droid | Class one |  |  |  | Legends |  | [wiki](https://starwars.fandom.com/wiki/Science_droid/Legends) |
| Science Research Droid | Biological science droid / Class one droid | TelBrinTel Corporation |  | Galactic Empire; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Science_Research_Droid) |
| SCM-22 stenographer |  | PowerPost |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/SCM-22_stenographer) |
| Scorpenek annihilator droid | Class four droid | Colicoid Creation Nest *(Legends)* |  | Pyke Syndicate | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Scorpenek_annihilator_droid) |
| Scorpion-droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scorpion-droid) |
| Scour swarm droid |  | Unidentified Iokath species |  | Unidentified Iokath species; ARIES | canon |  | [wiki](https://starwars.fandom.com/wiki/Scour_swarm_droid) |
| Scout transmitter | Spy droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scout_transmitter) |
| Scrambler droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scrambler_droid) |
| Scrubber droid | Cleaning droid | Industrial Automaton *(Legends)* |  | Royal Naboo Security Forces; Galactic Republic; Kaminoan government; Alliance to Restore the Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Scrubber_droid) |
| Scum-scrubber | Sanitation |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Scum-scrubber) |
| Scutiger-100 stealth droid | Assassin droid / Class four droid | Ghost Armaments |  | Confederacy military | canon |  | [wiki](https://starwars.fandom.com/wiki/Scutiger-100_stealth_droid) |
| SD-10 battle droid | Battle droid / Class four droid | Balmorran Arms |  | Galactic Empire; Balmorran Defense Force; Dark Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-10_battle_droid) |
| SD-4 battle droid | Battle droid | Balmorran Arms |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-4_battle_droid) |
| SD-5 battle droid | Battle droid | Balmorran Arms |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-5_battle_droid) |
| SD-54 Neutralization Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-54_Neutralization_Droid) |
| SD-6 Hulk infantry droid | Battle droid / Class four droid | Balmorran Arms |  | Galactic Republic; Galactic Empire; Independent | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-6_Hulk_infantry_droid) |
| SD-60 Personal Defense Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-60_Personal_Defense_Droid) |
| SD-9 battle droid | Battle droid / Class four droid | Balmorran Arms |  | Dark Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-9_battle_droid) |
| SD-K4 assassin droid | Assassin droid / Fourth-degree droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Death Watch; Galactic Empire; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-K4_assassin_droid) |
| SD-K4a mini-assassin droid | Assassin droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Death Watch; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-K4a_mini-assassin_droid) |
| SD-series battle droid | Battle droid | Balmorran Arms |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/SD-series_battle_droid) |
| SD-X-series stealth battle droid | battle droid / Class four droid | Tendrando Arms |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SD-X-series_stealth_battle_droid) |
| SDMN series session droid | Entertainment | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SDMN_series_session_droid) |
| SE-2 worker droid | Menial labor droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SE-2_worker_droid) |
| SE-2-4 servant droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SE-2-4_servant_droid) |
| SE-5 service droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SE-5_service_droid) |
| SE-6 domestic | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SE-6_domestic) |
| SE-77 Annihilation Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SE-77_Annihilation_Droid) |
| SE-89 Annihilation Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SE-89_Annihilation_Droid) |
| SE2 service droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SE2_service_droid) |
| SE4 servant droid | Servant droid; Protocol droid / Class three droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SE4_servant_droid) |
| SE8 waiter droid | Service droid | Industrial Automaton |  | Canto Casino and Racetrack; Crimson Dawn | canon |  | [wiki](https://starwars.fandom.com/wiki/SE8_waiter_droid) |
| Searcher 2050 exploration droid | Exploration droid/Probe droid | Arakyd Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Searcher_2050_exploration_droid) |
| SEC-M droid | Class five |  |  | Imperial Intelligence | canon |  | [wiki](https://starwars.fandom.com/wiki/SEC-M_droid) |
| Secretary droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Secretary_droid) |
| Security droid | Class four |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Security_droid) |
| Security droid (Colossus) | Security droid |  |  | Colossus | canon |  | [wiki](https://starwars.fandom.com/wiki/Security_droid_%28Colossus%29) |
| Security Droid BX | Security droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Security_Droid_BX) |
| Security monitor droid | Security droid / Class three droid |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Security_monitor_droid) |
| Seeker (droid) | Probe droid; Spy droid |  |  | Sith Order; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Seeker_%28droid%29) |
| Seismic surveyor | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Seismic_surveyor) |
| SEN-TRI | Worker droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SEN-TRI) |
| Senate cam droid | Holocam |  |  | Galactic Republic; Confederacy of Independent Systems | Legends |  | [wiki](https://starwars.fandom.com/wiki/Senate_cam_droid/Legends) |
| Senate Guard analysis droid | Analysis |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Senate_Guard_analysis_droid) |
| Senate hovercam droid | Cam droid / Class three droid | Cybot Galactica |  | Galactic Republic; Galactic Empire; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Senate_hovercam_droid) |
| Seneschal-series factotum droid | Service droid / Class three droid | Imperial DroidWorks |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Seneschal-series_factotum_droid) |
| Sensor droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sensor_droid) |
| Sentinel (Contingency) | Holodroid |  | In or prior to 20 BBY | Galactic Empire; Sith | canon |  | [wiki](https://starwars.fandom.com/wiki/Sentinel_%28Contingency%29) |
| Sentinel droid | Battle droid | Kellenech Technologies |  | Galactic Republic; Raff Syndicate; Sith Empire; Ahto City Civil Authority | canon |  | [wiki](https://starwars.fandom.com/wiki/Sentinel_droid) |
| Sentry droid | Security |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Sentry_droid) |
| Sentry droid Mark I | Sentry | Aratech Repulsor Company |  | G0-T0 | canon |  | [wiki](https://starwars.fandom.com/wiki/Sentry_droid_Mark_I) |
| Sentry Droid X-5 | Sentry droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sentry_Droid_X-5) |
| Separatist probe droid | Probe droid |  |  | Confederacy of Independent Systems; Techno Union | Legends |  | [wiki](https://starwars.fandom.com/wiki/Separatist_probe_droid/Legends) |
| Serenno flying droid | Probe |  |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Serenno_flying_droid) |
| Service droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Service_droid) |
| Service patch remote | Remote |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Service_patch_remote) |
| Servo-droid | Cleaning |  |  | The Wheel | canon |  | [wiki](https://starwars.fandom.com/wiki/Servo-droid) |
| Servomech | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Servomech) |
| Sewing assistant droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sewing_assistant_droid) |
| Sex droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sex_droid) |
| Shadow Security Droid | Security |  |  | Dark Empire; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Shadow_Security_Droid) |
| Shield remote | Remote |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Shield_remote) |
| Shoeshine droid | Class five |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Shoeshine_droid) |
| Shopkeeper droid | Class three droid |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Shopkeeper_droid) |
| Short-Range Transport droid | Labor droid |  |  | Stalgasin hive; Confederacy of Independent Systems; Plazir-15 government | canon |  | [wiki](https://starwars.fandom.com/wiki/Short-Range_Transport_droid) |
| Shrine droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Shrine_droid) |
| Siak-series protocol droid | Protocol droid / Class three droid | Roche Hive Mechanical Apparatus Design and Construction Activity for Those Who Need the Hive's Machines |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Siak-series_protocol_droid) |
| Siantide droid | Battle droid / Class four droid | War Trust | c. 3642 BBY | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Siantide_droid) |
| Siege Skytrooper | Battle droid / Class four droid | Eternal Empire |  | Eternal Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Siege_Skytrooper) |
| Sifter droid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sifter_droid) |
| Sigma series training unit | Lightsaber combat training droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Sigma_series_training_unit) |
| Signal droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Signal_droid) |
| SIS Surveillance Droid | Surveillance droid | Taptronics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SIS_Surveillance_Droid) |
| Sith Elite Warbot | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Sith_Elite_Warbot) |
| Sith Sentry | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sith_Sentry) |
| Sith Training Droid | Training droid; PROXY droid |  |  | Order of the Sith Lords | canon |  | [wiki](https://starwars.fandom.com/wiki/Sith_Training_Droid) |
| Sith war droid Mark I | Battle droid | Colicoids |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Sith_war_droid_Mark_I) |
| Sith war droid Mark II | Battle droid |  |  | Sith Empire; Imperial Military | canon |  | [wiki](https://starwars.fandom.com/wiki/Sith_war_droid_Mark_II) |
| SK series | Astromech droid | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SK_series) |
| SK-21 support droid | Battle droid |  |  | HK-47 | canon |  | [wiki](https://starwars.fandom.com/wiki/SK-21_support_droid) |
| SK-89's model |  |  |  | Kwikhaul Livery Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/SK-89%27s_model) |
| Skimming droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Skimming_droid) |
| Skyreaper drone | Class four |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Skyreaper_drone) |
| Skytrooper | Battle droid / Class four droid | Eternal Empire (formerly); Eternal Alliance |  | Eternal Empire (formerly); Eternal Alliance; Order of Zildrog | canon |  | [wiki](https://starwars.fandom.com/wiki/Skytrooper) |
| Slandarv's battle droid model | Battle droid | Slandarv |  | Galactic Empire (Intended); Darth Vader; Schism Imperial | canon |  | [wiki](https://starwars.fandom.com/wiki/Slandarv%27s_battle_droid_model) |
| Slave Droid SD-9 | Labor droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Slave_Droid_SD-9) |
| Slicer droid | Spy |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Slicer_droid) |
| Sludgegulper |  |  |  | The Great Heep | canon |  | [wiki](https://starwars.fandom.com/wiki/Sludgegulper) |
| SM-06 Detonator Droid | Battle droid / Class four droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SM-06_Detonator_Droid) |
| SM-series scavenger droid | Scavenger droid | New Republic Department of Research and Development |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/SM-series_scavenger_droid) |
| Small Size Droid | Battle |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Small_Size_Droid) |
| Smart mine | Battle |  |  |  | Legends |  | [wiki](https://starwars.fandom.com/wiki/Smart_mine/Legends) |
| Smartvac | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Smartvac) |
| Smelter droid | Hazardous-service |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Smelter_droid) |
| Snic 2-4-2 | Labor droid |  |  | Fromm Gang | canon |  | [wiki](https://starwars.fandom.com/wiki/Snic_2-4-2) |
| Sniffer droid |  |  |  | Coruscant Security Force | canon |  | [wiki](https://starwars.fandom.com/wiki/Sniffer_droid) |
| Sniper droideka | Battle droid | Colicoids |  | Confederacy of Independent Systems | Legends | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Sniper_droideka/Legends) |
| SO-1P autovalet droid | Service droid / Class five droid | Serv-O-Droid, Inc. |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/SO-1P_autovalet_droid) |
| Soil scrubber | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Soil_scrubber) |
| Sonic generator droid | Class four |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sonic_generator_droid) |
| Sorter droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sorter_droid) |
| Sower | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sower) |
| SP Eighty cleaner droid | Cleaning |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SP_Eighty_cleaner_droid) |
| SP-15 Surveillance Droid | Probe droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SP-15_Surveillance_Droid) |
| SP-4 analysis droid | Analysis droid / Class one droid | Cybot Galactica |  | Galactic Republic; Jedi Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/SP-4_analysis_droid) |
| SP-4 ISC crime scene analysis droid | Analysis droid; Forensics droid | Cybot Galactica |  | Jedi Order; Galactic Republic; Galactic Empire; Archaeological Association | canon |  | [wiki](https://starwars.fandom.com/wiki/SP-4_ISC_crime_scene_analysis_droid) |
| Spa droid | Service droid *(Legends)* |  |  | Droid Spa; Terminal 24 | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Spa_droid) |
| Space Battle Droid | Battle | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Space_Battle_Droid) |
| Spacecap Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Spacecap_Droid) |
| Spaceport Luggage Droid | Security droid |  |  | Star Liner Travel | canon |  | [wiki](https://starwars.fandom.com/wiki/Spaceport_Luggage_Droid) |
| Spaceport police droid | Police droid; Security droid / Class four droid |  |  | Various local law enforcement agencies; InterGalactic Banking Clan | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Spaceport_police_droid) |
| Sparring droid | Class four |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Sparring_droid) |
| SPD-R4 spider droid | Service droid; Maintenance droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SPD-R4_spider_droid) |
| Speaker droid | Speaker droid |  |  | Mothma family; Sculdun family | canon |  | [wiki](https://starwars.fandom.com/wiki/Speaker_droid) |
| Speaker droid (senate) |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Speaker_droid_%28senate%29) |
| Spearhead droid | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Spearhead_droid) |
| Spelunker probe droid | Mining droid; Probe droid | Arakyd Industries |  | Confederacy of Independent Systems; Commerce Guild | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Spelunker_probe_droid) |
| Spider Battle Droid | Battle droid | Baktoid Combat Automata |  | Baktoid Combat Automata | canon |  | [wiki](https://starwars.fandom.com/wiki/Spider_Battle_Droid) |
| Spider droid family | Droid walker | Baktoid Armor Workshop; Techno Union |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Spider_droid_family) |
| Spider probe droid | Probe droid | Arakyd-Harch Technologies |  | First Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Spider_probe_droid) |
| Spider-droid |  |  |  | Scourge | canon |  | [wiki](https://starwars.fandom.com/wiki/Spider-droid) |
| Spidertaur | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Spidertaur) |
| Spore-Tending Unit | Environmental droid |  |  | Jannimak | canon |  | [wiki](https://starwars.fandom.com/wiki/Spore-Tending_Unit) |
| Spotter droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Spotter_droid) |
| Sprayer | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sprayer) |
| Sprayer droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sprayer_droid) |
| Spy droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Spy_droid) |
| Spy drone | Surveillance and listening |  |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Spy_drone) |
| SR-78 Bulwark Defense Droid | Battle droid |  |  | The Shroud's organization | canon |  | [wiki](https://starwars.fandom.com/wiki/SR-78_Bulwark_Defense_Droid) |
| SRT autonomous short-range transport | Loader droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/SRT_autonomous_short-range_transport) |
| Ssi-ruuvi security droid | Security droid | Ssi-ruuk |  | Ssi-ruuvi Imperium | canon |  | [wiki](https://starwars.fandom.com/wiki/Ssi-ruuvi_security_droid) |
| ST-series military strategic analysis and tactics droid | Tactical droid / Class four droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Infinite Coil; Separatist holdouts | canon |  | [wiki](https://starwars.fandom.com/wiki/ST-series_military_strategic_analysis_and_tactics_droid) |
| Stage VI Bio-Desolator Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Stage_VI_Bio-Desolator_Droid) |
| Staircase droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Staircase_droid) |
| Star Navigator droid | Pilot droid |  |  | Morgan Elsbeth's forces; Thrawn's forces | canon |  | [wiki](https://starwars.fandom.com/wiki/Star_Navigator_droid) |
| Stealth droid | Battle |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Stealth_droid) |
| Stealth microdroid dust | Microdroid |  |  | Archaeologists; Droid Gotra | canon |  | [wiki](https://starwars.fandom.com/wiki/Stealth_microdroid_dust) |
| StelProbe V Droid | Exploration/contact droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/StelProbe_V_Droid) |
| Stevedore droid | Labor droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Stevedore_droid) |
| Stiletto security droid | Security droid / Class four droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Stiletto_security_droid) |
| Stone guardian | Security |  |  | Frangawl Cult | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Stone_guardian) |
| Storage and transceiving droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Storage_and_transceiving_droid) |
| Stormtrooper droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Stormtrooper_droid) |
| Street-cleaner droid | Sanitation |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Street-cleaner_droid) |
| Stretch droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Stretch_droid) |
| Strike Droid SD | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Strike_Droid_SD) |
| Strike-Orb | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Strike-Orb) |
| Sublight survey droid | Survey droid |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Sublight_survey_droid) |
| Submersible minelayer droid | Demolition; Submersible |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Submersible_minelayer_droid) |
| Submersible probe droid | Probe; Submersible |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Submersible_probe_droid) |
| Subminiature probe drone | Probe |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Subminiature_probe_drone) |
| Subservient Mark VII Attendant Droid | Service | Galinolo |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Subservient_Mark_VII_Attendant_Droid) |
| Subterranean Seeker Droid | Class five; Probe | Galactic Solutions Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Subterranean_Seeker_Droid) |
| Super battle droid rocket trooper | Battle droid | Baktoid Combat Automata |  | Confederacy of Independent Systems | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Super_battle_droid_rocket_trooper) |
| Super buzz droid | Sabotage |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Super_buzz_droid) |
| Super tactical droid | Tactical droid |  |  | Confederacy of Independent Systems | Legends | ST super tactical (JDS) | [wiki](https://starwars.fandom.com/wiki/Super_tactical_droid/Legends) |
| Supervisor droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Supervisor_droid) |
| Supply Droid | Maintenance droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Supply_Droid) |
| Support Droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Support_Droid) |
| Supreme-Class Servant Droid | Servant droid | Lovolan |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Supreme-Class_Servant_Droid) |
| Surveillance droid | Spy |  |  | Galactic Republic; Galactic Empire *(Legends)* | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Surveillance_droid) |
| Survey droid | Class two |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Survey_droid) |
| SW-1 sweeper droid | Sanitation |  |  | Land & Sky Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/SW-1_sweeper_droid) |
| SW1-04 Computer Repair Droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/SW1-04_Computer_Repair_Droid) |
| SWAT-droid | Battle |  |  | Galactic Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/SWAT-droid) |
| Sweeper droid | Cleaning droid |  | By 21 BBY |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Sweeper_droid) |
| SWL-5 overseer | Security droid | Stonewall Labs |  | Stonewall Labs | canon |  | [wiki](https://starwars.fandom.com/wiki/SWL-5_overseer) |
| Synthdroid |  | Loronar Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Synthdroid) |
| T-12 service droid | Maintenance |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/T-12_service_droid) |
| T-26G Torture Droid | Interrogation |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/T-26G_Torture_Droid) |
| T-3 | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/T-3) |
| T-41 Battle Droid | Battle droid | Kerkarr |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/T-41_Battle_Droid) |
| T-44 Assault Droid | Battle droid | Kerkarr |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/T-44_Assault_Droid) |
| T-831 |  | Zubintech |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/T-831) |
| T-Series Imperial Protocol Droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/T-Series_Imperial_Protocol_Droid) |
| T-series military strategic analysis and tactics droid | Tactical droid / Class four droid | Baktoid Combat Automata |  | Atha Prime; Confederacy of Independent Systems; Zygerrian Slave Empire; Separatist holdouts | canon |  | [wiki](https://starwars.fandom.com/wiki/T-series_military_strategic_analysis_and_tactics_droid) |
| T-series tactical droid | Tactical droid | Baktoid Combat Automata |  | Confederacy of Independent Systems; Dark Worlds; Zygerrian Slave Empire | Legends |  | [wiki](https://starwars.fandom.com/wiki/T-series_tactical_droid/Legends) |
| T0-D interrogation droid | Interrogation droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/T0-D_interrogation_droid) |
| T1-series utility droid | Maintenance droid | Duwani Mechanical Products |  |  | canon | T1 tactical (JDS) | [wiki](https://starwars.fandom.com/wiki/T1-series_utility_droid) |
| T3-series utility droid | Maintenance droid | Duwani Mechanical Products |  |  | canon | T3 (KotOR) | [wiki](https://starwars.fandom.com/wiki/T3-series_utility_droid) |
| T4 turret droid | battle droid / Class four droid | Colicoid Creation Nest |  | Trade Federation; Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/T4_turret_droid) |
| T5-TB Repair Droid | Maintenance droid | Ayor-v9 |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/T5-TB_Repair_Droid) |
| T7-series astromech droid | Astromech droid | Duwani Mechanical Products |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/T7-series_astromech_droid) |
| T7-series droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/T7-series_droid) |
| Tactical Defense Droid | Police droid |  |  | Janix Civil Defense; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Tactical_Defense_Droid) |
| Tactical droid | Battle droid / Class four droid |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Tactical_droid) |
| Tagge prototype battle droid | Battle droid | Tagge Corporation |  | Tagge Corporation; Confederacy of Independent Systems (Intended); Scourge (As a vessel) | canon |  | [wiki](https://starwars.fandom.com/wiki/Tagge_prototype_battle_droid) |
| Tailor droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tailor_droid) |
| Talkdroid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Talkdroid) |
| Talking magnetite cleaner | Cleaning droid |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Talking_magnetite_cleaner) |
| Tall Blue Droid | Security droid |  |  | Galactic Empire; Jawas | canon |  | [wiki](https://starwars.fandom.com/wiki/Tall_Blue_Droid) |
| Tall Sniper Droid | Battle droid | Baktoid Combat Automata |  | Baktoid Combat Automata | canon |  | [wiki](https://starwars.fandom.com/wiki/Tall_Sniper_Droid) |
| Tank droid Mark IV | Droid tank |  |  | Galactic Republic; Telos Security Force (possible) | canon |  | [wiki](https://starwars.fandom.com/wiki/Tank_droid_Mark_IV) |
| Tantiss medical droid | Medical droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Tantiss_medical_droid) |
| Tao-Ni Security Elite Protector | Security droid | Tao-Ni Security |  | IG-88's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/Tao-Ni_Security_Elite_Protector) |
| Tao-Ni Security Mechanized Alpha Class | Security droid | Tao-Ni Security |  | Tao-Ni Security | canon |  | [wiki](https://starwars.fandom.com/wiki/Tao-Ni_Security_Mechanized_Alpha_Class) |
| Tao-Ni Security Mechanized Beta Class | Security droid | Tao-Ni Security |  | Tao-Ni Security | canon |  | [wiki](https://starwars.fandom.com/wiki/Tao-Ni_Security_Mechanized_Beta_Class) |
| Tao-Ni Security Mechanized Omega Class | Security droid | Tao-Ni Security |  | Tao-Ni Security | canon |  | [wiki](https://starwars.fandom.com/wiki/Tao-Ni_Security_Mechanized_Omega_Class) |
| Tashelin serenading droid | Musician droid | Tashelin Industries |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tashelin_serenading_droid) |
| Taxi droid | Pilot |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Taxi_droid) |
| TC-SC infiltration droid | Assassin droid; Espionage droid / Class four droid | Cybot Galactica |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TC-SC_infiltration_droid) |
| TC-series protocol droid | Protocol droid / Class three | Cybot Galactica |  | Trade Federation; Hutt Clan; Galactic Republic; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/TC-series_protocol_droid) |
| TCH-series educational assistant droid | Educational |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TCH-series_educational_assistant_droid) |
| TDA-series droid assistant | Protocol droid | AccuTronics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TDA-series_droid_assistant) |
| TDK-160 research-assistant |  |  |  | Zerpen Industries | canon |  | [wiki](https://starwars.fandom.com/wiki/TDK-160_research-assistant) |
| Teacher Droid | Teacher droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Teacher_Droid) |
| Tech droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tech_droid) |
| Technical droid | Class two; Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Technical_droid) |
| Technical support droid |  |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Technical_support_droid) |
| Technician Droid TE | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Technician_Droid_TE) |
| Techno Union HoloDroid | Class five; Holodroid | Techno Union |  | Techno Union | canon |  | [wiki](https://starwars.fandom.com/wiki/Techno_Union_HoloDroid) |
| Techno-service droid | Service droid / Class three droid | Vertseth Automata |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Techno-service_droid) |
| Temirca droid |  |  |  | Mos Espa settlers | canon |  | [wiki](https://starwars.fandom.com/wiki/Temirca_droid) |
| Temple caretaker droid |  |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Temple_caretaker_droid) |
| Textile droid | Specialized labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Textile_droid) |
| Therapy droid | Class three |  |  | New Republic | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Therapy_droid) |
| Third-generation battle droid | Battle droid / Class three droid | Imperial Department of Military Research |  | Gideon's Imperial remnant | canon |  | [wiki](https://starwars.fandom.com/wiki/Third-generation_battle_droid) |
| Threepethosk protocol droid | Protocol |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Threepethosk_protocol_droid) |
| THX servant droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/THX_servant_droid) |
| Tibanna Gas Collection Droid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tibanna_Gas_Collection_Droid) |
| Ticket droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ticket_droid) |
| TIE training drone |  |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TIE_training_drone) |
| TIE/D automated starfighter | Droid starfighter | Sienar Fleet Systems; Cybot Galactica (piloting system); World Devastator factories (primary manufacturer) |  | Dark Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TIE/D_automated_starfighter) |
| Timely Tutor education droid | Educational |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Timely_Tutor_education_droid) |
| TL-4 | Tailor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TL-4) |
| TO-series | Protocol droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TO-series) |
| Tomb Guardian | Security | Zeffonian |  | Zeffo Sages | canon |  | [wiki](https://starwars.fandom.com/wiki/Tomb_Guardian) |
| Tool-and-Die series droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tool-and-Die_series_droid) |
| Tourism droid | Tourism droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tourism_droid) |
| Tow droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tow_droid) |
| Toy droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Toy_droid) |
| TRA-9 battle droid | Battle |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TRA-9_battle_droid) |
| Tracked labor droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tracked_labor_droid) |
| Tractor drone | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tractor_drone) |
| Trade Federation assassin droid | Assassin droid / Class four droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Trade_Federation_assassin_droid) |
| Trade Federation maintenance droid | Maintenance droid | Trade Federation |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Trade_Federation_maintenance_droid) |
| Traffic robo |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Traffic_robo) |
| Traffic-monitor droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Traffic-monitor_droid) |
| Training battle droid | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Training_battle_droid) |
| Training droid | Class four |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Training_droid) |
| Training Droid (Naboo) | Training |  |  | Royal Naboo Security Forces | canon |  | [wiki](https://starwars.fandom.com/wiki/Training_Droid_%28Naboo%29) |
| Training droid (Umbaran Sith Academy) | Training droid |  |  | Sith | canon |  | [wiki](https://starwars.fandom.com/wiki/Training_droid_%28Umbaran_Sith_Academy%29) |
| Trak-R | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Trak-R) |
| Translator droid | Class three |  |  | Galactic Empire; First Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Translator_droid) |
| Transport droid | Transport droid |  |  | Pixelito Port Hauling | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Transport_droid) |
| Transport ticketing droid |  |  |  | The Colossus | canon |  | [wiki](https://starwars.fandom.com/wiki/Transport_ticketing_droid) |
| Transportation droid | Class three |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Transportation_droid) |
| TRD-2 sparring droid | Training droid | Balmorran Arms |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TRD-2_sparring_droid) |
| Treadwell Harvester Droid | Agricultural |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Treadwell_Harvester_Droid) |
| Treddroid | Mining |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Treddroid) |
| TRI-TEK | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TRI-TEK) |
| Triage droid | Medical droid / Class one droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Triage_droid) |
| Triangle droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Triangle_droid) |
| TribBot mimic series | Entertainment | RetSpan Audionics |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TribBot_mimic_series) |
| Trophy droid |  |  |  | Hunters of the Outer Rim | canon |  | [wiki](https://starwars.fandom.com/wiki/Trophy_droid) |
| TS-series interrogation droid | Interrogation droid | Arakyd Industries |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TS-series_interrogation_droid) |
| TT-2G guard droid | Guard droid |  |  | Tassaa Bareesh | canon |  | [wiki](https://starwars.fandom.com/wiki/TT-2G_guard_droid) |
| TT-40 librarian droid | Librarian droid | TelBrinTel Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TT-40_librarian_droid) |
| TT-8L series | Security droid | Serv-O-Droid, Inc. |  | Jabba's criminal empire; Guavian Death Gang | canon |  | [wiki](https://starwars.fandom.com/wiki/TT-8L_series) |
| TT-8L/Y7 gatekeeper droid | Security droid / Class 5 | Serv-O-Droid, Inc. |  | Galactic Republic; Confederacy of Independent Systems; Jabba's criminal empire; Gideon's Imperial remnant | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/TT-8L/Y7_gatekeeper_droid) |
| TTS-15 Series Tutorial Droid | Class three | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TTS-15_Series_Tutorial_Droid) |
| TTS15-series education and tutorial droid | Educational | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TTS15-series_education_and_tutorial_droid) |
| TTS20-series dialectic droid | Educational | Industrial Automaton |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/TTS20-series_dialectic_droid) |
| Tunnel-grinder | Sanitation |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Tunnel-grinder) |
| Turbolift droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Turbolift_droid) |
| Turret droid | Battle droid |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Turret_droid) |
| Turret-droid | Combat droid |  |  | Golas Aram; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Turret-droid) |
| Tutor droid | Class three |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Tutor_droid) |
| TX-1118 Series "Terminax" Assassin Droid | Assassin | MerenData |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TX-1118_Series_%22Terminax%22_Assassin_Droid) |
| TX7 Long-Range Probe | Probe droid |  |  | House Thul | canon |  | [wiki](https://starwars.fandom.com/wiki/TX7_Long-Range_Probe) |
| Tythonian War Droid | Battle droid | Weapon Master |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/Tythonian_War_Droid) |
| TZ-3 Dominator Droid | Battle droid |  | destroyed 3640 BBY, Corellia | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/TZ-3_Dominator_Droid) |
| U2-C1-series housekeeping droid | Housekeeping droid / Class three droid | Publictechnic |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/U2-C1-series_housekeeping_droid) |
| U5 | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/U5) |
| Ubrikkian Steamworks medical unit | Medical droid | Ubrikkian Steamworks |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Ubrikkian_Steamworks_medical_unit) |
| Ugly assassin droid | Assassin droid | A student (helped design the droid) |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Ugly_assassin_droid) |
| UL-413 scaper droid | Scaper droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/UL-413_scaper_droid) |
| Ultra Droideka | Battle droid |  |  | Confederacy of Independent Systems | canon | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/Ultra_Droideka) |
| Unidentified angled-dome astromech series | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_angled-dome_astromech_series) |
| Unidentified anthropomorphic mantis-like droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_anthropomorphic_mantis-like_droid) |
| Unidentified astromech droid series | Astromech |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_astromech_droid_series) |
| Unidentified astromech line | Astromech |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_astromech_line) |
| Unidentified battle droid model | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_battle_droid_model) |
| Unidentified battle droid model (Zonus Corporation) | Battle droid |  |  | Zonus Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_battle_droid_model_%28Zonus_Corporation%29) |
| Unidentified Fortress Vader droid model | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_Fortress_Vader_droid_model) |
| Unidentified Gree Enclave droid model |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_Gree_Enclave_droid_model) |
| Unidentified guard droid | Security |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_guard_droid) |
| Unidentified heavy battle droid model | Droid walker |  |  | Trade Federation | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_heavy_battle_droid_model) |
| Unidentified Imperial assassin droid | Assassin droid; Labor droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_Imperial_assassin_droid) |
| Unidentified Imperial labor droid | Labor droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_Imperial_labor_droid) |
| Unidentified Imperial security droid | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_Imperial_security_droid) |
| Unidentified insectoid droid | Battle | Xylan |  | Xylan | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_insectoid_droid) |
| Unidentified labor droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_labor_droid) |
| Unidentified large-sensored astromech series | Astromech droid |  |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_large-sensored_astromech_series) |
| Unidentified maintenance droid (ML-08) | Repair droid; Utility droid |  |  | Alliance to Restore the Republic; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_maintenance_droid_%28ML-08%29) |
| Unidentified mining droid model | Mining droid / Class five droid |  |  | Kleb Zellock's criminal empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_mining_droid_model) |
| Unidentified monster droid model | Battle droid |  |  | Droid Crush Pirates of Bestoon; Galactic Empire; Droid uprising; Scourge (As a vessel) | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_monster_droid_model) |
| Unidentified probe droid model | Probe droid |  |  | Morgan Elsbeth's forces | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_probe_droid_model) |
| Unidentified probe droid model (Tanay) | Probe droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_probe_droid_model_%28Tanay%29) |
| Unidentified quadrupedal droid model |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_quadrupedal_droid_model) |
| Unidentified rounded-dome astromech series | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_rounded-dome_astromech_series) |
| Unidentified science droid model | Medical droid; Science droid |  |  | Galactic Republic; Jedi Order | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_science_droid_model) |
| Unidentified service droid model | Service |  |  | Galactic Empire; Scourge (As a vessel) | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_service_droid_model) |
| Unidentified spider droid | Battle droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_spider_droid) |
| Unidentified tiered-dome astromech series | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_tiered-dome_astromech_series) |
| Unidentified treaded droid model |  |  |  | Hez's Droid Market | canon |  | [wiki](https://starwars.fandom.com/wiki/Unidentified_treaded_droid_model) |
| Union Sentry Droid | Battle droid | Neimoidian droid factory |  | Confederacy of Independent Systems; HK-47's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/Union_Sentry_Droid) |
| Updated battle droid | Battle droid / Class four droid |  | c. 20 BBY | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Updated_battle_droid) |
| Upgraded battle droid | Battle droid |  | 22 BBY | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/Upgraded_battle_droid) |
| UPR-17 Slicing Droid | Spy |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/UPR-17_Slicing_Droid) |
| USD Class Pulverizer | Battle droid |  |  | HK-47's Droid Army | canon |  | [wiki](https://starwars.fandom.com/wiki/USD_Class_Pulverizer) |
| Util-Tec | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Util-Tec) |
| Uulshos justice droid | Assassin droid / Class four droid | Uulshos Manufacturing |  | Galactic Empire; Iron Knights | canon |  | [wiki](https://starwars.fandom.com/wiki/Uulshos_justice_droid) |
| UX-53 Autopolisher MK.II Droid | Class five droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/UX-53_Autopolisher_MK.II_Droid) |
| Uxiol Droid Manufacturing assault droid | Battle | Uxiol Droid Manufacturing |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Uxiol_Droid_Manufacturing_assault_droid) |
| Uxiol Droid Manufacturing patrol drone | Patrol droid | Uxiol Droid Manufacturing |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Uxiol_Droid_Manufacturing_patrol_drone) |
| V-302 Guard Droid | Security droid / Class four droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/V-302_Guard_Droid) |
| V-359 Guard Droid | Security droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/V-359_Guard_Droid) |
| V-5 transport droid |  |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/V-5_transport_droid) |
| V-828 Clearcutter | Battle droid |  |  | House of Thul | canon |  | [wiki](https://starwars.fandom.com/wiki/V-828_Clearcutter) |
| V-N6 Exterminator Droid | Battle droid |  |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/V-N6_Exterminator_Droid) |
| V-series droid supervisor | Supervisor droid / Class three droid | MerenData |  | Galactic Empire; Scourge | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/V-series_droid_supervisor) |
| V-series pilot droid | Pilot droid | Industrial Automaton |  | Galactic Republic; Corporate Sector Authority; New Republic; Galactic Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/V-series_pilot_droid) |
| V1 pilot droid | Pilot | Industrial Automaton |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/V1_pilot_droid) |
| V2-series commando droid | Battle droid / Class four droid |  |  | Confederacy of Independent Systems | canon |  | [wiki](https://starwars.fandom.com/wiki/V2-series_commando_droid) |
| V5-T transport droid | Loader | Veril Line Systems |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/V5-T_transport_droid) |
| V6-series pilot droid | Astromech droid / Class two droid | Industrial Automaton |  | Alliance to Restore the Republic; Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/V6-series_pilot_droid) |
| Vacuum droid | Cleaning droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Vacuum_droid) |
| Valet droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Valet_droid) |
| Vanguard probot | Probe droid / Class two droid | Arakyd Industries |  | Republic Explorational Corps | canon |  | [wiki](https://starwars.fandom.com/wiki/Vanguard_probot) |
| Variable geometry droid | Pilot |  |  | Galactic Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Variable_geometry_droid) |
| Vet droid | Medical |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Vet_droid) |
| Veterinary droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Veterinary_droid) |
| Vigilant 2X-series picket droid | Fourth Degree | Automata Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Vigilant_2X-series_picket_droid) |
| Vindicator Lockjaw | Guard droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Vindicator_Lockjaw) |
| Viper probe droid | Probe droid | Arakyd Industries | By 19 BBY | Galactic Empire; Second Revelation; New Republic; Imperial holdouts | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Viper_probe_droid) |
| Void-droid |  |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Void-droid) |
| VX series artillery droid | Artillery droid / Class four droid | Czerka Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/VX_series_artillery_droid) |
| W-series droideka | Battle droid | Phlac-Arphocc Automata Industries |  | Trade Federation; Confederacy of Independent Systems | Legends | Droideka + Sharpshooter (JDS + OuterRim) | [wiki](https://starwars.fandom.com/wiki/W-series_droideka/Legends) |
| WA-2G droid | Attendant droid |  |  | Pijali monarchy | canon |  | [wiki](https://starwars.fandom.com/wiki/WA-2G_droid) |
| Wall Crawler Droid | Security droid |  |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Wall_Crawler_Droid) |
| War-robot | Battle droid / Class four droid | Xim the Despot |  | Xim's empire; Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/War-robot) |
| Warbot | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Warbot) |
| Warden 10-24 security droid | Security | Ulban Arms |  | Brakiss | canon |  | [wiki](https://starwars.fandom.com/wiki/Warden_10-24_security_droid) |
| Warden droid | Security *(Legends)* |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Warden_droid) |
| Warrior-priest droid |  |  |  | Second Revelation | canon |  | [wiki](https://starwars.fandom.com/wiki/Warrior-priest_droid) |
| Waste droid | Sanitation |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Waste_droid) |
| Watcher Droid WX | Security droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Watcher_Droid_WX) |
| WB-35 mechanic droid | Maintenance | East Corner Heavy Industry |  | Land & Sky Corporation | canon |  | [wiki](https://starwars.fandom.com/wiki/WB-35_mechanic_droid) |
| WBY series | Educational |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WBY_series) |
| WBY-102 FirstMate | Sailing droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WBY-102_FirstMate) |
| Weapons droid | Battle |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Weapons_droid) |
| WED 15 "Septoid 2" Treadwell toolkit droid | Maintenance droid / Class 5 |  |  | Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/WED_15_%22Septoid_2%22_Treadwell_toolkit_droid) |
| WED Treadwell repair droid | Repair droid / Class 5 | Cybot Galactica |  | Alliance to Restore the Republic; Galactic Empire | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/WED_Treadwell_repair_droid) |
| WED-1016 'Techie' Droid | Maintenance droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WED-1016_%27Techie%27_Droid) |
| WED-15 Septoid Treadwell | Maintenance droid / Class 5 | Cybot Galactica *(Legends)* |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/WED-15_Septoid_Treadwell) |
| WED-15 Treadwell droid | Maintenance droid / Class 5 | Cybot Galactica *(Legends)* |  | Galactic Republic; Plazir-15 government | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/WED-15_Treadwell_droid) |
| WED-15-D3 Treadwell | Maintenance | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WED-15-D3_Treadwell) |
| WED-15-XT Treadwell droid | Maintenance droid / Class 5 | Cybot Galactica |  | Lars family | canon |  | [wiki](https://starwars.fandom.com/wiki/WED-15-XT_Treadwell_droid) |
| WED-20 Treadwell | 1st-degree survey/analysis droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WED-20_Treadwell) |
| WED-500 Treadwell | Hazardous-service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WED-500_Treadwell) |
| WED-600 Treadwell | Hazardous-service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/WED-600_Treadwell) |
| Welding Beetle | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Welding_Beetle) |
| Welding droid | Specialized labor |  |  |  | canon (+Legends) |  | [wiki](https://starwars.fandom.com/wiki/Welding_droid) |
| Wheel medi-droid | Medical droid |  |  | The Wheel | canon |  | [wiki](https://starwars.fandom.com/wiki/Wheel_medi-droid) |
| Wookiee medical droid | Medical droid / Class one | Wookiees |  | Alaris Prime colonists; Alliance to Restore the Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/Wookiee_medical_droid) |
| Worker Droid WX | Battle droid | Okara Droid Company |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Worker_Droid_WX) |
| X-0X unit | Recording droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/X-0X_unit) |
| X-1 Viper | Mechanized armor; Reconnaissance; Walker / Class four droid | Balmorran Arms |  | Balmorran Defense Force; New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/X-1_Viper) |
| X-8 blaster droid | Battle | Galactic Empire |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/X-8_blaster_droid) |
| X-ONK | Battle droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/X-ONK) |
| X10-D draft droid | Draft droid / Class five droid | Hsskor Dominion |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/X10-D_draft_droid) |
| X2-C3 Imperial astromech | Astromech droid / Class two droid | Sith Empire |  | Sith Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/X2-C3_Imperial_astromech) |
| X2-R Lookout Droid | Sentry |  |  | Hutt Cartel | canon |  | [wiki](https://starwars.fandom.com/wiki/X2-R_Lookout_Droid) |
| X4-Z2 Battle Droid | Battle droid / Class four droid |  |  | Exchange | canon |  | [wiki](https://starwars.fandom.com/wiki/X4-Z2_Battle_Droid) |
| Xc-84 Droid | Battle droid |  |  | White Maw | canon |  | [wiki](https://starwars.fandom.com/wiki/Xc-84_Droid) |
| XC2 administration droid | Administrative droid | Cybot Galactica |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/XC2_administration_droid) |
| XLT-014 labor droid | Loader droid / Class 5 | Publictechnic |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/XLT-014_labor_droid) |
| XPLR-R | Prototype exploration droid | Viper Sensor Intelligence Systems |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/XPLR-R) |
| XR-32 hunter droid | Battle droid |  |  | Sith Empire (Post–Great Hyperspace War) | canon |  | [wiki](https://starwars.fandom.com/wiki/XR-32_hunter_droid) |
| XT labor droid | General labor |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/XT_labor_droid) |
| XT-2a Surveyor Droid | Surveyor Droid |  |  | Ayor-v9 | canon |  | [wiki](https://starwars.fandom.com/wiki/XT-2a_Surveyor_Droid) |
| XT-6 droid | Service droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/XT-6_droid) |
| XX-3P0 | Protocol droid |  |  | Uffel droid community | canon |  | [wiki](https://starwars.fandom.com/wiki/XX-3P0) |
| XX-5 Service Droid | Service |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/XX-5_Service_Droid) |
| Y7-O1 Astromech Droid | Astromech droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Y7-O1_Astromech_Droid) |
| Yellow repair droid | Maintenance |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Yellow_repair_droid) |
| YI-5 Surveillance/Interrogation droid | Surveillance/Interrogation droid | Imperial Intelligence |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/YI-5_Surveillance/Interrogation_droid) |
| YOL general worker droid | Labor droid |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/YOL_general_worker_droid) |
| YVH 1 | Battle droid / Class four droid | Tendrando Arms |  | New Republic; Galactic Federation of Free Alliances; Five Worlds; Heritage Council | canon |  | [wiki](https://starwars.fandom.com/wiki/YVH_1) |
| YVH 5-S Bugcruncher | War droid | Tendrando Arms |  | New Republic; Galactic Federation of Free Alliances | canon |  | [wiki](https://starwars.fandom.com/wiki/YVH_5-S_Bugcruncher) |
| YVH S-series war droid | YVH-series battle |  |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/YVH_S-series_war_droid) |
| YVH-M | YVH-series battle |  |  | Galactic Alliance | canon |  | [wiki](https://starwars.fandom.com/wiki/YVH-M) |
| YVH-Series battle droid | Class four droid | Tendrando Arms |  | New Republic | canon |  | [wiki](https://starwars.fandom.com/wiki/YVH-Series_battle_droid) |
| Z-X3 experimental droid trooper | Battle droid / Class four droid | Tagge Company |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/Z-X3_experimental_droid_trooper) |
| Z2-9 Hover Vid-Cam droid | Cam |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Z2-9_Hover_Vid-Cam_droid) |
| Z5 series | Construction |  |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Z5_series) |
| Z65 patrol droid | Security droid / Fourth degree | SoroSuub Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Z65_patrol_droid) |
| Z7 series | Construction droid / Class five droid | Structgalactis, Inc. |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/Z7_series) |
| ZH-28 guard | Security droid | Stonewall Labs |  | Stonewall Labs | canon |  | [wiki](https://starwars.fandom.com/wiki/ZH-28_guard) |
| ZQ Infantry Support Unit | Battle droid | Sienar Intelligence Systems |  | Galactic Empire | canon |  | [wiki](https://starwars.fandom.com/wiki/ZQ_Infantry_Support_Unit) |
| ZX-10 Combat Droid | Battle droid | Czerka Corporation |  |  | canon |  | [wiki](https://starwars.fandom.com/wiki/ZX-10_Combat_Droid) |
| ZZ-model droid |  |  |  | Jedi Order | canon |  | [wiki](https://starwars.fandom.com/wiki/ZZ-model_droid) |

