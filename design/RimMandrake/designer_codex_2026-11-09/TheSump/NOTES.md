DRY RUN — TheSump Designer, stages 0 and 1 only

The mod was found at the requested `src/RimMandrake/TheSump` path. All three deliverables are agent-authored working artifacts. The proposed root is separate from the null `root`; every question is a draft and every guess is labelled. There are no owner approvals, waivers, stand-in replies, sent questions, ledger writes or completed stage claims. The mirror was only read; existing designer.log and designer_brief.md were left alone.

The top five correctness risks from the source read

1. `src/RimUtinni/UtinniPatches/Patches/RUT_TarShallow_GeneratedFilth.xml:36` — shallow tar's pickup-filth wiring and its sibling acceptance-mask patch still live in the campaign layer; no free-tier equivalent was found, so tar-on-boots and mouse-track promises may fail without Utinni.
2. `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_SumpLivingMap.cs:116` — the responder recognises only RM_TarGlass, while TheSump's cooling patch produces RM_Glasswalk; its synthetic RM_TarGlass test can pass while real cooled edges receive no crust/margin response.
3. `src/RimMandrake/TheSump/Source/RM_Comp_TarVaultSeal.cs:283` — clean extraction unseals the item but leaves it inside the shelf's held cells; the next Scan can seal and forbid it again before a hauler gets it out.
4. `src/RimMandrake/TheSump/Source/RM_Comp_TarVaultSeal.cs:121` — disabling the vault skips all scanning/unsealing, and no despawn/destroy cleanup exists in this comp; already sealed items can remain rot-disabled/forbidden when the advertised ordinary-shelf behaviour should resume.
5. `src/RimMandrake/EnvironmentalHazards/Source/RM_CompFloodIgniter.cs:105` — the fuse-post flood-fill tests terrain only and queues cells beyond closed sluices; independent vanilla-fire starts beyond a gate can bypass the gate-aware central liquid front.

These are source-based risks, not reproduced live diagnoses. For risk 1, the companion patch is `src/RimUtinni/UtinniPatches/Patches/RUT_TarShallow_FilthAcceptance.xml:54`. For risk 2, the conflicting assignment is `src/RimMandrake/TheSump/Patches/RM_Tar_GlasswalkCooling.xml:38`. The inventory keeps these mechanisms present; a defect does not turn built code into an unbuilt feature.

What could not be verified

No current gameplay, art or acceptance was verified. I did not build, deploy, change ModsConfig, touch the bridge, launch RimWorld, make a map/save, run a scene, validate a first-touch pass, run a repository test, or bind an oracle. Some repository tests write beside themselves or call live services; they were read only. The only executed checks validate these three local deliverables.

No proof is labelled current. The ledger records a Glasswalk A1 L2 PASS on 2026-11-06 at `3369575b5c78` and a living-map PASS that day at `89b4c56d88e335b8e5902cf0d8f30281e521f521`. Their raw Linux/stevedesktop reports are not in this mirror, and I did not match runtime, settings, compose, source or data fingerprints. Those passes are preserved as historical evidence. Network-fire A1/A2/A3 have recorded failures followed by build carries and a stale-build refusal; I found no later pass. A historical close may mean authored/compiled work and does not by itself accept the experience.

The walk is DRAFT and partly stale: it still names donor dependencies, a campaign-only vault and a much smaller settings set. About.xml still describes a mouse placeholder and deploy holds; current real mouse/beast defs and the hold file show those descriptions are historical. Old item NEXT lines were not treated as current implementation truth. No Sump tile-count defect was inferred; the fixed world is painted at the end.

The largest remaining design-to-code gaps are already identified in the inventory: pallick collapse and its mouse tell; custom mound/guard ecology; dredgel attraction and skarrid mobile dread; special native tar crossing; reliable initial indicator placement; the ordinary beast's day-ahead warning; natural seep flames and discovery triggers; distinctive archive finds; and the old promised smoke-wall consumer. These are distinct from the built bodies, generic jobs and support code. No new engineering solution or reduction in scope was approved here.

Current Brindeth yields no wood under a later size ruling, so the old claim that it supplies duckboards is false today. Existing WoodLog costs need a real supply check. The strong-solvent item has a trade hook, but a functioning foreign trade route was not established. I did not establish a current tar-gas fuel link into FlameStatues, gravship placement of the named gifts, or every ColdStorage aging/filter interaction. No flyer flight was tested.

The old RM_FlameStatuary is now save-compatibility content. Current secular statues belong to FlameStatues; the Holy Flame use interaction moved to UtinniStatues' Shkaar idol. The Sinking and effigy offerings are v2 by the owner's retarget events. The v2 document expressly excludes the other-faith Holy Flame rite, and the solvent pour is a deliberate weapon, so neither was casually swept into that deferral.

Proof-scene audit

`record.json` audits every chain/staged variant in TheSump's validation suite and directly relevant external proofs for asserted start, control, restoration and hold. Def lookup has an absent-name control; settings writes restore values; the exact-clock Glasswalk runner has a useful same-pawn granite comparison and disposes of its temporary map. Neither proves the complete Sump day.

Vault and kethrel hooks call direct methods and inspect immediate flags. They lack exception-safe cleanup; the kethrel hook destroys all nearby steel, and the vault hook can select unrelated ruined goods. The capstan proof forces power, bypasses acquisition/reel timing and leaves random snap possible. Most map-mechanics rows explicitly stage nothing and report UNMEASURED. The dig has no audible click/letter, while an automatic disarm job can send an under-skilled miner; question 04 addresses the unresolved reaction contract without re-asking skilled disarm.

The living-map hook restores its terrain/plants/settings but clears the pre-existing responder queues and uses synthetic time. The network-fire proof restores settings without restoring its canal, fluid, gate and fire state. None has a Designer recovery journal or owner-review hold. Later scene planning must retain independent feature scenes plus actual interactions: flood-to-cooling-to-mice/plants, fuse-to-liquid-network-to-gate, exposure-to-cleaning-to-gaslight, and harvest-to-preservation-to-retrieval. A direct-method pass is not their substitute.

Evidence and protocol limits

The source head read was `bc9b4bbb74d7dce9c020658c8f7e6dd6b2308b66`, MIRROR_HEAD stamped `2026-11-10T01:33:38-08:00`; it was unchanged at accounting. This is an externally refreshed mirror, not an atomic checkout or a live-game fingerprint. I did not recover git history, erased Transient review sheets or remote proof files.

The record accounts for the mod's current non-generated files/assets, live/closed Sump item families, ledger-only work and the relevant live-proof pointers. Assets are accounted for by capability, not judged visually. Current XML elements and patch additions take precedence over the older roster JSON's donor-era list. Broader design searches were bounded to direct Sump documents and named neighbour uncertainties; the whole planet's content was not audited. Inhabited injections and the neighbouring titan-passage question remain explicitly unknown rather than invented absences.

This was not a launcher invocation: no run ID, aliases packet, folded official done-set, budget or result was fabricated, and stages did not advance. Some early OWNER shard rows have no tsn; their decisions use real ITEM/path sources. Every OWNER reference used in the record must match an exact tsn in OWNER.jsonl. The experience sentence uses the requested experience-file source, without a fabricated ledger event.

Questions have had a local evidence/wording review only. The role's fresh author-independent review is still owed before a real sent turn; no reviewer identity, pass verdict or token charge was invented. The eight questions are a bank, with 01–02 first and at most three per later turn. The rehearsal makes no claim that an approved root, accepted showcase or handoff exists.

The role's usual instruction to file system faults/lessons does not override the explicit no-ledger boundary of this task. These observations remain here, with no priority or build item assigned.

Local deliverable checks passed: JSON parses; implementation/proof/scope fields and enum values are valid; inventory IDs are unique; question and coverage links resolve; all cited paths/items and exact OWNER tsns exist; all eight questions match QUESTIONS.md; the root remains null; and there are exactly three failure modes. Current XML was parsed as elements to cross-check roster/def coverage and confirm that no active TheSump deploy hold remains. These checks are not launcher acceptance or gameplay proof.
