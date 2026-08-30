<!-- status: PARALLEL BUILD — emitted 2026-08-29/30 by BENCH on the owner's
     instruction: "create fewer, more efficient, more clearly organized
     canonical lore files that ingest all the rulings... a new directory
     reconciled_lore to start emitting the improved, more precise, zero
     redundancy version of our lore to eventually switch into."
     NOT YET SWITCHED-INTO: no old doc carries a supersession pointer here yet.
     The switch is a separate owner-approved pass. -->

# reconciled_lore — the consolidated canon

One directory that answers "what is true in this campaign" without reading 110
documents. Every ruling through **2026-08-29** is ingested (turret doctrine,
Droidworks, Rakata dark-half, ion doctrine, research-tree deferral, shop-as-
quest-pack included).

## Reading order

| file | scope |
|---|---|
| `01_campaign.md` | premise, pillars, the loop, v1 start, names, delivery |
| `02_world.md` | Ash'karr: the lock, the three condensers, fire, the nightside |
| `03_deep_history.md` | Rakata/Forsaken, the Assailant, the war, what remains |
| `04_factions.md` | the 13, one canonical block each + inter-faction rulings |
| `05_the_clan.md` | Jawa society, The Salvation, the nine gods |
| `06_the_ship.md` | the Utinni/Kolyska, the nine tenants, flight, identity |
| `07_physics_and_arms.md` | the laws of harm, and every armament ruling to date |
| `08_droids.md` | the five states, Droidworks, the port |
| `09_arcs_dungeons_quests.md` | the designed player arcs and where they fire |
| `FUTURE_VECTORS.md` | where v2 wants to go, distilled and aligned |
| `INDEX.md` | every old doc → where its live content now lives |
| `GAPS.md` | genuinely unsettled questions, for the owner |

## The layering rule (this is what "zero redundancy" means here)

- **Contested NUMBERS live in `infrastructure/state/canon.yml`** and are cited,
  never copied. A number in these files is either uncontested or a pointer.
- **Engine fields live in the build specs** (`FACTION_SPEC.md`, the droid build
  spec, `gravship_flight_invariants.md`, `divine_satiation_engine.md` mechanics
  half). These files carry the FICTION and the RULINGS; the specs carry the XML.
- **Owner-verbatim quotes are preserved wherever they are load-bearing** — a
  ruling's words are its authority.
- Source tags are compact: `[owner 2026-08-15]` = an owner ruling on that date;
  `[measured]` = read from the game/dump, see the source doc.

## The provenance rule [owner 2026-08-30]

**Provenance lives in git, nowhere else.** Entries state what IS, never what
used to be — no amendment narrations, no before/after, no superseded-by
prose. A dated owner tag on a current rule is sourcing and stays; a story
about how the rule got here is git's job. (The contradiction map that guided
the reconciliation is in git history.)
