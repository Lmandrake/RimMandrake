# SUMP_TAR_HYDROLOGY_1 — how the tar flows: the Sump on FlowWorks

Eight owner rulings, 2026-09-24, post-sitting flow round (his framing, typed:
consider *"how the flow works on the rest of this biome since making tar
[moats] was one of the original inspirations of that particular mod and all the
places that the tar liquid might go in terms of an entire ecosystem if oceans
and rivers were made of tar"* — *"as well as even things like tar rain"*).
Engine ground: FlowWorks pulsed spread (sort+overflow depth grid, no per-tick
sim), `RM_Tar` registry row at Heavy viscosity, tar→chemfuel at FOUND
refineries (`liquids_framework_design.md` — and the found-refinery set-piece now
has its Inhabited fiction: "attempts at refineries," `SUMP_INHABITED_NOTES_1`).

## the rulings

1. **Tar rain — in the MOD, not this scenario.** Typed, verbatim: *"Tar rain is
   part of mod but not this scenario."* ⇒ `RM_TheSump` ships a tar-drizzle
   weather (coats terrain, tars pawns, roofs matter — feeds the solvent
   economy); the Ash'karr campaign scenario keeps it OFF. First explicit
   mod-vs-scenario feature split; sheet ban 4 ("no rain") stands untouched for
   the campaign — the ban was about water, and the scenario sees no tar rain
   either.
2. **Accumulation: belches only** (card). No background seep gain; the map's tar
   level changes only through belch events (and burning/removal). No slow-drown
   background pressure.
3. **Flood fronts cool to glass** (card). A belch flood self-limits: its edges
   harden into walkable glass-reach terrain, the middle stays soft — every belch
   rewrites the map, and natural glass is the process the glasswalk imitates.
4. **Full canal-work** (card). Players dig channels and gates for `RM_Tar`:
   drain a dig claim, feed the moat and refinery, flood a raider approach on
   command (FlowWorks' own weaponized-gate v1 idea, now sited here).
5. **Fire follows the network; gates are firebreaks** (card). Lit tar propagates
   along connected liquid — a lit canal burns to its gate, a lit pool to its
   edges. Gate placement is life-and-death craft; a belch during a moat-burn is
   a genuine catastrophe.
6. **Edges are sinks, never sources — the FlowWorks edge law.** First typed as
   *"Only outflow."*, then clarified in full, typed, verbatim: *"What I mean is
   that a canal, when dug to the edge of the map, can serve as a sink. It can
   remove any kind of liquid by allowing it to flow to some other map. However,
   we should not assume that another map will be a source of anything at the
   edge. So that is why it is a sink only. Sources can be as rich as needed on
   the local map. And if we are next to an ocean, it should already be on this
   map, connected to a canal as effectively an infinite source."*
   ⇒ For the Sump: no inflow seams — the tar's arrival stays geological and
   unseen; sources are LOCAL (seeps and belches, as rich as the design needs);
   a canal dug to the map edge drains any liquid off-map — the player's tar
   disposal; and the Deep Black mere (ruling 7), canal-connected, is the
   biome's effectively infinite on-map source. This is engine law for ALL
   FlowWorks liquids, not a Sump special — noted on
   `FLOWWORKS_BUILD_PROGRAM_1`.
7. **The Deep Black** (card): a landmark-scale unbroken deep-tar mere — beast
   country, undiggable from shore, the biome's "ocean" at MAP scale. ⛔ No new
   world-map body; the frozen world stays untouched (the "world-map body too"
   option was offered and not taken).
8. **The living map** (card): slow responders after every rewrite — soffeth
   rings grow at new seeps, mouse-lines re-route, flora margins migrate to new
   edges over days. The literacy game stays true after every belch.

## engineering-tier questions (not carded — build's discretion, flag surprises)

- Depth grades of tar vs the D/F depth primitives and pits: does a pit dug in
  the Sump fill with tar? (`PIT_SUPERDEEP_COLLAPSE_1` owns pit law.)
- Wading rules: entering shallow tar = mire + tarred hediff
  (`SUMP_TAR_NASTINESS_1`), never a swim.
- Heavy-viscosity `ticksPerTile` tuning for oozing floods and canals.
- The found tar-cracking refinery set-piece on Sump maps (industry found, not
  built) — fiction already in `SUMP_INHABITED_NOTES_1`.
- Temperature gating of flow/hardening (glass fronts imply cooling logic; keep
  it event-shaped, no per-tick sim — pillar 2).
- Worldmap tanker-raid target ("fly to that tar lake"): the Sump's tiles serve
  without a new world body, per ruling 7.

## verify

Quicktest: a belch pulse spreads by depth rules and leaves a glass rim; a canal
carries tar through a gate and stops at a closed one; igniting a connected canal
burns to the gate and no further; the mere generates as one landmark expanse;
tar-rain weather exists in the mod and is absent from the campaign scenario
preset; indicator flora re-seed near a new soft area within days.

## criteria

The tar is one connected, steerable, burnable, self-healing system — the mod
that was inspired by tar moats finally gets its tar world.
