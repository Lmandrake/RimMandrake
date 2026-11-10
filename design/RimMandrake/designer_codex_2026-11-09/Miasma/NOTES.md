DRY RUN — Miasma Designer, stages 0 and 1 only

record.json separates implementation, proof and scope for the built capabilities and the named missing/retired parts. root is null; root_draft is our proposal. QUESTIONS.md is a bank of eight draft asks, with 01–02 marked first. There are no answers, approvals, waivers, stage results, build orders, queue changes or ledger writes. Only this working folder was written. The source mirror and the existing designer.log/designer_brief.md were left alone.

What could not be verified

- Present-day gameplay, deployed DLL/data/art agreement, active composed mod list, settings, saves and all acceptance results. Nothing was built, deployed, started or staged; no bridge or ModsConfig was touched. No proof is marked current.
- The latest MIASMA_FIRST_SCRIPT_1 ledger verification (RUNNER.jsonl, 2026-11-06 15:09:06Z, tsn 1793977746998865014) is partial at bf7baa245011b4216c5d4a66b686e90f37f96282. Its raw HTML/log lives outside the supplied mirror. “Partial” cannot establish which feature passed. The walk's “NEVER RUN LIVE” is obsolete as a history claim.
- The warden art has historical L1 and L2 PASS events on 2026-11-04 at 3f30325fe676; the L2 runner reads the OBSERVED rendered elder texture, and negative verdict tests reject adult art. Earlier UNMEASURED attempts are not failures or acceptance. Neither this rehearsal nor that narrow state test certifies how ancient she looks, her declining pace, an NPC warning or a satisfying relationship before death.
- September live evidence exists for sampled warden wandering/duty, training exclusions and Ullavess killing Karravel with a feeding mote. Those records are retained as stale proof. The pathfinder item expressly leaves attack-chase paths unverified; a water destination and sampled water positions cannot prove no land segment, sea-connected canals or natural rescue.
- The root's continuous story is not accepted: surge to newly isolated pool to natural rescue; carrier cry; buyer actually arriving and paying through a trade; the correct crèche remembering sale; rescued young later choosing the colony and guarding after death; normal rot feed to a useful power net to a bed to corpse products and Cuisine cooking. Direct helper calls do not prove those links.
- No visual or audio judgment was made. Texture paths and sprite inventory were read/accounted, not inspected as installed art at play/study zoom. No flyer flight was tested. Generic frog calls, first letters and render-state paths cannot establish the promised soundscape.
- Standalone dependency completeness and the resolved cast are unverified. Miasma is a Biomes compose member and consumes shared classes/defs. The campaign cast patch must be read alongside the inline XML. The older roster JSON includes prior names and cut/tabled ideas; it is not the post-load def truth.
- No exact OWNER tsn for the chosen experience sentence was located in OWNER.jsonl. The specified biome_experiences file and walk both preserve its provenance; the paragraph is rooted in that existing choice. The mother/juvenile September rulings also retain their real path/item provenance. No substitute OWNER event or new quotation was fabricated.

Top five correctness risks from the code (static findings; not reproduced live)

1. src/RimMandrake/EnvironmentalHazards/Source/RM_GradientAxisRepaint.cs:78 — The surge maps existing water to other water grades or mud to crust, never creates new wet cells; later pool detection therefore need not produce any newly cut-off nursery pool.
2. src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_StrandingPools.cs:377 — Pool expiry destroys every still-spawned tracked occupant without checking its current location or player ownership, so a young that walked out or self-tamed can still vanish; the only sign is a log.
3. src/RimMandrake/Miasma/Source/RM_WardenMotherSuccession.cs:342 — Succession selects/saves an heir and messages but never transfers an anchor, guarding duty or smaller defence radius, so the promised guarding child can be only a label.
4. src/RimMandrake/Miasma/Source/RM_MothersPrice.cs:298 — Return takes the first nearby mother without matching the young's crèche, allowing tolerance to be granted to one mother while another marker's return count changes.
5. src/RimMandrake/Miasma/Defs/ThingDefs_Buildings/RM_DecayCell.xml:52 — The fuel filter accepts FoodRaw rather than the promised rot stream, excluding meals/corpses; ProofDecayCell's direct Refuel(float) bypasses this player-facing mismatch.

Evidence reconciled before drafting questions

The November 2 fluff follow-through removed mangal pollination gating and its switches, retained the swarm/composter/predation and kept succession (design/RimMandrake/fluff_cuts_2026-10-23.md:159, :166; FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO). The old “no trees without the fever” mechanism is consequently not an unbuilt feature to restore. validation.py still has a mangal_gated_on_swarm UNMEASURED row, and the walk repeats the earlier bargain. Both are stale oracles. The Nine rites are already v2 by OWNER:1792755171879607924; no rite is pitched again.

The current art no longer matches the old “no aged art wired” note: the elder texture is wired and a November 4 render-state proof exists. Raw-food power, a generic feeding mote and an heir record are likewise real built implementations, but each is narrower than some design prose implies. record.json preserves the separate gaps rather than erasing a built capability or calling it wholly unbuilt.

Further bounded discrepancies are in record.json: return removes the hediff that holds the tame/crèche link; balm reduces a permanent injury's severity despite cosmetic-only scope; fever-forging does not Scribe its peak-severity field; the carrier cry excludes carried young; and several plant/strange-boon effects remain descriptions or partial substitutes. These require proof/correction under existing requirements, not repeated owner approval. The separately filed RM_GlowingGrass drake reference remains in the present XML; the old missing-grass item was not assumed fixed.

Scene audit and protocol limits

Every chain in Miasma validation.py, its direct proof hooks, the warden-age runner and the shared script's relevant stranding placeholder are audited in record.json under scene_audit for asserted start, control, restoration and hold. The major problem is that production jobs and their interactions are usually bypassed: rot is forced immediately, fuel is injected as a number, and sale calls a helper directly. The price hook can mutate a real existing mother permanently and leaves its staged pawns; the bed proof leaves its bed/products; the age runner leaves a spawned mother and camera change. No recovery journal or explicit review hold accompanies those mutations. No scene was executed here.

This external dry run has no injected launcher run ID, persisted stage/budget or official folded built-evidence packet. built_reviewed is local accounting of actual source files, subject items, relevant ledger-only work and proof pointers, not certification that designer_stage.py accepted Stage 0. No result.json, stage advance, exam, lock, first-touch completion or Relentless handoff was manufactured.

The fresh author-independent review required before a real sent turn has not run. All asks stay draft with that limitation, as in the HugeThings reference. The user's no-ledger dry-run boundary also means no process fault, lesson or build item was filed. Missing confirmations are documented here; none was converted into owner assent.

Deliverable checks are local JSON/source/reference/coverage checks only. PowerShell was used because rg was not on PATH and python/python3 resolved to WindowsApps aliases; no source runner was invoked that might write caches into the mirror. The mirror can refresh externally; MIRROR_HEAD read during this pass was bc9dba6c8443c82f7964fd9b45d6b92dbe2112aa, 2026-11-10T00:47:51-08:00. This is not an atomic snapshot of earlier reads.

