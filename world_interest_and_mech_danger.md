# Making the World More Interesting — Deadlier Mechs, Crazy Animals, Unusual Threats

_Campaign doc for the RimWorld 1.6 / Odyssey gravship expedition. Companion to `required_mods.md`, `forbidden_mods.md`, `Gravship_Campaign_Planning_Discussion_2026-08-02.md` (§19 enemy-danger framework), and `cherry_picker_killlist.md`._

**Created:** 2026-08-03
**Status:** DRAFT candidate list — every Workshop ID + 1.6 status below was confirmed via Fetcher search (`2026-08-03_mech_danger_and_world_interest`, `2026-08-03_tribbles_and_prolific_wildlife`). Source zips for the GitHub-hosted candidates are being pulled for def-level examination (`2026-08-03_mech_world_source_pulls`); Workshop-only mods can't be source-audited until installed. Nothing here is subscribed yet — this is the vetting pass.

---

## 0. The lens (read first)

This request — "make mechs super dangerous, add crazy animals and unusual threats" — is governed by two things already in the docs, and they pull in the same direction:

1. **The §19 enemy-danger thesis** (planning doc): danger should come from **fewer enemies with dangerous *capabilities*, coherent tactics, and clear objectives** — NOT from "more bodies, more raid points, more hit points." §19.5 explicitly lists **"huge bullet-sponge enemies," "simply multiplying raid points," and "endless drop-pod spam"** under *What to Avoid*. So "super dangerous mechs" done right = smarter AI + qualitatively new mech capabilities (EMP, breaching, boarding, area-denial, ship-system attacks), tuned so retreat stays legitimate — **not** mechs with 3× HP.

2. **The anti-exponential principle** (forbidden_mods.md): the gravship + VFE-Factory are the ONLY scalable progression trees. **Enemy-side content and flavor/threat content pass the 7-question test trivially** — they raise no *player* capability ceiling. The three things that DO get scrutiny here: (a) mods that hand the *player* a parallel automation/logistics ladder (Rollers), (b) mods that dissolve gravship scarcity gates (Mini Gravships main, GravTech), (c) creatures that become an exponential *player* economy (Tribbles-as-livestock, Alpha Animals' "living resource farm").

**Bottom line up front:** almost everything you named is adoptable; two need a variant/config guardrail (Tribbles, Mini Gravships → Lite); two are genuine pillar conflicts to decline or heavily restrict (Rollers, GravTech); and the single best upgrade to "deadlier mechs" is a *qualitative* expansion (Reinforced Mechanoids 2 and/or Mechanoids: Total Warfare) sitting on top of the CAI-5000 smart-AI backbone you already adopted — with a hard "enemy-side only" discipline on VFE-Mechanoids' player toys.

---

## 1. DEADLIER MECHANOIDS

You already have the *behavior* layer decided: **CAI-5000** (smarter raid AI — tactical pathfinding, cover use) is the adopted backbone, and **Combat Extended is forbidden**. CAI-5000 is confirmed 1.6-current (GitHub `kbatbouta/CAI-5000`, plus a 1.6 recompile `Miquall/df`). What's missing is the *content* layer — more distinct, more capable mech archetypes — and a *tuning* knob. Recommendations, best-to-worst by pillar fit:

### ✅ Reinforced Mechanoids 2 (RM2) — TOP PICK for qualitative mech danger
- **Workshop:** source on GitHub `emipa606/ReinforcedMechanoid2` (packageId `Mlie.ReinforcedMechanoid2`). **Source audited 2026-08-03** (extracted into `mod_sources/ReinforcedMechanoid2-main`). **Confirmed 1.6-native** (About.xml supportedVersions=1.6; deps Harmony + Biotech + VEF Core). NOTE: `Helixien/ReinforcedMechanoids-Vol-1` is the **1.3-only original — superseded by RM2, do NOT install** (reference only).
- **What it is:** "An expansion of vanilla mechanoids adding new threats, weapons, buildings, a faction and gameplay mechanics that perfectly fit into the vanilla game." Community gold-standard *qualitative* mech mod. **Source audit confirms:** ~13 new mech types (Behemoth, Caretaker, Falcon, Gremlin, Harpy, Locust, Marshal, Ranger, Sentinel, Vulture, Wraith, Zealot, Matriarch) with dedicated ThinkTree/Duty/Maneuver defs = the coherent-tactics content §19 wants, not stat-inflated reskins.
- **Pillar verdict:** ✅ **ADOPT (enemy-side) — with one confirmed guardrail.** Source audit found a **player-buildable Gestalt Engine** (building + "gestate matriarch" recipe, gated behind research `RM_ReinforcedMechanoids`) — i.e. RM2 carries a real player-mechanitor payload, NOT just "modest buildings/weapons." **Apply the same enemy-side-only discipline as VFE-Mechanoids:** leave the Gestalt research untaken, or Cherry-Pick the Gestalt Engine building + gestate recipe out. The mech *threats* + faction are the adopt target. Verify its new faction plays nicely with Faction Filter / Sensible Factions; §19.5 weapon-balance audit still catches any power-creep outliers.

### ✅ Mechanoids: Total Warfare — STRONG PICK, escalation built in
- **Workshop:** 3555799437. **Confirmed 1.6**, updated 2026-05-04, ~44k subscribers. Appears **Workshop-only** (no GitHub repo surfaced → can't source-audit until installed).
- **What it is:** "Reconstructs vanilla combat logic, expands battle scale, adds ~a dozen distinctive mechanoid units" with **progressive difficulty that unlocks as you trigger conditions** — and, in the author's own words, "**avoiding unnecessary power creep**," with a raid-intensity slider if it gets overwhelming.
- **Pillar verdict:** ✅ **ADOPT (with a test-world trial).** The escalation-on-progress design mirrors VFE-Mechanoids' Total War concept and your "some enemies remain frightening throughout" goal (§19.6). The self-described *no-power-creep + adjustable* stance is exactly your §19.5 guardrail. **Caveats:** (1) Workshop-only = examine in-game, not from source; (2) it "reconstructs vanilla combat logic" — **verify CAI-5000 compatibility** (two mods touching combat logic can collide); test-world both together and read Player.log. **Decision point:** RM2 *or* Total Warfare *or* both — see tradeoffs in §7.

### ✅ Mechanoid Invaders — GREAT archetype fit, check the dependency
- **Workshop:** 3418853181. "XCOM-inspired combat mechs, each with a **unique mechanic** — AI-usable buffing abilities, toxins that hijack hosts to spawn more mechs."
- **Pillar verdict:** ✅ **ADOPT-CANDIDATE.** Unique-capability-per-unit is precisely the anti-bullet-sponge design §19 wants. **Dependency to verify:** requires **Expanded Biotech Style Genes** framework — Fetcher filed to confirm that's a pillar-neutral library (it should be; style-gene frameworks are cosmetic/definitional). Confirm before adopting.

### ✅ More Mechanoids (Continued) / More Vanilla Mechanoids — LIGHT variety filler
- **Workshop:** 3557972474 (Continued). Adds 5 vanilla-style types (Crawler, Skullywag, Flamebot, Mammoth, Assaulter) "for an endgame challenge."
- **Pillar verdict:** ✅ **OPTIONAL ADOPT.** Pure enemy variety, vanilla-styled. Lower priority than RM2/Total Warfare (some overlap). Fine to stack for texture; watch total mech-roster bloat (Cherry Picker can trim redundant/off-theme types). **Skip `MoreMechanoidsWorkModes`** (GitHub `WVCSergkart`) — that's a *player mechanitor* work-mode mod = automation ladder, forbidden.

### ✅ Odyssey Mechanoid Raid Adjustment — TUNING KNOB (adopt)
- **Workshop:** 3531624055. Adjusts mech-raid warning time, arrival delay, threat points, threat multiplier, interval, on/off toggle.
- **Pillar verdict:** ✅ **ADOPT.** Pure config lever, no content. This is your dial for the **pursuing-mechanoid cadence** the campaign leans on (tighten the timer so you run out of *time* to grab all cargo — the preferred counter-lever from required_mods.md over nerfing hauling). Passes 7-q trivially.

### ⚠️ VFE-Mechanoids — ENEMY-SIDE YES, player toys NO (already in stack, needs 1.6 refresh)
- **Local source is 1.5-capped/stale** (About.xml lists 1.3–1.5) → **must verify/refresh 1.6 before load.** Ships the native **"Total War" mechanic** (mech faction strengthens as more ships land = escalating danger, ✅ wanted) BUT also buildable player mechs + automated machines that **duplicate VFE-Factory and hit the mechanitor/automation ban.**
- **Pillar verdict:** ⚠️ **KEEP for the enemy faction + Total War escalation; discipline OFF the player-mech/automation payload** — identical ruling to the Drone Factory (adopt the threat, ban the workforce). The "disable Total War" toggle exists in mod options if the escalation ever stacks too hard with Total Warfare/RM2.

### ❌ Reject / avoid (wrong kind of danger)
- **Dire Raids (1542379675)** and **MultipleRaids (2043857349)** — these add danger by **multiplying raid points / spawning extra simultaneous raids.** That's the *exact* pattern §19.5 lists under "What to Avoid" (bigger numbers, not smarter enemies; performance-degradation-as-difficulty). ❌ **Do not adopt.** Your quantity dial is already the Raid Adjustment mod + Custom difficulty; danger should be *qualitative*.
- **RaidersNeverDie** — removes raider death-risk → longer bullet-sponge fights. ❌ Off-thesis.

---

## 2. CRAZY ANIMAL PACKS

All pure fauna-content mods pass the 7-question test trivially (they raise no player ceiling) — this is the "flavor welcome in any quantity" category. The only scrutiny is for creatures that become a *player exponential economy*.

### ✅ Alpha Animals — TOP PICK
- **Workshop:** 1541721856. 100+ vanilla-friendly creatures; design philosophy = **every creature brings a new mechanic** (walking tanks, night-time stalkers, indestructible plant monsters, giant spiders).
- **Pillar verdict:** ✅ **ADOPT.** This is §19's "qualitative danger" applied to wildlife — the animal analog of RM2. **One guardrail:** it includes a **"living resource farm" creature** — identify it in-game and, if it functions as an infinite renewable-resource generator, **Cherry-Pick it out** (same discipline as the anti-exponential principle; it's one authored creature, easy to remove without touching the rest). Everything else is clean.

### ✅ Vanilla Animals Expanded (VAE) — CLEAN BULK VARIETY
- **Workshop:** 2871933948. All VAE modules merged into one mod with **per-animal toggles** in options (no bloat).
- **Pillar verdict:** ✅ **ADOPT.** Pure vanilla-styled fauna variety. Per-animal toggles let you curate the roster to fit biomes/theme. Pairs naturally with Alpha Animals.

### ✅ More Dangerous Game — PREDATOR-THREAT TUNING (adopt)
- **Workshop:** 2364245786. Raises animal revenge chance, lets predators target colonists — "your colonists will be prey." Fully configurable.
- **Pillar verdict:** ✅ **ADOPT (tune to taste).** Config lever, no content ladder. Turns ambient wildlife into a real *unusual threat* (manhunter/predator pressure during expeditions and disposable field camps — thematically perfect for "land somewhere dangerous"). Start conservative; it can be brutal.

### ⚠️ Tribbles! (Continued) — FUN, but PILLAR EDGE-CASE (adopt as THREAT, not livestock)
- **Workshop:** 2672501251 (Continued; original 1813882773 by skyllianhamster). Adds Star Trek tribbles. Also available inside **YASTM / Yet Another Star Trek Mod (3547459322)** alongside other Trek fauna (Selath, Mugato, Targ) if you want the wider Trek bestiary — but note YASTM also adds phasers/disruptors/tricorders = **SW-theme collision + a weapon-balance surface** (§19.5), so prefer the **standalone Tribbles** mod over YASTM for theme coherence.
- **The pillar question:** a tribble is *by definition* an exponential breeder. That's a delightful comedic **infestation threat** (they overrun a map, devour your food stores, must be purged — a genuine "unusual threat") — but it becomes an **anti-exponential violation** the moment tribbles are a ranchable food/wealth/trade resource (infinite meat/breeding economy).
- **Pillar verdict:** ⚠️ **ADOPT as a threat/comedy creature; do NOT let it become a livestock economy.** Verify from the mod's defs (source being sought) whether tribbles are (a) tameable/butcherable with high reproduction — if so, self-limit: don't farm them, treat outbreaks as events to purge — or (b) already wild-only vermin, in which case it's clean as-is. Confirm 1.6 status (it's a "Continued" fork; the original was 1.2). **Great flavor, small guardrail.**

### 🎚️ "PROLIFIC amounts of animals on some maps" — this is a TUNING lever, not a mod to hunt
- Wildlife density per biome is exactly what **Choose Biome Commonality (2582875043)** and **Map Designer (2111424996)** control — both already on your Samuel-Streamer director-mod shortlist (`Custom_World.md`). You can dial specific biomes/maps to **prolific fauna density**, giving the "this world is *teeming*" feel on some landings and desolation on others — variety across destinations, which serves the expedition fantasy.
- **Pillar verdict:** ✅ **Use the director mods you already planned — and there's a better purpose-built option now confirmed.** The Fetcher search (`2026-08-03_tribbles_and_prolific_wildlife`, result now in) surfaced dedicated density mods that beat the biome-commonality workaround for *this specific* "teeming fauna" goal:
  - **Choose Wild Animal Spawns (WS 2564042934, GitHub `emipa606/ChooseWildAnimalSpawns`)** — ✅ **best fit.** Per-biome, per-animal spawn-rate control **plus an overall animal-density slider per biome**, works on vanilla + modded animals, copy-values between biomes. GitHub-hosted → source-auditable. This is exactly the "make some maps PROLIFIC" knob, with finer control than Map Designer.
  - **Animal Commonality Tweaker (WS 2591446825)** — loads last and overwrites the biome max-animal-density values (e.g. Tropical Swamp 6.5 vs Ice Sheet 0.2). Lighter, blunter; a fallback if you want one global multiplier rather than per-animal control.
  - **Always Wild Animals Continued (WS 3307454566)** — continually spawns animals at map edges (max count + check-interval configurable); explicitly respects Vanilla Events conditions that disable spawns. This is the "endless teeming" flavor but watch the perf cost + that it doesn't trivialize hunting into an infinite meat tap (mild anti-exp watch — it's wild spawns not ranch, so low risk, but note it).
  - **Pillar note:** all three are density/spawn tuning = flavor knobs, pass the 7-q test trivially (no player capability ceiling). Choose Wild Animal Spawns is the recommended adopt; the director mods (Biome Commonality + Map Designer) still cover world-shape and remain planned. 🔎 confirm each 1.6 tag before subscribing (per the 1.6-scoping rule).
- **Interaction note:** high animal density + **More Dangerous Game** + Alpha Animals predators = potentially very lethal landings. That's on-theme ("we are not ready to land there yet") but tune the three together, not independently.

---

## 3. UNUSUAL THREATS / WORLD EVENTS

### ✅ Vanilla Events Expanded (VEE) — TOP PICK
- **Workshop:** 1938420742. GitHub `Vanilla-Expanded/VanillaEventsExpanded` (source-available → auditable, being pulled). Adds new events "in line with vanilla — nothing too drastic," including a new **"Purple events"** tier: instead of strictly good/bad, they **force players to adapt** and last significantly longer than Toxic Fallout / Volcanic Winter. Configurable frequency (down to 0).
- **Pillar verdict:** ✅ **ADOPT.** "Force players to adapt" = your §19 counterplay thesis at the world-event level. No player ceiling raised. GitHub-hosted. Clean.

### 🔁 What you ALREADY have for "unusual threats" (build on these, don't duplicate)
Your stack already carries a lot of threat texture — recommendations should extend, not overlap:
- **VFE-Insectoids2** (local source) — biological-hazard force (§19.4 archetype: nests in machinery, crew isolation, uninhabitable-until-purged). ✅ already in.
- **VFE-Pirates + VFE-Deserters** (local) — human raider capability + the Imperial-pursuer militarized force.
- **CAI-5000** — the smart-AI layer that makes ALL of the above tactically dangerous (the single highest-leverage "danger" mod you have).
- **Ancient Urban Ruins + Dungeon Pack** — exploration threats gated behind *entering* structures (Hit Point enforcer makes them non-strippable-from-outside).
- **Custom difficulty (tuned)** — the vanilla knob §19.6 leans on for the "selective difficulty" distribution.

### 🎯 Gaps worth a dedicated look (candidates, lower confidence — verify 1.6 + source)
- A **siege/artillery-capability** enhancer for the §19.4 "Siege and Counter-Siege" archetype — vanilla + VFE-Pirates may already cover this; audit before adding a mod.
- **Anomaly is benched** (per docs) — so horror/entity threats are *out*; don't reintroduce them via an events mod. Keep VEE's config trimmed of any Anomaly-dependent events if present.

### ❌ Avoid
- Raid-quantity multipliers (Dire Raids / MultipleRaids — see §1) — quantity ≠ the danger you want.
- "Colony-shattering disaster" mega-event packs from big modpacks — audit each event for the §19.5 "untelegraphed one-shot" anti-pattern before trusting a bulk events mod beyond VEE.

---

## 4. THE FOUR NAMED MODS YOU FLAGGED — verdicts

### ❌ "Rollers" = **Industrial Rollers – Conveyor belts & Automation (WS 784327493)** — DECLINE (it can't feed VFE-Factory; it duplicates it)

**Re-evaluated 2026-08-03 against the specific question: "would Rollers assist VFE-Factory in a meaningful way, given we're going deep into VFE-Factory and supportive overlap is OK?"** The refined answer is no — and for a stronger reason than the first pass. This isn't the acceptable "supportive overlap" case; it's true duplication of the exact subsystem you want depth in.

- **What it is (established, from delivered search text):** Industrial Rollers builds "your own roller system which will transport goods to their destination without colonist interaction" — a standalone haul-automation network keyed to **vanilla stockpiles**, not to VFE-Factory machines. Its own Workshop page advertises pairing with **Project RimFactory** ("bundle the two mods and create the ultimate automated colony") and S.A.L. auto-crafters — i.e. it's architected for the RimFactory automation stack that `forbidden_mods.md` already excludes.
- **The decisive fact (established, from local source `VanillaFurnitureExpanded-Factory-main/1.6/`):** VFE-Factory **already ships its own complete conveyor-logistics layer** — surface conveyors, *underground* conveyor entrance/exit, a splitter with a filter tab (`ITab_SplitterFilter`) for routing/sorting, and a `HaulFromConveyor` job — and its factory machine defs reference conveyor input/output directly. **Going deep into VFE-Factory *is* going deep into its conveyors.** Rollers can't add that depth because it isn't upstream of the machines; there's no shared input/output comp for it to plug into. It would be a second, disconnected belt network running beside the sanctioned one.
- **Both "assist" paths fail:** (a) *feeding* the VFE machines — VFE conveyors + splitters already do this, so Rollers adds nothing to the sanctioned tree; (b) *extending* VFE routing — no integration hook exists, so the two belt systems can't interconnect.
- **Pillar verdict:** ❌ **DECLINE.** A base-wide parallel haul-automation network is precisely the "logistics economy that trivializes hauling labor and removes the pressure to move on" the pillars guard against — fails Q5 globally regardless of the VFE-depth reframe. Net negative, not neutral: two non-interoperable belt systems = compat/UX cost with zero payoff to the one tree you care about.
- **The way to actually go deep into VFE-Factory:** lean on its **underground conveyors** (long-distance routing between production cells — the one gap an external belt might have filled, already covered natively), the **splitter/filter** sorting, and the **BASIC→COMPLEX tier ladder**. That's sanctioned depth.

> **Premise resolved (2026-08-03):** confirmed "Rollers" = Industrial Rollers, and the "supportive overlap" hope doesn't hold because VFE-Factory already contains the conveyor system natively. Would only reopen if a 1.6 fork adds an explicit VFE-Factory input/output comp (not expected). Rollers' own 1.6-support status is unconfirmed (the classic roller mod stalled at 1.3 per the Reddit thread); Fetcher `2026-08-03_rollers_vfe_integration` filed to confirm, but it doesn't change the verdict.

### ✅ **Small Furniture (WS 3696700829)** — CLEAN ADOPT
- Adds small/medium furniture + workbenches as new variants or **resizes of existing buildings**, configurable in options.
- **Pillar verdict:** ✅ **ADOPT.** Pure space-efficiency QoL — ideal for a cramped gravship deck where every tile competes with substructure. Raises no ceiling; passes 7-q trivially. Exactly the "flavor/QoL welcome in any quantity" category. Appears Workshop-only (the GitHub hit was a different mod).

### ⚠️ **GravTech (WS 3545374124)** — SCARCITY-GATE RISK, examine before adopting
- **What it is:** "Create powerful gear and parts of a gravship **from gravcores**." Has a family of addons (Big Cannons for VGE, Anomaly for Gravship, Biotech for Gravship) and a **VGE-compat companion (WS 3737033254)** — so it's *designed to coexist with VGE*, unlike Mini Gravships.
- **The pillar question:** your docs establish that **gravcores are quest-only and are THE vanilla scarcity gate** on hull expansion (6-extender cap + gravcore-quest cadence). A mod that lets you **craft powerful gear from gravcores** either (a) creates a **parallel progression ladder** (spend gravcores → power gear → repeat), or (b) **devalues gravcore scarcity** by giving them a crafting sink that competes with expansion. 7-q: Q1 (parallel ladder?) and Q3 (scales via crafting?) are the live risks.
- **Pillar verdict:** ⚠️ **HOLD — examine defs before adopting.** VGE-compatible is a big plus (no sole-layer conflict), and "gravcore-gated powerful gear" *could* be fine if it's a small set of authored, non-repeatable items (a singular-exception, like the quest-only lightsaber ruling). It's a **problem if it's a repeatable crafting economy** or if it inflates player combat power against the §19.5 no-arms-race rule (esp. the "Big Cannons" addon). Source being sought; if Workshop-only, judge in a test world. **Lean: adopt a *narrow* subset (maybe the maintenance/utility items via the VGE-compat companion, WS 3737033254, which mentions a "Maintenance Device" for early game) and skip the Big Cannons combat addon.**

### ❌/⚠️ **Mini Gravship** — main version CONFLICTS; **Mini Gravships Lite** is the workaround
- **Mini Gravships (WS 3527312835):** its own description confirms the exact pillar violations your docs predicted — it **"removed the amount limit of gravship-linked structures"** (destroys the 6-extender hull cap), makes the **grav engine buildable** and power-producing (removes the gravcore-quest scarcity gate), buffs hull to 500hp, etc. ❌ **DECLINE** — breaks two scarcity pillars AND collides with VGE-as-sole-layer. The prior "forbidden" ruling is now **confirmed from the mod's own text.**
- **Mini Gravships Lite (WS 3538850569):** explicitly **strips the problematic parts** — no buildable grav engine, no structure-limit removal, no power changes; "most things kept as vanilla," patches only to make parts not-stealable/not-flammable, and it's designed to **"load near the top for compatibility with other gravship mods."** ⚠️ **EXAMINE as a possible adopt** — this is a genuinely different pillar profile. The open question is whether "Lite" still *overhauls* gravship structures (rival to VGE) or is a light compatibility/QoL patch that can sit alongside VGE. **Verify VGE coexistence in a test world before adopting; if it duplicates or overrides VGE's structure defs, decline it too.**

> **Net on the two gravship mods:** the campaign's "VGE = sole gravship layer" rule means any mod that *redefines gravship structures/engine* is a rival overhaul and out. Mini Gravships (main) does exactly that. GravTech and Mini Gravships **Lite** are the two that *might* coexist with VGE — both need a source/test-world check, and both should be adopted narrowly (utility, not combat power or scarcity-dissolution) if at all.

---

## 5. THE 7-QUESTION TEST — applied, at a glance

| Mod | Parallel player ladder? | Scales indefinitely? | Trivializes scarcity/ship? | Verdict |
|---|---|---|---|---|
| Reinforced Mechanoids 2 | No (enemy-side) | No | No | ✅ Adopt (enemy-side) — leave/Cherry-Pick the player Gestalt Engine (research-gated) |
| Mechanoids: Total Warfare | No (enemy-side) | No (no-power-creep by design) | No | ✅ Adopt (test CAI-5000 compat) |
| Mechanoid Invaders | No (enemy-side) | No | No | ✅ Adopt (verify style-gene dep) |
| More Mechanoids (Continued) | No | No | No | ✅ Optional |
| Odyssey Raid Adjustment | No (config) | No | No (it's the scarcity *dial*) | ✅ Adopt |
| VFE-Mechanoids | **Yes if player mechs used** | Yes (player automation) | No | ⚠️ Enemy-side only |
| Alpha Animals | No | No (except 1 "resource farm" creature) | No | ✅ Adopt (Cherry-Pick the farm creature) |
| Vanilla Animals Expanded | No | No | No | ✅ Adopt |
| More Dangerous Game | No (config) | No | No | ✅ Adopt |
| Tribbles! | No (unless farmed) | **Yes if ranched** | No | ⚠️ Threat-only, don't farm |
| Vanilla Events Expanded | No | No | No | ✅ Adopt |
| Dire Raids / MultipleRaids | No | Yes (raid-point inflation) | No | ❌ Wrong kind of danger (§19.5) |
| **Industrial Rollers** | **Yes (logistics automation)** | **Yes** | **Yes (labor/hauling)** | ❌ Decline — VFE-Factory already has native conveyors; Rollers can't feed them, only duplicate them |
| Small Furniture | No | No | No | ✅ Adopt |
| **GravTech** | **Maybe (gravcore crafting)** | **Maybe (repeatable?)** | **Maybe (devalues gravcores)** | ⚠️ Hold; narrow subset only |
| **Mini Gravships (main)** | No | **Yes (unlimited structures)** | **Yes (buildable engine, no cap)** | ❌ Decline + VGE conflict |
| Mini Gravships **Lite** | No | No | Maybe (verify not a VGE rival) | ⚠️ Examine for VGE coexistence |

---

## 6. LOAD-ORDER / COMPATIBILITY NOTES (for build time)

- **CAI-5000 + Mechanoids: Total Warfare** both touch combat logic → **test together first**, read Player.log. If they collide, CAI-5000 (behavior) is the keeper; pick RM2 (pure content, no AI override) over Total Warfare in that case.
- **Escalation stacking:** VFE-Mechanoids Total War + Total Warfare's progressive unlock + Dire-Raids-style multipliers would compound. You're NOT taking the multipliers (§1 reject), but **don't run both Total War *and* Total Warfare escalation at max** — pick one escalation driver, or dial one down via mod options / Raid Adjustment.
- **Alpha Animals + VAE + More Dangerous Game:** Alpha Animals notes its spawn probabilities were tuned "with no other animal mods installed." With VAE also on, **use per-animal toggles + biome commonality** to keep density sane, then layer More Dangerous Game's lethality on top last.
- **Mini Gravships Lite / GravTech vs VGE:** anything gravship-structural loads relative to VGE per each mod's own instruction; **VGE remains the authority** — if a mod overrides VGE structure defs, it's out.
- **Cherry Picker targets surfaced here:** Alpha Animals "living resource farm" creature; any redundant/off-theme mech types from More Mechanoids; YASTM weapons if that route were taken (it isn't).

---

## 7. DECISION TRANSLATION

**The decision:** which mods to add for deadlier mechs + crazy animals + unusual threats, without breaking the anti-exponential pillars or VGE-sole-layer.

**Recommended adopt set (high confidence):**
- Mechs: **Reinforced Mechanoids 2** (qualitative) + **Odyssey Raid Adjustment** (tuning) + keep **VFE-Mechanoids enemy-side** + **CAI-5000** (already in). Consider **Mechanoids: Total Warfare** and/or **Mechanoid Invaders** after a compat test.
- Animals: **Alpha Animals** + **Vanilla Animals Expanded** + **More Dangerous Game**; **Tribbles** as a threat/comedy creature only.
- Threats/events: **Vanilla Events Expanded**.
- Named QoL: **Small Furniture** ✅.
- Prolific-fauna maps: tune via **Choose Biome Commonality + Map Designer** (already planned) — no new mod needed.

**Viable alternatives / tradeoffs:**
- **RM2 vs Total Warfare vs both.** RM2 = GitHub-auditable, pure content, safest with CAI-5000. Total Warfare = bigger scope + built-in escalation + no-power-creep design, but Workshop-only and "reconstructs combat logic" (CAI-5000 collision risk). **Both** = richest roster but highest bloat/compat surface; if both, run only ONE escalation driver at full strength. **Lean: start with RM2 + CAI-5000; add Total Warfare only if you want more and it passes the compat test.**
- **GravTech:** narrow-utility-subset adopt vs full decline. Big Cannons addon is the part most likely to fail §19.5.

**Dependencies:** Mechanoid Invaders → Expanded Biotech Style Genes (verify pillar-neutral). VFE-family → Vanilla Expanded Framework (already in). RM2 → verify its faction vs Faction Filter.

**Principal risks:** (1) CAI-5000 × Total Warfare combat-logic collision; (2) animal-lethality stack (Alpha + VAE + More Dangerous Game + prolific density) becoming *un*fun-lethal rather than tense — tune incrementally; (3) GravTech/Tribbles quietly opening an exponential sink if adopted without the guardrails; (4) VFE-Mechanoids local source is 1.5-stale → 1.6 refresh required regardless.

**Missing information that would help:** def-level source for Total Warfare, GravTech, Mini Gravships Lite, Tribbles (Workshop-only ones can only be judged in a test world); confirmation of the Expanded Biotech Style Genes dependency; whether any 1.6 Rollers fork adds a VFE-Factory input/output comp (would reopen that verdict — not expected).

**Recommended next steps:** (1) Rollers premise now resolved — declined (§4), no action; (2) let the source-pull Fetcher land, extract RM2 + VEE into mod_sources, audit; (3) build a throwaway 1.6 test world with CAI-5000 + RM2 (+ Total Warfare) and read Player.log for combat-logic conflicts; (4) fold the adopted set into `required_mods.md` and add the Cherry-Pick targets (Alpha "resource farm" creature) to `cherry_picker_killlist.md`; (5) decide RM2-only vs RM2+Total Warfare after the compat test.

---

## 8. Provenance
- Workshop IDs + 1.6 status + self-descriptions: Fetcher `2026-08-03_mech_danger_and_world_interest` (23 searches, all worked) and `2026-08-03_tribbles_and_prolific_wildlife`.
- Source zips being pulled for def-level audit: Fetcher `2026-08-03_mech_world_source_pulls` (RM2, RM-Vol1, VEE, CAI-5000 1.6 recompile, Outland Genetics) + repo-confirmation searches for the Workshop-only candidates.
- Design constraints applied: `Gravship_Campaign_Planning_Discussion_2026-08-02.md` §19 (enemy-danger framework, esp. §19.4 archetypes + §19.5 what-to-avoid); `forbidden_mods.md` (anti-exponential principle, 7-question test, Project RimFactory exclusion, Mini Gravships/mechanitor bans, "mod count ≠ ceiling"); `required_mods.md` (CAI-5000 backbone, VGE sole layer, pursuing-mechanoid timer lever); `Custom_World.md` (biome-commonality director mods).
- **Evidence tags:** Workshop IDs/1.6-status/descriptions = **established** (Fetcher-confirmed). Pillar verdicts = **reasoned inference** from the mods' self-descriptions against the documented rules. Def-level behavior of Workshop-only mods (Total Warfare internals, GravTech recipes, Tribbles breeding, Mini Gravships Lite structure handling) = **to-be-verified** (marked ⚠️/HOLD, not asserted). "Rollers" = Industrial Rollers is now **confirmed**; that VFE-Factory ships native conveyors/splitter/underground routing is **established** (read from local 1.6 source).
