# Rot fauna assignment — DRAFT for the owner's sitting

Item context: BIOME_FAUNA_ASSIGNMENT_SITTING_1. Feeds ROT_HEALTH_SHARING_1 and
ROT_GUARDIAN_GROVES_1 (the RUT_RegenerantVeil alarm currently has 0 responders).
Drafted 2026-09-18, offline reads only. Nothing here is decided until he marks it.

## The mechanics being assigned

Three shipped, content-blind mechanics in `src/RimMandrake/CreatureBehaviors/Source/`.
None of them does anything until a race def carries the tag — this sitting is what
turns them on.

1. **Wound-link** (`RM_CompWoundLink` + `RM_WoundLinkExtension`). When a tagged
   creature takes a real wound (severity ≥ 8), 60% of it is mirrored onto each
   same-tag kin within 12 cells and subtracted once from the victim. Plain
   language: the herd shares the hit — one animal is harder to kill, but hunting
   one hurts them all. Same tag = one network organ. Different tags never interact.
2. **Kin-mending** (`RM_HediffComp_KinMending`, reads the SAME extension). While
   ≥2 same-tag kin are within the radius, the carrier heals its injuries faster —
   `extraSeverityHealedPerDay` on the hediff comp, owner's target range **2–4
   severity/day** (vanilla natural healing base is 8/day, MEASURED — so this is a
   +25% to +50% bonus while huddled). Plain language: the network heals its own,
   but only when they stay together.
3. **Alarm-responder** (`RM_AlarmResponderExtension`). When a guardian grove plant
   carrying `RM_CompPlantAlarm` (RUT_RegenerantVeil, RUT_FalseFruit — both radius
   18, blank comp tag = ANY tagged responder answers) is harvested or hurt, tagged
   fauna nearby go manhunter. **Currently 0 carriers, so the RegenerantVeil alarm
   is a live no-op** — this sitting fixes that.

One extension carries both wound-link and kin-mending (one tag, one radius), so a
race gets tagged once; alarm-responder is a separate, independent tag.

### Principles applied below (stated up front)

- **Wound-link tags define herds that share pain.** Tag by ecological clique,
  never universally — a biome-wide tag would let a snail soak a colossus' wounds.
- **Kin-mending fits the passive/prey kinds** — the network heals its own; the
  player's counter is to split the herd before hunting.
- **Alarm-responder fits territorial defenders near groves** — predators and
  guardians, not grazers; a grazer going manhunter reads as a bug, a mantis
  going manhunter reads as a trap sprung.
- Every row states its trade in plain language.

## The Rot's fauna roster

From `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` `<wildAnimals>` —
15 kinds, all still donor/import defNames (fauna admission was deferred to this
sitting), plus the kit's own shipped race. Class labels are the XML's own comments.

| # | defName | commonality | class (XML comment) |
|---|---------|-------------|---------------------|
| 1 | BMT_ChemSnail | 0.7 | ingest-strange |
| 2 | RSW_FungalWeevil | 0.4 | ingest-strange |
| 3 | BMT_GlowBat | 0.4 | ingest-strange |
| 4 | BMT_Pillbug | 0.4 | ingest-strange |
| 5 | BMT_GiantSlug | 0.3 | ingest-strange |
| 6 | AA_Swarmling | 0.3 | hybrid-vermin, adjust-keep |
| 7 | AA_Agaripod | 0.25 | hybrid-native |
| 8 | AA_MycoidColossus | 0.25 | hybrid-giant |
| 9 | RSW_BovineBeetle | 0.2 | ingest-producer |
| 10 | BMT_GiantSnail | 0.2 | ingest-strange |
| 11 | AA_Agaripawn | 0.2 | hybrid-native |
| 12 | AA_Wildpawn | 0.2 | hybrid-native, adjust-keep |
| 13 | AA_Wildpod | 0.2 | hybrid-native, adjust-keep |
| 14 | RSW_FungalMantis | 0.15 | guardian |
| 15 | BMT_CaveSpider | 0.05 | guardian |

Kit race: **RUT_Emberscythe** (`src/RimUtinni/RotSporeKit/Defs/ThingDefs_Races/RUT_Emberscythe.xml`)
ships in RotSporeKit but is a **Pyrelands** fire-follower, not Rot fauna — it is
not in the Rot's wildAnimals and already carries a solo self-heal
(InjuryHealingFactor 1.6). Rowed below for completeness; proposal is none/none/none.

Sheet law applied (design/Jawa/worldbuilding/biomes/the_rot.md §4/§5): hybrid-or-out
is the residence test; the ingest-strange tail rides trace commonality pending its
own admission judgment — tagging them does not admit them, and the tag survives a
later re-defName (the extension is patched, not baked).

## Draft assignments

One kin tag names one ecological clique — one network organ. A race can carry a
kin tag and still get only ONE of the two mechanisms (the tag is shared plumbing;
the wound-link comp and the kin-mending hediff are attached separately). Five
cliques proposed:

### Clique 1 — `RotAgarikin` (AA_Agaripod + AA_Agaripawn) — the flagship organ

- **Wound-link: YES, both.** The biome's emblematic natives; the sheet's thesis
  species. Trade: hunting one agari wounds every agari within 12 cells — one is
  harder to kill, but the hunter walks away from a bleeding grove. Tamed, your
  agari herd bleeds as one (the caravan-survival story the spec promises).
- **Kin-mending: YES, 3 sev/day.** Trade: a huddled agari herd shrugs off small
  wounds; split them up before you hunt.
- **Alarm-responder: no.** They are the treasure, not the guards.

### Clique 2 — `RotWildkin` (AA_Wildpod + AA_Wildpawn) — the soft aura variant

- **Wound-link: no.** The spec ruled the two variants land on DIFFERENT species;
  these are the softer kinds and take the aura only.
- **Kin-mending: YES, 4 sev/day (top of range).** Trade: the fastest healers in
  the biome, but only while together — alone, a wildpod is just a mushroom with
  legs.
- **Alarm-responder: no.**

### Clique 3 — `RotSlimekin` (BMT_ChemSnail + BMT_GiantSnail + BMT_GiantSlug)

- **Wound-link: no.** ChemSnail is the single commonest kind (0.7) — wound-link
  on it would make every casual hunt anywhere on the map ripple, and slugs do not
  rush to each other's aid; that reads as a bug, not a network.
- **Kin-mending: YES, 2 sev/day (bottom of range).** Trade: slime-kin knit a
  little faster in a cluster; barely visible, pure flavor-support. This is also
  the one deliberately CROSS-SPECIES tag — three species, one organ (see open
  question 3).
- **Alarm-responder: no.**

### Clique 4 — `RotBroodmates` (RSW_FungalWeevil + BMT_Pillbug)

- **Wound-link: no** — small prey, the 8-severity gate barely clears their body
  size; a gated mechanism that almost never fires is dead weight.
- **Kin-mending: YES, 2 sev/day.** Trade: broods recover if you leave survivors;
  finish a brood or expect it back.
- **Alarm-responder: no.**

### Clique 5 — `RotHerd` (RSW_BovineBeetle alone)

- **Wound-link: YES.** The producer/pack kind — the tamed-herd flagship. Trade:
  a beetle train survives a raid volley by spreading it; but one predator strike
  in the wild bloodies your whole tamed line if they graze together.
- **Kin-mending: YES, 2 sev/day.** Modest — it is already the safest animal here.
- **Alarm-responder: no.** A grazer going manhunter reads as a bug.

### Ungrouped

- **BMT_GlowBat — none/none/no.** Flocks scatter rather than share; a flying
  kin-mender is invisible to the player. Cleanest honest "none" row. (Alt: tag
  `RotGlowflock`, mend 2/day, if he wants zero untagged prey.)
- **AA_MycoidColossus — no kin tag (solitary; there is never a second colossus
  in 12 cells, so both mechanisms would be dead letters). Alarm-responder: YES.**
  Trade: harm a veil and, if a colossus is near, the forest itself walks over —
  the set-piece answer to ban 8. Rare (0.25), so it is the jackpot response, not
  the routine one.
- **AA_Swarmling — kin tag `RotSwarm`, wound-link YES, kin-mending no, alarm
  YES.** The swarm is one body: wound one, wound the swarm — which also means a
  grenade into a swarm is devastating (60% of every hit mirrors across the pack).
  Trade runs BOTH ways and that is the point of a swarm. No mending: vermin that
  self-heal make swarm clearance tedious. Alarm: vermin boiling out of the mat
  when the network screams is the cheap, common response.
- **RSW_FungalMantis — alarm-responder YES; no kin tag.** The XML already calls
  it "guardian"; a solitary ambush predator. Trade: the false-fruit trap now has
  teeth — the mimic pings, the mantis you never saw answers.
- **BMT_CaveSpider — alarm-responder YES; no kin tag.** Same guardian logic,
  rarest kind (0.05) — a spice response, not a reliable one.
- **RUT_Emberscythe — none/none/no.** Pyrelands animal, wrong biome; already has
  a solo self-heal stat. Tagging it here would leak Rot mechanics into fire country.

**Alarm responder roster: 4 kinds (Swarmling, FungalMantis, CaveSpider,
MycoidColossus), combined commonality 0.75 of a 4.2-total roster.** All proposed
with the SAME blank-match semantics the shipped comps use (comp tag blank = any
responder answers); no per-grove tag split proposed for v1.

## Tuning numbers proposed

All wound-link plumbing stays at the shipped spec values (radius 12, share 60%,
gate ≥8 severity, min 2 kin for mending) — nothing here proposes changing them;
this sitting assigns tags and picks per-species mending strength only.

| knob | value | why |
|------|-------|-----|
| KinMending, Wildkin | **4 sev/day** | Top of his 2–4 range; +50% over vanilla 8/day base. The aura-variant showcase species. |
| KinMending, Agarikin | **3 sev/day** | Mid-range; they already get wound-link, so stacking max mending on top over-armors the flagship. |
| KinMending, Slimekin / Broodmates / Herd | **2 sev/day** | Bottom of range (+25%); flavor-visible, hunt-irrelevant. |
| Wound-link carriers | Agarikin (2 kinds), Swarm, Herd | Herds that share pain; 4 of 15 kinds — tagged by clique, never universal. |
| Alarm responders | 4 kinds, blank-match | Fixes the 0-carrier no-op with three commonness tiers: common vermin (0.3), mid ambushers (0.2 combined), rare colossus (0.25). |

Plain-language ceiling check: a lone wounded wildpod heals at vanilla speed; in a
huddle it heals 1.5× vanilla. Nothing in this sheet makes any creature unkillable —
wound-link never prevents an outright kill (post-application by design), and
mending caps at +50% of natural healing.

## Wiring notes (FOUNDRY's, not the sitting's)

- Assignments land as UtinniPatches XML patches onto the donor/import race defs
  (`PatchOperationAddModExtension`-shape + `<comps>`/hediff wiring), each patch
  `PatchOperationFindMod`-gated per the standing law (never MayRequire on a patch
  Operation — INERT, measured 2026-09-17).
- Kin-mending is a HediffComp: each mending clique needs a small always-on hediff
  (or a per-race apply route) carrying `CompProperties_KinMending` with its
  `extraSeverityHealedPerDay`; strength is per-hediff-def, which is why the table
  above is per-clique.
- Both RM_ mechanisms already have Mod Settings kill-switches
  (`kinMendingEnabled`, boost multiplier) — the per-mod settings law is satisfied
  upstream.

## Open questions for the sitting

These three genuinely need your ruling — everything else above has a defensible
default you can just amend in the table.

**Q1 — Will the alarm actually find anybody?** The grove alarm reaches 18 cells
from the plant, but responders spawn wherever wildAnimals density puts them —
nothing herds guardians toward groves. So some alarms will ring into empty
forest. Options: **(a)** accept it — a trap that sometimes misfires is still a
trap (proposed default); **(b)** raise the comp radius (map-scale responses, but
"manhunters from across the map" can read as random aggro); **(c)** file a v2
item for guardian-biased spawning near groves. Trade in plain words: (a) is free
but inconsistent, (b) is consistent but can feel arbitrary, (c) costs a build.

**Q2 — Patch donor defs now, or wait for absorption?** All 15 kinds still wear
donor/import defNames (BMT_/AA_/RSW_), and `BMT_FAUNA_ABSORPTION_1` will re-home
the BMT_ ones. Patching now turns the mechanics on immediately but the BMT_ rows
get redone at absorption; waiting leaves the RegenerantVeil alarm a no-op longer.
Proposed default: patch now (patches are cheap and MayRequire-safe; redo is a
rename, not a redesign) — but it is your call because it schedules FOUNDRY work
twice.

**Q3 — May one kin tag span species?** `RotSlimekin` deliberately joins three
snail/slug species into one healing clique ("all slime of one flesh"). Same
mechanism would allow Agarikin+Wildkin to merge later. If you'd rather kin =
one species only, Slimekin splits three ways and the snails mostly stop mending
(they rarely cluster same-species). Proposed default: cross-species allowed
within a named clique, never biome-wide.

(Also flagged, not needing a ruling unless you disagree: GlowBat is the only
prey kind left with nothing — say the word and it gets `RotGlowflock` mend
2/day.)

## Decision table

Mark each row: ✓ as drafted / ✗ strike / write-in. Tag blank = no kin mechanics.
Mend is severity/day (your range 2–4; vanilla base 8).

| creature | kin tag | wound-link | kin-mend | alarm | one-line trade |
|----------|---------|-----------|----------|-------|----------------|
| AA_Agaripod | RotAgarikin | YES | 3 | no | herd shares pain and knits together |
| AA_Agaripawn | RotAgarikin | YES | 3 | no | same organ as the pod |
| AA_Wildpod | RotWildkin | no | 4 | no | fastest healer, only in company |
| AA_Wildpawn | RotWildkin | no | 4 | no | same organ as the pod |
| BMT_ChemSnail | RotSlimekin | no | 2 | no | flavor mend; commonest kind stays simple to hunt |
| BMT_GiantSnail | RotSlimekin | no | 2 | no | joins the slime organ |
| BMT_GiantSlug | RotSlimekin | no | 2 | no | joins the slime organ |
| RSW_FungalWeevil | RotBroodmates | no | 2 | no | broods recover if survivors remain |
| BMT_Pillbug | RotBroodmates | no | 2 | no | same brood organ |
| RSW_BovineBeetle | RotHerd | YES | 2 | no | tamed train spreads a raid volley |
| AA_Swarmling | RotSwarm | YES | no | YES | one body: wound one, wound all — both ways |
| AA_MycoidColossus | — | no | no | YES | the forest walks over, when it's near |
| RSW_FungalMantis | — | no | no | YES | the trap you never saw answers |
| BMT_CaveSpider | — | no | no | YES | rare spice response |
| BMT_GlowBat | — | no | no | no | honest none (or RotGlowflock 2 — your call) |
| RUT_Emberscythe | — | no | no | no | Pyrelands animal; keep Rot mechanics out of fire country |

Totals as drafted: 10 of 16 rows kin-tagged in 5 cliques; 4 wound-link carriers;
9 menders; 4 alarm responders (fixes the 0-carrier no-op).
