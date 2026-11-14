# RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE

## spec

A design pass for the Designer. `rimflow file --for` takes only a seat, and neither the Designer nor the Conductor is one, so this is filed for BENCH. The Conductor launches the Designer with `role_launch.py run-now --role Designer`.

Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 10, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):

> "I placed WAY too much water over the geyser and it spread over the surface of the ground pretty well. It did end up with random Spilled Water over the surface even though it is touching many open pits. We may want a "helper" to sweep over such situations and "scoop up" some of that water into the pits faster than a slow simulation would have it, a kind of shallow/spilled water helper that helps it find its way to available drains more readily. The ground should also be clearly indicated as wet, however we do that, as should any native terrain next to a pit filled with water types. I then emptied two pits completely (debug Drain option worked fantastic in both pits). But none of the spilled water at the edges of the pit dripped back in. However, over time, we did watch it evaporate off the ground (I think it was likely evaporation) and the height in cm did reduce and it disappeared off terrain completely in places. That was welcome and looked good, though it should leave wetted ground again for awhile. We need a design pass here. Do we still need wetted ground, or do we just use a very thin layer of spilled water to indicate wetted and let that suffice/act like wetted ground? That may be easier than carrying an extra state of "wetted, no remaining liquid" as now. Your advice is welcome here. It would primarily be for its effects on plants/agriculture."

Conductor advice 2026-11-14: prefer ONE state. Keep a thin film as the wetness itself: below a small depth it is drawn as darkened wet ground instead of water and evaporates slowly, so ground stays wet for a while with no second state to save, sync or test; plants read film depth. Cost to check in design: many thin-film cells must not keep the water simulation awake.

**DECIDED by the owner, 2026-11-14 12:01 PM PST** (follow-up ruling, same words file):

> "I agree with your assessment: ALL game wetness should now migrate to a thin film. That means that when a natural body of water is drained, it reveals "Mud" surface that retains that thin film of water as "wet mud" itself, then this dries. That also means some terrains may look different when water is over them, and this makes sense. Wet and dry versions of some terrain will implicitly make sense, while things like Tile and Cement will not change. This is probably for next version in the relevant mods."

The one-state question is closed: there is no separate "wetted, no liquid" state. Every source of game wetness becomes a thin film.

The pass must design:
1. **The film.** Below what depth a film is drawn as wet ground instead of water, how fast it evaporates, and what plants and agriculture read from its depth. It must also check that many thin-film cells do not keep the water simulation awake.
2. **Migrating every wetness source to the film.** This includes the existing two-squares wetting (`FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP`) and any other "wetted" state in the relevant mods.
3. **Mud under drained natural water.** A drained natural body of water reveals Mud. The film it keeps makes that Mud wet mud, which then dries.
4. **Wet and dry looks per terrain.** Some terrains get a wet look and a dry look. Tile and Cement do not change. The pass lists which terrains get which look.
5. **A sweep helper** that moves shallow spilled water into nearby open pits faster than the slow flow does. This includes water sitting at the lip of a pit he has just drained.
6. **Native terrain next to a pit holding water** reads as wet.

KEEP bars (approvals, the same look):
- "debug Drain option worked fantastic";
- the evaporation "was welcome and looked good".

Existing item to fold or reconcile: `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP` (proposed). Ground within two squares of a filled canal is wetted by Stillsand's spilled-water technique.

Design Version class: Divergent (next version), by his own "probably for next version in the relevant mods". The film migration, the mud and the wet and dry looks fall under that. Whether the sweep helper and the wet rim next to a pit wait with them, or land in FlowWorks 0.1.0, is not decided here.

Build effort: large for the build after the design; the pass itself is medium.

Acceptance test: none. This is a design pass, and its output is a design doc, not code. The build items that follow owe their own tests.
