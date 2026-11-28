# TheSump: next version (after the current build)

Divergent work: anything that extends the current vision of TheSump. Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** No version opens from this file: his review of the scope comes first.

## SUMP_INHABITED_NOTES_1: the Sump slice of the Inhabited injection: Sump factions more present, tar-expedition ruins, refinery attempts, miserable moisture farmers (moved from the ledger 2026-11-27)
- **Title (ledger):** "Sump Inhabited injection notes (owner, 2026-09-24, for later): junkers/Jawa/deep tribes/Black Star more present; tar-expedition ruins, refinery attempts, miserable moisture farmers".
- **Filed:** BENCH, 2026-09-24T13:49:59Z, kind design, caused by `SUMP_DESIGN_SITTING_1`. The notes are his, from that sitting, scoped by him "for later".
- **Note** (BENCH, 2026-10-29): "Done when: each of the owner's 2026-09-24 injection ideas (junkers, Jawa, deep tribes, Black Star presence; tar-expedition ruins; refinery attempts; miserable moisture farmers) is either filed as a RM_TheSump structure/faction-injection item or folded into the Sump roster sitting spec, and this item is closed pointing at them."
- **Sweep:** home `mod:TheSump`, group `inhabited-notes` (2026-11-24).
- **Two mods:** the content is the Sump's data; the machinery that places it is the Inhabited mod (`src/RimMandrake/Inhabited/`, item `INHABITED_AUGMENTATION_BUILD_1`). Inhabited has no design folder, so the entry lives here. When the Inhabited pass reaches the Sump's tiles, it takes this entry.
- **Watch out:** part 1 (faction presence weighting) is faction work. It waits for his word that faction work starts. Parts 2 and 3 are not faction work.
- **Acceptance test:** none, design notes for a later pass; the ticket's verify and criteria sections below are the bar to write when the version opens.
- **Moved whole from the ledger 2026-11-27** (Conductor call on the doubtful tickets of `design/pre_design_concepts/moved_2026-11-26.md`). The prose file follows, verbatim, headings demoted.

### SUMP_INHABITED_NOTES_1 — the Sump's cast of inhabitants, for the Inhabited injection later

Owner, 2026-09-24, typed in chat during the Sump sitting — his words verbatim, and
he scoped them himself: *"Those are notes for Inhabited injection later."*

> "Second thing. For this biome it should reward players who enjoy their colony
> being dirty, messy, idiosyncratic. It should frustrate players who want neat,
> tidy, controlled. The world factions that align with that are junkers, Jawa, deep
> tribes, black star. So they should be more present. Those are notes for Inhabited
> injection later. Old ruins of tar gathering expeditions. Attempts at refineries.
> Some rather miserable moisture farmers trying a go at it."

#### what this is

The Sump slice of the Inhabited work (`INHABITED_AUGMENTATION_BUILD_1`, the tile
augmentation matrix + structure archetypes). NOT now-work — it activates when the
Inhabited injection pass reaches the Sump's tiles.

1. **Faction presence weighting**: junkers, Jawa, deep tribes, Black Star are the
   Sump-aligned factions — more present here than their planet baseline.
2. **Structure/site content**: old ruins of tar-gathering expeditions; attempted
   refineries; some rather miserable moisture farmers trying a go at it. Map to the
   structure archetypes in `design/Jawa/worldbuilding/structure_procedural_spec.md`
   (mining-site/homestead families are the near templates) rather than inventing
   new archetype machinery.
3. **The play-style law behind it** (binds the mechanics too, recorded on
   `SUMP_TAR_NASTINESS_1`): the biome rewards dirty, messy, idiosyncratic colonies
   and frustrates neat, tidy, controlled ones.

#### verify

When the Inhabited pass covers Sump tiles: the four factions' presence is measurably
weighted up there, and the three site flavors exist as placeable/placed content.

#### criteria

A walk across the Sump reads as a place the tidy gave up on and the messy call home.

