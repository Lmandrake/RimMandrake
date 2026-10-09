# TWILIGHT_WELL_AVOIDS_CURRENT_1 — TB-3: twilight wells avoid the current lane map

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row TB-3 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| TB-3 | Twilight wells can open in the middle of a current lane, because they avoid a "channel bed" floor that has never been built. Ask the current's own lane map (which exists and is saved) as well. | nothing | S | low | TerminalBiomes | `RM_MapComponent_WellLedger.cs:197,208-211` tests tag `RM_ChannelBed`; `RM_BankSilt.xml:7` says RM_ChannelBed is "still unbuilt"; `RM_MapComponent_ChannelCurrent` already has `HasCurrent`/`IsSinkCell`. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

- Offline: build clean; IsChannelBed now also true where RM_MapComponent_ChannelCurrent.HasCurrent (toggle twilightWellAvoidsCurrent).
- L2 (owed, bridge): open many wells on a Twilight map; none inside a lane.
