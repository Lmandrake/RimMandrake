# WEBWORK_DEAD_GIANT_BUILD_1 — They Ate the Colossus: the wrapped urraveth skeleton, read bone by bone

Caused by `WEBWORK_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.webwork`. Design:
`design/Jawa/worldbuilding/biomes/webwork_bedazzle_review_2026-10-02.md` §5 idea 2 (GPT, "They Ate the
Colossus"), §8. Ruling: **the dead giant the spiders ate** (decision taken by question card 2026-10-02
07:17 PDT): *a wrapped skeleton bigger than a building, read bone by bone until you see what killed it.*
⛔ **Not** the living morravell (§3): it was not chosen and is not to be built. No living giant.

Mark 5 (GIANT beast), met as evidence: the owners ate it. Name **urraveth** (invented, collision-checked
in the review: none in `src/`, `design/` or Wookieepedia; artpipe `find urraveth` 0 hits, probe `korrum`
hits, 2026-10-02).

## spec

1. **A kind of site, never a worldgen feature.** A map `GenStep` (`RM_GenStep_UrravethRemains`, the shape
   of `RM_GenStep_WebworkNest`) places one wrapped skeleton on a Webwork map with a chance (Mod
   Settings, default about 1 in 4 maps). Never placed by touching the planet, never "one designated
   map". Needs open ground about 15 x 9 cells; skip the map if none fits (log once, no error).
2. **Several bone pieces, each its own building** (free tier, `RM_Urraveth_*`): skull, neck run, two or
   three spine/rib sections (the ribcage is walkable under, impassable at the ribs), pelvis, two limb
   piles. Each piece is **silk-wrapped** (a wrapped state with its own graphic) and minifies to nothing:
   too big to haul. Total footprint larger than any colony building (the point is scale). Static art, one
   facing each (south), drawn huge.
3. **Read bone by bone (inspection).** Each wrapped piece carries an examine job (vanilla
   `CompStudiable`-style progress, or a custom `JobDriver_ExamineRemains` if the vanilla study comp will
   not take a non-Anomaly building: 🔴 UNMEASURED, read `CompStudiable` in RimSage first). Finishing a
   piece cuts its wrapping (graphic switches to bare bone), yields a small stack of thrixweave
   (`WEBWORK_BASE_PORT_BUILD_1`; amount a Mod Settings number) and records one chapter of the death in a
   saved `MapComponent` (`RM_MapComponent_UrravethReading`). The chapters, in the order the pieces say
   them, are GPT's: **pinned** (limb piles: snapped legs, silk anchor stubs), **bound** (ribs: wrapping
   laid in living layers), **cut** (neck/skull: mandible scoring on the bone), **eaten** (pelvis/spine:
   scraped clean from inside). Each finished piece sends a short letter naming its chapter.
4. **The last wrapping.** When every piece is read, a final examine on the skull opens it and the
   component reports complete: a letter tells the whole death in one paragraph and the map draws the
   urraveth's outline (a one-time overlay or filth line tracing the body over the remains) so the size
   reads at a glance. The site's lesson is the biome's: the ollathrix took a creature bigger than a house.
5. **Loaded bones creak and can collapse, with warning.** Each piece has a load value: pawns standing on
   or under it, items stored on it, and any adjacent piece removed (deconstructed for bone) or heavily
   damaged. Past a threshold the piece enters **creaking** for a warning window (Mod Settings, default
   about 6 in-game hours): a creak sound, a dust mote, an inspect-pane line with the time left and a
   message. If the load is not taken off before the window ends, the piece collapses: damage to pawns
   and things in its footprint (scaled like a vanilla roof collapse), the piece becomes bone rubble
   (filth + a chunk), and pieces it supported start creaking in turn. Nothing collapses without the
   warning first, and no collapse happens while nobody is near (unloaded bones are stable forever).
6. **Readable signs.** The wrapped silhouette from across the map, the bare bone after each reading, the
   chapter letters, the creak and the dust, the outline at the end.
7. **Mod Settings:** on/off; site chance; thrixweave per piece; warning window; collapse damage.

Reuses: the nest GenStep shape, vanilla study/examine, vanilla roof-collapse damage maths, thrixweave
(`WEBWORK_BASE_PORT_BUILD_1`). New code: the reading component, the load/creak state, the outline.

Depends on: `WEBWORK_BASE_PORT_BUILD_1` (thrixweave). Art:
`infrastructure/artpipe/art_lists/webwork_turn1_2026-10-02.csv` (`RM_Urraveth_*` rows).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded in the Webwork functional script:
- Forcing the GenStep on a test Webwork map spawns every `RM_Urraveth_*` piece (count equals the def
  list), all in the wrapped state; with site chance 0, a generated map holds none. A planet/world read
  shows no change (no tile, landmark or mutator written).
- Completing the examine job on one piece: that piece reports `wrapped == false`, the reading component
  lists exactly that piece's chapter, a thrixweave stack of the configured size exists at the piece.
- After all pieces and the final skull examine: the component reports complete with four chapters in
  order (pinned, bound, cut, eaten) and the outline exists.
- Load: spawning enough pawns on a rib section sets it `creaking` with ticks-left equal to the configured
  window; removing them before it ends clears the state with no damage; leaving them past it collapses
  the piece (the piece is gone, rubble spawned, a pawn in the footprint took damage) and its supported
  neighbour reads `creaking`.
- A piece with no load stays non-creaking across 60,000 simulated ticks.
- Each Mod Settings toggle off removes exactly its effect.
