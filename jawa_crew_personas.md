# Jawa Crew Personas — the Five Founders

_Gravship Expedition campaign (RimWorld 1.6 / Odyssey). "Crashed Factory ship / Jawa stowaways" theme. Companion to `jawa_xenotype_and_religion.md` (xenotype + ideoligion + Part 4 society lore), `required_mods.md`, `faction_roster_v2.md`, and `context.md`._

**Created:** 2026-08-06. **Status:** DRAFT for review — five starting crew designed against canon Jawa material, our established Part 4 society lore, adopted mods, and the seeded story arcs. Names, skills, and traits are **authored intent**; every mod-dependent element is tagged so nothing reads as confirmed-buildable until verified in-game.

**Evidence tags:** ✅ verified from local source/canon · 🔎 needs in-game/mod confirmation · ◇ authored design intent (mine or user's) · ⚠️ pillar/feasibility flag.

---

## 0. Authoring tools — scope, and the 7-question pillar test

### 0.1 Character Editor — SCOPE NOTE (user, 2026-08-06) ✅ recorded

**Character Editor is used ONLY to tweak/fix lore-appropriate elements of a character — never to exploit gameplay.** The user was explicit: no min-maxing skills, no free bionics, no stat inflation. Its role is *fidelity* — making a pawn's genes/xenotype/name/backstory/appearance match the authored persona when the ordinary start doesn't produce it cleanly (e.g. forcing the Jawa xenotype onto a founder, correcting a childhood that the RNG mismatched, fixing a hood/appearance detail). This keeps it firmly on the **authoring-tool** side of the pillar line (same discipline shape as RimBridge in `rimbridge.md` §6: enrich the *fiction*, never raise the *player's ceiling*). Recorded so a future session doesn't re-litigate whether Character Editor is pillar-legal — it is, **at this scope only.**

### 0.2 The character-authoring + trait mods vs the 7-question test

The test (from `Gravship_Campaign_Planning_Discussion_2026-08-02.md` §12.2): (1) parallel progression ladder? (2) imposes dependency or removes a limitation? (3) scales indefinitely via trade/research/breeding/crafting/quests? (4) makes crew composition *less* important? (5) bypasses fuel/deck/expedition-risk/production-time/injury/mood/scarcity? (6) reducible to a single authored exception? (7) makes the ship more or less necessary?

**Backstory Constructor (WS 2907131508) ✅ adopted — PASSES cleanly.**
It authors *named characters* with hand-written lore + a `skillGains` table + a `workDisables` map (per `context.md`:513, `Custom_World.md`:64 — verified our docs). It is a **content-authoring tool, not a runtime system**: it sets a pawn's starting story once, at creation. Q1 no parallel ladder (it writes a fixed backstory, not a progression). Q3 no indefinite scaling (a backstory doesn't compound). Q4 it *increases* the importance of crew composition (distinct authored founders). Q5 it can *impose* limitations via `workDisables` (a Jawa who literally cannot do a work type — pillar-positive friction). Q6 it *is* the "single authored exception" mechanism. Q7 neutral to ship necessity. **Verdict: adopt for the five founders; it is the primary persona tool.** ⚠️ Only watch: don't hand a founder an inflated `skillGains` table that trivializes early game — author *characterful* skill spreads (with real weaknesses), not optimal ones.

**Character Editor ✅ adopted (context.md:307, "use Character Editor over Prepare Carefully — more stable, 1.6") — PASSES at the §0.1 scope.**
Preferred over Prepare Carefully for stability on 1.6. As a *fidelity/fix* tool (§0.1) it touches only appearance/xenotype/name/backstory correction. Q5 is the only risk row — Character Editor *can* bypass scarcity if abused (free skills/bionics/resources) — and the §0.1 scope note is exactly the self-restraint that closes it, identical in shape to the Leader-role / Droid-Depot self-limits already in the campaign. **Verdict: adopt as fix-only; the discipline, not the mod, is what keeps it clean.**

**Vanilla Traits Expanded ✅ ADOPT — with a per-trait audit (verdict reversed 2026-08-06 after Fetcher `2026-08-06_trait_mods_1p6`).**
Earlier I deferred VTE on the reasoning that it wasn't in our stack and could trip multiplier rows. The user corrected that ("File Fetcher requests for Traits mods to consider — these add a LOT to the game"), and the delivery settles the facts:
- **1.6-confirmed.** VTE's own `About.xml` (fetched, file `vanilla_traits_expanded_about.txt`) lists `supportedVersions` = 1.4 / **1.6**; packageId `VanillaExpanded.VanillaTraitsExpanded`; **WS 2296404655**; `modDependencies` = Harmony (2009463077) + **Vanilla Expanded Framework (2023507013)** — *both already in our stack.* No new framework burden. ✅
- **55 traits, and VTE says so itself:** "some being straight up stat upgrades." That candor is the whole point — VTE is a *mix* of storytelling traits and multiplier traits, so a blanket accept/reject is the wrong frame.
- **The per-trait screen is native.** VTE ships a **mod-options menu that sets any trait's commonality to 0** ("stopping it from ever appearing in the game again"). That IS our per-trait pillar audit, built into the mod: **keep the flavor/personality traits, zero-out any trait that grants a work-speed/skill/production multiplier or bypasses scarcity.** So VTE passes the 7-Q *as configured* — Q3/Q5 are only tripped by the multiplier subset, which we switch off at setup.
- **Setup action (◇, deferred to build time):** on first load, open VTE mod options and commonality-zero the stat-upgrade traits (the "straight up stat upgrades" it warns about); keep the quirky/behavioral ones. Since our five founders are hand-authored via Backstory Constructor, we mostly *hand-pick* their traits anyway — VTE's value is (a) a richer flavor pool to pick from for the founders and (b) more characterful randoms on any Jawa born/acquired later.

**What we already rely on for trait *behavior*** is the adopted social stack — **VSIE (WS 2439736083)** + **VSIE-Rational Trait Development (WS 2916405546)** + the growth-moment mods (RandomGrowthChoices Continued 3413983862 / Better Children Growth Moments 3642805464) — which drive emergent personality *from* traits. The Fetcher delivery (file 011) confirms VSIE and VTE are **independent, compatible mods** (community-confirmed you can run either without the other), so VTE layers cleanly onto our social stack.

**Other trait-pack candidates screened (delivery files 005–010) — DECLINE for now, to avoid pool bloat + duplicate flavor:** [DN] Bundle of Traits (WS 2600986277, ~27 traits), RimTraits – General Traits (WS 2206957172, ~46), RimTraits – Medieval Talents (WS 1916352291, ~35). All plausible, but stacking multiple trait packs multiplies the audit surface and dilutes each trait's rarity (VTE's commonality tuning gets swamped). One well-tuned pack (VTE) is the cleaner call. ⚠️ **Correction to a prior misread:** "More Persona Traits" (WS 2863308112) is about **persona *weapon* traits**, NOT pawn personality traits — exclude it from persona-trait consideration (it came from a streamer modlist name, not a real pawn-trait mod).

**Net:** the five founders are buildable with **Backstory Constructor + Character Editor (fix-scope) + vanilla/Biotech traits**, riding the already-adopted VSIE social layer. **VTE (now adopted, audited)** widens the flavor-trait palette to pick from but is **not a dependency** — every founder below is still authored to work on vanilla/Biotech traits alone, so the crew is buildable with or without VTE loaded.

---

## 1. Design principles for the founding five

Grounding sources, in priority order: **(a) canon Jawa material** — small hooded desert scavengers of Tatooine; obsessive traders and droid-tinkerers who *repair and resell* (often faulty) machines; travel in clan sandcrawlers; glowing orange/yellow eyes; speak Jawaese (the trade-cry "Utinni!" is canon vocabulary ✅); communicate partly by scent; clannish, wary of outsiders and of Tusken Raiders. **(b) Our Part 4 society lore** — all-male homosexual egg-laying clan; fast growth ⇄ rapid aging ⇄ honorable exile (the churn, not growth); **no recruitment** (kin-birth or the love-gate only); enslave-not-recruit; sell non-Jawa, keep-and-cherish Jawa; the new mood economy (grief on any Jawa death, joy on acquisition). **(c) The ideoligion** — "Articles of Passage," Nomad+Tunneler, automation *reverence not dependence*, haggling-as-devotion, ration-as-sacred. **(d) The seeded arcs** — §4.8 steal-the-droid-secret heist; §4.2 love-gate naturalization; §4.4 aging-exile succession.

**A good RimWorld starting trio-to-five needs:** complementary skills with real gaps (not five generalists); at least one crafter/constructor, one violence-capable pawn, one social/leader, one medic; and *characterful flaws* that generate story rather than optimal stat lines. The five below cover those roles **and** each one personally embodies one strand of the lore, so the crew *is* the design doc made flesh. Names are Jawaese-styled and evocative; ⚠️ hard-canon named Jawa individuals are extremely few, so treat these as **authored names in the canon style**, not claims of canon characters.

---

## 2. The Five Founders

### 2.1 Nekko Vok — "Captain of the Opened Hull" (Leader / Chief)

- **Role:** Ideoligion **Leader** ("Chief/Captain," per religion spec §2.3). The one who first cut into the crashed Factory ship's hull — mythologically the wielder of the relic **"The First Fusioncutter"** (§2.5). ◇
- **Age & arc seed:** **Oldest founder, near the aging threshold** — deliberately. Nekko is the living clock on the **§4.4 exile/succession arc**: the campaign's first great social test will be who leads when the Captain becomes "a net drain," and whether the clan honors its own harsh covenant on the pawn the player is most attached to. ◇⚠️ (This is the emotional core of the churn system aimed squarely at the player.)
- **Skills (authored spread, characterful not optimal):** high **Social** (negotiation/leadership; Jawa are traders), moderate **Intellectual**, low **Shooting**, poor **Mining/Construction** (he leads, he doesn't dig anymore). ◇ — author via Backstory Constructor `skillGains`; keep the totals modest.
- **Traits (vanilla/Biotech only):** a leadership-flavored positive (e.g. *Natural mood / Iron-willed* to model a steadying elder) + **Jawa xenotype genes** (DarkVision, small body). Avoid any work-speed multiplier trait. 🔎
- **`workDisables` idea:** disable **Violence** or **Mining** to force reliance on the others — a Chief who *cannot* do the grunt work makes crew composition matter (Q4-positive). ◇
- **Comedy/voice hook (SpeakUp/RimDialogue):** ceremonial, over-formal Jawaese pronouncements over trivial salvage; treats every haggle as a state occasion.
- **Embodies:** the Leader role + the succession/exile arc + the founding relic myth.

### 2.2 Tobb Nkik — "Keeper of the Articles" (Moral Guide / theologian)

- **Role:** Ideoligion **Moral Guide** ("Keeper of the Articles / Rememberer," §2.3) — the constitution-enforcer of the faith. ◇
- **Skills:** high **Intellectual** (the clan's researcher and rememberer), good **Social** (preaching/conversion), weak physical skills. ◇
- **Traits:** an *Ascetic*-style or *Too smart*-style vanilla trait fits the ration-as-sacred austerity and the intellectual bent. **No multiplier traits.** 🔎
- **The droid-mourner — mood-economy anchor (§4.2b):** Tobb feels the new **grief-on-Jawa-death** and **droid-funeral** beats hardest — he is the one who insists a destroyed droid gets its "retirement of the second hand" rite (§2.4), and who leads the mourning when *any* Jawa dies, even an enemy. This makes the abstract mood economy *diegetic* through one character. ◇
- **Comedy/voice hook:** quotes "the Articles" as scripture; scandalized by wasted repairable scrap; delivers eulogies for broken machinery.
- **Embodies:** the Moral Guide role + automation-reverence theology (§2.4/§2.7) + the mood economy (§4.2b).

### 2.3 Griz Utinn — "The Hands" (master scavenger / crafter)

- **Role:** the primary **crafter/constructor/miner** — the industrial spine of a crew whose whole economy is salvage-and-repair. ◇
- **Skills:** high **Crafting** + **Construction**, good **Mining**, passions in the making-things skills. The pawn who actually *runs* the VFE-Factory salvage loop and (eventually) the stolen Droid Factory. ◇
- **Traits:** *Hard worker* or an *industrious*-style vanilla trait + a **greed/haggler** flavor to tie into haggling-as-devotion (§2.7). **No production-speed multiplier from a trait pack** — keep it vanilla. 🔎
- **Arc seed — the §4.8 droid-theft protagonist:** Griz is the natural lead for the **steal-the-secret-of-droid-building** heist against the neutral territorial droids (DUM Squad / Rogue Droids). He's the one whose theology (repair, don't breed new hands) is *personally* tested when the clan finally seizes the means of manufacture. His `DarkVision` + Tunneler flavor makes him the ruin-crawler. ◇
- **Comedy/voice hook:** narrates loving repair monologues to half-dead droids; physically pained by scrapping something "still good."
- **Embodies:** the industrial pillar + the droid-theft arc + Tunneler burrowing-scavenger identity.

### 2.4 Yeku — "First-Hatched" (the young prodigy / shooter)

- **Role:** the crew's **violence-capable** pawn — hunter/shooter and skirmisher (Jawa fight by *running and shooting*, per the nomad-tactics note in `context.md`:307, not standing battles). ◇
- **Life-stage hook — the growth mechanic made visible (§4.3):** Yeku is the youngest founder, **recently and rapidly grown to adulthood** — the on-screen proof of the fast-growth engine. Author him as just-turned-adult so the RandomGrowthChoices / Better Children Growth Moments layer (adopted) has visibly shaped him. ◇
- **Skills:** high **Shooting**, decent **Animals** (a Jawa and his ill-tempered pack-beast), thin everywhere else — a specialist by youth, not yet rounded. ◇
- **Traits:** *Volatile / Nervous / Trigger-happy*-style vanilla trait — impulsive youth that generates VSIE social friction (arguments with elders). **Characterful, not optimal.** 🔎
- **Arc seed — the §4.2 love-gate candidate:** Yeku is the founder most likely to be the one who **falls in love with a captured other-clan Jawa slave**, triggering the naturalization ceremony that admits a new clan member through love. Seeding this on the *youngest* founder makes the love-gate a coming-of-age beat. ◇⚠️ (depends on the slave-romance feasibility flagged in §4.2 / the Fetcher pull `2026-08-06_jawa_reproduction_debt_mood_mods`).
- **Comedy/voice hook:** brash, impatient Jawaese chatter; overconfident "Utinni!" battle-cries; talks back to the Captain.
- **Embodies:** fast-growth (§4.3) + nomad skirmish tactics + the love-gate arc (§4.2).

### 2.5 Wim Ateeka — "The Twice-Kin" (medic / the living precedent of the love-gate)

- **Role:** the crew's **doctor/healer** — treats flesh and machine alike (a Jawa medic is a tinkerer who happens to work on bodies). ◇
- **Backstory hook — a naturalized outsider (§4.2 precedent):** Wim was born to a *different* Jawa clan, was **taken as a slave, and earned full clan membership through love** — the §4.2 love-gate, already resolved in his past. He is the *living proof* that the mechanic exists, and a foreshadowing of Yeku's arc. This gives the founding roster an internal history and makes the love-gate feel established, not hypothetical. ◇
- **Skills:** high **Medical**, good **Intellectual**, modest **Social** (still a little apart — "twice-kin," never quite forgets he was born elsewhere). ◇
- **Traits:** *Kind* or *Steadfast*-style vanilla trait; possibly a mild social penalty flavor to model the lingering outsider status (VSIE will surface this). **No multiplier traits.** 🔎
- **Tension hook:** Wim's presence quietly complicates the "sell non-Jawa, cherish Jawa" ethic — he embodies why *Jawa* slaves are never sold. If the clan ever wavers on the no-rot rule (§4.2), Wim is the conscience. ◇
- **Comedy/voice hook:** dry, slightly formal Jawaese; occasionally lets slip an unfamiliar loan-word from his birth-clan's dialect (a nice SpeakUp/RimDialogue flavor seam).
- **Embodies:** the medic role + the §4.2 love-gate as *established backstory* + the "kin is never sold" ethic.

---

## 3. Why these five, together

**Role coverage (RimWorld-sound):** Social/leadership (Nekko), Intellectual/research (Tobb), Crafting/Construction/Mining (Griz), Shooting/violence (Yeku), Medical (Wim). No dead weight, no five-generalist mush, and **deliberate gaps** (Nekko can't dig, Yeku is thin outside combat) that make each pawn matter — Q4-positive on the pillar test.

**Lore coverage (every strand embodied):** the two ideoligion roles (Nekko, Tobb); the industrial pillar (Griz); the reproduction/growth engine (Yeku, first-hatched); the aging/exile counterweight (Nekko, near threshold); the love-gate — both as *future* arc (Yeku) and *settled past* (Wim); the mood economy and automation theology (Tobb). The crew is the Part 4 lore rendered as five people.

**Arc coverage (the campaign's beats have protagonists):** succession/exile (Nekko), droid-theft heist §4.8 (Griz), love-gate §4.2 (Yeku → a future captive; Wim as precedent). The player starts with the *seeds* of all three defining arcs already planted in the founders.

---

## 4. Decision translation (per user's standing preferences)

**Decision this supports:** author five founders with Backstory Constructor (lore + `skillGains` + `workDisables`), fix appearance/xenotype fidelity with Character Editor at the §0.1 scope only, on vanilla/Biotech traits + the adopted VSIE social layer — no new mod dependency.

**Viable alternatives:** (a) **start with 3, grow to 5 by birth** — more faithful to the "small clan grows via eggs" fiction and a gentler early game, but delays role coverage (risky if you lose a specialist early); (b) **5 now** (this doc) — full role coverage from turn one, stronger opening, at the cost of some "we grew this clan" feeling; (c) a **6th founder** (a dedicated cook/hauler) if early-game logistics feel thin. **You chose 5 — this doc builds 5.** ◇

**Tradeoffs:** authoring five distinct founders is more upfront setup than a random start; the payoff is that the crew carries the lore and arcs from minute one. Deliberate skill gaps make the early game harder (intended friction).

**Dependencies:** Backstory Constructor (WS 2907131508 ✅), Character Editor (✅), the Jawa xenotype + Outland Genetics/HAR/Outer Rim (per `jawa_xenotype_and_religion.md` §1.5), the VSIE social stack (✅ adopted). The **love-gate / egg-laying / mood-economy** elements ride the open Fetcher pull `2026-08-06_jawa_reproduction_debt_mood_mods` — personas are authored so the *characters* exist regardless, with those mechanics layering in when confirmed.

**Principal risks:** (1) VTE multiplier creep — VTE is now ADOPTED (§0.2), but its "straight up stat upgrade" traits must be commonality-zeroed in mod options at setup, or they reintroduce Q3/Q5 multipliers; keep the audit discipline, not a blanket-off. Resist *stacking* additional trait packs (Bundle/RimTraits declined) — they swamp VTE's rarity tuning. (2) Character Editor scope-drift — the §0.1 discipline is the guardrail. (3) `skillGains` inflation — author weaknesses, not optimal lines. (4) The love-gate/egg-laying mechanics may need authored fallbacks (flagged in §4.6 of the religion doc) — Yeku's and Wim's arcs are written to survive as RP/RimBridge beats if no clean mod lands. Egg-laying specifically is a **confirmed gap** (§4.6): no verified 1.6 humanlike-oviparous mod exists.

**Missing info — now largely resolved (Fetcher `2026-08-06_jawa_reproduction_debt_mood_mods` delivered 2026-08-06, integrated into religion doc §4.2/§4.3/§4.6):** same-sex/male-pregnancy is ✅ solved (Simple Trans Expanded WS 3516912373 primary / Samesex IVF 2878580643 fallback); the love-gate slave-romance is ✅ mod-supported (More Slavery Stuff Continued WS 3530586159 precepts); the Hutt "pay-or-raid" beat is ✅ available (Tribute Demand 3711373966 / Raid Protection Fee 3650927927). **Two things stay bespoke:** literal **egg-laying** (⛔ no 1.6 mod — ship "narrate normal birth as eggs") and the **xenotype-death mourning** thought (no off-shelf mod — hand-author a ThoughtDef). So Wim's *settled* love-gate backstory and Yeku's *future* love-gate arc are both now mod-supported, not RP-only.

**Recommended next steps:** (1) you sanity-check the five personalities/roles below and flag any you want swapped or re-flavored; (2) on your word, I draft the concrete **Backstory Constructor entries** (title + lore prose + `skillGains` + `workDisables`) for each founder, ready to type into the mod; (3) when the Fetcher lands, I reconcile the love-gate/egg-laying/mood pieces and finalize Yeku's + Wim's arc mechanics.
