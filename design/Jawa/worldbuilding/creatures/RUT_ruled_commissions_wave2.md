<!-- status: design brief — nothing here is built except where a row says so -->
# The ruled commissions, wave 2 — seven creatures from the 2026-09-10 sitting

_Design brief, 2026-09-10, Fable pass (backgrounded from BENCH per
`infrastructure/agents/Agent_Policy.md`). This doc **specifies**: no XML, no C#, no art
generation. Format precedent: `creatures/RUT_hydrocarbon_ecology_commission.md` and
`creatures/goo_boom_commission.md` (the vhessk). Every rule INVENTED here rather than
derived from a ruling, sheet law, or measurement is flagged **[INVENTED]**._

**The commissions, as ruled (owner sitting 2026-09-10, recorded in
`review/round2/biome_findings.md` and `review/round2/decisions_propagated.json`):**

- nightside_ice (VISITOR LAW RULED line): *"NEEDS-MORE fills from the sheet's own
  unbuilt natives, COMMISSIONED: tunneler warren creature, inclusion-insect swarm,
  aurora-current feeder."*
- the_rust_cathedral (sitting line): *"COMMISSIONS ruled: mechanical cockroach + the
  little gear-like dancing creatures (to be made); organic cockroach already resident
  (Ling_Cockroach)."*
- the_pyrelands (RULED fire-web repopulation): *"COMMISSIONED: the fire-hawk (flier
  roster — carries burning twigs, flushes prey) and the furnace-beast (heat-banking
  migratory megafauna) — the two irreplaceable igniters. RECAST: Razorjack arrives as
  the fire-follower (flame-edge hunter); Barbslinger routed here as the ash-grazer."*

⚠️ **Build-state note, read first:** the two Pyrelands igniters were built as v1 defs by
FOUNDRY *during this same day* — `RUT_FireHawk` and `RUT_FurnaceBeast` exist in
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml` (working
tree, uncommitted at this writing) with real art, and the roster rows record it. §7/§8
are therefore the **mechanics-and-reconciliation briefs those defs still owe**, not
greenfield designs; nothing in this doc asks anyone to redo what stands. The other five
creatures have no def anywhere (checked: no RUT_ collision in `design/` or `src/`).

All defNames `RUT_` tier (`design/NAMING_SCHEME_PLAN.md` — endemic campaign content);
coined names per `Alien_Bestiary.md` §1 (opaque 1–2 syllable names, nickname carries
the warning); sheet-coined English names kept verbatim under the bladderboil precedent
(the owner's/sheet's own coinage outranks the bestiary default).

---

## 0. At a glance

| # | ruled seed | name | biome | engine shape | § |
|---|---|---|---|---|---|
| 1 | tunneler warren creature | **vhorr** (`RUT_Vhorr`) | nightside_ice | warren Building (Hive/CompSpawnerPawn pattern) + burst incident | §2 |
| 2 | inclusion-insect swarm | **chittik** (`RUT_Chittik`) | nightside_ice | event-spawned swarm pawn, dormant-by-absence | §3 |
| 3 | aurora-current feeder | **ilverr** (`RUT_Ilverr`) | nightside_ice | near-sessile giant ribbon pawn, spd ≤0.6 | §4 |
| 4 | mechanical cockroach | **deckroach** (`RUT_Deckroach`) | the_rust_cathedral | NEW mech-analog animal def (not a reskin, not a Mechanoid) | §5 |
| 5 | gear-like dancing creatures | **living bolt** (`RUT_LivingBolt`) | the_rust_cathedral | the sheet's ruled living bolts made a def — ONE species, not two | §6 |
| 6 | fire-hawk | `RUT_FireHawk` (BUILT) | the_pyrelands (flier roster) | mechanics brief: twig-carrying fire spread | §7 |
| 7 | furnace-beast | `RUT_FurnaceBeast` (BUILT) | the_pyrelands | mechanics brief: heat aura, bed-down ignition, ban-5 audit | §8 |
| R1 | Razorjack recast | `AA_Razorjack` | the_pyrelands | fire-follower recast — biome lists + story, no def surgery | §9a |
| R2 | Barbslinger routing | `AA_Barbslinger` | the_pyrelands | ash-grazer routing — one contradiction to verify | §9b |

---

# Part A — the Nightside Ice trio

## 1. The shared law, cited once

Every brief below is audited against `nightside_ice.md` (FROZEN) rather than restating
it per-creature:

- **§4 first pass (verbatim-protected):** life catalyses and waits; sessile, laminar,
  enormous; the one-move animal; **sensing is thermal, and only thermal** — the
  player's heating is the threat generator; reproduction by fragment and contact;
  nothing warm-blooded, nothing fast. **§6:** no bioluminescence in surface residents,
  no vision/sound/vibration sense, no flocking/fleeing surface fauna, no ordinary
  creature silhouettes — *"if a player can tell it is a creature before it acts, it is
  wrong for this biome."*
- **§3 dirty ice:** impure ice flows, holds inclusions, and delivers them violently;
  🔑 **the thaw pulse is the disaster** — warmth (a reconnection storm, a machine,
  **your own base**) softens dirty ice and releases what it held.
- **The visitor law (owner ruling 2026-09-10, `biome_findings.md` nightside section):**
  Tauntaun (margin herds straying in), Wampa and Jakobeast (following them) are
  **VISITORS-AND-DYING, never native** — low commonality, riding §4's own clause
  ("anything warm on the nightside is a visitor, a machine, or dying"). Visitors hunt
  by starlight/aurora and are exempt from thermal-only; **every straying herd is a
  walking thermal beacon that ends as a tunneler-warren event.** The trio below is the
  other half of that ruling: the natives the warm bodies feed.
- **All natives get the thermal-only sensing line** in their description (the ruling's
  own phrasing, applied to ShockGoat and CaveLemming at their refashion; applied here
  from birth).
- Palette: `palettes/biome_palette_anchors.json` nightside_ice — family
  `#10141f → #ccd6de`, accent `#4fd6a0` aurora-green ("in the pans and nowhere else,
  the shockingly clean saturated chemistry colour"); **banned: warm light of any
  kind.** Fauna defers to the family; nothing below claims the pan accent.

**The food web this trio closes** (assembly of ruled parts): the sky feeds nothing
here — the feed is *what strays and what falls*. Visitors die → the vhorr take them
(§2). The ice holds the dead and the small life of its bubbles → the thaw pulse
releases both (§3). The aurora's ground currents are the one standing energy income
(§2 second-pass: "what the aurora's ground currents deliver") → the ilverr farms it
(§4). Three natives, three ruled energy routes, zero invented ones.

## 2. The vhorr — the tunneler warren creature

The §4 second-pass archetype, verbatim, is the spec: *"the naked-mole-rat analog:
blind, thermal-sensing, moving within the dirty ice where nothing on the surface ever
sees it, feeding on what little arrives — which is the lost. A body dying on the
plateau is a warm signal in the ice; the tunnelers come to it from below.
**Surfacing is the burst.** Colonial, clonal, one warren per pan-margin. A threat to
the dying, and — through a thaw pulse — to a camp that has made itself warm."*

### 2a. Name and flavor

| field | value |
|---|---|
| defName / label | `RUT_Vhorr` / `vhorr` |
| nickname | "the undertakers" — salvager slang for what comes when something on the plateau stops being able to keep itself warm |
| name grammar | `vh-` initial — the bestiary's whisper register (`Alien_Bestiary.md` §1 rule: apex/dread names people say from a distance); one syllable, terminal doubled -rr (the biggest SW tell). Collision-swept: vhaal / vhessk / vhaggan all differ in final consonant |

**Description (player-facing, salvager register — carries the thermal-only line):**

> Nobody has seen a whole one and lived curious. What the ice gives up in a slab-fall
> is pale, jointless lengths of it, blind as the ice itself. It feels one thing only —
> warmth — and it is patient about it: a warren works toward a dying camp for days,
> under the ice, in no hurry, because on this plateau warmth never gets better. It gets
> slower. The margin folk do not bury their dead here. They say the ground already
> knows.

### 2b. The engine decision — warren as Building, burst as incident

The commission's own question, answered honestly across the three routes:

- **The warren: the Hive precedent, taken.** Vanilla infestation Hives are Buildings
  carrying `CompSpawnerPawn` (verified: `Source/RimWorld/Hive.cs`,
  `CompSpawnerPawn.SpawnPawnsUntilPoints` — spawns defenders up to a points budget).
  A **warren-mouth Building** on pan-margin ice, spawning vhorr pawns when
  provoked, is that pattern reskinned — full precedent, no invented machinery. The
  mech-cluster route (hostile verb-buildings) is rejected: a warren does not shoot;
  it *produces*, which is exactly what the Hive class is for.
- **The burst: the infestation incident is ALREADY the mechanic, inverted by climate.**
  Vanilla `InfestationCellFinder` (verified, lines 79–95) refuses cells below
  −17 °C and scores candidate cells by warmth (`InverseLerp(-17, -7)`) — vanilla
  infestation literally spawns underground colonies toward heat. On a −45 °C map that
  incident can never fire — **unless the player heats something.** A small C# incident
  worker cribbing that scoring with retuned thresholds makes the sheet's law
  mechanical for free: *the player's heated base creates the only eligible burst cells
  on the map.* Thermal-sensing as targeting falls out of the cell-scorer; no
  per-pawn thermal AI needed for v1. (The roster's logged `C#: within-ice movement +
  thaw-pulse surfacing` is this — scoped down from "movement inside ice," which the
  engine cannot render anyway: nothing on the surface ever sees them, saith the
  sheet, and the engine agrees.)
- **Simple pack spawn: rejected** — a wild wandering vhorr pack on the surface
  violates §6 (no pursuing surface fauna) and wastes the archetype. The vhorr is
  never ambient. It *arrives*, at warmth, from below.

### 2c. Behavior and numbers

| aspect | spec |
|---|---|
| the three triggers | (1) the **lost soul** event (§4b): the dying traveler's warmth draws a burst near them on a timer — save them before the ground does; (2) the **thaw pulse** (§4b): warrens near the softened ice surface early; (3) the **standing base check**: a heated structure on this biome rolls burst events the way vanilla rolls infestations — insulate and run cold, and nothing ever comes (§4's strategic tension, made literal) |
| the individual | pale segmented burrower, bodySize ~0.6 **[INVENTED]**, slow on the surface (spd ~2.5 — surfaced vhorr are out of their element **[INVENTED]**), melee bite; blind — no ranged anything |
| the warren | warren-mouth Building spawns 3–8 per burst by points **[INVENTED counts]**; killable; collapsing the mouth ends the event. One warren per pan-margin (§4 second pass, verbatim) — placement rare, margins only, never the interior |
| clonal law | §4: populations are clonal and strictly local — every vhorr from one warren is one lineage; no breeding mechanic, `CompSpawnerPawn` IS the reproduction (contact-and-fragment, honored by construction) |
| products | butchery: nothing edible — a catalyst-chemistry body is not food (§7: "not food, not water… ⚠️"); zero meat, zero leather, mirror the vhessk explicit-zero convention **[applied by choice; the sheet rules the biome yields no food, not the butchery table]** |
| admission audit | §6 pass: no eyes, thermal-only, never flocks on the surface (it has no surface life), not warm-blooded (it seeks warmth precisely because it has none — **[INVENTED framing, anchored on §4 "nothing here is warm-blooded"]**); silhouette only ever seen as a burst — the player cannot tell it is a creature before it acts, which is §9's art rule scored as gameplay |

### 2d. Art direction

Palette family only — bone-pale lengths against `#10141f` ice-dark; **no glow** (§6).
The identity image is not the creature but the **burst**: broken slab, dark hole,
pale movement. Sprite reads at review distance as "something the ice should not have
let out." One body sprite (they are clonal — identical is correct here, the 200-instance
repetition rule works FOR us); the warren-mouth gets the second sprite.

## 3. The chittik — the inclusion-insect swarm

The §4 second-pass line, verbatim: *"Icy insects — the small life of the inclusions:
things that live in the bubbles and mineral veins of dirty ice, active only in a thaw
pulse, dormant otherwise. Harmless individually; a slumping slab full of them is not."*

### 3a. Name and flavor

| field | value |
|---|---|
| defName / label | `RUT_Chittik` / `chittik` |
| nickname | "slab-fleas" — margin slang; a slab that got warm "has fleas" |
| name grammar | doubled -tt-, `-ik` small-quick vermin clade (`Alien_Bestiary.md` §1); collision-swept: skerrik (propane lakebed) shares the clade ENDING only and deliberately not the `karr-`/`-rrik` chitin morpheme — different biome, different chemistry, no implied kinship. `sissik` (a §1 example name) differs in both initial and internal consonant |

**Description (player-facing — carries the thermal-only line):**

> Dirty ice is full of bubbles, and the bubbles are full of these. Frozen, they are
> mineral flecks; nobody has ever picked one out of clean ice. Warm the ice and they
> remember what they are: a fingernail of legs and appetite that feels heat and
> nothing else. One is a curiosity. A slumping slab is a season's worth of them, all
> waking hungry at once, and every warm thing nearby is the only candle in the dark.

### 3b. The engine decision — dormant-by-absence, honest about what dormancy can do

**What exists:** vanilla `CompCanBeDormant` (verified:
`Source/RimWorld/CompCanBeDormant.cs`) is the mech-cluster dormancy machinery — but
its wake triggers are proximity/damage/signal, **not temperature**; and the donor pool
carries a measured dormancy special across many register rows (the roster's own
`dormant-until-thaw comp (donor mechanic exists)` line and prep §7.4's "borrow the
107-row dormancy comp"). **What does not exist:** a vanilla route for pawns embedded
invisibly inside terrain.

**The recommended v1 cuts the knot: the chittik is never ON the map while dormant.**
Dormancy is modeled as absence — the fiction says they are in the ice; the engine
says nothing exists yet. They enter play only as **event spawns**:

- **Thaw pulse** (§4b, the biome's ruled disaster): the pulse spawns chittik swarms
  from affected ice cells — the manhunter-pack incident pattern with a local spawn
  origin, briefly frenzied, dying back to torpor (despawn or downed-torpid) as the
  cold reasserts **[INVENTED: the frenzy-then-torpor curve]**.
- **Calving delivery** (§4b): a delivered slab has a chance to carry a small swarm.
- **The player's own heat**: a base structure warming ice cells rolls a small chittik
  wake the way §2c rolls a vhorr burst — same C# incident worker, second consumer,
  one spike serves both **[design economy, flagged]**.

This honors "active only in a thaw pulse, dormant otherwise" to the letter, keeps the
biome's standing map near-empty (owner card: near-empty is correct), and costs one
incident hook instead of a terrain-embedding system. `CompCanBeDormant` remains the
fallback if a later pass wants visible torpid swarms lying in slab-fall debris —
usable from XML on the spawned pawns, wake-on-damage for free.

### 3c. Numbers, audit, art

| aspect | spec |
|---|---|
| the individual | vermin-class: bodySize ~0.1, tiny bite, spd ~3.5 while warm **[INVENTED — fast-while-warm is lawful: §6 bans fast SURFACE fauna as residents; the chittik's active state exists only inside the disaster window, the same carve-out the burst itself rides — flagged for the owner regardless]** |
| the swarm | spawns in packs of 10–20 **[INVENTED]**; harmless singly (per the sheet, verbatim), lethal in aggregate to the unarmored |
| counterplay | fire and heat kill them fastest — and every heat source used is a beacon for the vhorr (§2): the biome's two threats chain, and the player chooses which to feed **[INVENTED interaction, anchored on both ruled mechanisms]** |
| products | none; too small to butcher (vermin convention) |
| admission audit | §6: no eyes, thermal-only, no flocking RESIDENTS (event-scoped), not warm-blooded, no nameable Earth silhouette (mineral-fleck body, legs only visible warm) |
| art | mineral grey-glint bodies inside the ice family values; the swarm reads as the ice itself crawling — motes/flecks over a slumped slab, not individual sprites at zoom |

## 4. The ilverr — the aurora-current feeder

The commission makes §2's second-pass energy ruling flesh: *"what arrives is what the
atmosphere carries in, and what the aurora's ground currents deliver."* The electrojet
physics is already canon (`the_propane_lakes.md` §3/§7 — the ruled ground-induced
currents the tap harvests, "weaker here than at the pole" per this sheet's §7). The
ilverr is the organism that got there first — the same claim shape the aviir made for
the lake, expressed in the uplands' sessile register.

### 4a. Name and flavor

| field | value |
|---|---|
| defName / label | `RUT_Ilverr` / `ilverr` |
| nickname | "witch-fence" — traveler slang for a faint line of light lying across dark ice where no line should be |
| name grammar | vowel-led and soft (the drifting-beauty register the fish commission refined), two syllables, terminal doubled -rr; collision-swept (no il-/ilv- morpheme in any register) |

**Description (player-facing — carries the thermal-only line):**

> A seam of faint green light, laid across the ice for a hundred meters, not moving —
> or moving the way a glacier moves. It is a single organism: a flat braided ribbon
> pressed into the ground along the lines where the aurora's currents run, drinking
> the sky's electricity the way roots drink water. It senses warmth and nothing else,
> and it wants nothing from you. Travelers steer by them, when there are any to steer
> by, and are grateful and uneasy in equal parts, because a fence means a farmer.

### 4b. The design — and the one reconciliation it needs

| aspect | spec |
|---|---|
| body plan | §4 taken literally: a **sheet-organism** — a flat braided ribbon, tens of meters in fiction, a multi-cell giant in engine terms (bodySize in the landform band beside AA_SummitCrab's 15 **[INVENTED: ~8]**; drawSize long and thin). Laminar, pressed into the boundary layer — the sheet's own body-plan sentence is the art order |
| movement | spd 0.5 **[INVENTED — inside the roster's own imported precedent: TetraSlug 0.6, "barely moving"]** — it relocates along its current seam over days; it never pursues, flees, or reacts to anything but a warm body close enough to matter (retaliation-only melee, weak) |
| energy | the ruled ground currents, farmed directly — the only native with a standing income, which is why it is the only native VISIBLE: it can afford to be. Everything else here lives on savings (§4); the ilverr lives on a salary **[INVENTED framing; both energy facts are ruled]** |
| 🔴 the visibility reconciliation | §6 bans **bioluminescence** in surface residents — "a seam metabolism cannot afford photons." The ilverr's light is argued as lawful because it is **not metabolic light**: it is corona discharge — leakage of the aurora's own current across the ribbon's wet-frost surface, spent from the sky's budget, not the body's. The precedent is the owner's OWN ruling on the same sitting: AA_ShockGoat arrives as a native with a "pale blue aura" (decisions register, owner's words) — an electrical glow ruled INTO a biome whose residents may not glow chemically. Same physics, same register. ⚠️ **Flagged as an owner call regardless (§11 Q1): the ban is frozen, and this is a reading, not an amendment** |
| aurora coupling | brightness follows the sky: dim under quiet stars, bright and rippling under a reconnection storm (§4b: "the electrojet tap over-produces" — so does the ilverr). v1 ships this painted/description-level; a real brightness tie is the same CompGlower-on-a-timer question the twinkle spike owns (TWINKLE_FLORA_SPIKE_1) — ride its verdict, never promised here |
| role in play | landmark navigation (the uplands' palespire); a legible SAFE line in a biome whose every other light is a warning — and bait for nothing: it is the one thing on the plateau that will never come toward you |
| products | none designed. Its charge-bearing tissue is deliberately NOT an item: the tap-crystal component slot is the aviir shard's (`RUT_hydrocarbon_ecology_commission.md` §14d) and a second electrical harvest would duplicate it — the same one-system discipline that folded the skerrik's chitin |
| admission audit | §6: sessile-laminar ✓, no eyes ✓, thermal-only ✓, enormous ✓, indistinguishable-from-landform ✓ (a line of frost-glow IS landform until told — §9's art rule); the glow is the one flagged reading |

### 4c. Art direction

The family's dark steps for the ribbon body (frost-grey braid, barely raised); the
corona a **desaturated aurora-green within the ambient register** (`#4fd6a0` family at
LOW saturation) — deliberately below the pans' saturated chemistry accent, which keeps
its monopoly. At map zoom the ilverr is a thin luminous line with direction; that
read — *a fence across the night* — is the whole sprite brief.

---

# Part B — the Rust Cathedral pair

Shared law (`the_rust_cathedral.md`, FROZEN): §6 ban 7 — no ordinary wildlife, nothing
organic outside §4's short list, green flora zero. §6 ban 1 — no §GM truth in
player-facing text. The concealment arc (§7b amendment, `CATHEDRAL_PLAYER_CONCEALMENT_ARC_1`
context): the Cathedral survives by looking dull, permits salvage as cover, and hides
from the player for a long while — so **nothing about its wildlife may read as
"designed" to a player who hasn't earned §GM**; strangeness must look like decay, not
intention. Palette: family `#241511 → #cfa065`, accent `#3fae8e` verdigris-at-the-coolant;
banned: green vegetation of any kind. Mech-analog fauna precedent: GR_Mechachicken and
GR_Mecharat arrive this round as mech-analog ANIMAL defs (`biome_findings.md`, with the
finding: add mech-analogs to §4's short list explicitly or the linter flags them —
both new defs below ship with that §4-amendment line owed at the canon sitting).

## 5. The deckroach — the mechanical cockroach

### 5a. The ruled frame

Ling_Cockroach is the **organic** roach, already resident (owner flag "might work here
after all," graded keep-at-trace, roster row). BMT_Megaroach is out — evicted
homeless-reserve, "one roach only." The commission is the OTHER roach: the mechanical
one, the Cathedral's own vermin.

### 5b. Reskin vs new — decided: NEW def

- **Not a BMT_Megaroach reskin.** That def is an organic animal (meat, leather,
  organic butchery) sitting in homeless-reserve; a reskin would carry organic products
  into a mechanical creature and re-seat a def the owner just unseated. Rejected.
- **Not a Mechanoid-class def.** The mechanoid axis is EXCLUDED from wild rosters by
  design (`MECHANOID_BIOME_PRESENCE_REVIEW_1`, restated in the roster's confidence
  block), and a true mechanoid drags faction, power and threat machinery a vermin
  never uses. Rejected.
- **The route that fits: the living-bolt def shape** — the roster's own ruled pattern
  for Cathedral mechanical wildlife (`new_defs`: "mechanical wildlife def shape — not
  organic, not tameable, not butcherable into meat"), which is also how the arriving
  GR_ mech-analogs work: ordinary animal-class defs whose mechanical nature is carried
  by graphics (`ThingDef.graphicData`, the OuterRim droid rendering route), products
  (scrap, not meat), and description. 🔴 Build-seat verification owed per house rule:
  the exact fields that zero the meat/leather yield and any VEF helper comps are
  verified against RimSage at build, never guessed here.

### 5c. Name, flavor, numbers

| field | value |
|---|---|
| defName / label | `RUT_Deckroach` / `deckroach` — Cathedral English register (living bolts, coolant eels: this biome names its things in plain haunted English, the sheet's own register). ⚠️ Flagged: "Mechachicken" just failed recognizability ON NAME; if "roach" falls the same way at the rename pass, the fallback is **deck-mite** (AA "Mit" precedent). The owner's commission word was "cockroach," so the name keeps it until he says otherwise |
| nickname | "sweepings" — what the droids call them; they will not step on one |
| the niche split vs Ling_Cockroach | the organic roach is the lone outside survivor scraping an organic living at the margins; the deckroach is **staff**. It works the rust film — grazing oxide bloom off the plate, polishing as it goes **[INVENTED behavior; anchored on §3's "the rust is a surface film" and §4's grooming register: "the Cathedral tolerates them, or grooms them, like a man brushing flies off a grave"]**. Where deckroaches are thick, the plate is clean — a §GM-legible tell (the mind maintains what it cares about) that never says so in text (ban 1: the description states the correlation as superstition, never the reason) |
| behavior | timid vermin, flees everything, wildGroupSize small clusters; commonality low (the cast stays near-empty; §1 "almost nothing alive" is the read to protect) |
| size | bodySize ~0.2, spd ~4 **[INVENTED]** |
| products | killed: a little steel/scrap, no meat, no leather (mechanical-wildlife convention); not tameable, trainability None |
| the crowding flag | with Mechachicken, Mecharat, deckroach and the bolts, the "mechanical vermin" shelf now holds four small strange things. ⚠️ Flagged for the owner (§11 Q3): he may trim — the deckroach's distinct claim is that it is the only one with a JOB |
| art | rust-film palette: dark metal body, ochre dust dulling, `#3fae8e` verdigris pinstripes at the joints as the one cool note — reads at distance as a moving bolt-head, which is exactly the biome's ambiguity register |

**Description (player-facing, ban-1-audited):**

> A cockroach the size of a hand, except it was never alive: stamped plates, pinned
> joints, and no maker's mark anywhere on it. It grazes rust the way a beetle grazes
> lichen, and the plate behind it is clean. Salvagers call them sweepings and let them
> be — partly because the droids get quiet when you don't, and partly because in ten
> thousand years nobody has ever found a dead one.

## 6. The gear-dancers — the living bolts, made a def

### 6a. One species, not two — the reconciliation this brief exists to make

The owner's sitting words — *"the little gear-like dancing creatures"* — are the frozen
sheet's own living bolts (§4, verbatim: *"component-looking creatures… they move in
complex, strange, dance-like patterns for no reason, baffling everyone — and their
little dances resonate with the mood of the greater mind"*). The roster already carries
them as a `new_defs` row ("roster item owns the def shape"). **This commission is that
def's brief, not a second dancing species** — inventing a sibling would spend a def to
say less and violate the near-empty read. ⚠️ Flagged (§11 Q4) in case the owner meant a
distinct second creature; nothing below breaks if he did — a variant reskins this spec.

| field | value |
|---|---|
| defName / label | `RUT_LivingBolt` / `living bolt` (the sheet's ruled name, kept) |
| the two-name pattern | vernacular "living bolts" (salvagers); the droids' own word for them is **"the dancers"** — the bestiary §2 two-register pattern, done with speech instead of a datapad **[INVENTED: the droids' name]** |
| §GM discipline | their origin (auto-growing tech remnants drifting in the mind's thoughts) is gated — ban 1. The player-facing description describes and never explains; "no reason" is load-bearing text |

### 6b. The dance — what it IS mechanically, honestly

The dance is the centerpiece and the engine has no "dance." The honest ladder:

1. **v1 base (zero new C#):** small mechanical-wildlife pawns (the §5c def shape),
   spawned in loose clusters, vanilla wander AI. Motion exists; "dance" is carried by
   grouped placement, art, and description. Cheap, real, insufficient alone.
2. **v1 recommended addition — per-body animation:** `Verse.AnimationDef` +
   `AnimationWorker_Keyframes` exist in the engine (verified; Anomaly's revenant
   spasm/hypnotise are shipped consumers) — a looping keyframe sway/spin/figure on the
   bolt's own body, driven by a small comp, gives every bolt a visible non-locomotor
   dance at near-zero tick cost. This is the twinkle-spike-shaped question for FAUNA:
   prove it on ONE def, measure, report (same protocol as TWINKLE_FLORA_SPIKE_1 —
   this brief names it the **bolt-dance spike**). Formation choreography (bolts
   coordinating patterns across cells) is explicitly NOT proposed — a multi-pawn
   JobGiver ballet is the expensive fantasy version, rejected.
3. **The mood wire is already owed elsewhere:** the hum-mood system
   (`RUST_CATHEDRAL_MECHANICS_1`, sheet §7b) rules that the mind's attitude is
   *"displayed by the bolts' dances"* and that *"the bolts freeze first"* when the hum
   drops. This brief supplies that system its contract: the dance comp exposes a
   small state ladder — **still / idle-sway / full dance** — and the mechanics item
   maps hum-mood onto it. The freeze IS the biome's warning klaxon; a player who
   learns to watch the bolts has learned hum-literacy's first word (§7 "hum-literacy"),
   and the concealment arc gets a tell that never explains itself |

### 6c. Numbers, products, art

| aspect | spec |
|---|---|
| stats | tiny: bodySize ~0.15, spd ~2, wholly non-combat, flees nothing (it does not register threats; it is not sensing YOU — **[INVENTED, ban-1-safe: stated as observed behavior]**), untargetable-by-predators in practice (nothing here hunts) |
| harm rule | killing one is sacrilege-adjacent: proposed to ride the ruled sacrilege economics' goodwill machinery at a small value rather than a new system **[INVENTED: the hookup; the economics are ruled]** — flagged §11 Q5 |
| products | none by butchery (mechanical, not butcherable — roster shape); the sheet's ruled **bolt-shed curiosities** (§7: "salable, watched") arrive instead as rare ground drops where bolts dance long — item `RUT_BoltShed`, §10b |
| art | a fat hex-headed bolt-body with too many small articulations, gear-flats catching light; family metals with verdigris accents; the sprite must read as a COMPONENT at rest — the player's first instinct ("pick it up and move it out of the way," owner verbatim) is the art acceptance test |

**Description (player-facing, ban-1-audited):**

> A bolt with legs, or a gear with opinions — the salvage guides genuinely disagree
> about which. They gather in the open and move: slow figures, repeated, precise,
> and to no purpose anyone has ever demonstrated. They do not eat, flee, or die of
> anything obvious. The droids call them the dancers and will stand a long time
> watching, and if you ask what the dance is for, the polite ones change the subject.
> One thing every hand learns fast: when the dancers stop, stop.

---

# Part C — the Pyrelands igniter pair

Shared law (`the_pyrelands.md`, FROZEN): §4 is the design, already ruled in prose —
these briefs bind it to defs and name the mechanics honestly. §6 bans: no tame
furnace-beast (ban 5); no fire-immune flora blanket; vanilla-Earth eviction. The ruled
fire chain: *"beast or bolt or bird ignites → hawks spread → burrowers dive → the burn
passes → scorch-fruit cracks open → Tribes and ash-grazers harvest the black → the
quickgrass sprints back → the storm re-arms."* Palette: grass-gold family
`#2e2410 → #e6cf7e`, accent `#62c944` regrowth green (flora's — the fauna wears ash,
ember and gold). Build state per §0's note: **both defs exist with art**
(`RUT_PyrelandsFauna.xml`, roster rows dated 2026-09-10); both roster rows record the
same debt this section specifies: *"twig-carrying / heat aura / bed-down ignition NOT
implemented — owed to PYRELANDS_MECHANICS_1 (unfiled)."*

## 7. The fire-hawk — `RUT_FireHawk` (built; mechanics owed)

### 7a. What stands (read from the built def, not re-designed)

Label "fire-hawk" (the sheet's own coinage — kept, bladderboil precedent); predator,
MoveSpeed 5.2, talons and beak, manhunterOnDamageChance 0.15; description already
carries the twig-carrying line. Commonality 0.15, band "igniter-flier."

### 7b. Flier-roster handling

The commission words say "flier roster" and R17 (`_freeze_rulings_2026-09-07.md`)
rules fliers cross biomes; the round-2 flier group (`reserved_groups_draft.md` §3)
is the roster home, with the Pyrelands as primary range. The known gap is on record
(`biome_findings.md`: the flier roster *"needs a per-biome presence field"*) — the
fire-hawk lands in that structure when it exists; until then the biome row it already
has stands. Range note for the field when it comes: Pyrelands primary; adjacent
hot-grass margins secondary; it follows FIRE, not biome borders **[INVENTED range]**.

### 7c. The fire-starting mechanic — the real engine route

**No vanilla comp makes an animal start fires.** The nearest shipped machinery is the
pyromaniac's spree (verified: `JobGiver_FireStartingSpree` +
`MentalState_FireStartingSpree`) — a job-driver that targets flammable cells/things
and ignites them. That is the pattern to crib, not to reuse (it is an internal
mental-state class). The spike, named for `PYRELANDS_MECHANICS_1` (unfiled — filing it
is this brief's first downstream action):

- a small C# comp/JobGiver on the hawk: **if a fire exists within scan radius**, fly a
  short sortie and ignite one flammable cell N cells beyond the fire's edge
  (direction random in v1; downwind if the spike finds wind cheap to read
  **[INVENTED parameters]**), on a long cooldown.
- 🔴 **Spread-only, never ex nihilo (proposed as the def's law):** the sheet makes the
  hawk one of four igniters, but its ruled behavior is carrying burning twigs — it
  needs a flame to steal from. Mechanically this is also the safety rail: a
  no-precondition igniter plus the ruled always-a-burn biome is a map-wide fire timer
  with feathers. Lightning and the furnace-beast start; the hawk SPREADS. ⚠️ Flagged
  (§11 Q6) because "four igniters" could be read as four independent starters.
- the flush-prey benefit ships as story + ordinary predation in v1 (it hunts what the
  flame moves; no targeting code) — honest cut, revisit only if the burn-line
  mechanic (`PYRELANDS_MECHANICS_1`'s migrating-burn presence) wants a coupling.

### 7d. One def-level finding for the mechanics pass

As built, the hawk carries `trainability Intermediate` and a tame-fail field — it is
**tameable**. No ban forbids that (ban 5 is the furnace-beast's), and a tamed
fire-spreader is a player story with teeth; but it should be a DECISION, not a
default. ⚠️ Flagged §11 Q7: tameable fire-hawk — keep (fire-falconry, Tribes-flavored)
or close (wildness high)? The brief recommends **keep**, priced by the fire it starts
being nobody's friend **[recommendation, owner's call]**.

## 8. The furnace-beast — `RUT_FurnaceBeast` (built; mechanics owed)

### 8a. What stands

Label "furnace-beast" (sheet coinage, kept); herd animal, non-predator, MoveSpeed 3.6,
horn + feet melee, `Leather_Heavy`, trainability None, **VEF
`CompProperties_Untameable`** (MayRequire VEF core), manhunterOnDamage 0.15,
commonality 0.08, band "igniter-megafauna." Description already carries the thermal
circuit, the following-for-warmth, and the smoldering bed-grounds.

### 8b. The heat aura — CompHeatPusher, cited and told the truth about

`Verse.CompHeatPusher` / `CompProperties_HeatPusher` exist (verified) and a ThingComp
attaches to a pawn — **but the vanilla temperature model spends pushed heat on the
containing room, and outdoors that is the map-wide outdoor temperature: a heat pusher
on a beast walking open grassland warms nothing a player can feel.** So the honest
split:

- **Enclosed spaces:** CompHeatPusher delivers exactly the ruled fantasy for free — a
  furnace-beast that wanders into a barn, a canyon room, or (nightside travel canon,
  sheet §7 cross-flow) a walled waystation genuinely heats it. Ship the comp; it is
  one XML node and every indoor encounter pays it off.
- **The open-field "walking hearth":** needs the owed C# — a small aura comp applying
  a warmth hediff (comfy-temperature offset) to pawns within a few cells
  **[INVENTED radius]** — this IS the "heat aura" line already logged against
  `PYRELANDS_MECHANICS_1` in the roster row; this brief specifies its shape: hediff
  aura, not cell temperature (fighting the outdoor model cell-by-cell is the
  expensive wrong route, rejected).

### 8c. Bed-down ignition

On completing a rest cycle **[trigger verified at build — never guess the tick hook]**,
chance to ignite its bed cells and/or convert them to the FireEcology kit's scorched
register (`ScorchableGround`/ash terrains — already built, per the sheet §3 and roster
provenance; the defs live under `src/RimMandrake/Pyrelands/`, RM_FE_ tier). This makes
the beast the sheet's second independent igniter — the one that CAN start from
nothing, which is why the hawk doesn't need to (§7c). Smolder, not blaze: 1–2 cells,
slow start **[INVENTED numbers]** — a herd's overnight ground lights the way a coal
does, not the way a bomb does.

### 8d. Ban 5 — "no tame furnace-beast," the mechanical truth

As built it is enforced twice over: `trainability None` and VEF's untameable comp
(which removes the taming interaction wholesale where VEF is present). The vanilla
backstop, verified at source: `TameUtility.CanTame` hard-refuses any pawn whose
Wildness stat ≥ 1.0 (`Source/RimWorld/TameUtility.cs` line 49) — **wildness 1.0 makes
taming mechanically impossible in bare vanilla, gizmo never offered.** Recommendation:
add wildness 1.0 at the mechanics pass so the ban holds even with VEF absent
(`MayRequire` means the comp silently vanishes on a list without VEF — the exact
silent-failure shape this repo documents). And the whole truth: dev mode and
mind-control mechanics (psychic animal tamer et al.) bypass every route; no XML makes
a ban absolute against tools that exist to break bans. The def can make taming
impossible in play, and that is what "mechanically enforceable" honestly means. One
housekeeping finding: the built def carries `manhunterOnTameFailChance 0.9` — dead
weight on an untameable creature; harmless, removable at the pass.

---

## 9. The recasts — one paragraph each, as ruled

### 9a. AA_Razorjack — the fire-follower

Ruled at the sitting (decisions register, verbatim note): *"RECAST at arrival: the
Pyrelands FIRE-FOLLOWER — hunts the flame edge and the flushed panic, not a generic
predator."* At def level this is a **story recast, not def surgery**: it enters the
Pyrelands biome list (plus its ruled Contagion propagation row), its description is
rewritten to the flame-edge hunting story — it works the burn's front, taking what the
fire flushes, and where the burn goes, it goes — and its art row already carries
"improve" from the register. Its stats already pass the flame-edge sort the way
Anooba's did (predator, fast); no stat changes proposed. The one coupling worth a line
in the description: fire-hawks flush from above, razorjacks take from below — the
flame edge has two hunters and they are not rivals, they are a method **[INVENTED
color; the two castings are both ruled]**.

### 9b. AA_Barbslinger — the ash-grazer

Ruled (decisions register): *"ROUTED: the_pyrelands as the ASH-GRAZER of the ruled
fire-web families."* Biome list entry plus description recast: it follows the burn at
a day's distance, grazing the regrowth sprint off the fresh black. ⚠️ **One
contradiction to verify before the row lands (build-seat, one look):** the register's
own eviction note called it a *"large predator"* — if the live def carries
`predator true`, an ash-grazer casting needs that flag and its diet read checked;
either the def reads herbivore/omnivore already and the note was loose, or a one-line
diet/predator adjustment is the single piece of def surgery this wave permits
**[the check is the deliverable; do not guess which way it falls]**. Grazing story
bonus, free: an ash-grazer herd on the black is the ruled ash-grazer family's first
body, and the burrower family remains the fire-web's one uncast slot (FOUNDRY's pick
at build, per the ruling).

---

## 10. Items — where natural, and only there

Reconciliation point as ever: `ECONOMY_TRADE_SWEEP_1` ratifies or reprices everything
below; nothing pre-empts it. The nightside trio deliberately ships **zero items** —
catalyst-chemistry bodies are not food (§7), the ilverr's charge tissue is ceded to
the aviir shard (§4b), and a biome whose register is "nothing here is for you" should
say so at the butcher table too.

### 10a. Furnace-hide — `RUT_FurnaceHide`

The built def's `Leather_Heavy` is a placeholder wearing a generic name. The natural
item: the mineral-banded, heat-banking hide as its own leather-class stuff —
**best-in-campaign cold insulation**, modest armor, and the story writes the stat
(you are wearing a stove's jacket). Obtained only by hunting the untameable (ban 5
holds: the hide is the one way a furnace-beast serves anyone, and the herd remembers
— manhunter numbers already lean that way). Must NOT duplicate: thrumbofur's
prestige-insulation slot in the vanilla economy — the sweep prices one above the
other, not both at the top **[flag for the sweep, not resolved here]**.

### 10b. Bolt-shed — `RUT_BoltShed`

Already ruled in the frozen sheet (§7: *"bolt-shed curiosities and eel-catch — both
salable, both watched"*). Given a def name here so the mechanics item can drop it:
small strange components shed where the dancers dance long; salable curiosity, modest
value, zero crafting use in v1 (a §GM-adjacent material must not become an economy
pillar while the concealment arc runs — **[INVENTED restraint]**). "Watched": selling
them where droids can see costs droid goodwill — wired to the ruled sacrilege
economics at the mechanics pass, flagged §11 Q5 with the kill-a-bolt question.

### 10c. Deckroach scrap

No bespoke def: killed deckroaches yield a little steel (vanilla item, §5c). A
fourth micro-material earns nothing — the skerrik-chitin precedent, applied.

---

## 11. Open questions — the owner's, not ours

1. **The ilverr's light (§4b):** corona-discharge reading of the frozen biolum ban —
   confirm (ShockGoat's ruled aura is the precedent), or the ilverr goes dark and is
   sensed only as the witch-fence silhouette against aurora-lit ice.
2. **Chittik active-state speed (§3c):** fast-while-warm inside disaster windows only —
   confirm the carve-out reading of §6's no-fast-fauna ban.
3. **Cathedral vermin crowding (§5c):** Mechachicken, Mecharat, deckroach, bolts —
   keep all four small mechanicals, or trim at review?
4. **Gear-dancers = living bolts (§6a):** one species (recommended, sheet-derived) —
   or did the sitting mean a second, distinct dancer?
5. **Bolt harm and bolt-shed sales (§6c/§10b):** ride the ruled sacrilege-goodwill
   economics at small values — confirm the hookup.
6. **Fire-hawk ignition law (§7c):** spread-only (recommended) or a fourth
   independent starter?
7. **Tameable fire-hawk (§7d):** keep as built (fire-falconry) or close?
8. **Furnace-hide (§10a):** commission the item now, or leave `Leather_Heavy` until
   ECONOMY_TRADE_SWEEP_1?

---

## 12. Sources read for this brief

- Biome sheets (all FROZEN): `biomes/nightside_ice.md` (§1–§9 whole, §4 verbatim law,
  visitor clause, thaw pulse, roster consequences); `biomes/the_rust_cathedral.md`
  (§1–§9, §GM, §7b concealment amendment, bans 1/7); `biomes/the_pyrelands.md`
  (§3–§8 verbatim igniter prose, ban 5)
- Rulings: `review/round2/biome_findings.md` (the three sitting-ruled commission
  lines, visitor law, fire-web repopulation, mech-analog arrivals + rename findings);
  `review/round2/decisions_propagated.json` (Tauntaun/Wampa/Jakobeast/ShockGoat/
  CaveLemming/Razorjack/Barbslinger owner notes, quoted verbatim);
  `review/round2/reserved_groups_draft.md` §3 (flier roster);
  `biomes/_freeze_rulings_2026-09-07.md` R17
- Rosters: `biomes/rosters/nightside_ice.json` (natives, new_defs, near-empty
  ruling), `the_rust_cathedral.json` (Ling_Cockroach row, Megaroach eviction, living
  bolts new_defs shape, mechanoid-axis exclusion), `the_pyrelands.json` (built
  igniter rows, PYRELANDS_MECHANICS_1 debts)
- Built defs: `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`
  (working tree, read 2026-09-10)
- Engine, verified via RimSage this pass: `CompHeatPusher`/`CompProperties_HeatPusher`;
  `CompCanBeDormant`; `Hive` + `CompSpawnerPawn.SpawnPawnsUntilPoints`;
  `InfestationCellFinder` warmth scoring (−17 °C floor, warm-cell preference);
  `JobGiver_FireStartingSpree`/`MentalState_FireStartingSpree`;
  `TameUtility.CanTame` (Wildness ≥ 1.0 refusal); `Verse.AnimationDef` +
  `AnimationWorker_Keyframes` (Anomaly consumers shipped)
- Format and law: `creatures/RUT_hydrocarbon_ecology_commission.md`;
  `creatures/goo_boom_commission.md`; `palettes/biome_palette_anchors.json`;
  `Alien_Bestiary.md` §1–§2; `design/NAMING_SCHEME_PLAN.md`
