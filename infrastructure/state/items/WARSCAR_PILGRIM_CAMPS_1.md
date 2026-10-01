# WARSCAR_PILGRIM_CAMPS_1 — the pilgrim camps open the Scarlands ladder (campaign tier)

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.10. Rung texts: `warscar_bedazzle_cast_2026-09-30.md` §6B, accepted
as written by card 2026-09-30; build the texts from that section, never from an agent's own pen.

## spec

1. **`RUT_PilgrimCamp`**: a small prefab set (cold fire, bedroll, a body sitting upright facing the
   Cathedral, a journal) placed by a genstep on `RUT_Scarlands`, and as a world `SitePartDef` for
   camps at authored locations on the fixed planet.
2. **`RUT_PilgrimJournal`**: a readable item (a read job, or `CompAnalyzable` to stay in one family).
   Reading calls **`GameComponent_LoreStage.AdvanceStage("Scarlands")`** — the missing caller of the
   shipped `RUT_ScarlandsLadder` (5 rungs, placeholder texts, no gate wired today).
3. **The rung texts** replace the five placeholders in `RUT_ScarlandsLadder.xml` once the owner has
   edited the drafts. Per R25 they let the player infer and never tell; §GM never in a description.
4. Journals are also **Antiquities artifacts** for the Reading Station, so the campaign's two lore
   systems share one item route.
5. **Readable sign:** the body in each camp stays. Pilgrims never vanish; they are found.
6. **Mod Settings:** camps per map.

## criteria

- Reading a journal advances the Scarlands stage by one (state read on `GameComponent_LoreStage`) and
  the biome description changes.
- Five camps read in sequence walk all five rungs; a sixth does nothing.
- The rung texts in the shipped XML match the owner-edited cast bible §6.

## ruling (card 2026-09-30)
Cast bible section 6B text is ruled final (accepted as written, decision taken by question card 2026-09-30) and is the build source; ship verbatim, not as placeholders. Source: design/Jawa/worldbuilding/biomes/warscar_bedazzle_cast_2026-09-30.md.
