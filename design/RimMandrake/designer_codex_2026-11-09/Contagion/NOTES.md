DRY RUN — Contagion Designer, stages 0 and 1 only

All new prose, interpretations, questions and guesses are agent-authored. The existing owner-chosen experience sentence is copied with its source; no new words are attributed to Mandrake. `root` is null, `root_draft` is proposed, and all eight asks remain `draft`. Questions 01–02 are marked to ask first.

What this reading establishes

- The requested folder exists: `src/RimMandrake/Contagion`. It contains the biome, its cast and plants, the Bloom/Burn engine, drawn tells, reactive shelter seeking, both Repulsor variants, Sunbeam combat and medical uses, unwanted mutations, organ manufacture, natural matched parts, all five unusual limbs, Draftprints/contracts, zhool haze, mulch, wreckage and scanner payload. These are already built capabilities to clarify and cover, not candidates for keeping.
- The root is built around the owner's choice in `design/RimMandrake/biome_experiences_2026-10-20.md:10`. The earlier definition sheet supplies detail; the new paragraph is not his quotation or approval. No OWNER identifier was invented for the experience row.
- The inventory separates implementation, proof and scope. It deliberately includes supporting tooling, unrostered legacy defs, ordinary hatching and natural restoration, optional VEF floating/fission, cross-mod payloads and retained placement code. Its granular entries are accounting units, not a proposed tree with that many leaves.
- `not_opened` means no scope reopening was located. It does not mean a capability is unapproved or disposable. The anticipatory Dive and Bodyprints remain in scope despite their implementation gaps; a historical Draftprint Part 1 pass does not accept the other parts.
- Existing source fixes supersede older item diagnoses: injection no longer completes on interruption, checks its toggle while running and fails when the host moves away; shelter search rotates candidate windows; tell reload state is seeded; sacs now tick normally; random limbs avoid vital sites. These are not new questions or missing features.
- Current roster rows use the owned zhool and blistered bulloo ports, rather than the old donor rows described in some item prose. Gawpsack alone is the sink tell. Shambles belongs to TheRot. Rawshade and Zhool'Iza are commissioned/design work, with no implemented race or living-canopy extension found in the source search.
- Ashfall Research Base and the Spire belong to separate campaign work. The stationary Coalescence does not satisfy the separately filed travelling-titan roster gap. The Forge owns its border die-off even though creep defs reside here. No placement count is treated as evidence of a defect.

What I could not verify

No build, deployment, bridge connection, game launch, ModsConfig edit, save write, scene staging, flight test, gameplay test, art judgment, tree lock, first-touch certification or ledger write was made. There is no claim that this is an accepted launcher run.

No proof is marked current. I did not compare running assemblies, loaded composition, defs, art and settings with source fingerprints. Historical verification events are preserved as historical evidence. In particular:

- `FOUNDRY.jsonl` records the no-Burn/dive control passing on October 30 at `6f61f5cf22e2`, with two other rows unmeasured. `BENCH.jsonl` records native-harm verification failing on November 6 at `553ac949d812`. A broader run's pass/classification result does not erase that failure.
- First-script verification explicitly allowed non-passes to be classified. That is proof that findings were accounted for, not proof that every mechanic passed.
- Saved-site A1/A2 verification on November 3 at `f94139e204de` establishes the recorded site checks for that revision. It does not accept every gameplay chain, its current v3 save contents or the natural mountain environment.
- `live_proofs/*.txt` contains commands, not the output of executing them. Referenced remote logs and removed Transient results were not recovered from another checkout.
- Fleshsop's historical close was explicitly conditional/WEAK. Its present weapon-system description and race tuning do not establish coordinated screen behavior.
- The working tests drive damage directly, accelerate deadlines/severity and place a Coalescence. They do not establish actual Sunbeam firing, four days of host care, useful warnings, natural Coalescence formation, matched versus mismatched install results, all five limbs' costs, medical removal or enjoyable contract hunting.
- Flora item descriptions promise insect repellent, wound sealing and seed fertilizer, but the sap/seed item defs alone supply no usable action here. Generic race descriptions also exceed their explicit tooling for some ecology: grub metamorphosis, tree-charge theft, specialized digestion, Sloshbelly water production and infection-front advance need their actual consumers located or their build gaps recorded before acceptance. These are not requests to rewrite existing promises.
- The optional VEF configuration, post-patch disease dependencies, campaign Helix caravan attachment, composed package guards, thermal shelter integration and current scanner/wreck outputs were not verified in a loaded game.
- Motion, color, sound, cast density and all limb facings remain visual/audio proof work. Pillar Arm and Lash have owned directional body art; Eyeburst/Caudal Spring retain borrowed presentation and Bellows has no body render node. Files on disk do not prove a good appearance.

Script audit

The per-chain audit is in `record.json.script_audit`. The suite has useful controls: absent Burn versus a directed shelter job, exposed/roofed visitors, armored natives, zero damage, toggles, slow/fast scheduling, contact near/far, a newly landed UV hit and observed zhool presence. These deserve retention.

The common preparation unroofs and clears pads, lays soil and removes wildlife. Cleanup restores settings to shipped defaults, ends conditions, destroys fixtures, undoes targeted retiling and ultimately returns the start biome/quiet-site statics. It does not restore original terrain, plants, roofs or removed wildlife from snapshots. It has no Designer scene-begin/end/hold recovery journal. A scratch-map instruction is not the same as proved restoration. Natural-rate ecology, colony-scale decisions and visual interactions need different starting states from cleared soil pads.

Top five correctness risks from the code reading

These are reading findings, not reproduced runtime diagnoses; no fixes or items were filed.

1. `src/RimMandrake/Contagion/Source/Hediff_AmoebaGestation.cs:44` — completion latches before `AmoebaHostUtility.cs:125` returns without a map; if gestation ticks in transport, the living host can remain permanently spent with no batch.
2. `src/RimMandrake/Contagion/Source/RM_ContagionSkyExtension.cs:95` — Burn shelter checks only the plant in the pawn's cell, so a pawn visibly under an adjacent crown can still be exposed; it does not consume shared crown geometry.
3. `src/RimMandrake/Contagion/Source/RM_GameCondition_ContagionBurn.cs:83` — native shelter orders happen after damage, leaving the approved pre-Burn Dive absent and vulnerable creatures liable to die before their first escape order.
4. `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionBulloos.xml:233` — zhool uses Pig meat without an explicit zero MeatAmount, unlike the main cast; inherited butchery output could breach the no-human-food design and needs a merged-def/butchery check.
5. `src/RimMandrake/Contagion/Source/JobDriver_RM_SampleDraftprint.cs:56` — placement failure is ignored after `DraftprintUtility.cs:51` marks the creature already sampled, potentially consuming its only scan without yielding a recoverable print.

Dry-run limits and checks

- This combines the requested stage 0 reading and stage 1 question preparation. No run ID, packet hash, budget, stage state, result.json or successful launcher check was fabricated.
- The role requires a fresh author-independent reviewer before questions are sent. This bank has an author evidence/wording check only, matching the reference dry run's pending-review status. No reviewer, pass verdict or token charge was invented. A real sitting should review the authoritative evidence and serve at most three questions per turn.
- The source/asset and relevant item accounting is in `built_reviewed`. Paths and ledger-only work are represented separately. It is not a full-file CLEAN review or the launcher's official replay/alias fold; a launched stage should regenerate and reconcile its precise built-evidence requirements.
- Both the frozen `infrastructure/state/ledger/events.jsonl` and seat shards were searched. Some September OWNER rows genuinely have no tsn; those use file/item provenance. Every OWNER tsn used in the artifacts is checked against OWNER.jsonl, without floating-point conversion.
- The mirror's `MIRROR_HEAD` read was `d38f30beddc230a019fa1f7185823d90e814fea8 2026-11-09T23:45:52-08:00`. The mirror refreshes externally; this is not an atomic snapshot. No git operation was needed.
- Artifact checks cover JSON parsing, field/enumeration validity, unique IDs, real source paths and cited line bounds, OWNER keys, inventory/question/coverage links and exactly two first questions. They do not accept the mod or the design.
- No system fault or lesson was filed through rimflow because the user's dry-run/no-ledger boundary takes precedence. No source or existing local log/brief was edited.

