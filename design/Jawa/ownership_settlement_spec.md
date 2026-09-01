<!-- status: RULED design spec — owner brainstorming sitting 2026-08-31 ("Superb! ...
     This is amazing! (two mods)"). Research input: design/Jawa/mods/ownership_mods_research.md
     (mod-ecosystem survey; Visit Settlements = study-and-replace). Canon:
     canon.yml ownership_fabric. Execution items: PROPERTY_FABRIC_BUILD_1 ·
     SETTLEMENT_VISIT_LOOP_1 · DISTRICT_TEMPLATE_LIBRARY_1 · SETTLEMENT_VERBS_WAVE_1. -->
# Ownership, theft and settlement interaction — the ruled design

The mod ecosystem has every piece except the combination: **ownership +
provenance + permissions + perception** as one system. That combination is
ours to build. Stealing stops being a verb and becomes a world.

## Ruled at the sitting (owner, 2026-08-31)

1. **Two mods.** `RM_Property` (RimMandrake tier, packageId
   `mandrake.rm.property`) is the campaign-blind fabric; **Inhabited** grows
   the visit lifecycle, district maps and verbs on top of it. All taste
   (faction security profiles, district manifests, verb tuning, Jawa claim
   heat) ships as RimUtinni data. Visit Settlements is studied for lifecycle
   edge cases and RETIRES from the mod list when our loop lands.
2. **Claims are a decaying vector.** Every Thing's perceived ownership is a
   set of claims `(claimant, strength 0–1, basis, timestamp)`. Strength
   decays from the timestamp at a rate set by a per-Thing RECOGNIZABILITY
   score (uniqueness, serials, quality/art, market value, named things,
   droids). A steel bar's stolen-claim dies in days; a named astromech's
   never does.
3. **Claims are virtual by default, recorded by exception.** Territorial
   (inside a faction's Faction-Territories region), situational (district
   zoning, a cast pawn's equipment) — computed, zero storage. Records exist
   only for: stolen, purchased, claim-fee-paid, gifted, inherited, looted.
   Decay is computed lazily; no tick cost, no comp on ten thousand rocks.
4. **Resolution follows narrative proximity** (owner's insight): the claimant
   of record is the most-resolved party the story has rendered — a faction
   blob at distance, a named cast pawn in their shop, an individual Jawa at
   home. **The player colony is NOT a faction: each colonist is their own
   claimant.** The Clan claimant holds only the survival spine — the Utinni,
   its systems, food and water. Everything else is someone's.
5. **Battle loot keeps its origin claim** at ~1.0, decaying by
   recognizability — fencing fresh Imperial rifles to Imperial-aligned buyers
   is a risk; old ones are just rifles.
6. **Perception is fully hidden.** No meter, no indicator, ever. Witnesses
   (pawns, fixed cameras as district props, an ambient per-faction
   surveillance chance — flying patrols, orbital eyes) hold knowledge as
   PEOPLE first; it propagates upward (gossip → district boss → faction
   record) at the faction's security-profile rate. Hutts excellent, Empire
   and Deepwater high, Tuskens ~nil. Consequences read the FACTION RECORD,
   never the event: prices cool, guards shadow, a fence recognizes a serial,
   a bounty, a recovery invoice, a raid. A crime nobody filed costs nothing.
   The player learns only by reading the world — dread is the mechanic.
7. **Scope is fully symmetric.** Settlements, territory-tagged wild maps, AND
   the colony: guests perceive-own their kit, NPCs can pilfer the player,
   "using my stuff" fires the same TakingEvent → witnessed by the owner →
   social fight per Jawa heat tuning.
8. **Maps are districts composed per settlement:** a library of authored Lua
   district templates (market row, cantina block, dwelling cluster, workshop
   yard, depot, shrine, scrapyard…) + a per-settlement manifest (districts,
   sizes, adjacency, cast assignment, security props) composed through the
   rimplace machinery.
9. **v1 verb families:** crime suite (pickpocket, night burglary, fencing,
   smuggling past gate searches), salvage-law gray zone (claim-fee gizmo,
   wreck rights, the powered-down droid), walkable commerce (merchandise,
   haggling, purchase as the legal provenance record), social fabric (rumors
   as intel, sabacc, hiring the placeless, bribes and bought rounds as
   propagation dampers).
10. **Build order: colony side first** — the fabric lands and matters at home
    months before the first visit map. **Pilot town: Junkers** (low security,
    forgiving, cheapest district art), Hutt town is the later showcase.

## The event spine (shared by every verb)

```
act (take/use/strip/sabotage/buy/claim) → TakingEvent
  → claim resolution: whose, how strong, decayed to what
  → perception roll: witnesses + fixed security + ambient surveillance
  → knowledge held by PEOPLE (suspect-confidence per witness)
  → propagation over days per security profile   ← bribes/rounds/kills dampen
  → faction record                               ← the only thing consequences read
```

Gate searches replace Visit Settlements' omniscient departure check: a
faction searches leavers only if its profile says so (Empire pats down,
Junkers wave through).

## Module boundaries

| unit | owns | must not know |
|---|---|---|
| `RM_Property` fabric | claimants, claims, decay, recognizability, provenance records, TakingEvent, perception+propagation, faction record | anything Star Wars; any district/verb |
| Inhabited visit loop | arrival→manifest→compose→cast→routes→departure→teardown; map-knowledge persistence (casing) | claim math |
| District library | Lua templates + composition; security props placement | who visits |
| Verbs | gizmos/jobs that EMIT TakingEvents and read AccessPolicy | perception outcomes (hidden even from the verb code's UI) |
| RimUtinni data | security profiles, manifests, heat/decay tuning, claim-fee tables | — |

## Sequenced execution (filed for FOUNDRY)

1. **PROPERTY_FABRIC_BUILD_1** — RM_Property mod: claim engine, recognizability,
   provenance records, TakingEvent + perception + propagation + faction record,
   colony-side friction (per-colonist claimants, Clan commons, guest claims,
   fight hook). Proven at the colony with zero visit machinery.
2. **SETTLEMENT_VISIT_LOOP_1** — Inhabited: peaceful-entry lifecycle for named
   frozen-world settlements, manifest schema, teardown to roster, casing
   persistence, gate-search hook. Junkers pilot manifest.
3. **DISTRICT_TEMPLATE_LIBRARY_1** — Lua district templates through rimplace
   (layout-layers lint applies); Junkers set first: scrapyard, dwelling
   cluster, cantina block, depot. Security props vocabulary.
4. **SETTLEMENT_VERBS_WAVE_1** — the four v1 families as jobs/gizmos emitting
   TakingEvents; fence/buyer provenance checks; claim-fee flow; rumor intel
   objects; sabacc.

Open tuning (execution-time, not blocking): decay curves per recognizability
band · propagation rates per profile · Jawa heat by trait/relationship ·
ambient surveillance chances · claim-fee pricing. All data, all RimUtinni.
