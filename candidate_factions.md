# candidate_factions.md — Race-based faction candidates (the expansion cast)

_Companion to `faction_dossiers.md` (the 4 decided factions). This doc proposes **additional** factions built from the Star Wars races the mod actually ships, grounded in (a) the **verified xenotype gene data** read from Outer Rim Galactic Diversity's 1.6 source on disk, and (b) **canonical SW lore**. Status: DRAFT 2026-08-05, UPDATED 2026-08-05 with the Fetcher sweep._

**Evidence tiering:** [GENE] = verified in the mod's 1.6 GeneDefs on disk · [CANON] = well-established SW lore (high-confidence from knowledge; Wookieepedia fetches were 403-blocked so not citation-backed — see note below) · [WS-CONFIRMED] = a Workshop mod verified to exist in the 2026-08-05 sweep · [DESIGN] = my proposed authoring · [LOCKED] = already-decided in our docs.

> **⚠️ SWEEP UPDATE (2026-08-05) — a premise shifted.** The full Outer Rim *series* and other authors ship several of these factions **prebuilt** (not just the 3 modules on disk). Two big consequences: (1) **Tuskens are already a faction** (Outer Rim – Tatooine addon) → §1 moves from "author from scratch" to "adopt + §19.5-audit." (2) The **Sith Order** is a prebuilt faction in JodemLee/TheForce_Psycast → a possible donor for the Empire's Sith-elite ranks. Full module enumeration + all Workshop IDs now live in `required_mods.md` (§"OUTER RIM SERIES — FULL MODULE ENUMERATION"). **Canon note:** the 16 Wookieepedia fetches all returned HTTP 403 (fandom blocks bots), so `[CANON-VERIFY]` flags are resolved from reliable knowledge and re-tagged `[CANON]`, NOT from citable fetched pages; if you want sources on record I can re-file via a mirror or you can paste pages.

---

## 0. What the two directives already settled (the roster math)

Your two rulings (2026-08-05) consolidated several races *into* the existing four factions rather than spawning new ones — this is good, it prevents faction-sprawl:

- **Sith / Massassi / Dathomirian-Nightsister / Miraluka** → **elite ranks of the Empire** (its DARK-side Force-user tier — VPE dark tree: lightning + telekinetic throw + fear; Miraluka lean light/neutral), NOT a faction. [folded into `faction_dossiers.md` §1]
- **Nikto / Weequay / Rodian / Trandoshan / Pyke** → **rank-and-file muscle of the Hutt-lord factions**, NOT standalone factions. [folded into §2]
- **Rare Jedi hero → Moisture Farmer factions** [user directive 2026-08-06]: the light side lives NOT in a Jedi faction but as an *uncommon* (low pawnGroupMaker weight) Force-user seeded into the existing Moisture-Farmer/settler factions of the world — curated VPE **light/telekinesis** set (heal, push/pull, non-lethal disable, deflection). Neither the player nor the Jawa ever gets the Force. [folded into `faction_dossiers.md` §1 + `required_mods.md` "THE FORCE SYSTEM — FINALIZED"]

So the question this doc answers is narrower and cleaner: *which remaining races are canonically their **own** autonomous societies* — not Imperial, not Hutt underlings — and therefore earn a faction slot of their own? Four candidates clear that bar. A fifth (Pyke) is a judgment call I flag explicitly.

---

## 1. TUSKEN RAIDER CLANS — the native desert xenophobes ⭐ strongest candidate — NOW: ADOPT, don't author

> **✅ SWEEP FINDING — this faction already exists.** [WS-CONFIRMED] **Outer Rim – Tatooine (Continued)** (WS 2390805026) ships the **Tusken Raider race + Jawa race** plus their weapons (Tusken **Cycler**, **Gaderffii**, Jawa **Ion Blaster**) and apparel (Tusken Wrappings/Garments, Jawa Robe). Crucially, **the faction itself is packaged as a SEPARATE opt-in addon mod** so you choose whether it spawns — exactly the modular control we want. This means: (a) the Tusken candidate shifts from *author-from-scratch* to **adopt-the-addon + §19.5 audit its pawnGroupMakers/arsenal**; (b) it double-confirms the **Jawa** look/arsenal for the player faction (Cycler + Ion Blaster are canon Tatooine weapons already balanced by the author — audit them under §19.5 alongside the Outer Rim weapon audit that already cleared GREEN). **Action: acquire Outer Rim – Tatooine + its faction addon; source-audit before install. Do NOT hand-author a Tusken FactionDef — curate the shipped one.** The design intent below (territorial ambush, no-parley, Neolithic floor) becomes the *curation target* for the adopted faction, not a build spec.

**Why they earn a slot:** [CANON] Tuskens (Sand People) are the *indigenous* population of Tatooine — not criminals, not Imperials, not underlings of anyone. They're territorial, xenophobic nomads who attack outsiders on sight and answer to no one. That makes them the one faction that is *native to the desert the whole campaign is set in* — a third pole between the Empire (from above) and the Hutts (from the markets): **the land itself is hostile, and it has people.**

**[GENE] What the mod gives them (verified):** the Tusken xenotype ships `Aggression_Aggressive`, `MaxTemp_SmallIncrease` (heat-adapted), `Outland_UnusualSpeech`, brown skin. This is *mechanically almost identical to the Jawa* (heat-adapted desert native) but tuned aggressive instead of skittish — a perfect mirror: the Jawa are the desert's scavengers, the Tuskens are the desert's predators.

- **Premise (one line):** *The desert had people before you crashed here, and they want you gone.*
- **Emotional register:** alien, wordless, territorial menace. No trade-babble, no negotiation — the anti-Hutt. → harsh sand-and-bone `colorSpectrum`; `UnusualSpeech` gene means they literally don't parley.
- **Disposition:** hostile but **not** `permanentEnemy` — they attack incursions into *their* turf (Faction Territories & Vassalage in-turf ambush is the perfect substrate) and raid for supplies, but they're a *place-based* threat, not a galaxy-spanning pursuer. You can, in principle, learn to avoid them; you can never befriend them easily.
- **Tech tier:** Neolithic/Industrial floor — gaderffii clubs, slugthrower rifles, salvaged low-tier gear. [DESIGN] §19.5: danger is *ambush + territory + numbers*, never gear tier. They're dangerous because they hit you where you're weak (crossing open desert), not because their guns are better.
- **⭐ Unique verb — territorial ambush.** They don't come to your base on a raid timer; they own stretches of the map and punish you for crossing. This makes *geography* dangerous and gives the desert biome teeth — synergizes directly with the [LOCKED] dark-biome / low-visibility layer and the salvage-diving loop (the ruins you want to loot are in *their* land).
- **Economy:** none — they don't trade. Loot from raiding a Tusken camp = banthas, moisture, low-tier salvage, cultural artifacts (sellable to Hutts).
- **[CANON] flavor hook:** Tuskens are intensely clan/tribe-based (a clan chief + war leaders; they raid in packs, take gaffi-stick trophies, and famously attack in single-file to hide their numbers). A defeated clan can be *displaced* rather than exterminated → supports a "push them off your turf" verb rather than genocide. Leader persona = a masked clan chief (no dialogue — the `UnusualSpeech` gene means they never parley). _(Established from general SW knowledge; not citation-backed — fandom fetch was 403-blocked.)_
- **Distinct-from line:** vs. Jawa — same desert, same heat-adaptation, opposite disposition: the Jawa flee and scavenge, the Tuskens hold ground and kill. vs. Empire — the Empire is *from above and everywhere*; the Tuskens are *from here and nowhere else*.
- **What Cherry Picker deletes:** nothing from the Tusken xenotype (it's core to theme); suppress any generic tribal faction so Tuskens are unambiguously *the* native people.
- **Dependency:** needs the Tusken xenotype (Galactic Diversity, [GENE]-confirmed on disk) + Faction Territories & Vassalage ([LOCKED] adopted).

---

## 2. GEONOSIAN HIVE — the insectoid droid-foundry colony

> **SWEEP NOTE:** no prebuilt *Geonosian faction* surfaced, but the **droid-army** side of their identity is available ready-made — **[JDS] Separatist Droid Army** (WS 3276499495) and **[KR] Separatist Army** (WS 3399017889), plus **Outer Rim – Separatists** (WS 3097604003). So a Geonosian hive can be authored as the *insectoid command layer* on top of an adopted CIS droid faction rather than built entirely from scratch. [WS-CONFIRMED]. ⚠️ The [KR] variant is self-described as lethal/"most likely fatal" — audit its numbers hard before trusting (§19.5).

**Why they earn a slot:** [CANON] Geonosians are a hive species who built the Separatist droid factories — canonically the galaxy's insectoid industrialists. That gives us a faction whose *identity is manufacturing*, which is thematically loaded for a campaign about a stolen Factory ship: an enemy that out-produces you, the dark mirror of the Jawa's salvage economy.

**[GENE] What the mod gives them (verified):** `Outland_EggLayer` + `Outland_LowFertility` (hive reproduction), `Outland_Wings_Insect` (flight/mobility), `Outland_InsectBody`, `AptitudeStrong_Crafting`. The crafting aptitude + egg-laying is the mechanical hook: a faction that is *many, winged, and builds things*.

- **Premise (one line):** *A hive that makes soldiers faster than you can kill them.*
- **Emotional register:** cold, swarming, non-individual — the insectoid uncanny. Closest thing in the cast to the vanilla-insectoid dread, but SW-flavored.
- **Disposition:** hostile, `canStageAttacks`; a *nest-based* threat like the Tuskens but vertical-mobile (winged). [DESIGN] Could be cast as **Separatist-aligned** (they built the droid army) — which bridges to the [LOCKED as territorial register, concept.md §92] Separatist-remnant androids and to the Droid Depot factions on disk (DUM Squad, Rogue Droids, escaped battle droid).
- **Tech tier:** Industrial, but *numbers* is the identity — many weak winged bodies + the droids they manufacture. §19.5: danger is *swarm + air mobility + droid support*, not stat inflation. The anti-exponential guard here is real and must be watched: "makes soldiers faster than you can kill them" must be authored as *pawnGroupMaker composition*, NOT a points-curve steepening. [DESIGN] cap it — the hive fields droids it *pre-built*, it doesn't scale infinitely.
- **⭐ Unique verb — manufactured reinforcement.** Where the Jawa recycle *up* from corpses, the Geonosians produce *out* from a hive. Defeating them yields droid-brain feedstock [LOCKED §460 recycling loop] — so the Geonosian hive is a *deliberate droid-brain source* for the Jawa economy. That's a clean cross-faction hook: the bug-factory feeds your robot-army.
- **Economy:** minimal; loot = droid components, brains, chitin, crafting materials.
- **Distinct-from line:** vs. Empire — the Empire is *few elite*; the Geonosians are *endless cheap*. vs. Tuskens — both nest-based, but Tuskens are Neolithic ground ambushers and Geonosians are winged industrial swarmers.
- **Principal risk:** insectoid swarms are the easiest place to *accidentally* break the anti-exponential pillar (spawn-scaling). Flag for the tightest §19.5 review of any faction in the cast.
- **Dependency:** Geonosian xenotype ([GENE]-confirmed) + Droid Depot factions (on disk) for the manufactured-droid support.

---

## 3. WOOKIEE FREE-HOLDS — the rare potential ally ⭐ fills a casting gap

**Why they earn a slot:** every faction above is enemy or neutral-hostile. [CANON] Wookiees were **enslaved by the Empire** (Kashyyyk was occupied under Order 66 / Imperial rule; Wookiee slave labor built Imperial facilities) — which makes them the *natural ally* of anyone the Empire hunts. Casting them as a possible ally fills a real gap: the Jawa underdog story is stronger if there's *someone* out there who might help, and an ally you have to earn is more valuable than a shop. _(No prebuilt Wookiee faction surfaced in the sweep — this remains author-from-scratch using the [GENE]-confirmed Wookiee xenotype; that's fine, it's a small neutral→ally FactionDef.)_

**[GENE] What the mod gives them (verified):** `MoveSpeed_Slow` + `MinTemp_LargeDecrease` (cold-adapted, so *out of their element* in the desert — a nice tension), `AptitudeStrong_Artistic`, `Outland_BodyScale_Large` (big, strong). Slow-but-strong melee warriors who feel the heat: mechanically distinct from every other faction (all the others are heat-adapted or neutral).

- **Premise (one line):** *Exiled warrior-craftsmen who also hate the Empire — if you can earn their trust.*
- **Emotional register:** noble, wronged, loyal — the cast's moral counterweight to all the venality.
- **Disposition:** **neutral-to-allied**, vassalage-eligible (Faction T&V). [DESIGN] Start at low/neutral goodwill; alliance is *earned* (help against a shared Imperial raid, gifts, quests). The only faction you'd genuinely *want* to defend.
- **Tech tier:** mid; bowcaster-analog ranged + heavy melee. §19.5: capability is *individual strength + loyalty*, small numbers — they're few and tough, the inverse of the Geonosian swarm.
- **⭐ Unique verb — the earnable alliance.** No other faction can become a true ally (Empire=never, Hutts=buyable-not-trustable, Tuskens/Geonosians=hostile). The Wookiees are the one relationship that *rewards investment* — a co-belligerent against the Empire in Act III.
- **Economy:** trade in crafted goods, wood/organics (they're out of place in the desert, so they *want* what the desert lacks — a natural trade complementarity with Jawa salvage).
- **[CANON] hook:** Wookiee life-debt culture — a Wookiee whose life you save is honor-bound to serve you (the Chewbacca/Han precedent). Mechanically perfect: a rescued Wookiee prisoner could join permanently as a recruited pawn, and the alliance is *earned* through rescue. _(Established SW knowledge; not citation-backed — fandom fetch 403-blocked.)_
- **Distinct-from line:** vs. everyone — the only faction defined by *loyalty* rather than threat or greed. The heart-note in a cast of predators and merchants.
- **Dependency:** Wookiee xenotype ([GENE]-confirmed) + Faction T&V vassalage/alliance ([LOCKED] adopted).

---

## 4. PYKE SPICE SYNDICATE — the rival cartel (judgment call)

**The call you need to make:** [CANON] the Pyke Syndicate is a *spice-running criminal cartel* headquartered on Kessel — canonically a **rival/peer** of the Hutts (both are major players in the galactic underworld / the Shadow Collective era), not their underlings. Under your Hutt reframe, Pykes could go two ways:
- **(a) Fold into the Hutt underling pool** (as I currently have them in §2 of the dossiers) — simplest, one criminal power.
- **(b) Stand as their own rival cartel** — a *third* criminal faction that competes with the Hutt lords for the same market. [DESIGN] This is the richer option: it turns "the criminal underworld" into a *contested* space you can exploit — Pykes vs. Hutts vs. each other, and you play the seams. It also gives spice (drug economy) a distinct owner separate from the Hutts' general fencing.

**[GENE] What the mod gives them:** `Outland_Blood_Green`, pale skin, large-headed. Modest genetic distinctiveness — their identity is *organizational* (the spice monopoly), not physiological, which slightly favors option (a) unless the spice-economy angle is wanted.

- **Recommendation:** default to **(a)** to keep the criminal underworld legible (one Hutt-centric power), and promote to **(b)** only if you want a drug/spice economy sub-game and a criminal *rivalry* to exploit. Low-cost to defer — it's a Faction Filter toggle, not a rebuild.
- **Distinct-from line (if promoted):** vs. Hutts — Hutts fence *everything* and sit on thrones; Pykes run *one product* (spice) and operate as a distributed syndicate. Different silhouette, different economy.

---

## 5. Considered and NOT recommended as standalone factions

- **Kaleesh** [GENE: `Skin_DeepRed`, `Outland_ScaleSkin`, `Outland_ChinHorns`, `Outland_JawTusks` — striking beast-skull warriors]: canonically a warrior culture (Grievous's people), but as a faction they'd overlap heavily with either the Tuskens (warrior clans) or Hutt muscle. **Better use:** a *signature mercenary pawnkind* inside a Hutt faction, or a named Bounty Hunter. Keep as a distinctive individual, not a faction. [DESIGN]
- **Trandoshan** [GENE: `Outland_Regeneration`, `Aggression_HyperAggressive`]: their canon role is *hunters/slavers for hire* — already claimed by the Bounty Hunters faction (a named Trandoshan hunter is a perfect trophy rival) and the Hutt muscle pool. Don't spend a faction slot; use as pawnkind + named hunter. [folded]
- **Rakata** [CANON-VERIFY: ancient dark-side empire, now Force-dead after their collapse]: fascinating lore but canonically *extinct/fallen* — no living faction to field. **Better use:** a *ruins/artifact theme* (their dead empire's tech as salvage), not a live faction. Ties to the Ancient Urban Ruins backbone.

---

## The expansion cast, diffed against the core four

| Faction | Role in cast | Numbers | Disposition | Unique verb | Fills what gap |
|---|---|---|---|---|---|
| **Tusken clans** | native desert predator | medium, clan | hostile, place-based | territorial ambush | makes the *land* hostile |
| **Geonosian hive** | insectoid industrialist | many, winged | hostile, nest | manufactured reinforcement | an enemy that *out-produces* |
| **Wookiee free-holds** | earnable ally | few, strong | neutral→ally | the earnable alliance | the *only* potential friend |
| **Pyke syndicate** (opt.) | rival cartel | medium | treacherous | single-product spice monopoly | contested criminal underworld |

Cross-check against the core four (Empire/Hutts/Bounty Hunters/Jawa): no expansion faction duplicates a core verb. Tuskens ≠ Jawa (predator vs scavenger, same desert). Geonosians ≠ Empire (cheap swarm vs elite few). Wookiees are unique (the only ally). Pykes ≠ Hutts only if promoted to option (b).

---

## Decision translation (what you actually need to decide)

**The decision:** which of these four join the final roster (the Sensible Factions casting call). They're not all-or-nothing — each is an independent Faction Filter allow-list entry.

**Recommended cast:** **Tuskens + Wookiees** are the two highest-value adds — they fill genuine gaps (native-land threat; the only ally) with zero pillar risk and both xenotypes are [GENE]-confirmed on disk. **Geonosians** are strong but carry the highest anti-exponential risk (swarm-scaling) — adopt with a tight §19.5 composition review. **Pykes** default to Hutt-underlings; promote only if you want a spice sub-economy.

**Viable alternatives:** run a *leaner* cast (core four + Tuskens only) if you want the desert-native pole without expanding management overhead; or a *fuller* cast (all four) if you want the underworld and the insectoid industrial mirror.

**Tradeoffs:** every added faction is more Cherry-Pick/Faction-Filter curation surface and more §19.5 audit work; against that, each adds a distinct pole the current cast lacks (native land, mass production, true friendship, criminal rivalry).

**Dependencies:** all four xenotypes are [GENE]-confirmed present in Galactic Diversity 1.6 on disk. Faction behavior rests on already-[LOCKED] adopted mods (Faction T&V, CAI-5000, Droid Depot). No new mod is required to field any of them.

**Principal risks:** (1) Geonosian swarm breaking the points-curve pillar — mitigate with composition-only escalation. (2) Tusken/Bounty-Hunter/Hutt-muscle *species overlap* (Trandoshan/Rodian appear in several) blurring silhouettes — mitigate by keeping named hunters visually/mechanically distinct from anonymous mooks (already noted in dossiers §diff). (3) faction-count creep diluting the curated surface — mitigate by casting only what fills a named gap.

**Missing info that would help:** the canon pull **partially failed** — all 16 Wookieepedia fetches returned HTTP 403 (fandom blocks bots), so the `[CANON-VERIFY]` flags were resolved from reliable knowledge (now `[CANON]`) rather than citable pages. If you want sources *on record*, I can re-file via a non-fandom mirror or StarWars.com, or you can paste pages. Still genuinely open: **JodemLee/TheForce_Psycast 1.6 status** (README shows 1.4/1.5/2.9 folders + a "Steam Version Latest" release, no explicit `/1.6` in the truncated tree — [VERIFY]); this affects whether the Empire's Sith-elite ranks come from that mod's prebuilt **Sith Order** faction or are hand-granted.

**⭐ NEW decisions the sweep created (not present at first draft):**
1. **Xenotype-source dedup:** run Outer Rim – Galactic Diversity alone (leanest — has our genes) vs. add Star Wars Xenotypes + the [BTD] REMIX dedup patch. Recommend OR-GD alone unless SWX's fixed Hutts/Mon-Cal are specifically wanted.
2. **Empire source:** use Outer Rim – Galactic Empire (+ optional VFE-Empire retheme WS 3292633931) and do NOT also run Star Wars – Factions (Continued) as a second Empire → avoid duplicate factions.
3. **Tusken/Jawa arsenal audit:** Outer Rim – Tatooine ships Cycler/Gaderffii/Ion Blaster — fold into the §19.5 weapon audit (likely GREEN like the rest of Outer Rim, but confirm).

**Recommended next steps:**
1. Make the casting call on these four (I recommend Tuskens + Wookiees firm, Geonosians conditional, Pykes deferred).
2. On Fetcher return: resolve the `[CANON-VERIFY]` flags, especially Tusken/Wookiee for leader personas + the Hutt/Pyke relationship.
3. For any faction cast: write its full dossier (the `faction_dossiers.md` template) + Cherry-Pick lines + pawnGroupMaker composition.
4. Re-run the full-cast diff (core four + expansion) to catch any silhouette collisions.
