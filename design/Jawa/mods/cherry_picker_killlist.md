<!-- status: live -->
> "Faction Filter" never existed; the live equivalents are **Sensible Factions** (3531306011) and **Faction Control** (2882785581), both active.

# Cherry Picker Kill-List — Gravship Expedition (DRAFT / candidate)

_What we likely want **Cherry Picker** (WS 3521312241) to delete from generation + menus, so a large library still presents a small, coherent "crashed Factory ship / Jawa stowaways" surface. This is the mechanical form of the 7-question test and the anti-exponential principle: the library can be big, but the **gameplay surface** stays curated. Companion tool: **Sensible Factions (3531306011) / Faction Control (2882785581) / Sensible Factions** (WS 3531306011) for controlling *spawns* (see the division-of-labor note below)._

**Status:** DRAFT. Every specific defName below is a **candidate to confirm against installed files** — do NOT feed guessed defNames to Cherry Picker. Per the campaign's engineering rules ("confirm every defName from installed files; never guess"), treat entries tagged 🔎 as "find the real defName in the Cherry Picker UI first." Cherry Picker reads live defs and lists them for you, so this is a menu-checklist, not a hand-authored XML file.

**Last updated:** the §0 inbox is appended continuously — check the newest entry's
date, not a header field. The categorised sections below (§§1–5) were last worked
**2026-08-02**; treat them as a plan of that date, not as current.

---

# 0. 📥 THE INBOX — append here the moment you notice something

**Created 2026-08-12 by a retired seat at the owner's request. BUILD owns this file and
maintains it from here** (`design/Jawa/mods/` per `infrastructure/agents/BUILD.md`).

**Why an inbox and not just the categorised lists below:** §§1–5 are a *plan* —
producing an entry there costs a pass. This is a *capture log*, and it exists for
the same reason `traps.md` does: **a cull you notice mid-task and do not write
down is one you pay full price to rediscover.** There is a lot of content in this
stack and most of what will not make the cut gets noticed in passing, while doing
something else.

**Cost of an entry: one line.** Do not categorise, do not verify the defName, do
not check dependencies. Just capture what you saw and why. Sorting and verifying
is a later pass — that is the whole point.

### ⚠️ Two buckets, and they are NOT interchangeable

Keep these separate from the first entry. They differ in *reversibility*, and
mixing them invites someone to action an irreversible cull as casually as a
reversible one.

| | mechanism | reversible? |
|---|---|---|
| **A · Drop the whole mod** | `ModsConfig.xml` / unsubscribe | ✅ **Yes.** Cheap, undo any time. |
| **B · Cull a def** | Cherry Picker — deletes it from generation **and** every menu | ⛔ **NO.** `design/Jawa/build_plan.md` Tier ① is explicit: *"the most irreversible tier — get it right once, then freeze it."* **Cannot be changed mid-save.** |

**Before actioning anything in bucket B**, read the two hard cautions in
"Division of labor" below — chiefly: delete the *top-level* thing (the xenotype,
the faction, the scenario) and let its private sub-defs fall out of use. Never
surgically delete a shared def another mod hard-depends on.

**Also consider bucket A′ — suppress instead of delete.** Sensible Factions /
Faction Control can stop a faction *spawning* without destroying anything. If you
might want it sometimes, filter it; only Cherry Pick pure off-theme clutter.

---

## §0.A — Whole-mod drop candidates

| mod | packageId | why | noticed |
|---|---|---|---|
| ~~**Alpha Vehicles – Neolithic**~~ | `sarg.alphavehiclesneolithic` | ⛔ **WITHDRAWN by the owner, 2026-08-12 — do not drop.** I filed it as off-theme ("a dog sled is a category error, not a reskin problem"). The owner's ruling is the opposite: **reskin it, horses → Banthas**, filed for BUILD in `design/V2_DREAMS.md` §0c. Recorded rather than deleted because the disagreement is the useful part — I judged the theme gap unbridgeable by art, and that call was not mine to make. | filed 2026-08-12 by a retired seat · withdrawn same day |
| **More Faction Interaction (Continued)** | `mlie.morefactioninteraction` | **10 assemblies and 114 defs of interaction content, and zero faction-*definition* capability** — it buys nothing for the faction work (Stage 1 mod survey; `design/V2_DREAMS.md` **B20**). Keep only if the interaction content is wanted on its own merits. | 2026-08-12, a retired seat, Stage 1 mod survey |

## §0.A′ — Suppressed instead of culled: **PROVEN**, with a third mechanism

_A′ was a theoretical option in this file until 2026-08-12. It is now demonstrated
end to end, and by a mechanism not listed above._

| mod | what was done | verified |
|---|---|---|
| **Outer Rim – Rebel Alliance** (`neronix17.outerrim.rebelalliance`) | Kept, enabled, **faction suppressed by a direct `FactionDef` patch** — `src/Jawa/Jawa_Patches/Patches/RebelAlliance_Suppress.xml` zeroes `requiredCountAtGameStart` (1→0), `settlementGenerationWeight` (0.3→0), `canMakeRandomly` (true→false), `maxConfigurableAtWorldCreation` (9999→0). | **0** instantiated `<def>OuterRim_RebelAlliance</def>` in a world of **55** factions, against 3 control factions at 1 each. `OuterRim_A280Blaster` present **5×** in the same world. |

**⚠️ The third mechanism.** The A′ note above names Sensible Factions / Faction
Control. There is a **fourth column on that spectrum** and it is the cheapest of
all: a four-op XML patch on the FactionDef itself. No manager, no settings UI, no
extra mod, and it is **as reversible as bucket A** — delete one file and redeploy.
Reach for it when the faction is the only thing you want gone and the mod's
*content* is the reason you subscribed.

**⚠️ Retune, never delete the FactionDef.** `ScenarioDefs/Scenario_Rebel.xml:115`
references it by name; removing the def would trade a world-map annoyance for a
`Could not resolve cross-reference` on every launch. Zeroing the numbers leaves
every reference intact. This is the same "delete the top-level thing" caution
below, arriving from the opposite direction — sometimes the top-level thing is
load-bearing and the *fields* are what you want.

**⚠️ Scope, stated because the measurement reads broader than it is.** That
result proves suppression at **world generation** — the world was rolled with the
patch already live. It says nothing about a world generated *before* the patch
existed. For an existing save the threat is different: `requiredCountAtGameStart=1`
makes RimWorld **top up missing required factions on load**, not only at worldgen.
That field now reads 0 in the live dump, so it cannot fire — but that is reasoning
until someone greps a loaded-and-resaved campaign file.

**⚠️ How to check, because the obvious grep lies.** Count `<def>NAME</def>`, never
the bare defName: a plain `grep -c OuterRim_RebelAlliance` returns **1** on a world
that does **not** contain the faction, because the def-name registry lists it next
to `OuterRim_RebelPlayerFaction`. And always run controls — a zero from a broken
query looks exactly like a zero from a suppressed faction.

## §0.B — Def-level cull candidates (⛔ irreversible — verify before actioning)

_Format:_ `| def / group | mod | why | noticed |`

### ⭐ Vanilla Vehicles Expanded — 12 of 23 vehicles cut (owner, 2026-08-12)

**defNames verified against the 21:09 live dump, not guessed.** All are
`VVE_<name>`; each also ships a `VVE_<name>_Blueprint` pair that must go with it.

| # | vehicle | defName | type | size |
|---|---|---|---|---|
| 1 | Dinghy | `VVE_Dinghy` | **Sea** | 2×4 |
| 2 | Trawler | `VVE_Trawler` | **Sea** | 2×5 |
| 3 | Mosquito | `VVE_Mosquito` | **Air** | 2×5 |
| 4 | Smuggler | `VVE_Smuggler` | **Air** | 3×6 |
| 5 | Warbird | `VVE_Warbird` | **Air** | 5×5 |
| 6 | Charley | `VVE_Charley` | Land | 1×1 |
| 7 | Dirtbike | `VVE_Dirtbike` | Land | 1×1 |
| 8 | Mule | `VVE_Mule` | Land | 2×4 |
| 9 | Traveller | `VVE_Traveller` | Land | 2×4 |
| 10 | Wagon | `VVE_Wagon` | Land | 2×4 |
| 11 | Roadrunner | `VVE_Roadrunner` | Land | 2×5 |
| 12 | Snatcher | `VVE_Snatcher` | Land | 2×5 |

**Patterns worth checking against intent** — stated as observations, not as
reasons the owner gave:

* **Both Sea vehicles are cut.** Self-evidently right on a desert world.
* **3 of 5 Air are cut**, but `VVE_Frog` and `VVE_Toad` (both Air) survive. So
  this is not "cut all aircraft" — worth confirming Frog and Toad are meant to
  stay, given `desert_world_design.md` §4-Orbital makes the sky a hostile ceiling.
* **All 7 armed vehicles survive** (`Bunsen`, `Highwayman`, `Roadkill`,
  `Scytheman`, `Toad`, `Bulldog`, `Tango` — the ones with `_MainTurret` defs).
  Everything cut is unarmed.
* **Remaining 11:** Bang Bus, Bulldog, Bunsen, Frog, Highwayman, Prowler,
  Roadkill, Scytheman, Tango, Toad, Wisent.

⚠️ **DEPENDENCY WARNING — do not Cherry Pick these blind.** Every one of the 12
is referenced from **six other def types**: `DesignationCategoryDef`,
`PawnKindDef`, `RecipeDef`, `ResearchProjectDef`, `ThingCategoryDef`,
`VehicleStatDef`. Most of those are near-certainly VVE's own paired defs —
Vehicle Framework generates a `PawnKindDef` per vehicle, since vehicles *are*
pawns — but **that is inference, not verified**, and this is the irreversible
bucket. Confirm before actioning.

⭐ **CHEAPER, REVERSIBLE ROUTE — consider before Cherry Picking.** If the goal is
"the player cannot build these", clearing `<designationCategory>` by
`PatchOperation` takes them out of the architect menu while leaving every def and
reference intact. That technique is already used in this project by
`Jawa_Doctrine/Patches/NoDroidManufacture.xml` and is documented as the cheap
lever for Mines 2.0. It is **as reversible as bucket A** — delete one file and
redeploy — and it cannot orphan a cross-reference. Cherry Pick only if they must
be gone from *every* menu and from generation, not merely unbuildable.

---

## Division of labor — which tool does what (read first)

Two tools overlap; use the right one so you don't fight yourself:

- **Sensible Factions (3531306011) / Faction Control (2882785581) (Sensible Factions)** → controls which factions *spawn* in a world. Reversible, allow-list style. Use this as the **first pass** for factions — allow-list the SW cast, suppress the rest. Nothing is destroyed.
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
- 🔎 **Pigskin → Gamorrean** (pig-like, tough, ugly — near 1:1 on Gamorrean guards). **DECIDED (user, 2026-08-06): author a CUSTOM Gamorrean race derived from Pigskin** — not just a label swap; we build our own xenotype (Pigskin as the mechanical base, tuned to taste) as the Hutts' pig-soldier stock.

**GENERAL LICENSE (user, 2026-08-06): we may freely TWEAK/REFLAVOR any Star Wars race into our own custom version.** We are NOT bound to ship the Galactic Diversity / vanilla xenotypes as-is — any of them can be adjusted (stats, genes, labels, lore) or forked into a bespoke race when it serves the campaign. The roster below is a starting palette, not a fixed contract.
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

**✅ VERIFIED IN-HAND RACE INVENTORY (on disk 2026-08-06 — this is the authoritative "what we actually have" list).** Enumerated against Outer Rim – Galactic Diversity 1.6 (all 54 shipped xenotype defs) + the bundled Chiss submod; the 5 reflavor bases are vanilla Biotech DLC xenotypes (base-game art). Every entry below has BOTH a def AND shipped art:
  - **Baseline:** Human (baseliner) — always present, the default galaxy stock.
  - **Player/core:** Jawa (no Force, ever).
  - **Star Wars species — denominator: the 42 species shipped by *Outer Rim – Galactic Diversity*, counted on disk 2026-08-06.** ⛔ Not the 44-xenotype art-audit subset (`design/Jawa/art/graphics_overhaul_protocol.md`), not the 70-xenotype BTD roster, not the 79 mechanically distinct species across all mods — four different populations, do not force them together. The 42: Sith, Massassi, Dathomirian, Miraluka, Twi'lek, Togruta, Iridonian (Zabrak), Chiss, Duros, Bith, Bothan, Cathar, Cerean, Chagrian, Devaronian, Gungan, Herglic, Iktotchi, Ithorian, Kaleesh, Kaminoan, Mirialan, Mon Calamari, Neimoidian, Nikto, Pantoran, Pyke, Quarren, Rakata, Rodian, Selkath, Sullustan, Trandoshan, Umbaran, Zeltron, Abednedo, Arkanian, Aqualish, Ewok, Geonosian, Tusken, Wookiee.
  - **Reflavored vanilla Biotech xenotypes (base-game art, relabeled/tuned):** Gamorrean ← Pigskin (custom-authored on the Pigskin base), Wookiee-kin ← Yttakin, Savant caste ← Genie, Brute stock ← Neanderthal, Desert alien ← Impid.
  - **❌ NOT available — do NOT plan around these:** **Skakoan** (no xenotype, no art — the faction-roster-v2 doc assumed it; it doesn't ship, and its sealed-suit/pressure-suit mechanic is DROPPED), **Houk** (no xenotype, no art), **Ghorfa** (not a race — only a lore line inside the Tusken description), **Force Gremlin** (on disk but Cherry-Picked out per above), and the disabled WIP files (`.xml.dis`, not active): **Chadra-Fan, Echani, Feeorin, Ishi Tib, Thyrsian**. Canon names (Skakoan/Houk/Ghorfa/Klatooinian/Vodran/Arkanian-Offshoot) are only adoptable as cosmetic text labels over existing art — never as new races, never adding a dependency.
  - _This inventory supersedes the former standalone `races.md` (Desktop), which was folded in here 2026-08-06 as the single source of truth._
  - 📐 **SCALE + VISUAL REFERENCE (added 2026-08-11): `research/Jawa/star_wars_species_scale_reference_atlas.pdf`.** This section owns *which* races we have; the atlas owns *how big they are and what they look like* — 46 species, one page each, sourced reference art plus a canonical height range normalised against a 1.80 m human. Check it before authoring or rebalancing any race's body-size genes. It is already load-bearing: the atlas puts **Gamorrean at 1.3–1.6 m — shorter than a human** — which contradicts the "hulking brute" framing our `Jawa_Xeno_Gamorrean` inherited from upstream (it carries `guy762_BodySizeGene_big`). Unresolved; see the note in `src/Jawa/Jawa_Patches/Defs/XenotypeDefs/GamorreanXenotype.xml`.
- **Confidence:** DECIDED. **Caution:** deleting a xenotype is safe; deleting the *genes* under it is where dependency errors appear — delete at the xenotype level. The kept reflavor is a NAMING/lore exercise (no def change needed to keep them; reflavor via labels/RP, optionally a light HAR/xenotype-description patch).
- **Full size spectrum (DECIDED):** user wants dedicated very-large + very-small race mods added so body-size genes (incl. the Jawa's small stature) are richly in the gene pool. Candidates being researched via Fetcher (`2026-08-02_jawa_flavor_tech_and_races`). This is additive (required_mods.md), not a Cherry Picker kill item.

---

## 3. Factions — mostly Sensible Factions (3531306011) / Faction Control (2882785581)'s job; Cherry Pick only the clashers (MEDIUM)

**Intent:** Sensible Factions (3531306011) / Faction Control (2882785581) does the allow-listing (SW factions in, rest suppressed). Cherry Picker only for factions you want *gone from menus entirely* or that create naming/lore collisions.

- ✅ **Two-Empires — FUSION, NOT deletion (user).** Both Empires stay. Narrative: **the vanilla Royalty Empire = the Galactic Empire's aristocratic/noble core** (Moffs, sector governors, noble houses — SW is full of local aristocrats); **the Outer Rim Galactic Empire = its military/troops.** ONE unified Empire-and-pursuer drawn from two mod sources. Do NOT Cherry Pick or Faction-Filter-out either Empire. Keeps all Royalty quest/trader/techprint hooks intact (the Configurable Techprints path needs Royalty).
  - **Reflavor mechanism (feasibility check owed):** giving Imperial nobles varied alien races may need a pawnkind/xenotype patch — Royalty pawnkinds have their own generation rules, so it may not be a simple toggle. **Fallback if a per-noble guarantee is hard:** varied races exist in the world and appear among Imperials naturally (not every noble guaranteed exotic). Verify before committing.
  - Titles/permits/honor reskinned to Imperial ranks (Moff/Governor/Grand Moff) — pure labels, zero mechanical cost. (Royalty stays NON-progression for the player per forbidden_mods.md — reflavor is about the *faction*, not opening a player title ladder.)
- 🔎 Delete pure off-theme faction defs dragged in by biome/content mods that Sensible Factions (3531306011) / Faction Control (2882785581) can't cleanly suppress (fantasy/insectoid/wrong-universe factions from any large-library additions).
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

> 🔴 **CORRECTION 2026-08-20 — half of the sentence below is false.** `vanillaquestsexpanded.ancients` (WS `3618306875`) **IS in the 578 `activeMods`**
> and ships **428 `VQEA_*` records** in the 2026-08-20 def dump, `VQEA_ArchogenInjector` among them. ✅ The **VFE-Ancients** half is correct: WS 2654846754 is
> deprecated at 1.5 and is not installed, so `VFEA_GeneTailoringPod` genuinely does not exist. ⚠️ This section's *retirement* is therefore **reopened as a
> question, not as work**: if the archite-power ladder is to stay out of player hands, VQE-Ancients is loaded and there IS something to Cherry-Pick.
> Whether the mod stays at all is the **owner's** mod-list call. Same correction filed at `design/Jawa/mods/required_mods.md` §ANCIENTS.

**Nothing to do here. ~~Both~~ VFE-Ancients (WS 2654846754) ~~and its 1.6 successor VQE-Ancients (WS 3618306875)~~ ~~were~~ was DROPPED from the mod list entirely** (user decision 2026-08-03 — the mod was only ever adopted for the Supply Slingshot, which the 1.6 successor deleted; see required_mods.md "ANCIENTS — DROPPED ENTIRELY").

~~With no Ancients mod installed there is **no archite-power system to Cherry-Pick** — the old target `VFEA_GeneTailoringPod` (and its successor `VQEA_ArchogenInjector`) do not exist in the stack.~~ **Corrected 2026-08-20:** `VFEA_GeneTailoringPod` does not exist (VFE-Ancients absent, as stated). `VQEA_ArchogenInjector` **does** — VQE-Ancients is active. The archite-power system is in the stack. If "powered" enemy raiders are wanted for danger, that comes from **CAI-5000** + the **Star-Wars-faction roster**, not from an Ancients module. This section is kept as a tombstone for provenance only.

## 5. Off-theme buildings / research / genes clutter (LOW — polish pass)

**Intent:** last-pass tidying once the big library is assembled; purely quality-of-surface.

- 🔎 Delete off-theme **architect-menu buildings** from large content packs that clutter the build menu without serving the theme (judgment call, low stakes — cosmetic clutter, not a pillar risk).
- 🔎 Delete off-theme **GeneDefs** ONLY if they appear as clutter in a gene menu we actually use — but remember genetics-lab use is forbidden anyway (Outland Genetics is a passive library), so this menu may barely be touched. Low priority.
- **Confidence:** LOW. Do this last, or skip.

---

## Priority order (do them in this sequence)

1. **Scenarios** (§1) — highest value, lowest risk, most Samuel-like.
2. **Sensible Factions (3531306011) / Faction Control (2882785581) pass** (allow-list SW cast) — before any faction Cherry Picking.
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
