# Hose port: GimmeSomeSlack → FlowWorks — FINAL design (2026-10-10)

status: FINAL (v2 + independent review + combined GPT review, merged). Next: owner card for §6 questions, then port step 0.
Item: `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST`. Design only: no mod code is written by this pass.
Owner order (typed 2026-10-10): *"send the improved version to GPT along with all of FlowWorks for a combined review.
Finally combine that design"*.

**How to read this document.** The base text is v2, `design/RimMandrake/hose_port_to_flowworks_design_v2_2026-10-10.md`
(068edd3af), which already applies the independent review `design/RimMandrake/hose_port_to_flowworks_review_2026-10-10.md`
(M1-M9, S1-S12). §3 below **replaces** the named v2 sections or sentences; where this document and v2 disagree, this
document wins. §4 (increments) and §6 (owner questions) replace v2 §10 and §11 whole. Paths are repo-relative to
`src/RimMandrake/` unless they start with `design/`. Every GPT finding was checked against the code before it was accepted
(§2); line numbers are at bench HEAD `62c5a31f7`.

## 0. Changelog v2 → FINAL

- **Relay chains (G1.1, BLOCKER).** A receiving relay reel has no native port, so v2's "both ports non-null" killed every
  chain. A relay reel now has an *inlet* vertex: its feeders' links end on it, and its own link starts from it (§3.1).
- **Tanks stay endpoints for hoses too (BENCH, merge pass).** v2's "every tank reached follows its links" would merge two
  lines through a tank — the accident v2's own M1 fix forbade. Links are never traversed from a tank (§3.1, Q7).
- **Native vs visual ports (G1.7).** Only FlowWorks' own pipe, tank and machines conduct; VE PipeSystem / DBH couplings stay
  drawn but never enter the net (§3.1).
- **Link eligibility = a valid lay (G1.6).** A hose whose lay was refused (`lay == null`) carries nothing, even while
  `Laid`; `Dropped` is defined as not carrying (§3.1).
- **Index refresh (G1.4).** `RM_HoseLinks` is rebuilt from all registered reels (not only from the queried key), so a port
  that changes from null → X or X → Y is found (§3.1).
- **Machine kinds corrected (G1.3).** `CompLiquidReactor` (not "RM_LiquidReaction"); bath benches identified by their
  recipes' `RM_RecipeLiquidExtension`, not by a comp that does not exist (§3.1).
- **Credit at the 11 real mutation sites, per tank leg (G1.8)**; flow lease is monotonic and the union of all credits
  (G1.11); `NetFlow` returns null when idle so debug flow still works (G1.9); the displayed tint is saved, not only the
  last liquid (G1.12); leases clear when a hose is wound, picked up or despawned (G1.13) (§3.2-3.4).
- **Timing bars corrected (G1.10).** "Flat within `releaseTicks`" was false: with shipped defaults the last credit stays
  live 375 ticks, then release 500, then transition 30 → flat at ~905 ticks. Bars now state the real bound (§3.6).
- **Route liveness at transfer (G1.5)**: a route is revalidated on use (§3.5); since liquid networks L2 a dead link bumps the topology revision.
- **Production kernel, not a model (G1.18 / G2.5 / G3.12).** The net rules move into a Verse-free production file
  (`RM_LiquidNetKernel.cs`) compiled into the SelfTest, as `RM_StockMath.cs` already is (§3.7).
- **Increments re-cut (G1.2 / G2.1).** Settings section + import land WITH the move (step 2), and the
  `useFlowWorksPumps` / `defaultFluid` deletions land with real flow (step 6), so every step compiles and keeps a settings
  screen (§4).
- **Style and settings migration (G2.2 / G2.3).** The old GSS global look is imported once into `hose_defaultLook`; GSS's
  bracket-offset injector stays GSS-only, outside the shared style core (§3.8).
- **SelfTest runner adapter (G2.4)**; step-1 visibility gate checks top-level types, not every `public` (G2.6);
  essential-patch failure has a real fallback (G2.7) (§3.7-3.9).
- **Harness (G5.*)**: GSS's `validation.py` support is extracted to a mod-neutral module; the style proof is made
  FlowWorks-standalone; GSS's `proof_all.py` hose coupling is split at 8 named points; log ownership parameterised;
  save-hygiene whitelist is the exact `.Hose.Jobs.JobDriver_*` pair; FlowWorks' SKIP→PASS adapter defect fixed first (§3.10).
- **Move list additions (G1.19 / G5.3)**: three icon paths in `CompHoseReel.cs:91-93`, the graphic class in
  `RM_HoseReelStyles.xml`, three identities in `validation_style_hose.py` (§3.10).
- **Pre-existing FlowWorks defects** the review found (pump pour starvation, converter starvation, bath unpaid craft,
  flood volume, palette exhaustion, heat budgeting, weir item loss, …) are listed in §5 for separate filing; three of them
  gate step 6 because hoses make them common (§5).
- **Totals: 61 GPT findings — 44 accepted into the design, 15 accepted as pre-existing FlowWorks defects (§5; five of
  them fixed inside the port), 1 noted (not port work), 1 rejected with evidence** (G4.1, a "missing brace" that is not there).

## 1. GPT review — how it ran

- Tool: `python3 src/RimMandrake/Utils/gpt_consult.py`, model **gpt-6.1-sol**, reasoning effort **high**, via Windows
  `codex.exe`. It ran (no usage-limit refusal). Five consults in parallel (2026-10-10 23:46, answered in 438-970 s), plus one
  re-run (C5b) for files C5 reported as truncated.
- "All of FlowWorks" was too large for one consult (~3.3 MB), so it was split by subsystem; every consult carried the v2
  design and its review. `build_manifests.py` asserts that every FlowWorks `Source/**/*.cs`, `*.csproj`, `Defs/**/*.xml`,
  `Patches/**/*.xml`, `About`, `Languages`, `validation*.py` and `northstar/*.py` file landed in exactly one consult
  ("FlowWorks files in no consult: none"). Not sent: `Textures/`, `art_source/`, `Tools/generate_liquid_suite.py`,
  `human_review.py`, `review_map*.py`, `selftest_flowworks_*.py` (review/art tooling outside the port), and the
  northstar `*.json` result files (data, not code).
- Exact file lists, prompts, raw answers and a one-command re-run are in `design/RimMandrake/hose_port_gpt_review_2026-10-10/`:

| consult | slice | files | chars sent | raw answer |
|---|---|---|---|---|
| C1 | flow core + hose: GSS `Source/Hose/**`, hose defs, FW `Machinery/**`, `LiquidTypes/**`, `RM_PumpMath`, machinery defs, LiquidDef registry, liquids framework design | 73 | 703,969 | `gpt_C1_flow_and_hose.md` |
| C2 | settings, saves, Harmony, deps, tests: FW Mod/settings, DefOf, csprojs, FW SelfTest, About, Languages, `_Shared` kits, EH def aliases, GSS Mod/LegacyName/DrawOrder/Cord*/StylePicker/AerialStyles/csprojs/3 hose selftests | 36 | 666,082 | `gpt_C2_settings_save_deps_tests.md` |
| C3 | FW top-level `Source/*.cs` (rest) + all `Patches` | 47 | 476,792 | `gpt_C3_flowworks_root_source.md` |
| C4 | FW subsystem sources (Rivers, Superdeep, Quarry, Drilling, ManyWaters, TakenByLand, Pits, Swale) + remaining Defs | 98 | 745,750 | `gpt_C4_flowworks_subsystems_defs.md` |
| C5 | harness: FW `validation.py`, `northstar/*.py`; GSS `validation_hose.py`, `validation_style_hose.py`, `northstar/proof_all.py` | 23 | 777,192 | `gpt_C5_harness.md` |
| C5b | re-run of the 4 northstar files C5 said were truncated (`extensions.py`, `validation_v2.py`, `preflight_flowworks.py`, `player_missions.py`) | 6 | 473,022 | `gpt_C5b_northstar_rerun.md` |

Re-run any consult: `sh design/RimMandrake/hose_port_gpt_review_2026-10-10/run_consult.sh <key>` from the repo root.

## 2. Disposition table

61 findings: 44 ACCEPT, 15 ACCEPT-PRE, 1 NOTE, 1 REJECT. IDs are `G<consult>.<n>` (C5b = `G6`). Verdicts: **ACCEPT** (applied in §3/§4), **ACCEPT-PRE** (true, pre-existing
FlowWorks defect; §5), **NOTE** (true, not port work), **REJECT** (evidence given). "Verified" = the cited lines were read
and say what GPT claims.

| id | sev | finding | verdict | evidence / where applied |
|---|---|---|---|---|
| G1.1 | BLOCKER | relay reel has no reel-side port, so chains cannot conduct | ACCEPT | verified `HosePorts.cs:44` (reel = None); relay found only by `RelayOf/FeedersOf`. §3.1 inlet vertex |
| G1.2 | BLOCKER | step 4 deletes `useFlowWorksPumps`/`defaultFluid` while readers live until step 6 | ACCEPT | verified `HoseFlow.cs:56`, `RM_MapComponent_Hoses.cs:486`. §4 deletions move to step 6 |
| G1.3 | MAJOR | "RM_LiquidReaction / RM_LiquidBath" comps do not exist | ACCEPT | verified `Kits/RM_LiquidReaction.cs:81` `CompLiquidReactor`; `RM_LiquidBath` is static, recipe extension. §3.1 |
| G1.4 | MAJOR | lazy lookup cannot discover a port that moved to a new key | ACCEPT | follows from `CompHoseReel.cs:82-89` re-picking. §3.1 full rebuild per tick-of-use |
| G1.5 | MAJOR | tick-keyed cache can be stale within the tick | ACCEPT (reduced) | a wind/despawn in a job tick can precede a building tick. §3.5: revalidate route links at transfer; no mutation hooks |
| G1.6 | MAJOR | `Laid` with a refused lay (`lay == null`) would carry | ACCEPT | verified `RM_MapComponent_Hoses.cs:202-203`. §3.1 |
| G1.7 | MAJOR | VE/DBH Pipe/Tank kinds would conduct as native | ACCEPT | verified `HosePorts.cs:55-65`. §3.1 native flag |
| G1.8 | MAJOR | Credit sites are the mutations, 11 of them, per tank leg | ACCEPT | verified pump `:152,169,231`, converter `:219,223`, adapter `:135,153`, reactor `:184-185,191`, bath `:148`. §3.2 |
| G1.9 | MAJOR | NetFlow's `false` masks DebugHoseFlow | ACCEPT | verified `HoseFlow.cs:121-125` first non-null wins. §3.3 |
| G1.10 | MAJOR | "flat within releaseTicks" false given lease + release + transition | ACCEPT | verified `HoseMath.cs:1226-1227`, `:52-68`. §3.6 bar text |
| G1.11 | MAJOR | last-writer stamps shorten windows / order-dependent liquid | ACCEPT | §3.2 monotonic lease, union per tick |
| G1.12 | MAJOR | saving `lastLiquid` loses the displayed tint mid-dwell | ACCEPT | §3.4 save `tintLiquid` too |
| G1.13 | MAJOR | stamps survive wind-in / redeploy | ACCEPT | `CompHoseReel.cs:111-126, 533-548` reset state but would not reset new fields. §3.2 |
| G1.14 | MAJOR | pour picks first canal-capable tank, starves later liquid | ACCEPT-PRE (gates step 6) | verified `Building_LiquidPump.cs:184-191, 211-228`. §5 P1 |
| G1.15 | MAJOR | converter returns on first unproductive input | ACCEPT-PRE (gates step 6) | verified `CompLiquidConverter.cs:206-217`. §5 P2 |
| G1.16 | MAJOR | bath completion can skip the debit | ACCEPT-PRE (gates step 6) | verified `Kits/RM_LiquidBath.cs:145-148` silently no-ops. §5 P3 |
| G1.17 | MAJOR | relay discovery (`RelayAt/FeedersOf/Loops`) is not O(1) | ACCEPT | §3.5 relay adjacency built once per refresh; perf budget counts it |
| G1.18 | MAJOR | offline model ≠ production graph | ACCEPT | §3.7 production kernel |
| G1.19 | MAJOR | move list misses icon paths and style graphic class | ACCEPT | `CompHoseReel.cs:91-93` verified. §3.10 |
| G1.20 | MINOR | driver namespace is `.Hose.Jobs.` | ACCEPT | verified `Jobs/JobDriver_CarryHoseEnd.cs:8`. §3.9 |
| G1.21 | MINOR | `minPlumpDwell` has no control yet now drives tint | ACCEPT | verified `HoseSettings.cs:213`. §3.8 |
| G1.22 | MINOR | station reach is position-centred, not footprint distance | NOTE | true (`Building_LiquidPump.cs:73-79`), unchanged by the port; §5 P11 |
| G2.1 | MAJOR | steps 2-4 leave releases with no hose settings screen / import | ACCEPT | §4 step 2 carries settings section + import |
| G2.2 | MAJOR | unstyled reels change look (GSS global → Scrapper) | ACCEPT | verified `Aerial/StylePicker.cs:70`. §3.8 one-time look import |
| G2.3 | MAJOR | shared style core would drag `InjectBracketOffsets` / `AerialMaterials` | ACCEPT | verified `StylePicker.cs:52, 128-141`. §3.8 |
| G2.4 | MAJOR | moved checks call `Program.Check`; FW runner has only `Case` | ACCEPT | verified GSS `SelfTest/Program.cs:34`, FW `Program.cs:69`. §3.7 |
| G2.5 | MAJOR | separate net model cannot prove production | ACCEPT | = G1.18 |
| G2.6 | MAJOR | `grep "public "` = 0 gate impossible (operators must be public) | ACCEPT | verified `Core/CordMath.cs:36-38`. §3.9 gate on top-level types |
| G2.7 | MAJOR | essential patches (save-skip, alias, def alias) have no fallback | ACCEPT | `PatchApplier.cs:84-96` catches and continues. §3.9 |
| G3.1 | MAJOR | pump-fed channel may stall after reload (`driverInputTick` unsaved) | ACCEPT-PRE (plausible; test first) | verified `RM_MapComponent_Excavation.cs:1483-1485, 1196-1200`; the stall path itself not reproduced. §5 P4 |
| G3.2 | MAJOR | LiquidDef/FluidDef mapping unspecified for credits / nozzle | ACCEPT (step 9) | pump already maps via `canalFluid` (`Building_LiquidPump.cs:110-123`); credits use the LiquidDef the pump resolved. Census gates step 9 |
| G3.3 | MAJOR | flood fills a D4 cell for one `volumePerTile` | ACCEPT-PRE | verified `Flood_FlowWorks.cs:333-343` vs `RM_MapComponent_Excavation.cs:1256-1261`. §5 P5 |
| G3.4 | MAJOR | `legacyFloodViaEngineEnabled` off restores terrain race | ACCEPT-PRE | verified `Flood_FlowWorks.cs:333, 353-354`. §5 P6 |
| G3.5 | MAJOR | tar cooling writes glass onto engine-owned cells | ACCEPT-PRE | verified `Flood_FlowWorks.cs:377-390`. §5 P6 |
| G3.6 | MAJOR | palette exhaustion → key 0 → fluid identity changes | ACCEPT-PRE | verified `RM_MapComponent_Excavation.cs:303-319`. §5 P7 |
| G3.7 | MAJOR | fire burn pulse can consume replacement water | ACCEPT-PRE (unverified path) | `RM_LiquidFire.cs:428-450` read; interleaving not reproduced. §5 P8 |
| G3.8 | MAJOR | heat budget starves later excavated / natural cells | ACCEPT-PRE | verified `RM_LiquidHeat.cs:112-134` (prefix from 0 every interval). §5 P9 |
| G3.9 | MAJOR | natural heat cache trusts stale terrain 15,000 ticks | ACCEPT-PRE (unverified hook) | §5 P9 |
| G3.10 | MAJOR | nozzle step needs a sealed-cell (sluice) contract | ACCEPT (step 9) | §4 step 9 tests |
| G3.11 | MINOR | pump proof reads first adjacent tank, not the hose's far tank | ACCEPT | verified `RM_NorthstarProofs.cs:128-137`. §4 step 8 |
| G3.12 | MINOR | offline gate drift | ACCEPT | = G1.18 |
| G4.1 | BLOCKER | `RM_WorldComponent_SweptAway.cs:154` extra `}` | **REJECT** | file is 153 lines, 27 `{` and 27 `}` (counted 2026-10-11); the DLL builds. Probably an artefact of the inlined text. The fix it proposes (both DLLs built at every code step) is already in §4 |
| G4.2 | MAJOR | step 9 needs a deep-sand (water-tagged solid) negative case | ACCEPT (step 9) | `RM_DeepSand.xml:128-158`. §4 step 9 |
| G4.3 | MAJOR | weir washing despawns before placing; failed place orphans item | ACCEPT-PRE | verified `RM_Weir.cs:421-426`. §5 P10 |
| G4.4 | MINOR | second settings owner `RiverSteamMod` not in the inventory | ACCEPT | verified `ManyWaters/RiverSteamSettings.cs:23, 50`. Step 0 inventories every `Mod`/`ModSettings`; hose section goes in `RimMandrakeFlowWorksSettings`, river steam untouched |
| G5.1 | BLOCKER | `validation_hose.py` imports GSS `validation` (`V.Bridge`, `row`, `hrow`) | ACCEPT | verified `validation_hose.py:49,64`; GSS `validation.py:135,153,621`. §3.10 |
| G5.2 | BLOCKER | style proof imports `validation_aerial` / `validation_style` | ACCEPT | verified `validation_style_hose.py:127-130`. §3.10 |
| G5.3 | MAJOR | style offline gate hard-codes file, class, root | ACCEPT | §3.10 |
| G5.4 | MAJOR | GSS `proof_all.py` hose coupling is wider than 5 blocks | ACCEPT | verified `proof_all.py:251-259`. §3.10 split list |
| G5.5 | MAJOR | DECLARED_ROWS + matrix declarations + FW result path need one contract | ACCEPT | §3.10 |
| G5.6 | MAJOR | RL6 requires provider `"relay"` | ACCEPT | verified `validation_hose.py:576-582`. §3.10 |
| G5.7 | MAJOR | log ownership filter treats FlowWorks errors as foreign | ACCEPT | §3.10 |
| G5.8 | MAJOR | H10b/SL2/H11 whitelist inconsistent | ACCEPT | §3.9-3.10 |
| G5.9 | MAJOR | SL4 passes after losing the driver | ACCEPT | §4 step 8 dedicated migration fixtures |
| G5.10 | MAJOR | settings rows need typed registry, not a bool list | ACCEPT | verified `northstar/extensions.py:79-90` (all toggles default `True`). §3.10 |
| G5.11 | MAJOR | FW `validation.py` keeps PASS on a SKIP | ACCEPT-PRE (gates step 2) | verified `FlowWorks/validation.py:128-131`. §5 P12 |

### 2b. C5b (re-run of the northstar files C5 reported truncated)

| id | sev | finding | verdict | evidence / where applied |
|---|---|---|---|---|
| G6.1 | MAJOR | settings registries outside `validation.py` (`extensions.py` registry, `validation_v2.py` defaults, `site_spec.SETTINGS`/`toggles()`) | ACCEPT | `extensions.py:79-90` verified. §3.10 typed registry covers all of them, with an equality check |
| G6.2 | MAJOR | preflight P-B4 passes with a required field ABSENT | ACCEPT-PRE (gates step 4) | verified `preflight_flowworks.py:409-425`. §5 P13 |
| G6.3 | MAJOR | log needles miss the mixed-version line and "Cleaning up invalid job state" | ACCEPT | verified `preflight_flowworks.py:346-351`. §3.10 |
| G6.4 | MAJOR | `_wait` rounds up to 250-tick pulses, so a 60-tick bar cannot be proved | ACCEPT | verified `extensions.py:214-217`. §3.6: discover port ≤ 60 ticks (probe read at exact tick), transfer by next pump cycle |
| G6.5 | MAJOR | mission chain goal reads max of any 3 tanks, not the hose's destination | ACCEPT-PRE | verified `player_missions.py:677-693`. §5 P14; not used as evidence for any hose bar |

## 3. Amendments to v2 (replace the named v2 text)

### 3.1 Net membership (replaces v2 §4.1)

**Vertices.** The BFS walks cells of FlowWorks' universal pipe (as today) and *port things*. A port thing has a **visual
kind** (`HosePorts.Classify`, unchanged, drives the drawing) and a **hydraulic role**, decided only by FlowWorks types:
- `Tank` — `Building_LiquidTank` (incl. `RM_UniversalCargoTank`): added to the result, never traversed through (keeps
  `RM_LiquidNet.cs:14-17`'s endpoint invariant — see "tank links" below);
- `Pipe` — a thing with `RM_UniversalPipeExtension`: its cells enqueued;
- `Machine` — `Building_LiquidPump`, or a thing with `CompLiquidConverter`, `CompLiquidPipeAdapter` or `CompLiquidReactor`,
  or a bench whose ThingDef is a recipe user of any recipe carrying `RM_RecipeLiquidExtension` (resolved once at startup into
  a def set): an origin, never a conductor;
- `None` — everything else, **including VE PipeSystem and DBH things**, which stay visual couplings only (G1.7). Liquid
  enters or leaves those nets through `CompLiquidPipeAdapter`, a Machine. Where a thing has both an adapter comp and a VE
  storage comp, the adapter wins (Machine).

**Links.** A laid reel R contributes one link `inlet(R) — far(R)`:
- `inlet(R)` = R's native reel-side port if `R.Port()` returns a thing with a hydraulic role, **else R itself as a relay
  vertex** when R has at least one feeder (`FeedersOf(R)` non-empty). A relay vertex conducts: reaching it via a feeder's
  link continues along R's own link, and vice versa (G1.1).
- `far(R)` = `RelayOf(R)` (the next reel, as a relay vertex) or `HosePorts.FindAt(end)` filtered to a hydraulic role.
- A link exists only while: hoses enabled; R is `Laid` (`Dropped` and every carry/wind state = no link); **R's current lay
  is non-null** (a refused lay carries nothing, G1.6); both ends resolve to `Spawned` things. Open end = no link.
- The reel footprint never conducts; a stored reel touching two pipe runs does not join them (v2, kept).

**Tank links (BENCH merge finding, not from GPT).** v2 §4.1 rule 2 let "every tank reached" follow its hose links, so a
hose screwed onto a tank in a pipe run joined the run — which breaks the same endpoint invariant M1 protected
(`RM_LiquidNet.cs:14-17`). FINAL: links are traversed from the origin, from pipe cells and from relay vertices, **never
from a tank**. A tank reached by any path is added to the result and stops there. So pump → pipe → tank T —hose— tank U
does NOT reach U; pump —hose→ T and pump-at-far-end —hose→ T both reach T. Selftests pin all three. **Restated on components
(liquid networks L2, `liquid_network_semantics_design_2026-10-11.md` §3.1):** there is no walk "from" anything any more; pipe
cells, relays and hoses are conductors, tanks and machines attach to every component they touch. So the pump's component (the
pipe run) does not hold U, and T, attached to both the run and the T–U hose, has U in its own store (tank–hose–tank is one
component of one conductor). `NetComponentChecks.cs` and `HoseNetChecks.cs` pin it. Q7 is RULED yes (2026-10-11): a tank passes liquid on through a hose screwed onto it with no
pump. Since liquid networks L4 that is done by tank jobs (Empty / Fill, one click on the tank; rev 2 §3.2), not by the old
equalising feed, which is deleted.

**Index.** `RM_HoseLinks` (per map) is reel list → `(inlet, far)` pairs and a `vertex → links` dictionary, read from the
reels' existing 60-tick port caches and `RelayOf`. Since liquid networks L2 it is rebuilt only when its signature (each live
reel's id, inlet and far identity) changes; that once-per-tick-on-use signature check is the backstop that bumps the map's
topology revision. A rebuild costs O(reels), so a port that changes null → X or X → Y is always seen (G1.4); the relay adjacency
(`RelayAt`/`FeedersOf`) is built once in that rebuild and shared with drawing and `Loops` (G1.17).

**Seeding** (v2 rule 1, kept): pipe cells around/under the origin, plus every link whose either end is the origin.

### 3.2 Crediting (replaces v2 §4.2 call sites and stamp rules)

- Credit happens after each **committed move**, one call per tank leg, never on lookup. Since liquid networks L1
  (`liquid_network_semantics_design_2026-10-11.md` §4) every site moves through `RM_LiquidTransfer.Move` and credits only
  inside the block of a Move that returned its units: pump draw (channel, source) and pour (`Building_LiquidPump.cs`
  TryDraw/TryPour); converter input and output (`CompLiquidConverter.cs`); adapter feed and draw
  (`CompLiquidPipeAdapter.cs`); reactor A, B and product (`Kits/RM_LiquidReaction.cs`); bath (`Kits/RM_LiquidBath.cs`); and,
  new with L1, the tank-to-tank move (since L4 the tank-jobs settle, `RM_LiquidNet.SettleTick`, `CreditRoute`). Capture the liquid before a removal (an emptied
  tank clears `storedLiquid`). Never credit item output, venting, terrain-backed baths, or refused moves (G1.8). The C#
  caller-coverage case `Transfer_caller_coverage` (`Source/SelfTest/TransferChecks.cs`) asserts the 11 + 1 sites, and the
  Python lint `selftest_hose_port.py` P9 still checks the 11 tags.
- Stamp = a **lease**: `flowUntil = max(flowUntil, now + 1.5 × cadence)` — monotonic, so a short-cadence credit never
  shortens a longer one; liquids credited in the same tick are a set, and the tint candidate is the one with most units,
  ties by defName (deterministic, G1.11).
- `NetFlow` flowing = `now <= flowUntil`. The hose's `lastMovedUnits/Tick/Cadence` fields of v2 collapse into
  `flowUntil` + `lastLiquid`; `HoseMath.PumpFlowing` gains a lease form (Verse-free, selftested).
- **Lifecycle:** `flowUntil` is cleared when the hose leaves `Laid` (wind, pick-up, drop), on despawn and on a new lay;
  tint identity is kept (it is how the strand last looked) until the state reaches Flat (G1.13).
- Route revalidation: before stamping, each link on the route is re-checked against the eligibility predicate (§3.5).

### 3.3 Flow signal (amends v2 §4.3)

`NetFlow` returns `null` (not `false`) when the lease has expired, so `DebugHoseFlow` still answers in dev tests; a hose
with neither is "not flowing" by `Signal`'s default. Tests: never-credited reel with debug on → plump; 3-hop debug chain;
real flow with debug off throughout the real-flow rows (G1.9).

### 3.4 Tint (amends v2 §4.4)

Two saved fields: `rmHoseTintLiquid` (what the strand shows) and `rmHoseLastLiquid` (the pending candidate) plus
`rmHosePendingSince` (int). On load the strand shows `tintLiquid`. The switch rule (`minPlumpDwell` of continuous
candidacy, "continuous" = credited in every lease window since `pendingSince`) is a Verse-free function. First credit on a
hose with no tint sets it at once (G1.12). Fallback colour for debug flow: `RM_Liquid_FreshWater`, null-safe (v2).

### 3.5 Performance and cache (amends v2 §9)

- **Replaced by liquid networks L2** (`liquid_network_semantics_design_2026-10-11.md` §3.1): the per-origin per-tick cache
  (`RM_NetCache`) is deleted. Components, stores and a predecessor tree per component are kept per topology revision
  (`RM_NetTopologyCache`), bumped by a Harmony hook on every pipe/tank/machine spawn and despawn, by `RM_HoseLinks`' signature,
  and by the pipes/hoses switches; a quiet map rebuilds nothing.
- Every `Credit` and every transfer re-runs the link eligibility predicate on the route's links (O(route length)); a
  failed link drops that tank for this transfer and bumps the revision (G1.5).
- Budget (step 7) now counts the `RM_HoseLinks` rebuild, the relay adjacency and `World()`'s snapshot cost in the map
  component, not only the BFS (G1.17): 20 reels, 4 pumps, 10 tanks, ≤ 0.05 ms/tick mean.

### 3.6 Bars (amends v2 §5.7 new bars)

`NS_hose_plumps_only_from_powered_pump`: power cut → the hose leaves Plump no later than
`1.5 × 250 + releaseTicks + transitionTicks` ticks after the last successful transfer (shipped defaults: 375 + 500 + 30 =
905), and no earlier than `minPlumpDwell` after it plumped (G1.10). `NS_hose_carries_real_units` reads the far tank's
units delta and the credited reel ids from a new pump/hose probe field, not `RM_NorthstarProofs.cs:128-137`'s first
adjacent tank (G3.11). New: `NS_hose_dropped_carries_nothing`, `NS_tank_does_not_bridge_pipe_runs`,
`NS_external_pipe_is_visual_only` (a VE pipe between two native runs does not merge them).
`NS_hose_port_removed` is split (G6.4): the replacement port is discovered ≤ 60 ticks after the rebuild (probe read at an
exact tick, not through `_wait`'s whole-pulse rounding), and liquid moves by the next pump cycle after that.

### 3.7 SelfTests (amends v2 §5.6)

- **Production kernel.** The net's traversal, link eligibility, route recording, cache key, lease and tint-switch rules
  live in `FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs`, Verse-free, over an injected graph interface; `RM_LiquidNet`
  is a thin Verse adapter that builds the graph. The SelfTest compiles the same file (as `RM_StockMath.cs`,
  `Program.cs:15-25`). `HoseNetChecks.cs` asserts against the kernel; a hand model is only an oracle in fuzz (G1.18).
- **Runner adapter.** FlowWorks' SelfTest gets a `Program.Check(bool, string)` shim that records each assertion under its
  moved suite name, so moved checks compile unchanged and the step-2 count compares assertion counts, not `Case` counts;
  every moved suite is invoked from `Main` and a failure sets the exit code (G2.4).
- Kernel cases added to v2's list: tank-endpoint (both directions of §3.1), external pipe between two runs, dropped hose,
  refused lay, null→X and X→Y port change, same-tick wind between two transfers, all four pipe/hose switch combinations,
  mixed liquids in one net, ring termination, lease monotonicity and caller-order independence, save mid-tint-switch,
  redeploy before lease expiry.

### 3.8 Settings and style (amends v2 §8 and the StylePicker row of §5.2)

- The hose settings section + window group + import land in **step 2** with the move; `useFlowWorksPumps` and
  `defaultFluid` stay as inert fields until step 6 deletes them with their readers (G1.2 / G2.1).
- `minPlumpDwell` gets a control in the *Flexible hoses* group (G1.21).
- One-time look import: when `hoseSettingsImported` is false, `hose_defaultLook` is set from GSS's global `style` setting
  read by key from the same settings-file family (`Mod_*_GimmeSomeSlackMod.xml` / `Mod_*_MessyConduitMod.xml`, by the
  enum → look mapping of `AerialMaterials.LookOf`, copied as a 4-row table), else Scrapper (G2.2). No runtime GSS read.
- `_Shared/StylePicker/` holds only the def-agnostic index, menu and patch bodies. `InjectBracketOffsets`
  (`Aerial/StylePicker.cs:52, 128-141`) and anything reading `AerialMaterials` stay in GSS as a GSS bootstrap run after its
  registration (G2.3).
- Step 0 inventories every `Mod`/`ModSettings` class in both mods (FlowWorks has two: `RimMandrakeFlowWorksMod` and
  `RiverSteamMod`, G4.4).

### 3.9 Saves and Harmony (amends v2 §6 and §8 Harmony paragraph)

- Driver whitelist: exactly `RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd` and `…JobDriver_RetractHose`, only as a
  `curDriver` `Class=` value; the same XML-aware helper is used by H10b, SL2 and H11; H11 detects old (GSS, MessyConduit)
  and new class-resolution errors (G1.20 / G5.8).
- **Essential patches.** Save-skip, type alias and def alias are applied outside `PatchApplier`'s soft path and checked by
  `harmony.GetPatchedMethods()` after apply. If save-skip is missing, the hose map component is not added to maps
  (hoses draw nothing, reels keep their saved ends) and one red line names it; if the type alias is missing, one red line
  and the job-cleanup warning remains the only loss (a mid-carry job ends). Step 2's gate asserts all three present (G2.7).
- Step-1 visibility gate: every **top-level type** in `_Shared/SlackGeometry` is `internal` (a Roslyn-free regex on
  `^\s*(public|internal)\s+(sealed |static |readonly )*(class|struct|enum|interface)`); members such as operators stay
  `public` (G2.6).

### 3.10 Harness move (amends v2 §5.4 and §5.7)

- Extract GSS `validation.py`'s mod-neutral support (`Bridge`, `row`, `hrow`, save helpers) into
  `src/RimMandrake/Utils/validation_core.py`; GSS and FlowWorks scripts import it and supply their own probe class, assembly
  name, settings entry and owned namespace (G5.1, G5.7). Gate: import smoke test of every moved script with GSS's folder
  absent from `sys.path`.
- `validation_style_hose.py`: the designator/style operations it borrows from `validation_aerial`/`validation_style`
  move into the core module; the FlowWorks probe answers them; and the three identities (`RM_Hoses.xml` → `RM_HoseReel.xml`,
  graphic class, texture root) are updated; `--offline` runs in step 2 (G5.2, G5.3).
- GSS `proof_all.py` is split at: imports (`:251-259`), `PB` composition, preflight hose probe, matrix cleanup, save
  staging, SL2, SL3, SL4, dispatch and restoration; an offline mock run of GSS's driver fails on any hose-probe call (G5.4).
- One manifest contract: FlowWorks walk `checkout:` names a FlowWorks manifest that unions core rows, `proof_hose.py`'s
  `DECLARED_ROWS` and the hose scenes filtered out of GSS's matrix; results reach FlowWorks' `validation.py` through the same
  current-hash JSON path; offline tests for declared = emitted, missing, stale and partial (G5.5).
- Log needles (`preflight_flowworks.py:346-351`) gain the mixed-version line, unresolved legacy hose class names and
  "Cleaning up invalid job state", each with an offline positive test (G6.3).
- RL6 is split: `RL6_debug_flow_propagates` (provider `debug`) and the real-flow relay bar `NS_relay_chain_carries` (G5.6).
- Settings rows: a typed registry (key, owning settings class, field name, Scribe key, default, flip value) replaces the
  bool-only `MACH_TOGGLES`/`DEFAULTS` (`northstar/extensions.py:79-90`), with typed flip/restore tests (G5.10). It is the one source for `extensions.py`'s `SETTINGS_OF`/`DEFAULTS`,
  `validation_v2.py`'s defaults tables and `site_spec.SETTINGS`/`toggles()`; an offline test asserts the harness covers
  exactly the settings the C# sections expose (G6.1). The all-off fixture includes machinery, river, river-steam and hose
  switches.
- Textual move list additions: `CompHoseReel.cs:91-93` icon paths, `RM_HoseReelStyles.xml` graphic `Class`, every moved
  string scanned for `GimmeSomeSlack` (G1.19).

## 4. Final port increments (replaces v2 §10)

Each step lands alone, builds **both** DLLs (`winbuild.py`, `.srchash`), passes `run_selftests.py` and its named gate.

| # | step | files | behaviour | offline gate |
|---|---|---|---|---|
| 0 | **Census + harness defect fix** | read-only, plus `FlowWorks/validation.py` | v2 census + every `Mod`/`ModSettings`, every hose string in moved files, the 11 credit sites; fix SKIP→PASS (P12) | counts written to the step-2 commit; sanity probe `HoseSelfTest` = 129; adapter test: SKIP never certifies |
| 1 | **Shared geometry + style core** | `_Shared/SlackGeometry/*`, `_Shared/StylePicker/*`, GSS usings/csprojs, `CordMaterials.cs` | none (GSS keeps bracket injector) | GSS SelfTest counts byte-identical; top-level-type gate (§3.9); GSS DLL rebuilt |
| 2 | **Move + alias + settings** | GSS `Source/Hose/**`, hose defs/textures/selftests → FlowWorks; `RM_HoseLegacy.cs`; `RM_HoseSettings.cs` + window group + import (hose keys + look); `HoseLook.cs`; old-GSS detection; `validation_core.py` + moved harness; art-ledger re-point | unchanged flow (adapter carried verbatim); settings screen present throughout | moved assertion count == step-0 count via `Program.Check` shim; GSS count == old − that; `MapTypeName`; settings-import fixtures ×3 file names + look import; essential-patch census (3 present); no defName in both mods; `grep FlowWorks GimmeSomeSlack/Source` = 0; moved scripts import with GSS absent; style `--offline` |
| 3 | **Load order** | FlowWorks About.xml `loadAfter` | none | `lint_mod_defs` |
| 4 | **Universal pipe** (+ P13 first) | `RM_LiquidLogistics.xml`, `RM_UniversalPipeExtension`, def alias, `universalPipesEnabled` | rename + PROVISIONAL pipe stats | alias table test; `machinery_pipes` chain; typed toggle registry rows |
| 5 | **Pre-port FlowWorks fixes that hoses make common** | `Building_LiquidPump.cs` (P1), `CompLiquidConverter.cs` (P2), `Kits/RM_LiquidBath.cs` (P3) | pour finds a feasible tank/destination pair; converter tries later inputs; bath craft pays or does not complete | SelfTest cases water-first/tar-channel pour; short first input; disconnect mid-craft |
| 6 | **Real flow** | `RM_LiquidNetKernel.cs` (new), `RM_LiquidNet.cs`, `RM_HoseLinks.cs`, `HosePorts.cs` (hydraulic role), `HoseFlow.cs`, `CompHoseReel.cs` (lease, tint fields), `RM_MapComponent_Hoses.cs`, 11 credit sites; delete `FlowWorksPumpFlow`, `RelayHoseFlow`, `HoseTint`, `useFlowWorksPumps`, `defaultFluid` | §3.1-3.4 | `HoseNetChecks` on the kernel (§3.7 list); caller-coverage lint (11 sites) |
| 7 | **Cache + perf** | kernel + adapter | §3.5 | same-tick two-call = one BFS; next tick rebuilds; revalidation drops a wound link; perf budget incl. index rebuild |
| 8 | **Live proof (one bridge session)** | harness only | v2 step 8 + §3.6 bars + dedicated pre-port mid-**carry** and mid-**retract** save fixtures that fail on "Cleaning up invalid job state" or a could-not-find-class line (G5.9); pump probe reads the far tank (G3.11) | `selftest_proof_all.py` + manifest contract tests |
| 9 | *(Q3)* **Nozzle in liquid** | `HoseEnds.cs`, pump reach | open nozzle in a pumpable cell extends the coupled pump's reach | mapping census LiquidDef↔FluidDef (G3.2); reject deep sand, dry terrain, closed sluice; accept open sluice/grate, registered liquids; disabled liquid; exhausted source (G3.10, G4.2) |

## 5. Pre-existing FlowWorks defects found by the review (not port work unless marked)

To be filed as FlowWorks items (BENCH files them after this doc lands; each line carries its evidence):
- **P1** pour starvation (G1.14) — *fixed in step 5*. **P2** converter starvation (G1.15) — *step 5*. **P3** bath unpaid
  craft (G1.16) — *step 5*.
- **P4** pump-fed channel may stall after reload: `driverInputTick` unsaved (G3.1) — write the brimming-outlet reload
  test first; fix only if it fails.
- **P5** flood debits one `volumePerTile` for a full-depth fill (G3.3). **P6** flood switch-off terrain race and tar
  cooling onto engine-owned cells (G3.4, G3.5). **P7** fluid palette exhaustion returns key 0 (G3.6).
- **P8** fire burn pulse may consume replacement water (G3.7, unverified path). **P9** heat budget prefix starvation and
  15,000-tick natural cache (G3.8, G3.9).
- **P10** weir washing loses an item when placement fails (G4.3). **P11** station reach is position-centred (G1.22).
- **P12** `FlowWorks/validation.py:128-131` keeps PASS on SKIP (G5.11) — *fixed in step 0*.
- **P13** preflight P-B4 passes with required settings fields ABSENT (G6.2) — *fixed in step 4, before the rename*.
- **P14** the machinery mission goal accepts any filled tank (G6.5) — not evidence for hose bars until bound to a
  destination tank by identity with a units delta.

## 6. Owner questions (replaces v2 §11; the review's re-wording, with the defaults the port uses)

1. **Static "liquid hose" → "universal pipe"?** FlowWorks has a second, conduit-style line also called a hose, built as
   the tanker raid's quick hose spool. The reel does that job better (portable, length limit, winds back). *Default:* yes —
   the reel is the raid's hose; the conduit line is renamed universal pipe, made sturdier, old saves keep their pipes.
2. **Hoses switched off: carry liquid invisibly?** *Default:* no — off hides hoses and they carry nothing; a tank fed only
   through a hose stops filling; reels keep their ends, so switching back on restores everything.
3. **Open nozzle in a pond or canal acts as the pump's intake/outlet?** The hose already says "intake in water" and moves
   nothing. *Default:* yes, as step 9 once the port is proven, on by default with a switch.
4. **Art and look.** (a) 40 hose PNGs move byte-for-byte during the art pause. *Default:* yes, relocation not art work.
   (b) Reels built without a picked look. *Default:* FlowWorks' own default-look setting, seeded once from your current GSS
   look so nothing you built changes appearance.
5. **Build tab** — stated default, not a question: Production, where every FlowWorks machine is.
6. **Flow direction drawn** — stated default: not in this job.
7. **RULED (owner, typed 2026-10-11):** *"Yes, a tank would pass liquid on to a hose screwed into it, without a pump needed."*
   A tank feeds a hose coupled to it directly — the tank is a source for that hose, no pump required. This is a hose
   feed, not a net merge: two PIPE lines still never join through a tank (`RM_LiquidNet.cs:14-17`).
