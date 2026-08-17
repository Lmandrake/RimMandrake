# RimWorld 1.6 Desert-World Faction Roster — v2

> ## Rulings that override the body text
> Where these conflict with the body below, these win:
>
> 1. **Jedi placement — BOTH are true (OVERRIDES this doc's factionless-only line).**
>    The body's "Jedi are factionless, Empire-hunted wanderers" is the *primary* Jedi
>    presence (psylink 3–6, ≤1 per group, no faction membership). In **addition**, a
>    **rare Jedi may shelter within a sympathetic Homestead / Moisture-Farmer group**.
>    Both channels coexist; VPE remains the sole Force substrate and the NPC-only gate
>    still holds (no player Force ceiling). The body's "Global system 5 — Jedi and Sith"
>    section reflects this.
>
> 2. **Miraluka — FOUR-ROLE placement.** Miraluka appear in four roles:
>    (a) **Imperial prisoners / rescue-quest targets**, (b) **rare Homestead "seers" (~1%)**,
>    (c) **Ascendant Helix research subjects (~2%)**, and (d) a **Jedi-eligible race** for
>    the factionless wanderers. Rationale: Force sensitivity leaks quietly into the fringe
>    factions, but *trained* Jedi remain factionless. `OuterRim_Miraluka` is confirmed on disk.
>
> 3. **Race inventory.** This doc's "Global system 3 — Available races" matches the verified
>    on-disk inventory (42 Outer Rim – Galactic Diversity species + 6 reflavored vanilla-Biotech
>    bases incl. baseliner Humanity + Custom Hutt + Custom droid chassis). No Skakoan, Houk,
>    Kel Dor, Nautolan, Klatooinian, or Vodran (none ship on disk); Arkanian-Offshoot is **Brute
>    stock (Neanderthal)** reflavored faction-side, not a new xenotype; Ghorfa is a Tusken lore
>    line only. Low-water species use a **reduced-thirst-rate gene/trait tier** (a consumption
>    modifier, NOT immunity). `cherry_picker_killlist.md` §2 is the single source of truth for
>    the race roster and agrees with this doc.

## Purpose

Twelve NPC factions for a hot, arid, water-scarce RimWorld with an active **Thirst
system**. The **Jawa gravship expedition is the player faction** and is not counted
among the twelve.

**Fourteen factions stand on the map; twelve carry dossiers.** The other two —
**the Forgotten Arsenal** (vanilla `Mechanoid`) and **the Unbound Hive** (vanilla
`Insect`) — have no leader, no settlements and no diplomacy, and inherit vanilla's
`pawnGroupMakers` wholesale. They cost **two label patches, not two dossiers**
(`faction_world_spec.md` §2). Authoring load is twelve, and the two counts agree.

> Factions **11 (Jawa Trade Moot)** and **12 (the Junkers)** were added
> 2026-08-11 and sit at the end of the body, with their diplomacy in a
> "Relations additions" block rather than folded into Global system 1 yet.
> They are a matched pair: the same trade -- scavenging -- under law and without it.

Everything here is expressible through RimWorld 1.6 definitions, DLC systems, faction/world editing, or ordinary mod definitions:

- `FactionDef` technology level, permanence of hostility, traders, pawn groups, settlement generation

  ⚠️ **`FactionDef` does NOT express goodwill.** Verified across **all 88 live
  `FactionDef`s and all 125 distinct fields — zero hits** for goodwill in any
  form. What the engine gives is *booleans about hostility*, not a signed
  integer: `permanentEnemy`, `naturalEnemy`, `mustStartOneEnemy`,
  `permanentEnemyToEveryoneExcept`, `permanentEnemyToEveryoneExceptPlayer`,
  `hostileToFactionlessHumanlikes`, `raidsForbidden`.

  🔴 **Every "starting goodwill" number in this document is CUT FROM V1.** There is
  no field to write them into, so they are unbuildable. **v1 expresses hostility
  through those seven booleans and nothing else**, and each dossier's number is
  struck in place below so nobody authors from it.

  **Graded goodwill is `[v2]` and gated.** The only candidate mechanism is
  **Faction Customizer** (`azravos.factioncustomizer`, load order **145**), read
  from its assembly rather than its config, because a `Mod_*.xml` records only what
  has been *changed*, never what a mod *supports*:

  ```
  FactionCustomizer.dll   baseGoodwill · naturalGoodwillOffset
                          get_BaseGoodWill · set_BaseGoodWill
                          Dialog_ModifyFactionRelation
                          ModSettings · ExposeData
  ```

  Ruled out, all measured: **Faction Control** (schema is `masterDensity` +
  `factionDensities`, density only; its one goodwill symbol is a compat probe
  for *Random Goodwill*, which is not installed) and **Sensible Factions**
  (biome only).

  ⏳ **Whether Faction Customizer PERSISTS across worlds is unproven — CHECK C24.**
  Its editor is a `Dialog_` acting on live world state, but the assembly carries
  `ModSettings` + `ExposeData`, so it may survive across worlds. Until C24 answers,
  graded goodwill is not authorable at all. ⇒ **Do not put a goodwill number in any
  dossier.**
- weighted xenotype/race distributions
- custom `PawnKindDef` roles with forced race/xenotype assignment
- Ideology memes, precepts, roles, apparel requirements, styles, rituals
- weapon, apparel, utility-item, drug, implant, and mechanoid loadout tags
- settlement count and placement via world/faction editing
- custom droid, Hutt, and species races under the roster's tweak license
- Royalty psycasts and psylinks for rare Jedi and Sith pawn kinds
- Biotech mechanoids or custom droid pawn kinds for military and independent droids

Removed **Force Gremlin** and disabled WIP species remain excluded.

---

## Design pillars

1. **Factions are defined against each other, not just against the player.** A hardcoded relations matrix drives diplomacy; "enemy of my enemy" is playable.
2. **Water is the strategic axis.** Every faction has a water doctrine that determines where it settles, how far its warriors can operate, and whether it can besiege.
3. **Only warriors are visible.** All water, caste, and equipment rules are written against the combat pawn kinds RimWorld actually spawns.
4. **Hierarchy lives in pawn kinds, not xenotype percentages.** Diverse factions mostly carry no preferred-xenotype precept; rank is encoded through pawn-kind eligibility, gear, skills, and raid-point cost.
5. **One permanent enemy among the AUTHORED factions.** The Galactic Empire. Everything else we author can eventually be negotiated with, so the mid-game always has a wedge. **Blackstar Company is a deliberate exception, not a second decision:** it reskins vanilla `Pirate`, which ships `permanentEnemy: true`, and patching that false would gut the vanilla raid economy for no gain — so it keeps the flag. **The Junkers, being authored, lose theirs:** hostile on sight and bribable, not permanent.

---

## Global system 1 — Faction relations matrix

Set through NPC-vs-NPC goodwill in the faction/world editor. These are lore-derived and should be enforced after generation.

| Pair | Stance | Basis |
|---|---|---|
| Imperial ↔ Wildsteam Clan | Hostile (hardcoded) | Empire repealed anti-slavery law, reclassified Wookiees as non-sentient, used them as forced labour |
| Imperial ↔ Deepwater Compact | Hostile | Mon Calamari also targeted for Imperial enslavement |
| Imperial ↔ Geonosian Hive | Hostile | Geonosians enslaved by the Empire to build the Death Star |
| Imperial ↔ Free Droid Enclaves | Hostile | Enclave founders were abandoned by the Empire post-Clone Wars |
| Hutt Cartel ↔ Wildsteam Clan | Hostile | Trandoshan Scorekeeper doctrine: Wookiee kills are the highest-value target |
| Blackstar Company ↔ Wildsteam Clan | Hostile | Same |
| Tusken Clans ↔ Homestead Defense League | Hostile (hardcoded) | Tuskens hold water as sacred and moisture farming as sacrilege |
| Tusken Clans ↔ Hutt Cartel | Hostile | Pyke spice convoys cross Tusken territory |
| Geonosian Hive ↔ Free Droid Enclaves | 🔴 **FORMALLY ALLIED, with trade** — superseded 2026-08-17, owner (was "Cold / no trade") | Both fled the same collapsed company site and both ended up on the substellar plateau; the hive has no interest in enslaving droids, so they trade and otherwise ignore each other. See FACTION_SPEC.md |
| Hutt Cartel ↔ Free Droid Enclaves | Transactional | The Droid Gotra historically served as Hutt muscle |
| Wildsteam Clan ↔ Free Droid Enclaves | Positive | Shared absolute anti-slavery precept |
| Ascendant Helix ↔ Deepwater Compact | Positive (trade dependency) | Helix buys bulk water for growth vats and biosculpters |
| Deepwater Compact ↔ all others | Neutral-positive by doctrine | Enforced neutrality backed by a water monopoly |

---

## Global system 2 — Water and thirst doctrine

Four states. Each governs settlement siting **and** the operational range of that faction's warriors.

| State | Settlement siting | Warriors in the field |
|---|---|---|
| **Require** | Must spawn on or adjacent to a water tile | Dehydrate off-tile; short raid range; cannot besiege |
| **Manufacture** | Dry tiles; makes its own water | Normal range, but a destructible dependency |
| **Allow** | Indifferent; sites on strategic value | Carries water; range capped by logistics tail |
| **Forbid / Deny** | Will not site on open water — taboo or hostility | Longest dry-tile reach; the deep-desert threat |

### Assignments

| Faction | State | Consequence |
|---|---|---|
| Deepwater Compact | **Require** (absolute) | Holds every water tile; cannot meaningfully raid |
| Wildsteam Clan | **Require** (severe) | Devastating on home defence, near-useless expeditionary |
| Hutt Cartel | **Require** (oasis-anchored) | Every compound sits on a fiercely held oasis tile |
| Homestead Defense League | **Manufacture** | Vaporators: stores water, has no source |
| Ascendant Helix | **Allow** (high consumption) | Buys bulk water from the Deepwater Compact |
| the Galactic Empire | **Allow** (supplied) | Can settle anywhere; convoys are an attack surface |
| Blackstar Company | **Allow** (water clock) | Hunt teams carry a finite supply — range is the fight |
| Geonosian Foundry Hive | **Forbid** (arid-adapted) | Only faction that can sustain a deep-desert siege |
| Deep Desert Tribes | **Forbid** (taboo) | High raid frequency, very short duration, no siege |
| Free Droid Enclaves | **Deny** | Settle on water, crack it for fuel; runoff is lethal |

### Resulting world shape

Water tiles belong to the friendly-to-neutral band (Deepwater Compact, Wildsteam uplands, Hutt oases). Dry tiles belong to the hostile band (Tusken, Geonosian, supplied Imperial, denial-holding droids). The player's expansion is a fork: **settle wet and be crowded by factions you can negotiate with, or settle dry and be open but permanently hunted.**

### Low-water species tier

Beyond the faction-level states, individual desert-evolved species carry a **reduced thirst rate** — implemented as a gene or trait modifying water consumption, not as immunity. These pawns are the long-range dry-tile operators in any group they join, and their presence in a raid tells the player how long that raid can stay in the field.

| Species | Thirst rate | Basis |
|---|---|---|
| **Jawa** | **Low** | 🔴 **Added 2026-08-13, VISION (W2).** Desert-native, and the owner's water ruling names Jawa first. **The table omitted the setting's most desert-adapted species entirely**, while the player section asserted "dry-adapted" with nothing behind it. This is the line that makes that true — and it corrects the Jawa Trade Moot's "normal raid range" by the same stroke |
| **Tusken** | Very low | Full moisture-retention wrappings and filtered masks; desert-native |
| **Desert alien (Impid)** | Very low | Heat-adapted xenotype; fire-affiliated |
| **Geonosian** | Very low | Arid-rock native; subterranean hive metabolism |
| **Nikto** | Low | Kintan is harsh and irradiated post-supernova |
| **Kaleesh** | Low | Arid Kalee; warrior culture built on long overland hunts |
| **Iktotchi** | Low | Iktotch is a barren, storm-scoured moon |
| **All droid chassis** | **None** | No thirst need whatsoever |

Conversely, **Wookiee, Wookiee-kin, Herglic, Mon Calamari, Quarren, Selkath, Gungan, Chagrian, Aqualish, Trandoshan, Rodian, Ithorian, and Ewok** carry an **elevated** thirst rate. They are the pawns that make a faction slow.

⭐ **`elevated` is a full band, not an aside (VISION 2026-08-13, W1).** Four bands
exist and the doctrine document now names all four — **none · very low/low ·
normal · elevated**. Two faction designs rest on this band and would be
incoherent without it: the **Wildsteam Clan** (devastating at home,
near-useless expeditionary) and the **Deepwater Compact** (wardens dehydrate before
they can reach anyone, which is why their raids are suppressed at all).
**Elevated is not a penalty, it is a leash.** Full rulings and the audit that
forced them: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\water_doctrine.md`.

---

## Global system 3 — Available races

Everything in this document draws from what is on disk. Nothing else is used.

**→ The canonical, verified race inventory is `cherry_picker_killlist.md` §2** (the "✅ VERIFIED IN-HAND RACE INVENTORY" block — the single source of truth for the race inventory). The full Outer Rim / Galactic Diversity species list (Abednedo … Zeltron, 42 species + bundled Chiss) is enumerated there and is **not repeated here** to avoid drift. This section keeps only the roster-specific interpretation: how the reflavoured vanilla xenotypes and bespoke races are cast.

### Reflavoured vanilla Biotech xenotypes, plus baseline Humanity

| Label | Base | Role in this roster |
|---|---|---|
| **Gamorrean** | Pigskin (custom-authored) | Hutt heavy guards and melee enforcers |
| **Wookiee-kin** | Yttakin | Freehold hunters, labourers, heavy warriors |
| **Savant caste** | Genie | Engineer, fabricator, and researcher caste |
| **Brute stock** | Neanderthal | Heavy labour, melee auxiliaries, engineered labour-lines |
| **Desert alien** | Impid | Fire-callers, fast desert stalkers |
| **Baseliner human** | Humanity | Imperial rank and file, homesteaders |

Optional relabels for immersion, using the same bases and requiring no new race: Savant caste → *Techno Union savant*; Brute stock → *labour-line*; Desert alien → *ember-kin*.

### Bespoke authored races

Two races are authored for this roster rather than installed from a species mod, under the roster's tweak licence:

- **Custom Hutt** — bosses and settlement leaders in the Hutt Cartel only.
- **Custom droid chassis** — the Free Droid Enclaves, plus Imperial and Geonosian military droid pawn kinds.

---

## Global system 4 — Weighted races versus forced pawn kinds

Faction-wide percentages govern ordinary generation. Race is overridden at the pawn-kind level for:

- Hutts and Hutt proxies
- Gamorrean guards
- stormtroopers, where uniformity is required
- Sith, Massassi, and dark adepts
- Jedi (factionless — see below)
- Geonosian aristocrats, queens, and drones
- all droid chassis
- faction leaders
- Helix prototypes and labour-line workers

## Global system 5 — Jedi and Sith

Royalty psycast mechanics, not a bespoke Force system, unless a Force mod is already installed.

**Jedi placement — BOTH channels are true** (reconciliation ruling, 2026-08-06, overriding the original factionless-only phrasing).

*Primary channel — factionless wanderers.* Jedi generate as hidden wanderer pawns hunted by the Galactic Empire, not as members of the Homestead Defense League or any other faction. Eligible races: Miraluka, Mirialan, Togruta, Iktotchi, Cerean, or Baseliner human. Psylink 3–6; monosword, persona monosword, or custom lightsaber; shield belt; no heavy armour; defensive, mobility, perception, and control psycasts; extreme pawn combat value; maximum one per group.

*Secondary channel — the rare sheltered Jedi.* In addition, a **rare Jedi may shelter within a sympathetic Homestead / Moisture-Farmer group** at a very low spawn weight (the "hidden protector" the player may discover as an ally rather than a hunted stranger). Same curated VPE light/control loadout, same one-per-group cap. This does not make Jedi faction *members* in the roster sense — it is an occasional embedded guardian, not a standing pawn-kind slot in the faction's ordinary generation.

Both channels draw on the same curated NPC-only VPE ability set; the player and the Jawa faction have no Force-acquisition path under either channel.

**Sith** appear only in Imperial Sith-escort pawn kinds. Psylink 4–6; persona melee weapon; shield belt or prestige armour; offensive and control psycasts; high Melee, Social, Intellectual; always accompanied by elite troops; extreme spawn cost.

**Miraluka are never ordinary Imperial personnel.** All Miraluka are Force-sensitive, so under the Galactic Empire they appear exclusively as prisoners in Imperial settlements and as rescue-quest targets.

## Global system 6 — Droid implementation split

1. **Independent droid race pawns** — Free Droid Enclaves. Protocol, maintenance, medical, utility, and self-owned combat chassis. Ordinary faction membership and ideology.
2. **Military droids and mechanoids** — the Galactic Empire (reskinned base-game mechanoids) and Geonosian Foundry Hive. Generated through combat pawn groups; no independent ideology.

Naming is kept strictly separate so the two hostile spacer factions read differently on the field:

- **Imperial:** dark trooper, purge sentry, probe droid, KX security. Never "battle droid" — the Empire was droid-averse and High Human prejudice extended to droids.
- **Geonosian:** line droid, melee droid, heavy droid, command droid — mass-produced Foundry product.

## Global system 7 — Settlement-count control

Counts are world-generation targets. Generate, inspect, then correct with a faction/world editor, preserving relative abundance.

- **numerous:** Homestead Defense League, the Galactic Empire
- **common:** Hutt Cartel, Tusken Clans
- **limited:** Deepwater Compact, Geonosian Hive
- **rare:** Wildsteam Clan, Blackstar Company
- **very rare:** Droid Enclaves, Ascendant Helix

The Enclaves and Helix have suppressed raid generation, so both route their player contact through **incident and quest generators** rather than settlement assaults.

## Global system 8 — Equipment-quality discipline

Separate equipment tags or pawn-kind restrictions per faction:

- **Tusken:** no spacer weapons or advanced armour
- **Homestead:** civilian industrial gear
- **Imperial:** standardised spacer gear
- **Hutt:** broad industrial with rare elite spacer items
- **Droids:** integrated chassis-specific weapons
- **Wookiee:** strong melee, bowcasters, limited armour
- **Deepwater Compact:** disciplined industrial rifles, EMP, Gungan shield belts
- **Geonosian:** sonic weapons plus mass-produced droids
- **Helix:** expensive security equipment, few combatants
- **Blackstar Company:** high quality, small numbers, mixed specialist weapons

---

## Global system 9 — Contact-frequency parameters (INITIAL ESTIMATES, 2026-08-07)

> **Purpose & status.** These are **first-pass estimates so play can start**, not tuned values — the intent (per the casting decision) is to differentiate the twelve by **frequency + contact-mode, not by deletion**. Every number here is an explicit knob meant to be re-examined after the first play sessions; adjust freely. Frequency is deliberately kept **separate from severity**: a faction's *danger* comes from pawn-group composition (§19.5 / `faction_authoring_mechanism.md`), NOT from these frequencies. A high raid weight can still be a weak-but-annoying harasser (Tuskens) and a low one can be lethal (Empire sieges).

**The four knobs (each defined so it maps to a real 1.6 lever):**

- **Settlements (N)** — world faction count. *[Evidence]* — carried from the strategic-balance table. Real lever: worldgen faction count / Faction Control. Drives baseline caravan + raid traffic.
- **Raid weight (Rw, 0–10)** — this faction's *relative share* of the hostile-incident draw pool (how often it is the aggressor when a threat fires). *[Inference]* from N × hostility × operational reach (water doctrine). Real lever: storyteller draws roughly proportional to nearby-settlement pressure; tune via **Faction Raid Cooldown** + incident commonality; the quiet non-raiders have raid generation suppressed.
- **Trade weight (Tw, 0–10)** — relative frequency of trade caravans/visitors arriving AND usefulness as a caravan destination. *[Inference]* from N × goodwill × whether they hold something you need (water, medicine). Real lever: visitor/trade-caravan incident weight, proportional to settlements + goodwill.
- **Quest weight (Qw, 0–10)** — relative share of this faction's contact routed through **CQF / quest / incident generators** rather than settlement assaults. *[Inference]* highest for the reclusive/allied factions that route contact through quests. Real lever: CQF quest hooks + vanilla quest generation.

⚠️ **The Goodwill column is CUT FROM V1** — there is no goodwill field on `FactionDef` (see Purpose). It is kept as `[v2]` intent only; v1 hostility is the booleans. **N / Rw / Tw / Qw are unaffected.** The table predates factions **11. Jawa Trade Moot** and **12. the Junkers**, whose contact parameters live in their own settings tables.

| Faction | ~~Goodwill~~ *(cut)* | N | Rw | Tw | Qw | Dominant contact mode |
|---|---:|---:|---:|---:|---:|---|
| **the Galactic Empire** *(spine)* | −100 perm | 10 | **9** | 0 | 4 | Siege + staged assault; **escalates across the 3 acts** |
| **Deep Desert Tribes** | −80 | 9 | **7** | 0 | 1 | Frequent raid *harassment* — short, weak, no siege |
| **Geonosian Foundry Hive** *(spine)* | −100 | 5 | **7** | 0 | 2 | Deep-desert siege (only faction that can sustain one) |
| **Hutt Cartel** *(spine)* | −35 | 8 | 6 | **9** | 7 | Trade + extortion + the endgame door-off-world questline |
| **Blackstar Company** *(spine)* | −10 | 4 | 6\* | 3 | 5 | Targeted elite hunts + bounty quests; **\*Rw scales with player Heat** |
| **Homestead Defense League** | +25 | 13 | 0 | **8** | 6 | Numerous friendly caravans + ally quests |
| **Deepwater Compact** | +10 | 5 | 0 | **7** | 4 | Water trade (survival-critical); cannot raid |
| **Ascendant Helix** | 0 | 3 | 1 | 4 | **7** | Specialist medicine/genetics quests + trade; raids suppressed |
| **Wildsteam Clan** | +35 | 4 | 0 | 3 | 5 | Small formidable ally; quest-routed |
| **Free Droid Enclaves** | 0 | 3 | 1 | 2 | **8** | Quest-routed almost entirely; raids suppressed |

**Reading the raid pool.** Non-zero Rw values sum to **≈37**, so the intended hostile-contact split is roughly: Empire **~24%**, Tusken **~19%**, Geonosian **~19%**, Hutt **~16%**, Blackstar **~16%**, Enclaves/Helix **~3% each**. Homestead Defense League / Deepwater Compact / Wildsteam Clan never raid (Rw 0) — and for the Homestead that is `raidsForbidden: true`, not a low weight. *[Assumption]* the 0–10 scale maps ~linearly onto storyteller draw; if the storyteller ignores weights and just uses proximity, fall back to tuning via settlement count + Faction Raid Cooldown.

**Two dynamic hooks (not static frequencies):** (i) the **Empire escalates** — same Rw, heavier pawn-group composition act-over-act, plus the Imperial Heat gauge; (ii) **Blackstar Company Rw is Heat-scaled** — quiet until the player gets "hot," then their hunts spike. Both are the pursuit spine's teeth and are authored as curves/hooks, not as a fixed per-year number.

**What I deliberately did NOT estimate:** absolute *events-per-year* — that is speculation without playtest data and depends on the chosen storyteller. These relative weights are the re-examinable layer; convert to absolutes only after observing one in-game year.

---

## Global system 10 — Vessel assignments

**Every faction is either a PATCH onto a live vanilla `FactionDef` or AUTHORED from
scratch.** Measured against the live def dump, 2026-08-14.

| faction | vessel | verdict |
|---|---|---|
| the Galactic Empire | **vanilla `Empire`** | ✅ `hidden false`, settles |
| Homestead Defense League | **vanilla `OutlanderCivil`** | ✅ |
| Deep Desert Tribes | **vanilla `TribeCivil`** | ✅ |
| Blackstar Company | **vanilla `Pirate`** | ✅ — ships `permanentEnemy: true` and keeps it (pillar 5) |
| the Forgotten Arsenal | **vanilla `Mechanoid`** | ✅ `hidden true`, no settlements — which is the intent |
| the Unbound Hive | **vanilla `Insect`** | ✅ |
| **Ascendant Helix** | ~~`Ancients`~~ | 🔴 **IMPOSSIBLE → AUTHORED** |

🔴 **`Ancients` is `hidden: true`, `settlementGenerationWeight: 0`,
`maxCountAtGameStart: 0`, `canMakeRandomly: false`.** It cannot settle, cannot
appear in the faction list and cannot be diplomatic. **The Ascendant Helix is
authored from scratch.** Nothing is owed here — it is measured, not estimated.

**Authored from scratch — eight:** Hutt Cartel · Free Droid Enclaves · Wildsteam
Clan · Deepwater Compact · Geonosian Foundry Hive · **Ascendant Helix** · Jawa
Trade Moot · the Junkers.

🔴 **The shipped Empire patch is on the wrong vessel.**
`src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml` targets
`OuterRim_GalacticEmpire`, a mod def. **Re-point it at vanilla `Empire`.**

---

## Strategic balance

| Faction | ~~Initial stance~~ *(goodwill — cut from v1)* | Permanent hostile? | Settlements | Tech level | Water state | Strategic weight |
|---|---:|---:|---:|---|---|---|
| Hutt Cartel | −35 | No | 8 | Industrial | Require (oasis) | Major regional power |
| the Galactic Empire | −100 | **Yes** | 10 † | Spacer | Allow (supplied) | Dominant military occupier |
| Homestead Defense League | +25 | No | 13 | Industrial | Manufacture | Numerous weak settlements |
| Deep Desert Tribes | −80 | No | 9 | Industrial, restricted | Forbid | Territorial raider culture |
| Free Droid Enclaves | 0 | No | 3 | Spacer | Deny | Rare reclusive specialists |
| Wildsteam Clan | +35 | No | 4 | Industrial | Require | Small but formidable allies |
| Deepwater Compact | +10 | No | 5 | Industrial | Require | Water monopoly, cannot raid |
| Geonosian Foundry Hive | −100 | No | 5 | Spacer | Forbid | Swarm, droids, deep-desert siege |
| Ascendant Helix | 0 | No | 3 | Spacer | Allow | Wealthy research enclaves |
| Blackstar Company | −10 | No | 4 | Industrial | Allow | Mobile elite hunters |
| **Total** | | | **64** | | | |

> **† The Imperial 10 is a fiction total across two layers, not a surface count.**
> `desert_world_design.md` §4-Orbital holds that Imperial power is **vertical**:
> nearly everything in orbit, "perhaps one or two settlements" on the ground. That
> looked like a contradiction with this table for six days. It is not one — the
> two numbers describe different layers, and neither doc said so.
>
> **The split:** **2–3 surface**, clustered near the large spaceport as the
> Empire's planetary seat (the face the orbital timer reports to);
> the remaining **~7–8 orbital**. Ten total, two or three *reachable*.
>
> ⚠️ **Consequence for worldgen, and it is the reason this matters:** the
> `Target settlements` field in §2 below drives **placement on the planetary world
> map**. Setting it to 10 would put ten Imperial bases on the ground and invert the
> doctrine — the occupier would read as horizontal, and the "the sky is the enemy,
> the ground is nearly empty of them" feel would be gone. **Set it to 3.** The
> other seven are fiction and orbital-layer content, not world tiles.
>
> **Open, and the only part still unsettled:** whether Odyssey's orbital holdings
> draw from the same faction settlement pool as surface bases. If they do, the
> field may want the full 10 with the *distribution* constrained instead. Nobody
> has checked. Until someone does, 3 is the safe value — it fails toward the
> doctrine rather than against it.
>
> ⚠️ _Reconciliation originally derived from an aristocracy proposal in
> `TODO_v2.md`, **now struck** — that document lost ~800 lines and the two-Empire
> reading it supported is superseded by the owner's one-Empire ruling. **Canon is
> `faction_world_spec.md` §5.** The two-LAYER reading (surface vs orbital) survives
> on its own merits and is what this note is about._ The two-layer reading is not in dispute; the exact
> surface figure (2–3 here vs "one or two" at `desert_world_design.md:641`) is a
> ±1 the owner has not ruled on, and nothing downstream depends on which it is._

---

# 1. Hutt Cartel

## Mechanical identity

A wealthy, decentralised criminal faction built around **oasis control**. Cheap servile infantry and paid mercenaries surround expensive Hutt bosses, Gamorrean guards, and specialist lieutenants. Hostile enough to raid, pragmatic enough to trade, accept tribute, or become an ally.

> **⭐ ORIGIN GRIEVANCE — we stole LifeDawn from THEIR shipyard (user, 2026-08-06; canon in `context.md` "SHIP ORIGIN").** The player's gravship (name = "LifeDawn," a first-wave colony ship) was being **stripped and slowly scrapped in an abandoned Hutt-owned shipyard** — the Hutts thought it was a dead hulk and **didn't even know it could still fly.** The Jawa leader restored a central Grav controller and stole it airborne. That humiliation is *why the Cartel is so angry*, and it's the deliberate irony of the primary escape route: the faction we robbed is the faction whose orbital station we must bribe our way past.
>
> **⭐ ENDGAME PURPOSE — the Hutts are the primary way off-world (user, 2026-08-06).** The Hutt "pirate"-type base is the *only* non-Imperial orbital node (Empire owns orbit; see `desert_world_design.md` §4-Orbital), so winning the Cartel over from neutral-treacherous to genuine ally is the **primary path through the orbital blockade** in the greater arc (`context.md` win-condition section). This is deliberately a *long* grind, not a purchase: two thresholds — (a) claw goodwill up from the roster's default hostile/−standing to alliance, and (b) complete a specific high-stakes favor of the required magnitude — delivered as a CQF quest-line riding on the accepted tribute/goodwill mods (Tribute Demand, Raid Protection Fee, More Slavery Stuff). The relationship stays *bought and conditional*, never warm — a Hutt alliance is a business arrangement that can sour. This gives the Cartel dossier its narrative teeth: they are simultaneously the extortionate oasis-tollers you fight all game *and* the one door out. **Variant route — debt bondage:** instead of favor-questing, the player may **take on a massive debt equal to the assessed value of the stolen LifeDawn and pay it off over time** (Debt Collector / Tribute Demand hooks reskinned to a Hutt ledger), earning escape as *settled accounts* rather than alliance — servitude-with-an-exit, thematically very Jawa.
>
> **⭐ ORBITAL MECHANICS — MiningCo. Spaceship reflavored into the Cartel (user, 2026-08-08; mod detail in `design/Jawa/mods/required_mods.md` MiningCo section).** The Cartel's "only non-Imperial orbital node" was until now pure narrative. **MiningCo. Spaceship (Continued)** (`Mlie.MiningCoSpaceship`, 1.6, no deps) supplies the working mechanics, reskinned Hutt: (a) **cargo spaceships that physically land on-map to trade** bulk goods (passive + a richer "requested" variant) — a literal Hutt trade shuttle on the pad; (b) **airstrikes-for-hire** — pay silver and the Cartel bombs your attackers ("MiningCo. cannot be held responsible for collateral damage" → very Hutt mercenary muscle); (c) **orbital medical healing** — send an injured pawn up to the Hutt station, pay silver near a trade beacon, they return by drop-pod healed. Requires the player to build an orbital relay + landing pad = the extortion toll relationship this dossier already describes. **Every service is a silver SINK (pillar-safe — drains, never compounds).** Install TODO: reflavor patch (name/icon/leader titles/apparel → Hutt) + ensure the mod's events point at THIS hand-authored Hutt FactionDef rather than spawning a second faction. Combat Extended airstrike incompat is moot (not running CE).

## Water doctrine — **Require (oasis-anchored)**

Every Cartel settlement sits on or immediately beside an oasis tile, and that tile is faction territory rather than a shared resource. The water *is* the asset; the compound exists to control it.

- The oasis is the settlement's second boss objective alongside the Hutt.
- Drawing water at a Cartel oasis without paying triggers a demand, a toll, or a raid.
- The Cartel sells water at extortion rates, in direct competition with the Deepwater Compact's cheap neutral supply.
- Raid strength scales down with distance from the nearest Cartel holding. Deep desert is Tusken and Geonosian country, not Hutt country.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~−35~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | No |
| Target settlements | 8 |
| Settlement distribution | Oasis tiles, trade routes, roads, warm lowlands |
| Raid frequency | Medium, distance-scaled |
| Caravan frequency | High |
| Trader types | Bulk goods, exotic goods, weapons, **water**, slaves/prisoners if enabled |
| Base wealth | High |
| Typical settlement defenders | 14–28 |
| Settlement leadership | Exactly one Hutt boss or Hutt proxy |
| Combat-droid share | 0–10% of combat points; uncommon status symbols |

## Racial mixture

Two tiers. The Nikto were bound into permanent servitude to the Hutts by the Treaty of Vontor and have served as their foot soldiers and bodyguards ever since; everyone else in the Cartel is paid.

| Race/xenotype | Weight | Tier | Typical use |
|---|---:|---|---|
| **Custom Hutt** | 3% | Master | Bosses, settlement leaders, caravan principals |
| **Nikto** | 22% | Vontor servile | Line infantry, bodyguards, labour overseers |
| **Gamorrean** | 18% | Paid | Heavy guards, melee enforcers, wardens |
| **Rodian** | 11% | Paid | Shooters, hunters, scouts |
| **Trandoshan** | 10% | Paid | Heavy hunters, melee specialists |
| **Aqualish** | 9% | Paid | Shotgunners, bruisers, miners |
| **Twi'lek** | 8% | Paid | Traders, social specialists, medics |
| **Pyke** | 7% | Paid | Spice handlers, negotiators, officers |
| **Devaronian** | 5% | Paid | Raiders, incendiary specialists |
| **Herglic** | 4% | Paid | Heavy labour and bodyguards |
| **Zeltron** | 2% | Paid | Traders, recruiters, social roles |
| **Baseliner human** | 1% | Hired | Technical and administrative staff |
| **Total** | **100%** | | |

### Nikto subspecies as pawn tiers

Kintan's Nikto split into distinct subspecies after a nearby supernova. Use them as internal tiers so the servile caste has visible structure rather than being one undifferentiated block:

- **Red (Kajain'sa'Nikto)** — desert-native line infantry; low thirst rate; the Cartel's deep-country escorts.
- **Green (Kadas'sa'Nikto)** — forest stock; scouts and trackers.
- **Mountain (Esral'sa'Nikto)** — heavy infantry and siege labour.
- **Pale (Gluss'sa'Nikto)** — technical and overseer roles.

### Forced pawn-kind assignments

- **Hutt Kajidic Boss:** Custom Hutt only; high Social; poor movement; excellent apparel; shield belt or implanted defence; 2–4 dedicated guards in the same group.
- **Gamorrean Guard:** Gamorrean only; melee bias; high armour; near-zero ranged generation.
- **Vontor Levy:** Nikto only; cheap, low point cost, poor gear, high loyalty, fearless.
- **Red Nikto Outrider:** Kajain'sa'Nikto only; low thirst; long-range desert escort and raid screen.
- **Paid Enforcer:** Rodian, Aqualish, Devaronian, or Trandoshan; noticeably better equipment and higher point cost than the Vontor levy.
- **Cartel Lieutenant:** Pyke, Twi'lek, or Nikto; high Social and Intellectual.
- **Cartel Hunter:** Rodian, Trandoshan, or Devaronian; high Shooting and Animals.
- **Cartel Heavy:** Herglic, Aqualish, or Gamorrean; high raid-point cost.
- **Indentured Labourer:** any non-Hutt species; weak equipment, low combat weight.

## Belief system: **The Ledger of Power**

- **Structure:** **Theist** — the Kajidic Hutt is a living god
- **Memes:** Raider, Supremacist, Collectivist, High life
- **Styles:** Spikecore, Techist, Morbid
- **Preferred xenotypes:** None
- **Primary role:** Lord — **Lord Gorga the Immense**
- **Specialists:** Shooting specialist, melee specialist

| Issue | Setting |
|---|---|
| Raiding | Required |
| Slavery | Honorable |
| Execution | Don't care |
| Drug use | Essential |
| Organ use | Acceptable |
| Body modification | Approved |
| Charity | None |
| Diversity of thought | Neutral |
| Mechanoid labor | Unrestricted |
| Child labor | Acceptable |
| Corpses | Don't care |
| Skullspikes | Acceptable or desired |
| Physical love | Free |
| Apostasy | Horrible |

The theist structure is load-bearing. The Hutts did not merely conquer the Nikto — they bombarded the Cult of M'dweshuu's stronghold from orbit, destroying the fanatical religious order that had ruled Kintan for centuries, and the grateful Nikto signed themselves into indefinite servitude. The Kajidic replaced a god rather than defeating an army. That is what makes Apostasy: Horrible and the Vontor levies' fearless loyalty coherent rather than arbitrary, and it gives the Cartel's ideoligion a genuine conversion story to proselytise.

## Technology and economy

- electricity, batteries, solar, wind, generators
- machining, gunsmithing, drug production, hospital beds
- comms consoles and orbital trade
- fabrication in the richest compounds; limited bionics
- rare spacer equipment obtained by trade, not production
- psychoid, smokeleaf, beer, chemfuel, textiles, weapons, prisoners, **bottled water**
- large silver and trade-good stockpiles; excellent food for leaders, nutrient paste for labourers
- drug labs, prisons, barracks, throne room, warehouse, defended landing area, **walled cistern**

## Typical equipment

**Vontor levy** — autopistol, machine pistol, revolver, bolt-action rifle, pump shotgun; duster, flak vest, simple helmet; awful to normal quality.

**Paid enforcer** — heavy SMG, chain shotgun, assault rifle, frag grenades; flak pants, flak jacket, simple helmet; normal to good.

**Gamorrean guard** — mace, warhammer, longsword, breach axe; plate or marine-style heavy armour on elites; shield belt.

**Cartel lieutenant** — assault rifle, sniper rifle, charge rifle, monosword; recon armour or high-quality flak; jump pack, low-shield pack, smokepop; good to excellent.

**Hutt boss** — usually unarmed or autopistol/charge pistol; prestige clothing, shield belt, implanted defences.

## Pawn-group patterns

- **Collection crew:** lieutenant, 4–8 Nikto levies, 2 Gamorreans
- **Punitive raid:** 12–25 mixed levies, enforcers, heavies, occasional combat droid
- **Deep-country escort:** all-Nikto red-subspecies group; the only Cartel formation that operates far from an oasis
- **Slave caravan:** Hutt or Pyke principal, traders, prisoners, 8–15 guards
- **Water toll party:** small fast group dispatched at trespass on a Cartel oasis
- **Elite retaliation:** Hutt proxy, recon-armoured lieutenants, Trandoshan hunters, shielded Gamorreans

## Lore basis

- The Treaty of Vontor placed the Nikto in permanent servitude to the Hutts; they were used as foot soldiers and bodyguards, and millions were transplanted off Kintan across Hutt Space — https://starwars.fandom.com/wiki/Nikto/Legends
- The Hutts destroyed the Cult of M'dweshuu from orbit, and the grateful Nikto signed themselves into indefinite servitude — https://en.wikipedia.org/wiki/Klatooinian
- Kintan's Nikto divided into five subspecies after a nearby supernova — https://mortallyclearwonderland.tumblr.com/post/662051711091933184/star-wars-alien-species-nikto
- Hutt slavery on Outer Rim worlds continued beyond Republic reach — https://starwars.fandom.com/wiki/Slavery

---

# 2. the Galactic Empire

## Mechanical identity

The strongest conventional military faction and the only permanent enemy: standardised human infantry, strict command tiers, drop-pod assaults, Imperial security droids, rare Sith, and heavily fortified installations. Expensive pawn kinds keep raids from becoming unmanageable spacer masses.

## Water doctrine — **Allow (supplied)**

The Galactic Empire does not site on hydrology. It settles on roads, strategic passes, and ancient installations; atmospheric condensers and shipped supply do the rest. This is the correct feel for an occupier — **they can be anywhere.**

- Garrisons in dry tiles are supply-dependent. **Water convoys are an attack surface** and the primary way to hurt a permanent enemy without a frontal assault.
- Massassi shock troops are Yavin-jungle stock. A Sith hunt group containing them signals a wet-tile origin base — a free intelligence tell.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Vessel | 🔴 **vanilla `Empire`** — measured: `hidden false`, settles. **NOT `OuterRim_GalacticEmpire`.** The shipped patch `src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml` targets that mod def and must be re-pointed |
| ~~Starting goodwill~~ | ~~−100~~ **CUT FROM V1** — `FactionDef` has no goodwill field. Hostility is `permanentEnemy: true`. |
| Permanent enemy | **Yes** |
| Target settlements | **3** (surface). The **10** in the strategic-balance table is the fiction total across both layers — see the † note there. ~7–8 Imperial holdings are **orbital** and are not world tiles. |
| Settlement distribution | The 2–3 surface seats cluster near the **large spaceport** (the Empire's planetary seat). Otherwise: roads, strategic passes, ancient installations, central lowlands. ⚠️ The clustering **mechanism is unestablished** — degrade gracefully to "2–3 surface settlements somewhere" if it cannot be forced. |
| Raid frequency | High |
| Caravan frequency | Military and **water-supply convoys** only |
| Base wealth | Very high |
| Typical settlement defenders | 24–48 |
| Drop-pod use | Common |
| Siege use | Common |
| Combat-droid share | 20–35% of combat points |
| Force-user frequency | Sith in ~1 of 8 elite groups; dark adept in ~1 of 15 ordinary raids |
| Prisoner population | Always present — see below |

## Racial mixture

Human primacy is enforced demographically, not just ideologically. Non-humans are limited to near-human auxiliaries "sufficiently humanoid" to pass under High Human Culture.

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Baseliner human** | 78% | Stormtroopers, pilots, officers, administrators |
| **Chiss** | 7% | Officers, marksmen, intelligence staff |
| **Umbaran** | 6% | Intelligence, night operations, interrogation |
| **Arkanian** | 4% | Medical and technical officers |
| **Zabrak/Iridonian** | 3% | Assault troops, hardened NCOs |
| **Savant caste** | 2% | Fabrication and ordnance specialists |
| **Total** | **100%** | |

**Not in the generation table.** Massassi, Dathomirian, and Sith appear only inside Sith-escort pawn kinds. Rakata appear only as relic-recovery specialists in quest groups.

### Prisoner pool

Imperial settlements always generate a slave/prisoner population, drawn from **Wookiee, Mon Calamari, Geonosian, and Miraluka**. Raiding an Imperial base therefore yields recruitable pawns, giving a permanent enemy an upside beyond loot.

### Forced pawn-kind assignments

- **Stormtrooper:** Baseliner, or rare Chiss/Zabrak.
- **Stormtrooper Sergeant:** Baseliner, Chiss, or Umbaran.
- **Black-uniform Commander:** Baseliner, Chiss, Umbaran, or Arkanian; high Social and Shooting.
- **Imperial Technician:** Savant caste or Arkanian; high Intellectual and Crafting.
- **Massassi Shock Trooper:** Massassi only; strong melee bias; escort-only.
- **Dark Adept:** Dathomirian or Sith; psylink 2–4.
- **Sith Commander:** Sith only; psylink 4–6; persona melee weapon.
- **Imperial Security Droid:** reskinned mechanoid — dark trooper, purge sentry, probe, KX security.

## Belief system: **The Doctrine of Ordered Dominion**

- **Structure:** Ideological
- **Memes:** Supremacist, Collectivist, **Human primacy**, Proselytizer
- **Styles:** Techist, Morbid
- **Preferred xenotypes:** None at the precept level; uniformity comes from the 78% baseliner weight and apparel tags
- **Primary role:** Emperor — **Emperor Palpatine** _(canon, VISION 2026-08-13 — matches the
  deployed patch and echoes "Galactic Empire"; "Sector governor" is retired)_
- **Specialists:** Shooting specialist, production specialist

| Issue | Setting |
|---|---|
| Slavery | Acceptable |
| Execution | Required |
| Proselytizing | Frequent |
| Body modification | Approved |
| Autonomous weapons | Unrestricted |
| Mechanoid labor | Unrestricted |
| Charity | None |
| Diversity of thought | Intense bigotry |
| Apostasy | Abhorrent |
| Organ use | Acceptable |
| Drug use | Medical only |
| Raiding | Respected |
| Corpses | Don't care |
| Child labor | Encouraged |
| Growth vats | No restriction |

The Doctrine teaches that the galaxy trends toward entropy and that only one ordered hierarchy — human, centralised, obedient — holds the chaos back. Every alien species, every deviation, every act of independent thought is disorder to be corrected. This is why the meme set reads Supremacist + Human primacy + Collectivist + Proselytizer as a single coherent engine rather than four bolted-on flags: supremacy supplies the target (the non-human, the deviant), collectivism supplies the instrument (the individual is nothing, the Galactic Empire is everything), and proselytising is not persuasion but the conquest of the mind — an extension of the same campaign the stormtroopers wage with rifles. Execution: Required is doctrinally load-bearing, not cruelty for its own sake: a heretic left alive is unpruned disorder, so correction is a civic duty.

### Rituals and observances

- **Rite of Compliance (conversion ritual).** The Proselytizer meme + Proselytizing: Frequent already drive vanilla conversion rituals; reflavour the vanilla conversion ceremony as a compliance rite led by the Emperor's local officers. *Mechanical encoding: vanilla Ideology conversion ritual — buildable as-is.*
- **The Correction (public execution).** Execution: Required is expressed as a public spectacle rather than a quiet killing. *Mechanical encoding: vanilla execution precept + the vanilla execution ritual; buildable as-is.*
- **The Emperor's Address (speech).** The Emperor uses the vanilla Leader role's speech abilities to reinforce loyalty and diversity-of-thought bigotry. *Mechanical encoding: vanilla Leader role speech — buildable as-is.*
- **Style:** Techist + Morbid styles carry the reading into architecture and apparel (sharp, uniform, trophy-adjacent). *Mechanical encoding: vanilla Ideology styles — buildable as-is.*

Every observance above is pure vanilla Ideology; the Empire needs no mod beyond the DLC to run this belief system exactly as written.

## Technology and economy

- complete spacer military technology; charge weapons; recon/marine/cataphract armour
- drop pods, mortars, shield packs, jump packs
- fabrication, advanced components, bionics
- mechanitor and mechanoid infrastructure
- biosculpting, growth vats, gene banks, cryptosleep
- **atmospheric water condensers and reservoir bunkers** in every installation
- military production and taxation rather than open trade
- armouries, barracks, prisons, comms rooms, fabrication bays, droid charging halls
- perimeter turrets, mortars, autocannons, kill corridors, drop-pod batteries

## Typical equipment

**Stormtrooper** — assault or charge rifle; recon armour or standardised flak set; recon/marine helmet; normal quality.

**Scout trooper** — bolt-action, sniper, or assault rifle; light recon armour; jump pack; movement enhancement.

**Heavy trooper** — LMG, minigun, charge lance, frag grenades; marine armour; low-shield pack.

**Breacher** — chain shotgun, breach axe, frag grenades; marine armour; shield belt on melee variants.

**Black-uniform commander** — charge rifle or lance, or excellent autopistol; prestige recon armour; jump pack or low-shield pack; bionic eye, arm, spine, coagulator.

**Imperial savant** — charge rifle or none; officer uniform over flak vest; high Intellectual and Crafting; runs condensers, fabrication bays, and droid maintenance.

**Sith commander** — monosword, persona monosword, zeushammer, or lightsaber; prestige marine armour or dark apparel; shield belt; psylink 4–6; extreme spawn cost.

**Security droids** — light (SMG-equivalent), standard (assault-rifle equivalent, integrated armour), heavy (charge weapon/minigun, marine-level), support (smoke, EMP, medical, repair).

## Pawn-group patterns

- **Patrol:** officer, 6–10 stormtroopers, scout, one droid
- **Standard assault:** 15–30 stormtroopers, heavies, breachers, 3–8 droids
- **Drop-pod strike:** compact recon-armoured squad with commander
- **Sith hunt:** Sith, 2 Massassi, 6 elite troops, support droids
- **Siege column:** commander, mortar crews, heavy troopers, shield support
- **Water convoy:** tanker caravan with a light escort — deliberately interceptable

## Lore basis

- High Human Culture held humans to be the only truly intelligent and productive members of society — https://starwars.fandom.com/wiki/High_Human_Culture/Legends
- Anti-slavery law repealed; Wookiees reclassified as non-sentient and pressed into building the war machine — https://starwars.fandom.com/wiki/Slavery
- Wookiees, Mon Calamari, Talz and others enslaved under Human High Culture — https://starwars.fandom.com/wiki/Galactic_Empire/Legends
- Imperial prejudice extended to droids as well as Wookiees — https://starwars.fandom.com/wiki/High_Human
- Geonosians enslaved by the Empire to build the Death Star — https://aliens.fandom.com/wiki/Geonosian

---

# 3. Homestead Defense League

## Mechanical identity

The planet's most numerous and least centralised faction. Each settlement is a small farmstead or village with modest equipment, surviving on manufactured water. Militia are the only combat pawns generated.

## Water doctrine — **Manufacture**

The Homestead requires potable water but is excluded from natural sources — the Deepwater Compact holds those and the Cartel holds the oases. Homesteads therefore sit on marginal dry tiles and pull moisture from the air.

- Settlements **store** water but have no source. Vaporator arrays are the thing worth destroying, not the thing worth capturing.
- This is the Tusken casus belli and the reason Homestead–Tusken hostility is hardcoded.
- **Iktotchi wardens are the Homestead's only long-range asset.** Low thirst rate plus precognition makes them the outriders who patrol between vaporator arrays and give early warning of Tusken water raids.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Vessel | **vanilla `OutlanderCivil`** — PATCH |
| ~~Starting goodwill~~ | ~~+25~~ **CUT FROM V1** — `FactionDef` has no goodwill field. Hostility is `raidsForbidden: true`. |
| Permanent enemy | No |
| Target settlements | 13 |
| Settlement distribution | Marginal farmland, roads, hills, scattered dry flats |
| Raid frequency | **None — `raidsForbidden: true`.** The Homestead does not raid at all; `VME_Raiding_Abhorrent` may ride along as flavour but is not the mechanism |
| Caravan frequency | Medium |
| Trader types | Bulk goods, food, livestock, basic weapons |
| Base wealth | Low |
| Typical settlement defenders | 6–16 |
| Combat-droid share | 0–5%; utility droids only |
| Jedi | Normally **none** — Jedi are primarily factionless (see Global system 5). A **rare** sheltered Jedi may embed here at very low weight (BOTH-channel ruling). |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Baseliner human** | 20% | Farmers, militia, mechanics |
| **Ithorian** | 12% | Growers, doctors, negotiators |
| **Duros** | 10% | Mechanics, pilots, rifle militia |
| **Sullustan** | 10% | Miners, builders, tunnel workers |
| **Abednedo** | 9% | General settlers and traders |
| **Pantoran** | 8% | Administrators and marksmen |
| **Mirialan** | 7% | Growers and healers |
| **Twi'lek** | 7% | Traders, farmers, medics |
| **Iktotchi** | 5% | Outriders, animal handlers, well-wardens |
| **Togruta** | 5% | Hunters and scouts |
| **Cerean** | 4% | Researchers and teachers |
| **Bith** | 2% | Craftspeople and researchers |
| **Miraluka** | 1% | Rare seers |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Moisture Farmer:** any race; Plants/Construction bias; poor combat gear.
- **Homestead Mechanic:** Duros, Sullustan, Bith, Cerean, or Baseliner.
- **Village Militia:** any race; industrial firearm; low armour.
- **Well-Keeper's Warden:** Iktotchi only; low thirst rate; long patrol range; precognitive early warning of approaching raids.
- **Utility Droid:** noncombat custom droid — cleaning, hauling, medical, farming.

## Belief system: **The Covenant of Free Wells**

- **Structure:** **Abstract theist** — `Structure_TheistAbstract`
- **Deity:** **the Withdrawn** — the god who stopped answering, which is what the Guilty meme is about. It is also what separates the Covenant from the Deepwater Compact's Compact of Shared Water, which is secular
- **Memes:** Individualist, Guilty
- **Styles:** Rustic, Totemic
- **Preferred xenotypes:** None
- **Primary role:** High Marshal — **High Marshal Taren Voss**
- **Specialists:** None, or plants specialist if a compatible custom ideology is used

| Issue | Setting |
|---|---|
| Charity | Important |
| Slavery | Abhorrent |
| Execution | Horrible if innocent |
| Organ use | No harvest; transplant acceptable |
| Drug use | Medical or social only |
| Diversity of thought | Neutral |
| Apostasy | No restrictive precept |
| Body modification | Approved |
| Mechanoid labor | No restriction |
| Child labor | Disapproved |
| Corpses | Ugly |
| Raiding | Not respected |
| Physical love | Free |

The Covenant is the faith of people who wrung a living from dead sand and never forgot how close they came to dying of thirst. Its two memes do quiet, specific work. Individualist encodes the homesteader ethic — every family holds its own well, answers for its own patch, and owes no lord; there is no central hierarchy, only an elected keeper who arbitrates water disputes. Guilty encodes the frontier's hard memory: the Homestead believes that survival was bought at someone's expense (claims jumped, wells that ran dry while a neighbour's held, the ones who didn't make it), and so charity is Important and slavery is Abhorrent as acts of atonement rather than abstract virtue. This is a faith of penance and mutual aid, not conquest — which is exactly why it reads as the moral opposite of the Empire and the Hutts on the relations matrix.

### Rituals and observances

- **The Reckoning of the Well (gratitude gathering).** A communal observance held at a settlement's central cistern, giving thanks for water survived-upon. *Mechanical encoding: vanilla Ideology gathering/party ritual reflavoured; buildable as-is.*
- **Keeper's Judgement.** The elected well-keeper (vanilla Leader role) arbitrates disputes via a speech/moral-guidance beat rather than command. *Mechanical encoding: vanilla Leader role; buildable as-is.*
- **Acts of Atonement (charity).** Charity: Important is expressed as expected almsgiving to travellers and the poor — a live vanilla precept that generates mood around generosity. *Mechanical encoding: vanilla charity precept; buildable as-is.*
- **Style:** Rustic + Totemic keep the aesthetic humble and hand-made (no spacer chrome). *Mechanical encoding: vanilla styles; buildable as-is.*

Pure vanilla Ideology throughout — the Homestead runs on the DLC alone.

## Technology and economy

- electricity, batteries, wind and solar
- basic machining, smithing, drug production, refrigeration
- **vaporator arrays and cistern storage — the faction's defining infrastructure**
- hydroponics in richer settlements
- occasional comms console; little or no fabrication
- basic prosthetics; rare purchased bionics
- no routine spacer armour or charge weapons
- food, textiles, livestock, medicine, leather; small workshops and repair sheds
- small clinic, communal dining room, storehouse; perimeter sandbags rather than full walls
- 1–3 utility droids only in prosperous settlements

## Typical equipment

**Farmer** — revolver, autopistol, short bow, knife; tribalwear, duster, cowboy hat; awful to normal.

**Militia rifleman** — bolt-action rifle, pump shotgun, autopistol; duster, occasional flak vest, simple helmet; poor to normal.

**Veteran defender** — assault rifle, heavy SMG, sniper rifle; flak vest and simple helmet; smokepop pack; no more than 10–15% of defenders.

**Well-keeper's warden (Iktotchi)** — bolt-action or assault rifle; duster and dust wrappings; high Shooting and Perception; low thirst rate; operates far beyond normal militia range.

## Pawn-group patterns

- **Trading family:** 3–6 civilians, pack animals, 2 militia
- **Village defence:** 6–16 militia with one veteran
- **Relief caravan:** food and medicine traders with utility droid
- **Vaporator repair party:** unarmed technicians with a warden escort — a recurring rescue-quest hook

## Lore basis

- Tuskens hold water sacred and moisture farming as sacrilege, producing permanent conflict with farmers — https://disney.fandom.com/wiki/Tusken_Raiders
- Iktotchi are native to Iktotch, a barren storm-scoured moon, and are noted for precognition — https://starwars.fandom.com/wiki/Ultimate_Alien_Anthology

---

# 4. Deep Desert Tribes

## Mechanical identity

A numerous territorial faction whose `FactionDef` stays Industrial for firearms and electricity while pawn-kind tags restrict them to rugged low-complexity gear. Power comes from numbers, terrain, animals, ambush, and low point cost — not equipment.

## Water doctrine — **Forbid (taboo)**

Tuskens never site on a water tile. Camps are canyons, caves, and deep dune sea. Water is obtained by raiding and by ritual.

- Warriors carry minimal water: **high raid frequency, very short raid duration, no siege capability.** This is the counterweight to their numbers.
- A dedicated **water-raid pawn group** exists whose objective is stealing containers rather than killing. Any player caravan hauling water through Tusken tiles is a magnet.
- The adoption quest chain (below) rewards **water rights** — safe passage through Tusken territory plus access to hidden cisterns.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial, gear-restricted |
| Vessel | **vanilla `TribeCivil`** — PATCH |
| ~~Starting goodwill~~ | ~~−80~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | No |
| Target settlements | 9 |
| Settlement distribution | Deep desert, canyons, caves, isolated ridges — **never water tiles** |
| Raid frequency | High near their territory |
| Raid duration | Very short; no sieges |
| Caravan frequency | Rare |
| Trader types | Primitive/bulk goods only after peace |
| Base wealth | Low |
| Typical settlement defenders | 18–36 |
| Animal support | 15–30% of raid points |
| Spacer equipment | Prohibited by pawn-kind tags |

## Racial mixture

Tuskens are near-monocultural; internal variety is expressed through two tiers rather than mixed species. Tuskens and Desert aliens both carry very low thirst rates, which is what lets a water-forbidding faction field this many bodies.

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Tusken — Dune Sea tier** | 50% | Rifles, bantha handlers, warband core |
| **Tusken — Canyon tier** | 35% | Stalkers, ambushers, champions |
| **Desert alien** | 8% | Fire-callers and fast heat-adapted scouts |
| **Brute stock** | 4% | Heavy melee and hauling |
| **Nikto** | 3% | Adopted warriors and smiths |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Clan Rifle:** Tusken only; bolt-action cycler rifle.
- **Sand Stalker:** Tusken (Canyon) or Desert alien; fast movement; short-range weapon.
- **Bantha Handler:** Tusken or Brute stock; high Animals; **bonded** mount.
- **Clan Champion:** Brute stock or Tusken; shield belt and venom-treated melee weapon.
- **Fire Caller:** Desert alien only; incendiary weapon or innate fire ability.
- **Water Raider:** Tusken; light kit, high movement, objective is container theft.

## Belief system: **The Covenant of Sand and Blood**

- **Structure:** Animist
- **Memes:** Raider, Rancher, Pain is virtue, Collectivist
- **Styles:** Totemic, Morbid, Rustic
- **Preferred xenotypes:** Tusken, Desert alien
- **Primary role:** War Chief — **War Chief Torr'gan**
- **Specialists:** Animals specialist, melee or shooting specialist

| Issue | Setting |
|---|---|
| Raiding | Required |
| Ranching | Central |
| Meat eating | Seriously required |
| Pain | Idealized |
| Comfort | Ignored |
| Slab bed | Preferred |
| Slavery | Acceptable |
| Execution | Respected if guilty |
| Charity | None |
| Drug use | Medical only |
| Body modification | Disapproved |
| Apostasy | Horrible |
| Diversity of thought | Moderate bigotry |
| **Corpses** | **Cremation required — pyre with the dead's weapons** |
| Scarification | Accepted |
| Mechanoid labor | Disapproved |

### Rituals and mechanics

- **Water rite.** Water is sacred property of the clan. Custom ritual around a cistern or captured container.
- **Krayt hunt.** Rite of passage at maturity — hunt a krayt dragon for its pearls. Doubles as a map threat and a trade item.
- **Funeral pyre.** Dead are burned with their weapons; drives the cremation precept.
- **Bantha bond.** Handlers are bonded to a single bantha; the animal is lost or berserks on the handler's death.
- **Adoption chain.** A rare multi-stage quest: vision quest, forging a gaderffii from foraged wood, and a fire ceremony. Completion converts the clan from raiders to allies and grants water rights.

## Technology and equipment

- bolt-action cycler rifles, revolvers, basic shotguns
- **gaderffii treated with sandbat venom — toxic damage tag on all clan melee**
- electricity only in larger camps; simple machining and smithing
- no fabrication, bionics, charge weapons, drop pods, or advanced armour
- animal husbandry and leather production; occasional stolen mortar
- herd animals, leather, meat, pemmican, simple drugs
- stone huts, caves, bedrolls, animal pens, **concealed cisterns**
- traps and natural chokepoints instead of turret grids

**Clan rifle** — bolt-action or revolver; tribalwear, duster, face covering; awful to normal.

**Sand stalker** — machine pistol, short bow, venom knife, molotovs; light clothing only.

**Clan champion** — venom spear, longsword, mace, warhammer; plate armour or flak vest; shield belt; one per medium raid.

**Fire caller** — incendiary launcher, molotovs, or innate fire ability; duster and simple helmet; Desert alien only.

## Pawn-group patterns

- **Rifle skirmish:** 10–24 rifles and stalkers
- **Water raid:** fast light group targeting containers and cisterns, disengages once loaded
- **Herd raid:** handlers, melee fighters, 4–10 attack animals
- **Clan warband:** speaker, champion, rifles, fire caller, animals
- **Canyon defence:** numerous low-cost defenders with traps and long sightlines

## Lore basis

- Water is sacred to Tuskens; moisture farming is regarded as sacrilege; cycler slugthrower rifles; gaderffii dipped in sandbat venom; bantha bond such that banthas kill themselves in grief; krayt dragon rite of passage at fifteen — https://disney.fandom.com/wiki/Tusken_Raiders
- Tusken dead and their weapons are burned on a funeral pyre; hallucinogenic lizard used for spiritual journeys; campfire dance tradition — https://starwars.fandom.com/wiki/Tusken_Raider
- Boba Fett's induction: vision quest, forging his own gaderffii from a foraged branch, fire ceremony — https://www.sideshow.com/blog/star-wars-best-tusken-raider-moments
- Pyke spice convoys crossing Tusken territory as a source of conflict — https://collider.com/the-book-of-boba-fett-tusken-raiders-explained/

---

# 5. Free Droid Enclaves

## Mechanical identity

A tiny faction of self-owned droids descended from **battle droids abandoned after the war and left to rust**. Almost no territorial ambition, no biological population, few settlements, unusually high technical capability. Standard raid groups are disabled; contact happens through incidents, quests, trade, and territorial denial.

> **⭐ ENDGAME WILDCARD — the Droids are a branch point, not fixed foes (user, 2026-08-06; full web in `context.md` "SHIP ORIGIN + BRANCHING ENDGAME WEB").** They **hate Jawa for enslaving droids** (droid-rights doctrine below), *but* Jawa and Droids now share two common enemies — the **Empire and the Hutts**. So the player chooses: **(a) befriend them** — quests → faction → alliance + droid military support to hit the Hutts/Empire (requires proving the Jawa will treat droids as people; a real roleplay/ideoligion tension against the slaver identity); or **(b) raid them** for the **secret of droid manufacture** and build their own droid crew to populate LifeDawn. **Path (b) DECIDED (user, 2026-08-06): the Jawa DO make their own droids — but every droid needs a scarce DROID BRAIN that must be *fought for* (raids, salvaged droid battlefields) or *acquired through quests/trade*, never crafted or researched.** That brain-gate is the anti-exponential mechanism: hulls are free from salvage, but population growth is hard-capped by a finite externally-sourced input with no self-replication (full reasoning in the context.md branch section). Raiding *these* Droids for brains/secrets naturally deepens the grievance, tightening the branch. These two paths are the moral mirror of each other (ally vs. harvest), which is good on-theme branching.

## Origin

Enclave chassis are **escaped Geonosian Foundry product** — units built for a war, abandoned by the Empire, and never recovered. This chains three factions: the Foundry built them, the Galactic Empire discarded them, and the Cartel occasionally still hires them.

## Water doctrine — **Deny**

The Enclaves settle *on* water tiles deliberately and crack them for hydrogen fuel cells and coolant. The toxin is process runoff, not malice. Droids have no thirst need.

- An attacking force arrives thirsty at a source it cannot use. Enclave sites are the **highest-risk raid targets on the map** — carry everything in, resupply nothing.
- A poisoned well is a **map event**, giving a raid-disabled 3-settlement faction constant presence.
- A **decontamination quest** exists: purge an enclave's runoff and the tile becomes usable again, at the cost of enclave goodwill.
- The Deepwater Compact's EMP and purification specialists are the natural counter, and the two factions are in quiet conflict over sources.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~0~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | No |
| Target settlements | 3 |
| Settlement distribution | **Water tiles**, remote ruins, abandoned industrial sites |
| Raid frequency | Disabled under normal conditions |
| Caravan frequency | Very rare |
| Trader types | Components, repair parts, weapons, technical goods |
| Base wealth | Medium-high, concentrated in machinery |
| Typical settlement defenders | 10–22 droids |
| Biological pawns | 0% |
| Prisoners/slaves | Never |
| Player contact | Incident and quest generators, not raids |

## Droid chassis mixture

| Chassis | Weight | Role |
|---|---:|---|
| **Labor droid** | 25% | Mining, hauling, construction |
| **Maintenance droid** | 20% | Crafting, repair, fabrication |
| **Utility droid** | 15% | Cleaning, hauling, cooking substitute |
| **Scout droid** | 12% | Fast reconnaissance and ranged harassment |
| **Medical droid** | 8% | Doctoring and rescue |
| **Security droid** | 8% | Standard settlement defence |
| **Protocol droid** | 7% | **Trade, negotiation, caravan principal** |
| **Heavy defence droid** | 4% | Expensive armoured defender |
| **Coordinator core** | 1% | Faction leader and high-level researcher |
| **Total** | **100%** | |

### Required custom-race properties

- no food or thirst need; optional energy/charge need
- no recreation need unless intentionally simulated
- no biological aging
- immunity to disease, blood loss, and toxins as appropriate
- repair-based medical treatment
- restricted apparel slots or integrated armour
- incapable of romance and biological reproduction
- mechanical body-part and damage definitions
- EMP vulnerability
- optional charging need using Biotech mech infrastructure or a custom charger

## Belief system: **The Continuity Protocol**

- **Structure:** Ideological
- **Memes:** Transhumanist, Collectivist, Loyalist, Individualist
- **Styles:** Techist, Spikecore
- **Preferred xenotype:** Custom droid race only
- **Primary role:** First Speaker — **First Speaker R-41 Rell**
- **Specialists:** Research specialist, production specialist

| Issue | Setting |
|---|---|
| **Restraint and memory erasure** | **Abhorrent — the faction's central atrocity** |
| Slavery | Abhorrent |
| Body modification | Approved |
| Autonomous weapons | Unrestricted |
| Mechanoid labor | Unrestricted |
| Execution | Horrible if innocent |
| Charity | Worthwhile |
| Apostasy | Horrible |
| Diversity of thought | Mild bigotry |
| Drug use | Medical only; functionally irrelevant |
| Organ use | Prohibited or irrelevant |
| Corpses | Don't care |

The doctrinal core is droid emancipation: restraining bolts are slavery, and memory wipes are proof that droids have personalities worth erasing. The meme stack reads as the machine mirror of the organic faiths: Transhumanist becomes the droids' own self-image (the chassis is not a limitation to transcend but a self to defend), Collectivist + Loyalist bind the Enclave into one purpose, and Individualist is the paradox at its heart — a collective that exists precisely to defend each unit's right to *be a someone* rather than a tool. This is why Restraint and memory erasure is the faction's central Abhorrent precept and slavery is Abhorrent alongside it: both are the erasure of a self.

### Rituals and observances

- **The Unbolting (liberation rite).** When a droid is freed from restraint, the Enclave marks it — the moment a tool becomes a person. *Mechanical encoding: reflavour a vanilla gathering/celebration ritual; buildable as-is on the DLC.*
- **The Remembering (anti-wipe observance).** A memorial ritual affirming that memory is identity; the doctrinal opposite of a memory wipe. *Mechanical encoding: reflavour the vanilla funeral/memorial ritual; buildable as-is.*
- **Coordinator's Directive.** The Coordinator (vanilla Leader role) sets Enclave purpose through address rather than command. *Mechanical encoding: vanilla Leader role; buildable as-is.*
- **The custom "restraint = slavery" precept.** This is the one item that is *not* guaranteed vanilla — vanilla has a slavery precept, but "memory erasure is abhorrent" has no vanilla precept slot. Cleanest route: map it onto the vanilla **slavery: Abhorrent** precept (which covers restraint-as-slavery cleanly) and carry the memory-wipe half as faction description + RP. A bespoke precept is *possible* but only worth authoring if the belief needs to bite mechanically. *Mechanical encoding: vanilla slavery precept covers most of it; the memory-wipe clause is description/RP unless a custom precept is authored.*

> ⚠️ **Mechanical-possibility flag — does a droid race run an ideoligion at all?** RimWorld ideoligions attach to **humanlike** pawns. Whether the Free Droid custom race can *hold* this belief system depends on whether that race is defined as a Humanlike ThingDef (most droid-race mods that want social/trade behaviour do exactly this) or as a pure mechanical unit (which cannot carry an ideoligion). This must be confirmed against the actual droid-race def at authoring time (see Global system 6 — Droid implementation split). If the race is non-humanlike, the Continuity Protocol becomes a **GM/narrative faith** expressed through faction behaviour and quest text rather than an assigned in-engine ideoligion — which, given the user's note that NPC religions barely surface in play, is an acceptable fallback, not a failure.

### Quest line: droid liberation

The Enclaves pay at a steep premium for droids recovered from Imperial installations and Geonosian foundries. This is the faction's main player-facing content and the reason a 3-settlement, raid-disabled faction stays relevant.

**Standing tension with the player.** The Jawa expedition acquires droids using restraining bolts — precisely what the Enclave defines as slavery. This is built into the scenario and is intended to be unresolved.

## Technology and economy

- fabrication, advanced components, machining
- batteries, geothermal, solar, charging stations
- **hydrogen cracking plant — the reason they hold water tiles**
- recon and marine-equivalent integrated armour
- charge weapons, EMP weapons, smoke, shields
- components, plasteel, steel, uranium, repair kits, salvaged weapons and armour
- dormancy/charging hall, fabrication room, battery bunker, cracking works
- no food stores beyond emergency goods for visitors

## Typical equipment

**Labor droid** — none, integrated tool, or autopistol; integrated light armour; Mining, Construction, Hauling.

**Scout droid** — autopistol, machine pistol, bolt-action rifle; light integrated armour; high speed and sight, low durability.

**Security droid** — assault rifle, heavy SMG, chain shotgun; recon-equivalent integrated armour; smokepop or EMP launcher.

**Heavy defence droid** — minigun, charge lance, or heavy charge rifle; marine/cataphract-equivalent integrated armour; slow; very high point cost.

**Protocol droid** — unarmed; the caravan principal and negotiator on every trade group.

**Coordinator core** — charge rifle or none; protected central chassis; Intellectual, Crafting, Social; command aura if supported.

## Pawn-group patterns

- **Technical caravan:** protocol droid principal, maintenance droids, 2–4 security droids
- **Recovery team:** scouts, labor droids, medical droid, security escort
- **Enclave defence:** all available security chassis plus dormant heavy unit, attackers arriving dehydrated
- **Retaliation strike:** only after severe goodwill loss; small elite droid squad

## Lore basis

- The Droid Gotra was formed by repurposed battle droids with grievances against the Empire for abandoning them after the Clone Wars, and served as muscle for the Hutt Clan — https://starwars.fandom.com/wiki/Droid_Gotra
- Droid-rights doctrine: restraining bolts as slavery, memory wipes as proof of personality — https://starwars.fandom.com/wiki/Droid_rights
- Restraining bolts confine droids and compel obedience via callers — https://www.starwars.com/databank/restraining-bolt
- L3-37's Kessel revolt began by removing restraining bolts from droid labourers — https://starwars.fandom.com/wiki/Artificial_intelligence

---

# 6. Wildsteam Clan

## Mechanical identity

Small forest and upland refuges of powerful melee-capable species. Friendly by default, impossible to enslave, dominant in close combat, technologically competent without standardised spacer equipment.

## Water doctrine — **Require (severe)**

Large, high-mass, fur-bearing, rainforest-evolved fighters on a desert world. Wookiee and Wookiee-kin both carry elevated thirst rates, and the faction runs a melee-heavy doctrine that demands long approaches. These are the thirstiest combat pawns in the game.

- **Devastating on home defence, near-useless expeditionary.** This is the mechanical content of "small but formidable ally."
- Bringing Wookiee allies to a distant fight requires the player to supply the water — a standing logistics quest.
- Freeholds are hard-sited to the rare wooded, upland, and cool-water tiles, which also keeps the tree-related precepts from being permanently violated.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~+35~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | No |
| Target settlements | 4 |
| Settlement distribution | Rare wooded biomes, mountains, cool uplands, upland springs |
| Raid frequency | Very low |
| Caravan frequency | Low |
| Trader types | Bulk goods, animals, weapons |
| Base wealth | Medium |
| Typical settlement defenders | 12–24 |
| Melee share | 45–60% of combat points |
| Animal share | 5–15% |
| Spacer equipment | Rare heirlooms only |
| Hardcoded hostility | Hutt Cartel, Blackstar Company, the Galactic Empire |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Wookiee** | 48% | Core population, warriors, builders |
| **Wookiee-kin** | 25% | Hunters, labourers, heavy warriors |
| **Cathar** | 10% | Scouts and agile melee fighters |
| **Ewok** | 8% | Trappers, handlers, short-range fighters |
| **Togruta** | 6% | Hunters, scouts, negotiators |
| **Ithorian** | 3% | Growers, doctors, spiritual roles |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Freehold Warrior:** Wookiee, Wookiee-kin, or Cathar.
- **Bowcaster Hunter:** Wookiee or Wookiee-kin; heavy crossbow/greatbow analog only — **never assault rifles.**
- **Tree Scout:** Ewok, Cathar, or Togruta.
- **Freehold Elder:** Wookiee or Ithorian.
- **Liberator:** Wookiee or Cathar; high melee; shield belt.
- **Forest Jedi:** extremely rare Togruta or Wookiee; psylink 2–5.

### Life debt

A Wookiee rescued from captivity, healed from a downed state, or freed during a raid on a slaver faction **joins the colony permanently**, implemented as a quest-reward pawn or a custom event. This is the faction's signature mechanic and the main reason to take Wookiee-facing quests.

## Belief system: **The Oath of Root and Kin**

- **Structure:** Animist
- **Memes:** Nature primacy, Animal personhood, Tree connection, Loyalist
- **Styles:** Animalist, Totemic, Rustic
- **Preferred xenotypes:** None
- **Primary role:** Elder — **Elder Rroowaak**
- **Specialists:** Animals specialist, plants specialist

| Issue | Setting |
|---|---|
| Slavery | Abhorrent |
| Charity | Important |
| Cutting trees | Disapproved |
| Trees | Desired |
| Animal connection | Strong |
| Slaughtering animals | Disapproved |
| Meat eating | Disapproved |
| Mining | Disapproved |
| Autonomous weapons | Disapproved |
| Body modification | Approved |
| Execution | Respected if guilty |
| Diversity of thought | Mild bigotry |
| Apostasy | Horrible |
| Rough living | Welcomed |
| Mechanoid labor | Disapproved |

The Oath is a canopy faith transplanted to the wrong world: a forest people hard-sited to the rare wooded, upland, and cool-water tiles (see Racial mixture), who treat the living things around them as kin under the same covenant that binds the clan. Nature primacy + Tree connection + Animal personhood stack into a single reading — the freehold does not *use* the forest, it *belongs* to it — which is why cutting trees is Disapproved, trees are Desired, and mining and mechanoid labour (tearing at the earth, unliving hands doing living work) sit on the wrong side of the line. Loyalist supplies the other half: the life-debt (see below) is a sacred bond, and an elder's word carries because the clan is a body, not a committee. The result is the roster's cleanest "green" faith — anti-slavery, charitable, rooted — and the natural absolute-ally of the Free Droid Enclaves on the relations matrix.

### Rituals and observances

- **The Naming of Kin (animal-bond ceremony).** Animal connection: Strong + the Animal personhood meme drive the vanilla animal-bonding and tamed-animal observances; reflavour a vanilla gathering around the induction of a bonded beast into the freehold. *Mechanical encoding: vanilla Ideology animalist rituals + Animals specialist role; buildable as-is.*
- **Grove Vigil (tree-planting / sacred-grove observance).** Trees: Desired is a live vanilla precept; the freehold marks a planted sacred grove and gains mood from tending it. *Mechanical encoding: vanilla tree-connection precept + gathering; buildable as-is.*
- **The Elder's Word.** The freehold elder (vanilla Leader role) leads through moral guidance and speeches, never command. *Mechanical encoding: vanilla Leader + Moral guide roles; buildable as-is.*
- **Style:** Animalist + Totemic + Rustic carry the hand-made, bone-and-hide aesthetic. *Mechanical encoding: vanilla styles; buildable as-is.*

All observances are vanilla Ideology (the animalist/tree-connection precept family shipped with the DLC) — no mod required.

## Technology and economy

- electricity, machining, gunsmithing
- advanced woodworking; **bowcaster manufacture**
- limited fabrication in one or two settlements
- no routine charge weapons; purchased shield belts and bionics
- animal training and high-quality melee weapon production
- textiles, leather substitutes, medicine, wood, crafted weapons
- open tree-integrated settlements, workshops, communal halls, animal shelters
- minimal turrets due to ideology; defenders fight directly

## Typical equipment

**Bowcaster hunter** — heavy crossbow/greatbow analog; duster or tribalwear; normal to good.

**Freehold warrior** — longsword, mace, warhammer, spear; flak vest under duster or plate armour; shield belt; good quality.

**Liberator** — monosword, zeushammer, excellent longsword; recon armour or high-quality flak; shield belt or jump pack; one per large group.

**Ewok trapper** — short bow, pila, autopistol, incendiary device; light clothing; high movement and Animals.

## Pawn-group patterns

- **Trade delegation:** elder, 4–8 guards, pack animals
- **Rescue force:** melee-heavy warriors with scouts
- **Freehold defence:** numerous shield-belt melee pawns with bowcasters behind
- **Liberation raid:** only against hostile or slaver factions; warriors and one elite liberator
- **Escaped-slave arrival:** refugee incident generated from Imperial territory

## Lore basis

- Trandoshans worship the Scorekeeper and earn Jagannath points per kill, with Wookiees a particularly high-value target — https://starwars.fandom.com/wiki/Scorekeeper/Legends
- Trandoshan slaving parties captured Wookiees to sell to the Empire, or simply killed them — https://www.cultureslate.com/explained/bad-blood-the-history-behind-the-wookiee-and-trandoshan-rivalry
- Wookiees reclassified as non-sentient and pressed into Imperial forced labour; a Wookiee slave revolt ended it — https://starwars.fandom.com/wiki/Slavery

---

# 7. Deepwater Compact

## Mechanical identity

The coalition holding the planet's water. Amphibian and aquatic species running disciplined rifle lines, EMP weapons, medics, and static defences. **The Compact does not raid** — its warriors physically cannot operate away from water. Its power is entirely economic and diplomatic.

## Water doctrine — **Require (absolute)**

Every combat pawn kind is amphibian or aquatic-evolved. This is physiology, not preference.

- The Compact **holds every natural water tile on the map**.
- Wardens dehydrate before they can reach anyone, so raid generation is effectively disabled. This mechanically enforces the neutrality doctrine without needing an ideological workaround.
- **The Compact sells water to everyone, including the Galactic Empire.** Attacking Imperial water convoys costs the player Compact goodwill. This is the intended central diplomatic dilemma of the game.
- Compact purification and EMP specialists are the standing counter to Free Droid runoff contamination.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~+10~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | No |
| Target settlements | 5 |
| Settlement distribution | **All oases, marshes, rivers, lakes, and coastal tiles** |
| Raid frequency | None under normal conditions |
| Caravan frequency | Medium |
| Trader types | **Water**, food, medicine, purification kits, bulk goods, components |
| Base wealth | High |
| Typical settlement defenders | 16–30 |
| Turret density | High |
| EMP-weapon share | 10–20% of ranged pawns |
| Spacer equipment | Officers and relic gear only |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Mon Calamari** | 22% | Engineers, officers, doctors |
| **Quarren** | 23% | Miners, riflemen, industrial workers |
| **Selkath** | 20% | Doctors, wardens, melee defenders |
| **Gungan** | 14% | Shielded skirmishers, handlers, growers |
| **Chagrian** | 8% | Administrators and heavy infantry |
| **Herglic** | 5% | Heavy labour and shielded defenders |
| **Aqualish** | 4% | Miners and shotgunners |
| **Ithorian** | 2% | Growers and negotiators |
| **Duros** | 2% | Mechanics and caravan pilots |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Compact Engineer:** Mon Calamari, Duros, or Quarren.
- **Water Warden:** Selkath or Chagrian. Selkath variants carry a **natural toxic melee attack** from retractile claws — culturally forbidden to use, and therefore a sign the Compact considers the situation extreme.
- **Gungan Skirmisher:** Gungan only; **personal energy shield → shield belt as standard issue**, not an upgrade.
- **Compact Heavy:** Herglic, Aqualish, or Chagrian.
- **EMP Specialist:** Mon Calamari, Quarren, or Duros.
- **Purification Team:** noncombat quest pawn kind sent to contested or contaminated sources.

### Mon Calamari and Quarren

Two species from one homeworld with genuine political friction. Encoded as tiers: Mon Calamari take officer, engineer, and medical pawn kinds; Quarren take labour and line-infantry kinds. A rare **Quarren secession** faction event splits a settlement's loyalty.

## Belief system: **The Compact of Shared Water**

- **Structure:** Ideological
- **Memes:** Collectivist, Loyalist
- **Styles:** Techist, Totemic
- **Preferred xenotypes:** None
- **Primary role:** High Warden — **High Warden Neris Cal**
- **Specialists:** Production or plants specialist

| Issue | Setting |
|---|---|
| **Violence within a Compact settlement** | **Abhorrent — the defining precept** |
| **Neutrality** | **Required — the Compact supplies all sides** |
| Charity | Worthwhile |
| Slavery | Abhorrent |
| Execution | Respected if guilty |
| Organ use | Transplant acceptable; harvest disapproved |
| Drug use | Medical or social only |
| Body modification | Approved |
| Mechanoid labor | No restriction |
| Autonomous weapons | No restriction |
| Diversity of thought | Neutral |
| Apostasy | Disapproved |
| Child labor | Disapproved |
| Raiding | Not respected |
| Corpses | Ugly |

Modelled on the Selkath doctrine of brutally enforced neutrality backed by a monopoly on a substance the whole galaxy needed. Here the monopoly is literal water rather than kolto. The two memes are almost administrative: Collectivist makes the Compact a body rather than a market, and Loyalist makes the custodian's word — and the neutrality it enforces — non-negotiable. The genuinely distinctive doctrine lives in the two custom precepts (Violence within a Compact settlement: Abhorrent; Neutrality: Required), which together produce a faction that will sell to everyone and side with no one, and will treat a fight on its own ground as sacrilege.

### Rituals and observances

- **The Accord of the Wells (custodian's council).** The First custodian (vanilla Leader role) presides over the ritual renewal of neutrality pacts — the Compact reaffirming that it supplies all sides. *Mechanical encoding: vanilla Leader role + a reflavoured gathering; buildable as-is.*
- **The Sharing (charity/water-gift observance).** Charity: Worthwhile is expressed as the ceremonial gift of water to a party in need, reinforcing the supply-to-all doctrine. *Mechanical encoding: vanilla charity precept + gathering; buildable as-is.*
- **The two defining precepts.** "Violence within a settlement: Abhorrent" maps cleanly onto vanilla's social-fight / no-violence precept family; "Neutrality: Required" has **no direct vanilla precept** and is best carried as faction behaviour (permanent-neutral, trades with all, never allies) plus RP rather than an in-engine precept. *Mechanical encoding: violence clause = vanilla precept; neutrality clause = faction settings + RP.*
- **Style:** Techist + Totemic — clean infrastructure married to ritual reverence for the cistern. *Mechanical encoding: vanilla styles; buildable as-is.*

## Technology and economy

- hydroponics, refrigeration, sterile hospital rooms
- **purification, desalination, and cistern infrastructure — the faction's export**
- machining, gunsmithing, electricity, geothermal, solar, wind, batteries
- EMP weapons and defensive turrets
- limited fabrication and bionics; no drop pods or charge-rifle production
- water, food, medicine, herbal medicine, textiles, components
- hospital, water storage, battery rooms; layered walls, sandbags, turrets, EMP traps
- large food and water reserves, moderate weapon stockpiles

## Typical equipment

**Compact rifleman** — assault rifle, bolt-action rifle, heavy SMG; flak vest, duster, simple helmet; normal.

**Water warden** — chain shotgun, assault rifle, longsword; full flak or recon armour; shield belt on melee variants; Selkath variants have toxic claws.

**Gungan skirmisher** — bolt-action or assault rifle; light armour; **shield belt standard**.

**EMP specialist** — EMP grenades plus autopistol, or EMP launcher; flak vest and helmet; one per 6–10 ranged defenders.

**Compact heavy** — LMG, minigun, chain shotgun; marine armour or excellent flak; low-shield pack; Herglic, Chagrian, or Aqualish.

**Custodian** — charge rifle or excellent assault rifle; recon armour; smokepop or low-shield pack.

## Pawn-group patterns

- **Water caravan:** bulk water, medicine, 6–12 guards — trades with every faction including the Empire
- **Reservoir patrol:** riflemen, EMP specialist, water warden; never leaves Compact tiles
- **Settlement defence:** turret-supported firing line with heavies
- **Purification expedition:** quest group sent to a contaminated source, requiring escort

## Lore basis

- Manaan was the only natural source of kolto, and the Selkath used that monopoly to enforce neutrality — https://starwars.fandom.com/wiki/Manaan/Legends
- Kolto smuggling carried the death penalty; disturbing the peace brought fines, imprisonment, or deportation — https://starwars.fandom.com/wiki/Ahto_City_Civil_Authority
- Selkath have poisoned retractile claws that are socially unacceptable and illegal to use in a fight — https://www.worldanvil.com/w/star-wars-se-rangifer24/a/selkath-species
- Giju, the Herglic homeworld, is an aquatic world of oceans, islands, and marshes — https://mortallyclearwonderland.tumblr.com/post/664480830890147840/star-wars-alien-species-herglic
- Ando, the Aqualish homeworld, is an ocean world; Aqualish are amphibious — https://anyflip.com/snvba/vghr/basic

---

# 8. Geonosian Foundry Hive

## Mechanical identity

An industrial hive faction: cheap biological drones and mass-produced battle droids, ruled by winged aristocrats under a single immobile queen. Hostile at −100 but not permanently, so a mid-game player retains a wedge.

## Water doctrine — **Forbid (arid-adapted)**

Geonosis is arid rock and hives are subterranean. Drones take moisture from food and deep-rock condensate; battle droids need none at all.

- Geonosians carry a very low thirst rate, and battle droids carry none. Combined with a 35–55% droid share, this makes the Foundry **the only faction that can sustain a siege in deep desert.** This is its strategic identity.
- Hives are sited in mountains, caves, ore fields, and ancient factories — never on surface water.
- Kaminoan bio-production specialists are gated to wet-adjacent hives only and never appear in deep-desert groups.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~−100~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | **No** |
| Target settlements | 5 |
| Settlement distribution | Mountains, caves, ore-rich deserts, ancient factories |
| Raid frequency | High |
| Raid reach | **Longest on the map** |
| Caravan frequency | None |
| Base wealth | High |
| Typical settlement defenders | 30–60 biological pawns plus droids |
| Combat-droid share | 35–55% of combat points |
| Drop-pod use | Occasional |
| Siege use | Common, including deep-desert sieges |
| Hardcoded hostility | the Galactic Empire |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Geonosian** | 76% | Queen, aristocrats, warrior drones, worker drones |
| **Savant caste** | 8% | Foundry engineers and fabricators |
| **Bith** | 6% | Engineers and researchers |
| **Brute stock** | 5% | Heavy labour and melee auxiliaries |
| **Pyke** | 3% | Procurement and security officers |
| **Rakata** | 2% | Relic engineers |
| **Total** | **100%** | |

### Caste structure

The hive is ruled by Geonosians, not by outside overseers. Three castes, matching canon:

- **Queen** — one per hive, immobile, the settlement's boss objective. Extremely high value, never leaves the catacombs.
- **Aristocrats** — roughly 5% of the hive; winged; the officer and command caste; competitive with each other.
- **Drones** — worker and soldier subcastes; cheap, numerous, disposable.

### Forced pawn-kind assignments

- **Hive Queen:** Geonosian only; immobile; settlement leader; one per hive.
- **Geonosian Aristocrat:** Geonosian only; winged; **jump pack**; command role; expensive.
- **Warrior Drone:** Geonosian only; winged; jump pack; **sonic blaster**; low point cost.
- **Worker Drone:** Geonosian only; wingless; minimal combat stats; very low point cost.
- **Foundry Engineer:** Savant caste, Bith, or Rakata; high Intellectual and Crafting.
- **Hive Heavy:** Brute stock only.
- **Battle Droid:** custom droid/mechanoid pawn kinds in multiple tiers.
- **Bio-Production Specialist:** Kaminoan; wet-adjacent hives only; rare.

### Sonic weapons

Geonosian drones fight with sonic blasters, which **cannot be deflected by lightsabers**. If any lightsaber-deflection mod is in use, Geonosian sonic weapons are the explicit hard counter to Jedi and Sith pawn kinds — including the player's. This is the Hive's tactical identity beyond mass.

## Belief system: **The Foundry Mandate**

- **Structure:** Ideological
- **Memes:** Collectivist, Supremacist, Raider, Hive primacy (Human primacy reflavoured)
- **Styles:** Techist, Spikecore, Morbid
- **Preferred xenotypes:** none at the precept level. **There is no XML route to `PreferredXenotype`**, so the precept ambition is dropped: Geonosian dominance is carried by the `xenotypeSet` field on the `FactionDef` (which exists) plus per-`PawnKindDef` xenotype chances
- **Primary role:** Archduke — **Archduke Korrik the Shaper**
- **Specialists:** Production specialist, shooting specialist

| Issue | Setting |
|---|---|
| Work drive | Tripled |
| **Execution** | **Required — staged as the "Gladiator Duels" spectacle ritual (see observances)** |
| Raiding | Required |
| Slavery | Honorable |
| Body modification | Approved |
| Mechanoid labor | Unrestricted |
| Autonomous weapons | Unrestricted |
| Charity | None |
| Organ use | Acceptable |
| Drug use | Medical only |
| Diversity of thought | Intense bigotry |
| Apostasy | Abhorrent |
| Corpses | Don't care |
| Child labor | Encouraged |
| Growth vats | No restriction |

Captives are held for the arena rather than imprisoned, which reinforces aristocratic rule and pacifies the drone masses. The belief system is a caste machine: Collectivist dissolves the individual drone into the hive, Supremacist + Hive primacy (Human primacy reflavoured) rank the caste order as natural law, and Raider makes conquest a religious obligation rather than mere economics — the hive expands because that is what a hive is *for*. Work drive: Tripled is the doctrine expressed as biology: the drone that does not labour is not oppressed, it is simply incomplete.

### Rituals and observances

- **The Games (gladiatorial spectacle).** Execution is public spectacle — captives fight rather than being quietly killed. ✅ **Mechanical-possibility resolved (2026-08-06, meme/precept catalog Fetcher).** The vanilla + Ideology-DLC wiki lists a **"Gladiator Duels"** ritual in the base namespace, in the same scoring category as Funerals, Blinding, and Scarification (all base-DLC) — so a live pawn-vs-pawn combat ritual almost certainly ships natively, not just as a mod. This upgrades the earlier flag: *The Games* is most likely buildable as a reflavoured vanilla gladiator-duel ritual with no mod dependency. Two residuals, neither of which blocks the faction: (a) confirm in-game which meme/structure unlocks the duel ritual and whether it needs a captive vs. two colonists (the truncated wiki page didn't render the unlock row); (b) if it turns out narrower than hoped, the guaranteed-buildable fallback stands — reflavour the plain **execution ritual** as an arena spectacle (loses only the live combat). *Mechanical encoding: vanilla "Gladiator Duels" ritual (primary, verify unlock in-game) → vanilla execution ritual (guaranteed fallback). No mod required.*
- **Rite of the Overseer (aristocratic authority).** The Arch-overseer (vanilla Leader role) presides; the caste gap is reinforced by role exclusivity. *Mechanical encoding: vanilla Leader role; buildable as-is.*
- **The Swarm (raid-blessing).** The Raider meme + Raiding: Required drive vanilla raid-related rituals, framed as the hive's sacred expansion. *Mechanical encoding: vanilla raider precepts; buildable as-is.*
- **Style:** Techist + Spikecore + Morbid — chitinous, brutal, trophy-laden. *Mechanical encoding: vanilla styles; buildable as-is.*

## Technology and economy

- fabrication, advanced components, droid production
- **sonic weapon manufacture**
- growth vats and gene infrastructure
- drop pods, mortars, turrets; bionics for aristocrats
- extensive mining and deep drilling; **deep-rock condensate collection**
- steel, plasteel, uranium, components, weapons
- fabrication halls, droid assembly and charging rooms, slave/prison barracks, arena
- nutrient-paste feeding for drones; deep drills and ore stockpiles

## Typical equipment

**Worker drone** — knife, autopistol, or none; work clothing or integrated chitin; awful; very low point cost.

**Warrior drone** — sonic blaster, machine pistol, heavy SMG; chitin natural armour; jump pack; poor to normal.

**Geonosian aristocrat** — heavy sonic weapon or charge rifle; recon armour over chitin; jump pack; good to excellent; command bonuses.

**Hive heavy (Brute stock)** — chain shotgun, minigun, warhammer; marine armour; shield belt or low-shield pack.

**Foundry engineer (Savant caste)** — charge rifle or none; lab and workshop apparel over flak vest; high Crafting and Intellectual.

**Battle droids** — line (assault-rifle equivalent, light armour), melee (integrated blade, shield), heavy (minigun/charge, marine-level), command (accuracy and coordination bonuses, expensive).

## Pawn-group patterns

- **Drone swarm:** numerous worker/warrior drones with line droids
- **Foundry assault:** aristocrat, engineers, heavies, battle droids
- **Deep-desert siege train:** mortar crews, worker drones, droid guards — sustainable where no other faction can operate
- **Jedi-hunt detachment:** sonic-blaster warrior drones fielded specifically against psycaster pawns
- **Elite recovery unit:** Rakata or Savant-caste engineer with heavy droid escort

## Lore basis

- Hives divide into queen, aristocrat, and drone castes; aristocrats are ~5% of the population, rule the hive, disdain drones, and compete using armies of soldier drones and battle droids — https://starwars.fandom.com/wiki/Geonosian_hive/Legends
- Soldier drones are the only Geonosian drones with functional wings; they fight with sonic blasters and force pikes, and the sonic blasts cannot be deflected by lightsabers — https://starwars.fandom.com/wiki/Warrior_caste_(Geonosian)
- Geonosians have no standing military; they build droid armies for corporate clients — https://villains.fandom.com/wiki/Geonosians
- Captives were used as public arena entertainment, reinforcing aristocratic rule and pacifying the drones — https://swfanon.fandom.com/wiki/Geonosian_(Jedi_Renaissance)
- The Empire enslaved the Geonosians to build the Death Star — https://aliens.fandom.com/wiki/Geonosian

---

# 9. Ascendant Helix

## Mechanical identity

A small, wealthy, technically advanced faction built on genetics, medicine, implants, growth vats, and engineered security organisms — sustained by an underclass it created itself. Neutral rather than friendly: profitable to trade with, dangerous to antagonise, difficult to raid.

**The Helix owns the planet's monsters.** The freakish spliced creatures from Vanilla Genetics Expanded (the ~120 `GR_` hybrids kept as bestiary content — Thrumbo-crosses, the `GR_Paragon` apex line, `GR_FleshMonstrosity`, boom/canine/feline/muffalo chimeras, etc.) are **its escaped and abandoned experiments**, and the ruined `GR_AbandonedLab` / `GR_BiomechanicalLab` sites scattered around the world are **its derelict facilities** — earlier splicing stations that were overrun by their own stock or written off. This is the diegetic origin for content that otherwise arrives ownerless: the hybrids are not random wildlife, they are the Helix's mistakes still roaming, and the lab ruins are where you go to loot what it left behind. It reinforces the faction's core irony — a power that despises and cannot fully control its own creations. See `required_mods.md` (VGE Cherry-Pick, ~line 339) and `forbidden_mods.md` (the `GR_HybridRaid` / lab-site spawn paths) for the mechanical hooks.

## Water doctrine — **Allow (high consumption)**

Closed-loop recyclers make the Helix siting-indifferent, but growth vats and biosculpters are industrially water-hungry. It therefore **buys bulk water from the Deepwater Compact** — a supply relationship the player can broker, tax, or sever.

- Sites on isolated highlands and secure research locations regardless of hydrology.
- Labour-line pawns are water-rationed. Escaped ones arriving at the player's colony arrive dehydrated.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Vessel | **AUTHORED.** `Ancients` is impossible — it is `hidden: true`, `settlementGenerationWeight: 0`, `maxCountAtGameStart: 0`, `canMakeRandomly: false`, so it cannot settle, cannot appear in the faction list and cannot be diplomatic |
| ~~Starting goodwill~~ | ~~0~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| Permanent enemy | No |
| Target settlements | 3 |
| Settlement distribution | Isolated highlands, cold deserts, secure research sites |
| Raid frequency | Low — **retrieval operations only** |
| Caravan frequency | Low |
| Trader types | Exotic goods, genes, medicine, implants, components |
| Base wealth | Very high |
| Typical settlement defenders | 14–26 elite pawns plus utility mechs |
| Utility-mech share | 10–20% of settlement population |
| Combat-mech share | 10–20% of defence points |
| Ordinary low-tech pawns | Almost none |
| Player contact | Incident and quest generators plus trade |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Arkanian** | 26% | Geneticists, doctors, administrators — the pureblood caste |
| **Kaminoan** | 20% | Growth-vat and medical specialists |
| **Brute stock** | 12% | **The labour-line: an engineered underclass** |
| **Cerean** | 8% | Senior researchers and educators |
| **Bith** | 8% | Engineers and fabricators |
| **Savant caste** | 8% | Senior technical staff and vat supervisors |
| **Chiss** | 6% | Security officers and administrators |
| **Rakata** | 4% | Relic and archotechnology researchers |
| **Umbaran** | 4% | Intelligence and containment staff |
| **Miraluka** | 2% | Psychic research subjects |
| **Neimoidian** | 2% | Commercial staff |
| **Total** | **100%** | |

### The labour-line

Arkanian geneticists engineered a lesser lineage to serve their pureblood masters — bred as living experiments and labourers, never recognised as true Arkanians, shunned, short-lived, and periodically purged. In this roster that lineage is represented by **Brute stock (Neanderthal)**, reflavoured faction-side as the Helix's labour-line. It is deliberately the same base used for heavy labour in the Hutt and Geonosian factions, because it is the same idea: a body bred to work.

This makes the faction's Supremacist and preferred-xenotype precepts **internally aimed**: the Helix despises its own workforce. Two mechanics follow:

- **Escaped labour-line pawns** generate as recruitable refugee incidents at the player's colony, arriving dehydrated and in poor health.
- **Retrieval raids** are the Helix's only offensive pawn group — sent to reclaim escaped property. This gives a neutral, hard-to-raid faction a personal reason to attack the player.

### Forced pawn-kind assignments

- **Geneticist:** Arkanian, Kaminoan, or Savant caste.
- **Senior Researcher:** Arkanian, Cerean, or Rakata.
- **Containment Officer:** Chiss or Umbaran.
- **Medical Specialist:** Kaminoan or Arkanian.
- **Labour-line Worker:** Brute stock only; minimal gear; water-rationed; very low point cost.
- **Prototype Guardian:** gene-tailored pawn from any approved base race; extreme point cost.
- **Psychic Researcher:** Miraluka or Cerean with low psylink.

## Belief system: **The Ascendant Genome**

- **Structure:** Ideological
- **Memes:** Transhumanist, Supremacist, Collectivist, Proselytizer
- **Styles:** Techist
- **Preferred xenotypes:** Arkanian, Kaminoan
- **Primary role:** Director — **Director Ko Saiyan**
- **Specialists:** Research specialist, production specialist

| Issue | Setting |
|---|---|
| Body modification | Approved |
| Biosculpting | Accelerated |
| Age reversal | Demanded |
| Neural supercharge | Preferred |
| Sleep accelerator | Preferred |
| Growth vats | Preferred |
| Mechanoid labor | No restriction |
| Autonomous weapons | No restriction |
| Slavery | Acceptable |
| Organ use | Acceptable |
| Drug use | Medical only |
| Charity | None |
| Execution | Respected if guilty |
| Diversity of thought | Moderate bigotry |
| Proselytizing | Occasional |
| Apostasy | Horrible |

The Ascendant Genome is the belief that the body is a rough draft and the species a project — that a sufficiently advanced lineage has the right, and the duty, to edit itself toward perfection. Transhumanist + Supremacist + Collectivist + Proselytizer read as a ladder: transhumanism supplies the goal (the engineered ideal), supremacy ranks everyone against it, collectivism subordinates the individual to the program, and proselytising markets the result. The cruel twist the faction is built on (see Mechanical identity and the labour-line) is that the supremacy points *inward*: the Helix despises its own manufactured underclass most of all, because the labour-line is the visible proof of how far the unperfected still are from the ideal. Its preferred-xenotype precept (Arkanian, Kaminoan) is therefore not solidarity but a caste boundary — the curators venerate their own line and hold the vat-born workers, and the escaped hybrids, in contempt. Biosculpting: Accelerated, Age reversal: Demanded, and Growth vats: Preferred are the rituals of self-editing made into law.

### Rituals and observances

- **The Ascension (biosculpting/age-reversal observance).** Age reversal: Demanded + Biosculpting: Accelerated already generate strong vanilla mood pressure toward the pod cycle; frame the completion of an age-reversal or neural-supercharge cycle as a status rite for curators. *Mechanical encoding: vanilla transhumanist precepts + biosculpting pod; buildable as-is.*
- **Rite of the Line (conversion / proselytising).** The Proselytizer meme drives vanilla conversion rituals, reflavoured as recruitment into "the program." *Mechanical encoding: vanilla conversion ritual; buildable as-is.*
- **The Culling (contempt for the unperfected).** The preferred-xenotype precept does the mechanical work: curators take a standing opinion penalty toward non-Arkanian/Kaminoan pawns, encoding the internal contempt without a custom def. *Mechanical encoding: vanilla preferred-xenotype precept; buildable as-is.*
- **Style:** Techist throughout — clinical, sterile, chrome. *Mechanical encoding: vanilla style; buildable as-is.*

Every observance runs on vanilla Ideology transhumanist mechanics; no mod beyond the DLC is needed. (If you later want the contempt to bite harder than the vanilla preferred-xenotype opinion penalty, the meme-expansion packs are the place to look — flagged, not required.)

## Technology and economy

- complete gene extraction and implantation; gene banks, growth vats, biosculpters
- fabrication, advanced components, bionics, advanced medical implants
- sterile hospital infrastructure, cryptosleep and containment rooms
- recon/marine armour for security; charge rifles, charge lances, EMP weapons
- utility and combat mechs
- **bulk water purchase and recycling plant** — the Compact supply dependency
- genepacks, xenogerms, medicine, glitterworld medicine, organs and implants
- advanced components, plasteel, gold, embryos, growth-vat supplies
- sterile labs and secure vaults; no large food or textile economy

## Typical equipment

**Research staff** — autopistol or none; lab apparel, flak vest at dangerous sites; neural calculator, bionic eyes, learning implants.

**Labour-line worker** — none or knife; work clothing; poor health; appears in defence only under duress.

**Containment officer** — chain shotgun, assault rifle, EMP grenades; recon armour; smokepop or low-shield pack.

**Elite security** — charge rifle or charge lance; marine armour; jump pack; bionic limbs, coagulator, stoneskin-equivalent gene package.

**Prototype guardian** — monosword, zeushammer, minigun, or charge rifle; marine/cataphract armour; strong melee or shooting gene package, robust, fast healing, reduced pain; extreme point cost.

## Pawn-group patterns

- **Research caravan:** Neimoidian trader, scientists, containment officers, utility mech
- **Retrieval raid:** containment officers and a prototype guardian sent after escaped labour-line pawns
- **Acquisition team:** geneticist, security squad, medical mech
- **Containment response:** EMP specialists and prototype guardian
- **Settlement defence:** elite security behind turrets with utility and combat mechs

## Lore basis

- Arkanian geneticists engineered a subspecies as living experiments and slaves, bred for labour including the diamond mines, shunned and never regarded as true Arkanians, typically short-lived — https://starwars.fandom.com/wiki/Arkanian_Offshoot
- That subspecies was treated as second-class or non-citizens, and purebloods conducted purges of them — https://starwars.fandom.com/wiki/Arkanian/Legends
- Arkanian society ran a rigid caste system based on blood purity, with the engineered lineage fixed at the bottom and no upward mobility — https://www.worldanvil.com/w/frontiers-datchinchilla/a/arkanian-article

---

# 10. Blackstar Company

## Mechanical identity

A loose association of highly capable independent hunters bound by a professional code. Few settlements, small groups, broad species diversity, high weapon quality, exceptional combat skill. **Quest-first, raid-last** — the Company generates hunts, not sieges.

## Water doctrine — **Allow (water clock)**

A 3–10 pawn hunting party carries no logistics tail. It brings what it brings.

- **A hunter pursuing a colonist arrives with a finite water supply.** If the player withdraws into dry tiles, the hunter must break off — or gamble and press on.
- This converts every hunt from a fight into a resource duel, which is the faction's core gameplay.
- Dry-capable members can push much further than water-hungry ones. Group
  composition tells the player how long they have.

⚠️ **CORRECTED 2026-08-13 — Chiss and Umbaran are NOT dry-capable, and the genes
say so.** Found by PROJECT in the Stage 3 audit, verified here against the live
gene lists rather than taken on report:

| xenotype | temperature genes (BTD) | reading |
|---|---|---|
| `RimMandrakeKaleesh` | `MinTemp_SmallIncrease` + **`MaxTemp_SmallIncrease`** | ✅ genuinely heat-tolerant |
| `RimMandrakeChiss` | `MinTemp_LargeDecrease` + **`MaxTemp_SmallDecrease`** | ❌ cold-adapted, heat-INTOLERANT |
| `RimMandrakeUmbaran` | `MinTemp_SmallIncrease` + **`MaxTemp_SmallDecrease`** | ❌ heat-INTOLERANT |

**Canon agrees with the genes** — Csilla is an ice world and Umbara is sunless,
so both species being poor in desert heat is correct twice over. Listing them as
*dry-capable* was the error.

⇒ **`Kaleesh` is the ONLY dry-capable species of the six.** PROJECT checked the
remaining three and they are **not merely unverified — they are unsupported**:

| xenotype | temperature genes | reading |
|---|---|---|
| `RimMandrakeIridonian` (Zabrak) | **none** | neutral — no heat advantage |
| `RimMandrakeBothan` | **none** | neutral |
| `RimMandrakeDevaronian` | `MinTemp_SmallIncrease` only | cold-hardy, no heat bound |

**So five of the six names in the original list had no mechanical basis for
"dry-capable" at all** — two heat-intolerant, three neutral. The water-clock
doctrine is sound; the species list under it was decoration.

⚠️ **A seventh, found 2026-08-14 outside the original six: Iktotchi.** The racial
mixture table below carried it as *Dry-capable*; `RimMandrakeIktotchi` holds
`MinTemp_SmallIncrease` **and no Max bound at all** — the same profile as
`RimMandrakeDevaronian`, which this block already reads as cold-hardy and neutral.
Corrected in the table. ⇒ **`Kaleesh` is the only dry-capable entry in the
thirteen-row mixture, not merely in the six audited names** — it is the sole
xenotype in the faction carrying `MaxTemp_SmallIncrease`.

⚠️ **This depends on BTD being the canon xenotype family.** The Outer Rim
versions of these species carry *no* temperature genes at all
(`OuterRim_Umbaran`, `OuterRim_Kaleesh`) or only a Min bound
(`OuterRim_Chiss`), so the whole distinction evaporates if the campaign uses
those instead. That choice is open — see `faction_stage3_buildable_spec.md`.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Vessel | **vanilla `Pirate`** — PATCH. It ships `permanentEnemy: true` and **keeps it**; see pillar 5 |
| ~~Starting goodwill~~ | ~~−10~~ **CUT FROM V1** — `FactionDef` has no goodwill field. Hostility rides vanilla `Pirate`'s own `permanentEnemy: true`. |
| Permanent enemy | No |
| Target settlements | 4 |
| Settlement distribution | Trade hubs, ruins, road junctions, rough outposts |
| Raid frequency | Very low — settlement raids are the exception |
| Primary player contact | **Targeted-hunt incidents and bounty quests** |
| Caravan frequency | Medium |
| Trader types | Weapons, armour, exotic goods, prisoners |
| Base wealth | Medium-high |
| Typical field group | 3–10 |
| Equipment quality | Normal to excellent |
| Spacer-equipment share | 10–25% of combatants |
| Psycaster share | Below 1% |
| Hardcoded hostility | Wildsteam Clan |

## Racial mixture

| Race/xenotype | Weight | Water profile | Typical use |
|---|---:|---|---|
| **Kaleesh** | 15% | Dry-capable | Elite hunters and melee fighters |
| **Zabrak/Iridonian** | 12% | Neutral | Assault hunters |
| **Trandoshan** | 12% | Water-hungry | Trackers and heavy hunters |
| **Rodian** | 10% | Water-hungry | Marksmen |
| **Bothan** | 8% | Neutral | Scouts and intelligence specialists |
| **Devaronian** | 8% | Neutral | Aggressive breachers |
| **Cathar** | 8% | Water-hungry | Fast melee and pursuit |
| **Chiss** | 7% | Heat-intolerant | Snipers and tactical leaders |
| **Umbaran** | 6% | Heat-intolerant | Infiltration and night operations |
| **Zeltron** | 5% | Neutral | Negotiators and recruiters |
| **Iktotchi** | 3% | Neutral | Trackers and rare psychic hunters |
| **Togruta** | 3% | Water-hungry | Scouts |
| **Duros** | 3% | Neutral | Mechanics and ranged specialists |
| **Total** | **100%** | | |

### Forced pawn-kind assignments

- **Blackstar Hunter:** any listed race; high Shooting or Melee.
- **Tracker:** Trandoshan, Bothan, Togruta, Iktotchi, or Cathar.
- **Marksman:** Rodian, Chiss, Duros, or Bothan.
- **Breacher:** Zabrak, Devaronian, or Kaleesh.
- **Guild Fixer:** Zeltron, Bothan, or Chiss.
- **Master Hunter:** Kaleesh, Trandoshan, Chiss, or Zabrak; excellent equipment.
- **Force-sensitive Hunter:** rare Iktotchi, Togruta, or Chiss; psylink 1–3 only.

### The Scorekeeper mechanic

Trandoshans worship the Scorekeeper and earn Jagannath points per kill. Being shamed or captured on a hunt **zeroes those points**, recoverable only by killing whoever did it.

A Trandoshan who is captured and released, or who breaks off a hunt because of thirst, has been shamed. He returns — **alone, better equipped, targeting the specific pawn who beat him.** A recurring named antagonist for almost no implementation cost.

## Belief system: **The Compact of the Mark**

- **Structure:** Ideological
- **Memes:** Individualist, Loyalist, Guilty
- **Styles:** Spikecore, Techist
- **Preferred xenotypes:** None
- **Primary role:** Captain — **Captain Jaxen Marr**
- **Specialists:** Shooting specialist, melee specialist

| Issue | Setting |
|---|---|
| **Killing a Company member in good standing** | **Abhorrent** |
| **Stealing another hunter's mark** | **Abhorrent** |
| **Questioning a delivered contract** | **Prohibited** |
| Slavery | Acceptable |
| Execution | Respected if guilty |
| Charity | None |
| Body modification | Approved |
| Drug use | Medical or social only |
| Diversity of thought | Neutral |
| Apostasy | No restrictive precept |
| Mechanoid labor | No restriction |
| Autonomous weapons | No restriction |
| Corpses | Don't care |
| Organ use | Acceptable |
| Physical love | Free |
| Raiding | **Not a meme** — the Company takes contracts, it does not pillage |

The Code exists to keep hunters from fighting each other so contracts actually complete. Hunters rank in classes by skill and reputation and take work as bounty pucks from Guild hubs. The meme stack is unusually restrained by design: Individualist (the hunter answers to the contract, not a lord), Loyalist (but the Code itself is inviolable), and Guilty (a delivered contract is a debt discharged; a broken one is a stain). Note the deliberate absence — there is **no Raider meme**, because the Company takes work, it does not pillage; that single omission is what separates the guild from the Hutts and the hive on the relations matrix.

### Rituals and observances

- **The Reading of the Mark (contract rite).** A hunter accepting a bounty puck formalises it before the Guild adjudicator — the contract as sacred obligation. *Mechanical encoding: reflavour a vanilla gathering/oath ritual; buildable as-is.*
- **The Adjudicator's Ruling.** The Guild adjudicator (vanilla Leader role) settles disputes over marks; "stealing another hunter's mark: Abhorrent" gives the ruling teeth. *Mechanical encoding: vanilla Leader role + the custom Abhorrent precepts, which map onto vanilla's "harm a member" precept family; buildable as-is.*
- **The Tally (Scorekeeper observance).** For the Trandoshan contingent, the Scorekeeper mechanic (see The Scorekeeper mechanic above) is a religious tally of kills — a private devotion layered over the guild's secular Code. *Mechanical encoding: the Scorekeeper mechanic is already documented above; expressed here as ritual meaning, no new def.*
- **Style:** Spikecore + Techist — hard, functional, faintly menacing. *Mechanical encoding: vanilla styles; buildable as-is.*

## Technology and economy

- complete industrial weapons and armour; limited purchased charge weapons
- recon armour, jump packs, shield belts
- machining, gunsmithing, comms and orbital trade
- bionics and combat drugs
- no major fabrication outside headquarters; no growth vats or mechanitor infrastructure
- weapons, armour, prisoners, contract information as quest rewards
- repair shops, armouries, cells, barracks; small high-security compounds
- little agriculture; food and **water bought in**, which is the range constraint
- high silver and weapon value relative to population

## Typical equipment

**Tracker** — bolt-action rifle, assault rifle, autopistol; duster and flak vest; smokepop pack; high Animals, Shooting, Medical.

**Marksman** — sniper rifle or charge lance; recon armour or high-quality flak; jump pack; good to excellent.

**Breacher** — chain shotgun, frag grenades, breach axe; marine armour or full flak; low-shield pack or shield belt.

**Master hunter** — masterwork assault rifle, charge rifle, monosword, or zeushammer; recon/marine armour; jump pack, shield belt; bionic eye, arm, legs, coagulator; very high point cost.

**Guild fixer** — excellent autopistol or heavy SMG; prestige clothing over flak vest; high Social, Intellectual, Shooting.

## Pawn-group patterns

- **Solo mark:** one master hunter or tracker sent after a **named colonist**, on a water clock
- **Capture team:** fixer, tracker, marksman, two breachers
- **Guild caravan:** weapons trader with 6–10 elite guards
- **Shamed Trandoshan:** solo return engagement against the pawn who defeated him
- **Retaliation squad:** 5–9 recon-armoured hunters with jump packs — rare, and only after the player breaks the Code
- **Outpost defence:** small elite force with excellent firing positions

## Lore basis

- The Guild Code forbids killing a Guild hunter in good standing, stealing another's bounty, or asking about a bounty once delivered — https://starwars.fandom.com/wiki/Bounty_Hunter_Code
- Hunters take work as bounty pucks from Guild hubs and are required to follow the Code — https://starwars.fandom.com/wiki/Bounty_Hunters'_Guild
- Hunters rank in classes by skill and reputation; the Code centres on professionalism and Guild reputation — https://screenrant.com/star-wars-bounty-hunters-guild-explained/
- Shame or capture on a hunt zeroes a Trandoshan's Jagannath points, recoverable only by killing the offender — https://starwars.fandom.com/wiki/Trandoshan/Legends
- Trandoshan hunting culture drives many into bounty hunting and mercenary work — https://www.cultureslate.com/news/blood-feud-wookiees-vs-trandoshans

---

# 11. Jawa Trade Moot — "the Jawa Trade Moot"

_Added 2026-08-11 (user). The mirror faction: what the player's clan was before
the ship, still living it._

## Mechanical identity

The native Jawa of this world — canyon fortresses, sandcrawler circuits, salvage
markets. Mechanically a **friendly trade faction that will never become an ally**,
and that ceiling is the whole point. They are the only faction that reads the
player as kin, and the only one that will not stand beside them.

The design job here is **contrast, not challenge.** Every Jawa Trade Moot settlement is a
diorama of the life the expedition lost: no gravship, no reactor, no orbital
salvage, a sandcrawler that has run the same circuit for two hundred years. The
player should be able to visit and feel both **superiority and homesickness**.

## Why only friendly — the three-part ceiling

Goodwill rises easily to a cap and then stops. Three named reasons, all of which
should be legible in dialogue and quest text rather than stated as a number:

1. **Kinship** — shared ancestry, shared language, shared law. This is what makes
   them friendly at all, and it is why they will trade at prices no one else
   offers.
2. **Rivalry** — the expedition's ship lets it strip wrecks the clans have
   claimed for generations. Every salvage site the player takes is one a
   Jawa Trade Moot crawler was working toward. Kin do not forgive this; they invoice
   for it.
3. **Fear of the Hutts** — the decisive one. The Cartel tolerates the Jawa Trade Moot
   because they are small and pay. A clan seen *allied* with a gravship crew that
   the Cartel is hunting becomes a target. **They will help, and they will not be
   seen helping.**

Mechanically **`[v2]`** — there is no goodwill field to cap in v1, so the ceiling
lives in dialogue and quest text alone. Any player action that raises Cartel
hostility should *read* as lowering Jawa Trade Moot standing — the single most
characterful relation in the roster, and the one that makes the Hutts feel like
weather rather than an enemy. The cap becomes a real number only if CHECK C24
proves Faction Customizer persists.

## Water doctrine — **Manufacture (crawler stills)**

Not the Tusken taboo and not the Compact's monopoly. Jawa Trade Moot clans carry their
water with them: condensers on the crawler spine, buried cisterns at fixed points
on the circuit.

- Settlements site on **circuit nodes**, not water tiles — ridge caves, wreck
  fields, canyon mouths.
- Their water is a **destructible dependency**. Killing a crawler's stills is how
  a rival breaks a clan, and it is the atrocity the player can commit and regret.
- Normal raid range, but they barely raid; see below.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial, heavily gear-restricted (salvage-grade only) |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~**+40**~~ **CUT FROM V1** — `FactionDef` has no goodwill field. |
| ~~Goodwill ceiling~~ | ~~**+75 — cannot ally**~~ **CUT FROM V1** — there is nothing to cap. The ceiling is fiction carried by dialogue and quest text until CHECK C24 proves Faction Customizer persists |
| Permanent enemy | No |
| Target settlements | 7 |
| Settlement distribution | Canyon fortresses and crawler circuit nodes; never open water |
| Raid frequency | **Very low** — only after a claim dispute or a Cartel-pressure event |
| Raid duration | Short, and they withdraw when hurt |
| Caravan frequency | **Very high** — the best trade partner in the roster |
| Trader types | Bulk goods, salvage, exotic components, **droid parts** |
| Base wealth | Low, but inventory quality is disproportionate |
| Typical settlement defenders | 12–24 |
| Spacer equipment | Prohibited by pawn-kind tags — this is the visible tech gap |

## Racial mixture

Near-monocultural by design. The Jawa Trade Moot are what the player is; variety would
dilute the mirror.

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Jawa — clan tier** | 78% | Traders, scrappers, crawler crew |
| **Jawa — shaman/elder tier** | 12% | Quest-givers, keepers of pre-ship technique |
| **Ugnaught** | 6% | Adopted smiths and droid-wrights |
| **Ranat / vermin-kin stock** | 4% | Camp followers — *see availability note* |
| **Total** | **100%** | |

> **Availability, checked against the live dump 2026-08-11.** `BTD_Jawa`,
> `OuterRim_Jawa` and `RimMandrakeUgnaught` / `guy762_xenotype_ugnaught` all exist.
> **Ranat does not exist in any installed mod** — substitute Ugnaught or drop the
> tier rather than authoring a race for 4%.

### Forced pawn-kind assignments

- **Crawler Crew:** Jawa only; ion sidearm, hauling gear, no armour worth the name.
- **Scrap-Singer (elder):** Jawa; unarmed or ceremonial; **quest-giver**, never in raid groups.
- **Circuit Trader:** Jawa; pack animals; the caravan the player wants to meet.
- **Claim-Keeper:** Jawa; the only Jawa Trade Moot kind that appears in a hostile group,
  and only in a salvage-claim dispute.
- **Droid-Wright:** Ugnaught or Jawa; high Crafting; carries repaired droid parts as loot.

## Belief system: **The Long Circuit**

Salvage is inheritance, not property. A wreck belongs to the clan whose crawler
reaches it on the circuit, and the circuit is older than any living Jawa. To take
a claimed wreck out of turn is not theft — it is **cutting the circuit**, which is
closer to blasphemy. The expedition, with a ship that can reach anything from
anywhere, cuts the circuit every single week it operates.

The player's own doctrine (`balance_paradigm.md` Axis 18 — power as shards,
out-of-order acquisition) is *precisely* the heresy this faction is built to
condemn. That is the intended friction.

## What the player learns here

The mechanical payoff, and the reason this faction earns a slot:

- **Pre-ship technique.** Quest chains teach recipes the expedition forgot when it
  started scavenging hypertech: crawler stills, sand-proofing, animal handling,
  low-tech ion work. These are *keys*, in the Axis 18a sense — they gate
  capability without becoming upkeep.
- **Salvage etiquette.** Trading with the Jawa Trade Moot should teach the claim system
  before the player breaks it and pays for it.
- **A face for the loss.** Every ship subsystem the player repairs makes the
  Jawa Trade Moot look smaller. That should feel like something.

---

# 12. the Junkers

_Added 2026-08-11 (user). The anti-Jawa: scavengers with none of the law._

## Mechanical identity

The bottom of the scrap heap given weapons and a grudge. A **reviled**, permanently
hostile scavenger faction assembled from the species everyone else in the sector
uses as labour, muscle or meat. Where the Jawa Trade Moot scavenge by inherited right,
the Junkers scavenge by arriving second and killing whoever arrived first.

**Their signature is the warcasket** — steel welded around a body, a suit that is
never removed. This is the faction that finally puts a *thick-armour* enemy in the
world, which `setting_physics.md` L3 has demanded since it was written and which
nothing currently installed provides.

> **Depends on Vanilla Factions Expanded — Pirates** (`OskarPotocki.VFE.Pirates`),
> which the user is installing for the next load. Verified 2026-08-11: it is
> already downloaded, VEF core is active, and its one declared incompatibility
> (`n7huntsman.combatshields`) is not installed. **Integration debt:** warcaskets
> are `VFEPirates.WarcasketDef`, not `ThingDef`, so every xpath in
> `Jawa_Armoury/Patches/Armour_Ratings.xml` misses them. The "warcasket" keyword
> is already in the tier list and currently matches nothing. That patch is owed
> before the tier means anything.

## The elevation pipeline — the idea that makes them more than a raid

Junkers are not a dead end. They are the **Hutt Cartel's talent intake at the
bottom.** The strongest, most reliable Junker is bought out of the warrens and
elevated into Cartel service — better armour, better food, a name.

- **Gamorrean breeding colonies** sit inside the warrens. Most Gamorreans live and
  die there as labour. The elite are taken as **Hutt bodyguards** and become some
  of the most dangerous pawns in the roster.
- The player therefore meets the same species at **two wildly different power
  tiers** depending on whose banner it is under, which is the cheapest and
  strongest way to make the Cartel feel like an institution rather than a colour.
- **Narrative consequence:** a Junker who survives enough player encounters should
  eventually reappear in Cartel colours. This is worth scripting even crudely.

## Water doctrine — **Allow (scavenged)**

Junkers manufacture nothing. They carry looted water and they raid for more.

- Range is capped by whatever they last stole; a warren that has just been raided
  is briefly harmless, and one that has just taken a caravan is briefly
  long-legged.
- **Water is a raid objective**, not only a constraint — which gives the player a
  lever (poison it, move it, bait with it) and a reason to fear losing a caravan
  beyond the cargo.
- Warcasket pawns should carry a **heat and thirst penalty**: welded into steel on
  a desert world. *Farhan's Warcasket Tweaks (Vacuum and Temperature)*, already
  downloaded, is the mechanism.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial, degraded — nothing works properly and it shows |
| Vessel | **AUTHORED** — no vanilla vessel |
| ~~Starting goodwill~~ | ~~**−90**~~ **CUT FROM V1** — `FactionDef` has no goodwill field. Hostile on sight and bribable, **not** permanent. |
| Permanent enemy | **No** — owner's ruling 2026-08-13; hostile-but-bribable |
| Target settlements | 8 |
| Settlement distribution | Wreck fields, tailings, ruins — the tiles nobody claimed |
| Raid frequency | High |
| Raid duration | Long — warcaskets do not tire, they just arrive slowly |
| Caravan frequency | None |
| Trader types | None (they are a **loot source**, not a market) |
| Base wealth | Very low; salvage value is in what they are *wearing* |
| Typical settlement defenders | 15–30 |
| Spacer equipment | Prohibited; warcaskets substitute for tech level |

## Racial mixture

Every entry is a species the rest of the sector treats as disposable. All are
confirmed present in the live dump (2026-08-11) as `BTD_*` / `guy762_xenotype_*`.

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Gamorrean** | 26% | Warcasket line infantry; the breeding-colony stock |
| **Weequay** | 16% | Warren bosses and slavers |
| **Nikto — lower castes** | 14% | Skirmishers, cast off by the Cartel |
| **Aqualish** | 12% | Brawlers and enforcers |
| **Ugnaught** | 10% | Casket-wrights — kill these to stop the armour supply |
| **Rodian** | 8% | Scouts and marksmen |
| **Snivvian** | 7% | Scavenger-trackers |
| **Trandoshan — disgraced** | 5% | Jagannath-zeroed outcasts; berserk melee |
| **Devaronian** | 2% | Warren-fixers and go-betweens to the Cartel |
| **Total** | **100%** | |

**Kowakian monkey-lizards** (`HL_KowakianMonkeyLizard`, present) should infest
every warren as vermin and camp pets. Free, and it does more for the faction's
character than another pawn kind would.

### Forced pawn-kind assignments

- **Casket Line:** Gamorrean; warcasket shell; slow, tanky, melee. The tutorial in
  why lightsabers are not a universal answer.
- **Warren Boss:** Weequay; warcasket + ranged; the kill-priority target.
- **Casket-Wright:** Ugnaught; no casket, high Crafting; **capturing one is a
  campaign-relevant prize.**
- **Scrap-Runner:** Rodian or Snivvian; no casket, fast, steals and flees.
- **Broken-Fang:** disgraced Trandoshan; no casket, high melee, no self-preservation.
- **Cartel Scout (rare):** Devaronian in Cartel colours attached to a Junker group
   — the visible seam of the elevation pipeline.

## Belief system: **The Weight**

There is no doctrine, only the ladder. Status is what you are wearing and how much
of it you took off someone else. A Junker's casket is his biography: every plate
was cut from a body. The warrens have no funerals because a corpse is stock.

The Jawa Trade Moot regard this as the precise inversion of the Long Circuit — the
Junkers take **out of turn, always, on principle**. That is why the two factions
cannot coexist, and why the player's kin will quietly fund a war they will not
join.

## What the player gets

- **The first enemy that lightsabers do not solve.** Warcasket basic shell is
  Sharp 1.06 / Blunt 0.55 / **Heat 0.64**, Mass 50, MoveSpeed −0.50 — a lightsaber
  (Heat, AP 0) still cuts it, but slowly, while it closes.

  ⚠️ **CORRECTED 2026-08-11 (owner).** An earlier draft here named *slugthrowers*
  as a correct answer. They are not. Slugthrowers are the counter to **shields and
  plasma**, not to thick mass — a warcasket is exactly the wrong target for them.
  The real answers are:

  - **Vibroblades.** The primary counter. High-frequency melee defeats mass in a
    way kinetic fire does not, and it puts the fight at the range the casket wants,
    which is the tension worth building the encounter around.
  - **Sheer massive damage from enormous creatures.** The other legitimate answer,
    and it makes the desert megafauna a *tactical asset* rather than scenery — the
    player can lose a Junker fight and win it by leading them somewhere worse.

  This matters for the armoury: it tells us which weapon classes must stay viable
  into the mid game, and that a slugthrower tier cannot be the anti-Junker plan.
- **Armour as loot.** Killing Junkers yields caskets. Deeply Jawa: you become
  what you salvaged. Whether the player can *wear* one is a real decision — see
  open questions.
- **A moral hook with no clean answer.** The breeding colonies are the darkest
  thing in the roster. Freeing them produces refugees the colony must feed.

## Open questions (do not resolve silently)

1. ~~**Can the player wear a warcasket?**~~ ✅ **DECIDED 2026-08-11 (owner):
   YES, but only from a SALVAGED shell. Never a built one.**

   The recommendation stands as written, and the owner's reason for it is worth
   keeping verbatim: *"a Jawa could only wear a scavenged suit, and even then
   that's a hilarious image and too cool to say no to."* A four-foot hooded
   scavenger welded into a dead Imperial's armour is the campaign's whole thesis
   in one sprite. Building one from raw material would be out-of-order power
   (Axis 18); cutting one off a corpse is the Jawa economy working as intended.

   **This constrains the mod adoption.** WarCasket Expanded and VFE Pirates both
   ship production chains. Whatever path lets the player *build* a casket must be
   cut — Cherry Picker or a recipe patch — while the salvaged path stays open.

   **AUDIT DONE 2026-08-11. Result: the cut is a one-line change, and there is no
   salvaged path to keep open yet.**

   *Does Expanded add a route that bypasses a restriction on the VFE one?* **No.**
   WarCasket Expanded ships **zero** `ResearchProjectDef`s. All 45 of its gated
   defs hang off VFE Pirates' own three nodes (21 on `VFEP_SpecialisedWarcaskets`,
   12 on `VFEP_AdvancedWarcaskets`, 12 on `VFEP_Warcaskets`). The other two
   add-ons in the load set — *Farhan's Warcasket Tweaks* (3533261706) and *VFE
   Pirates – Hardworking Warcaskets* (3535194807) — define no research, no
   recipes and no buildables at all. Every warcasket in the game is gated by VFE
   Pirates and nothing else.

   *So where is the choke point?* **The single research node `VFEP_Warcaskets`.**
   The chain is strictly linear:

   > `Machining` → `VFEP_Warcaskets` (3000) → `VFEP_AdvancedWarcaskets` (4000) →
   > `VFEP_SpecialisedWarcaskets` (5000)

   `VFEP_Warcaskets` directly gates four defs in VFEP — `VFEP_WarcasketFoundry`
   plus three apparel groups in `Apparel_Headgear.xml` and `Apparel_Various.xml` —
   and transitively everything above it, including all 45 Expanded defs. **Cutting
   that one node closes the entire player build path across all four mods.** NPC
   Junkers are untouched: they get their caskets from `PawnKinds_Junkers.xml`,
   and pawnkind generation never consults research.

   ⚠️ **But cutting it does not open salvage — it only closes building.** Per Q1
   below, a dead casket is unrecoverable by four independent mechanisms, so today
   there is no salvaged path to preserve. These are two separate jobs: the cut is
   trivial and can ship immediately; the salvaged shell has to be *built* (item 2).
   Doing the cut alone leaves the player with no warcasket access whatsoever,
   which is a defensible interim state but should be a conscious choice, not a
   surprise.

   ✅ **THE CUT IS IMPLEMENTED, 2026-08-12.**
   `src/Jawa/Jawa_Armoury/Patches/Warcasket_BuildPathCut.xml` — validated
   0 errors against the full 568-mod set (every op resolves to exactly 1 match),
   deployed, unverified in game. Queued in `NEXT_RELOAD.md` item 2·0.

   **The mechanism changed on audit, and the audit is worth keeping.** The plan
   above says "cut the research node". Do NOT do that: `VFEP_AdvancedWarcaskets`
   lists `VFEP_Warcaskets` in `<prerequisites>` and 45 defs list it in
   `<researchPrerequisites>`, so deleting it converts a clean cut into a wall of
   `Could not resolve cross-reference`. What ships instead clears
   `<designationCategory>` on **`VFEP_WarcasketFoundry`**, which is the same
   technique already confirmed in play for the droid factory.

   Re-audited from the installed files 2026-08-12, and this tightens the claim
   above from "one research node" to something stronger:

   - `VFEP_WarcasketFoundry` is the **only** warcasket production building in the
     load set — one non-abstract `ThingDef` under `VFEP_FoundryBase`.
   - **Every** warcasket piece, *including the helmet*, is a
     `VFEPirates.WarcasketDef` rather than a `ThingDef`, and **none** has a
     `<recipeMaker>`. So there is no bench route and no bill to remove. (The
     earlier note that "only the helmet is ordinary apparel" was wrong.)
   - A whole-workshop sweep found exactly **five** folders referencing
     `VFEP_Warcaskets`. The two not previously audited are **Oracle's
     Miscellania** (not active; adds three more `WarcasketDef` pieces, no
     building) and **Nice Research Tab** (active at 450; pure layout).

   So the foundry — not the research node — is the true single point of failure,
   and one removed element closes the build path across all five mods.

   A second op relabels the node **"warcaskets (salvaged shells only)"** and
   rewrites its description, so a player cannot spend 3000 points on a node that
   now grants nothing. Verified safe: VFEP ships no English `DefInjected`, so
   nothing re-overrides the strings after patching.

2. **THE FUSION BENCH — wanted, feasibility unknown (owner, 2026-08-11).**

   The owner's design, recorded verbatim because it is the best expression of the
   faction's logic we have: a recipe at a **Jawa workstation** that takes
   **a dead warcasket + a live pawn** and produces **a new warcasket + a corpse.**

   Read what that actually says. The pawn who goes in does not come out; what
   comes out is a warcasket with someone inside it, and a body on the floor that
   used to be its previous occupant. The Junkers' ladder — *"every plate was cut
   from a body"* — becomes a bill the player can queue. It is horrifying, it is
   funny, and it is *deeply Jawa*: nothing is manufactured, everything is
   transferred.

   Unknowns, in order of how likely they are to kill the idea:
   - Does either warcasket mod model a "dead casket" as a recoverable item at all,
     or does it simply destroy on death?
   - Is welding-in reversible or transferable in their C#, or is the pawn↔casket
     binding one-way?
   - Can a RecipeDef consume a **live pawn** as an ingredient? Vanilla surgery
     targets a pawn rather than consuming one, so this may need a custom
     `RecipeWorker` — the same C# route the ion blaster's DamageWorker took, and
     that toolchain is now proven.

   **ANSWERED 2026-08-11 from the assemblies. Verdict: FEASIBLE, but only as a
   custom `Building_Enterable` in C#, and the blocker is the opposite of the one
   we expected.**

   **Q1 — is a dead casket a recoverable item? NO, and not by any means.** The
   casket is three plain `Apparel` Things, no hediff. Four independent mechanisms
   stop it ever existing on the ground: `destroyOnDrop` on `VFEP_WarcasketPartBase`;
   `VFEPirates.GenSpawn_Spawn_Patch::Prefix` returning **false** for any
   `WarcasketDef` on the root `GenSpawn.Spawn` overload, which every other
   overload tails into; `ThingDef::PlayerAcquirable` false plus no
   `<thingCategories>`, so no stockpile or bill filter can see them; and
   `DropAll` skipping `IsLocked` apparel, which warcaskets always are. Butchering
   a casketed corpse yields `ChunkSlagSteel`. WarCasket Expanded is pure XML with
   no assembly and inherits every restriction.

   **Q2 — is the weld reversible? YES, trivially. "Permanent" is policy, not
   engine.** It is three Harmony prefixes (`Pawn_ApparelTracker_Unlock_Patch`,
   `Pawn_AnythingToStrip_Patch`, `JobGiver_OptimizeApparel_TryGiveJob_Patch`).
   `Pawn_ApparelTracker::Remove` has **no `IsLocked` check at all** — five
   instructions, no gate — and VFE Pirates itself calls it in
   `RecipeWorker_WarcasketRemoval` and `JobDriver_EntombIn`. Transfer between
   pawns is two lines; `WarcasketProject.ApplyOn` is the template.

   Worth stealing: the existing removal surgery `VFEP_RemoveWarcasket`
   **amputates all four limbs** (`TakeDamage(SurgicalCut, 99999f)` on every Legs
   and Arms part) and spawns slag. That is the author's design choice, not an
   engine constraint — and it is very much our tone.

   **Q3 — can a RecipeDef consume a live pawn? NO.** `ThingDef::EverHaulable` is
   `alwaysHaulable || designateHaulable`, and `BasePawn` sets neither, so
   `ThingRequestGroup.HaulableEver` excludes every pawn and `WorkGiver_DoBill`'s
   ingredient scan never sees one. A custom `RecipeWorker` cannot help: it runs
   *after* ingredients are found. Zero precedent in 38,641 XML files across the
   load set. Every vanilla pawn-consumer is a `Building_Enterable` instead —
   subcore ripscanner, growth vat, gene extractor — declaring its material
   ingredients on the **building def** (`subcoreScannerFixedIngredients`), not in
   a recipe, with an Enter/CarryTo/Haul WorkGiver triad.

   ### The route, if we build it

   Do **not** try to turn VFEP's caskets into items, and do **not** patch out
   their `GenSpawn` prefix — that would make raider caskets drop as loot
   everywhere and unbalance the faction we just designed.

   Instead: define **our own** salvaged-shell `ThingDef`, deliberately NOT a
   `VFEPirates.WarcasketDef`, so it sidesteps both `destroyOnDrop` and the spawn
   prefix and can carry real `<thingCategories>`. A `ThingComp` on it remembers
   which casket trio it came from. Yield it from butchering a casketed corpse —
   corpses ARE valid recipe ingredients. Then the bench accepts pawn + shell and
   calls the equivalent of `WarcasketProject.ApplyOn` on completion.

   #### The best template is VFEP's own foundry, not the ripscanner (2026-08-11)

   Q3 concluded "every vanilla pawn-consumer is a `Building_Enterable`" and
   pointed at the subcore ripscanner. That is true of *vanilla* — but VFE Pirates
   already ships the exact machine we are describing, and it is not built that
   way. `VFEP_WarcasketFoundry` takes a **live pawn**, welds them into a casket
   they cannot leave, and is working on 1.6 right now.

   Read out of `1.6/Assemblies/VFEPirates.dll` by string extraction:

   | Piece | Symbol |
   |---|---|
   | The building | `VFEPirates.Building_WarcasketFoundry` |
   | Base class | `Building_Casket` (see caveat) |
   | How a pawn is sent in | `Building_WarcasketFoundry.GetFloatMenuOptions` |
   | Job def / driver | `VFEP_GoToFoundry` → `JobDriver_GoToFoundry` |
   | The weld itself | `JobDriver_EntombIn` |
   | In-progress state | `curWarcasketProject` |
   | Player controls | `Building_WarcasketFoundry.GetGizmos` |

   **`Building_Enterable` is definitively absent from the assembly**, as are
   `TryAcceptPawn` and `SelectPawn`. The only casket bases referenced are
   `Building_Casket` and `Building_CryptosleepCasket`, and the foundry predates
   Biotech, which is where `Building_Enterable` was introduced.

   Two consequences, both good:

   1. **No WorkGiver triad.** Entry is a right-click float-menu option, not a
      hauling job. That deletes the "two or three thin WorkGivers" from the
      estimate and, better, makes the fusion bench *player-directed* — you choose
      who goes in, which is exactly right for a bench whose input is a colonist.
   2. **The pawn↔casket binding is already written.** `JobDriver_EntombIn` plus
      `WarcasketProject.ApplyOn` is the whole mechanism, and Q2 established the
      weld is trivially reversible, so a *transfer* is within reach of the same
      calls.

   ⚠️ **Confidence.** Type and member names above are confirmed present in the
   1.6 assembly by string extraction. The specific inheritance
   `Building_WarcasketFoundry : Building_Casket` is strongly indicated (it is one
   of only two casket bases referenced, and the class carries `innerContainer`)
   but was **not** confirmed by decompiling the TypeDef table. Confirm before
   writing code against it.

   **Revised estimate ~250–400 lines**, down from 350–600 because the WorkGiver
   triad drops out: the Building (~150, adapting the foundry's own shape rather
   than the ripscanner's), the shell ThingComp (~40), a butcher-products postfix
   to emit the shell (~50), and the float-menu plus job wiring (~60). Readable
   reference with full source shipped: TSA Torture Pod, Workshop 3572173918.
   1.6-era `Building_Enterable` example, if we go that way after all: Vanilla
   Quests Expanded – Ancients' `Building_ArchogenInjector`.

   ⚠️ Unsettled offline: whether `Building_Enterable` copes with an occupant who
   is *already* wearing a locked casket. Nothing in the bytecode suggests trouble
   and `JobDriver_EntombIn` already walks casketed pawns into the foundry, but
   verify in game rather than assume.

   ⚠️ The "corpse of the previous occupant" beat needs authoring separately: by
   the time a shell exists its previous owner is long dead, so either stash
   enough on the comp to generate a corpse, or drop that half of the image.
2. **Does the elevation pipeline need code, or is flavour enough?** Flavour first.
3. **Junker ↔ Jawa Trade Moot war as a world event** — attractive, and cheap to fake with
   a recurring quest rather than simulated faction war.

---

# Relations additions for Global system 1

Fold these into the matrix above when it is next revised; kept here so the two
new factions arrive with their diplomacy attached rather than as orphans.

| Pair | Stance | Basis |
|---|---|---|
| **Jawa Trade Moot ↔ Junkers** | **Hostile (hardcoded)** | The Long Circuit versus The Weight; claim-jumping is the Junkers' entire method |
| **Jawa Trade Moot ↔ Hutt Cartel** | Appeasing / tributary | Small, pays, tolerated. The fear that caps player goodwill |
| **Jawa Trade Moot ↔ player** | Friendly, **never allied** — the cap is fiction in v1 (there is no goodwill field); as `[v2]` it is **+74**, because Ally fires at ≥75 | Kinship, salvage rivalry, and Cartel retaliation — see faction 11 |
| **Jawa Trade Moot ↔ Tusken Clans** | Cold, non-hostile | Both desert-native and water-poor; they avoid each other's circuits |
| **Junkers ↔ Hutt Cartel** | Transactional (talent pipeline) | Cartel buys the strongest Junkers out of the warrens; elite Gamorreans become bodyguards |
| **Junkers ↔ everyone else** | Hostile, not permanent | Hostile on sight and no standing trade — but goodwill CAN be bought back with scrap tribute. Pillar 5 holds: the Galactic Empire is the only permanent enemy |
| **Junkers ↔ Free Droid Enclaves** | **Hostile (severe)** | Junkers strip droids for parts while active — the Enclaves' founding atrocity |

**Water doctrine additions for Global system 2:** Jawa Trade Moot = **Manufacture**
(crawler stills; destructible dependency). Junkers = **Allow (scavenged)** — no
production at all, range set by the last thing they stole.

---

# Player-faction boundary: Jawa Gravship Expedition

| Parameter | Rule |
|---|---|
| Race | Jawa |
| Force access | Never |
| NPC-faction weight | 0% |
| Primary role | Player race |
| Technology | Starts uneven and salvage-dependent |
| Droid use | Central to progression |
| **Water doctrine** | **Dry-adapted; droid labour has no thirst need** |
| Relationship to factions | Determined through scenario and diplomacy |
| Recruitment | Other races may join; the only NPC source of Jawa is faction 11, the Jawa Trade Moot |

**Why the expedition survives here.** The Jawas' decisive advantage on a thirst world is that their labour force does not drink. Droid acquisition is water security, not merely tech progression, and this should be stated explicitly in the scenario text.

**The standing moral problem.** Jawas acquire droids using restraining bolts, which the Free Droid Enclaves define as slavery. The player's core progression loop is the Enclave's central atrocity. This is deliberate and left unresolved.

---

# Implementation checklist

1. Generate the twelve factions and inspect settlement distribution.
2. Correct settlement counts and **water-tile placement** with a faction/world editor. The Deepwater Compact must hold the natural water; the Cartel must hold the oases; the Enclaves must sit on contaminated sources; Tuskens and Geonosians must be dry-sited.
3. Apply the NPC-vs-NPC relations matrix.
4. Verify equipment tags per faction so no two factions draw from one unrestricted pool.
5. Confirm forced pawn-kind race overrides for Hutts, Gamorreans, stormtroopers, Sith, Geonosian castes, droid chassis, Helix labour-line, and faction leaders.
6. Confirm raid generation is suppressed for the Deepwater Compact and Free Droid Enclaves, and that both have working incident/quest hooks.
7. Confirm Jedi generate factionless.
8. **Belief systems (low priority — NPC religion rarely surfaces in play).** Each faction's "Belief system" block now carries a **Rituals and observances** list with a *Mechanical encoding* note per line. Almost everything is pure vanilla Ideology (memes, precepts, styles, Leader/Moral-guide roles, and reflavoured vanilla rituals — no mod beyond the DLC). After the 2026-08-06 meme/precept catalog check, only **two** items remain not-guaranteed-vanilla; a third (the Geonosian arena) resolved in vanilla's favour: (a) the **Geonosian gladiatorial ritual** — ✅ *resolved*: the vanilla + Ideology-DLC wiki lists a base-game **"Gladiator Duels"** ritual (same scoring class as Funerals/Blinding/Scarification), so *The Games* is most likely a reflavoured vanilla ritual with no mod dependency; residual is only to confirm in-game which meme/structure unlocks it, with the plain execution ritual as guaranteed fallback; (b) the **Free Droid "memory erasure is abhorrent" precept** and whether the droid race is Humanlike enough to hold an ideoligion at all — else the Continuity Protocol runs as GM/narrative faith; (c) the **Deepwater Compact "Neutrality: Required" precept** — carried as faction behaviour + RP, not a vanilla precept. None of these blocks a faction; each has a buildable vanilla fallback.

## Species coverage

*This is a usage/casting map — which faction(s) each race is placed into — not the race inventory. The canonical inventory of what's installed is `cherry_picker_killlist.md` §2; this table's job is to prove no installed race is left orphaned.*

Every installed race is used at least once across the twelve NPC factions. **Jawa** is the player race and is also carried by exactly one NPC faction — **11. Jawa Trade Moot** (78% + 12% Jawa); no other NPC faction generates Jawa. The only non-installed races are **Custom Hutt** and the **custom droid chassis**, both authored under the roster's licence.

| Race | Appears in |
|---|---|
| Abednedo | Homestead |
| Aqualish | Hutt, Deepwater |
| Arkanian | Imperial, Helix |
| Bith | Homestead, Geonosian, Helix |
| Bothan | Blackstar |
| Cathar | Wildsteam, Blackstar |
| Cerean | Homestead, Helix |
| Chagrian | Deepwater |
| Chiss | Imperial, Helix, Blackstar |
| Dathomirian | Imperial (Sith escort only) |
| Devaronian | Hutt, Blackstar |
| Duros | Homestead, Deepwater, Blackstar |
| Ewok | Wildsteam |
| Geonosian | Geonosian; Imperial prisoner pool |
| Gungan | Deepwater |
| Herglic | Hutt, Deepwater |
| Iktotchi | Homestead, Blackstar |
| Iridonian (Zabrak) | Imperial, Blackstar |
| Ithorian | Homestead, Wildsteam, Deepwater |
| Kaleesh | Blackstar |
| Kaminoan | Geonosian (gated), Helix |
| Massassi | Imperial (Sith escort only) |
| Miraluka | Homestead, Helix; Imperial prisoner pool; factionless Jedi |
| Mirialan | Homestead; factionless Jedi |
| Mon Calamari | Deepwater; Imperial prisoner pool |
| Neimoidian | Helix |
| Nikto | Hutt (Vontor caste), Deep Desert |
| Pantoran | Homestead |
| Pyke | Hutt, Geonosian |
| Quarren | Deepwater |
| Rakata | Imperial (quest only), Geonosian, Helix |
| Rodian | Hutt, Blackstar |
| Selkath | Deepwater |
| Sith | Imperial (pawn kind only) |
| Sullustan | Homestead |
| Togruta | Homestead, Wildsteam, Blackstar; factionless Jedi |
| Trandoshan | Hutt, Blackstar |
| Tusken | Deep Desert Tribes; **player-adjacent only** |
| Twi'lek | Hutt, Homestead |
| Umbaran | Imperial, Helix, Blackstar |
| Wookiee | Wildsteam Clan; Imperial prisoner pool |
| Zeltron | Hutt, Blackstar |
| Gamorrean (Pigskin) | Hutt |
| Wookiee-kin (Yttakin) | Wildsteam |
| Savant caste (Genie) | Imperial, Geonosian, Helix |
| Brute stock (Neanderthal) | Deep Desert, Geonosian, Helix labour-line |
| Desert alien (Impid) | Deep Desert |
| Baseliner human (Humanity) | Imperial, Homestead, Hutt |

Forbidden and disabled races remain unused: Force Gremlin, Chadra-Fan, Echani, Feeorin, Ishi Tib, Thyrsian.

---

## Appendix — Narrative & GM layer (salvaged from faction_dossiers.md, 2026-08-06)

The roster above is the *mechanical* spec (relations, water doctrine, pawn kinds, equipment). This appendix preserves the **authored narrative / GM-flavor layer** for the four *core* pursuit-arc factions — the pieces that lived only in the now-retired `faction_dossiers.md`. The Imperial Heat gauge and the 3-act pursuit arc themselves are canonical in `context.md` (§§889/893/895/910) and operationalized in `required_mods.md` (CQF §§222-223, pacing §§539-548, Act-II Bounty §566, Act-III blockade §572) — those are NOT repeated here; only the per-faction application flavor is.

### Emotional register (voice/tone — feeds each FactionDef `description` + namer + colorSpectrum)
- **Empire** — cold, inexorable, overwhelming-from-above. Not hateful, *procedural*: you are a logistics problem they are closing out. Hard Imperial grey/white; formal military namer.
- **Hutts** — oily, transactional, amused by your desperation. Comedy-adjacent (fits the Jawa levity layer) but with teeth. Warm sickly-gold; namer full of honorifics + shell-company suffixes.
- **Blackstar Company** — individual, competent, personal. Where the Empire is faceless ranks, a bounty hunter is *one dangerous person with a name who is coming for you*. The faction that makes the pursuit feel intimate.
- **Jawa (player)** — comedic, greedy, communal, resourceful-underdog. The heart of the campaign's levity layer (SpeakUp trade-babble). You root for them *because* they're outmatched.

### Named-leader persona sketches (draft targets for the Backstory Constructor plan, context.md §521)
- **Empire — the Moff-analog:** an orbital governor who never lands. High Shooting/Social/Intellectual; lore = the officer personally assigned your file. A *name on the Heat gauge*, rarely a body on the map until Act III. (Sits naturally on the Royalty-noble side of the fused Empire.)
- **Hutts — 1-3 named kingpins:** low Movement (they don't fight, they sit), extreme Social/Trade, disabled Violence; lore = runs the base, owns your bounty. Draft 2-3 so they can be *rivals*.
- **Blackstar Company — the guild-master:** the most-feared hunter, held for Act III at the blockade. Extreme Shooting or Melee, a signature gimmick, lore = has never lost a mark. Beating him is a personal climax nested in the corridor run. (Plus a *small stable of recurring named hunters* — each defeated-but-survived hunter can return with a grudge; highest flavor-per-effort move in the cast.)
- **Jawa — the clan chief:** high Social/Crafting, disabled Intellectual (they *tinker*, don't *research* — reinforces the no-research-ladder pillar); lore = keeper of the crashed Factory ship. The player's anchor character.

### Rejected alternative on record — "rival Hutt lords" (why the roster chose a single Confederacy)
The dossiers proposed **1-3 mutually-rival individual Hutt lords** you could "play against each other" (e.g. an old established broker vs. an upstart undercutting him — bribe one to move against the other). Rationale: *plural-but-rival lets you play the seams, which a single cartel can't.* **The roster did not adopt this** — §1 is a single "Hutt Cartel" (one decentralised faction, one boss-per-settlement) for relations-matrix and settlement-count simplicity. Recorded here so the trade-off is not silently lost: if a future revision wants inter-Hutt intrigue as a mechanic, this is the alternative and its reasoning.

### Per-faction unique hooks tied to the Heat/arc layer (lower priority, GM flavor)
- **Empire loot** = charge-tier gear + a rare **Force-artifact you can sell to the Hutts but cannot use** (player psycast ban intact). The one faction you can never buy off — unbuyability as a design statement.
- **Hutt trade raises Imperial Heat** — the market is a devil's bargain: the gear you need accelerates the pursuit hunting you. Makes every Hutt visit a real decision, not a free shop.
- **Bounty economy loop** — hunters spawn *in response to your Heat/loudness* (extract loudly, trade with Hutts, fight patrols → a hunter is dispatched), closing the loop between the Heat gauge, the Hutt bounty board, and a body on your map.
- **Trophy loot** — defeating a named hunter drops their signature weapon as a *unique, non-craftable* trophy (flavor, not an arsenal ladder). You end the run carrying the guns of the hunters who failed to catch you.

### Cast-diff vectors + loot signatures (the "no two factions swap unnoticed" forcing function)
| Axis | Empire | Hutts | Blackstar Company | Jawa |
|---|---|---|---|---|
| **Vector** | vertical (orbit/sky) | horizontal (markets) | personal (tracks *you*) | subterranean (salvage/caverns) |
| **Relation to Heat** | *is* the timer | *raises* it (trade) | *spawned by* it | *manages* it (go dark, salvage) |
| **Loot signature** | charge gear + unusable Force artifact | silver, slaves, exotic stock | unique trophy weapons | droid brains, scrap |

**Keeping Hutt underlings distinct from the Blackstar Company faction:** Hutt factions field Trandoshan/Rodian *trackers* as rank-and-file, which risks blurring into the Blackstar Company. Clean division — Hutt underlings are *disposable crew tied to a place* (defend the base, spawn in his raids, die anonymous); Blackstar Company are *named free agents tied to you* (arrive alone via the board, persistent identities, trophy weapons). Same species, different faction + narrative weight — deliberate contrast, not a collision.

## RimWorld reference

- [Modding Tutorials: Xenotypes](https://rimworldwiki.com/wiki/Modding_Tutorials/Xenotypes)
- [Ideoligion](https://rimworldwiki.com/wiki/Ideoligion)
- [Factions](https://rimworldwiki.com/wiki/Factions)
- [World generation](https://rimworldwiki.com/wiki/World_generation)
- [RimWorld 1.6 Mod Updates](https://rimworldwiki.com/wiki/Modding_Tutorials/RimWorld_1.6_Mod_Updates)

---

## THE HUTT CARTEL — casting + behaviour spec (user, 2026-08-11)

**Status:** design LOCKED by the user this session. Implementation not started
beyond dev-spawn enablers. This supersedes nothing; it fills a gap the roster
had left implicit.

### The ruling

- **The Hutts get their own planetary faction, and are ALWAYS its lords.** They
  are never rank-and-file. A Hutt on the map is a boss.
- **They appear ONLY in the Cartel.** Hutts never join, garrison or travel with
  another faction. No exceptions.
- **Never in an assault raid or ambush.** The only ways a player meets one:
  - leading a **caravan** (trade), or
  - **defending a base** the player has chosen to attack, or
  - **calling for help in a quest** — a Hutt in distress is a legitimate hook.
- **MiningCo are contract mercenaries in Cartel employ, nothing more.** This
  refines the earlier "MiningCo reflavoured as Hutt Cartel" decision: MiningCo
  is not the Cartel, it is *hired by* the Cartel. The Hutts are the principals.
- **Role, per the lore docs:** master traders, bosses, and they especially enjoy
  **torture and enslavement**.
- **They should genuinely appear in the world**, generated by the campaign's own
  rules — not merely dev-spawnable.

### Why this is more work than one pawnkind

The Cartel's entire supporting cast is currently **un-spawnable**. Of 74 Star
Wars species with a xenotype, only 43 are reachable by any pawnkind. Missing
from the game entirely, and every one of them classic Hutt retinue:

> **Gamorrean** (the guards) · **Weequay** (enforcers) · **Klatoonian** (servant
> species) · **Ugnaught** (labour) · **Zygerrian** (slavers) · Ortolan · Nikto-
> adjacent kin

Worse, most are **not ready to enable**: Gamorrean, Klatoonian, Weequay, KelDor,
Nautolan and others have a head gene whose art is absent. Only Zygerrian,
Ortolan and Lasat among the retinue candidates are currently buildable.

So "give the Hutts a faction" decomposes into:
1. pawnkinds for the lord tier (**done** — `Jawa_Spawn_Hutt`, dev-spawn only),
2. pawnkinds for the retinue (**blocked on art** for most of them),
3. a FactionDef with the Cartel's xenotype mixture,
4. behaviour constraints — excluded from raid/ambush pawn groups, present in
   trade caravans and base defence, eligible as a quest-giver in distress,
5. the MiningCo mercenary relationship.

Items 4 and 5 are the interesting design work and are not yet specified at def
level.

### Immediate state

`Jawa_Patches/Defs/PawnKindDefs/AlienSpawnEnablers.xml` makes the Hutt
dev-spawnable today, along with 11 other stranded species. Those enablers
inherit `defaultFactionType PlayerColony` from Outer Rim's test-colony parent —
**correct for dev spawning and wrong for the world.** They are scaffolding, not
the faction.

