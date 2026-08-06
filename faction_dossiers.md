# faction_dossiers.md — Filled per-faction profiles (the decided cast)

_Applies the `faction_authoring_mechanism.md` template to the four factions already decided in `context.md`/`concept.md`, before the full Sensible Factions casting call. Each dossier is grounded in existing locked lore (cited to context.md where it exists) and then pushed for maximum flavor via the restrict / augment / improve lens the user asked for. Status: DRAFT 2026-08-05 — content proposals for approval, not yet built into patches/saves._

**Evidence tiering used throughout:** [LOCKED] = already-decided lore in our docs · [DESIGN] = my proposed authoring on top · [VERIFY] = needs an in-game or source check before build.

**The one rule that governs every "augment" below:** danger and identity are *compositional* — new pawnkinds, powers, apparel, doctrine, loot — never a bump to `maxPawnCostPerTotalPointsCurve` or raw stat multipliers (proven in the Outer Rim source, see mechanism doc §0). Every augment here adds a *quality*, not a bigger number.

---

## Cross-faction design: the "restrict / augment / improve" lens

For each faction I work three moves the user named:
- **Restrict** — what we *delete* (Cherry Picker) or *deny* them, so their silhouette is sharp. Subtraction is identity.
- **Augment** — what signature capability, power, or unit we *add* that no other faction has.
- **Improve** — how we make the *existing* material read better: doctrine, apparel coherence, named leaders, loot signature.

And I hold each to the **3-act arc** (Act I rumors → Act II targeted raids → Act III blockade/run to the launch corridor) and the **Imperial Heat gauge** (the GM-layer pursuit variable), both [LOCKED] in context.md §889/§895.

---

## 1. THE GALACTIC EMPIRE — the vertical pursuer

**Premise (one line):** *A disciplined military state that owns the sky and wants its stolen Factory ship back.* [LOCKED — "ANTAGONIST LOCKED: THE EMPIRE pursues the Jawas," context.md §301]

**Emotional register:** cold, inexorable, overwhelming-from-above. Not hateful — *procedural*. You are a logistics problem they are closing out. → tone of `description`; `colorSpectrum` a hard Imperial grey/white; `factionNameMaker` a formal military namer.

**Disposition / doctrine:** `permanentEnemy=true`, `canSiege=true`, `canStageAttacks=true`. Escalation is authored by *swapping which pawnGroupMakers spawn per act*, not steepening any curve:
- **Act I** — thin patrols, scouts, bounty-poster flavor; the Empire "barely knows you exist" [LOCKED §893]. Groups: light troopers, a scout, no elites.
- **Act II** — coherent targeted raids once CAI-5000 fixes your position [LOCKED §893]; groups add officers, heavies, the first Force-user.
- **Act III** — blockade / net closing; groups add elite compositions + the signature power units for the run to the corridor.
- **Orbital supremacy** [LOCKED §910]: the Empire holds only ~1–2 surface settlements but nearly all orbit. The **orbital-detection timer** (main Imperial Heat driver) applies everywhere the sky is open; **Faction Territories & Vassalage** in-turf ambush is the *secondary, additive* surcharge on ground they hold. Design toward the counter: overhead cover / caverns / dark biomes buy time against the sky.

**Tech tier:** Ultra (charge-tier). This is the *only* faction that gets the top tier — it's how they read as "above" you without bigger raid points.

**Signature arsenal/apparel:** charge weapons, Imperial armor, disciplined ranks. VFE-Deserters supplies a militarized Imperial force [LOCKED §321]. §19.5 note: quality + coordination, groups stay *small*; curve untouched.
- **Improve:** enforce apparel coherence — every Imperial pawn reads as *uniformed* (same armor set + color), so a raid looks like an army, not a mob. This is a `pawnKindDef` apparel-tag tightening, near-zero cost, huge visual payoff.

**⭐ Augment — THE FORCE (NPC-only), the Empire's unique verb.** [DESIGN — FINALIZED 2026-08-06: VPE-only, see below]
- **The Sith-species pawns ARE the Empire's elite ranks** [user directive 2026-08-05] — not a separate faction. Canon-exact: the mod's Force-species (Sith, Massassi, Dathomirian/Nightsister, Miraluka) become the Empire's rare **Inquisitor / Adept / Dark-Adept** pawnkinds. This is a *consolidation* — it sharpens the Empire (its top tier is visibly, biologically different — red-skinned tendriled Sith, hulking Massassi enforcers) instead of proliferating factions. A raid's escalation now reads racially as well as mechanically: Act I is human troopers; Act III fields the red-skinned Force elite.
- Each carries a *curated* **dark-side** set of AI-friendly Force powers: **Force lightning** (the signature — map to VPE's chain/discharge-type ability), a **Force-push** (knockback, breaks your firing line), a **Force-speed dash** (Skip-analog, closes distance — negates your kiting), and **fear/berserk-style debuffs**. Curated for powers the AI *actually uses well* (self-buff + mobility + simple targeted), not the whole tree.
- **Light-side counterpart lives elsewhere, by design:** the Moisture Farmer factions of the world field a **rare Jedi hero** (low pawnGroupMaker weight) with a curated **light/telekinesis** set — **healing, telekinetic push/pull, non-lethal disables, deflection/self-buffs.** No dark powers on the Jedi, no light powers on the Sith. Neither the player nor the Jawa gets any Force at all. (See candidate/Moisture-Farmer notes.)
- **Why it's the perfect Empire augment:** it does something the player structurally *cannot* (player psycast ban intact) — the cleanest possible expression of "an enemy you're not ready to fight yet" (§19.9). It's also diegetically exact: the Empire has the Force; scrappers don't.
- **Pillar safety:** [LOCKED policy] the ban is on *player* psycasting only; Royalty/psycasts "may remain installed for factions, equipment, enemies, quests" (context.md §723). NPC-only Force raises no player ceiling → passes the 7-question test by construction, same logic as the Imperial Heat gauge.
- **FINALIZED substrate (user decision 2026-08-06 — VPE only, no dedicated Force mod):**
  - [Established] Vanilla RimWorld enemies **never** cast psycasts even with a psylink (RimWorld Wiki, Royalty page) — so enemy Force *requires* a mod that adds enemy-cast AI. The augment is not free; it depends on VPE below.
  - [Established] ✅ **Vanilla Psycasts Expanded** (WS 2842502659, updated Jan 2026 → 1.6) is the **sole Force substrate.** It ships **built-in enemy psycaster AI** + a storyteller that force-spawns enemy casters who "use all their unlocked abilities" — the reason enemies actually cast. Deps Harmony + VEF Core (both in stack). Do **not** also run **Powerful Psycast AI Continued** (WS 3276102794) — it conflicts with VPE at the C# spawn level and is redundant.
  - [Decision] **DROPPED — JodemLee/TheForce_Psycast.** No `/1.6` folder in the repo (1.4/1.5/2.9 only) and the Steam page (WS 3100942433) is now titled **"[Discontinued]."** We do not gamble the campaign on a dead mod. Likewise **not adopting** Star Wars: The Force Factions (WS 3557220783) or "A complete Force system" (WS 3594298838). This makes the Force a **curation/patch on VPE**, which *fully eliminates* the discontinued-mod 1.6 risk.
  - [Design] **Two curated ability sets, each locked to the right NPCs via Faction Filter:**
    - **Dark tree → Empire Sith-race elite ONLY** (Sith/Massassi/Dathomirian-Nightsister): Force lightning + telekinetic throw + fear/berserk debuffs. Spawns only in Empire pawnGroupMakers. **Miraluka are NOT part of this tier** [user ruling 2026-08-06] — they appear exclusively as Imperial prisoners / rescue-quest targets (captured Force-sensitives).
    - **Light/telekinesis tree → Jedi, BOTH channels [user ruling 2026-08-06]:** (1) primary = **factionless, Empire-hunted lone wanderers** (no faction membership, psylink 3–6, ≤1 per encounter); (2) also a *rare* Jedi sheltering within a sympathetic Moisture-Farmer/Homestead faction (low spawn weight). Powers: heal + push/pull + non-lethal disable + deflection/self-buff. Uncommon and memorable.
    - **Players & Jawa → NONE.** No neuroformer/psytrainer/anima/recruit path; no Jawa pawnkind carries psylink.
  - [Inference] Grant powers to each pawnkind via a fixed hediff/psylink on the *kind*; Cherry-Pick/suppress any player-acquisition node, **never** the AbilityDefs/Hediffs the enemy AI casts (context.md §634). Prefer VPE's existing AI-flagged AbilityDefs so the AI casts competently; custom-label only for flavor.
  - **⏳ ONE OPEN CHECK (gates the patch, not the decision) — Fetcher FILED `2026-08-06_vpe_ability_defs`:** confirm which VPE AbilityDefs map to Force-lightning / telekinetic-throw / heal and that each carries the AI-usable flag + targeting hints. About.xml pulled `2026-08-06_force_and_or_sources_corrected` (verifies supportedVersions 1.4/1.5/1.6 + deps Harmony/Royalty/VEF-Core + the enemy-caster AI & Basilicus Bestower storyteller; it does NOT list individual ability/path names, so those remain unfabricated pending the Defs-tree pull now in flight).

**Economy / interaction:** does **not** trade with you. Loot = charge-tier gear + a rare Force-artifact you can sell to the Hutts but not use. No alliance, no vassalage — the one faction you can never buy off. That unbuyability is itself a design statement.

**Named leader persona (Backstory Constructor):** *Moff-analog* — an orbital governor who never lands. High Shooting/Social/Intellectual, no menial work-disables that matter; lore = the officer personally assigned your file. He's a *name on the Heat gauge*, rarely a body on the map until Act III.

**What Cherry Picker deletes from their source:** non-Imperial sub-factions VFE-Deserters/Outer Rim bundle. **Two-Empires resolution [LOCKED, required_mods.md line 460 — supersedes the old "suppress vanilla Empire" idea]:** the vanilla Royalty Empire is **FUSED** with the Outer Rim Galactic Empire into ONE Empire — Royalty = the aristocratic/Moff/noble-house core (keeps all its quest/trader/techprint hooks, needed for Configurable Techprints), Outer Rim = its military/troops. So we do **not** suppress or delete either; we frame them as two faces of one power (the Moff-analog leader persona sits naturally on the Royalty-noble side). **Guard [user directive 2026-08-05]:** do **NOT** delete the Sith/Massassi/Dathomirian/Miraluka xenotypes — they are now the Empire's *elite ranks*, not soup. Any Cherry-Pick pass that strips "off-theme Force species" must whitelist these four. If they'd otherwise spawn in random outlander factions, restrict them to the Empire's pawnGroupMakers via Faction Filter rather than deleting the xenotype.

**Distinct-from line:** vs. everyone — the Empire is *few, elite, relentless, and above you*. They own the timer. Every other faction operates *under* their sky.

---

## 2. THE HUTT KAJIDICS — the treacherous market (1–3 individual Hutt lords)

**Premise (one line):** *A handful of individual Hutt crime-lords, each ruling a pirate faction of notorious mercenary races — the only markets that don't care about your standing, and each other's rivals.* [LOCKED — "Hutts = economic/criminal power, trade you can't trust," concept.md §92; "pirate-type base tradeable by anyone regardless of standing," context.md §910]

**⚠️ Structural reframe [user directive 2026-08-05]:** Hutts do **not** form a mass "cartel of Hutts." Canonically a Hutt is a *lord* — the faction is his *kajidic* (crime clan), and the bodies are his hired underlings, not fellow Hutts. So the correct shape is **1–3 individual Hutt kingpins**, each the **named leader-persona** atop a *separate* pirate faction whose rank-and-file are the **notorious pirate/mercenary races** (canon: Nikto, Weequay, Rodian, Trandoshan, Pyke — all in the mod's xenotype roster). Jabba's-palace composition exactly: one Hutt on the dais, a motley of alien muscle around him. This also lets 2–3 Hutts be *mutual rivals* — you can play one against another, which the single-cartel framing couldn't do. **[VERIFY]** exact Hutt social org filed in `2026-08-05_sw_race_faction_lore.txt` (Hutt / Hutt Cartel Wookieepedia pages).

**Emotional register:** oily, transactional, amused by your desperation. Comedy-adjacent (fits the Jawa levity layer) but with teeth. → warm sickly-gold `colorSpectrum`; a namer full of honorifics and shell-company suffixes ("...of Merchant's Cartel," which the Gravtasm save already shows the engine generating).

**Roster composition (the anti-Empire silhouette):** each Hutt faction fields a *mixed alien mob* — Nikto/Weequay enforcers, a Trandoshan slaver-hunter, Rodian bounty-tracker, Pyke spice-runner — deliberately incoherent where the Empire is uniform. The Hutt himself (large, slow, non-combatant, sits in his base) is the leader Thing the save points `<leader>` at; he almost never appears on a raid map.

**Disposition / doctrine:** **not** `permanentEnemy`. This is the key structural contrast with the Empire. They run a **"pirate"-type base** — mechanically tradeable by anyone regardless of goodwill [LOCKED §910] — but are **situationally hostile**: bounty/extortion, they'll turn on you when the Empire's price is right.
- **Improve:** wire the betrayal to the Heat gauge — trading with the Hutts *raises* Imperial Heat [LOCKED §895], so the market is a genuine devil's bargain: the gear you need accelerates the pursuit that's hunting you. That single interaction makes every Hutt visit a real decision, not a free shop.

**Tech tier:** Spacer/mixed — they *sell* across tiers (that's their whole point) but *field* only mid-tier muscle. Gate their trade stock with the tech-tier stock filter [LOCKED plan, context.md §582] so "buy anything" doesn't leak endgame gear early.

**Signature arsenal/apparel:** motley — hired guns, slavers, mercs in mismatched flashy gear (deliberately *incoherent*, the anti-Empire: a mob, not an army). Improve via a distinct "cartel enforcer" apparel palette (gaudy, armored, individualistic).

**⭐ Augment — the market *as a mechanic*, not a trader visit.** [DESIGN]
- Give the Hutts a **placed, persistent base** (their [LOCKED] pirate-base location) that is the *only* reliable market on a planet where the Empire owns the lanes. This turns "a trade caravan wandered by" into "there is a place on the map that means commerce + danger."
- **Bounty board:** the Hutts *broker Imperial bounties on you* — a diegetic bridge that lets Hutt activity feed the bounty-hunter faction (§3). Trade with them and they know exactly where you are.
- **Improve — treachery events:** BuyAnything/trade oddities [VERIFY mechanic, context.md §634] give exotic lateral stock; pair with Cherry-Pick guard so no ceiling-raising tech leaks in.

**Economy / interaction:** the heart of the faction. Tradeable regardless of standing; can be *temporarily* placated with bribes; can NEVER be trusted. No vassalage (they vassalize *you* if anything). Loot from raiding them = silver, slaves-to-free, exotic trade goods, and intel that lowers Heat (you killed the informants).

**Named leader persona(s):** **1–3 individual named Hutts**, each a distinct kingpin persona (Backstory Constructor) atop his own faction — low Movement (they don't fight, they sit), extreme Social/Trade, disabled Violence; lore = runs the base, owns your bounty. Draft 2–3 so they can be *rivals*: e.g. an old established broker vs. an upstart undercutting him — you bribe one to move against the other. The face(s) you negotiate with and want to strangle.

**What Cherry Picker deletes:** collapse the generic pirate factions (VFE-Pirates *junkers/mercenaries*, Binary Star Raiders) — either **suppress** them via Faction Filter or **reflavor** them as the Hutt-lord factions, so the only criminal powers on the map are the named Hutts. Keep each Hutt roster to "alien muscle (Nikto/Weequay/Rodian/Trandoshan/Pyke) + the Hutt + slaves"; delete off-theme slaver xenotypes the source drags in.

**Distinct-from line:** vs. Empire — the Hutts are *venal, buyable, horizontal, and plural-but-rival* (individual lords who operate on the surface, in the markets, and against each other) where the Empire is *incorruptible, vertical, monolithic, above*. One you bribe; one you flee.

---

## 3. THE BOUNTY HUNTERS — the Act-II personal pursuers

**Premise (one line):** *Independent professionals the Empire (via the Hutts) hires to do what patrols can't — find you, specifically.* [LOCKED — "Bounty Hunters as Act-II pursuer"; RH2 Faction: Bounty Hunters adopted]

**Emotional register:** individual, competent, personal. Where the Empire is faceless ranks, a bounty hunter is *one dangerous person with a name who is coming for you*. This is the faction that makes the pursuit feel intimate.

**Disposition / doctrine:** hostile but **not** a mass army — they arrive as **small elite groups or lone hunters**, often via the bounty board (Hutt bridge, §2). Their doctrine is *tracking*: they show up where you *are*, not where a raid path leads — CAI-5000's smart-targeting is the perfect substrate. They're the human-scale expression of Act II's "the Empire fixes your position" [LOCKED §893].
- **Improve — escalating named rivals:** rather than generic spawns, author a **small stable of recurring named hunters** (Backstory Constructor). Each defeated-but-survived hunter can return with a grudge. This is cheap authored content that produces emergent serialized drama — the single highest flavor-per-effort move in the whole cast.

**Tech tier:** mid-to-high but *idiosyncratic* — each hunter has a *signature* weapon/gimmick, not a uniform. Diversity is the identity.

**Signature arsenal/apparel:** RH2 supplies the faction; each hunter reads distinct. §19.5: they're dangerous through *capability + tracking*, small numbers, no curve change. [VERIFY — RH2 arsenal tier audit still open per the gap-source request, to confirm they don't hand the player a tech ladder on loot.]

**⭐ Augment — the bounty economy loop.** [DESIGN]
- Hunters spawn *in response to your Heat / loudness* — extract loudly, trade with Hutts, fight patrols → a hunter gets dispatched. This makes them a *consequence* of your choices, closing the loop between the Heat gauge, the Hutt board, and a body on your map.
- **Trophy loot:** defeating a named hunter drops their signature weapon — a *unique, non-craftable* trophy (so it's flavor, not an arsenal ladder). You end the campaign carrying the guns of the hunters who failed to catch you.

**Economy / interaction:** minimal trade; occasionally a hunter can be *bought off* once (temporary, expensive) — reinforcing the Hutt "everything's for sale" theme by contrast with the Empire's incorruptibility.

**Named leader persona:** the **guild-master / most-feared hunter** — the final personal rival, held for Act III, arriving at the blockade. Extreme Shooting or Melee, a signature gimmick, lore = has never lost a mark. Beating him is a personal climax nested inside the corridor run.

**What Cherry Picker deletes:** RH2's off-theme faction bits; keep it to "hunters + guild." Ensure no player-recruitable bounty-hunter *workshop* path sneaks in.

**Distinct-from line:** vs. Empire — bounty hunters are *individual, named, personal, idiosyncratic* where the Empire is *collective, faceless, uniform, procedural*. The Empire is weather; a bounty hunter is a knock at the door.

---

## 4. THE JAWA SCAVENGER CLANS — the player faction (and their kin)

**Premise (one line):** *Small, skittish, brilliant desert scavengers who strip anything that stops moving and build power from the corpses of their enemies.* [LOCKED — custom Jawa xenotype: short, heat-adapted, night-vision, scavenger, context.md §274; Droid-brain-recycling fantasy §460/§463]

**Emotional register:** comedic, greedy, communal, resourceful-underdog. The heart of the campaign's levity layer (SpeakUp trade-babble, the Jawa corpus). You root for them *because* they're outmatched.

**Disposition / doctrine (as the player faction + any NPC Jawa kin-clans):** if we cast neutral/allied Jawa kin-clans as NPCs, they're **not** permanentEnemy — skittish, hit-and-grab, retreat when hurt (CAI-5000 flavor), ambush in their own dune turf (Faction T&V). Many-but-weak: a swarm of low-tier bodies, no elites. §19.5: threat (for the NPC version) or capability (for the player) is *numbers + unpredictability + salvage*, never gear tier.

**Tech tier:** Industrial *floor* — deliberately the lowest in the cast. Their power comes from *recycling upward*, not starting high. This is the anti-exponential pillar made into a faction identity.

**Signature arsenal/apparel:** VWE-Makeshift junk tier [LOCKED, ADOPTED] + salvaged low-tier Outer Rim cast-offs. Iconic silhouette: hooded, glowing eyes, mismatched scavenged armor. The *look* is already the brand.

**⭐ Augment — recycling as the faction's whole economic identity.** [LOCKED mechanic, elevated to identity]
- **Droid-brain recycling** [LOCKED §460/§463]: every defeated Imperial/Separatist droid butchers into an `OuterRim_DroidBrain`; the from-scratch brain recipe is *disabled*, so brains come **only** from recycling defeated droids, rare trader stock, or salvage. Droids become elite, hard-won assets built *from the corpses of the Empire that hunts you* — the perfect thematic inversion, and an anti-exponential control by scarcity rather than a build-restriction.
- **Improve — the scavenger verb everywhere:** lean the whole faction into "value from others' garbage" — salvage yields, ruin-diving (Ancient Urban Ruins backbone), stripping wrecks. Their progression is *lateral reclamation*, never a tech ladder.

**Economy / interaction:** trade scrap/components; want anything shiny; can ally with Jawa kin-clans and *maybe* placate the Hutts (never the Empire). This is the faction whose alliances *matter* because they have so little.

**Named leader persona:** the **clan chief** — high Social/Crafting, disabled Intellectual (they *tinker*, they don't *research* — reinforces no-research-ladder pillar); lore = keeper of the crashed Factory ship, the one who decided to fix it and flee. The player's anchor character. (Draft 3–5 founding personas per the [LOCKED] Backstory Constructor plan, context.md §521.)

**What Cherry Picker deletes:** any off-theme xenotypes the SW species pack drags in around the Jawa; keep the clan roster clean (Jawa + a few reflavored kin).

**Distinct-from line:** vs. everyone — the Jawa are *small, many, poor, and rising through salvage*, the mirror-image of the Empire (*tall, few, rich, descending from orbit*). The entire campaign is that contrast: the scrappers who build from garbage vs. the state that owns the sky.

---

## The cast, diffed (the forcing function)

| Axis | Empire | Hutt kajidics (×1–3) | Bounty Hunters | Jawa clans |
|---|---|---|---|---|
| **Silhouette** | uniform army; grey human ranks → red-skinned Sith elite by Act III | gaudy alien mob around a throned Hutt | idiosyncratic individuals | hooded swarm, glowing eyes |
| **Numbers** | few, elite | medium muscle, plural rival lords | very few / lone | many, weak |
| **Tech** | Ultra (only one) | sells all / fields mid | mid-high idiosyncratic | Industrial floor |
| **Disposition** | permanent enemy, incorruptible, monolithic | tradeable-always, treacherous, *rival to each other* | hired, buyable-once | player / allied kin |
| **Unique verb** | THE FORCE (NPC-only), wielded by Sith-race ranks | the persistent market + bounty board; play lords off each other | named recurring rivals | recycle enemies into assets |
| **Vector** | vertical (orbit/sky) | horizontal (markets) | personal (tracks *you*) | subterranean (salvage/caverns) |
| **Relation to Heat** | *is* the timer | *raises* it (trade) | *spawned by* it | *manages* it (go dark, salvage) |
| **Loot signature** | charge gear + unusable Force artifact | silver, slaves, exotic stock | unique trophy weapons | droid brains, scrap |

Every row differs across all four columns → the cast passes the diff test. No two factions could swap profiles unnoticed.

**Hutt underlings vs. the standalone Bounty Hunters — keeping them distinct.** The Hutt factions now field Trandoshan/Rodian *trackers* as rank-and-file muscle, which risks blurring into the Bounty Hunters faction (§3). The clean division: Hutt underlings are **disposable crew tied to a place** (they defend the Hutt's base, spawn in his raids, die anonymous); the Bounty Hunters are **named free agents tied to you** (they arrive alone via the board, have persistent identities, carry trophy weapons). A Rodian in a Hutt raid is a mook; a *named* Rodian hunter dispatched by that Hutt's bounty is a Bounty-Hunter-faction spawn. Same species, different faction + different narrative weight — that contrast is deliberate, not a collision.

---

## Dependencies & next steps (decision translation)

**Ready to build now (no gate):** Hutts, Bounty Hunters, Jawa clans — all rest on [LOCKED] lore + adopted mods. Their dossiers can go straight to (B) generation-layer patches + (C) save placement.

**Gated on VERIFY:** the Empire's **Force augment** — needs the Fetcher return (`2026-08-05_enemy_psycast_ai.txt`) confirming (1) the 1.6 Force mod + VPE basis, (2) the pawnkind-only grant path with no player access, (3) the Cherry-Pick guard scope. *Workaround so we don't block:* the Empire dossier is fully buildable *without* the Force today (charge-tier + uniformed ranks + orbital doctrine already make it distinct); the Force is an *additive* signature we bolt on once verified. Do not hold the Empire on it.

**Still gated (campaign-wide):** the full Sensible Factions casting call decides whether Separatist-remnant androids [LOCKED as a territorial register, concept.md §92] and other Outer Rim factions join the cast — those get dossiers when cast.

**Recommended next steps:**
1. On Fetcher return: resolve the Force VERIFY items; finalize the Empire augment.
2. Draft the Backstory Constructor personas (Empire Moff, Hutt broker, 2–3 named bounty hunters, 3–5 Jawa founders) — the named-leadership layer is the highest flavor-per-effort work.
3. Write the (B) override patches per dossier (descriptions, meme lists, pawnGroupMaker act-compositions, raidLootMaker filters).
4. Add each faction's Cherry-Pick lines to `cherry_picker_killlist.md`.
5. Re-diff after personas are written; re-differentiate any drift.
