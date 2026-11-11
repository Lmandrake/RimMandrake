## spec
Resolve the difference between a juvenile-only race's maximum supported pawn tier and HugeThings' lineage-based AdultTier classifier. RM_ReefbackJuv inherits base32 but supports only factors0.2/0.5: GetTier reaches T2, while AdultTier's maxFactor floor1 reports T3. Passage therefore rejects this candidate when a living T3 already exists, although the arrived calf cannot count as a living T3 itself. This is a concrete semantic difference, not proof that the intended lineage classification is wrong.

Preserve the owner's 2026-10-21 "Calves are ok" ruling (OWNER tsn1792618983088247673), biome-owned pool/list rules, land/sea matching and explicit force overrides. Obtain an independent delegated design ruling on lineage versus maximum-supported classification and the T3 spacing rule. Apply the warranted bounded fix, or document why retaining the current classification is intended; do not quietly change calf eligibility. Keep DefQualifies' conservative comp-attachment purpose separate from event tier semantics.

Evidence: whittle/ht-reefback-calf/JUDGE.md, section Consequences; evidence/raw/measure/broaden-followups.json; evidence/raw/owner-calf-ruling.json. Production source: HugeThings/Source/Titanic/Tiering/TitanicTierUtility.cs:78-105, Events/TitanPassage.cs:55-73 and118-120, Kernel/RM_TitanicKernel.cs:212-217. No existing live item covered this selected difference when filed.

## verify
The policy is explicit and independently judged. Focused kernel checks retain normal adult, juvenile-only, growth-above-one and force controls. Loaded minimal-tier C# reads and spacing-predicate calls agree with the chosen policy under default and custom thresholds; report loaded-method scope rather than a completed passage.

## criteria
- A1 L0: Source/specifications agree with an independent delegated classifier/spacing decision; focused positive and negative controls pass without changing the calf allowance or other passage gates.
- A2 L1: On a fresh deployed minimal-tier process, representative juvenile-only and ordinary adult definitions plus growth/force/threshold controls produce the chosen actual GetTier/AdultTier and T3-spacing results.

NEXT: inspect the exact owner calf ruling and raw gate matrix, freeze one whole Whittle statement, and obtain the delegated semantic decision before changing classification.

New mechanism not yet observed: the chosen juvenile-only event classification/spacing contract has no loaded-method proof; no claim of a natural passage or crossing is made here.
