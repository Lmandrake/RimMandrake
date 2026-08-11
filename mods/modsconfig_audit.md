# RimSort config audit — 2026-08-09

Source of truth: `Config/ModsConfig.xml` (RimWorld **1.6.4871 rev590**) vs. `required_mods.md`.
**163 mods active · 1,117 installed · 114 of the required set are ON.**

---

## 1. ⛔ Conflicts that are ACTIVE right now — fix these first

| # | Problem | Why it matters |
|---|---|---|
| 1 | **Ancient Ruins All Deconstructible** (`meteores...aurad`) is ON **together with Ancient Urban Ruins Hit Point** | `required_mods.md` Tier 0: *"**NEVER** AUR Hit Point + All Deconstructible."* AUR-Hit-Point is the **Type-1 enforcer** — it gives ruin walls real HP so you must physically enter. All-Deconstructible cancels exactly that, letting you strip ruins from outside. Turn **All Deconstructible OFF**. |
| 2 | **Big and Small – Framework** (`redmattis.betterprerequisites`) is ON **together with Large Pawns** | Two size authorities double-scale pawns. Decision of 2026-08-08 was **Large Pawns, skip Big-and-Small**. Note the framework is also a dependency for other B&S modules — check nothing else needs it before disabling. |
| 3 | **Star Wars Xenotypes** is ON **together with Outer Rim – Galactic Diversity** | Duplicate-xenotype risk. `required_mods.md` recommendation **(a) = run OR-GD alone**; option (b) requires adding *[BTD] Xenotype REMIX: Star Wars* (3458153185) to dedup. Currently you have (b)-without-the-dedup. |

---

## 2. ✅ Already correct — don't "fix" these

- **Exactly one fog-of-war source.** CAI 5000 (continued) is ON; **(NWN) Real Fog of War is OFF**. That is the intended state — leave it off.
- **Water stack is right.** DBH **Lite** + DBH **Thirst** are both ON; full Dubs Bad Hygiene is not active. Matches the Lite+Thirst-only ruling exactly.
- **Forbidden mods all correctly OFF:** Mini Gravships, Dungeon Core, Real Ruins, Vanilla Psycasts Expanded (+ Hemosage/Puppeteer/autocast). Combat Extended, Rim War, Held Human, Industrial Rollers, and pocket-dimension storage aren't installed at all.
- **Perspective: Buildings** — you run the *Continued* fork (3346955193), which covers it.

---

## 3. Required but currently OFF (59)

### Frameworks / storage
- [ ] Adaptive Storage Framework
- [ ] LWM's Deep Storage

### World / biome / landing
- [ ] Alpha Biomes
- [ ] Biome Transitions
- [ ] Vanilla Landmarks Expanded
- [ ] Map Designer
- [ ] Prepare Landing (Continued)

### Creatures
- [ ] Alpha Animals
- [ ] Megafauna
- [ ] Dark Ages: Beasts and Monsters
- [ ] Vanilla Genetics Expanded

### Ship
- [ ] Bigger Gravships

### Quests / structures
- [ ] Vanilla Quests Expanded – The Generator
- [ ] Vanilla Quests Expanded – Ancients
- [ ] Vanilla Quests Expanded – Cryptoforge
- [ ] Go Explore!
- [ ] RimQuest (Continued)
- [ ] Call For Intel

### Factions / curation
- [ ] Faction Raid Cooldown (Continued)
- [ ] Ideology Scavenger Role
- [ ] **Cherry Picker** ⭐ load-bearing — the whole curation layer depends on it
- [ ] **Sensible Factions** ⭐ the faction allow-list; also the gating dependency for the parked per-faction pass

### Trade
- [ ] Tech Level Enforcement
- [ ] Trader Ships
- [ ] Trading Options Continue
- [ ] Recycle This (Continued)

### Social / romance / voice
- [ ] **Way Better Romance** ⭐ see §5 — the romance backbone is off while its add-ons are on
- [ ] Romance On The Rim
- [ ] Vanilla Social Interactions Expanded
- [ ] VSIE – Rational Trait Development
- [ ] [RH2] CPERS: Arrest Here!
- [ ] **SpeakUp** ⭐ see §5 — fork caveat

### Ideology
- [ ] Vanilla Ideology Expanded – Memes and Structures
- [ ] Vanilla Ideology Expanded – Relics and Artifacts
- [ ] Alpha Memes
- [ ] Epochs – Incense

### Apparel / decoration
- [ ] Vanilla Apparel Expanded
- [ ] Vanilla Apparel Expanded — Accessories
- [ ] [RH2] Uncle Boris' – Used Furniture
- [ ] Signs and Comments
- [ ] Knick Knacks *(already ON — no action)*

### QoL / UI
- [ ] Allow Tool
- [ ] Common Sense
- [ ] Dubs Mint Menus
- [ ] RimHUD
- [ ] Interaction Bubbles
- [ ] Numbers
- [ ] RIMMSqol
- [ ] Snap Out!
- [ ] Durable Clothes (Continued)
- [ ] Defensive Positions – Forked
- [ ] Replace Stuff – Continued
- [ ] Build From Inventory – Continued
- [ ] Better Workbench Management
- [ ] Giddy-Up 2 Forked

### Events / settlements
- [ ] Better Ambushes Continued
- [ ] Vanilla Outposts Expanded

### Authoring tools (needed for setup, optional during play)
- [ ] Character Editor
- [ ] Scenario Amender

---

## 4. Required but NOT DOWNLOADED

**Genuinely missing — needs subscribing:**
- **Vanilla Helixien Gas Expanded** (`2877699803`) — ADOPTED 2026-08-10 as a §3B terrain treasure. Absent from the Workshop tree entirely, not merely disabled. **Adoption is conditional on stripping the infinite starting gas pocket** — see `required_mods.md`.
- **Outer Rim – Droid Depot** ⚠️ a core theme mod (the droid layer + the DroidBrain anti-exponential gate). I could not resolve its Workshop ID in the subscribe pass — it may only ship inside another Outer Rim module.
- **ReGrowth: Desert Expansion** — only a Japanese translation surfaces in Workshop search; the original may be delisted.
- **RimDialogue** — doc ID 3365889763 is gone from the Workshop.
- **Simple Slavery Collars** — GitHub-only (TRIBeagle), never on the Workshop.

**Subscribed today, Steam just hasn't synced yet** (restart Steam or verify files):
- Dungeon Pack · [AP] Slaveholding · R_IOTR · More Slavery Stuff *(see §5)*

---

## 5. Three judgement calls worth making before you launch

**The romance stack is half-assembled.** *Intimacy – Friends n' Lovers* and *Intimacy – Gender Works* are ON, but **Way Better Romance** — which `required_mods.md` calls the *backbone*, and the only mod delivering unlimited partners while **retaining jealousy** — is OFF, and **R_IOTR** (the bridge between them) hasn't downloaded. Right now you have the add-ons without the thing they attach to. Either enable WBR + R_IOTR, or turn the Intimacy pair off until they're ready.

**There is currently no voice layer at all.** SpeakUp is installed but OFF, and RimDialogue isn't installed. Also, the installed SpeakUp is `jpt.speakup` — the **stale jptrrs master (1.2/1.3)**. The docs require the **`sergiodinapoli` fork** for 1.6. Worth resolving before you rely on JawaVoice, since JawaVoice is authored as a SpeakUp reskin.

**More Slavery Stuff:** the doc's *(Continued)* fork (3530586159) is delisted. Base 2896845138 exists and is the only option — but confirm its `supportedVersions` includes 1.6 from the extracted folder before enabling, per the standing rule.

---

## 6. Method note

Two bugs I hit and corrected, recorded so the audit can be re-run reliably:
1. Reading `<packageId>` with a naive first-match regex picks up **dependency blocks** inside `About.xml`, producing a garbage map (Harmony → Camera+). Parse XML and take only the direct child of `<ModMetaData>`.
2. `ModsConfig.xml` contains **`<knownExpansions>`** as well as `<activeMods>`; grepping all `<li>` overcounts by 5 and duplicates the DLC.
