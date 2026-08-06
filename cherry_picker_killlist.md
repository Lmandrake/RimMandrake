# Cherry Picker Kill-List — Gravship Expedition (DRAFT / candidate)

_What we likely want **Cherry Picker** (WS 3521312241) to delete from generation + menus, so a large library still presents a small, coherent "crashed Factory ship / Jawa stowaways" surface. This is the mechanical form of the 7-question test and the anti-exponential principle: the library can be big, but the **gameplay surface** stays curated. Companion tool: **Faction Filter / Sensible Factions** (WS 3531306011) for controlling *spawns* (see the division-of-labor note below)._

**Status:** DRAFT. Every specific defName below is a **candidate to confirm against installed files** — do NOT feed guessed defNames to Cherry Picker. Per the campaign's engineering rules ("confirm every defName from installed files; never guess"), treat entries tagged 🔎 as "find the real defName in the Cherry Picker UI first." Cherry Picker reads live defs and lists them for you, so this is a menu-checklist, not a hand-authored XML file.

**Last updated:** 2026-08-02

---

## Division of labor — which tool does what (read first)

Two tools overlap; use the right one so you don't fight yourself:

- **Faction Filter (Sensible Factions)** → controls which factions *spawn* in a world. Reversible, allow-list style. Use this as the **first pass** for factions — allow-list the SW cast, suppress the rest. Nothing is destroyed.
- **Cherry Picker** → *deletes the def* from generation AND from all menus/pickers entirely. Use this for things you never want to see *anywhere* (off-theme xenotypes cluttering the pawn editor, competing scenarios in the picker, off-theme genes in the gene assembler, off-theme content in the architect menu).
- **Rule of thumb:** if you might want it *sometimes* (a faction that could be an occasional trader), filter it. If it's pure off-theme clutter that breaks the fiction (a fantasy dragon race, a vanilla scenario you'll never pick), Cherry Pick it.

**⚠️ Two hard cautions before deleting anything:**
1. **Don't delete a def another mod hard-depends on.** Cherry Picker can remove a ThingDef/GeneDef that a XenotypeDef or RecipeDef references, causing red errors. Delete the *top-level* thing (the xenotype, the faction, the scenario) and let its private sub-defs fall out of use, rather than surgically deleting a shared gene another race needs. Test on a throwaway world and read `Player.log`.
2. **Cherry Picker is applied at generation.** Removing a scenario/xenotype after a save already uses it can break that save. Set the kill-list at campaign start (same discipline as Ancient Urban Ruins Hit Point).

---

## 1. Scenarios — narrow the picker to our start (HIGH confidence, clean)

**Intent:** the scenario picker should offer essentially ONE thing — our crashed-Factory-ship start — the way Samuel deletes 12 ScenarioDefs so the player can't wander off-theme. This is the safest, highest-value Cherry Picker use (scenarios have few inbound dependencies).

- 🔎 Delete vanilla `Crashlanded`, `RichExplorer`, `LostTribe`, `NakedBrutality`, `TheAnomaly` (Anomaly is benched anyway) — EXCEPT whichever base we build our start on top of. **Decision needed:** do we author our start as a *starting save* (then we can delete ALL vanilla scenarios) or as a scenario-def derived from one vanilla base (then keep that ONE)? See required_mods.md scenario-as-save decision.
- 🔎 Delete scenario defs dragged in by content mods (Alpha Biomes, Vanilla Quests Expanded modules, Outer Rim, etc.) that aren't our start.
- **Keep:** our authored start only. **Confidence:** HIGH. **Pillar:** subtractive theming — the world's first choice is on-theme.

---

## 2. Xenotypes — delete off-theme, keep the SW roster (MEDIUM — judgment calls)

**Intent:** the pawn/xenotype menus should show the Star Wars roster (Jawa via Outer Rim Galactic Diversity; Hutts/Twi'leks/Gungans/Mon Cal etc. via Star Wars Xenotypes), NOT RimWorld-native xenohumans that break the fiction. This is exactly what Samuel does (Gravtasm deletes 26 XenotypeDefs).

**High-confidence kills (break SW fiction hardest):**
- 🔎 **Sanguophage** — psychic space-vampires clash hard with a grounded-SW scrapper world, and they trail deathrest/hemogen mechanics that flirt with a parallel progression system. Strong delete candidate. **Pillar:** theme coherence + anti-exponential (removes a whole hemogen sub-economy from temptation).
- 🔎 Alpha Genes / other-mod fantasy xenotypes if any get dragged in (dragons, elves, etc.) — delete on sight; wrong universe.

**DECIDED (user, 2026-08-02) — vanilla xenohumans to KEEP + reflavor as SW species:**
- 🔎 **Yttakin → Wookiee-kin** (large, hairy, cold-hardy brute — the big-species stand-in; Wookiee/Talz/Whiphid flavor).
- 🔎 **Pigskin → Gamorrean** (pig-like, tough, ugly — near 1:1 on Gamorrean guards).
- 🔎 **Genie → savant caste** (brilliant, frail — Imperial-court protocol advisors/savants).
- 🔎 **Neanderthal → brute species** (strong, primitive — Nikto/Weequay merc/laborer stock).
- 🔎 **Impid → desert alien** (fast, heat-loving, fire-spitting — Tatooine-style desert world fit).

**DECIDED — Cherry-Pick OUT (delete these vanilla/mod xenotypes):**
- ✅ **Force Gremlin** — FORBID (user, 2026-08-06). Delete both confirmed Galactic-Diversity xenotypes: **`OuterRim_ForceGremlin`** + **`OuterRim_ForceGremlinTribal`** ([SRC-AUDITED] in `Xenotype_ForceGremlin.xml`). Reason: a Force-touched gremlin race muddies the finalized NPC-only Force gate (dark→Empire Sith-races, light→rare Moisture-Farmer Jedi, none for anyone else). Removing it keeps the Force strictly a faction-restricted signature, not an ambient xenotype anyone can roll. **Caution:** delete at the xenotype level; the mod patches it into pawnkinds via `PawnKindPatches.xml`, so also confirm no kept pawnkind hard-refs it (read `Player.log` on a throwaway world).
- 🔎 **Dirtmole** — cut (miner flavor not wanted in the kept set).
- 🔎 **Highmate** — cut (consort caste; user did not keep it).
- 🔎 **Waster** — cut (toxic/pollution flavor reads Fallout, weakest SW fit).
- 🔎 **Sanguophage** — cut (psychic space-vampire breaks SW fiction + trails a hemogen/deathrest sub-economy = anti-exponential risk).
- 🔎 Any fantasy/wrong-universe xenotypes dragged in by the large library (dragons, elves, etc.) — cut on sight.

- **Keep always:** Jawa + all Star Wars Xenotypes + the 5 reflavored vanilla races above. **Baseliner** stays (default humans).
- **Confidence:** DECIDED. **Caution:** deleting a xenotype is safe; deleting the *genes* under it is where dependency errors appear — delete at the xenotype level. The kept reflavor is a NAMING/lore exercise (no def change needed to keep them; reflavor via labels/RP, optionally a light HAR/xenotype-description patch).
- **Full size spectrum (DECIDED):** user wants dedicated very-large + very-small race mods added so body-size genes (incl. the Jawa's small stature) are richly in the gene pool. Candidates being researched via Fetcher (`2026-08-02_jawa_flavor_tech_and_races`). This is additive (required_mods.md), not a Cherry Picker kill item.

---

## 3. Factions — mostly Faction Filter's job; Cherry Pick only the clashers (MEDIUM)

**Intent:** Faction Filter does the allow-listing (SW factions in, rest suppressed). Cherry Picker only for factions you want *gone from menus entirely* or that create naming/lore collisions.

- ✅ **Two-Empires — RESOLVED BY FUSION (user, 2026-08-02), NOT deletion.** Both Empires stay. Narrative: **the vanilla Royalty Empire = the Galactic Empire's aristocratic/noble core** (Moffs, sector governors, noble houses — SW is full of local aristocrats); **the Outer Rim Galactic Empire = its military/troops.** ONE unified Empire-and-pursuer drawn from two mod sources. This supersedes the earlier "suppress the vanilla Empire" recommendation — do NOT Cherry Pick or Faction-Filter-out either Empire. Keeps all Royalty quest/trader/techprint hooks intact (the Configurable Techprints path needs Royalty).
  - **Reflavor mechanism (feasibility check owed):** giving Imperial nobles varied alien races may need a pawnkind/xenotype patch — Royalty pawnkinds have their own generation rules, so it may not be a simple toggle. **Fallback if a per-noble guarantee is hard:** varied races exist in the world and appear among Imperials naturally (not every noble guaranteed exotic). Verify before committing.
  - Titles/permits/honor reskinned to Imperial ranks (Moff/Governor/Grand Moff) — pure labels, zero mechanical cost. (Royalty stays NON-progression for the player per forbidden_mods.md — reflavor is about the *faction*, not opening a player title ladder.)
- 🔎 Delete pure off-theme faction defs dragged in by biome/content mods that Faction Filter can't cleanly suppress (fantasy/insectoid/wrong-universe factions from any large-library additions).
- **Keep:** Outer Rim Empire, Separatists, and the SW faction roster (we WANT full diversity as live enemies — required_mods.md).
- **Confidence:** MEDIUM.

---

## 4. Weapons / apparel / recipes — LINKED to open audits (LOW confidence / deferred)

**Intent:** these overlap two decisions that aren't closed yet — don't act until they are.

- 🔎 **Lightsaber craft recipe** — already DECIDED (required_mods.md): disable the basic component-bench craft recipe so lightsabers are quest/loot only. Cherry Picker deleting that **RecipeDef** is one clean way to enforce it. **Confidence:** HIGH on intent, 🔎 on the exact recipe defName. **Pillar:** §19.5 no player arms race.
- 🔎 **Vanilla weapons/apparel** — only relevant if we adopt the NoVanillaWeapons/NoVanillaApparel "immersion by amputation" trick, which is **deferred pending the Outer Rim weapon-balance audit (§19.5)**. If we go that route, Cherry Picker could delete vanilla weapon ThingDefs instead of running the separate No-Vanilla mods. **Do NOT do this yet** — blocked on the audit. **Confidence:** LOW / deferred.
- 🔎 **Stat-creep SW gear** — any Outer Rim/KotOR weapon flagged as a power-creep outlier by the §19.5 audit becomes a Cherry Picker delete candidate. Blocked on the audit.

---

## 4b. ~~VFE-Ancients player POWERS ladder~~ — 🪦 RETIRED (Ancients dropped, user 2026-08-03)

**Nothing to do here. Both VFE-Ancients (WS 2654846754) and its 1.6 successor VQE-Ancients (WS 3618306875) were DROPPED from the mod list entirely** (user decision 2026-08-03 — the mod was only ever adopted for the Supply Slingshot, which the 1.6 successor deleted; see required_mods.md "ANCIENTS — DROPPED ENTIRELY").

With no Ancients mod installed there is **no archite-power system to Cherry-Pick** — the old target `VFEA_GeneTailoringPod` (and its successor `VQEA_ArchogenInjector`) do not exist in the stack. If "powered" enemy raiders are wanted for danger, that comes from **CAI-5000** + the **Star-Wars-faction roster**, not from an Ancients module. This section is kept as a tombstone for provenance only.

## 5. Off-theme buildings / research / genes clutter (LOW — polish pass)

**Intent:** last-pass tidying once the big library is assembled; purely quality-of-surface.

- 🔎 Delete off-theme **architect-menu buildings** from large content packs that clutter the build menu without serving the theme (judgment call, low stakes — cosmetic clutter, not a pillar risk).
- 🔎 Delete off-theme **GeneDefs** ONLY if they appear as clutter in a gene menu we actually use — but remember genetics-lab use is forbidden anyway (Outland Genetics is a passive library), so this menu may barely be touched. Low priority.
- **Confidence:** LOW. Do this last, or skip.

---

## Priority order (do them in this sequence)

1. **Scenarios** (§1) — highest value, lowest risk, most Samuel-like.
2. **Faction Filter pass** (allow-list SW cast) — before any faction Cherry Picking.
3. **Xenotypes** (§2) — delete the fiction-breakers, decide the judgment-call set.
4. **Two-Empires decision** (§3) — resolve with option (c) unless a reason to delete.
5. **Lightsaber recipe** (§4) — enforce the already-made decision.
6. ~~**VFE-Ancients player powers** (§4b)~~ — 🪦 RETIRED; Ancients dropped from the mod list entirely (user 2026-08-03). No step here.
7. **Deferred:** vanilla-weapon deletion + stat-creep gear (§4) — AFTER the §19.5 audit.
8. **Polish** (§5) — optional, last.

## Open decisions this list surfaces
- **Scenario-as-save vs scenario-def** (governs how aggressively §1 can delete vanilla scenarios).
- **Two-Empires** resolution (§3) — verify the vanilla Royalty Empire isn't load-bearing for the Techprints path before deleting; lean to Faction-Filter-suppress instead.
- **Xenotype keep/reflavor set** (§2) — pure taste; needs your call on how "pure SW" vs "populated galaxy" the roster should feel.
- **NoVanillaWeapons route** (§4) — still blocked on the Outer Rim weapon-balance audit (§19.5).

_When we build for real: open Cherry Picker in a throwaway 1.6 world with the full intended library loaded, walk this list top-to-bottom confirming each real defName, then read `Player.log` for any dependency red-errors before committing to the campaign save._
