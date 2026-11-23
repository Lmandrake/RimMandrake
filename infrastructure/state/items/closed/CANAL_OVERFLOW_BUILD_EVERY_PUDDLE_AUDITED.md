# CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED — overfilled canals spill onto the ground

Owner, 2026-10-21: *"Do a design pass on what we could do when a canal is overfilled. Is it possible to
have it actually spill out onto the world?"* The design pass is done. This item is the BUILD, and it is
**not authorized yet**: it waits on the owner decisions D1–D10.

## spec
`design/RimMandrake/canal_overflow_flooding_2026-10-21.md`. §6 (the GPT review, as taken) overrides §3–§4
wherever they differ.

## criteria
- Stage 0 is the build-pinned integration spike: temp-terrain side effects and costs, measured.
- Stage 1 is the water-only kernel with atomic dL transfers. It conserves to the dL, with
  back-pressure refusal and no destroy.
- Persistence: a save/load continuation gives the same trajectory as an uninterrupted run.
- Settings OFF behaves exactly as today, and turning a spill OFF never makes water vanish silently.
- The live acceptance rows are §4 stage 4 of the spec, as amended by §6 items 10 and 12.

## carried faults (fix with the build)
`Flood_FlowWorks` has undisclosed exits: expiry, an empty frontier, or a missing def with volume left. It
also carries a float-notch volume, unsaved refusals and a global `Rand`. Its P14 comment wrongly claims
that a spill over natural water is reachable (spec §1.2 and §6 item 15).

## NEXT
`CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` — proposed, owner decisions D1–D10 open; NEXT: put D1–D10 to the owner as question cards.
