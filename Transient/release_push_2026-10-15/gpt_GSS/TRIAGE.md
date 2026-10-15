# GSS pre-release GPT consult — triage (BENCH, 2026-10-15)

Five consults (`answer_A.md`, `answer_B1.md`, `answer_B2.md`, `answer_C.md`, `answer_D.md`; B timed out once at 585 s
and was re-split into B1 + B2). 53 findings. Every one was checked by reading the code at HEAD `21abf9dd8e` (paths
under `src/RimMandrake/GimmeSomeSlack/Source/` unless shown). GPT findings are evidence, not facts; several severities
were changed.

- **CONFIRMED**: I read the code and the mechanism is real (the player-visible effect may still be unmeasured; noted).
- **PLAUSIBLE**: the mechanism needs a live or offline check to decide; the check is written.
- **REJECTED**: the reason is given.

**Totals: 33 CONFIRMED, 15 PLAUSIBLE, 5 REJECTED.** Filed as 13 themed items (one item per theme, each
naming its finding IDs, so the queue does not get 48 one-line items).

## Top by severity

| # | finding | sev | verdict | item |
|---|---|---|---|---|
| 1 | C3: shock contact cells include the HANGING part of a fallen wire, whose points carry the insulator height as extra +Z (`AerialMath.LayFallen`: `g.Z + h*k*k`). `RebuildContacts` (`RM_FallenWireShock.cs:66-70`) takes every `l.Pts` point, so pawns 1-3 cells NORTH of a mast with a live fallen wire are knocked out (a weak heart dies) while standing under thin air. | high | CONFIRMED | `GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR` |
| 2 | D3: with the cables master OFF, the designator style getter `Patch_DesignatorBuild_StyleGetter_Conduit` (`Aerial/ConduitStylePicker.cs:371-374`) is not gated (the menu patch at :358 is), and `StandingLamp_<Look>` styles carry their own `graphicData` (`Defs/Aerial/RM_ConduitStyles.xml:134+`). Existing lamps keep GSS art and new lamps still get GSS styles. Breaks the owner's "each master switch brings the vanilla art back at once". | high | CONFIRMED | `GSS_LAMP_STYLE_FIX_OFF_STILL_STYLED` |
| 3 | C5: the power-tap clamp has no `CompFlickable` (`Defs/Aerial/RM_AerialAnchors.xml:241-251`), yet the theft letter says "Remove or switch off the clamp" (`PowerTheftConsequences.cs:58`) and the code gates on `FlickUtility.WantsToBeOn`. The player has no off switch. | medium-high | CONFIRMED | `GSS_TAP_CLAMP_FIX_NO_OFF_SWITCH` |
| 4 | C14: `TapRegistry`'s ledger is STATIC, keyed by `PowerNet` (`Aerial/CompPowerTap.cs:139`, `TapLedger.cs`). `Prune` runs only above 64 entries and `TapRegistry.Clear()` has no caller (grep). After loading another save, the old nets stay referenced, and with them their `PowerNetManager` and old `Map` (memory held for the session). Debits are not mis-paid (new nets are new keys). Same class as lesson 20261015T025544Z. | medium | CONFIRMED | `GSS_STATICS_FIX_OUTLIVE_THE_SAVE` |
| 5 | C2: switching the aerial master off, or re-stringing, does not clear `shockCells` until the next 250-tick sweep; `CheckPawns` (`RM_FallenWireShock.cs:81-85`) checks only `fallenWireShock`, not `AerialSettings.enabled` or that the wire still exists. Up to ~4 s of shocks from a wire that is gone or switched off. | medium | CONFIRMED | `GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR` |
| 6 | D2: `LampsOf` (`Aerial/RM_MapComponent_ConduitRuns.cs:161-167`) falls back to adjacency even when the lamp's `connectParent` is on ANOTHER run, so restyling run B repaints a lamp wired to run A. | medium | CONFIRMED | `GSS_LAMP_RUN_FIX_NEIGHBOUR_PAINTS_IT` |
| 7 | B14: `floorRipple` now defaults to **true** (`GimmeSomeSlackMod.cs:84,126,158`; the 2026-10-06 record says false), and `CordMotion.Ripple` allocates a List and an array per strand per frame. Every outdoor cord pays it by default. Also re-opens the 2026-10-06 A11 render question (rippling cord vanishing when its midpoint is off screen), which was parked on "off by default". | medium (perf) | CONFIRMED | `GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON` |

## All findings

### Consult A — cord graph

| id | finding (short) | sev | verdict | why / check | item |
|---|---|---|---|---|---|
| A1 | No graph edge between two ADJACENT transmitter buildings (`CordWorldAdapter.cs:73-85`) | low | REJECTED | True in code, but nothing visible: adjacent buildings touch, each hooks its own conduit, and liveness is read from the vanilla net per cell. No cord is missing that a player could see. | — |
| A2 | Junction pile wants `max(3, 1+N/2)` connectors but cables cap at 24 (`Core/CordBuilder.cs:859,911`): idle junction boxes on big piles | low | PLAUSIBLE | Offline: a 20x20 pile fixture, assert it emitted >24 connectors AND `CordAudit.ArtFit(...).PileIdleConnectors == 0` (ReviewRound1Checks only covers small piles). | `GSS_CORD_LAY_FIX_HEAPS_IN_DOORWAYS` |
| A3 | A closed degree-2 conduit ring with no device promotes one cell, which `Classify` falls through to `Terminal` (`Core/CordGraph.cs:430-435,598-605`): a frayed "broken" end on an unbroken ring | low | PLAUSIBLE | Offline: reduce a hollow 8x8 conduit perimeter, assert 0 Terminal nodes and no Fray decals. (Depends on the self-loop's degree, not read.) | same |
| A4 | Tree cost is in the corridor hash now, but the dirty mask (`RM_MapComponent_CordGraph.cs:889`) has no `Things` flag, so felling a tree does not trigger a rebuild | low | CONFIRMED | Cosmetic: route updates at the next qualifying event. | same |
| A5 | String-pull `Clear` (`_Shared/SlackGeometry/CordPlanner.cs:157-166`) tests clearance only, discarding A*'s tree detour | low | CONFIRMED | Cords lie through tree cells (trees are walkable; not a north-star breach). | same |
| A6 | Edge cache key lacks `BlockKind`: a wall swapped for another impassable kind keeps the old dive plate | low | PLAUSIBLE | Reachable with Replace Stuff (in-place wall swap). Offline: lead through Wall, change crossed cells to Device, compare incremental vs fresh build decals. | same |
| A7 | Cache key lacks `HomeX/HomeZ`: a re-hung wall attachment keeps a lead ending under its old wall | low | PLAUSIBLE | Offline: change only HomeX/HomeZ, compare incremental vs fresh geometry. | same |
| A8 | Visible dirty event after this frame's rebuild is dropped (`builtFrame` latch + on-screen early return, `RM_MapComponent_CordGraph.cs:892`) | low | PLAUSIBLE | Needs two changes in one frame from another mod's update; check: bridge action that rebuilds, changes a visible wall, regenerates; compare to fresh build after 2 frames. | same |
| A9 | Long-run (>40 cell) end heaps check clearance only, and the replaced ramp ignores doorway pins (`_Shared/SlackGeometry/CordLayer.cs:426-462`): heaps can land in a doorway, against design §8 "no loops or heaps in the doorway" | low-med | CONFIRMED | Offline seed sweep: a 45-cell cord through a door 2-4 cells from an end; assert no heap overlaps the door cell. | same |
| A10 | Tangle geometry rebuilt on every rebuild even with all edges cached; connector placement O(n^2) | low | PLAUSIBLE | Offline benchmark: repeated unchanged builds of a ~5,000-cell field, time per build. | `GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON` |

### Consult B1 — cord rendering

| id | finding | sev | verdict | why / check | item |
|---|---|---|---|---|---|
| B11 | A styled conduit's `ThingStyleDef` graphic escapes the invisibility swap | — | REJECTED | GSS's conduit styles are graphic-less markers by design (`RM_ConduitStyles.xml` header: "no graphicData, so Thing.Graphic keeps the def's own (invisible) graphic"); no mod on the lists styles conduit with art. | — |
| B12 | Shader-sway strands skip the LOD path (`SectionLayer_RM_MessyCords.cs:125-140,162`) and vanish at far zoom | low | PLAUSIBLE | Live: shader sway + LOD on, a wall-terminal hanging strand; at near and far zoom read enabled submeshes + dynamic draw membership; exactly one representation each. | `GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT` |
| B13 | Hookup to `IsOtherConduit` (HiddenConduit, excluded defs) is classed `PatchCable` and the prefix PRINTS a visible cable (`ConduitVisuals.cs:91-94,191-206`) | medium | PLAUSIBLE | Depends on vanilla reaching `PrintWirePieceConnecting` for HiddenConduit. Live: a consumer 3 cells from hidden conduit, regenerate its section, read `HookupCablesPrinted` delta and screenshot; expect 0. | same |
| B14 | `Ripple` allocates per strand per frame, and floorRipple is ON by default | medium | CONFIRMED | See top-7. Check: allocation sample paused, ripple on vs off, 500-cord outdoor base. | `GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON` |
| B15 | `Whip` rescans the snap schedule from t=0 each call (`Core/CordMotion.cs:44-58`); ~t/1.3 s iterations per tail per frame until the 10,000 s wrap | low-med | CONFIRMED | Offline: count loop iterations at t=1 vs t=9000. Late in a session, ~7k hash steps per whip tail per frame. | same |
| B16 | Static `PrintedStatic` (`SectionLayer_RM_MessyCords.cs:67,96`) is never pruned; removed maps' section keys and strand-key strings stay for the session | low | CONFIRMED | grep: no removal anywhere. | `GSS_STATICS_FIX_OUTLIVE_THE_SAVE` |

### Consult B2 — mod shell, settings, probes

| id | finding | sev | verdict | why / check | item |
|---|---|---|---|---|---|
| B21 | `PatchApplier` failure forces a setting false and it is saved / reset wrongly | — | REJECTED | No GSS patch carries `[PatchFeature(..., settingsType, field)]` (grep), so `Fail()` never writes a GSS setting. | — |
| B22 | Probe mailbox `request` is static with no game identity; a queued teleport by `thingIDNumber` can fire in the next loaded game | low | CONFIRMED | Harness-only (bridge verbs), but exactly the repeating-ID class. | `GSS_PROBES_FIX_BLIND_SPOTS` |
| B23 | `rect:` audit counts edges by either endpoint but hashes geometry by OWNER only (`GimmeSomeSlackProbe.cs:225,235`): a cord entering the rect is counted but its vertices are never audited | medium | CONFIRMED | Instrument blind spot: M2b "no vertex unwalkable" can be green without seeing incoming cords. | same |
| B24 | Closing settings always runs `RegenerateEverythingNow` on every map (`GimmeSomeSlackMod.cs:188`, via `WriteSettings`) | low | CONFIRMED | A redraw hitch on each close even when nothing changed; unmeasured on the full list. | `GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON` |
| B25 | Unknown-command reply `J.S(cmd).Trim('"')` can emit malformed JSON (`GimmeSomeSlackProbe.cs:138`) | low | CONFIRMED | Probe returns bad JSON for a command ending in `"`. | `GSS_PROBES_FIX_BLIND_SPOTS` |
| B26 | `census` serialises `excludedConduits` as its type name | low | CONFIRMED | Instrument cannot see the exclusion list or its Reset-all. | same |

### Consult C — overhead lines

| id | finding | sev | verdict | why / check | item |
|---|---|---|---|---|---|
| C1 | A victim-net rebuild between a tap's debit (thing tick T) and settlement (net tick reading T) loses that one debit | low (GPT: critical) | CONFIRMED | Real, but it is one tick of energy per victim-net rebuild; not a conservation break that accumulates. Offline: extend the conservation selftest with a key swap between debit and settle. | `GSS_TAP_CLAMP_FIX_NO_OFF_SWITCH` |
| C2 | Shock cells survive master-off / re-string until the next sweep | medium | CONFIRMED | Top-5. Live: fallen live wire, pawn adjacent; restring, then move pawn onto an old contact within 20 ticks; expect no hediff. | `GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR` |
| C3 | Hanging part's screen-height points become ground shock cells | high | CONFIRMED | Top-1. Live: cut a horizontal span, pawn on `floor(top.x), floor(top.z)` (north of the mast base), step 40 ticks; expect no `RM_FallenWireShock`. | same |
| C4 | Fallen wire mesh uses `spanY` for every vertex (`RM_MapComponent_Aerial.cs:513,721-742`): the grounded tail draws above pawns | medium | CONFIRMED | Pawns walking over a downed wire are drawn under it. Offline: assert grounded vertices' y < Pawn altitude. | `GSS_FALLEN_LINE_REDRAW_FLOATS_OVER_PAWNS` |
| C5 | Clamp has no CompFlickable, but the letter and code assume one | med-high | CONFIRMED | Top-3. | `GSS_TAP_CLAMP_FIX_NO_OFF_SWITCH` |
| C6 | Knockback goes away from the tip, i.e. ALONG the wire, and stops at the first contact cell (`RM_FallenWireShock.cs:174-182`): mid-strand contact gets no knockback | medium | CONFIRMED | Breaks the owner's "throws them back a little" on most contacts. Live: pawn mid-tail, knockback 2, read position before/after. | `GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR` |
| C7 | Goodwill accrual charges a whole 250-tick window if ANY energy was drained in it | low-med | CONFIRMED | Intermittent drains are overcharged up to 250x. Offline: `TheftGoodwillAccrue` scheduler test, 1 draining tick per window. | `GSS_TAP_CLAMP_FIX_NO_OFF_SWITCH` |
| C8 | One `caughtBy` slot: biting a second faction forgets the first's discovery and accrual | low | CONFIRMED | Doc says "once per clamp per victim faction". | same |
| C9 | `DirtyCell` clears all lays but dirties one section; a remote fallen tail's fray can stay at the old place | low | PLAUSIBLE | Live as GPT wrote: compare owner section's fray-quad centre with census `tip` after a remote wall + unrelated anchor change. | `GSS_FALLEN_LINE_REDRAW_FLOATS_OVER_PAWNS` |
| C10 | `Alert_WireDown.Culprits` filters `m.IsPlayerHome` | low | CONFIRMED | Player anchors on a non-home map get no alert; the probe's `alert` verb calls `Down(map)` and hides it. | `GSS_AERIAL_HINTS_FIX_SMALL_FIBS` |
| C11 | Placement ghost (`PlaceWorkers_Aerial.cs:28-33`) picks from all anchors; real auto-link filters by look (`RM_MapComponent_Aerial.cs:232`) | low | CONFIRMED | Preview line can point at a pole it will not link. | same |
| C12 | "Re-string cut wires" is instant and free, no pawn job (`CompAerialAnchor.cs:356-366,429-434`); design §2.6: a 300-tick pawn job | medium | CONFIRMED | Design-vs-code; needs the owner's decision (keep instant or build the job). | `GSS_RESTRING_DECIDE_FREE_INSTANT_SPLICE` |
| C13 | Explosion damage to a span has no distance falloff; design §2.6 says `damage x falloff` | low | CONFIRMED | Design-vs-code; same decision item. | same |
| C14 | Static tap ledger holds old `PowerNet`s (and their maps) across loads | medium | CONFIRMED | Top-4. Check: after load, `TapRegistry.Count` must be 0 before any tap ticks. | `GSS_STATICS_FIX_OUTLIVE_THE_SAVE` |
| C15 | `CompAerialAnchor.debugSkipReseed` is static and survives load/new game | low | CONFIRMED | Harness-only: an interrupted negative control leaves real games without the despawn reseed. | `GSS_PROBES_FIX_BLIND_SPOTS` |
| C16 | `DrawLocalDrops` allocates and sorts terminals every frame per visible anchor | low | PLAUSIBLE | Profile paused GC.Alloc on a 200-anchor view. | `GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON` |
| C17 | `SectionLayer_RM_AerialGround.LastPrintedVerts/LastFallenPrinted/LastShadowsPrinted` are static, last-section-anywhere values reported by every map's census | low | CONFIRMED | Instrument can report another map's or another section's count. | `GSS_PROBES_FIX_BLIND_SPOTS` |

### Consult D — styles

| id | finding | sev | verdict | why / check | item |
|---|---|---|---|---|---|
| D1 | Legacy (unstored) members follow a later default change while adopted members keep the old look: one run, two looks | medium | PLAUSIBLE | Live: default Scrapper, unstyled run + unstyled mast, build a styled mast onto it, change default to Industrial; `cstyles`/`styles` must show one look per run. | `GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED` |
| D2 | Lamp claimed by an adjacent run it is not wired to | medium | CONFIRMED | Top-6. Live: lamp wired to run A beside run B; `crestyle` B; lamp `rawStyle` unchanged. | `GSS_LAMP_RUN_FIX_NEIGHBOUR_PAINTS_IT` |
| D3 | Master-off still styles and draws GSS lamps | high | CONFIRMED | Top-2. | `GSS_LAMP_STYLE_FIX_OFF_STILL_STYLED` |
| D4 | Run-style pending queues are not saved | low | PLAUSIBLE | Drained every `MapComponentUpdate` (`RM_MapComponent_ConduitRuns.cs:48`), so the window is about one frame; needs an autosave long-event landing in that frame. Check: bridge spawn + immediate save in one call, reload, compare with a `cprocess`-first control. | `GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED` |
| D5 | Several queued links resolve against the final topology (`RunOf(a, exclude, a, b)`, :254) | low | PLAUSIBLE | "Auto-link selected" creates several links in one action. Check: same fixture processed after each link vs after all; styles must match. | same |
| D6 | A queued link consumed after it was cut or moved maps | — | REJECTED | The queue drains every Update and tick; cut-or-transfer between queue and drain needs both in the same frame. | — |
| D7 | Bulk styled spawn floods each placement's run: O(N^2) | low | PLAUSIBLE | Matters only for a large styled gravship landing. Check: count `RunOf` visits for N vs 2N styled cells. | same |
| D8 | Only `PowerConduit`/`WaterproofConduit` are run members (`ConduitStyles.cs:26`); a modded conduit drawn as cords is a gap in the style graph | low-med | CONFIRMED | Runs joined only through a modded conduit can hold two looks. | same |
| D9 | "Restyle this run" overwrites a lamp carrying another mod's/Ideology's style (null look reads as unstyled, `ConduitStyles.cs:328`) | low | PLAUSIBLE | Only if something else styles StandingLamp. Check: give a lamp a non-GSS ThingStyleDef, `crestyle` its run, assert the style survives. | `GSS_LAMP_RUN_FIX_NEIGHBOUR_PAINTS_IT` |
| D10 | Pile art (strips vs junctions) from the global default | — | REJECTED | `opt.PileAt` per cell from the stored style (`RM_MapComponent_CordGraph.cs:219`) overrides it; only unstyled cells use the default, which is the rule. | — |
| D11 | Last-picked looks are static for the process; a new game starts with the old colony's picks | low | CONFIRMED | `ClearPicks` has probe callers only. Settings text says the default "sets what new games start with". | `GSS_STATICS_FIX_OUTLIVE_THE_SAVE` |
| D12 | Placement probes designate on the CURRENT map but search the given map, and return success with `made == null` | low | CONFIRMED | Harness-only. | `GSS_PROBES_FIX_BLIND_SPOTS` |
| D13 | Join hint cache keyed by cell + frame only (`ConduitStylePicker.cs:261-270`): stale hint for up to 30 frames after a map switch | low | CONFIRMED | Cosmetic. | `GSS_AERIAL_HINTS_FIX_SMALL_FIBS` |
| D14 | `cline` probe overshoots on unequal diagonals (`ConduitStyleProbe.cs:84-85`) | low | CONFIRMED | Harness-only: the scene built is not the one asked for. | `GSS_PROBES_FIX_BLIND_SPOTS` |

## What the consults confirmed is fine (GPT's "checked" lists, spot-read)

The 2026-10-06 fixes A1, A2, A5, A6, A10, A15, A17, A18, A19, A20 and B9 are present. Scribe payloads for spans,
fallen wires, seeds and pending auto-links look complete. Aerial work runs per map, not only on the viewed map.
Production material caches are keyed by def, style and texture, not by thing IDs or ticks. No `.Translate()` keys are
used, so there is no missing-Keyed risk.

## Not covered

Multiplayer sync. Interplay with specific named mods was reasoned about, not tested; no transpilers exist. Selftest and
harness Python were not sent.
