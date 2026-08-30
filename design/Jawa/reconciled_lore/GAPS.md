# Gaps — genuinely unsettled, for the owner

Nothing here was invented or resolved by the reconciliation pass. Each entry
names what turns on the answer. Ordered by how much downstream work waits.

## Design-shaping

1. ✅ RULED (owner, 2026-08-30): **the Deep Desert Tribes are the
   fire-farmers** — burn-cycle agriculture as a nomadic way of life (follow
   the burns, harvest the flush). One re-flavor pass over their faction text +
   backstory hooks rides PAWN_FLAVOR_STARWARS_1; no world edits.

2. **Free Droid Enclave geography.** The Geonosian two-outposts ruling gives
   the droids a plateau presence beside their volcanic/poison-springs homes —
   *"whether the volcanic enclaves and the plateau enclaves are one faction or
   a split"* is explicitly unresolved [2026-08-17].
3. ✅ RULED ALIVE (owner, 2026-08-29): a Droidworks-era faction behavior —
   droid-held tiles get Biotech-polluted ground and fouled water. Filed as
   DROID_TILES_SOURED_TERRAIN_1, sequenced with Droidworks phase 3.
4. ✅ RULED DEAD (owner, 2026-08-29): Royalty's player-facing systems are off
   as a decision, not a side effect. canon.yml `royalty.dead_ruled`.
5. ✅ RULED (owner, 2026-08-30): **v1 is OPEN-ENDED** — arcs provide climaxes,
   nothing rolls credits; authored endings (the god-map roads) are v2. The
   pressure systems (pursuit cadence, pride-crisis) give late-game shape.
6. ✅ RULED (owner, 2026-08-29): zero ambient Anomaly; the Assailant dungeon
   gets the fleshmass exception, and the sarlacc may draw on it too.
   canon.yml `anomaly_content.boundary_ruled`.

## Ship-mind arc (the forgotten_war open list, still open)

7. ✅ RULED (owner, 2026-08-29, canon.yml cradle_memory): the TEMPLE — the
   Cradle substrate — remembers when it was whole and one; nine now dwell
   within it, speaking, and no unified voice remains. None of the nine seeks
   unity or merger. (The nine know they are nine the way housemates do.)
8. ✅ RULED (owner, 2026-08-29): the crew know the vessel is ANCIENT; the
   Rakatan story is not known at start — it is learned FROM THE SHIP as events
   unfold, surfacing from the substrate's memory of its whole era.
9. ⭐ SKETCHED, not yet canon (owner, 2026-08-29 — full register in
   divine_satiation_engine.md "in front" section): engagement makes a god
   louder; crew behavior picks who is "in front" per map; ship lights signal
   it; ship rules (weapons, fuel, raids) enforce it; hologram room for
   messages; landing = judgement of the past map. Awaits canonization at a
   bench sitting.
10. ✅ RULED NO (owner, 2026-08-30): the ship NARRATES, never converses — the
    purpose cannot be summoned, questioned, or bargained with; addressing it
    yields only narration about the attempt. canon.yml cradle_memory.

## Deadline-bound

11. **Giant ants at the world screen.** `GiantAnt_Faction` is zeroed by
    default; a faction absent at world creation can never be added. Tick it to
    1 at the freeze (ants exist as unbuilt background) or accept that v2 ants
    need a new world.
12. **Player-side `VME_Nomad`** (`DEPLOY_SALVATION_RID_1`): the tribes carry
    it; the player .rid does not, and the −50-mood hazard is real only on the
    player side. Decide before the .rid is loaded at the freeze.

## Smaller, filed

13. Crystalline cavern glow: bioluminescent (decay-gradient's) or mineral
    (the crags') — either is good; deciding it is worth one line.
14. The Junkers' water doctrine still assumes universal thirst (the one
    faction the W-audit could not fix from existing text).
15. Industrial water draw (W7) — vats and biosculpters; matters only when
    water is tracked (v2), noted so it is not invented twice.
16. setting_physics still-open: what jams and how visibly (L12); how long a
    lightsaber takes through a bulkhead (L3); does Faraday-type armour help
    organics against lightning (L16).
17. ISEKAI grant-items dispensing `Jawa_` traits through its generic comp —
    owner's later call [flagged 2026-08-29].
18. Stale Setdown machinery: `ashkarr_paint.py` HOME_LATLON abort-guard and
    the populate/repair landmark placement still act on the struck start
    [flagged in canon start_struck]; ripping them out needs a ruling.
19. `jawa_society.md` §4.2b ThoughtDef proposals are keyed to `OuterRim_Jawa`
    — substitute `MandrakeJawa` at build (known staleness, recorded there).
20. **Droidworks assumptions 1–19** await the owner's pass:
    `design/Jawa/droidworks_assumptions.md`.
