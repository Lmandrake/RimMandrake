DRY RUN — Cauldron Designer, stages 0 and 1 only

All proposals, interpretations and guesses in these files are agent text. The only quoted owner experience is copied from the source the user specified, `design/RimMandrake/biome_experiences_2026-10-20.md:9`. It is his existing sentence, not his approval of our expanded paragraph. `root` is null; `root_draft` is an agent proposal. The seven questions remain draft. Nothing went on the ledger.

The mod was found at `src/RimMandrake/Cauldron`. All writes in this task are confined to this working folder. The source mirror and existing designer_brief.md/designer.log were left alone.

What the reading establishes

- The biome is already a bundle of weather, metal forestry, flora hazards/resources, native and ported fauna, vent ecology, gas, liquid industry, acid-proof material/gear, ship protection and grove renewal. The inventory is intentionally more detailed than a future core tree: supporting capabilities must remain accounted for without becoming dozens of new approval questions or leaves.
- Its local About.xml and several class headers contain historical statements. Vent drinking, prying, real gas, filters and acid air are built. The validation walk still refers to the removed martyr tree, an old roster, absent overlay art, and older settings/terrain facts. Current code/defs take precedence for implementation, while later rulings govern intent.
- The dry thunderstorm is deliberate (`OWNER:1792370870264139349`), not the old GPT review's leftover to fix. The owner experience requires the storm; no new choice about keeping lightning is offered. The geometry-based sun ruling still stands: weather colour is not proof of permanent physical dusk.
- Both assay overlays and the five dew variants are on disk. The separate age-based scab/slag/crystal-fan coat is not implemented in this snapshot: no extension, kernel tier, toggle or deposit art was found. The existing trunk-deposits test pins a design and conditionally checks overlays; it does not make the coat built. The filed flecks misregistration/palette issue remains an existing issue, not a new plant proposal or permission to replace kept art.
- The historical roster JSON still contains donor names, older keeps and evictions. The actual RM_Cauldron XML and Utinni patch are the present wiring. No animal is moved, evicted or offered for removal. The owner-kept art digest is GPT opinion without permission to act.
- The owner explicitly affirmed toxic pools in `OWNER:1793251119194850898`. Local water poisoning uses ToxicWater terrains; FlowWorks separately understands AcidWater/ToxicWater liquids. I did not turn the absence of a local pool generator into a claim that the fixed world has no pools.

What could not be verified

1. What “including you” ultimately requires. The local implementation has metal-load illness and acid damage, but no Cauldron-specific lasting adaptation or mutation hook was found in local source/defs or direct Cauldron/hediff references across src. That bounded absence does not certify every other mod lacks mutation machinery. Question 01 asks the intended result before any such feature is inferred.
2. A current gameplay pass. No game, bridge, build, deployment, mod-list edit, save edit, flight test, art judgement, test suite or acceptance scene was run. No proof is labelled current. On-disk DLL/stamp presence does not prove a matching deployed or loaded assembly.
3. The delivered world's current tile/mutators, open-pool chemistry, terrain-to-liquid binding, resolved post-compose roster and cross-mod effects. No large save/def/log census or tile count is offered as proof. Zero painted tiles would not be a defect.
4. The full player route from finding/studying a rig through research, construction, supply, cartridges, power and usable output. The stored works proofs directly stage the apparatus and stock. The normal study unlock, acid-water processing, long cartridge life, real crafts, worn sealing, canal-gate acid operation and ship lining need their own observations.
5. A Cauldron that is visually and audibly right in play. Texture existence, sky values and a flight eligibility report do not accept storm mood, mineral biology, wet ground, selections, motion, dew saturation, fleck registration or the giant's readable intent. Suush flight is an owner-present review only. Vanilla audio sourcing is settled; no new sound pipeline question is appropriate.
6. A useful one-hour falter. `OWNER:1792108481222070856` already sets that target. The code follows a weather transition; the current suite proves order and sampled states, not the full warning length or workers' chance to act. Do not ask him to choose the number again.
7. Sustainable labour, throughput and costs at forty colonists. Forestry, shearing, cartridges, tap output, ecology and protection are not yet one proven operating story. The questions clarify that story without offering to cancel working protections.
8. Complete historical raw evidence. October/November Transient HTML/logs and remote Steve reports referenced by ledger entries are not in this mirror. Old art sheets/review sources also point outside it. Existing owner exercise is not denied; absence of a located proof is not a claim he never tried it.

Historical proof, read carefully

- `northstar/live_ruins_works_drift_20261021b.json` passes generated rig/dressing/shrine and gas drift, while its works refinement row fails on a status-text read and downstream works rows are UNMEASURED. The separate c report passes the works rows. The earlier drift report includes a failed-loaded-map ClearOf exception that current code guards. These are targeted reports with skipped rows, not all-green whole-mod runs.
- Yield has an actual October 20 verify/close (`FOUNDRY.jsonl:6384`); the old rerun item's checkbox is not the current outcome. Several October GPT fixes are already in source: edge guards, diagonal gas drift, Add overflow protection, saved hush count, drink-walk toggle cancellation and roasted-food fixes. They are not refiled as new bugs.
- The November 6 RUNNER entries pass enrichment and rhossak but fail vent enrichment (`RUNNER.jsonl:4954–4957`; exact source pointers in record.json). November 10 UTC retries were quarantined, with no verdict (`5986`, `5989`, `5992`). The missing report prevents attributing that failure to a particular mechanic.
- VEXXITH_USES closed on offline evidence; the ledger separately names `VEXXITH_GEAR_PROVE_ONE_LOAD_AWAY` for live load/map checks and owned art (`BENCH.jsonl:9630`). Do not present the offline close as proof that raiders, suits or hulls have run correctly in the game.
- Nettle ON evidence exists historically; the missing nettle OFF comparison is explicitly filed as `CAULDRON_NETTLE_OFFARM_BUILD_TWO_OF_THREE`. A roundtrip of the setting is not that comparison. Rhossak grove/sprout/gall chains now exist despite older item prose saying unscripted, but their controls and attribution are weak.

Top five correctness risks noticed while reading (not live diagnoses)

1. `src/RimMandrake/Cauldron/Defs/HediffDefs/RM_VentMetalLoad.xml:79` — supposedly nonlethal metal load subtracts lethal capacities; an already impaired pawn may die (requires injured-subject verification).
2. `src/RimMandrake/Cauldron/Source/RM_VentGas.cs:184` — ignition checks eight neighbours without the diffusion/drift corner barrier checks; separated diagonal gas pockets may ignite through a sealed corner.
3. `src/RimMandrake/Cauldron/Source/RM_AcidAir.cs:80` — one liner makes every player ship building on the map protected, potentially including a disconnected second hull.
4. `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs:398` — bloom exposure ignores capping, so a cap's gas protection and its metal-load protection diverge; correctness depends on the safety boundary in question 04.
5. `src/RimMandrake/Cauldron/validation.py:1409` — the shot-Suush test accepts death/disappearance without any explosion-specific observation.

Proof-scene audit

The per-chain audit in record.json names asserted start, discriminating controls, restoration and hold, including the read-only mapgen chains, all active mechanic chains, and supporting offline tooling. Main gaps are:

- `_prep` clears and changes ground/roofs, settles bystanders and removes wildlife. `_stable` destroys actors/things and resets weather; it does not restore the prior map. The drift fixture's ClearOf empties gas across the whole map. A saved test site and eventual disposable-map reload can be a recovery strategy only when actually recorded and confirmed.
- Settings restoration is reread, but restores shipped defaults; preflight assumes those defaults. There is no persistent scene-begin/end/hold record, no interrupted-scene recovery promise, and no owner-review hold. No scene was staged in this dry run.
- Near/far exposure, roof/native/off contrasts, actual wood/metal harvest and the seeded cloud movement comparison are meaningful controls. They should be preserved.
- BeatFire uptake does not prove extinguishing or retaliation; being able to fly does not prove floating appearance; disappearance does not prove detonation; machine spawn does not prove discovery/research; a capped label does not prove the cloud actually stops being replenished.
- Grove tests need sleep/location assertions and attribution controls: ordinary regrowth may add nearby plants, the trio needs a two/galled/off contrast, and map-wide gall meat can come from elsewhere. Restart, saved progress, reseeding/rebinding, stable supply, acid-air/metal-load interaction and natural ecology are still important unaccepted seams.

Dry-run adaptation and review status

This was requested outside the launcher and across two stages. No run ID, budget, alias fold, packet hash, result.json, stage advance, tree, floor, oracle, exam, locked concept or first-touch certification was invented. `built_reviewed` maps the local file list and mod-specific item/proof pointers to capabilities; this is not the launcher's exact folded done-item set and not a CLEAN code-review certificate. Other design search hits were read only where they affected a named uncertainty or direct neighbour.

The role normally requires fresh author-independent review before any ask is sent. This bank has had a local source/wording audit only. It deliberately records review pending and remains a draft, as did the HugeThings example. No pass verdict or owner answer is fabricated. A real sitting starts with 01–02 and serves at most three at a time; silence changes nothing.

The owner experience comes from the explicitly authorised file source. OWNER references used elsewhere are exact tsns found in OWNER.jsonl, stored as strings to avoid integer rounding. Older rulings without such an event use item/path provenance. Event text written by an agent, even on an OWNER-seat event, is not automatically the owner's quotation.

No code fixes, system items or lessons were filed because this task authorises only the three dry-run files and forbids ledger writes. The mirror refreshes externally; MIRROR_HEAD was recorded during reading, without claiming an atomic snapshot. PowerShell was used because rg is not available on PATH and Python resolves to the Windows app aliases. Only the deliverables' JSON structure, source references, OWNER tsns, IDs, inventory links and wording are checked here; no runtime or launcher acceptance is claimed.

Deliverable checks passed: JSON parses; required inventory fields and allowed states are present; every source path and cited line exists; ITEM references resolve to prose or ledger entries; every OWNER tsn exists exactly in OWNER.jsonl; question and coverage links resolve to inventory IDs; the bank has seven draft questions with two first markers and no removal offers; failure_modes has exactly three entries; no current-proof or approved-root claim is present. Question text agrees between Markdown and JSON. These checks do not substitute for the pending independent review.

