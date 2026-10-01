1. **High — §3.4 / P-S1.** Problem: requiring every plot cell to be Soil, unroofed, and empty contradicts authored reservoirs, the rain-test roof, ladders, and test fixtures. Fix: store per-cell expected base terrain, roof, and allowed things in the sidecar and compare against that manifest.

2. **High — §3.4.** Problem: the reusable save has no immutable hash or version contract; stale map-component data can survive code, def, or settings changes. Fix: hash the save, sidecar, game build, DLL, defs, and prep-script version; rebuild the golden save on any mismatch.

3. **High — §3.4 / between runs.** Problem: nothing prevents a run, autosave, or manual save from overwriting the golden trial site. Fix: keep a read-only golden save, copy it to a uniquely named working slot per run, disable autosave, and never save the working map.

4. **High — §3.1–3.2.** Problem: disk hashes do not prove which DLL the running process loaded, especially with duplicate Workshop/local copies. Fix: expose assembly path, MVID/version, and SHA through the bridge and compare them after launch; reject duplicate package IDs and assembly names across all mod roots.

5. **High — §3.1.** Problem: the tier does not pin the RimWorld build, DLC package IDs/versions, Harmony/dependencies, or exact load order. Fix: record and assert the complete ordered active-mod list plus game build and dependency versions.

6. **High — §3.1 / step 10.** Problem: restoring `FULL.LATEST` can silently replace the user’s real list, and `finally` will not run after process/host failure. Fix: transactionally back up the exact initial `ModsConfig.xml`, hash it, and use a watchdog/recovery command to restore that exact file.

7. **Med — §4 step 1.** Problem: “kill game” risks unsaved user state and may leave Steam/RimWorld processes or locked files. Fix: require a dedicated test instance, request graceful quit, verify process exit, then deploy and swap configs.

8. **High — §3.2.** Problem: source-at-HEAD comparison ignores dirty/uncommitted source and build inputs. Fix: hash the actual source tree, project files, referenced assemblies, build configuration, and resulting DLL; record the git commit plus dirty diff hash.

9. **High — §3.4 / P-S2.** Problem: “no body yet, or stock == capacity” permits two materially different baselines, while body classification is sticky. Fix: require explicit body IDs, classification, fluid, capacity, stock, cell set, and limitless flag in the golden manifest.

10. **High — §3.4.** Problem: painting reservoirs and then saving may allow a tick to classify them before the asserted baseline is captured. Fix: pause before painting, force one documented classification step, record the result, then save; never accept an unclassified alternative.

11. **Med — §3.4.** Problem: the limitless reservoir’s geometry is unspecified; “strip at the edge” may be under 50 connected valid cells or touch unusable border cells. Fix: prescribe exact coordinates and connected-cell count, then assert edge contact and `limitless=true`.

12. **Med — §3.4.** Problem: `TemperateForest or AridShrubland` leaves biome, tile, world seed, map seed, elevation, rainfall, and map size variable. Fix: pin one world/map seed and tile, record all generation parameters, and reject any mismatch.

13. **High — §3.3.** Problem: restoring toggles to shipped defaults may alter the user’s persisted settings, and static writes may serialize on save/quit despite the stated assumption. Fix: back up `ModSettings.xml`, restore the exact original bytes, and verify after game exit.

14. **High — §2.5 / §4 step 4.** Problem: worldgen toggle `typedLiquidShoresEnabled` cannot be validated on the prebuilt map. Fix: generate paired maps from the same seed with the toggle on/off, or provide a deterministic mapgen harness that proves the generated terrain delta.

15. **High — §2.5.** Problem: many toggle components have only feature names, not concrete predicates, timing, or thresholds; merely declaring `toggle=` can satisfy the floor. Fix: specify executable on/off state deltas and failure criteria for every toggle, especially corrosion, containers, drilling, shooting, and escape.

16. **High — §3.6.** Problem: god mode does not disable storyteller incidents, quests, map events, lightning, or wildlife spawning. Fix: install/assert a no-incident storyteller or test suppressor and disable each event source explicitly throughout stepped ticks.

17. **Med — §3.6.** Problem: checking weather name `Clear` and buildup does not prove an outgoing rain transition or rain rate has stopped. Fix: report current/next weather, transition state, rain rate, and forced-weather expiry; require zero rain before and after every non-rain component.

18. **Med — §3.4/3.6.** Problem: plants, animals, filth, snow, and visitors can respawn during the 60,000-tick fire test. Fix: disable spawning/growth systems or rescan and fail at fixed intervals; include animals and motes/effects in contamination checks.

19. **High — §3.5.** Problem: checking only plot centres can miss frozen reservoir/channel cells or roof-driven temperature differences. Fix: batch-check every source, excavated, pawn, and screenshot cell immediately before the bar.

20. **Med — §3.7.** Problem: repeatedly setting absolute game ticks to noon may move time backward or skip simulation and can disturb pulse scheduling, seasons, conditions, and RNG. Fix: advance monotonically to the next noon or control visual lighting independently without changing simulation ticks.

21. **High — §3.7.** Problem: detecting pulse phase via a sentinel F change is state-mutating and fails when flow is disabled, full, or stationary. Fix: expose the component’s pulse counter/`nextPulseTick` and step to it exactly without a sentinel.

22. **High — §3.7.** Problem: `step_game_ticks` is assumed synchronous and exact. Fix: assert start/end tick, exact delta, paused state, completed long events, map identity, and pulse count after every step.

23. **High — §3.7.** Problem: “N=3 and a stated threshold” states no thresholds, and reloading one save may replay identical RNG rather than independent trials. Fix: define per-test pass thresholds and use recorded distinct seeds or RNG states.

24. **High — §3.8 / pit bars.** Problem: teleporting or placing a hostile pawn on a pit cell may bypass the movement-entry capture hook. Fix: stage the pawn adjacent and force an actual cell transition; separately test direct spawn behavior only if it is part of the contract.

25. **High — §2.4.** Problem: the depth-ladder walk conflicts with superdeep capture—the pawn may be captured before reaching D=4. Fix: run the visual traversal with capture explicitly disabled, then restore defaults and test capture separately.

26. **Med — §3.8.** Problem: drafted colonists in a holding room are not sufficient isolation; hostile pawns, animals, mental states, and jobs can still interfere. Fix: despawn all non-test pawns or freeze them in holders, disable needs/AI, and assert the map pawn roster before each bar.

27. **Med — §3.8 / shots.** Problem: render resolution, UI scale, language, graphics quality, texture compression, renderer, and window focus are unpinned. Fix: assert a fixed graphics profile, resolution, UI scale, language, and foreground game window.

28. **High — §2.1 / §6.8.** Problem: luma/variance accepts a stale screenshot, wrong map, desktop, or unrelated game frame. Fix: require a fresh timestamp/hash, expected dimensions, game-window crop, map/tick/camera metadata, and a temporary in-scene calibration marker at a known cell.

29. **High — §2.1.** Problem: “last screenshot” is fragile; cleanup, calibration, or failure diagnostics can silently become the judged frame. Fix: explicitly nominate one artifact path per bar and freeze its hash in the result record.

30. **High — change bars.** Problem: a diptych can appear changed because of camera, lighting, weather, animation phase, or labels rather than the mechanic. Fix: lock crop/zoom/light, align pixels, capture exact ticks, and include machine-checked state deltas alongside the composite.

31. **High — `canal_fill_front_watchable`.** Problem: two tar frames do not prove “water near-instant, tar creeping,” and cross-map geometry/RNG may differ. Fix: produce a four-panel water/tar × pulse-1/pulse-3 composite from identical golden-map copies and assert different front distances.

32. **High — visual bars generally.** Problem: an unconstrained vision judge can call tinted Gravel a canal or pit, creating expected false passes. Fix: use bar-specific rubrics, minimum visible scale, positive/negative reference images, and require agreement from repeated judging or owner review on ambiguous results.

33. **High — cannot-show bars.** Problem: absence inside one crop cannot establish “never,” and defects can sit just outside the frame. Fix: scope wording to the staged footprint and combine the screenshot with exhaustive state/asset scans of the footprint plus buffer.

34. **High — `canal_dry_reads_as_obstacle`.** Problem: accepting any path cost above Soil lets the known-broken value 6 pass despite the ruled value 30. Fix: gate on the exact effective movement cost/behavior required by the ruling, including pawn traversal timing.

35. **High — `canal_fill_spreads_along_itself`.** Problem: the budget fallback is vacuous—an all-dry channel is monotone non-increasing and could pass. Fix: require a wet mouth, minimum filled distance/volume, no gaps, and fail outright if settling exceeds budget.

36. **High — settle/conservation.** Problem: requiring unchanged stock conflicts with refill/recession, while steady flow to an edge can have constant F but rising sink totals. Fix: disable unrelated stock modifiers per bar and define equilibrium over F, stock, source/refill, sink, overflow, rain, and burn deltas.

37. **High — `reservoir_fill_visibly_drops`.** Problem: the conservation equation omits refill, rain, burn, recession/capacity changes, and direct driver injection; the 5×5 pond may also be insufficient. Fix: freeze unrelated flows, calculate a complete signed ledger, and precompute adequate reservoir capacity.

38. **High — fluid bars.** Problem: `ActiveFluid` is map-wide and the proposed reflection setter may not refresh existing bodies, terrain graphics, or serialized state. Fix: set and verify fluid before first classification on a fresh map copy, force graphic refresh, and reject bars until a supported read/write API exists.

39. **High — fire bars.** Problem: fixed checks at 600/6,000/60,000 ticks are RNG-sensitive; natural water may not legally hold Fire, and “burned cells” is undefined. Fix: define eligible cells and expected propagation contract, poll within bounded windows, use seeded repetitions, and record the exact ignited/burned cell set.

40. **High — §4 / tickets.** Problem: the sequence assumes unbuilt driver tools, revalidated bars, and blocked mechanics, yet calls a RED run “GREEN-minimal”; the 70–80 minute estimate also excludes site creation, restarts, retries, judge throttling, and potentially slow 60k-tick stepping. Fix: add hard dependency gates, name the first execution a baseline/RED trial, measure each phase separately, and budget serial fallback plus retry time.