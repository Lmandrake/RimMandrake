# RimWorld shield/forcefield mod survey — 2026-09

Queue item: `SHIELD_MODS_LEVERAGE_1`. Owner ruling: leverage existing shield mods
deeply rather than build our shield system from scratch. Design target: modulated
plasma fields tuned per threat (thermal rejection/mirror sheen, thermal
absorption/glow, light kinetic particulate screens, heavy solid bubbles that
overheat and explode when collapsed); electricity-only power; slow-moving things
pass through (canon); module-based switching capacity on ONE shield building.

Compiled from parallel web research passes (Steam Workshop, GitHub, RimWorld
wiki, forums/Reddit) on 2026-09-01/02. Steam Workshop pages are JS-rendered and
several fetches returned only nav/footer shell rather than description text —
figures sourced from Workshop *search snippets* rather than a direct page read
are marked accordingly. Nothing here has been checked against a live game;
this is desk research only.

---

## Baseline: what's already native, no mod required

### Odyssey DLC gravship shield generator (vanilla, RimWorld 1.6)
- **Building.** 3x3 footprint, 200W power draw, must sit on gravship
  substructure within 19 tiles of the grav engine.
- **Mechanic.** Activated shield covers ground *and* aerial/overhead
  projectiles, 500 HP, lasts 100 seconds or until collapsed by EMP, 25-tile
  radius, 4-hour cooldown after use. Acquired via quest/crate, not freely
  buildable from a research bench (unconfirmed whether a later unlock exists).
- **Why it matters for us:** this is the mechanic any mod-based system
  competes with or should hook into for gravship coverage. It is NOT open to
  XML patching in the usual CompProperties sense unless Ludeon exposed the comp
  publicly — treat as a Harmony-patch target, not a def-only one, until
  verified against the actual Assembly-CSharp comp.
- Source: RimWorldWiki `Gravship_shield_generator` page (via search snippet).

### Vanilla personal shield belt (apparel, all versions)
- Blocks ranged projectile damage in a small personal bubble; ignores melee
  and is vulnerable to EMP; drains on hits and recharges over time. Baseline
  only — not a mod, not part of the candidate set, cited here so it isn't
  double-counted as "leverage."

---

## Per-mod cards

### 1. Vanilla Expanded Framework (VEF) — the shared shield ENGINE
- **packageId:** `OskarPotocki.VanillaFactionsExpanded.Core`
- **1.5/1.6:** actively maintained as the dependency spine for the whole
  Vanilla Expanded line; treat as tracking current RimWorld versions.
- **Open source:** yes — github.com/Vanilla-Expanded (VEF is the shared repo;
  exact shield-engine path found: `Source/VEF/Apparels/Comps/CompShieldField.cs`,
  `CompShieldBubble.cs`, `CompShield.cs`, `CompProperties_Shield.cs`).
- **What it implements:** this is the actual shield *engine* used by every
  downstream Vanilla Expanded mod that has a shield, including VFE Security
  (card #2). `CompProperties_ShieldField` exposes radius, energy pool, power
  draw (active vs. idle/standby), and wires to `CompProperties_Explosive` for
  an EMP-type blast when the shield's energy pool is fully drained — i.e. the
  "overheat/explode when collapsed" behavior we want already exists here in a
  near-literal form. EMP interaction is hardcoded: EMP either zeroes the
  energy pool directly or disarms the shield for N ticks, and EMP damage is
  weighted 4x normal against shield energy.
- **Provenance note:** a code comment in VEF explicitly credits **Frontier
  Security's** projectile-interception method ("inspired by Frontier
  Security's method, distributed under an open-source non-profit license") —
  meaning Frontier Developments Shields (card #4) has already been absorbed
  into this engine's design. Anything using VEF's shield comps shares this one
  engine; that also means a standalone Frontier Shields install may be
  redundant with, or conflict with, anything built on VEF.
- **Moddability:** high. Radius/energy/power/EMP-multiplier are XML
  CompProperties fields; the interception math itself (per-projectile
  intercept roll, explosion parameters) is C#, so tuning numbers is
  patch-only but changing the *formula* needs a Harmony patch or fork.

### 2. Vanilla Furniture Expanded - Security (VFE Security)
- **packageId:** `VanillaExpanded.VFESecurity` (authors: Oskar Potocki,
  Sokyran, Taranchuk).
- **1.5/1.6:** About.xml lists 1.3–1.6 in `supportedVersions`, but this is
  aspirational, not confirmed-working — the current Steam Workshop listing
  (id 3622310364) is titled **"[1.6 Hack] [DEPRECATED]"** and Steam itself
  flags it incompatible; the mod is described as being rebuilt from the
  ground up for 1.6. **Treat 1.6 support as UNKNOWN/in-flux**, not confirmed.
- **Open source:** yes, MIT,
  github.com/Vanilla-Expanded/VanillaFurnitureExpanded-Security (an older
  community fork also exists at AndroidQuazar/VanillaFurnitureExpanded-Security).
- **What it implements — changed shape in 1.6, important:** the 1.4/1.5
  branches ship a classic `Buildings_ShieldGenerator.xml` (small/large/
  archotech shield generator ThingDefs) — but **the 1.6 branch has removed
  that file entirely**, replacing it with `Buildings_Repulsors.xml`
  (`VFES_SmallRepulsor` / `VFES_LargeRepulsor`) plus a new `CompPointDefense.cs`.
  Two separate mechanisms now exist side by side:
  - **Repulsors** (dome shield): built on VEF's `CompProperties_ShieldField`.
    Radius 5.9 / 16.9 tiles (small/large), energy pool 36 / 28, power draw
    2900W / 5000W while active, 300W idle/standby; only auto-activates during
    an active threat. EMP bypasses/drains it fast; depletion can trigger an
    explosion (same `CompProperties_Explosive` EMP-type wiring as VEF, same
    radius as the shield) — this directly matches our "overheat/explode on
    collapse" design beat.
  - **Point-defense turrets** (`CompPointDefense`): a *separate* mechanic, not
    a passive bubble — a turret comp on `Building_TurretGun` that actively
    shoots down individual incoming projectiles and drop pods within a
    radius, fuel-consuming, with an intercept-chance formula keyed to
    projectile *speed*. Per this pass's finding, **slower projectiles are
    intercepted more reliably** in this system — the inverse of what our
    canon wants ("slow-moving things pass through" shields). If we lean on
    this comp, the speed-vs-intercept curve needs inverting or replacing, not
    just re-tuned.
- **Moddability:** high for the Repulsor bubble (XML CompProperties, shares
  VEF's engine); point-defense intercept math and EMP rules are hardcoded C#
  (`blacklistedProjectileDefs` list is XML-exposed, but the chance formula is
  not) — fork/patch required to change the formula itself.
- **Odyssey/gravship compatibility:** UNKNOWN. No direct compatibility report
  found for VFES repulsors vs. the native gravship shield generator (stacking,
  conflict, or double-coverage). Steam discussion threads surfaced instead
  describe unrelated pre-1.6 bugs (1 FPS on shuttle arrival, shields failing
  to stop drop pods) that predate the repulsor rewrite and may not reflect
  current code.

### 3. Frontier Developments Shields (historical; several forks)
- **Lineage:** original `rimworld-frontierdevelopment/Shields` (MIT), with
  community continuations at github.com/emipa606/ShieldGeneratorsByFrontierDevelopments
  ("Continued"), plus rizay, subitan, and JonnyNova forks — one codebase
  lineage, not independent mods.
- **1.5/1.6:** no confirmed 1.6 support found; last clearly-dated activity
  found was ~2020-2021. Some listing sites show a version range of "1.3-1.6"
  but this reads as an unverified aggregator tag, not a changelog confirmation.
- **Open source:** yes, MIT.
- **What it implements:** three shield-generator tiers with 3m / 3-10m /
  5-25m radius domes. Blocks bullets, rockets, mortars, drop pods, and
  meteorites; pawns, fire, SRTS, and trader ships pass through (a rough
  precedent for our "slow-moving things pass through" rule, though the
  pass-through set here is by *thing type*, not by speed threshold — worth
  checking exactly how "slow" is defined if we study this further). Heat-based
  overheat leads to shutdown; low idle power draw, high draw while
  intercepting; effective strength is tied to the battery capacity available
  on the connected powernet. Reported Combat Extended-compatible ("just
  works" — CE reportedly overhauled its own area-shield interception to
  cooperate).
- **Moddability:** CompProperties-based, not hardcoded — patchable.
- **Leverage note:** since VEF's own shield engine explicitly credits this
  mod's method as its inspiration, running a standalone Frontier Shields
  install *alongside* anything VEF/VFES-based risks redundant or conflicting
  projectile-interception claims on the same target. Best treated as a
  **historical reference for the heat/overheat and radius-tier design**, not
  a mod to run alongside our build.

### 4. ED-Shields / "ED-Shields (Continued)"
- **Repo:** github.com/jaxxa/ED-Shields (MIT). Steam Workshop continuation:
  id 2566443779.
- **1.5/1.6:** UNKNOWN — a Continued fork exists (evidence of ongoing
  community maintenance) but explicit 1.6 version confirmation was not found
  in this pass.
- **Open source:** yes, MIT.
- **What it implements:** rebuilt around Comps since a v2.0 rework (the
  README itself frames this as "Comps instead of custom C# ThingDefs," i.e.
  a deliberate moddability improvement). Strength = damage capacity, Radius =
  area of effect; blocks bullets, mortars, and other indirect fire. A
  "Vertical Projector" module specifically targets drop pods, causing a
  violent drop-pod crash rather than a clean intercept; a "Horizontal
  Projector" module extends the shield's radius; a "Power Converter" module
  allows degraded operation when off the power grid. No explicit heat/
  overheat model was found documented in the README.
- **Moddability:** high — Comp-based by explicit design intent.
- **Leverage note:** the module set (Vertical/Horizontal Projector, Power
  Converter as pluggable attachments changing one generator's behavior) is
  the closest precedent found anywhere in this survey for our **"module-based
  switching capacity on ONE shield building"** requirement. Worth a close
  read even though version support is unconfirmed.

### 5. Shield Expanded (newer mod, author's first RimWorld mod)
- **Steam Workshop id:** 3575073524.
- **1.5/1.6:** UNKNOWN precisely, but recency (author states this is a first
  mod, and it appears in current-era search results) suggests 1.5/1.6-era
  targeting; not independently confirmed.
- **Open source:** not surfaced in this pass — UNKNOWN/needs direct check.
- **What it implements:** a shield *network* — shields, "server" units, and
  control terminals as separate buildings — rewritten around
  `CompProjectileInterceptor` with a custom `ShieldNet` indexed by the
  building's `PowerNet`. Can reportedly be configured to intercept-and-prevent
  the resulting explosion. Also ships separate shield-belt apparel resisting
  specific damage types. Author is described as actively refactoring the mod
  for maintainability (i.e. still live).
- **Moddability:** likely comp-based (uses vanilla's own
  `CompProjectileInterceptor` base rather than a from-scratch interception
  system) — plausibly easier to patch/extend than a fully custom engine, but
  unverified without reading the actual source.
- **Leverage note:** the networked-generator + control-terminal shape is
  close to our "module-based switching" ask at the base-building scale (as
  opposed to ED-Shields' single-building-with-attachments shape). A good
  second candidate for a direct compatibility test.

### 6. Gravship-specific shield mods (compete for the same Odyssey slot)
- **"Shield Generator"** (Steam id 3591079938) — wall-mounted generator
  built specifically for gravships. Auto-activates on threat detection,
  color/transparency customizable, blocks all projectiles except "Graser
  Beams," and shatters with a large in-room EMP explosion on full battery
  drain (another close match to our overheat/explode design beat). Its own
  page explicitly states it is **not Combat Extended-compatible and "won't
  ever be."** Open-source status: UNKNOWN.
- **"Powerful Gravship Shield Generator"** (Steam id 3524963393) — appears to
  buff the *vanilla* gravship shield comp directly (infinite-power
  activation, longer charge) rather than add a new building; its own Workshop
  page currently flags it as incompatible/needing a fix. Open-source status:
  UNKNOWN.
- **Leverage note:** both are evidence that hooking/extending the native
  Odyssey comp (rather than building a fully separate shield engine) is a
  well-trodden path other modders have already taken for the gravship slot
  specifically — useful precedent even without source access.

### 7. Save Our Ship 2 (SoS2) — ship hull shields
- **1.5/1.6:** 1.5 support confirmed ("SOS2.7 ... for 1.5 and beyond");
  explicit 1.6 confirmation UNKNOWN from this pass — needs a direct Workshop
  page read.
- **Open source:** yes, but fragmented — no single canonical repo found.
  Active forks located: copeland3300/SaveOurShip2, KentHaeger/SaveOurShip2,
  tinygrox/SaveOurShip2. (spdskatr appears to be an early
  tooling/RWModdingResources contributor, not the current maintainer of a
  single canonical repo, contrary to the initial assumption going into this
  research.) License text itself not independently verified.
- **What it implements:** ship shields absorb incoming projectile energy and
  this generates **heat** — heat/radiation management is a core mod theme
  (reactors and shields both strain the ship and crew, can ignite
  compartments on overload). This is thematically close to our
  "thermal absorption glowing red-orange" design beat. Point-defense is a
  **separate** mechanic from the hull shield: point-defense-mode lasers
  intercept incoming torpedoes, which travel as visibly slow triangles on the
  map — i.e. shield coverage and point-defense are two independent systems in
  SoS2, not one comp.
- **Dependencies:** requires Harmony + Vehicle Framework.
- **Moddability/specifics:** exact power draw, bubble radius, and hull
  integration mechanics were not surfaced at search-snippet depth — UNKNOWN,
  would need a direct source read.
- **Leverage note:** relevant almost entirely for its **heat-as-consequence**
  framing (shield absorption -> heat -> ship-wide risk), which maps onto our
  "thermal absorption glowing red-orange" concept better than any other mod
  surveyed. Ship-hull-specific mechanics and its Vehicle Framework dependency
  make it a poor fit to run alongside a base/gravship-building shield system.

### 8. Combat Extended (CE) and "Combat Extended: Shields"
- CE core itself does **not** add a hull/ship or building-scale shield
  mechanic — it changes global ballistics (armor penetration, miss chance,
  etc.) that any shield mod's projectiles pass through. CE core is open
  source (github: CombatExtended-Continued/CombatExtended), with a public
  Compatibility-Patch-Guide wiki page.
- Shield-specific behavior lives in a separate addon, **"Combat Extended:
  Shields"** (Steam Workshop id 1586351220, plus a "Lite Patch" compat/
  rebalance variant). This adds **personal/vehicle shield-belt-style items
  across historical eras** (Zulu Nguni shield, Persian wicker shield, a
  modern "Assault Shield") — i.e. melee/personal equipment, not
  building-scale forcefields. **Different category from what our design
  needs.** Addon's own repo/license: UNKNOWN, not surfaced.
- Frontier Developments Shields (card #3) is separately reported CE-compatible
  by its own listing.
- **Leverage note:** low relevance to a base/ship shield *building* — useful
  only as a source of CE-interaction patterns if we ever need our shield
  building to cooperate with CE's ballistics model.

### 9. "MIM WH40k" series / Ancot
- **Ancot** turns out to be a xenotype/race modder (Milira, Wolfein, Crowju
  xenotypes) — **not** a shield-mod author. Likely conflated in the original
  brief with "MIM," a different author/series. Treat the "Ancot" lead as a
  mismatch.
- **MIM — Warhammer 40k series**: a modular collection (Core library + per-
  faction packs: Adeptus Astartes, Orks, Chaos, Armors, Weapons, Ideology).
  "MIM - WH40k Core" is a shared dependency library with no standalone
  function of its own. **No confirmed void-shield/energy-shield generator
  building was found** in search snippets for this series — packageId,
  GitHub repo, and exact shield mechanics are all **UNKNOWN**. Workshop pages
  for this series returned only JS-rendered nav shell on fetch, not
  description text, so this is a genuine gap, not a considered "no."
- **Leverage note:** needs a direct Workshop page read (or in-game
  inspection of an installed copy) before any conclusion — do not treat the
  absence of a hit as confirmation there's no void-shield mechanic here.

### 10. Not found / ruled out
- **"Simple Utilities: Shields"** — does not appear to exist under this or a
  close variant name. Not found.
- **Dubs (any shield product)** — no standalone Dubs shield mod found; the
  one promising search hit turned out to describe Frontier Developments'
  own stress/plasma-heat mechanic, not a Dubs product. Not found.

### 11. Located but not examined in depth (flagged for follow-up only)
- **Spacer Shields 1.6** (Steam ids 3536995307, older base 3269174665) —
  "Power Pavise" (heavy, melee+ranged) and "Force Buckler" (portable
  repulsor). No public GitHub found.
- **Reverse Engineered Mechanoid Shields**
  (github.com/GeodesicDragon/rimworld-rems) — mechanoid-style shield mod,
  open source.
- **Combat Shields (Continued)** (github.com/emipa606/CombatShields) —
  historical/melee shield *objects* (e.g. a Nguni shield), Simple Sidearms
  compatible, open source, actively maintained via emipa606's Continued-mod
  pipeline. Different category (melee weapon-shields, not forcefields).
- **EnergyShield** — described as an "infinitely upgradable" energy shield
  tech tree resisting bullets/mortars/airdrops/explosions. Found via
  Reddit/discussion search only; not confirmed for 1.6; no GitHub link
  surfaced. UNKNOWN.
- **Eccentric Tech - Advanced Shields** — advanced shield belts; search
  snippet confirmed only up to 1.5. 1.6 support UNKNOWN.
- **Toggleable Shields Continued** — a QoL toggle layer sitting over other
  shield-belt mods; not itself a shield implementation.
- **"Vanilla Expanded Shields Fix"** (Steam id 2844928074) — its mere
  existence is evidence that Vanilla Expanded's own shield system has had
  known bugs serious enough to warrant a third-party fix mod; worth reading
  if we build on the VEF engine (card #1).
- **"Shields, Shields. SHIELDS!"**, **"Plasma Shield Implant"** (personal/
  animal implant shield, blocks melee not ranged), **"Shield Expansion"**
  (Steam id 3778744771) — located, not examined.

---

## Shortlist — ranked for our leverage

1. **STUDY DEEP (primary engine to build on):** Vanilla Expanded Framework's
   `CompShieldField` / `CompProperties_Shield` (card #1), as expressed in VFE
   Security's 1.6 Repulsor buildings (card #2). MIT-licensed, actively
   maintained, already implements energy-pool drain -> EMP-triggered
   explosion (our "overheat/explode on collapse" beat) via XML-tunable
   CompProperties. This is the strongest fork/extend candidate found. Caveat:
   VFES's own 1.6 status is currently flagged incompatible/rebuilt, and the
   companion point-defense comp's speed-vs-intercept curve runs backwards
   from our "slow things pass through" canon and would need inverting, not
   reusing as-is.

2. **STUDY (native precedent, hook don't duplicate):** Odyssey's native
   gravship shield generator, plus the two Steam mods that already hook that
   same slot — "Shield Generator" (id 3591079938) and "Powerful Gravship
   Shield Generator" (id 3524963393). Confirms extending the vanilla comp is
   a proven path for gravship-scale coverage; source access to either
   third-party mod is unconfirmed, so this may end up disassembly/Harmony
   work rather than a clean fork.

3. **STUDY (best module-architecture precedent):** ED-Shields (card #4) for
   its Vertical/Horizontal Projector + Power Converter module pattern — the
   closest match anywhere in this survey to "module-based switching capacity
   on ONE shield building." Version support unconfirmed; read the source
   regardless of whether we run it live.

4. **RUN-ALONGSIDE CANDIDATE (test compatibility):** Shield Expanded (card
   #5) — newer, actively developed, already close to a networked
   generator+terminal shape; worth an actual install-and-test pass before
   committing design decisions around it.

5. **STUDY, HISTORICAL ONLY (do not run alongside VEF-based work):** Frontier
   Developments Shields (card #3) — its method is already folded into VEF's
   engine per VEF's own code comments, so running it alongside anything
   VEF/VFES-based risks duplicate/conflicting projectile-interception claims
   on the same target. Keep for its heat/overheat and tiered-radius framing
   only.

6. **STUDY, THEMATIC ONLY:** Save Our Ship 2 (card #7) for its
   shield-absorption-generates-heat framing, which is the best match found
   for our "thermal absorption glowing red-orange" beat — but its
   ship-hull/Vehicle-Framework-specific mechanics make it unsuitable to run
   alongside a base/gravship building system.

7. **DEPRIORITIZE / SKIP:** "Combat Extended: Shields" addon (personal/
   historical shield items, wrong category entirely); MIM WH40k series
   (insufficient verified information — a real gap, not a ruled-out "no");
   Dubs and "Simple Utilities: Shields" (not found — likely don't exist).

---

## UNKNOWN items requiring a follow-up pass (not resolved in this survey)

- VFE Security 1.6 Repulsor compatibility with the native Odyssey gravship
  shield generator (stacking, conflict, double-coverage) — no report found
  either way.
- MIM WH40k series: whether any pack in the collection ships a void-shield/
  energy-shield generator building at all; packageId, GitHub repo, mechanics
  all unverified (Workshop pages returned only nav shell on fetch).
- Explicit RimWorld 1.6 support confirmation (not just an aggregator's
  version-range tag) for: Frontier Developments Shields/forks, ED-Shields
  (Continued), Shield Expanded, Save Our Ship 2, EnergyShield, Eccentric Tech
  - Advanced Shields.
  Open-source/license status for: Shield Expanded, "Shield Generator" (id
  3591079938), "Powerful Gravship Shield Generator" (id 3524963393), Spacer
  Shields, "Combat Extended: Shields" addon.
- SoS2 ship-shield numeric specifics (power draw, bubble radius, exact hull
  integration) — not surfaced at search-snippet depth; needs a direct source
  read of one of the current forks (copeland3300, KentHaeger, or tinygrox).
- Whether VFE Security's point-defense intercept-by-speed formula is
  correctly characterized as "slower = more interceptable" versus a possible
  misreading of the source in this pass — worth a direct code read before
  relying on the finding to rule the comp out.

This survey used WebSearch/WebFetch only; several Steam Workshop pages
returned JS-rendered shells rather than description text on fetch, so
Workshop-sourced specifics above are search-snippet-derived unless a GitHub
source file is cited directly. No local files, mod list, or game state were
touched in producing this report.
