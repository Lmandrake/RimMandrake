# candidate_factions.md — Race-based faction candidates (the expansion cast)

_Companion to `faction_dossiers.md` (the 4 decided factions). This doc proposes **additional** factions built from the Star Wars races the mod actually ships, grounded in (a) the **verified xenotype gene data** read from Outer Rim Galactic Diversity's 1.6 source on disk, and (b) **canonical SW lore** — the latter flagged `[VERIFY pending Fetcher]` where it rests on online sources not yet returned (`2026-08-05_sw_race_faction_lore.txt` filed). Status: DRAFT 2026-08-05 — candidates for your casting call, not yet built._

**Evidence tiering:** [GENE] = verified in the mod's 1.6 GeneDefs on disk · [CANON-VERIFY] = SW lore, pending Fetcher confirmation · [DESIGN] = my proposed authoring · [LOCKED] = already-decided in our docs.

---

## 0. What the two directives already settled (the roster math)

Your two rulings (2026-08-05) consolidated several races *into* the existing four factions rather than spawning new ones — this is good, it prevents faction-sprawl:

- **Sith / Massassi / Dathomirian-Nightsister / Miraluka** → **elite ranks of the Empire** (its Force-user tier), NOT a faction. [folded into `faction_dossiers.md` §1]
- **Nikto / Weequay / Rodian / Trandoshan / Pyke** → **rank-and-file muscle of the Hutt-lord factions**, NOT standalone factions. [folded into §2]

So the question this doc answers is narrower and cleaner: *which remaining races are canonically their **own** autonomous societies* — not Imperial, not Hutt underlings — and therefore earn a faction slot of their own? Four candidates clear that bar. A fifth (Pyke) is a judgment call I flag explicitly.

---

## 1. TUSKEN RAIDER CLANS — the native desert xenophobes ⭐ strongest candidate

**Why they earn a slot:** [CANON-VERIFY] Tuskens (Sand People) are the *indigenous* population of Tatooine — not criminals, not Imperials, not underlings of anyone. They're territorial, xenophobic nomads who attack outsiders on sight and answer to no one. That makes them the one faction that is *native to the desert the whole campaign is set in* — a third pole between the Empire (from above) and the Hutts (from the markets): **the land itself is hostile, and it has people.**

**[GENE] What the mod gives them (verified):** the Tusken xenotype ships `Aggression_Aggressive`, `MaxTemp_SmallIncrease` (heat-adapted), `Outland_UnusualSpeech`, brown skin. This is *mechanically almost identical to the Jawa* (heat-adapted desert native) but tuned aggressive instead of skittish — a perfect mirror: the Jawa are the desert's scavengers, the Tuskens are the desert's predators.

- **Premise (one line):** *The desert had people before you crashed here, and they want you gone.*
- **Emotional register:** alien, wordless, territorial menace. No trade-babble, no negotiation — the anti-Hutt. → harsh sand-and-bone `colorSpectrum`; `UnusualSpeech` gene means they literally don't parley.
- **Disposition:** hostile but **not** `permanentEnemy` — they attack incursions into *their* turf (Faction Territories & Vassalage in-turf ambush is the perfect substrate) and raid for supplies, but they're a *place-based* threat, not a galaxy-spanning pursuer. You can, in principle, learn to avoid them; you can never befriend them easily.
- **Tech tier:** Neolithic/Industrial floor — gaderffii clubs, slugthrower rifles, salvaged low-tier gear. [DESIGN] §19.5: danger is *ambush + territory + numbers*, never gear tier. They're dangerous because they hit you where you're weak (crossing open desert), not because their guns are better.
- **⭐ Unique verb — territorial ambush.** They don't come to your base on a raid timer; they own stretches of the map and punish you for crossing. This makes *geography* dangerous and gives the desert biome teeth — synergizes directly with the [LOCKED] dark-biome / low-visibility layer and the salvage-diving loop (the ruins you want to loot are in *their* land).
- **Economy:** none — they don't trade. Loot from raiding a Tusken camp = banthas, moisture, low-tier salvage, cultural artifacts (sellable to Hutts).
- **[CANON-VERIFY] flavor hook:** Tuskens ritually mark territory and are intensely clan-based; a defeated clan can be *displaced* rather than destroyed. Pending Wookieepedia confirm of their social org for the leader persona.
- **Distinct-from line:** vs. Jawa — same desert, same heat-adaptation, opposite disposition: the Jawa flee and scavenge, the Tuskens hold ground and kill. vs. Empire — the Empire is *from above and everywhere*; the Tuskens are *from here and nowhere else*.
- **What Cherry Picker deletes:** nothing from the Tusken xenotype (it's core to theme); suppress any generic tribal faction so Tuskens are unambiguously *the* native people.
- **Dependency:** needs the Tusken xenotype (Galactic Diversity, [GENE]-confirmed on disk) + Faction Territories & Vassalage ([LOCKED] adopted).

---

## 2. GEONOSIAN HIVE — the insectoid droid-foundry colony

**Why they earn a slot:** [CANON-VERIFY] Geonosians are a hive species who built the Separatist droid factories — canonically the galaxy's insectoid industrialists. That gives us a faction whose *identity is manufacturing*, which is thematically loaded for a campaign about a stolen Factory ship: an enemy that out-produces you, the dark mirror of the Jawa's salvage economy.

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

**Why they earn a slot:** every faction above is enemy or neutral-hostile. [CANON-VERIFY] Wookiees were **enslaved by the Empire** (Kashyyyk was occupied) — which makes them the *natural ally* of anyone the Empire hunts. Casting them as a possible ally fills a real gap: the Jawa underdog story is stronger if there's *someone* out there who might help, and an ally you have to earn is more valuable than a shop.

**[GENE] What the mod gives them (verified):** `MoveSpeed_Slow` + `MinTemp_LargeDecrease` (cold-adapted, so *out of their element* in the desert — a nice tension), `AptitudeStrong_Artistic`, `Outland_BodyScale_Large` (big, strong). Slow-but-strong melee warriors who feel the heat: mechanically distinct from every other faction (all the others are heat-adapted or neutral).

- **Premise (one line):** *Exiled warrior-craftsmen who also hate the Empire — if you can earn their trust.*
- **Emotional register:** noble, wronged, loyal — the cast's moral counterweight to all the venality.
- **Disposition:** **neutral-to-allied**, vassalage-eligible (Faction T&V). [DESIGN] Start at low/neutral goodwill; alliance is *earned* (help against a shared Imperial raid, gifts, quests). The only faction you'd genuinely *want* to defend.
- **Tech tier:** mid; bowcaster-analog ranged + heavy melee. §19.5: capability is *individual strength + loyalty*, small numbers — they're few and tough, the inverse of the Geonosian swarm.
- **⭐ Unique verb — the earnable alliance.** No other faction can become a true ally (Empire=never, Hutts=buyable-not-trustable, Tuskens/Geonosians=hostile). The Wookiees are the one relationship that *rewards investment* — a co-belligerent against the Empire in Act III.
- **Economy:** trade in crafted goods, wood/organics (they're out of place in the desert, so they *want* what the desert lacks — a natural trade complementarity with Jawa salvage).
- **[CANON-VERIFY] hook:** life-debt culture — a rescued Wookiee could join permanently. Pending Wookieepedia confirm.
- **Distinct-from line:** vs. everyone — the only faction defined by *loyalty* rather than threat or greed. The heart-note in a cast of predators and merchants.
- **Dependency:** Wookiee xenotype ([GENE]-confirmed) + Faction T&V vassalage/alliance ([LOCKED] adopted).

---

## 4. PYKE SPICE SYNDICATE — the rival cartel (judgment call)

**The call you need to make:** [CANON-VERIFY] the Pyke Syndicate is a *spice-running criminal cartel* — canonically a **rival/peer** of the Hutts, not their underlings. Under your Hutt reframe, Pykes could go two ways:
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

**Missing info that would help:** the online canon pull (`2026-08-05_sw_race_faction_lore.txt`) resolves the `[CANON-VERIFY]` flags — Tusken social org (leader persona), Wookiee life-debt (ally mechanic), Hutt-vs-Pyke relationship (the option-a/b call), and Geonosian hive structure. Also confirms **JodemLee/TheForce_Psycast** 1.6 status, which affects the Empire's Force ranks.

**Recommended next steps:**
1. Make the casting call on these four (I recommend Tuskens + Wookiees firm, Geonosians conditional, Pykes deferred).
2. On Fetcher return: resolve the `[CANON-VERIFY]` flags, especially Tusken/Wookiee for leader personas + the Hutt/Pyke relationship.
3. For any faction cast: write its full dossier (the `faction_dossiers.md` template) + Cherry-Pick lines + pawnGroupMaker composition.
4. Re-run the full-cast diff (core four + expansion) to catch any silhouette collisions.
