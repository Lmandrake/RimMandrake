1. **High — §3.12 / §4 steps 5–8.** `session.sweep()` destroys every `Building` in the 52×52 area, including the test walls, although `prep_site()` runs only once. Later chains can run against a wall-free site. **Fix:** give every chain an explicit fixture setup and verification, or restrict teardown to recorded dynamic thing IDs and preserve terrain/walls.

2. **High — §3.4.** The six-cell exclusion margin is smaller than `TryFindWallMarkCell`’s search radius of up to 12 cells. A painter can select an outside wall or place a mark outside the counted rect. **Fix:** clear at least the full search radius plus pawn offset, keep every painter and fixture that far from the boundary, and assert no other full-fill edifices exist in the complete search area.

3. **High — §§2, 3.1.** **M** is not the actual spree pool. `GraffitiPool` selects by `ModExtension_Graffiti`, form, and meme eligibility; not every `Filth_Mark` is eligible, and an eligible foreign def might not use exactly that class. **Fix:** derive separate live sets: base-mod visual defs, actual pool-eligible defs for the test ideo, designator defs, and all cleanup filth. Use `typeof(Filth_Mark).IsAssignableFrom(thingClass)`, not exact equality.

4. **High — §3.1 full rung.** Letting foreign **M** members enter the same gallery makes the base mod’s result depend on SacredGraffiti/GraffitiImperial content. Sacred marks can correctly fail a “punk/urban” test. **Fix:** judge base-owned defs by `modContentPack.PackageId`; test foreign pool integrations in separately reported compatibility components.

5. **High — §2 bar 1.** “At least one thing per painter” cannot prove each painter painted. Filth can gain thickness, same-def deposits can merge, and rival defs can replace one another at a cell. One painter could make all surviving things. **Fix:** isolate one wall lane per painter and expose maker ID or paint-event telemetry; stop each painter after its first successful placement and verify one event attributed to each pawn.

6. **High — §§2 bars 1–2, 3.11.** Six simultaneous painters share targets and reservations. Their marks can overwrite each other, so final object count and distinct-def count are not counts of successful painting. **Fix:** use separated wall segments outside one another’s search radius, or run painters sequentially while retaining their first result.

7. **High — §3.11.** A final `<3 defNames` result is still RNG-sensitive; recording a map seed does not replay the global `Rand` state after map AI, weather, and rendering consume randomness. **Fix:** set a dedicated deterministic seed around pool selection or expose a seeded pool-pick test. Condition the result on a known number of successful selections, not 3000 elapsed ticks.

8. **High — §2 bars 3–6.** One spawned instance per def tests only one `Graphic_Random` variant. A good variant can hide a broken, English-bearing, transparent, or dirt-like sibling. **Fix:** enumerate live resolved subgraphics and render every variant for every in-scope def.

9. **High — §2 bar 3.** The gallery is geometrically impossible as specified. There are already roughly 42 marks, exceeding the 40-cell site width, and a 42-cell row at 64 px/cell exceeds a normal screenshot width. **Fix:** use bounded pages or a grid of short wall runs. The pipeline must AND the judgment from every page.

10. **High — §2 bar 3.** “Every spree-eligible def” does not implement “every mark.” With the no-meme ideo, most glyphs and designator-only forms are absent from this component. **Fix:** bind `mark_reads_at_play_zoom` to every base-owned visual def and every variant, regardless of its current pawn’s pool eligibility.

11. **High — §2 bar 9.** `never_real_world_english` examines only Vandal. Tags, throw-ups, stencils, flyers, glyphs, and future defs can contain English while the bar passes. **Fix:** enumerate every in-scope mark variant; present them in paged close-ups with exact coverage recorded.

12. **High — §2 bar 6.** `mark_carries_no_earth_signage` covers a hard-coded designator subset rather than all marks. The state predicate proves only that instances exist, not that the complete domain was inspected. **Fix:** derive the full visual-def set live and judge every variant; do not equate designator eligibility with signage risk.

13. **High — §2 bar 10.** Three selected marks cannot establish `never_reads_as_dirt` for the complete set. **Fix:** compare every mark variant against controls, in paged panels with exact mark/control coordinates.

14. **High — §§2, 6.** `spawn_batch` bypasses `FilthMaker.TryMakeFilth`, `Filth_Mark.MakeMark`, going-over behavior, maker/quality initialization, and possibly mesh invalidation. The gallery can look perfect while naturally painted marks are broken. **Fix:** include at least one instance of every player-reachable creation path and prove its resolved graphic matches the direct-spawn fixture.

15. **High — §2 `textures_resolve`.** `Graphic.MatSingle.mainTexture` is not sufficient for `Graphic_Random` or `CornerFiller`/linked graphics. It can inspect only one material and miss bad directional or link-mask subgraphics. **Fix:** traverse every resolved subgraphic, orientation, and link mask, checking texture, shader, transparency, and material; retain the offline file audit only as a cross-check.

16. **High — §§1, 5.** With 38 unresolved textures, the expected outcome is not merely two RED bars. `textures_resolve` and several must-show galleries should fail or become unjudgeable. **Fix:** either wire owner-approved art before the GREEN attempt or label the first execution an infrastructure/diagnostic RED and enumerate all expected failures.

17. **High — §§3.4, state components.** Treating a failed ordered paint job as evidence that Concrete rejects `Unnatural` is invalid; job failure, pathing, reservations, settings, and placement can all produce zero marks. **Fix:** read `TerrainDef.filthAcceptanceMask` directly and add an instrumented `FilthMaker.TryMakeFilth` control that reports its return/result.

18. **High — validation walk / state components.** The required rejection behavior on terrain that does not accept `Unnatural` is never tested. **Fix:** create matched accepting and rejecting cells, invoke the same placement path, and assert creation only on the accepting terrain. Also verify every pool-eligible def’s placement mask.

19. **High — validation walk / §2 state components.** Nothing exercises `JoyGiver_PaintGraffiti` as recreation or verifies Meditative joy. An ordered job bypasses the JoyGiver entirely. **Fix:** lower recreation, permit recreation scheduling, invoke or naturally select the JoyGiver, then verify the job, joy kind, and recreation increase.

20. **High — validation walk / `mental_break_assigns_paint_job`.** Observing one current job within 300 ticks does not prove a spree repeatedly paints “for a stretch.” **Fix:** record at least two distinct paint-job assignments or successful placements separated in time while the same mental state remains active.

21. **High — settings components.** Four settings tests only write/read fields. GREEN is possible when their consumers are dead or inverted. **Fix:** add behavioral A/B controls: ThoughtWorker/reaction for viewer reaction, controlled breach scoring for breach bias, an exiting raider for exit tagging, and cleaning-job availability for auto-clean protection.

22. **High — `painting_toggle_blocks`.** Zero marks with painting disabled is a non-causal negative assertion; it passes if the break, job, path, or terrain is broken. **Fix:** use the identical prepared pawn/site for an enabled positive control and a disabled negative control, assert the mental-state/job gate outcome, then reverse the order in a second deterministic case.

23. **Medium — §3.3 / toggles.** `paintIntervalTicks` is one of the six settings but has no independent setting or cadence test. **Fix:** test read/write/clamping at 60 and 1000 and verify observed placement timestamps change accordingly.

24. **High — §3.7.** Fresh `Colonist` generation is not deterministic. Xenotype, age, traits, work tags, manipulation, consciousness, area restriction, and ideology can change job eligibility even after healing and setting Artistic 8. **Fix:** use a fixed pawn template and assert adult humanlike status, enabled Artistic work, capacities, reachability, reservation ability, area, mental state, and current job before each behavior test.

25. **High — §3.7.** “Spawned within walk distance ≤3” does not prove `CanReserveAndReach` for the selected target. **Fix:** expose and assert path/reservation checks for each pawn’s isolated target, and record job failure conditions if a toil aborts.

26. **High — §3.7.** Mentally broken pawns normally cannot be drafted or obey move orders, so “draft and move out of frame” is unreliable. **Fix:** safely despawn them by recorded pawn ID, or terminate the mental state and teleport them; then re-read the marks before capture.

27. **High — §3.7.** Cleaning priority zero and Home removal do not cancel an already assigned cleaning job or reservation. Auto-home can also re-add area around newly spawned player walls. Full lists may have cleaning mechs or modded cleaners that ignore colonist work priorities. **Fix:** disable auto-home, clear active cleaning jobs/reservations, despawn or freeze all non-test pawns/mechs, and assert no cleaner has a target in the site immediately before and after tick advancement.

28. **High — §§3.7–3.8.** Removing unrelated pawns only within 60 cells and “accepting” a live storyteller leaves deterministic execution vulnerable to wander-ins, incidents, visitors, raids, and map conditions. **Fix:** require storyteller/incidents disabled, clear queued incidents and map conditions, and remove or immobilize unrelated pawns map-wide.

29. **High — §3.5.** Clear weather and noon do not guarantee stable lighting. Weather transitions, eclipse/darkness/volcanic-winter conditions, sky-glow, and modded conditions can change the image. **Fix:** assert zero light-altering conditions, zero rain rate/transition, and a fixed `GameGlowAt`/sky-glow range at every subject immediately before capture.

30. **Medium — §3.5.** The test only uses unroofed outdoor steel walls on concrete. It can pass while marks disappear on ordinary roofed indoor walls or different wall contrast. **Fix:** add a roofed, fixed-lamp room control and at least one contrasting wall stuff; record glow numerically.

31. **High — §3.5.** Re-pinning `TicksGame` before a shutter can move time backwards and corrupt job timers, mental-state durations, needs, and storyteller scheduling. **Fix:** set time only between chains before pawns are spawned, and always move forward to the next valid daylight window.

32. **Medium — §3.5.** A generic 10–30 °C cell range is not the relevant pawn precondition. **Fix:** assert each painter’s safe-temperature range contains the site temperature and verify no temperature hediff appears during the chain.

33. **High — §3.4.** `clear_area`/thing destruction does not necessarily remove blueprints, frames, designations, zones, pollution, gas, fire, motes/flecks, reservations, or area assignments. Several can affect jobs or screenshots. **Fix:** clear and verify each non-Thing grid/state explicitly; use a rendered-ROI check for unqueryable visual residue.

34. **High — §3.4.** Fog is described as verified through “a cell read,” which does not prove the complete gallery or camera region is unfogged. **Fix:** batch-read every subject and margin cell for fog, roof, snow, terrain, and bounds.

35. **High — §§3.4, 3.12.** Removing roofs and then destroying supports can generate roof-collapse debris or injuries. **Fix:** clear roofs before support changes, verify no thick roof remains, wait for collapse processing, then clear and reverify the site.

36. **High — §§3.1–3.2.** A matching deployed DLL does not prove that DLL is the one loaded. Duplicate package IDs, workshop copies, or assembly resolution can load another path. **Fix:** read live active mod package IDs, root directories, assembly locations, MVIDs, and source hashes from `LoadedModManager`/loaded assemblies.

37. **High — §§3.1, 4.** Parsing `ModsConfig.xml` proves only the next-load configuration. DLC status alone does not prove the complete running mod list or order. **Fix:** compare the exact live `RunningModsListForReading` order to the intended manifest and require the expected game PID/session nonce.

38. **High — `defs_load_clean`.** The bridge becomes available after XML loading, so a bridge log offset cannot reliably capture errors emitted from process start. Config errors also often name a def or file, not the package ID. **Fix:** tail `Player.log` externally from a recorded launch offset/PID and search assembly names, all `RM_` def names, XML paths, texture errors, and generic exceptions with stack context.

39. **High — §3.3.** `persist=False` does not guarantee owner settings remain untouched; RimWorld or a mod can write in-memory settings on shutdown. Existing owner settings can also cause the default assertion to refuse every run. **Fix:** launch with an isolated test configuration root, or hash/back up all relevant config files and restore them only after the process is down.

40. **High — §4 step 10.** Restoring FULL `ModsConfig.xml` while the minimal-list game is still alive risks the game writing its active minimal list back during shutdown. **Fix:** stop the game, verify the process is gone, restore atomically, then hash-compare with the backup.

41. **High — §6 driver.** Negative assertions are unsafe unless every RPC validates `success`, schema, map ID, tick, completeness, and pagination. A timeout or truncated empty response can make “zero marks,” “no roof,” or “no cleaners” pass. **Fix:** fail closed on every call, require returned/expected cell counts, paginate thing reads, and run a capability/schema preflight before altering the map.

42. **High — §§3.4, 3.9.** Operations implicitly targeting the “current map” can diverge from the map being photographed if UI focus or current map changes. **Fix:** assign a unique map ID and pass/verify it on every spawn, read, camera, and screenshot operation; assert `ProgramState.Playing` and not world view.

43. **High — §3.9.** Camera read-back before the screenshot does not prove the asynchronous capture used that state. Camera lerp, clamping, UI scale, or a later jump can change framing. **Fix:** wait for render-frame settlement, capture camera/map/tick metadata immediately around the shot, and calculate that every asserted subject cell lies inside the viewport with margin.

44. **High — §3.9.** Mean luminance merely rejects a black frame; a loading screen, menu, or wrong bright map can pass. **Fix:** validate dimensions, fresh file hash/time, map identity, expected wall/floor pixels in the subject ROI, and exact subject-coordinate projection.

45. **Medium — §3.9.** Two ordinary walls are weak calibration targets, and `rootSize` can be clamped or altered by camera mods. **Fix:** use high-contrast calibration markers at known coordinates, derive px/cell in both axes from the actual captured PNG, and assert tolerance after every framing change.

46. **High — §§3.9, 6.9.** `claude --version` does not prove the judge can read a fresh Windows screenshot path. **Fix:** run an end-to-end image canary through the exact interpreter, working directory, and command line, requiring it to identify a generated nonce or marker.

47. **High — visual components generally.** State is often checked before pawns are moved, meshes settle, UI is cleared, or the camera changes. The screenshot can therefore differ from the asserted world. **Fix:** make capture transactional: pause, prepare framing/UI, re-run the complete state/layout predicate, capture, record image hash, and perform a post-capture identity check before cleanup.

48. **High — §2 bar 7.** `wall_closeup` asserts only one mark but promises a screenshot with three painted marks on a seven-cell run. Random painting does not guarantee that layout. **Fix:** assert the exact three mark IDs, cells, wall cells, absence of other objects, and viewport containment—or change the promised shot to match the predicate.

49. **High — §2 bar 2.** Three distinct `defName`s do not prove visible variety; three defs can resolve to identical art or recolors. Conversely, variants of one def may be visibly distinct. **Fix:** require distinct resolved texture/variant identities and preferably distinct forms, then bind their exact cells to the judged screenshot.

50. **Medium — §2 bar 8.** The Beauty comparison has no visual-to-state association and uses random variants. The judge may not know which is −15 and which is −3, or a cherry-picked pair may distort the result. **Fix:** pin resolved variants, assert fixed left/right coordinates, state that mapping in the prompt, and test a predetermined representative set rather than whichever variants happen to spawn.

51. **High — §3.4 / rendering.** Calling `map_commit` after painted marks would conceal a real mod defect in map-mesh dirtying; not calling it after raw fixture writes can create an infrastructure failure. **Fix:** commit fixture terrain/walls only. Capture naturally painted/replaced filth before any manual mesh dirty; use a later forced commit solely as diagnostic evidence, never as a passing image.

52. **High — cannot-show prompts.** Standard UI contains English, and the dirt-control frame deliberately contains dirt. A literal judge can fail the English bar because of UI text or fail the dirt bar because it sees the controls. **Fix:** crop to the playfield/mark ROI, hide all persistent UI, provide exact graffiti/control positions, and word the question explicitly about pixels inside the graffiti slots.

53. **High — §2 judge design.** A single unpinned `claude -p` answer is neither deterministic nor resistant to charitable “overall looks fine” judgments. **Fix:** pin model and prompt hashes, retain full responses, include known-good/known-bad calibration panels, require itemized inspection of every slot, and use unanimous repeated judgments for negative universal bars.

54. **High — §2 pagination.** Merely claiming the same bar from several gallery components does not prove the runner aggregates them universally. One passing page might satisfy coverage. **Fix:** define aggregation as AND across every component claiming that bar, or create explicit per-page child assertions whose conjunction gates the parent bar.

55. **High — §3.11 / variant coverage.** Spawning `4·N` instances does not guarantee all `Graphic_Random` variants. PNG count is also not necessarily the loaded subgraphic count. **Fix:** enumerate `Graphic_Random.subGraphics` live and provide a deterministic variant-index fixture, or spawn until exact live paths are covered with a hard cap that yields REFUSED—not a partial judgment.

56. **Medium — §3.10.** Fixed tick budgets can false-fail slow but correct jobs, while “TPS below 60” conflates infrastructure performance with a mod defect. **Fix:** poll explicit toil/job/placement milestones with a generous tick deadline and a separate wall-clock watchdog; classify timeouts and low TPS as REFUSED/INFRA, not bar RED.

57. **High — validation walk / `defs_resolve`.** The plan no longer tests the walk’s parent-chain claim, and `ParentName` inheritance is generally resolved away at runtime. The walk also names the break as a `MentalStateDef` and still states `thingClass=Filth`. **Fix:** correct the walk before WIRED, bind XML inheritance to an offline structural assertion, and bind runtime behavior to the resolved `Filth_Mark`, `MentalBreakDef`, and state-def graph.

58. **High — §4 full rung.** Restoring a full-list XML does not make the current minimal process a full-list run. **Fix:** shut down, restore/select the exact full manifest, relaunch, verify the live active list and loaded assembly provenance, then create a fresh map and site.

59. **High — owner review.** A one-time owner approval can become stale after textures, DLL, walk text, driver prompts, camera policy, or judge model change. **Fix:** bind the approval to the run-sheet hash, walk hash, source/DLL hash, texture manifest, screenshot hashes, driver/prompt hash, and judge model; invalidate it on any material change.